<template>
  <div class="iteration-detail">
    <!-- 主体内容 -->
    <div class="main-content">
      <!-- 基本信息卡片 -->
      <el-card
        shadow="hover"
        class="info-card"
      >
        <template #header>
          <div class="card-header">
            <h2>
              迭代名称: {{ iterationDetail.iteration_name || "未知迭代" }}
            </h2>
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
          <!-- 左边列 -->
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(iterationDetail.status)">
              {{ getStatusText(iterationDetail.status) || "-" }}
            </el-tag>
          </el-descriptions-item>

          <!-- 右边列 -->
          <el-descriptions-item label="所属项目">
            {{ iterationDetail.project_name || "-" }}
          </el-descriptions-item>

          <!-- 左边列 -->
          <el-descriptions-item label="测试版本">
            {{ iterationDetail.version || "-" }}
          </el-descriptions-item>

          <!-- 右边列 -->
          <el-descriptions-item label="开始日期">
            {{ formatDateTime(iterationDetail.start_date) || "-" }}
          </el-descriptions-item>

          <!-- 左边列 -->
          <el-descriptions-item label="创建人">
            {{ iterationDetail.created_by_name || "-" }}
          </el-descriptions-item>

          <!-- 右边列 -->
          <el-descriptions-item label="结束日期">
            {{ formatDateTime(iterationDetail.end_date) || "-" }}
          </el-descriptions-item>

          <!-- 左边列 -->
          <el-descriptions-item label="更新人">
            {{ iterationDetail.updated_by_name || "-" }}
          </el-descriptions-item>

          <!-- 右边列 -->
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(iterationDetail.created_at) || "-" }}
          </el-descriptions-item>

          <!-- 左边列 -->
          <el-descriptions-item label="迭代描述">
            {{ iterationDetail.description || "-" }}
          </el-descriptions-item>

          <!-- 右边列 -->
          <el-descriptions-item label="更新时间">
            {{ formatDateTime(iterationDetail.updated_at) || "-" }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 统计图表区域 -->
      <!-- 迭代进度日历 -->
      <el-row
        :gutter="20"
        class="chart-section"
      >
        <el-col :span="24">
          <el-card shadow="hover">
            <div class="calendar-container">
              <div
                v-if="iterationDetail.start_date && iterationDetail.end_date"
                class="iteration-calendar"
              >
                <div class="calendar-header">
                  <div class="date-range">
                    <span class="date-label">开始日期：</span>
                    <span class="date-value">{{
                      formatDateTime(iterationDetail.start_date)
                    }}</span>
                  </div>
                  <div class="date-range">
                    <span class="date-label">结束日期：</span>
                    <span class="date-value">{{
                      formatDateTime(iterationDetail.end_date)
                    }}</span>
                  </div>
                  <div class="date-range">
                    <span class="date-label">持续时间：</span>
                    <span class="date-value">{{
                      calculateDuration(
                        iterationDetail.start_date,
                        iterationDetail.end_date,
                      )
                    }}
                      天</span>
                  </div>
                </div>
                <div class="calendar-progress">
                  <div class="progress-label">
                    <span>需求分布统计：</span>
                    <span class="progress-percentage">{{
                      calculateRequirementProgress(
                        iterationDetail.requirement_stats,
                      )
                    }}%</span>
                  </div>
                  <div class="chart-container">
                    <v-chart
                      v-if="iterationDetail.requirement_stats"
                      :option="barChartOption"
                      autoresize
                      style="height: 250px"
                    />
                    <div
                      v-else
                      class="empty-chart"
                    >
                      暂无进度数据
                    </div>
                  </div>
                </div>
              </div>
              <div
                v-else
                class="empty-chart"
              >
                暂无进度数据
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑迭代"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="iterationForm"
        :model="iterationForm"
        :rules="iterationRules"
        label-width="120px"
      >
        <el-form-item
          label="迭代名称"
          prop="iteration_name"
          required
        >
          <el-input
            v-model="iterationForm.iteration_name"
            placeholder="请输入迭代名称"
          />
        </el-form-item>
        <el-form-item
          label="迭代目标"
          prop="goal"
          required
        >
          <el-input
            v-model="iterationForm.goal"
            type="textarea"
            placeholder="请输入迭代目标"
            :rows="3"
          />
        </el-form-item>
        <el-form-item
          label="测试版本"
          prop="version"
          required
        >
          <el-input
            v-model="iterationForm.version"
            placeholder="请输入测试版本"
          />
        </el-form-item>
        <el-form-item
          label="开始日期"
          prop="start_date"
          required
        >
          <el-date-picker
            v-model="iterationForm.start_date"
            type="datetime"
            placeholder="选择开始日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item
          label="结束日期"
          prop="end_date"
          required
        >
          <el-date-picker
            v-model="iterationForm.end_date"
            type="datetime"
            placeholder="选择结束日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item
          label="状态"
          prop="status"
          required
        >
          <el-select
            v-model="iterationForm.status"
            placeholder="选择状态"
          >
            <el-option
              label="计划中"
              value="planning"
            />
            <el-option
              label="进行中"
              value="active"
            />
            <el-option
              label="已完成"
              value="completed"
            />
            <el-option
              label="已取消"
              value="cancelled"
            />
          </el-select>
        </el-form-item>
        <el-form-item
          label="备注"
          prop="description"
        >
          <el-input
            v-model="iterationForm.description"
            type="textarea"
            placeholder="请输入备注信息"
            :rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="editDialogVisible = false">
            取消
          </el-button>
          <el-button
            type="primary"
            @click="submitForm"
          >
            确定
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getIteration, updateIteration } from "@/api/iteration";
import { ElMessage } from "element-plus";
import { Edit, ArrowLeft } from "@element-plus/icons-vue";
import VChart from "vue-echarts";
// 导入ECharts核心模块和渲染器
import * as echarts from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
// 导入柱状图组件
import { BarChart } from "echarts/charts";
// 导入必要的组件
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  DatasetComponent,
  TransformComponent,
} from "echarts/components";

// 注册必须的组件
echarts.use([
  CanvasRenderer,
  BarChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  DatasetComponent,
  TransformComponent,
]);

export default {
  name: "IterationDetail",
  components: {
    Edit,
    ArrowLeft,
    VChart,
  },
  setup() {
    const route = useRoute();
    const router = useRouter();
    const iterationId = computed(() => route.params.id);

    // 迭代详情数据
    const iterationDetail = ref({});
    const loading = ref(false);

    // 编辑对话框
    const editDialogVisible = ref(false);
    const iterationForm = reactive({
      id: null,
      iteration_name: "",
      goal: "",
      version: "",
      start_date: "",
      end_date: "",
      status: "planning",
      description: "",
    });

    const iterationRules = {
      iteration_name: [
        { required: true, message: "请输入迭代名称", trigger: "blur" },
        {
          min: 2,
          max: 50,
          message: "迭代名称长度在 2 到 50 个字符",
          trigger: "blur",
        },
      ],
      goal: [
        { required: true, message: "请输入迭代目标", trigger: "blur" },
        {
          min: 5,
          max: 200,
          message: "迭代目标长度在 5 到 200 个字符",
          trigger: "blur",
        },
      ],
      version: [
        { required: true, message: "请输入测试版本", trigger: "blur" },
        {
          min: 1,
          max: 30,
          message: "测试版本长度在 1 到 30 个字符",
          trigger: "blur",
        },
      ],
      start_date: [
        { required: true, message: "请选择开始日期", trigger: "change" },
      ],
      end_date: [
        { required: true, message: "请选择结束日期", trigger: "change" },
        {
          validator: (rule, value, callback) => {
            if (iterationForm.start_date && value < iterationForm.start_date) {
              callback(new Error("结束日期不能早于开始日期"));
            } else {
              callback();
            }
          },
          trigger: "change",
        },
      ],
      status: [{ required: true, message: "请选择状态", trigger: "change" }],
    };

    // 获取迭代详情
    const fetchIterationDetail = async () => {
      if (!iterationId.value) return;
      loading.value = true;
      try {
        const response = await getIteration(iterationId.value);
        if (response && response.code === 200 && response.data) {
          iterationDetail.value = response.data;
        }
      } catch (error) {
        console.error("获取迭代详情失败:", error);
        ElMessage.error("获取迭代详情失败: " + (error?.message || "未知错误"));
      } finally {
        loading.value = false;
      }
    };

    // 返回列表
    const handleBack = () => {
      router.push("/iterations");
    };

    // 编辑迭代
    const handleEdit = () => {
      iterationForm.id = iterationDetail.value.id;
      iterationForm.iteration_name = iterationDetail.value.iteration_name;
      iterationForm.goal = iterationDetail.value.goal;
      iterationForm.version = iterationDetail.value.version;
      iterationForm.start_date = iterationDetail.value.start_date;
      iterationForm.end_date = iterationDetail.value.end_date;
      iterationForm.status = iterationDetail.value.status;
      iterationForm.description = iterationDetail.value.description;
      editDialogVisible.value = true;
    };

    // 重置表单
    const resetForm = () => {
      iterationForm.id = null;
      iterationForm.iteration_name = "";
      iterationForm.goal = "";
      iterationForm.version = "";
      iterationForm.start_date = "";
      iterationForm.end_date = "";
      iterationForm.status = "planning";
      iterationForm.description = "";
      if (this.$refs.iterationForm) {
        this.$refs.iterationForm.resetFields();
      }
    };

    // 提交表单
    const submitForm = async () => {
      if (!this.$refs.iterationForm) return;
      try {
        await this.$refs.iterationForm.validate();

        const iterationData = {
          iteration_name: iterationForm.iteration_name,
          goal: iterationForm.goal,
          version: iterationForm.version,
          start_date: iterationForm.start_date,
          end_date: iterationForm.end_date,
          status: iterationForm.status,
          description: iterationForm.description,
        };

        const response = await updateIteration(iterationForm.id, iterationData);
        if (response && response.code === 200) {
          ElMessage.success("迭代更新成功");
          editDialogVisible.value = false;
          fetchIterationDetail();
        }
      } catch (error) {
        console.error("更新迭代失败:", error);
        ElMessage.error("更新迭代失败: " + (error?.message || "未知错误"));
      }
    };

    // 根据状态获取标签类型
    const getStatusType = (status) => {
      const statusMap = {
        planning: "info",
        active: "primary",
        completed: "success",
        cancelled: "danger",
      };
      return statusMap[status] || "info";
    };

    // 根据状态获取文本
    const getStatusText = (status) => {
      const statusMap = {
        planning: "计划中",
        active: "进行中",
        completed: "已完成",
        cancelled: "已取消",
      };
      return statusMap[status] || status;
    };

    // 格式化时间
    const formatDateTime = (dateTime) => {
      if (!dateTime) return "-";
      return dateTime.replace("T", " ");
    };

    // 计算需求进度百分比
    const calculateRequirementProgress = (requirementStats) => {
      if (!requirementStats || !requirementStats.total) return 0;

      const total = requirementStats.total;
      const completed = requirementStats.completed || 0;
      const progress = Math.round((completed / total) * 100);

      return Math.min(progress, 100);
    };

    // 计算迭代持续时间（天数）
    const calculateDuration = (startDate, endDate) => {
      if (!startDate || !endDate) return 0;

      const start = new Date(startDate);
      const end = new Date(endDate);
      const diffTime = Math.abs(end - start);
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1; // 包含开始和结束日期

      return diffDays;
    };

    // 柱状图配置项
    const barChartOption = computed(() => {
      const requirementStats = iterationDetail.value.requirement_stats || {};

      // 准备数据
      const categories = ["未开始", "进行中", "已完成", "已取消"];
      const data = [
        requirementStats.new || 0,
        requirementStats.in_progress || 0,
        requirementStats.completed || 0,
        requirementStats.cancelled || 0,
      ];

      // 颜色配置
      const colors = ["#909399", "#409eff", "#67c23a", "#f56c6c"];

      return {
        tooltip: {
          trigger: "axis",
          axisPointer: {
            type: "shadow",
          },
          formatter: "{b}: {c} ({d}%)",
        },
        grid: {
          left: "3%",
          right: "4%",
          bottom: "3%",
          containLabel: true,
        },
        xAxis: {
          type: "category",
          data: categories,
          axisLabel: {
            interval: 0,
          },
        },
        yAxis: {
          type: "value",
          name: "需求数量",
        },
        series: [
          {
            name: "需求状态",
            type: "bar",
            data: data,
            itemStyle: {
              color: (params) => colors[params.dataIndex],
            },
            label: {
              show: true,
              position: "top",
              formatter: "{c}",
            },
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: "rgba(0, 0, 0, 0.5)",
              },
            },
            barWidth: "60%",
          },
        ],
      };
    });

    // 组件挂载时获取数据
    onMounted(() => {
      fetchIterationDetail();
    });

    return {
      iterationDetail,
      loading,
      editDialogVisible,
      iterationForm,
      iterationRules,
      fetchIterationDetail,
      handleBack,
      handleEdit,
      resetForm,
      submitForm,
      getStatusType,
      getStatusText,
      formatDateTime,
      calculateRequirementProgress,
      calculateDuration,
      barChartOption,
    };
  },
};
</script>

<style scoped>
.iteration-detail {
  padding: 20px;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-card {
  margin-bottom: 20px;
  border-radius: 8px;
  overflow: hidden;
}

.info-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #303133;
  padding: 5px 0;
}

.info-card h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.chart-section {
  margin-bottom: 20px;
}

.chart-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

.empty-chart {
  text-align: center;
  color: #909399;
  font-size: 14px;
  padding: 40px 0;
}

.stats-card {
  margin-bottom: 20px;
  border-radius: 8px;
  overflow: hidden;
}

.stats-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #303133;
  padding: 5px 0;
}

.stats-card .card-header span {
  font-weight: 700;
  font-size: 16px;
}

.stats-card h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.empty-table {
  text-align: center;
  color: #909399;
  font-size: 14px;
  padding: 40px 0;
}

/* 标签页样式 */
.el-tabs__header {
  margin-bottom: 20px;
}

/* 表格样式 */
.el-table {
  margin-top: 16px;
}

/* 日历样式 */
.calendar-container {
  padding: 20px;
}

.iteration-calendar {
  width: 100%;
}

.calendar-header {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.date-range {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-label {
  font-weight: 500;
  color: #606266;
}

.date-value {
  color: #303133;
  font-weight: 600;
}

.calendar-progress {
  margin-top: 20px;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.progress-percentage {
  font-weight: 600;
  color: #409eff;
  font-size: 18px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .info-card .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .chart-section .el-col {
    margin-bottom: 20px;
  }

  .el-descriptions :deep(.el-descriptions__item-label) {
    background-color: #fafafa;
  }

  .calendar-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .progress-label {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
}
</style>
