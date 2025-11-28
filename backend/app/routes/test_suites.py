from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models.models import db, TestSuite, User
from app.helpers.helpers import success_response, error_response, parse_pagination_params

# 创建Blueprint
bp = Blueprint('test_suites', __name__, url_prefix='/api/test-suites')


@bp.route('/', methods=['GET'])
@login_required
def get_test_suites():
    """获取测试套件列表，支持分页和筛选"""
    try:
        # 解析分页参数
        page, per_page = parse_pagination_params(request)
        
        # 基础查询
        query = TestSuite.query
        
        # 处理筛选条件
        if request.args.get('status'):
            query = query.filter_by(status=request.args['status'])
        
        if request.args.get('parent_id'):
            # 如果指定了parent_id，则返回该父套件下的子套件
            query = query.filter_by(parent_id=request.args['parent_id'])
        elif 'all' not in request.args:
            # 默认只返回顶级套件（parent_id为空）
            query = query.filter_by(parent_id=None)
        
        # 执行分页查询
        pagination = query.order_by(TestSuite.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 构造响应数据
        items = [suite.to_dict() for suite in pagination.items]
        
        return success_response({
            'items': items,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
    except Exception as e:
        return error_response(f'获取测试套件失败: {str(e)}', 500)


@bp.route('/<int:suite_id>', methods=['GET'])
@login_required
def get_test_suite(suite_id):
    """获取单个测试套件详情"""
    try:
        suite = TestSuite.query.get_or_404(suite_id)
        return success_response(suite.to_dict())
    except Exception as e:
        return error_response(f'获取测试套件详情失败: {str(e)}', 500)


@bp.route('/', methods=['POST'])
@login_required
def create_test_suite():
    """创建新的测试套件"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        if not data.get('suite_name'):
            return error_response('套件名称不能为空', 400)
        
        # 创建新套件
        new_suite = TestSuite(
            suite_name=data['suite_name'],
            description=data.get('description', ''),
            parent_id=data.get('parent_id'),
            status=data.get('status', 'active'),
            creator_id=current_user.id
        )
        
        db.session.add(new_suite)
        db.session.commit()
        
        return success_response(new_suite.to_dict(), 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'创建测试套件失败: {str(e)}', 500)


@bp.route('/<int:suite_id>', methods=['PUT'])
@login_required
def update_test_suite(suite_id):
    """更新测试套件信息"""
    try:
        suite = TestSuite.query.get_or_404(suite_id)
        data = request.get_json()
        
        # 更新字段
        if 'suite_name' in data:
            suite.suite_name = data['suite_name']
        if 'description' in data:
            suite.description = data['description']
        if 'parent_id' in data:
            # 检查是否会形成循环引用
            if data['parent_id'] is not None:
                parent = TestSuite.query.get(data['parent_id'])
                if parent:
                    # 简单检查是否会形成循环
                    current = parent
                    while current:
                        if current.id == suite_id:
                            return error_response('不能将套件设置为自己的子套件或间接子套件', 400)
                        current = current.parent
            suite.parent_id = data['parent_id']
        if 'status' in data:
            suite.status = data['status']
        
        db.session.commit()
        
        return success_response(suite.to_dict())
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新测试套件失败: {str(e)}', 500)


@bp.route('/<int:suite_id>', methods=['DELETE'])
@login_required
def delete_test_suite(suite_id):
    """删除测试套件"""
    try:
        suite = TestSuite.query.get_or_404(suite_id)
        
        # 检查是否有子套件
        if suite.children.count() > 0:
            return error_response('该套件包含子套件，无法删除', 400)
        
        # 检查是否有测试用例
        if suite.test_cases.count() > 0:
            return error_response('该套件包含测试用例，无法删除', 400)
        
        db.session.delete(suite)
        db.session.commit()
        
        return success_response({'message': '测试套件已成功删除'})
    except Exception as e:
        db.session.rollback()
        return error_response(f'删除测试套件失败: {str(e)}', 500)


@bp.route('/<int:suite_id>/tree', methods=['GET'])
@login_required
def get_suite_tree(suite_id=None):
    """获取测试套件的树形结构"""
    try:
        # 如果提供了suite_id，则从该套件开始构建树，否则构建完整的树
        if suite_id:
            root_suites = [TestSuite.query.get_or_404(suite_id)]
        else:
            root_suites = TestSuite.query.filter_by(parent_id=None).all()
        
        # 递归构建树
        def build_tree(suite):
            suite_dict = suite.to_dict()
            children = []
            for child in suite.children:
                children.append(build_tree(child))
            suite_dict['children'] = children
            return suite_dict
        
        tree_data = [build_tree(suite) for suite in root_suites]
        
        return success_response(tree_data)
    except Exception as e:
        return error_response(f'获取套件树结构失败: {str(e)}', 500)


@bp.route('/options', methods=['GET'])
@login_required
def get_suite_options():
    """获取测试套件选项列表，用于下拉选择"""
    try:
        suites = TestSuite.query.filter_by(status='active').all()
        
        # 递归构建选项树
        def build_options(suite, prefix=''):
            result = [{
                'value': suite.id,
                'label': f'{prefix}{suite.suite_name}'
            }]
            for child in suite.children:
                result.extend(build_options(child, prefix + '  └ '))
            return result
        
        options = []
        for root_suite in TestSuite.query.filter_by(parent_id=None).all():
            options.extend(build_options(root_suite))
        
        return success_response(options)
    except Exception as e:
        return error_response(f'获取套件选项失败: {str(e)}', 500)