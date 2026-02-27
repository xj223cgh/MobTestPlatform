<template>
  <div class="device-script-execution">
    <div class="page-header-container">
      <div class="title-section">
        <h1>设备脚本执行：{{ taskInfo.task_name || '加载中...' }}</h1>
      </div>
      <div class="buttons-section">
        <el-button
          v-if="canStart && !executing && taskStatus !== 'completed'"
          type="primary"
          :loading="starting"
          @click="handleStartExecute"
        >
          <el-icon><VideoPlay /></el-icon>
          开始执行
        </el-button>
        <el-button
          v-if="taskStatus === 'running' && executing"
          type="danger"
          :loading="stopping"
          @click="handleStopExecute"
        >
          <el-icon><VideoPause /></el-icon>
          终止执行
        </el-button>
        <template v-if="taskStatus === 'completed' && reportAutoGenerate === 'auto'">
          <span class="report-hint">
            任务完成时已自动生成报告；如需改为手动生成，请前往
            <router-link :to="{ path: '/settings', query: { tab: 'feature' } }" class="report-hint-link">系统设置</router-link>
            修改。
          </span>
          <el-button
            type="success"
            @click="handleViewReport"
          >
            <el-icon><Document /></el-icon>
            查看报告
          </el-button>
        </template>
        <el-button
          v-if="taskStatus === 'completed' && reportAutoGenerate !== 'auto'"
          type="primary"
          :loading="generatingReport"
          @click="handleGenerateReport"
        >
          <el-icon><Document /></el-icon>
          生成报告
        </el-button>
        <el-button @click="handleBack">
          <el-icon><ArrowLeft /></el-icon>
          返回列表
        </el-button>
      </div>
    </div>

    <div class="main-content">
      <el-card v-loading="loading" class="info-card">
        <template #header>
          <span>任务信息</span>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务名称">{{ taskInfo.task_name }}</el-descriptions-item>
          <el-descriptions-item label="任务状态">
            <el-tag :type="statusTagType">{{ statusText }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="脚本文件">{{ taskInfo.script_file || '-' }}</el-descriptions-item>
          <el-descriptions-item label="执行设备" :span="2">
            <template v-if="devices.length">
              <el-tag v-for="d in devices" :key="d.id" size="small" style="margin-right: 8px">
                {{ formatDeviceDisplay(d) }}
              </el-tag>
            </template>
            <span v-else>-</span>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <el-card class="terminal-card">
        <template #header>
          <div class="terminal-header">
            <span>终端输出</span>
            <div class="terminal-header-right">
              <span v-if="taskStatus === 'completed'" class="terminal-header-hint">
                任务已执行完成，请前往报告详情中查看各设备的终端输出及执行状态
              </span>
              <span v-else-if="!executing" class="terminal-header-hint">
                点击「开始执行」后，将在此处实时显示各设备的脚本执行输出
              </span>
            </div>
          </div>
        </template>
        <div ref="terminalRef" class="terminal-output" v-html="terminalHtml"></div>
        <div v-if="!terminalOutput && !executing" class="terminal-placeholder"></div>
        <div v-if="executing" class="terminal-status">
          <el-icon class="is-loading"><Loading /></el-icon>
          正在执行设备脚本…
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { ArrowLeft, VideoPlay, VideoPause, Document, Loading } from "@element-plus/icons-vue";
import testTaskApi from "@/api/testTask";
import deviceApi from "@/api/device";
import { getReportList, manualGenerateReport } from "@/api/report";
import { getUserSettings } from "@/api/settings";
import { isPermissionError } from "@/utils/request";

const route = useRoute();
const router = useRouter();
const taskId = route.params.id;

const loading = ref(true);
const starting = ref(false);
const stopping = ref(false);
const executing = ref(false);
const generatingReport = ref(false);
const taskInfo = ref({});
const devices = ref([]);
const terminalOutput = ref("");
const terminalRef = ref(null);
const abortRequested = ref(false);
/** 报告生成方式：auto 时显示「查看报告」，否则显示「生成报告」 */
const reportAutoGenerate = ref("manual");

const taskStatus = computed(() => taskInfo.value?.status || "pending");

const statusText = computed(() => {
  const map = { pending: "待执行", running: "执行中", paused: "已暂停", completed: "已完成" };
  return map[taskStatus.value] || taskStatus.value;
});

const statusTagType = computed(() => {
  const map = { pending: "info", running: "warning", paused: "warning", completed: "success" };
  return map[taskStatus.value] || "info";
});

/** 设备展示口径统一：设备名称 (设备ID)，与报告/列表一致 */
function formatDeviceDisplay(d) {
  const id = d?.device_id ?? d?.id;
  const name = d?.device_name;
  if (name && id) return `${name} (${id})`;
  return name || id || "-";
}

/** 可以开始执行：待执行或已完成（重新执行），且有关联设备 */
const canStart = computed(() => {
  const status = taskStatus.value;
  return (status === "pending" || status === "completed") && devices.value.length > 0;
});

/** 将终端文本转成带换行的 HTML，便于显示 */
const terminalHtml = computed(() => {
  if (!terminalOutput.value) return "";
  const escaped = terminalOutput.value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\n/g, "<br/>");
  return escaped;
});

const loadTaskDetail = async () => {
  if (!taskId) return;
  loading.value = true;
  try {
    const res = await testTaskApi.getTestTaskDetail(taskId);
    taskInfo.value = res.data?.test_task || {};
    if (taskInfo.value.task_type !== "device_script") {
      ElMessage.warning("该任务不是设备脚本任务");
      router.replace({ name: "TestTasks" });
      return;
    }
    const devRes = await testTaskApi.getTaskDevices(taskId);
    devices.value = devRes.data?.devices || [];
    // 持久化的终端输出：任务完成后 result 中存有 terminal_log，刷新或再次打开时可恢复
    const rawResult = taskInfo.value.result;
    if (rawResult && typeof rawResult === "string") {
      try {
        const parsed = JSON.parse(rawResult);
        if (parsed && typeof parsed.terminal_log === "string") {
          terminalOutput.value = parsed.terminal_log;
        }
      } catch (_) {
        // 忽略解析失败
      }
    }
  } catch (e) {
    console.error("加载任务详情失败", e);
    ElMessage.error("加载任务详情失败");
  } finally {
    loading.value = false;
  }
};

const appendOutput = (text, label) => {
  const line = label ? `[${label}] ${text}` : text;
  terminalOutput.value += (terminalOutput.value ? "\n" : "") + line;
  nextTickScrollToBottom();
};

function nextTickScrollToBottom() {
  if (terminalRef.value) {
    requestAnimationFrame(() => {
      terminalRef.value.scrollTop = terminalRef.value.scrollHeight;
    });
  }
}

const runDeviceScript = async (device) => {
  let taskType = "shell";
  if (taskInfo.value.script_file) {
    const ext = taskInfo.value.script_file.toLowerCase().split(".").pop();
    if (ext === "py") taskType = "python";
  }
  const requestData = {
    task_type: taskType,
    command: taskInfo.value.command || "",
    task_id: parseInt(taskId, 10),
  };
  if (taskInfo.value.file_path) {
    requestData.file_path = taskInfo.value.file_path;
    requestData.script_file = taskInfo.value.script_file;
  }
  const res = await deviceApi.executeDeviceTask(device.id, requestData);
  const data = res.data || {};
  const name = device.device_id || device.device_name || `设备 ${device.id}`;
  if (data.stdout) appendOutput(data.stdout.trim(), name);
  if (data.stderr) appendOutput(data.stderr.trim(), `${name} (stderr)`);
  if (data.exit_code !== undefined) appendOutput(`退出码: ${data.exit_code}`, name);
  return data;
};

const handleStartExecute = async () => {
  if (!devices.value.length) {
    ElMessage.warning("任务未关联设备，无法执行");
    return;
  }
  starting.value = true;
  abortRequested.value = false;
  terminalOutput.value = "";
  const executionResults = [];
  try {
    // 执行前检查设备是否在线（ADB 连接），避免离线时点击执行却无终端输出
    const offlineList = [];
    for (const d of devices.value) {
      try {
        const res = await deviceApi.getDeviceStatus(d.id);
        if (res.data?.status !== "connected") {
          offlineList.push(formatDeviceDisplay(d));
        }
      } catch {
        offlineList.push(formatDeviceDisplay(d));
      }
    }
    if (offlineList.length) {
      starting.value = false;
      ElMessage.warning(`以下设备未连接，请连接后再执行：${offlineList.join("、")}`);
      return;
    }

    await testTaskApi.executeTestTask(taskId);
    await loadTaskDetail();
    executing.value = true;
    ElMessage.success("任务已开始执行");

    for (const device of devices.value) {
      if (abortRequested.value) {
        appendOutput("用户终止执行", "系统");
        break;
      }
      const deviceName = device.device_id || device.device_name || `设备 ${device.id}`;
      try {
        appendOutput(`开始执行设备: ${deviceName}`, "系统");
        const startTime = Date.now();
        const data = await runDeviceScript(device);
        const executionTime = Math.round((Date.now() - startTime) / 1000);
        const success = data && (data.exit_code === 0 || data.exit_code === undefined);
        executionResults.push({
          device_id: device.device_id || device.device_name,
          device_name: device.device_name || device.device_id || "-",
          status: success ? "success" : "failed",
          execution_time: executionTime,
          exit_code: data?.exit_code ?? (success ? 0 : -1),
          output: data?.stdout ?? "",
          error_output: data?.stderr ?? "",
        });
      } catch (err) {
        const msg = err.response?.data?.message || err.message || "执行失败";
        appendOutput(`执行失败: ${msg}`, device.device_id || device.device_name || "设备");
        executionResults.push({
          device_id: device.device_id || device.device_name,
          device_name: device.device_name || device.device_id || "-",
          status: "failed",
          execution_time: 0,
          exit_code: -1,
          output: "",
          error_output: String(msg),
        });
      }
    }

    // 终止时补全未执行设备为 cancelled，保证报告设备列表与状态一致
    if (abortRequested.value && devices.value.length) {
      const executedIds = new Set(executionResults.map((e) => e.device_id || e.device_name));
      for (const device of devices.value) {
        const key = device.device_id || device.device_name || device.id;
        if (key != null && !executedIds.has(key)) {
          executionResults.push({
            device_id: device.device_id || device.device_name,
            device_name: device.device_name || device.device_id || "-",
            status: "cancelled",
            execution_time: 0,
            exit_code: null,
            output: "",
            error_output: "用户终止执行",
          });
          executedIds.add(key);
        }
      }
    }

    const resultPayload = {
      executions: executionResults,
      terminal_log: terminalOutput.value || "",
    };
    if (abortRequested.value) {
      await testTaskApi.completeTestTask(taskId, { result: resultPayload });
      ElMessage.info("任务已终止");
    } else {
      await testTaskApi.completeTestTask(taskId, { result: resultPayload });
      ElMessage.success("任务已完成");
    }
    await loadTaskDetail();
  } catch (err) {
    if (isPermissionError(err)) return;
    console.error("执行失败", err);
    ElMessage.error(err.response?.data?.message || err.message || "执行失败");
  } finally {
    starting.value = false;
    executing.value = false;
  }
};

const handleStopExecute = async () => {
  try {
    await ElMessageBox.confirm("确定要终止当前执行吗？", "终止执行", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    });
    abortRequested.value = true;
    stopping.value = true;
    ElMessage.info("正在终止…");
  } catch {
    // 用户取消
  } finally {
    stopping.value = false;
  }
};

const handleViewReport = async () => {
  try {
    const res = await getReportList({ task_id: taskId, report_type: "device_script", page: 1, size: 1 });
    const list = res.data?.reports || [];
    if (list.length > 0) {
      router.push({ name: "ReportDetailByRecord", params: { id: list[0].id } });
    } else {
      router.push({ name: "ReportManagement", query: { report_type: "device_script" } });
    }
  } catch {
    router.push({ name: "ReportManagement", query: { report_type: "device_script" } });
  }
};

const handleGenerateReport = async () => {
  try {
    await ElMessageBox.confirm("确认为该任务生成报告？生成后将跳转到报告详情。", "生成报告", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "info",
    });
  } catch {
    return;
  }
  generatingReport.value = true;
  try {
    const res = await manualGenerateReport(taskId);
    if (res?.success && res?.data?.report_id) {
      ElMessage.success("报告已生成");
      router.push({ name: "ReportDetailByRecord", params: { id: res.data.report_id } });
    } else {
      ElMessage.error(res?.message || "生成报告失败");
    }
  } catch (e) {
    ElMessage.error(e?.response?.data?.message || e?.message || "生成报告失败");
  } finally {
    generatingReport.value = false;
  }
};

const loadReportSetting = async () => {
  try {
    const res = await getUserSettings();
    if (res?.data && res.data.report_auto_generate === "auto") {
      reportAutoGenerate.value = "auto";
    } else {
      reportAutoGenerate.value = "manual";
    }
  } catch {
    reportAutoGenerate.value = "manual";
  }
};

const handleBack = () => {
  router.push({ name: "TestTasks", query: { tab: "device_script" } });
};

onMounted(() => {
  loadReportSetting();
  loadTaskDetail();
});
</script>

<style lang="scss" scoped>
.device-script-execution {
  padding: 16px;
  min-height: 100vh;
  background: var(--el-bg-color-page, #f5f7fa);
}

.page-header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;

  .title-section h1 {
    margin: 0;
    font-size: 20px;
    font-weight: 600;
  }

  .buttons-section {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }

  .report-hint {
    font-size: 12px;
    color: var(--el-text-color-secondary, #909399);
    margin-right: 4px;
  }

  .report-hint-link {
    color: var(--el-color-primary);
    text-decoration: none;
    &:hover {
      text-decoration: underline;
    }
  }
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-card {
  flex-shrink: 0;
}

.terminal-card {
  flex: 1;
  min-height: 320px;
  display: flex;
  flex-direction: column;

  .terminal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
  }

  .terminal-header-right {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
  }

  .terminal-header-hint {
    font-size: 14px;
    color: var(--el-text-color-regular, #606266);
  }

  .terminal-output {
    flex: 1;
    min-height: 240px;
    max-height: 60vh;
    overflow-y: auto;
    font-family: "Consolas", "Monaco", monospace;
    font-size: 13px;
    line-height: 1.5;
    padding: 12px;
    background: #1e1e1e;
    color: #d4d4d4;
    border-radius: 4px;
    white-space: pre-wrap;
    word-break: break-all;
  }

  .terminal-placeholder {
    min-height: 200px;
    color: var(--el-text-color-secondary);
    font-size: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;
  }

  .terminal-status {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 0;
    color: var(--el-color-primary);
  }
}
</style>
