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
from app.services.permission_service import permission_required
from werkzeug.exceptions import NotFound

from app.models.models import TestTask, db, TestCase, Report, User
from app.utils.helpers import (
    success_response, error_response, get_pagination_params, log_user_action,
)

bp = Blueprint('reports', __name__, url_prefix='/api/reports')



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
        status=test_task.status,
        iteration_name=test_task.iteration.iteration_name if getattr(test_task, 'iteration', None) else None,
        suite_id=getattr(test_task, 'suite_id', None),
        suite_name=test_task.suite_name_snapshot or (test_task.suite.suite_name if getattr(test_task, 'suite', None) else None),
        requirement_name=test_task.version_requirement.requirement_name if getattr(test_task, 'version_requirement', None) and test_task.version_requirement else None,
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

        task_id_arg = request.args.get('task_id')
        if task_id_arg:
            try:
                query = query.filter_by(task_id=int(task_id_arg))
            except ValueError:
                pass

        search = request.args.get('search')
        if search:
            query = query.filter(Report.task_name.ilike(f'%{search}%'))
        
        status = request.args.get('status')
        if status:
            from sqlalchemy import or_, and_
            query = query.outerjoin(TestTask, Report.task_id == TestTask.id).filter(
                or_(Report.status == status, and_(Report.status.is_(None), TestTask.status == status))
            )
        
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


def _task_info_from_report(report):
    """用报告快照构建 task_info"""
    task = report.task
    base = (task.to_dict() if task else {})
    snapshot = {
        'task_id': report.task_id,
        'project_id': report.project_id,
        'task_name': report.task_name,
        'project_name': report.project_name,
        'status': report.status if report.status is not None else base.get('status'),
        'completed_at': report.completed_at.isoformat() if report.completed_at else base.get('completed_time'),
        'iteration_name': report.iteration_name or base.get('iteration_name'),
        'suite_id': report.suite_id if report.suite_id is not None else base.get('suite_id'),
        'suite_name': report.suite_name or base.get('suite_name'),
        'version_requirement_name': report.requirement_name or base.get('version_requirement_name'),
    }
    for k, v in snapshot.items():
        if v is not None:
            base[k] = v
    base['created_by'] = (report.creator.real_name if report.creator else None) or base.get('creator_name') or '-'
    base['assignee_name'] = report.assignee.real_name if report.assignee else '-'
    return base


@bp.route('/record/<int:report_id>', methods=['GET'])
@login_required
def get_report_by_id(report_id):
    """按报告 ID 获取报告详情（落库数据，task_info 以报告快照为准）"""
    try:
        report = Report.query.get_or_404(report_id)
        task_info = _task_info_from_report(report)
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
@permission_required('report.delete')
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
@permission_required('report.delete')
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
    """按任务 ID 获取报告数据"""
    return _get_report_data_impl(task_id)


@bp.route('/<int:task_id>/data', methods=['GET'])
@login_required
def get_report_data(task_id):
    """按任务 ID 获取报告数据（路由别名）"""
    return _get_report_data_impl(task_id)


def _get_report_data_impl(task_id):
    """获取报告数据：优先返回已落库报告，若无则实时生成（不落库）"""
    try:
        test_task = TestTask.query.get_or_404(task_id)
        task_info = test_task.to_dict()
        task_info['created_by'] = task_info.get('creator_name') or '-'
        task_info['completed_at'] = task_info.get('completed_time')

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
        return error_response(500, f'获取报告数据失败: {str(e)}')


def generate_test_case_report(test_task):
    """生成测试用例任务报告（优先快照）。"""
    use_snapshots = getattr(test_task, 'case_snapshots', None) and len(test_task.case_snapshots) > 0

    task_executions = {e.case_id: e for e in (test_task.case_executions or [])}
    stats = {'pass': 0, 'fail': 0, 'blocked': 0, 'not_applicable': 0}
    for e in (test_task.case_executions or []):
        if e.status in stats:
            stats[e.status] += 1
    executed_cases = sum(stats.values())
    pass_count = stats['pass']
    suite_name = test_task.suite_name_snapshot or (test_task.suite.suite_name if getattr(test_task, 'suite', None) else None) or ""

    details = []

    if use_snapshots:
        case_snapshots = list(test_task.case_snapshots)
        total_cases = len(case_snapshots)
        pass_rate = round(pass_count / total_cases * 100, 1) if total_cases > 0 else 0

        for snap in case_snapshots:
            exec_for_task = task_executions.get(snap.case_id)
            try:
                executed_by = exec_for_task.executor.username if exec_for_task and exec_for_task.executor else None
                actual_result = getattr(exec_for_task, 'actual_result', None) or (exec_for_task.notes if exec_for_task else None)
                executed_at = getattr(exec_for_task, 'execution_time', None) or getattr(exec_for_task, 'created_at', None) if exec_for_task else None
                remarks = getattr(exec_for_task, 'remarks', None) or (exec_for_task.notes if exec_for_task else None)
            except Exception:
                executed_by = actual_result = executed_at = remarks = None
            details.append({
                'case_id': snap.case_id,
                'case_number': snap.case_number,
                'case_title': snap.case_name or '',
                'priority': snap.priority,
                'preconditions': snap.preconditions,
                'steps': snap.steps,
                'expected_result': snap.expected_result,
                'status': (exec_for_task.status if exec_for_task else '') or '',
                'actual_result': actual_result,
                'executed_by': executed_by,
                'executed_at': executed_at,
                'remarks': remarks,
            })
    else:
        # 无快照时从关联用例或套件用例中生成
        try:
            if test_task.suite_id and test_task.suite:
                test_cases = test_task.suite.test_cases if test_task.suite.test_cases else []
            else:
                test_cases = list(test_task.test_cases) if test_task.test_cases else []
        except Exception:
            test_cases = []
        total_cases = len(test_cases)
        pass_rate = round(pass_count / total_cases * 100, 1) if total_cases > 0 else 0

        for test_case in test_cases:
            exec_for_task = task_executions.get(test_case.id)
            case_title = getattr(test_case, 'case_name', None) or getattr(test_case, 'case_title', None) or ''
            case_number = getattr(test_case, 'case_number', None)
            preconditions = getattr(test_case, 'preconditions', None)
            steps = getattr(test_case, 'steps', None)
            expected_result = getattr(test_case, 'expected_result', None)
            priority = getattr(test_case, 'priority', None)
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
    return {'summary': summary, 'details': details}


def generate_device_script_report(test_task):
    """生成设备脚本任务报告（含任务基本信息与设备执行明细）"""
    import json

    task_name = getattr(test_task, 'task_name', None) or ''
    script_file = getattr(test_task, 'script_file', None) or ''
    command = getattr(test_task, 'command', None) or ''
    scheduled_time = test_task.scheduled_time.isoformat() if getattr(test_task, 'scheduled_time', None) else None
    completed_at = test_task.completed_time.isoformat() if getattr(test_task, 'completed_time', None) else None
    task_devices = list(test_task.devices) if getattr(test_task, 'devices', None) else []

    device_executions = []
    if test_task.result:
        try:
            result_data = json.loads(test_task.result) if isinstance(test_task.result, str) else test_task.result
            if isinstance(result_data, dict) and 'executions' in result_data:
                device_executions = result_data['executions'] or []
        except Exception:
            device_executions = []

    if device_executions:
        total_devices = len(device_executions)
        success_count = sum(1 for e in device_executions if e.get('status') == 'success')
        failed_count = total_devices - success_count
        success_rate = round(success_count / total_devices * 100, 1) if total_devices > 0 else 0
        details = []
        for e in device_executions:
            details.append({
                'device_id': e.get('device_id'),
                'device_name': e.get('device_name'),
                'status': e.get('status'),
                'execution_time': e.get('execution_time'),
                'exit_code': e.get('exit_code'),
                'output': e.get('output'),
                'error_output': e.get('error_output'),
            })
    else:
        total_devices = len(task_devices)
        success_count = 0
        failed_count = 0
        success_rate = 0
        details = []
        for d in task_devices:
            details.append({
                'device_id': getattr(d, 'device_id', None) or getattr(d, 'id'),
                'device_name': getattr(d, 'device_name', None) or '',
                'status': 'unknown',
                'execution_time': None,
                'exit_code': None,
                'output': '',
                'error_output': '未记录执行结果',
            })

    summary = {
        'total_devices': total_devices,
        'success_count': success_count,
        'failed_count': failed_count,
        'success_rate': success_rate,
        'task_name': task_name,
        'script_file': script_file,
        'command': command,
        'scheduled_time': scheduled_time,
        'completed_at': completed_at,
    }

    return {
        'summary': summary,
        'details': details,
    }
