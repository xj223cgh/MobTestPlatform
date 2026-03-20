/** 角色权限 API：配置读写。 */
import request from "@/utils/request";

export const getPermissionGroups = () => {
  return request({
    url: "/roles/permissions",
    method: "get",
  });
};

export const getRolePermissions = (role) => {
  return request({
    url: `/roles/${role}/permissions`,
    method: "get",
  });
};

export const updateRolePermissions = (role, permissions) => {
  return request({
    url: `/roles/${role}/permissions`,
    method: "put",
    data: { permissions },
  });
};
