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
          <el-col :span="6">
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
          <el-col :span="6">
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
          <el-col :span="6">
            <div class="stat-item-with-chart">
              <div class="stat-header">
                <div class="stat-label">迭代总数</div>
                <div class="stat-value">{{ projectDetail.iteration_count || 0 }}</div>
              </div>
              <div class="chart-container-small">
                <v-chart :option="iterationChartOption" autoresize />
              </div>
            </div>
          </el-col>
          
          <!-- 版本需求统计 -->
          <el-col :span="6">
            <div class="stat-item-with-chart">
              <div class="stat-header">
                <div class="stat-label">需求总数</div>
                <div class="stat-value">{{ projectDetail.requirement_count || 0 }}</div>
              </div>
              <div class="chart-container-small">
                <v-chart :option="requirementChartOption" autoresize />
              </div>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>



    <!-- 版本需求列表 -->
    <div class="info-section">
      <el-card shadow="hover" class="info-card">
        <template #header>
          <div class="card-header">
            <span>版本需求</span>
            <div class="header-actions">
              <el-button type="primary" @click="handleCreateRequirement">
                <el-icon><Plus /></el-icon>
                新建需求
              </el-button>
            </div>
          </div>
        </template>
        <el-table
          v-loading="requirementsLoading"
          :data="versionRequirements"
          stripe
          border
          style="width: 100%"
          fit
        >

          <el-table-column prop="requirement_name" label="需求名称" min-width="180" align="center">
            <template #default="scope">
              {{ scope.row.requirement_name || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="requirement_description" label="需求描述" min-width="220" align="center">
            <template #default="scope">
              {{ scope.row.requirement_description || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="iteration_name" label="所属迭代" width="120" align="center">
            <template #default="scope">
              {{ scope.row.iteration_name || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="90" align="center">
            <template #default="scope">
              <el-tag :type="getRequirementStatusType(scope.row.status)">{{ getRequirementStatusText(scope.row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="priority" label="优先级" width="90" align="center">
            <template #default="scope">
              <el-tag :type="getPriorityType(scope.row.priority)">{{ getPriorityText(scope.row.priority) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="assigned_to_name" label="负责人" width="110" align="center">
            <template #default="scope">
              {{ scope.row.assigned_to_name || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="start_date" label="开始时间" width="140" align="center">
            <template #default="scope">
              {{ formatDateTime(scope.row.start_date) }}
            </template>
          </el-table-column>
          <el-table-column prop="end_date" label="结束时间" width="140" align="center">
            <template #default="scope">
              {{ formatDateTime(scope.row.end_date) }}
            </template>
          </el-table-column>
          <el-table-column prop="estimated_hours" label="预估工时" width="100" align="center">
            <template #default="scope">
              {{ scope.row.estimated_hours || 0 }}h
            </template>
          </el-table-column>
          <el-table-column prop="actual_hours" label="实际工时" width="100" align="center">
            <template #default="scope">
              {{ scope.row.actual_hours || 0 }}h
            </template>
          </el-table-column>
          <el-table-column label="操作" min-width="280" align="center" fixed="right">
            <template #default="scope">
              <div class="operation-buttons">
                <el-button type="primary" size="small" @click="handleViewTestCase(scope.row)">
                  查看用例
                </el-button>
                <el-button type="warning" size="small" @click="handleViewBugs(scope.row)">
                  查看缺陷
                </el-button>
                <el-button type="success" size="small" @click="handleEditRequirement(scope.row)">
                  编辑
                </el-button>
                <el-button type="danger" size="small" @click="handleDeleteRequirement(scope.row)">
                  删除
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Edit, ArrowLeft, Plus, Document, Warning, Delete } from '@element-plus/icons-vue'
import { getProject, getProjectVersionRequirements, getProjectIterations } from '@/api/project'
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
const requirementsLoading = ref(false)
const projectDetail = ref({})
const versionRequirements = ref([])
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

// 版本需求图表配置
const requirementChartOption = ref({
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
      name: '需求状态',
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

// 版本需求状态类型映射
const getRequirementStatusType = (status) => {
  const statusMap = {
    new: 'info',
    in_progress: 'warning',
    completed: 'success',
    cancelled: 'danger'
  }
  return statusMap[status] || 'info'
}

// 版本需求状态文本映射
const getRequirementStatusText = (status) => {
  const statusMap = {
    new: '未开始',
    in_progress: '进行中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return statusMap[status] || status || '-'  
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
  
  // 更新版本需求状态分布饼图
  const requirementStats = projectDetail.value.requirement_stats || {}
  requirementChartOption.value.series[0].data = [
    { value: requirementStats.new || 0, name: '新建' },
    { value: requirementStats.in_progress || 0, name: '进行中' },
    { value: requirementStats.completed || 0, name: '已完成' },
    { value: requirementStats.cancelled || 0, name: '已取消' }
  ]
}

// 获取项目详情
const fetchProjectDetail = async () => {
  loading.value = true
  try {
    const projectId = route.params.id
    const response = await getProject(projectId)
    // 假设后端返回的数据结构是 { project: { ... } }
    projectDetail.value = response.project || {}
    
    // 更新路由meta.title，使面包屑显示更具体的标题
    if (projectDetail.value.project_name) {
      // 更新路由meta.title
      route.meta.title = `项目详情 - ${projectDetail.value.project_name}`
    }
    
    // 获取版本需求列表
    await fetchVersionRequirements()
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

// 获取版本需求列表
const fetchVersionRequirements = async () => {
  requirementsLoading.value = true
  try {
    const projectId = route.params.id
    const response = await getProjectVersionRequirements(projectId)
    versionRequirements.value = response.version_requirements || []
  } catch (error) {
    console.error('获取版本需求列表失败:', error)
    ElMessage.error('获取版本需求列表失败')
    versionRequirements.value = []
  } finally {
    requirementsLoading.value = false
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

// 创建版本需求
const handleCreateRequirement = () => {
  ElMessage.info('创建需求功能待实现')
}

// 查看测试用例
const handleViewTestCase = (row) => {
  ElMessage.info(`查看需求${row.requirement_name}的测试用例`)
}

// 查看缺陷列表
const handleViewBugs = (row) => {
  ElMessage.info(`查看需求${row.requirement_name}的缺陷列表`)
}

// 编辑版本需求
const handleEditRequirement = (row) => {
  ElMessage.info(`编辑需求: ${row.requirement_name}`)
}

// 删除版本需求
const handleDeleteRequirement = (row) => {
  ElMessage.info(`删除需求: ${row.requirement_name}`)
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
  padding: 10px 0px;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* 统计项头部样式 */
.stat-header {
  text-align: center;
  margin-top: 5px;
  margin-bottom: -30px;
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

/* 操作按钮样式 */
.operation-buttons {
  display: flex;
  justify-content: center;
  gap: 10px;
}
</style>