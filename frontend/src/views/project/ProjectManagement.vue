<template>
  <div class="project-management">
    <div class="page-header">
      <div class="header-content">
        <h1>项目管理</h1>
        <p class="description">管理系统项目信息</p>
      </div>
      <div class="header-actions">
        <el-button
          type="primary"
          :loading="loading"
          @click="handleCreateProject"
        >
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
            style="width: 200px"
            @clear="getProjectList"
            @keyup.enter="getProjectList"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="statusFilter"
            placeholder="全部状态"
            clearable
            style="width: 120px"
            @clear="getProjectList"
          >
            <el-option label="全部" value="" />
            <el-option label="未开始" value="not_started" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="已暂停" value="paused" />
            <el-option label="已完成" value="completed" />
            <el-option label="已关闭" value="closed" />
          </el-select>
        </el-form-item>

        <el-form-item label="优先级">
          <el-select
            v-model="priorityFilter"
            placeholder="全部优先级"
            clearable
            style="width: 120px"
            @clear="getProjectList"
          >
            <el-option label="全部" value="" />
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="getProjectList">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button :loading="loading" @click="resetFilters">
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
        <el-table-column
          prop="id"
          label="项目ID"
          type="index"
          width="100"
          fixed="left"
          align="center"
        />
        <el-table-column
          prop="project_name"
          label="项目名称"
          min-width="150"
          fixed="left"
          align="center"
        >
          <template #default="scope">
            {{ scope.row.project_name || "-" }}
          </template>
        </el-table-column>
        <el-table-column
          prop="status"
          label="状态"
          min-width="80"
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
          min-width="80"
          align="center"
        >
          <template #default="scope">
            <el-tag :type="getPriorityType(scope.row.priority)">
              {{ getPriorityText(scope.row.priority) || "-" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="creator_name"
          label="项目成员"
          min-width="140"
          align="center"
        >
          <template #default="scope">
            <div class="creator-select-wrapper">
              <!-- 使用临时变量存储当前显示的值，避免修改原始数据 -->
              <el-select
                v-model="scope.row._displayUserId"
                placeholder="项目成员"
                size="small"
                style="width: 90%"
                @change="handleCreatorChange(scope.row)"
              >
                <!-- 先显示创建者选项 -->
                <el-option
                  v-if="scope.row.creator_id && scope.row.creator_name"
                  :key="scope.row.creator_id"
                  :label="scope.row.creator_name + '（创建人）'"
                  :value="scope.row.creator_id"
                />

                <!-- 遍历项目成员，过滤掉创建者（已经单独显示） -->
                <el-option
                  v-for="member in (scope.row.members || []).filter(
                    (member) => member.user_id !== scope.row.creator_id,
                  )"
                  :key="member.user_id"
                  :label="member.user_name"
                  :value="member.user_id"
                />
              </el-select>
            </div>
          </template>
        </el-table-column>
        <el-table-column
          prop="owner_name"
          label="负责人"
          min-width="100"
          align="center"
        >
          <template #default="scope">
            {{ scope.row.owner_name || "-" }}
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
        <el-table-column
          label="操作"
          min-width="190"
          fixed="right"
          align="center"
        >
          <template #default="scope">
            <div class="operation-buttons">
              <el-button
                type="primary"
                size="small"
                @click="handleViewProject(scope.row)"
              >
                查看
              </el-button>
              <el-button
                type="success"
                size="small"
                @click="handleEditProject(scope.row)"
              >
                编辑
              </el-button>
              <el-button
                type="danger"
                size="small"
                :disabled="scope.row.is_owner"
                @click="handleDeleteProject(scope.row)"
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

    <!-- 创建/编辑项目对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="projectFormRef"
        :model="projectForm"
        :rules="projectRules"
        label-width="100px"
      >
        <el-form-item label="项目名称" prop="project_name">
          <el-input
            v-model="projectForm.project_name"
            placeholder="请输入项目名称"
          />
        </el-form-item>
        <el-form-item label="项目描述" prop="description" required>
          <el-input
            v-model="projectForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入项目描述"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="projectForm.status" placeholder="请选择项目状态">
            <el-option label="未开始" value="not_started" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="已暂停" value="paused" />
            <el-option label="已完成" value="completed" />
            <el-option label="已关闭" value="closed" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-select
            v-model="projectForm.priority"
            placeholder="请选择项目优先级"
          >
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item label="项目负责人" prop="owner_id" required>
          <el-select
            v-model="projectForm.owner_id"
            placeholder="请选择项目负责人"
            style="width: 100%"
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
            style="width: 100%"
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
          <div style="margin-top: 5px; font-size: 12px; color: #909399">
            <span>注意：当前项目负责人无法从成员列表中删除</span>
          </div>
        </el-form-item>
        <el-form-item label="开始日期" prop="start_date" required>
          <el-date-picker
            v-model="projectForm.start_date"
            type="datetime"
            placeholder="请选择开始日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="结束日期" prop="end_date" required>
          <el-date-picker
            v-model="projectForm.end_date"
            type="datetime"
            placeholder="请选择结束日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="项目文档链接" prop="doc_url">
          <el-input
            v-model="projectForm.doc_url"
            placeholder="请输入项目文档链接"
          />
        </el-form-item>
        <el-form-item label="流水线链接" prop="pipeline_url">
          <el-input
            v-model="projectForm.pipeline_url"
            placeholder="请输入流水线链接"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false"> 取消 </el-button>
        <el-button
          type="primary"
          :loading="dialogLoading"
          @click="handleSaveProject"
        >
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 删除项目确认对话框 -->
    <el-dialog v-model="deleteDialogVisible" title="删除项目" width="400px">
      <p>确定要删除项目 "{{ deleteProjectName }}" 吗？此操作不可撤销！</p>
      <template #footer>
        <el-button @click="deleteDialogVisible = false"> 取消 </el-button>
        <el-button
          type="danger"
          :loading="dialogLoading"
          @click="handleConfirmDelete"
        >
          删除
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from "vue";
import { ElMessage } from "element-plus";
import { Plus, Search, Refresh } from "@element-plus/icons-vue";
import {
  getProjects,
  createProject,
  updateProject,
  deleteProject,
} from "@/api/project";
import { getUserList } from "@/api/user";
import { useRouter } from "vue-router";
import { useUserStore } from "@/stores/user";
import dayjs from "dayjs";

// 响应式数据
const loading = ref(false);
const projectList = ref([]);

// 路由实例
const router = useRouter();

// 搜索和筛选
const searchQuery = ref("");
const statusFilter = ref("");
const priorityFilter = ref("");

// 搜索表单
const searchForm = reactive({});

// 分页
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0,
});

// 时间格式化函数
const formatDateTime = (dateTime) => {
  return dateTime ? dayjs(dateTime).format("YYYY-MM-DD HH:mm:ss") : "-";
};

// 状态类型映射
const getStatusType = (status) => {
  const statusMap = {
    not_started: "info",
    in_progress: "success",
    paused: "warning",
    completed: "success",
    closed: "danger",
  };
  return statusMap[status] || "info";
};

// 状态文本映射
const getStatusText = (status) => {
  const statusMap = {
    not_started: "未开始",
    in_progress: "进行中",
    paused: "已暂停",
    completed: "已完成",
    closed: "已关闭",
  };
  return statusMap[status] || status || "-";
};

// 优先级类型映射
const getPriorityType = (priority) => {
  const priorityMap = {
    high: "danger",
    medium: "warning",
    low: "success",
  };
  return priorityMap[priority] || "info";
};

// 优先级文本映射
const getPriorityText = (priority) => {
  const priorityMap = {
    high: "高",
    medium: "中",
    low: "低",
  };
  return priorityMap[priority] || priority;
};

// 创建/编辑项目对话框
const dialogVisible = ref(false);
const dialogTitle = ref("");
const dialogLoading = ref(false);
const editingProjectId = ref(null);

// 删除项目对话框
const deleteDialogVisible = ref(false);
const deleteProjectId = ref(null);
const deleteProjectName = ref("");

// 表单引用
const projectFormRef = ref(null);

// 表单数据
const projectForm = reactive({
  project_name: "",
  description: "",
  status: "not_started",
  priority: "medium",
  owner_id: "", // 项目负责人ID
  start_date: "",
  end_date: "",
  doc_url: "",
  pipeline_url: "",
  selectedUsers: [], // 多选用户ID数组
});

// 所有用户列表，用于选择项目成员
const allUsers = ref([]);

// 获取所有用户列表
const getAllUsers = async () => {
  try {
    const response = await getUserList();
    allUsers.value = response.data?.users || [];
  } catch (error) {
    console.error("获取用户列表失败:", error);
    ElMessage.error("获取用户列表失败");
  }
};

// 监听项目负责人变化
watch(
  () => projectForm.owner_id,
  (newOwnerId, oldOwnerId) => {
    if (!newOwnerId) return;

    // 先过滤掉旧的负责人ID（如果存在），然后添加新的负责人ID
    const updatedUsers = projectForm.selectedUsers.filter(
      (id) => id !== oldOwnerId,
    );

    // 确保新的负责人ID被添加到列表中
    if (!updatedUsers.includes(newOwnerId)) {
      updatedUsers.push(newOwnerId);
    }

    // 更新项目成员列表
    projectForm.selectedUsers = updatedUsers;
  },
);

// 处理项目成员变化，确保当前负责人无法被删除
const handleMembersChange = () => {
  if (!projectForm.owner_id) return;

  // 检查当前负责人是否在项目成员列表中
  if (!projectForm.selectedUsers.includes(projectForm.owner_id)) {
    // 如果不在，自动添加回列表
    projectForm.selectedUsers.push(projectForm.owner_id);
    // 显示提示信息
    ElMessage.warning("当前项目负责人无法从成员列表中删除");
  }
};

// 用于项目成员下拉列表的排序，将负责人排在顶部
const getSortedUsers = () => {
  if (!projectForm.owner_id) return allUsers.value;

  // 创建用户列表的副本，避免修改原始数据
  const sortedUsers = [...allUsers.value];

  // 排序：将项目负责人排在最前面
  return sortedUsers.sort((a, b) => {
    if (a.id == projectForm.owner_id) return -1;
    if (b.id == projectForm.owner_id) return 1;
    return 0;
  });
};

// 表单验证规则
const projectRules = {
  project_name: [
    { required: true, message: "请输入项目名称", trigger: "blur" },
    {
      min: 1,
      max: 100,
      message: "项目名称长度在 1 到 100 个字符",
      trigger: "blur",
    },
  ],
  description: [{ required: true, message: "请输入项目描述", trigger: "blur" }],
  status: [{ required: true, message: "请选择项目状态", trigger: "change" }],
  priority: [
    { required: true, message: "请选择项目优先级", trigger: "change" },
  ],
  owner_id: [
    { required: true, message: "请选择项目负责人", trigger: "change" },
  ],
  start_date: [
    { required: true, message: "请选择开始日期", trigger: "change" },
  ],
  end_date: [{ required: true, message: "请选择结束日期", trigger: "change" }],
};

// 获取项目列表
const getProjectList = async () => {
  loading.value = true;
  try {
    const params = {
      page: pagination.currentPage,
      size: pagination.pageSize,
      search: searchQuery.value,
      status: statusFilter.value,
      priority: priorityFilter.value,
    };

    const response = await getProjects(params);
    // 后端返回标准格式：{code: 200, message: 'success', data: {items: [...], total: 10}}
    projectList.value = response.data?.items || [];
    // 为每个项目添加_displayUserId字段，初始值为creator_id
    projectList.value.forEach((project) => {
      project._displayUserId = project.creator_id;
    });
    pagination.total = response.data?.total || 0;
  } catch (error) {
    console.error("获取项目列表失败:", error);
    ElMessage.error("获取项目列表失败");
    projectList.value = [];
    pagination.total = 0;
  } finally {
    loading.value = false;
  }
};

// 重置筛选条件
const resetFilters = () => {
  searchQuery.value = "";
  statusFilter.value = "";
  priorityFilter.value = "";
  pagination.currentPage = 1;
  getProjectList();
};

// 分页大小变化
const handleSizeChange = (size) => {
  pagination.pageSize = size;
  pagination.currentPage = 1;
  getProjectList();
};

// 当前页码变化
const handleCurrentChange = (current) => {
  pagination.currentPage = current;
  getProjectList();
};

// 重置表单
const resetForm = () => {
  if (projectFormRef.value) {
    projectFormRef.value.resetFields();
  }
  editingProjectId.value = null;
  Object.assign(projectForm, {
    project_name: "",
    description: "",
    status: "not_started",
    priority: "medium",
    start_date: "",
    end_date: "",
    doc_url: "",
    pipeline_url: "",
    selectedUsers: [],
  });
};

// 打开创建项目对话框
const handleCreateProject = () => {
  dialogTitle.value = "创建项目";
  resetForm();
  getAllUsers();
  dialogVisible.value = true;
};

// 打开编辑项目对话框
const handleEditProject = (row) => {
  dialogTitle.value = "编辑项目";
  editingProjectId.value = row.id;

  // 转换项目成员数据为多选格式
  const members = row.members || [];
  const selectedUsers = members.map((member) => member.user_id);

  // 设置表单数据
  Object.assign(projectForm, {
    project_name: row.project_name || "",
    description: row.description || "",
    status: row.status || "not_started",
    priority: row.priority || "medium",
    owner_id: row.owner_id || "",
    start_date: row.start_date || "",
    end_date: row.end_date || "",
    doc_url: row.doc_url || "",
    pipeline_url: row.pipeline_url || "",
    selectedUsers: selectedUsers,
  });
  getAllUsers();
  dialogVisible.value = true;
};

// 保存项目
const handleSaveProject = async () => {
  if (!projectFormRef.value) return;

  await projectFormRef.value.validate();

  // 引入useUserStore获取当前登录用户信息
  const userStore = useUserStore();
  const currentUserId = userStore.userInfo.id;

  // 构建保存数据，将selectedUsers转换为members数组格式
  const saveData = { ...projectForm };

  // 只有创建项目时才设置creator_id，编辑时不修改创建者
  if (!editingProjectId.value) {
    // 添加创建者ID为当前登录用户ID
    saveData.creator_id = currentUserId;
  }

  // 转换多选用户为members数组格式，固定使用tester角色
  saveData.members = saveData.selectedUsers.map((userId) => ({
    user_id: userId,
    role: "tester", // 固定默认角色为tester
  }));

  // 删除不需要发送给后端的字段
  delete saveData.selectedUsers;

  dialogLoading.value = true;
  try {
    let response;
    if (editingProjectId.value) {
      // 编辑项目
      response = await updateProject(editingProjectId.value, saveData);
      ElMessage.success("项目更新成功");
    } else {
      // 创建项目
      response = await createProject(saveData);
      ElMessage.success("项目创建成功");
    }

    dialogVisible.value = false;
    getProjectList(); // 重新获取项目列表
  } catch (error) {
    console.error("保存项目失败:", error);
    ElMessage.error(editingProjectId.value ? "项目更新失败" : "项目创建失败");
  } finally {
    dialogLoading.value = false;
  }
};

// 打开删除项目对话框
const handleDeleteProject = (row) => {
  deleteProjectId.value = row.id;
  deleteProjectName.value = row.project_name || "未知项目";
  deleteDialogVisible.value = true;
};

// 确认删除项目
const handleConfirmDelete = async () => {
  if (!deleteProjectId.value) return;

  dialogLoading.value = true;
  try {
    await deleteProject(deleteProjectId.value);
    ElMessage.success("项目删除成功");
    deleteDialogVisible.value = false;
    getProjectList(); // 重新获取项目列表
  } catch (error) {
    console.error("删除项目失败:", error);
    ElMessage.error("项目删除失败");
  } finally {
    dialogLoading.value = false;
  }
};

// 查看项目
const handleViewProject = (row) => {
  // 跳转到项目详情页面
  router.push(`/projects/${row.id}`);
};

// 获取创建者选项列表 - 直接使用后端返回的项目成员数据
const getCreatorOptions = (row) => {
  // 确保使用项目成员表的数据
  if (row.members && row.members.length > 0) {
    return row.members;
  }

  // 如果没有成员数据，至少包含当前创建者
  if (row.creator_id && row.creator_name) {
    return [
      {
        user_id: row.creator_id,
        user_name: row.creator_name,
      },
    ];
  }

  return [];
};

// 处理创建者变更 - 恢复原始值，实现可展开但不可选择
const handleCreatorChange = (row) => {
  // 恢复_displayUserId为creator_id，而不是修改原始creator_id
  row._displayUserId = row.creator_id;
};

// 生命周期钩子 - 组件挂载时获取项目列表
onMounted(() => {
  getProjectList();
});
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

/* 项目成员样式 */
.no-members {
  margin-bottom: 10px;
  color: #909399;
}

.member-item {
  margin-bottom: 10px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.member-fields {
  display: flex;
  align-items: center;
  gap: 10px;
}

.member-fields .el-select {
  margin-right: 10px;
}
</style>
