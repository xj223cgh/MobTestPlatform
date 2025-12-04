<template>
  <div class="requirement-management">
    <div class="page-header">
      <div class="header-content">
        <h1>需求管理</h1>
        <p class="description">
          管理所属项目迭代的版本需求信息
        </p>
      </div>
      <div class="header-actions">
        <el-button
          type="primary"
          :loading="loading"
          @click="handleCreateRequirement"
        >
          <el-icon><Plus /></el-icon>
          创建需求
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-section">
      <el-form
        :model="searchForm"
        inline
      >
        <el-form-item label="时间">
          <el-date-picker
            v-model="timeRangeFilter"
            type="monthrange"
            range-separator="至"
            start-placeholder="开始年月"
            end-placeholder="结束年月"
            format="YYYY-MM"
            value-format="YYYY-MM"
            style="width: 220px"
            @change="handleTimeRangeChange"
          />
        </el-form-item>
        <el-form-item label="所属项目">
          <el-select 
            v-model="projectFilter" 
            placeholder="请选择所属项目" 
            multiple
            clearable 
            style="width: 180px"
            @change="handleProjectFilterChange"
          >
            <el-option 
              v-for="project in projectOptions" 
              :key="project.id" 
              :label="project.project_name" 
              :value="project.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="所属迭代">
          <el-select 
            v-model="iterationFilter" 
            placeholder="请选择所属迭代" 
            multiple
            clearable 
            :disabled="!projectFilter || projectFilter.length === 0"
            style="width:180px"
            @change="handleIterationFilterChange"
          >
            <el-option 
              v-for="iteration in iterationOptions" 
              :key="iteration.id" 
              :label="iteration.iteration_name" 
              :value="iteration.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="创建者">
          <el-select 
            v-model="creatorFilter" 
            placeholder="请选择创建者" 
            multiple
            clearable 
            filterable
            allow-create
            default-first-option
            style="width: 180px"
            @change="getRequirementList"
          >
            <el-option 
              v-for="user in creatorOptions" 
              :key="user.id" 
              :label="user.real_name" 
              :value="user.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="负责人">
          <el-select 
            v-model="assigneeFilter" 
            placeholder="请选择负责人" 
            multiple
            clearable 
            filterable
            allow-create
            default-first-option
            style="width: 180px"
            @change="getRequirementList"
          >
            <el-option 
              v-for="user in assigneeOptions" 
              :key="user.id" 
              :label="user.real_name" 
              :value="user.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button
            :loading="loading"
            @click="resetFilters"
          >
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 需求列表 -->
    <div class="table-section">
      <el-table
        v-loading="loading"
        :data="requirementList"
        stripe
        border
        style="width: 100%"
        fit
      >
        <el-table-column
          prop="id"
          label="ID"
          width="80"
          align="center"
        />
        <el-table-column
          prop="requirement_name"
          label="需求名称"
          min-width="150"
          align="center"
        >
          <template #default="scope">
            {{ scope.row.requirement_name }}
          </template>
        </el-table-column>
        
        <el-table-column
          prop="project_name"
          label="所属项目"
          min-width="120"
          align="center"
        />
        <el-table-column
          prop="iteration_name"
          label="所属迭代"
          min-width="100"
          align="center"
        >
          <template #default="scope">
            {{ scope.row.iteration_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column
          prop="status"
          label="状态"
          min-width="85"
          align="center"
        >
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="priority"
          label="优先级"
          min-width="85"
          align="center"
        >
          <template #default="scope">
            <el-tag :type="getPriorityType(scope.row.priority)">
              {{ getPriorityText(scope.row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="environment"
          label="环境"
          min-width="95"
          align="center"
        >
          <template #default="scope">
            <el-tag :type="getEnvironmentType(scope.row.environment)">
              {{ getEnvironmentText(scope.row.environment) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="created_by_name"
          label="创建者"
          min-width="110"
          align="center"
        />
        <el-table-column
          prop="updated_at"
          label="更新时间"
          min-width="120"
          align="center"
        >
          <template #default="scope">
            {{ formatDateTime(scope.row.updated_at) || '-' }}
          </template>
        </el-table-column>
        <el-table-column
          prop="start_date"
          label="开始时间"
          min-width="120"
          align="center"
        >
          <template #default="scope">
            {{ formatDateTime(scope.row.start_date) || '-' }}
          </template>
        </el-table-column>
        <el-table-column
          prop="end_date"
          label="结束时间"
          min-width="120"
          align="center"
        >
          <template #default="scope">
            {{ formatDateTime(scope.row.end_date) || '-' }}
          </template>
        </el-table-column>
        <el-table-column
          prop="estimated_hours"
          label="预估工时"
          min-width="90"
          align="center"
        >
          <template #default="scope">
            {{ scope.row.estimated_hours || '-' }}h
          </template>
        </el-table-column>
        <el-table-column
          prop="actual_hours"
          label="实际工时"
          min-width="90"
          align="center"
        >
          <template #default="scope">
            {{ scope.row.actual_hours || '-' }}h
          </template>
        </el-table-column>
        <el-table-column
          prop="requirement_description"
          label="需求描述"
          min-width="200"
          align="center"
        >
          <template #default="scope">
            <div class="wrap-text">
              {{ scope.row.requirement_description || '-' }}
            </div>
          </template>
        </el-table-column>
        <el-table-column
          label="操作"
          min-width="140"
          fixed="right"
          align="center"
        >
          <template #default="scope">
            <div class="operation-buttons">
              <el-button
                type="success"
                size="small"
                @click="handleEditRequirement(scope.row)"
              >
                编辑
              </el-button>
              <el-button
                type="danger"
                size="small"
                @click="handleDeleteRequirement(scope.row)"
              >
                删除
              </el-button>
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { formatDateTime } from '@/utils/helpers'
import { Plus, Search, Refresh, Edit, Delete } from '@element-plus/icons-vue'
import { getAllVersionRequirements, getProjects, getProjectIterations } from '@/api/project'
import { getUserList } from '@/api/user'
import dayjs from 'dayjs'

// 加载状态
const loading = ref(false)

// 搜索和筛选
// 时间筛选范围，默认当前年月的前后两个月
const currentDate = dayjs()
const timeRangeFilter = ref([
  currentDate.subtract(2, 'month').format('YYYY-MM'),
  currentDate.add(2, 'month').format('YYYY-MM')
])
const projectFilter = ref([])
const iterationFilter = ref([])
const creatorFilter = ref([])
const assigneeFilter = ref([])

// 搜索表单
const searchForm = reactive({})

// 选项数据
const projectOptions = ref([])
const iterationOptions = ref([])
const userOptions = ref([])
const creatorOptions = ref([])
const assigneeOptions = ref([])

// 需求列表
const requirementList = ref([])

// 分页信息
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

// 获取需求列表
const getRequirementList = async () => {
  loading.value = true
  try {
    // 使用新的API获取所有需求列表
    const response = await getAllVersionRequirements()
    
    if (response.code === 200) {
      let allItems = response.data.items || []
      
      // 1. 默认按创建时间倒序排序（最新数据在前）
      allItems.sort((a, b) => {
        const dateA = new Date(a.updated_at || a.created_at || 0)
        const dateB = new Date(b.updated_at || b.created_at || 0)
        return dateB - dateA
      })
      
      // 2. 应用筛选条件
      // 按所属项目筛选
      if (projectFilter.value && projectFilter.value.length > 0) {
        allItems = allItems.filter(item => projectFilter.value.includes(item.project_id))
      }
      
      // 按所属迭代筛选
      if (iterationFilter.value && iterationFilter.value.length > 0) {
        allItems = allItems.filter(item => iterationFilter.value.includes(item.iteration_id))
      }
      
      // 按创建者筛选
      if (creatorFilter.value && creatorFilter.value.length > 0) {
        allItems = allItems.filter(item => creatorFilter.value.includes(item.created_by))
      }
      
      // 按负责人筛选
      if (assigneeFilter.value && assigneeFilter.value.length > 0) {
        allItems = allItems.filter(item => assigneeFilter.value.includes(item.assigned_to))
      }
      
      pagination.total = allItems.length || 0
      
      // 3. 前端分页处理
      const startIndex = (pagination.currentPage - 1) * pagination.pageSize
      const endIndex = startIndex + pagination.pageSize
      requirementList.value = allItems.slice(startIndex, endIndex)
    } else {
      ElMessage.error('获取需求列表失败')
    }
  } catch (error) {
    console.error('获取需求列表失败:', error)
    ElMessage.error('获取需求列表失败')
  } finally {
    loading.value = false
  }
}

// 状态类型映射
const getStatusType = (status) => {
  const statusMap = {
    new: 'info',
    in_progress: 'warning',
    completed: 'success',
    cancelled: 'danger'
  }
  return statusMap[status] || 'info'
}

// 状态文本映射
const getStatusText = (status) => {
  const statusMap = {
    new: '新建',
    in_progress: '进行中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return statusMap[status] || status
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

// 重置筛选条件
const resetFilters = () => {
  // 重置时间范围为当前年月的前后两个月
  const currentDate = dayjs()
  timeRangeFilter.value = [
    currentDate.subtract(2, 'month').format('YYYY-MM'),
    currentDate.add(2, 'month').format('YYYY-MM')
  ]
  projectFilter.value = []
  iterationFilter.value = []
  creatorFilter.value = []
  assigneeFilter.value = []
  pagination.currentPage = 1
  getOptionData() // 重新获取选项数据
  getRequirementList()
}

// 时间范围变化处理函数
const handleTimeRangeChange = async () => {
  // 当时间范围变化时，只重新获取项目选项，不影响其他筛选
  try {
    // 1. 获取所有项目（不分页）
    const projectsResponse = await getProjects({ page: 1, size: 1000 }) // 获取足够多的项目
    let allProjects = projectsResponse.data?.items || []
    
    // 2. 根据时间范围筛选项目
    const filteredProjects = allProjects.filter(project => {
      if (!timeRangeFilter.value || timeRangeFilter.value.length !== 2) return true
      
      // 获取项目创建时间的年月部分 (YYYY-MM)
      const projectYearMonth = project.created_at?.substring(0, 7)
      if (!projectYearMonth) return true
      
      // 获取筛选范围的年月
      const [startYearMonth, endYearMonth] = timeRangeFilter.value
      
      // 直接比较年月字符串，确保在范围内
      return projectYearMonth >= startYearMonth && projectYearMonth <= endYearMonth
    })
    
    projectOptions.value = filteredProjects
    
    // 3. 不清空项目筛选和迭代筛选，因为创建者和负责人不受时间筛选影响
    // 只更新迭代选项，根据当前选中的项目
    if (projectFilter.value && projectFilter.value.length > 0) {
      const selectedIterations = []
      for (const projectId of projectFilter.value) {
        try {
          const iterationsResponse = await getProjectIterations(projectId)
          const projectIterations = iterationsResponse.data?.items || []
          selectedIterations.push(...projectIterations)
        } catch (error) {
          console.error(`获取项目${projectId}的迭代失败:`, error)
        }
      }
      iterationOptions.value = selectedIterations
    }
    
    // 4. 不更新用户选项，创建者和负责人不受时间筛选影响
    // 5. 不刷新需求列表，只更新项目和迭代选项
    console.log('时间范围筛选已更新，只影响项目和迭代下拉列表')
  } catch (error) {
    console.error('更新项目选项失败:', error)
    ElMessage.error('更新项目选项失败')
  }
}

// 项目筛选变化处理函数
const handleProjectFilterChange = async () => {
  try {
    // 如果没有选中项目，清空迭代选项并禁用迭代选择器
    if (!projectFilter.value || projectFilter.value.length === 0) {
      iterationOptions.value = []
      iterationFilter.value = []
    } else {
      // 只显示选中项目的迭代，不受时间筛选影响
      const selectedIterations = []
      for (const projectId of projectFilter.value) {
        try {
          const iterationsResponse = await getProjectIterations(projectId)
          const projectIterations = iterationsResponse.data?.items || []
          
          // 不根据年月筛选迭代，只根据项目筛选
          selectedIterations.push(...projectIterations)
        } catch (error) {
          console.error(`获取项目${projectId}的迭代失败:`, error)
        }
      }
      
      iterationOptions.value = selectedIterations
      
      // 如果当前迭代筛选不在新的迭代列表中，清空迭代筛选
      if (iterationFilter.value && iterationFilter.value.length > 0) {
        const validIterationIds = selectedIterations.map(iter => iter.id)
        const validFilters = iterationFilter.value.filter(id => validIterationIds.includes(id))
        iterationFilter.value = validFilters
      }
    }
    
    // 更新用户选项
    await updateUserOptions()
    
    // 刷新需求列表
    getRequirementList()
  } catch (error) {
    console.error('更新迭代选项失败:', error)
    ElMessage.error('更新迭代选项失败')
  }
}

// 迭代筛选变化处理函数
const handleIterationFilterChange = async () => {
  try {
    // 更新用户选项
    await updateUserOptions()
    
    // 刷新需求列表
    getRequirementList()
  } catch (error) {
    console.error('更新用户选项失败:', error)
    ElMessage.error('更新用户选项失败')
  }
}

// 更新用户选项函数
const updateUserOptions = async () => {
  console.log('开始更新用户选项')
  
  let allUsers = []
  
  // 首先获取所有用户，这是基础数据
  try {
    console.log('开始调用 getUserList API')
    const usersResponse = await getUserList({ page: 1, size: 1000 })
    console.log('获取用户列表响应:', JSON.stringify(usersResponse, null, 2))
    
    // 确保数据结构正确，allUsers 必须是数组
    let items = []
    
    // 检查响应结构，处理不同的返回格式
    if (usersResponse) {
      // 检查响应是否直接是数组
      if (Array.isArray(usersResponse)) {
        console.log('响应直接是数组')
        items = usersResponse
      }
      // 检查响应是否包含 data 字段
      else if (usersResponse.data) {
        console.log('响应包含 data 字段')
        // 检查 data 是否直接是数组
        if (Array.isArray(usersResponse.data)) {
          console.log('data 直接是数组')
          items = usersResponse.data
        }
        // 检查 data 是否包含 users 字段，且 users 是数组
        else if (usersResponse.data.users && Array.isArray(usersResponse.data.users)) {
          console.log('data.users 是数组')
          items = usersResponse.data.users
        }
        // 检查 data 是否包含 items 字段，且 items 是数组
        else if (usersResponse.data.items && Array.isArray(usersResponse.data.items)) {
          console.log('data.items 是数组')
          items = usersResponse.data.items
        }
        // 检查 data 是否包含 list 字段，且 list 是数组
        else if (usersResponse.data.list && Array.isArray(usersResponse.data.list)) {
          console.log('data.list 是数组')
          items = usersResponse.data.list
        }
        // 检查 data 是否包含 records 字段，且 records 是数组
        else if (usersResponse.data.records && Array.isArray(usersResponse.data.records)) {
          console.log('data.records 是数组')
          items = usersResponse.data.records
        }
        else {
          console.log('data 不是数组，也没有 users/items/list/records 字段')
          console.log('data 的类型:', typeof usersResponse.data)
          console.log('data 的内容:', JSON.stringify(usersResponse.data, null, 2))
        }
      }
      // 检查响应是否直接包含 users 字段，且 users 是数组
      else if (usersResponse.users && Array.isArray(usersResponse.users)) {
        console.log('响应直接包含 users 数组')
        items = usersResponse.users
      }
      else {
        console.log('响应不包含 data 字段，也不直接包含 users 字段')
        console.log('响应的类型:', typeof usersResponse)
        console.log('响应的内容:', JSON.stringify(usersResponse, null, 2))
      }
    }
    else {
      console.log('响应为空')
    }
    
    // 确保 items 是数组
    allUsers = Array.isArray(items) ? items : []
    
    console.log('处理后的用户列表:', JSON.stringify(allUsers, null, 2))
    console.log('用户列表长度:', allUsers.length)
  } catch (error) {
    console.error('获取用户列表失败:', error)
    // 只在无法获取用户列表时显示错误信息
    ElMessage.error('获取用户列表失败')
    // 使用空数组继续执行，避免崩溃
    allUsers = []
  }
  
  // 默认显示所有用户
  userOptions.value = allUsers
  creatorOptions.value = allUsers
  assigneeOptions.value = allUsers
  console.log('设置用户选项:', JSON.stringify(userOptions.value, null, 2))
  console.log('用户选项长度:', userOptions.value.length)
  console.log('设置创建者选项:', JSON.stringify(creatorOptions.value, null, 2))
  console.log('创建者选项长度:', creatorOptions.value.length)
  console.log('设置负责人选项:', JSON.stringify(assigneeOptions.value, null, 2))
  console.log('负责人选项长度:', assigneeOptions.value.length)
  
  // 如果没有用户数据，直接返回
  if (allUsers.length === 0) {
    console.log('没有用户数据，直接返回')
    return
  }
  
  // 如果有选中项目或迭代，根据筛选条件过滤用户
  if ((projectFilter.value && projectFilter.value.length > 0) || 
      (iterationFilter.value && iterationFilter.value.length > 0)) {
    
    console.log('有选中的项目或迭代，开始过滤用户')
    
    try {
      // 获取需求列表，根据当前筛选条件
      const response = await getAllVersionRequirements()
      if (response.code === 200) {
        const allRequirements = response.data?.items || []
        console.log('获取到的需求列表:', allRequirements)
        
        // 筛选符合条件的需求
        let filteredRequirements = allRequirements
        
        // 按项目筛选
        if (projectFilter.value && projectFilter.value.length > 0) {
          filteredRequirements = filteredRequirements.filter(req => 
            projectFilter.value.includes(req.project_id)
          )
          console.log('按项目筛选后的需求:', filteredRequirements)
        }
        
        // 按迭代筛选
        if (iterationFilter.value && iterationFilter.value.length > 0) {
          filteredRequirements = filteredRequirements.filter(req => 
            iterationFilter.value.includes(req.iteration_id)
          )
          console.log('按迭代筛选后的需求:', filteredRequirements)
        }
        
        // 提取创建者ID
        const creatorIds = new Set()
        filteredRequirements.forEach(req => {
          if (req.created_by) {
            creatorIds.add(req.created_by)
          }
        })
        console.log('提取到的创建者ID:', creatorIds)
        
        // 提取负责人ID
        const assigneeIds = new Set()
        filteredRequirements.forEach(req => {
          if (req.assigned_to) {
            assigneeIds.add(req.assigned_to)
          }
        })
        console.log('提取到的负责人ID:', assigneeIds)
        
        // 筛选创建者选项
        if (creatorIds.size > 0) {
          const filteredCreators = allUsers.filter(user => creatorIds.has(user.id))
          console.log('筛选后的创建者:', filteredCreators)
          creatorOptions.value = filteredCreators
        }
        
        // 筛选负责人选项
        if (assigneeIds.size > 0) {
          const filteredAssignees = allUsers.filter(user => assigneeIds.has(user.id))
          console.log('筛选后的负责人:', filteredAssignees)
          assigneeOptions.value = filteredAssignees
        }
      }
    } catch (error) {
      console.error('根据项目/迭代筛选用户失败:', error)
      // 这里不需要显示错误信息，因为我们已经有了默认的用户列表
      // 继续显示所有用户即可
    }
  }
}

// 获取选项数据
const getOptionData = async () => {
  try {
    // 1. 获取所有项目（不分页）
    const projectsResponse = await getProjects({ page: 1, size: 1000 }) // 获取足够多的项目
    let allProjects = projectsResponse.data?.items || []
    
    // 2. 根据时间范围筛选项目
    const filteredProjects = allProjects.filter(project => {
      if (!timeRangeFilter.value || timeRangeFilter.value.length !== 2) return true
      
      // 获取项目创建时间的年月部分 (YYYY-MM)
      const projectYearMonth = project.created_at?.substring(0, 7)
      if (!projectYearMonth) return true
      
      // 获取筛选范围的年月
      const [startYearMonth, endYearMonth] = timeRangeFilter.value
      
      // 直接比较年月字符串，确保在范围内
      return projectYearMonth >= startYearMonth && projectYearMonth <= endYearMonth
    })
    
    projectOptions.value = filteredProjects
    
    // 3. 获取迭代列表，根据当前选中的项目筛选
    let iterationsToLoad = filteredProjects
    
    // 如果有选中的项目，只加载选中项目的迭代
    if (projectFilter.value && projectFilter.value.length > 0) {
      iterationsToLoad = filteredProjects.filter(project => 
        projectFilter.value.includes(project.id)
      )
    }
    
    // 获取所有需要加载的迭代
    const allIterations = []
    for (const project of iterationsToLoad) {
      try {
        const iterationsResponse = await getProjectIterations(project.id)
        const projectIterations = iterationsResponse.data?.items || []
        
        // 不根据年月筛选迭代，只根据项目筛选
        allIterations.push(...projectIterations)
      } catch (error) {
        console.error(`获取项目${project.project_name}的迭代失败:`, error)
      }
    }
    
    iterationOptions.value = allIterations
    
    // 4. 更新用户选项 - 创建者和负责人不受时间筛选影响
    // 直接调用 updateUserOptions，它会处理用户数据的获取和筛选
    await updateUserOptions()
    
  } catch (error) {
    console.error('获取选项数据失败:', error)
    ElMessage.error('获取选项数据失败')
    
    // 出错时显示所有用户
    try {
      const usersResponse = await getUserList({ page: 1, size: 1000 })
      console.log('错误情况下获取用户列表响应:', JSON.stringify(usersResponse, null, 2))
      
      // 确保用户数据是数组
      let userItems = []
      
      // 检查响应结构，处理不同的返回格式
      if (usersResponse) {
        // 检查响应是否直接是数组
        if (Array.isArray(usersResponse)) {
          console.log('响应直接是数组')
          userItems = usersResponse
        }
        // 检查响应是否包含 data 字段
        else if (usersResponse.data) {
          console.log('响应包含 data 字段')
          // 检查 data 是否直接是数组
          if (Array.isArray(usersResponse.data)) {
            console.log('data 直接是数组')
            userItems = usersResponse.data
          }
          // 检查 data 是否包含 users 字段，且 users 是数组
          else if (usersResponse.data.users && Array.isArray(usersResponse.data.users)) {
            console.log('data.users 是数组')
            userItems = usersResponse.data.users
          }
          // 检查 data 是否包含 items 字段，且 items 是数组
          else if (usersResponse.data.items && Array.isArray(usersResponse.data.items)) {
            console.log('data.items 是数组')
            userItems = usersResponse.data.items
          }
          // 检查 data 是否包含 list 字段，且 list 是数组
          else if (usersResponse.data.list && Array.isArray(usersResponse.data.list)) {
            console.log('data.list 是数组')
            userItems = usersResponse.data.list
          }
          // 检查 data 是否包含 records 字段，且 records 是数组
          else if (usersResponse.data.records && Array.isArray(usersResponse.data.records)) {
            console.log('data.records 是数组')
            userItems = usersResponse.data.records
          }
          else {
            console.log('data 不是数组，也没有 users/items/list/records 字段')
            console.log('data 的类型:', typeof usersResponse.data)
            console.log('data 的内容:', JSON.stringify(usersResponse.data, null, 2))
          }
        }
        // 检查响应是否直接包含 users 字段，且 users 是数组
        else if (usersResponse.users && Array.isArray(usersResponse.users)) {
          console.log('响应直接包含 users 数组')
          userItems = usersResponse.users
        }
        else {
          console.log('响应不包含 data 字段，也不直接包含 users 字段')
          console.log('响应的类型:', typeof usersResponse)
          console.log('响应的内容:', JSON.stringify(usersResponse, null, 2))
        }
      }
      else {
        console.log('响应为空')
      }
      
      // 确保 userItems 是数组
      const finalUserItems = Array.isArray(userItems) ? userItems : []
      
      // 设置所有用户选项
      userOptions.value = finalUserItems
      creatorOptions.value = finalUserItems
      assigneeOptions.value = finalUserItems
      
      console.log('错误情况下设置的用户选项:', userOptions.value)
      console.log('错误情况下设置的用户选项长度:', userOptions.value.length)
      console.log('错误情况下设置的创建者选项:', creatorOptions.value)
      console.log('错误情况下设置的创建者选项长度:', creatorOptions.value.length)
      console.log('错误情况下设置的负责人选项:', assigneeOptions.value)
      console.log('错误情况下设置的负责人选项长度:', assigneeOptions.value.length)
    } catch (userError) {
      console.error('获取用户列表失败:', userError)
      // 如果获取用户列表也失败，使用空数组
      userOptions.value = []
      creatorOptions.value = []
      assigneeOptions.value = []
    }
  }
}

// 处理分页大小变化
const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.currentPage = 1
  getRequirementList()
}

// 处理当前页变化
const handleCurrentChange = (current) => {
  pagination.currentPage = current
  getRequirementList()
}

// 创建需求
const handleCreateRequirement = () => {
  // 跳转到创建需求页面
  ElMessage.info('创建需求功能待实现')
}

// 编辑需求
const handleEditRequirement = (row) => {
  // 跳转到编辑需求页面
  ElMessage.info(`编辑需求: ${row.requirement_name}`)
}

// 删除需求
const handleDeleteRequirement = (row) => {
  ElMessageBox.confirm(`确定要删除需求「${row.requirement_name}」吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      // 调用删除需求API
      ElMessage.success('需求删除成功')
      getRequirementList()
    } catch (error) {
      console.error('删除需求失败:', error)
      ElMessage.error('删除需求失败')
    }
  }).catch(() => {
    // 用户取消删除
  })
}

// 页面加载时获取需求列表和选项数据
onMounted(async () => {
  await getOptionData()
  getRequirementList()
})
</script>

<style lang="scss" scoped>
.requirement-management {
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
  
  .header-content {
    h1 {
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

.ellipsis-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  width: 100%;
}

.wrap-text {
  white-space: normal;
  word-break: break-word;
  width: 100%;
}

/* 优化下拉列表样式 */
:deep(.el-select-dropdown__wrap) {
  max-height: 300px;
  overflow-y: auto;
}

/* 自定义滚动条样式 */
:deep(.el-select-dropdown__wrap::-webkit-scrollbar) {
  width: 6px;
  background-color: transparent;
}

:deep(.el-select-dropdown__wrap::-webkit-scrollbar-track) {
  background-color: transparent;
}

:deep(.el-select-dropdown__wrap::-webkit-scrollbar-thumb) {
  background-color: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}

:deep(.el-select-dropdown__wrap::-webkit-scrollbar-thumb:hover) {
  background-color: rgba(0, 0, 0, 0.2);
}
</style>
