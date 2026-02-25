from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.exc import OperationalError

from app.models.models import (
    TestTask, db, TestSuite, TestCase, Device, TestCaseExecution, UserSetting,
    TaskCaseSnapshot, TaskFolder, TEST_TASK_STATUS, TEST_EXECUTION_STATUS
)
from app.utils.helpers import (
    success_response, error_response, get_pagination_params, log_user_action,
    validate_json_data
)

# 创建Blueprint
bp = Blueprint('test_tasks', __name__, url_prefix='/api/test-tasks')

# 本地时区（与 models 一致）
_LOCAL_TZ = timezone(timedelta(hours=8))


def _save_task_case_snapshots(test_task, suite, test_cases):
    """为测试任务写入用例集名称与用例内容快照，用于历史追溯。"""
    now = datetime.now(_LOCAL_TZ)
    test_task.suite_name_snapshot = suite.suite_name if suite else None
    test_task.case_snapshot_at = now
    # 删除该任务已有快照
    TaskCaseSnapshot.query.filter_by(task_id=test_task.id).delete()
    for case in test_cases:
        snap = TaskCaseSnapshot(
            task_id=test_task.id,
            case_id=case.id,
            case_number=case.case_number,
            case_name=case.case_name,
            priority=case.priority,
            test_data=case.test_data,
            preconditions=case.preconditions,
            steps=case.steps,
            expected_result=case.expected_result,
            actual_result=case.actual_result,
        )
        db.session.add(snap)


# ---------- 任务文件夹（按任务类型分开的目录） ----------

TASK_FOLDER_MAX_DEPTH = 3  # 任务目录最多 3 层

def _get_folder_depth(folder_id, task_type):
    """计算文件夹深度，根级为 1，子级依次为 2、3。"""
    if folder_id is None:
        return 0
    f = TaskFolder.query.filter_by(id=folder_id, task_type=task_type).first()
    if not f:
        return 0
    depth = 1
    while f.parent_id:
        depth += 1
        f = TaskFolder.query.filter_by(id=f.parent_id, task_type=task_type).first()
        if not f:
            break
    return depth

def _is_descendant_of(folder_id, ancestor_id, task_type):
    """判断 folder_id 是否为 ancestor_id 的子孙（含子节点），用于防止移动成环。"""
    if not folder_id or not ancestor_id or folder_id == ancestor_id:
        return folder_id == ancestor_id
    f = TaskFolder.query.filter_by(id=folder_id, task_type=task_type).first()
    while f and f.parent_id:
        if f.parent_id == ancestor_id:
            return True
        f = TaskFolder.query.filter_by(id=f.parent_id, task_type=task_type).first()
    return False

def _apply_folder_order(folder):
    """将当前文件夹视为“拖到 sort_order 位置”，同层兄弟按新顺序重排并提交。
    避免仅按 (sort_order, id) 重排时，拖到某条“上方”导致 sort_order 相同、id 导致顺序还原。"""
    siblings = TaskFolder.query.filter_by(
        task_type=folder.task_type, parent_id=folder.parent_id
    ).all()
    if not siblings:
        return
    # 按当前 (sort_order, id) 得到顺序，再从中移除被移动项，插入到目标下标
    ordered = sorted(siblings, key=lambda f: (f.sort_order, f.id))
    ordered = [f for f in ordered if f.id != folder.id]
    idx = max(0, min(folder.sort_order, len(ordered)))
    ordered.insert(idx, folder)
    for i, f in enumerate(ordered):
        f.sort_order = i
    db.session.commit()


def _task_folder_tree(folders):
    """将扁平文件夹列表转为树形，children 按 sort_order 排序，节点带 depth（1-based）。"""
    by_id = {f.id: {**f.to_dict(), 'children': []} for f in folders}
    roots = []
    for f in folders:
        node = by_id[f.id]
        if f.parent_id is None:
            roots.append(node)
        else:
            parent = by_id.get(f.parent_id)
            if parent:
                parent['children'].append(node)
            else:
                roots.append(node)
    def set_depth(nodes, d):
        for n in nodes:
            n['depth'] = d
            set_depth(n.get('children') or [], d + 1)
    set_depth(roots, 1)
    for node in roots:
        node['children'].sort(key=lambda x: (x.get('sort_order', 0), x['id']))
    roots.sort(key=lambda x: (x.get('sort_order', 0), x['id']))
    return roots


@bp.route('/task-folders', methods=['GET'])
@login_required
def get_task_folders():
    """获取任务文件夹树，按任务类型过滤"""
    task_type = request.args.get('task_type', '').strip()
    if task_type not in ('test_case', 'device_script'):
        return error_response(400, '请指定 task_type: test_case 或 device_script')
    folders = TaskFolder.query.filter_by(task_type=task_type).order_by(TaskFolder.sort_order, TaskFolder.id).all()
    tree = _task_folder_tree(folders)
    return success_response({'folders': tree})


@bp.route('/task-folders', methods=['POST'])
@login_required
@validate_json_data(['name', 'task_type'])
def create_task_folder():
    """创建任务文件夹"""
    data = request.get_json()
    name = (data.get('name') or '').strip()
    if not name:
        return error_response(400, '文件夹名称不能为空')
    task_type = data.get('task_type')
    if task_type not in ('test_case', 'device_script'):
        return error_response(400, 'task_type 必须为 test_case 或 device_script')
    parent_id = data.get('parent_id')
    if parent_id is not None:
        parent = TaskFolder.query.filter_by(id=parent_id, task_type=task_type).first()
        if not parent:
            return error_response(400, '父文件夹不存在或类型不匹配')
        parent_depth = _get_folder_depth(parent_id, task_type)
        if parent_depth >= TASK_FOLDER_MAX_DEPTH:
            return error_response(400, f'任务目录最多 {TASK_FOLDER_MAX_DEPTH} 层，该位置已达最大层级')
    sort_order = data.get('sort_order', 0)
    folder = TaskFolder(name=name, parent_id=parent_id, task_type=task_type, sort_order=sort_order)
    db.session.add(folder)
    db.session.commit()
    log_user_action("创建任务文件夹", f"名称: {name}, 类型: {task_type}")
    return success_response({'folder': folder.to_dict()}, '创建成功')


@bp.route('/task-folders/<int:folder_id>', methods=['PATCH'])
@login_required
def update_task_folder(folder_id):
    """更新任务文件夹（重命名、移动、排序）"""
    folder = TaskFolder.query.get_or_404(folder_id)
    data = request.get_json() or {}
    if 'name' in data:
        name = (data.get('name') or '').strip()
        if name:
            folder.name = name
    if 'parent_id' in data:
        new_parent_id = data['parent_id'] if data['parent_id'] else None
        if new_parent_id is not None:
            if new_parent_id == folder_id:
                return error_response(400, '不能将文件夹移动到自身下')
            if _is_descendant_of(new_parent_id, folder_id, folder.task_type):
                return error_response(400, '不能将文件夹移动到其子级下')
            parent_depth = _get_folder_depth(new_parent_id, folder.task_type)
            if parent_depth >= TASK_FOLDER_MAX_DEPTH:
                return error_response(400, f'任务目录最多 {TASK_FOLDER_MAX_DEPTH} 层，该位置已达最大层级')
        folder.parent_id = new_parent_id
    if 'sort_order' in data:
        folder.sort_order = data['sort_order']
    order_updated = 'parent_id' in data or 'sort_order' in data
    if order_updated:
        _apply_folder_order(folder)
    else:
        db.session.commit()
    return success_response({'folder': folder.to_dict()}, '更新成功')


@bp.route('/task-folders/<int:folder_id>', methods=['DELETE'])
@login_required
def delete_task_folder(folder_id):
    """删除任务文件夹（子文件夹由 DB 外键 CASCADE 递归删除，该文件夹下任务 folder_id 置空）"""
    folder = TaskFolder.query.get_or_404(folder_id)
    TestTask.query.filter_by(folder_id=folder_id).update({'folder_id': None})
    db.session.commit()
    db.session.delete(folder)
    db.session.commit()
    log_user_action("删除任务文件夹", f"ID: {folder_id}, 名称: {folder.name}")
    return success_response(message='删除成功')


# ---------- 测试任务列表与详情 ----------

@bp.route('', methods=['GET'])
@login_required
def get_test_tasks():
    """获取测试任务列表"""
    page, size = get_pagination_params()
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '').strip()
    priority = request.args.get('priority', '').strip()
    task_type = request.args.get('task_type', '').strip()
    project_id = request.args.get('project_id', '').strip()
    iteration_id = request.args.get('iteration_id', '').strip()
    executor_id = request.args.get('executor_id', '').strip()
    folder_id = request.args.get('folder_id', '').strip()  # 可选，任务文件夹ID；空或未传则不过滤

    # 构建查询
    query = TestTask.query

    # 文件夹过滤（传 "null" 或 0 表示未归类，传正整数表示该文件夹下）
    if folder_id not in ('', None):
        if folder_id == 'null' or folder_id == '0':
            query = query.filter(TestTask.folder_id.is_(None))
        else:
            try:
                fid = int(folder_id)
                query = query.filter(TestTask.folder_id == fid)
            except ValueError:
                pass

    # 搜索过滤
    if search:
        query = query.filter(
            TestTask.task_name.contains(search) |
            TestTask.task_description.contains(search)
        )
    
    # 状态过滤
    if status:
        query = query.filter(TestTask.status == status)
    
    # 优先级过滤
    if priority:
        query = query.filter(TestTask.priority == priority)
    
    # 任务类型过滤
    if task_type:
        query = query.filter(TestTask.task_type == task_type)
    
    # 项目过滤
    if project_id:
        query = query.filter(TestTask.project_id == int(project_id))
    
    # 迭代过滤
    if iteration_id:
        query = query.filter(TestTask.iteration_id == int(iteration_id))
    
    # 负责人过滤
    if executor_id:
        query = query.filter(TestTask.executor_id == int(executor_id))
    
    # 预加载关联，避免 to_dict() 时 N+1 查询（含 case_snapshots、case_executions 用于统计）
    query = query.options(
        joinedload(TestTask.project),
        joinedload(TestTask.iteration),
        joinedload(TestTask.creator),
        joinedload(TestTask.executor),
        joinedload(TestTask.suite).selectinload(TestSuite.test_cases),
        joinedload(TestTask.version_requirement),
        joinedload(TestTask.folder),
        selectinload(TestTask.devices),
        selectinload(TestTask.test_cases),
        selectinload(TestTask.case_snapshots),
        selectinload(TestTask.case_executions),
    )
    
    try:
        pagination = query.order_by(TestTask.created_at.desc()).paginate(
            page=page, per_page=size, error_out=False
        )
        test_tasks = []
        for test_task in pagination.items:
            try:
                test_tasks.append(test_task.to_dict())
            except Exception as e:
                # 单条 to_dict 失败不拖垮整列表，记录并跳过或返回最小结构
                try:
                    test_tasks.append({
                        'id': test_task.id,
                        'task_name': getattr(test_task, 'task_name', ''),
                        'task_type': getattr(test_task, 'task_type', 'test_case'),
                        'status': getattr(test_task, 'status', 'pending'),
                        'priority': getattr(test_task, 'priority', 'medium'),
                        'folder_id': getattr(test_task, 'folder_id', None),
                        'folder_name': None,
                        'statistics': {'pass_rate': 0, 'total_cases': 0, 'not_executed': 0},
                    })
                except Exception:
                    pass
    except OperationalError as e:
        err_msg = str(e.orig) if getattr(e, 'orig', None) else str(e)
        if 'folder_id' in err_msg or 'Unknown column' in err_msg or 'task_folders' in err_msg:
            return error_response(
                500,
                "数据库表结构缺少任务文件夹相关字段。请执行 database/03_create_tables.py 同步表结构后重试。"
            )
        return error_response(500, f"数据库错误: {err_msg}")
    except Exception as e:
        return error_response(500, f"获取任务列表失败: {type(e).__name__} - {str(e)}")
    
    return success_response({
        'test_tasks': test_tasks,
        'pagination': {
            'page': page,
            'size': size,
            'total': pagination.total,
            'pages': pagination.pages
        }
    })


@bp.route('/<int:task_id>', methods=['GET'])
@login_required
def get_test_task(task_id):
    """获取测试任务详情"""
    test_task = TestTask.query.options(
        selectinload(TestTask.case_snapshots),
    ).get_or_404(task_id)
    return success_response({
        'test_task': test_task.to_dict()
    })


@bp.route('', methods=['POST'])
@login_required
@validate_json_data(['task_name'])
def create_test_task():
    """创建测试任务"""
    data = request.get_json()
    

    
    # 兼容前端字段：test_cases（套件ID）映射到 suite_id
    if 'test_cases' in data and not data.get('suite_id'):
        data['suite_id'] = data['test_cases']

    
    # 验证套件是否存在
    if data.get('suite_id'):
        suite = TestSuite.query.get(data['suite_id'])
        if not suite:

            return error_response(400, "指定的测试套件不存在")

    
    folder_id = data.get('folder_id')
    if folder_id is not None and folder_id != '':
        folder = TaskFolder.query.get(folder_id)
        if folder and folder.task_type == data.get('task_type', 'test_case'):
            pass  # 使用该 folder_id
        else:
            folder_id = None
    else:
        folder_id = None

    test_task = TestTask(
        task_name=data['task_name'],
        task_description=data.get('task_description', ''),
        folder_id=folder_id,
        priority=data.get('priority', 'medium'),
        status=data.get('status', 'pending'),
        task_type=data.get('task_type', 'test_case'),
        creator_id=current_user.id,
        executor_id=data.get('executor_id') if data.get('executor_id') and data.get('executor_id') != '' else None,
        suite_id=data.get('suite_id') if data.get('suite_id') and data.get('suite_id') != '' else None,
        version_requirement_id=data.get('version_requirement_id') if data.get('version_requirement_id') and data.get('version_requirement_id') != '' else None,
        documentation_url=data.get('documentation_url'),
        version_info=data.get('version_info'),
        project_id=data.get('project_id') if data.get('project_id') and data.get('project_id') != '' else None,
        iteration_id=data.get('iteration_id') if data.get('iteration_id') and data.get('iteration_id') != '' else None,
        # 设备脚本任务专用字段
        script_file=data.get('script_file'),
        file_path=data.get('file_path'),
        file_hash=data.get('file_hash'),
        command=data.get('command')
    )
    

    
    # 处理计划时间范围
    scheduled_time = data.get('scheduled_time')
    if scheduled_time:
        if isinstance(scheduled_time, list) and len(scheduled_time) == 2:
            # 前端传递的是时间范围数组 [开始时间, 结束时间]
            test_task.scheduled_time = scheduled_time[0]
            test_task.scheduled_end_time = scheduled_time[1]
        else:
            # 兼容单个时间点
            test_task.scheduled_time = scheduled_time
    
    try:
        # 根据任务类型处理关联
        task_type = data.get('task_type', 'test_case')

        
        # 处理测试用例关联（仅测试用例任务）
        # 注意：前端传递的 test_cases 字段是套件ID，不是测试用例ID列表
        # 如果需要关联测试用例，应该通过 suite_id 来获取套件中的测试用例
        if task_type == 'test_case' and data.get('suite_id'):
            # 如果指定了测试套件，获取该套件中的所有测试用例
            suite = TestSuite.query.get(data['suite_id'])
            if suite:
                test_cases = suite.test_cases
                test_task.test_cases = test_cases
            else:
                test_task.test_cases = []
            suite_for_snapshot = suite if suite else None
            cases_for_snapshot = list(test_task.test_cases) if test_task.test_cases else []
        else:
            test_task.test_cases = []
            suite_for_snapshot = None
            cases_for_snapshot = []

        # 处理设备关联（仅设备脚本任务）
        if task_type == 'device_script':
            if data.get('devices'):
                devices = Device.query.filter(Device.device_id.in_(data['devices'])).all()
                test_task.devices = devices
            else:
                test_task.devices = []

        db.session.add(test_task)
        db.session.flush()
        # 测试用例任务：写入用例集名称与用例内容快照，支持历史追溯
        if task_type == 'test_case' and (suite_for_snapshot or cases_for_snapshot):
            _save_task_case_snapshots(test_task, suite_for_snapshot, cases_for_snapshot)
        db.session.commit()

        
        log_user_action("创建测试任务", f"任务名称: {test_task.task_name}")
        

        return success_response({
            'test_task': test_task.to_dict()
        }, "测试任务创建成功")
        
    except Exception as e:
        db.session.rollback()
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] 创建测试任务失败 - 错误详情: {error_details}")
        print(f"[ERROR] 请求数据: {data}")
        return error_response(500, "测试任务创建失败，请稍后重试")


@bp.route('/<int:task_id>', methods=['PUT'])
@login_required
def update_test_task(task_id):
    """更新测试任务"""
    test_task = TestTask.query.get_or_404(task_id)
    data = request.get_json()
    
    # 兼容前端字段：test_cases（套件ID）映射到 suite_id
    if 'test_cases' in data and not data.get('suite_id'):
        data['suite_id'] = data['test_cases']
    
    # 更新字段
    if 'task_name' in data:
        test_task.task_name = data['task_name']
    
    if 'task_description' in data:
        test_task.task_description = data['task_description']
    
    if 'priority' in data:
        test_task.priority = data['priority']
    
    if 'status' in data:
        test_task.status = data['status']
        # 如果任务状态变为运行中，记录开始时间
        if data['status'] == 'running' and test_task.started_time is None:
            test_task.started_time = datetime.now(timezone(timedelta(hours=8)))
        # 如果任务状态变为已完成，记录结束时间
        elif data['status'] == 'completed' and test_task.completed_time is None:
            test_task.completed_time = datetime.now(timezone(timedelta(hours=8)))
    
    if 'result' in data:
        test_task.result = data['result']
    
    if 'task_type' in data:
        test_task.task_type = data['task_type']
    
    # 更新任务相关信息
    # 关联用例集在创建任务时固定，更新任务时不允许修改/删除
    if 'suite_id' in data and test_task.task_type == 'test_case':
        pass  # 忽略 suite_id 更新，保持创建时的关联
    elif 'suite_id' in data:
        suite_id = data['suite_id']
        if suite_id is not None and suite_id != '':
            suite = TestSuite.query.get(suite_id)
            if not suite:
                return error_response(400, "指定的测试套件不存在")
            test_task.suite_id = suite_id
        else:
            test_task.suite_id = None
    
    if 'version_requirement_id' in data:
        test_task.version_requirement_id = data['version_requirement_id']
    
    if 'documentation_url' in data:
        test_task.documentation_url = data['documentation_url']
    
    if 'version_info' in data:
        test_task.version_info = data['version_info']
    
    # 处理计划时间范围
    if 'scheduled_time' in data:
        scheduled_time = data['scheduled_time']
        if scheduled_time:
            if isinstance(scheduled_time, list) and len(scheduled_time) == 2:
                # 前端传递的是时间范围数组 [开始时间, 结束时间]
                test_task.scheduled_time = scheduled_time[0]
                test_task.scheduled_end_time = scheduled_time[1]
            else:
                # 兼容单个时间点
                test_task.scheduled_time = scheduled_time
        else:
            test_task.scheduled_time = None
            test_task.scheduled_end_time = None
    
    if 'project_id' in data:
        test_task.project_id = data['project_id']
    
    if 'iteration_id' in data:
        test_task.iteration_id = data['iteration_id']
    
    if 'executor_id' in data:
        test_task.executor_id = data['executor_id']

    if 'folder_id' in data:
        fid = data['folder_id']
        if fid and TaskFolder.query.get(fid) and TaskFolder.query.get(fid).task_type == test_task.task_type:
            test_task.folder_id = fid
        else:
            test_task.folder_id = None

    # 设备脚本任务专用字段更新
    if 'script_file' in data:
        test_task.script_file = data['script_file']
    
    if 'file_path' in data:
        test_task.file_path = data['file_path']
    
    if 'file_hash' in data:
        test_task.file_hash = data['file_hash']
    
    if 'command' in data:
        test_task.command = data['command']
    
    # 根据任务类型处理关联
    current_task_type = test_task.task_type
    new_task_type = data.get('task_type', current_task_type)

    # 处理测试用例关联（仅测试用例任务）；已存在的测试用例任务不修改关联与快照
    if new_task_type == 'test_case':
        if test_task.id and test_task.task_type == 'test_case':
            # 更新时保持原有 suite_id 与 test_cases，不根据 data 变更
            suite_for_snapshot = None
            cases_for_snapshot = []
        elif data.get('suite_id'):
            suite = TestSuite.query.get(data['suite_id'])
            if suite:
                test_task.test_cases = suite.test_cases
            else:
                test_task.test_cases = []
            suite_for_snapshot = suite if suite else None
            cases_for_snapshot = list(test_task.test_cases) if test_task.test_cases else []
        else:
            test_task.test_cases = []
            suite_for_snapshot = None
            cases_for_snapshot = []
    else:
        test_task.test_cases = []
        suite_for_snapshot = None
        cases_for_snapshot = []

    # 处理设备关联（仅设备脚本任务）
    if new_task_type == 'device_script':
        if 'devices' in data:
            devices = Device.query.filter(Device.device_id.in_(data['devices'])).all()
            test_task.devices = devices
        else:
            test_task.devices = []
    elif new_task_type != 'device_script':
        test_task.devices = []

    if new_task_type != current_task_type:
        test_task.task_type = new_task_type

    try:
        # 快照仅在创建任务时写入，更新任务时不覆盖，避免冗余并保持“创建时状态”的历史语义
        # 若任务类型改为非测试用例任务，则清除快照
        if new_task_type != 'test_case':
            TaskCaseSnapshot.query.filter_by(task_id=test_task.id).delete()
            test_task.suite_name_snapshot = None
            test_task.case_snapshot_at = None
        db.session.commit()
        
        log_user_action("更新测试任务", f"任务ID: {task_id}")
        
        return success_response({
            'test_task': test_task.to_dict()
        }, "测试任务更新成功")
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, "测试任务更新失败，请稍后重试")


@bp.route('/<int:task_id>', methods=['DELETE'])
@login_required
def delete_test_task(task_id):
    """删除测试任务"""
    test_task = TestTask.query.get_or_404(task_id)
    
    try:
        db.session.delete(test_task)
        db.session.commit()
        
        log_user_action("删除测试任务", f"任务名称: {test_task.task_name}")
        
        return success_response(message="测试任务删除成功")
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, "测试任务删除失败，请稍后重试")


@bp.route('/<int:task_id>/executions', methods=['GET'])
@login_required
def get_task_executions(task_id):
    """获取测试任务的用例执行结果列表"""
    try:
        task = TestTask.query.get_or_404(task_id)
        
        # 基础查询
        query = TestCaseExecution.query.filter_by(task_id=task_id)
        
        # 处理状态筛选
        if request.args.get('status'):
            query = query.filter_by(status=request.args['status'])
        
        executions = query.all()
        execution_list = [e.to_dict() for e in executions]
        
        return success_response(execution_list)
    except Exception as e:
        return error_response(500, f'获取执行结果失败: {str(e)}')


@bp.route('/<int:task_id>/executions/<int:case_id>', methods=['POST'])
@login_required
def update_case_execution(task_id, case_id):
    """更新测试用例在任务中的执行状态"""
    try:
        task = TestTask.query.get_or_404(task_id)
        test_case = TestCase.query.get_or_404(case_id)
        
        data = request.get_json()
        if not data:
            return error_response(400, '请求体不能为空')
        # status 必填（创建/更新执行记录用）；notes 可选
        if 'status' not in data or data['status'] not in TEST_EXECUTION_STATUS:
            return error_response(400, '无效的执行状态')
        
        # 查找或创建执行记录
        execution = TestCaseExecution.query.filter_by(
            task_id=task_id,
            case_id=case_id
        ).first()
        if not execution:
            execution = TestCaseExecution(
                task_id=task_id,
                case_id=case_id,
                executor_id=current_user.id
            )
            db.session.add(execution)
        
        # 更新执行状态（仅写任务执行记录 TestCaseExecution，不更新用例库 TestCase）
        execution.status = data['status']
        if 'notes' in data:
            execution.notes = data['notes']
        execution.execution_time = datetime.now(timezone(timedelta(hours=8)))
        db.session.commit()
        
        return success_response(execution.to_dict())
    except Exception as e:
        db.session.rollback()
        return error_response(500, f'更新执行状态失败: {str(e)}')


@bp.route('/<int:task_id>/statistics', methods=['GET'])
@login_required
def get_task_statistics(task_id):
    """获取测试任务的统计信息（按本任务的执行记录 TestCaseExecution 统计通过率）"""
    try:
        task = TestTask.query.get_or_404(task_id)
        if task.case_snapshots and len(task.case_snapshots) > 0:
            total_cases = len(task.test_cases) if task.test_cases else 0
        elif task.suite_id and task.suite:
            total_cases = len(task.suite.test_cases) if task.suite else 0
        else:
            total_cases = len(task.test_cases) if task.test_cases else 0
        executions = TestCaseExecution.query.filter_by(task_id=task_id).all()
        stats = {'pass': 0, 'fail': 0, 'blocked': 0, 'not_applicable': 0}
        for e in executions:
            if e.status in stats:
                stats[e.status] += 1
        total_executed = sum(stats.values())
        pass_rate = (stats['pass'] / total_cases * 100) if total_cases > 0 else 0
        not_executed = total_cases - total_executed
        return success_response({
            'statistics': {
                'pass_count': stats['pass'],
                'fail_count': stats['fail'],
                'blocked_count': stats['blocked'],
                'not_applicable_count': stats['not_applicable'],
                'total_executed': total_executed,
                'not_executed': not_executed,
                'total_cases': total_cases,
                'pass_rate': round(pass_rate, 2)
            }
        })
    except Exception as e:
        return error_response(500, f'获取统计信息失败: {str(e)}')


# XMind视图功能已移除，暂时不再支持脑图实现


@bp.route('/options', methods=['GET'])
@login_required
def get_task_options():
    """获取测试任务状态和优先级选项"""
    try:
        return success_response({
            'status_options': list(TEST_TASK_STATUS),
            'priority_options': ['high', 'medium', 'low'],
            'task_type_options': ['test_case', 'device_script'],
            'execution_status_options': list(TEST_EXECUTION_STATUS)
        })
    except Exception as e:
        return error_response(500, f'获取任务选项失败: {str(e)}')


@bp.route('/<int:task_id>/execute', methods=['POST'])
@login_required
def execute_test_task(task_id):
    """执行测试任务"""
    test_task = TestTask.query.get_or_404(task_id)
    
    if test_task.status not in ['pending', 'completed']:
        return error_response(400, "只能执行待执行或已完成状态的测试任务")
    
    try:
        # 如果是重新执行已完成的任务，重置状态为待执行
        if test_task.status == 'completed':
            test_task.status = 'pending'
            test_task.started_time = None
            test_task.completed_time = None
            test_task.executor_id = None
        else:
            # 首次执行，更新任务状态为执行中
            test_task.status = 'running'
            test_task.started_time = datetime.now(timezone(timedelta(hours=8)))
            test_task.completed_time = None
            test_task.executor_id = current_user.id
        
        # 清空之前的执行记录
        if test_task.task_type == 'test_case':
            TestCaseExecution.query.filter_by(task_id=task_id).delete()
        
        db.session.commit()
        
        log_user_action("执行测试任务", f"任务ID: {task_id}")
        
        return success_response({
            'test_task': test_task.to_dict()
        }, "测试任务开始执行")
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, "测试任务执行失败，请稍后重试")


@bp.route('/<int:task_id>/pause', methods=['POST'])
@login_required
def pause_test_task(task_id):
    """暂停测试任务"""
    test_task = TestTask.query.get_or_404(task_id)
    
    if test_task.status != 'running':
        return error_response(400, "只能暂停运行中的测试任务")
    
    try:
        test_task.status = 'paused'
        db.session.commit()
        
        log_user_action("暂停测试任务", f"任务ID: {task_id}")
        
        return success_response({
            'test_task': test_task.to_dict()
        }, "测试任务已暂停")
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, "测试任务暂停失败，请稍后重试")


@bp.route('/<int:task_id>/resume', methods=['POST'])
@login_required
def resume_test_task(task_id):
    """恢复测试任务"""
    test_task = TestTask.query.get_or_404(task_id)
    
    if test_task.status != 'paused':
        return error_response(400, "只能恢复暂停中的测试任务")
    
    try:
        test_task.status = 'running'
        db.session.commit()
        
        log_user_action("恢复测试任务", f"任务ID: {task_id}")
        
        return success_response({
            'test_task': test_task.to_dict()
        }, "测试任务已恢复")
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, "测试任务恢复失败，请稍后重试")

@bp.route('/<int:task_id>/complete', methods=['POST'])
@login_required
def complete_test_task(task_id):
    """完成测试任务；若用户设置为自动生成报告则落库"""
    test_task = TestTask.query.get_or_404(task_id)

    if test_task.status != 'running':
        return error_response(400, "只能完成运行中的测试任务")

    try:
        test_task.status = 'completed'
        test_task.completed_time = datetime.now(timezone(timedelta(hours=8)))

        # 用户设置：自动生成报告（默认自动）
        auto_gen = True
        setting = UserSetting.query.filter_by(
            user_id=current_user.id,
            setting_key='report_auto_generate'
        ).first()
        if setting and setting.setting_value == 'manual':
            auto_gen = False
        if auto_gen:
            from app.routes.reports import create_report_for_task
            create_report_for_task(test_task)

        db.session.commit()

        log_user_action("完成测试任务", f"任务ID: {task_id}")

        return success_response({
            'test_task': test_task.to_dict()
        }, "测试任务已完成")

    except Exception as e:
        db.session.rollback()
        return error_response(500, "测试任务完成失败，请稍后重试")

@bp.route('/<int:task_id>/cancel', methods=['POST'])
@login_required
def cancel_test_task(task_id):
    """取消测试任务"""
    test_task = TestTask.query.get_or_404(task_id)
    
    if test_task.status not in ['pending', 'running', 'paused']:
        return error_response(400, "只能取消待执行、运行中或暂停中的测试任务")
    
    try:
        # 保存原始状态
        original_status = test_task.status
        test_task.status = 'pending'
        test_task.started_time = None
        test_task.completed_time = None
        db.session.commit()
        
        log_user_action("取消测试任务", f"任务ID: {task_id}, 原状态: {original_status}")
        
        return success_response({
            'test_task': test_task.to_dict()
        }, "测试任务已取消")
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, "测试任务取消失败，请稍后重试")


@bp.route('/<int:task_id>/devices', methods=['GET'])
@login_required
def get_task_devices(task_id):
    """获取测试任务关联的设备列表"""
    try:
        task = TestTask.query.get_or_404(task_id)
        devices = [device.to_dict() for device in task.devices]
        
        return success_response({
            'devices': devices,
            'total': len(devices)
        })
    except Exception as e:
        return error_response(500, f'获取设备列表失败: {str(e)}')


@bp.route('/<int:task_id>/test-cases', methods=['GET'])
@login_required
def get_task_test_cases(task_id):
    """获取测试任务关联的测试用例列表（有快照时返回快照内容；状态按本任务执行记录）"""
    try:
        task = TestTask.query.options(
            selectinload(TestTask.case_snapshots),
            selectinload(TestTask.test_cases),
            selectinload(TestTask.case_executions),
        ).get_or_404(task_id)
        if task.case_snapshots and len(task.case_snapshots) > 0:
            # 状态只按本任务的执行记录（TestCaseExecution），不用用例库/用例表当前状态
            execution_status_by_case = {e.case_id: e.status for e in (task.case_executions or [])}
            suite_name = task.suite_name_snapshot or (task.suite.suite_name if task.suite else None) or ""
            test_cases = []
            for s in task.case_snapshots:
                d = s.to_dict()
                d['status'] = execution_status_by_case.get(s.case_id, '')
                d['suite_id'] = task.suite_id
                d['suite_name'] = suite_name
                test_cases.append(d)
        else:
            # 无快照时仍用关联用例；状态按本任务执行记录，避免用用例表 status
            execution_status_by_case = {
                e.case_id: e.status for e in TestCaseExecution.query.filter_by(task_id=task_id).all()
            }
            test_cases = []
            for case in (task.test_cases or []):
                d = case.to_dict()
                d['status'] = execution_status_by_case.get(case.id, '')
                test_cases.append(d)
        return success_response({
            'test_cases': test_cases,
            'total': len(test_cases)
        })
    except Exception as e:
        return error_response(500, f'获取测试用例列表失败: {str(e)}')
