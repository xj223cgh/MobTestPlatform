from flask import Blueprint, request, session
from flask_login import login_user, logout_user, login_required, current_user

from app.models.models import User, db
from app.utils.helpers import (
    success_response, error_response, log_user_action,
    validate_json_data, validate_phone, validate_username
)
from app.utils.auth_utils import SessionManager, PasswordManager, TwoFactorAuth
from app.utils.auth import PermissionManager, rate_limiter

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['POST', 'GET'])
@rate_limiter.rate_limit(limit=5, window=60)  # 1分钟内最多5次登录尝试
def login():
    """用户登录"""
    # 处理GET请求（Flask-Login重定向过来的）
    if request.method == 'GET':
        # 如果已经登录，返回已登录状态
        if current_user.is_authenticated:
            return success_response({"message": "Already logged in"}, "已登录")
        # 未登录返回未授权错误
        return error_response(401, "请登录")
    
    # 处理POST请求（正常登录）
    # 检查请求是否有JSON数据
    if not request.is_json:
        return error_response(400, "请求必须是JSON格式")
    
    data = request.get_json()
    # 验证必要字段
    if not all(key in data for key in ['username', 'password']):
        return error_response(400, "缺少必要字段")
    
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return error_response(400, "用户名和密码不能为空")
    
    # 查找用户
    # 先检查用户是否存在
    user = User.query.filter(
        (User.username == username) | (User.phone == username)
    ).first()
    
    if not user:
        return error_response(401, "用户名不存在")
    
    # 用户存在，检查密码
    if not user.check_password(password):
        return error_response(401, "密码错误")
    
    if not user.is_active:
        return error_response(401, "账户已被禁用，请联系管理员解除禁制")
    
    # 创建会话
    from flask_login import login_user
    login_user(user, remember=True)
    
    # 记录登录日志
    log_user_action("登录", f"IP: {request.remote_addr}")
    
    return success_response({
        'user': user.to_dict(),
        'permissions': PermissionManager.get_user_permissions(user)
    }, "登录成功")


@bp.route('/logout', methods=['POST', 'GET'])
def logout():
    """用户登出"""
    try:
        # 无论用户是否登录都尝试登出
        username = None
        if current_user.is_authenticated:
            username = current_user.username
            from flask_login import logout_user
            logout_user()
            log_user_action("用户登出", f"用户名: {username}")
        else:
            # 即使未认证也清除可能的session数据
            from flask_login import logout_user
            logout_user()
        
        return success_response(message="登出成功")
        
    except Exception as e:
        # 即使出错也尝试清除session
        try:
            from flask_login import logout_user
            logout_user()
        except:
            pass
        
        # 记录错误但不影响用户登出
        import logging
        logging.error(f"Logout error: {str(e)}")
        
        return success_response(message="登出成功")


@bp.route('/register', methods=['POST'])
@validate_json_data(['username', 'phone', 'password', 'real_name'])
def register():
    """用户注册"""
    data = request.get_json()
    username = data.get('username', '').strip()
    phone = data.get('phone', '').strip()
    password = data.get('password', '')
    real_name = data.get('real_name', '').strip()
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
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return error_response(400, "用户名已存在")
    
    # 检查手机号是否已存在
    if User.query.filter_by(phone=phone).first():
        return error_response(400, "手机号已注册")
    
    # 创建新用户（默认为admin角色）
    user = User(
        username=username,
        phone=phone,
        real_name=real_name,
        gender=gender,
        department=department,
        role='admin'  # 新注册用户默认为实习生角色
    )
    user.set_password(password)
    
    try:
        db.session.add(user)
        db.session.commit()
        
        log_user_action("注册", f"新用户: {username}")
        
        return success_response({
            'user': user.to_dict()
        }, "注册成功")
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, "注册失败，请稍后重试")


@bp.route('/current-user', methods=['GET'])
@login_required
def get_current_user():
    """获取当前登录用户信息"""
    return success_response({
        'user': current_user.to_dict()
    })


@bp.route('/change-password', methods=['POST'])
@login_required
@validate_json_data(['old_password', 'new_password'])
def change_password():
    """修改密码"""
    data = request.get_json()
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')
    
    if not old_password or not new_password:
        return error_response(400, "原密码和新密码不能为空")
    
    if len(new_password) < 6:
        return error_response(400, "新密码长度不能少于6位")
    
    # 验证原密码
    if not current_user.check_password(old_password):
        return error_response(400, "原密码错误")
    
    # 更新密码
    current_user.set_password(new_password)
    
    try:
        db.session.commit()
        log_user_action("修改密码")
        return success_response(message="密码修改成功")
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, "密码修改失败，请稍后重试")


@bp.route('/check-session', methods=['GET'])
def check_session():
    """检查会话状态"""
    from flask_login import current_user
    
    if current_user.is_authenticated:
        return success_response({
            'authenticated': True,
            'user': current_user.to_dict()
        })
    else:
        return success_response({
            'authenticated': False
        })


@bp.route('/forgot-password', methods=['POST'])
@rate_limiter.rate_limit(limit=3, window=300)  # 5分钟内最多3次请求
@validate_json_data(['email'])
def forgot_password():
    """忘记密码"""
    data = request.get_json()
    email = data['email'].strip()
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return error_response(404, "邮箱不存在")
    
    # 生成重置令牌
    reset_token = PasswordManager.generate_reset_token(user.id)
    
    # TODO: 发送重置邮件
    # 这里应该发送包含重置链接的邮件
    
    log_user_action("请求密码重置", f"邮箱: {email}")
    
    return success_response(message="密码重置邮件已发送")


@bp.route('/reset-password', methods=['POST'])
@validate_json_data(['token', 'password'])
def reset_password():
    """重置密码"""
    data = request.get_json()
    token = data['token']
    password = data['password']
    
    # 验证令牌
    user_id = PasswordManager.verify_reset_token(token)
    if not user_id:
        return error_response(400, "无效或过期的重置令牌")
    
    # 验证密码强度
    is_valid, message = PasswordManager.validate_password(password)
    if not is_valid:
        return error_response(400, message)
    
    # 更新密码
    user = User.query.get(user_id)
    user.set_password(password)
    
    try:
        db.session.commit()
        log_user_action("密码重置成功", f"用户ID: {user_id}")
        return success_response(message="密码重置成功")
    except Exception as e:
        db.session.rollback()
        return error_response(500, "密码重置失败，请稍后重试")


@bp.route('/enable-2fa', methods=['POST'])
@login_required
def enable_2fa():
    """启用双因素认证"""
    # 生成密钥
    secret = TwoFactorAuth.generate_secret()
    
    # 生成二维码
    qr_code = TwoFactorAuth.generate_qr_code(current_user.email, secret)
    
    # 临时保存密钥（等待验证）
    session['2fa_secret'] = secret
    
    return success_response({
        'secret': secret,
        'qr_code': qr_code
    }, "双因素认证设置信息已生成")


@bp.route('/verify-2fa', methods=['POST'])
@login_required
@validate_json_data(['token'])
def verify_2fa():
    """验证双因素认证"""
    data = request.get_json()
    token = data['token']
    secret = session.get('2fa_secret')
    
    if not secret:
        return error_response(400, "请先启用双因素认证")
    
    if TwoFactorAuth.verify_token(secret, token):
        # 保存密钥到用户记录
        current_user.two_factor_secret = secret
        current_user.two_factor_enabled = True
        
        try:
            db.session.commit()
            session.pop('2fa_secret', None)
            
            log_user_action("启用双因素认证", f"用户ID: {current_user.id}")
            return success_response(message="双因素认证启用成功")
        except Exception as e:
            db.session.rollback()
            return error_response(500, "双因素认证启用失败")
    else:
        return error_response(400, "验证码错误")


@bp.route('/disable-2fa', methods=['POST'])
@login_required
@validate_json_data(['password', 'token'])
def disable_2fa():
    """禁用双因素认证"""
    data = request.get_json()
    password = data['password']
    token = data['token']
    
    # 验证密码
    if not current_user.check_password(password):
        return error_response(400, "密码错误")
    
    # 验证2FA令牌
    if not TwoFactorAuth.verify_token(current_user.two_factor_secret, token):
        return error_response(400, "验证码错误")
    
    # 禁用2FA
    current_user.two_factor_enabled = False
    current_user.two_factor_secret = None
    
    try:
        db.session.commit()
        log_user_action("禁用双因素认证", f"用户ID: {current_user.id}")
        return success_response(message="双因素认证已禁用")
    except Exception as e:
        db.session.rollback()
        return error_response(500, "双因素认证禁用失败")


@bp.route('/permissions', methods=['GET'])
@login_required
def get_permissions():
    """获取当前用户权限"""
    return success_response({
        'permissions': [],
        'permission_info': []
    })