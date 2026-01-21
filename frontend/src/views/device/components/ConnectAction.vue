<template>
  <el-tooltip placement="top" :content="loading ? '连接中...' : '连接设备'">
    <el-button
      type="primary"
      text
      :loading="loading"
      @click="handleClick(device)"
    >
      <template #icon>
        <el-icon v-if="!loading">
          <Connection />
        </el-icon>
      </template>
    </el-button>
  </el-tooltip>
</template>

<script setup>
import { ref } from "vue";
import { ElMessage } from "element-plus";
import { Connection } from "@element-plus/icons-vue";

const props = defineProps({
  device: {
    type: Object,
    default: () => ({}),
  },
  handleConnect: {
    type: Function,
    default: () => false,
  },
});

const loading = ref(false);

async function handleClick(device) {
  loading.value = true;

  try {
    await props.handleConnect(device.id);
    ElMessage.success("设备连接成功");
  } catch (error) {
    console.warn("设备连接失败:", error);
    ElMessage.error("设备连接失败");
  } finally {
    loading.value = false;
  }
}
</script>

<style lang="scss" scoped>
:deep() .el-button {
  padding: 4px 8px;
}
</style>
