<template>
  <div class="test-task-management">
    <div class="default-page-container">
      <div class="default-page">
        <el-empty
          description="测试任务功能正在开发中"
          :image-size="200"
        >
          <!-- 可以在这里添加一些操作按钮，如果需要的话 -->
        </el-empty>
      </div>
    </div>
  </div>
</template>

<script setup>
// 测试任务功能缺省页面
</script>
<style lang="scss" scoped>
.test-task-management {
  padding: 20px;
}

.default-page-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 600px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.default-page {
  width: 100%;
  max-width: 600px;
  text-align: center;
  padding: 40px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}
</style>
