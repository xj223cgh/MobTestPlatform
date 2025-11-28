<template>
  <div class="test-case-management">
    <div class="page-header">
      <div class="header-content">
        <h1>测试用例管理</h1>
        <p class="description">管理和执行测试用例</p>
      </div>
      <div class="header-tabs">
        <el-tabs v-model="activeTab" @tab-click="handleTabClick">
          <el-tab-pane label="用例列表" name="list">
            <!-- 默认显示用例列表内容 -->
          </el-tab-pane>
          <el-tab-pane label="用例评审" name="reviews">
            <!-- 用例评审内容将通过路由显示 -->
          </el-tab-pane>
        </el-tabs>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          新建用例
        </el-button>
        <el-button @click="handleImport">
          <el-icon><Upload /></el-icon>
          导入用例
        </el-button>
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          导出用例
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon total">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ stats.total }}</div>
              <div class="stat-label">用例总数</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon passed">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ stats.passed }}</div>
              <div class="stat-label">通过用例</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon failed">
              <el-icon><CircleClose /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ stats.failed }}</div>
              <div class="stat-label">失败用例</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon pending">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ stats.pending }}</div>
              <div class="stat-label">待执行用例</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-section">
      <el-form :model="searchForm" inline>
        <el-form-item label="用例名称">
          <el-input
            v-model="searchForm.name"
            placeholder="请输入用例名称"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="模块">
          <el-select
            v-model="searchForm.module"
            placeholder="请选择模块"
            clearable
            @clear="handleSearch"
            @change="handleSearch"
          >
            <el-option label="登录模块" value="login" />
            <el-option label="用户管理" value="user" />
            <el-option label="设备管理" value="device" />
            <el-option label="测试管理" value="test" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select
            v-model="searchForm.priority"
            placeholder="请选择优先级"
            clearable
            @clear="handleSearch"
            @change="handleSearch"
          >
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="searchForm.status"
            placeholder="请选择状态"
            clearable
            @clear="handleSearch"
            @change="handleSearch"
          >
            <el-option label="通过" value="passed" />
            <el-option label="失败" value="failed" />
            <el-option label="待执行" value="pending" />
            <el-option label="跳过" value="skipped" />
          </el-select>
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
    </div>

    <!-- 测试用例表格 -->
    <div class="table-section">
      <el-table
        v-loading="loading"
        :data="testCaseList"
        stripe
        border
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="用例名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="module" label="模块" width="100">
          <template #default="{ row }">
            <el-tag :type="getModuleTagType(row.module)">
              {{ getModuleLabel(row.module) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="80">
          <template #default="{ row }">
            <el-tag :type="getPriorityTagType(row.priority)">
              {{ getPriorityLabel(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="creator" label="创建者" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="handleView(row)"
            >
              查看
            </el-button>
            <el-button
              type="success"
              size="small"
              @click="handleExecute(row)"
            >
              执行
            </el-button>
            <el-button
              type="warning"
              size="small"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 批量操作 -->
      <div class="batch-actions" v-if="selectedCases.length > 0">
        <span>已选择 {{ selectedCases.length }} 项</span>
        <el-button type="success" @click="handleBatchExecute">
          批量执行
        </el-button>
        <el-button type="danger" @click="handleBatchDelete">
          批量删除
        </el-button>
      </div>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          current-page="pagination.page"
          page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 测试用例表单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="testCaseFormRef"
        :model="testCaseForm"
        :rules="testCaseRules"
        label-width="100px"
      >
        <el-form-item label="用例名称" prop="name">
          <el-input
            v-model="testCaseForm.name"
            placeholder="请输入用例名称"
          />
        </el-form-item>
        <el-form-item label="所属模块" prop="module">
          <el-select v-model="testCaseForm.module" placeholder="请选择模块">
            <el-option label="登录模块" value="login" />
            <el-option label="用户管理" value="user" />
            <el-option label="设备管理" value="device" />
            <el-option label="测试管理" value="test" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-radio-group v-model="testCaseForm.priority">
            <el-radio label="high">高</el-radio>
            <el-radio label="medium">中</el-radio>
            <el-radio label="low">低</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="前置条件" prop="preconditions">
          <el-input
            v-model="testCaseForm.preconditions"
            type="textarea"
            :rows="3"
            placeholder="请输入前置条件"
          />
        </el-form-item>
        <el-form-item label="测试步骤" prop="steps">
          <el-input
            v-model="testCaseForm.steps"
            type="textarea"
            :rows="5"
            placeholder="请输入测试步骤，每行一个步骤"
          />
        </el-form-item>
        <el-form-item label="预期结果" prop="expected_result">
          <el-input
            v-model="testCaseForm.expected_result"
            type="textarea"
            :rows="3"
            placeholder="请输入预期结果"
          />
        </el-form-item>
        <el-form-item label="备注" prop="remarks">
          <el-input
            v-model="testCaseForm.remarks"
            type="textarea"
            :rows="2"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 测试用例详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="测试用例详情"
      width="800px"
    >
      <div class="test-case-detail" v-if="currentTestCase">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="用例ID">{{ currentTestCase.id }}</el-descriptions-item>
          <el-descriptions-item label="用例名称">{{ currentTestCase.name }}</el-descriptions-item>
          <el-descriptions-item label="所属模块">
            <el-tag :type="getModuleTagType(currentTestCase.module)">
              {{ getModuleLabel(currentTestCase.module) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="优先级">
            <el-tag :type="getPriorityTagType(currentTestCase.priority)">
              {{ getPriorityLabel(currentTestCase.priority) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTagType(currentTestCase.status)">
              {{ getStatusLabel(currentTestCase.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建者">{{ currentTestCase.creator }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDateTime(currentTestCase.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDateTime(currentTestCase.updated_at) }}</el-descriptions-item>
          <el-descriptions-item label="前置条件" :span="2">{{ currentTestCase.preconditions || '-' }}</el-descriptions-item>
          <el-descriptions-item label="测试步骤" :span="2">
            <div class="steps-content">
              {{ currentTestCase.steps }}
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="预期结果" :span="2">{{ currentTestCase.expected_result || '-' }}</el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">{{ currentTestCase.remarks || '-' }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, Upload, Download, Document, CircleCheck, CircleClose, Clock } from '@element-plus/icons-vue'
import { getTestCaseList, createTestCase, updateTestCase, deleteTestCase, getTestCaseStats, batchDeleteTestCases, exportTestCases } from '@/api/testCase'
import dayjs from 'dayjs'

// 响应式数据
const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const isEdit = ref(false)
const dialogTitle = ref('')
const testCaseFormRef = ref()
const currentTestCase = ref(null)
const selectedCases = ref([])
const activeTab = ref('list')

// 统计数据
const stats = reactive({
  total: 0,
  passed: 0,
  failed: 0,
  pending: 0
})

// 搜索表单
const searchForm = reactive({
  name: '',
  module: '',
  priority: '',
  status: ''
})

// 测试用例表单
const testCaseForm = reactive({
  id: null,
  name: '',
  module: '',
  priority: 'medium',
  preconditions: '',
  steps: '',
  expected_result: '',
  remarks: ''
})

// 表单验证规则
const testCaseRules = {
  name: [
    { required: true, message: '请输入用例名称', trigger: 'blur' }
  ],
  module: [
    { required: true, message: '请选择模块', trigger: 'change' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ],
  steps: [
    { required: true, message: '请输入测试步骤', trigger: 'blur' }
  ]
}

// 测试用例列表
const testCaseList = ref([])

// 分页
const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

// 获取测试用例列表
const fetchTestCaseList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      ...searchForm
    }
    const response = await getTestCaseList(params)
    if (response.success) {
      testCaseList.value = response.data.list
      pagination.total = response.data.total
    } else {
      ElMessage.error(response.message || '获取测试用例列表失败')
    }
  } catch (error) {
    console.error('获取测试用例列表失败:', error)
    ElMessage.error('获取测试用例列表失败')
  } finally {
    loading.value = false
  }
}

// 获取测试用例统计
const fetchTestCaseStats = async () => {
  try {
    const response = await getTestCaseStats()
    if (response.success) {
      Object.assign(stats, response.data)
    }
  } catch (error) {
    console.error('获取测试用例统计失败:', error)
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchTestCaseList()
}

// 重置搜索
const handleReset = () => {
  Object.assign(searchForm, {
    name: '',
    module: '',
    priority: '',
    status: ''
  })
  handleSearch()
}

// 新增测试用例
const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新建测试用例'
  dialogVisible.value = true
  resetForm()
}

// 编辑测试用例
const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑测试用例'
  dialogVisible.value = true
  Object.assign(testCaseForm, {
    id: row.id,
    name: row.name,
    module: row.module,
    priority: row.priority,
    preconditions: row.preconditions,
    steps: row.steps,
    expected_result: row.expected_result,
    remarks: row.remarks
  })
}

// 查看测试用例详情
const handleView = (row) => {
  currentTestCase.value = row
  detailDialogVisible.value = true
}

// 执行测试用例
const handleExecute = (row) => {
  ElMessage.success(`正在执行测试用例: ${row.name}`)
  // 这里可以添加实际的执行逻辑
}

// 删除测试用例
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除测试用例 "${row.name}" 吗？此操作不可恢复。`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const response = await deleteTestCase(row.id)
      if (response.success) {
        ElMessage.success('删除成功')
        fetchTestCaseList()
        fetchTestCaseStats()
      } else {
        ElMessage.error(response.message || '删除失败')
      }
    } catch (error) {
      console.error('删除测试用例失败:', error)
      ElMessage.error('删除失败')
    }
  })
}

// 导入测试用例
const handleImport = () => {
  ElMessage.info('导入功能开发中...')
}

// 导出测试用例
const handleExport = async () => {
  try {
    const response = await exportTestCases(searchForm)
    // 处理文件下载
    const blob = new Blob([response], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `test_cases_${dayjs().format('YYYY-MM-DD_HH-mm-ss')}.xlsx`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

// 选择变化
const handleSelectionChange = (selection) => {
  selectedCases.value = selection
}

// 批量执行
const handleBatchExecute = () => {
  if (selectedCases.value.length === 0) {
    ElMessage.warning('请选择要执行的测试用例')
    return
  }
  ElMessage.success(`正在批量执行 ${selectedCases.value.length} 个测试用例`)
}

// 批量删除
const handleBatchDelete = () => {
  if (selectedCases.value.length === 0) {
    ElMessage.warning('请选择要删除的测试用例')
    return
  }
  
  ElMessageBox.confirm(
    `确定要删除选中的 ${selectedCases.value.length} 个测试用例吗？此操作不可恢复。`,
    '确认批量删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const ids = selectedCases.value.map(item => item.id)
      const response = await batchDeleteTestCases(ids)
      if (response.success) {
        ElMessage.success('批量删除成功')
        fetchTestCaseList()
        fetchTestCaseStats()
      } else {
        ElMessage.error(response.message || '批量删除失败')
      }
    } catch (error) {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  })
}

// 提交表单
const handleSubmit = async () => {
  if (!testCaseFormRef.value) return
  
  try {
    await testCaseFormRef.value.validate()
    submitLoading.value = true
    
    let response
    if (isEdit.value) {
      response = await updateTestCase(testCaseForm.id, testCaseForm)
    } else {
      response = await createTestCase(testCaseForm)
    }
    
    if (response.success) {
      ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
      dialogVisible.value = false
      fetchTestCaseList()
      fetchTestCaseStats()
    } else {
      ElMessage.error(response.message || '操作失败')
    }
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('操作失败')
  } finally {
    submitLoading.value = false
  }
}

// 重置表单
const resetForm = () => {
  Object.assign(testCaseForm, {
    id: null,
    name: '',
    module: '',
    priority: 'medium',
    preconditions: '',
    steps: '',
    expected_result: '',
    remarks: ''
  })
  if (testCaseFormRef.value) {
    testCaseFormRef.value.resetFields()
  }
}

// 分页处理
const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  fetchTestCaseList()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  fetchTestCaseList()
}

// 工具函数
const getModuleLabel = (module) => {
  const moduleMap = {
    login: '登录模块',
    user: '用户管理',
    device: '设备管理',
    test: '测试管理'
  }
  return moduleMap[module] || module
}

const getModuleTagType = (module) => {
  const typeMap = {
    login: 'primary',
    user: 'success',
    device: 'warning',
    test: 'info'
  }
  return typeMap[module] || 'info'
}

const getPriorityLabel = (priority) => {
  const priorityMap = {
    high: '高',
    medium: '中',
    low: '低'
  }
  return priorityMap[priority] || priority
}

const getPriorityTagType = (priority) => {
  const typeMap = {
    high: 'danger',
    medium: 'warning',
    low: 'success'
  }
  return typeMap[priority] || 'info'
}

const getStatusLabel = (status) => {
  const statusMap = {
    passed: '通过',
    failed: '失败',
    pending: '待执行',
    not_applicable: '不适用'
  }
  return statusMap[status] || status
}

const getStatusTagType = (status) => {
  const typeMap = {
    passed: 'success',
    failed: 'danger',
    pending: 'warning',
    not_applicable: 'info'
  }
  return typeMap[status] || 'info'
}

const formatDateTime = (dateTime) => {
  return dateTime ? dayjs(dateTime).format('YYYY-MM-DD HH:mm:ss') : '-'
}

// 标签页点击处理
const handleTabClick = (tab) => {
  if (tab.paneName === 'reviews') {
    window.location.href = '/test-cases/case-reviews'
  }
}

// 页面加载
onMounted(() => {
  fetchTestCaseList()
  fetchTestCaseStats()
})
</script>

<style lang="scss" scoped>
.test-case-management {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
  
  .header-content {
    h1 {
      margin: 0 0 8px 0;
      font-size: 24px;
      font-weight: 600;
      color: #303133;
    }
    
    .description {
      margin: 0;
      color: #909399;
      font-size: 14px;
    }
  }
}

.header-tabs {
  margin-top: 16px;
}

.header-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  margin-bottom: 16px;
}

.stats-section {
  margin-bottom: 20px;
  
  .stat-card {
    display: flex;
    align-items: center;
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease;
    
    &:hover {
      transform: translateY(-2px);
    }
    
    .stat-icon {
      width: 50px;
      height: 50px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 15px;
      font-size: 24px;
      color: white;
      
      &.total {
        background: linear-gradient(135deg, #409eff, #66b1ff);
      }
      
      &.passed {
        background: linear-gradient(135deg, #67c23a, #85ce61);
      }
      
      &.failed {
        background: linear-gradient(135deg, #f56c6c, #f78989);
      }
      
      &.pending {
        background: linear-gradient(135deg, #e6a23c, #ebb563);
      }
    }
    
    .stat-content {
      .stat-number {
        font-size: 28px;
        font-weight: 600;
        color: #303133;
        line-height: 1;
      }
      
      .stat-label {
        font-size: 14px;
        color: #909399;
        margin-top: 5px;
      }
    }
  }
}

.search-section {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 10px;
  
  .el-form {
    margin: 0;
  }
}

.table-section {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  
  .batch-actions {
    padding: 15px 20px;
    background: #f5f7fa;
    border-top: 1px solid #e4e7ed;
    display: flex;
    align-items: center;
    gap: 10px;
    
    span {
      color: #606266;
      font-size: 14px;
    }
  }
  
  .pagination {
    padding: 20px;
    text-align: right;
    border-top: 1px solid #e4e7ed;
  }
}

.test-case-detail {
  .el-descriptions {
    margin: 0;
  }
  
  .steps-content {
    white-space: pre-line;
    line-height: 1.6;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

// 响应式设计
@media (max-width: 768px) {
  .test-case-management {
    padding: 10px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .stats-section {
    .el-col {
      margin-bottom: 10px;
    }
  }
  
  .search-section {
    padding: 15px;
    
    .el-form {
      .el-form-item {
        margin-bottom: 15px;
        margin-right: 0;
        width: 100%;
        
        .el-input,
        .el-select {
          width: 100%;
        }
      }
    }
  }
}
</style>