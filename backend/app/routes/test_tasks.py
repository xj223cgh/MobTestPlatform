from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime

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
    
    # 构建查询
    query = TestTask.query
    
    # 搜索过滤
    if search:
        query = query.filter(
            TestTask.task_name.contains(search) |
            TestTask.description.contains(search)
        )
    
    # 状态过滤
    if status:
        query = query.filter(TestTask.status == status)
    
    # 优先级过滤
    if priority:
        query = query.filter(TestTask.priority == priority)
    
    # 分页
    pagination = query.paginate(
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
    
    # 验证套件是否存在
    if data.get('suite_id'):
        suite = TestSuite.query.get(data['suite_id'])
        if not suite:
            return error_response(400, "指定的测试套件不存在")
    
    test_task = TestTask(
        task_name=data['task_name'],
        description=data.get('description', ''),
        priority=data.get('priority', 'medium'),
        status=data.get('status', 'pending'),
        created_by=current_user.id,
        suite_id=data.get('suite_id'),
        documentation_url=data.get('documentation_url'),
        version_info=data.get('version_info'),
        schedule_start=data.get('schedule_start'),
        schedule_end=data.get('schedule_end')
    )
    
    try:
        # 处理测试用例关联
        if data.get('test_cases'):
            test_cases = TestCase.query.filter(TestCase.id.in_(data['test_cases'])).all()
            test_task.test_cases = test_cases
        
        # 处理设备关联
        if data.get('devices'):
            devices = Device.query.filter(Device.id.in_(data['devices'])).all()
            test_task.devices = devices
            
        db.session.add(test_task)
        db.session.commit()
        
        log_user_action("创建测试任务", f"任务名称: {test_task.task_name}")
        
        return success_response({
            'test_task': test_task.to_dict()
        }, "测试任务创建成功")
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, "测试任务创建失败，请稍后重试")


@bp.route('/<int:task_id>', methods=['PUT'])
@login_required
def update_test_task(task_id):
    """更新测试任务"""
    from datetime import datetime
    test_task = TestTask.query.get_or_404(task_id)
    data = request.get_json()
    
    # 更新字段
    if 'task_name' in data:
        test_task.task_name = data['task_name']
    
    if 'description' in data:
        test_task.description = data['description']
    
    if 'priority' in data:
        test_task.priority = data['priority']
    
    if 'status' in data:
        test_task.status = data['status']
        # 如果任务状态变为运行中，记录开始时间
        if data['status'] == 'running' and test_task.start_time is None:
            test_task.start_time = datetime.now(timezone(timedelta(hours=8)))
        # 如果任务状态变为已完成，记录结束时间
        elif data['status'] == 'completed' and test_task.end_time is None:
            test_task.end_time = datetime.now(timezone(timedelta(hours=8)))
    
    if 'result' in data:
        test_task.result = data['result']
    
    # 更新任务相关信息
    if 'suite_id' in data:
        if data['suite_id'] is not None:
            suite = TestSuite.query.get(data['suite_id'])
            if not suite:
                return error_response(400, "指定的测试套件不存在")
        test_task.suite_id = data['suite_id']
    
    if 'documentation_url' in data:
        test_task.documentation_url = data['documentation_url']
    
    if 'version_info' in data:
        test_task.version_info = data['version_info']
    
    if 'schedule_start' in data:
        test_task.schedule_start = data['schedule_start']
    
    if 'schedule_end' in data:
        test_task.schedule_end = data['schedule_end']
    
    # 处理测试用例关联
    if 'test_cases' in data:
        test_cases = TestCase.query.filter(TestCase.id.in_(data['test_cases'])).all()
        test_task.test_cases = test_cases
    
    # 处理设备关联
    if 'devices' in data:
        devices = Device.query.filter(Device.id.in_(data['devices'])).all()
        test_task.devices = devices
    
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
        return error_response(f'获取执行结果失败: {str(e)}', 500)


@bp.route('/<int:task_id>/executions/<int:case_id>', methods=['POST'])
@login_required
def update_case_execution(task_id, case_id):
    """更新测试用例在任务中的执行状态"""
    from datetime import datetime
    try:
        task = TestTask.query.get_or_404(task_id)
        test_case = TestCase.query.get_or_404(case_id)
        
        data = request.get_json()
        
        # 验证状态值
        if 'status' not in data or data['status'] not in TEST_EXECUTION_STATUS:
            return error_response('无效的执行状态', 400)
        
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
        return error_response(f'更新执行状态失败: {str(e)}', 500)


@bp.route('/<int:task_id>/statistics', methods=['GET'])
@login_required
def get_task_statistics(task_id):
    """获取测试任务的统计信息"""
    try:
        task = TestTask.query.get_or_404(task_id)
        
        # 获取所有执行记录
        executions = TestCaseExecution.query.filter_by(task_id=task_id).all()
        
        # 统计各状态的数量
        stats = {
            'pass': 0,
            'fail': 0,
            'blocked': 0,
            'not_applicable': 0
        }
        
        for execution in executions:
            if execution.status in stats:
                stats[execution.status] += 1
        
        # 计算总数和通过率
        total_executed = sum(stats.values())
        pass_rate = (stats['pass'] / total_executed * 100) if total_executed > 0 else 0
        
        # 获取未执行的用例数量
        total_cases = len(task.test_cases)
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
        return error_response(f'获取统计信息失败: {str(e)}', 500)


# XMind视图功能已移除，暂时不再支持脑图实现


@bp.route('/<int:task_id>/execute', methods=['POST'])
@login_required
def execute_test_task(task_id):
    """执行测试任务"""
    test_task = TestTask.query.get_or_404(task_id)
    
    if test_task.status != 'pending':
        return error_response(400, "只能执行待执行状态的测试任务")
    
    try:
        # 更新任务状态为执行中
        test_task.status = 'running'
        db.session.commit()
        
        log_user_action("执行测试任务", f"任务ID: {task_id}")
        
        # TODO: 这里应该调用实际的测试执行逻辑
        # 暂时模拟执行成功
        test_task.status = 'completed'
        test_task.result = '{"success": true, "message": "测试执行完成"}'
        db.session.commit()
        
        return success_response({
            'test_task': test_task.to_dict()
        }, "测试任务执行完成")
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, "测试任务执行失败，请稍后重试")


@bp.route('/options', methods=['GET'])
@login_required
def get_task_options():
    """获取测试任务状态和优先级选项"""
    try:
        return success_response({
            'status_options': list(TEST_TASK_STATUS),
            'priority_options': ['high', 'medium', 'low'],
            'execution_status_options': list(TEST_EXECUTION_STATUS)
        })
    except Exception as e:
        return error_response(f'获取任务选项失败: {str(e)}', 500)