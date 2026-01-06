<template>
  <el-tooltip
    effect="light"
    placement="top"
    :offset="1"
    content="更多操作"
  >
    <el-dropdown :hide-on-click="false" trigger="click">
      <el-button
        type="primary"
        text
        :disabled="!isOnline"
      >
        <template #icon>
          <el-icon><Operation /></el-icon>
        </template>
      </el-button>

      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item @click="handleHome">
            <template #icon>
              <el-icon><HomeFilled /></el-icon>
            </template>
            主页
          </el-dropdown-item>
          <el-dropdown-item @click="handleSleep">
            <template #icon>
              <el-icon><SwitchButton /></el-icon>
            </template>
            息屏
          </el-dropdown-item>
          <el-dropdown-item @click="handleWake">
            <template #icon>
              <el-icon><Sunny /></el-icon>
            </template>
            亮屏
          </el-dropdown-item>
          <el-dropdown-item @click="handleOtg">
            <template #icon>
              <el-icon><Connection /></el-icon>
            </template>
            OTG模式
          </el-dropdown-item>
          <el-dropdown-item @click="handleScreenshot">
            <template #icon>
              <el-icon><Crop /></el-icon>
            </template>
            截图
          </el-dropdown-item>
          <el-dropdown-item @click="handleReboot">
            <template #icon>
              <el-icon><Refresh /></el-icon>
            </template>
            重启设备
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </el-tooltip>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Operation, HomeFilled, SwitchButton, Sunny, Connection, Crop, Refresh } from '@element-plus/icons-vue'
import deviceApi from '@/api/device'

const props = defineProps({
  row: {
    type: Object,
    default: () => ({}),
  },
  isOnline: {
    type: Boolean,
    default: false,
  },
})

const loading = ref(false)

async function handleOtg() {
  try {
    // 调用后端API启动USB功能，使用正确的命令语法和功能选项
    // 注意：svc usb setFunctions 命令的正确用法，otg不是有效选项
    await deviceApi.executeAdbCommand(`-s ${props.row.id} shell svc usb setFunctions mtp`)
    ElMessage.success('USB功能已设置为MTP模式')
  } catch (error) {
    console.warn('设置USB功能失败:', error)
    // 错误信息由全局拦截器处理，这里只需重置状态
  }
}

async function handleScreenshot() {
  try {
    // 使用设备管理API中的截图功能，直接获取截图
    const response = await deviceApi.getDeviceScreenshot(props.row.id)
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `screenshot-${props.row.id}-${Date.now()}.png`)
    document.body.appendChild(link)
    link.click()
    
    // 清理
    link.remove()
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('截图成功')
  } catch (error) {
    console.warn('截图失败:', error)
    // 错误信息由全局拦截器处理，这里只需重置状态
  }
}

async function handleHome() {
  try {
    // 使用adb命令模拟主页键
    await deviceApi.executeAdbCommand(`-s ${props.row.id} shell input keyevent 3`)
    ElMessage.success('主页命令已发送')
  } catch (error) {
    console.warn('执行主页命令失败:', error)
    // 错误信息由全局拦截器处理，这里只需重置状态
  }
}

async function handleSleep() {
  try {
    // 使用adb命令模拟电源键，实现息屏
    await deviceApi.executeAdbCommand(`-s ${props.row.id} shell input keyevent 26`)
    ElMessage.success('息屏命令已发送')
  } catch (error) {
    console.warn('执行息屏命令失败:', error)
    // 错误信息由全局拦截器处理，这里只需重置状态
  }
}

async function handleWake() {
  try {
    // 使用adb命令模拟唤醒键，实现亮屏
    await deviceApi.executeAdbCommand(`-s ${props.row.id} shell input keyevent 224`)
    ElMessage.success('亮屏命令已发送')
  } catch (error) {
    console.warn('执行亮屏命令失败:', error)
    // 错误信息由全局拦截器处理，这里只需重置状态
  }
}

async function handleReboot() {
  try {
    // 使用adb命令重启设备
    await deviceApi.executeAdbCommand(`-s ${props.row.id} reboot`)
    ElMessage.success('设备重启命令已发送')
  } catch (error) {
    console.warn('重启设备失败:', error)
    // 错误信息由全局拦截器处理，这里只需重置状态
  }
}
</script>

<style lang="scss" scoped>
:deep() .el-button {
  padding: 4px 8px;
  margin-right: 4px;
}
</style>
