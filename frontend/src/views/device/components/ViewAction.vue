<template>
  <el-tooltip placement="top" content="查看详情">
    <el-button type="primary" text @click="handleClick(row)">
      <template #icon>
        <el-icon><View /></el-icon>
      </template>
    </el-button>
  </el-tooltip>
</template>

<script setup>
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { View } from "@element-plus/icons-vue";

const props = defineProps({
  row: {
    type: Object,
    default: () => ({}),
  },
  isOnline: {
    type: Boolean,
    default: false,
  },
});

const router = useRouter();

function handleClick(row = props.row) {
  if (!props.isOnline) {
    ElMessage.warning("当前设备离线，无法查看详情");
    return;
  }

  router.push({
    name: "DeviceDetail",
    params: { id: row.id },
  });
}
</script>

<style lang="scss" scoped>
:deep() .el-button {
  padding: 4px 8px;
}
</style>
