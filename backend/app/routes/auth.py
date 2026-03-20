"""认证路由：登录、登出、注册、密码重置、邮箱绑定。"""
import random
import string
from datetime import timedelta, datetime

from flask import Blueprint, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user

from app.models.models import User, db, SystemSetting, EmailVerifyCode, LOCAL_TIMEZONE
from app.utils.helpers import (
    success_response, error_response, log_user_action,
    validate_json_data, validate_phone, validate_username, validate_qq_email,
)
from app.utils.auth_utils import PasswordManager
from app.utils.auth import rate_limiter
from app.services.permission_service import get_user_permission_codes
from app.services.email_service import send_login_code, send_reset_password_link, send_bind_verify_code, send_unbind_verify_code

bp = Blueprint('auth', __name__)

# 安全设置中的 key
SECURITY_KEYS = {
    "password_policy": "password_policy",
    "login_failure_lock": "login_failure_lock",
    "session_timeout_minutes": "session_timeout_minutes",
}


def _get_password_policy():
    """从系统设置读取密码策略（JSON 数组），如 ["minLength","uppercase","numbers"]"""
    setting = SystemSetting.query.filter_by(setting_key=SECURITY_KEYS["password_policy"]).first()
    if not setting or not setting.setting_value:
        return []
    try:
        import json
        v = json.loads(setting.setting_value)
        return v if isinstance(v, list) else []
    except (ValueError, TypeError):
        return []


def _get_login_failure_lock_threshold():
    """从系统设置读取登录失败锁定次数，0 表示不锁定。"""
    setting = SystemSetting.query.filter_by(setting_key=SECURITY_KEYS["login_failure_lock"]).first()
    if not setting or setting.setting_value is None or str(setting.setting_value).strip() == "":
        return 0
    try:
        v = int(setting.setting_value)
        return v if 0 <= v <= 10 else 0
    except (ValueError, TypeError):
        return 0


@bp.route('/login', methods=['POST', 'GET'])
@rate_limiter.rate_limit(limit=5, window=60)  # 1分钟内最多5次登录尝试
def login():
    """用户登录"""
    # 处理GET请求（Flask-Login重定向过来的）
    if request.method == 'GET':
        if current_user.is_authenticated:
            return success_response({"message": "Already logged in"}, "Already logged in")
        # 未登录返回未授权错误，使用英文消息避免UnicodeEncodeError
        return error_response(401, "Please login")
    
    if not request.is_json:
        return error_response(400, "请求必须是JSON格式")
    
    data = request.get_json()
    if not all(key in data for key in ['username', 'password']):
        return error_response(400, "缺少必要字段")
    
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return error_response(400, "用户名和密码不能为空")
    
    user = User.query.filter(
        (User.username == username) | (User.phone == username)
    ).first()
    
    if not user:
        return error_response(401, "用户名或密码错误")
    
    # 登录失败锁定：检查是否在锁定期内
    lock_threshold = _get_login_failure_lock_threshold()
    now = datetime.now(LOCAL_TIMEZONE)
    if lock_threshold > 0 and getattr(user, "locked_until", None):
        locked_until = user.locked_until
        # 统一转为带时区的比较
        lock_time = locked_until if locked_until.tzinfo else locked_until.replace(tzinfo=LOCAL_TIMEZONE)
        if lock_time > now:
            return error_response(401, "账户已锁定，请稍后再试或联系管理员")
        user.failed_login_attempts = 0
        user.locked_until = None
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

    if not user.check_password(password):
        if lock_threshold > 0:
            user.failed_login_attempts = getattr(user, "failed_login_attempts", 0) + 1
            if user.failed_login_attempts >= lock_threshold:
                user.locked_until = now + timedelta(minutes=30)
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
            if user.failed_login_attempts >= lock_threshold:
                return error_response(401, "登录失败次数过多，账户已锁定30分钟，请稍后再试")
        return error_response(401, "用户名或密码错误")

    if not user.is_active:
        return error_response(401, "账户已被禁用，请联系管理员解除禁制")

    if lock_threshold > 0 and (getattr(user, "failed_login_attempts", 0) or getattr(user, "locked_until", None)):
        user.failed_login_attempts = 0
        user.locked_until = None
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
    
    # 从系统设置读取会话超时时间（分钟），无则用 .env 的 SESSION_TIMEOUT_MINUTES 默认值
    session_timeout_minutes = current_app.config.get('SESSION_TIMEOUT_MINUTES', 1440)
    setting = SystemSetting.query.filter_by(setting_key="session_timeout_minutes").first()
    if setting and setting.setting_value:
        try:
            v = int(setting.setting_value)
            if 30 <= v <= 10080:  # 30 分钟 ~ 7 天
                session_timeout_minutes = v
        except (ValueError, TypeError):
            pass
    current_app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=session_timeout_minutes)
    
    # 创建会话（启用永久会话以使用上面配置的超时时间）
    login_user(user, remember=True)
    session.permanent = True
    
    log_user_action("登录", f"IP: {request.remote_addr}")
    
    return success_response({
        'user': user.to_dict(),
        'permissions': get_user_permission_codes(user)
    }, "登录成功")


@bp.route('/send-login-code', methods=['POST'])
@rate_limiter.rate_limit(limit=5, window=60)  # 同一 IP 1 分钟内最多 5 次
def send_login_code_route():
    """发送 QQ 邮箱登录验证码（6 位数字，5 分钟有效）"""
    if not request.is_json:
        return error_response(400, "请求必须是 JSON 格式")
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    if not email:
        return error_response(400, "请输入邮箱")
    if not validate_qq_email(email):
        return error_response(400, "仅支持 QQ 邮箱（格式：QQ号@qq.com，如 123456789@qq.com）")
    user = User.query.filter_by(email=email).first()
    if not user:
        return error_response(400, "该邮箱未绑定账号，请使用密码登录或先在用户设置中绑定邮箱")
    code = ''.join(random.choices(string.digits, k=6))
    expires_at = datetime.now(LOCAL_TIMEZONE) + timedelta(minutes=5)
    try:
        EmailVerifyCode.query.filter_by(email=email, purpose='login').delete()
        record = EmailVerifyCode(email=email, code=code, purpose='login', expires_at=expires_at)
        db.session.add(record)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return error_response(500, "发送失败，请稍后重试")
    ok, send_err = send_login_code(email, code)
    if not ok:
        if send_err == "recipient_refused":
            return error_response(400, "该邮箱无法接收邮件，请检查邮箱是否正确或在用户设置中重新绑定为有效 QQ 邮箱")
        return error_response(500, "邮件发送失败，请稍后重试")
    return success_response(message="验证码已发送到您的邮箱，5 分钟内有效")


@bp.route('/login-by-email', methods=['POST'])
@rate_limiter.rate_limit(limit=5, window=60)
def login_by_email():
    """邮箱验证码登录"""
    if not request.is_json:
        return error_response(400, "请求必须是 JSON 格式")
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    code = (data.get('code') or '').strip()
    if not email:
        return error_response(400, "请输入邮箱")
    if not validate_qq_email(email):
        return error_response(400, "仅支持 QQ 邮箱（格式：QQ号@qq.com）")
    if not code or len(code) != 6:
        return error_response(400, "请输入 6 位验证码")
    now = datetime.now(LOCAL_TIMEZONE)
    record = EmailVerifyCode.query.filter_by(
        email=email, purpose='login', code=code
    ).filter(EmailVerifyCode.expires_at > now).order_by(EmailVerifyCode.created_at.desc()).first()
    if not record:
        return error_response(400, "验证码错误或已过期，请重新获取")
    user = User.query.filter_by(email=email).first()
    if not user:
        return error_response(401, "该邮箱未绑定账号")
    if not user.is_active:
        return error_response(401, "账户已被禁用，请联系管理员")
    # 邮箱登录同样需要检查账户是否在锁定期内
    lock_threshold = _get_login_failure_lock_threshold()
    if lock_threshold > 0 and user.locked_until:
        lock_time = user.locked_until if user.locked_until.tzinfo else user.locked_until.replace(tzinfo=LOCAL_TIMEZONE)
        if lock_time > now:
            return error_response(401, "账户已锁定，请稍后再试或联系管理员")
        user.failed_login_attempts = 0
        user.locked_until = None
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
    try:
        EmailVerifyCode.query.filter_by(id=record.id).delete()
        db.session.commit()
    except Exception:
        db.session.rollback()
    session_timeout_minutes = current_app.config.get('SESSION_TIMEOUT_MINUTES', 1440)
    setting = SystemSetting.query.filter_by(setting_key="session_timeout_minutes").first()
    if setting and setting.setting_value:
        try:
            v = int(setting.setting_value)
            if 30 <= v <= 10080:
                session_timeout_minutes = v
        except (ValueError, TypeError):
            pass
    current_app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=session_timeout_minutes)
    login_user(user, remember=True)
    session.permanent = True
    log_user_action("邮箱验证码登录", f"IP: {request.remote_addr}")
    return success_response({
        'user': user.to_dict(),
        'permissions': get_user_permission_codes(user)
    }, "登录成功")


@bp.route('/send-bind-email-code', methods=['POST'])
@rate_limiter.rate_limit(limit=5, window=60)
def send_bind_email_code():
    """发送邮箱绑定验证码（配置邮箱时验证真实性，不要求已登录）"""
    if not request.is_json:
        return error_response(400, "请求必须是 JSON 格式")
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    if not email:
        return error_response(400, "请输入邮箱")
    if not validate_qq_email(email):
        return error_response(400, "仅支持 QQ 邮箱（格式：QQ号@qq.com）")
    code = ''.join(random.choices(string.digits, k=6))
    expires_at = datetime.now(LOCAL_TIMEZONE) + timedelta(minutes=5)
    try:
        EmailVerifyCode.query.filter_by(email=email, purpose='bind_verify').delete()
        record = EmailVerifyCode(email=email, code=code, purpose='bind_verify', expires_at=expires_at)
        db.session.add(record)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return error_response(500, "发送失败，请稍后重试")
    ok, send_err = send_bind_verify_code(email, code)
    if not ok:
        if send_err == "recipient_refused":
            return error_response(400, "该邮箱无法接收邮件，请检查是否为有效 QQ 邮箱")
        return error_response(500, "邮件发送失败，请稍后重试")
    return success_response(message="验证码已发送到该邮箱，5 分钟内有效")


@bp.route('/confirm-email-binding', methods=['POST'])
@login_required
def confirm_email_binding():
    """当前用户确认邮箱绑定（验证码通过后写入当前用户邮箱）"""
    if not request.is_json:
        return error_response(400, "请求必须是 JSON 格式")
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    code = (data.get('code') or '').strip()
    if not email:
        return error_response(400, "请输入邮箱")
    if not validate_qq_email(email):
        return error_response(400, "仅支持 QQ 邮箱")
    if not code or len(code) != 6:
        return error_response(400, "请输入 6 位验证码")
    now = datetime.now(LOCAL_TIMEZONE)
    record = EmailVerifyCode.query.filter_by(
        email=email, purpose='bind_verify', code=code
    ).filter(EmailVerifyCode.expires_at > now).order_by(EmailVerifyCode.created_at.desc()).first()
    if not record:
        return error_response(400, "验证码错误或已过期，请重新获取")
    existing = User.query.filter_by(email=email).first()
    if existing and existing.id != current_user.id:
        return error_response(400, "该邮箱已被其他用户使用")
    try:
        EmailVerifyCode.query.filter_by(id=record.id).delete()
        current_user.email = email
        db.session.commit()
    except Exception:
        db.session.rollback()
        return error_response(500, "保存失败，请稍后重试")
    return success_response(message="邮箱绑定成功")


@bp.route('/send-unbind-email-code', methods=['POST'])
@login_required
@rate_limiter.rate_limit(limit=5, window=60)
def send_unbind_email_code():
    """向当前用户已绑定邮箱发送解除绑定验证码"""
    email = (current_user.email or '').strip()
    if not email:
        return error_response(400, "当前未绑定邮箱，无需解除")
    if not validate_qq_email(email):
        return error_response(400, "当前绑定邮箱格式异常")
    code = ''.join(random.choices(string.digits, k=6))
    expires_at = datetime.now(LOCAL_TIMEZONE) + timedelta(minutes=5)
    EmailVerifyCode.query.filter_by(email=email, purpose='unbind_verify').delete()
    record = EmailVerifyCode(email=email, code=code, purpose='unbind_verify', expires_at=expires_at)
    db.session.add(record)
    db.session.commit()
    ok, send_err = send_unbind_verify_code(email, code)
    if not ok:
        if send_err == "recipient_refused":
            return error_response(400, "该邮箱无法接收邮件，请检查邮箱是否有效")
        return error_response(500, "验证码发送失败，请稍后重试")
    return success_response(message="验证码已发送到您的邮箱，5 分钟内有效")


@bp.route('/unbind-email', methods=['POST'])
@login_required
def unbind_email():
    """当前用户解除邮箱绑定（需传入验证码）"""
    if not request.is_json:
        return error_response(400, "请求必须是 JSON 格式")
    data = request.get_json(silent=True) or {}
    code = (data.get('code') or '').strip()
    if not code or len(code) != 6:
        return error_response(400, "请输入 6 位验证码")
    email = (current_user.email or '').strip()
    if not email:
        return error_response(400, "当前未绑定邮箱")
    now = datetime.now(LOCAL_TIMEZONE)
    record = EmailVerifyCode.query.filter_by(
        email=email, purpose='unbind_verify', code=code
    ).filter(EmailVerifyCode.expires_at > now).order_by(EmailVerifyCode.created_at.desc()).first()
    if not record:
        return error_response(400, "验证码错误或已过期，请重新获取")
    try:
        EmailVerifyCode.query.filter_by(id=record.id).delete()
        current_user.email = None
        db.session.commit()
    except Exception:
        db.session.rollback()
        return error_response(500, "操作失败，请稍后重试")
    return success_response(message="已解除邮箱绑定")


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
        except Exception:
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
    
    if not validate_username(username):
        return error_response(400, "用户名长度必须在3-14个字节之间")
    
    if not validate_phone(phone):
        return error_response(400, "手机号格式不正确")

    # 按系统安全设置中的密码策略校验
    policy = _get_password_policy()
    valid, msg = PasswordManager.validate_password_with_policy(
        password, policy, min_length_default=6
    )
    if not valid:
        return error_response(400, msg)
    
    if not real_name:
        return error_response(400, "真实姓名不能为空")
    
    if User.query.filter_by(username=username).first():
        return error_response(400, "用户名已存在")
    
    if User.query.filter_by(phone=phone).first():
        return error_response(400, "手机号已注册")
    
    user = User(
        username=username,
        phone=phone,
        real_name=real_name,
        gender=gender,
        department=department,
        role='admin'  # 新注册用户默认为普通成员角色
    )
    user.set_password(password)
    
    try:
        db.session.add(user)
        db.session.commit()
        log_user_action("注册", f"新用户: {username}")
        admin_users = User.query.filter(User.role.in_(['super', 'manager'])).all()
        if admin_users:
            from app.services.notification_service import notify_users
            dept_label = f'，部门：{department}' if department else ''
            notify_users(
                [u.id for u in admin_users], 'user_registered', '新用户注册',
                f'新用户 {real_name}（账号 {username}）已注册{dept_label}，请及时审核',
                'user', user.id
            )
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

    # 按系统安全设置中的密码策略校验新密码
    policy = _get_password_policy()
    valid, msg = PasswordManager.validate_password_with_policy(
        new_password, policy, min_length_default=6
    )
    if not valid:
        return error_response(400, msg)
    
    if not current_user.check_password(old_password):
        return error_response(400, "原密码错误")
    
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

    if not current_user.is_authenticated:
        return success_response({'authenticated': False})
    try:
        return success_response({
            'authenticated': True,
            'user': current_user.to_dict()
        })
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning('check_session: to_dict failed, %s', e)
        return success_response({'authenticated': False})


@bp.route('/forgot-password', methods=['POST'])
@rate_limiter.rate_limit(limit=3, window=300)  # 5分钟内最多3次请求
@validate_json_data(['email'])
def forgot_password():
    """忘记密码"""
    data = request.get_json()
    email = (data['email'] or '').strip().lower()
    if not validate_qq_email(email):
        return error_response(400, "仅支持 QQ 邮箱（格式：QQ号@qq.com）")
    user = User.query.filter_by(email=email).first()
    if not user:
        return error_response(404, "该邮箱未绑定账号")
    reset_token = PasswordManager.generate_reset_token(user.id, expires_in=1800)
    base_url = current_app.config.get('FRONTEND_RESET_PASSWORD_URL', 'http://localhost:8080/reset-password')
    reset_link = f"{base_url.rstrip('/')}?token={reset_token}"
    ok, send_err = send_reset_password_link(email, reset_link)
    if not ok:
        if send_err == "recipient_refused":
            return error_response(400, "该邮箱无法接收邮件，请检查邮箱是否正确或联系管理员重新绑定")
        return error_response(500, "邮件发送失败，请稍后重试")
    log_user_action("请求密码重置", f"邮箱: {email}")
    return success_response(message="密码重置邮件已发送，请查收")


@bp.route('/reset-password', methods=['POST'])
@validate_json_data(['token', 'password'])
def reset_password():
    """重置密码"""
    data = request.get_json()
    token = data['token']
    password = data['password']
    
    user_id = PasswordManager.verify_reset_token(token, max_age=1800)
    if not user_id:
        return error_response(400, "无效或过期的重置令牌")

    # 按系统安全设置中的密码策略校验
    policy = _get_password_policy()
    is_valid, message = PasswordManager.validate_password_with_policy(
        password, policy, min_length_default=6
    )
    if not is_valid:
        return error_response(400, message)
    
    user = User.query.get(user_id)
    if not user:
        return error_response(404, "用户不存在")
    user.set_password(password)
    
    try:
        db.session.commit()
        log_user_action("密码重置成功", f"用户ID: {user_id}")
        return success_response(message="密码重置成功")
    except Exception as e:
        db.session.rollback()
        return error_response(500, "密码重置失败，请稍后重试")


@bp.route('/permissions', methods=['GET'])
@login_required
def get_permissions():
    """获取当前用户权限（埋点编码列表）"""
    permissions = get_user_permission_codes(current_user)
    return success_response({
        'permissions': permissions,
    })