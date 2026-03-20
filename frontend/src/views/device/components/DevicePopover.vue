<template>
  <el-popover
    ref="popoverRef"
    placement="right"
    width="336"
    trigger="hover"
    popper-class="device-popover-popper !p-0 !overflow-hidden !rounded-lg"
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
      class="device-popover-body"
      :class="{ '!h-auto': !connectFlag }"
    >
      <div
        v-if="connectFlag"
        class="device-popover-screencap"
      >
        <img
          v-if="deviceInfo.screencap"
          :src="deviceInfo.screencap"
          class="device-popover-screencap-img"
          alt="设备截图"
          @click="handlePreview"
        >
        <div
          v-else
          class="text-center p-1 text-gray-500"
        >
          <el-icon class="text-xl mb-0.5">
            <Picture />
          </el-icon>
          <p class="text-xs">
            无法获取截图
          </p>
        </div>
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

async function onBeforeEnter() {
  Object.assign(deviceInfo.value, { ...props.device });

  if (!connectFlag.value) {
    return false;
  }

  isHovering.value = true;

  if (!deviceInfo.value.screencap) {
    loading.value = true;
  }

  screencapTimer.value = setInterval(() => {
    getScreencap();
  }, 5 * 1000);

  await getScreencap();

  loading.value = false;
}

async function getScreencap() {
  try {
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
    const rawOutput = response.data.stdout;
    // 只保留base64部分，去除可能的错误信息
    const base64Data = rawOutput
      .replace(/\n/g, "")
      .replace(/^.*?base64,?/i, "");

    if (
      base64Data &&
      base64Data.length > 0 &&
      /^[A-Za-z0-9+/=]+$/.test(base64Data)
    ) {
      const screencap = `data:image/png;base64,${base64Data}`;
      Object.assign(deviceInfo.value, { screencap });
    } else {
      console.warn("获取截图失败: 无效的base64数据");
      Object.assign(deviceInfo.value, { screencap: void 0 });
    }
  } catch (error) {
    console.warn("获取截图失败:", error);
    Object.assign(deviceInfo.value, { screencap: void 0 });
  }
}



function parseBatteryInfo(output) {
  const battery = {
    batteryPercentage: null,
    isCharging: null,
    temperatureCelsius: null,
    powerSource: null,
    voltageV: null,
  };

  const lines = output.split("\n");

  let acPowered = false;
  let usbPowered = false;
  let wirelessPowered = false;

  for (const line of lines) {
    const trimmedLine = line.trim();

    if (trimmedLine.startsWith("level:")) {
      const match = trimmedLine.match(/level:\s*(\d+)/);
      if (match) {
        battery.batteryPercentage = parseInt(match[1]);
      }
    }
    else if (trimmedLine.startsWith("status:")) {
      const match = trimmedLine.match(/status:\s*(\d+)/);
      if (match) {
        const status = parseInt(match[1]);
        battery.isCharging = status === 2 || status === 5; // 2: charging, 5: full
      }
    }
    else if (trimmedLine.startsWith("temperature:")) {
      const match = trimmedLine.match(/temperature:\s*(\d+)/);
      if (match) {
        const temp = parseInt(match[1]);
        battery.temperatureCelsius = temp / 10; // 转换为摄氏度
      }
    }
    else if (trimmedLine.startsWith("AC powered:")) {
      acPowered = trimmedLine.includes("true");
    } else if (trimmedLine.startsWith("USB powered:")) {
      usbPowered = trimmedLine.includes("true");
    } else if (trimmedLine.startsWith("Wireless powered:")) {
      wirelessPowered = trimmedLine.includes("true");
    }
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
  isHovering.value = false;
}



watch(connectFlag, (newVal, oldVal) => {
  if (oldVal && !newVal) {
    clearInterval(screencapTimer.value);
  }
});

onBeforeUnmount(() => {
  onAfterLeave();
});
</script>

<style lang="scss" scoped>
.device-popover-body {
  padding: 8px;
  max-height: 85vh;
  overflow: hidden;
  box-sizing: border-box;
}

.device-popover-screencap {
  width: 320px;
  height: 600px;
  overflow: hidden;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  background: var(--el-fill-color-light, #f5f7fa);
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  cursor: pointer;
}

/* 铺满容器宽度、顶对齐，避免左侧空白；仅缩小不放大 */
.device-popover-screencap-img {
  width: 100%;
  height: auto;
  max-height: 100%;
  object-fit: contain;
  object-position: top left;
  display: block;
}
</style>

<style lang="scss">
/* 弹层宽度由 width="560" 控制，确保内容不溢出 */
.device-popover-popper {
  box-sizing: border-box;
}
</style>
