from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models.models import db, TestSuite, User
from app.utils.helpers import success_response, error_response, get_pagination_params

# 创建Blueprint
bp = Blueprint('test_suites', __name__, url_prefix='/api/test-suites')


@bp.route('/', methods=['GET'])
@login_required
def get_test_suites():
    """获取测试套件列表，支持分页、筛选和树形结构"""
    try:
        # 检查是否需要返回树形结构
        with_children = request.args.get('with_children', 'false').lower() == 'true'
        
        if with_children:
            # 返回完整的树形结构
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
        else:
            # 解析分页参数
            page, per_page = get_pagination_params()
            
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
        return error_response(500, f'获取测试套件失败: {str(e)}')


@bp.route('/<int:suite_id>', methods=['GET'])
@login_required
def get_test_suite(suite_id):
    """获取单个测试套件详情"""
    try:
        suite = TestSuite.query.get_or_404(suite_id)
        return success_response(suite.to_dict())
    except Exception as e:
        return error_response(500, f'获取测试套件详情失败: {str(e)}')


def get_suite_depth(suite_id):
    """计算测试套件的深度"""
    depth = 0
    current = TestSuite.query.get(suite_id)
    while current and current.parent_id:
        depth += 1
        current = current.parent
    return depth

@bp.route('/', methods=['POST'])
@login_required
def create_test_suite():
    """创建新的测试套件"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        if not data.get('suite_name'):
            return error_response(400, '套件名称不能为空')
        
        # 验证type字段
        suite_type = data.get('type', 'folder')
        if suite_type not in ['folder', 'suite']:
            return error_response(400, '套件类型无效，只能是folder或suite')
        
        parent_id = data.get('parent_id')
        
        # 计算深度
        depth = 0
        if parent_id is not None:
            parent_suite = TestSuite.query.get(parent_id)
            if not parent_suite:
                return error_response(400, '父套件不存在')
            
            # 如果有父套件，验证父套件类型
            if parent_suite.type != 'folder':
                return error_response(400, '只能在文件夹中创建子套件')
            
            # 计算新套件的深度
            depth = get_suite_depth(parent_id) + 1
            
            # 限制深度不超过5层
            if depth >= 5:
                return error_response(400, '测试套件深度不能超过5层')
            
            # 最深一层只能是用例集
            if depth == 4 and suite_type != 'suite':
                return error_response(400, '最深一层只能创建用例集')
        
        # 计算新节点的sort_order，默认添加到尾部
        # 查找同级别最大的sort_order值
        max_sort_order = db.session.query(db.func.max(TestSuite.sort_order))
        if parent_id is not None:
            max_sort_order = max_sort_order.filter_by(parent_id=parent_id)
        else:
            max_sort_order = max_sort_order.filter_by(parent_id=None)
        
        max_sort_order = max_sort_order.scalar() or 0
        new_sort_order = max_sort_order + 1
        
        # 创建新套件
        new_suite = TestSuite(
            suite_name=data['suite_name'],
            description=data.get('description', ''),
            parent_id=parent_id,
            status=data.get('status', 'active'),
            type=suite_type,
            creator_id=current_user.id,
            project_id=data.get('project_id'),
            version_requirement_id=data.get('version_requirement_id'),
            iteration_id=data.get('iteration_id'),
            sort_order=new_sort_order
        )
        
        db.session.add(new_suite)
        db.session.commit()
        
        return success_response(new_suite.to_dict(), 201)
    except Exception as e:
        db.session.rollback()
        return error_response(500, f'创建测试套件失败: {str(e)}')


@bp.route('/<int:suite_id>', methods=['PUT'])
@login_required
def update_test_suite(suite_id):
    """更新测试套件信息"""
    try:
        suite = TestSuite.query.get_or_404(suite_id)
        data = request.get_json()
        
        # 记录原始值，用于后续排序调整
        original_parent_id = suite.parent_id
        original_sort_order = suite.sort_order
        original_type = suite.type
        
        # 更新字段
        if 'suite_name' in data:
            suite.suite_name = data['suite_name']
        if 'description' in data:
            suite.description = data['description']
        if 'parent_id' in data:
            # 检查是否会形成循环引用
            new_parent_id = data['parent_id']
            if new_parent_id is not None:
                parent = TestSuite.query.get(new_parent_id)
                if parent:
                    # 简单检查是否会形成循环
                    current = parent
                    while current:
                        if current.id == suite_id:
                            return error_response(400, '不能将套件设置为自己的子套件或间接子套件')
                        current = current.parent
                    # 验证父套件类型必须是folder
                    if parent.type != 'folder':
                        return error_response(400, '只能将套件移动到文件夹中')
                    
                    # 计算新的深度
                    new_depth = get_suite_depth(new_parent_id) + 1
                    # 限制深度不超过5层
                    if new_depth >= 5:
                        return error_response(400, '测试套件深度不能超过5层')
                    
                    # 最深一层只能是用例集
                    if new_depth == 4 and suite.type != 'suite':
                        return error_response(400, '最深一层只能是用例集')
            else:
                # 根套件深度为0
                new_depth = 0
            suite.parent_id = new_parent_id
        if 'status' in data:
            suite.status = data['status']
        if 'sort_order' in data:
            suite.sort_order = data['sort_order']
        if 'type' in data:
            new_type = data['type']
            if new_type not in ['folder', 'suite']:
                return error_response(400, '套件类型无效，只能是folder或suite')
            
            # 计算当前套件的深度
            depth = get_suite_depth(suite.id)
            
            # 最深一层只能是用例集
            if depth == 4 and new_type != 'suite':
                return error_response(400, '最深一层只能是用例集')
            
            # 验证类型变更的合法性
            if new_type == 'suite':
                # 如果要改为用例集，必须没有子套件
                if len(suite.children) > 0:
                    return error_response(400, '包含子套件的套件不能改为用例集')
            
            # 如果要改为文件夹，需要确保父套件类型合法
            if new_type == 'folder' and suite.parent_id is not None:
                parent = TestSuite.query.get(suite.parent_id)
                if parent and parent.type != 'folder':
                    return error_response(400, '只能在文件夹中创建文件夹')
            
            suite.type = new_type
        
        # 移除评审相关字段的直接更新，评审状态由评审任务管理
        
        # 更新项目相关信息
        if 'project_id' in data:
            suite.project_id = data['project_id']
        if 'version_requirement_id' in data:
            suite.version_requirement_id = data['version_requirement_id']
        if 'iteration_id' in data:
            suite.iteration_id = data['iteration_id']
        
        # 如果父级或排序发生变化，需要重新调整排序
        if ('parent_id' in data and data['parent_id'] != original_parent_id) or \
           ('sort_order' in data and data['sort_order'] != original_sort_order):
            
            # 处理父级变化的情况：如果父级变化，先将原父级下的节点重新排序
            if data['parent_id'] != original_parent_id:
                # 原父级下的节点重新排序
                original_siblings = TestSuite.query.filter_by(parent_id=original_parent_id).all()
                original_siblings.sort(key=lambda x: x.sort_order)
                for i, sibling in enumerate(original_siblings):
                    sibling.sort_order = i + 1
                
                # 如果移动到新的父节点，将当前节点的sort_order设置为新父节点下的最大值+1
                max_sort_order = db.session.query(db.func.max(TestSuite.sort_order))
                max_sort_order = max_sort_order.filter_by(parent_id=suite.parent_id).scalar() or 0
                suite.sort_order = max_sort_order + 1
            
            # 获取所有新的同级节点，包括当前节点
            # 注意：这里不能直接从数据库查询，因为当前节点的sort_order还没有提交到数据库
            # 我们需要构建一个包含所有节点的列表，包括当前节点
            
            # 1. 获取除当前节点外的所有同级节点
            other_siblings = TestSuite.query.filter(
                TestSuite.parent_id == suite.parent_id,
                TestSuite.id != suite.id
            ).all()
            
            # 2. 创建完整的同级节点列表
            all_siblings = [suite] + other_siblings
            
            # 3. 按照sort_order排序
            all_siblings.sort(key=lambda x: (x.sort_order, 0 if x.id == suite_id else 1))
            
            # 4. 重新分配连续的sort_order值
            for i, sibling in enumerate(all_siblings):
                sibling.sort_order = i + 1
        
        db.session.commit()
        
        return success_response(suite.to_dict())
    except Exception as e:
        db.session.rollback()
        return error_response(500, f'更新测试套件失败: {str(e)}')


@bp.route('/<int:suite_id>/sync-reviewer', methods=['POST'])
@login_required
def sync_reviewer_to_cases(suite_id):
    """同步评审人到用例集下的所有用例（已废弃，评审人信息从评审任务中获取）"""
    try:
        # 获取测试套件
        suite = TestSuite.query.get_or_404(suite_id)
        
        # 检查是否为用例集
        if suite.type != 'suite':
            return error_response(400, '只有用例集才能同步评审人到用例')
        
        # 获取该用例集下的所有用例
        from app.models.models import TestCase
        cases = TestCase.query.filter_by(suite_id=suite_id).all()
        
        # 评审人信息从评审任务中获取，不再需要同步
        # 提交更改
        db.session.commit()
        
        return success_response({"message": f"评审人同步功能已废弃，评审人信息从评审任务中获取", "cases_count": len(cases)})
    except Exception as e:
        db.session.rollback()
        return error_response(500, f'同步评审人失败: {str(e)}')


@bp.route('/<int:suite_id>', methods=['DELETE'])
@login_required
def delete_test_suite(suite_id):
    """删除测试套件"""
    try:
        suite = TestSuite.query.get_or_404(suite_id)
        
        # 检查是否有子套件
        if suite.children.count() > 0:
            return error_response(400, '该套件包含子套件，无法删除')
        
        # 检查是否有测试用例
        if suite.test_cases.count() > 0:
            return error_response(400, '该套件包含测试用例，无法删除')
        
        db.session.delete(suite)
        db.session.commit()
        
        return success_response({'message': '测试套件已成功删除'})
    except Exception as e:
        db.session.rollback()
        return error_response(500, f'删除测试套件失败: {str(e)}')


@bp.route('/tree', methods=['GET'])
@login_required
def get_suite_tree():
    """获取完整的测试套件树形结构"""
    try:
        root_suites = TestSuite.query.filter_by(parent_id=None).order_by(TestSuite.sort_order).all()
        
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
        return error_response(500, f'获取套件树结构失败: {str(e)}')


@bp.route('/<int:suite_id>/tree', methods=['GET'])
@login_required
def get_suite_tree_by_id(suite_id):
    """获取指定测试套件的树形结构"""
    try:
        suite = TestSuite.query.get_or_404(suite_id)
        
        # 递归构建树
        def build_tree(suite):
            suite_dict = suite.to_dict()
            children = []
            for child in suite.children:
                children.append(build_tree(child))
            suite_dict['children'] = children
            return suite_dict
        
        tree_data = build_tree(suite)
        
        return success_response([tree_data])
    except Exception as e:
        return error_response(500, f'获取套件树结构失败: {str(e)}')


@bp.route('/options', methods=['GET'])
@login_required
def get_suite_options():
    """获取测试套件选项列表，用于下拉选择"""
    try:
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
        for root_suite in TestSuite.query.filter_by(parent_id=None).order_by(TestSuite.sort_order).all():
            options.extend(build_options(root_suite))
        
        return success_response(options)
    except Exception as e:
        return error_response(500, f'获取套件选项失败: {str(e)}')


@bp.route('/<int:suite_id>/test-cases', methods=['GET'])
@login_required
def get_suite_test_cases(suite_id):
    """获取测试套件中的测试用例"""
    try:
        from app.models.models import TestCase
        from app.utils.helpers import get_pagination_params
        
        # 解析分页参数
        page, size = get_pagination_params()
        
        # 构建查询
        query = TestCase.query.filter_by(suite_id=suite_id)
        
        # 分页
        pagination = query.paginate(
            page=page, per_page=size, error_out=False
        )
        
        test_cases = [test_case.to_dict() for test_case in pagination.items]
        
        return success_response({
            'items': test_cases,
            'total': pagination.total,
            'page': page,
            'per_page': size
        })
    except Exception as e:
        return error_response(500, f'获取套件测试用例失败: {str(e)}')