<template>
  <el-popover
    ref="popoverRef"
    placement="right"
    width="330"
    trigger="hover"
    popper-class="!p-0 !overflow-hidden !rounded-lg"
    :disabled="!connectFlag"
    @before-enter="onBeforeEnter"
    @after-leave="onAfterLeave"
  >
    <template #reference>
      <el-link
        type="primary"
        :underline="false"
        icon="InfoFilled"
        :disabled="!connectFlag"
      />
    </template>

    <div
      v-loading="loading"
      element-loading-text="加载中"
      class="p-2"
      :class="{ '!h-auto': !connectFlag }"
    >
      <div
        v-if="connectFlag"
        class="flex-none overflow-hidden rounded-lg shadow bg-gray-200 dark:bg-gray-700 object-contain cursor-pointer flex items-center justify-center"
        style="height: 600px"
      >
        <img
          v-if="deviceInfo.screencap"
          :src="deviceInfo.screencap"
          class="w-full h-full object-contain"
          alt="设备截图"
          @click="handlePreview"
        />
        <div v-else class="text-center p-1 text-gray-500">
          <el-icon class="text-xl mb-0.5">
            <Picture />
          </el-icon>
          <p class="text-xs">无法获取截图</p>
        </div>
      </div>

      <div class="overflow-auto mt-1" style="max-height: 40px">
        <el-descriptions
          border
          :column="1"
          class="el-descriptions--custom text-sm"
        >
          <el-descriptions-item label="设备序列号">
            {{ deviceInfo.id }}
          </el-descriptions-item>

          <template v-if="deviceInfo.battery">
            <el-descriptions-item label="电池电量">
              {{
                deviceInfo.battery.batteryPercentage !== null
                  ? `${deviceInfo.battery.batteryPercentage}%`
                  : "-"
              }}
            </el-descriptions-item>
            <el-descriptions-item label="是否充电">
              {{
                deviceInfo.battery.isCharging !== null
                  ? deviceInfo.battery.isCharging
                    ? "是"
                    : "否"
                  : "-"
              }}
            </el-descriptions-item>
            <el-descriptions-item label="温度">
              {{
                deviceInfo.battery.temperatureCelsius !== null
                  ? `${deviceInfo.battery.temperatureCelsius}℃`
                  : "-"
              }}
            </el-descriptions-item>
            <el-descriptions-item label="电源来源">
              {{
                deviceInfo.battery.powerSource !== null
                  ? deviceInfo.battery.powerSource
                  : "-"
              }}
            </el-descriptions-item>
            <el-descriptions-item label="电压">
              {{
                deviceInfo.battery.voltageV !== null
                  ? `${deviceInfo.battery.voltageV}v`
                  : "-"
              }}
            </el-descriptions-item>
          </template>
        </el-descriptions>
      </div>
    </div>

    <el-image-viewer
      v-if="imageViewerProps.visible"
      :url-list="[deviceInfo.screencap]"
      @close="onViewerClose"
    />
  </el-popover>
</template>

<script setup>
import { ref, computed, onBeforeUnmount, watch } from "vue";
import { ElMessage } from "element-plus";
import { Picture } from "@element-plus/icons-vue";
import deviceApi from "@/api/device";

const props = defineProps({
  device: {
    type: Object,
    default: () => ({}),
  },
});

const loading = ref(false);

const deviceInfo = ref({
  screencap: void 0,
  battery: void 0,
});

const connectFlag = computed(() => ["online"].includes(props.device.status));

const screencapTimer = ref();

// 跟踪悬浮状态
const isHovering = ref(false);

const imageViewerProps = ref({
  visible: false,
});

function handlePreview() {
  imageViewerProps.value.visible = true;
}

function onViewerClose() {
  imageViewerProps.value.visible = false;
}

const horizontalFlag = ref(false);

function onScreencapLoad(event) {
  const { naturalHeight, naturalWidth } = event.target;
  horizontalFlag.value = naturalWidth > naturalHeight;
}

async function onBeforeEnter() {
  Object.assign(deviceInfo.value, { ...props.device });

  if (!connectFlag.value) {
    return false;
  }

  // 进入悬浮状态
  isHovering.value = true;

  if (!deviceInfo.value.screencap) {
    loading.value = true;
  }

  screencapTimer.value = setInterval(() => {
    getScreencap();
    getBattery();
  }, 5 * 1000);

  await Promise.allSettled([getScreencap(), getBattery()]);

  loading.value = false;
}

async function getScreencap() {
  try {
    // 检查设备连接状态
    if (!connectFlag.value) {
      Object.assign(deviceInfo.value, { screencap: void 0 });
      return;
    }

    // 使用adb命令获取截图并转换为base64，传递悬浮状态
    const response = await deviceApi.executeAdbCommand(
      `-s ${props.device.id} shell screencap -p | base64`,
      {
        isHovering: isHovering.value,
      },
    );
    // 处理base64数据，去除换行符和可能的错误信息
    const rawOutput = response.data.stdout;
    // 只保留base64部分，去除可能的错误信息
    const base64Data = rawOutput
      .replace(/\n/g, "")
      .replace(/^.*?base64,?/i, "");

    // 验证base64数据是否有效
    if (
      base64Data &&
      base64Data.length > 0 &&
      /^[A-Za-z0-9+/=]+$/.test(base64Data)
    ) {
      const screencap = `data:image/png;base64,${base64Data}`;
      Object.assign(deviceInfo.value, { screencap });
    } else {
      console.warn("获取截图失败: 无效的base64数据");
      // 设置默认占位图
      Object.assign(deviceInfo.value, { screencap: void 0 });
    }
  } catch (error) {
    console.warn("获取截图失败:", error);
    // 设备已断开连接，清空截图信息
    Object.assign(deviceInfo.value, { screencap: void 0 });
  }
}

async function getBattery() {
  try {
    // 检查设备连接状态
    if (!connectFlag.value) {
      return;
    }

    // 使用adb命令获取电池信息，传递悬浮状态
    const response = await deviceApi.executeAdbCommand(
      `-s ${props.device.id} shell dumpsys battery`,
      {
        isHovering: isHovering.value,
      },
    );

    // 解析电池信息输出
    const batteryInfo = parseBatteryInfo(response.data.stdout);
    Object.assign(deviceInfo.value, { battery: batteryInfo });
  } catch (error) {
    console.warn("获取电池信息失败:", error);
    // 设备已断开连接，清空电池信息
    Object.assign(deviceInfo.value, { battery: null });
  }
}

// 解析电池信息
function parseBatteryInfo(output) {
  const battery = {
    batteryPercentage: null,
    isCharging: null,
    temperatureCelsius: null,
    powerSource: null,
    voltageV: null,
  };

  // 解析输出行
  const lines = output.split("\n");

  // 首先尝试解析现代Android设备的输出格式
  let acPowered = false;
  let usbPowered = false;
  let wirelessPowered = false;

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
    // 解析温度
    else if (trimmedLine.startsWith("temperature:")) {
      const match = trimmedLine.match(/temperature:\s*(\d+)/);
      if (match) {
        const temp = parseInt(match[1]);
        battery.temperatureCelsius = temp / 10; // 转换为摄氏度
      }
    }
    // 解析电源来源相关信息
    else if (trimmedLine.startsWith("AC powered:")) {
      acPowered = trimmedLine.includes("true");
    } else if (trimmedLine.startsWith("USB powered:")) {
      usbPowered = trimmedLine.includes("true");
    } else if (trimmedLine.startsWith("Wireless powered:")) {
      wirelessPowered = trimmedLine.includes("true");
    }
    // 解析老式设备的powered信息
    else if (trimmedLine.includes("plugged:")) {
      const match = trimmedLine.match(/plugged:\s*(\d+)/);
      if (match) {
        const plugged = parseInt(match[1]);
        if (plugged === 0) {
          battery.powerSource = "电池";
        } else if (plugged === 1) {
          battery.powerSource = "AC电源";
        } else if (plugged === 2) {
          battery.powerSource = "USB";
        } else if (plugged === 4) {
          battery.powerSource = "无线充电";
        }
      }
    }
    // 解析电压
    else if (trimmedLine.startsWith("voltage:")) {
      const match = trimmedLine.match(/voltage:\s*(\d+)/);
      if (match) {
        const voltage = parseInt(match[1]);
        battery.voltageV = voltage / 1000; // 转换为伏特
      }
    }
  }

  // 根据电源类型确定电源来源（如果没有通过plugged字段设置）
  if (battery.powerSource === null) {
    if (acPowered) {
      battery.powerSource = "AC电源";
    } else if (usbPowered) {
      battery.powerSource = "USB";
    } else if (wirelessPowered) {
      battery.powerSource = "无线充电";
    } else {
      battery.powerSource = "电池";
    }
  }

  return battery;
}

function onAfterLeave() {
  clearInterval(screencapTimer.value);
  onViewerClose();
  loading.value = false;
  // 离开悬浮状态
  isHovering.value = false;
}

function onError() {
  clearInterval(screencapTimer.value);
}

// 监听设备连接状态变化，当设备断开连接时清除定时器
watch(connectFlag, (newVal, oldVal) => {
  if (oldVal && !newVal) {
    // 设备从连接状态变为断开状态
    clearInterval(screencapTimer.value);
  }
});

onBeforeUnmount(() => {
  onAfterLeave();
});
</script>

<style lang="scss" scoped>
// 强制el-link样式，确保与其他元素居中对齐
:deep() .el-link {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  min-width: 32px !important;
  min-height: 32px !important;
  padding: 0 !important;
  margin: 0 !important;
}

:deep() .el-descriptions--custom .el-descriptions__label {
  width: auto;
  max-width: 120px;
}
</style>
