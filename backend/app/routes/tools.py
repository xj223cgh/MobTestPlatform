from flask import Blueprint, request
from flask_login import login_required, current_user

from app.models.models import Tool, db
from app.utils.helpers import (
    success_response, error_response, get_pagination_params, log_user_action,
    validate_json_data
)

bp = Blueprint('tools', __name__)


@bp.route('', methods=['GET'])
@login_required
def get_tools():
    """获取工具列表"""
    page, size = get_pagination_params()
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    status = request.args.get('status', '').strip()
    
    # 构建查询
    query = Tool.query
    
    # 搜索过滤
    if search:
        query = query.filter(
            Tool.name.contains(search) |
            Tool.description.contains(search) |
            Tool.version.contains(search)
        )
    
    # 分类过滤
    if category:
        query = query.filter(Tool.category == category)
    
    # 状态过滤
    if status:
        query = query.filter(Tool.status == status)
    
    # 分页
    pagination = query.paginate(
        page=page, per_page=size, error_out=False
    )
    
    tools = [tool.to_dict() for tool in pagination.items]
    
    return success_response({
        'tools': tools,
        'pagination': {
            'page': page,
            'size': size,
            'total': pagination.total,
            'pages': pagination.pages
        }
    })


@bp.route('/<int:tool_id>', methods=['GET'])
@login_required
def get_tool(tool_id):
    """获取工具详情"""
    tool = Tool.query.get_or_404(tool_id)
    return success_response({
        'tool': tool.to_dict()
    })


@bp.route('', methods=['POST'])
@login_required
@validate_json_data(['name', 'category', 'path'])
def create_tool():
    """创建工具"""
    data = request.get_json()
    
    tool = Tool(
        name=data['name'],
        description=data.get('description', ''),
        version=data.get('version', '1.0.0'),
        category=data['category'],
        path=data['path'],
        parameters=data.get('parameters', ''),
        status=data.get('status', 'active'),
        created_by=current_user.id
    )
    
    try:
        db.session.add(tool)
        db.session.commit()
        
        log_user_action("创建工具", f"工具名称: {tool.name}")
        
        return success_response({
            'tool': tool.to_dict()
        }, "工具创建成功")
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, "工具创建失败，请稍后重试")


@bp.route('/<int:tool_id>', methods=['PUT'])
@login_required
def update_tool(tool_id):
    """更新工具"""
    tool = Tool.query.get_or_404(tool_id)
    data = request.get_json()
    
    # 更新字段
    if 'name' in data:
        tool.name = data['name']
    
    if 'description' in data:
        tool.description = data['description']
    
    if 'version' in data:
        tool.version = data['version']
    
    if 'category' in data:
        tool.category = data['category']
    
    if 'path' in data:
        tool.path = data['path']
    
    if 'parameters' in data:
        tool.parameters = data['parameters']
    
    if 'status' in data:
        tool.status = data['status']
    
    try:
        db.session.commit()
        
        log_user_action("更新工具", f"工具ID: {tool_id}")
        
        return success_response({
            'tool': tool.to_dict()
        }, "工具更新成功")
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, "工具更新失败，请稍后重试")


@bp.route('/<int:tool_id>', methods=['DELETE'])
@login_required
def delete_tool(tool_id):
    """删除工具"""
    tool = Tool.query.get_or_404(tool_id)
    
    try:
        db.session.delete(tool)
        db.session.commit()
        
        log_user_action("删除工具", f"工具名称: {tool.name}")
        
        return success_response(message="工具删除成功")
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, "工具删除失败，请稍后重试")


@bp.route('/<int:tool_id>/execute', methods=['POST'])
@login_required
def execute_tool(tool_id):
    """执行工具"""
    tool = Tool.query.get_or_404(tool_id)
    
    if tool.status != 'active':
        return error_response(400, "只能执行激活状态的工具")
    
    data = request.get_json() or {}
    custom_parameters = data.get('parameters', {})
    
    try:
        log_user_action("执行工具", f"工具名称: {tool.name}")
        
        # TODO: 这里应该调用实际的工具执行逻辑
        # 暂时模拟执行成功
        result = {
            'success': True,
            'message': '工具执行完成',
            'output': '执行结果输出...',
            'execution_time': '1.23s'
        }
        
        return success_response({
            'tool': tool.to_dict(),
            'result': result
        }, "工具执行完成")
        
    except Exception as e:
        return error_response(500, "工具执行失败，请稍后重试")


@bp.route('/category-options', methods=['GET'])
@login_required
def get_category_options():
    """获取工具分类选项"""
    category_options = [
        {'value': 'automation', 'label': '自动化测试'},
        {'value': 'performance', 'label': '性能测试'},
        {'value': 'security', 'label': '安全测试'},
        {'value': 'compatibility', 'label': '兼容性测试'},
        {'value': 'monitoring', 'label': '监控工具'},
        {'value': 'debugging', 'label': '调试工具'},
        {'value': 'utility', 'label': '实用工具'}
    ]
    
    return success_response({
        'category_options': category_options
    })


@bp.route('/status-options', methods=['GET'])
@login_required
def get_status_options():
    """获取状态选项"""
    status_options = [
        {'value': 'active', 'label': '激活'},
        {'value': 'inactive', 'label': '停用'},
        {'value': 'maintenance', 'label': '维护中'}
    ]
    
    return success_response({
        'status_options': status_options
    })