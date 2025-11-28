from flask import Blueprint, request
from flask_login import login_required, current_user

from app.models.models import User, db
from app.utils.helpers import (
    success_response, error_response, validate_phone, 
    validate_username, get_pagination_params, log_user_action,
    validate_json_data
)

bp = Blueprint('users', __name__)


@bp.route('', methods=['GET'])
@login_required
def get_users():
    """获取用户列表"""
    page, size = get_pagination_params()
    search = request.args.get('search', '').strip()
    role = request.args.get('role', '').strip()
    is_active_param = request.args.get('is_active', '').strip()
    
    # 构建查询
    query = User.query
    
    # 搜索过滤
    if search:
        # 用户名查询使用BINARY关键字确保严格区分大小写
        # 真实姓名和手机号保持不区分大小写的contains查询
        query = query.filter(
            db.or_(
                db.text(f'BINARY "username" LIKE :username_pattern').params(username_pattern=f'%{search}%'),
                User.real_name.contains(search),
                User.phone.contains(search)
            )
        )
    
    # 角色过滤
    if role:
        query = query.filter(User.role == role)
    
    # 状态过滤
    if is_active_param:
        # 将字符串转换为布尔值
        is_active = is_active_param.lower() == 'true'
        query = query.filter(User.is_active == is_active)
    
    # 分页
    pagination = query.paginate(
        page=page, per_page=size, error_out=False
    )
    
    users = [user.to_dict() for user in pagination.items]
    
    return success_response({
        'users': users,
        'pagination': {
            'page': page,
            'size': size,
            'total': pagination.total,
            'pages': pagination.pages
        }
    })


@bp.route('/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    """获取用户详情"""
    user = User.query.get_or_404(user_id)
    return success_response({
        'user': user.to_dict()
    })


@bp.route('', methods=['POST'])
@login_required
@validate_json_data(['username', 'phone', 'password', 'real_name', 'role'])
def create_user():
    """创建用户"""
    data = request.get_json()
    username = data.get('username', '').strip()
    phone = data.get('phone', '').strip()
    password = data.get('password', '')
    real_name = data.get('real_name', '').strip()
    role = data.get('role', 'admin')
    gender = data.get('gender', 'other')
    department = data.get('department', '').strip()
    
    # 验证输入
    if not validate_username(username):
        return error_response(400, "用户名长度必须在3-14个字节之间")
    
    if not validate_phone(phone):
        return error_response(400, "手机号格式不正确")
    
    if len(password) < 6:
        return error_response(400, "密码长度不能少于6位")
    
    if not real_name:
        return error_response(400, "真实姓名不能为空")
    
    if role not in ['super', 'manager', 'tester', 'admin']:
        return error_response(400, "无效的角色类型")
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return error_response(400, "用户名已存在")
    
    # 检查手机号是否已存在
    if User.query.filter_by(phone=phone).first():
        return error_response(400, "手机号已注册")
    
    # 创建新用户
    user = User(
        username=username,
        phone=phone,
        real_name=real_name,
        gender=gender,
        department=department,
        role=role
    )
    user.set_password(password)
    
    try:
        db.session.add(user)
        db.session.commit()
        
        log_user_action("创建用户", f"用户名: {username}, 角色: {role}")
        
        return success_response({
            'user': user.to_dict()
        }, "用户创建成功")
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, "用户创建失败，请稍后重试")


@bp.route('/<int:user_id>', methods=['PUT'])
@login_required
@validate_json_data(['real_name'])
def update_user(user_id):
    """更新用户信息"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    # 更新字段
    if 'real_name' in data:
        real_name = data['real_name'].strip()
        if not real_name:
            return error_response(400, "真实姓名不能为空")
        user.real_name = real_name
    
    if 'gender' in data:
        gender = data['gender']
        if gender in ['male', 'female', 'other']:
            user.gender = gender
    
    if 'department' in data:
        user.department = data['department'].strip()
    
    if 'phone' in data:
        phone = data['phone'].strip()
        if not validate_phone(phone):
            return error_response(400, "手机号格式不正确")
        
        # 检查手机号是否已被其他用户使用
        existing_user = User.query.filter(
            User.phone == phone, User.id != user_id
        ).first()
        if existing_user:
            return error_response(400, "手机号已被其他用户使用")
        
        user.phone = phone
    
    if 'role' in data:
        role = data['role']
        if role not in ['super', 'manager', 'tester', 'admin']:
            return error_response(400, "无效的角色类型")
        
        user.role = role
    
    if 'is_active' in data:
        user.is_active = data['is_active']
    
    try:
        db.session.commit()
        
        log_user_action("更新用户", f"用户ID: {user_id}")
        
        return success_response({
            'user': user.to_dict()
        }, "用户信息更新成功")
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, "用户信息更新失败，请稍后重试")


@bp.route('/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    """删除用户"""
    user = User.query.get_or_404(user_id)
    
    try:
        db.session.delete(user)
        db.session.commit()
        
        log_user_action("删除用户", f"用户名: {user.username}")
        
        return success_response(message="用户删除成功")
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, "用户删除失败，请稍后重试")


@bp.route('/<int:user_id>/reset-password', methods=['POST'])
@login_required
@validate_json_data(['new_password'])
def reset_user_password(user_id):
    """重置用户密码"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    new_password = data.get('new_password', '')
    
    if len(new_password) < 6:
        return error_response(400, "新密码长度不能少于6位")
    
    user.set_password(new_password)
    
    try:
        db.session.commit()
        
        log_user_action("重置密码", f"用户ID: {user_id}")
        
        return success_response(message="密码重置成功")
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, "密码重置失败，请稍后重试")


@bp.route('/<int:user_id>/toggle-status', methods=['POST'])
@login_required
def toggle_user_status(user_id):
    """切换用户状态（启用/禁用）"""
    user = User.query.get_or_404(user_id)
    
    # 切换用户状态
    user.is_active = not user.is_active
    
    try:
        db.session.commit()
        
        action = "禁用" if not user.is_active else "启用"
        log_user_action(f"{action}用户", f"用户ID: {user_id}, 用户名: {user.username}")
        
        return success_response({
            'user': user.to_dict()
        }, f"用户{action}成功")
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, "用户状态切换失败，请稍后重试")


@bp.route('/roles', methods=['GET'])
@login_required
def get_roles():
    """获取角色列表"""
    roles = [
        {'value': 'super', 'label': '超级管理员'},
        {'value': 'manager', 'label': '管理员'},
        {'value': 'tester', 'label': '测试人员'},
        {'value': 'admin', 'label': '实习生'}
    ]
    
    return success_response({
        'roles': roles
    })