# -*- coding: utf-8 -*-
"""
功能埋点常量：仅对以下 5 个模块做权限配置，其余功能不做权限限制。
1. 项目管理：入口、增、删、改
2. 迭代管理：入口、增、删、改
3. 需求管理：入口、增、删、改
4. 权限配置：入口、管理员/测试人员/普通成员分别可配置
5. 用户管理：入口、增、删、改、编辑用户
"""

PERMISSION_GROUPS = [
    {
        "module": "project",
        "moduleLabel": "项目管理",
        "entryPermission": "project.list",
        "permissions": [
            ("project.list", "入口"),
            ("project.create", "新建项目"),
            ("project.edit", "编辑项目"),
            ("project.delete", "删除项目"),
        ],
    },
    {
        "module": "iteration",
        "moduleLabel": "迭代管理",
        "entryPermission": "iteration.list",
        "permissions": [
            ("iteration.list", "入口"),
            ("iteration.create", "新建迭代"),
            ("iteration.edit", "编辑迭代"),
            ("iteration.delete", "删除迭代"),
        ],
    },
    {
        "module": "requirement",
        "moduleLabel": "需求管理",
        "entryPermission": "requirement.list",
        "permissions": [
            ("requirement.list", "入口"),
            ("requirement.create", "新建需求"),
            ("requirement.edit", "编辑需求"),
            ("requirement.delete", "删除需求"),
        ],
    },
    {
        "module": "role",
        "moduleLabel": "权限配置",
        "entryPermission": "role.permission_config",
        "permissions": [
            ("role.permission_config", "入口"),
            ("role.manager_config", "管理员权限配置"),
            ("role.tester_config", "测试人员权限配置"),
            ("role.admin_config", "普通成员权限配置"),
        ],
    },
    {
        "module": "user",
        "moduleLabel": "用户管理",
        "entryPermission": "user.list",
        "permissions": [
            ("user.list", "入口"),
            ("user.create", "新建用户"),
            ("user.edit", "编辑用户"),
            ("user.delete", "删除用户"),
        ],
    },
    {
        "module": "report",
        "moduleLabel": "报告管理",
        "entryPermission": None,
        "permissions": [
            ("report.delete", "删除报告"),
        ],
    },
]


def get_all_permission_codes():
    """返回全部埋点编码列表"""
    codes = []
    for g in PERMISSION_GROUPS:
        codes.extend([p[0] for p in g["permissions"]])
    return codes


def get_permissions_grouped():
    """返回按模块分组的埋点列表，供前端配置页展示"""
    return PERMISSION_GROUPS


# 默认角色权限：role_permissions 无记录时使用；super 见 permission_service。
DEFAULT_ROLE_PERMISSIONS = {
    "manager": [
        "project.list", "project.create", "project.edit", "project.delete",
        "iteration.list", "iteration.create", "iteration.edit", "iteration.delete",
        "requirement.list", "requirement.create", "requirement.edit", "requirement.delete",
        "role.permission_config", "role.manager_config", "role.tester_config", "role.admin_config",
        "user.list", "user.create", "user.edit", "user.delete",
        "report.delete",
    ],
    "tester": [
        "project.list", "project.create", "project.edit",
        "iteration.list", "iteration.create", "iteration.edit", "iteration.delete",
        "requirement.list", "requirement.create", "requirement.edit", "requirement.delete",
    ],
    "admin": [
        "project.list", "project.create", "project.edit",
        "iteration.list", "iteration.create", "iteration.edit",
        "requirement.list", "requirement.create", "requirement.edit", "requirement.delete",
    ],
}
