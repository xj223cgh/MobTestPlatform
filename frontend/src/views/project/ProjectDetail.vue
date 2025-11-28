<template>
  <div class="project-detail">
    <!-- 项目基本信息 -->
    <div class="info-section">
      <el-card shadow="hover" class="info-card">
        <template #header>
          <div class="card-header">
              <h2>项目名称: {{ projectDetail.project_name || '未知项目' }}</h2>
            <div class="header-actions">
              <el-button type="primary" @click="handleEdit">
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
        <el-descriptions :column="2" border>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(projectDetail.status)">{{ getStatusText(projectDetail.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="环境">
            <el-tag :type="getEnvironmentType(projectDetail.environment)">{{ getEnvironmentText(projectDetail.environment) || '-' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="优先级">
            <el-tag :type="getPriorityType(projectDetail.priority)">{{ getPriorityText(projectDetail.priority) || '-' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="负责人">{{ projectDetail.owner_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="开始日期">{{ formatDateTime(projectDetail.start_date) }}</el-descriptions-item>
          <el-descriptions-item label="结束日期">{{ formatDateTime(projectDetail.end_date) }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDateTime(projectDetail.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDateTime(projectDetail.updated_at) }}</el-descriptions-item>
        </el-descriptions>
      </el-card>
    </div>

    <!-- 项目描述 -->
    <div class="info-section">
      <el-card shadow="hover" class="info-card">
        <template #header>
          <div class="card-header">
            <span>项目描述</span>
            <span class="description-count">{{ (projectDetail.description || '').length }} 字符</span>
          </div>
        </template>
        <div class="description-content">
          {{ projectDetail.description || '暂无描述' }}
        </div>
      </el-card>
    </div>

    <!-- 项目链接 -->
    <div class="info-section">
      <el-card shadow="hover" class="info-card">
        <template #header>
          <div class="card-header">
            <span>项目链接</span>
          </div>
        </template>
        <el-descriptions :column="1" border label-width="140px">
          <el-descriptions-item label="文档链接">
            <a v-if="projectDetail.doc_url" :href="projectDetail.doc_url" target="_blank" class="project-link">{{ projectDetail.doc_url }}</a>
            <span v-else>-</span>
          </el-descriptions-item>
          <el-descriptions-item label="流水线链接">
            <a v-if="projectDetail.pipeline_url" :href="projectDetail.pipeline_url" target="_blank" class="project-link">{{ projectDetail.pipeline_url }}</a>
            <span v-else>-</span>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
    </div>

    <!-- 项目统计 -->
    <div class="info-section">
      <el-card shadow="hover" class="info-card">
        <template #header>
          <div class="card-header">
            <span>项目统计</span>
          </div>
        </template>
        
        <!-- 统计概览 -->
        <el-row :gutter="20" class="stats-overview">
          <!-- 缺陷统计 -->
          <el-col :span="8">
            <div class="stat-item-with-chart">
              <div class="stat-header">
                <div class="stat-label">缺陷总数</div>
                <div class="stat-value">{{ projectDetail.bug_stats?.total || 0 }}</div>
              </div>
              <div class="chart-container-small">
                <v-chart :option="bugCategoryChartOption" autoresize />
              </div>
            </div>
          </el-col>
          
          <!-- 用例统计 -->
          <el-col :span="8">
            <div class="stat-item-with-chart">
              <div class="stat-header">
                <div class="stat-label">用例总数</div>
                <div class="stat-value">{{ projectDetail.case_stats?.total || 0 }}</div>
              </div>
              <div class="chart-container-small">
                <v-chart :option="caseExecutionChartOption" autoresize />
              </div>
            </div>
          </el-col>
          
          <!-- 迭代统计 -->
          <el-col :span="8">
            <div class="stat-item-with-chart">
              <div class="stat-header">
                <div class="stat-label">迭代总数</div>
                <div class="stat-value">{{ projectDetail.iteration_stats?.total || 0 }}</div>
              </div>
              <div class="chart-container-small">
                <v-chart :option="iterationChartOption" autoresize />
              </div>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Edit, ArrowLeft } from '@element-plus/icons-vue'
import { getProject } from '@/api/project'
import dayjs from 'dayjs'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import VChart from 'vue-echarts'

// 注册必要的组件
use([CanvasRenderer, PieChart, BarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

// 响应式数据
const loading = ref(false)
const projectDetail = ref({})
const route = useRoute()
const router = useRouter()

// 图表配置选项
const bugCategoryChartOption = ref({
  title: {
    text: '',
    left: 'center'
  },
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c} ({d}%)'
  },
  legend: {
    orient: 'horizontal',
    bottom: 0,
    left: 'center',
    textStyle: {
      fontSize: 10
    },
    itemGap: 10,
    padding: [10, 0, 0, 0]
  },
  series: [
    {
      name: '缺陷分类',
      type: 'pie',
      radius: '65%',
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 0,
        borderColor: '#fff',
        borderWidth: 1
      },
      label: {
        show: true,
        position: 'outside',
        formatter: '{b}: {c} ({d}%)',
        fontSize: 10
      },
      emphasis: {
        label: {
          show: true,
          fontSize: '12',
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: true
      },
      data: []
    }
  ]
})

const caseExecutionChartOption = ref({
  title: {
    text: '',
    left: 'center'
  },
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c} ({d}%)'
  },
  legend: {
    orient: 'horizontal',
    bottom: 0,
    left: 'center',
    textStyle: {
      fontSize: 10
    },
    itemGap: 10,
    padding: [10, 0, 0, 0]
  },
  series: [
    {
      name: '用例执行情况',
      type: 'pie',
      radius: '65%',
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 0,
        borderColor: '#fff',
        borderWidth: 1
      },
      label: {
        show: true,
        position: 'outside',
        formatter: '{b}: {c} ({d}%)',
        fontSize: 10
      },
      emphasis: {
        label: {
          show: true,
          fontSize: '12',
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: true
      },
      data: []
    }
  ]
})

const iterationChartOption = ref({
  title: {
    text: '',
    left: 'center'
  },
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c} ({d}%)'
  },
  legend: {
    orient: 'horizontal',
    bottom: 0,
    left: 'center',
    textStyle: {
      fontSize: 10
    },
    itemGap: 10,
    padding: [10, 0, 0, 0]
  },
  series: [
    {
      name: '迭代统计',
      type: 'pie',
      radius: '65%',
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 0,
        borderColor: '#fff',
        borderWidth: 1
      },
      label: {
        show: true,
        position: 'outside',
        formatter: '{b}: {c} ({d}%)',
        fontSize: 10
      },
      emphasis: {
        label: {
          show: true,
          fontSize: '12',
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: true
      },
      data: []
    }
  ]
})

// 状态类型映射
const getStatusType = (status) => {
  const statusMap = {
    not_started: 'info',
    in_progress: 'success',
    paused: 'warning',
    completed: 'success',
    closed: 'danger'
  }
  return statusMap[status] || 'info'
}

// 状态文本映射
const getStatusText = (status) => {
  const statusMap = {
    not_started: '未开始',
    in_progress: '进行中',
    paused: '已暂停',
    completed: '已完成',
    closed: '已关闭'
  }
  return statusMap[status] || status || '-'  
}

// 环境类型映射
const getEnvironmentType = (environment) => {
  const envMap = {
    test: 'info',
    staging: 'warning',
    production: 'success'
  }
  return envMap[environment] || 'info'
}

// 环境文本映射
const getEnvironmentText = (environment) => {
  const envMap = {
    test: '测试环境',
    staging: '预发环境',
    production: '正式环境'
  }
  return envMap[environment] || environment
}

// 优先级类型映射
const getPriorityType = (priority) => {
  const priorityMap = {
    high: 'danger',
    medium: 'warning',
    low: 'success'
  }
  return priorityMap[priority] || 'info'
}

// 优先级文本映射
const getPriorityText = (priority) => {
  const priorityMap = {
    high: '高',
    medium: '中',
    low: '低'
  }
  return priorityMap[priority] || priority
}

// 时间格式化函数
const formatDateTime = (dateTime) => {
  return dateTime ? dayjs(dateTime).format('YYYY-MM-DD HH:mm:ss') : '-' 
}

// 更新图表数据
const updateCharts = () => {
  // 更新缺陷分类饼图
  const bugStats = projectDetail.value.bug_stats || {}
  bugCategoryChartOption.value.series[0].data = [
    { value: bugStats.high || 0, name: '高优先级' },
    { value: bugStats.medium || 0, name: '中优先级' },
    { value: bugStats.low || 0, name: '低优先级' }
  ]
  
  // 更新用例执行情况饼图
  const caseStats = projectDetail.value.case_stats || {}
  caseExecutionChartOption.value.series[0].data = [
    { value: caseStats.passed || 0, name: '通过' },
    { value: caseStats.failed || 0, name: '失败' },
    { value: caseStats.blocked || 0, name: '阻塞' },
    { value: caseStats.not_applicable || 0, name: '不适用' },
    { value: caseStats.not_run || 0, name: '未执行' }
  ]
  
  // 更新迭代统计饼图（不显示缺陷数量，改为显示迭代基本统计）
  const iterationStats = projectDetail.value.iteration_stats || {}
  const iterations = iterationStats.iterations || []
  
  // 如果有迭代数据，显示迭代进度分布
  if (iterations.length > 0) {
    // 统计不同状态的迭代数量
    const statusCount = {
      '进行中': 0,
      '已完成': 0,
      '已关闭': 0
    }
    
    iterations.forEach(iter => {
      const status = iter.status || '进行中'
      if (statusCount[status]) {
        statusCount[status]++
      } else {
        statusCount[status]++
      }
    })
    
    iterationChartOption.value.series[0].data = Object.entries(statusCount)
      .filter(([_, count]) => count > 0)
      .map(([status, count]) => ({ name: status, value: count }))
  } else {
    // 如果没有迭代数据，显示默认数据
    iterationChartOption.value.series[0].data = [
      { name: '暂无数据', value: 1 }
    ]
  }
}

// 获取项目详情
const fetchProjectDetail = async () => {
  loading.value = true
  try {
    const projectId = route.params.id
    const response = await getProject(projectId)
    // 假设后端返回的数据结构是 { project: { ... } }
    projectDetail.value = response.project || {}
  } catch (error) {
    console.error('获取项目详情失败:', error)
    ElMessage.error('获取项目详情失败')
    projectDetail.value = {}
  } finally {
    loading.value = false
    // 更新图表
    updateCharts()
  }
}

// 监听projectDetail变化，更新图表
watch(projectDetail, () => {
  updateCharts()
}, { deep: true })

// 返回列表
const handleBack = () => {
  router.push('/projects')
}

// 编辑项目
const handleEdit = () => {
  ElMessage.info('编辑功能待实现')
}

// 生命周期钩子 - 组件挂载时获取项目详情
onMounted(() => {
  fetchProjectDetail()
})
</script>

<style lang="scss" scoped>
.project-detail {
  padding: 20px;
  min-height: 100vh;
  background-color: #f5f7fa;
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
  color: #303133;
  padding: 5px 0;
}

.card-header span {
  font-weight: 700;
  font-size: 16px;
}

.description-content {
  line-height: 1.6;
  color: #606266;
  max-height: 300px;
  overflow-y: auto;
  padding: 10px;
  background-color: #fafafa;
  border-radius: 4px;
  border: 1px solid #ebeef5;
}

.description-count {
  font-size: 12px;
  color: #909399;
  font-weight: normal;
  margin-left: 10px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
  
  .stat-label {
    font-size: 14px;
    color: #606266;
    margin-bottom: 8px;
  }
  
  .stat-value {
    font-size: 24px;
    font-weight: 500;
    color: #303133;
  }
}

/* 统计概览样式 */
.stats-overview {
  margin-bottom: 0;
}

/* 带图表的统计项样式 */
.stat-item-with-chart {
  background-color: #f5f7fa;
  border-radius: 8px;
  padding: 15px;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* 统计项头部样式 */
.stat-header {
  text-align: center;
  margin-top: 5px;
  margin-bottom: -35px;
  padding: 0 10px;
}

/* 小图表容器样式 */
.chart-container-small {
  height: 300px;
  width: 100%;
  min-width: 150px;
  margin-bottom: 15px;
}

/* 项目链接样式 */
.project-link {
  display: block;
  word-break: break-all;
  white-space: normal;
  line-height: 1.5;
  color: #409eff;
  text-decoration: none;
  
  &:hover {
    color: #66b1ff;
    text-decoration: underline;
  }
}
</style>