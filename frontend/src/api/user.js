/** 用户 API：列表、创建、编辑、删除。 */
import request from "@/utils/request";

/** 需 user.list 权限，用于用户管理页 */
export function getUserList(params) {
  return request({
    url: "/users",
    method: "get",
    params,
  });
}

/** 仅需登录，用于评审人/负责人/执行人等下拉 */
export function getUserOptions(params) {
  return request({
    url: "/users/options",
    method: "get",
    params: params || { size: 1000 },
  });
}

export function createUser(data) {
  return request({
    url: "/users",
    method: "post",
    data,
  });
}

export function updateUser(id, data) {
  return request({
    url: `/users/${id}`,
    method: "put",
    data,
  });
}

export function deleteUser(id) {
  return request({
    url: `/users/${id}`,
    method: "delete",
  });
}

export function toggleUserStatus(id) {
  return request({
    url: `/users/${id}/toggle-status`,
    method: "post",
  });
}

/** 管理员操作；验证码通过后写入，只有能收到验证码才证明邮箱存在 */
export function confirmUserEmail(id, data) {
  return request({
    url: `/users/${id}/confirm-email`,
    method: "post",
    data: { email: data.email, code: data.code },
  });
}

export function resetUserPassword(id, data) {
  return request({
    url: `/users/${id}/reset-password`,
    method: "post",
    data,
  });
}

export default {
  getUserList,
  getUserOptions,
  createUser,
  updateUser,
  deleteUser,
  toggleUserStatus,
  resetUserPassword,
};
