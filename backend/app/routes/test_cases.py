from flask import Blueprint, request
from flask_login import login_required, current_user

from app.models.models import TestCase, db, TestSuite
from app.utils.helpers import (
    success_response, error_response, get_pagination_params, log_user_action,
    validate_json_data
)

bp = Blueprint('test_cases', __name__, url_prefix='/api/test-cases')


@bp.route('', methods=['GET'])
@login_required
def get_test_cases():
    """获取用例列表"""
    page, size = get_pagination_params()
    search = request.args.get('search', '').strip()
    priority = request.args.get('priority', '').strip()
    status = request.args.get('status', '').strip()
    suite_id = request.args.get('suite_id', '').strip()
    
    # 构建查询
    query = TestCase.query
    
    # 搜索过滤
    if search:
        query = query.filter(
            TestCase.case_name.contains(search) |
            TestCase.case_description.contains(search) |
            TestCase.preconditions.contains(search)
        )
    
    # 优先级过滤
    if priority:
        query = query.filter(TestCase.priority == priority)
    
    # 状态过滤
    if status:
        query = query.filter(TestCase.status == status)
    
    # 模块过滤已移除，模块信息通过套件关联获取
    
    # 套件过滤
    if suite_id:
        query = query.filter(TestCase.suite_id == suite_id)
    
    # 分页
    pagination = query.paginate(
        page=page, per_page=size, error_out=False
    )
    
    test_cases = [test_case.to_dict() for test_case in pagination.items]
    
    return success_response({
        'test_cases': test_cases,
        'pagination': {
            'page': page,
            'size': size,
            'total': pagination.total,
            'pages': pagination.pages
        }
    })


@bp.route('/<int:case_id>', methods=['GET'])
@login_required
def get_test_case(case_id):
    """获取用例详情"""
    test_case = TestCase.query.get_or_404(case_id)
    return success_response({
        'test_case': test_case.to_dict()
    })


@bp.route('', methods=['POST'])
@login_required
@validate_json_data(['case_name'])
def create_test_case():
    """创建测试用例"""
    data = request.get_json()
    
    # 验证套件是否存在
    suite = None
    if data.get('suite_id'):
        suite = TestSuite.query.get(data['suite_id'])
        if not suite:
            return error_response(400, "指定的测试套件不存在")
    
    # 验证用例编号格式
    case_number = data.get('case_number', '')
    if case_number:
        import re
        # 放宽用例编号格式验证，允许纯数字格式，用于导入场景
        if not re.match(r'^(?:.+-.+-.+)?\d{1,3}$', case_number):
            return error_response(400, "用例编号格式不正确，应为：xxx-xxx-xxx001~xxx-xxx-xxx999 或纯数字")
        # 验证数字部分在1-999之间
        num_match = re.search(r'\d+$', case_number)
        if num_match:
            num = int(num_match.group(0))
            if num < 1 or num > 999:
                return error_response(400, "用例编号数字部分必须在001-999之间")
    
    # 使用前端传递的项目相关信息，优先使用前端传递的值，否则从套件获取
    # 支持前端传递ID或名称，名称需要额外处理（当前版本暂不支持名称匹配，优先使用套件信息）
    project_id = data.get('project_id') or (suite.project_id if suite else None)
    version_requirement_id = data.get('version_requirement_id') or (suite.version_requirement_id if suite else None)
    iteration_id = data.get('iteration_id') or (suite.iteration_id if suite else None)
    
    test_case = TestCase(
        case_number=case_number,
        case_name=data['case_name'],
        case_description=data.get('case_description', ''),
        preconditions=data.get('preconditions', ''),
        steps=data.get('steps', ''),
        expected_result=data.get('expected_result', ''),
        actual_result=data.get('actual_result', ''),
        test_data=data.get('test_data', ''),
        priority=data.get('priority', 'P1'),
        status=data.get('status', ''),
        creator_id=current_user.id,
        assignee_id=current_user.id,  # 默认将当前登录用户设为负责人
        suite_id=data.get('suite_id'),
        project_id=project_id,
        version_requirement_id=version_requirement_id,
        iteration_id=iteration_id
    )
    
    try:
        db.session.add(test_case)
        db.session.commit()
        
        log_user_action("创建测试用例", f"用例名称: {test_case.case_name}")
        
        return success_response({
            'test_case': test_case.to_dict()
        }, "测试用例创建成功")
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, "测试用例创建失败，请稍后重试")


@bp.route('/<int:case_id>', methods=['PUT'])
@login_required
def update_test_case(case_id):
    """更新测试用例"""
    test_case = TestCase.query.get_or_404(case_id)
    data = request.get_json()
    
    # 更新字段
    if 'case_number' in data:
        case_number = data['case_number']
        if case_number:
            import re
            if not re.match(r'^.+-.+-.+\d{3}$', case_number):
                return error_response(400, "用例编号格式不正确，应为：xxx-xxx-xxx001~xxx-xxx-xxx999")
            # 验证数字部分在1-999之间
            num_match = re.search(r'\d{3}$', case_number)
            if num_match:
                num = int(num_match.group(0))
                if num < 1 or num > 999:
                    return error_response(400, "用例编号数字部分必须在001-999之间")
        test_case.case_number = case_number
    
    if 'case_name' in data:
        test_case.case_name = data['case_name']
    
    if 'case_description' in data:
        test_case.case_description = data['case_description']
    
    if 'preconditions' in data:
        test_case.preconditions = data['preconditions']
    
    if 'steps' in data:
        test_case.steps = data['steps']
    
    if 'expected_result' in data:
        test_case.expected_result = data['expected_result']
    
    if 'actual_result' in data:
        test_case.actual_result = data['actual_result']
    
    if 'test_data' in data:
        test_case.test_data = data['test_data']
    
    if 'priority' in data:
        test_case.priority = data['priority']
    
    if 'status' in data:
        test_case.status = data['status']
        # 当状态变化时，更新最后执行时间
        from datetime import datetime, timezone, timedelta
        # 使用UTC+8本地时间
        local_timezone = timezone(timedelta(hours=8))
        test_case.executed_at = datetime.now(local_timezone)
    
    # 直接传递的项目相关信息，优先级高于从套件获取
    if 'project_id' in data:
        test_case.project_id = data['project_id']
    
    if 'version_requirement_id' in data:
        test_case.version_requirement_id = data['version_requirement_id']
    
    if 'iteration_id' in data:
        test_case.iteration_id = data['iteration_id']
    
    if 'suite_id' in data:
        # 验证套件是否存在
        if data['suite_id'] is not None:
            suite = TestSuite.query.get(data['suite_id'])
            if not suite:
                return error_response(400, "指定的测试套件不存在")
            # 如果没有直接传递项目相关信息，则从套件获取
            if 'project_id' not in data:
                test_case.project_id = suite.project_id
            if 'version_requirement_id' not in data:
                test_case.version_requirement_id = suite.version_requirement_id
            if 'iteration_id' not in data:
                test_case.iteration_id = suite.iteration_id
        test_case.suite_id = data['suite_id']
    
    if 'assignee_id' in data:
        test_case.assignee_id = data['assignee_id']
    
    if 'reviewer_id' in data:
        test_case.reviewer_id = data['reviewer_id']
    
    if 'review_comments' in data:
        test_case.review_comments = data['review_comments']
    
    try:
        db.session.commit()
        
        log_user_action("更新测试用例", f"用例ID: {case_id}")
        
        return success_response({
            'test_case': test_case.to_dict()
        }, "测试用例更新成功")
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, "测试用例更新失败，请稍后重试")


@bp.route('/<int:case_id>', methods=['DELETE'])
@login_required
def delete_test_case(case_id):
    """删除测试用例"""
    test_case = TestCase.query.get_or_404(case_id)
    
    try:
        db.session.delete(test_case)
        db.session.commit()
        
        log_user_action("删除测试用例", f"用例名称: {test_case.case_name}")
        
        return success_response(message="测试用例删除成功")
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, "测试用例删除失败，请稍后重试")


@bp.route('/priority-options', methods=['GET'])
@login_required
def get_priority_options():
    """获取优先级选项"""
    priority_options = [
        {'value': 'P0', 'label': 'P0'},
        {'value': 'P1', 'label': 'P1'},
        {'value': 'P2', 'label': 'P2'},
        {'value': 'P3', 'label': 'P3'},
        {'value': 'P4', 'label': 'P4'}
    ]
    
    return success_response({
        'priority_options': priority_options
    })


@bp.route('/status-options', methods=['GET'])
@login_required
def get_status_options():
    """获取状态选项"""
    status_options = [
        {'value': '', 'label': ''},
        {'value': 'pass', 'label': '通过'},
        {'value': 'fail', 'label': '失败'},
        {'value': 'blocked', 'label': '阻塞'},
        {'value': 'not_applicable', 'label': '不适用'}
    ]
    
    return success_response({
        'status_options': status_options
    })


# 模块列表功能已移除，模块信息通过套件关联获取


# XMind相关功能已移除，因为不再支持xmind_data字段


@bp.route('/batch-delete', methods=['POST'])
@login_required
def batch_delete_test_cases():
    """批量删除测试用例"""
    data = request.get_json()
    case_ids = data.get('ids', [])
    
    if not case_ids or not isinstance(case_ids, list):
        return error_response(400, "请提供要删除的测试用例ID列表")
    
    try:
        # 删除所有指定ID的测试用例
        TestCase.query.filter(TestCase.id.in_(case_ids)).delete(synchronize_session=False)
        db.session.commit()
        
        log_user_action("批量删除测试用例", f"删除了 {len(case_ids)} 个测试用例")
        
        return success_response(message="测试用例批量删除成功")
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, "测试用例批量删除失败，请稍后重试")