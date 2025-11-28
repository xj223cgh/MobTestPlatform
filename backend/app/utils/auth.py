from functools import wraps
from flask import request, jsonify, current_app
from flask_login import current_user
from app.models.models import User, db
from app.utils.helpers import error_response

class PermissionManager:
    """权限管理器"""
    
    # 权限定义
    PERMISSIONS = {
        # 用户管理权限
        'user:read': '查看用户',
        'user:write': '管理用户',
        'user:delete': '删除用户',
        
        # 设备管理权限
        'device:read': '查看设备',
        'device:write': '管理设备',
        'device:delete': '删除设备',
        
        # 用例管理权限
        'testcase:read': '查看用例',
        'testcase:write': '管理用例',
        'testcase:delete': '删除用例',
        
        # 测试任务权限
        'task:read': '查看测试任务',
        'task:write': '管理测试任务',
        'task:execute': '执行测试任务',
        'task:delete': '删除测试任务',
        
        # 缺陷管理权限
        'bug:read': '查看缺陷',
        'bug:write': '管理缺陷',
        'bug:delete': '删除缺陷',
        
        # 工具管理权限
        'tool:read': '查看工具',
        'tool:write': '管理工具',
        'tool:execute': '执行工具',
        'tool:delete': '删除工具',
        
        # 报告管理权限
        'report:read': '查看报告',
        'report:write': '管理报告',
        'report:delete': '删除报告',
        
        # 系统管理权限
        'system:manage': '系统管理',
        'system:log': '查看日志',
    }
    
    # 角色权限映射
    ROLE_PERMISSIONS = {
        'admin': [
            'user:read', 'user:write', 'user:delete',
            'device:read', 'device:write', 'device:delete',
            'testcase:read', 'testcase:write', 'testcase:delete',
            'task:read', 'task:write', 'task:execute', 'task:delete',
            'bug:read', 'bug:write', 'bug:delete',
            'tool:read', 'tool:write', 'tool:execute', 'tool:delete',
            'report:read', 'report:write', 'report:delete',
            'system:manage', 'system:log'
        ],
        'tester': [
            'device:read',
            'testcase:read', 'testcase:write',
            'task:read', 'task:write', 'task:execute',
            'bug:read', 'bug:write',
            'tool:read', 'tool:execute',
            'report:read'
        ],
        'manager': [
            'user:read', 'user:write',
            'device:read', 'device:write',
            'testcase:read', 'testcase:write',
            'task:read', 'task:write', 'task:execute',
            'bug:read', 'bug:write',
            'tool:read', 'tool:execute',
            'report:read', 'report:write',
            'system:log'
        ],
        'super': [
            'user:read', 'user:write', 'user:delete',
            'device:read', 'device:write', 'device:delete',
            'testcase:read', 'testcase:write', 'testcase:delete',
            'task:read', 'task:write', 'task:execute', 'task:delete',
            'bug:read', 'bug:write', 'bug:delete',
            'tool:read', 'tool:write', 'tool:execute', 'tool:delete',
            'report:read', 'report:write', 'report:delete',
            'system:manage', 'system:log'
        ]
    }
    
    @classmethod
    def get_permissions_by_role(cls, role):
        """根据角色获取权限列表"""
        return cls.ROLE_PERMISSIONS.get(role, [])
    
    @classmethod
    def has_permission(cls, user, permission):
        """检查用户是否有指定权限"""
        if not user or not user.is_authenticated:
            return False
        
        # 超级管理员拥有所有权限
        if user.role == 'super':
            return True
        
        # 检查用户角色的权限
        user_permissions = cls.get_permissions_by_role(user.role)
        return permission in user_permissions
    
    @classmethod
    def check_permission(cls, permission):
        """权限检查装饰器"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not current_user.is_authenticated:
                    return error_response(401, "用户未登录")
                
                if not cls.has_permission(current_user, permission):
                    return error_response(403, "权限不足")
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    @classmethod
    def get_user_permissions(cls, user):
        """获取用户的所有权限"""
        if not user:
            return []
        
        # 超级管理员拥有所有权限
        if user.role == 'super':
            return list(cls.PERMISSIONS.keys())
        
        return cls.get_permissions_by_role(user.role)
    
    @classmethod
    def get_permission_info(cls):
        """获取所有权限信息"""
        return [
            {
                'key': key,
                'name': name,
                'category': cls._get_permission_category(key)
            }
            for key, name in cls.PERMISSIONS.items()
        ]
    
    @classmethod
    def _get_permission_category(cls, permission):
        """获取权限分类"""
        if permission.startswith('user:'):
            return '用户管理'
        elif permission.startswith('device:'):
            return '设备管理'
        elif permission.startswith('testcase:'):
            return '用例管理'
        elif permission.startswith('task:'):
            return '测试任务'
        elif permission.startswith('bug:'):
            return '缺陷管理'
        elif permission.startswith('tool:'):
            return '工具管理'
        elif permission.startswith('report:'):
            return '报告管理'
        elif permission.startswith('system:'):
            return '系统管理'
        else:
            return '其他'


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
        'email': current_user.email,
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