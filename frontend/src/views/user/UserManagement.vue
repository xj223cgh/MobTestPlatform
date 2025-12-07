<template>
  <div class="user-management">
    <div class="page-header">
      <div class="header-content">
        <h1>用户管理</h1>
        <p class="description">
          管理系统用户账号与权限
        </p>
      </div>
      <div class="header-actions">
        <el-button
          type="primary"
          @click="handleAdd"
        >
          <el-icon><Plus /></el-icon>
          新增用户
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-section">
      <el-form
        :model="searchForm"
        inline
      >
        <el-form-item label="用户名/姓名">
          <el-input
            v-model="searchForm.username"
            placeholder="请输入用户名/姓名"
            clearable
            style="width: 150px"
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input
            v-model="searchForm.phone"
            placeholder="请输入手机号"
            clearable
            style="width: 150px"
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="角色">
          <el-select
            v-model="searchForm.role"
            placeholder="全部角色"
            clearable
            style="width: 120px"
            @clear="handleSearch"
          >
            <el-option
              label="超级管理员"
              value="super"
            />
            <el-option
              label="管理员"
              value="manager"
            />
            <el-option
              label="测试人员"
              value="tester"
            />
            <el-option
              label="实习生"
              value="admin"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="用户状态">
          <el-select
            v-model="searchForm.status"
            placeholder="全部状态"
            clearable
            style="width: 120px"
            @clear="handleSearch"
          >
            <el-option
              label="启用"
              value="true"
            />
            <el-option
              label="禁用"
              value="false"
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

    <!-- 用户表格 -->
    <div class="table-section">
      <el-table
        v-loading="loading"
        :data="userList"
        stripe
        border
        style="width: 100%"
        fit
      >
        <el-table-column
          prop="id"
          label="ID"
          min-width="60"
          align="center"
        >
          <template #default="{ row }">
            {{ row.id || '-' }}
          </template>
        </el-table-column>
        <el-table-column
          prop="username"
          label="用户名"
          min-width="110"
          align="center"
        >
          <template #default="{ row }">
            {{ row.username || '-' }}
          </template>
        </el-table-column>
        <el-table-column
          prop="real_name"
          label="真实姓名"
          min-width="100"
          align="center"
        >
          <template #default="{ row }">
            {{ row.real_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column
          prop="phone"
          label="手机号"
          min-width="130"
          align="center"
        >
          <template #default="{ row }">
            {{ row.phone || '-' }}
          </template>
        </el-table-column>
        <el-table-column
          prop="department"
          label="部门"
          min-width="110"
          align="center"
        >
          <template #default="{ row }">
            {{ row.department || '-' }}
          </template>
        </el-table-column>
        <el-table-column
          prop="role"
          label="角色"
          min-width="90"
          align="center"
        >
          <template #default="{ row }">
            <template v-if="row.role">
              <el-tag :type="getRoleTagType(row.role)">
                {{ getRoleLabel(row.role) }}
              </el-tag>
            </template>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column
          prop="is_active"
          label="状态"
          min-width="70"
          align="center"
        >
          <template #default="{ row }">
            <template v-if="row.is_active !== undefined">
              <el-tag :type="row.is_active ? 'success' : 'danger'">
                {{ row.is_active ? '启用' : '禁用' }}
              </el-tag>
            </template>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column
          prop="created_at"
          label="创建时间"
          min-width="140"
          align="center"
        >
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column
          label="操作"
          min-width="180"
          fixed="right"
          align="center"
        >
          <template #default="{ row }">
            <div class="operation-buttons">
              <el-button
                type="primary"
                size="small"
                @click="handleEdit(row)"
              >
                编辑
              </el-button>
              <el-button
                :type="row.is_active ? 'warning' : 'success'"
                size="small"
                @click="handleToggleStatus(row)"
              >
                {{ row.is_active ? '禁用' : '启用' }}
              </el-button>
              <el-button
                type="danger"
                size="small"
                @click="handleDelete(row)"
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
        :current-page="pagination.page"
        :page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 用户表单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="userFormRef"
        :model="userForm"
        :rules="userRules"
        label-width="80px"
      >
        <el-form-item
          label="用户名"
          prop="username"
        >
          <el-input
            v-model="userForm.username"
            placeholder="请输入用户名"
            :disabled="isEdit"
          />
        </el-form-item>
        <el-form-item
          label="真实姓名"
          prop="real_name"
        >
          <el-input
            v-model="userForm.real_name"
            placeholder="请输入真实姓名"
          />
        </el-form-item>
        <el-form-item
          label="手机号"
          prop="phone"
        >
          <el-input
            v-model="userForm.phone"
            placeholder="请输入手机号"
          />
        </el-form-item>
        <el-form-item
          v-if="!isEdit"
          label="密码"
          prop="password"
        >
          <el-input
            v-model="userForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        <el-form-item
          label="角色"
          prop="role"
        >
          <el-select
            v-model="userForm.role"
            placeholder="请选择角色"
            style="width: 100%"
          >
            <el-option
              label="超级管理员"
              value="super"
            />
            <el-option
              label="管理员"
              value="manager"
            />
            <el-option
              label="测试人员"
              value="tester"
            />
            <el-option
              label="实习生"
              value="admin"
            />
          </el-select>
        </el-form-item>
        <el-form-item
          label="性别"
          prop="gender"
        >
          <el-select
            v-model="userForm.gender"
            placeholder="请选择性别"
            style="width: 100%"
          >
            <el-option
              label="男"
              value="male"
            />
            <el-option
              label="女"
              value="female"
            />
            <el-option
              label="其他"
              value="other"
            />
          </el-select>
        </el-form-item>
        <el-form-item
          label="部门"
          prop="department"
        >
          <el-input
            v-model="userForm.department"
            placeholder="请输入所属部门"
            clearable
          />
        </el-form-item>
        <el-form-item
          label="状态"
          prop="is_active"
        >
          <el-radio-group v-model="userForm.is_active">
            <el-radio :label="true">
              启用
            </el-radio>
            <el-radio :label="false">
              禁用
            </el-radio>
          </el-radio-group>
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh } from '@element-plus/icons-vue'
import { getUserList, createUser, updateUser, deleteUser, toggleUserStatus } from '@/api/user'
import dayjs from 'dayjs'

// 响应式数据
const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const dialogTitle = ref('')
const userFormRef = ref()

// 搜索表单
const searchForm = reactive({
  username: '',
  phone: '',
  role: '',
  status: ''
})

// 用户表单
const userForm = reactive({
  id: null,
  username: '',
  real_name: '',
  phone: '',
  password: '',
  role: '',
  is_active: true,
  gender: 'other',
  department: ''
})

// 表单验证规则
const userRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  real_name: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  is_active: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ],
  gender: [
    { required: true, message: '请选择性别', trigger: 'change' }
  ],
  department: [
    { max: 100, message: '部门名称不能超过100个字符', trigger: 'blur' }
  ]
}

// 用户列表
const userList = ref([])

// 分页
const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

// 获取用户列表
const fetchUserList = async () => {
  try {
    loading.value = true
    // 构建请求参数，处理各筛选条件
    const params = {
      page: pagination.page,
      size: pagination.size
    }
    
    // 构建搜索参数 - 后端API使用统一的search参数
    // 只有当username或phone有值时才添加search参数
    let searchValue = ''
    if (searchForm.username) {
      searchValue = searchForm.username
    } else if (searchForm.phone) {
      searchValue = searchForm.phone
    }
    
    // 只有当searchValue有值时才添加到请求参数中
    if (searchValue) {
      params.search = searchValue
    }
    
    // 只有当role有值时才添加role参数
    if (searchForm.role) {
      params.role = searchForm.role
    }
    
    // 只有当status有明确值（'true'或'false'）时才添加is_active参数
    // 当status被清除（空字符串）时，不添加该参数，实现数据重置
    if (searchForm.status === 'true' || searchForm.status === 'false') {
      params.is_active = searchForm.status === 'true'
    }
    
    console.log('API请求参数:', params)
    const response = await getUserList(params)
    // 使用后端实际返回的数据结构
    userList.value = response.data.users || []
    pagination.total = response.data.pagination.total || 0
  } catch (error) {
    ElMessage.error('获取用户列表失败')
    console.error('获取用户列表错误:', error)
  } finally {
    loading.value = false
  }
}

// 搜索 - 点击搜索按钮时才会应用所有筛选条件
const handleSearch = () => {
  // 重置页码为1，确保从第一页开始显示筛选结果
  pagination.page = 1
  
  // 调用fetchUserList函数，该函数内部会根据各筛选条件的值来决定是否添加对应的筛选参数
  fetchUserList()
}

// 重置搜索
const handleReset = () => {
  Object.assign(searchForm, {
    username: '',
    phone: '',
    role: '',
    status: ''
  })
  handleSearch()
}

// 新增用户
const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增用户'
  dialogVisible.value = true
  resetForm()
}

// 编辑用户
const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑用户'
  dialogVisible.value = true
  Object.assign(userForm, {
      id: row.id,
      username: row.username,
      real_name: row.real_name,
      phone: row.phone,
      password: '',
      role: row.role,
      is_active: row.is_active,
      gender: row.gender || 'other',
      department: row.department || ''
    })
}

// 删除用户
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除用户 "${row.username}" 吗？此操作不可恢复。`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const response = await deleteUser(row.id)
      if (response.success) {
        ElMessage.success('删除成功')
        fetchUserList()
      } else {
        ElMessage.error(response.message || '删除失败')
      }
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

// 切换用户状态
const handleToggleStatus = (row) => {
  const action = row.is_active ? '禁用' : '启用'
  ElMessageBox.confirm(
    `确定要${action}用户 "${row.username}" 吗？`,
    `确认${action}`,
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const response = await toggleUserStatus(row.id)
      // 直接使用响应，不再检查response.success
      ElMessage.success(`${action}成功`)
      fetchUserList()
    } catch (error) {
      ElMessage.error(`${action}失败`)
    }
  })
}

// 提交表单
const handleSubmit = async () => {
  if (!userFormRef.value) return;
  const isValid = await userFormRef.value.validate();
  if (!isValid) return;
  submitLoading.value = true;
  try {
    // 构建提交数据
    const submitData = {
      username: userForm.username,
      real_name: userForm.real_name,
      phone: userForm.phone,
      role: userForm.role,
      is_active: userForm.is_active,
      gender: userForm.gender,
      department: userForm.department
    };
    
    // 如果是新增用户且有密码，则添加密码
    if (!isEdit.value && userForm.password) {
      submitData.password = userForm.password;
    }
    
    let response;
    if (isEdit.value) {
      response = await updateUser(userForm.id, submitData);
    } else {
      response = await createUser(submitData);
    }
    
    if (response.success) {
      ElMessage.success(isEdit.value ? '编辑成功' : '创建成功');
      dialogVisible.value = false;
      fetchUserList();
    } else {
      ElMessage.error(response.message || (isEdit.value ? '编辑失败' : '创建失败'));
    }
  } catch (error) {
    ElMessage.error('操作失败');
  } finally {
    submitLoading.value = false;
  }
}

// 重置表单
const resetForm = () => {
  Object.assign(userForm, {
    id: null,
    username: '',
    real_name: '',
    phone: '',
    password: '',
    role: '',
    is_active: true,
    gender: 'other',
    department: ''
  })
  if (userFormRef.value) {
    userFormRef.value.resetFields()
  }
}

// 分页处理
const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  fetchUserList()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  fetchUserList()
}

// 工具函数
// 获取角色标签
const getRoleLabel = (role) => {
  const roleMap = {
    'super': '超级管理员',
    'admin': '实习生', 
    'manager': '管理员',
    'tester': '测试人员'
  }
  return roleMap[role] || role
}

// 获取性别标签
const getGenderLabel = (gender) => {
  const genderMap = {
    'male': '男',
    'female': '女',
    'other': '其他'
  }
  return genderMap[gender] || '其他'
}

// 获取角色标签类型
const getRoleTagType = (role) => {
  const typeMap = {
    'super': 'danger',
    'admin': 'info',
    'manager': 'warning', 
    'tester': 'success'
  }
  return typeMap[role] || 'info'
}

const formatDateTime = (dateTime) => {
  return dateTime ? dayjs(dateTime).format('YYYY-MM-DD HH:mm:ss') : '-' 
}

// 页面加载
onMounted(() => {
  fetchUserList()
})
</script>

<style lang="scss" scoped>
.user-management {
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