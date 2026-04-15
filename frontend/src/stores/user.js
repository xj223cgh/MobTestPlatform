/** 用户状态：登录态、权限、个人信息。 */
import { defineStore } from "pinia";
import { ref, computed } from "vue";
import {
  login as loginApi,
  loginByEmail as loginByEmailApi,
  logout as logoutApi,
  checkSession,
  getPermissions as getPermissionsApi,
} from "@/api/auth";
import { ElMessage } from "element-plus";

const USER_KEY = "mob_user";
const PERMISSIONS_KEY = "mob_permissions";
const REMEMBER_KEY = "mob_remember";

export const useUserStore = defineStore("user", () => {
  const userInfo = ref(JSON.parse(sessionStorage.getItem(USER_KEY) || "null"));
  const permissions = ref(JSON.parse(sessionStorage.getItem(PERMISSIONS_KEY) || "[]"));
  const loading = ref(false);

  const isAuthenticated = computed(() => !!userInfo.value);
  const userName = computed(() => userInfo.value?.username || "");
  const userRole = computed(() => userInfo.value?.role || "");
  const avatar = computed(() => userInfo.value?.avatar || "");

  /** 账号密码登录；成功后持久化用户信息与权限到 sessionStorage，remember 时额外写 localStorage */
  const login = async (credentials) => {
    try {
      loading.value = true;
      const response = await loginApi(credentials);

      if (response.code === 200) {
        const { user, permissions: permList } = response.data;

        userInfo.value = user;
        sessionStorage.setItem(USER_KEY, JSON.stringify(user));
        const permArr = Array.isArray(permList) ? permList : [];
        permissions.value = permArr;
        sessionStorage.setItem(PERMISSIONS_KEY, JSON.stringify(permArr));

        if (credentials.remember) {
          const rememberData = {
            username: credentials.username,
            password: btoa(credentials.password), // 简单编码，实际项目中应使用更安全的加密
            remember: true,
          };
          localStorage.setItem(REMEMBER_KEY, JSON.stringify(rememberData));
        } else {
          localStorage.removeItem(REMEMBER_KEY);
        }

        ElMessage.success(response.message || "登录成功");
        return true;
      } else {
        ElMessage.error(response.message || "登录失败");
        return false;
      }
    } catch (error) {
      if (!error._messageShown) {
        ElMessage.error(error.response?.data?.message || "登录失败");
      }
      return false;
    } finally {
      loading.value = false;
    }
  };

  const loginByEmail = async (payload) => {
    try {
      loading.value = true;
      const response = await loginByEmailApi(payload);
      if (response.code === 200) {
        const { user, permissions: permList } = response.data;
        userInfo.value = user;
        sessionStorage.setItem(USER_KEY, JSON.stringify(user));
        const permArr = Array.isArray(permList) ? permList : [];
        permissions.value = permArr;
        sessionStorage.setItem(PERMISSIONS_KEY, JSON.stringify(permArr));
        ElMessage.success(response.message || "登录成功");
        return true;
      } else {
        ElMessage.error(response.message || "登录失败");
        return false;
      }
    } catch (error) {
      if (!error._messageShown) {
        ElMessage.error(error.response?.data?.message || "登录失败");
      }
      return false;
    } finally {
      loading.value = false;
    }
  };

  /** 登出：无论后端是否成功都清空本地状态，保证用户一定能退出 */
  const logout = async () => {
    try {
      await logoutApi();
    } catch (error) {
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
      userInfo.value = null;
      permissions.value = [];
      sessionStorage.removeItem(USER_KEY);
      sessionStorage.removeItem(PERMISSIONS_KEY);
      localStorage.removeItem("testCaseExpandedKeys");
      localStorage.removeItem("testCaseSelectedSuite");

      if (!window.location.pathname.includes("/login")) {
        ElMessage.success("已退出登录");
      }
    }
  };

  /** 校验会话有效性：401 强制踢出，网络/500 等保留本地状态避免误踢 */
  const checkAuth = async () => {
    try {
      loading.value = true;
      const response = await checkSession();

      if (response.code === 200 && response.data) {
        if (response.data.authenticated && response.data.user) {
          userInfo.value = response.data.user;
          sessionStorage.setItem(USER_KEY, JSON.stringify(response.data.user));
          try {
            const permRes = await getPermissionsApi();
            if (permRes.code === 200 && Array.isArray(permRes.data?.permissions)) {
              permissions.value = permRes.data.permissions;
              sessionStorage.setItem(PERMISSIONS_KEY, JSON.stringify(permRes.data.permissions));
            }
          } catch (_) {}
          return true;
        }
        userInfo.value = null;
        permissions.value = [];
        sessionStorage.removeItem(USER_KEY);
        sessionStorage.removeItem(PERMISSIONS_KEY);
        return false;
      }
      // 非 200 或无 data：无法确认状态，保留本地
      return !!userInfo.value;
    } catch (error) {
      const status = error.response?.status;
      if (status === 401) {
        userInfo.value = null;
        permissions.value = [];
        sessionStorage.removeItem(USER_KEY);
        sessionStorage.removeItem(PERMISSIONS_KEY);
        return false;
      }
      // 404/500/网络错误等：不强制踢出，保留本地状态
      return !!userInfo.value;
    } finally {
      loading.value = false;
    }
  };

  const updateUserInfo = (newUserInfo) => {
    userInfo.value = { ...userInfo.value, ...newUserInfo };
    sessionStorage.setItem(USER_KEY, JSON.stringify(userInfo.value));
  };

  const getRememberedCredentials = () => {
    try {
      const rememberedData = localStorage.getItem(REMEMBER_KEY);
      if (rememberedData) {
        const data = JSON.parse(rememberedData);
        if (data.remember && data.username && data.password) {
          return {
            username: data.username,
            password: atob(data.password),
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

  const clearRememberedCredentials = () => {
    localStorage.removeItem(REMEMBER_KEY);
  };

  /** 判断当前用户是否拥有指定权限埋点 */
  const hasPermission = (code) => {
    if (!permissions.value || !Array.isArray(permissions.value)) return false;
    return permissions.value.includes(code);
  };

  const fetchPermissions = async () => {
    try {
      const res = await getPermissionsApi();
      if (res.code === 200 && Array.isArray(res.data?.permissions)) {
        permissions.value = res.data.permissions;
        sessionStorage.setItem(PERMISSIONS_KEY, JSON.stringify(res.data.permissions));
        return true;
      }
    } catch (_) {}
    return false;
  };

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
    userInfo,
    permissions,
    loading,

    isAuthenticated,
    userName,
    userRole,
    avatar,

    login,
    loginByEmail,
    logout,
    checkAuth,
    updateUserInfo,
    hasPermission,
    fetchPermissions,
    getRememberedCredentials,
    clearRememberedCredentials,
    updateRememberedCredentials,
  };
});
