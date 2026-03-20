/** 认证 API：登录、注册、密码重置。 */
import request from "@/utils/request";

export const login = (data) => {
  return request({
    url: "/auth/login",
    method: "post",
    data,
  });
};

export const sendLoginCode = (data) => {
  return request({
    url: "/auth/send-login-code",
    method: "post",
    data: { email: data.email },
  });
};

export const loginByEmail = (data) => {
  return request({
    url: "/auth/login-by-email",
    method: "post",
    data: { email: data.email, code: data.code },
  });
};

export const logout = () => {
  return request({
    url: "/auth/logout",
    method: "post",
  });
};

export const register = (data) => {
  return request({
    url: "/auth/register",
    method: "post",
    data,
  });
};

export const getUserInfo = () => {
  return request({
    url: "/auth/current-user",
    method: "get",
  });
};

export const checkSession = () => {
  return request({
    url: "/auth/check-session",
    method: "get",
  });
};

export const forgotPassword = (data) => {
  return request({
    url: "/auth/forgot-password",
    method: "post",
    data,
  });
};

export const resetPassword = (data) => {
  return request({
    url: "/auth/reset-password",
    method: "post",
    data,
  });
};

export const changePassword = (data) => {
  return request({
    url: "/auth/change-password",
    method: "post",
    data,
  });
};

/** 返回埋点编码列表 */
export const getPermissions = () => {
  return request({
    url: "/auth/permissions",
    method: "get",
  });
};

/** 配置邮箱时验证真实性 */
export const sendBindEmailCode = (data) => {
  return request({
    url: "/auth/send-bind-email-code",
    method: "post",
    data: { email: data.email },
  });
};

/** 验证码通过后写入 */
export const confirmEmailBinding = (data) => {
  return request({
    url: "/auth/confirm-email-binding",
    method: "post",
    data: { email: data.email, code: data.code },
  });
};

/** 发到当前用户已绑定邮箱 */
export const sendUnbindEmailCode = () => {
  return request({
    url: "/auth/send-unbind-email-code",
    method: "post",
  });
};

/** 需传验证码 */
export const unbindEmail = (data) => {
  return request({
    url: "/auth/unbind-email",
    method: "post",
    data: data ? { code: data.code } : {},
  });
};
