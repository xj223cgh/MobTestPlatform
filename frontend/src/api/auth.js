import request from "@/utils/request";

// 登录
export const login = (data) => {
  return request({
    url: "/auth/login",
    method: "post",
    data,
  });
};

// 登出
export const logout = () => {
  return request({
    url: "/auth/logout",
    method: "post",
  });
};

// 注册
export const register = (data) => {
  return request({
    url: "/auth/register",
    method: "post",
    data,
  });
};

// 获取用户信息
export const getUserInfo = () => {
  return request({
    url: "/auth/current-user",
    method: "get",
  });
};

// 检查会话
export const checkSession = () => {
  return request({
    url: "/auth/check-session",
    method: "get",
  });
};

// 忘记密码
export const forgotPassword = (data) => {
  return request({
    url: "/auth/forgot-password",
    method: "post",
    data,
  });
};

// 重置密码
export const resetPassword = (data) => {
  return request({
    url: "/auth/reset-password",
    method: "post",
    data,
  });
};

// 修改密码
export const changePassword = (data) => {
  return request({
    url: "/auth/change-password",
    method: "post",
    data,
  });
};
