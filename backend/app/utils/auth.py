from functools import wraps
from flask import request, current_app
from flask_login import current_user
from app.utils.helpers import error_response


class APIKeyAuth:
    """API密钥认证"""
    
    @staticmethod
    def validate_api_key(api_key):
        """验证API密钥"""
        # TODO: 实现API密钥验证逻辑
        # 这里可以从数据库或配置中验证API密钥
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

# API认证装饰器 - 使用Flask-Login的current_user
def token_required(f):
    """API接口认证装饰器，确保用户已登录"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return error_response(401, "用户未认证，请先登录")
        return f(*args, **kwargs)
    return decorated

# 获取用户信息函数
def get_user_info():
    """获取当前登录用户信息"""
    if not current_user.is_authenticated:
        return None
    return {
        'id': current_user.id,
        'username': current_user.username,
        'role': current_user.role
    }

# 角色权限装饰器
def role_required(roles):
    """检查用户是否具有指定角色的装饰器，支持单个角色或角色列表"""
    # 确保roles始终是列表形式
    if isinstance(roles, str):
        roles = [roles]
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
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
        
        # 清理过期的请求记录
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if now - req_time < window
        ]
        
        # 检查是否超过限制
        if len(self.requests[key]) >= limit:
            return False
        
        # 记录当前请求
        self.requests[key].append(now)
        return True
    
    def rate_limit(self, limit=100, window=60):
        """速率限制装饰器"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # 使用IP地址作为限制键
                key = request.remote_addr
                
                if not self.is_allowed(key, limit, window):
                    return error_response(429, "请求过于频繁，请稍后重试")
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator


# 全局速率限制器实例
rate_limiter = RateLimiter()