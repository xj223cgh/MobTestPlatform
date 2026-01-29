<template>
  <div class="home">
    <div class="page-header">
      <h1 class="title">
        首页
      </h1>
      <div class="actions">
        <el-button
          type="primary"
          @click="refreshData"
        >
          <el-icon><Refresh /></el-icon>
          刷新数据
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
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">
            {{ stats.users }}
          </div>
          <div class="stat-label">
            用户总数
          </div>
        </div>
      </div>

      <div
        v-loading="loading"
        class="stat-card"
      >
        <div class="stat-icon success">
          <el-icon><Monitor /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">
            {{ stats.devices }}
          </div>
          <div class="stat-label">
            设备总数
          </div>
        </div>
      </div>

      <div
        v-loading="loading"
        class="stat-card"
      >
        <div class="stat-icon danger">
          <el-icon><List /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">
            {{ stats.testTasks }}
          </div>
          <div class="stat-label">
            测试任务
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
          />
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

// 统计数据
const stats = reactive({
  users: 0,
  devices: 0,
  testTasks: 0,
});

// 任务趋势周期
const taskTrendPeriod = ref("7d");

// 最近活动
const recentActivities = ref([]);

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
    data: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
  },
  yAxis: {
    type: "value",
  },
  series: [
    {
      name: "完成任务",
      type: "line",
      smooth: true,
      data: [12, 13, 10, 13, 9, 23, 21],
      itemStyle: {
        color: "#67C23A",
      },
    },
    {
      name: "失败任务",
      type: "line",
      smooth: true,
      data: [5, 3, 7, 2, 4, 6, 3],
      itemStyle: {
        color: "#F56C6C",
      },
    },
    {
      name: "进行中任务",
      type: "line",
      smooth: true,
      data: [8, 12, 15, 10, 13, 11, 14],
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
      data: [
        { value: 335, name: "在线", itemStyle: { color: "#67C23A" } },
        { value: 310, name: "离线", itemStyle: { color: "#909399" } },
        { value: 234, name: "忙碌", itemStyle: { color: "#E6A23C" } },
        { value: 135, name: "维护", itemStyle: { color: "#F56C6C" } },
      ],
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
    if (response.code === 200) {
      Object.assign(stats, response.data);
    } else {
      // 如果API调用失败，使用默认数据
      stats.users = 156;
      stats.devices = 42;
      stats.testTasks = 324;
    }
  } catch (error) {
    console.error("获取统计数据失败:", error);
    // 使用默认数据
    stats.users = 156;
    stats.devices = 42;
    stats.testTasks = 324;
  }
};

// 获取最近活动
const fetchRecentActivities = async () => {
  try {
    const response = await getRecentActivities({ limit: 10 });
    if (response.code === 200) {
      recentActivities.value = response.data;
    } else {
      // 如果API调用失败，使用默认数据
      recentActivities.value = [
        {
          id: 1,
          type: "task",
          title: "测试任务完成",
          description: "Android登录功能测试任务已成功完成",
          created_at: new Date(Date.now() - 1000 * 60 * 5),
        },
        {
          id: 2,
          type: "device",
          title: "设备上线",
          description: "设备 iPhone 14 Pro 已连接并上线",
          created_at: new Date(Date.now() - 1000 * 60 * 15),
        },
        {
          id: 3,
          type: "user",
          title: "新用户注册",
          description: "测试工程师 张三 已注册账号",
          created_at: new Date(Date.now() - 1000 * 60 * 30),
        },
      ];
    }
  } catch (error) {
    console.error("获取最近活动失败:", error);
    // 使用默认数据
    recentActivities.value = [
      {
        id: 1,
        type: "task",
        title: "测试任务完成",
        description: "Android登录功能测试任务已成功完成",
        created_at: new Date(Date.now() - 1000 * 60 * 5),
      },
      {
        id: 2,
        type: "device",
        title: "设备上线",
        description: "设备 iPhone 14 Pro 已连接并上线",
        created_at: new Date(Date.now() - 1000 * 60 * 15),
      },
      {
        id: 3,
        type: "user",
        title: "新用户注册",
        description: "测试工程师 张三 已注册账号",
        created_at: new Date(Date.now() - 1000 * 60 * 30),
      },
    ];
  }
};

// 刷新数据
const refreshData = async () => {
  loading.value = true;
  try {
    await Promise.all([fetchStats(), fetchRecentActivities()]);
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

// 组件挂载时获取数据
onMounted(() => {
  refreshData();
});
</script>

<style lang="scss" scoped>
.home {
  padding: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;

  .stat-card {
    background: #fff;
    border-radius: $border-radius-base;
    padding: 25px;
    display: flex;
    align-items: center;
    gap: 20px;
    box-shadow: $box-shadow-light;
    transition: $transition;

    &:hover {
      transform: translateY(-2px);
      box-shadow: $box-shadow-dark;
    }

    .stat-icon {
      width: 60px;
      height: 60px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      color: #fff;

      &.primary {
        background: linear-gradient(135deg, #409eff, #66b1ff);
      }

      &.success {
        background: linear-gradient(135deg, #67c23a, #85ce61);
      }

      &.warning {
        background: linear-gradient(135deg, #e6a23c, #ebb563);
      }

      &.danger {
        background: linear-gradient(135deg, #f56c6c, #f78989);
      }
    }

    .stat-content {
      .stat-number {
        font-size: 32px;
        font-weight: 600;
        color: $text-primary;
        line-height: 1;
        margin-bottom: 5px;
      }

      .stat-label {
        font-size: 14px;
        color: $text-secondary;
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
    border-radius: $border-radius-base;
    padding: 20px;
    box-shadow: $box-shadow-light;

    .chart-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;

      h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: $text-primary;
      }
    }

    .chart-container {
      height: 300px;

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
    border-radius: $border-radius-base;
    padding: 20px;
    box-shadow: $box-shadow-light;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;

      h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: $text-primary;
      }
    }

    .activity-list {
      .activity-item {
        display: flex;
        gap: 15px;
        padding: 15px 0;
        border-bottom: 1px solid $border-extra-light;

        &:last-child {
          border-bottom: none;
        }

        .activity-icon {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 16px;
          color: #fff;
          flex-shrink: 0;

          &.task {
            background: linear-gradient(135deg, #409eff, #66b1ff);
          }

          &.device {
            background: linear-gradient(135deg, #67c23a, #85ce61);
          }

          &.user {
            background: linear-gradient(135deg, #e6a23c, #ebb563);
          }
        }

        .activity-content {
          flex: 1;

          .activity-title {
            font-size: 14px;
            font-weight: 500;
            color: $text-primary;
            margin-bottom: 5px;
          }

          .activity-desc {
            font-size: 13px;
            color: $text-regular;
            margin-bottom: 5px;
          }

          .activity-time {
            font-size: 12px;
            color: $text-secondary;
          }
        }
      }
    }
  }
}

// 响应式
@media (max-width: 1200px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .home {
    padding: 10px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
    gap: 15px;

    .stat-card {
      padding: 20px;

      .stat-icon {
        width: 50px;
        height: 50px;
        font-size: 20px;
      }

      .stat-content {
        .stat-number {
          font-size: 24px;
        }
      }
    }
  }
}
</style>
