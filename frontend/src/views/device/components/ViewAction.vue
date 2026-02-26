<template>
  <el-tooltip
    placement="top"
    content="查看详情"
  >
    <el-button
      type="primary"
      text
      @click="handleClick(row)"
    >
      <template #icon>
        <el-icon><View /></el-icon>
      </template>
    </el-button>
  </el-tooltip>
</template>

<script setup>
import { View } from "@element-plus/icons-vue";

const props = defineProps({
  row: {
    type: Object,
    default: () => ({}),
  },
});

const emit = defineEmits(["view"]);

function handleClick(row = props.row) {
  emit("view", row);
}
</script>

<style lang="scss" scoped>
:deep() .el-button {
  padding: 4px 8px;
}
</style>
