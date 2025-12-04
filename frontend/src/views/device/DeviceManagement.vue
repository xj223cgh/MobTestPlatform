<template>
  <div class="device-management">
    <div class="page-header">
      <div class="header-content">
        <h1>设备管理</h1>
        <p class="description">
          管理测试设备和设备状态
        </p>
      </div>
      <div class="header-actions">
        <el-button
          type="primary"
          @click="handleAdd"
        >
          <el-icon><Plus /></el-icon>
          添加设备
        </el-button>
        <el-button @click="handleRefresh">
          <el-icon><Refresh /></el-icon>
          刷新状态
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon online">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">
                {{ stats.online }}
              </div>
              <div class="stat-label">
                在线设备
              </div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon offline">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">
                {{ stats.offline }}
              </div>
              <div class="stat-label">
                离线设备
              </div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon busy">
              <el-icon><Loading /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">
                {{ stats.busy }}
              </div>
              <div class="stat-label">
                忙碌设备
              </div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon total">
              <el-icon><DataBoard /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">
                {{ stats.total }}
              </div>
              <div class="stat-label">
                设备总数
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-section">
      <el-form
        :model="searchForm"
        inline
      >
        <el-form-item label="设备名称">
          <el-input
            v-model="searchForm.name"
            placeholder="请输入设备名称"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="设备类型">
          <el-select
            v-model="searchForm.type"
            placeholder="请选择设备类型"
            clearable
            @clear="handleSearch"
            @change="handleSearch"
          >
            <el-option
              label="Android手机"
              value="android_phone"
            />
            <el-option
              label="iOS手机"
              value="ios_phone"
            />
            <el-option
              label="Android平板"
              value="android_tablet"
            />
            <el-option
              label="iOS平板"
              value="ios_tablet"
            />
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
            <el-option
              label="在线"
              value="online"
            />
            <el-option
              label="离线"
              value="offline"
            />
            <el-option
              label="忙碌"
              value="busy"
            />
            <el-option
              label="维护"
              value="maintenance"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            @click="handleSearch"
          >
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

    <!-- 设备表格 -->
    <div class="table-section">
      <el-table
        v-loading="loading"
        :data="deviceList"
        stripe
        border
        style="width: 100%"
      >
        <el-table-column
          prop="id"
          label="ID"
          width="80"
        />
        <el-table-column
          prop="name"
          label="设备名称"
          min-width="150"
        />
        <el-table-column
          prop="type"
          label="设备类型"
          width="120"
        >
          <template #default="{ row }">
            <el-tag :type="getDeviceTypeTagType(row.type)">
              {{ getDeviceTypeLabel(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="platform"
          label="平台"
          width="80"
        >
          <template #default="{ row }">
            <el-tag :type="row.platform === 'android' ? 'success' : 'primary'">
              {{ row.platform.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="os_version"
          label="系统版本"
          width="100"
        />
        <el-table-column
          prop="status"
          label="状态"
          width="100"
        >
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="ip_address"
          label="IP地址"
          width="130"
        />
        <el-table-column
          prop="last_seen"
          label="最后在线"
          width="160"
        >
          <template #default="{ row }">
            {{ formatDateTime(row.last_seen) }}
          </template>
        </el-table-column>
        <el-table-column
          label="操作"
          width="250"
          fixed="right"
        >
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
              :disabled="row.status !== 'online'"
              @click="handleConnect(row)"
            >
              连接
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

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          :current-page="pagination.page"
          :page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 设备表单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="deviceFormRef"
        :model="deviceForm"
        :rules="deviceRules"
        label-width="100px"
      >
        <el-form-item
          label="设备名称"
          prop="name"
        >
          <el-input
            v-model="deviceForm.name"
            placeholder="请输入设备名称"
          />
        </el-form-item>
        <el-form-item
          label="设备类型"
          prop="type"
        >
          <el-select
            v-model="deviceForm.type"
            placeholder="请选择设备类型"
          >
            <el-option
              label="Android手机"
              value="android_phone"
            />
            <el-option
              label="iOS手机"
              value="ios_phone"
            />
            <el-option
              label="Android平板"
              value="android_tablet"
            />
            <el-option
              label="iOS平板"
              value="ios_tablet"
            />
          </el-select>
        </el-form-item>
        <el-form-item
          label="平台"
          prop="platform"
        >
          <el-radio-group v-model="deviceForm.platform">
            <el-radio label="android">
              Android
            </el-radio>
            <el-radio label="ios">
              iOS
            </el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item
          label="系统版本"
          prop="os_version"
        >
          <el-input
            v-model="deviceForm.os_version"
            placeholder="请输入系统版本"
          />
        </el-form-item>
        <el-form-item
          label="IP地址"
          prop="ip_address"
        >
          <el-input
            v-model="deviceForm.ip_address"
            placeholder="请输入IP地址"
          />
        </el-form-item>
        <el-form-item
          label="端口"
          prop="port"
        >
          <el-input-number
            v-model="deviceForm.port"
            :min="1"
            :max="65535"
            placeholder="请输入端口号"
          />
        </el-form-item>
        <el-form-item
          label="描述"
          prop="description"
        >
          <el-input
            v-model="deviceForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入设备描述"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="submitLoading"
            @click="handleSubmit"
          >
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 设备详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="设备详情"
      width="800px"
    >
      <div
        v-if="currentDevice"
        class="device-detail"
      >
        <el-descriptions
          :column="2"
          border
        >
          <el-descriptions-item label="设备ID">
            {{ currentDevice.id }}
          </el-descriptions-item>
          <el-descriptions-item label="设备名称">
            {{ currentDevice.name }}
          </el-descriptions-item>
          <el-descriptions-item label="设备类型">
            <el-tag :type="getDeviceTypeTagType(currentDevice.type)">
              {{ getDeviceTypeLabel(currentDevice.type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="平台">
            <el-tag :type="currentDevice.platform === 'android' ? 'success' : 'primary'">
              {{ currentDevice.platform.toUpperCase() }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="系统版本">
            {{ currentDevice.os_version }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTagType(currentDevice.status)">
              {{ getStatusLabel(currentDevice.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="IP地址">
            {{ currentDevice.ip_address }}
          </el-descriptions-item>
          <el-descriptions-item label="端口">
            {{ currentDevice.port }}
          </el-descriptions-item>
          <el-descriptions-item label="最后在线">
            {{ formatDateTime(currentDevice.last_seen) }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(currentDevice.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item
            label="描述"
            :span="2"
          >
            {{ currentDevice.description || '-' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, Monitor, Loading, DataBoard } from '@element-plus/icons-vue'
import { getDeviceList, createDevice, updateDevice, deleteDevice, getDeviceStats } from '@/api/device'
import dayjs from 'dayjs'

// 响应式数据
const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const isEdit = ref(false)
const dialogTitle = ref('')
const deviceFormRef = ref()
const currentDevice = ref(null)

// 统计数据
const stats = reactive({
  online: 0,
  offline: 0,
  busy: 0,
  total: 0
})

// 搜索表单
const searchForm = reactive({
  name: '',
  type: '',
  status: ''
})

// 设备表单
const deviceForm = reactive({
  id: null,
  name: '',
  type: '',
  platform: 'android',
  os_version: '',
  ip_address: '',
  port: 5555,
  description: ''
})

// 表单验证规则
const deviceRules = {
  name: [
    { required: true, message: '请输入设备名称', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择设备类型', trigger: 'change' }
  ],
  platform: [
    { required: true, message: '请选择平台', trigger: 'change' }
  ],
  os_version: [
    { required: true, message: '请输入系统版本', trigger: 'blur' }
  ],
  ip_address: [
    { required: true, message: '请输入IP地址', trigger: 'blur' },
    { pattern: /^(\d{1,3}\.){3}\d{1,3}$/, message: '请输入正确的IP地址', trigger: 'blur' }
  ],
  port: [
    { required: true, message: '请输入端口号', trigger: 'blur' }
  ]
}

// 设备列表
const deviceList = ref([])

// 分页
const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

// 获取设备列表
const fetchDeviceList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      ...searchForm
    }
    const response = await getDeviceList(params)
    if (response.success) {
      deviceList.value = response.data.list
      pagination.total = response.data.total
    } else {
      ElMessage.error(response.message || '获取设备列表失败')
    }
  } catch (error) {
    console.error('获取设备列表失败:', error)
    ElMessage.error('获取设备列表失败')
  } finally {
    loading.value = false
  }
}

// 获取设备统计
const fetchDeviceStats = async () => {
  try {
    const response = await getDeviceStats()
    if (response.success) {
      Object.assign(stats, response.data)
    }
  } catch (error) {
    console.error('获取设备统计失败:', error)
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchDeviceList()
}

// 重置搜索
const handleReset = () => {
  Object.assign(searchForm, {
    name: '',
    type: '',
    status: ''
  })
  handleSearch()
}

// 刷新状态
const handleRefresh = () => {
  fetchDeviceList()
  fetchDeviceStats()
  ElMessage.success('状态已刷新')
}

// 新增设备
const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '添加设备'
  dialogVisible.value = true
  resetForm()
}

// 编辑设备
const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑设备'
  dialogVisible.value = true
  Object.assign(deviceForm, {
    id: row.id,
    name: row.name,
    type: row.type,
    platform: row.platform,
    os_version: row.os_version,
    ip_address: row.ip_address,
    port: row.port,
    description: row.description
  })
}

// 查看设备详情
const handleView = (row) => {
  currentDevice.value = row
  detailDialogVisible.value = true
}

// 连接设备
const handleConnect = (row) => {
  ElMessage.success(`正在连接设备: ${row.name}`)
  // 这里可以添加实际的连接逻辑
}

// 删除设备
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除设备 "${row.name}" 吗？此操作不可恢复。`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const response = await deleteDevice(row.id)
      if (response.success) {
        ElMessage.success('删除成功')
        fetchDeviceList()
        fetchDeviceStats()
      } else {
        ElMessage.error(response.message || '删除失败')
      }
    } catch (error) {
      console.error('删除设备失败:', error)
      ElMessage.error('删除失败')
    }
  })
}

// 提交表单
const handleSubmit = async () => {
  if (!deviceFormRef.value) return
  
  try {
    await deviceFormRef.value.validate()
    submitLoading.value = true
    
    let response
    if (isEdit.value) {
      response = await updateDevice(deviceForm.id, deviceForm)
    } else {
      response = await createDevice(deviceForm)
    }
    
    if (response.success) {
      ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
      dialogVisible.value = false
      fetchDeviceList()
      fetchDeviceStats()
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
  Object.assign(deviceForm, {
    id: null,
    name: '',
    type: '',
    platform: 'android',
    os_version: '',
    ip_address: '',
    port: 5555,
    description: ''
  })
  if (deviceFormRef.value) {
    deviceFormRef.value.resetFields()
  }
}

// 分页处理
const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  fetchDeviceList()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  fetchDeviceList()
}

// 工具函数
const getDeviceTypeLabel = (type) => {
  const typeMap = {
    android_phone: 'Android手机',
    ios_phone: 'iOS手机',
    android_tablet: 'Android平板',
    ios_tablet: 'iOS平板'
  }
  return typeMap[type] || type
}

const getDeviceTypeTagType = (type) => {
  const typeMap = {
    android_phone: 'success',
    ios_phone: 'primary',
    android_tablet: 'warning',
    ios_tablet: 'info'
  }
  return typeMap[type] || 'info'
}

const getStatusLabel = (status) => {
  const statusMap = {
    online: '在线',
    offline: '离线',
    busy: '忙碌',
    maintenance: '维护'
  }
  return statusMap[status] || status
}

const getStatusTagType = (status) => {
  const typeMap = {
    online: 'success',
    offline: 'danger',
    busy: 'warning',
    maintenance: 'info'
  }
  return typeMap[status] || 'info'
}

const formatDateTime = (dateTime) => {
  return dateTime ? dayjs(dateTime).format('YYYY-MM-DD HH:mm:ss') : '-'
}

// 页面加载
onMounted(() => {
  fetchDeviceList()
  fetchDeviceStats()
})
</script>

<style lang="scss" scoped>
.device-management {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
      
      &.online {
        background: linear-gradient(135deg, #67c23a, #85ce61);
      }
      
      &.offline {
        background: linear-gradient(135deg, #f56c6c, #f78989);
      }
      
      &.busy {
        background: linear-gradient(135deg, #e6a23c, #ebb563);
      }
      
      &.total {
        background: linear-gradient(135deg, #409eff, #66b1ff);
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
  
  .pagination {
    padding: 20px;
    text-align: right;
    border-top: 1px solid #e4e7ed;
  }
}

.device-detail {
  .el-descriptions {
    margin: 0;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

// 响应式设计
@media (max-width: 768px) {
  .device-management {
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