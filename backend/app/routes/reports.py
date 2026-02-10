"""
测试报告：生成与落库逻辑

- 自动生成：任务完成时（POST /test-tasks/<id>/complete），若用户未关闭「自动生成报告」，
  则调用 create_report_for_task 生成报告并写入 reports 表。
- 手动生成：POST /api/reports/generate/<task_id>，对已完成任务生成一条新报告并落库。
- 报告数据：GET /api/reports/<task_id>/data 优先返回该任务已落库的最新报告；若无则实时计算不落库。
"""
from datetime import datetime

from flask import Blueprint, request
from flask_login import login_required, current_user
from werkzeug.exceptions import NotFound

from app.models.models import TestTask, db, TestCase, Report, User
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
        creator_id=test_task.creator_id,
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
        
        # 报告类型筛选
        if request.args.get('report_type'):
            query = query.filter_by(report_type=request.args['report_type'])
        
        # 任务名称搜索
        search = request.args.get('search')
        if search:
            query = query.filter(Report.task_name.ilike(f'%{search}%'))
        
        # 任务状态筛选（需要关联TestTask表）
        status = request.args.get('status')
        if status:
            query = query.join(TestTask, Report.task_id == TestTask.id).filter(TestTask.status == status)
        
        # 创建人筛选（需要关联User表）
        creator = request.args.get('creator')
        if creator:
            query = query.join(User, Report.creator_id == User.id).filter(User.real_name.ilike(f'%{creator}%'))
        
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
    """获取报告数据：优先返回已落库报告，若无则实时生成（不落库）"""
    try:
        test_task = TestTask.query.get_or_404(task_id)
        task_info = test_task.to_dict()
        task_info['created_by'] = task_info.get('creator_name') or '-'
        task_info['completed_at'] = task_info.get('completed_time')

        # 优先使用已落库的报告（最新一条）
        report = Report.query.filter_by(task_id=task_id).order_by(Report.created_at.desc()).first()
        if report:
            report_data = {
                'summary': report.summary or {},
                'details': report.details or [],
                'task_info': task_info,
                'from_storage': True,
                'report_id': report.id,
            }
            return success_response(report_data)

        # 无落库报告时实时生成（不写入数据库）
        if test_task.task_type == 'test_case':
            report_data = generate_test_case_report(test_task)
        elif test_task.task_type == 'device_script':
            report_data = generate_device_script_report(test_task)
        else:
            report_data = {'summary': {}, 'details': []}
        report_data['task_info'] = task_info
        report_data['from_storage'] = False
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
                executions_with_time = [e for e in test_case.executions if getattr(e, 'execution_time', None) or getattr(e, 'created_at', None)]
                latest_execution = max(
                    executions_with_time,
                    key=lambda x: x.execution_time or getattr(x, 'created_at', None) or datetime.min
                ) if executions_with_time else None
            executed_by = None
            if latest_execution and latest_execution.executor:
                executed_by = latest_execution.executor.username
            details.append({
                'case_id': test_case.id,
                'case_title': (getattr(test_case, 'case_name', None) or getattr(test_case, 'case_title', None)) or '',
                'status': test_case.status or '',
                'actual_result': getattr(latest_execution, 'actual_result', None) or (latest_execution.notes if latest_execution else None),
                'executed_by': executed_by,
                'executed_at': getattr(latest_execution, 'execution_time', None) or getattr(latest_execution, 'created_at', None) if latest_execution else None,
                'remarks': getattr(latest_execution, 'remarks', None) or (latest_execution.notes if latest_execution else None)
            })
        except Exception:
            details.append({
                'case_id': test_case.id,
                'case_title': (getattr(test_case, 'case_name', None) or getattr(test_case, 'case_title', None)) or '',
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
