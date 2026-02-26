<template>
  <el-dialog
    v-model="visible"
    title="设备详情"
    width="560px"
    destroy-on-close
    @closed="handleClosed"
  >
    <div
      v-loading="loading"
      class="device-detail-dialog-body"
    >
      <el-descriptions
        v-if="device.id || device.device_id"
        :column="1"
        border
      >
        <el-descriptions-item label="设备序列号">
          {{ device.id || device.device_id || "-" }}
        </el-descriptions-item>
        <el-descriptions-item label="设备名称">
          {{ device.name || device.device_name || "未命名设备" }}
        </el-descriptions-item>
        <el-descriptions-item label="设备型号">
          {{ device.device_model || "-" }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusTagType(device.status)">
            {{ getStatusText(device.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="操作系统">
          {{ device.os_type || "-" }}
        </el-descriptions-item>
        <el-descriptions-item label="系统版本">
          {{ device.os_version || "-" }}
        </el-descriptions-item>
        <el-descriptions-item label="连接方式">
          <el-tag
            v-if="device.wifi !== undefined"
            :type="device.wifi ? 'success' : 'primary'"
            size="small"
          >
            {{ device.wifi ? "WiFi" : "USB" }}
          </el-tag>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="设备电量">
          <template v-if="device.battery && device.battery.batteryPercentage !== null">
            <el-progress
              :percentage="device.battery.batteryPercentage"
              :stroke-width="8"
              :color="getBatteryColor(device.battery.batteryPercentage)"
              :show-text="true"
            />
            <div style="margin-top: 6px">
              <el-tag
                :type="device.battery.isCharging ? 'success' : 'info'"
                size="small"
              >
                {{ device.battery.isCharging ? "充电中" : "未充电" }}
              </el-tag>
            </div>
          </template>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="温度">
          {{
            device.battery && device.battery.temperatureCelsius != null
              ? `${device.battery.temperatureCelsius}℃`
              : "-"
          }}
        </el-descriptions-item>
        <el-descriptions-item label="电源来源">
          {{ device.battery && device.battery.powerSource != null ? device.battery.powerSource : "-" }}
        </el-descriptions-item>
        <el-descriptions-item label="电压">
          {{
            device.battery && device.battery.voltageV != null
              ? `${device.battery.voltageV}v`
              : "-"
          }}
        </el-descriptions-item>
        <el-descriptions-item label="设备负责人">
          {{ device.owner_name || "-" }}
        </el-descriptions-item>
        <el-descriptions-item label="最后更新">
          {{ device.updated_at || "-" }}
        </el-descriptions-item>
      </el-descriptions>
      <el-empty
        v-else-if="!loading"
        description="暂无设备信息"
      />
    </div>
    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from "vue";
import { ElMessage } from "element-plus";
import deviceApi from "@/api/device";
import { getStatusTagType, getStatusText } from "@/utils/deviceStatus";

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  /** 设备数据库 ID，用于请求详情 */
  deviceId: {
    type: Number,
    default: null,
  },
  /** 初始行数据（无 deviceId 时直接展示） */
  row: {
    type: Object,
    default: () => ({}),
  },
});

const emit = defineEmits(["update:modelValue"]);

const visible = ref(props.modelValue);
const loading = ref(false);
const device = ref({});

watch(
  () => props.modelValue,
  (val) => {
    visible.value = val;
    if (val) {
      open();
    }
  },
  { immediate: true },
);
watch(visible, (val) => {
  emit("update:modelValue", val);
});

function getBatteryColor(percentage) {
  if (percentage < 20) return "#f56c6c";
  if (percentage < 50) return "#e6a23c";
  return "#67c23a";
}

async function open() {
  device.value = { ...(props.row || {}) };
  if (props.deviceId) {
    loading.value = true;
    try {
      const response = await deviceApi.getDeviceDetail(props.deviceId);
      device.value = response.data.device || {};
    } catch (error) {
      ElMessage.error(
        "获取设备详情失败：" + (error.response?.data?.message || error.message),
      );
    } finally {
      loading.value = false;
    }
  }
}

function handleClosed() {
  device.value = {};
}
</script>

<style scoped>
.device-detail-dialog-body {
  min-height: 120px;
}
</style>
