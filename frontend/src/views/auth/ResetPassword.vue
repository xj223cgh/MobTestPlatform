<template>
  <div class="reset-password-container">
    <div class="reset-password-card">
      <div class="reset-password-header">
        <div class="logo-text">
          MobTest
        </div>
        <h1>重置密码</h1>
        <p>请设置您的新密码</p>
      </div>

      <el-form
        ref="resetFormRef"
        :model="resetForm"
        :rules="resetRules"
        class="reset-password-form"
        @submit.prevent="handleResetPassword"
      >
        <el-form-item prop="password">
          <el-input
            v-model="resetForm.password"
            type="password"
            placeholder="请输入新密码"
            size="large"
            prefix-icon="Lock"
            show-password
            clearable
          />
        </el-form-item>

        <el-form-item prop="confirmPassword">
          <el-input
            v-model="resetForm.confirmPassword"
            type="password"
            placeholder="请确认新密码"
            size="large"
            prefix-icon="Lock"
            show-password
            clearable
            @keyup.enter="handleResetPassword"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="reset-btn"
            @click="handleResetPassword"
          >
            重置密码
          </el-button>
        </el-form-item>

        <div class="back-link">
          <el-link
            type="primary"
            @click="goToLogin"
          >
            <el-icon><ArrowLeft /></el-icon>
            返回登录
          </el-link>
        </div>
      </el-form>
    </div>

    <div class="reset-password-footer">
      <p>&copy; 2024 移动端测试平台. All rights reserved.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { resetPassword } from "@/api/auth";
import { ElMessage } from "element-plus";
import { ArrowLeft } from "@element-plus/icons-vue";

const router = useRouter();
const route = useRoute();

// 表单引用
const resetFormRef = ref(null);

// 加载状态
const loading = ref(false);

// 重置密码表单
const resetForm = reactive({
  password: "",
  confirmPassword: "",
});

// 邮箱和token
const email = ref("");
const token = ref("");

// 密码验证器
const validatePassword = (rule, value, callback) => {
  if (value === "") {
    callback(new Error("请输入新密码"));
  } else if (value.length < 6) {
    callback(new Error("密码长度不能少于 6 个字符"));
  } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(value)) {
    callback(new Error("密码必须包含大小写字母和数字"));
  } else {
    if (resetForm.confirmPassword !== "") {
      resetFormRef.value?.validateField("confirmPassword");
    }
    callback();
  }
};

// 确认密码验证器
const validateConfirmPassword = (rule, value, callback) => {
  if (value === "") {
    callback(new Error("请再次输入密码"));
  } else if (value !== resetForm.password) {
    callback(new Error("两次输入密码不一致"));
  } else {
    callback();
  }
};

// 表单验证规则
const resetRules = {
  password: [{ validator: validatePassword, trigger: "blur" }],
  confirmPassword: [{ validator: validateConfirmPassword, trigger: "blur" }],
};

// 处理重置密码
const handleResetPassword = async () => {
  if (!resetFormRef.value) return;

  try {
    await resetFormRef.value.validate();
    loading.value = true;

    const response = await resetPassword({
      email: email.value,
      token: token.value,
      password: resetForm.password,
    });

    if (response.success) {
      ElMessage.success("密码重置成功，请登录");
      setTimeout(() => {
        router.push("/login");
      }, 1500);
    } else {
      ElMessage.error(response.message || "重置失败");
    }
  } catch (error) {
    console.error("重置密码失败:", error);
    ElMessage.error(error.response?.data?.message || "重置失败");
  } finally {
    loading.value = false;
  }
};

// 跳转到登录页面
const goToLogin = () => {
  router.push("/login");
};

// 初始化
onMounted(() => {
  // 从查询参数获取邮箱和token
  email.value = route.query.email || "";
  token.value = route.query.token || "";

  if (!email.value || !token.value) {
    ElMessage.error("重置链接无效，请重新申请");
    router.push("/forgot-password");
  }
});
</script>

<style lang="scss" scoped>
.reset-password-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.reset-password-card {
  width: 100%;
  max-width: 400px;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
  margin-bottom: 20px;
}

.reset-password-header {
  text-align: center;
  margin-bottom: 30px;

  .logo-text {
    font-size: 32px;
    font-weight: 700;
    color: $primary-color;
    margin-bottom: 20px;
    letter-spacing: 2px;
  }

  h1 {
    font-size: 28px;
    font-weight: 600;
    color: $text-primary;
    margin: 0 0 10px 0;
  }

  p {
    font-size: 14px;
    color: $text-secondary;
    margin: 0;
  }
}

.reset-password-form {
  .el-form-item {
    margin-bottom: 20px;
  }

  .reset-btn {
    width: 100%;
    height: 45px;
    font-size: 16px;
    font-weight: 500;
  }
}

.back-link {
  text-align: center;
  margin-top: 20px;

  .el-link {
    font-size: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
  }
}

.reset-password-footer {
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;

  p {
    margin: 0;
  }
}

// 响应式
@media (max-width: 480px) {
  .reset-password-card {
    padding: 30px 20px;
  }

  .reset-password-header {
    h1 {
      font-size: 24px;
    }
  }
}
</style>
