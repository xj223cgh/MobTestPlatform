<template>
  <div class="device-management">
    <div class="page-header">
      <div class="header-content">
        <h1>设备管理</h1>
        <div class="right-content flex items-center" style="gap: 25px">
          <el-button type="primary" :icon="Operation" @click="openTaskDialog">
            测试任务
          </el-button>
          <div class="refresh-control">
            <span class="refresh-text">{{
              autoRefreshEnabled ? "自动刷新" : "手动刷新"
            }}</span>
            <el-switch
              v-model="autoRefreshEnabled"
              @change="handleAutoRefreshChange"
            />
          </div>
          <el-button
            type="default"
            :icon="loading ? '' : 'Refresh'"
            :loading="loading"
            placement="right"
            circle
            title="刷新设备"
            @click="refreshDevices"
          />
          <WirelessGroup
            ref="wirelessGroupRef"
            v-bind="{ handleRefresh: refreshDevices }"
            @auto-connected="onAutoConnected"
          />
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

          <el-table-column
            type="selection"
            :selectable="selectable"
            align="center"
            width="65"
          />

          <el-table-column
            label="设备序列号"
            sortable
            show-overflow-tooltip
            align="center"
            min-width="160"
            width="auto"
          >
            <template #default="{ row }">
              <div class="device-serial-wrapper">
                <div class="popover-wrapper">
                  <DevicePopover :key="row.status" :device="row" />
                </div>
                <span class="device-id">{{ row.id }}</span>
                <el-link
                  type="primary"
                  :underline="false"
                  title="WiFi"
                  class="wifi-link"
                >
                  <el-icon v-if="row.wifi">
                    <Operation />
                  </el-icon>
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
            width="auto"
          >
            <template #default="{ row }">
              <template v-if="editingDeviceId === row.id">
                <el-input
                  v-model="editingDeviceName"
                  size="small"
                  autofocus
                  clearable
                  @blur="saveDeviceNameEdit(row)"
                  @keyup.enter="saveDeviceNameEdit(row)"
                  @keyup.esc="cancelDeviceNameEdit"
                />
              </template>
              <div
                v-else
                class="cursor-pointer"
                @dblclick="startDeviceNameEdit(row)"
              >
                {{ row.name || "未命名设备" }}
              </div>
            </template>
          </el-table-column>

          <el-table-column
            v-slot="{ row }"
            label="设备状态"
            prop="status"
            align="center"
            sortable
            show-overflow-tooltip
            min-width="100"
            width="auto"
          >
            <el-tag :type="getStatusTagType(row.status)">
              <span class="flex-none">{{
                getStatusText(row.status) || "-"
              }}</span>
            </el-tag>
          </el-table-column>

          <el-table-column
            v-slot="{ row }"
            label="设备电量"
            align="center"
            sortable
            show-overflow-tooltip
            min-width="180"
            width="auto"
          >
            <div
              style="
                display: flex;
                align-items: center;
                justify-content: center;
                width: 100%;
                height: 100%;
                padding: 8px 0;
              "
            >
              <div
                v-if="row.battery && row.battery.batteryPercentage !== null"
                style="width: 100%; text-align: center"
              >
                <div
                  style="
                    display: inline-block;
                    text-align: center;
                    width: 120px;
                  "
                >
                  <el-progress
                    :percentage="row.battery.batteryPercentage"
                    :stroke-width="8"
                    :show-text="true"
                    :color="getBatteryColor(row.battery.batteryPercentage)"
                    style="width: 100% !important; margin: 0 auto !important"
                  />
                </div>
              </div>
              <div v-else style="width: 100%; text-align: center">-</div>
            </div>
          </el-table-column>

          <el-table-column
            v-slot="{ row }"
            label="是否充电"
            align="center"
            sortable
            show-overflow-tooltip
            min-width="100"
            width="auto"
          >
            <el-tag
              :type="row.battery && row.battery.isCharging ? 'success' : 'info'"
            >
              {{
                row.battery && row.battery.isCharging !== null
                  ? row.battery.isCharging
                    ? "是"
                    : "否"
                  : "-"
              }}
            </el-tag>
          </el-table-column>

          <el-table-column
            v-slot="{ row }"
            label="设备负责人"
            align="center"
            sortable
            show-overflow-tooltip
            min-width="180"
            width="auto"
          >
            <el-select
              v-model="row.owner_id"
              placeholder="请选择负责人"
              clearable
              filterable
              style="width: 160px"
              @change="handleOwnerChange(row)"
            >
              <el-option
                v-for="user in userList"
                :key="user.id"
                :label="user.real_name"
                :value="user.id"
              />
            </el-select>
          </el-table-column>

          <el-table-column
            v-slot="{ row }"
            label="设备操作"
            align="center"
            min-width="220"
            width="auto"
          >
            <div class="flex items-center justify-between w-full px-2">
              <div class="flex-1 flex justify-center">
                <ConnectAction
                  v-if="row.status === 'offline' && row.wifi"
                  v-bind="{
                    device: row,
                    handleConnect,
                  }"
                />
              </div>

              <div class="flex-1 flex justify-center">
                <ViewAction :row="row" :is-online="row.status === 'online'" />
              </div>

              <div class="flex-1 flex justify-center">
                <MirrorAction
                  :ref="getMirrorActionRefs"
                  v-bind="{
                    row,
                    toggleRowExpansion,
                    isOnline: row.status === 'online',
                  }"
                />
              </div>

              <div class="flex-1 flex justify-center">
                <MoreDropdown
                  v-bind="{
                    row,
                    toggleRowExpansion,
                    isOnline: row.status === 'online',
                  }"
                />
              </div>

              <div class="flex-1 flex justify-center">
                <WirelessAction
                  v-bind="{
                    row,
                    handleConnect,
                    handleRefresh: refreshDevices,
                    isOnline: row.status === 'online',
                  }"
                />
              </div>

              <div class="flex-1 flex justify-center">
                <RemoveAction
                  v-if="row.status === 'offline'"
                  v-bind="{
                    device: row,
                    handleRefresh: refreshDevices,
                  }"
                />
              </div>
            </div>
          </el-table-column>
          <el-table-column type="expand" width="75">
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

    <TaskDialog
      ref="taskDialogRef"
      :devices="deviceList"
      @refresh-devices="refreshDevices"
    />
  </div>
</template>

<script setup>
import {
  ref,
  computed,
  onMounted,
  onUnmounted,
  getCurrentInstance,
  nextTick,
  watch,
} from "vue";
import { useRoute } from "vue-router";
import { ElMessage } from "element-plus";
import {
  Refresh,
  Monitor,
  Download,
  WarningFilled,
  Operation,
} from "@element-plus/icons-vue";
import deviceApi from "@/api/device";
import userApi from "@/api/user";
import {
  deviceStatus,
  getStatusTagType,
  getStatusText,
} from "@/utils/deviceStatus";

// 导入设备相关组件
import DevicePopover from "./components/DevicePopover.vue";
import ConnectAction from "./components/ConnectAction.vue";
import ViewAction from "./components/ViewAction.vue";
import MirrorAction from "./components/MirrorAction.vue";
import MoreDropdown from "./components/MoreDropdown.vue";
import WirelessAction from "./components/WirelessAction.vue";
import RemoveAction from "./components/RemoveAction.vue";
import WirelessGroup from "./components/WirelessGroup.vue";
import TaskDialog from "./components/TaskDialog.vue";
// 导入设备控制栏组件
import ControlBar from "@/components/ControlBar/index.vue";

const loading = ref(false);
const deviceList = ref([]);
const mirrorActionRefs = ref([]);
const selectionRows = ref([]);
const wirelessGroupRef = ref(null);
const userList = ref([]);
const editingDeviceId = ref(null);
const editingDeviceName = ref("");
const autoRefreshTimer = ref(null);
const autoRefreshInterval = ref(5000);
const autoRefreshEnabled = ref(false);
const taskDialogRef = ref(null);

const route = useRoute();
const { proxy } = getCurrentInstance();

const isMultipleRow = computed(() => selectionRows.value.length > 0);

const hasOnlineDevices = computed(() => {
  return deviceList.value.some((device) => device.status === "online");
});

// 获取电池颜色
const getBatteryColor = (percentage) => {
  if (percentage < 20) {
    return "#f56c6c";
  } else if (percentage < 50) {
    return "#e6a23c";
  } else {
    return "#67c23a";
  }
};

// 转换ADB状态到数据库状态
const convertAdbStatusToDbStatus = (adbStatus) => {
  const statusMap = {
    device: "online",
    unauthorized: "offline",
    offline: "offline",
  };
  return statusMap[adbStatus] || "offline";
};

// 获取设备电池信息
const getDeviceBatteryInfo = async (deviceId) => {
  try {
    const response = await deviceApi.executeAdbCommand(
      `-s ${deviceId} shell dumpsys battery`,
    );
    const batteryInfo = parseBatteryInfo(response.data.stdout);
    return batteryInfo;
  } catch (error) {
    console.warn(`获取设备 ${deviceId} 电池信息失败:`, error);
    return null;
  }
};

// 解析电池信息
const parseBatteryInfo = (output) => {
  const battery = {
    batteryPercentage: null,
    isCharging: null,
  };

  const lines = output.split("\n");

  for (const line of lines) {
    const trimmedLine = line.trim();

    // 解析电池电量
    if (trimmedLine.startsWith("level:")) {
      const match = trimmedLine.match(/level:\s*(\d+)/);
      if (match) {
        battery.batteryPercentage = parseInt(match[1]);
      }
    }
    // 解析充电状态
    else if (trimmedLine.startsWith("status:")) {
      const match = trimmedLine.match(/status:\s*(\d+)/);
      if (match) {
        const status = parseInt(match[1]);
        battery.isCharging = status === 2 || status === 5; // 2: charging, 5: full
      }
    }
  }

  return battery;
};

// 获取设备列表
const getDevices = async () => {
  loading.value = true;
  try {
    // 获取ADB设备列表
    const adbResponse = await deviceApi.getAdbDevices();
    const adbDevices = adbResponse.data.devices || [];

    // 获取数据库中的设备列表
    const dbResponse = await deviceApi.getDeviceList({ page: 1, size: 1000 });
    const dbDevices = dbResponse.data.devices || [];

    // 创建设备ID到ADB设备的映射
    const adbDeviceMap = new Map();
    adbDevices.forEach((adbDevice) => {
      adbDeviceMap.set(adbDevice.id, adbDevice);
    });

    // 检查哪些设备从ADB中断开了，更新数据库状态
    for (const dbDevice of dbDevices) {
      const adbDevice = adbDeviceMap.get(dbDevice.device_id);
      // 如果设备之前是online状态，但现在ADB中没有，说明断开了
      if (dbDevice.status === "online" && !adbDevice) {
        try {
          await deviceApi.updateDevice(dbDevice.id, { status: "offline" });
        } catch (error) {
          console.warn(`更新设备 ${dbDevice.device_id} 状态失败:`, error);
        }
      }
      // 如果设备之前不是online状态，但现在ADB中有，说明连接了
      else if (dbDevice.status !== "online" && adbDevice) {
        try {
          await deviceApi.updateDevice(dbDevice.id, { status: "online" });
        } catch (error) {
          console.warn(`更新设备 ${dbDevice.device_id} 状态失败:`, error);
        }
      }
    }

    // 检查ADB中有但数据库中没有的设备，自动创建设备记录
    const dbDeviceIdSet = new Set(dbDevices.map((db) => db.device_id));
    for (const adbDevice of adbDevices) {
      if (!dbDeviceIdSet.has(adbDevice.id) && adbDevice.status === "device") {
        try {
          // 自动创建设备记录
          const response = await deviceApi.createDevice({
            device_name: adbDevice.name || adbDevice.id,
            device_model: adbDevice.name || "Unknown",
            os_type: "android",
            os_version: "Unknown",
            device_id: adbDevice.id,
            status: "online",
          });
          console.log(`自动创建设备记录: ${adbDevice.id}`);
        } catch (error) {
          console.warn(`自动创建设备 ${adbDevice.id} 失败:`, error);
        }
      }
    }

    // 重新获取数据库设备列表（包含新创建的设备）
    const dbResponseAfterCreate = await deviceApi.getDeviceList({
      page: 1,
      size: 1000,
    });
    const dbDevicesAfterCreate = dbResponseAfterCreate.data.devices || [];

    // 合并数据库设备和ADB设备信息
    const mergedDevices = await Promise.all(
      dbDevicesAfterCreate.map(async (dbDevice) => {
        const adbDevice = adbDeviceMap.get(dbDevice.device_id);

        // 获取电池信息（只有ADB连接的设备才能获取）
        let batteryInfo = null;
        if (adbDevice && adbDevice.status === "device") {
          batteryInfo = await getDeviceBatteryInfo(dbDevice.device_id);
        }

        // 合并设备信息
        return {
          // 基础信息优先使用数据库的
          id: dbDevice.device_id,
          device_id: dbDevice.device_id,
          name: dbDevice.device_name || adbDevice?.name || dbDevice.device_id,
          device_model: dbDevice.device_model,
          os_type: dbDevice.os_type,
          os_version: dbDevice.os_version,
          // 状态：如果ADB有连接则使用online，否则使用数据库状态
          status: adbDevice ? "online" : dbDevice.status,
          // WiFi标识
          wifi: adbDevice ? adbDevice.wifi : false,
          // 电池信息
          battery: batteryInfo,
          // 负责人信息
          owner_id: dbDevice.owner_id,
          owner_name: dbDevice.owner_name,
          // 保存数据库设备ID,用于更新
          db_id: dbDevice.id,
        };
      }),
    );

    deviceList.value = mergedDevices;
  } catch (error) {
    ElMessage.error(
      "获取设备列表失败：" + (error.response?.data?.message || error.message),
    );
    deviceList.value = [];
  } finally {
    loading.value = false;
  }
};

// 获取用户列表
const getUserList = async () => {
  try {
    const response = await userApi.getUserList({ page: 1, size: 1000 });
    userList.value = response.data.users || [];
  } catch (error) {
    console.error("获取用户列表失败：", error);
  }
};

// 开始编辑设备名称
const startDeviceNameEdit = (device) => {
  editingDeviceId.value = device.id;
  editingDeviceName.value = device.name || "";
};

// 保存设备名称编辑
const saveDeviceNameEdit = async (device) => {
  try {
    if (!editingDeviceName.value.trim()) {
      ElMessage.warning("设备名称不能为空");
      editingDeviceName.value = device.name || "";
      return;
    }

    if (device.db_id) {
      // 更新数据库中的设备名称
      await deviceApi.updateDevice(device.db_id, {
        device_name: editingDeviceName.value,
      });
      ElMessage.success("设备名称更新成功");
    } else {
      // 创建新的设备记录
      const response = await deviceApi.createDevice({
        device_name: editingDeviceName.value,
        device_model: device.name || "Unknown",
        os_type: "android",
        os_version: "Unknown",
        device_id: device.id,
        status: convertAdbStatusToDbStatus(device.status),
      });

      // 更新设备的db_id
      const index = deviceList.value.findIndex((item) => item.id === device.id);
      if (index !== -1) {
        deviceList.value[index].db_id = response.data.device.id;
      }

      ElMessage.success("设备名称保存成功");
    }

    // 更新本地设备名称
    const index = deviceList.value.findIndex((item) => item.id === device.id);
    if (index !== -1) {
      deviceList.value[index].name = editingDeviceName.value;
    }
  } catch (error) {
    ElMessage.error(
      "保存设备名称失败：" + (error.response?.data?.message || error.message),
    );
  } finally {
    editingDeviceId.value = null;
    editingDeviceName.value = "";
  }
};

// 取消设备名称编辑
const cancelDeviceNameEdit = () => {
  editingDeviceId.value = null;
  editingDeviceName.value = "";
};

// 处理负责人变更
const handleOwnerChange = async (device) => {
  try {
    if (device.db_id) {
      // 更新现有设备的负责人
      await deviceApi.updateDevice(device.db_id, { owner_id: device.owner_id });
      ElMessage.success("设备负责人更新成功");
    } else {
      // 创建新设备记录
      const response = await deviceApi.createDevice({
        device_name: device.name || device.id,
        device_model: device.name || "Unknown",
        os_type: "android",
        os_version: "Unknown",
        device_id: device.id,
        status: convertAdbStatusToDbStatus(device.status),
        owner_id: device.owner_id,
      });

      // 更新设备的db_id
      device.db_id = response.data.device.id;
      ElMessage.success("设备信息保存成功");
    }
  } catch (error) {
    ElMessage.error(
      "保存设备负责人失败：" + (error.response?.data?.message || error.message),
    );
  }
};

// 刷新设备列表
const refreshDevices = () => {
  getDevices();
};

// 选择设备
const selectable = (row) => {
  return row.status === "online";
};

// 选择设备变化
const onSelectionChange = (rows) => {
  selectionRows.value = rows;
};

// 获取MirrorAction引用
const getMirrorActionRefs = (ref) => {
  if (!ref?.row?.id) {
    return false;
  }

  const exists = mirrorActionRefs.value.some(
    (item) => item.row.id === ref.row.id,
  );
  if (exists) {
    return false;
  }

  mirrorActionRefs.value.push(ref);
};

// 切换行展开/收起
const toggleRowExpansion = (...args) => {
  proxy.$refs.tableRef.toggleRowExpansion(...args);
};

// 连接设备
const handleConnect = (...args) => {
  proxy.$refs.wirelessGroupRef?.connect?.(...args);
};

// 打开任务对话框
const openTaskDialog = () => {
  taskDialogRef.value?.open();
};

// 自动连接成功
const onAutoConnected = () => {};

// 启动自动刷新
const startAutoRefresh = () => {
  if (!autoRefreshEnabled.value) {
    return;
  }
  if (autoRefreshTimer.value) {
    clearInterval(autoRefreshTimer.value);
  }
  autoRefreshTimer.value = setInterval(() => {
    getDevices();
  }, autoRefreshInterval.value);
};

// 停止自动刷新
const stopAutoRefresh = () => {
  if (autoRefreshTimer.value) {
    clearInterval(autoRefreshTimer.value);
    autoRefreshTimer.value = null;
  }
};

// 处理自动刷新开关变化
const handleAutoRefreshChange = (enabled) => {
  // 保存到 localStorage
  localStorage.setItem("deviceAutoRefreshEnabled", enabled.toString());

  if (enabled) {
    startAutoRefresh();
  } else {
    stopAutoRefresh();
  }
};

// 检查是否在设备相关页面
const isDevicePage = () => {
  return route.name === "Devices" || route.name === "DeviceDetail";
};

// 监听路由变化
watch(
  () => route.name,
  (newName, oldName) => {
    if (isDevicePage()) {
      if (autoRefreshEnabled.value) {
        startAutoRefresh();
      }
    } else {
      stopAutoRefresh();
    }
  },
);

// 组件挂载时获取设备列表
onMounted(() => {
  // 从 localStorage 读取自动刷新状态
  const savedAutoRefresh = localStorage.getItem("deviceAutoRefreshEnabled");
  if (savedAutoRefresh !== null) {
    autoRefreshEnabled.value = savedAutoRefresh === "true";
    // 如果自动刷新是开启状态，则启动自动刷新
    if (autoRefreshEnabled.value) {
      startAutoRefresh();
    }
  }

  getDevices();
  getUserList();
});

// 组件卸载时停止自动刷新
onUnmounted(() => {
  stopAutoRefresh();
});
</script>

<style lang="scss" scoped>
.device-management {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.refresh-control {
  display: flex;
  align-items: center;
  gap: 8px;

  .refresh-text {
    font-size: 14px;
    color: #606266;
    white-space: nowrap;
  }
}

.cursor-pointer {
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s;

  &:hover {
    background-color: #f5f7fa;
  }
}

.device-serial-wrapper {
  display: inline-block;
  width: 100%;
  padding: 0 8px;
  text-align: center;

  .popover-wrapper {
    display: inline-block;
    vertical-align: middle;
  }

  .device-id {
    display: inline-block;
    vertical-align: middle;
    margin: 0 12px;
    max-width: calc(100% - 80px);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .wifi-link {
    display: inline-block;
    vertical-align: middle;
  }
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
  .el-table {
    width: 100% !important;

    .el-table__body-wrapper {
      overflow-x: auto;
    }

    .el-table__row {
      td {
        padding: 8px 0;
      }
    }
  }

  .el-table .el-table__row .cell {
    padding: 8px 0;
  }
}
</style>
