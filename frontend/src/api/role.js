import request from "@/utils/request";

// 获取全量埋点（按模块分组）
export const getPermissionGroups = () => {
  return request({
    url: "/roles/permissions",
    method: "get",
  });
};

// 获取指定角色的已配置埋点
export const getRolePermissions = (role) => {
  return request({
    url: `/roles/${role}/permissions`,
    method: "get",
  });
};

// 更新指定角色的埋点配置
export const updateRolePermissions = (role, permissions) => {
  return request({
    url: `/roles/${role}/permissions`,
    method: "put",
    data: { permissions },
  });
};

// 角色列表（下拉用）
export const getRolesList = () => {
  return request({
    url: "/roles/list",
    method: "get",
  });
};
