import secrets
import hashlib
import time
from datetime import datetime, timedelta, timezone

# 设置本地时区为UTC+8
LOCAL_TIMEZONE = timezone(timedelta(hours=8))
from itsdangerous import URLSafeTimedSerializer
import pyotp
import qrcode
import io
import base64
from flask import current_app


class PasswordManager:
    """密码管理器"""
    
    @staticmethod
    def generate_reset_token(user_id, expires_in=3600):
        """生成密码重置令牌"""
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return serializer.dumps(user_id, salt='password-reset-salt')
    
    @staticmethod
    def verify_reset_token(token, max_age=3600):
        """验证密码重置令牌"""
        try:
            serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            user_id = serializer.loads(token, salt='password-reset-salt', max_age=max_age)
            return user_id
        except:
            return None
    
    @staticmethod
    def validate_password(password):
        """验证密码强度"""
        if len(password) < 6:
            return False, "密码长度不能少于6位"
        
        if not any(c.isupper() for c in password):
            return False, "密码必须包含大写字母"
        
        if not any(c.islower() for c in password):
            return False, "密码必须包含小写字母"
        
        if not any(c.isdigit() for c in password):
            return False, "密码必须包含数字"
        
        return True, "密码强度符合要求"


class TwoFactorAuth:
    """双因素认证管理器"""
    
    @staticmethod
    def generate_secret():
        """生成2FA密钥"""
        return pyotp.random_base32()
    
    @staticmethod
    def generate_qr_code(email, secret):
        """生成2FA二维码"""
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=email,
            issuer_name="移动端测试平台"
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_base64}"
    
    @staticmethod
    def verify_token(secret, token):
        """验证2FA令牌"""
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(token, valid_window=1)
        except:
            return False


class SessionManager:
    """会话管理器"""
    
    @staticmethod
    def create_session(user_id, user_data=None):
        """创建会话"""
        session['user_id'] = user_id
        session['authenticated'] = True
        session['created_at'] = datetime.now(LOCAL_TIMEZONE).isoformat()
        
        if user_data:
            session['user_data'] = user_data
        
        return session
    
    @staticmethod
    def destroy_session():
        """销毁会话"""
        session.clear()
    
    @staticmethod
    def is_authenticated():
        """检查是否已认证"""
        return session.get('authenticated', False)
    
    @staticmethod
    def get_user_id():
        """获取当前用户ID"""
        return session.get('user_id')
    
    @staticmethod
    def refresh_session():
        """刷新会话"""
        session.permanent = True
        session.modified = True