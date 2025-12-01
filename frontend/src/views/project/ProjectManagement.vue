<template>
  <div class="project-management">
    <div class="page-header">
      <div class="header-content">
        <h1>项目管理</h1>
        <p class="description">管理系统项目信息</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="handleCreateProject" :loading="loading">
          <el-icon><Plus /></el-icon>
          创建项目
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-section">
      <el-form :model="searchForm" inline>
        <el-form-item label="项目名称">
          <el-input
            v-model="searchQuery"
            placeholder="请输入项目名称"
            clearable
            @clear="getProjectList"
            @keyup.enter="getProjectList"
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select 
            v-model="statusFilter" 
            placeholder="全部状态" 
            clearable 
            @clear="getProjectList"
            style="width: 120px"
          >
            <el-option label="全部" value=""></el-option>
            <el-option label="未开始" value="not_started"></el-option>
            <el-option label="进行中" value="in_progress"></el-option>
            <el-option label="已暂停" value="paused"></el-option>
            <el-option label="已完成" value="completed"></el-option>
            <el-option label="已关闭" value="closed"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="优先级">
          <el-select 
            v-model="priorityFilter" 
            placeholder="全部优先级" 
            clearable 
            @clear="getProjectList"
            style="width: 120px"
          >
            <el-option label="全部" value=""></el-option>
            <el-option label="高" value="high"></el-option>
            <el-option label="中" value="medium"></el-option>
            <el-option label="低" value="low"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="getProjectList" :loading="loading">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetFilters" :loading="loading">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 项目列表 -->
    <div class="table-section">
      <el-table
        v-loading="loading"
        :data="projectList"
        stripe
        border
        style="width: 100%"
        fit
      >
      <el-table-column prop="id" label="项目ID" type="index" width="100" fixed="left" align="center"></el-table-column>
      <el-table-column prop="project_name" label="项目名称" min-width="150" fixed="left" align="center">
          <template #default="scope">
            {{ scope.row.project_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" min-width="80" align="center">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">{{ getStatusText(scope.row.status) }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="priority" label="优先级" min-width="80" align="center">
          <template #default="scope">
            <el-tag :type="getPriorityType(scope.row.priority)">{{ getPriorityText(scope.row.priority) || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="creator_name" label="创建者" min-width="100" align="center">
          <template #default="scope">
            {{ scope.row.creator_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="owner_name" label="负责人" min-width="100" align="center">
          <template #default="scope">
            {{ scope.row.owner_name || '-' }}
          </template>
        </el-table-column>   
        <el-table-column label="开始日期" min-width="120" align="center">
          <template #default="scope">
            {{ formatDateTime(scope.row.start_date) }}
          </template>
        </el-table-column>
        <el-table-column label="结束日期" min-width="120" align="center">
          <template #default="scope">
            {{ formatDateTime(scope.row.end_date) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="190" fixed="right" align="center">
          <template #default="scope">
            <div class="operation-buttons">
              <el-button type="primary" size="small" @click="handleViewProject(scope.row)">查看</el-button>
              <el-button type="success" size="small" @click="handleEditProject(scope.row)">编辑</el-button>
              <el-button type="danger" size="small" @click="handleDeleteProject(scope.row)" :disabled="scope.row.is_owner">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
    </div>
    
    <!-- 分页 - 固定在右侧区域底部 -->
    <div class="fixed-pagination">
      <el-pagination
        :current-page="pagination.currentPage"
        :page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="pagination.total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Search, Refresh } from '@element-plus/icons-vue'
import { getProjects } from '@/api/project'
import { useRouter } from 'vue-router'
import dayjs from 'dayjs'

// 响应式数据
const loading = ref(false)
const projectList = ref([])

// 路由实例
const router = useRouter()

// 搜索和筛选
const searchQuery = ref('')
const statusFilter = ref('')

const priorityFilter = ref('')

// 搜索表单
const searchForm = reactive({})

// 分页
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

// 时间格式化函数
const formatDateTime = (dateTime) => {
  return dateTime ? dayjs(dateTime).format('YYYY-MM-DD HH:mm:ss') : '-' 
}

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

// 获取项目列表
const getProjectList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.currentPage,
      size: pagination.pageSize,
      search: searchQuery.value,
      status: statusFilter.value,

      priority: priorityFilter.value
    }
    
    const response = await getProjects(params)
    // 后端返回标准格式：{code: 200, message: 'success', data: {items: [...], total: 10}}
    projectList.value = response.data?.items || []
    pagination.total = response.data?.total || 0
  } catch (error) {
    console.error('获取项目列表失败:', error)
    ElMessage.error('获取项目列表失败')
    projectList.value = []
    pagination.total = 0
  } finally {
    loading.value = false
  }
}

// 重置筛选条件
const resetFilters = () => {
  searchQuery.value = ''
  statusFilter.value = ''
  priorityFilter.value = ''
  pagination.currentPage = 1
  getProjectList()
}

// 分页大小变化
const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.currentPage = 1
  getProjectList()
}

// 当前页码变化
const handleCurrentChange = (current) => {
  pagination.currentPage = current
  getProjectList()
}

// 创建项目
const handleCreateProject = () => {
  // 这里可以跳转到创建项目页面或打开创建项目对话框
  ElMessage.info('创建项目功能待实现')
}

// 查看项目
const handleViewProject = (row) => {
  // 跳转到项目详情页面
  router.push(`/projects/${row.id}`)
}

// 编辑项目
const handleEditProject = (row) => {
  // 这里可以跳转到编辑项目页面或打开编辑项目对话框
  ElMessage.info(`编辑项目: ${row.project_name}`)
}

// 删除项目
const handleDeleteProject = (row) => {
  // 这里可以实现删除项目功能
  ElMessage.info(`删除项目: ${row.project_name}`)
}

// 生命周期钩子 - 组件挂载时获取项目列表
onMounted(() => {
  getProjectList()
})
</script>

<style lang="scss" scoped>
.project-management {
  padding: 20px;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  
  .header-content h1 {
    margin: 0;
    font-size: 24px;
    font-weight: 500;
    color: #303133;
  }
  
  .description {
    margin: 8px 0 0;
    color: #606266;
    font-size: 14px;
  }
}

.header-actions {
  display: flex;
  gap: 10px;
}

.search-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.table-section {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 70px; /* 为固定的分页组件留出空间 */
}

/* 固定分页组件样式 */
.fixed-pagination {
  position: fixed;
  bottom: 0;
  right: 0;
  left: 240px;
  z-index: 100;
  background: white;
  padding: 15px 20px;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: center;
  align-items: center;
}

.fixed-pagination .pagination {
  margin: 0;
  text-align: center;
  border-top: none;
  width: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .fixed-pagination {
    left: 0;
    right: 0;
  }
  
  .table-section {
    margin-bottom: 70px;
  }
}

.operation-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
  align-items: center;
}
</style>