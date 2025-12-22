import { defineStore } from "pinia";
import { ref, computed } from "vue";
import {
  login as loginApi,
  logout as logoutApi,
  checkSession,
} from "@/api/auth";
import { ElMessage } from "element-plus";

const USER_KEY = "mob_user";
const REMEMBER_KEY = "mob_remember";

export const useUserStore = defineStore("user", () => {
  // 状态
  const userInfo = ref(JSON.parse(sessionStorage.getItem(USER_KEY) || "null"));
  const loading = ref(false);

  // 计算属性
  const isAuthenticated = computed(() => !!userInfo.value);
  const userName = computed(() => userInfo.value?.username || "");
  const userRole = computed(() => userInfo.value?.role || "");
  const avatar = computed(() => userInfo.value?.avatar || "");

  // 登录
  const login = async (credentials) => {
    try {
      loading.value = true;
      const response = await loginApi(credentials);

      if (response.code === 200) {
        const { user } = response.data;

        // 保存用户信息到sessionStorage
        userInfo.value = user;
        sessionStorage.setItem(USER_KEY, JSON.stringify(user));

        // 处理记住我功能
        if (credentials.remember) {
          // 保存用户名和密码到localStorage（加密存储）
          const rememberData = {
            username: credentials.username,
            password: btoa(credentials.password), // 简单编码，实际项目中应使用更安全的加密
            remember: true,
          };
          localStorage.setItem(REMEMBER_KEY, JSON.stringify(rememberData));
        } else {
          // 清除记住的信息
          localStorage.removeItem(REMEMBER_KEY);
        }

        ElMessage.success(response.message || "登录成功");
        return true;
      } else {
        ElMessage.error(response.message || "登录失败");
        return false;
      }
    } catch (error) {
      ElMessage.error(error.response?.data?.message || "登录失败");
      return false;
    } finally {
      loading.value = false;
    }
  };

  // 登出
  const logout = async () => {
    try {
      // 尝试调用后端登出接口
      await logoutApi();
    } catch (error) {
      // 即使后端登出失败也要清除本地数据
      // 如果是网络错误或服务器错误，不显示错误提示给用户
      // 因为登出操作对用户来说应该是无感知的
      if (
        !(
          error.response?.status >= 500 ||
          error.code === "ECONNABORTED" ||
          !error.response
        )
      ) {
        // 其他错误（如4xx）也静默处理，因为登出总是要成功的
      }
    } finally {
      // 无论后端请求是否成功，都清除本地数据
      userInfo.value = null;
      sessionStorage.removeItem(USER_KEY);

      // 清除面包屑历史
      sessionStorage.removeItem("breadcrumbHistory");

      // 注意：不在这里清除记住的登录信息，让用户主动选择是否记住

      // 只有在真正需要时才显示成功消息
      // 避免在页面跳转时显示消息
      if (!window.location.pathname.includes("/login")) {
        ElMessage.success("已退出登录");
      }
    }
  };

  // 检查认证状态
  const checkAuth = async () => {
    try {
      loading.value = true;

      // 尝试调用检查会话接口
      const response = await checkSession();

      if (response.code === 200) {
        if (response.data.authenticated) {
          const { user } = response.data;
          userInfo.value = user;
          sessionStorage.setItem(USER_KEY, JSON.stringify(user));
          return true;
        } else {
          // 后端明确返回未认证，清除本地数据
          userInfo.value = null;
          sessionStorage.removeItem(USER_KEY);
          return false;
        }
      } else {
        // API调用成功但返回错误码，保留本地数据
        return !!userInfo.value;
      }
    } catch (error) {
      // 检查是否是接口不存在(404)错误
      if (error.response && error.response.status === 404) {
        // 接口未实现，保留本地数据
        return !!userInfo.value;
      } else {
        // 其他错误（网络错误、500等），保留本地数据
        // 只有当明确知道未认证时才清除数据
        return !!userInfo.value;
      }
    } finally {
      loading.value = false;
    }
  };

  // 更新用户信息
  const updateUserInfo = (newUserInfo) => {
    userInfo.value = { ...userInfo.value, ...newUserInfo };
    sessionStorage.setItem(USER_KEY, JSON.stringify(userInfo.value));
  };

  // 获取记住的登录信息
  const getRememberedCredentials = () => {
    try {
      const rememberedData = localStorage.getItem(REMEMBER_KEY);
      if (rememberedData) {
        const data = JSON.parse(rememberedData);
        if (data.remember && data.username && data.password) {
          return {
            username: data.username,
            password: atob(data.password), // 解码密码
            remember: true,
          };
        }
      }
      return null;
    } catch (error) {
      // 清除损坏的数据
      localStorage.removeItem(REMEMBER_KEY);
      return null;
    }
  };

  // 清除记住的登录信息
  const clearRememberedCredentials = () => {
    localStorage.removeItem(REMEMBER_KEY);
  };

  // 更新记住的登录信息（当用户在登录页面取消勾选记住我时调用）
  const updateRememberedCredentials = (username, password, remember) => {
    if (remember && username && password) {
      const rememberData = {
        username: username,
        password: btoa(password),
        remember: true,
      };
      localStorage.setItem(REMEMBER_KEY, JSON.stringify(rememberData));
    } else {
      localStorage.removeItem(REMEMBER_KEY);
    }
  };

  return {
    // 状态
    userInfo,
    loading,

    // 计算属性
    isAuthenticated,
    userName,
    userRole,
    avatar,

    // 方法
    login,
    logout,
    checkAuth,
    updateUserInfo,
    getRememberedCredentials,
    clearRememberedCredentials,
    updateRememberedCredentials,
  };
});
