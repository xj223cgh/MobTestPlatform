from flask import Blueprint, request
from flask_login import login_required, current_user

from app.models.models import Bug, db
from app.utils.helpers import (
    success_response, error_response, get_pagination_params, log_user_action,
    validate_json_data
)

bp = Blueprint('bugs', __name__)


@bp.route('', methods=['GET'])
@login_required
def get_bugs():
    """获取缺陷列表"""
    page, size = get_pagination_params()
    search = request.args.get('search', '').strip()
    severity = request.args.get('severity', '').strip()
    status = request.args.get('status', '').strip()
    priority = request.args.get('priority', '').strip()
    
    # 构建查询
    query = Bug.query
    
    # 搜索过滤
    if search:
        query = query.filter(
            Bug.title.contains(search) |
            Bug.description.contains(search) |
            Bug.steps.contains(search)
        )
    
    # 严重程度过滤
    if severity:
        query = query.filter(Bug.severity == severity)
    
    # 状态过滤
    if status:
        query = query.filter(Bug.status == status)
    
    # 优先级过滤
    if priority:
        query = query.filter(Bug.priority == priority)
    
    # 分页
    pagination = query.paginate(
        page=page, per_page=size, error_out=False
    )
    
    bugs = [bug.to_dict() for bug in pagination.items]
    
    return success_response({
        'bugs': bugs,
        'pagination': {
            'page': page,
            'size': size,
            'total': pagination.total,
            'pages': pagination.pages
        }
    })


@bp.route('/<int:bug_id>', methods=['GET'])
@login_required
def get_bug(bug_id):
    """获取缺陷详情"""
    bug = Bug.query.get_or_404(bug_id)
    return success_response({
        'bug': bug.to_dict()
    })


@bp.route('', methods=['POST'])
@login_required
@validate_json_data(['bug_title', 'severity', 'priority'])
def create_bug():
    """创建缺陷"""
    data = request.get_json()
    
    bug = Bug(
        title=data['title'],
        description=data.get('description', ''),
        steps=data.get('steps', ''),
        expected_result=data.get('expected_result', ''),
        actual_result=data.get('actual_result', ''),
        severity=data['severity'],
        priority=data['priority'],
        status=data.get('status', 'open'),
        assignee_id=data.get('assignee_id'),
        reporter_id=current_user.id
    )
    
    try:
        db.session.add(bug)
        db.session.commit()
        
        log_user_action("创建缺陷", f"缺陷标题: {bug.title}")
        
        return success_response({
            'bug': bug.to_dict()
        }, "缺陷创建成功")
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, "缺陷创建失败，请稍后重试")


@bp.route('/<int:bug_id>', methods=['PUT'])
@login_required
def update_bug(bug_id):
    """更新缺陷"""
    bug = Bug.query.get_or_404(bug_id)
    data = request.get_json()
    
    # 更新字段
    if 'title' in data:
        bug.title = data['title']
    
    if 'description' in data:
        bug.description = data['description']
    
    if 'steps' in data:
        bug.steps = data['steps']
    
    if 'expected_result' in data:
        bug.expected_result = data['expected_result']
    
    if 'actual_result' in data:
        bug.actual_result = data['actual_result']
    
    if 'severity' in data:
        bug.severity = data['severity']
    
    if 'priority' in data:
        bug.priority = data['priority']
    
    if 'status' in data:
        bug.status = data['status']
    
    if 'assignee_id' in data:
        bug.assignee_id = data['assignee_id']
    
    try:
        db.session.commit()
        
        log_user_action("更新缺陷", f"缺陷ID: {bug_id}")
        
        return success_response({
            'bug': bug.to_dict()
        }, "缺陷更新成功")
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, "缺陷更新失败，请稍后重试")


@bp.route('/<int:bug_id>', methods=['DELETE'])
@login_required
def delete_bug(bug_id):
    """删除缺陷"""
    bug = Bug.query.get_or_404(bug_id)
    
    try:
        db.session.delete(bug)
        db.session.commit()
        
        log_user_action("删除缺陷", f"缺陷标题: {bug.title}")
        
        return success_response(message="缺陷删除成功")
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, "缺陷删除失败，请稍后重试")


@bp.route('/severity-options', methods=['GET'])
@login_required
def get_severity_options():
    """获取严重程度选项"""
    severity_options = [
        {'value': 'critical', 'label': '严重'},
        {'value': 'major', 'label': '主要'},
        {'value': 'minor', 'label': '次要'},
        {'value': 'trivial', 'label': '轻微'}
    ]
    
    return success_response({
        'severity_options': severity_options
    })


@bp.route('/priority-options', methods=['GET'])
@login_required
def get_priority_options():
    """获取优先级选项"""
    priority_options = [
        {'value': 'high', 'label': '高'},
        {'value': 'medium', 'label': '中'},
        {'value': 'low', 'label': '低'}
    ]
    
    return success_response({
        'priority_options': priority_options
    })


@bp.route('/status-options', methods=['GET'])
@login_required
def get_status_options():
    """获取状态选项"""
    status_options = [
        {'value': 'open', 'label': '打开'},
        {'value': 'in_progress', 'label': '处理中'},
        {'value': 'resolved', 'label': '已解决'},
        {'value': 'closed', 'label': '已关闭'},
        {'value': 'reopened', 'label': '重新打开'}
    ]
    
    return success_response({
        'status_options': status_options
    })