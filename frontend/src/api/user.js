import request from "@/utils/request";

// 获取用户列表（需 user.list 权限，用于用户管理页）
export function getUserList(params) {
  return request({
    url: "/users",
    method: "get",
    params,
  });
}

// 获取用户选项（仅需登录，用于评审人/负责人/执行人等下拉）
export function getUserOptions(params) {
  return request({
    url: "/users/options",
    method: "get",
    params: params || { size: 1000 },
  });
}

// 创建用户
export function createUser(data) {
  return request({
    url: "/users",
    method: "post",
    data,
  });
}

// 更新用户
export function updateUser(id, data) {
  return request({
    url: `/users/${id}`,
    method: "put",
    data,
  });
}

// 删除用户
export function deleteUser(id) {
  return request({
    url: `/users/${id}`,
    method: "delete",
  });
}

// 切换用户状态
export function toggleUserStatus(id) {
  return request({
    url: `/users/${id}/toggle-status`,
    method: "post",
  });
}

// 重置用户密码
export function resetUserPassword(id, data) {
  return request({
    url: `/users/${id}/reset-password`,
    method: "post",
    data,
  });
}

// 默认导出所有方法
export default {
  getUserList,
  getUserOptions,
  createUser,
  updateUser,
  deleteUser,
  toggleUserStatus,
  resetUserPassword,
};
