<template>
  <div class="report-detail-page">
    <div class="page-header">
      <div class="header-left">
        <el-button type="primary" size="small" @click="handleBack">
          <el-icon><ArrowLeft /></el-icon>
          返回报告列表
        </el-button>
        <h2 style="margin-left: 20px;">{{ currentReport?.task_name || '报告详情' }}</h2>
      </div>
      <div class="header-right">
        <el-button size="small" @click="handleExportReport">
          <el-icon><Download /></el-icon>
          导出报告
        </el-button>
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <div v-else-if="currentReport" class="report-content">
      <!-- 报告概览 -->
      <el-card class="report-overview" shadow="hover">
        <template #header>
          <div class="card-header">
            <h4>报告概览</h4>
          </div>
        </template>

        <div class="overview-content">
          <div class="overview-info">
            <div class="info-item">
              <span class="label">任务ID：</span>
              <span class="value">{{ currentReport.id }}</span>
            </div>
            <div class="info-item">
              <span class="label">任务类型：</span>
              <el-tag :type="currentReport.task_type === 'test_case' ? 'primary' : 'success'">
                {{ currentReport.task_type === 'test_case' ? '测试用例任务' : '设备脚本任务' }}
              </el-tag>
            </div>
            <div class="info-item">
              <span class="label">任务状态：</span>
              <el-tag :type="getStatusTagType(currentReport.status)">
                {{ getStatusLabel(currentReport.status) }}
              </el-tag>
            </div>
            <div class="info-item">
              <span class="label">创建人：</span>
              <span class="value">{{ currentReport.created_by }}</span>
            </div>
            <div class="info-item">
              <span class="label">创建时间：</span>
              <span class="value">{{ formatDateTime(currentReport.created_at) }}</span>
            </div>
            <div class="info-item">
              <span class="label">完成时间：</span>
              <span class="value">{{ currentReport.completed_at ? formatDateTime(currentReport.completed_at) : '-' }}</span>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 测试用例报告内容 -->
      <el-card v-if="currentReport.task_type === 'test_case'" class="report-content-section" shadow="hover" style="margin-top: 20px">
        <template #header>
          <div class="card-header">
            <h4>测试用例执行情况</h4>
          </div>
        </template>

        <div class="test-case-report">
          <!-- 统计卡片 -->
          <div class="stats-cards">
            <el-card class="stat-card" shadow="hover">
              <div class="stat-content">
                <div class="stat-number">{{ reportSummary.total_cases }}</div>
                <div class="stat-label">总用例数</div>
              </div>
            </el-card>
            <el-card class="stat-card" shadow="hover">
              <div class="stat-content">
                <div class="stat-number">{{ reportSummary.executed_cases }}</div>
                <div class="stat-label">已执行</div>
              </div>
            </el-card>
            <el-card class="stat-card success" shadow="hover">
              <div class="stat-content">
                <div class="stat-number">{{ reportSummary.pass_count }}</div>
                <div class="stat-label">通过</div>
              </div>
            </el-card>
            <el-card class="stat-card danger" shadow="hover">
              <div class="stat-content">
                <div class="stat-number">{{ reportSummary.fail_count }}</div>
                <div class="stat-label">失败</div>
              </div>
            </el-card>
            <el-card class="stat-card warning" shadow="hover">
              <div class="stat-content">
                <div class="stat-number">{{ reportSummary.blocked_count }}</div>
                <div class="stat-label">阻塞</div>
              </div>
            </el-card>
            <el-card class="stat-card info" shadow="hover">
              <div class="stat-content">
                <div class="stat-number">{{ reportSummary.pass_rate }}%</div>
                <div class="stat-label">通过率</div>
              </div>
            </el-card>
          </div>

          <!-- 执行结果表格 -->
          <el-table
            :data="reportDetails"
            stripe
            border
            style="margin-top: 20px; width: 100%"
            fit
          >
            <el-table-column prop="case_id" label="用例ID" min-width="80" align="center" />
            <el-table-column prop="case_title" label="用例标题" min-width="250" />
            <el-table-column prop="status" label="执行状态" min-width="100" align="center">
              <template #default="{ row }">
                <el-tag
                  :type="row.status === 'pass' ? 'success' : row.status === 'fail' ? 'danger' : row.status === 'blocked' ? 'warning' : 'info'"
                >
                  {{ row.status === 'pass' ? '通过' : row.status === 'fail' ? '失败' : row.status === 'blocked' ? '阻塞' : '不适用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="executed_by" label="执行人" min-width="100" align="center" />
            <el-table-column prop="executed_at" label="执行时间" min-width="160" align="center">
              <template #default="{ row }">
                {{ row.executed_at ? formatDateTime(row.executed_at) : '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="actual_result" label="实际结果" min-width="200" />
            <el-table-column prop="remarks" label="备注" min-width="150" />
          </el-table>
        </div>
      </el-card>

      <!-- 设备脚本报告内容 -->
      <el-card v-else-if="currentReport.task_type === 'device_script'" class="report-content-section" shadow="hover" style="margin-top: 20px">
        <template #header>
          <div class="card-header">
            <h4>设备脚本执行情况</h4>
          </div>
        </template>

        <div class="device-script-report">
          <!-- 脚本信息 -->
          <el-card class="script-info" shadow="hover" style="margin-bottom: 20px">
            <div class="script-info-content">
              <div class="info-item">
                <span class="label">脚本文件名：</span>
                <span class="value">{{ currentReport.script_file || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">执行命令：</span>
                <span class="value">{{ currentReport.command || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">文件路径：</span>
                <span class="value">{{ currentReport.file_path || '-' }}</span>
              </div>
            </div>
          </el-card>

          <!-- 执行结果统计 -->
          <div class="stats-cards">
            <el-card class="stat-card" shadow="hover">
              <div class="stat-content">
                <div class="stat-number">{{ deviceReportSummary.total_devices }}</div>
                <div class="stat-label">总设备数</div>
              </div>
            </el-card>
            <el-card class="stat-card success" shadow="hover">
              <div class="stat-content">
                <div class="stat-number">{{ deviceReportSummary.success_count }}</div>
                <div class="stat-label">执行成功</div>
              </div>
            </el-card>
            <el-card class="stat-card danger" shadow="hover">
              <div class="stat-content">
                <div class="stat-number">{{ deviceReportSummary.failed_count }}</div>
                <div class="stat-label">执行失败</div>
              </div>
            </el-card>
            <el-card class="stat-card info" shadow="hover">
              <div class="stat-content">
                <div class="stat-number">{{ deviceReportSummary.success_rate }}%</div>
                <div class="stat-label">成功率</div>
              </div>
            </el-card>
          </div>

          <!-- 设备执行结果表格 -->
          <el-table
            :data="deviceReportDetails"
            stripe
            border
            style="margin-top: 20px; width: 100%"
            fit
          >
            <el-table-column prop="device_id" label="设备ID" min-width="80" align="center" />
            <el-table-column prop="device_name" label="设备名称" min-width="150" />
            <el-table-column prop="status" label="执行状态" min-width="100" align="center">
              <template #default="{ row }">
                <el-tag
                  :type="row.status === 'success' ? 'success' : 'danger'"
                >
                  {{ row.status === 'success' ? '成功' : '失败' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="execution_time" label="执行时间(s)" min-width="120" align="center" />
            <el-table-column prop="exit_code" label="退出码" min-width="100" align="center" />
            <el-table-column label="操作" min-width="120" align="center">
              <template #default="{ row }">
                <el-button
                  type="primary"
                  size="small"
                  @click="handleViewOutput(row)"
                >
                  <el-icon><Document /></el-icon>
                  查看输出
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-card>
    </div>

    <div v-else class="empty-state">
      <el-empty description="无法获取报告数据" />
      <el-button type="primary" style="margin-top: 20px;" @click="handleBack">
        返回报告列表
      </el-button>
    </div>

    <!-- 执行输出弹窗 -->
    <el-dialog
      v-model="outputDialogVisible"
      :title="`执行输出 - ${currentOutputDetail?.device_name || ''}`"
      width="80%"
    >
      <div class="output-dialog">
        <div class="output-header">
          <div class="info-item">
            <span class="label">设备ID：</span>
            <span class="value">{{ currentOutputDetail?.device_id }}</span>
          </div>
          <div class="info-item">
            <span class="label">设备名称：</span>
            <span class="value">{{ currentOutputDetail?.device_name }}</span>
          </div>
          <div class="info-item">
            <span class="label">退出码：</span>
            <span class="value">{{ currentOutputDetail?.exit_code }}</span>
          </div>
        </div>
        <div class="output-content">
          <div class="output-section">
            <h5>标准输出：</h5>
            <pre class="output-pre">{{ currentOutputDetail?.output || '无输出' }}</pre>
          </div>
          <div class="output-section" v-if="currentOutputDetail?.error_output">
            <h5>错误输出：</h5>
            <pre class="output-pre error">{{ currentOutputDetail?.error_output }}</pre>
          </div>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="outputDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="handleCopyOutput">复制输出</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { ArrowLeft, Download, Document } from '@element-plus/icons-vue';
import dayjs from 'dayjs';
import { getReportData } from '@/api/report';

// 路由相关
const route = useRoute();
const router = useRouter();

// 响应式数据
const loading = ref(true);
const outputDialogVisible = ref(false);
const currentReport = ref(null);
const currentOutputDetail = ref(null);
const reportSummary = ref({
  total_cases: 0,
  executed_cases: 0,
  pass_count: 0,
  fail_count: 0,
  blocked_count: 0,
  not_applicable_count: 0,
  pass_rate: 0
});
const reportDetails = ref([]);
const deviceReportSummary = ref({
  total_devices: 0,
  success_count: 0,
  failed_count: 0,
  success_rate: 0
});
const deviceReportDetails = ref([]);

// 获取报告ID
const reportId = ref(route.params.id);

// 获取报告数据
const fetchReportData = async () => {
  try {
    loading.value = true;
    const response = await getReportData(reportId.value);
    if (response.success) {
      currentReport.value = response.data.task_info;
      
      // 根据任务类型处理报告数据
      if (currentReport.value.task_type === 'test_case') {
        reportSummary.value = response.data.summary;
        reportDetails.value = response.data.details;
      } else if (currentReport.value.task_type === 'device_script') {
        deviceReportSummary.value = response.data.summary;
        deviceReportDetails.value = response.data.details;
      }
    } else {
      ElMessage.error(response.message || '获取报告数据失败');
    }
  } catch (error) {
    ElMessage.error('获取报告数据失败');
  } finally {
    loading.value = false;
  }
};

// 返回报告列表
const handleBack = () => {
  router.push('/report');
};

// 导出报告
const handleExportReport = () => {
  ElMessage.info('导出功能正在开发中，敬请期待');
};

// 查看设备执行输出
const handleViewOutput = (row) => {
  currentOutputDetail.value = row;
  outputDialogVisible.value = true;
};

// 复制输出
const handleCopyOutput = () => {
  if (!currentOutputDetail.value) return;
  
  const output = `${currentOutputDetail.value.output || ''}\n${currentOutputDetail.value.error_output || ''}`;
  navigator.clipboard.writeText(output)
    .then(() => {
      ElMessage.success('输出已复制到剪贴板');
    })
    .catch(() => {
      ElMessage.error('复制失败');
    });
};

// 格式化日期时间
const formatDateTime = (dateTime) => {
  return dateTime ? dayjs(dateTime).format('YYYY-MM-DD HH:mm:ss') : '-';
};

// 获取状态标签类型
const getStatusTagType = (status) => {
  const typeMap = {
    'pending': 'info',
    'executing': 'warning',
    'completed': 'success',
    'terminated': 'danger'
  };
  return typeMap[status] || 'info';
};

// 获取状态标签文本
const getStatusLabel = (status) => {
  const labelMap = {
    'pending': '待执行',
    'executing': '执行中',
    'completed': '已完成',
    'terminated': '已终止'
  };
  return labelMap[status] || status;
};

// 页面加载时获取报告数据
onMounted(() => {
  fetchReportData();
});
</script>

<style lang="scss" scoped>
.report-detail-page {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.page-header {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;

  .header-left {
    display: flex;
    align-items: center;
  }

  h2 {
    margin: 0;
    color: #303133;
    font-size: 24px;
    font-weight: 600;
  }
}

.loading-container {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.report-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: white;
  padding: 50px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

/* 报告概览样式 */
.report-overview {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  h4 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
  }
}

.overview-content {
  padding: 10px 0;
}

.overview-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;

  .label {
    font-weight: 500;
    color: #606266;
    min-width: 80px;
  }

  .value {
    color: #303133;
    word-break: break-word;
  }
}

/* 统计卡片样式 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-5px);
  }

  &.success {
    border-left: 4px solid #67c23a;
  }

  &.danger {
    border-left: 4px solid #f56c6c;
  }

  &.warning {
    border-left: 4px solid #e6a23c;
  }

  &.info {
    border-left: 4px solid #909399;
  }
}

.stat-content {
  padding: 10px 0;
}

.stat-number {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

/* 脚本信息样式 */
.script-info {
  margin-bottom: 20px;
}

.script-info-content {
  padding: 10px 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 15px;
}

/* 设备脚本报告样式 */
.device-script-report {
  padding: 10px 0;
}

/* 输出弹窗样式 */
.output-dialog {
  padding: 10px 0;
}

.output-header {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.output-content {
  max-height: 500px;
  overflow-y: auto;
}

.output-section {
  margin-bottom: 15px;
}

.output-section h5 {
  margin: 0 0 10px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.output-pre {
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 15px;
  margin: 0;
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  line-height: 1.5;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 400px;
  overflow-y: auto;
}

.output-pre.error {
  background: #fef0f0;
  border-color: #fbc4ab;
  color: #f56c6c;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .overview-info {
    grid-template-columns: 1fr;
  }

  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .script-info-content {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;

    .header-left {
      flex-direction: column;
      align-items: flex-start;
      gap: 15px;
    }

    h2 {
      margin-left: 0 !important;
    }
  }
}
</style>
