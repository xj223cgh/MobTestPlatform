<template>
  <div class="test-task-management">
    <div class="filter-section">
      <el-form
        :inline="true"
        :model="filterForm"
        class="filter-form"
      >
        <el-form-item label="搜索">
          <el-input
            v-model="filterForm.search"
            placeholder="任务名称/描述"
            clearable
            style="width: 180px"
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="filterForm.status"
            placeholder="全部状态"
            clearable
            style="width: 120px"
            @change="handleSearch"
          >
            <el-option
              label="待执行"
              value="pending"
            />
            <el-option
              label="执行中"
              value="running"
            />
            <el-option
              label="已暂停"
              value="paused"
            />
            <el-option
              label="已完成"
              value="completed"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select
            v-model="filterForm.priority"
            placeholder="全部优先级"
            clearable
            style="width: 120px"
            @change="handleSearch"
          >
            <el-option
              label="高"
              value="high"
            />
            <el-option
              label="中"
              value="medium"
            />
            <el-option
              label="低"
              value="low"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="负责人">
          <el-select
            v-model="filterForm.executor_id"
            placeholder="全部负责人"
            clearable
            filterable
            style="width: 140px"
            @change="handleSearch"
          >
            <el-option
              v-for="u in userOptions"
              :key="u.id"
              :label="u.real_name"
              :value="u.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            @click="handleSearch"
          >
            搜索
          </el-button>
          <el-button @click="handleReset">
            重置
          </el-button>
        </el-form-item>
        <el-form-item style="margin-left: auto">
          <el-button
            circle
            title="刷新任务列表"
            @click="loadTasks"
          >
            <el-icon><Refresh /></el-icon>
          </el-button>
          <el-button
            type="primary"
            @click="handleCreate"
          >
            <el-icon><Plus /></el-icon>
            创建任务
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 任务类型选项卡 -->
    <div class="task-tabs-section">
      <el-tabs
        v-model="activeTab"
        class="task-tabs"
        @tab-change="handleTabChange"
      >
        <!-- 测试用例任务 -->
        <el-tab-pane
          label="测试用例任务"
          name="test_case"
        >
          <div class="table-section">
            <div class="table-scroll-viewport">
              <el-table
                v-loading="loading.testCase"
                :data="taskList.testCase"
              stripe
              border
              style="width: 100%"
              fit
            >
              <el-table-column
                prop="task_name"
                label="任务名称"
                min-width="150"
                show-overflow-tooltip
                align="center"
              />
              <el-table-column
                prop="executor_name"
                label="负责人"
                width="100"
                show-overflow-tooltip
                align="center"
              >
                <template #default="{ row }">
                  {{ row.executor_name || "-" }}
                </template>
              </el-table-column>
              <el-table-column
                prop="priority"
                label="优先级"
                width="75"
                align="center"
              >
                <template #default="{ row }">
                  <el-tag
                    :type="getPriorityType(row.priority)"
                    size="small"
                  >
                    {{ getPriorityText(row.priority) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column
                prop="status"
                label="状态"
                width="85"
                align="center"
              >
                <template #default="{ row }">
                  <el-tag
                    :type="getStatusType(row.status)"
                    size="small"
                  >
                    {{ getStatusText(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column
                label="计划时间"
                width="180"
                align="center"
              >
                <template #default="{ row }">
                  <div
                    v-if="row.scheduled_time || row.scheduled_end_time"
                    class="time-range"
                  >
                    <div class="time-item">
                      <span class="time-label">开始:</span>
                      <span class="time-value">{{
                        formatDateTime(row.scheduled_time)
                      }}</span>
                    </div>
                    <div class="time-item">
                      <span class="time-label">结束:</span>
                      <span class="time-value">{{
                        formatDateTime(row.scheduled_end_time)
                      }}</span>
                    </div>
                  </div>
                  <span
                    v-else
                    class="no-data"
                  >-</span>
                </template>
              </el-table-column>
              <el-table-column
                label="统计"
                width="280"
                align="center"
              >
                <template #default="{ row }">
                  <div
                    v-if="row.statistics"
                    class="stats-mini"
                  >
                    <div class="stats-header">
                      <span class="stats-rate">
                        <span class="stats-label">通过率:</span>
                        <span
                          class="stats-percentage"
                          :style="{
                            color: getProgressColor(row.statistics.pass_rate),
                          }"
                        >
                          {{ row.statistics.pass_rate }}%
                        </span>
                      </span>
                      <span class="stats-total">总数: {{ row.statistics.total_cases }}</span>
                    </div>
                    <el-progress
                      :percentage="row.statistics.pass_rate"
                      :color="getProgressColor(row.statistics.pass_rate)"
                      :stroke-width="6"
                      :show-text="false"
                    />
                    <div class="stats-detail">
                      <div class="stats-item pass">
                        <span class="item-label">通过</span>
                        <span class="item-value">{{
                          row.statistics.pass_count
                        }}</span>
                      </div>
                      <div class="stats-item fail">
                        <span class="item-label">失败</span>
                        <span class="item-value">{{
                          row.statistics.fail_count
                        }}</span>
                      </div>
                      <div class="stats-item blocked">
                        <span class="item-label">阻塞</span>
                        <span class="item-value">{{
                          row.statistics.blocked_count
                        }}</span>
                      </div>
                      <div class="stats-item not-applicable">
                        <span class="item-label">不适用</span>
                        <span class="item-value">{{
                          row.statistics.not_applicable_count
                        }}</span>
                      </div>
                      <div class="stats-item not-executed">
                        <span class="item-label">未执行</span>
                        <span class="item-value">{{
                          row.statistics.not_executed
                        }}</span>
                      </div>
                    </div>
                  </div>
                  <span
                    v-else
                    class="no-data"
                  >-</span>
                </template>
              </el-table-column>
              <el-table-column
                label="操作"
                width="190"
                fixed="right"
                align="center"
              >
                <template #default="{ row }">
                  <el-button
                    v-if="row.status === 'pending'"
                    size="small"
                    circle
                    title="开始执行"
                    @click="handleExecute(row)"
                  >
                    <el-icon color="#67c23a">
                      <VideoPlay />
                    </el-icon>
                  </el-button>
                  <el-button
                    v-if="row.status === 'running'"
                    size="small"
                    circle
                    title="继续执行"
                    @click="handleExecute(row)"
                  >
                    <el-icon color="#409eff">
                      <VideoPlay />
                    </el-icon>
                  </el-button>
                  <el-button
                    v-if="row.status === 'running'"
                    size="small"
                    circle
                    title="终止"
                    @click="handleStopTask(row)"
                  >
                    <el-icon color="#f56c6c">
                      <VideoPause />
                    </el-icon>
                  </el-button>
                  <el-button
                    v-if="row.status === 'completed'"
                    size="small"
                    circle
                    title="重新执行"
                    @click="handleReExecute(row)"
                  >
                    <el-icon color="#409eff">
                      <RefreshRight />
                    </el-icon>
                  </el-button>
                  <el-button
                    v-if="row.status === 'completed'"
                    size="small"
                    circle
                    title="生成报告"
                    @click="handleGenerateReport(row)"
                  >
                    <el-icon color="#409eff">
                      <Document />
                    </el-icon>
                  </el-button>
                  <el-button
                    size="small"
                    circle
                    title="详情"
                    @click="handleView(row)"
                  >
                    <el-icon color="#909399">
                      <View />
                    </el-icon>
                  </el-button>
                  <el-button
                    size="small"
                    circle
                    title="删除"
                    @click="handleDelete(row)"
                  >
                    <el-icon color="#f56c6c">
                      <Delete />
                    </el-icon>
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            </div>

            <div class="pagination-container">
              <el-pagination
                :current-page="pagination.testCase.page"
                :page-size="pagination.testCase.size"
                :total="pagination.testCase.total"
                layout="total, prev, pager, next, jumper"
                @current-change="(page) => handlePageChange(page, 'testCase')"
              />
            </div>
          </div>
        </el-tab-pane>

        <!-- 设备脚本任务 -->
        <el-tab-pane
          label="设备脚本任务"
          name="device_script"
        >
          <div class="table-section">
            <div class="table-scroll-viewport">
              <el-table
                v-loading="loading.deviceScript"
                :data="taskList.deviceScript"
              stripe
              border
              style="width: 100%"
              fit
            >
              <el-table-column
                prop="task_name"
                label="任务名称"
                min-width="180"
                show-overflow-tooltip
                align="center"
              />
              <el-table-column
                prop="executor_name"
                label="负责人"
                width="180"
                show-overflow-tooltip
                align="center"
              >
                <template #default="{ row }">
                  {{ row.executor_name || "-" }}
                </template>
              </el-table-column>
              <el-table-column
                prop="priority"
                label="优先级"
                width="100"
                align="center"
              >
                <template #default="{ row }">
                  <el-tag
                    :type="getPriorityType(row.priority)"
                    size="small"
                  >
                    {{ getPriorityText(row.priority) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column
                prop="status"
                label="状态"
                width="110"
                align="center"
              >
                <template #default="{ row }">
                  <el-tag
                    :type="getStatusType(row.status)"
                    size="small"
                  >
                    {{ getStatusText(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column
                prop="script_file"
                label="脚本文件"
                min-width="150"
                align="center"
              >
                <template #default="{ row }">
                  <template v-if="row.script_file">
                    <div class="script-file-link-wrapper">
                      <a
                        class="script-file-link"
                        @click.prevent="handleDownloadScript(row)"
                      >
                        <el-icon><Download /></el-icon>
                        <span>{{ row.script_file }}</span>
                      </a>
                    </div>
                  </template>
                  <span
                    v-else
                    class="no-data"
                  >-</span>
                </template>
              </el-table-column>
              <el-table-column
                label="计划时间"
                width="220"
                align="center"
              >
                <template #default="{ row }">
                  <div
                    v-if="row.scheduled_time || row.scheduled_end_time"
                    class="time-range"
                  >
                    <div class="time-item">
                      <span class="time-label">开始:</span>
                      <span class="time-value">{{
                        formatDateTime(row.scheduled_time)
                      }}</span>
                    </div>
                    <div class="time-item">
                      <span class="time-label">结束:</span>
                      <span class="time-value">{{
                        formatDateTime(row.scheduled_end_time)
                      }}</span>
                    </div>
                  </div>
                  <span
                    v-else
                    class="no-data"
                  >-</span>
                </template>
              </el-table-column>
              <el-table-column
                label="操作"
                width="230"
                fixed="right"
                align="center"
              >
                <template #default="{ row }">
                  <el-button
                    v-if="row.status === 'pending'"
                    size="small"
                    circle
                    title="开始执行"
                    @click="handleExecute(row)"
                  >
                    <el-icon color="#67c23a">
                      <VideoPlay />
                    </el-icon>
                  </el-button>
                  <el-button
                    v-if="row.status === 'running'"
                    size="small"
                    circle
                    title="终止"
                    @click="handleStopTask(row)"
                  >
                    <el-icon color="#f56c6c">
                      <VideoPause />
                    </el-icon>
                  </el-button>
                  <el-button
                    v-if="row.status === 'completed'"
                    size="small"
                    circle
                    title="重新执行"
                    @click="handleReExecute(row)"
                  >
                    <el-icon color="#409eff">
                      <RefreshRight />
                    </el-icon>
                  </el-button>
                  <el-button
                    v-if="row.status === 'completed'"
                    size="small"
                    circle
                    title="生成报告"
                    @click="handleGenerateReport(row)"
                  >
                    <el-icon color="#409eff">
                      <Document />
                    </el-icon>
                  </el-button>
                  <el-button
                    size="small"
                    circle
                    title="详情"
                    @click="handleView(row)"
                  >
                    <el-icon color="#909399">
                      <View />
                    </el-icon>
                  </el-button>
                  <el-button
                    size="small"
                    circle
                    title="删除"
                    @click="handleDelete(row)"
                  >
                    <el-icon color="#f56c6c">
                      <Delete />
                    </el-icon>
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            </div>

            <div class="pagination-container">
              <el-pagination
                :current-page="pagination.deviceScript.page"
                :page-size="pagination.deviceScript.size"
                :total="pagination.deviceScript.total"
                layout="total, prev, pager, next, jumper"
                @current-change="
                  (page) => handlePageChange(page, 'deviceScript')
                "
              />
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <TaskDialog
      ref="taskDialogRef"
      @refresh="loadTasks"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  Plus,
  Search,
  VideoPlay,
  View,
  Delete,
  RefreshRight,
  VideoPause,
  Refresh,
  Download,
  Document,
} from "@element-plus/icons-vue";
import testTaskApi from "@/api/testTask";
import projectApi from "@/api/project";
import { getUserList } from "@/api/user";
import deviceApi from "@/api/device";
import { manualGenerateReport } from "@/api/report";
import TaskDialog from "./components/TaskDialog.vue";

const activeTab = ref("test_case");
const loading = reactive({
  testCase: false,
  deviceScript: false,
});
const taskList = reactive({
  testCase: [],
  deviceScript: [],
});
const userOptions = ref([]);
const taskDialogRef = ref(null);
const router = useRouter();
const route = useRoute();

const filterForm = reactive({
  search: "",
  status: "",
  priority: "",
  task_type: "",
  executor_id: "",
});

const pagination = reactive({
  testCase: {
    page: 1,
    size: 10,
    total: 0,
  },
  deviceScript: {
    page: 1,
    size: 10,
    total: 0,
  },
});

const getStatusType = (status) => {
  const typeMap = {
    pending: "info",
    running: "warning",
    paused: "warning",
    completed: "success",
  };
  return typeMap[status] || "info";
};

const getStatusText = (status) => {
  const textMap = {
    pending: "待执行",
    running: "执行中",
    paused: "已暂停",
    completed: "已完成",
  };
  return textMap[status] || status;
};

const getPriorityType = (priority) => {
  const typeMap = {
    high: "danger",
    medium: "warning",
    low: "info",
  };
  return typeMap[priority] || "info";
};

const getPriorityText = (priority) => {
  const textMap = {
    high: "高",
    medium: "中",
    low: "低",
  };
  return textMap[priority] || priority;
};

const getProgressColor = (percentage) => {
  if (percentage >= 80) return "#67c23a";
  if (percentage >= 60) return "#e6a23c";
  return "#f56c6c";
};

const formatDate = (dateString) => {
  if (!dateString) return "-";
  const date = new Date(dateString);
  return date.toLocaleString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const formatDateTime = (dateString) => {
  if (!dateString) return "-";
  const date = new Date(dateString);
  return date.toLocaleString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const loadTasks = async () => {
  // 加载测试用例任务
  loading.testCase = true;
  try {
    // 构建测试用例任务参数，确保 task_type 为 test_case，不被 filterForm 覆盖
    const testCaseParams = {
      ...filterForm,
      page: pagination.testCase.page,
      size: pagination.testCase.size,
      task_type: "test_case", // 放在后面，确保覆盖 filterForm 中的 task_type
    };

    const testCaseResponse = await testTaskApi.getTestTaskList(testCaseParams);
    taskList.testCase = testCaseResponse.data.test_tasks;
    pagination.testCase.total = testCaseResponse.data.pagination.total;
  } catch (error) {
    console.error("加载测试用例任务列表失败:", error);
    ElMessage.error("加载测试用例任务列表失败");
  } finally {
    loading.testCase = false;
  }

  // 加载设备脚本任务
  loading.deviceScript = true;
  try {
    // 构建设备脚本任务参数，确保 task_type 为 device_script，不被 filterForm 覆盖
    const deviceScriptParams = {
      ...filterForm,
      page: pagination.deviceScript.page,
      size: pagination.deviceScript.size,
      task_type: "device_script", // 放在后面，确保覆盖 filterForm 中的 task_type
    };

    const deviceScriptResponse =
      await testTaskApi.getTestTaskList(deviceScriptParams);
    taskList.deviceScript = deviceScriptResponse.data.test_tasks;
    pagination.deviceScript.total = deviceScriptResponse.data.pagination.total;
  } catch (error) {
    console.error("加载设备脚本任务列表失败:", error);
    ElMessage.error("加载设备脚本任务列表失败");
  } finally {
    loading.deviceScript = false;
  }
};

const loadUsers = async () => {
  try {
    const response = await getUserList({ page: 1, size: 1000 });
    userOptions.value = response.data?.items || response.data?.users || [];
  } catch (error) {
    console.error("加载用户列表失败:", error);
  }
};

const handleSearch = () => {
  pagination.testCase.page = 1;
  pagination.deviceScript.page = 1;
  loadTasks();
};

const handleReset = () => {
  Object.assign(filterForm, {
    search: "",
    status: "",
    priority: "",
    task_type: "",
    executor_id: "",
  });
  pagination.testCase.page = 1;
  pagination.deviceScript.page = 1;
  loadTasks();
};

const handleCreate = () => {
  taskDialogRef.value?.open();
};

const handleExecute = async (row) => {
  try {
    // 对于测试用例任务，在新标签页中打开用例执行页面
    if (row.task_type === "test_case") {
      const url = `${window.location.origin}/test-tasks/${row.id}/execute`;
      window.open(url, "_blank");
    } else {
      // 对于设备脚本任务，执行前检查设备连接状态
      if (row.status === 'pending' || row.status === 'completed') {
        // 获取任务关联的设备列表
        const taskDevicesResponse = await testTaskApi.getTaskDevices(row.id);
        const taskDevices = taskDevicesResponse.data?.devices || [];
        
        if (taskDevices.length === 0) {
          ElMessage.warning("任务未关联任何设备，无法执行");
          return;
        }
        
        // 检查设备连接状态
        let allDevicesConnected = true;
        const disconnectedDevices = [];
        
        for (const device of taskDevices) {
          try {
            const statusResponse = await deviceApi.getDeviceStatus(device.id);
            const deviceStatus = statusResponse.data?.status;
            if (deviceStatus !== 'connected') {
              allDevicesConnected = false;
              disconnectedDevices.push(device.device_name || device.device_id);
            }
          } catch (error) {
            // 设备状态检查失败，视为未连接
            allDevicesConnected = false;
            disconnectedDevices.push(device.device_name || device.device_id);
          }
        }
        
        if (!allDevicesConnected) {
          ElMessage.warning(`以下设备未连接，无法执行任务：${disconnectedDevices.join(', ')}`);
          return;
        }
        
        // 执行待执行或已完成的任务
        await testTaskApi.executeTestTask(row.id);
        ElMessage.success("测试任务开始执行");
        loadTasks();
        
        // 对于设备脚本任务，自动执行设备脚本
        if (row.task_type === "device_script") {
          try {
            // 根据脚本文件扩展名确定任务类型
            let taskType = "shell";
            if (row.script_file) {
              const fileExt = row.script_file.toLowerCase().split('.').pop();
              if (fileExt === "py") {
                taskType = "python";
              }
            }
            
            // 构建请求数据
            const requestData = {
              task_type: taskType, // 根据脚本文件扩展名确定任务类型
              command: row.command || "",
              task_id: row.id // 传递任务ID，以便后端在脚本执行完成后更新任务状态
            };
            
            // 如果有脚本文件，使用file_path
            if (row.file_path) {
              requestData.file_path = row.file_path;
              requestData.script_file = row.script_file;
            }
            
            // 执行设备脚本
            for (const device of taskDevices) {
              await deviceApi.executeDeviceTask(device.id, requestData);
            }
            
            ElMessage.success("设备脚本开始执行");
          } catch (error) {
            console.error("执行设备脚本失败:", error);
            ElMessage.error(
              "执行设备脚本失败：" + (error.response?.data?.message || error.message)
            );
          }
        }
      } else {
        ElMessage.warning("当前任务状态不支持此操作");
      }
    }
  } catch (error) {
    if (error !== "cancel") {
      console.error("执行测试任务失败:", error);
      ElMessage.error(
        "执行测试任务失败：" + (error.response?.data?.message || error.message),
      );
      
      // 如果是设备脚本任务，且任务状态为执行中，自动终止任务
      if (row.task_type === "device_script" && row.status === "running") {
        try {
          await testTaskApi.completeTestTask(row.id);
          ElMessage.success("任务已自动终止");
          loadTasks();
        } catch (stopError) {
          console.error("终止任务失败:", stopError);
        }
      }
    }
  }
};

const handleStopTask = async (row) => {
  try {
    await ElMessageBox.confirm("请选择要执行的操作：", "停止任务", {
      distinguishCancelAndClose: true,
      confirmButtonText: "结束任务",
      cancelButtonText: "取消操作",
      type: "warning",
    });

    await testTaskApi.completeTestTask(row.id);
    ElMessage.success("任务已结束");
    loadTasks();
  } catch (error) {
    if (error !== "cancel" && error !== "close") {
      console.error("停止任务失败:", error);
      ElMessage.error(
        "停止任务失败：" + (error.response?.data?.message || error.message),
      );
    }
  }
};

const handleReExecute = async (row) => {
  try {
    await testTaskApi.executeTestTask(row.id);
    ElMessage.success("任务已重置为待执行");
    loadTasks();
  } catch (error) {
    if (error !== "cancel") {
      console.error("重新执行任务失败:", error);
      ElMessage.error(
        "重新执行任务失败：" + (error.response?.data?.message || error.message),
      );
    }
  }
};

const handleGenerateReport = async (row) => {
  try {
    const res = await manualGenerateReport(row.id);
    if (res?.success && res?.data?.report_id) {
      ElMessage.success("报告已生成");
      router.push(`/report/record/${res.data.report_id}`);
    } else {
      ElMessage.error(res?.message || "生成报告失败");
    }
  } catch (e) {
    ElMessage.error(e?.response?.data?.message || e?.message || "生成报告失败");
  }
};

const handleView = (row) => {
  taskDialogRef.value?.open(row.id);
};

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      "确认删除该测试任务吗？删除后无法恢复！",
      "提示",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      },
    );

    await testTaskApi.deleteTestTask(row.id);
    ElMessage.success("测试任务删除成功");
    loadTasks();
  } catch (error) {
    if (error !== "cancel") {
      console.error("删除测试任务失败:", error);
      ElMessage.error(
        "删除测试任务失败：" + (error.response?.data?.message || error.message),
      );
    }
  }
};

// 下载脚本文件
const handleDownloadScript = (row) => {
  if (row.file_path) {
    // 构建完整的下载URL，包含原始文件名作为查询参数
    const downloadUrl = `/api/files/${row.file_path}?filename=${encodeURIComponent(row.script_file || "script_file")}`;


    // 创建下载链接并触发下载
    const a = document.createElement("a");
    a.href = downloadUrl;
    a.download = row.script_file || "script_file";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  } else {
    ElMessage.warning("脚本文件路径不存在");
  }
};

const handleSizeChange = (size, taskType) => {
  pagination[taskType].size = size;
  pagination[taskType].page = 1;
  loadTasks();
};

const handlePageChange = (page, taskType) => {
  pagination[taskType].page = page;
  loadTasks();
};

const handleTabChange = () => {
  // 切换标签页时不需要重新加载，因为已经在loadTasks中加载了所有数据
  // 如果需要根据标签页动态加载，可以在这里调用loadTasks()
};

onMounted(() => {
  loadTasks();
  loadUsers();
  
  // 添加页面可见性监听，当页面重新可见时刷新数据
  document.addEventListener('visibilitychange', handleVisibilityChange);
});

// 监听路由变化，当导航到任务列表页面时自动刷新数据
watch(
  () => route.path,
  (newPath) => {
    // 当用户导航到任务管理页面时，刷新任务列表
    if (newPath === "/test-task") {
      loadTasks();
    }
  }
);

// 页面可见性变化处理
const handleVisibilityChange = () => {
  if (document.visibilityState === 'visible') {
    // 当页面重新可见时，刷新任务列表
    loadTasks();
  }
};
</script>

<style lang="scss" scoped>
.test-task-management {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: #f5f7fa;
}

.filter-section {
  flex-shrink: 0;
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  min-width: 0;
}

.filter-section .filter-form {
  margin: 0;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px 16px;
  width: 100%;
  min-width: 0;
}

.filter-section :deep(.el-form-item) {
  flex: 0 0 auto;
  margin-bottom: 0;
  margin-right: 0;
}

/* 任务标签页区域填满剩余高度 */
.task-tabs-section {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.task-tabs-section :deep(.el-tabs) {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.task-tabs-section :deep(.el-tabs__content) {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.task-tabs-section :deep(.el-tabs__panel) {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.task-tabs-section :deep(.el-tab-pane) {
  height: 100%;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.table-section {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 56px;
}

/* 表格视口填满高度，不出现横向滚动条，表格列自适应宽度 */
.table-section .table-scroll-viewport {
  max-height: none !important;
  flex: 1;
  min-height: 0;
  overflow-x: hidden;
  overflow-y: auto;
}

.table-section .table-scroll-viewport :deep(.el-table) {
  min-width: 0 !important;
}

.table-section .table-scroll-viewport :deep(.el-table__body-wrapper) {
  overflow-x: hidden !important;
}

.table-section {
  :deep(.el-button.is-circle) {
    padding: 12px;
    background-color: transparent !important;
    border: 1px solid #dcdfe6;

    &:hover {
      background-color: #f5f7fa !important;
    }

    .el-icon {
      font-size: 16px;
    }
  }

  :deep(.el-button + .el-button) {
    margin-left: 10px;
  }

  .time-range {
    font-size: 13px;
    line-height: 2;

    .time-item {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;

      .time-label {
        color: #909399;
        font-size: 12px;
        min-width: 32px;
      }

      .time-value {
        color: #303133;
        font-size: 13px;
        font-weight: 500;
      }
    }
  }

  .no-data {
    color: #c0c4cc;
    font-size: 13px;
  }

  .stats-mini {
    .stats-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 6px;

      .stats-rate {
        display: flex;
        align-items: center;
        gap: 4px;

        .stats-label {
          color: #606266;
          font-size: 11px;
          font-weight: 500;
        }

        .stats-percentage {
          font-size: 13px;
          font-weight: 700;
        }
      }

      .stats-total {
        font-size: 11px;
        color: #409eff;
        font-weight: 600;
      }
    }

    .stats-detail {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-top: 6px;

      .stats-item {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 11px;
        font-weight: 500;

        .item-label {
          font-size: 11px;
          color: #909399;
        }

        .item-value {
          font-size: 12px;
          font-weight: 600;
        }

        &.pass {
          .item-value {
            color: #67c23a;
          }
        }

        &.fail {
          .item-value {
            color: #f56c6c;
          }
        }

        &.blocked {
          .item-value {
            color: #e6a23c;
          }
        }

        &.not-applicable {
          .item-value {
            color: #909399;
          }
        }

        &.not-executed {
          .item-value {
            color: #909399;
          }
        }
      }
    }
  }
}

.pagination-container {
  position: fixed;
  bottom: 0;
  right: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  background: white;
  padding: 15px 20px;
  border-top: 1px solid #e4e7ed;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.pagination-container .el-pagination {
  margin: 0;
  text-align: center;
}

.script-file-link-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
}

.script-file-link {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #409eff;
  cursor: pointer;
  text-decoration: none;
  font-size: 14px;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.3s;
}

.script-file-link:hover {
  color: #66b1ff;
  background-color: #ecf5ff;
}
</style>
