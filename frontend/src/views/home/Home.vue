<template>
  <div class="home">
    <div class="page-header">
      <div class="header-left">
        <h1 class="title">{{ systemSettingsStore.systemName || '移动测试平台' }}</h1>
        <p class="subtitle">{{ systemSettingsStore.systemDescription || '专业的移动测试管理平台' }}</p>
      </div>
      <div class="actions">
        <el-button
          type="primary"
          @click="refreshData"
        >
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div
        v-loading="loading"
        class="stat-card stat-card--clickable"
        @click="router.push('/projects')"
      >
        <div class="stat-icon primary">
          <el-icon><FolderOpened /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">
            {{ stats.projects || 0 }}
          </div>
          <div class="stat-label">
            项目总数
          </div>
          <div :class="['stat-trend', stats.projectsGrowth > 0 ? 'positive' : stats.projectsGrowth < 0 ? 'negative' : '']">
            <el-icon v-if="stats.projectsGrowth > 0"><CaretTop /></el-icon>
            <el-icon v-else-if="stats.projectsGrowth < 0"><CaretBottom /></el-icon>
            <el-icon v-else><Minus /></el-icon>
            {{ Math.abs(stats.projectsGrowth) }}%
          </div>
        </div>
      </div>

      <div
        v-loading="loading"
        class="stat-card stat-card--clickable"
        @click="router.push('/test-cases')"
      >
        <div class="stat-icon success">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">
            {{ stats.testCases || 0 }}
          </div>
          <div class="stat-label">
            测试用例
          </div>
          <div :class="['stat-trend', stats.testCasesGrowth > 0 ? 'positive' : stats.testCasesGrowth < 0 ? 'negative' : '']">
            <el-icon v-if="stats.testCasesGrowth > 0"><CaretTop /></el-icon>
            <el-icon v-else-if="stats.testCasesGrowth < 0"><CaretBottom /></el-icon>
            <el-icon v-else><Minus /></el-icon>
            {{ Math.abs(stats.testCasesGrowth) }}%
          </div>
        </div>
      </div>

      <div
        v-loading="loading"
        class="stat-card stat-card--clickable"
        @click="router.push('/test-tasks')"
      >
        <div class="stat-icon warning">
          <el-icon><List /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">
            {{ stats.testTasks || 0 }}
          </div>
          <div class="stat-label">
            测试任务
          </div>
          <div :class="['stat-trend', stats.testTasksGrowth > 0 ? 'positive' : stats.testTasksGrowth < 0 ? 'negative' : '']">
            <el-icon v-if="stats.testTasksGrowth > 0"><CaretTop /></el-icon>
            <el-icon v-else-if="stats.testTasksGrowth < 0"><CaretBottom /></el-icon>
            <el-icon v-else><Minus /></el-icon>
            {{ Math.abs(stats.testTasksGrowth) }}%
          </div>
        </div>
      </div>

      <div
        v-loading="loading"
        class="stat-card stat-card--clickable"
        @click="router.push('/devices')"
      >
        <div class="stat-icon info">
          <el-icon><Monitor /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">
            {{ stats.devices || 0 }}
          </div>
          <div class="stat-label">
            测试设备
          </div>
          <div :class="['stat-trend', stats.devicesGrowth > 0 ? 'positive' : stats.devicesGrowth < 0 ? 'negative' : '']">
            <el-icon v-if="stats.devicesGrowth > 0"><CaretTop /></el-icon>
            <el-icon v-else-if="stats.devicesGrowth < 0"><CaretBottom /></el-icon>
            <el-icon v-else><Minus /></el-icon>
            {{ Math.abs(stats.devicesGrowth) }}%
          </div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-grid">
      <!-- 测试任务趋势图 -->
      <div class="chart-card">
        <div class="chart-header">
          <h3>测试任务趋势</h3>
          <el-select
            v-model="taskTrendPeriod"
            size="small"
            style="width: 120px"
            @change="loadTaskTrendData"
          >
            <el-option
              label="最近7天"
              value="7d"
            />
            <el-option
              label="最近30天"
              value="30d"
            />
            <el-option
              label="最近90天"
              value="90d"
            />
          </el-select>
        </div>
        <div class="chart-container">
          <v-chart
            class="chart"
            :option="taskTrendOption"
            v-loading="chartLoading.taskTrend"
          />
        </div>
      </div>

      <!-- 设备状态分布 -->
      <div class="chart-card">
        <div class="chart-header">
          <h3>设备状态分布</h3>
        </div>
        <div class="chart-container">
          <v-chart
            class="chart"
            :option="deviceStatusOption"
            v-loading="chartLoading.deviceStatus"
          />
        </div>
      </div>
    </div>
    
    <!-- 第二行图表 -->
    <div class="charts-grid-2">
      <!-- 任务状态分布 -->
      <div class="chart-card">
        <div class="chart-header">
          <h3>任务状态分布</h3>
        </div>
        <div class="chart-container">
          <v-chart
            class="chart"
            :option="taskStatusOption"
            v-loading="chartLoading.taskStatus"
          />
        </div>
      </div>

      <!-- 最近访问项目 -->
      <div class="chart-card">
        <div class="chart-header">
          <h3>最近访问项目</h3>
        </div>
        <div class="project-list">
          <div
            v-for="project in recentProjects"
            :key="project.id"
            class="project-item"
          >
            <div class="project-info">
              <div class="project-name">{{ project.project_name }}</div>
              <div class="project-meta">
                <el-tag :type="getProjectStatusType(project.status)" size="small">
                  {{ getProjectStatusLabel(project.status) }}
                </el-tag>
                <span class="project-owner">{{ project.owner_name || '未分配' }}</span>
              </div>
            </div>
            <div class="project-time">
              {{ formatTime(project.updated_at) }}
            </div>
          </div>
          <el-empty v-if="!recentProjects.length" description="暂无项目" :image-size="80" />
        </div>
      </div>
    </div>

    <div class="activity-section">
      <div class="card">
        <div class="card-header">
          <h3>最近活动</h3>
          <el-select
            v-model="activityTimeRange"
            size="small"
            class="activity-time-select"
          >
            <el-option label="默认(近期10条)" value="default" />
            <el-option label="近3天" value="3d" />
            <el-option label="近7天" value="7d" />
            <el-option label="近30天" value="30d" />
            <el-option label="3个月内" value="90d" />
          </el-select>
        </div>
        <div class="activity-list">
          <div
            v-for="activity in recentActivities"
            :key="activity.id"
            class="activity-item"
            :class="{ 'activity-item-clickable': getActivityRoute(activity) }"
            @click="handleActivityClick(activity)"
          >
            <div
              class="activity-icon"
              :class="[activity.type, { 'is-notification': activity._isNotification }]"
            >
              <el-icon>
                <component :is="getActivityIcon(activity)" />
              </el-icon>
            </div>
            <div class="activity-content">
              <div class="activity-title" :class="{ 'activity-title-link': getActivityRoute(activity) }">
                {{ activity.title }}
              </div>
              <div class="activity-desc">
                {{ activity.description }}
              </div>
              <div class="activity-time">
                {{ formatTime(activity.created_at) }}
              </div>
            </div>
            <el-icon v-if="getActivityRoute(activity)" class="activity-arrow"><ArrowRight /></el-icon>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { LineChart, PieChart } from "echarts/charts";
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from "echarts/components";
import VChart from "vue-echarts";
import { ElMessage } from "element-plus";
import { ArrowRight } from "@element-plus/icons-vue";
import dayjs from "dayjs";
import {
  getHomeStats,
  getRecentActivities,
  getTaskTrendData,
  getDeviceStatusData,
  getRecentProjects,
  getTaskStatusDistribution,
} from "@/api/home";
import { getNotifications } from "@/api/notifications";
import { isPermissionError } from "@/utils/request";
import { useSystemSettingsStore } from "@/stores/systemSettings";
import { getNotificationRoute } from "@/utils/notificationLink";

const router = useRouter();
const systemSettingsStore = useSystemSettingsStore();

use([
  CanvasRenderer,
  LineChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
]);

const loading = ref(false);
const chartLoading = reactive({
  taskTrend: false,
  deviceStatus: false,
  taskStatus: false,
});

const stats = reactive({
  projects: 0,
  projectsGrowth: 0,
  testCases: 0,
  testCasesGrowth: 0,
  testTasks: 0,
  testTasksGrowth: 0,
  devices: 0,
  devicesGrowth: 0,
});

const taskTrendPeriod = ref("7d");

// 最近活动：全量缓存，时间范围筛选后取前 10 条
const recentActivitiesAll = ref([]);
const activityTimeRange = ref("default");
const ACTIVITY_LIMIT = 10;

const recentActivities = computed(() => {
  const list = recentActivitiesAll.value || [];
  if (activityTimeRange.value === "default") {
    return list.slice(0, ACTIVITY_LIMIT);
  }
  const now = Date.now();
  const days = { "3d": 3, "7d": 7, "30d": 30, "90d": 90 }[activityTimeRange.value] || 0;
  const cutoff = now - days * 24 * 60 * 60 * 1000;
  const cutoffStr = new Date(cutoff).toISOString();
  return list.filter((a) => (a.created_at || "") >= cutoffStr).slice(0, ACTIVITY_LIMIT);
});

const recentProjects = ref([]);

const taskTrendData = reactive({
  dates: [],
  completed: [],
  failed: [],
  running: [],
});

const deviceStatusData = ref([]);
const taskStatusData = ref([]);

const taskTrendOption = computed(() => ({
  title: {
    show: false,
  },
  tooltip: {
    trigger: "axis",
  },
  legend: {
    data: ["完成任务", "失败任务", "进行中任务"],
  },
  grid: {
    left: "3%",
    right: "4%",
    bottom: "3%",
    containLabel: true,
  },
  xAxis: {
    type: "category",
    boundaryGap: false,
    data: taskTrendData.dates,
  },
  yAxis: {
    type: "value",
  },
  series: [
    {
      name: "完成任务",
      type: "line",
      smooth: true,
      data: taskTrendData.completed,
      itemStyle: {
        color: "#67C23A",
      },
    },
    {
      name: "失败任务",
      type: "line",
      smooth: true,
      data: taskTrendData.failed,
      itemStyle: {
        color: "#F56C6C",
      },
    },
    {
      name: "进行中任务",
      type: "line",
      smooth: true,
      data: taskTrendData.running,
      itemStyle: {
        color: "#E6A23C",
      },
    },
  ],
}));

const deviceStatusOption = computed(() => ({
  title: {
    show: false,
  },
  tooltip: {
    trigger: "item",
    formatter: "{a} <br/>{b}: {c} ({d}%)",
  },
  legend: {
    orient: "vertical",
    left: "left",
  },
  series: [
    {
      name: "设备状态",
      type: "pie",
      radius: ["40%", "70%"],
      avoidLabelOverlap: false,
      label: {
        show: false,
        position: "center",
      },
      emphasis: {
        label: {
          show: true,
          fontSize: "18",
          fontWeight: "bold",
        },
      },
      labelLine: {
        show: false,
      },
      data: deviceStatusData.value.map((item) => ({
        ...item,
        itemStyle: {
          color:
            item.name === "在线"
              ? "#67C23A"
              : item.name === "离线"
              ? "#909399"
              : item.name === "忙碌"
              ? "#E6A23C"
              : "#F56C6C",
        },
      })),
    },
  ],
}));

const taskStatusOption = computed(() => ({
  title: {
    show: false,
  },
  tooltip: {
    trigger: "item",
    formatter: "{a} <br/>{b}: {c} ({d}%)",
  },
  legend: {
    orient: "vertical",
    left: "left",
  },
  series: [
    {
      name: "任务状态",
      type: "pie",
      radius: ["40%", "70%"],
      avoidLabelOverlap: false,
      label: {
        show: false,
        position: "center",
      },
      emphasis: {
        label: {
          show: true,
          fontSize: "18",
          fontWeight: "bold",
        },
      },
      labelLine: {
        show: false,
      },
      data: taskStatusData.value.map((item) => ({
        ...item,
        itemStyle: {
          color:
            item.name === "已完成"
              ? "#67C23A"
              : item.name === "执行中"
              ? "#409EFF"
              : item.name === "待执行"
              ? "#909399"
              : item.name === "失败"
              ? "#F56C6C"
              : "#C0C4CC",
        },
      })),
    },
  ],
}));

const getActivityIcon = (activity) => {
  if (activity && activity._isNotification) return "Bell";
  const type = typeof activity === "string" ? activity : activity?.type;
  const iconMap = {
    task: "List",
    device: "Monitor",
    user: "User",
    project: "Folder",
    iteration: "Refresh",
    requirement: "Document",
    suite: "Files",
  };
  return iconMap[type] || "Document";
};

const formatTime = (time) => {
  return dayjs(time).format("YYYY-MM-DD HH:mm:ss");
};

const fetchStats = async () => {
  try {
    const response = await getHomeStats();
    if (response.code === 200 || response.success) {
      Object.assign(stats, response.data);
    }
  } catch (error) {
    if (isPermissionError(error)) return;
    console.error("获取统计数据失败:", error);
    ElMessage.error("获取统计数据失败");
  }
};

const loadTaskTrendData = async () => {
  chartLoading.taskTrend = true;
  try {
    const response = await getTaskTrendData({ period: taskTrendPeriod.value });
    if (response.code === 200 || response.success) {
      const data = response.data;
      taskTrendData.dates = data.dates || [];
      taskTrendData.completed = data.completed || [];
      taskTrendData.failed = data.failed || [];
      taskTrendData.running = data.running || [];
    }
  } catch (error) {
    console.error("获取任务趋势数据失败:", error);
  } finally {
    chartLoading.taskTrend = false;
  }
};

const loadDeviceStatusData = async () => {
  chartLoading.deviceStatus = true;
  try {
    const response = await getDeviceStatusData();
    if (response.code === 200 || response.success) {
      deviceStatusData.value = response.data || [];
    }
  } catch (error) {
    console.error("获取设备状态数据失败:", error);
  } finally {
    chartLoading.deviceStatus = false;
  }
};

const loadTaskStatusData = async () => {
  chartLoading.taskStatus = true;
  try {
    const response = await getTaskStatusDistribution();
    if (response.code === 200 || response.success) {
      taskStatusData.value = response.data || [];
    }
  } catch (error) {
    console.error("获取任务状态数据失败:", error);
  } finally {
    chartLoading.taskStatus = false;
  }
};

const loadRecentProjects = async () => {
  try {
    const response = await getRecentProjects({ limit: 5 });
    if (response.code === 200 || response.success) {
      recentProjects.value = response.data || [];
    }
  } catch (error) {
    console.error("获取最近项目失败:", error);
  }
};

// 获取最近活动：合并首页 activities 与当前用户通知，按时间倒序，多拉一些供时间范围筛选
const fetchRecentActivities = async () => {
  try {
    const fetchLimit = 80;
    const [actRes, notifRes] = await Promise.all([
      getRecentActivities({ limit: fetchLimit }),
      getNotifications({ page: 1, size: fetchLimit }).catch(() => ({ data: {} })),
    ]);
    const list = [];
    if (actRes?.code === 200 || actRes?.success) {
      (actRes.data || []).forEach((a) => list.push({ ...a, _sort: a.created_at }));
    }
    const notifItems = notifRes?.data?.items || [];
    const formatReviewSummary = (s) => {
      if (!s || typeof s !== "string") return "";
      return s
        .replace(/结果：approved/g, "结果：已通过")
        .replace(/结果：rejected/g, "结果：已拒绝")
        .replace(/结果：pending/g, "结果：待审核");
    };
    notifItems.forEach((n) => {
      list.push({
        id: `n_${n.id}`,
        type: n.type || "notification",
        title: n.title,
        description: formatReviewSummary(n.summary || ""),
        created_at: n.created_at,
        _sort: n.created_at,
        _isNotification: true,
        // 保留通知路由信息，供点击跳转使用
        related_type: n.related_type,
        related_id: n.related_id,
      });
    });
    list.sort((a, b) => (b._sort || "").localeCompare(a._sort || ""));
    recentActivitiesAll.value = list.map(({ _sort, ...item }) => item);
  } catch (error) {
    console.error("获取最近活动失败:", error);
  }
};

/**
 * 根据活动项解析跳转路由：
 * - 通知类活动（_isNotification）：使用 getNotificationRoute 映射
 * - 普通活动：优先使用 related_type + related_id（统一走 getNotificationRoute），
 *   兼容仅有 id 前缀格式（task_X / device_X / user_X）的旧数据
 */
const getActivityRoute = (activity) => {
  if (!activity) return null;
  if (activity._isNotification) {
    return getNotificationRoute({ related_type: activity.related_type, related_id: activity.related_id });
  }
  // 优先使用后端明确返回的 related_type + related_id（覆盖 project/iteration/requirement 等所有类型）
  if (activity.related_type && activity.related_id) {
    return getNotificationRoute({ related_type: activity.related_type, related_id: activity.related_id });
  }
  // 兼容旧格式：从 id 前缀中提取
  const idStr = String(activity.id || "");
  if (idStr.startsWith("task_")) {
    return { path: "/test-tasks", query: { highlight_id: idStr.replace("task_", "") } };
  }
  if (idStr.startsWith("device_")) {
    return { path: "/devices", query: { highlight_device_id: idStr.replace("device_", "") } };
  }
  if (idStr.startsWith("user_")) {
    return { path: "/users", query: { user_id: idStr.replace("user_", "") } };
  }
  return null;
};

const handleActivityClick = (activity) => {
  const route = getActivityRoute(activity);
  if (route) {
    router.push(route);
  }
};

const refreshData = async () => {
  loading.value = true;
  try {
    await Promise.all([
      fetchStats(),
      fetchRecentActivities(),
      loadTaskTrendData(),
      loadDeviceStatusData(),
      loadTaskStatusData(),
      loadRecentProjects(),
    ]);
    ElMessage.success("数据刷新成功");
  } catch (error) {
    if (isPermissionError(error)) return;
    ElMessage.error("数据刷新失败");
  } finally {
    loading.value = false;
  }
};

const getProjectStatusType = (status) => {
  const types = {
    not_started: "info",
    in_progress: "warning",
    completed: "success",
    on_hold: "danger",
  };
  return types[status] || "info";
};

const getProjectStatusLabel = (status) => {
  const labels = {
    not_started: "未开始",
    in_progress: "进行中",
    completed: "已完成",
    on_hold: "已暂停",
  };
  return labels[status] || status;
};

onMounted(() => {
  systemSettingsStore.load();
  refreshData();
});
</script>

<style lang="scss" scoped>
.home {
  padding: 20px;
  background: var(--el-bg-color-page, #f5f7fa);
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  
  .header-left {
    .title {
      font-size: 28px;
      font-weight: 600;
      color: var(--el-text-color-primary, #303133);
      margin: 0 0 8px 0;
    }
    
    .subtitle {
      font-size: 14px;
      color: var(--el-text-color-secondary, #909399);
      margin: 0;
    }
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 30px;

  .stat-card {
    background: var(--el-bg-color, #fff);
    border-radius: 8px;
    padding: 24px;
    display: flex;
    align-items: center;
    gap: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.06);
    transition: all 0.3s;
    border: 1px solid var(--el-border-color-light, #ebeef5);

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.1);
    }

    &--clickable {
      cursor: pointer;

      &:hover {
        border-color: var(--el-color-primary-light-5, #a0cfff);
        box-shadow: 0 6px 24px 0 rgba(64, 158, 255, 0.15);
      }
    }

    .stat-icon {
      width: 56px;
      height: 56px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 26px;
      color: #fff;
      flex-shrink: 0;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);

      &.primary {
        background: linear-gradient(135deg, #5c6fd6 0%, #6b7ee8 100%);
      }

      &.success {
        background: linear-gradient(135deg, #52a852 0%, #6bc06b 100%);
      }

      &.warning {
        background: linear-gradient(135deg, #d4896b 0%, #e8a078 100%);
      }

      &.info {
        background: linear-gradient(135deg, #52a8a8 0%, #6bc0c0 100%);
      }
    }

    .stat-content {
      flex: 1;
      
      .stat-number {
        font-size: 28px;
        font-weight: 600;
        color: var(--el-text-color-primary, #303133);
        line-height: 1.2;
        margin-bottom: 6px;
      }

      .stat-label {
        font-size: 14px;
        color: var(--el-text-color-secondary, #909399);
        margin-bottom: 8px;
      }
      
      .stat-trend {
        display: inline-flex;
        align-items: center;
        gap: 2px;
        font-size: 12px;
        color: var(--el-text-color-secondary, #909399);
        
        &.positive {
          color: #67c23a;
        }
        
        &.negative {
          color: #f56c6c;
        }
      }
    }
  }
}

.charts-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 30px;

  .chart-card {
    background: var(--el-bg-color, #fff);
    border-radius: 8px;
    padding: 24px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.06);
    border: 1px solid var(--el-border-color-light, #ebeef5);

    .chart-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--el-border-color-lighter, #f0f2f5);

      h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: var(--el-text-color-primary, #303133);
      }
    }

    .chart-container {
      height: 320px;

      .chart {
        height: 100%;
        width: 100%;
      }
    }
  }
}

.activity-section {
  .card {
    background: var(--el-bg-color, #fff);
    border-radius: 8px;
    padding: 24px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.06);
    border: 1px solid var(--el-border-color-light, #ebeef5);

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 16px;

      .activity-time-select {
        width: 160px;
      }
      border-bottom: 1px solid var(--el-border-color-lighter, #f0f2f5);

      h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: var(--el-text-color-primary, #303133);
      }
    }

    .activity-list {
      max-height: 380px;
      overflow-y: auto;
      overflow-x: hidden;
      
      .activity-item {
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 16px 0;
        border-bottom: 1px solid var(--el-border-color-lighter, #f5f7fa);
        transition: all 0.2s;

        &:last-child {
          border-bottom: none;
        }
        
        &:hover {
          background-color: var(--el-fill-color-light, #fafafa);
          padding-left: 8px;
          margin-left: -8px;
          padding-right: 8px;
          margin-right: -8px;
          border-radius: 4px;
        }

        &.activity-item-clickable {
          cursor: pointer;

          &:hover {
            background-color: var(--el-color-primary-light-9, #ecf5ff);
          }
        }

        .activity-arrow {
          color: var(--el-text-color-placeholder, #c0c4cc);
          flex-shrink: 0;
          font-size: 14px;
        }

        .activity-icon {
          width: 40px;
          height: 40px;
          border-radius: 10px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 18px;
          color: #fff;
          flex-shrink: 0;

          &.task {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          }

          &.device {
            background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
          }

          &.user {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
          }

          &.project {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
          }

          &.iteration {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
          }

          &.requirement {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
          }

          &.suite {
            background: linear-gradient(135deg, #fa709a 0%, #a18cd1 100%);
          }

          &.is-notification {
            background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
          }
        }

        .activity-content {
          flex: 1;
          min-width: 0;

          .activity-title {
            font-size: 14px;
            font-weight: 500;
            color: var(--el-text-color-primary, #303133);
            margin-bottom: 6px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;

            &.activity-title-link {
              color: var(--el-color-primary);
            }
          }

          .activity-desc {
            font-size: 13px;
            color: var(--el-text-color-regular, #606266);
            margin-bottom: 6px;
            line-height: 1.5;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }

          .activity-time {
            font-size: 12px;
            color: var(--el-text-color-secondary, #909399);
          }
        }
      }
    }
  }
}

.charts-grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 30px;

  .chart-card {
    background: var(--el-bg-color, #fff);
    border-radius: 8px;
    padding: 24px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.06);
    border: 1px solid var(--el-border-color-light, #ebeef5);

    .chart-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--el-border-color-lighter, #f0f2f5);

      h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: var(--el-text-color-primary, #303133);
      }
    }

    .chart-container {
      height: 280px;

      .chart {
        height: 100%;
        width: 100%;
      }
    }
    
    .project-list {
      max-height: 280px;
      overflow-y: auto;
      overflow-x: hidden;
      padding-right: 8px;
      margin-right: -8px;
      
      .project-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 14px 8px 14px 0;
        border-bottom: 1px solid var(--el-border-color-lighter, #f5f7fa);
        transition: all 0.2s;
        gap: 12px;
        
        &:last-child {
          border-bottom: none;
        }
        
        &:hover {
          background-color: var(--el-fill-color-light, #fafafa);
          padding-left: 8px;
          padding-right: 8px;
          margin-left: -8px;
          border-radius: 4px;
        }
        
        .project-info {
          flex: 1;
          min-width: 0;
          
          .project-name {
            font-size: 14px;
            font-weight: 500;
            color: var(--el-text-color-primary, #303133);
            margin-bottom: 8px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }
          
          .project-meta {
            display: flex;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
            
            .project-owner {
              font-size: 13px;
              color: var(--el-text-color-secondary, #909399);
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
            }
          }
        }
        
        .project-time {
          font-size: 12px;
          color: var(--el-text-color-secondary, #C0C4CC);
          white-space: nowrap;
          flex-shrink: 0;
          margin-left: 8px;
        }
      }
    }
  }
}

@media (max-width: 1400px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1200px) {
  .charts-grid,
  .charts-grid-2 {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .home {
    padding: 15px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
    
    .header-left {
      .title {
        font-size: 24px;
      }
    }
  }

  .stats-grid {
    grid-template-columns: 1fr;
    gap: 15px;

    .stat-card {
      padding: 20px;

      .stat-icon {
        width: 48px;
        height: 48px;
        font-size: 22px;
      }

      .stat-content {
        .stat-number {
          font-size: 24px;
        }
      }
    }
  }
  
  .charts-grid,
  .charts-grid-2 {
    .chart-card {
      padding: 16px;
      
      .chart-container {
        height: 260px;
      }
    }
  }
}
</style>
