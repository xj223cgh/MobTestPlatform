<template>
  <div class="project-detail">
    <div class="info-section">
      <el-card
        shadow="hover"
        class="info-card"
      >
        <template #header>
          <div class="card-header">
            <h2>项目名称: {{ projectDetail.project_name || "未知项目" }}</h2>
            <div class="header-actions">
              <el-button
                type="primary"
                @click="handleEdit"
              >
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button @click="handleBack">
                <el-icon><ArrowLeft /></el-icon>
                返回列表
              </el-button>
            </div>
          </div>
        </template>
        <el-descriptions
          :column="2"
          border
        >
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(projectDetail.status)">
              {{ getStatusText(projectDetail.status) }}
            </el-tag>
          </el-descriptions-item>

          <el-descriptions-item label="优先级">
            <el-tag :type="getPriorityType(projectDetail.priority)">
              {{ getPriorityText(projectDetail.priority) || "-" }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="负责人">
            {{ projectDetail.owner_name || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="创建者">
            {{ projectDetail.creator_name || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="开始日期">
            {{ formatDateTime(projectDetail.start_date) }}
          </el-descriptions-item>
          <el-descriptions-item label="结束日期">
            {{ formatDateTime(projectDetail.end_date) }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(projectDetail.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatDateTime(projectDetail.updated_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
    </div>

    <el-dialog
      v-model="dialogVisible"
      title="编辑项目"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="projectFormRef"
        :model="projectForm"
        :rules="projectRules"
        label-width="100px"
      >
        <el-form-item
          label="项目名称"
          prop="project_name"
        >
          <el-input
            v-model="projectForm.project_name"
            placeholder="请输入项目名称"
          />
        </el-form-item>
        <el-form-item
          label="项目描述"
          prop="description"
          required
        >
          <el-input
            v-model="projectForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入项目描述"
          />
        </el-form-item>
        <el-form-item
          label="状态"
          prop="status"
        >
          <el-select
            v-model="projectForm.status"
            placeholder="请选择项目状态"
          >
            <el-option
              label="未开始"
              value="not_started"
            />
            <el-option
              label="进行中"
              value="in_progress"
            />
            <el-option
              label="已暂停"
              value="paused"
            />
            <el-option
              label="已完成"
              value="completed"
            />
            <el-option
              label="已关闭"
              value="closed"
            />
          </el-select>
        </el-form-item>
        <el-form-item
          label="优先级"
          prop="priority"
        >
          <el-select
            v-model="projectForm.priority"
            placeholder="请选择项目优先级"
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
        <el-form-item
          label="项目负责人"
          prop="owner_id"
          required
        >
          <el-select
            v-model="projectForm.owner_id"
            placeholder="请选择项目负责人"
            style="width: 100%"
            @change="handleOwnerChange"
          >
            <el-option
              v-for="user in allUsers"
              :key="user.id"
              :label="user.real_name || user.username"
              :value="user.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="项目成员">
          <el-select
            v-model="projectForm.selectedUsers"
            multiple
            placeholder="请选择项目成员"
            style="width: 100%"
            collapse-tags
            :collapse-tags-tooltip="true"
            @change="handleMembersChange"
          >
            <el-option
              v-for="user in getSortedUsers()"
              :key="user.id"
              :label="user.real_name || user.username"
              :value="user.id"
            />
          </el-select>
          <div style="margin-top: 5px; font-size: 12px; color: #909399">
            <span>注意：当前项目负责人无法从成员列表中删除</span>
          </div>
        </el-form-item>
        <el-form-item
          label="开始日期"
          prop="start_date"
          required
        >
          <el-date-picker
            v-model="projectForm.start_date"
            type="datetime"
            placeholder="请选择开始日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item
          label="结束日期"
          prop="end_date"
          required
        >
          <el-date-picker
            v-model="projectForm.end_date"
            type="datetime"
            placeholder="请选择结束日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item
          label="项目文档链接"
          prop="doc_url"
        >
          <el-input
            v-model="projectForm.doc_url"
            placeholder="请输入项目文档链接"
          />
        </el-form-item>
        <el-form-item
          label="流水线链接"
          prop="pipeline_url"
        >
          <el-input
            v-model="projectForm.pipeline_url"
            placeholder="请输入流水线链接"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">
          取消
        </el-button>
        <el-button
          type="primary"
          :loading="dialogLoading"
          @click="handleSaveProject"
        >
          保存
        </el-button>
      </template>
    </el-dialog>

    <el-row
      :gutter="20"
      class="info-section-row"
    >
      <el-col :span="12">
        <div class="info-section">
          <el-card
            shadow="hover"
            class="info-card equal-height-card"
          >
            <template #header>
              <div class="card-header">
                <span>项目链接</span>
              </div>
            </template>
            <el-descriptions
              :column="1"
              border
              label-width="120px"
            >
              <el-descriptions-item label="文档链接">
                <a
                  v-if="projectDetail.doc_url"
                  :href="projectDetail.doc_url"
                  target="_blank"
                  class="project-link"
                >{{ projectDetail.doc_url }}</a>
                <span v-else>-</span>
              </el-descriptions-item>
              <el-descriptions-item label="流水线链接">
                <a
                  v-if="projectDetail.pipeline_url"
                  :href="projectDetail.pipeline_url"
                  target="_blank"
                  class="project-link"
                >{{ projectDetail.pipeline_url }}</a>
                <span v-else>-</span>
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </div>
      </el-col>

      <el-col :span="12">
        <div class="info-section">
          <el-card
            shadow="hover"
            class="info-card equal-height-card"
          >
            <template #header>
              <div class="card-header">
                <span>项目描述</span>
                <span class="description-count">{{ (projectDetail.description || "").length }}/{{
                  100
                }}</span>
              </div>
            </template>
            <div class="description-content">
              {{ projectDetail.description || "暂无描述" }}
            </div>
          </el-card>
        </div>
      </el-col>
    </el-row>

    <div class="info-section">
      <el-card
        shadow="hover"
        class="info-card"
      >
        <template #header>
          <div class="card-header">
            <span>项目统计</span>
          </div>
        </template>

        <el-row
          :gutter="20"
          class="stats-overview"
        >
          <el-col :span="8">
            <div class="stat-item-with-chart">
              <div class="stat-header">
                <div class="stat-label">
                  用例总数
                </div>
                <div class="stat-value">
                  {{ projectDetail.case_stats?.total || 0 }}
                </div>
              </div>
              <div class="chart-container-small">
                <v-chart
                  :option="caseExecutionChartOption"
                  autoresize
                />
              </div>
              <div class="chart-caption">
                <span
                  v-for="item in caseExecutionLegend"
                  :key="item.name"
                  class="chart-caption-item"
                  :class="{ 'chart-caption-item-inactive': !caseExecutionSelected[item.name] }"
                  @click="toggleCaseExecution(item.name)"
                >
                  <span
                    class="chart-caption-rect"
                    :style="{ backgroundColor: caseExecutionSelected[item.name] ? item.color : undefined }"
                  />
                  <span
                    class="chart-caption-label"
                    :style="{ color: caseExecutionSelected[item.name] ? item.color : undefined }"
                  >{{ item.name }}</span>
                </span>
              </div>
            </div>
          </el-col>

          <el-col :span="8">
            <div class="stat-item-with-chart">
              <div class="stat-header">
                <div class="stat-label">
                  迭代总数
                </div>
                <div class="stat-value">
                  {{ projectDetail.iteration_count || 0 }}
                </div>
              </div>
              <div class="chart-container-small">
                <v-chart
                  :option="iterationChartOption"
                  autoresize
                />
              </div>
              <div class="chart-caption">
                <span
                  v-for="item in iterationLegend"
                  :key="item.name"
                  class="chart-caption-item"
                  :class="{ 'chart-caption-item-inactive': !iterationSelected[item.name] }"
                  @click="toggleIteration(item.name)"
                >
                  <span
                    class="chart-caption-rect"
                    :style="{ backgroundColor: iterationSelected[item.name] ? item.color : undefined }"
                  />
                  <span
                    class="chart-caption-label"
                    :style="{ color: iterationSelected[item.name] ? item.color : undefined }"
                  >{{ item.name }}</span>
                </span>
              </div>
            </div>
          </el-col>

          <el-col :span="8">
            <div class="stat-item-with-chart">
              <div class="stat-header">
                <div class="stat-label">
                  需求总数
                </div>
                <div class="stat-value">
                  {{ projectDetail.requirement_count || 0 }}
                </div>
              </div>
              <div class="chart-container-small">
                <v-chart
                  :option="requirementChartOption"
                  autoresize
                />
              </div>
              <div class="chart-caption">
                <span
                  v-for="item in requirementLegend"
                  :key="item.name"
                  class="chart-caption-item"
                  :class="{ 'chart-caption-item-inactive': !requirementSelected[item.name] }"
                  @click="toggleRequirement(item.name)"
                >
                  <span
                    class="chart-caption-rect"
                    :style="{ backgroundColor: requirementSelected[item.name] ? item.color : undefined }"
                  />
                  <span
                    class="chart-caption-label"
                    :style="{ color: requirementSelected[item.name] ? item.color : undefined }"
                  >{{ item.name }}</span>
                </span>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { Edit, ArrowLeft } from "@element-plus/icons-vue";
import { getProject, updateProject } from "@/api/project";
import { getUserOptions } from "@/api/user";
import { useUserStore } from "@/stores/user";
import { useSystemSettingsStore } from "@/stores/systemSettings";
import dayjs from "dayjs";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { PieChart, BarChart } from "echarts/charts";
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from "echarts/components";
import VChart from "vue-echarts";

use([
  CanvasRenderer,
  PieChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
]);

const loading = ref(false);
const projectDetail = ref({});
const route = useRoute();
const router = useRouter();

const dialogVisible = ref(false);
const dialogTitle = ref("");
const dialogLoading = ref(false);
const projectFormRef = ref(null);
const editingProjectId = ref(null);

const allUsers = ref([]);

// 系统设置（用于图表图例深色模式文字颜色）
const settingsStore = useSystemSettingsStore();

/** 根据当前主题更新三个统计图的图例样式：正常/未选中时文字与图标颜色 */
function applyLegendTheme() {
  const isDark = settingsStore.theme === "dark";
  const legendColor = isDark ? "#e5eaf3" : undefined;
  const inactiveColor = isDark ? "#6b6c6e" : "#909399";
  const textStyle = { fontSize: 11, color: legendColor };

  const legend = {
    ...caseExecutionChartOption.value.legend,
    textStyle,
    inactiveColor,
  };
  caseExecutionChartOption.value.legend = legend;
  iterationChartOption.value.legend = { ...iterationChartOption.value.legend, textStyle, inactiveColor };
  requirementChartOption.value.legend = { ...requirementChartOption.value.legend, textStyle, inactiveColor };
}

const projectForm = reactive({
  project_name: "",
  description: "",
  status: "not_started",
  priority: "medium",
  owner_id: "",
  start_date: "",
  end_date: "",
  doc_url: "",
  pipeline_url: "",
  selectedUsers: [],
});

const getAllUsers = async () => {
  try {
    const response = await getUserOptions({ size: 1000 });
    allUsers.value = response.data?.items || [];
  } catch (error) {
    console.error("获取用户列表失败:", error);
    ElMessage.error("获取用户列表失败");
  }
};

watch(
  () => projectForm.owner_id,
  (newOwnerId, oldOwnerId) => {
    if (!newOwnerId) return;

    // 先过滤掉旧的负责人ID（如果存在），然后添加新的负责人ID
    const updatedUsers = projectForm.selectedUsers.filter(
      (id) => id !== oldOwnerId,
    );

    if (!updatedUsers.includes(newOwnerId)) {
      updatedUsers.push(newOwnerId);
    }

    projectForm.selectedUsers = updatedUsers;
  },
);

const handleOwnerChange = () => {};

const handleMembersChange = () => {
  if (!projectForm.owner_id) return;

  if (!projectForm.selectedUsers.includes(projectForm.owner_id)) {
    projectForm.selectedUsers.push(projectForm.owner_id);
    ElMessage.warning("当前项目负责人无法从成员列表中删除");
  }
};

// 项目成员下拉排序：负责人排在顶部
const getSortedUsers = () => {
  if (!projectForm.owner_id) return allUsers.value;

  const sortedUsers = [...allUsers.value];
  return sortedUsers.sort((a, b) => {
    if (a.id == projectForm.owner_id) return -1;
    if (b.id == projectForm.owner_id) return 1;
    return 0;
  });
};

const projectRules = {
  project_name: [
    { required: true, message: "请输入项目名称", trigger: "blur" },
    {
      min: 1,
      max: 100,
      message: "项目名称长度在 1 到 100 个字符",
      trigger: "blur",
    },
  ],
  description: [{ required: true, message: "请输入项目描述", trigger: "blur" }],
  status: [{ required: true, message: "请选择项目状态", trigger: "change" }],
  priority: [
    { required: true, message: "请选择项目优先级", trigger: "change" },
  ],
  owner_id: [
    { required: true, message: "请选择项目负责人", trigger: "change" },
  ],
  start_date: [
    { required: true, message: "请选择开始日期", trigger: "change" },
  ],
  end_date: [{ required: true, message: "请选择结束日期", trigger: "change" }],
};

// 扇形图底部图题：对应颜色的矩形 + 文字标签（与图表扇区一致）
const caseExecutionLegend = [
  { name: "通过", color: "#5cb85c" },
  { name: "失败", color: "#ff6e6e" },
  { name: "阻塞", color: "#ffc107" },
  { name: "不适用", color: "#8e44ad" },
  { name: "未执行", color: "#a6a6a6" },
];
const iterationLegend = [
  { name: "规划中", color: "#428bca" },
  { name: "进行中", color: "#5cb85c" },
  { name: "已完成", color: "#ffc107" },
  { name: "已取消", color: "#ff6e6e" },
];
const requirementLegend = [
  { name: "新建", color: "#a6a6a6" },
  { name: "进行中", color: "#ffc107" },
  { name: "已完成", color: "#5cb85c" },
  { name: "已取消", color: "#ff6e6e" },
];

// 图题对应项是否在扇形图中显示（true=显示，false=不显示，点击图题切换）
const caseExecutionSelected = ref({
  通过: true,
  失败: true,
  阻塞: true,
  不适用: true,
  未执行: true,
});
const iterationSelected = ref({
  规划中: true,
  进行中: true,
  已完成: true,
  已取消: true,
});
const requirementSelected = ref({
  新建: true,
  进行中: true,
  已完成: true,
  已取消: true,
});

function toggleCaseExecution(name) {
  caseExecutionSelected.value = {
    ...caseExecutionSelected.value,
    [name]: !caseExecutionSelected.value[name],
  };
  applyChartLegendSelected();
}
function toggleIteration(name) {
  iterationSelected.value = {
    ...iterationSelected.value,
    [name]: !iterationSelected.value[name],
  };
  applyChartLegendSelected();
}
function toggleRequirement(name) {
  requirementSelected.value = {
    ...requirementSelected.value,
    [name]: !requirementSelected.value[name],
  };
  applyChartLegendSelected();
}
function applyChartLegendSelected() {
  caseExecutionChartOption.value.legend = {
    ...caseExecutionChartOption.value.legend,
    selected: { ...caseExecutionSelected.value },
  };
  iterationChartOption.value.legend = {
    ...iterationChartOption.value.legend,
    selected: { ...iterationSelected.value },
  };
  requirementChartOption.value.legend = {
    ...requirementChartOption.value.legend,
    selected: { ...requirementSelected.value },
  };
}

const caseExecutionChartOption = ref({
  title: {
    text: "",
    left: "center",
  },
  tooltip: {
    trigger: "item",
    formatter: "{b}: {c} ({d}%)",
  },
  legend: {
    show: false,
    selected: {},
  },
  series: [
    {
      name: "用例执行情况",
      type: "pie",
      radius: "62%",
      center: ["50%", "44%"],
      avoidLabelOverlap: true,
      minAngle: 2,
      itemStyle: {
        borderRadius: 0,
        borderColor: "#fff",
        borderWidth: 1,
      },
      label: {
        show: true,
        position: "outside",
        formatter: "{b}: {c} ({d}%)",
        fontSize: 11,
      },
      emphasis: {
        label: {
          show: true,
          fontSize: "13",
          fontWeight: "bold",
        },
      },
      labelLine: {
        show: true,
        length: 8,
        length2: 10,
      },
      data: [],
    },
  ],
});

const iterationChartOption = ref({
  title: {
    text: "",
    left: "center",
  },
  tooltip: {
    trigger: "item",
    formatter: "{b}: {c} ({d}%)",
  },
  legend: {
    show: false,
    selected: {},
  },
  series: [
    {
      name: "迭代统计",
      type: "pie",
      radius: "62%",
      center: ["50%", "44%"],
      avoidLabelOverlap: true,
      minAngle: 2,
      itemStyle: {
        borderRadius: 0,
        borderColor: "#fff",
        borderWidth: 1,
      },
      label: {
        show: true,
        position: "outside",
        formatter: "{b}: {c} ({d}%)",
        fontSize: 11,
      },
      emphasis: {
        label: {
          show: true,
          fontSize: "13",
          fontWeight: "bold",
        },
      },
      labelLine: {
        show: true,
        length: 8,
        length2: 10,
      },
      data: [],
    },
  ],
});

const requirementChartOption = ref({
  title: {
    text: "",
    left: "center",
  },
  tooltip: {
    trigger: "item",
    formatter: "{b}: {c} ({d}%)",
  },
  legend: {
    show: false,
    selected: {},
  },
  series: [
    {
      name: "需求状态",
      type: "pie",
      radius: "62%",
      center: ["50%", "44%"],
      avoidLabelOverlap: true,
      minAngle: 2,
      itemStyle: {
        borderRadius: 0,
        borderColor: "#fff",
        borderWidth: 1,
      },
      label: {
        show: true,
        position: "outside",
        formatter: "{b}: {c} ({d}%)",
        fontSize: 11,
      },
      emphasis: {
        label: {
          show: true,
          fontSize: "13",
          fontWeight: "bold",
        },
      },
      labelLine: {
        show: true,
        length: 8,
        length2: 10,
      },
      data: [],
    },
  ],
});

const getStatusType = (status) => {
  const statusMap = {
    not_started: "info",
    in_progress: "success",
    paused: "warning",
    completed: "success",
    closed: "danger",
  };
  return statusMap[status] || "info";
};

const getStatusText = (status) => {
  const statusMap = {
    not_started: "未开始",
    in_progress: "进行中",
    paused: "已暂停",
    completed: "已完成",
    closed: "已关闭",
  };
  return statusMap[status] || status || "-";
};

const getPriorityType = (priority) => {
  const priorityMap = {
    high: "danger",
    medium: "warning",
    low: "success",
  };
  return priorityMap[priority] || "info";
};

const getPriorityText = (priority) => {
  const priorityMap = {
    high: "高",
    medium: "中",
    low: "低",
  };
  return priorityMap[priority] || priority;
};

const formatDateTime = (dateTime) => {
  return dateTime ? dayjs(dateTime).format("YYYY-MM-DD HH:mm:ss") : "-";
};

// 为饼图设置与报告详情一致的 formatter（0 显示 0%）及多 0 值错开显示的 minAngle
function applyPieChartFormatters(optionRef) {
  const data = optionRef.value.series[0].data || [];
  const total = data.reduce((s, d) => s + (d.value ?? 0), 0);
  const zeroCount = data.filter((d) => (d.value ?? 0) === 0).length;
  optionRef.value.series[0].minAngle = zeroCount >= 2 ? 8 : 2;
  const pct = (v) => (total > 0 ? (((v ?? 0) / total) * 100).toFixed(1) : "0");
  optionRef.value.tooltip.formatter = (params) =>
    `${params.name}: ${params.value ?? 0} (${pct(params.value)}%)`;
  optionRef.value.series[0].label.formatter = (params) =>
    `${params.name}: ${params.value ?? 0} (${pct(params.value)}%)`;
}

const updateCharts = () => {
  const caseStats = projectDetail.value.case_stats || {};
  caseExecutionChartOption.value.series[0].data = [
    {
      value: caseStats.passed || 0,
      name: "通过",
      itemStyle: { color: "#5cb85c" },
    },
    {
      value: caseStats.failed || 0,
      name: "失败",
      itemStyle: { color: "#ff6e6e" },
    },
    {
      value: caseStats.blocked || 0,
      name: "阻塞",
      itemStyle: { color: "#ffc107" },
    },
    {
      value: caseStats.not_applicable || 0,
      name: "不适用",
      itemStyle: { color: "#8e44ad" },
    },
    {
      value: caseStats.not_run || 0,
      name: "未执行",
      itemStyle: { color: "#a6a6a6" },
    },
  ];
  applyPieChartFormatters(caseExecutionChartOption);

  const iterationStats = projectDetail.value.iteration_stats || {};
  const statusMap = {
    planning: "规划中",
    active: "进行中",
    completed: "已完成",
    cancelled: "已取消",
  };

  iterationChartOption.value.series[0].data = [
    {
      name: statusMap["planning"],
      value: iterationStats.planning || 0,
      itemStyle: { color: "#428bca" },
    },
    {
      name: statusMap["active"],
      value: iterationStats.active || 0,
      itemStyle: { color: "#5cb85c" },
    },
    {
      name: statusMap["completed"],
      value: iterationStats.completed || 0,
      itemStyle: { color: "#ffc107" },
    },
    {
      name: statusMap["cancelled"],
      value: iterationStats.cancelled || 0,
      itemStyle: { color: "#ff6e6e" },
    },
  ];
  applyPieChartFormatters(iterationChartOption);

  const requirementStats = projectDetail.value.requirement_stats || {};
  requirementChartOption.value.series[0].data = [
    {
      value: requirementStats.new || 0,
      name: "新建",
      itemStyle: { color: "#a6a6a6" },
    },
    {
      value: requirementStats.in_progress || 0,
      name: "进行中",
      itemStyle: { color: "#ffc107" },
    },
    {
      value: requirementStats.completed || 0,
      name: "已完成",
      itemStyle: { color: "#5cb85c" },
    },
    {
      value: requirementStats.cancelled || 0,
      name: "已取消",
      itemStyle: { color: "#ff6e6e" },
    },
  ];
  applyPieChartFormatters(requirementChartOption);

  applyLegendTheme();
  applyChartLegendSelected();
};

const fetchProjectDetail = async () => {
  loading.value = true;
  try {
    const projectId = route.params.id;
    const response = await getProject(projectId);
    projectDetail.value = response.data?.project || {};
  } catch (error) {
    console.error("获取项目详情失败:", error);
    ElMessage.error("获取项目详情失败");
    projectDetail.value = {};
  } finally {
    loading.value = false;
    updateCharts();
  }
};

watch(
  projectDetail,
  () => {
    updateCharts();
  },
  { deep: true },
);

watch(
  () => settingsStore.theme,
  () => {
    applyLegendTheme();
  },
);

const handleBack = () => {
  router.push("/projects");
};

const resetForm = () => {
  if (projectFormRef.value) {
    projectFormRef.value.resetFields();
  }
  editingProjectId.value = null;
  Object.assign(projectForm, {
    project_name: "",
    description: "",
    status: "not_started",
    priority: "medium",
    owner_id: "",
    start_date: "",
    end_date: "",
    doc_url: "",
    pipeline_url: "",
    selectedUsers: [],
  });
};

const handleEdit = () => {
  dialogTitle.value = "编辑项目";
  editingProjectId.value = projectDetail.value.id;

  const members = projectDetail.value.members || [];
  const selectedUsers = members.map((member) => member.user_id);

  Object.assign(projectForm, {
    project_name: projectDetail.value.project_name || "",
    description: projectDetail.value.description || "",
    status: projectDetail.value.status || "not_started",
    priority: projectDetail.value.priority || "medium",
    owner_id: projectDetail.value.owner_id || "",
    start_date: projectDetail.value.start_date || "",
    end_date: projectDetail.value.end_date || "",
    doc_url: projectDetail.value.doc_url || "",
    pipeline_url: projectDetail.value.pipeline_url || "",
    selectedUsers: selectedUsers,
  });
  getAllUsers();
  dialogVisible.value = true;
};

const handleSaveProject = async () => {
  if (!projectFormRef.value) return;

  await projectFormRef.value.validate();

  const userStore = useUserStore();
  const currentUserId = userStore.userInfo.id;

  const saveData = { ...projectForm };

  // 只有创建项目时才设置creator_id，编辑时不修改创建者
  if (!editingProjectId.value) {
    saveData.creator_id = currentUserId;
  }

  saveData.members = saveData.selectedUsers.map((userId) => ({
    user_id: userId,
    role: "tester",
  }));

  delete saveData.selectedUsers;

  dialogLoading.value = true;
  try {
    const projectId = projectDetail.value.id;
    const response = await updateProject(projectId, saveData);

    Object.assign(projectDetail.value, response.data.project || {});

    ElMessage.success("项目更新成功");
    dialogVisible.value = false;
  } catch (error) {
    console.error("更新项目失败:", error);
    ElMessage.error("项目更新失败");
  } finally {
    dialogLoading.value = false;
  }
};

onMounted(() => {
  fetchProjectDetail();
});
</script>

<style lang="scss" scoped>
.project-detail {
  padding: 20px;
  min-height: 100vh;
  background-color: var(--el-bg-color-page, #f5f7fa);
}

.header-actions {
  display: flex;
  gap: 10px;
}

.info-section {
  margin-bottom: 20px;
}

.info-card {
  border-radius: 8px;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: var(--el-text-color-primary, #303133);
  padding: 5px 0;
}

.card-header span {
  font-weight: 700;
  font-size: 16px;
}

.description-content {
  line-height: 1.6;
  color: var(--el-text-color-regular, #606266);
  max-height: 300px;
  overflow-y: auto;
  padding: 10px;
  background-color: var(--el-fill-color-light, #fafafa);
  border-radius: 4px;
  border: 1px solid var(--el-border-color-lighter, #ebeef5);
}

.description-count {
  font-size: 12px;
  color: var(--el-text-color-secondary, #909399);
  font-weight: normal;
  margin-left: 10px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background-color: var(--el-fill-color-light, #f5f7fa);
  border-radius: 8px;

  .stat-label {
    font-size: 14px;
    color: var(--el-text-color-regular, #606266);
    margin-bottom: 8px;
  }

  .stat-value {
    font-size: 24px;
    font-weight: 500;
    color: var(--el-text-color-primary, #303133);
  }
}

/* 统计概览样式：允许扇形图外侧标注完整显示 */
.stats-overview {
  margin-bottom: 0;
  overflow: visible;
}

/* 带图表的统计项样式 */
.stat-item-with-chart {
  background-color: var(--el-fill-color-light, #f5f7fa);
  border-radius: 8px;
  padding: 10px 0px;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow: visible;
}

/* 统计项头部样式（上）：与扇形图留出间距 */
.stat-header {
  text-align: center;
  margin-top: 5px;
  margin-bottom: 12px;
  padding: 0 10px;
}

/* 小图表容器样式（中）：留出左右空间避免扇形图外侧数据标注被裁切 */
.chart-container-small {
  height: 260px;
  width: 100%;
  min-width: 150px;
  margin-bottom: 0;
  overflow: visible;
  padding: 0 8px;
  box-sizing: border-box;
}

/* 扇形图底部属性（下）：紧贴扇形图，缩小与图表的间距 */
.chart-caption {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 6px 12px;
  padding: 0 4px 2px;
  margin-top: -16px;
}
.chart-caption-item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  white-space: nowrap;
  cursor: pointer;
  user-select: none;
  transition: opacity 0.2s, color 0.2s, background-color 0.2s;
}
.chart-caption-item:hover {
  opacity: 0.85;
}
.chart-caption-rect {
  width: 14px;
  height: 10px;
  border-radius: 2px;
  flex-shrink: 0;
  transition: background-color 0.2s;
}
.chart-caption-item-inactive .chart-caption-rect {
  background-color: var(--el-text-color-placeholder, #c0c4cc) !important;
}
.chart-caption-label {
  transition: color 0.2s;
}
.chart-caption-item-inactive .chart-caption-label {
  color: var(--el-text-color-placeholder, #c0c4cc) !important;
  text-decoration: line-through;
}

/* 项目链接样式 */
.project-link {
  display: block;
  word-break: break-all;
  white-space: normal;
  line-height: 1.5;
  color: var(--el-color-primary);
  text-decoration: none;

  &:hover {
    color: var(--el-color-primary-light-3);
    text-decoration: underline;
  }
}

/* 等高卡片样式 */
.equal-height-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 调整行样式，确保列对齐 */
.info-section-row {
  display: flex;
  align-items: stretch;
}

/* 确保卡片内容区域能自动扩展 */
.info-card {
  display: flex;
  flex-direction: column;
}

/* 调整描述内容区域，使其能自动扩展 */
.description-content {
  flex: 1;
  min-height: 80px;
  line-height: 1.6;
  color: #606266;
  overflow-y: auto;
  padding: 10px;
  background-color: #fafafa;
  border-radius: 4px;
  border: 1px solid #ebeef5;
}

/* 操作按钮样式 */
.operation-buttons {
  display: flex;
  justify-content: center;
  gap: 10px;
}
</style>
