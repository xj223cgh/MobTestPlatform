<template>
  <div class="device-management">
    <div class="page-header">
      <div class="header-content">
        <h1>设备管理</h1>
        <div class="right-content flex items-center" style="gap: 15px;">
          <el-button
            type="default"
            :icon="loading ? '' : 'Refresh'"
            :loading="loading"
            placement="right"
            circle
            title="刷新设备"
            @click="refreshDevices"
          >
          </el-button>
          <WirelessGroup ref="wirelessGroupRef" v-bind="{ handleRefresh: refreshDevices }" @auto-connected="onAutoConnected" />
        </div>
      </div>
    </div>

    <div class="device-content">
      <el-card shadow="hover" class="device-card">
        <el-table
          ref="tableRef"
          v-loading="loading && !deviceList.length"
          element-loading-text="加载中"
          :data="deviceList"
          style="width: 100%"
          border
          height="100%"
          row-key="id"
          @selection-change="onSelectionChange"
        >
          <template #empty>
            <el-empty description="暂无设备连接" />
          </template>

          <el-table-column type="selection" :selectable="selectable" align="center"></el-table-column>

          <el-table-column
            label="设备序列号"
            sortable
            show-overflow-tooltip
            align="center"
            min-width="200"
          >
            <template #default="{ row }">
              <div class="flex items-center justify-center space-x-2 relative w-full">
                <DevicePopover :key="row.status" :device="row" class="" />

                <div class="flex-1 text-center truncate">
                  {{ row.id }}
                </div>

                <el-link type="primary" :underline="false" title="WiFi" class="flex-none">
                  <el-icon v-if="row.wifi"><Operation /></el-icon>
                </el-link>
              </div>
            </template>
          </el-table-column>

          <el-table-column
            label="设备名称"
            sortable
            show-overflow-tooltip
            align="center"
            min-width="180"
          >
            <template #default="{ row }">
              <Remark :device="row" class="" @update:device="updateDevice" />
            </template>
          </el-table-column>

          <el-table-column
            v-slot="{ row }"
            label="设备状态"
            prop="status"
            align="center"
            sortable
            show-overflow-tooltip
            min-width="180"
          >
            <el-tag :type="getStatusTagType(row.status)">
              <div class="flex items-center">
                <el-tooltip
                  v-if="['unauthorized'].includes(row.status)"
                  content="设备未授权"
                  placement="top"
                >
                  <el-link type="danger" :underline="false" icon="WarningFilled" class="mr-1 flex-none"></el-link>
                </el-tooltip>

                <span class="flex-none">{{ getStatusText(row.status) || '-' }}</span>
              </div>
            </el-tag>
          </el-table-column>

          <el-table-column
            v-slot="{ row }"
            label="设备电量"
            align="center"
            sortable
            show-overflow-tooltip
            min-width="180"
          >
            <div style="display: flex; align-items: center; justify-content: center; width: 100%; height: 100%; padding: 8px 0;">
              <div v-if="row.battery && row.battery.batteryPercentage !== null" style="width: 100%; text-align: center;">
                <div style="display: inline-block; text-align: center; width: 120px;">
                  <el-progress
                    :percentage="row.battery.batteryPercentage"
                    :stroke-width="8"
                    :show-text="true"
                    :color="getBatteryColor(row.battery.batteryPercentage)"
                    style="width: 100% !important; margin: 0 auto !important;"
                  ></el-progress>
                </div>
              </div>
              <div v-else style="width: 100%; text-align: center;">-</div>
            </div>
          </el-table-column>

          <el-table-column
            v-slot="{ row }"
            label="是否充电"
            align="center"
            sortable
            show-overflow-tooltip
            min-width="150"
          >
            <el-tag :type="row.battery && row.battery.isCharging ? 'success' : 'info'">
              {{ row.battery && row.battery.isCharging !== null ? (row.battery.isCharging ? '是' : '否') : '-' }}
            </el-tag>
          </el-table-column>

          <el-table-column
            v-slot="{ row }"
            label="设备操作"
            align="center"
            min-width="200"
          >
            <div class="flex items-center justify-between w-full px-2">
              <div class="flex-1 flex justify-center">
                <ConnectAction
                  v-if="['offline'].includes(row.status) && row.wifi"
                  v-bind="{
                    device: row,
                    handleConnect,
                  }"
                />
              </div>

              <div class="flex-1 flex justify-center">
                <MirrorAction
                  v-if="['device', 'unauthorized'].includes(row.status)"
                  :ref="getMirrorActionRefs"
                  v-bind="{ row, toggleRowExpansion }"
                />
              </div>

              <div class="flex-1 flex justify-center">
                <MoreDropdown v-if="['device'].includes(row.status)" v-bind="{ row, toggleRowExpansion }" />
              </div>

              <div class="flex-1 flex justify-center">
                <WirelessAction v-if="['device', 'unauthorized'].includes(row.status)" v-bind="{ row, handleConnect, handleRefresh: refreshDevices }" />
              </div>

              <div class="flex-1 flex justify-center">
                <RemoveAction
                  v-if="['offline'].includes(row.status)"
                  v-bind="{
                    device: row,
                    handleRefresh: refreshDevices,
                  }"
                />
              </div>
            </div>
          </el-table-column>
          <el-table-column type="expand">
            <template #header>
              <el-icon class="" title="更多操作">
                <Operation />
              </el-icon>
            </template>

            <template #default="{ row }">
              <ControlBar :device="row" class="-my-4" />
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, getCurrentInstance, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Monitor, Download, WarningFilled, Operation } from '@element-plus/icons-vue'
import deviceApi from '@/api/device'
import { deviceStatus, getStatusTagType, getStatusText } from '@/utils/deviceStatus'

// 导入设备相关组件
import DevicePopover from './components/DevicePopover.vue'
import Remark from './components/Remark.vue'
import ConnectAction from './components/ConnectAction.vue'
import MirrorAction from './components/MirrorAction.vue'
import MoreDropdown from './components/MoreDropdown.vue'
import WirelessAction from './components/WirelessAction.vue'
import RemoveAction from './components/RemoveAction.vue'
import WirelessGroup from './components/WirelessGroup.vue'
// 导入设备控制栏组件
import ControlBar from '@/components/ControlBar/index.vue'

const loading = ref(false)
const deviceList = ref([])
const mirrorActionRefs = ref([])
const selectionRows = ref([])
const wirelessGroupRef = ref(null)

const { proxy } = getCurrentInstance()

const isMultipleRow = computed(() => selectionRows.value.length > 0)

// 获取电池颜色
const getBatteryColor = (percentage) => {
  if (percentage < 20) {
    return '#f56c6c'
  } else if (percentage < 50) {
    return '#e6a23c'
  } else {
    return '#67c23a'
  }
}

// 获取设备电池信息
const getDeviceBatteryInfo = async (deviceId) => {
  try {
    const response = await deviceApi.executeAdbCommand(`-s ${deviceId} shell dumpsys battery`)
    const batteryInfo = parseBatteryInfo(response.data.stdout)
    return batteryInfo
  } catch (error) {
    console.warn(`获取设备 ${deviceId} 电池信息失败:`, error)
    return null
  }
}

// 解析电池信息
const parseBatteryInfo = (output) => {
  const battery = {
    batteryPercentage: null,
    isCharging: null
  }
  
  const lines = output.split('\n')
  
  for (const line of lines) {
    const trimmedLine = line.trim()
    
    // 解析电池电量
    if (trimmedLine.startsWith('level:')) {
      const match = trimmedLine.match(/level:\s*(\d+)/)
      if (match) {
        battery.batteryPercentage = parseInt(match[1])
      }
    }
    // 解析充电状态
    else if (trimmedLine.startsWith('status:')) {
      const match = trimmedLine.match(/status:\s*(\d+)/)
      if (match) {
        const status = parseInt(match[1])
        battery.isCharging = status === 2 || status === 5 // 2: charging, 5: full
      }
    }
  }
  
  return battery
}

// 获取设备列表
const getDevices = async () => {
  loading.value = true
  try {
    const response = await deviceApi.getAdbDevices()
    const devices = response.data.devices
    
    // 为每个设备获取电池信息
    const devicesWithBattery = await Promise.all(
      devices.map(async (device) => {
        if (device.status === 'device') {
          const batteryInfo = await getDeviceBatteryInfo(device.id)
          return { ...device, battery: batteryInfo }
        }
        return { ...device, battery: null }
      })
    )
    
    deviceList.value = devicesWithBattery
  } catch (error) {
    ElMessage.error('获取设备列表失败：' + (error.response?.data?.message || error.message))
    deviceList.value = []
  } finally {
    loading.value = false
  }
}

// 刷新设备列表
const refreshDevices = () => {
  getDevices()
}

// 更新设备信息
const updateDevice = (updatedDevice) => {
  const index = deviceList.value.findIndex(item => item.id === updatedDevice.id)
  if (index !== -1) {
    deviceList.value[index] = updatedDevice
  }
}

// 选择设备
const selectable = (row) => {
  return ['device', 'emulator'].includes(row.status)
}

// 选择设备变化
const onSelectionChange = (rows) => {
  selectionRows.value = rows
}

// 获取MirrorAction引用
const getMirrorActionRefs = (ref) => {
  if (!ref?.row?.id) {
    return false
  }
  
  const exists = mirrorActionRefs.value.some(item => item.row.id === ref.row.id)
  if (exists) {
    return false
  }
  
  mirrorActionRefs.value.push(ref)
}

// 切换行展开/收起
const toggleRowExpansion = (...args) => {
  proxy.$refs.tableRef.toggleRowExpansion(...args)
}

// 连接设备
const handleConnect = (...args) => {
  proxy.$refs.wirelessGroupRef?.connect?.(...args)
}

// 自动连接成功
const onAutoConnected = () => {}

// 组件挂载时获取设备列表
onMounted(() => {
  getDevices()
})
</script>

<style lang="scss" scoped>
.device-management {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.page-header {
    margin-bottom: 20px;
    padding-bottom: 20px;
    border-bottom: 1px solid #e4e7ed;

    .header-content {
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 100%;

      h1 {
        margin: 0;
        font-size: 24px;
        font-weight: 600;
        color: #303133;
      }
      
      .right-content {
        display: flex;
        align-items: center;
        space-x: 2;
      }
    }
  }

.device-content {
  flex: 1;
  overflow: hidden;
  margin-bottom: 20px;
  
  .device-card {
    height: 100%;
    display: flex;
    flex-direction: column;
  }
}



:deep() {
  .el-table .el-table__row .cell {
    padding: 12px 0;
  }
}
</style>
