<template>
  <div class="user-management">
    <div class="page-header">
      <div class="header-content">
        <h1 class="header-title">用户管理</h1>
        <span class="header-description">管理系统用户账号与权限</span>
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
        class="search-form"
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
              label="普通成员"
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
        <el-form-item class="search-buttons">
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
      <div class="table-scroll-viewport">
        <el-table
          ref="userTableRef"
          v-loading="loading"
          :data="userList"
          stripe
          border
          style="width: 100%"
          fit
          :row-class-name="getRowClassName"
          row-key="id"
        >
        <el-table-column
          prop="id"
          label="ID"
          min-width="60"
          align="center"
        >
          <template #default="{ row }">
            {{ row.id || "-" }}
          </template>
        </el-table-column>
        <el-table-column
          prop="username"
          label="用户名"
          min-width="110"
          align="center"
        >
          <template #default="{ row }">
            {{ row.username || "-" }}
          </template>
        </el-table-column>
        <el-table-column
          prop="real_name"
          label="真实姓名"
          min-width="100"
          align="center"
        >
          <template #default="{ row }">
            {{ row.real_name || "-" }}
          </template>
        </el-table-column>
        <el-table-column
          prop="phone"
          label="手机号"
          min-width="130"
          align="center"
        >
          <template #default="{ row }">
            {{ row.phone || "-" }}
          </template>
        </el-table-column>
        <el-table-column
          prop="department"
          label="部门"
          min-width="110"
          align="center"
        >
          <template #default="{ row }">
            {{ row.department || "-" }}
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
                {{ row.is_active ? "启用" : "禁用" }}
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
          width="150"
          fixed="right"
          align="center"
        >
          <template #default="{ row }">
            <div class="operation-buttons">
              <el-button
                type="primary"
                size="small"
                class="op-btn"
                @click="handleEdit(row)"
              >
                编辑
              </el-button>
              <el-tooltip v-if="row.username === 'Lethe'" content="超级管理员账号不可禁用" placement="top">
                <span>
                  <el-button
                    :type="row.is_active ? 'warning' : 'success'"
                    size="small"
                    class="op-btn"
                    disabled
                  >
                    {{ row.is_active ? "禁用" : "启用" }}
                  </el-button>
                </span>
              </el-tooltip>
              <el-button
                v-else
                :type="row.is_active ? 'warning' : 'success'"
                size="small"
                class="op-btn"
                @click="handleToggleStatus(row)"
              >
                {{ row.is_active ? "禁用" : "启用" }}
              </el-button>
              <el-tooltip v-if="row.username === 'Lethe'" content="超级管理员账号不可删除" placement="top">
                <span>
                  <el-button type="danger" size="small" class="op-btn" disabled>删除</el-button>
                </span>
              </el-tooltip>
              <el-button
                v-else
                type="danger"
                size="small"
                class="op-btn"
                @click="handleDelete(row)"
              >
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      </div>
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
            :disabled="isEdit && userForm.username === 'Lethe'"
          >
            <el-option
              v-if="userForm.username === 'Lethe'"
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
              label="普通成员"
              value="admin"
            />
          </el-select>
          <div v-if="isEdit && userForm.username === 'Lethe'" class="form-item-tip">超级管理员账号角色固定，不可修改</div>
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
import { ref, reactive, onMounted, computed, watch, nextTick } from "vue";
import { useRoute } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { Plus, Search, Refresh } from "@element-plus/icons-vue";
import {
  getUserList,
  createUser,
  updateUser,
  deleteUser,
  toggleUserStatus,
} from "@/api/user";
import dayjs from "dayjs";
import { isPermissionError } from "@/utils/request";
import { useUserStore } from "@/stores/user";

// 响应式数据
const loading = ref(false);
const submitLoading = ref(false);
const dialogVisible = ref(false);
const isEdit = ref(false);
const dialogTitle = ref("");
const userFormRef = ref();

// 路由：从用例集信息（创建人）跳转时高亮指定行
const route = useRoute();
const highlightId = computed(() => {
  const id = route.query?.user_id;
  return id ? Number(id) : null;
});
const getRowClassName = ({ row }) => {
  if (highlightId.value && row.id === highlightId.value) return "highlight-row";
  return "";
};

// 用户store
const userStore = useUserStore();

// 计算属性：当前登录用户ID
const currentUserId = computed(() => userStore.userInfo?.id);

// 搜索表单
const searchForm = reactive({
  username: "",
  phone: "",
  role: "",
  status: "",
});

// 用户表单
const userForm = reactive({
  id: null,
  username: "",
  real_name: "",
  phone: "",
  password: "",
  role: "",
  is_active: true,
  gender: "other",
  department: "",
});

// 表单验证规则
const userRules = {
  username: [
    { required: true, message: "请输入用户名", trigger: "blur" },
    {
      min: 3,
      max: 20,
      message: "用户名长度在 3 到 20 个字符",
      trigger: "blur",
    },
  ],
  real_name: [{ required: true, message: "请输入真实姓名", trigger: "blur" }],
  phone: [
    { required: true, message: "请输入手机号", trigger: "blur" },
    {
      pattern: /^1[3-9]\d{9}$/,
      message: "请输入正确的手机号",
      trigger: "blur",
    },
  ],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 6, message: "密码长度不能少于6位", trigger: "blur" },
  ],
  role: [{ required: true, message: "请选择角色", trigger: "change" }],
  is_active: [{ required: true, message: "请选择状态", trigger: "change" }],
  gender: [{ required: true, message: "请选择性别", trigger: "change" }],
  department: [
    { max: 100, message: "部门名称不能超过100个字符", trigger: "blur" },
  ],
};

// 用户列表
const userList = ref([]);
const userTableRef = ref(null);

// 分页
const pagination = reactive({
  page: 1,
  size: 10,
  total: 0,
});

// 获取用户列表
const fetchUserList = async () => {
  try {
    loading.value = true;
    const needHighlight = highlightId.value != null;
    const params = {
      page: needHighlight ? 1 : pagination.page,
      size: needHighlight ? 10000 : pagination.size,
    };

    let searchValue = "";
    if (searchForm.username) searchValue = searchForm.username;
    else if (searchForm.phone) searchValue = searchForm.phone;
    if (searchValue) params.search = searchValue;
    if (searchForm.role) params.role = searchForm.role;
    if (searchForm.status === "true" || searchForm.status === "false") {
      params.is_active = searchForm.status === "true";
    }

    const response = await getUserList(params);
    let items = response.data.users || [];
    const total = response.data.pagination?.total ?? 0;

    if (needHighlight && items.length > 0) {
      const idx = items.findIndex((u) => u.id === highlightId.value);
      if (idx >= 0) {
        const pageSize = pagination.size;
        pagination.page = Math.floor(idx / pageSize) + 1;
        const start = (pagination.page - 1) * pageSize;
        userList.value = items.slice(start, start + pageSize);
      } else {
        userList.value = items.slice(0, pagination.size);
        pagination.page = 1;
      }
      pagination.total = total;
    } else {
      userList.value = items;
      pagination.total = total;
    }
  } catch (error) {
    if (isPermissionError(error)) return;
    ElMessage.error("获取用户列表失败");
    console.error("获取用户列表错误:", error);
  } finally {
    loading.value = false;
  }
};

// 搜索 - 点击搜索按钮时才会应用所有筛选条件
const handleSearch = () => {
  // 重置页码为1，确保从第一页开始显示筛选结果
  pagination.page = 1;

  // 调用fetchUserList函数，该函数内部会根据各筛选条件的值来决定是否添加对应的筛选参数
  fetchUserList();
};

// 重置搜索
const handleReset = () => {
  Object.assign(searchForm, {
    username: "",
    phone: "",
    role: "",
    status: "",
  });
  handleSearch();
};

// 新增用户
const handleAdd = () => {
  isEdit.value = false;
  dialogTitle.value = "新增用户";
  dialogVisible.value = true;
  resetForm();
};

// 编辑用户
const handleEdit = (row) => {
  isEdit.value = true;
  dialogTitle.value = "编辑用户";
  dialogVisible.value = true;
  Object.assign(userForm, {
    id: row.id,
    username: row.username,
    real_name: row.real_name,
    phone: row.phone,
    password: "",
    role: row.role,
    is_active: row.is_active,
    gender: row.gender || "other",
    department: row.department || "",
  });
};

// 删除用户
const handleDelete = (row) => {
  // 防止用户删除自己的账户
  if (row.id === currentUserId.value) {
    ElMessage.warning("无法删除自己的账户");
    return;
  }
  
  ElMessageBox.confirm(
    `确定要删除用户 "${row.username}" 吗？此操作不可恢复。`,
    "确认删除",
    {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    },
  ).then(async () => {
    try {
      const response = await deleteUser(row.id);
      if (response.success) {
        ElMessage.success("删除成功");
        fetchUserList();
      } else {
        // 有后端返回的提示时不再重复「删除失败」
        if (!response.message) {
          ElMessage.error("删除失败");
        }
      }
    } catch (error) {
      if (isPermissionError(error)) return;
      // 校验类（如 400 关联引用）已由拦截器提示，不再重复「删除失败」
      if (!error.response?.data?.message) {
        ElMessage.error("删除失败");
      }
    }
  });
};

// 切换用户状态
const handleToggleStatus = (row) => {
  // 防止用户禁用/启用自己的账户
  if (row.id === currentUserId.value) {
    ElMessage.warning("无法操作自己的账户状态");
    return;
  }
  
  const action = row.is_active ? "禁用" : "启用";
  ElMessageBox.confirm(
    `确定要${action}用户 "${row.username}" 吗？`,
    `确认${action}`,
    {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    },
  ).then(async () => {
    try {
      const response = await toggleUserStatus(row.id);
      // 直接使用响应，不再检查response.success
      ElMessage.success(`${action}成功`);
      fetchUserList();
    } catch (error) {
      if (isPermissionError(error)) return;
      if (!error?.response?.data?.message) {
        ElMessage.error(`${action}失败`);
      }
    }
  });
};

// 提交表单
const handleSubmit = async () => {
  if (!userFormRef.value) return;
  const isValid = await userFormRef.value.validate();
  if (!isValid) return;
  
  // 防止用户修改自己的账户状态
  if (isEdit.value && userForm.id === currentUserId.value) {
    // 如果用户试图修改自己的状态，强制保持启用
    userForm.is_active = true;
  }
  
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
      department: userForm.department,
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
      ElMessage.success(isEdit.value ? "编辑成功" : "创建成功");
      dialogVisible.value = false;
      fetchUserList();
    } else {
      ElMessage.error(
        response.message || (isEdit.value ? "编辑失败" : "创建失败"),
      );
    }
  } catch (error) {
    if (isPermissionError(error)) return;
    // 校验类错误（如手机号重复、真实姓名为空等）已由请求拦截器统一提示，此处不再重复
    const hasShown = error?.response?.data?.message || (error?.response?.data?.errors && Object.keys(error.response.data.errors).length > 0);
    if (!hasShown) {
      ElMessage.error("操作失败");
    }
  } finally {
    submitLoading.value = false;
  }
};

// 重置表单
const resetForm = () => {
  Object.assign(userForm, {
    id: null,
    username: "",
    real_name: "",
    phone: "",
    password: "",
    role: "",
    is_active: true,
    gender: "other",
    department: "",
  });
  if (userFormRef.value) {
    userFormRef.value.resetFields();
  }
};

// 分页处理
const handleSizeChange = (size) => {
  pagination.size = size;
  pagination.page = 1;
  fetchUserList();
};

const handleCurrentChange = (page) => {
  pagination.page = page;
  fetchUserList();
};

// 工具函数
// 获取角色标签
const getRoleLabel = (role) => {
  const roleMap = {
    super: "超级管理员",
    admin: "普通成员",
    manager: "管理员",
    tester: "测试人员",
  };
  return roleMap[role] || role;
};

// 获取性别标签
const getGenderLabel = (gender) => {
  const genderMap = {
    male: "男",
    female: "女",
    other: "其他",
  };
  return genderMap[gender] || "其他";
};

// 获取角色标签类型
const getRoleTagType = (role) => {
  const typeMap = {
    super: "danger",
    admin: "info",
    manager: "warning",
    tester: "success",
  };
  return typeMap[role] || "info";
};

const formatDateTime = (dateTime) => {
  return dateTime ? dayjs(dateTime).format("YYYY-MM-DD HH:mm:ss") : "-";
};

// 高亮行滚动到视口（仅当通过 user_id 跳转时）
const scrollToHighlightRow = () => {
  if (!highlightId.value || !userList.value.length) return;
  nextTick(() => {
    setTimeout(() => {
      const table = userTableRef.value?.$el;
      if (!table) return;
      const row = table.querySelector("tr.highlight-row");
      if (row) row.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }, 150);
  });
};

// 仅 Lethe 可拥有超级管理员：用户名非 Lethe 时若当前选了 super 则重置为 admin
watch(
  () => userForm.username,
  (name) => {
    if (name !== "Lethe" && userForm.role === "super") {
      userForm.role = "admin";
    }
  }
);

watch(
  () => [userList.value.length, highlightId.value],
  () => scrollToHighlightRow(),
  { flush: "post" }
);

// 页面加载
onMounted(() => {
  fetchUserList();
});
</script>

<style lang="scss" scoped>
.user-management {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: var(--el-bg-color-page, #f5f7fa);
}

.page-header {
  flex-shrink: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  background: var(--el-bg-color, white);
  padding: 16px 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--el-border-color-lighter, transparent);

  .header-content {
    display: flex;
    align-items: baseline;
    gap: 12px;
  }

  .header-title {
    margin: 0;
    font-size: 24px;
    font-weight: 500;
    color: var(--el-text-color-primary, #303133);
  }

  .header-description {
    color: var(--el-text-color-regular, #606266);
    font-size: 14px;
  }
}

.search-section {
  flex-shrink: 0;
  background: var(--el-bg-color, white);
  padding: 16px 20px;
  border-radius: 8px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--el-border-color-lighter, transparent);
}

/* 去掉表单项默认下边距，使搜索区域上下空白与 padding 一致 */
.search-section :deep(.el-form) {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px 16px;
  margin-bottom: 0;
}

.search-section :deep(.el-form-item) {
  margin-bottom: 0;
  margin-right: 0;
}

.search-section :deep(.search-buttons) {
  margin-left: auto;
}

.table-section {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: var(--el-bg-color, white);
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 70px; /* 为固定的分页组件留出空间 */
  border: 1px solid var(--el-border-color-lighter, transparent);
}

/* 用户列表固定在一屏内，仅表格区域垂直滚动 */
.table-section .table-scroll-viewport {
  flex: 1;
  min-height: 0;
  overflow-x: hidden;
  overflow-y: auto;
}

.table-section .table-scroll-viewport :deep(.el-table__body-wrapper) {
  overflow-x: hidden !important;
}

/* 从用例集信息（创建人）跳转时的选中行高亮（直接显示，无边框） */
.table-section :deep(tr.highlight-row > td) {
  background-color: var(--el-color-primary-light-9, #ecf5ff) !important;
}
.table-section :deep(tr.highlight-row:hover > td) {
  background-color: var(--el-color-primary-light-8, #d9ecff) !important;
}

/* 固定分页组件样式 */
.fixed-pagination {
  position: fixed;
  bottom: 0;
  right: 0;
  z-index: 100;
  background: var(--el-bg-color, white);
  padding: 15px 20px;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: center;
  align-items: center;
  border-top: 1px solid var(--el-border-color-light, #e4e7ed);
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

.form-item-tip {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

/* 操作列：与需求管理页面一致，紧凑按钮样式 */
.operation-buttons {
  display: flex;
  gap: 4px;
  justify-content: center;
  align-items: center;
  flex-wrap: nowrap;
  padding: 2px 0;
}

.operation-buttons :deep(.el-button.op-btn),
.operation-buttons :deep(.el-button) {
  flex: none;
  min-width: 0;
  padding: 2px 6px;
  font-size: 12px;
  margin: 0;
  white-space: nowrap;
}
</style>
