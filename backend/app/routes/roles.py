# -*- coding: utf-8 -*-
"""角色与权限配置：全量埋点分组、按角色查询/更新配置。"""

from flask import Blueprint, request
from flask_login import login_required, current_user

from app.models.models import RolePermission, db, ROLE_ENUM
from app.constants.permissions import (
    get_permissions_grouped,
    get_all_permission_codes,
)
from app.services.permission_service import get_role_permission_codes, has_permission
from app.utils.helpers import success_response, error_response, log_user_action

bp = Blueprint("roles", __name__, url_prefix="/api/roles")


@bp.route("/permissions", methods=["GET"])
@login_required
def get_all_permissions_grouped():
    """获取全量埋点（按模块分组），供角色权限配置页展示。需 role.permission_config 或超管。"""
    if not has_permission(current_user, "role.permission_config"):
        return error_response(403, "权限不足")
    return success_response({"groups": get_permissions_grouped()})


@bp.route("/<role>/permissions", methods=["GET"])
@login_required
def get_role_permissions(role):
    """获取指定角色已配置的埋点编码列表。需 role.permission_config。"""
    if not has_permission(current_user, "role.permission_config"):
        return error_response(403, "权限不足")
    if role not in ROLE_ENUM:
        return error_response(400, "无效的角色")
    codes = get_role_permission_codes(role)
    return success_response({"role": role, "permissions": codes})


# 角色与“可配置该角色”埋点的对应关系
ROLE_CONFIG_PERMISSION = {
    "manager": "role.manager_config",
    "tester": "role.tester_config",
    "admin": "role.admin_config",
}


@bp.route("/<role>/permissions", methods=["PUT"])
@login_required
def update_role_permissions(role):
    """更新指定角色的埋点配置。需 role.permission_config 且具备该角色的配置权限（如 role.manager_config）。"""
    if not has_permission(current_user, "role.permission_config"):
        return error_response(403, "权限不足")
    if role not in ROLE_ENUM:
        return error_response(400, "无效的角色")
    if role == "super":
        return error_response(400, "超管权限不可修改，始终拥有全部功能")
    config_perm = ROLE_CONFIG_PERMISSION.get(role)
    if config_perm and not has_permission(current_user, config_perm):
        return error_response(403, "您没有该角色的权限配置权限")

    data = request.get_json()
    if not data or "permissions" not in data:
        return error_response(400, "缺少 permissions 数组")

    all_codes = set(get_all_permission_codes())
    new_codes = [c for c in data["permissions"] if isinstance(c, str) and c in all_codes]

    try:
        RolePermission.query.filter_by(role=role).delete()
        for code in new_codes:
            db.session.add(RolePermission(role=role, permission_code=code))
        db.session.commit()
        log_user_action("更新角色权限配置", f"角色: {role}, 埋点数量: {len(new_codes)}")
        return success_response({"role": role, "permissions": new_codes}, "保存成功")
    except Exception as e:
        db.session.rollback()
        return error_response(500, "保存失败")


@bp.route("/list", methods=["GET"])
@login_required
def list_roles():
    """获取角色列表（含展示名）。任意登录用户可查看。"""
    roles = [
        {"value": "super", "label": "超管"},
        {"value": "manager", "label": "管理员"},
        {"value": "tester", "label": "测试人员"},
        {"value": "admin", "label": "普通成员"},
    ]
    return success_response({"roles": roles})
