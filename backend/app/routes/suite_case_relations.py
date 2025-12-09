from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.models.models import db, TestSuite, TestCase
from app.utils.auth import role_required
from app.utils.helpers import success_response, error_response

# 创建蓝图
bp = Blueprint('suite_case_relations', __name__, url_prefix='/api/suite-case-relations')


@bp.route('/<int:suite_id>/cases', methods=['GET'])
@login_required
@role_required(['manager', 'tester', 'admin'])
def get_suite_cases(suite_id):
    """
    获取测试套件中的测试用例列表
    """
    try:
        # 查询套件
        suite = TestSuite.query.get_or_404(suite_id, description='测试套件不存在')
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        priority = request.args.get('priority')
        status = request.args.get('status')
        search = request.args.get('search')
        
        # 构建查询
        query = TestCase.query.filter_by(suite_id=suite_id)
        
        # 应用过滤条件
        if priority:
            query = query.filter_by(priority=priority)
        if status:
            query = query.filter_by(status=status)
        if search:
            query = query.filter(TestCase.case_name.like(f'%{search}%'))
        
        # 分页查询
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        cases = pagination.items
        
        # 转换为字典列表
        cases_data = [case.to_dict() for case in cases]
        
        return success_response({
            'items': cases_data,
            'total': pagination.total,
            'page': page,
            'page_size': page_size,
            'total_pages': pagination.pages
        })
    except Exception as e:
        return error_response(500, str(e))


@bp.route('/<int:suite_id>/add-cases', methods=['POST'])
@login_required
@role_required(['manager', 'tester', 'admin'])
def add_cases_to_suite(suite_id):
    """
    向测试套件中添加测试用例
    """
    try:
        # 查询套件
        suite = TestSuite.query.get_or_404(suite_id, description='测试套件不存在')
        
        # 获取请求数据
        data = request.get_json()
        case_ids = data.get('case_ids', [])
        
        if not case_ids:
            return error_response(400, '请提供要添加的测试用例ID列表')
        
        # 检查用例是否存在且属于同一项目
        cases = TestCase.query.filter(
            TestCase.id.in_(case_ids),
            TestCase.project_id == suite.project_id
        ).all()
        
        existing_case_ids = [case.id for case in cases]
        missing_ids = set(case_ids) - set(existing_case_ids)
        
        if missing_ids:
            return error_response(400, f'测试用例不存在或不属于同一项目: {list(missing_ids)}')
        
        # 更新用例的套件ID
        for case in cases:
            case.suite_id = suite_id
        
        db.session.commit()
        
        return success_response({
            'message': '成功添加测试用例到测试套件',
            'added_count': len(cases)
        })
    except Exception as e:
        db.session.rollback()
        return error_response(500, str(e))


@bp.route('/<int:suite_id>/remove-cases', methods=['POST'])
@login_required
@role_required(['manager', 'tester', 'admin'])
def remove_cases_from_suite(suite_id):
    """
    从测试套件中移除测试用例
    """
    try:
        # 检查套件是否存在
        suite = TestSuite.query.get_or_404(suite_id, description='测试套件不存在')
        
        # 获取请求数据
        data = request.get_json()
        case_ids = data.get('case_ids', [])
        
        if not case_ids:
            return error_response(400, '请提供要移除的测试用例ID列表')
        
        # 查询属于该套件的用例
        cases = TestCase.query.filter(
            TestCase.id.in_(case_ids),
            TestCase.suite_id == suite_id
        ).all()
        
        # 更新用例的套件ID为None
        for case in cases:
            case.suite_id = None
        
        db.session.commit()
        
        return success_response({
            'message': '成功从测试套件中移除测试用例',
            'removed_count': len(cases)
        })
    except Exception as e:
        db.session.rollback()
        return error_response(500, str(e))


@bp.route('/<int:suite_id>/available-cases', methods=['GET'])
@login_required
@role_required(['manager', 'tester', 'admin'])
def get_available_cases(suite_id):
    """
    获取可添加到测试套件的测试用例（属于同一项目但未分配到其他套件的用例）
    """
    try:
        # 查询套件
        suite = TestSuite.query.get_or_404(suite_id, description='测试套件不存在')
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        priority = request.args.get('priority')
        status = request.args.get('status')
        search = request.args.get('search')
        
        # 构建查询：属于同一项目但未分配到任何套件的用例
        query = TestCase.query.filter(
            TestCase.project_id == suite.project_id,
            TestCase.suite_id.is_(None)
        )
        
        # 应用过滤条件
        if priority:
            query = query.filter_by(priority=priority)
        if status:
            query = query.filter_by(status=status)
        if search:
            query = query.filter(TestCase.case_name.like(f'%{search}%'))
        
        # 分页查询
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        cases = pagination.items
        
        # 转换为字典列表
        cases_data = [case.to_dict() for case in cases]
        
        return success_response({
            'items': cases_data,
            'total': pagination.total,
            'page': page,
            'page_size': page_size,
            'total_pages': pagination.pages
        })
    except Exception as e:
        return error_response(500, str(e))


@bp.route('/<int:suite_id>/move-cases', methods=['POST'])
@login_required
@role_required(['manager', 'tester', 'admin'])
def move_cases_between_suites(suite_id):
    """
    将测试用例从一个套件移动到另一个套件
    """
    try:
        # 检查源套件是否存在
        source_suite = TestSuite.query.get_or_404(suite_id, description='源测试套件不存在')
        
        # 获取请求数据
        data = request.get_json()
        case_ids = data.get('case_ids', [])
        target_suite_id = data.get('target_suite_id')
        
        if not case_ids:
            return error_response(400, '请提供要移动的测试用例ID列表')
        
        if not target_suite_id:
            return error_response(400, '请提供目标测试套件ID')
        
        # 检查目标套件是否存在且属于同一项目
        target_suite = TestSuite.query.filter_by(
            id=target_suite_id,
            project_id=source_suite.project_id
        ).first_or_404(description='目标测试套件不存在或不属于同一项目')
        
        # 查询属于源套件的用例
        cases = TestCase.query.filter(
            TestCase.id.in_(case_ids),
            TestCase.suite_id == suite_id
        ).all()
        
        # 更新用例的套件ID
        for case in cases:
            case.suite_id = target_suite_id
        
        db.session.commit()
        
        return success_response({
            'message': '成功移动测试用例',
            'moved_count': len(cases),
            'source_suite_id': suite_id,
            'target_suite_id': target_suite_id
        })
    except Exception as e:
        db.session.rollback()
        return error_response(500, str(e))


# 模块相关功能已移除，模块信息通过套件关联获取