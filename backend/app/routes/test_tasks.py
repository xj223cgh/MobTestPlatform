from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timezone, timedelta

from app.models.models import TestTask, db, TestSuite, TestCase, Device, TestCaseExecution, TEST_TASK_STATUS, TEST_EXECUTION_STATUS
from app.utils.helpers import (
    success_response, error_response, get_pagination_params, log_user_action,
    validate_json_data
)

# 创建Blueprint
bp = Blueprint('test_tasks', __name__, url_prefix='/api/test-tasks')


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
    
    # 构建查询
    query = TestTask.query
    
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
    
    # 分页
    pagination = query.order_by(TestTask.created_at.desc()).paginate(
        page=page, per_page=size, error_out=False
    )
    
    test_tasks = [test_task.to_dict() for test_task in pagination.items]
    
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
    test_task = TestTask.query.get_or_404(task_id)
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

    
    test_task = TestTask(
        task_name=data['task_name'],
        task_description=data.get('task_description', ''),
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
        else:
            # 其他任务类型不关联测试用例
            test_task.test_cases = []
        
        # 处理设备关联（仅设备脚本任务）
        if task_type == 'device_script':
            if data.get('devices'):
                devices = Device.query.filter(Device.device_id.in_(data['devices'])).all()
                test_task.devices = devices
            else:
                # 如果没有提供设备列表，清空设备关联
                test_task.devices = []
        # 其他任务类型不关联设备，不需要显式设置为空列表
        

        db.session.add(test_task)
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
    if 'suite_id' in data:
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
    
    # 处理测试用例关联（仅测试用例任务）
    # 注意：前端传递的 test_cases 字段是套件ID，不是测试用例ID列表
    # 如果需要关联测试用例，应该通过 suite_id 来获取套件中的测试用例
    if new_task_type == 'test_case':
        if data.get('suite_id'):
            # 如果指定了测试套件，获取该套件中的所有测试用例
            suite = TestSuite.query.get(data['suite_id'])
            if suite:
                test_task.test_cases = suite.test_cases
            else:
                test_task.test_cases = []
        else:
            # 如果没有指定套件，清空测试用例关联
            test_task.test_cases = []
    elif new_task_type != 'test_case':
        # 如果任务类型不是测试用例任务，清空测试用例关联
        test_task.test_cases = []
    
    # 处理设备关联（仅设备脚本任务）
    if new_task_type == 'device_script':
        if 'devices' in data:
            devices = Device.query.filter(Device.device_id.in_(data['devices'])).all()
            test_task.devices = devices
        else:
            # 如果没有提供设备列表，清空设备关联
            test_task.devices = []
    elif new_task_type != 'device_script':
        # 如果任务类型不是设备脚本任务，清空设备关联
        test_task.devices = []
    
    # 如果任务类型改变，更新任务类型
    if new_task_type != current_task_type:
        test_task.task_type = new_task_type
    
    try:
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
        
        # 验证状态值
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
        
        # 更新执行状态
        execution.status = data['status']
        if 'notes' in data:
            execution.notes = data['notes']
        execution.execution_time = datetime.now(timezone(timedelta(hours=8)))
        
        # 更新测试用例的最后执行时间
        test_case.executed_at = datetime.now(timezone(timedelta(hours=8)))
        
        db.session.commit()
        
        return success_response(execution.to_dict())
    except Exception as e:
        db.session.rollback()
        return error_response(500, f'更新执行状态失败: {str(e)}')


@bp.route('/<int:task_id>/statistics', methods=['GET'])
@login_required
def get_task_statistics(task_id):
    """获取测试任务的统计信息"""
    try:
        task = TestTask.query.get_or_404(task_id)
        
        # 获取关联的测试用例 - 当关联了用例集时，动态获取用例集中的所有用例
        test_cases = []
        if task.suite_id and task.suite:
            # 如果关联了用例集，动态获取用例集中的所有用例
            test_cases = task.suite.test_cases if task.suite else []
        else:
            # 否则使用任务直接关联的用例
            test_cases = task.test_cases if task.test_cases else []
        
        # 直接从测试用例表中统计各状态的数量，不需要TestCaseExecution表
        stats = {
            'pass': 0,
            'fail': 0,
            'blocked': 0,
            'not_applicable': 0
        }
        
        for test_case in test_cases:
            if test_case.status in stats:
                stats[test_case.status] += 1
        
        # 计算总数和通过率
        total_executed = sum(stats.values())
        pass_rate = (stats['pass'] / total_executed * 100) if total_executed > 0 else 0
        
        total_cases = len(test_cases)
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
    """完成测试任务"""
    test_task = TestTask.query.get_or_404(task_id)
    
    if test_task.status != 'running':
        return error_response(400, "只能完成运行中的测试任务")
    
    try:
        test_task.status = 'completed'
        test_task.completed_time = datetime.now(timezone(timedelta(hours=8)))
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
    """获取测试任务关联的测试用例列表"""
    try:
        task = TestTask.query.get_or_404(task_id)
        test_cases = [case.to_dict() for case in task.test_cases]
        
        return success_response({
            'test_cases': test_cases,
            'total': len(test_cases)
        })
    except Exception as e:
        return error_response(500, f'获取测试用例列表失败: {str(e)}')
