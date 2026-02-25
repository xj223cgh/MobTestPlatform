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
    # 创建人与负责人可为不同人：负责人优先取任务执行人
    assignee_id = test_task.executor_id if test_task.executor_id != test_task.creator_id else None
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
        assignee_id=assignee_id or test_task.executor_id,
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
        task_info['created_by'] = (report.creator.real_name if report.creator else None) or task_info.get('creator_name') or '-'
        task_info['assignee_name'] = report.assignee.real_name if report.assignee else '-'
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


@bp.route('/<int:report_id>', methods=['DELETE'])
@login_required
def delete_report(report_id):
    """单个删除报告"""
    try:
        report = Report.query.get_or_404(report_id)
        db.session.delete(report)
        db.session.commit()
        log_user_action("删除报告", f"报告ID: {report_id}")
        return success_response(None, "删除成功")
    except NotFound:
        raise
    except Exception as e:
        db.session.rollback()
        return error_response(500, str(e))


@bp.route('/batch-delete', methods=['POST'])
@login_required
def batch_delete_reports():
    """批量删除报告，请求体: { "ids": [1, 2, 3] }"""
    try:
        data = request.get_json() or {}
        ids = data.get("ids") or []
        if not ids:
            return error_response(400, "请选择要删除的报告")
        if not isinstance(ids, list):
            ids = [ids]
        ids = [int(x) for x in ids if x is not None]
        if not ids:
            return error_response(400, "请选择要删除的报告")
        deleted = Report.query.filter(Report.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()
        log_user_action("批量删除报告", f"删除 {deleted} 条，IDs: {ids}")
        return success_response({"deleted": deleted}, f"成功删除 {deleted} 条报告")
    except Exception as e:
        db.session.rollback()
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
    """生成测试用例任务报告：生成时写入一次性快照（用例集名+用例完整内容）以支持历史追溯"""
    use_snapshots = getattr(test_task, 'case_snapshots', None) and len(test_task.case_snapshots) > 0
    try:
        if use_snapshots:
            test_cases = list(test_task.test_cases) if test_task.test_cases else []
        elif test_task.suite_id and test_task.suite:
            test_cases = test_task.suite.test_cases if test_task.suite.test_cases else []
        else:
            test_cases = list(test_task.test_cases) if test_task.test_cases else []
    except Exception:
        test_cases = []
    snapshot_map = {s.case_id: s for s in (test_task.case_snapshots or [])} if use_snapshots else {}
    total_cases = len(test_cases)

    task_executions = {e.case_id: e for e in (test_task.case_executions or [])}
    stats = {'pass': 0, 'fail': 0, 'blocked': 0, 'not_applicable': 0}
    for e in (test_task.case_executions or []):
        if e.status in stats:
            stats[e.status] += 1
    executed_cases = sum(stats.values())
    pass_count = stats['pass']
    pass_rate = round(pass_count / total_cases * 100, 1) if total_cases > 0 else 0
    suite_name = test_task.suite_name_snapshot or (test_task.suite.suite_name if test_task.suite else None) or ""
    summary = {
        'suite_name': suite_name,
        'total_cases': total_cases,
        'executed_cases': executed_cases,
        'pass_count': pass_count,
        'fail_count': stats['fail'],
        'blocked_count': stats['blocked'],
        'not_applicable_count': stats['not_applicable'],
        'pass_rate': pass_rate
    }

    details = []
    for test_case in test_cases:
        snap = snapshot_map.get(test_case.id)
        exec_for_task = task_executions.get(test_case.id)
        case_title = (snap.case_name if snap else None) or getattr(test_case, 'case_name', None) or getattr(test_case, 'case_title', None) or ''
        case_number = snap.case_number if snap else getattr(test_case, 'case_number', None)
        preconditions = snap.preconditions if snap else getattr(test_case, 'preconditions', None)
        steps = snap.steps if snap else getattr(test_case, 'steps', None)
        expected_result = snap.expected_result if snap else getattr(test_case, 'expected_result', None)
        priority = snap.priority if snap else getattr(test_case, 'priority', None)
        try:
            executed_by = exec_for_task.executor.username if exec_for_task and exec_for_task.executor else None
            actual_result = getattr(exec_for_task, 'actual_result', None) or (exec_for_task.notes if exec_for_task else None)
            executed_at = getattr(exec_for_task, 'execution_time', None) or getattr(exec_for_task, 'created_at', None) if exec_for_task else None
            remarks = getattr(exec_for_task, 'remarks', None) or (exec_for_task.notes if exec_for_task else None)
        except Exception:
            executed_by = actual_result = executed_at = remarks = None
        details.append({
            'case_id': test_case.id,
            'case_number': case_number,
            'case_title': case_title,
            'priority': priority,
            'preconditions': preconditions,
            'steps': steps,
            'expected_result': expected_result,
            'status': (exec_for_task.status if exec_for_task else '') or '',
            'actual_result': actual_result,
            'executed_by': executed_by,
            'executed_at': executed_at,
            'remarks': remarks,
        })
    return {'summary': summary, 'details': details}


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
