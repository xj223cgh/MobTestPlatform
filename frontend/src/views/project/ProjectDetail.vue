<template>
  <div class="project-detail">
    <!-- 项目基本信息 -->
    <div class="info-section">
      <el-card
        shadow="hover"
        class="info-card"
      >
        <template #header>
          <div class="card-header">
            <h2>项目名称: {{ projectDetail.project_name || '未知项目' }}</h2>
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
              {{ getPriorityText(projectDetail.priority) || '-' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="负责人">
            {{ projectDetail.owner_name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建者">
            {{ projectDetail.creator_name || '-' }}
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

    <!-- 编辑项目对话框 -->
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
            style="width: 100%;"
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
        
        <!-- 项目成员 -->
        <el-form-item label="项目成员">
          <el-select
            v-model="projectForm.selectedUsers"
            multiple
            placeholder="请选择项目成员"
            style="width: 100%;"
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
          <div style="margin-top: 5px; font-size: 12px; color: #909399;">
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

    <!-- 项目描述和链接 -->
    <el-row
      :gutter="20"
      class="info-section-row"
    >
      <!-- 项目链接 -->
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

      <!-- 项目描述 -->
      <el-col :span="12">
        <div class="info-section">
          <el-card
            shadow="hover"
            class="info-card equal-height-card"
          >
            <template #header>
              <div class="card-header">
                <span>项目描述</span>
                <span class="description-count">{{ (projectDetail.description || '').length }}/{{ 100 }}</span>
              </div>
            </template>
            <div class="description-content">
              {{ projectDetail.description || '暂无描述' }}
            </div>
          </el-card>
        </div>
      </el-col>
    </el-row>

    <!-- 项目统计 -->
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
        
        <!-- 统计概览 -->
        <el-row
          :gutter="20"
          class="stats-overview"
        >
          <!-- 缺陷统计 -->
          <el-col :span="6">
            <div class="stat-item-with-chart">
              <div class="stat-header">
                <div class="stat-label">
                  缺陷总数
                </div>
                <div class="stat-value">
                  {{ projectDetail.bug_stats?.total || 0 }}
                </div>
              </div>
              <div class="chart-container-small">
                <v-chart
                  :option="bugCategoryChartOption"
                  autoresize
                />
              </div>
            </div>
          </el-col>
          
          <!-- 用例统计 -->
          <el-col :span="6">
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
            </div>
          </el-col>
          
          <!-- 迭代统计 -->
          <el-col :span="6">
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
            </div>
          </el-col>
          
          <!-- 版本需求统计 -->
          <el-col :span="6">
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
import { getProject, updateProject } from '@/api/project'
import { getUserList } from '@/api/user'
import { useUserStore } from '@/stores/user'
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

// 编辑对话框相关数据
const dialogVisible = ref(false)
const dialogTitle = ref('')
const dialogLoading = ref(false)
const projectFormRef = ref(null)
const editingProjectId = ref(null)

// 所有用户列表，用于选择项目成员
const allUsers = ref([])

// 表单数据
const projectForm = reactive({
  project_name: '',
  description: '',
  status: 'not_started',
  priority: 'medium',
  owner_id: '',
  start_date: '',
  end_date: '',
  doc_url: '',
  pipeline_url: '',
  selectedUsers: []
})

// 获取所有用户列表
const getAllUsers = async () => {
  try {
    const response = await getUserList()
    allUsers.value = response.data?.users || []
  } catch (error) {
    console.error('获取用户列表失败:', error)
    ElMessage.error('获取用户列表失败')
  }
}

// 监听项目负责人变化
watch(() => projectForm.owner_id, (newOwnerId, oldOwnerId) => {
  if (!newOwnerId) return
  
  // 先过滤掉旧的负责人ID（如果存在），然后添加新的负责人ID
  const updatedUsers = projectForm.selectedUsers.filter(id => id !== oldOwnerId)
  
  // 确保新的负责人ID被添加到列表中
  if (!updatedUsers.includes(newOwnerId)) {
    updatedUsers.push(newOwnerId)
  }
  
  // 更新项目成员列表
  projectForm.selectedUsers = updatedUsers
})

// 处理项目负责人变化，确保项目成员列表正确
const handleOwnerChange = () => {
  // 这个函数会被watch函数自动处理，这里保留为空函数以保持与项目列表页面的一致性
}

// 处理项目成员变化，确保当前负责人无法被删除
const handleMembersChange = () => {
  if (!projectForm.owner_id) return
  
  // 检查当前负责人是否在项目成员列表中
  if (!projectForm.selectedUsers.includes(projectForm.owner_id)) {
    // 如果不在，自动添加回列表
    projectForm.selectedUsers.push(projectForm.owner_id)
    // 显示提示信息
    ElMessage.warning('当前项目负责人无法从成员列表中删除')
  }
}

// 用于项目成员下拉列表的排序，将负责人排在顶部
const getSortedUsers = () => {
  if (!projectForm.owner_id) return allUsers.value
  
  // 创建用户列表的副本，避免修改原始数据
  const sortedUsers = [...allUsers.value]
  
  // 排序：将项目负责人排在最前面
  return sortedUsers.sort((a, b) => {
    if (a.id == projectForm.owner_id) return -1
    if (b.id == projectForm.owner_id) return 1
    return 0
  })
}

// 表单验证规则
const projectRules = {
  project_name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 1, max: 100, message: '项目名称长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入项目描述', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择项目状态', trigger: 'change' }
  ],
  priority: [
    { required: true, message: '请选择项目优先级', trigger: 'change' }
  ],
  owner_id: [
    { required: true, message: '请选择项目负责人', trigger: 'change' }
  ],
  start_date: [
    { required: true, message: '请选择开始日期', trigger: 'change' }
  ],
  end_date: [
    { required: true, message: '请选择结束日期', trigger: 'change' }
  ]
}

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
  // 利用ECharts默认行为：值为0的数据项不会显示在饼图上，但会保留在图例中
  
  // 更新缺陷分类饼图 - 高优先级红色、中优先级黄色、低优先级绿色
  const bugStats = projectDetail.value.bug_stats || {}
  bugCategoryChartOption.value.series[0].data = [
    { value: bugStats.high || 0, name: '高优先级', itemStyle: { color: '#ff6e6e' } },
    { value: bugStats.medium || 0, name: '中优先级', itemStyle: { color: '#ffc107' } },
    { value: bugStats.low || 0, name: '低优先级', itemStyle: { color: '#5cb85c' } }
  ]
  
  // 更新用例执行情况饼图 - 通过绿色、失败红色、阻塞黄色、不适用紫色、未执行灰色
  const caseStats = projectDetail.value.case_stats || {}
  caseExecutionChartOption.value.series[0].data = [
    { value: caseStats.passed || 0, name: '通过', itemStyle: { color: '#5cb85c' } },
    { value: caseStats.failed || 0, name: '失败', itemStyle: { color: '#ff6e6e' } },
    { value: caseStats.blocked || 0, name: '阻塞', itemStyle: { color: '#ffc107' } },
    { value: caseStats.not_applicable || 0, name: '不适用', itemStyle: { color: '#8e44ad' } },
    { value: caseStats.not_run || 0, name: '未执行', itemStyle: { color: '#a6a6a6' } }
  ]
  
  // 更新迭代统计饼图 - 与实际迭代表状态属性值对应
  const iterationStats = projectDetail.value.iteration_stats || {}
  
  // 状态映射，将英文状态转换为中文显示，保持与后端一致
  const statusMap = {
    'planning': '规划中',
    'active': '进行中',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  
  // 直接使用后端返回的统计数据，添加对应颜色
  iterationChartOption.value.series[0].data = [
    { name: statusMap['planning'], value: iterationStats.planning || 0, itemStyle: { color: '#428bca' } },
    { name: statusMap['active'], value: iterationStats.active || 0, itemStyle: { color: '#5cb85c' } },
    { name: statusMap['completed'], value: iterationStats.completed || 0, itemStyle: { color: '#ffc107' } },
    { name: statusMap['cancelled'], value: iterationStats.cancelled || 0, itemStyle: { color: '#ff6e6e' } }
  ]
  
  // 更新需求状态分布饼图 - 新建灰色、进行中黄色、已完成绿色、已取消红色
  const requirementStats = projectDetail.value.requirement_stats || {}
  requirementChartOption.value.series[0].data = [
    { value: requirementStats.new || 0, name: '新建', itemStyle: { color: '#a6a6a6' } },
    { value: requirementStats.in_progress || 0, name: '进行中', itemStyle: { color: '#ffc107' } },
    { value: requirementStats.completed || 0, name: '已完成', itemStyle: { color: '#5cb85c' } },
    { value: requirementStats.cancelled || 0, name: '已取消', itemStyle: { color: '#ff6e6e' } }
  ]

}

// 获取项目详情
const fetchProjectDetail = async () => {
  loading.value = true
  try {
    const projectId = route.params.id
    const response = await getProject(projectId)
    // 后端返回的数据结构是 { code: 200, message: 'success', data: { project: {...} } }
    projectDetail.value = response.data?.project || {}
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

// 重置表单
const resetForm = () => {
  if (projectFormRef.value) {
    projectFormRef.value.resetFields()
  }
  editingProjectId.value = null
  Object.assign(projectForm, {
    project_name: '',
    description: '',
    status: 'not_started',
    priority: 'medium',
    owner_id: '',
    start_date: '',
    end_date: '',
    doc_url: '',
    pipeline_url: '',
    selectedUsers: []
  })
}

// 打开编辑项目对话框
const handleEdit = () => {
  dialogTitle.value = '编辑项目'
  editingProjectId.value = projectDetail.value.id
  
  // 转换项目成员数据为多选格式
  const members = projectDetail.value.members || []
  const selectedUsers = members.map(member => member.user_id)
  
  // 设置表单数据
  Object.assign(projectForm, {
    project_name: projectDetail.value.project_name || '',
    description: projectDetail.value.description || '',
    status: projectDetail.value.status || 'not_started',
    priority: projectDetail.value.priority || 'medium',
    owner_id: projectDetail.value.owner_id || '',
    start_date: projectDetail.value.start_date || '',
    end_date: projectDetail.value.end_date || '',
    doc_url: projectDetail.value.doc_url || '',
    pipeline_url: projectDetail.value.pipeline_url || '',
    selectedUsers: selectedUsers
  })
  getAllUsers()
  dialogVisible.value = true
}

// 保存项目
const handleSaveProject = async () => {
  if (!projectFormRef.value) return
  
  await projectFormRef.value.validate()
  
  // 引入useUserStore获取当前登录用户信息
  const userStore = useUserStore()
  const currentUserId = userStore.userInfo.id
  
  // 构建保存数据，将selectedUsers转换为members数组格式
  const saveData = { ...projectForm }
  
  // 只有创建项目时才设置creator_id，编辑时不修改创建者
  if (!editingProjectId.value) {
    // 添加创建者ID为当前登录用户ID
    saveData.creator_id = currentUserId
  }
  
  // 转换多选用户为members数组格式，固定使用tester角色
  saveData.members = saveData.selectedUsers.map(userId => ({
    user_id: userId,
    role: 'tester' // 固定默认角色为tester
  }))
  
  // 删除不需要发送给后端的字段
  delete saveData.selectedUsers
  
  dialogLoading.value = true
  try {
    const projectId = projectDetail.value.id
    const response = await updateProject(projectId, saveData)
    
    // 更新本地项目详情数据
    Object.assign(projectDetail.value, response.data.project || {})
    
    ElMessage.success('项目更新成功')
    dialogVisible.value = false
  } catch (error) {
    console.error('更新项目失败:', error)
    ElMessage.error('项目更新失败')
  } finally {
    dialogLoading.value = false
  }
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