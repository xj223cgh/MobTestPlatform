<template>
  <div class="report-management">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>报告管理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="generateReport">
          <el-icon><Document /></el-icon>
          生成报告
        </el-button>
        <el-button @click="exportReports">
          <el-icon><Download /></el-icon>
          导出报告
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon">
                <el-icon size="40" color="#409EFF"><Document /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ stats.totalReports }}</div>
                <div class="stats-label">总报告数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon">
                <el-icon size="40" color="#67C23A"><CircleCheck /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ stats.successReports }}</div>
                <div class="stats-label">成功报告</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon">
                <el-icon size="40" color="#F56C6C"><CircleClose /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ stats.failedReports }}</div>
                <div class="stats-label">失败报告</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon">
                <el-icon size="40" color="#E6A23C"><Clock /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ stats.pendingReports }}</div>
                <div class="stats-label">待处理报告</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="报告名称">
          <el-input
            v-model="searchForm.name"
            placeholder="请输入报告名称"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="任务名称">
          <el-input
            v-model="searchForm.taskName"
            placeholder="请输入任务名称"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="报告类型">
          <el-select v-model="searchForm.type" placeholder="请选择报告类型" clearable>
            <el-option label="测试报告" value="test" />
            <el-option label="性能报告" value="performance" />
            <el-option label="覆盖率报告" value="coverage" />
            <el-option label="错误报告" value="error" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="成功" value="success" />
            <el-option label="失败" value="failed" />
            <el-option label="进行中" value="running" />
            <el-option label="待处理" value="pending" />
          </el-select>
        </el-form-item>
        <el-form-item label="创建时间">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 报告列表 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="reportList"
        stripe
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="报告名称" min-width="150" />
        <el-table-column prop="taskName" label="任务名称" min-width="150" />
        <el-table-column prop="type" label="报告类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getReportTypeTag(row.type)">
              {{ getReportTypeText(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="successRate" label="成功率" width="100">
          <template #default="{ row }">
            <el-progress
              :percentage="row.successRate"
              :color="getProgressColor(row.successRate)"
              :stroke-width="6"
            />
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="执行时长" width="120" />
        <el-table-column prop="createdAt" label="创建时间" width="160" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="viewReport(row)"
            >
              查看
            </el-button>
            <el-button
              type="success"
              size="small"
              @click="downloadReport(row)"
            >
              下载
            </el-button>
            <el-dropdown @command="(command) => handleCommand(command, row)">
              <el-button type="info" size="small">
                更多<el-icon class="el-icon--right"><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="share">分享</el-dropdown-item>
                  <el-dropdown-item command="compare">比较</el-dropdown-item>
                  <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          current-page="pagination.page"
          page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 生成报告对话框 -->
    <el-dialog
      v-model="generateDialogVisible"
      title="生成报告"
      width="600px"
      @close="handleGenerateDialogClose"
    >
      <el-form
        ref="generateFormRef"
        :model="generateForm"
        :rules="generateRules"
        label-width="100px"
      >
        <el-form-item label="报告名称" prop="name">
          <el-input v-model="generateForm.name" placeholder="请输入报告名称" />
        </el-form-item>
        <el-form-item label="任务选择" prop="taskId">
          <el-select v-model="generateForm.taskId" placeholder="请选择任务" style="width: 100%">
            <el-option
              v-for="task in taskList"
              :key="task.id"
              :label="task.name"
              :value="task.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="报告类型" prop="type">
          <el-select v-model="generateForm.type" placeholder="请选择报告类型" style="width: 100%">
            <el-option label="测试报告" value="test" />
            <el-option label="性能报告" value="performance" />
            <el-option label="覆盖率报告" value="coverage" />
            <el-option label="错误报告" value="error" />
          </el-select>
        </el-form-item>
        <el-form-item label="报告格式" prop="format">
          <el-checkbox-group v-model="generateForm.format">
            <el-checkbox label="html">HTML</el-checkbox>
            <el-checkbox label="pdf">PDF</el-checkbox>
            <el-checkbox label="json">JSON</el-checkbox>
            <el-checkbox label="excel">Excel</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="包含内容">
          <el-checkbox-group v-model="generateForm.includeContent">
            <el-checkbox label="summary">摘要</el-checkbox>
            <el-checkbox label="details">详细信息</el-checkbox>
            <el-checkbox label="charts">图表</el-checkbox>
            <el-checkbox label="logs">日志</el-checkbox>
            <el-checkbox label="screenshots">截图</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="generateDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleGenerateReport">生成</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 报告详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="报告详情"
      width="80%"
      top="5vh"
      @close="handleDetailDialogClose"
    >
      <div v-if="currentReport" class="report-detail">
        <!-- 报告基本信息 -->
        <el-descriptions title="基本信息" :column="3" border>
          <el-descriptions-item label="报告名称">{{ currentReport.name }}</el-descriptions-item>
          <el-descriptions-item label="任务名称">{{ currentReport.taskName }}</el-descriptions-item>
          <el-descriptions-item label="报告类型">
            <el-tag :type="getReportTypeTag(currentReport.type)">
              {{ getReportTypeText(currentReport.type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTag(currentReport.status)">
              {{ getStatusText(currentReport.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="成功率">{{ currentReport.successRate }}%</el-descriptions-item>
          <el-descriptions-item label="执行时长">{{ currentReport.duration }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ currentReport.createdAt }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ currentReport.updatedAt }}</el-descriptions-item>
          <el-descriptions-item label="文件大小">{{ currentReport.fileSize }}</el-descriptions-item>
        </el-descriptions>

        <!-- 测试结果统计 -->
        <div class="report-stats">
          <h3>测试结果统计</h3>
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-value success">{{ currentReport.totalCases }}</div>
                <div class="stat-label">总用例数</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-value success">{{ currentReport.passedCases }}</div>
                <div class="stat-label">通过用例</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-value failed">{{ currentReport.failedCases }}</div>
                <div class="stat-label">失败用例</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-value warning">{{ currentReport.skippedCases }}</div>
                <div class="stat-label">跳过用例</div>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 报告内容 -->
        <div class="report-content">
          <h3>报告内容</h3>
          <el-tabs v-model="activeTab">
            <el-tab-pane label="摘要" name="summary">
              <div v-html="currentReport.summary" class="report-html"></div>
            </el-tab-pane>
            <el-tab-pane label="详细信息" name="details">
              <div v-html="currentReport.details" class="report-html"></div>
            </el-tab-pane>
            <el-tab-pane label="图表" name="charts">
              <div v-if="currentReport.charts" class="report-charts">
                <div v-for="(chart, index) in currentReport.charts" :key="index" class="chart-item">
                  <div :id="`chart-${index}`" style="width: 100%; height: 400px;"></div>
                </div>
              </div>
            </el-tab-pane>
            <el-tab-pane label="日志" name="logs">
              <div class="report-logs">
                <pre>{{ currentReport.logs }}</pre>
              </div>
            </el-tab-pane>
            <el-tab-pane label="截图" name="screenshots">
              <div class="report-screenshots">
                <el-image
                  v-for="(screenshot, index) in currentReport.screenshots"
                  :key="index"
                  :src="screenshot.url"
                  :preview-src-list="[screenshot.url]"
                  fit="cover"
                  class="screenshot-item"
                />
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document, Download, Search, Refresh, CircleCheck, CircleClose, Clock, ArrowDown } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { reportApi } from '@/api/report'
import { testTaskApi } from '@/api/testTask'

// 响应式数据
const loading = ref(false)
const reportList = ref([])
const selectedReports = ref([])
const generateDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const currentReport = ref(null)
const taskList = ref([])
const activeTab = ref('summary')

// 统计数据
const stats = reactive({
  totalReports: 0,
  successReports: 0,
  failedReports: 0,
  pendingReports: 0
})

// 搜索表单
const searchForm = reactive({
  name: '',
  taskName: '',
  type: '',
  status: '',
  dateRange: []
})

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 生成报告表单
const generateForm = reactive({
  name: '',
  taskId: '',
  type: '',
  format: ['html'],
  includeContent: ['summary', 'details']
})

// 表单验证规则
const generateRules = {
  name: [
    { required: true, message: '请输入报告名称', trigger: 'blur' }
  ],
  taskId: [
    { required: true, message: '请选择任务', trigger: 'change' }
  ],
  type: [
    { required: true, message: '请选择报告类型', trigger: 'change' }
  ],
  format: [
    { required: true, message: '请选择报告格式', trigger: 'change' }
  ]
}

const generateFormRef = ref(null)

// 计算属性
const getReportTypeTag = (type) => {
  const typeMap = {
    test: '',
    performance: 'success',
    coverage: 'warning',
    error: 'danger'
  }
  return typeMap[type] || ''
}

const getReportTypeText = (type) => {
  const typeMap = {
    test: '测试报告',
    performance: '性能报告',
    coverage: '覆盖率报告',
    error: '错误报告'
  }
  return typeMap[type] || type
}

const getStatusTag = (status) => {
  const statusMap = {
    success: 'success',
    failed: 'danger',
    running: 'warning',
    pending: 'info'
  }
  return statusMap[status] || ''
}

const getStatusText = (status) => {
  const statusMap = {
    success: '成功',
    failed: '失败',
    running: '进行中',
    pending: '待处理'
  }
  return statusMap[status] || status
}

const getProgressColor = (percentage) => {
  if (percentage >= 80) return '#67C23A'
  if (percentage >= 60) return '#E6A23C'
  return '#F56C6C'
}

// 方法
const getReportList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      ...searchForm
    }
    
    if (searchForm.dateRange && searchForm.dateRange.length === 2) {
      params.startDate = searchForm.dateRange[0]
      params.endDate = searchForm.dateRange[1]
    }
    
    const response = await reportApi.getReportList(params)
    reportList.value = response.data.items
    pagination.total = response.data.total
  } catch (error) {
    ElMessage.error('获取报告列表失败')
  } finally {
    loading.value = false
  }
}

const getReportStats = async () => {
  try {
    const response = await reportApi.getReportStats()
    Object.assign(stats, response.data)
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

const getTaskList = async () => {
  try {
    const response = await testTaskApi.getTestTaskList({ page: 1, size: 1000 })
    taskList.value = response.data.items
  } catch (error) {
    console.error('获取任务列表失败:', error)
  }
}

const handleSearch = () => {
  pagination.page = 1
  getReportList()
}

const handleReset = () => {
  Object.assign(searchForm, {
    name: '',
    taskName: '',
    type: '',
    status: '',
    dateRange: []
  })
  handleSearch()
}

const handleSelectionChange = (selection) => {
  selectedReports.value = selection
}

const handleSizeChange = (size) => {
  pagination.size = size
  getReportList()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  getReportList()
}

const generateReport = () => {
  generateDialogVisible.value = true
}

const handleGenerateReport = async () => {
  if (!generateFormRef.value) return
  
  try {
    await generateFormRef.value.validate()
    await reportApi.generateReport(generateForm)
    ElMessage.success('报告生成成功')
    generateDialogVisible.value = false
    getReportList()
  } catch (error) {
    if (error.response) {
      ElMessage.error('生成报告失败')
    }
  }
}

const handleGenerateDialogClose = () => {
  generateFormRef.value?.resetFields()
  Object.assign(generateForm, {
    name: '',
    taskId: '',
    type: '',
    format: ['html'],
    includeContent: ['summary', 'details']
  })
}

const viewReport = async (report) => {
  try {
    const response = await reportApi.getReportDetail(report.id)
    currentReport.value = response.data
    detailDialogVisible.value = true
    
    // 渲染图表
    setTimeout(() => {
      renderCharts()
    }, 100)
  } catch (error) {
    ElMessage.error('获取报告详情失败')
  }
}

const handleDetailDialogClose = () => {
  currentReport.value = null
  activeTab.value = 'summary'
}

const downloadReport = async (report) => {
  try {
    const response = await reportApi.downloadReport(report.id, 'pdf')
    const blob = new Blob([response.data], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${report.name}.pdf`
    link.click()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    ElMessage.error('下载报告失败')
  }
}

const exportReports = async () => {
  try {
    const response = await reportApi.exportReports(searchForm)
    const blob = new Blob([response.data], { type: 'application/vnd.ms-excel' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'reports.xlsx'
    link.click()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    ElMessage.error('导出报告失败')
  }
}

const handleCommand = async (command, report) => {
  switch (command) {
    case 'share':
      await shareReport(report)
      break
    case 'compare':
      await compareReport(report)
      break
    case 'delete':
      await deleteReport(report)
      break
  }
}

const shareReport = async (report) => {
  try {
    const response = await reportApi.shareReport(report.id)
    ElMessage.success(`分享链接已生成: ${response.data.shareUrl}`)
  } catch (error) {
    ElMessage.error('分享报告失败')
  }
}

const compareReport = async (report) => {
  ElMessage.info('比较功能开发中...')
}

const deleteReport = async (report) => {
  try {
    await ElMessageBox.confirm('确定要删除这个报告吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await reportApi.deleteReport(report.id)
    ElMessage.success('删除成功')
    getReportList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const renderCharts = () => {
  if (!currentReport.value || !currentReport.value.charts) return
  
  currentReport.value.charts.forEach((chart, index) => {
    const chartDom = document.getElementById(`chart-${index}`)
    if (chartDom) {
      const myChart = echarts.init(chartDom)
      myChart.setOption(chart.options)
    }
  })
}

// 生命周期
onMounted(() => {
  getReportList()
  getReportStats()
  getTaskList()
})
</script>

<style scoped>
.report-management {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.stats-cards {
  margin-bottom: 20px;
}

.stats-card {
  height: 100px;
}

.stats-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stats-icon {
  margin-right: 15px;
}

.stats-info {
  flex: 1;
}

.stats-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
}

.stats-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.search-card {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.report-detail {
  max-height: 70vh;
  overflow-y: auto;
}

.report-stats {
  margin: 20px 0;
}

.report-stats h3 {
  margin-bottom: 15px;
  color: #303133;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-value.success {
  color: #67C23A;
}

.stat-value.failed {
  color: #F56C6C;
}

.stat-value.warning {
  color: #E6A23C;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.report-content {
  margin-top: 20px;
}

.report-content h3 {
  margin-bottom: 15px;
  color: #303133;
}

.report-html {
  line-height: 1.6;
  color: #303133;
}

.report-charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.chart-item {
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  padding: 20px;
}

.report-logs {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 20px;
}

.report-logs pre {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.5;
  color: #303133;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.report-screenshots {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.screenshot-item {
  width: 100%;
  height: 150px;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.3s;
}

.screenshot-item:hover {
  transform: scale(1.05);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

:deep(.el-progress-bar__outer) {
  background-color: #f0f2f5;
}

:deep(.el-progress-bar__inner) {
  transition: width 0.3s ease;
}

:deep(.el-descriptions__label) {
  font-weight: 500;
}

:deep(.el-tabs__content) {
  padding-top: 20px;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .stats-cards .el-col {
    margin-bottom: 10px;
  }

  .report-charts {
    grid-template-columns: 1fr;
  }

  .report-screenshots {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
}
</style>