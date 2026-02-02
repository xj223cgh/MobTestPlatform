<template>
  <div
    ref="reportContentRef"
    class="report-detail-page"
  >
    <!-- 顶部按钮区域 -->
    <div class="summary-bar">
      <div class="summary-title">
        {{ currentReport?.task_name || '报告详情' }}
      </div>
      <div class="summary-actions">
        <el-dropdown
          trigger="click"
          @command="handleExportReport"
        >
          <el-button>
            <el-icon><Download /></el-icon>
            导出报告
            <el-icon class="el-icon--right">
              <ArrowDown />
            </el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="print">
                打印/另存为 PDF
              </el-dropdown-item>
              <el-dropdown-item command="excel">
                导出 Excel
              </el-dropdown-item>
              <el-dropdown-item command="html">
                导出 HTML
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button
          type="primary"
          style="margin-left: 8px"
          @click="handleBack"
        >
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
      </div>
    </div>

    <div
      v-if="loading"
      class="loading-container"
    >
      <el-skeleton
        :rows="5"
        animated
      />
      <el-skeleton
        :rows="3"
        animated
        style="margin-top: 20px"
      />
    </div>

    <div
      v-else-if="loadError"
      class="error-state"
    >
      <el-empty description="获取报告数据失败">
        <el-button
          type="primary"
          @click="fetchReportData"
        >
          重试
        </el-button>
      </el-empty>
    </div>

    <div
      v-else-if="currentReport"
      class="report-content"
    >
          <!-- 报告概览 -->
          <div class="overview-section">
            <h4 class="section-title">
              报告概览
            </h4>
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
                <span class="label">所属项目：</span>
                <span class="value">{{ currentReport.project_name || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">所属迭代：</span>
                <span class="value">{{ currentReport.iteration_name || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">所属需求：</span>
                <span class="value">{{ currentReport.requirement_name || '-' }}</span>
              </div>
              <div v-if="currentReport.task_type === 'test_case'" class="info-item">
                <span class="label">用例集：</span>
                <el-link 
                  type="primary" 
                  :underline="false"
                  @click="goToTestSuite(currentReport.suite_id)"
                >
                  {{ currentReport.suite_name || '-' }}
                </el-link>
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

          <!-- 测试用例：统计卡片 + 图表 -->
          <template v-if="currentReport.task_type === 'test_case'">
            <div class="stats-section">
              <h4 class="section-title">
                执行统计
              </h4>
              <div class="stats-cards">
                <el-card
                  class="stat-card clickable"
                  shadow="hover"
                  @click="quickFilter = quickFilter === 'fail' ? '' : 'fail'"
                >
                  <div class="stat-content">
                    <div class="stat-number">
                      {{ reportSummary.total_cases }}
                    </div>
                    <div class="stat-label">
                      总用例数
                    </div>
                  </div>
                </el-card>
                <el-card
                  class="stat-card clickable"
                  shadow="hover"
                  @click="quickFilter = quickFilter === 'pass' ? '' : 'pass'"
                >
                  <div class="stat-content success">
                    <div class="stat-number">
                      {{ reportSummary.pass_count }}
                    </div>
                    <div class="stat-label">
                      通过
                    </div>
                  </div>
                </el-card>
                <el-card
                  class="stat-card clickable"
                  shadow="hover"
                  @click="quickFilter = quickFilter === 'fail' ? '' : 'fail'"
                >
                  <div class="stat-content danger">
                    <div class="stat-number">
                      {{ reportSummary.fail_count }}
                    </div>
                    <div class="stat-label">
                      失败
                    </div>
                  </div>
                </el-card>
                <el-card
                  class="stat-card clickable"
                  shadow="hover"
                  @click="quickFilter = quickFilter === 'blocked' ? '' : 'blocked'"
                >
                  <div class="stat-content warning">
                    <div class="stat-number">
                      {{ reportSummary.blocked_count }}
                    </div>
                    <div class="stat-label">
                      阻塞
                    </div>
                  </div>
                </el-card>
                <el-card
                  class="stat-card"
                  shadow="hover"
                >
                  <div class="stat-content info">
                    <div class="stat-number">
                      {{ reportSummary.pass_rate }}%
                    </div>
                    <div class="stat-label">
                      通过率
                    </div>
                  </div>
                </el-card>
              </div>
            </div>
            <div class="charts-section">
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-card">
                    <h5>执行结果分布</h5>
                    <v-chart
                      :option="testCasePieOption"
                      autoresize
                      style="height: 280px"
                    />
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="chart-card">
                    <h5>状态统计</h5>
                    <v-chart
                      :option="testCaseBarOption"
                      autoresize
                      style="height: 280px"
                    />
                  </div>
                </el-col>
              </el-row>
            </div>
          </template>

          <!-- 设备脚本：统计 + 图表 -->
          <template v-else-if="currentReport.task_type === 'device_script'">
            <!-- 脚本信息 -->
            <div class="script-section">
              <h4 class="section-title">
                脚本信息
              </h4>
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
            </div>
            <div class="stats-section">
              <h4 class="section-title">
                执行统计
              </h4>
              <div class="stats-cards">
                <el-card
                  class="stat-card clickable"
                  shadow="hover"
                  @click="quickFilter = quickFilter === 'failed' ? '' : 'failed'"
                >
                  <div class="stat-content">
                    <div class="stat-number">
                      {{ deviceReportSummary.total_devices }}
                    </div>
                    <div class="stat-label">
                      总设备数
                    </div>
                  </div>
                </el-card>
                <el-card
                  class="stat-card clickable"
                  shadow="hover"
                  @click="quickFilter = ''"
                >
                  <div class="stat-content success">
                    <div class="stat-number">
                      {{ deviceReportSummary.success_count }}
                    </div>
                    <div class="stat-label">
                      成功
                    </div>
                  </div>
                </el-card>
                <el-card
                  class="stat-card clickable"
                  shadow="hover"
                  @click="quickFilter = quickFilter === 'failed' ? '' : 'failed'"
                >
                  <div class="stat-content danger">
                    <div class="stat-number">
                      {{ deviceReportSummary.failed_count }}
                    </div>
                    <div class="stat-label">
                      失败
                    </div>
                  </div>
                </el-card>
                <el-card
                  class="stat-card"
                  shadow="hover"
                >
                  <div class="stat-content info">
                    <div class="stat-number">
                      {{ deviceReportSummary.success_rate }}%
                    </div>
                    <div class="stat-label">
                      成功率
                    </div>
                  </div>
                </el-card>
              </div>
            </div>
            <div class="charts-section">
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-card">
                    <h5>执行结果分布</h5>
                    <v-chart
                      :option="devicePieOption"
                      autoresize
                      style="height: 280px"
                    />
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="chart-card">
                    <h5>设备执行时间</h5>
                    <v-chart
                      :option="deviceBarOption"
                      autoresize
                      style="height: 280px"
                    />
                  </div>
                </el-col>
              </el-row>
            </div>
          </template>

          <!-- 设备明细 -->
          <div v-if="currentReport?.task_type === 'device_script'" class="device-details-section">
            <h4 class="section-title">设备明细</h4>
            <div class="table-toolbar">
              <el-input
                v-model="deviceSearchKeyword"
                placeholder="搜索设备名称、ID"
                clearable
                style="width: 240px"
                @input="handleDeviceSearch"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
              <el-select
                v-model="deviceStatusFilter"
                placeholder="状态筛选"
                clearable
                style="width: 120px"
                @change="handleDeviceFilter"
              >
                <el-option
                  label="全部"
                  value=""
                />
                <el-option
                  label="成功"
                  value="success"
                />
                <el-option
                  label="失败"
                  value="failed"
                />
              </el-select>
              <el-button
                :type="quickFilter === 'failed' ? 'danger' : 'default'"
                @click="quickFilter = quickFilter === 'failed' ? '' : 'failed'"
              >
                仅失败设备
              </el-button>
            </div>
            <el-table
              :data="paginatedDeviceDetails"
              stripe
              border
              style="width: 100%"
              fit
            >
              <el-table-column
                prop="device_id"
                label="设备ID"
                width="90"
                align="center"
              >
                <template #default="{ row }">
                  <el-link
                    type="primary"
                    :underline="false"
                    @click="goToDevice(row.device_id)"
                  >
                    {{ row.device_id }}
                  </el-link>
                </template>
              </el-table-column>
              <el-table-column
                prop="device_name"
                label="设备名称"
                min-width="150"
                show-overflow-tooltip
              />
              <el-table-column
                prop="status"
                label="执行状态"
                width="100"
                align="center"
              >
                <template #default="{ row }">
                  <el-tag :type="row.status === 'success' ? 'success' : 'danger'">
                    {{ row.status === 'success' ? '成功' : '失败' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column
                prop="execution_time"
                label="执行时间(s)"
                width="120"
                align="center"
                sortable
              />
              <el-table-column
                prop="exit_code"
                label="退出码"
                width="90"
                align="center"
              />
              <el-table-column
                label="操作"
                width="120"
                align="center"
                fixed="right"
              >
                <template #default="{ row }">
                  <el-button
                    type="primary"
                    size="small"
                    link
                    @click="handleViewOutput(row)"
                  >
                    <el-icon><Document /></el-icon>
                    查看输出
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-pagination
              :current-page="deviceCurrentPage"
              :page-size="devicePageSize"
              :page-sizes="[10, 20, 50, 100]"
              :total="filteredDeviceDetails.length"
              layout="total, sizes, prev, pager, next"
              style="margin-top: 16px; justify-content: flex-end"
            />
          </div>
    </div>

    <div
      v-else
      class="empty-state"
    >
      <el-empty description="无法获取报告数据" />
      <el-button
        type="primary"
        style="margin-top: 20px"
        @click="handleBack"
      >
        返回报告列表
      </el-button>
    </div>

    <!-- 执行输出弹窗 -->
    <el-dialog
      v-model="outputDialogVisible"
      :title="`执行输出 - ${currentOutputDetail?.device_name || ''}`"
      width="85%"
      class="output-dialog"
      destroy-on-close
    >
      <div class="output-dialog-content">
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
        <div class="output-toolbar">
          <el-input
            v-model="outputSearchKeyword"
            placeholder="搜索输出内容"
            clearable
            size="small"
            style="width: 200px"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button
            size="small"
            @click="handleCopyOutput"
          >
            复制
          </el-button>
          <el-button
            size="small"
            @click="handleDownloadOutput"
          >
            下载
          </el-button>
        </div>
        <el-tabs
          v-model="outputActiveTab"
          class="output-tabs"
        >
          <el-tab-pane
            label="标准输出"
            name="stdout"
          >
            <div class="output-section">
              <pre
                class="output-pre"
              >{{ currentOutputDetail?.output || '无输出' }}</pre>
            </div>
          </el-tab-pane>
          <el-tab-pane
            label="错误输出"
            name="stderr"
          >
            <div class="output-section">
              <pre class="output-pre error">{{ currentOutputDetail?.error_output || '无错误输出' }}</pre>
            </div>
          </el-tab-pane>
          <el-tab-pane
            label="合并视图"
            name="merged"
          >
            <div class="output-section">
              <pre class="output-pre merged">{{ mergedOutput }}</pre>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
      <template #footer>
        <el-button @click="outputDialogVisible = false">
          关闭
        </el-button>
        <el-button
          type="primary"
          @click="handleCopyOutput"
        >
          复制输出
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { ArrowLeft, Download, Document, ArrowDown, Search } from '@element-plus/icons-vue';
import VChart from 'vue-echarts';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { PieChart, BarChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components';
import dayjs from 'dayjs';
import { getReportData } from '@/api/report';
import { saveAs } from 'file-saver';
import * as XLSX from 'xlsx';

use([CanvasRenderer, PieChart, BarChart, GridComponent, TooltipComponent, LegendComponent]);

const route = useRoute();
const router = useRouter();

const loading = ref(true);
const loadError = ref(false);
const outputDialogVisible = ref(false);
const currentReport = ref(null);
const currentOutputDetail = ref(null);
const reportContentRef = ref(null);
const reportSummary = ref({
  total_cases: 0,
  executed_cases: 0,
  pass_count: 0,
  fail_count: 0,
  blocked_count: 0,
  not_applicable_count: 0,
  pass_rate: 0
});
const deviceReportSummary = ref({
  total_devices: 0,
  success_count: 0,
  failed_count: 0,
  success_rate: 0
});
const deviceReportDetails = ref([]);

const activeTab = ref('overview');
const quickFilter = ref('');
const deviceSearchKeyword = ref('');
const deviceStatusFilter = ref('');
const outputActiveTab = ref('stdout');
const outputSearchKeyword = ref('');

const deviceCurrentPage = ref(1);
const devicePageSize = ref(20);

const reportId = ref(route.params.id);

// 图表配置 - 测试用例饼图
const testCasePieOption = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { bottom: 0 },
  color: ['#67c23a', '#f56c6c', '#e6a23c', '#909399'],
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    avoidLabelOverlap: false,
    itemStyle: { borderColor: '#fff', borderWidth: 2 },
    label: { show: true, formatter: '{b}: {c}' },
    data: [
      { value: reportSummary.value.pass_count, name: '通过' },
      { value: reportSummary.value.fail_count, name: '失败' },
      { value: reportSummary.value.blocked_count, name: '阻塞' },
      { value: reportSummary.value.not_applicable_count, name: '不适用' }
    ].filter(d => d.value > 0)
  }]
}));

// 测试用例柱状图
const testCaseBarOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: ['通过', '失败', '阻塞', '不适用'] },
  yAxis: { type: 'value' },
  series: [{
    type: 'bar',
    data: [
      { value: reportSummary.value.pass_count, itemStyle: { color: '#67c23a' } },
      { value: reportSummary.value.fail_count, itemStyle: { color: '#f56c6c' } },
      { value: reportSummary.value.blocked_count, itemStyle: { color: '#e6a23c' } },
      { value: reportSummary.value.not_applicable_count, itemStyle: { color: '#909399' } }
    ]
  }]
}));

// 设备饼图
const devicePieOption = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { bottom: 0 },
  color: ['#67c23a', '#f56c6c'],
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    avoidLabelOverlap: false,
    itemStyle: { borderColor: '#fff', borderWidth: 2 },
    label: { show: true, formatter: '{b}: {c}' },
    data: [
      { value: deviceReportSummary.value.success_count, name: '成功' },
      { value: deviceReportSummary.value.failed_count, name: '失败' }
    ].filter(d => d.value > 0)
  }]
}));

// 设备执行时间柱状图
const deviceBarOption = computed(() => {
  const details = deviceReportDetails.value;
  const topDevices = [...details]
    .sort((a, b) => (b.execution_time || 0) - (a.execution_time || 0))
    .slice(0, 10);
  return {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: topDevices.map(d => d.device_name || d.device_id || '-') },
    yAxis: { type: 'value', name: '秒' },
    series: [{
      type: 'bar',
      data: topDevices.map(d => d.execution_time || 0),
      itemStyle: {
        color: (params) => (params.data > 60 ? '#f56c6c' : '#409eff')
      }
    }]
  };
});



// 筛选后的设备数据
const filteredDeviceDetails = computed(() => {
  let list = [...deviceReportDetails.value];
  if (quickFilter.value === 'failed') {
    list = list.filter(r => r.status !== 'success');
  }
  if (deviceStatusFilter.value) {
    const target = deviceStatusFilter.value === 'failed' ? 'failed' : deviceStatusFilter.value;
    list = list.filter(r => (target === 'success' ? r.status === 'success' : r.status !== 'success'));
  }
  if (deviceSearchKeyword.value) {
    const kw = deviceSearchKeyword.value.toLowerCase();
    list = list.filter(r =>
      (r.device_name || '').toLowerCase().includes(kw) ||
      String(r.device_id || '').toLowerCase().includes(kw)
    );
  }
  return list;
});

const paginatedDeviceDetails = computed(() => {
  const start = (deviceCurrentPage.value - 1) * devicePageSize.value;
  return filteredDeviceDetails.value.slice(start, start + devicePageSize.value);
});

watch([quickFilter, deviceStatusFilter, deviceSearchKeyword], () => {
  deviceCurrentPage.value = 1;
});

// 输出弹窗 - 合并输出
const mergedOutput = computed(() => {
  if (!currentOutputDetail.value) return '';
  const out = currentOutputDetail.value.output || '';
  const err = currentOutputDetail.value.error_output || '';
  if (!err) return out;
  return `=== 标准输出 ===\n${out}\n\n=== 错误输出 ===\n${err}`;
});

// 搜索关键词功能已移除，直接显示原始输出

const fetchReportData = async () => {
  try {
    loading.value = true;
    loadError.value = false;
    const id = reportId.value;
    if (!id) {
      loadError.value = true;
      ElMessage.error('报告ID无效');
      return;
    }
    const response = await getReportData(id);
    if (response && response.success && response.data) {
      currentReport.value = response.data.task_info;
      if (currentReport.value.task_type === 'test_case') {
        reportSummary.value = response.data.summary || {};
      } else if (currentReport.value.task_type === 'device_script') {
        deviceReportSummary.value = response.data.summary || {};
        deviceReportDetails.value = response.data.details || [];
      }
    } else {
      loadError.value = true;
      ElMessage.error(response?.message || '获取报告数据失败');
    }
  } catch (error) {
    loadError.value = true;
    const msg = error?.response?.data?.message || error?.message || '获取报告数据失败';
    ElMessage.error(msg);
  } finally {
    loading.value = false;
  }
};

const handleBack = () => router.push('/report');
const handleDeviceSearch = () => { deviceCurrentPage.value = 1; };
const handleDeviceFilter = () => { deviceCurrentPage.value = 1; };

const goToTestSuite = (suiteId) => {
  router.push({ path: '/test-cases', query: { suite_id: suiteId } });
};

const goToDevice = (deviceId) => {
  router.push({ path: `/devices/${deviceId}` });
};

const handleViewOutput = (row) => {
  currentOutputDetail.value = row;
  outputDialogVisible.value = true;
  outputSearchKeyword.value = '';
  outputActiveTab.value = 'stdout';
};

const handleCopyOutput = () => {
  if (!currentOutputDetail.value) return;
  const text = mergedOutput.value;
  navigator.clipboard.writeText(text)
    .then(() => ElMessage.success('已复制到剪贴板'))
    .catch(() => ElMessage.error('复制失败'));
};

const handleDownloadOutput = () => {
  if (!currentOutputDetail.value) return;
  const text = mergedOutput.value;
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
  const name = `output_${currentOutputDetail.value.device_name || currentOutputDetail.value.device_id}_${dayjs().format('YYYYMMDDHHmmss')}.txt`;
  saveAs(blob, name);
  ElMessage.success('已下载');
};

const handleExportReport = async (format) => {
  if (!currentReport.value) return;
  try {
    if (format === 'excel') {
      await exportExcel();
    } else if (format === 'html') {
      await exportHtml();
    } else if (format === 'print') {
      handlePrint();
    }
  } catch (e) {
    if (e.name !== 'AbortError') {
      ElMessage.error('导出失败：' + (e.message || '未知错误'));
    }
  }
};

async function exportExcel() {
  const wb = XLSX.utils.book_new();
  const taskInfo = currentReport.value;
  const overviewData = [
    ['报告概览'],
    ['任务ID', taskInfo.id],
    ['任务名称', taskInfo.task_name],
    ['任务类型', taskInfo.task_type === 'test_case' ? '测试用例任务' : '设备脚本任务'],
    ['所属项目', taskInfo.project_name || '-'],
    ['所属迭代', taskInfo.iteration_name || '-'],
    ['所属需求', taskInfo.requirement_name || '-'],
    ['用例集', taskInfo.suite_name || '-'],
    ['状态', getStatusLabel(taskInfo.status)],
    ['创建人', taskInfo.created_by],
    ['创建时间', formatDateTime(taskInfo.created_at)],
    ['完成时间', taskInfo.completed_at ? formatDateTime(taskInfo.completed_at) : '-'],
    []
  ];
  XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet(overviewData), '概览');

  if (currentReport.value.task_type === 'test_case') {
    const summaryData = [
      ['执行统计'],
      ['总用例数', reportSummary.value.total_cases],
      ['已执行', reportSummary.value.executed_cases],
      ['通过', reportSummary.value.pass_count],
      ['失败', reportSummary.value.fail_count],
      ['阻塞', reportSummary.value.blocked_count],
      ['通过率', reportSummary.value.pass_rate + '%'],
      []
    ];
    XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet(summaryData), '统计');
  } else {
    const summaryData = [
      ['执行统计'],
      ['总设备数', deviceReportSummary.value.total_devices],
      ['成功', deviceReportSummary.value.success_count],
      ['失败', deviceReportSummary.value.failed_count],
      ['成功率', deviceReportSummary.value.success_rate + '%'],
      []
    ];
    XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet(summaryData), '统计');
    const detailsData = [
      ['设备ID', '设备名称', '执行状态', '执行时间(s)', '退出码'],
      ...filteredDeviceDetails.value.map(r => [
        r.device_id,
        r.device_name,
        r.status === 'success' ? '成功' : '失败',
        r.execution_time,
        r.exit_code
      ])
    ];
    XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet(detailsData), '设备明细');
  }
  
  try {
    // 生成 Excel 文件数据
    const fileName = `报告_${currentReport.value.task_name}_${dayjs().format('YYYYMMDDHHmmss')}.xlsx`;
    const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
    const blob = new Blob([wbout], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    
    // 检查是否支持 File System Access API
    if ('showSaveFilePicker' in window) {
      // 使用本地文件保存窗口
      const fileHandle = await window.showSaveFilePicker({
        suggestedName: fileName,
        types: [
          {
            description: 'Excel 文件',
            accept: {
              'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
            }
          }
        ]
      });
      
      // 写入文件
      const writableStream = await fileHandle.createWritable();
      await writableStream.write(blob);
      await writableStream.close();
      
      ElMessage.success('Excel 导出成功');
    } else {
      // 降级方案：使用浏览器保存对话框
      saveAs(blob, fileName);
      ElMessage.success('Excel 导出成功');
    }
  } catch (error) {
    if (error.name !== 'AbortError') {
      ElMessage.error('导出失败：' + (error.message || '未知错误'));
    }
  }
}

async function exportHtml() {
  const taskInfo = currentReport.value;
  let html = `<!DOCTYPE html><html><head><meta charset="utf-8"><title>${taskInfo.task_name}</title>
<style>body{font-family:sans-serif;padding:20px;}table{border-collapse:collapse;width:100%;}th,td{border:1px solid #ddd;padding:8px;}th{background:#f5f5f5;}</style></head><body>`;
  html += `<h1>${taskInfo.task_name}</h1><p>创建时间：${formatDateTime(taskInfo.created_at)} | 创建人：${taskInfo.created_by}</p>`;
  html += `<p>所属项目：${taskInfo.project_name || '-'} | 所属迭代：${taskInfo.iteration_name || '-'} | 所属需求：${taskInfo.requirement_name || '-'} | 用例集：${taskInfo.suite_name || '-'}</p>`;
  if (currentReport.value.task_type === 'test_case') {
    html += `<h2>执行统计</h2><p>通过率：${reportSummary.value.pass_rate}% | 通过：${reportSummary.value.pass_count} | 失败：${reportSummary.value.fail_count}</p>`;
  } else {
    html += `<h2>执行统计</h2><p>成功率：${deviceReportSummary.value.success_rate}% | 成功：${deviceReportSummary.value.success_count} | 失败：${deviceReportSummary.value.failed_count}</p>`;
    html += '<h2>设备明细</h2><table><tr><th>设备ID</th><th>设备名称</th><th>状态</th><th>执行时间(s)</th><th>退出码</th></tr>';
    filteredDeviceDetails.value.forEach(r => {
      html += `<tr><td>${r.device_id}</td><td>${r.device_name}</td><td>${r.status === 'success' ? '成功' : '失败'}</td><td>${r.execution_time || '-'}</td><td>${r.exit_code || '-'}</td></tr>`;
    });
    html += '</table>';
  }
  html += '</body></html>';
  
  try {
    const fileName = `报告_${taskInfo.task_name}_${dayjs().format('YYYYMMDDHHmmss')}.html`;
    const blob = new Blob([html], { type: 'text/html;charset=utf-8' });
    
    // 检查是否支持 File System Access API
    if ('showSaveFilePicker' in window) {
      // 使用本地文件保存窗口
      const fileHandle = await window.showSaveFilePicker({
        suggestedName: fileName,
        types: [
          {
            description: 'HTML 文件',
            accept: {
              'text/html': ['.html']
            }
          }
        ]
      });
      
      // 写入文件
      const writableStream = await fileHandle.createWritable();
      await writableStream.write(blob);
      await writableStream.close();
      
      ElMessage.success('HTML 导出成功');
    } else {
      // 降级方案：使用浏览器保存对话框
      saveAs(blob, fileName);
      ElMessage.success('HTML 导出成功');
    }
  } catch (error) {
    if (error.name !== 'AbortError') {
      ElMessage.error('导出失败：' + (error.message || '未知错误'));
    }
  }
}

function handlePrint() {
  window.print();
}

const formatDateTime = (dateTime) => (dateTime ? dayjs(dateTime).format('YYYY-MM-DD HH:mm:ss') : '-');

const getStatusLabel = (status) => {
  const map = { pending: '待执行', executing: '执行中', completed: '已完成', terminated: '已终止' };
  return map[status] || status;
};



onMounted(() => fetchReportData());
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
    gap: 16px;
  }

  .page-title {
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

.error-state {
  background: white;
  padding: 50px;
  border-radius: 8px;
  text-align: center;
}

.report-content {
  background: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.summary-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: white;
  border-radius: 8px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);

  .summary-title {
    font-size: 18px;
    font-weight: 600;
    color: #303133;
  }

  .summary-actions {
    display: flex;
    align-items: center;
    gap: 8px;
  }
}

/* 标签页组件已移除 */

.overview-section,
.script-section {
  margin-bottom: 24px;
}

.overview-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
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

.section-title {
  margin: 0 0 16px 0;
  font-size: 15px;
  font-weight: 600;
}

.stats-section {
  margin-bottom: 24px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 16px;
}

.stat-card {
  text-align: center;
  transition: all 0.3s;

  &.clickable {
    cursor: pointer;
  }

  &:hover {
    transform: translateY(-3px);
  }

  .stat-content {
    padding: 12px 0;

    &.success .stat-number { color: #67c23a; }
    &.danger .stat-number { color: #f56c6c; }
    &.warning .stat-number { color: #e6a23c; }
    &.info .stat-number { color: #409eff; }
  }
}

.stat-number {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: #606266;
}

.charts-section {
  margin-top: 24px;
}

.chart-card {
  background: #fafafa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;

  h5 {
    margin: 0 0 12px 0;
    font-size: 14px;
    font-weight: 600;
  }
}

.script-info-content {
  padding: 10px 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.table-toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: white;
  padding: 50px;
  border-radius: 8px;
}

.output-dialog-content {
  padding: 0;
}

.output-header {
  display: flex;
  gap: 20px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.output-toolbar {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 12px;
}

.output-tabs {
  :deep(.el-tabs__content) {
    max-height: 450px;
    overflow-y: auto;
  }
}

.output-section {
  margin: 0;
}

.output-pre {
  background: #1e1e1e;
  color: #d4d4d4;
  border-radius: 4px;
  padding: 16px;
  margin: 0;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  line-height: 1.6;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 400px;
  overflow-y: auto;

  :deep(mark) {
    background: #ffeb3b;
    color: #000;
    padding: 0 2px;
  }
}

.output-pre.error {
  background: #2d1f1f;
  color: #f48771;
}

.output-pre.merged {
  background: #1e1e1e;
  color: #d4d4d4;
}

/* 打印样式：隐藏导航、按钮等，仅保留报告内容 */
@media print {
  .page-header .header-right,
  .el-button,
  .el-tabs__header,
  .el-pagination,
  .table-toolbar,
  .el-dropdown {
    display: none !important;
  }

  .report-detail-page {
    padding: 0;
    background: white;
  }

  .report-content {
    box-shadow: none;
  }

  .stat-card:hover,
  .stat-card.clickable {
    transform: none;
  }
}
</style>
