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
    module = request.args.get('module', '').strip()
    suite_id = request.args.get('suite_id', '').strip()
    
    # 构建查询
    query = TestCase.query
    
    # 搜索过滤
    if search:
        query = query.filter(
            TestCase.case_name.contains(search) |
            TestCase.description.contains(search) |
            TestCase.preconditions.contains(search)
        )
    
    # 优先级过滤
    if priority:
        query = query.filter(TestCase.priority == priority)
    
    # 状态过滤
    if status:
        query = query.filter(TestCase.status == status)
    
    # 模块过滤
    if module:
        query = query.filter(TestCase.module == module)
    
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
@validate_json_data(['case_name', 'priority', 'module'])
def create_test_case():
    """创建测试用例"""
    data = request.get_json()
    
    # 验证套件是否存在
    if data.get('suite_id'):
        suite = TestSuite.query.get(data['suite_id'])
        if not suite:
            return error_response(400, "指定的测试套件不存在")
    
    test_case = TestCase(
        case_name=data['case_name'],
        description=data.get('description', ''),
        preconditions=data.get('preconditions', ''),
        steps=data.get('steps', ''),
        expected_result=data.get('expected_result', ''),
        actual_result=data.get('actual_result', ''),
        priority=data['priority'],
        status=data.get('status', 'active'),
        module=data['module'],
        author_id=current_user.id,
        suite_id=data.get('suite_id'),
        xmind_data=data.get('xmind_data')
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
    if 'case_name' in data:
        test_case.case_name = data['case_name']
    
    if 'description' in data:
        test_case.description = data['description']
    
    if 'preconditions' in data:
        test_case.preconditions = data['preconditions']
    
    if 'steps' in data:
        test_case.steps = data['steps']
    
    if 'expected_result' in data:
        test_case.expected_result = data['expected_result']
    
    if 'actual_result' in data:
        test_case.actual_result = data['actual_result']
    
    if 'priority' in data:
        test_case.priority = data['priority']
    
    if 'status' in data:
        test_case.status = data['status']
    
    if 'module' in data:
        test_case.module = data['module']
    
    if 'suite_id' in data:
        # 验证套件是否存在
        if data['suite_id'] is not None:
            suite = TestSuite.query.get(data['suite_id'])
            if not suite:
                return error_response(400, "指定的测试套件不存在")
        test_case.suite_id = data['suite_id']
    
    if 'xmind_data' in data:
         test_case.xmind_data = data['xmind_data']
    
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
        {'value': 'active', 'label': '激活'},
        {'value': 'inactive', 'label': '停用'},
        {'value': 'draft', 'label': '草稿'}
    ]
    
    return success_response({
        'status_options': status_options
    })


@bp.route('/modules', methods=['GET'])
@login_required
def get_modules():
    """获取模块列表"""
    modules = [
        {'value': 'login', 'label': '登录模块'},
        {'value': 'user_management', 'label': '用户管理'},
        {'value': 'device_management', 'label': '设备管理'},
        {'value': 'test_management', 'label': '测试管理'},
        {'value': 'bug_management', 'label': '缺陷管理'},
        {'value': 'tools', 'label': '工具集'},
        {'value': 'system', 'label': '系统设置'}
    ]
    
    return success_response({
        'modules': modules
    })


@bp.route('/xmind/import', methods=['POST'])
@login_required
def import_xmind():
    """导入xmind文件，创建测试用例"""
    data = request.get_json()
    
    # 验证必要字段
    if not data.get('xmind_data'):
        return error_response(400, "xmind数据不能为空")
    
    if not data.get('suite_id'):
        return error_response(400, "请指定测试套件")
    
    # 验证套件是否存在
    suite = TestSuite.query.get(data['suite_id'])
    if not suite:
        return error_response(400, "指定的测试套件不存在")
    
    try:
        # 创建一个基于xmind数据的测试用例
        new_case = TestCase(
            case_name=data.get('case_name', '从XMind导入的测试用例'),
            description='从XMind导入',
            module=data.get('module', '默认模块'),
            priority=data.get('priority', 'medium'),
            status=data.get('status', 'draft'),
            author_id=current_user.id,
            suite_id=data['suite_id'],
            xmind_data=data['xmind_data']
        )
        
        db.session.add(new_case)
        db.session.commit()
        
        log_user_action("导入XMind测试用例", f"用例名称: {new_case.case_name}")
        
        return success_response({
            'test_case': new_case.to_dict()
        }, "XMind测试用例导入成功")
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, "XMind测试用例导入失败，请稍后重试")


@bp.route('/<int:case_id>/export/xmind', methods=['GET'])
@login_required
def export_xmind(case_id):
    """导出测试用例为xmind格式"""
    test_case = TestCase.query.get_or_404(case_id)
    
    if not test_case.xmind_data:
        return error_response(400, "该测试用例没有xmind数据")
    
    log_user_action("导出XMind测试用例", f"用例ID: {case_id}")
    
    return success_response({
        'case_id': test_case.id,
        'case_name': test_case.case_name,
        'xmind_data': test_case.xmind_data
    })