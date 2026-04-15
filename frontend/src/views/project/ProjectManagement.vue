<template>
  <div class="project-management">
    <div class="page-header">
      <div class="header-content">
        <h1>项目管理</h1>
        <p class="description">
          管理系统项目信息
        </p>
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

    <div class="search-section">
      <el-form
        :model="searchForm"
        inline
      >
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
            <el-option
              label="全部"
              value=""
            />
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

        <el-form-item label="优先级">
          <el-select
            v-model="priorityFilter"
            placeholder="全部优先级"
            clearable
            style="width: 120px"
            @clear="getProjectList"
          >
            <el-option
              label="全部"
              value=""
            />
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
        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            @click="getProjectList"
          >
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
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

    <div class="table-section">
      <div class="table-scroll-viewport">
        <el-table
          ref="projectTableRef"
          v-loading="loading"
          :data="projectList"
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
          type="index"
          width="80"
          fixed="left"
          align="center"
        />
        <el-table-column
          prop="project_name"
          label="项目名称"
          min-width="175"
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
              {{ getPriorityText(scope.row.priority) || "-" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="creator_name"
          label="项目成员"
          min-width="175"
          align="center"
        >
          <template #default="scope">
            <div class="creator-select-wrapper">
              <el-select
                v-model="scope.row._displayUserId"
                placeholder="项目成员"
                size="small"
                style="width: 90%"
                @change="handleCreatorChange(scope.row)"
              >
                <el-option
                  v-if="scope.row.creator_id && scope.row.creator_name"
                  :key="scope.row.creator_id"
                  :label="scope.row.creator_name + '（创建人）'"
                  :value="scope.row.creator_id"
                />

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
          min-width="125"
          align="center"
        >
          <template #default="scope">
            {{ scope.row.owner_name || "-" }}
          </template>
        </el-table-column>
        <el-table-column
          label="开始日期"
          min-width="120"
          align="center"
        >
          <template #default="scope">
            {{ formatDateTime(scope.row.start_date) }}
          </template>
        </el-table-column>
        <el-table-column
          label="结束日期"
          min-width="120"
          align="center"
        >
          <template #default="scope">
            {{ formatDateTime(scope.row.end_date) }}
          </template>
        </el-table-column>
        <el-table-column
          label="操作"
          width="160"
          fixed="right"
          align="center"
        >
          <template #default="scope">
            <div class="operation-buttons">
              <el-button
                type="primary"
                size="small"
                class="op-btn"
                @click="handleViewProject(scope.row)"
              >
                查看
              </el-button>
              <el-button
                type="success"
                size="small"
                class="op-btn"
                @click="handleEditProject(scope.row)"
              >
                编辑
              </el-button>
              <el-button
                type="danger"
                size="small"
                class="op-btn"
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
    </div>

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

    <el-dialog
      v-model="deleteDialogVisible"
      title="删除项目"
      width="400px"
    >
      <p>确定要删除项目 "{{ deleteProjectName }}" 吗？此操作不可撤销！</p>
      <template #footer>
        <el-button @click="deleteDialogVisible = false">
          取消
        </el-button>
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
// 项目管理列表页：搜索、筛选、分页、CRUD，支持消息跳转高亮闪烁目标行
import { ref, reactive, computed, onMounted, watch, nextTick } from "vue";
import { ElMessage } from "element-plus";
import { Plus, Search, Refresh } from "@element-plus/icons-vue";
import {
  getProjects,
  createProject,
  updateProject,
  deleteProject,
} from "@/api/project";
import { getUserOptions } from "@/api/user";
import { useRouter, useRoute } from "vue-router";
import { useUserStore } from "@/stores/user";
import { useSystemSettingsStore } from "@/stores/systemSettings";
import dayjs from "dayjs";

const systemSettingsStore = useSystemSettingsStore();

const loading = ref(false);
const projectList = ref([]);

const router = useRouter();
const route = useRoute();
const projectTableRef = ref(null);
const highlightId = computed(() => {
  const id = route.query.highlight_id;
  return id ? Number(id) : null;
});
const flashRowId = ref(null);
let flashClearTimer = null;
const getRowClassName = ({ row }) => {
  if (flashRowId.value && row.id === flashRowId.value) return "notification-flash-row";
  if (highlightId.value && row.id === highlightId.value) return "highlight-row";
  return "";
};

const searchQuery = ref("");
const statusFilter = ref("");
const priorityFilter = ref("");

const searchForm = reactive({});

// 分页（每页条数使用系统设置，默认 10）
const pagination = reactive({
  currentPage: 1,
  pageSize: systemSettingsStore.defaultPageSize || 10,
  total: 0,
});

const formatDateTime = (dateTime) => {
  return dateTime ? dayjs(dateTime).format("YYYY-MM-DD HH:mm:ss") : "-";
};

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

const getPriorityType = (priority) => {
  const priorityMap = {
    high: "danger",
    medium: "warning",
    low: "success",
  };
  return priorityMap[priority] || "info";
};

const getPriorityText = (priority) => {
  const priorityMap = {
    high: "高",
    medium: "中",
    low: "低",
  };
  return priorityMap[priority] || priority;
};

const dialogVisible = ref(false);
const dialogTitle = ref("");
const dialogLoading = ref(false);
const editingProjectId = ref(null);

const deleteDialogVisible = ref(false);
const deleteProjectId = ref(null);
const deleteProjectName = ref("");

const projectFormRef = ref(null);

const projectForm = reactive({
  project_name: "",
  description: "",
  status: "not_started",
  priority: "medium",
  owner_id: "",
  start_date: "",
  end_date: "",
  doc_url: "",
  pipeline_url: "",
  selectedUsers: [],
});

const allUsers = ref([]);

const getAllUsers = async () => {
  try {
    const response = await getUserOptions({ size: 1000 });
    allUsers.value = response.data?.items || [];
  } catch (error) {
    console.error("获取用户列表失败:", error);
    ElMessage.error("获取用户列表失败");
  }
};

watch(
  () => projectForm.owner_id,
  (newOwnerId, oldOwnerId) => {
    if (!newOwnerId) return;

    const updatedUsers = projectForm.selectedUsers.filter(
      (id) => id !== oldOwnerId,
    );

    if (!updatedUsers.includes(newOwnerId)) {
      updatedUsers.push(newOwnerId);
    }

    projectForm.selectedUsers = updatedUsers;
  },
);

// 处理项目成员变化，确保当前负责人无法被删除
const handleMembersChange = () => {
  if (!projectForm.owner_id) return;

  if (!projectForm.selectedUsers.includes(projectForm.owner_id)) {
    projectForm.selectedUsers.push(projectForm.owner_id);
    ElMessage.warning("当前项目负责人无法从成员列表中删除");
  }
};

// 用于项目成员下拉列表的排序，将负责人排在顶部
const getSortedUsers = () => {
  if (!projectForm.owner_id) return allUsers.value;

  const sortedUsers = [...allUsers.value];

  return sortedUsers.sort((a, b) => {
    if (a.id == projectForm.owner_id) return -1;
    if (b.id == projectForm.owner_id) return 1;
    return 0;
  });
};

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

const getProjectList = async () => {
  loading.value = true;
  try {
    const needHighlight = highlightId.value != null;
    const params = {
      page: needHighlight ? 1 : pagination.currentPage,
      size: needHighlight ? 10000 : pagination.pageSize,
      search: searchQuery.value,
      status: statusFilter.value,
      priority: priorityFilter.value,
    };

    const response = await getProjects(params);
    let items = response.data?.items || [];
    const total = response.data?.total || 0;
    // 为每个项目添加_displayUserId字段，初始值为creator_id
    items.forEach((project) => {
      project._displayUserId = project.creator_id;
    });

    if (needHighlight && items.length > 0) {
      const idx = items.findIndex((p) => p.id === highlightId.value);
      if (idx >= 0) {
        const pageSize = pagination.pageSize;
        pagination.currentPage = Math.floor(idx / pageSize) + 1;
        const start = (pagination.currentPage - 1) * pageSize;
        projectList.value = items.slice(start, start + pageSize);
      } else {
        projectList.value = items.slice(0, pagination.pageSize);
        pagination.currentPage = 1;
      }
      pagination.total = total;
    } else {
      projectList.value = items;
      pagination.total = total;
    }
  } catch (error) {
    console.error("获取项目列表失败:", error);
    ElMessage.error("获取项目列表失败");
    projectList.value = [];
    pagination.total = 0;
  } finally {
    loading.value = false;
  }
};

const resetFilters = () => {
  searchQuery.value = "";
  statusFilter.value = "";
  priorityFilter.value = "";
  pagination.currentPage = 1;
  getProjectList();
};

const handleSizeChange = (size) => {
  pagination.pageSize = size;
  pagination.currentPage = 1;
  getProjectList();
};

const handleCurrentChange = (current) => {
  pagination.currentPage = current;
  getProjectList();
};

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

const handleCreateProject = () => {
  dialogTitle.value = "创建项目";
  resetForm();
  getAllUsers();
  dialogVisible.value = true;
};

const handleEditProject = (row) => {
  dialogTitle.value = "编辑项目";
  editingProjectId.value = row.id;

  const members = row.members || [];
  const selectedUsers = members.map((member) => member.user_id);

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

const handleSaveProject = async () => {
  if (!projectFormRef.value) return;

  await projectFormRef.value.validate();

  const userStore = useUserStore();
  const currentUserId = userStore.userInfo.id;

  const saveData = { ...projectForm };

  // 只有创建项目时才设置creator_id，编辑时不修改创建者
  if (!editingProjectId.value) {
    saveData.creator_id = currentUserId;
  }

  saveData.members = saveData.selectedUsers.map((userId) => ({
    user_id: userId,
    role: "tester",
  }));

  delete saveData.selectedUsers;

  dialogLoading.value = true;
  try {
    let response;
    if (editingProjectId.value) {
      response = await updateProject(editingProjectId.value, saveData);
      ElMessage.success("项目更新成功");
    } else {
      response = await createProject(saveData);
      ElMessage.success("项目创建成功");
    }

    dialogVisible.value = false;
    getProjectList();
  } catch (error) {
    console.error("保存项目失败:", error);
    ElMessage.error(editingProjectId.value ? "项目更新失败" : "项目创建失败");
  } finally {
    dialogLoading.value = false;
  }
};

const handleDeleteProject = (row) => {
  deleteProjectId.value = row.id;
  deleteProjectName.value = row.project_name || "未知项目";
  deleteDialogVisible.value = true;
};

const handleConfirmDelete = async () => {
  if (!deleteProjectId.value) return;

  dialogLoading.value = true;
  try {
    await deleteProject(deleteProjectId.value);
    ElMessage.success("项目删除成功");
    deleteDialogVisible.value = false;
    getProjectList();
  } catch (error) {
    console.error("删除项目失败:", error);
    // 400 等校验提示已由 request 拦截器统一展示，此处仅处理无 response 的情况
    if (!error.response?.data?.message) {
      ElMessage.error("项目删除失败");
    }
  } finally {
    dialogLoading.value = false;
  }
};

const handleViewProject = (row) => {
  router.push(`/projects/${row.id}`);
};

// 处理创建者变更 - 恢复原始值，实现可展开但不可选择
const handleCreatorChange = (row) => {
  row._displayUserId = row.creator_id;
};

// 高亮行滚动到视口（仅当通过 highlight_id 或消息跳转时）
const scrollToHighlightRow = () => {
  const targetId = flashRowId.value || highlightId.value;
  if (!targetId || !projectList.value.length) return;
  nextTick(() => {
    setTimeout(() => {
      const table = projectTableRef.value?.$el;
      if (!table) return;
      const row = table.querySelector("tr.notification-flash-row, tr.highlight-row");
      if (row) row.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }, 150);
  });
};

watch(
  () => route.query?.highlight_id,
  (idVal) => {
    if (flashClearTimer) {
      clearTimeout(flashClearTimer);
      flashClearTimer = null;
    }
    if (!idVal) {
      flashRowId.value = null;
      return;
    }
    flashRowId.value = Number(idVal);
  },
  { immediate: true }
);

// 已在项目页时收到新通知跳转（query 变化）→ 重新加载列表以定位目标项
watch(
  () => route.query?.highlight_id,
  (idVal, oldVal) => {
    if (idVal && idVal !== oldVal) getProjectList();
  }
);

watch(
  () => [projectList.value, flashRowId.value],
  () => {
    const id = flashRowId.value;
    if (!id || !projectList.value.length) return;
    const hasRow = projectList.value.some((p) => p.id === id);
    if (!hasRow) return;
    if (flashClearTimer) return;
    flashClearTimer = setTimeout(() => {
      flashRowId.value = null;
      const q = { ...route.query };
      delete q.highlight_id;
      router.replace({ path: route.path, query: Object.keys(q).length ? q : undefined });
      flashClearTimer = null;
    }, 2600);
  },
  { flush: "post" }
);

watch(
  () => [projectList.value.length, highlightId.value, flashRowId.value],
  () => scrollToHighlightRow(),
  { flush: "post" }
);

onMounted(() => {
  getProjectList();
});
</script>

<style lang="scss" scoped>
.project-management {
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
    align-items: center;
    gap: 12px;
    min-width: 0;
  }

  .header-content h1 {
    margin: 0;
    font-size: 24px;
    font-weight: 500;
    color: var(--el-text-color-primary, #303133);
  }

  .description {
    margin: 0;
    color: var(--el-text-color-regular, #606266);
    font-size: 14px;
  }
}

.header-actions {
  display: flex;
  gap: 10px;
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

/* 去掉表单项默认下边距，使搜索区域上下空白对称 */
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

.search-section :deep(.el-form-item:last-child) {
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

/* 表格区域占满剩余高度，表头冻结、表体垂直滚动（由 Layout 全局样式配合） */
.table-section .table-scroll-viewport {
  flex: 1;
  min-height: 0;
  overflow-x: hidden;
  overflow-y: auto;
}

.table-section .table-scroll-viewport :deep(.el-table__body-wrapper) {
  overflow-x: hidden !important;
}

/* 从用例管理等处跳转时的选中行高亮（直接显示，无边框） */
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

/* 操作列：紧凑按钮，参考需求管理 */
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
