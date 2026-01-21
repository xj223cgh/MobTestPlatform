<template>
  <el-tooltip placement="top" content="移除设备">
    <el-button
      type="danger"
      text
      :loading="loading"
      @click="handleClick(device)"
    >
      <template #icon>
        <el-icon v-if="!loading">
          <Delete />
        </el-icon>
      </template>
    </el-button>
  </el-tooltip>
</template>

<script setup>
import { ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Delete } from "@element-plus/icons-vue";
import deviceApi from "@/api/device";

const props = defineProps({
  device: {
    type: Object,
    default: () => ({}),
  },
  handleRefresh: {
    type: Function,
    default: () => {},
  },
});

const loading = ref(false);

async function handleClick(device = props.device) {
  try {
    // 确认移除
    await ElMessageBox.confirm(
      `确定要移除设备 ${device.name || device.id} 吗？`,
      "确认移除",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      },
    );

    loading.value = true;

    // 如果设备在数据库中存在，则删除数据库记录
    if (device.db_id) {
      await deviceApi.deleteDevice(device.db_id);
    }

    // 刷新设备列表
    props.handleRefresh();

    ElMessage.success("设备已移除");
  } catch (error) {
    if (error !== "cancel") {
      console.warn("移除设备失败:", error);
      ElMessage.error(
        "移除设备失败：" + (error.response?.data?.message || error.message),
      );
    }
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
