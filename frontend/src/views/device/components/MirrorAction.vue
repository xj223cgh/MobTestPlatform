<template>
  <el-tooltip placement="top" :content="loading ? '启动中...' : '启动投屏'">
    <el-button
      type="primary"
      text
      :disabled="['unauthorized', 'offline'].includes(row.status)"
      :loading="loading"
      @click="handleClick(row)"
    >
      <template #icon>
        <el-icon v-if="!loading"><Monitor /></el-icon>
      </template>
    </el-button>
  </el-tooltip>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Monitor } from '@element-plus/icons-vue'
import deviceApi from '@/api/device'

const props = defineProps({
  row: {
    type: Object,
    default: () => ({}),
  },
  toggleRowExpansion: {
    type: Function,
    default: () => () => false,
  },
})

const loading = ref(false)

async function handleClick(row = props.row) {
  loading.value = true

  props.toggleRowExpansion(row, true)

  try {
    // 调用后端API启动投屏，执行scrcpy命令
    // 使用与原escrcpy相同的命令格式，确保独立窗口显示
    await deviceApi.executeAdbCommand(`scrcpy --serial="${row.id}" --window-title="设备 ${row.id} 投屏" --disable-screensaver`)
    
    loading.value = false
    ElMessage.success('投屏启动成功')
  } catch (error) {
    console.error('投屏失败:', error)
    loading.value = false
    // 错误信息由全局拦截器处理，这里只需重置状态
  }
}
</script>

<style lang="scss" scoped>
:deep() .el-button {
  padding: 4px 8px;
}
</style>
