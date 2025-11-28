<template>
  <div class="error-container">
    <div class="error-content">
      <div class="error-icon">
        <el-icon size="120" color="#f56c6c">
          <Lock />
        </el-icon>
      </div>
      <h1 class="error-title">403</h1>
      <h2 class="error-subtitle">访问被拒绝</h2>
      <p class="error-description">
        抱歉，您没有权限访问此页面。请联系管理员获取相应权限。
      </p>
      <div class="error-actions">
        <el-button type="primary" size="large" @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回上页
        </el-button>
        <el-button size="large" @click="goHome">
          <el-icon><HomeFilled /></el-icon>
          返回首页
        </el-button>
      </div>
    </div>
    <div class="error-footer">
      <p>&copy; 2024 移动端测试平台. All rights reserved.</p>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ArrowLeft, HomeFilled, Lock } from '@element-plus/icons-vue'

const router = useRouter()

// 返回上一页
const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    router.push('/')
  }
}

// 返回首页
const goHome = () => {
  router.push('/')
}
</script>

<style lang="scss" scoped>
.error-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

.error-content {
  text-align: center;
  max-width: 600px;
}

.error-icon {
  margin-bottom: 30px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

.error-title {
  font-size: 120px;
  font-weight: 700;
  color: #f56c6c;
  margin: 0;
  line-height: 1;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

.error-subtitle {
  font-size: 32px;
  font-weight: 600;
  color: $text-primary;
  margin: 20px 0;
}

.error-description {
  font-size: 16px;
  color: $text-secondary;
  margin: 20px 0 40px 0;
  line-height: 1.6;
}

.error-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;

  .el-button {
    min-width: 120px;
    height: 45px;
    font-size: 16px;
    font-weight: 500;
  }
}

.error-footer {
  position: absolute;
  bottom: 20px;
  text-align: center;
  color: $text-secondary;
  font-size: 14px;

  p {
    margin: 0;
  }
}

// 响应式
@media (max-width: 768px) {
  .error-title {
    font-size: 80px;
  }

  .error-subtitle {
    font-size: 24px;
  }

  .error-description {
    font-size: 14px;
  }

  .error-actions {
    flex-direction: column;
    align-items: center;

    .el-button {
      width: 200px;
    }
  }
}

@media (max-width: 480px) {
  .error-content {
    padding: 20px;
  }

  .error-title {
    font-size: 60px;
  }

  .error-subtitle {
    font-size: 20px;
  }

  .error-icon {
    margin-bottom: 20px;
  }
}
</style>