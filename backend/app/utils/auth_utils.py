from datetime import datetime, timedelta, timezone

LOCAL_TIMEZONE = timezone(timedelta(hours=8))
from itsdangerous import URLSafeTimedSerializer
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
    
    # 与前端安全设置中的 passwordPolicy 选项一致
    POLICY_MIN_LENGTH = "minLength"
    POLICY_UPPERCASE = "uppercase"
    POLICY_LOWERCASE = "lowercase"
    POLICY_NUMBERS = "numbers"
    POLICY_SPECIAL_CHARS = "specialChars"

    @staticmethod
    def validate_password(password):
        """验证密码强度（默认策略：至少6位，含大小写和数字）"""
        return PasswordManager.validate_password_with_policy(
            password,
            [
                PasswordManager.POLICY_MIN_LENGTH,
                PasswordManager.POLICY_UPPERCASE,
                PasswordManager.POLICY_LOWERCASE,
                PasswordManager.POLICY_NUMBERS,
            ],
            min_length_default=6,
        )

    @staticmethod
    def validate_password_with_policy(password, policy_list, min_length_default=8):
        """
        根据系统设置中的密码策略校验密码。
        policy_list: 来自 system_settings.password_policy 的 JSON 数组，如 ["minLength","uppercase","numbers"]
        """
        if not password:
            return False, "密码不能为空"
        if not isinstance(policy_list, list):
            policy_list = []
        policy_set = set(policy_list)

        if PasswordManager.POLICY_MIN_LENGTH in policy_set or not policy_set:
            min_len = 8 if policy_set else min_length_default
            if len(password) < min_len:
                return False, f"密码长度不能少于{min_len}位"
        if PasswordManager.POLICY_UPPERCASE in policy_set:
            if not any(c.isupper() for c in password):
                return False, "密码必须包含大写字母"
        if PasswordManager.POLICY_LOWERCASE in policy_set:
            if not any(c.islower() for c in password):
                return False, "密码必须包含小写字母"
        if PasswordManager.POLICY_NUMBERS in policy_set:
            if not any(c.isdigit() for c in password):
                return False, "密码必须包含数字"
        if PasswordManager.POLICY_SPECIAL_CHARS in policy_set:
            if all(c.isalnum() for c in password):
                return False, "密码必须包含特殊字符"

        return True, "密码强度符合要求"

