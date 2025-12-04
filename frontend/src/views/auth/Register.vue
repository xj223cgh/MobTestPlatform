<template>
  <div class="register-container">
    <div class="register-card">
      <div class="register-header">
        <h1>用户注册</h1>
        <p class="register-subtitle">
          Mobile Test Platform
        </p>
      </div>

      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        class="register-form"
        @submit.prevent="handleRegister"
      >
        <el-form-item prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="请输入用户名"
            size="large"
            prefix-icon="User"
            clearable
          />
        </el-form-item>

        <el-form-item prop="phone">
          <el-input
            v-model="registerForm.phone"
            placeholder="请输入手机号"
            size="large"
            prefix-icon="Phone"
            clearable
          />
        </el-form-item>

        <el-form-item prop="realName">
          <el-input
            v-model="registerForm.realName"
            placeholder="请输入真实姓名"
            size="large"
            prefix-icon="User"
            clearable
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            prefix-icon="Lock"
            show-password
            clearable
            @keyup.enter="handleRegister"
          />
        </el-form-item>

        <el-form-item prop="agreement">
          <div class="agreement-options">
            <el-checkbox v-model="registerForm.agreement">
              我已阅读并同意
              <el-link
                type="primary"
                style="vertical-align: baseline;"
                @click="showAgreement"
              >
                《用户协议》
              </el-link>
              和
              <el-link
                type="primary"
                style="vertical-align: baseline;"
                @click="showPrivacy"
              >
                《隐私政策》
              </el-link>
            </el-checkbox>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="register-btn"
            @click="handleRegister"
            @keyup.enter="handleRegister"
          >
            注册
          </el-button>
        </el-form-item>

        <div class="login-link">
          <el-link
            type="primary"
            @click="goToLogin"
          >
            已有账号？立即登录
          </el-link>
        </div>
      </el-form>
    </div>

    <div class="register-footer">
      <p>&copy; 2025 移动测试平台. All rights reserved.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { register } from '@/api/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()

// 表单引用
const registerFormRef = ref(null)

// 加载状态
const loading = ref(false)

// 注册表单
const registerForm = reactive({
  username: '',
  phone: '',
  realName: '',
  password: '',
  agreement: false
})

// 密码验证器
const validatePassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请输入密码'))
  } else if (value.length < 6) {
    callback(new Error('密码长度不能少于 6 个字符'))
  } else {
    callback()
  }
}

// 表单验证规则
const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号', trigger: 'blur' }
  ],
  realName: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '姓名长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { validator: validatePassword, trigger: 'blur' }
  ],
  agreement: [
    { required: true, message: '请同意用户协议和隐私政策', trigger: 'change' }
  ]
}

// 处理注册
const handleRegister = async () => {
  if (!registerFormRef.value) return

  // 显式检查隐私协议是否勾选
  if (!registerForm.agreement) {
    ElMessage.warning('请阅读并同意用户协议和隐私政策')
    return
  }

  try {
    await registerFormRef.value.validate()
    loading.value = true

    const response = await register({
      username: registerForm.username,
      phone: registerForm.phone,
      real_name: registerForm.realName,
      password: registerForm.password
    })

    if (response.code === 200) {
      ElMessage.success('注册成功，请登录')
      router.push('/login')
    } else {
      ElMessage.error(response.message || '注册失败')
    }
  } catch (error) {
    console.error('注册失败:', error)
    // 如果是验证错误，不显示额外错误信息，避免重复提示
    if (error.name !== 'Error') {
      ElMessage.error(error.response?.data?.message || '注册失败，请稍后重试')
    }
  } finally {
    loading.value = false
  }
}

// 跳转到登录页面
const goToLogin = () => {
  router.push('/login')
}

// 显示用户协议
const showAgreement = () => {
  ElMessage.info('用户协议页面待完善')
}

// 显示隐私政策
const showPrivacy = () => {
  ElMessage.info('隐私政策页面待完善')
}
</script>

<style lang="scss" scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-card {
  width: 100%;
  max-width: 400px; // 从450px减小到400px
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  padding: 30px 30px 20px 30px; // 统一与登录页面一致：减少下内边距从30px到20px
  margin-bottom: 20px;
}

.register-header {
  text-align: center;
  margin-bottom: 25px; // 与登录页面保持一致的头部间距

  h1 {
    font-size: 28px;
    font-weight: 600;
    color: #303133; // 与登录页面保持一致的标题颜色
    margin: 0 0 10px 0;
  }

  .register-subtitle {
    font-size: 14px;
    color: #909399; // 与登录页面保持一致的副标题颜色
    margin: 0;
    font-weight: normal;
  }
}

.register-form {
  min-height: 380px; // 由于注册页面字段更多，适当增加高度到380px
  display: flex;
  flex-direction: column;
  
  .el-form {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    
    .el-form-item {
      margin-bottom: 18px; // 从24px减少到18px，减少整体高度
      
      &:last-child {
        margin-bottom: 0;
      }
    }
  }

  .register-btn {
    width: 100%;
    height: 45px; // 与登录按钮保持一致的高度
    font-size: 16px;
    font-weight: 500;
  }

  // 用户协议复选框样式
  .agreement-options {
    width: 100%;
    font-size: 14px;
    padding: 4px 0; // 与登录页面保持一致的垂直内边距
  }

  .el-checkbox {
    :deep(.el-checkbox__label) {
      color: #606266; // 与登录页面保持一致的文本颜色
      font-size: 14px;
      line-height: 1.5;
      
      // 确保复选框文本颜色不受勾选状态影响
      .el-link {
        font-size: inherit;
        line-height: inherit;
      }
    }
    
    // 确保复选框文本颜色不受勾选状态影响
    :deep(.el-checkbox__input.is-checked + .el-checkbox__label) {
      color: #606266;
    }
  }
}

.login-link {
  text-align: center;
  margin-top: 6px; // 从8px减少到6px，进一步减少上边距
  font-size: 14px;
  color: #606266; // 与登录页面保持一致的文本颜色
}

.register-footer {
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;

  p {
    margin: 0;
  }
}

// 响应式
@media (max-width: 480px) {
  .register-card {
    padding: 30px 20px;
  }

  .register-header {
    h1 {
      font-size: 24px;
    }
  }
  
  // 确保注册页面在小屏幕下也有相同的响应式处理
  .register-form {
    .agreement-options {
      padding: 2px 0; // 在小屏幕下减少垂直内边距
    }
    
    .el-form-item {
      margin-bottom: 16px; // 在小屏幕下进一步减少间距
    }
  }
}
</style>