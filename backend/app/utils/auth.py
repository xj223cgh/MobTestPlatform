from functools import wraps
from flask import request, current_app
from flask_login import current_user
from app.utils.helpers import error_response


class APIKeyAuth:
    """API密钥认证"""
    
    @staticmethod
    def validate_api_key(api_key):
        """验证API密钥"""
        valid_keys = current_app.config.get('VALID_API_KEYS', [])
        return api_key in valid_keys
    
    @staticmethod
    def require_api_key(f):
        """API密钥认证装饰器"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_key = request.headers.get('X-API-Key')
            if not api_key:
                return error_response(401, "缺少API密钥")
            
            if not APIKeyAuth.validate_api_key(api_key):
                return error_response(401, "无效的API密钥")
            
            return f(*args, **kwargs)
        return decorated_function

def token_required(f):
    """API接口认证装饰器，确保用户已登录"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user is None or not getattr(current_user, 'is_authenticated', False):
            return error_response(401, "用户未认证，请先登录")
        return f(*args, **kwargs)
    return decorated

def get_user_info():
    """获取当前登录用户信息"""
    if current_user is None or not getattr(current_user, 'is_authenticated', False):
        return None
    return {
        'id': current_user.id,
        'username': current_user.username,
        'role': current_user.role
    }

def role_required(roles):
    """检查用户是否具有指定角色的装饰器，支持单个角色或角色列表"""
    if isinstance(roles, str):
        roles = [roles]
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user is None or not getattr(current_user, 'is_authenticated', False):
                return error_response(401, "用户未认证，请先登录")
            
            if current_user.role not in roles:
                return error_response(403, "权限不足，需要以下角色之一：{}".format(', '.join(roles)))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


class RateLimiter:
    """简单的速率限制器"""
    
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, key, limit, window):
        """检查是否允许请求"""
        import time
        
        now = time.time()
        if key not in self.requests:
            self.requests[key] = []
        
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if now - req_time < window
        ]
        
        if len(self.requests[key]) >= limit:
            return False
        
        self.requests[key].append(now)
        return True
    
    def rate_limit(self, limit=100, window=60):
        """速率限制装饰器"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                key = request.remote_addr
                
                if not self.is_allowed(key, limit, window):
                    return error_response(429, "请求过于频繁，请稍后重试")
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator


rate_limiter = RateLimiter()