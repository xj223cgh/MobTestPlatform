<template>
  <div class="device-detail">
    <div class="page-header">
      <div class="header-content">
        <el-button
          :icon="ArrowLeft"
          @click="goBack"
        >
          返回
        </el-button>
        <h1>设备详情</h1>
        <el-button
          type="primary"
          :icon="Operation"
          :disabled="!isOnline"
          @click="openTaskDialog"
        >
          测试任务
        </el-button>
        <div class="refresh-control">
          <el-switch
            v-model="autoRefreshEnabled"
            @change="handleAutoRefreshChange"
          />
          <span class="refresh-text">{{
            autoRefreshEnabled ? "自动刷新" : "手动刷新"
          }}</span>
        </div>
      </div>
    </div>

    <div
      v-loading="loading"
      class="device-detail-content"
    >
      <el-row :gutter="20">
        <el-col :span="24">
          <el-card
            shadow="hover"
            class="device-info-card"
          >
            <template #header>
              <div class="card-header">
                <span class="card-title">设备信息</span>
                <el-tag :type="getStatusTagType(device.status)">
                  {{ getStatusText(device.status) }}
                </el-tag>
              </div>
            </template>

            <el-descriptions
              :column="3"
              border
            >
              <el-descriptions-item label="设备序列号">
                {{ device.id || "-" }}
              </el-descriptions-item>
              <el-descriptions-item label="设备名称">
                {{ device.name || "未命名设备" }}
              </el-descriptions-item>
              <el-descriptions-item label="设备型号">
                {{ device.device_model || "-" }}
              </el-descriptions-item>
              <el-descriptions-item label="操作系统">
                {{ device.os_type || "-" }}
              </el-descriptions-item>
              <el-descriptions-item label="系统版本">
                {{ device.os_version || "-" }}
              </el-descriptions-item>
              <el-descriptions-item label="连接方式">
                <el-tag
                  :type="device.wifi ? 'success' : 'primary'"
                  size="small"
                >
                  {{ device.wifi ? "WiFi" : "USB" }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="设备电量">
                <div
                  v-if="
                    device.battery && device.battery.batteryPercentage !== null
                  "
                >
                  <el-progress
                    :percentage="device.battery.batteryPercentage"
                    :stroke-width="8"
                    :color="getBatteryColor(device.battery.batteryPercentage)"
                    :show-text="true"
                  />
                  <div style="margin-top: 8px">
                    <el-tag
                      :type="device.battery.isCharging ? 'success' : 'info'"
                      size="small"
                    >
                      {{ device.battery.isCharging ? "充电中" : "未充电" }}
                    </el-tag>
                  </div>
                </div>
                <span v-else>-</span>
              </el-descriptions-item>
              <el-descriptions-item label="设备负责人">
                {{ device.owner_name || "-" }}
              </el-descriptions-item>
              <el-descriptions-item label="最后更新">
                {{ device.updated_at || "-" }}
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>
      </el-row>

      <el-row
        :gutter="20"
        style="margin-top: 20px"
      >
        <el-col :span="24">
          <el-card
            shadow="hover"
            class="mirror-card"
          >
            <template #header>
              <div class="card-header">
                <span class="card-title">设备投屏</span>
                <div class="header-actions">
                  <el-button
                    type="primary"
                    :icon="Monitor"
                    :disabled="!isOnline"
                    :loading="mirrorLoading"
                    @click="startMirror"
                  >
                    {{ mirrorLoading ? "启动中..." : "启动投屏" }}
                  </el-button>
                </div>
              </div>
            </template>

            <div class="mirror-container">
              <div
                v-if="!mirrorStarted"
                class="mirror-placeholder"
              >
                <el-empty description="点击上方按钮启动投屏">
                  <el-icon
                    :size="80"
                    color="#909399"
                  >
                    <Monitor />
                  </el-icon>
                </el-empty>
              </div>
              <div
                v-else
                class="mirror-content"
              >
                <div class="mirror-placeholder">
                  <el-alert
                    title="投屏功能开发中"
                    type="info"
                    description="设备投屏功能正在开发中，敬请期待..."
                    :closable="false"
                    show-icon
                  >
                    <template #default>
                      <p style="margin-top: 10px">
                        计划采用 ws-scrcpy
                        框架实现，支持在浏览器中直接查看和控制设备屏幕
                      </p>
                    </template>
                  </el-alert>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-row
        :gutter="20"
        style="margin-top: 20px"
      >
        <el-col :span="24">
          <el-card
            shadow="hover"
            class="operations-card"
          >
            <template #header>
              <div class="card-header">
                <span class="card-title">快捷操作</span>
              </div>
            </template>

            <div class="operations-grid">
              <el-button
                :icon="Camera"
                :disabled="!isOnline"
                @click="takeScreenshot"
              >
                截图
              </el-button>
              <el-button
                :icon="RefreshRight"
                :disabled="!isOnline"
                @click="refreshDevice"
              >
                刷新状态
              </el-button>
              <el-button
                :icon="Lock"
                :disabled="!isOnline"
                @click="lockDevice"
              >
                锁定设备
              </el-button>
              <el-button
                :icon="Unlock"
                :disabled="!isOnline"
                @click="unlockDevice"
              >
                解锁设备
              </el-button>
              <el-button
                :icon="Refresh"
                :disabled="!isOnline"
                @click="restartDevice"
              >
                重启设备
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <TaskDialog
        ref="taskDialogRef"
        :devices="[device]"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import {
  ArrowLeft,
  Monitor,
  Camera,
  RefreshRight,
  Lock,
  Unlock,
  Refresh,
  Operation,
} from "@element-plus/icons-vue";
import deviceApi from "@/api/device";
import { getStatusTagType, getStatusText } from "@/utils/deviceStatus";
import TaskDialog from "./components/TaskDialog.vue";

const route = useRoute();
const router = useRouter();

const loading = ref(false);
const mirrorLoading = ref(false);
const mirrorStarted = ref(false);
const autoRefreshTimer = ref(null);
const autoRefreshInterval = ref(5000);
const autoRefreshEnabled = ref(true);
const taskDialogRef = ref(null);
const device = ref({
  id: "",
  name: "",
  device_model: "",
  os_type: "",
  os_version: "",
  status: "",
  wifi: false,
  battery: null,
  owner_name: "",
  updated_at: "",
});

const isOnline = computed(() => device.value.status === "online");

const getBatteryColor = (percentage) => {
  if (percentage < 20) {
    return "#f56c6c";
  } else if (percentage < 50) {
    return "#e6a23c";
  } else {
    return "#67c23a";
  }
};

const goBack = () => {
  router.back();
};

const loadDeviceDetail = async () => {
  const deviceId = route.params.id;
  if (!deviceId) {
    ElMessage.error("设备ID不能为空");
    return;
  }

  loading.value = true;
  try {
    const response = await deviceApi.getDeviceDetail(deviceId);
    device.value = response.data.device || {};
  } catch (error) {
    ElMessage.error(
      "获取设备详情失败：" + (error.response?.data?.message || error.message),
    );
  } finally {
    loading.value = false;
  }
};

const startMirror = async () => {
  mirrorLoading.value = true;
  try {
    await deviceApi.executeAdbCommand(
      `scrcpy --serial="${device.value.id}" --window-title="设备 ${device.value.id} 投屏" --disable-screensaver`,
    );
    mirrorStarted.value = true;
    ElMessage.success("投屏启动成功");
  } catch (error) {
    ElMessage.error(
      "投屏启动失败：" + (error.response?.data?.message || error.message),
    );
  } finally {
    mirrorLoading.value = false;
  }
};

const takeScreenshot = async () => {
  try {
    ElMessage.info("截图功能开发中...");
  } catch (error) {
    ElMessage.error(
      "截图失败：" + (error.response?.data?.message || error.message),
    );
  }
};

const refreshDevice = async () => {
  try {
    await loadDeviceDetail();
    ElMessage.success("设备状态已刷新");
  } catch (error) {
    ElMessage.error(
      "刷新失败：" + (error.response?.data?.message || error.message),
    );
  }
};

const lockDevice = async () => {
  try {
    ElMessage.info("锁定设备功能开发中...");
  } catch (error) {
    ElMessage.error(
      "锁定设备失败：" + (error.response?.data?.message || error.message),
    );
  }
};

const unlockDevice = async () => {
  try {
    ElMessage.info("解锁设备功能开发中...");
  } catch (error) {
    ElMessage.error(
      "解锁设备失败：" + (error.response?.data?.message || error.message),
    );
  }
};

const restartDevice = async () => {
  try {
    ElMessage.info("重启设备功能开发中...");
  } catch (error) {
    ElMessage.error(
      "重启设备失败：" + (error.response?.data?.message || error.message),
    );
  }
};

// 打开任务对话框
const openTaskDialog = () => {
  taskDialogRef.value?.open();
};

// 启动自动刷新
const startAutoRefresh = () => {
  if (!autoRefreshEnabled.value) {
    return;
  }
  if (autoRefreshTimer.value) {
    clearInterval(autoRefreshTimer.value);
  }
  autoRefreshTimer.value = setInterval(() => {
    loadDeviceDetail();
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
  { immediate: true },
);

onMounted(() => {
  loadDeviceDetail();
});

onUnmounted(() => {
  stopAutoRefresh();
});
</script>

<style lang="scss" scoped>
.device-detail {
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

.page-header {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;

  .header-content {
    display: flex;
    align-items: center;
    gap: 25px;

    h1 {
      margin: 0;
      font-size: 24px;
      font-weight: 600;
      color: #303133;
    }
  }
}

.device-detail-content {
  flex: 1;
  overflow: auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  .card-title {
    font-size: 16px;
    font-weight: 600;
    color: #303133;
  }

  .header-actions {
    display: flex;
    gap: 10px;
  }
}

.mirror-container {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;

  .mirror-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .mirror-content {
    width: 100%;
    height: 100%;
  }
}

.operations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 15px;
}

:deep() {
  .el-card__body {
    padding: 20px;
  }

  .el-descriptions {
    .el-descriptions__label {
      font-weight: 600;
    }
  }
}
</style>
