"""测试套件/用例集路由：目录树、CRUD、导入导出。"""
from flask import Blueprint, request
from flask_login import login_required, current_user
from app.models.models import db, TestSuite, TestCase, TestTask, TestSuiteReviewTask
from app.utils.helpers import success_response, error_response, get_pagination_params

bp = Blueprint('test_suites', __name__, url_prefix='/api/test-suites')


@bp.route('/', methods=['GET'])
@login_required
def get_test_suites():
    """获取测试套件列表，支持分页、筛选和树形结构"""
    try:
        with_children = request.args.get('with_children', 'false').lower() == 'true'
        
        if with_children:
            root_suites = TestSuite.query.filter_by(parent_id=None).filter(
                TestSuite.deleted_at.is_(None)
            ).all()

            def build_tree(suite):
                suite_dict = suite.to_dict()
                children = []
                for child in suite.children:
                    if child.deleted_at is None:
                        children.append(build_tree(child))
                suite_dict['children'] = children
                return suite_dict

            tree_data = [build_tree(suite) for suite in root_suites]
            return success_response(tree_data)
        else:
            page, per_page = get_pagination_params()
            query = TestSuite.query
            
            if request.args.get('status'):
                query = query.filter_by(status=request.args['status'])
            
            if request.args.get('parent_id'):
                query = query.filter_by(parent_id=request.args['parent_id'])
            elif 'all' not in request.args:
                query = query.filter_by(parent_id=None)
            
            pagination = query.order_by(TestSuite.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            items = [suite.to_dict() for suite in pagination.items]
            
            return success_response({
                'items': items,
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'pages': pagination.pages
            })
    except Exception as e:
        return error_response(500, f'获取测试套件失败: {str(e)}')


@bp.route('/<int:suite_id>', methods=['GET'])
@login_required
def get_test_suite(suite_id):
    """获取单个测试套件详情"""
    try:
        suite = TestSuite.query.get_or_404(suite_id)
        return success_response(suite.to_dict())
    except Exception as e:
        return error_response(500, f'获取测试套件详情失败: {str(e)}')


def get_suite_depth(suite_id):
    """计算测试套件的深度"""
    depth = 0
    current = TestSuite.query.get(suite_id)
    while current and current.parent_id:
        depth += 1
        current = current.parent
    return depth

@bp.route('/', methods=['POST'])
@login_required
def create_test_suite():
    """创建新的测试套件"""
    try:
        data = request.get_json()
        
        if not data.get('suite_name'):
            return error_response(400, '套件名称不能为空')
        if len(data['suite_name']) > 30:
            return error_response(400, '套件名称不能超过30个字符')
        
        suite_type = data.get('type', 'folder')
        if suite_type not in ['folder', 'suite']:
            return error_response(400, '套件类型无效，只能是folder或suite')
        
        parent_id = data.get('parent_id')
        
        depth = 0
        if parent_id is not None:
            parent_suite = TestSuite.query.get(parent_id)
            if not parent_suite:
                return error_response(400, '父套件不存在')
            
            if parent_suite.type != 'folder':
                return error_response(400, '只能在文件夹中创建子套件')
            
            depth = get_suite_depth(parent_id) + 1
            
            # 限制深度不超过5层
            if depth >= 5:
                return error_response(400, '测试套件深度不能超过5层')
            
            # 最深一层只能是用例集
            if depth == 4 and suite_type != 'suite':
                return error_response(400, '最深一层只能创建用例集')
        
        max_sort_order = db.session.query(db.func.max(TestSuite.sort_order))
        if parent_id is not None:
            max_sort_order = max_sort_order.filter_by(parent_id=parent_id)
        else:
            max_sort_order = max_sort_order.filter_by(parent_id=None)
        
        max_sort_order = max_sort_order.scalar() or 0
        new_sort_order = max_sort_order + 1
        
        project_id = data.get('project_id')
        iteration_id = data.get('iteration_id')
        if parent_id is not None:
            parent_suite = TestSuite.query.get(parent_id)
            if parent_suite:
                project_id = parent_suite.project_id
                if iteration_id is None:
                    iteration_id = parent_suite.iteration_id
        if project_id is None:
            return error_response(400, '缺少所属项目，请指定 project_id')
        
        new_suite = TestSuite(
            suite_name=data['suite_name'],
            description=data.get('description', ''),
            parent_id=parent_id,
            status=data.get('status', 'active'),
            type=suite_type,
            creator_id=current_user.id,
            project_id=project_id,
            version_requirement_id=data.get('version_requirement_id'),
            iteration_id=iteration_id,
            sort_order=new_sort_order
        )
        
        db.session.add(new_suite)
        db.session.commit()

        return success_response(new_suite.to_dict(), "创建成功")
    except Exception as e:
        db.session.rollback()
        return error_response(500, f'创建测试套件失败: {str(e)}')


@bp.route('/<int:suite_id>', methods=['PUT'])
@login_required
def update_test_suite(suite_id):
    """更新测试套件信息"""
    try:
        suite = TestSuite.query.get_or_404(suite_id)
        data = request.get_json()
        
        original_parent_id = suite.parent_id
        original_sort_order = suite.sort_order
        original_type = suite.type
        
        if 'suite_name' in data:
            name = data['suite_name']
            if len(name) > 30:
                return error_response(400, '套件名称不能超过30个字符')
            suite.suite_name = name
        if 'description' in data:
            suite.description = data['description']
        if 'parent_id' in data:
            # 检查是否会形成循环引用
            new_parent_id = data['parent_id']
            if new_parent_id is not None:
                parent = TestSuite.query.get(new_parent_id)
                if parent:
                    # 简单检查是否会形成循环
                    current = parent
                    while current:
                        if current.id == suite_id:
                            return error_response(400, '不能将套件设置为自己的子套件或间接子套件')
                        current = current.parent
                    # 验证父套件类型必须是folder
                    if parent.type != 'folder':
                        return error_response(400, '只能将套件移动到文件夹中')
                    
                    # 计算新的深度
                    new_depth = get_suite_depth(new_parent_id) + 1
                    # 限制深度不超过5层
                    if new_depth >= 5:
                        return error_response(400, '测试套件深度不能超过5层')
                    
                    # 最深一层只能是用例集
                    if new_depth == 4 and suite.type != 'suite':
                        return error_response(400, '最深一层只能是用例集')
                    
                    # 移动后归属新父所在项目：当前节点及所有后代 project_id 与父一致（严格项目隔离）
                    new_project_id = parent.project_id
                    suite.project_id = new_project_id
                    _set_project_id_recursive(suite, new_project_id)
            else:
                # 根套件深度为0
                new_depth = 0
            suite.parent_id = new_parent_id
        if 'status' in data:
            suite.status = data['status']
        if 'sort_order' in data:
            suite.sort_order = data['sort_order']
        if 'type' in data:
            new_type = data['type']
            if new_type not in ['folder', 'suite']:
                return error_response(400, '套件类型无效，只能是folder或suite')
            
            # 计算当前套件的深度
            depth = get_suite_depth(suite.id)
            
            # 最深一层只能是用例集
            if depth == 4 and new_type != 'suite':
                return error_response(400, '最深一层只能是用例集')
            
            # 验证类型变更的合法性
            if new_type == 'suite':
                # 如果要改为用例集，必须没有子套件
                if len(suite.children) > 0:
                    return error_response(400, '包含子套件的套件不能改为用例集')
            
            # 如果要改为文件夹，需要确保父套件类型合法
            if new_type == 'folder' and suite.parent_id is not None:
                parent = TestSuite.query.get(suite.parent_id)
                if parent and parent.type != 'folder':
                    return error_response(400, '只能在文件夹中创建文件夹')
            
            suite.type = new_type
        
        # 移除评审相关字段的直接更新，评审状态由评审任务管理
        
        if 'project_id' in data:
            if suite.parent_id is not None:
                parent = TestSuite.query.get(suite.parent_id)
                if parent:
                    suite.project_id = parent.project_id
            else:
                suite.project_id = data['project_id']
        if 'version_requirement_id' in data:
            suite.version_requirement_id = data['version_requirement_id']
        if 'iteration_id' in data:
            suite.iteration_id = data['iteration_id']
        
        # 如果父级或排序发生变化，需要重新调整排序
        parent_id_changed = 'parent_id' in data and data['parent_id'] != original_parent_id
        sort_order_changed = 'sort_order' in data and data['sort_order'] != original_sort_order
        if parent_id_changed or sort_order_changed:
            
            if parent_id_changed:
                original_siblings = TestSuite.query.filter_by(parent_id=original_parent_id).all()
                original_siblings.sort(key=lambda x: x.sort_order)
                for i, sibling in enumerate(original_siblings):
                    sibling.sort_order = i + 1
                
                # 如果移动到新的父节点，将当前节点的sort_order设置为新父节点下的最大值+1
                max_sort_order = db.session.query(db.func.max(TestSuite.sort_order))
                max_sort_order = max_sort_order.filter_by(parent_id=suite.parent_id).scalar() or 0
                suite.sort_order = max_sort_order + 1
            
            other_siblings = TestSuite.query.filter(
                TestSuite.parent_id == suite.parent_id,
                TestSuite.id != suite.id
            ).all()
            
            all_siblings = [suite] + other_siblings
            all_siblings.sort(key=lambda x: (x.sort_order, 0 if x.id == suite_id else 1))
            for i, sibling in enumerate(all_siblings):
                sibling.sort_order = i + 1
        
        db.session.commit()
        
        return success_response(suite.to_dict())
    except Exception as e:
        db.session.rollback()
        return error_response(500, f'更新测试套件失败: {str(e)}')


def _collect_suite_ids(suite_obj):
    """收集该套件及其所有子孙套件的 id 列表（用于关联引用校验）"""
    ids = [suite_obj.id]
    for child in suite_obj.children:
        ids.extend(_collect_suite_ids(child))
    return ids


def _set_deleted_at_recursive(suite_obj, deleted_at):
    """递归设置 deleted_at（逻辑删除/恢复）"""
    suite_obj.deleted_at = deleted_at
    for child in suite_obj.children:
        _set_deleted_at_recursive(child, deleted_at)


def _set_project_id_recursive(suite_obj, project_id):
    """递归设置 project_id（移动节点时使整棵子树归属同一项目）"""
    for child in suite_obj.children:
        child.project_id = project_id
        _set_project_id_recursive(child, project_id)


def _get_suite_parent_path(parent_id):
    """从父节点向上追溯到根，返回文件夹路径字符串，如 全部/文件夹A/子文件夹"""
    if not parent_id:
        return '全部'
    parts = []
    current = TestSuite.query.get(parent_id)
    while current:
        parts.append(current.suite_name or '')
        current = TestSuite.query.get(current.parent_id) if current.parent_id else None
    parts.reverse()
    return '全部/' + '/'.join(p for p in parts if p) if parts else '全部'


@bp.route('/<int:suite_id>', methods=['DELETE'])
@login_required
def delete_test_suite(suite_id):
    """逻辑删除（入回收站）或彻底删除（仅回收站内可彻底删除）。"""
    try:
        from app.models.models import TestSuiteReviewHistory, TestCaseReviewHistory
        from datetime import datetime
        from app.models.models import LOCAL_TIMEZONE

        suite = TestSuite.query.get_or_404(suite_id)
        data = (request.get_json() or {}) if request.is_json else {}

        if data.get('logical'):
            # 逻辑删除：入回收站
            now = datetime.now(LOCAL_TIMEZONE)
            _set_deleted_at_recursive(suite, now)
            db.session.commit()
            return success_response({'message': '已移入回收站'})
        if not data.get('permanent') and suite.deleted_at is None:
            return error_response(400, '请先移入回收站后再彻底删除')
        # 彻底删除（仅回收站内可调用）
        suite_ids = _collect_suite_ids(suite)
        tasks_count = TestTask.query.filter(
            TestTask.suite_id.isnot(None),
            TestTask.suite_id.in_(suite_ids),
        ).count()
        if tasks_count > 0:
            return error_response(
                400,
                "有关联的测试任务引用该用例集，无法彻底删除。请先在测试任务中解除关联后再试。",
            )
        review_count = TestSuiteReviewTask.query.filter(
            TestSuiteReviewTask.suite_id.in_(suite_ids),
        ).count()
        if review_count > 0:
            return error_response(
                400,
                "该用例集存在评审任务，无法彻底删除。请先完成或关闭相关评审后再试。",
            )

        def recursive_delete(suite_obj):
            # 1. 删除子套件（递归）
            for child in suite_obj.children:
                recursive_delete(child)
            
            # 2. 删除关联的评审任务及其详情（先删除，避免测试用例删除后外键问题）
            if hasattr(suite_obj, 'review_tasks'):
                for review_task in suite_obj.review_tasks:
                    # 删除评审任务详情
                    for case_review in review_task.case_reviews:
                        db.session.delete(case_review)
                    # 删除评审任务
                    db.session.delete(review_task)
            
            # 3. 删除关联的测试用例
            for test_case in suite_obj.test_cases:
                db.session.delete(test_case)
            
            # 4. 更新关联的评审历史记录（设置suite_id为NULL）
            review_histories = TestSuiteReviewHistory.query.filter_by(suite_id=suite_obj.id).all()
            for history in review_histories:
                history.suite_id = None
            
            # 5. 删除套件本身
            db.session.delete(suite_obj)

        recursive_delete(suite)
        
        db.session.commit()
        
        return success_response({'message': '测试套件及其关联数据已成功删除'})
    except Exception as e:
        db.session.rollback()
        return error_response(500, f'删除测试套件失败: {str(e)}')


@bp.route('/tree', methods=['GET'])
@login_required
def get_suite_tree():
    """获取完整的测试套件树形结构（仅包含未逻辑删除的套件）"""
    try:
        root_suites = TestSuite.query.filter_by(parent_id=None).filter(
            TestSuite.deleted_at.is_(None)
        ).order_by(TestSuite.sort_order).all()
        
        def build_tree(suite):
            suite_dict = suite.to_dict()
            children = []
            for child in suite.children:
                if child.deleted_at is None:
                    children.append(build_tree(child))
            suite_dict['children'] = children
            return suite_dict
        
        tree_data = [build_tree(suite) for suite in root_suites]
        
        return success_response(tree_data)
    except Exception as e:
        return error_response(500, f'获取套件树结构失败: {str(e)}')


def _suite_not_deleted():
    """未删除（未入回收站）的过滤条件"""
    return TestSuite.deleted_at.is_(None)


@bp.route('/folder-tree', methods=['GET'])
@login_required
def get_folder_tree():
    """获取纯文件夹目录树（不含用例集节点），支持按项目筛选；严格按 project_id 隔离，仅返回该项目的文件夹；排除已逻辑删除的"""
    try:
        project_id = request.args.get('project_id', type=int)
        base = TestSuite.query.filter(_suite_not_deleted())
        root_folders = base.filter_by(parent_id=None, type='folder')
        if project_id is not None:
            root_folders = root_folders.filter_by(project_id=project_id)
        root_folders = root_folders.order_by(TestSuite.sort_order).all()

        def build_folder_tree(folder, filter_project_id=None):
            d = folder.to_dict()
            suite_q = TestSuite.query.filter(
                TestSuite.parent_id == folder.id,
                TestSuite.type == 'suite',
                _suite_not_deleted()
            )
            if filter_project_id is not None:
                suite_q = suite_q.filter_by(project_id=filter_project_id)
            d['suite_count'] = suite_q.count()
            children = [
                c for c in folder.children
                if c.type == 'folder' and c.deleted_at is None
                and (filter_project_id is None or c.project_id == filter_project_id)
            ]
            children.sort(key=lambda x: (x.sort_order or 0, x.id))
            d['children'] = [build_folder_tree(c, filter_project_id) for c in children]
            return d

        tree_data = [build_folder_tree(f, project_id) for f in root_folders]
        root_suite_query = base.filter_by(parent_id=None, type='suite')
        if project_id is not None:
            root_suite_query = root_suite_query.filter_by(project_id=project_id)
        root_suite_count = root_suite_query.count()

        return success_response({
            'tree': tree_data,
            'root_suite_count': root_suite_count,
        })
    except Exception as e:
        return error_response(500, f'获取文件夹树失败: {str(e)}')


@bp.route('/recycled', methods=['GET'])
@login_required
def get_recycled_suites():
    """获取回收站中的用例集列表（仅用例集，不含文件夹），支持分页"""
    try:
        query = TestSuite.query.filter(
            TestSuite.deleted_at.isnot(None),
            TestSuite.type == 'suite'
        ).order_by(TestSuite.deleted_at.desc())
        project_id = request.args.get('project_id', type=int)
        if project_id is not None:
            query = query.filter_by(project_id=project_id)
        page, size = get_pagination_params()
        pagination = query.paginate(page=page, per_page=size, error_out=False)
        out = []
        for s in pagination.items:
            d = s.to_dict()
            d['deleted_at'] = s.deleted_at.isoformat() if s.deleted_at else None
            if s.parent_id:
                parent = TestSuite.query.get(s.parent_id)
                d['parent_folder_name'] = parent.suite_name if parent else None
                d['parent_path'] = _get_suite_parent_path(s.parent_id)
            else:
                d['parent_folder_name'] = None
                d['parent_path'] = '全部'
            out.append(d)
        return success_response({'items': out, 'total': pagination.total})
    except Exception as e:
        return error_response(500, f'获取回收站列表失败: {str(e)}')


@bp.route('/recycled/batch-permanent-delete', methods=['POST'])
@login_required
def batch_permanent_delete_recycled():
    """回收站内批量彻底删除用例集"""
    try:
        from app.models.models import TestSuiteReviewHistory
        data = request.get_json() or {}
        ids = data.get('ids') or []
        if not ids or not isinstance(ids, list):
            return error_response(400, '请提供要删除的 id 列表')
        ids = [int(x) for x in ids if x is not None]
        if not ids:
            return error_response(400, '请提供有效的 id 列表')
        suites = TestSuite.query.filter(TestSuite.id.in_(ids)).all()
        to_delete = []
        for suite in suites:
            if suite.deleted_at is None:
                return error_response(400, f'用例集 id={suite.id} 未在回收站中，无法彻底删除')
            if suite.type != 'suite':
                return error_response(400, f'仅支持彻底删除用例集，id={suite.id} 不是用例集')
            suite_ids = _collect_suite_ids(suite)
            tasks_count = TestTask.query.filter(
                TestTask.suite_id.isnot(None),
                TestTask.suite_id.in_(suite_ids),
            ).count()
            if tasks_count > 0:
                return error_response(
                    400,
                    f'用例集"{suite.suite_name}"有关联的测试任务引用，无法彻底删除。请先在测试任务中解除关联后再试。',
                )
            review_count = TestSuiteReviewTask.query.filter(
                TestSuiteReviewTask.suite_id.in_(suite_ids),
            ).count()
            if review_count > 0:
                return error_response(
                    400,
                    f'用例集"{suite.suite_name}"存在评审任务，无法彻底删除。请先完成或关闭相关评审后再试。',
                )
            to_delete.append(suite)

        def recursive_delete(suite_obj):
            for child in suite_obj.children:
                recursive_delete(child)
            if hasattr(suite_obj, 'review_tasks'):
                for review_task in suite_obj.review_tasks:
                    for case_review in review_task.case_reviews:
                        db.session.delete(case_review)
                    db.session.delete(review_task)
            for test_case in suite_obj.test_cases:
                db.session.delete(test_case)
            review_histories = TestSuiteReviewHistory.query.filter_by(suite_id=suite_obj.id).all()
            for history in review_histories:
                history.suite_id = None
            db.session.delete(suite_obj)

        for suite in to_delete:
            recursive_delete(suite)
        db.session.commit()
        return success_response({'message': f'已彻底删除 {len(to_delete)} 项'})
    except Exception as e:
        db.session.rollback()
        return error_response(500, f'批量彻底删除失败: {str(e)}')


@bp.route('/recycled/<int:suite_id>/restore', methods=['POST'])
@login_required
def restore_recycled_suite(suite_id):
    """从回收站恢复用例集（逻辑删除撤销）。若父文件夹已被删除则恢复到根目录。"""
    try:
        suite = TestSuite.query.get_or_404(suite_id)
        if suite.deleted_at is None:
            return error_response(400, '该记录未在回收站中')
        if suite.type != 'suite':
            return error_response(400, '仅支持恢复用例集')
        parent = TestSuite.query.get(suite.parent_id) if suite.parent_id else None
        if suite.parent_id and (not parent or parent.deleted_at is not None):
            suite.parent_id = None
        _set_deleted_at_recursive(suite, None)
        db.session.commit()
        return success_response(suite.to_dict())
    except Exception as e:
        db.session.rollback()
        return error_response(500, f'恢复失败: {str(e)}')


@bp.route('/<int:folder_id>/case-sets', methods=['GET'])
@login_required
def get_case_sets(folder_id):
    """获取指定文件夹下的用例集列表（folder_id=0 表示根级目录）；排除已逻辑删除的"""
    try:
        query = TestSuite.query.filter(_suite_not_deleted())
        if folder_id == 0:
            query = query.filter_by(parent_id=None, type='suite')
        else:
            folder = TestSuite.query.get_or_404(folder_id)
            if folder.type != 'folder' or folder.deleted_at is not None:
                return error_response(400, '该节点不是文件夹或已删除')
            query = query.filter_by(parent_id=folder_id, type='suite')

        project_id = request.args.get('project_id', type=int)
        if project_id is not None:
            query = query.filter_by(project_id=project_id)

        page, size = get_pagination_params()

        search = request.args.get('search', '').strip()
        if search:
            query = query.filter(TestSuite.suite_name.like(f'%{search}%'))

        review_status = request.args.get('review_status')
        if review_status:
            query = query.filter_by(review_status=review_status)

        pagination = query.order_by(TestSuite.sort_order).paginate(
            page=page, per_page=size, error_out=False
        )
        items = [s.to_dict() for s in pagination.items]
        # 为每条用例集附加当前最新评审任务的发起人/评审人，供前端悬浮文案区分角色
        suite_ids = [s.id for s in pagination.items]
        if suite_ids:
            latest_tasks = (
                TestSuiteReviewTask.query.filter(TestSuiteReviewTask.suite_id.in_(suite_ids))
                .order_by(TestSuiteReviewTask.created_at.desc())
                .all()
            )
            latest_by_suite = {}
            for t in latest_tasks:
                if t.suite_id not in latest_by_suite:
                    latest_by_suite[t.suite_id] = t
            for it in items:
                t = latest_by_suite.get(it['id'])
                it['review_initiator_id'] = t.initiator_id if t else None
                it['review_reviewer_id'] = t.reviewer_id if t else None
                if t and t.status in ('pending', 'in_review'):
                    it['review_status'] = t.status
        return success_response({
            'items': items,
            'total': pagination.total,
            'page': page,
            'per_page': size,
            'pages': pagination.pages,
        })
    except Exception as e:
        return error_response(500, f'获取用例集列表失败: {str(e)}')


@bp.route('/<int:suite_id>/move', methods=['POST'])
@login_required
def move_suite(suite_id):
    """移动用例集到另一个文件夹"""
    try:
        suite = TestSuite.query.get_or_404(suite_id)
        data = request.get_json()
        target_folder_id = data.get('target_folder_id')

        if target_folder_id is not None:
            target = TestSuite.query.get(target_folder_id)
            if not target or target.type != 'folder':
                return error_response(400, '目标必须是文件夹')
            if target.deleted_at is not None:
                return error_response(400, '目标文件夹已被删除，无法移动到此处')
            new_project_id = target.project_id
        else:
            new_project_id = None

        suite.parent_id = target_folder_id
        # 同步被移动节点及其所有子节点的 project_id
        suite.project_id = new_project_id
        _set_project_id_recursive(suite, new_project_id)
        max_order = db.session.query(db.func.max(TestSuite.sort_order)).filter_by(
            parent_id=target_folder_id
        ).scalar() or 0
        suite.sort_order = max_order + 1
        db.session.commit()
        return success_response(suite.to_dict())
    except Exception as e:
        db.session.rollback()
        return error_response(500, f'移动失败: {str(e)}')


@bp.route('/<int:suite_id>/copy', methods=['POST'])
@login_required
def copy_suite(suite_id):
    """复制用例集（含脑图数据和解析出的 test_cases）"""
    try:
        import json as _json
        source = TestSuite.query.get_or_404(suite_id)
        if source.type != 'suite':
            return error_response(400, '只能复制用例集')

        data = request.get_json() or {}
        target_folder_id = data.get('target_folder_id', source.parent_id)

        # project_id 应从目标文件夹继承，避免跨项目隔离被破坏
        if target_folder_id is not None:
            target_folder = TestSuite.query.get(target_folder_id)
            if not target_folder or target_folder.type != 'folder':
                return error_response(400, '目标必须是文件夹')
            if target_folder.deleted_at is not None:
                return error_response(400, '目标文件夹已在回收站中')
            target_project_id = target_folder.project_id
        else:
            target_project_id = source.project_id

        max_order = db.session.query(db.func.max(TestSuite.sort_order)).filter_by(
            parent_id=target_folder_id
        ).scalar() or 0

        copy_name = f'{source.suite_name} (副本)'
        if len(copy_name) > 30:
            copy_name = (source.suite_name[:25] or '副本') + ' (副本)'
            copy_name = copy_name[:30]
        new_suite = TestSuite(
            suite_name=copy_name,
            description=source.description,
            parent_id=target_folder_id,
            status=source.status,
            type='suite',
            creator_id=current_user.id,
            project_id=target_project_id,
            version_requirement_id=source.version_requirement_id,
            iteration_id=source.iteration_id,
            sort_order=max_order + 1,
            case_mindmap_data=source.case_mindmap_data,
            case_count=source.case_count,
            case_edit_status='drafting',
            review_status='not_reviewed',
        )
        db.session.add(new_suite)
        db.session.flush()

        old_cases = TestCase.query.filter_by(suite_id=source.id).all()
        for oc in old_cases:
            nc = TestCase(
                case_name=oc.case_name,
                priority=oc.priority,
                test_data=oc.test_data,
                preconditions=oc.preconditions,
                steps=oc.steps,
                expected_result=oc.expected_result,
                group_path=oc.group_path,
                tags=oc.tags,
                markers=oc.markers,
                mindmap_node_id=oc.mindmap_node_id,
                suite_id=new_suite.id,
                project_id=new_suite.project_id,
                version_requirement_id=new_suite.version_requirement_id,
                iteration_id=new_suite.iteration_id,
                creator_id=current_user.id,
                status='',
            )
            db.session.add(nc)

        db.session.commit()
        return success_response(new_suite.to_dict(), "复制成功")
    except Exception as e:
        db.session.rollback()
        return error_response(500, f'复制失败: {str(e)}')


@bp.route('/import', methods=['POST'])
@login_required
def import_suite():
    """导入用例集（支持 JSON / Excel / CSV）"""
    import json as _json, uuid as _uuid, io, csv
    try:
        file = request.files.get('file')
        if not file or not file.filename:
            return error_response(400, '请选择文件')

        parent_id = request.form.get('parent_id', type=int) or None
        project_id = request.form.get('project_id', type=int) or None
        ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''

        cases_data = []

        if ext == 'json':
            raw = _json.load(file)
            if isinstance(raw, dict):
                root = raw.get('root') or raw
                suite_name = root.get('text', root.get('data', {}).get('text', file.filename.rsplit('.', 1)[0]))
                mindmap_data = raw
            else:
                suite_name = file.filename.rsplit('.', 1)[0]
                mindmap_data = None
                cases_data = raw if isinstance(raw, list) else []
        elif ext in ('xlsx', 'xls'):
            try:
                import openpyxl
            except ImportError:
                return error_response(400, '服务端缺少 openpyxl 依赖，无法解析 Excel')
            wb = openpyxl.load_workbook(io.BytesIO(file.read()), data_only=True)
            ws = wb.active
            rows = list(ws.iter_rows(values_only=True))
            if not rows:
                return error_response(400, 'Excel 为空')
            headers = [str(h or '').strip().lower() for h in rows[0]]
            for row in rows[1:]:
                d = dict(zip(headers, row))
                cases_data.append({
                    'case_name': d.get('用例名称') or d.get('case_name') or d.get('name', ''),
                    'priority': d.get('优先级') or d.get('priority', 'P1'),
                    'preconditions': d.get('前置条件') or d.get('preconditions', ''),
                    'steps': d.get('操作步骤') or d.get('steps', ''),
                    'expected_result': d.get('预期结果') or d.get('expected_result', ''),
                    'test_data': d.get('测试数据') or d.get('test_data', ''),
                })
            suite_name = file.filename.rsplit('.', 1)[0]
            mindmap_data = None
        elif ext == 'csv':
            text = file.read().decode('utf-8-sig')
            reader = csv.DictReader(io.StringIO(text))
            for row in reader:
                cases_data.append({
                    'case_name': row.get('用例名称') or row.get('case_name') or row.get('name', ''),
                    'priority': row.get('优先级') or row.get('priority', 'P1'),
                    'preconditions': row.get('前置条件') or row.get('preconditions', ''),
                    'steps': row.get('操作步骤') or row.get('steps', ''),
                    'expected_result': row.get('预期结果') or row.get('expected_result', ''),
                    'test_data': row.get('测试数据') or row.get('test_data', ''),
                })
            suite_name = file.filename.rsplit('.', 1)[0]
            mindmap_data = None
        else:
            return error_response(400, '不支持的文件格式，请上传 JSON / Excel / CSV')

        max_order = db.session.query(db.func.max(TestSuite.sort_order)).filter_by(parent_id=parent_id).scalar() or 0
        new_suite = TestSuite(
            suite_name=suite_name[:30],
            description=f'由文件 {file.filename} 导入',
            parent_id=parent_id,
            type='suite',
            status='active',
            creator_id=current_user.id,
            project_id=project_id,
            sort_order=max_order + 1,
            review_status='not_reviewed',
        )
        db.session.add(new_suite)
        db.session.flush()

        case_count = 0
        if mindmap_data:
            new_suite.case_mindmap_data = _json.dumps(mindmap_data, ensure_ascii=False)
        if cases_data:
            from datetime import datetime, timezone, timedelta
            _now = datetime.now(timezone(timedelta(hours=8)))
            children_nodes = []
            for idx, c in enumerate(cases_data):
                cname = str(c.get('case_name', '')).strip()
                if not cname:
                    continue
                case_count += 1
                case_number = f'TC-{new_suite.id}-{case_count:03d}'
                tc = TestCase(
                    case_number=case_number,
                    case_name=cname,
                    priority=c.get('priority', 'P1'),
                    preconditions=c.get('preconditions', ''),
                    steps=c.get('steps', ''),
                    expected_result=c.get('expected_result', ''),
                    test_data=c.get('test_data', ''),
                    suite_id=new_suite.id,
                    project_id=project_id,
                    creator_id=current_user.id,
                    assignee_id=current_user.id,
                )
                db.session.add(tc)
                nid = str(_uuid.uuid4())[:8]
                chain = []
                if c.get('preconditions'):
                    chain.append({'id': f'pc-{nid}', 'text': c['preconditions'], 'attribute': 'precondition', 'children': []})
                if c.get('steps'):
                    step_node = {'id': f'st-{nid}', 'text': c['steps'], 'attribute': 'step', 'children': []}
                    if c.get('expected_result'):
                        step_node['children'].append({'id': f'er-{nid}', 'text': c['expected_result'], 'attribute': 'expected_result'})
                    if chain:
                        chain[-1]['children'] = [step_node]
                    else:
                        chain.append(step_node)
                elif c.get('expected_result'):
                    er_node = {'id': f'er-{nid}', 'text': c['expected_result'], 'attribute': 'expected_result'}
                    if chain:
                        chain[-1]['children'] = [er_node]
                    else:
                        chain.append(er_node)
                td_chain = chain
                if c.get('test_data'):
                    td_chain = [{'id': f'td-{nid}', 'text': c['test_data'], 'attribute': 'test_data', 'children': chain}]
                case_node = {'id': f'ct-{nid}', 'text': cname, 'attribute': 'case_title', 'priority': c.get('priority', 'P1'), 'children': td_chain}
                children_nodes.append(case_node)
            if children_nodes and not mindmap_data:
                mm = {'data': {'text': suite_name[:30]}, 'children': [{'data': n} for n in children_nodes]}
                new_suite.case_mindmap_data = _json.dumps(mm, ensure_ascii=False)

        new_suite.case_count = case_count
        db.session.commit()
        return success_response({'message': f'导入成功，共 {case_count} 条用例', 'suite_id': new_suite.id})
    except Exception as e:
        db.session.rollback()
        return error_response(500, f'导入失败: {str(e)}')


@bp.route('/<int:suite_id>/tree', methods=['GET'])
@login_required
def get_suite_tree_by_id(suite_id):
    """获取指定测试套件的树形结构"""
    try:
        suite = TestSuite.query.get_or_404(suite_id)
        
        # 递归构建树
        def build_tree(suite):
            suite_dict = suite.to_dict()
            children = []
            for child in suite.children:
                children.append(build_tree(child))
            suite_dict['children'] = children
            return suite_dict
        
        tree_data = build_tree(suite)
        
        return success_response([tree_data])
    except Exception as e:
        return error_response(500, f'获取套件树结构失败: {str(e)}')


@bp.route('/options', methods=['GET'])
@login_required
def get_suite_options():
    """获取测试套件选项列表，用于下拉选择"""
    try:
        def build_options(suite, prefix=''):
            result = [{
                'value': suite.id,
                'label': f'{prefix}{suite.suite_name}'
            }]
            for child in suite.children:
                result.extend(build_options(child, prefix + '  └ '))
            return result
        
        options = []
        for root_suite in TestSuite.query.filter_by(parent_id=None).order_by(TestSuite.sort_order).all():
            options.extend(build_options(root_suite))
        
        return success_response(options)
    except Exception as e:
        return error_response(500, f'获取套件选项失败: {str(e)}')


@bp.route('/<int:suite_id>/test-cases', methods=['GET'])
@login_required
def get_suite_test_cases(suite_id):
    """获取测试套件中的测试用例"""
    try:
        from app.models.models import TestCase
        from app.utils.helpers import get_pagination_params
        
        page, size = get_pagination_params()
        query = TestCase.query.filter_by(suite_id=suite_id)
        pagination = query.paginate(
            page=page, per_page=size, error_out=False
        )
        
        test_cases = [test_case.to_dict() for test_case in pagination.items]
        
        return success_response({
            'items': test_cases,
            'total': pagination.total,
            'page': page,
            'per_page': size
        })
    except Exception as e:
        return error_response(500, f'获取套件测试用例失败: {str(e)}')