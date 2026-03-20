/** Axios 实例：/api 前缀、携带 Cookie、业务 code 与 401 处理。 */
import axios from "axios";
import { ElMessage, ElMessageBox } from "element-plus";
import { useUserStore } from "@/stores/user";
import router from "@/router";

const request = axios.create({
  baseURL: "/api",
  timeout: 30000,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

let disconnectAlertTimer = null;
const MIN_ALERT_INTERVAL = 2000;

request.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    console.error("请求错误:", error);
    return Promise.reject(error);
  },
);

request.interceptors.response.use(
  (response) => {
    const res = response?.data || {};

    if (res.code && res.code !== 200 && res.code !== 201) {
      const err = new Error(res.message || "操作失败");
      err._messageShown = true;
      ElMessage.error(res.message || "操作失败");
      return Promise.reject(err);
    }

    res.success = true;
    return res;
  },
  async (error) => {
    const { response, config } = error;
    const userStore = useUserStore();

    const isDeviceDisconnected = (response) => {
      const errorMessage = response?.data?.message || "";
      const requestUrl = config?.url || "";
      return (
        errorMessage.includes("disconnected") ||
        errorMessage.includes("not found") ||
        errorMessage.includes("offline") ||
        errorMessage.includes("device not found") ||
        errorMessage.includes("no devices/emulators found") ||
        requestUrl.includes("/adb/") ||
        requestUrl.includes("/device/")
      );
    };

    if (response) {
      const { status, data } = response;

      if (isDeviceDisconnected(response)) {
        // 只有在悬浮状态下才显示设备断开连接的错误提示
        if (config?.isHovering) {
          if (!disconnectAlertTimer) {
            ElMessage.error("设备已断开连接，请检查设备连接状态");
            disconnectAlertTimer = setTimeout(() => {
              disconnectAlertTimer = null;
            }, MIN_ALERT_INTERVAL);
          }
        }
        return Promise.reject(error);
      }

      switch (status) {
        case 401:
          if (config.url && config.url.includes("/auth/login")) {
            // 登录接口的401错误直接返回，不处理为"登录状态已过期"
            return Promise.reject(error);
          } else {
            // 其他接口的401错误才是登录状态过期
            ElMessageBox.confirm("登录状态已过期，请重新登录", "系统提示", {
              confirmButtonText: "重新登录",
              cancelButtonText: "取消",
              type: "warning",
            }).then(() => {
              userStore.logout();
              router.push("/login");
            });
          }
          break;

        case 403:
          // 权限不足：统一在此提示一次，打标后 reject，业务 catch 可据此不再重复弹窗
          const permissionMsg = data?.message && String(data.message).trim() ? data.message : "权限不足，请检查角色权限配置或联系管理员";
          ElMessage.warning(permissionMsg);
          if (error && typeof error === "object") {
            error._permissionHandled = true;
            error._messageShown = true;
          }
          break;

        case 404:
          // 若有后端文案则优先展示
          ElMessage.error(data?.message || "请求的资源不存在");
          if (error && typeof error === "object") error._messageShown = true;
          break;

        case 400:
          // 业务校验/约束类提示（后端可能返回 error 或 message）
          ElMessage.warning(data?.error || data?.message || "请求无效");
          if (error && typeof error === "object") error._messageShown = true;
          break;

        case 422:
          {
            const errors = data?.errors || {};
            const errorMessages = Object.values(errors).flat();
            ElMessage.error(errorMessages.join(", ") || "请求参数错误");
            if (error && typeof error === "object") error._messageShown = true;
          }
          break;

        case 429:
          ElMessage.error("请求过于频繁，请稍后再试");
          if (error && typeof error === "object") error._messageShown = true;
          break;

        case 409:
          // 版本冲突等由业务层弹窗处理，此处不自动提示
          if (error && typeof error === "object") error._versionConflict = true;
          break;

        case 500:
          // 只有在悬浮状态下或非设备相关请求才显示错误提示
          if (config?.isHovering || !isDeviceDisconnected(response)) {
            ElMessage.error(data?.message || "服务器内部错误，请稍后再试");
            if (error && typeof error === "object") error._messageShown = true;
          }
          break;

        default:
          // 只有在悬浮状态下或非设备相关请求才显示错误提示
          if (config?.isHovering || !isDeviceDisconnected(response)) {
            ElMessage.error(data?.message || `请求失败 (${status})`);
            if (error && typeof error === "object") error._messageShown = true;
            console.error(`HTTP错误 ${status}:`, error);
          }
      }
    } else if (error.code === "ECONNABORTED") {
      // 只有在悬浮状态下才显示超时错误提示
      if (config?.isHovering) {
        ElMessage.error("请求超时，请检查网络连接");
      }
    } else {
      // 只有在悬浮状态下才显示网络错误提示
      if (config?.isHovering) {
        ElMessage.error("网络错误，请检查网络连接");
      }
    }

    return Promise.reject(error);
  },
);

/** 是否为权限不足类错误（拦截器已统一提示，业务 catch 可据此不再重复弹窗） */
export function isPermissionError(err) {
  return err?.response?.status === 403 || err?._permissionHandled === true;
}

export default request;
