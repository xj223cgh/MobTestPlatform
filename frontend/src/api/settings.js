import request from "@/utils/request";

/** 用户个人设置（与后端 /api/settings 对应） */
export const getUserSettings = () => {
  return request({
    url: "/settings/user",
    method: "get",
  });
};

export const updateUserSettings = (data) => {
  return request({
    url: "/settings/user",
    method: "put",
    data,
  });
};

/** 系统设置 */
export const getSystemSettings = () => {
  return request({
    url: "/settings/system",
    method: "get",
  });
};

export const updateSystemSettings = (data) => {
  return request({
    url: "/settings/system",
    method: "put",
    data,
  });
};
