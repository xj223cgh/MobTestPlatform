<template>
  <div class="device-management">
    <div class="page-header">
      <div class="header-content">
        <h1>设备管理</h1>
      </div>
    </div>

    <!-- 缺省页面 -->
    <div class="device-default-page">
      <el-empty
        description="设备管理功能正在开发中，敬请期待"
        :image-size="200"
      />
    </div>
  </div>
</template>

<script setup></script>

<style lang="scss" scoped>
.device-management {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;

  .header-content {
    h1 {
      margin: 0;
      font-size: 24px;
      font-weight: 600;
      color: #303133;
    }
  }
}

.device-default-page {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 60vh;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}
</style>
