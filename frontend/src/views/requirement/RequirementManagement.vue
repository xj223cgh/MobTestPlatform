<template>
  <div class="requirement-management">
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
            style="width: 200px"
            @change="handleTimeRangeChange"
          />
        </el-form-item>
        <el-form-item label="所属项目">
          <el-select
            v-model="projectFilter"
            placeholder="请选择项目"
            multiple
            clearable
            style="width: 135px"
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
            placeholder="请选择迭代"
            multiple
            clearable
            :disabled="!projectFilter || projectFilter.length === 0"
            style="width: 135px"
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
        <el-form-item label="负责人">
          <el-select
            v-model="assigneeFilter"
            placeholder="请选择负责人"
            multiple
            clearable
            filterable
            allow-create
            default-first-option
            style="width: 140px"
            @change="getRequirementList"
          >
            <el-option
              v-for="user in assigneeOptions"
              :key="user.id"
              :label="user.real_name || user.username"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
        <div class="search-actions">
          <el-form-item>
            <el-button
              :loading="loading"
              @click="resetFilters"
            >
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              :loading="loading"
              @click="handleCreateRequirement"
            >
              <el-icon><Plus /></el-icon>
              创建
            </el-button>
          </el-form-item>
        </div>
      </el-form>
    </div>

    <!-- 需求列表：表格放在滚动视口内，横向滚动条在视口底部，无需滚到列表底部即可左右滑动 -->
    <div class="table-section">
      <div class="table-scroll-viewport">
        <el-table
        ref="requirementTableRef"
        v-loading="loading"
        :data="requirementList"
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
          width="80"
          align="center"
        >
          <template #default="scope">
            {{ scope.row.id ?? "-" }}
          </template>
        </el-table-column>
        <el-table-column
          prop="requirement_name"
          label="需求名称"
          min-width="120"
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
            {{ scope.row.iteration_name || "-" }}
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
          prop="assigned_to_name"
          label="负责人"
          min-width="110"
          align="center"
        >
          <template #default="scope">
            {{ scope.row.assigned_to_name || scope.row.assigned_to || "-" }}
          </template>
        </el-table-column>
        <el-table-column
          prop="estimated_hours"
          label="预估工时"
          min-width="90"
          align="center"
        >
          <template #default="scope">
            {{
              scope.row.estimated_hours ? `${scope.row.estimated_hours}h` : "-"
            }}
          </template>
        </el-table-column>
        <el-table-column
          label="操作"
          width="150"
          fixed="right"
          align="center"
        >
          <template #default="scope">
            <div class="operation-buttons">
              <el-button
                type="success"
                size="small"
                class="op-btn"
                @click="handleEditRequirement(scope.row)"
              >
                编辑
              </el-button>
              <el-button
                type="danger"
                size="small"
                class="op-btn"
                @click="handleDeleteRequirement(scope.row)"
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
        ref="requirementFormRef"
        :model="requirementForm"
        :rules="requirementRules"
        label-width="100px"
      >
        <el-form-item
          label="需求名称"
          prop="requirement_name"
          required
        >
          <el-input
            v-model="requirementForm.requirement_name"
            placeholder="请输入需求名称"
          />
        </el-form-item>
        <el-form-item
          label="需求描述"
          prop="description"
          required
        >
          <el-input
            v-model="requirementForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入需求描述"
          />
        </el-form-item>
        <el-form-item
          label="所属项目"
          prop="project_id"
          required
        >
          <el-select
            v-model="requirementForm.project_id"
            placeholder="请选择所属项目"
            style="width: 100%"
            clearable
            @change="handleProjectChange"
          >
            <el-option
              v-for="project in projectOptions"
              :key="project.id"
              :label="project.project_name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item
          label="所属迭代"
          prop="iteration_id"
        >
          <el-select
            v-model="requirementForm.iteration_id"
            placeholder="请选择所属迭代"
            style="width: 100%"
            clearable
            :disabled="!requirementForm.project_id"
            :loading="iterationLoading"
            @focus="
              requirementForm.project_id && loadDialogIterations(requirementForm.project_id)
            "
          >
            <template #empty>
              <div v-if="!requirementForm.project_id">
                请先选择项目
              </div>
              <div v-else-if="iterationLoading">
                数据加载中...
              </div>
              <div v-else-if="dialogIterationOptions.length === 0">
                <span>暂无迭代数据</span>
                <el-button
                  type="primary"
                  link
                  size="small"
                  @click="loadDialogIterations(requirementForm.project_id)"
                >
                  重新加载
                </el-button>
              </div>
              <div v-else>
                未找到匹配的迭代
              </div>
            </template>
            <el-option
              v-for="iteration in dialogIterationOptions"
              :key="iteration.id"
              :label="iteration.iteration_name"
              :value="iteration.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item
          label="状态"
          prop="status"
          required
        >
          <el-select
            v-model="requirementForm.status"
            placeholder="请选择需求状态"
          >
            <el-option
              label="新建"
              value="new"
            />
            <el-option
              label="进行中"
              value="in_progress"
            />
            <el-option
              label="已完成"
              value="completed"
            />
            <el-option
              label="已取消"
              value="cancelled"
            />
          </el-select>
        </el-form-item>
        <el-form-item
          label="优先级"
          prop="priority"
          required
        >
          <el-select
            v-model="requirementForm.priority"
            placeholder="请选择优先级"
          >
            <el-option
              label="P0"
              value="P0"
            />
            <el-option
              label="P1"
              value="P1"
            />
            <el-option
              label="P2"
              value="P2"
            />
            <el-option
              label="P3"
              value="P3"
            />
            <el-option
              label="P4"
              value="P4"
            />
          </el-select>
        </el-form-item>
        <el-form-item
          label="环境"
          prop="environment"
          required
        >
          <el-select
            v-model="requirementForm.environment"
            placeholder="请选择环境"
          >
            <el-option
              label="测试环境"
              value="test"
            />
            <el-option
              label="预发环境"
              value="staging"
            />
            <el-option
              label="正式环境"
              value="production"
            />
          </el-select>
        </el-form-item>
        <el-form-item
          label="预估工时"
          prop="estimated_hours"
        >
          <el-input-number
            v-model="requirementForm.estimated_hours"
            :min="0"
            :step="0.5"
            placeholder="请输入预估工时"
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item
          label="分配给"
          prop="assigned_to"
          required
        >
          <el-select
            v-model="requirementForm.assigned_to"
            placeholder="请选择负责人"
            style="width: 100%"
          >
            <el-option
              v-for="user in assigneeOptions"
              :key="user.id"
              :label="user.real_name || user.username"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item
          label="开始时间"
          prop="start_date"
          required
        >
          <el-date-picker
            v-model="requirementForm.start_date"
            type="datetime"
            placeholder="请选择开始时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item
          label="结束时间"
          prop="end_date"
          required
        >
          <el-date-picker
            v-model="requirementForm.end_date"
            type="datetime"
            placeholder="请选择结束时间"
            style="width: 100%"
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
          @click="handleSaveRequirement"
        >
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch, nextTick } from "vue";
import { useRouter } from "vue-router";
import { useRoute } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { formatDateTime } from "@/utils/helpers";
import { Plus, Search, Refresh, Edit, Delete } from "@element-plus/icons-vue";
import {
  getAllVersionRequirements,
  getProjects,
  getProjectIterations,
  createVersionRequirement,
  updateVersionRequirement,
  deleteVersionRequirement,
} from "@/api/project";
import { getUserOptions } from "@/api/user";
import { useSystemSettingsStore } from "@/stores/systemSettings";
import dayjs from "dayjs";

const route = useRoute();
const router = useRouter();

// 从用例集信息跳转时高亮指定行（仅此时有值）
const highlightId = computed(() => {
  const id = route.query?.highlight_id;
  return id ? Number(id) : null;
});
// 消息跳转时的短暂闪烁行（2.5s 后清除）
const flashRowId = ref(null);
let flashClearTimer = null;
const getRowClassName = ({ row }) => {
  if (flashRowId.value && row.id === flashRowId.value) return "notification-flash-row";
  if (highlightId.value && row.id === highlightId.value) return "highlight-row";
  return "";
};

const loading = ref(false);

// 时间筛选范围，默认当前年月的前后两个月
const currentDate = dayjs();
const timeRangeFilter = ref([
  currentDate.subtract(2, "month").format("YYYY-MM"),
  currentDate.add(2, "month").format("YYYY-MM"),
]);
const projectFilter = ref([]);
const iterationFilter = ref([]);
const assigneeFilter = ref([]);

const searchForm = reactive({});

const projectOptions = ref([]);
const iterationOptions = ref([]);
/** 弹窗内「所属迭代」下拉数据（按选中项目单独加载） */
const dialogIterationOptions = ref([]);
const iterationLoading = ref(false);
const userOptions = ref([]);
const creatorOptions = ref([]);
const assigneeOptions = ref([]);

const requirementList = ref([]);
const requirementTableRef = ref(null);

// 分页信息（每页条数使用系统设置，默认 10）
const systemSettingsStore = useSystemSettingsStore();
const pagination = reactive({
  currentPage: 1,
  pageSize: systemSettingsStore.defaultPageSize || 10,
  total: 0,
});

const dialogVisible = ref(false);
const dialogTitle = ref("");
const dialogLoading = ref(false);
const editingRequirementId = ref(null);

const requirementFormRef = ref(null);

const requirementForm = reactive({
  requirement_name: "",
  description: "",
  status: "new",
  project_id: "",
  iteration_id: "",
  priority: "P1",
  environment: "test",
  estimated_hours: null,
  actual_hours: null,
  assigned_to: "",
  start_date: "",
  end_date: "",
});

const filteredIterationOptions = computed(() => {
  if (!requirementForm.project_id) {
    return [];
  }
  return iterationOptions.value.filter((iteration) => {
    return iteration.project_id === requirementForm.project_id;
  });
});

const requirementRules = {
  requirement_name: [
    { required: true, message: "请输入需求名称", trigger: "blur" },
    {
      min: 1,
      max: 200,
      message: "需求名称长度在 1 到 200 个字符",
      trigger: "blur",
    },
  ],
  description: [{ required: true, message: "请输入需求描述", trigger: "blur" }],
  project_id: [
    { required: true, message: "请选择所属项目", trigger: "change" },
  ],
  status: [{ required: true, message: "请选择需求状态", trigger: "change" }],
  priority: [{ required: true, message: "请选择优先级", trigger: "change" }],
  environment: [{ required: true, message: "请选择环境", trigger: "change" }],
  assigned_to: [{ required: true, message: "请选择负责人", trigger: "change" }],
  start_date: [
    { required: true, message: "请选择开始时间", trigger: "change" },
  ],
  end_date: [{ required: true, message: "请选择结束时间", trigger: "change" }],
};

const getRequirementList = async () => {
  loading.value = true;
  try {
    const response = await getAllVersionRequirements();

    if (response.code === 200) {
      let allItems = response.data.items || [];

      // 1. 默认按创建时间倒序排序（最新数据在前）
      allItems.sort((a, b) => {
        const dateA = new Date(a.updated_at || a.created_at || 0);
        const dateB = new Date(b.updated_at || b.created_at || 0);
        return dateB - dateA;
      });

      if (projectFilter.value && projectFilter.value.length > 0) {
        allItems = allItems.filter((item) =>
          projectFilter.value.includes(item.project_id),
        );
      }

      if (iterationFilter.value && iterationFilter.value.length > 0) {
        allItems = allItems.filter((item) =>
          iterationFilter.value.includes(item.iteration_id),
        );
      }

      if (assigneeFilter.value && assigneeFilter.value.length > 0) {
        allItems = allItems.filter((item) =>
          assigneeFilter.value.includes(item.assigned_to),
        );
      }

      pagination.total = allItems.length || 0;

      // 若有 highlight_id（从用例集信息跳转），跳到该需求所在页
      const hid = route.query?.highlight_id;
      if (hid) {
        const idx = allItems.findIndex((i) => i.id === Number(hid));
        if (idx >= 0)
          pagination.currentPage =
            Math.floor(idx / pagination.pageSize) + 1;
      }

      const startIndex = (pagination.currentPage - 1) * pagination.pageSize;
      const endIndex = startIndex + pagination.pageSize;
      requirementList.value = allItems.slice(startIndex, endIndex);
    } else {
      ElMessage.error("获取需求列表失败");
    }
  } catch (error) {
    console.error("获取需求列表失败:", error);
    ElMessage.error("获取需求列表失败");
  } finally {
    loading.value = false;
  }
};

const getStatusType = (status) => {
  const statusMap = {
    new: "info",
    in_progress: "warning",
    completed: "success",
    cancelled: "danger",
  };
  return statusMap[status] || "info";
};

const getStatusText = (status) => {
  const statusMap = {
    new: "新建",
    in_progress: "进行中",
    completed: "已完成",
    cancelled: "已取消",
  };
  return statusMap[status] || status;
};

const getPriorityType = (priority) => {
  const priorityMap = {
    P0: "danger",
    P1: "danger",
    P2: "warning",
    P3: "success",
    P4: "info",
  };
  return priorityMap[priority] || "info";
};

const getPriorityText = (priority) => priority || "P1";

const getEnvironmentType = (environment) => {
  const envMap = {
    test: "info",
    staging: "warning",
    production: "success",
  };
  return envMap[environment] || "info";
};

const getEnvironmentText = (environment) => {
  const envMap = {
    test: "测试环境",
    staging: "预发环境",
    production: "正式环境",
  };
  return envMap[environment] || environment;
};

const resetFilters = () => {
  const currentDate = dayjs();
  timeRangeFilter.value = [
    currentDate.subtract(2, "month").format("YYYY-MM"),
    currentDate.add(2, "month").format("YYYY-MM"),
  ];
  projectFilter.value = [];
  iterationFilter.value = [];
  assigneeFilter.value = [];
  pagination.currentPage = 1;
  getOptionData();
  getRequirementList();
};

const handleTimeRangeChange = async () => {
  try {
    const projectsResponse = await getProjects({ page: 1, size: 10000 });
    let allProjects = projectsResponse.data?.items || [];

    const filteredProjects = allProjects.filter((project) => {
      if (!timeRangeFilter.value || timeRangeFilter.value.length !== 2)
        return true;

      const projectYearMonth = project.created_at?.substring(0, 7);
      if (!projectYearMonth) return true;

      const [startYearMonth, endYearMonth] = timeRangeFilter.value;
      return (
        projectYearMonth >= startYearMonth && projectYearMonth <= endYearMonth
      );
    });

    projectOptions.value = filteredProjects;

    if (projectFilter.value && projectFilter.value.length > 0) {
      const selectedIterations = [];
      for (const projectId of projectFilter.value) {
        try {
          const iterationsResponse = await getProjectIterations(projectId);
          const projectIterations = iterationsResponse.data?.items || [];
          selectedIterations.push(...projectIterations);
        } catch (error) {
          console.error(`获取项目${projectId}的迭代失败:`, error);
        }
      }
      iterationOptions.value = selectedIterations;
    }

    console.log("时间范围筛选已更新，只影响项目和迭代下拉列表");
  } catch (error) {
    console.error("更新项目选项失败:", error);
    ElMessage.error("更新项目选项失败");
  }
};

const handleProjectFilterChange = async () => {
  try {
    if (!projectFilter.value || projectFilter.value.length === 0) {
      iterationOptions.value = [];
      iterationFilter.value = [];
    } else {
      const selectedIterations = [];
      for (const projectId of projectFilter.value) {
        try {
          const iterationsResponse = await getProjectIterations(projectId);
          const projectIterations = iterationsResponse.data?.items || [];
          selectedIterations.push(...projectIterations);
        } catch (error) {
          console.error(`获取项目${projectId}的迭代失败:`, error);
        }
      }

      iterationOptions.value = selectedIterations;

      if (iterationFilter.value && iterationFilter.value.length > 0) {
        const validIterationIds = selectedIterations.map((iter) => iter.id);
        const validFilters = iterationFilter.value.filter((id) =>
          validIterationIds.includes(id),
        );
        iterationFilter.value = validFilters;
      }
    }

    await updateUserOptions();
    getRequirementList();
  } catch (error) {
    console.error("更新迭代选项失败:", error);
    ElMessage.error("更新迭代选项失败");
  }
};

const handleIterationFilterChange = async () => {
  try {
    await updateUserOptions();
    getRequirementList();
  } catch (error) {
    console.error("更新用户选项失败:", error);
    ElMessage.error("更新用户选项失败");
  }
};

// 更新用户选项函数（使用仅需登录的 getUserOptions，不依赖 user.list 权限）
const updateUserOptions = async () => {
  let allUsers = [];
  try {
    const usersResponse = await getUserOptions({ size: 1000 });
    allUsers = usersResponse?.data?.items || [];
  } catch (error) {
    console.error("获取用户列表失败:", error);
    ElMessage.error("获取用户列表失败");
  }

  userOptions.value = allUsers;
  creatorOptions.value = allUsers;
  assigneeOptions.value = allUsers;

  if (allUsers.length === 0) return;

  if (
    (projectFilter.value && projectFilter.value.length > 0) ||
    (iterationFilter.value && iterationFilter.value.length > 0)
  ) {
    console.log("有选中的项目或迭代，开始过滤用户");

    try {
      const response = await getAllVersionRequirements();
      if (response.code === 200) {
        const allRequirements = response.data?.items || [];
        console.log("获取到的需求列表:", allRequirements);
        let filteredRequirements = allRequirements;

        if (projectFilter.value && projectFilter.value.length > 0) {
          filteredRequirements = filteredRequirements.filter((req) =>
            projectFilter.value.includes(req.project_id),
          );
          console.log("按项目筛选后的需求:", filteredRequirements);
        }

        if (iterationFilter.value && iterationFilter.value.length > 0) {
          filteredRequirements = filteredRequirements.filter((req) =>
            iterationFilter.value.includes(req.iteration_id),
          );
          console.log("按迭代筛选后的需求:", filteredRequirements);
        }

        const creatorIds = new Set();
        filteredRequirements.forEach((req) => {
          if (req.created_by) {
            creatorIds.add(req.created_by);
          }
        });
        console.log("提取到的创建者ID:", creatorIds);

        const assigneeIds = new Set();
        filteredRequirements.forEach((req) => {
          if (req.assigned_to) {
            assigneeIds.add(req.assigned_to);
          }
        });
        console.log("提取到的负责人ID:", assigneeIds);

        if (creatorIds.size > 0) {
          const filteredCreators = allUsers.filter((user) =>
            creatorIds.has(user.id),
          );
          console.log("筛选后的创建者:", filteredCreators);
          creatorOptions.value = filteredCreators;
        }

        if (assigneeIds.size > 0) {
          const filteredAssignees = allUsers.filter((user) =>
            assigneeIds.has(user.id),
          );
          console.log("筛选后的负责人:", filteredAssignees);
          assigneeOptions.value = filteredAssignees;
        }
      }
    } catch (error) {
      console.error("根据项目/迭代筛选用户失败:", error);
    }
  }
};

const getOptionData = async () => {
  try {
    const projectsResponse = await getProjects({ page: 1, size: 10000 });
    let allProjects = projectsResponse.data?.items || [];

    const filteredProjects = allProjects.filter((project) => {
      if (!timeRangeFilter.value || timeRangeFilter.value.length !== 2)
        return true;

      const projectYearMonth = project.created_at?.substring(0, 7);
      if (!projectYearMonth) return true;

      const [startYearMonth, endYearMonth] = timeRangeFilter.value;
      return (
        projectYearMonth >= startYearMonth && projectYearMonth <= endYearMonth
      );
    });

    projectOptions.value = filteredProjects;

    let iterationsToLoad = filteredProjects;

    if (projectFilter.value && projectFilter.value.length > 0) {
      iterationsToLoad = filteredProjects.filter((project) =>
        projectFilter.value.includes(project.id),
      );
    }

    const allIterations = [];
    for (const project of iterationsToLoad) {
      try {
        const iterationsResponse = await getProjectIterations(project.id);
        const projectIterations = iterationsResponse.data?.items || [];
        allIterations.push(...projectIterations);
      } catch (error) {
        console.error(`获取项目${project.project_name}的迭代失败:`, error);
      }
    }

    iterationOptions.value = allIterations;

    await updateUserOptions();
  } catch (error) {
    console.error("获取选项数据失败:", error);
    ElMessage.error("获取选项数据失败");

    try {
      const usersResponse = await getUserOptions({ size: 1000 });
      const items = usersResponse?.data?.items || [];
      userOptions.value = items;
      creatorOptions.value = items;
      assigneeOptions.value = items;
    } catch (userError) {
      console.error("获取用户列表失败:", userError);
      userOptions.value = [];
      creatorOptions.value = [];
      assigneeOptions.value = [];
    }
  }
};

const handleSizeChange = (size) => {
  pagination.pageSize = size;
  pagination.currentPage = 1;
  getRequirementList();
};

const handleCurrentChange = (current) => {
  pagination.currentPage = current;
  getRequirementList();
};

const resetForm = () => {
  if (requirementFormRef.value) {
    requirementFormRef.value.resetFields();
  }
  editingRequirementId.value = null;
  dialogIterationOptions.value = [];
  Object.assign(requirementForm, {
    requirement_name: "",
    description: "",
    status: "new",
    project_id: "",
    iteration_id: "",
    priority: "P1",
    environment: "test",
    estimated_hours: null,
    actual_hours: null,
    assigned_to: "",
    start_date: "",
    end_date: "",
  });
};

const loadDialogIterations = async (projectId) => {
  if (!projectId) {
    dialogIterationOptions.value = [];
    return;
  }
  iterationLoading.value = true;
  dialogIterationOptions.value = [];
  try {
    const res = await getProjectIterations(projectId, { page: 1, page_size: 1000 });
    dialogIterationOptions.value = res?.data?.items ?? [];
  } catch (e) {
    console.error("加载迭代列表失败:", e);
    ElMessage.error("加载迭代列表失败");
  } finally {
    iterationLoading.value = false;
  }
};

const handleProjectChange = () => {
  requirementForm.iteration_id = "";
  if (requirementForm.project_id) {
    loadDialogIterations(requirementForm.project_id);
  } else {
    dialogIterationOptions.value = [];
  }
};

const handleCreateRequirement = () => {
  dialogTitle.value = "创建需求";
  resetForm();
  dialogVisible.value = true;
};

const handleEditRequirement = (row) => {
  dialogTitle.value = "编辑需求";
  editingRequirementId.value = row.id;

  Object.assign(requirementForm, {
    requirement_name: row.requirement_name || "",
    description: row.requirement_description || "",
    status: row.status || "new",
    project_id: row.project_id || "",
    iteration_id: row.iteration_id || "",
    priority: row.priority || "P1",
    environment: row.environment || "test",
    estimated_hours: row.estimated_hours || null,
    actual_hours: row.actual_hours || null,
    assigned_to: row.assigned_to || "",
    start_date: row.start_date || "",
    end_date: row.end_date || "",
  });
  if (requirementForm.project_id) {
    loadDialogIterations(requirementForm.project_id);
  } else {
    dialogIterationOptions.value = [];
  }
  dialogVisible.value = true;
};

const handleSaveRequirement = async () => {
  if (!requirementFormRef.value) return;

  await requirementFormRef.value.validate();

  const saveData = {
    requirement_name: requirementForm.requirement_name,
    description: requirementForm.description,
    status: requirementForm.status,
    project_id: requirementForm.project_id,
    iteration_id: requirementForm.iteration_id || null,
    priority: requirementForm.priority,
    environment: requirementForm.environment,
    estimated_hours: requirementForm.estimated_hours,
    actual_hours: requirementForm.actual_hours,
    assigned_to: requirementForm.assigned_to || null,
    start_date: requirementForm.start_date,
    end_date: requirementForm.end_date,
  };

  dialogLoading.value = true;
  try {
    let response;
    if (editingRequirementId.value) {
      response = await updateVersionRequirement(
        requirementForm.project_id,
        editingRequirementId.value,
        saveData,
      );
      ElMessage.success("需求更新成功");
    } else {
      response = await createVersionRequirement(
        requirementForm.project_id,
        saveData,
      );
      ElMessage.success("需求创建成功");
    }

    dialogVisible.value = false;
    getRequirementList();
  } catch (error) {
    console.error("保存需求失败:", error);
    ElMessage.error(
      editingRequirementId.value ? "需求更新失败" : "需求创建失败",
    );
  } finally {
    dialogLoading.value = false;
  }
};

const handleDeleteRequirement = (row) => {
  ElMessageBox.confirm(
    `确定要删除需求「${row.requirement_name}」吗？`,
    "提示",
    {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    },
  )
    .then(async () => {
      try {
        await deleteVersionRequirement(row.project_id, row.id);
        ElMessage.success("需求删除成功");
        getRequirementList();
      } catch (error) {
        console.error("删除需求失败:", error);
        if (!error.response?.data?.message) {
          ElMessage.error("删除需求失败");
        }
      }
    })
    .catch(() => {});
};

// 页面加载时：需求列表立即请求，选项数据并行加载，避免列表等待下拉数据
// 高亮行滚动到视口（仅当通过 highlight_id 或消息跳转时）
const scrollToHighlightRow = () => {
  const targetId = flashRowId.value || highlightId.value;
  if (!targetId || !requirementList.value.length) return;
  nextTick(() => {
    setTimeout(() => {
      const table = requirementTableRef.value?.$el;
      if (!table) return;
      const row = table.querySelector("tr.notification-flash-row, tr.highlight-row");
      if (row) row.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }, 150);
  });
};

// 消息跳转：从 query 设置要闪烁的 id，等列表渲染出该行后再启动 2.5s 清除定时器
watch(
  () => route.query?.highlight_id ?? route.query?.requirementId,
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

// 列表加载出目标行后再启动清除定时器，确保行先带上样式
watch(
  () => [requirementList.value, flashRowId.value],
  () => {
    const id = flashRowId.value;
    if (!id || !requirementList.value.length) return;
    const hasRow = requirementList.value.some((r) => r.id === id);
    if (!hasRow) return;
    if (flashClearTimer) return;
    flashClearTimer = setTimeout(() => {
      flashRowId.value = null;
      const q = { ...route.query };
      delete q.highlight_id;
      delete q.requirementId;
      router.replace({ path: route.path, query: Object.keys(q).length ? q : undefined });
      flashClearTimer = null;
    }, 2600);
  },
  { flush: "post" }
);

watch(
  () => [requirementList.value.length, highlightId.value, flashRowId.value],
  () => scrollToHighlightRow(),
  { flush: "post" }
);

// 已在需求页时收到新通知跳转（query 变化）→ 重新加载列表以定位目标项
watch(
  () => route.query?.highlight_id,
  (idVal, oldVal) => {
    if (idVal && idVal !== oldVal) getRequirementList();
  }
);

onMounted(() => {
  getRequirementList();
  getOptionData();
});
</script>

<style lang="scss" scoped>
.requirement-management {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: #f5f7fa;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.search-section {
  flex-shrink: 0;
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  overflow-x: hidden;
  min-width: 0;
}

.search-section :deep(.el-form) {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px 16px;
  width: 100%;
}

.search-section :deep(.el-form-item) {
  margin-bottom: 0;
  margin-right: 0;
  flex: 0 0 auto;
  white-space: nowrap;
}

.search-section :deep(.el-form-item .el-date-editor),
.search-section :deep(.el-form-item .el-select) {
  min-width: 0;
}

/* 两个按钮始终靠右：一行时在右侧，换行时也在行末右对齐 */
.search-section .search-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 0 16px;
}

.search-section .search-actions :deep(.el-form-item) {
  margin-bottom: 0;
}

.table-section {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 56px; /* 分页条高度，表格底部与分页无明显间隔 */
}

/* 表格视口填满剩余高度，仅纵向滚动，不显示横向滑动条 */
.table-section .table-scroll-viewport {
  max-height: none !important;
  flex: 1;
  min-height: 0;
  overflow-x: hidden;
  overflow-y: auto;
}

.table-section .table-scroll-viewport :deep(.el-table) {
  min-width: 0 !important;
}

/* 从用例集信息跳转时的选中行高亮（直接显示，无边框） */
.table-section :deep(tr.highlight-row > td) {
  background-color: var(--el-color-primary-light-9, #ecf5ff) !important;
}
.table-section :deep(tr.highlight-row:hover > td) {
  background-color: var(--el-color-primary-light-8, #d9ecff) !important;
}

.table-section .table-scroll-viewport :deep(.el-table__body-wrapper) {
  overflow-x: hidden !important;
}

/* 固定分页组件样式 */
.fixed-pagination {
  position: fixed;
  bottom: 0;
  right: 0;
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
    margin-bottom: 56px;
  }
}

/* 操作列：三按钮单行、紧凑宽度，列已 fixed="right" 冻结 */
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

/* 确保在小屏幕下操作列不会被遮挡 */
:deep(.el-table__fixed-right) {
  height: calc(100% - 32px) !important;
}

:deep(.el-table__fixed-right-patch) {
  display: none;
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
