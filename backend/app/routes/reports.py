from datetime import datetime

from flask import Blueprint, request
from flask_login import login_required, current_user
from werkzeug.exceptions import NotFound

from app.models.models import TestTask, db, TestCase, Report
from app.utils.helpers import (
    success_response, error_response, get_pagination_params, log_user_action,
)

# 创建Blueprint
bp = Blueprint('reports', __name__, url_prefix='/api/reports')


def _json_serial(obj):
    """将 datetime 转为字符串以便 JSON 存储"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def _make_serializable(data):
    """递归把 summary/details 中的 datetime 转为字符串"""
    if data is None:
        return None
    if isinstance(data, dict):
        return {k: _make_serializable(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_make_serializable(i) for i in data]
    if isinstance(data, datetime):
        return data.isoformat()
    return data


def create_report_for_task(test_task):
    """根据任务生成报告并落库，返回 Report 或 None"""
    if test_task.task_type == 'test_case':
        report_data = generate_test_case_report(test_task)
    elif test_task.task_type == 'device_script':
        report_data = generate_device_script_report(test_task)
    else:
        return None
    summary = _make_serializable(report_data.get('summary') or {})
    details = _make_serializable(report_data.get('details') or [])
    report = Report(
        task_id=test_task.id,
        report_type=test_task.task_type,
        task_name=test_task.task_name or '',
        project_id=test_task.project_id,
        project_name=test_task.project.project_name if test_task.project else None,
        summary=summary,
        details=details,
        completed_at=test_task.completed_time,
    )
    db.session.add(report)
    db.session.flush()
    return report


@bp.route('/', methods=['GET'])
@login_required
def list_reports():
    """报告列表（从 reports 表分页）"""
    try:
        page, per_page = get_pagination_params()
        query = Report.query.order_by(Report.created_at.desc())
        if request.args.get('report_type'):
            query = query.filter_by(report_type=request.args['report_type'])
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        items = [r.to_dict() for r in pagination.items]
        return success_response({
            'reports': items,
            'pagination': {
                'page': pagination.page,
                'size': pagination.per_page,
                'total': pagination.total,
            },
        })
    except Exception as e:
        return error_response(500, str(e))


@bp.route('/record/<int:report_id>', methods=['GET'])
@login_required
def get_report_by_id(report_id):
    """按报告 ID 获取报告详情（落库数据）"""
    try:
        report = Report.query.get_or_404(report_id)
        task = report.task
        task_info = task.to_dict() if task else {}
        task_info['created_by'] = task_info.get('creator_name') or '-'
        task_info['completed_at'] = task_info.get('completed_time')
        return success_response({
            'task_info': task_info,
            'summary': report.summary or {},
            'details': report.details or [],
        })
    except NotFound:
        raise
    except Exception as e:
        return error_response(500, str(e))


@bp.route('/generate/<int:task_id>', methods=['POST'])
@login_required
def manual_generate_report(task_id):
    """手动生成报告：为指定任务生成并落库，返回报告 ID"""
    try:
        test_task = TestTask.query.get_or_404(task_id)
        if test_task.status != 'completed':
            return error_response(400, '仅支持对已完成的任务生成报告')
        report = create_report_for_task(test_task)
        if not report:
            return error_response(400, '不支持该任务类型的报告')
        db.session.commit()
        log_user_action("手动生成报告", f"任务ID: {task_id}, 报告ID: {report.id}")
        return success_response({'report_id': report.id, 'report': report.to_dict()}, '报告已生成')
    except NotFound:
        raise
    except Exception as e:
        db.session.rollback()
        return error_response(500, str(e))


@bp.route('/task/<int:task_id>/data', methods=['GET'])
@login_required
def get_report_data_by_task(task_id):
    """按任务 ID 获取报告数据（实时计算，兼容旧前端）"""
    return _get_report_data_impl(task_id)


@bp.route('/<int:task_id>/data', methods=['GET'])
@login_required
def get_report_data(task_id):
    """按任务 ID 获取报告数据（兼容原 URL /reports/:task_id/data）"""
    return _get_report_data_impl(task_id)


def _get_report_data_impl(task_id):
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
