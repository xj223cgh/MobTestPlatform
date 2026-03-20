<template>
  <div class="control-bar">
    <div class="flex flex-wrap gap-4 px-4">
      <!-- 返回按钮 -->
      <el-button
        type="primary"
        text
        :disabled="isButtonDisabled"
        title="返回"
        class="control-button"
        @click="executeCommand('input keyevent 4')"
      >
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>

      <!-- 主页按钮 -->
      <el-button
        type="primary"
        text
        :disabled="isButtonDisabled"
        title="主页"
        class="control-button"
        @click="executeCommand('input keyevent 3')"
      >
        <el-icon><HomeFilled /></el-icon>
        主页
      </el-button>

      <!-- 最近任务按钮 -->
      <el-button
        type="primary"
        text
        :disabled="isButtonDisabled"
        title="最近任务"
        class="control-button"
        @click="executeCommand('input keyevent 187')"
      >
        <el-icon><List /></el-icon>
        最近任务
      </el-button>

      <!-- 通知按钮 -->
      <el-button
        type="primary"
        text
        :disabled="isButtonDisabled"
        title="通知"
        class="control-button"
        @click="executeCommand('cmd statusbar expand-notifications')"
      >
        <el-icon><Bell /></el-icon>
        通知
      </el-button>

      <!-- 截图按钮 -->
      <el-button
        type="primary"
        text
        :disabled="isButtonDisabled"
        title="截图"
        class="control-button"
        @click="handleScreenshot"
      >
        <el-icon><Crop /></el-icon>
        截图
      </el-button>

      <!-- 亮屏按钮 -->
      <el-button
        type="primary"
        text
        :disabled="isButtonDisabled"
        title="亮屏"
        class="control-button"
        @click="executeCommand('input keyevent 224')"
      >
        <el-icon><Sunny /></el-icon>
        亮屏
      </el-button>

      <!-- 息屏按钮 -->
      <el-button
        type="primary"
        text
        :disabled="isButtonDisabled"
        title="息屏"
        class="control-button"
        @click="executeCommand('input keyevent 26')"
      >
        <el-icon><SwitchButton /></el-icon>
        息屏
      </el-button>

      <!-- 音量加按钮 -->
      <el-button
        type="primary"
        text
        :disabled="isButtonDisabled"
        title="音量加"
        class="control-button"
        @click="executeCommand('input keyevent 24')"
      >
        <el-icon><Plus /></el-icon>
        音量加
      </el-button>

      <!-- 音量减按钮 -->
      <el-button
        type="primary"
        text
        :disabled="isButtonDisabled"
        title="音量减"
        class="control-button"
        @click="executeCommand('input keyevent 25')"
      >
        <el-icon><Minus /></el-icon>
        音量减
      </el-button>

      <!-- 静音按钮 -->
      <el-button
        type="primary"
        text
        :disabled="isButtonDisabled"
        title="静音"
        class="control-button"
        @click="executeCommand('input keyevent 164')"
      >
        <el-icon><Mute /></el-icon>
        静音
      </el-button>

      <!-- 重启按钮 -->
      <el-button
        type="primary"
        text
        :disabled="isButtonDisabled"
        title="重启"
        class="control-button"
        @click="executeCommand('reboot')"
      >
        <el-icon><Refresh /></el-icon>
        重启
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { ElMessage } from "element-plus";
import {
  ArrowLeft,
  HomeFilled,
  Bell,
  Crop,
  Refresh,
  List,
  Sunny,
  SwitchButton,
  Plus,
  Minus,
  Mute,
} from "@element-plus/icons-vue";
import deviceApi from "@/api/device";

// 定义组件属性
const props = defineProps({
  device: {
    type: Object,
    default: () => ({}),
  },
  disabled: {
    type: Boolean,
    default: false,
  },
});

// 计算设备禁用状态（离线/未授权或不可操作时禁用）
const disabledStatus = computed(() => {
  return ["unauthorized", "offline"];
});
const isButtonDisabled = computed(() => {
  return props.disabled || disabledStatus.value.includes(props.device?.status);
});

async function executeCommand(command) {
  try {
    const needsShell = command.startsWith("input ") || command.startsWith("cmd ") || command.startsWith("svc ");
    const fullCommand = needsShell
      ? `-s ${props.device.id} shell ${command}`
      : `-s ${props.device.id} ${command}`;

    await deviceApi.executeAdbCommand(fullCommand);
    if (command !== "input keyevent 26") {
      ElMessage.success("命令执行成功");
    }
  } catch (error) {
    console.warn("执行命令失败:", error);
    // 关闭屏幕命令不显示错误提示
    if (command !== "input keyevent 26") {
      ElMessage.error("命令执行失败");
    }
  }
}

// 截图功能
async function handleScreenshot() {
  try {
    // 使用adb命令截图
    await deviceApi.executeAdbCommand(
      `-s ${props.device.id} shell screencap -p /sdcard/screenshot.png`,
    );
    // 下载截图到本地
    await deviceApi.executeAdbCommand(
      `-s ${props.device.id} pull /sdcard/screenshot.png ./screenshot-${props.device.id}-${Date.now()}.png`,
    );
    ElMessage.success("截图成功");
  } catch (error) {
    console.warn("截图失败:", error);
    ElMessage.error("截图失败");
  }
}
</script>

<style scoped>
.control-bar {
  background-color: #f0f2f5;
  border-radius: 4px;
  padding: 16px 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  width: 100%;
}

.control-bar :deep(.el-button) {
  padding: 8px 16px;
  min-width: 80px;
}
</style>
