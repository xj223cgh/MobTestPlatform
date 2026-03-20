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
        <!-- 仅远程访问时显示：本机（部署机）直接使用服务器 adb 管理设备，无需 Agent，不展示入口 -->
        <el-button
          v-if="showAgentConfigEntry"
          type="default"
          size="default"
          @click="agentConfigVisible = true"
        >
          <el-icon><Setting /></el-icon>
          本机 Agent
        </el-button>
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

    <!-- 本机 Agent 配置入口弹窗 -->
    <el-dialog
      v-model="agentConfigVisible"
      title="本机 Agent 配置"
      width="520px"
      class="agent-config-dialog"
      destroy-on-close
      @open="onAgentConfigOpen"
      @close="onAgentConfigClose"
    >
      <div class="agent-config-content">
        <div class="agent-config-status-card">
          <div class="agent-config-status-row">
            <span class="agent-config-status-label">当前状态</span>
            <el-tag v-if="agentBinding?.bound && agentBinding?.agent_online" type="success" size="large">已绑定 · Agent 已连接</el-tag>
            <el-tag v-else-if="agentBinding?.bound" type="warning" size="large">已绑定 · Agent 未连接</el-tag>
            <el-tag v-else type="info" size="large">未绑定</el-tag>
            <el-button type="primary" link size="small" class="agent-refresh-binding-btn" :loading="agentBindingRefreshing" @click="refreshAgentBinding">刷新状态</el-button>
          </div>
          <p v-if="agentBinding?.bound && !agentBinding?.agent_online" class="agent-config-status-hint">
            请在本机重新运行 Agent 或在下方点击「启动 Agent」（若支持）。关闭 Agent 后约 1 分钟内会显示为未连接。
          </p>
        </div>

        <div class="agent-config-section">
          <div class="agent-config-usage-header" @click="agentUsageCollapsed = !agentUsageCollapsed">
            <span class="agent-config-section-title">使用方式</span>
            <el-icon class="agent-usage-toggle" :class="{ 'agent-usage-collapsed': agentUsageCollapsed }">
              <ArrowDown />
            </el-icon>
          </div>
          <div v-show="!agentUsageCollapsed" class="agent-config-usage">
            <template v-if="isPlatformHost && agentCanLaunch">
              <p class="agent-config-usage-desc">您正在<strong>部署平台的本机</strong>访问，可直接由平台在本机启动 Agent 并自动绑定，无需手动运行程序。</p>
            </template>
            <template v-else>
              <p class="agent-config-usage-desc">您正在<strong>其他电脑</strong>访问平台，需在<strong>本机</strong>运行 Agent 并完成绑定后，才能在此电脑上管理 USB 设备：</p>
              <ol class="agent-config-usage-steps">
                <li>下载 <strong>MobTestAgent.exe</strong> 到本机（见下方下载按钮）。</li>
                <li><strong>运行 Agent 时必须指定平台地址</strong>，在本机打开命令行，进入 Agent 所在目录后执行：<br />
                  <code class="agent-cmd-block">MobTestAgent.exe --base-url {{ agentPlatformBaseUrl || 'http://服务器IP:5000' }}</code>
                  <span v-if="agentPlatformBaseUrl" class="agent-copy-url-wrap">（平台地址由管理员在 .env 中配置）</span>
                </li>
                <li>运行成功后，在本页点击 <strong>「绑定本机」</strong> 完成绑定；未自动绑定时会显示 6 位绑定码，在本机执行 <code>MobTestAgent.exe --base-url 平台地址 --bind-code 绑定码</code>。</li>
              </ol>
              <p v-if="!agentDownloadAvailable" class="agent-guide-unavailable">
                当前无法下载 Agent，请管理员将 MobTestAgent.exe 放入服务器 agent/dist/ 目录后刷新本页。
              </p>
            </template>
          </div>
        </div>

        <div v-if="(!isPlatformHost || !agentCanLaunch) && agentDownloadAvailable" class="agent-config-section agent-config-download-row">
          <el-button
            type="primary"
            :loading="agentDownloading"
            class="agent-download-btn"
            @click="doDownloadAgentWithPicker"
          >
            <el-icon><Download /></el-icon>
            下载 Agent
          </el-button>
          <p class="agent-config-download-tip">点击后选择保存位置</p>
        </div>

        <div class="agent-config-section agent-config-actions-wrap">
          <div class="agent-config-section-title">操作</div>
          <div class="agent-config-actions-btns">
            <template v-if="isPlatformHost && agentCanLaunch">
              <el-button type="primary" :loading="agentLaunchLoading" @click="doPlatformLaunchAgent">启动 Agent</el-button>
            </template>
            <template v-if="!agentBinding?.bound">
              <el-button type="primary" @click="openBindDialog">绑定本机</el-button>
            </template>
            <template v-else>
              <el-button type="default" @click="confirmUnbind">解绑</el-button>
            </template>
            <el-button type="default" @click="agentCleanVisible = true">清理本机 Agent</el-button>
          </div>
          <p v-if="isPlatformHost && agentCanLaunch" class="agent-config-launch-tip">在本机启动并自动绑定当前用户</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="agentConfigVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 清理本机 Agent 弹窗 -->
    <el-dialog
      v-model="agentCleanVisible"
      title="清理本机 Agent"
      width="480px"
      destroy-on-close
      class="agent-clean-dialog"
    >
      <p class="agent-clean-desc">
        将解除平台绑定并清理本机 Agent 数据（协议注册与本地配置文件）。若本机正在运行 Agent，将自动执行清理并退出程序。
      </p>
      <p class="agent-clean-tip">
        清理后若需再用，重新下载并运行 Agent 后绑定即可。
      </p>
      <template #footer>
        <el-button @click="agentCleanVisible = false">取消</el-button>
        <el-button type="primary" :loading="agentCleanLoading" @click="doAgentClean">
          解绑并清理
        </el-button>
      </template>
    </el-dialog>

    <!-- 绑定码弹窗 -->
    <el-dialog
      v-model="bindingCodeVisible"
      title="绑定本机 Agent"
      width="420px"
      destroy-on-close
      @close="bindingCode = ''"
  >
      <p class="binding-tip">本机未检测到 Agent 或一键绑定未成功时，可在本机运行 Agent 时加参数 <code>--bind-code 下方绑定码</code> 完成绑定。</p>
      <div class="binding-code-box">
        <span class="binding-code">{{ bindingCode || '------' }}</span>
      </div>
      <p v-if="bindingCodeExpiresAt" class="binding-expire">绑定码 {{ bindingCodeExpiresAt }} 前有效</p>
      <template #footer>
        <el-button @click="bindingCodeVisible = false">关闭</el-button>
      </template>
    </el-dialog>

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
                  v-if="row.canOperate && row.status === 'offline' && row.wifi"
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
                  v-if="row.canOperate"
                  :ref="getMirrorActionRefs"
                  v-bind="{
                    row,
                    toggleRowExpansion,
                    isOnline: row.status === 'online',
                  }"
                />
                <span v-else class="device-view-only-hint">—</span>
              </div>

              <div class="flex-1 flex justify-center">
                <MoreDropdown
                  v-if="row.canOperate"
                  v-bind="{
                    row,
                    toggleRowExpansion,
                    isOnline: row.status === 'online',
                  }"
                />
                <span v-else class="device-view-only-hint">—</span>
              </div>

              <div class="flex-1 flex justify-center">
                <WirelessAction
                  v-if="row.canOperate"
                  v-bind="{
                    row,
                    handleConnect,
                    handleRefresh: refreshDevices,
                    isOnline: row.status === 'online',
                  }"
                />
                <span v-else class="device-view-only-hint">—</span>
              </div>

              <div class="flex-1 flex justify-center">
                <RemoveAction
                  v-if="row.canOperate && row.status === 'offline'"
                  v-bind="{
                    device: row,
                    handleRefresh: refreshDevices,
                  }"
                />
                <span v-else-if="!row.canOperate" class="device-view-only-hint">—</span>
              </div>
            </div>
            <span v-if="row.canOperate === false" class="device-view-only-hint">（该设备由其他用户 Agent 连接，仅可查看）</span>
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
                :disabled="!row.canOperate"
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
  Operation,
  Delete,
  Setting,
  ArrowDown,
} from "@element-plus/icons-vue";
import deviceApi from "@/api/device";
import userApi from "@/api/user";
import agentApi from "@/api/agent";
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

const agentBinding = ref(null);
const agentBindingLoaded = ref(false);
const agentBindingRefreshing = ref(false);
const bindingCodeVisible = ref(false);
const bindingCode = ref("");
const bindingCodeExpiresAt = ref("");
const agentConfigVisible = ref(false);
const agentCleanVisible = ref(false);
const agentCleanLoading = ref(false);
// 本机 Agent 是否在运行（通过 127.0.0.1:8765/status 检测）
const agentRunningLocally = ref(false);
const AGENT_LOCAL_STATUS_URL = 'http://127.0.0.1:8765/status';
const AGENT_LOCAL_BIND_URL_PREFIX = 'http://127.0.0.1:8765/bind?token=';
const AGENT_LOCAL_CLEAN_URL = 'http://127.0.0.1:8765/clean';
const AUTO_BIND_POLL_INTERVAL_MS = 10000;
const AUTO_BIND_PAUSE_AFTER_FAILS = 5;
const AUTO_BIND_PAUSE_MS = 60000;
const AGENT_LAUNCH_PROTOCOL = 'mobtestagent://start';
// 下载 Agent 安装包：路径可选，未配置时后端不可用
const agentDownloadAvailable = ref(false);
const agentDownloadFilename = ref('MobTestAgent.exe');
const agentDownloadUrl = '/api/agent/download';
// 是否支持由平台在服务器本机启动 Agent（服务器已配置 exe）
const agentCanLaunch = ref(false);
// 当前访问是否来自部署平台的本机
const isPlatformHost = ref(false);
// 是否显示「本机 Agent」入口：仅远程访问时显示；本机（部署机）= 访问端即部署机，直接用服务器 adb，不需要 Agent
const showAgentConfigEntry = computed(() => agentBindingLoaded.value && !isPlatformHost.value);
// 平台地址（供使用方式展示，由后端 .env AGENT_PLATFORM_BASE_URL 配置）
const agentPlatformBaseUrl = ref('');
const agentLaunchLoading = ref(false);
// 使用方式内容是否收起
const agentUsageCollapsed = ref(false);

let autoBindPollingTimer = null;
let autoBindFailCount = 0;
let lastAutoBindSuccessToast = 0;
const AUTO_BIND_TOAST_DEBOUNCE_MS = 5000;
const autoBindInProgress = ref(false);

async function probeAgentLocal() {
  try {
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), 2500);
    const r = await fetch(AGENT_LOCAL_STATUS_URL, { signal: ctrl.signal });
    clearTimeout(t);
    const json = await r.json().catch(() => ({}));
    agentRunningLocally.value = r.ok && (json?.status === 'ok');
  } catch {
    agentRunningLocally.value = false;
  }
}

async function fetchAgentDownloadInfo() {
  try {
    const res = await agentApi.getAgentDownloadInfo();
    const d = res.data || {};
    agentDownloadAvailable.value = !!d.available;
    if (d.filename) agentDownloadFilename.value = d.filename;
  } catch {
    agentDownloadAvailable.value = false;
  }
}

const agentDownloading = ref(false);
/** 通过“另存为”下载 Agent，用户选择保存位置；保存后提示将路径填到「Agent 存放位置」（浏览器不暴露保存路径，无法自动回填） */
async function doDownloadAgentWithPicker() {
  if (!agentDownloadAvailable.value) return;
  if (typeof window.showSaveFilePicker !== 'function') {
    const a = document.createElement('a');
    a.href = agentDownloadUrl;
    a.download = agentDownloadFilename.value;
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    return;
  }
  agentDownloading.value = true;
  try {
    const fileHandle = await window.showSaveFilePicker({
      suggestedName: agentDownloadFilename.value,
      types: [{ description: '可执行文件', accept: { 'application/octet-stream': ['.exe'] } }],
      startIn: 'downloads',
    });
    const res = await fetch(agentDownloadUrl, { credentials: 'include' });
    if (!res.ok) throw new Error(res.statusText);
    const blob = await res.blob();
    const writable = await fileHandle.createWritable();
    await writable.write(blob);
    await writable.close();
    ElMessage.success('已保存。因浏览器安全限制无法自动获取保存路径，请将保存目录粘贴到上方「Agent 存放位置」便于下次一键复制启动命令。');
  } catch (e) {
    if (e?.name === 'AbortError') return;
    ElMessage.error(e?.message || '下载失败');
    const a = document.createElement('a');
    a.href = agentDownloadUrl;
    a.download = agentDownloadFilename.value;
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  } finally {
    agentDownloading.value = false;
  }
}

function openAgentProtocol() {
  window.location.href = AGENT_LAUNCH_PROTOCOL;
}

async function fetchAgentLaunchInfo() {
  try {
    const res = await agentApi.getAgentLaunchInfo();
    agentCanLaunch.value = !!res.data?.can_launch;
    isPlatformHost.value = !!res.data?.is_platform_host;
    agentPlatformBaseUrl.value = (res.data?.platform_base_url || '').trim();
  } catch {
    agentCanLaunch.value = false;
    isPlatformHost.value = false;
    agentPlatformBaseUrl.value = '';
  }
}

async function doPlatformLaunchAgent() {
  agentLaunchLoading.value = true;
  try {
    const res = await agentApi.launchAgent();
    const data = res.data || {};
    if (data.success && data.bound) {
      agentRunningLocally.value = true;
      agentBinding.value = { bound: true, agent_online: true, binding: {} };
      await fetchAgentBinding();
      ElMessage.success(data.message || 'Agent 已启动并已绑定');
    }
  } catch (e) {
    const msg = e?.response?.data?.message || e?.message || '启动失败';
    ElMessage.error(msg);
  } finally {
    agentLaunchLoading.value = false;
  }
}

let agentBindingPollTimer = null;
const AGENT_BINDING_POLL_MS = 12000; // 弹窗打开时每 12 秒刷新一次绑定状态，便于关闭 Agent 后状态更新
async function onAgentConfigOpen() {
  fetchAgentDownloadInfo();
  fetchAgentLaunchInfo();
  await fetchAgentBinding();
  if (agentBindingPollTimer) clearInterval(agentBindingPollTimer);
  agentBindingPollTimer = setInterval(() => {
    if (!agentConfigVisible.value) {
      if (agentBindingPollTimer) clearInterval(agentBindingPollTimer);
      agentBindingPollTimer = null;
      return;
    }
    fetchAgentBinding();
  }, AGENT_BINDING_POLL_MS);
}
function onAgentConfigClose() {
  if (agentBindingPollTimer) {
    clearInterval(agentBindingPollTimer);
    agentBindingPollTimer = null;
  }
}

function stopAutoBindPolling() {
  if (autoBindPollingTimer) {
    clearTimeout(autoBindPollingTimer);
    autoBindPollingTimer = null;
  }
}

function startAutoBindPolling() {
  if (autoBindPollingTimer) return;
  if (agentBinding.value?.bound) return;
  if (!agentConfigVisible.value) return;
  function schedule() {
    if (!agentConfigVisible.value) return;
    tryAutoBind().then(() => {
      if (agentBinding.value?.bound || !agentConfigVisible.value) return;
      autoBindPollingTimer = setTimeout(schedule, AUTO_BIND_POLL_INTERVAL_MS);
    });
  }
  autoBindPollingTimer = setTimeout(schedule, AUTO_BIND_POLL_INTERVAL_MS);
}

async function tryAutoBind() {
  if (!agentConfigVisible.value || agentBinding.value?.bound || autoBindInProgress.value) return;
  if (autoBindFailCount >= AUTO_BIND_PAUSE_AFTER_FAILS) {
    stopAutoBindPolling();
    autoBindFailCount = 0;
    autoBindPollingTimer = setTimeout(() => {
      autoBindPollingTimer = null;
      startAutoBindPolling();
    }, AUTO_BIND_PAUSE_MS);
    return;
  }
  try {
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), 2500);
    const r = await fetch(AGENT_LOCAL_STATUS_URL, { signal: ctrl.signal });
    clearTimeout(t);
    const json = await r.json().catch(() => ({}));
    if (!r.ok || json?.status !== 'ok') {
      autoBindFailCount += 1;
      return;
    }
  } catch {
    autoBindFailCount += 1;
    return;
  }
  autoBindFailCount = 0;
  autoBindInProgress.value = true;
  try {
    const res = await agentApi.createBindingCode();
    const data = res.data || {};
    const bindToken = data.binding_token;
    if (!bindToken) return;
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), 4000);
    const r = await fetch(
      `${AGENT_LOCAL_BIND_URL_PREFIX}${encodeURIComponent(bindToken)}`,
      { method: 'GET', signal: ctrl.signal },
    );
    clearTimeout(t);
    const result = await r.json().catch(() => ({}));
    if (result && result.success) {
      stopAutoBindPolling();
      agentRunningLocally.value = true;
      // 乐观更新：先让配置页立即显示已绑定，再拉服务端状态覆盖（避免 get_binding 延迟/失败导致仍显示未绑定）
      agentBinding.value = { bound: true, agent_online: true, binding: {} };
      try {
        await fetchAgentBinding();
      } catch (_) {
        // 保留乐观状态，不置空
      }
      const now = Date.now();
      if (now - lastAutoBindSuccessToast >= AUTO_BIND_TOAST_DEBOUNCE_MS) {
        lastAutoBindSuccessToast = now;
        ElMessage.success('本机 Agent 已自动绑定');
      }
    }
  } catch (_) {
    // createBindingCode 失败（如 500）时也计为失败，避免疯狂重试
    autoBindFailCount += 1;
  } finally {
    autoBindInProgress.value = false;
  }
}

async function fetchAgentBinding() {
  try {
    const res = await agentApi.getAgentBinding();
    const data = res.data;
    agentBinding.value = data?.bound !== undefined ? { ...data } : null;
  } catch (e) {
    if (!agentBinding.value?.bound) {
      agentBinding.value = null;
    }
  } finally {
    agentBindingLoaded.value = true;
    if (agentBinding.value?.bound) {
      stopAutoBindPolling();
    } else {
      startAutoBindPolling();
    }
  }
}
function getAgentBindingStateText() {
  const b = agentBinding.value;
  if (b?.bound && b?.agent_online) return '已绑定 · Agent 已连接';
  if (b?.bound) return '已绑定 · Agent 未连接';
  return '未绑定';
}
async function refreshAgentBinding() {
  agentBindingRefreshing.value = true;
  try {
    await fetchAgentBinding();
    ElMessage.success('已刷新，当前状态：' + getAgentBindingStateText());
  } finally {
    agentBindingRefreshing.value = false;
  }
}
async function openBindDialog() {
  try {
    const res = await agentApi.createBindingCode();
    const data = res.data || {};
    const bindToken = data.binding_token;
    if (bindToken) {
      try {
        const ctrl = new AbortController();
        const t = setTimeout(() => ctrl.abort(), 4000);
        const r = await fetch(
          `${AGENT_LOCAL_BIND_URL_PREFIX}${encodeURIComponent(bindToken)}`,
          { method: "GET", signal: ctrl.signal },
        );
        clearTimeout(t);
        const json = await r.json();
        if (json && json.success) {
          agentRunningLocally.value = true;
          agentBinding.value = { bound: true, agent_online: true, binding: {} };
          try {
            await fetchAgentBinding();
          } catch (_) {}
          ElMessage.success("绑定成功");
          return;
        }
      } catch (_) {
        // 本机未运行 Agent 或请求失败，展示绑定码兜底
      }
    }
    bindingCode.value = data.code || "";
    const exp = data.expires_at;
    bindingCodeExpiresAt.value = exp ? new Date(exp).toLocaleString("zh-CN") : "";
    bindingCodeVisible.value = true;
  } catch (e) {
    ElMessage.error(e.response?.data?.message || "获取绑定码失败");
  }
}
function closeBindingDialog() {
  bindingCodeVisible.value = false;
  bindingCode.value = "";
}

async function doAgentClean() {
  agentCleanLoading.value = true;
  try {
    try {
      await agentApi.unbindAgent();
    } catch (e) {
      const msg = e?.response?.data?.message || '';
      if (msg && !msg.includes('未绑定')) ElMessage.warning(msg);
    }
    let localCleaned = false;
    try {
      const ctrl = new AbortController();
      const t = setTimeout(() => ctrl.abort(), 5000);
      const r = await fetch(AGENT_LOCAL_CLEAN_URL, { signal: ctrl.signal });
      clearTimeout(t);
      if (r.ok) localCleaned = true;
    } catch (_) {
      // 本机未运行 Agent 或请求失败
    }
    if (localCleaned) {
      ElMessage.success('平台已解绑；本机 Agent 已执行清理并退出。');
    } else {
      ElMessage.success('平台已解绑。本机未检测到运行中的 Agent，若曾安装过 Agent，请手动运行 clean_agent.bat 或 MobTestAgent.exe --clean 完成本机清理。');
    }
    agentCleanVisible.value = false;
    fetchAgentBinding();
    probeAgentLocal();
  } catch (e) {
    ElMessage.error(e?.message || '操作失败');
  } finally {
    agentCleanLoading.value = false;
  }
}

async function confirmUnbind() {
  try {
    await ElMessageBox.confirm("确定解除与本机 Agent 的绑定吗？", "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    });
    await agentApi.unbindAgent();
    ElMessage.success("已解绑");
    agentBinding.value = null;
    fetchAgentBinding();
  } catch (e) {
    if (e !== "cancel") ElMessage.error(e.response?.data?.message || "解绑失败");
  }
}

const route = useRoute();
const router = useRouter();

const openDeviceDetail = (row) => {
  deviceDetailRow.value = row;
  deviceDetailDialogVisible.value = true;
};
const { proxy } = getCurrentInstance();

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
    let adbDevices = [];
    try {
      const adbResponse = await deviceApi.getAdbDevices();
      adbDevices = adbResponse.data?.devices || [];
    } catch (adbErr) {
      // Agent 未响应或未绑定时使用空列表，仍展示数据库中的设备数据
      console.warn('获取 Agent 设备列表失败，仅展示数据库设备:', adbErr?.response?.data?.message || adbErr?.message);
    }

    const dbResponse = await deviceApi.getDeviceList({ page: 1, size: 1000 });
    const dbDevices = dbResponse.data.devices || [];

    const adbDeviceMap = new Map();
    adbDevices.forEach((adbDevice) => {
      adbDeviceMap.set(adbDevice.id, adbDevice);
    });

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

    const dbDeviceIdSet = new Set(dbDevices.map((db) => db.device_id));
    for (const adbDevice of adbDevices) {
      if (!dbDeviceIdSet.has(adbDevice.id) && adbDevice.status === "device") {
        try {
          await deviceApi.createDevice({
            device_name: adbDevice.name || adbDevice.id,
            device_model: adbDevice.name || "Unknown",
            os_type: "android",
            os_version: "Unknown",
            device_id: adbDevice.id,
            status: "online",
          });
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
    const dbDeviceIdSetAfter = new Set(dbDevicesAfterCreate.map((d) => d.device_id));
    // 全部设备均展示；仅当前用户 Agent 连接的设备可操作（canOperate），其他设备仅可查看
    const mergedFromDb = await Promise.all(
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
          status: adbDevice ? "online" : dbDevice.status,
          wifi: adbDevice ? adbDevice.wifi : false,
          battery: batteryInfo,
          owner_id: dbDevice.owner_id,
          owner_name: dbDevice.owner_name,
          db_id: dbDevice.id,
          canOperate: !!adbDevice,
        };
      }),
    );
    // 当前用户 Agent 已连接但尚未入库的设备也展示，避免「连接了设备却看不到」
    const adbOnlyDevices = adbDevices
      .filter((adb) => adb.status === "device" && !dbDeviceIdSetAfter.has(adb.id))
      .map((adb) => ({
        id: adb.id,
        device_id: adb.id,
        name: adb.name || adb.id,
        device_model: adb.name || "Unknown",
        os_type: "android",
        os_version: "Unknown",
        status: "online",
        wifi: !!adb.wifi,
        battery: null,
        owner_id: null,
        owner_name: null,
        db_id: null,
        canOperate: true,
      }));
    const mergedDevices = [...mergedFromDb, ...adbOnlyDevices];

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

watch(agentConfigVisible, (visible) => {
  if (!visible) stopAutoBindPolling();
});

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

let removeVisibilityListener = () => {};

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
  fetchAgentLaunchInfo(); // 先区分是否本机，再决定是否展示「本机 Agent」入口
  fetchAgentBinding();
  // 不在挂载时请求 8765/status，避免未运行 Agent 时控制台刷 ERR_CONNECTION_REFUSED；改为打开「本机 Agent」配置弹窗时再探测

  const handler = () => {
    if (document.visibilityState === "visible") {
      if (agentConfigVisible.value) {
        probeAgentLocal();
        fetchAgentDownloadInfo();
      }
    }
  };
  document.addEventListener("visibilitychange", handler);
  removeVisibilityListener = () => document.removeEventListener("visibilitychange", handler);
});

onUnmounted(() => {
  removeVisibilityListener();
  stopAutoRefresh();
  stopAutoBindPolling();
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

.agent-config-content {
  padding: 0 4px;
}
.agent-config-status-card {
  margin-bottom: 20px;
  padding: 14px 16px;
  background: var(--el-fill-color-lighter);
  border-radius: 8px;
}
.agent-config-status-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.agent-refresh-binding-btn {
  margin-left: 8px;
}
.device-view-only-hint {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  display: block;
  margin-top: 4px;
}
.agent-config-status-label {
  font-size: 14px;
  color: var(--el-text-color-regular);
  min-width: 72px;
}
.agent-config-status-hint {
  margin: 8px 0 0;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  line-height: 1.4;
}
.agent-config-section {
  margin-bottom: 16px;
}
.agent-config-section-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 8px;
}
.agent-config-usage-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  user-select: none;
  margin-bottom: 8px;
}
.agent-config-usage-header .agent-config-section-title {
  margin-bottom: 0;
}
.agent-usage-toggle {
  transition: transform 0.2s;
}
.agent-usage-toggle.agent-usage-collapsed {
  transform: rotate(-90deg);
}
.agent-config-usage-desc {
  margin: 0 0 8px;
  font-size: 13px;
  color: var(--el-text-color-regular);
  line-height: 1.5;
}
.agent-config-usage-steps {
  margin: 0;
  padding-left: 20px;
  font-size: 13px;
  color: var(--el-text-color-regular);
  line-height: 1.6;
}
.agent-config-usage-steps li {
  margin-bottom: 4px;
}
.agent-config-usage-steps code {
  padding: 1px 6px;
  background: var(--el-fill-color);
  border-radius: 4px;
  font-size: 12px;
}
.agent-config-usage-steps code.agent-cmd-block {
  display: inline-block;
  max-width: 100%;
  padding: 6px 10px;
  margin: 4px 0;
  word-break: break-all;
}
.agent-copy-url-wrap {
  display: inline;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
.agent-config-download-row {
  margin-bottom: 16px;
}
.agent-config-download-row .agent-download-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.agent-config-download-tip {
  margin: 8px 0 0;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  line-height: 1.4;
}
.agent-config-actions-wrap {
  margin-bottom: 0;
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color-lighter);
}
.agent-config-actions-btns {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}
.agent-config-actions-wrap .agent-config-launch-tip {
  margin: 10px 0 0;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  line-height: 1.4;
}
.agent-guide-unavailable {
  margin: 0;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.agent-clean-desc {
  margin: 0 0 12px;
  color: var(--el-text-color-regular);
  font-size: 14px;
  line-height: 1.6;
}
.agent-clean-tip {
  margin: 0;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.binding-tip {
  margin: 0 0 12px;
  color: var(--el-text-color-regular);
  font-size: 14px;
}
.binding-code-box {
  text-align: center;
  padding: 16px;
  background: var(--el-fill-color-light);
  border-radius: 8px;
  margin-bottom: 8px;
}
.binding-code {
  font-size: 28px;
  font-weight: 600;
  letter-spacing: 8px;
  color: var(--el-color-primary);
}
.binding-expire {
  margin: 0;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.agent-guide-content {
  padding: 0 8px;
}
.agent-guide-intro {
  margin: 0 0 20px;
  color: var(--el-text-color-regular);
  font-size: 14px;
  line-height: 1.6;
}
.agent-guide-steps {
  margin-bottom: 16px;
}
.agent-guide-steps :deep(.el-step__description) {
  padding-right: 0;
}
.agent-guide-steps p {
  margin: 4px 0 8px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  line-height: 1.5;
}
.agent-guide-steps p:last-child {
  margin-bottom: 0;
}
.agent-guide-download-wrap {
  margin: 12px 0 0;
}
.agent-download-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--el-color-primary);
  color: #fff;
  border-radius: var(--el-border-radius-base);
  text-decoration: none;
  font-size: 14px;
  transition: opacity 0.2s;
}
.agent-download-btn:hover {
  color: #fff;
  opacity: 0.9;
}
.agent-guide-unavailable {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}
.agent-guide-tip {
  color: var(--el-color-info);
  font-size: 12px;
}
.binding-tip code,
.agent-guide-steps code {
  padding: 1px 6px;
  background: var(--el-fill-color);
  border-radius: 4px;
  font-size: 12px;
}
.agent-guide-cmd {
  margin: 8px 0;
  padding: 10px 12px;
  background: var(--el-fill-color-dark);
  border-radius: 6px;
  font-size: 12px;
  line-height: 1.5;
  overflow-x: auto;
}
.agent-guide-footer {
  margin: 0;
  padding: 12px;
  background: var(--el-fill-color-light);
  border-radius: 6px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
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
