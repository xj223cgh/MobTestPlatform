from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from werkzeug.exceptions import NotFound

from app.models.models import TestTask, db, TestCase
from app.utils.helpers import (
    success_response, error_response, get_pagination_params, log_user_action,
    validate_json_data
)

# 创建Blueprint
bp = Blueprint('reports', __name__, url_prefix='/api/reports')


@bp.route('/<int:task_id>/data', methods=['GET'])
@login_required
def get_report_data(task_id):
    """获取报告数据"""
    try:
        # 获取测试任务
        test_task = TestTask.query.get_or_404(task_id)
        
        # 构建任务基本信息，兼容前端字段名
        task_info = test_task.to_dict()
        # 前端期望 created_by、completed_at
        task_info['created_by'] = task_info.get('creator_name') or '-'
        task_info['completed_at'] = task_info.get('completed_time')
        
        # 根据任务类型生成不同的报告数据
        if test_task.task_type == 'test_case':
            report_data = generate_test_case_report(test_task)
        elif test_task.task_type == 'device_script':
            report_data = generate_device_script_report(test_task)
        else:
            report_data = {
                'summary': {},
                'details': []
            }
        
        report_data['task_info'] = task_info
        return success_response(report_data)
    except NotFound:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        return error_response(500, f'获取报告数据失败: {str(e)}')


def generate_test_case_report(test_task):
    """生成测试用例任务报告"""
    # 获取关联的测试用例：优先从套件获取（与 to_dict 逻辑一致）
    try:
        if test_task.suite_id and test_task.suite:
            test_cases = test_task.suite.test_cases if test_task.suite.test_cases else []
        else:
            test_cases = list(test_task.test_cases) if test_task.test_cases else []
    except Exception:
        test_cases = []
    
    # 初始化统计数据
    stats = {
        'pass': 0,
        'fail': 0,
        'blocked': 0,
        'not_applicable': 0
    }
    
    # 统计用例执行情况
    for test_case in test_cases:
        if test_case.status in stats:
            stats[test_case.status] += 1
    
    # 计算总数和通过率
    total_cases = len(test_cases)
    executed_cases = sum(stats.values())
    pass_count = stats['pass']
    pass_rate = round(pass_count / executed_cases * 100, 1) if executed_cases > 0 else 0
    
    # 构建报告摘要
    summary = {
        'total_cases': total_cases,
        'executed_cases': executed_cases,
        'pass_count': pass_count,
        'fail_count': stats['fail'],
        'blocked_count': stats['blocked'],
        'not_applicable_count': stats['not_applicable'],
        'pass_rate': pass_rate
    }
    
    # 构建详细数据
    details = []
    for test_case in test_cases:
        try:
            latest_execution = None
            if test_case.executions:
                executions_with_time = [e for e in test_case.executions if e.created_at]
                latest_execution = max(executions_with_time, key=lambda x: x.created_at) if executions_with_time else None
            executed_by = None
            if latest_execution and latest_execution.executor:
                executed_by = latest_execution.executor.username
            details.append({
                'case_id': test_case.id,
                'case_title': test_case.case_title or '',
                'status': test_case.status or '',
                'actual_result': latest_execution.actual_result if latest_execution else None,
                'executed_by': executed_by,
                'executed_at': latest_execution.created_at if latest_execution else None,
                'remarks': latest_execution.remarks if latest_execution else None
            })
        except Exception:
            details.append({
                'case_id': test_case.id,
                'case_title': getattr(test_case, 'case_title', '') or '',
                'status': getattr(test_case, 'status', '') or '',
                'actual_result': None,
                'executed_by': None,
                'executed_at': None,
                'remarks': None
            })
    
    return {
        'summary': summary,
        'details': details
    }


def generate_device_script_report(test_task):
    """生成设备脚本任务报告"""
    # 初始化统计数据
    total_devices = 0
    success_count = 0
    failed_count = 0
    
    # 从任务结果中提取设备执行数据
    device_executions = []
    if test_task.result:
        try:
            import json
            result_data = json.loads(test_task.result)
            # 检查结果数据结构
            if isinstance(result_data, dict) and 'executions' in result_data:
                device_executions = result_data['executions']
        except Exception as e:
            # 结果解析失败，使用空列表
            device_executions = []
    
    # 初始化统计数据
    total_devices = len(device_executions)
    success_count = sum(1 for exec in device_executions if exec.get('status') == 'success')
    failed_count = total_devices - success_count
    success_rate = round(success_count / total_devices * 100, 1) if total_devices > 0 else 0
    
    # 构建报告摘要
    summary = {
        'total_devices': total_devices,
        'success_count': success_count,
        'failed_count': failed_count,
        'success_rate': success_rate
    }
    
    # 构建详细数据
    details = []
    for execution in device_executions:
        details.append({
            'device_id': execution.get('device_id'),
            'device_name': execution.get('device_name'),
            'status': execution.get('status'),
            'execution_time': execution.get('execution_time'),
            'exit_code': execution.get('exit_code'),
            'output': execution.get('output'),
            'error_output': execution.get('error_output')
        })
    
    return {
        'summary': summary,
        'details': details
    }
