<template>
  <div>
    <el-tooltip v-if="!row.wifi" placement="top" content="开启无线模式">
      <el-button
        type="primary"
        text
        :disabled="!isOnline"
        @click="handleWifi(row)"
      >
        <template #icon>
        <el-icon><Connection /></el-icon>
      </template>
      </el-button>
    </el-tooltip>

    <el-tooltip v-if="row.wifi" placement="top" :content="stopLoading ? '断开连接中...' : '断开无线连接'">
      <el-button
        type="danger"
        text
        :loading="stopLoading"
        :disabled="!isOnline"
        @click="handleStop(row)"
      >
        <template #icon>
          <el-icon v-if="!stopLoading"><Close /></el-icon>
        </template>
      </el-button>
    </el-tooltip>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Connection, Close } from '@element-plus/icons-vue'
import deviceApi from '@/api/device'

const props = defineProps({
  row: {
    type: Object,
    default: () => ({}),
  },
  handleConnect: {
    type: Function,
    default: () => () => false,
  },
  handleRefresh: {
    type: Function,
    default: () => () => false,
  },
  isOnline: {
    type: Boolean,
    default: false,
  },
})

const stopLoading = ref(false)

async function handleWifi(row) {
  try {
    // 调用后端API获取设备IP，指定设备ID
    const ipResponse = await deviceApi.executeAdbCommand(`-s ${row.id} shell ifconfig wlan0 | grep 'inet ' | awk '{print $2}'`)
    const host = ipResponse.data.stdout.trim()
    
    if (!host) {
      throw new Error('无法获取设备IP地址')
    }
    
    // 调用后端API开启tcpip模式，指定设备ID
    await deviceApi.executeAdbCommand(`-s ${row.id} tcpip 5555`)
    
    // 模拟延迟，确保tcpip模式已启动
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 连接到设备
    await props.handleConnect(`${host}:5555`)
    
    ElMessage.success('无线模式已开启')
  }
  catch (error) {
    console.warn('开启无线模式失败:', error)
    ElMessage.error('开启无线模式失败')
  }
}

async function handleStop(row) {
  stopLoading.value = true

  try {
    // 调用后端API断开设备连接
    await deviceApi.executeAdbCommand(`disconnect ${row.id}`)
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 更新数据库中的设备状态为offline
    if (row.db_id) {
      await deviceApi.updateDevice(row.db_id, { status: 'offline' })
    }
    
    // 刷新设备列表
    props.handleRefresh()
    
    ElMessage.success('无线连接已断开')
  }
  catch (error) {
    console.warn('断开无线连接失败:', error)
    ElMessage.error('断开无线连接失败')
  }
  finally {
    stopLoading.value = false
  }
}
</script>

<style lang="scss" scoped>
:deep() .el-button {
  padding: 4px 8px;
}
</style>