<template>
  <div class="home">
    <div class="page-header">
      <div class="header-left">
        <h1 class="title">移动测试平台</h1>
        <p class="subtitle">专业的移动应用测试管理系统</p>
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
        class="stat-card"
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
        class="stat-card"
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
        class="stat-card"
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
        class="stat-card"
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

    <!-- 最近活动 -->
    <div class="activity-section">
      <div class="card">
        <div class="card-header">
          <h3>最近活动</h3>
          <el-link
            type="primary"
            @click="viewAllActivities"
          >
            查看全部
          </el-link>
        </div>
        <div class="activity-list">
          <div
            v-for="activity in recentActivities"
            :key="activity.id"
            class="activity-item"
          >
            <div
              class="activity-icon"
              :class="activity.type"
            >
              <el-icon>
                <component :is="getActivityIcon(activity.type)" />
              </el-icon>
            </div>
            <div class="activity-content">
              <div class="activity-title">
                {{ activity.title }}
              </div>
              <div class="activity-desc">
                {{ activity.description }}
              </div>
              <div class="activity-time">
                {{ formatTime(activity.created_at) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from "vue";
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
import dayjs from "dayjs";
import {
  getHomeStats,
  getRecentActivities,
  getTaskTrendData,
  getDeviceStatusData,
  getRecentProjects,
  getTaskStatusDistribution,
} from "@/api/home";

// 注册 ECharts 组件
use([
  CanvasRenderer,
  LineChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
]);

// 加载状态
const loading = ref(false);
const chartLoading = reactive({
  taskTrend: false,
  deviceStatus: false,
  taskStatus: false,
});

// 统计数据
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

// 任务趋势周期
const taskTrendPeriod = ref("7d");

// 最近活动
const recentActivities = ref([]);

// 最近项目
const recentProjects = ref([]);

// 趋势数据
const taskTrendData = reactive({
  dates: [],
  completed: [],
  failed: [],
  running: [],
});

// 设备状态数据
const deviceStatusData = ref([]);

// 任务状态数据
const taskStatusData = ref([]);

// 测试任务趋势图配置
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

// 设备状态分布图配置
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

// 任务状态分布图配置
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

// 获取活动图标
const getActivityIcon = (type) => {
  const iconMap = {
    task: "List",
    device: "Monitor",
    user: "User",
  };
  return iconMap[type] || "Document";
};

// 格式化时间
const formatTime = (time) => {
  return dayjs(time).format("YYYY-MM-DD HH:mm:ss");
};

// 获取统计数据
const fetchStats = async () => {
  try {
    const response = await getHomeStats();
    if (response.code === 200 || response.success) {
      Object.assign(stats, response.data);
    }
  } catch (error) {
    console.error("获取统计数据失败:", error);
    ElMessage.error("获取统计数据失败");
  }
};

// 加载任务趋势数据
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

// 加载设备状态数据
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

// 加载任务状态数据
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

// 加载最近项目
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

// 获取最近活动
const fetchRecentActivities = async () => {
  try {
    const response = await getRecentActivities({ limit: 10 });
    if (response.code === 200 || response.success) {
      recentActivities.value = response.data || [];
    }
  } catch (error) {
    console.error("获取最近活动失败:", error);
  }
};

// 刷新数据
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
    ElMessage.error("数据刷新失败");
  } finally {
    loading.value = false;
  }
};

// 查看所有活动
const viewAllActivities = () => {
  // TODO: 跳转到活动页面
  ElMessage.info("查看全部活动功能待完善");
};

// 获取项目状态标签类型
const getProjectStatusType = (status) => {
  const types = {
    not_started: "info",
    in_progress: "warning",
    completed: "success",
    on_hold: "danger",
  };
  return types[status] || "info";
};

// 获取项目状态标签文本
const getProjectStatusLabel = (status) => {
  const labels = {
    not_started: "未开始",
    in_progress: "进行中",
    completed: "已完成",
    on_hold: "已暂停",
  };
  return labels[status] || status;
};

// 组件挂载时获取数据
onMounted(() => {
  refreshData();
});
</script>

<style lang="scss" scoped>
.home {
  padding: 20px;
  background: #f5f7fa;
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
      color: #303133;
      margin: 0 0 8px 0;
    }
    
    .subtitle {
      font-size: 14px;
      color: #909399;
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
    background: #fff;
    border-radius: 8px;
    padding: 24px;
    display: flex;
    align-items: center;
    gap: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.06);
    transition: all 0.3s;
    border: 1px solid #ebeef5;

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.1);
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

      &.primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      }

      &.success {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
      }

      &.warning {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
      }

      &.info {
        background: linear-gradient(135deg, #30cfd0 0%, #330867 100%);
      }
    }

    .stat-content {
      flex: 1;
      
      .stat-number {
        font-size: 28px;
        font-weight: 600;
        color: #303133;
        line-height: 1.2;
        margin-bottom: 6px;
      }

      .stat-label {
        font-size: 14px;
        color: #909399;
        margin-bottom: 8px;
      }
      
      .stat-trend {
        display: inline-flex;
        align-items: center;
        gap: 2px;
        font-size: 12px;
        color: #909399;
        
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
    background: #fff;
    border-radius: 8px;
    padding: 24px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.06);
    border: 1px solid #ebeef5;

    .chart-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 16px;
      border-bottom: 1px solid #f0f2f5;

      h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: #303133;
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
    background: #fff;
    border-radius: 8px;
    padding: 24px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.06);
    border: 1px solid #ebeef5;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 16px;
      border-bottom: 1px solid #f0f2f5;

      h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: #303133;
      }
    }

    .activity-list {
      max-height: 380px;
      overflow-y: auto;
      overflow-x: hidden;
      
      .activity-item {
        display: flex;
        gap: 15px;
        padding: 16px 0;
        border-bottom: 1px solid #f5f7fa;
        transition: all 0.2s;

        &:last-child {
          border-bottom: none;
        }
        
        &:hover {
          background-color: #fafafa;
          padding-left: 8px;
          margin-left: -8px;
          padding-right: 8px;
          margin-right: -8px;
          border-radius: 4px;
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
        }

        .activity-content {
          flex: 1;
          min-width: 0;

          .activity-title {
            font-size: 14px;
            font-weight: 500;
            color: #303133;
            margin-bottom: 6px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }

          .activity-desc {
            font-size: 13px;
            color: #606266;
            margin-bottom: 6px;
            line-height: 1.5;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }

          .activity-time {
            font-size: 12px;
            color: #909399;
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
    background: #fff;
    border-radius: 8px;
    padding: 24px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.06);
    border: 1px solid #ebeef5;

    .chart-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 16px;
      border-bottom: 1px solid #f0f2f5;

      h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: #303133;
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
        border-bottom: 1px solid #f5f7fa;
        transition: all 0.2s;
        gap: 12px;
        
        &:last-child {
          border-bottom: none;
        }
        
        &:hover {
          background-color: #fafafa;
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
            color: #303133;
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
              color: #909399;
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
            }
          }
        }
        
        .project-time {
          font-size: 12px;
          color: #C0C4CC;
          white-space: nowrap;
          flex-shrink: 0;
          margin-left: 8px;
        }
      }
    }
  }
}

// 响应式
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
