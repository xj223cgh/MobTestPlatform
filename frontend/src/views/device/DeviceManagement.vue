<template>
  <div class="device-management">
    <div class="page-header">
      <div class="header-content">
        <h1>设备管理</h1>
        <p class="description">
          管理已连接的测试设备
        </p>
      </div>
      <div class="header-actions">
        <el-button
          v-if="selectionRows.length > 0"
          type="danger"
          :icon="Delete"
          @click="handleBatchDelete"
        >
          删除选中 ({{ selectionRows.length }})
        </el-button>
        <el-button
          type="primary"
          :icon="Operation"
          @click="openTaskDialog"
        >
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

    <div class="device-content">
      <el-card
        shadow="hover"
        class="device-card"
      >
        <div class="table-scroll-container">
          <el-table
            ref="tableRef"
            v-loading="loading && !deviceList.length"
            element-loading-text="加载中"
            :data="deviceList"
            style="width: 100%"
            border
            row-key="id"
            height="100%"
            :row-class-name="getDeviceRowClassName"
            @selection-change="onSelectionChange"
          >
          <template #empty>
            <el-empty description="暂无设备连接" />
          </template>

          <el-table-column
            type="selection"
            :selectable="selectable"
            align="center"
            width="45"
          />

          <el-table-column
            label="设备序列号"
            sortable
            align="center"
            min-width="170"
          >
            <template #default="{ row }">
              <div class="device-serial-wrapper">
                <div class="popover-wrapper">
                  <DevicePopover
                    :key="row.status"
                    :device="row"
                  />
                </div>
                <el-tooltip
                  :content="row.id"
                  placement="top"
                  effect="dark"
                >
                  <span class="device-id">{{ row.id }}</span>
                </el-tooltip>
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
            min-width="130"
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
            min-width="110"
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
            min-width="130"
          >
            <div
              v-if="row.battery && row.battery.batteryPercentage !== null"
              style="display: flex; flex-direction: column; align-items: center; gap: 2px; padding: 4px 8px; width: 100%; box-sizing: border-box;"
            >
              <el-progress
                :percentage="row.battery.batteryPercentage"
                :stroke-width="8"
                :show-text="false"
                :color="getBatteryColor(row.battery.batteryPercentage)"
                style="width: 100%;"
              />
              <span
                :style="{ color: getBatteryColor(row.battery.batteryPercentage), fontSize: '12px', lineHeight: 1 }"
              >{{ row.battery.batteryPercentage }}%</span>
            </div>
            <span v-else>-</span>
          </el-table-column>

          <el-table-column
            v-slot="{ row }"
            label="是否充电"
            align="center"
            sortable
            show-overflow-tooltip
            min-width="105"
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
            min-width="160"
          >
            <el-select
              v-model="row.owner_id"
              placeholder="请选择负责人"
              clearable
              filterable
              style="width: 140px"
              @change="handleOwnerChange(row)"
            >
              <el-option
                v-for="user in userList"
                :key="user.id"
                :label="user.real_name || user.username"
                :value="user.id"
              />
            </el-select>
          </el-table-column>

          <el-table-column
            v-slot="{ row }"
            label="设备操作"
            align="center"
            min-width="220"
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
                <ViewAction
                  :row="row"
                  @view="openDeviceDetail"
                />
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
          <el-table-column
            type="expand"
            width="75"
          >
            <template #header>
              <el-icon
                class=""
                title="更多操作"
              >
                <Operation />
              </el-icon>
            </template>

            <template #default="{ row }">
              <ControlBar
                :device="row"
                class="-my-4"
              />
            </template>
          </el-table-column>
        </el-table>
        </div>
      </el-card>
    </div>

    <TaskDialog
      ref="taskDialogRef"
      :devices="deviceList"
      @refresh-devices="refreshDevices"
    />

    <DeviceDetailDialog
      v-model="deviceDetailDialogVisible"
      :device-id="deviceDetailRow?.db_id ?? null"
      :row="deviceDetailRow || {}"
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
import { useRoute, useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  Refresh,
  Monitor,
  Download,
  WarningFilled,
  Operation,
  Delete,
} from "@element-plus/icons-vue";
import deviceApi from "@/api/device";
import userApi from "@/api/user";
import {
  deviceStatus,
  getStatusTagType,
  getStatusText,
} from "@/utils/deviceStatus";
import { isPermissionError } from "@/utils/request";

import DevicePopover from "./components/DevicePopover.vue";
import ConnectAction from "./components/ConnectAction.vue";
import ViewAction from "./components/ViewAction.vue";
import MirrorAction from "./components/MirrorAction.vue";
import MoreDropdown from "./components/MoreDropdown.vue";
import WirelessAction from "./components/WirelessAction.vue";
import RemoveAction from "./components/RemoveAction.vue";
import WirelessGroup from "./components/WirelessGroup.vue";
import TaskDialog from "./components/TaskDialog.vue";
import DeviceDetailDialog from "./components/DeviceDetailDialog.vue";
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
const tableRef = ref(null);
const deviceDetailDialogVisible = ref(false);
const deviceDetailRow = ref(null);

const route = useRoute();
const router = useRouter();

const openDeviceDetail = (row) => {
  deviceDetailRow.value = row;
  deviceDetailDialogVisible.value = true;
};
const { proxy } = getCurrentInstance();

const isMultipleRow = computed(() => selectionRows.value.length > 0);

const hasOnlineDevices = computed(() => {
  return deviceList.value.some((device) => device.status === "online");
});

// 通知/活动跳转时高亮闪烁对应设备行（query: highlight_device_id）
const flashDeviceId = ref(null);
let flashClearTimer = null;
const getDeviceRowClassName = ({ row }) => {
  if (flashDeviceId.value && row.id === flashDeviceId.value) return "notification-flash-row";
  return "";
};

const getBatteryColor = (percentage) => {
  if (percentage < 20) {
    return "#f56c6c";
  } else if (percentage < 50) {
    return "#e6a23c";
  } else {
    return "#67c23a";
  }
};

const convertAdbStatusToDbStatus = (adbStatus) => {
  const statusMap = {
    device: "online",
    unauthorized: "offline",
    offline: "offline",
  };
  return statusMap[adbStatus] || "offline";
};

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

const parseBatteryInfo = (output) => {
  const battery = {
    batteryPercentage: null,
    isCharging: null,
  };

  const lines = output.split("\n");

  for (const line of lines) {
    const trimmedLine = line.trim();

    if (trimmedLine.startsWith("level:")) {
      const match = trimmedLine.match(/level:\s*(\d+)/);
      if (match) {
        battery.batteryPercentage = parseInt(match[1]);
      }
    } else if (trimmedLine.startsWith("status:")) {
      const match = trimmedLine.match(/status:\s*(\d+)/);
      if (match) {
        const status = parseInt(match[1]);
        battery.isCharging = status === 2 || status === 5; // 2: charging, 5: full
      }
    }
  }

  return battery;
};

const getDevices = async () => {
  loading.value = true;
  try {
    const adbResponse = await deviceApi.getAdbDevices();
    const adbDevices = adbResponse.data.devices || [];

    const dbResponse = await deviceApi.getDeviceList({ page: 1, size: 1000 });
    const dbDevices = dbResponse.data.devices || [];

    const adbDeviceMap = new Map();
    adbDevices.forEach((adbDevice) => {
      adbDeviceMap.set(adbDevice.id, adbDevice);
    });

    // 检查哪些设备从ADB中断开了，更新数据库状态
    for (const dbDevice of dbDevices) {
      const adbDevice = adbDeviceMap.get(dbDevice.device_id);
      if (dbDevice.status === "online" && !adbDevice) {
        try {
          await deviceApi.updateDevice(dbDevice.id, { status: "offline" });
        } catch (error) {
          console.warn(`更新设备 ${dbDevice.device_id} 状态失败:`, error);
        }
      } else if (dbDevice.status !== "online" && adbDevice) {
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

    const dbResponseAfterCreate = await deviceApi.getDeviceList({
      page: 1,
      size: 1000,
    });
    const dbDevicesAfterCreate = dbResponseAfterCreate.data.devices || [];

    const mergedDevices = await Promise.all(
      dbDevicesAfterCreate.map(async (dbDevice) => {
        const adbDevice = adbDeviceMap.get(dbDevice.device_id);

        let batteryInfo = null;
        if (adbDevice && adbDevice.status === "device") {
          batteryInfo = await getDeviceBatteryInfo(dbDevice.device_id);
        }

        return {
          id: dbDevice.device_id,
          device_id: dbDevice.device_id,
          name: dbDevice.device_name || adbDevice?.name || dbDevice.device_id,
          device_model: dbDevice.device_model,
          os_type: dbDevice.os_type,
          os_version: dbDevice.os_version,
          // 状态：如果ADB有连接则使用online，否则使用数据库状态
          status: adbDevice ? "online" : dbDevice.status,
          wifi: adbDevice ? adbDevice.wifi : false,
          battery: batteryInfo,
          owner_id: dbDevice.owner_id,
          owner_name: dbDevice.owner_name,
          db_id: dbDevice.id,
        };
      }),
    );

    // 排序：在线优先，同状态按设备名称/设备ID 排序，符合使用习惯
    const statusOrder = { online: 0, busy: 1, offline: 2, maintenance: 3 };
    const getStatusSortKey = (d) => statusOrder[d.status] ?? 4;
    const getNameKey = (d) => (d.name || d.device_id || d.id || "").toLowerCase();
    deviceList.value = mergedDevices.slice().sort((a, b) => {
      const statusDiff = getStatusSortKey(a) - getStatusSortKey(b);
      if (statusDiff !== 0) return statusDiff;
      return getNameKey(a).localeCompare(getNameKey(b), "zh-CN");
    });
  } catch (error) {
    if (isPermissionError(error)) return;
    ElMessage.error(
      "获取设备列表失败：" + (error.response?.data?.message || error.message),
    );
    deviceList.value = [];
  } finally {
    loading.value = false;
  }
};

// 获取用户列表（仅需登录的 options 接口，用于负责人下拉）
const getUserList = async () => {
  try {
    const response = await userApi.getUserOptions({ size: 1000 });
    userList.value = response.data?.items || [];
  } catch (error) {
    console.error("获取用户列表失败：", error);
  }
};

const startDeviceNameEdit = (device) => {
  editingDeviceId.value = device.id;
  editingDeviceName.value = device.name || "";
};

const saveDeviceNameEdit = async (device) => {
  try {
    if (!editingDeviceName.value.trim()) {
      ElMessage.warning("设备名称不能为空");
      editingDeviceName.value = device.name || "";
      return;
    }

    if (device.db_id) {
      await deviceApi.updateDevice(device.db_id, {
        device_name: editingDeviceName.value,
      });
      ElMessage.success("设备名称更新成功");
    } else {
      const response = await deviceApi.createDevice({
        device_name: editingDeviceName.value,
        device_model: device.name || "Unknown",
        os_type: "android",
        os_version: "Unknown",
        device_id: device.id,
        status: convertAdbStatusToDbStatus(device.status),
      });

      const index = deviceList.value.findIndex((item) => item.id === device.id);
      if (index !== -1) {
        deviceList.value[index].db_id = response.data.device.id;
      }

      ElMessage.success("设备名称保存成功");
    }

    const index = deviceList.value.findIndex((item) => item.id === device.id);
    if (index !== -1) {
      deviceList.value[index].name = editingDeviceName.value;
    }
  } catch (error) {
    if (isPermissionError(error)) return;
    ElMessage.error(
      "保存设备名称失败：" + (error.response?.data?.message || error.message),
    );
  } finally {
    editingDeviceId.value = null;
    editingDeviceName.value = "";
  }
};

const cancelDeviceNameEdit = () => {
  editingDeviceId.value = null;
  editingDeviceName.value = "";
};

const handleOwnerChange = async (device) => {
  try {
    if (device.db_id) {
      await deviceApi.updateDevice(device.db_id, { owner_id: device.owner_id });
      ElMessage.success("设备负责人更新成功");
    } else {
      const response = await deviceApi.createDevice({
        device_name: device.name || device.id,
        device_model: device.name || "Unknown",
        os_type: "android",
        os_version: "Unknown",
        device_id: device.id,
        status: convertAdbStatusToDbStatus(device.status),
        owner_id: device.owner_id,
      });

      device.db_id = response.data.device.id;
      ElMessage.success("设备信息保存成功");
    }
  } catch (error) {
    if (isPermissionError(error)) return;
    ElMessage.error(
      "保存设备负责人失败：" + (error.response?.data?.message || error.message),
    );
  }
};

const refreshDevices = () => {
  getDevices();
};

// 选择设备（允许在线和离线设备勾选，以支持批量删除）
const selectable = (row) => {
  return row.status === "online" || row.status === "offline";
};

const onSelectionChange = (rows) => {
  selectionRows.value = rows;
};

const handleBatchDelete = async () => {
  if (selectionRows.value.length === 0) {
    ElMessage.warning('请先选择要删除的设备');
    return;
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectionRows.value.length} 台设备吗？`,
      '批量删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    for (const device of selectionRows.value) {
      if (device.db_id == null) {
        console.warn('设备缺少 db_id，跳过删除:', device.device_id || device.id);
        continue;
      }
      await deviceApi.deleteDevice(device.db_id);
    }

    ElMessage.success('批量删除成功');
    selectionRows.value = [];
    await refreshDevices();
  } catch (error) {
    if (error !== 'cancel') {
      if (isPermissionError(error)) return;
      ElMessage.error('批量删除失败：' + (error.message || error));
    }
  }
};

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

const toggleRowExpansion = (...args) => {
  proxy.$refs.tableRef.toggleRowExpansion(...args);
};

const handleConnect = (...args) => {
  proxy.$refs.wirelessGroupRef?.connect?.(...args);
};

const openTaskDialog = () => {
  taskDialogRef.value?.open();
};

const onAutoConnected = () => {};

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

const stopAutoRefresh = () => {
  if (autoRefreshTimer.value) {
    clearInterval(autoRefreshTimer.value);
    autoRefreshTimer.value = null;
  }
};

const handleAutoRefreshChange = (enabled) => {
  localStorage.setItem("deviceAutoRefreshEnabled", enabled.toString());

  if (enabled) {
    startAutoRefresh();
  } else {
    stopAutoRefresh();
  }
};

const isDevicePage = () => {
  return route.name === "Devices" || route.name === "DeviceDetail";
};

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

// 带 highlight_device_id 进入时，列表加载后定位并闪烁对应行
watch(
  () => [deviceList.value, route.query.highlight_device_id],
  ([list, hid]) => {
    if (!hid || !list.length) return;
    const found = list.some((r) => r.id === hid);
    if (!found) return;
    if (flashClearTimer) { clearTimeout(flashClearTimer); flashClearTimer = null; }
    flashDeviceId.value = hid;
    nextTick(() => {
      const table = tableRef.value?.$el;
      if (!table) return;
      const row = table.querySelector("tr.notification-flash-row");
      if (row) row.scrollIntoView({ behavior: "smooth", block: "nearest" });
    });
    flashClearTimer = setTimeout(() => {
      flashDeviceId.value = null;
      flashClearTimer = null;
      const q = { ...route.query };
      delete q.highlight_device_id;
      router.replace({ path: route.path, query: Object.keys(q).length ? q : undefined });
    }, 2600);
  },
  { flush: "post" },
);

onMounted(() => {
  const savedAutoRefresh = localStorage.getItem("deviceAutoRefreshEnabled");
  if (savedAutoRefresh !== null) {
    autoRefreshEnabled.value = savedAutoRefresh === "true";
    if (autoRefreshEnabled.value) {
      startAutoRefresh();
    }
  }

  getDevices();
  getUserList();
});

onUnmounted(() => {
  stopAutoRefresh();
  if (flashClearTimer) { clearTimeout(flashClearTimer); flashClearTimer = null; }
});
</script>

<style lang="scss" scoped>
.device-management {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: var(--el-bg-color-page, #f5f7fa);
}

.refresh-control {
  display: flex;
  align-items: center;
  gap: 8px;

  .refresh-text {
    font-size: 14px;
    color: var(--el-text-color-regular, #606266);
    white-space: nowrap;
  }
}

.cursor-pointer {
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s;

  &:hover {
    background-color: var(--el-fill-color-light, #f5f7fa);
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
  flex-shrink: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  background: var(--el-bg-color, white);
  padding: 16px 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--el-border-color-lighter, transparent);

  .header-content {
    display: flex;
    align-items: center;
    gap: 12px;
    min-width: 0;
  }

  .header-content h1 {
    margin: 0;
    font-size: 24px;
    font-weight: 500;
    color: var(--el-text-color-primary, #303133);
  }

  .description {
    margin: 0;
    color: var(--el-text-color-regular, #606266);
    font-size: 14px;
  }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.device-content {
  flex: 1;
  overflow: hidden;
  margin-bottom: 20px;

  .device-card {
    height: 100%;
    display: flex;
    flex-direction: column;

    :deep(.el-card__body) {
      flex: 1;
      overflow: hidden;
      padding: 0;
    }
  }

  .table-scroll-container {
    width: 100%;
    height: 100%;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 20px;
  }
}

:deep() {
  .el-table {
    width: 100% !important;

    .el-table__body-wrapper {
      overflow-x: hidden;
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
