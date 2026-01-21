<template>
  <div class="flex items-center flex-none" style="gap: 15px">
    <div class="w-96 flex-none">
      <el-autocomplete
        v-model="address"
        placeholder="192.168.0.1:5555"
        clearable
        :fetch-suggestions="fetchSuggestions"
        class="!w-full"
        value-key="id"
        @select="onSelect"
      >
        <template #default="{ item }">
          <div class="flex items-center">
            <div class="flex-1 w-0">
              {{ item.id }}
            </div>
            <div
              class="flex-none leading-none"
              @click.prevent.stop="handleRemove(item)"
            >
              <el-icon class="hover:text-primary-500 !active:text-primary-700">
                <Close />
              </el-icon>
            </div>
          </div>
        </template>
      </el-autocomplete>
    </div>

    <el-button-group>
      <el-button
        type="primary"
        :icon="loading ? '' : 'Connection'"
        :loading="loading"
        :disabled="!address.trim()"
        class="flex-none !border-none"
        @click="handleConnect()"
      >
        连接
      </el-button>

      <el-button
        v-if="loading"
        type="default"
        plain
        class="flex-none"
        @click="handleUnConnect()"
      >
        取消
      </el-button>
    </el-button-group>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { ElMessage } from "element-plus";
import deviceApi from "@/api/device";

const props = defineProps({
  handleRefresh: {
    type: Function,
    default: () => () => false,
  },
});

const emit = defineEmits(["auto-connected"]);

const loading = ref(false);
const address = ref("");
const wirelessList = ref([]);

// 转换ADB状态到数据库状态
const convertAdbStatusToDbStatus = (adbStatus) => {
  const statusMap = {
    device: "online",
    unauthorized: "offline",
    offline: "offline",
    online: "online",
    busy: "busy",
    maintenance: "maintenance",
  };
  return statusMap[adbStatus] || "offline";
};

async function fetchSuggestions(value, callback) {
  let results = [];

  if (value) {
    results = wirelessList.value.filter(
      (item) => item.id.toLowerCase().indexOf(value.toLowerCase()) === 0,
    );
  } else {
    results = [...wirelessList.value];
  }

  callback(results);
}

function onSelect(device) {
  address.value = device.id;
}

function handleRemove(info) {
  const index = wirelessList.value.findIndex((item) => info.id === item.id);

  if (index !== -1) {
    wirelessList.value.splice(index, 1);
  }
}

async function handleConnect() {
  const deviceAddress = address.value;

  if (!deviceAddress) {
    ElMessage.warning("请输入设备地址");
    return false;
  }

  loading.value = true;

  try {
    ElMessage.info("正在连接设备...");

    // 调用后端API连接无线设备
    const response = await deviceApi.executeAdbCommand(
      `connect ${deviceAddress}`,
    );

    // 检查响应是否成功
    if (response.success && response.data.exit_code === 0) {
      // 添加到无线列表
      wirelessList.value.push({ id: deviceAddress });

      ElMessage.success(`设备 ${deviceAddress} 连接成功`);

      // 保存设备到数据库
      await saveDeviceToDatabase(deviceAddress);

      // 只有连接成功才刷新设备列表
      props.handleRefresh();
    } else {
      // 连接失败
      const errorMessage = response.data?.stderr || "设备连接失败";
      ElMessage.error(errorMessage);
    }
  } catch (error) {
    console.warn("连接设备失败:", error);

    // 根据错误类型提供更详细的提示
    let errorMessage = "设备连接失败";
    if (error.response) {
      if (error.response.status === 404) {
        errorMessage = "设备地址不存在或无法访问";
      } else if (error.response.status === 500) {
        errorMessage = error.response.data?.message || "服务器错误，请稍后重试";
      } else if (error.response.data && error.response.data.message) {
        errorMessage = error.response.data.message;
      }
    } else if (error.message) {
      errorMessage = `连接失败: ${error.message}`;
    }

    ElMessage.error(errorMessage);
  } finally {
    loading.value = false;
  }
}

// 保存设备到数据库
async function saveDeviceToDatabase(deviceId) {
  try {
    // 检查设备是否已存在
    const existingDevices = await deviceApi.getDeviceList({
      page: 1,
      size: 1000,
    });
    const existingDevice = existingDevices.data.devices.find(
      (d) => d.device_id === deviceId,
    );

    if (!existingDevice) {
      // 获取设备详细信息
      const deviceInfoResponse = await deviceApi.executeAdbCommand(
        `-s ${deviceId} shell getprop ro.product.model`,
      );
      const deviceModel = deviceInfoResponse.data.stdout.trim() || "Unknown";

      // 获取Android版本
      const versionResponse = await deviceApi.executeAdbCommand(
        `-s ${deviceId} shell getprop ro.build.version.release`,
      );
      const osVersion = versionResponse.data.stdout.trim() || "Unknown";

      // 获取设备状态
      const statusResponse = await deviceApi.executeAdbCommand(
        `-s ${deviceId} get-state`,
      );
      const adbStatus = statusResponse.data.stdout.trim() || "offline";

      // 创建设备记录
      await deviceApi.createDevice({
        device_name: deviceModel,
        device_model: deviceModel,
        os_type: "android",
        os_version: osVersion,
        device_id: deviceId,
        status: convertAdbStatusToDbStatus(adbStatus),
      });
    } else {
      // 设备已存在，更新状态为online
      if (existingDevice.status !== "online") {
        await deviceApi.updateDevice(existingDevice.id, { status: "online" });
      }
    }
  } catch (error) {
    console.error("保存设备到数据库失败:", error);
  }
}

function handleUnConnect() {
  loading.value = false;
}
</script>

<style lang="scss" scoped>
:deep() .el-autocomplete {
  width: 100%;
}
</style>
