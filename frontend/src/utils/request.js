import axios from "axios";
import { ElMessage, ElMessageBox } from "element-plus";
import { useUserStore } from "@/stores/user";
import router from "@/router";

// 创建axios实例
const request = axios.create({
  baseURL: "/api", // API基础路径，用于Vite代理转发
  timeout: 30000, // 增加超时时间到30秒
  withCredentials: true, // 支持跨域cookie
  headers: {
    "Content-Type": "application/json",
  },
});

// 设备断开连接错误提示的防抖计时器
let disconnectAlertTimer = null;
const MIN_ALERT_INTERVAL = 2000; // 最小提示间隔，单位：毫秒

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // Session认证不需要手动添加token，浏览器会自动处理session cookie
    return config;
  },
  (error) => {
    console.error("请求错误:", error);
    return Promise.reject(error);
  },
);

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    const res = response?.data || {};

    // 如果响应中包含code字段且不为200，则认为是业务错误
    if (res.code && res.code !== 200) {
      ElMessage.error(res.message || "操作失败");
      return Promise.reject(new Error(res.message || "操作失败"));
    }

    // 为成功响应添加success字段
    res.success = true;
    return res;
  },
  async (error) => {
    const { response, config } = error;
    const userStore = useUserStore();

    // 检查是否是设备断开连接导致的错误
    const isDeviceDisconnected = (response) => {
      const errorMessage = response?.data?.message || "";
      const requestUrl = config?.url || "";
      // 检查错误信息或URL中是否包含设备相关的断开连接关键词
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

      // 先检查是否是设备断开连接导致的错误
      if (isDeviceDisconnected(response)) {
        // 只有在悬浮状态下才显示设备断开连接的错误提示
        if (config?.isHovering) {
          // 添加防抖机制，确保短时间内只显示一次错误提示
          if (!disconnectAlertTimer) {
            ElMessage.error("设备已断开连接，请检查设备连接状态");
            // 设置防抖计时器
            disconnectAlertTimer = setTimeout(() => {
              disconnectAlertTimer = null;
            }, MIN_ALERT_INTERVAL);
          }
        }
        return Promise.reject(error);
      }

      switch (status) {
        case 401:
          // 检查是否是登录接口的401错误
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
          // 权限不足
          ElMessage.error("权限不足，无法访问该资源");
          router.push("/403");
          break;

        case 404:
          // 资源不存在
          ElMessage.error("请求的资源不存在");
          break;

        case 422:
          // 表单验证错误
          {
            const errors = data?.errors || {};
            const errorMessages = Object.values(errors).flat();
            ElMessage.error(errorMessages.join(", ") || "请求参数错误");
          }
          break;

        case 429:
          // 请求过于频繁
          ElMessage.error("请求过于频繁，请稍后再试");
          break;

        case 500:
          // 服务器错误
          // 只有在悬浮状态下或非设备相关请求才显示错误提示
          if (config?.isHovering || !isDeviceDisconnected(response)) {
            ElMessage.error(data?.message || "服务器内部错误，请稍后再试");
          }
          break;

        default:
          // 其他错误
          // 只有在悬浮状态下或非设备相关请求才显示错误提示
          if (config?.isHovering || !isDeviceDisconnected(response)) {
            ElMessage.error(data?.message || `请求失败 (${status})`);
            console.error(`HTTP错误 ${status}:`, error);
          }
      }
    } else if (error.code === "ECONNABORTED") {
      // 请求超时
      // 只有在悬浮状态下才显示超时错误提示
      if (config?.isHovering) {
        ElMessage.error("请求超时，请检查网络连接");
      }
    } else {
      // 网络错误
      // 只有在悬浮状态下才显示网络错误提示
      if (config?.isHovering) {
        ElMessage.error("网络错误，请检查网络连接");
      }
    }

    return Promise.reject(error);
  },
);

export default request;
