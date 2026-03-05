"""脑图数据管理路由 - 用例集脑图 CRUD、解析同步到 test_cases"""
import json
import uuid
from datetime import datetime, timezone, timedelta

from flask import Blueprint, request
from flask_login import login_required, current_user

from app.models.models import db, TestSuite, TestCase, TestCaseExecution, CaseTag, CaseMarker, MindmapVersion
from app.utils.helpers import success_response, error_response

LOCAL_TIMEZONE = timezone(timedelta(hours=8))

bp = Blueprint('mindmap', __name__, url_prefix='/api/mindmap')

MAX_DEPTH = 10


# ---------------------------------------------------------------------------
# 脑图 CRUD
# ---------------------------------------------------------------------------

@bp.route('/<int:suite_id>', methods=['GET'])
@login_required
def get_mindmap(suite_id):
    """获取用例集的脑图数据"""
    try:
        suite = TestSuite.query.get_or_404(suite_id)
        if suite.type != 'suite':
            return error_response(400, '只有用例集才有脑图数据')

        mindmap_data = None
        if suite.case_mindmap_data:
            try:
                mindmap_data = json.loads(suite.case_mindmap_data)
            except json.JSONDecodeError:
                mindmap_data = None

        from_cases = None
        if not mindmap_data:
            # 无脑图数据时：若 test_cases 表中有用例（如 AI 生成），则从用例反推脑图并返回
            from_cases = _build_mindmap_from_cases(suite)
            mindmap_data = from_cases or _build_default_mindmap(suite)

        case_count = (from_cases['metadata']['total_cases'] if from_cases else None) or suite.case_count or 0
        mindmap_version = getattr(suite, 'mindmap_version', None)
        if mindmap_version is None:
            mindmap_version = 0
        return success_response({
            'suite_id': suite.id,
            'suite_name': suite.suite_name,
            'case_edit_status': suite.case_edit_status or 'drafting',
            'case_count': case_count,
            'review_status': suite.review_status or 'not_reviewed',
            'mindmap_data': mindmap_data,
            'mindmap_version': mindmap_version,
            'project_id': suite.project_id,
            'version_requirement_id': suite.version_requirement_id,
            'version_requirement_name': suite.version_requirement.requirement_name if suite.version_requirement else None,
        })
    except Exception as e:
        return error_response(500, f'获取脑图数据失败: {str(e)}')


@bp.route('/<int:suite_id>', methods=['PUT'])
@login_required
def save_mindmap(suite_id):
    """保存脑图数据并同步到 test_cases 表"""
    try:
        suite = TestSuite.query.get_or_404(suite_id)
        if suite.type != 'suite':
            return error_response(400, '只有用例集才能保存脑图数据')

        data = request.get_json()
        mindmap_data = data.get('mindmap_data')
        if not mindmap_data or 'root' not in mindmap_data:
            return error_response(400, '脑图数据格式无效')

        # 多人编辑：版本冲突检测（支持 force_overwrite 强制覆盖）
        client_version = data.get('mindmap_version')
        force_overwrite = data.get('force_overwrite') is True
        current_version = getattr(suite, 'mindmap_version', None)
        if current_version is None:
            current_version = 0
        if not force_overwrite and client_version is not None and client_version != current_version:
            return error_response(
                409,
                '脑图已被他人更新，请刷新后重新编辑再保存，或选择强制覆盖。',
                data={'server_version': current_version}
            )

        depth = _get_tree_depth(mindmap_data['root'])
        if depth > MAX_DEPTH:
            return error_response(400, f'脑图层级不能超过{MAX_DEPTH}层，当前{depth}层')

        suite.mindmap_version = current_version + 1
        suite.case_mindmap_data = json.dumps(mindmap_data, ensure_ascii=False)
        suite.last_saved_at = datetime.now(LOCAL_TIMEZONE)
        suite.last_saved_by = current_user.id

        if 'case_edit_status' in data:
            suite.case_edit_status = data['case_edit_status']

        cases = _parse_mindmap_to_cases(mindmap_data['root'], suite)
        _sync_cases_to_db(cases, suite)

        suite.case_count = len(cases)
        mindmap_data.setdefault('metadata', {})
        mindmap_data['metadata']['total_cases'] = len(cases)
        mindmap_data['metadata']['last_saved_at'] = suite.last_saved_at.isoformat()
        mindmap_data['metadata']['last_saved_by'] = current_user.id
        suite.case_mindmap_data = json.dumps(mindmap_data, ensure_ascii=False)
        db.session.add(MindmapVersion(
            suite_id=suite.id,
            snapshot=suite.case_mindmap_data,
            created_by=current_user.id,
        ))
        db.session.commit()
        # 每个用例集最多保留 30 个版本
        versions = MindmapVersion.query.filter_by(suite_id=suite.id).order_by(MindmapVersion.id.desc()).offset(30).all()
        for v in versions:
            db.session.delete(v)
        if versions:
            db.session.commit()

        return success_response({
            'suite_id': suite.id,
            'case_count': suite.case_count,
            'last_saved_at': suite.last_saved_at.isoformat(),
            'mindmap_version': suite.mindmap_version,
        })
    except Exception as e:
        db.session.rollback()
        return error_response(500, f'保存脑图失败: {str(e)}')


@bp.route('/<int:suite_id>/version', methods=['GET'])
@login_required
def get_mindmap_version(suite_id):
    """仅返回脑图版本号，用于多人编辑时轮询检测他人是否已保存"""
    try:
        suite = TestSuite.query.get_or_404(suite_id)
        if suite.type != 'suite':
            return error_response(400, '只有用例集才有脑图数据')
        version = getattr(suite, 'mindmap_version', None)
        if version is None:
            version = 0
        return success_response({'mindmap_version': version})
    except Exception as e:
        return error_response(500, f'获取版本失败: {str(e)}')


@bp.route('/<int:suite_id>/versions', methods=['GET'])
@login_required
def get_mindmap_versions(suite_id):
    """获取用例集脑图版本列表（用于版本回退）"""
    try:
        suite = TestSuite.query.get_or_404(suite_id)
        if suite.type != 'suite':
            return error_response(400, '只有用例集才有脑图版本')
        versions = MindmapVersion.query.filter_by(suite_id=suite_id).order_by(MindmapVersion.id.desc()).limit(50).all()
        return success_response([v.to_dict() for v in versions])
    except Exception as e:
        return error_response(500, f'获取版本列表失败: {str(e)}')


@bp.route('/<int:suite_id>/rollback', methods=['POST'])
@login_required
def rollback_mindmap(suite_id):
    """回退到指定版本（将当前脑图数据替换为该版本快照）"""
    try:
        suite = TestSuite.query.get_or_404(suite_id)
        if suite.type != 'suite':
            return error_response(400, '只有用例集才能回退脑图')
        data = request.get_json() or {}
        version_id = data.get('version_id')
        if not version_id:
            return error_response(400, '缺少 version_id')
        ver = MindmapVersion.query.filter_by(id=version_id, suite_id=suite_id).first()
        if not ver:
            return error_response(404, '版本不存在')
        suite.case_mindmap_data = ver.snapshot
        suite.last_saved_at = datetime.now(LOCAL_TIMEZONE)
        suite.last_saved_by = current_user.id
        db.session.commit()
        mindmap_data = json.loads(ver.snapshot) if ver.snapshot else None
        return success_response({
            'suite_id': suite.id,
            'mindmap_data': mindmap_data,
            'message': '已回退到该版本',
        })
    except Exception as e:
        db.session.rollback()
        return error_response(500, f'回退失败: {str(e)}')


@bp.route('/<int:suite_id>/validate', methods=['POST'])
@login_required
def validate_mindmap(suite_id):
    """校验脑图数据是否符合用例规范"""
    try:
        data = request.get_json()
        mindmap_data = data.get('mindmap_data')
        if not mindmap_data or 'root' not in mindmap_data:
            return error_response(400, '脑图数据格式无效')

        errors = _validate_attribute_chains(mindmap_data['root'])
        if errors:
            return success_response({'valid': False, 'errors': errors})
        return success_response({'valid': True, 'errors': []})
    except Exception as e:
        return error_response(500, f'校验失败: {str(e)}')


@bp.route('/<int:suite_id>/status', methods=['PUT'])
@login_required
def update_edit_status(suite_id):
    """更新用例编辑状态"""
    try:
        suite = TestSuite.query.get_or_404(suite_id)
        data = request.get_json()
        new_status = data.get('case_edit_status')
        if new_status not in ('drafting', 'completed'):
            return error_response(400, '无效的编辑状态')
        suite.case_edit_status = new_status
        db.session.commit()
        return success_response({'case_edit_status': new_status})
    except Exception as e:
        db.session.rollback()
        return error_response(500, f'更新状态失败: {str(e)}')


# ---------------------------------------------------------------------------
# 标签 & 标记 CRUD
# ---------------------------------------------------------------------------

@bp.route('/tags/<int:project_id>', methods=['GET'])
@login_required
def get_tags(project_id):
    tags = CaseTag.query.filter_by(project_id=project_id).all()
    return success_response([t.to_dict() for t in tags])


@bp.route('/tags', methods=['POST'])
@login_required
def create_tag():
    data = request.get_json()
    tag = CaseTag(
        tag_name=data['tag_name'],
        tag_color=data.get('tag_color', '#409EFF'),
        project_id=data['project_id'],
        creator_id=current_user.id,
    )
    db.session.add(tag)
    db.session.commit()
    return success_response(tag.to_dict(), 201)


@bp.route('/tags/<int:tag_id>', methods=['DELETE'])
@login_required
def delete_tag(tag_id):
    tag = CaseTag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    return success_response({'message': '标签已删除'})


@bp.route('/markers/<int:project_id>', methods=['GET'])
@login_required
def get_markers(project_id):
    markers = CaseMarker.query.filter_by(project_id=project_id).all()
    if not markers:
        _init_system_markers(project_id)
        markers = CaseMarker.query.filter_by(project_id=project_id).all()
    return success_response([m.to_dict() for m in markers])


@bp.route('/markers', methods=['POST'])
@login_required
def create_marker():
    data = request.get_json()
    marker = CaseMarker(
        marker_name=data['marker_name'],
        marker_type='custom',
        project_id=data['project_id'],
        creator_id=current_user.id,
    )
    db.session.add(marker)
    db.session.commit()
    return success_response(marker.to_dict(), 201)


@bp.route('/markers/<int:marker_id>', methods=['DELETE'])
@login_required
def delete_marker(marker_id):
    marker = CaseMarker.query.get_or_404(marker_id)
    if marker.marker_type == 'system':
        return error_response(400, '系统标记不能删除')
    db.session.delete(marker)
    db.session.commit()
    return success_response({'message': '标记已删除'})


# ---------------------------------------------------------------------------
# 内部工具函数
# ---------------------------------------------------------------------------

def _build_default_mindmap(suite):
    """为空用例集构建默认脑图结构"""
    return {
        'version': '2.0',
        'root': {
            'id': 'root',
            'text': suite.suite_name,
            'children': [],
        },
        'metadata': {
            'total_cases': 0,
            'last_saved_at': None,
            'last_saved_by': None,
        },
    }


def _build_mindmap_from_cases(suite):
    """
    根据 test_cases 表中的用例数据构建脑图 JSON（用于 AI 生成用例后或仅有 DB 用例无脑图时）。
    链路与脑图编辑一致：case_title → test_data(可选) → precondition → step → expected_result。
    若该用例集无任何用例则返回 None。
    """
    cases = TestCase.query.filter_by(suite_id=suite.id).order_by(TestCase.id).all()
    if not cases:
        return None
    root_children = []
    for c in cases:
        node_id = c.mindmap_node_id or str(uuid.uuid4())
        title_node = {
            'id': node_id,
            'text': (c.case_name or '').strip() or '未命名用例',
            'attribute': 'case_title',
            'priority': (c.priority or 'P1').strip() or 'P1',
            'tags': (c.tags if isinstance(c.tags, list) else []) or [],
            'markers': (c.markers if isinstance(c.markers, list) else []) or [],
            'children': [],
        }
        if c.test_data and str(c.test_data).strip():
            td_node = {'id': str(uuid.uuid4()), 'text': (c.test_data or '').strip(), 'attribute': 'test_data', 'children': []}
            prec_node = {'id': str(uuid.uuid4()), 'text': (c.preconditions or '').strip(), 'attribute': 'precondition', 'children': []}
            td_node['children'].append(prec_node)
            title_node['children'].append(td_node)
        else:
            prec_node = {'id': str(uuid.uuid4()), 'text': (c.preconditions or '').strip(), 'attribute': 'precondition', 'children': []}
            title_node['children'].append(prec_node)
        step_node = {'id': str(uuid.uuid4()), 'text': (c.steps or '').strip(), 'attribute': 'step', 'children': []}
        prec_node['children'].append(step_node)
        er_node = {'id': str(uuid.uuid4()), 'text': (c.expected_result or '').strip(), 'attribute': 'expected_result', 'children': []}
        step_node['children'].append(er_node)
        root_children.append(title_node)
    root = {'id': 'root', 'text': suite.suite_name, 'children': root_children}
    return {
        'version': '2.0',
        'root': root,
        'metadata': {
            'total_cases': len(cases),
            'last_saved_at': None,
            'last_saved_by': None,
        },
    }


def _get_tree_depth(node, current=1):
    """计算脑图树的最大深度"""
    children = node.get('children', [])
    if not children:
        return current
    return max(_get_tree_depth(c, current + 1) for c in children)


def _parse_mindmap_to_cases(root_node, suite):
    """递归遍历脑图树，提取完整用例列表"""
    cases = []
    _walk_for_cases(root_node, [], cases, suite)
    return cases


def _walk_for_cases(node, group_path, cases, suite):
    """递归遍历：遇到 case_title 或独立 precondition 时提取用例"""
    attr = node.get('attribute')

    if attr == 'case_title':
        case = _extract_case(node, group_path)
        if case:
            cases.append(case)
        return

    if attr == 'precondition':
        case = _extract_case_no_title(node, group_path)
        if case:
            cases.append(case)
        return

    new_path = group_path + [node.get('text', '')] if node.get('id') != 'root' else group_path
    for child in node.get('children', []):
        _walk_for_cases(child, new_path, cases, suite)


def _extract_case(title_node, group_path):
    """从 case_title 沿链提取单条用例
    链路: case_title → test_data(可选) → precondition → step(1个) → expected_result(1个)
    steps 和 expected_result 均为纯文本
    """
    case_name = title_node.get('text', '')
    priority = _resolve_priority(title_node)
    node_id = title_node.get('id', str(uuid.uuid4()))
    tags = title_node.get('tags', [])
    markers = title_node.get('markers', [])

    next_node = title_node
    test_data_text = ''

    td_node = _find_child_by_attr(next_node, 'test_data')
    if td_node:
        test_data_text = td_node.get('text', '')
        next_node = td_node

    prec_node = _find_child_by_attr(next_node, 'precondition')
    if not prec_node:
        return None

    step_node = _find_child_by_attr(prec_node, 'step')
    if not step_node:
        return None

    er_node = _find_child_by_attr(step_node, 'expected_result')

    return {
        'mindmap_node_id': node_id,
        'case_name': case_name,
        'priority': priority,
        'test_data': test_data_text,
        'preconditions': prec_node.get('text', ''),
        'steps': step_node.get('text', ''),
        'expected_result': er_node.get('text', '') if er_node else '',
        'group_path': ' > '.join(group_path) if group_path else '',
        'tags': tags,
        'markers': markers,
    }


def _extract_case_no_title(prec_node, group_path):
    """从独立 precondition 提取用例（无 case_title 场景）"""
    case_name = group_path[-1] if group_path else prec_node.get('text', '')
    priority = _resolve_priority(prec_node)
    node_id = prec_node.get('id', str(uuid.uuid4()))
    tags = prec_node.get('tags', [])
    markers = prec_node.get('markers', [])

    step_node = _find_child_by_attr(prec_node, 'step')
    if not step_node:
        return None
    er_node = _find_child_by_attr(step_node, 'expected_result')

    return {
        'mindmap_node_id': node_id,
        'case_name': case_name,
        'priority': priority,
        'test_data': '',
        'preconditions': prec_node.get('text', ''),
        'steps': step_node.get('text', ''),
        'expected_result': er_node.get('text', '') if er_node else '',
        'group_path': ' > '.join(group_path[:-1]) if len(group_path) > 1 else '',
        'tags': tags,
        'markers': markers,
    }


def _find_child_by_attr(node, attribute):
    for child in node.get('children', []):
        if child.get('attribute') == attribute:
            return child
    return None


def _resolve_priority(node):
    """从节点自身及其子链中解析优先级（最深层优先）"""
    best = node.get('priority')

    def _walk_priority(n):
        nonlocal best
        p = n.get('priority')
        if p:
            best = p
        for c in n.get('children', []):
            _walk_priority(c)

    _walk_priority(node)
    return best or 'P1'


def _sync_cases_to_db(parsed_cases, suite):
    """将解析出的用例与 test_cases 表同步（增/改/删）"""
    existing = {c.mindmap_node_id: c for c in
                TestCase.query.filter_by(suite_id=suite.id).all()
                if c.mindmap_node_id}

    new_node_ids = {c['mindmap_node_id'] for c in parsed_cases}

    for pc in parsed_cases:
        nid = pc['mindmap_node_id']
        if nid in existing:
            tc = existing[nid]
            tc.case_name = pc['case_name']
            tc.priority = pc['priority']
            tc.test_data = pc.get('test_data', '')
            tc.preconditions = pc['preconditions']
            tc.steps = pc['steps']
            tc.expected_result = pc['expected_result']
            tc.group_path = pc['group_path']
            tc.tags = pc['tags']
            tc.markers = pc['markers']
        else:
            tc = TestCase(
                case_name=pc['case_name'],
                priority=pc['priority'],
                test_data=pc.get('test_data', ''),
                preconditions=pc['preconditions'],
                steps=pc['steps'],
                expected_result=pc['expected_result'],
                group_path=pc['group_path'],
                tags=pc['tags'],
                markers=pc['markers'],
                mindmap_node_id=nid,
                suite_id=suite.id,
                project_id=suite.project_id,
                version_requirement_id=suite.version_requirement_id,
                iteration_id=suite.iteration_id,
                creator_id=current_user.id,
                status='',
            )
            db.session.add(tc)

    for nid, tc in existing.items():
        if nid not in new_node_ids:
            # 先删除引用该用例的执行记录，避免 case_id NOT NULL 约束报错
            TestCaseExecution.query.filter_by(case_id=tc.id).delete(synchronize_session=False)
            db.session.delete(tc)


def _validate_attribute_chains(root_node):
    """校验脑图中所有属性链是否符合规范"""
    errors = []
    _validate_walk(root_node, errors, [])
    return errors


def _validate_walk(node, errors, path):
    """校验：根下可有多层分组节点；用例链路仅出现在末尾，且为单链
    链路: 用例标题 → 测试数据(可选) → 前置条件 → 操作步骤 → 预期结果
    链上节点均不能有同级，预期结果不能有子节点
    """
    attr = node.get('attribute')
    txt = node.get('text', '(空节点)')
    cur = path + [txt]
    children = node.get('children', [])

    if attr == 'case_title':
        if len(children) != 1:
            errors.append(f'"{txt}": 用例标题下必须有且只有1个子节点（测试数据或前置条件），当前{len(children)}个')
            return
        ch = children[0]
        ch_attr = ch.get('attribute')
        if ch_attr == 'test_data':
            _validate_test_data(ch, errors, cur)
        elif ch_attr == 'precondition':
            _validate_prec(ch, errors, cur)
        else:
            errors.append(f'"{txt}": 用例标题下只能是测试数据或前置条件，当前为{ch_attr or "分组"}')
        return

    if attr == 'test_data':
        _validate_test_data(node, errors, cur)
        return

    if attr == 'precondition':
        if len(children) != 1:
            errors.append(f'"{txt}": 前置条件下必须有且只有1个操作步骤，当前{len(children)}个')
            return
        if children[0].get('attribute') != 'step':
            errors.append(f'"{txt}": 前置条件下必须是操作步骤节点')
            return
        _validate_step(children[0], errors, cur)
        return

    if attr == 'step':
        _validate_step(node, errors, cur)
        return

    if attr == 'expected_result':
        if children:
            errors.append(f'"{txt}": 预期结果节点下不允许有子节点')
        return

    for child in children:
        ca = child.get('attribute')
        if ca in ('step', 'expected_result'):
            errors.append(f'"{child.get("text","")}": 分组节点下不能直接放置操作步骤或预期结果')
        else:
            _validate_walk(child, errors, cur)


def _validate_test_data(node, errors, path):
    """测试数据下必须有且只有1个前置条件"""
    children = node.get('children', [])
    if len(children) != 1:
        errors.append(f'"{node.get("text","")}": 测试数据下必须有且只有1个前置条件，当前{len(children)}个')
        return
    if children[0].get('attribute') != 'precondition':
        errors.append(f'"{node.get("text","")}": 测试数据下必须是前置条件节点')
        return
    prec = children[0]
    prec_children = prec.get('children', [])
    if len(prec_children) != 1 or prec_children[0].get('attribute') != 'step':
        errors.append(f'"{prec.get("text","")}": 前置条件下必须有且只有1个操作步骤')
        return
    _validate_step(prec_children[0], errors, path)


def _validate_prec(node, errors, path):
    """前置条件下必须有且只有1个操作步骤"""
    steps = [c for c in node.get('children', []) if c.get('attribute') == 'step']
    if len(steps) != 1:
        errors.append(f'"{node.get("text","")}": 前置条件下必须有且只有1个操作步骤，当前{len(steps)}个')
        return
    _validate_step(steps[0], errors, path)


def _validate_step(node, errors, path):
    """操作步骤下必须有且只有1个预期结果，且预期结果无子节点"""
    children = node.get('children', [])
    if len(children) != 1:
        errors.append(f'"{node.get("text","")}": 操作步骤下必须有且只有1个预期结果，当前{len(children)}个')
        return
    er = children[0]
    if er.get('attribute') != 'expected_result':
        errors.append(f'"{node.get("text","")}": 操作步骤下必须是预期结果节点')
        return
    if er.get('children'):
        errors.append(f'"{er.get("text","")}": 预期结果节点下不允许有子节点')


def _init_system_markers(project_id):
    """为项目初始化系统标记"""
    for name in ['未完成', '待确认', '待修改']:
        exists = CaseMarker.query.filter_by(project_id=project_id, marker_name=name).first()
        if not exists:
            db.session.add(CaseMarker(
                marker_name=name,
                marker_type='system',
                project_id=project_id,
                creator_id=current_user.id,
            ))
    db.session.commit()
