<template>
  <div class="bug-management">
    <div class="page-header">
      <h1>缺陷管理</h1>
    </div>

    <!-- 缺省页面 -->
    <div class="bug-default-page">
      <el-empty
        description="缺陷管理功能正在开发中，敬请期待"
        :image-size="200"
      />
    </div>
  </div>
</template>

<script setup></script>

<style scoped>
.bug-management {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.page-header h1 {
  margin: 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.bug-default-page {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 60vh;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}
</style>
