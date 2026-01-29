<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <div class="logo-placeholder">
          <el-icon
            size="80"
            color="#667eea"
          >
            <Monitor />
          </el-icon>
        </div>
        <h1>移动测试平台</h1>
        <p>Mobile Test Platform</p>
      </div>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            size="large"
            prefix-icon="User"
            clearable
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            prefix-icon="Lock"
            show-password
            clearable
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <div class="login-options">
            <el-checkbox
              v-model="loginForm.remember"
              @change="handleRememberChange"
            >
              记住用户名密码
            </el-checkbox>
            <el-link
              type="primary"
              @click="goToForgotPassword"
            >
              忘记密码？
            </el-link>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="login-btn"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>

        <div class="register-link">
          <el-link
            type="primary"
            @click="goToRegister"
          >
            还没有账号？立即注册
          </el-link>
        </div>
      </el-form>
    </div>

    <div class="login-footer">
      <p>&copy; 2025 移动测试平台. All rights reserved.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "@/stores/user";
import { Monitor } from "@element-plus/icons-vue";

const router = useRouter();
const userStore = useUserStore();

// 表单引用
const loginFormRef = ref(null);

// 加载状态
const loading = ref(false);

// 登录表单
const loginForm = reactive({
  username: "",
  password: "",
  remember: false,
});

// 监听记住我复选框变化
const handleRememberChange = () => {
  if (!loginForm.remember) {
    // 如果用户取消勾选记住我，清除已记住的信息
    userStore.clearRememberedCredentials();
  } else if (loginForm.username && loginForm.password) {
    // 如果用户勾选记住我且有用户名密码，更新记住的信息
    userStore.updateRememberedCredentials(
      loginForm.username,
      loginForm.password,
      true,
    );
  }
};

// 页面加载时检查记住的登录信息
onMounted(() => {
  const rememberedCredentials = userStore.getRememberedCredentials();
  if (rememberedCredentials) {
    loginForm.username = rememberedCredentials.username;
    loginForm.password = rememberedCredentials.password;
    loginForm.remember = rememberedCredentials.remember;
  }
});

// 表单验证规则
const loginRules = {
  username: [
    { required: true, message: "请输入用户名", trigger: "blur" },
    {
      min: 3,
      max: 20,
      message: "用户名长度在 3 到 20 个字符",
      trigger: "blur",
    },
  ],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 6, message: "密码长度不能少于 6 个字符", trigger: "blur" },
  ],
};

// 处理登录
const handleLogin = async () => {
  if (!loginFormRef.value) return;

  try {
    await loginFormRef.value.validate();
    loading.value = true;

    const success = await userStore.login({
      username: loginForm.username,
      password: loginForm.password,
      remember: loginForm.remember,
    });

    if (success) {
      // 登录成功，跳转到首页
      router.push("/home");
    }
  } catch (error) {
    console.error("登录失败:", error);
  } finally {
    loading.value = false;
  }
};

// 跳转到注册页面
const goToRegister = () => {
  router.push("/register");
};

// 跳转到忘记密码页面
const goToForgotPassword = () => {
  router.push("/forgot-password");
};
</script>

<style lang="scss" scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px; // 从450px减小到400px
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  padding: 30px 30px 20px 30px; // 减少下内边距从30px到20px
  margin-bottom: 20px;
}

.login-header {
  text-align: center;
  margin-bottom: 25px; // 与注册页面保持一致的头部间距

  .logo-placeholder {
    margin-bottom: 20px;
    display: flex;
    justify-content: center;
  }

  h1 {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 10px 0;
  }

  p {
    font-size: 14px;
    color: #909399;
    margin: 0;
  }
}

.login-form {
  min-height: 286px;
  display: flex;
  flex-direction: column;

  .el-form {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: space-between;

    .el-form-item {
      margin-bottom: 18px;

      &:last-child {
        margin-bottom: 0;
      }
    }
  }

  .login-options {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    font-size: 14px;
    padding: 4px 0; // 增加一些垂直内边距
  }

  .login-btn {
    width: 100%;
    height: 45px;
    font-size: 16px;
    font-weight: 500;
  }

  // 记住账号密码复选框样式
  :deep(.el-checkbox) {
    .el-checkbox__label {
      color: #606266;
      font-size: 14px;
      line-height: 1.5;
    }

    .el-checkbox__input.is-checked + .el-checkbox__label {
      color: #606266;
    }
  }
}

.register-link {
  text-align: center;
  margin-top: 6px; // 从8px减少到6px，进一步减少上边距
  font-size: 14px;
  color: #606266; // 与注册页面保持一致的文本颜色
}

.login-footer {
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;

  p {
    margin: 0;
  }
}

// 响应式
@media (max-width: 480px) {
  .login-card {
    padding: 30px 20px;
  }

  .login-header {
    h1 {
      font-size: 24px;
    }
  }

  .login-form {
    .login-options {
      flex-direction: column;
      gap: 10px;
      align-items: flex-start;
    }
  }
}
</style>
