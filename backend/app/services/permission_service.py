# -*- coding: utf-8 -*-
"""角色权限服务：根据用户角色返回可配置的埋点集合，支持 permission_required 鉴权。"""

from functools import wraps
from flask_login import current_user

from app.models.models import RolePermission, db
from app.constants.permissions import (
    get_all_permission_codes,
    DEFAULT_ROLE_PERMISSIONS,
)
from app.utils.helpers import error_response


def get_role_permission_codes(role):
    """
    获取某角色已配置的埋点编码列表。
    - super：直接返回全部埋点（不查库）。
    - 其他角色：先查 role_permissions 表，若有记录则用库内配置；否则用默认 DEFAULT_ROLE_PERMISSIONS。
    - 兼容旧数据：若库中存在 role.list，视为拥有 role.manager_config、role.tester_config、role.admin_config。
    """
    if role == "super":
        return get_all_permission_codes()

    rows = RolePermission.query.filter_by(role=role).all()
    if rows:
        codes = [r.permission_code for r in rows]
        # 兼容：旧配置 role.list 视为拥有三个角色配置权限
        if "role.list" in codes:
            for new_code in ("role.manager_config", "role.tester_config", "role.admin_config"):
                if new_code not in codes:
                    codes.append(new_code)
        return codes
    return DEFAULT_ROLE_PERMISSIONS.get(role, [])


def get_user_permission_codes(user):
    """获取当前用户有效埋点列表。未登录返回空列表。"""
    if not user or not getattr(user, "is_authenticated", False) or not user.is_authenticated:
        return []
    return get_role_permission_codes(user.role)


def has_permission(user, permission_code):
    """判断用户是否拥有指定埋点。"""
    if not user or not getattr(user, "is_authenticated", False) or not user.is_authenticated:
        return False
    codes = get_user_permission_codes(user)
    return permission_code in codes


def permission_required(permission_code):
    """接口鉴权装饰器：要求当前用户拥有指定埋点，否则 403。"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return error_response(401, "用户未登录")
            if not has_permission(current_user, permission_code):
                return error_response(403, "权限不足")
            return f(*args, **kwargs)
        return decorated_function
    return decorator
