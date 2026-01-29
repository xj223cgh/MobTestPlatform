<template>
  <div class="forgot-password-container">
    <div class="forgot-password-card">
      <div class="forgot-password-header">
        <div class="logo-text">
          MobTest
        </div>
        <h1>忘记密码</h1>
        <p>请输入您的邮箱地址，我们将发送重置密码链接</p>
      </div>

      <el-form
        ref="forgotFormRef"
        :model="forgotForm"
        :rules="forgotRules"
        class="forgot-password-form"
        @submit.prevent="handleForgotPassword"
      >
        <el-form-item prop="email">
          <el-input
            v-model="forgotForm.email"
            placeholder="请输入邮箱地址"
            size="large"
            prefix-icon="Message"
            clearable
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="forgot-btn"
            @click="handleForgotPassword"
          >
            发送重置链接
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

    <div class="forgot-password-footer">
      <p>&copy; 2024 移动端测试平台. All rights reserved.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { forgotPassword } from "@/api/auth";
import { ElMessage } from "element-plus";
import { ArrowLeft } from "@element-plus/icons-vue";

const router = useRouter();

// 表单引用
const forgotFormRef = ref(null);

// 加载状态
const loading = ref(false);

// 忘记密码表单
const forgotForm = reactive({
  email: "",
});

// 表单验证规则
const forgotRules = {
  email: [
    { required: true, message: "请输入邮箱地址", trigger: "blur" },
    { type: "email", message: "请输入有效的邮箱地址", trigger: "blur" },
  ],
};

// 处理忘记密码
const handleForgotPassword = async () => {
  if (!forgotFormRef.value) return;

  try {
    await forgotFormRef.value.validate();
    loading.value = true;

    const response = await forgotPassword({
      email: forgotForm.email,
    });

    if (response.success) {
      ElMessage.success("重置密码链接已发送到您的邮箱，请查收");
      setTimeout(() => {
        router.push("/login");
      }, 2000);
    } else {
      ElMessage.error(response.message || "发送失败");
    }
  } catch (error) {
    console.error("发送重置链接失败:", error);
    ElMessage.error(error.response?.data?.message || "发送失败");
  } finally {
    loading.value = false;
  }
};

// 跳转到登录页面
const goToLogin = () => {
  router.push("/login");
};
</script>

<style lang="scss" scoped>
.forgot-password-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.forgot-password-card {
  width: 100%;
  max-width: 400px;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
  margin-bottom: 20px;
}

.forgot-password-header {
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
    line-height: 1.5;
  }
}

.forgot-password-form {
  .el-form-item {
    margin-bottom: 20px;
  }

  .forgot-btn {
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

.forgot-password-footer {
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;

  p {
    margin: 0;
  }
}

// 响应式
@media (max-width: 480px) {
  .forgot-password-card {
    padding: 30px 20px;
  }

  .forgot-password-header {
    h1 {
      font-size: 24px;
    }

    p {
      font-size: 13px;
    }
  }
}
</style>
