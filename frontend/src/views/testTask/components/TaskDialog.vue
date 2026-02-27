<template>
  <el-dialog
    v-model="visible"
    width="900px"
    :close-on-click-modal="false"
    @closed="handleClosed"
  >
    <template #header>
      <div
        style="
          display: flex;
          justify-content: space-between;
          align-items: center;
          width: 100%;
        "
      >
        <span>{{ isEdit ? "任务详情" : "创建任务" }}</span>
        <el-button
          type="text"
          size="default"
          :icon="Refresh"
          title="刷新设备列表"
          style="
            margin-right: 8px;
            padding: 0;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
          "
          @click="refreshDevices"
        />
      </div>
    </template>
    <el-form
      ref="formRef"
      v-loading="loading"
      :model="form"
      :rules="rules"
      label-width="100px"
    >
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item
            label="任务名称"
            prop="task_name"
          >
            <el-input
              v-model="form.task_name"
              placeholder="请输入任务名称"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item
            label="任务类型"
            prop="task_type"
          >
            <el-select
              v-model="form.task_type"
              placeholder="请选择任务类型"
              :disabled="isEdit"
              @change="handleTaskTypeChange"
            >
              <el-option
                label="测试用例任务"
                value="test_case"
              />
              <el-option
                label="设备脚本任务"
                value="device_script"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item
            label="优先级"
            prop="priority"
          >
            <el-select
              v-model="form.priority"
              placeholder="请选择优先级"
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
        </el-col>
        <el-col :span="24">
          <el-form-item
            label="任务目录"
            prop="folder_id"
          >
            <div class="task-folder-selector">
              <el-popover
                :visible="folderPopoverVisible"
                placement="bottom-start"
                trigger="manual"
                width="auto"
                teleport="body"
                @clickoutside="folderPopoverVisible = false"
              >
                <template #reference>
                  <div class="task-folder-input-wrap">
                    <el-input
                      v-model="selectedFolderPath"
                      placeholder="选填，不选则归入全部"
                      readonly
                      class="task-folder-input"
                      @click="handleFolderInputClick"
                    />
                    <el-button
                      size="small"
                      class="task-folder-clear-btn"
                      :icon="Refresh"
                      :title="isEdit ? '恢复为打开时的任务目录' : '清空选择'"
                      @click.stop="resetFolderSelection"
                    >
                      重置
                    </el-button>
                  </div>
                </template>
                <div class="task-folder-tree-popover">
                  <el-tree
                    :data="taskFolderTreeData"
                    :props="{ label: 'name', children: 'children' }"
                    node-key="id"
                    :current-node-key="form.folder_id || undefined"
                    highlight-current
                    class="task-folder-tree"
                    :expand-on-click-node="false"
                    @node-click="handleTaskFolderSelect"
                  >
                    <template #default="{ node, data }">
                      <span
                        class="tree-node-content"
                        :class="{ 'current-node': data.id === form.folder_id }"
                      >
                        <el-icon class="node-icon"><Folder /></el-icon>
                        <span>{{ node.label }}</span>
                      </span>
                    </template>
                  </el-tree>
                </div>
              </el-popover>
            </div>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item
            v-if="form.task_type !== 'device_script'"
            label="所属项目"
            prop="project_id"
          >
            <el-select
              v-model="form.project_id"
              placeholder="请选择项目"
              @change="handleProjectChange"
            >
              <el-option
                v-for="project in projects"
                :key="project.id"
                :label="project.project_name"
                :value="project.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item
            v-if="form.task_type !== 'device_script'"
            label="所属迭代"
            prop="iteration_id"
          >
            <el-select
              v-model="form.iteration_id"
              placeholder="请选择迭代"
              :disabled="!form.project_id"
              @change="handleIterationChange"
            >
              <el-option
                v-for="iteration in iterations"
                :key="iteration.id"
                :label="iteration.iteration_name"
                :value="iteration.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item
            v-if="form.task_type !== 'device_script'"
            label="所属需求"
            prop="version_requirement_id"
          >
            <el-select
              v-model="form.version_requirement_id"
              placeholder="请选择需求"
              :disabled="!form.iteration_id"
            >
              <el-option
                v-for="requirement in requirements"
                :key="requirement.id"
                :label="requirement.requirement_name"
                :value="requirement.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item
            label="负责人"
            prop="executor_id"
          >
            <el-select
              v-model="form.executor_id"
              placeholder="请选择任务负责人"
              clearable
            >
              <el-option
                v-for="user in users"
                :key="user.id"
                :label="user.real_name"
                :value="user.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="16">
          <el-form-item
            label="计划时间"
            prop="scheduled_time"
          >
            <el-date-picker
              v-model="form.scheduled_time"
              :type="
                form.task_type === 'device_script'
                  ? 'datetime'
                  : 'datetimerange'
              "
              :range-separator="'至'"
              :start-placeholder="'开始时间'"
              :end-placeholder="'结束时间'"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DD HH:mm:ss"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 脚本文件和设备选择 - 仅设备脚本任务显示（放在计划时间后，便于首屏可见） -->
        <template v-if="form.task_type === 'device_script'">
        <el-form-item
          label="脚本文件"
          prop="script_file"
        >
          <div class="file-input-wrapper">
            <el-input
              v-if="!isEdit"
              v-model="form.script_file"
              placeholder="请选择脚本文件"
              readonly
            />
            <!-- 任务详情（编辑）时脚本文件只读，仅支持查看/下载 -->
            <div
              v-else
              class="file-link-wrapper"
            >
              <template v-if="form.script_file">
                <a
                  class="script-file-link"
                  @click.prevent="downloadScriptFile"
                >
                  <el-icon><Download /></el-icon>
                  {{ form.script_file }}
                </a>
              </template>
              <span v-else class="no-script">无</span>
            </div>
            <el-button
              v-if="!isEdit"
              type="primary"
              @click="selectScriptFile"
            >
              选择文件
            </el-button>
          </div>
        </el-form-item>

        <el-form-item
          label="完整执行命令"
          prop="command"
        >
          <el-input
            v-model="form.command"
            type="textarea"
            :rows="4"
            :placeholder="`请输入完整执行命令，格式示例：
1. Python脚本: python -m test.py --arg1 value1 --arg2 value2
2. Shell脚本: ./test.sh arg1 arg2 arg3
3. 无参数直接运行脚本: python test.py`"
          />
        </el-form-item>

        <el-form-item
          label="执行设备"
          prop="device_ids"
          required
        >
          <el-select
            v-model="form.device_ids"
            multiple
            collapse-tags
            collapse-tags-tooltip
            placeholder="请选择执行设备（可多选，必填）"
            style="width: 100%"
            clearable
          >
            <el-option
              v-for="device in devices"
              :key="device.id"
              :label="`${device.device_id} (${device.status === 'online' ? '在线' : '离线'})`"
              :value="device.id"
              :disabled="device.status !== 'online'"
            />
          </el-select>
          <div v-if="devices.length === 0" class="form-item-hint">暂无可用设备，请先在设备管理中连接设备</div>
        </el-form-item>
      </template>

      <el-form-item
        label="任务描述"
        prop="task_description"
      >
        <el-input
          v-model="form.task_description"
          type="textarea"
          :rows="2"
          placeholder="请输入任务描述"
        />
      </el-form-item>

      <el-form-item
        label="相关文档"
        prop="documentation_url"
      >
        <el-input
          v-model="form.documentation_url"
          type="textarea"
          :rows="5"
          placeholder="请输入相关文档链接，每行一个，例如：&#10;1. 需求文档链接&#10;2. 提测文档链接&#10;3. 测试方案链接"
        />
      </el-form-item>

      <!-- 关联用例集 - 仅测试用例任务显示；编辑时不可修改/删除（创建时固定） -->
      <el-form-item
        v-if="form.task_type === 'test_case'"
        label="关联用例集"
        prop="test_cases"
      >
        <div class="suite-selector-wrapper">
          <!-- 编辑模式：只读展示，不可选择/删除 -->
          <template v-if="isEdit">
            <template v-if="taskDetail?.suite_id">
              <div class="suite-link-wrapper suite-readonly">
                <a
                  class="suite-link"
                  @click="handleSuiteClick"
                >
                  <el-icon><Link /></el-icon>
                  <span>{{ selectedSuiteName || taskDetail.suite_name || "查看用例执行（快照）" }}</span>
                </a>
              </div>
              <div class="suite-hint">
                关联用例集在创建任务时已固定，不可修改或删除
              </div>
            </template>
            <span v-else class="no-suite">未关联用例集（仅创建时可设置）</span>
          </template>
          <!-- 新建模式：可选择用例集 -->
          <template v-else>
            <template v-if="taskDetail?.suite_id">
              <div class="suite-link-wrapper">
                <a
                  class="suite-link"
                  @click="handleSuiteClick"
                >
                  <el-icon><Link /></el-icon>
                  <span>{{ selectedSuiteName || taskDetail.suite_name || "查看用例执行（快照）" }}</span>
                </a>
                <el-icon
                  class="clear-icon"
                  :size="14"
                  @click.stop="handleDeleteSuite"
                >
                  <CircleClose />
                </el-icon>
              </div>
            </template>
            <template v-else>
              <el-popover
                :visible="suitePopoverVisible"
                placement="bottom-start"
                trigger="manual"
                width="auto"
                teleport="body"
                @clickoutside="suitePopoverVisible = false"
              >
                <template #reference>
                  <el-input
                    v-model="selectedSuiteName"
                    placeholder="点击选择用例集"
                    readonly
                    @click="handleSuiteInputClick"
                  />
                </template>
                <div
                  class="suite-tree-popover"
                  style="width: 100%; min-width: 400px; max-width: 600px"
                >
                  <el-tree
                    ref="suiteTreeRef"
                    :data="suiteTree"
                    :props="{ label: 'suite_name', children: 'children' }"
                    node-key="id"
                    :current-node-key="form.test_cases"
                    :expand-on-click-node="false"
                    :filter-node-method="filterSuiteType"
                    style="
                      max-height: 300px;
                      overflow-y: auto;
                      width: 100%;
                      padding-right: 10px;
                    "
                    @node-click="handleSuiteSelect"
                  >
                    <template #default="{ node, data }">
                      <span class="tree-node-content">
                        <el-icon
                          class="node-icon"
                          :class="{ 'folder-icon': data.type === 'folder' }"
                        >
                          <Folder v-if="data.type === 'folder'" />
                          <Document v-else />
                        </el-icon>
                        <span class="node-label">{{ node.label }}</span>
                        <span
                          v-if="data.type === 'suite' && data.cases_count > 0"
                          class="case-count"
                        >
                          ({{ data.cases_count }})
                        </span>
                      </span>
                    </template>
                  </el-tree>
                </div>
              </el-popover>
            </template>
          </template>
        </div>
      </el-form-item>

      <el-row
        v-if="isEdit"
        :gutter="20"
      >
        <el-col :span="8">
          <el-form-item label="任务状态">
            <el-tag :type="getStatusType(taskDetail?.status)">
              {{ getStatusText(taskDetail?.status) }}
            </el-tag>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="创建者">
            <el-tag
              type="info"
              size="default"
            >
              {{ taskDetail?.creator_name || "-" }}
            </el-tag>
          </el-form-item>
        </el-col>
      </el-row>

      <el-divider
        v-if="isEdit && taskDetail?.statistics"
        content-position="left"
      >
        执行统计
      </el-divider>
      <div
        v-if="isEdit && taskDetail?.statistics"
        class="stats-detail-section"
      >
        <div class="stats-header">
          <div class="stats-rate">
            <span class="stats-label">通过率:</span>
            <span
              class="stats-percentage"
              :style="{
                color: getProgressColor(taskDetail.statistics.pass_rate),
              }"
            >
              {{ taskDetail.statistics.pass_rate }}%
            </span>
          </div>
          <span class="stats-total">总数: {{ taskDetail.test_case_count }}</span>
        </div>
        <el-progress
          :percentage="taskDetail.statistics.pass_rate"
          :color="getProgressColor(taskDetail.statistics.pass_rate)"
          :stroke-width="6"
          :show-text="false"
        />
        <div class="stats-detail">
          <div class="stats-item pass">
            <span class="item-label">通过</span>
            <span class="item-value">{{
              taskDetail.statistics.pass_count
            }}</span>
          </div>
          <div class="stats-item fail">
            <span class="item-label">失败</span>
            <span class="item-value">{{
              taskDetail.statistics.fail_count
            }}</span>
          </div>
          <div class="stats-item blocked">
            <span class="item-label">阻塞</span>
            <span class="item-value">{{
              taskDetail.statistics.blocked_count
            }}</span>
          </div>
          <div class="stats-item not-executed">
            <span class="item-label">未执行</span>
            <span class="item-value">{{
              taskDetail.statistics.not_executed
            }}</span>
          </div>
        </div>
      </div>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">
        {{ isEdit ? "关闭" : "取消" }}
      </el-button>
      <el-button
        v-if="isEdit && form.task_type === 'device_script'"
        type="success"
        @click="goToDeviceScriptExecution"
      >
        <el-icon><View /></el-icon>
        查看执行情况
      </el-button>
      <el-button
        v-if="!isEdit"
        type="primary"
        :loading="submitting"
        @click="handleSubmit"
      >
        创建
      </el-button>
      <el-button
        v-if="isEdit"
        type="primary"
        :loading="submitting"
        @click="handleUpdate"
      >
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from "vue";
import { ElMessage } from "element-plus";
import {
  Folder,
  Document,
  Link,
  CircleClose,
  Refresh,
  Download,
  View,
} from "@element-plus/icons-vue";
import { useRouter } from "vue-router";
import testTaskApi from "@/api/testTask";
import projectApi from "@/api/project";
import {
  getIterations,
  getProjectIterations,
  getIterationRequirements,
} from "@/api/iteration";
import { getTestSuiteList, getTestSuiteTree } from "@/api/testSuite";
import { getProjectVersionRequirements } from "@/api/project";
import * as testCaseApi from "@/api/testCase";
import { getUserList } from "@/api/user";
import deviceApi from "@/api/device";
import { uploadFile } from "@/api/files";

const emit = defineEmits(["refresh"]);
const router = useRouter();

const visible = ref(false);
const loading = ref(false);
const submitting = ref(false);
const isEdit = ref(false);
const formRef = ref(null);
const suiteTreeRef = ref(null);
const taskId = ref(null);
const taskDetail = ref(null);
const executions = ref([]);

const projects = ref([]);
const iterations = ref([]);
const requirements = ref([]);
const suiteTree = ref([]);
const suitePopoverVisible = ref(false);
const selectedSuiteName = ref("");
const users = ref([]);
const folderOptions = ref([]);
// 任务目录选择（树形）
const folderPopoverVisible = ref(false);
const selectedFolderPath = ref("");
const taskFolderTreeData = ref([]);
const taskFolderTreeRaw = ref([]);
/** 编辑时打开弹窗时的任务目录原值，用于「重置」恢复 */
const initialFolderId = ref(null);
const initialFolderPath = ref("");

const form = reactive({
  task_name: "",
  task_description: "",
  task_type: "test_case",
  folder_id: null,
  project_id: "",
  version_requirement_id: "",
  iteration_id: "",
  priority: "medium",
  documentation_url: "",
  scheduled_time: "",
  test_cases: "",
  // 设备脚本任务专用字段
  script_file: "",
  file_path: "",
  file_hash: "",
  command: "",
  device_ids: [],
});

// 设备列表
const devices = ref([]);

const rules = {
  task_name: [{ required: true, message: "请输入任务名称", trigger: "blur" }],
  task_type: [{ required: true, message: "请选择任务类型", trigger: "change" }],
  project_id: [],
  priority: [{ required: true, message: "请选择优先级", trigger: "change" }],
  // 设备脚本任务验证规则（编辑时脚本文件为只读展示，不做必填校验）
  script_file: [
    {
      trigger: "change",
      validator: (rule, value, callback) => {
        if (form.task_type !== "device_script") {
          callback();
          return;
        }
        if (isEdit.value) {
          callback();
          return;
        }
        if (!value) {
          callback(new Error("请选择脚本文件"));
        } else {
          callback();
        }
      },
    },
  ],
  device_ids: [
    {
      required: true,
      message: "请选择执行设备",
      trigger: "change",
      validator: (rule, value, callback) => {
        if (
          form.task_type === "device_script" &&
          (!value || value.length === 0)
        ) {
          callback(new Error("请选择至少一个执行设备"));
        } else {
          callback();
        }
      },
    },
  ],
};

const getStatusType = (status) => {
  const typeMap = {
    pending: "info",
    running: "warning",
    paused: "warning",
    completed: "success",
  };
  return typeMap[status] || "info";
};

const getStatusText = (status) => {
  const textMap = {
    pending: "待执行",
    running: "执行中",
    paused: "已暂停",
    completed: "已完成",
  };
  return textMap[status] || status;
};

const getProgressColor = (percentage) => {
  if (percentage >= 80) return "#67c23a";
  if (percentage >= 60) return "#e6a23c";
  return "#f56c6c";
};

const getExecutionStatusType = (status) => {
  const typeMap = {
    pass: "success",
    fail: "danger",
    blocked: "warning",
    not_applicable: "info",
  };
  return typeMap[status] || "info";
};

const getExecutionStatusText = (status) => {
  const textMap = {
    pass: "通过",
    fail: "失败",
    blocked: "阻塞",
    not_applicable: "不适用",
  };
  return textMap[status] || status;
};

const formatDate = (dateString) => {
  if (!dateString) return "-";
  const date = new Date(dateString);
  return date.toLocaleString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const loadProjects = async () => {
  try {
    const response = await projectApi.getProjects({ page: 1, size: 10000 });
    projects.value = response.data?.items || response.data?.projects || [];
  } catch (error) {
    console.error("加载项目列表失败:", error);
  }
};

const loadUsers = async () => {
  try {
    const response = await getUserList({ page: 1, size: 1000 });
    users.value = response.data?.users || [];
  } catch (error) {
    console.error("加载用户列表失败:", error);
  }
};

// 加载设备列表
const loadDevices = async () => {
  try {
    const response = await deviceApi.getDeviceList();
    devices.value = response.data?.devices || response.data || [];
  } catch (error) {
    console.error("加载设备列表失败:", error);
  }
};

// 选择脚本文件
const selectedFile = ref(null);

const selectScriptFile = () => {
  const input = document.createElement("input");
  input.type = "file";
  input.accept = ".py,.sh";

  input.onchange = (e) => {
    const file = e.target.files[0];
    if (file) {
      selectedFile.value = file;
      form.script_file = file.name;
      ElMessage.success(`已选择脚本文件: ${file.name}`);
    }
  };

  input.click();
};

// 删除脚本文件
const handleDeleteScriptFile = () => {
  form.script_file = "";
  form.file_path = "";
  form.file_hash = "";
  selectedFile.value = null;
  ElMessage.success("已删除脚本文件");
};

const loadIterations = async () => {
  if (!form.project_id) {
    iterations.value = [];
    return;
  }
  try {
    const response = await getProjectIterations(form.project_id, {
      page: 1,
      size: 1000,
    });
    iterations.value = response.data?.items || response.data?.iterations || [];
  } catch (error) {
    console.error("加载迭代列表失败:", error);
  }
};

const loadRequirements = async () => {
  if (!form.iteration_id) {
    requirements.value = [];
    return;
  }
  try {
    const response = await getIterationRequirements(form.iteration_id);
    requirements.value = response.data?.items || [];
  } catch (error) {
    console.error("加载需求列表失败:", error);
  }
};

const loadSuites = async () => {
  try {
    const response = await getTestSuiteTree();
    suiteTree.value = response.data || [];

  } catch (error) {
    console.error("加载测试套件树失败:", error);
  }
};

const filterSuiteType = (value, data) => {
  return true;
};

const findSuiteById = (suites, id) => {
  for (const suite of suites) {
    if (suite.id === id) {
      return suite;
    }
    if (suite.children && suite.children.length > 0) {
      const found = findSuiteById(suite.children, id);
      if (found) {
        return found;
      }
    }
  }
  return null;
};

/** 在树中根据 suiteId 查找并返回从根到该节点的路径字符串（如 "文件夹1 / 文件夹2 / 用例集名"） */
const findSuitePathInTree = (nodes, suiteId, parentPath = []) => {
  if (!nodes || !Array.isArray(nodes)) return null;
  for (const n of nodes) {
    const name = n.suite_name ?? n.label ?? "";
    const currentPath = [...parentPath, name];
    if (n.id === suiteId) return currentPath.join(" / ");
    if (n.children?.length) {
      const found = findSuitePathInTree(n.children, suiteId, currentPath);
      if (found) return found;
    }
  }
  return null;
};

const handleSuiteSelect = async (data, node) => {
  if (data.type !== "suite") {
    node.expanded = !node.expanded;
    return;
  }

  form.test_cases = data.id;
  // 显示用例集存放路径：从根到当前节点的名称用 " / " 拼接
  const pathParts = [];
  let p = node;
  while (p) {
    pathParts.unshift(p.label);
    p = p.parent;
  }
  selectedSuiteName.value = pathParts.length ? pathParts.join(" / ") : data.suite_name;
  suitePopoverVisible.value = false;

  // 编辑已有任务时通过接口更新关联；新建任务时仅更新表单，提交时一并带上 suite_id
  if (taskId.value) {
    try {
      await testTaskApi.updateTestTask(taskId.value, { suite_id: data.id });
      ElMessage.success("关联用例集成功");
      await loadTaskDetail();
    } catch (error) {
      console.error("关联用例集失败:", error);
      ElMessage.error(
        "关联用例集失败：" +
          (error.response?.data?.message || error.message || "未知错误"),
      );
    }
  } else {
    ElMessage.success("已选择用例集，保存任务后将生效");
  }
};

const handleSuiteInputClick = () => {
  if (suiteTree.value.length === 0) {
    loadSuites();
  }
  suitePopoverVisible.value = !suitePopoverVisible.value;
};

const handleDeleteSuite = async () => {
  form.test_cases = "";
  selectedSuiteName.value = "";

  if (taskId.value) {
    try {
      await testTaskApi.updateTestTask(taskId.value, { suite_id: null });
      ElMessage.success("已删除关联的用例集");
      await loadTaskDetail();
    } catch (error) {
      console.error("删除用例集失败:", error);
      ElMessage.error(
        "删除用例集失败：" +
          (error.response?.data?.message || error.message || "未知错误"),
      );
    }
  } else {
    ElMessage.success("已取消选择用例集");
  }
};

// 点击关联用例集：在新标签页打开用例执行页（展示快照数据）；若任务已完成则不显示「完成任务」按钮
const handleSuiteClick = () => {
  if (!taskId.value) return;
  handleClose();
  const base = `${window.location.origin}/test-tasks/${taskId.value}/execute`;
  const isCompleted = taskDetail.value?.status === "completed";
  const url = isCompleted ? `${base}?hideComplete=1` : base;
  window.open(url, "_blank");
};

const loadTaskDetail = async () => {
  loading.value = true;
  try {
    const response = await testTaskApi.getTestTaskDetail(taskId.value);
    taskDetail.value = response.data.test_task;

    // 处理时间范围：将开始和结束时间组合成数组
    const scheduledTimeArray = [];
    if (taskDetail.value.scheduled_time) {
      scheduledTimeArray.push(taskDetail.value.scheduled_time);
    }
    if (taskDetail.value.scheduled_end_time) {
      scheduledTimeArray.push(taskDetail.value.scheduled_end_time);
    }

    Object.assign(form, {
      task_name: taskDetail.value.task_name,
      task_description: taskDetail.value.task_description,
      task_type: taskDetail.value.task_type,
      folder_id: taskDetail.value.folder_id ?? null,
      project_id: taskDetail.value.project_id,
      version_requirement_id: taskDetail.value.version_requirement_id,
      iteration_id: taskDetail.value.iteration_id,
      priority: taskDetail.value.priority,
      documentation_url: taskDetail.value.documentation_url,
      scheduled_time: scheduledTimeArray.length > 0 ? scheduledTimeArray : "",
      test_cases: taskDetail.value.suite_id || "",
      executor_id: taskDetail.value.executor_id,
      // 设备脚本任务专用字段
      script_file: taskDetail.value.script_file || "",
      file_path: taskDetail.value.file_path || "",
      file_hash: taskDetail.value.file_hash || "",
      command: taskDetail.value.command || "",
      device_ids: taskDetail.value.devices?.map((device) => device.id) || [],
    });

    if (taskDetail.value.suite_id) {
      if (suiteTree.value.length === 0) {
        await loadSuites();
      }
      const path = findSuitePathInTree(
        suiteTree.value,
        taskDetail.value.suite_id,
      );
      selectedSuiteName.value =
        path || taskDetail.value.suite_name || "";
    }

    await loadProjects();
    await loadUsers();
    await loadRequirements();
    await loadIterations();
    await loadSuites();
    await loadDevices();
    await loadFolderOptions(taskDetail.value.task_type);
    initialFolderId.value = form.folder_id ?? null;
    initialFolderPath.value = selectedFolderPath.value || "全部";
  } catch (error) {
    console.error("加载任务详情失败:", error);
    // 若用户已在加载完成前关闭弹窗，不再提示，避免误报
    if (visible.value) {
      ElMessage.error("加载任务详情失败");
    }
  } finally {
    loading.value = false;
  }
};

const loadExecutions = async () => {
  try {
    const response = await testTaskApi.getTaskExecutions(taskId.value);
    executions.value = response.data;
  } catch (error) {
    console.error("加载执行记录失败:", error);
  }
};

const handleTaskTypeChange = () => {
  if (form.task_type === "device_script") {
    form.test_cases = "";
    selectedSuiteName.value = "";
  }
  // 切换任务类型时不清空已选执行设备，避免误清空
  loadTaskFolderTree(form.task_type);
};

function flattenFolderTree(nodes, depth = 0) {
  const list = [];
  if (!nodes || !nodes.length) return list;
  const indent = "　".repeat(depth);
  for (const n of nodes) {
    if (n.id && n.id !== "__all__") {
      list.push({ id: n.id, label: indent + (n.name || "未命名") });
    }
    if (n.children?.length) {
      list.push(...flattenFolderTree(n.children, depth + 1));
    }
  }
  return list;
}

/** 在任务目录树中根据 folderId 查找从根到该节点的路径名称（用于显示） */
function findTaskFolderPath(nodes, folderId, parentPath = []) {
  if (!nodes || !Array.isArray(nodes)) return null;
  if (folderId == null || folderId === "" || folderId === "__none__") return null;
  for (const n of nodes) {
    const name = n.name || "未命名";
    const currentPath = [...parentPath, name];
    if (n.id === folderId) return currentPath.join(" / ");
    if (n.children?.length) {
      const found = findTaskFolderPath(n.children, folderId, currentPath);
      if (found) return found;
    }
  }
  return null;
}

const loadTaskFolderTree = async (taskType) => {
  if (!taskType) {
    taskFolderTreeRaw.value = [];
    taskFolderTreeData.value = [];
    return;
  }
  try {
    const res = await testTaskApi.getTaskFolderTree(taskType);
    const roots = res.data?.folders ?? [];
    taskFolderTreeRaw.value = roots;
    taskFolderTreeData.value = roots;
    folderOptions.value = flattenFolderTree(roots);
    updateSelectedFolderPath();
  } catch (e) {
    console.error("加载任务目录失败", e);
    taskFolderTreeRaw.value = [];
    taskFolderTreeData.value = [];
    folderOptions.value = [];
  }
};

const updateSelectedFolderPath = () => {
  if (form.folder_id == null || form.folder_id === "") {
    selectedFolderPath.value = "全部";
    return;
  }
  const path = findTaskFolderPath(taskFolderTreeRaw.value, form.folder_id);
  selectedFolderPath.value = path || "未命名";
};

const handleFolderInputClick = () => {
  if (taskFolderTreeData.value.length === 0 && form.task_type) {
    loadTaskFolderTree(form.task_type);
  }
  folderPopoverVisible.value = !folderPopoverVisible.value;
};

const handleTaskFolderSelect = (data) => {
  form.folder_id = data.id;
  const path = findTaskFolderPath(taskFolderTreeRaw.value, data.id);
  selectedFolderPath.value = path || data.name || "未命名";
  folderPopoverVisible.value = false;
};

/** 任务目录：编辑时为恢复原值，创建时为清空（清空后显示「全部」） */
const resetFolderSelection = () => {
  if (isEdit.value) {
    form.folder_id = initialFolderId.value;
    selectedFolderPath.value = initialFolderPath.value || "全部";
  } else {
    form.folder_id = null;
    selectedFolderPath.value = "全部";
  }
  folderPopoverVisible.value = false;
};

/** 兼容旧逻辑：仍提供扁平列表给可能依赖 folderOptions 的代码 */
const loadFolderOptions = async (taskType) => {
  await loadTaskFolderTree(taskType);
};

const handleProjectChange = () => {
  form.version_requirement_id = "";
  form.iteration_id = "";
  form.test_cases = "";
  selectedSuiteName.value = "";
  loadRequirements();
  loadIterations();
};

const handleIterationChange = () => {
  form.version_requirement_id = "";
  loadRequirements();
};

const handleSubmit = async () => {
  try {
    await formRef.value.validate();

    submitting.value = true;

    // 处理表单数据，根据任务类型处理时间字段
    const submitData = { ...form };

    // 处理空字符串字段，将其转换为null或删除
    if (!submitData.project_id || submitData.project_id === "") {
      delete submitData.project_id;
    }
    if (
      !submitData.version_requirement_id ||
      submitData.version_requirement_id === ""
    ) {
      delete submitData.version_requirement_id;
    }
    if (!submitData.iteration_id || submitData.iteration_id === "") {
      delete submitData.iteration_id;
    }
    if (!submitData.test_cases || submitData.test_cases === "") {
      delete submitData.test_cases;
    }
    if (submitData.folder_id == null || submitData.folder_id === "") {
      delete submitData.folder_id;
    }
    if (!submitData.command || submitData.command === "") {
      delete submitData.command;
    }

    // 处理设备脚本任务的文件字段
    if (form.task_type === "device_script") {
      // 设备脚本任务：只需要开始时间
      if (submitData.scheduled_time) {
        // 直接使用单个时间值
      } else {
        delete submitData.scheduled_time;
      }

      // 确保设备ID字段名正确
      if (submitData.device_ids && submitData.device_ids.length > 0) {
        submitData.devices = submitData.device_ids;
      } else {
        submitData.devices = [];
      }
      delete submitData.device_ids;

      // 如果有选中的文件，上传文件到服务器
      if (selectedFile.value) {
        try {
          const response = await uploadFile(selectedFile.value);
          const fileData = response.data;

          // 更新提交数据中的文件信息
          submitData.script_file = fileData.filename;
          submitData.file_path = fileData.file_path;
          submitData.file_hash = fileData.file_hash;
        } catch (error) {
          console.error("文件上传失败:", error);
          ElMessage.error(`文件上传失败: ${error.message || "未知错误"}`);
          submitting.value = false;
          return;
        }
      }
    } else {
      // 测试用例任务：需要开始时间和结束时间
      if (submitData.scheduled_time && submitData.scheduled_time.length === 2) {
        // 将数组转换为开始时间和结束时间
        const [startTime, endTime] = submitData.scheduled_time;
        submitData.scheduled_time = startTime;
        submitData.scheduled_end_time = endTime;
      } else {
        delete submitData.scheduled_time;
      }

      // 非设备脚本任务，删除设备和文件相关字段
      delete submitData.device_ids;
      delete submitData.script_file;
      delete submitData.file_path;
      delete submitData.file_hash;
    }



    await testTaskApi.createTestTask(submitData);

    ElMessage.success("测试任务创建成功");
    handleClose();
    emit("refresh");
  } catch (error) {
    if (error !== false && error.response) {
      console.error("创建测试任务失败:", error);
      ElMessage.error(
        "创建测试任务失败：" +
          (error.response?.data?.message || error.message || "未知错误"),
      );
    }
  } finally {
    submitting.value = false;
  }
};

const handleUpdate = async () => {
  try {
    await formRef.value.validate();

    submitting.value = true;



    // 只发送需要更新的字段，避免发送空字符串导致验证错误
    const updateData = {
      task_name: form.task_name,
      task_description: form.task_description,
      task_type: form.task_type,
      priority: form.priority,
      documentation_url: form.documentation_url,
      executor_id: form.executor_id,
    };
    if (form.folder_id != null && form.folder_id !== "") {
      updateData.folder_id = form.folder_id;
    } else {
      updateData.folder_id = null;
    }

    // 处理可选字段，只有非空时才添加到updateData
    if (form.project_id && form.project_id !== "") {
      updateData.project_id = form.project_id;
    }
    if (form.version_requirement_id && form.version_requirement_id !== "") {
      updateData.version_requirement_id = form.version_requirement_id;
    }
    if (form.iteration_id && form.iteration_id !== "") {
      updateData.iteration_id = form.iteration_id;
    }

    // 处理时间字段
    if (form.task_type === "device_script") {
      // 设备脚本任务：只需要开始时间（详情加载后可能是单元素数组）
      if (form.scheduled_time) {
        updateData.scheduled_time = Array.isArray(form.scheduled_time)
          ? form.scheduled_time[0]
          : form.scheduled_time;
      }
    } else {
      // 测试用例任务：需要开始时间和结束时间
      if (form.scheduled_time && form.scheduled_time.length === 2) {
        updateData.scheduled_time = form.scheduled_time[0];
        updateData.scheduled_end_time = form.scheduled_time[1];
      }
    }

    // 根据任务类型添加不同的字段
    if (form.task_type === "test_case") {
      // 仅新建时提交用例集；编辑时关联用例集不可修改，不传 suite_id
      if (!isEdit.value && form.test_cases && form.test_cases !== "") {
        updateData.suite_id = form.test_cases;
      }

      // 非设备脚本任务，清空设备和文件相关字段
      updateData.devices = [];
      updateData.script_file = null;
      updateData.file_path = null;
      updateData.file_hash = null;
      updateData.command = null;
    } else if (form.task_type === "device_script") {
      // 设备脚本任务专用字段
      if (form.script_file && form.script_file !== "") {
        updateData.script_file = form.script_file;
      }
      if (form.file_path && form.file_path !== "") {
        updateData.file_path = form.file_path;
      }
      if (form.file_hash && form.file_hash !== "") {
        updateData.file_hash = form.file_hash;
      }
      if (form.command && form.command !== "") {
        updateData.command = form.command;
      }
      if (form.device_ids && form.device_ids.length > 0) {
        updateData.devices = form.device_ids;
      } else {
        updateData.devices = [];
      }

      // 设备脚本任务，清空用例集关联
      updateData.suite_id = null;
    }

    await testTaskApi.updateTestTask(taskId.value, updateData);

    ElMessage.success("测试任务更新成功");

    // 编辑模式下，更新后重新加载任务详情而不是关闭对话框
    if (isEdit.value) {
      await loadTaskDetail();
    } else {
      handleClose();
    }

    emit("refresh");
  } catch (error) {
    // 表单校验失败时 error 可能无 response，需单独提示
    if (error === false || (error && !error.response)) {
      ElMessage.warning("请检查表单必填项与填写格式");
      return;
    }
    if (error?.response) {
      console.error("更新测试任务失败:", error);
      ElMessage.error(
        "更新测试任务失败：" +
          (error.response?.data?.message || error.message || "未知错误"),
      );
    }
  } finally {
    submitting.value = false;
  }
};

/** 设备脚本任务详情：跳转到设备脚本执行页 */
const goToDeviceScriptExecution = () => {
  if (!taskId.value) return;
  visible.value = false;
  router.push({ name: "DeviceScriptExecution", params: { id: taskId.value } });
};

const handleClose = () => {
  visible.value = false;
};

const handleClosed = () => {
  formRef.value?.resetFields();
  Object.assign(form, {
    task_name: "",
    task_description: "",
    task_type: "test_case",
    folder_id: null,
    project_id: "",
    version_requirement_id: "",
    iteration_id: "",
    priority: "medium",
    documentation_url: "",
    scheduled_time: "",
    test_cases: "",
    script_file: "",
    file_path: "",
    file_hash: "",
    command: "",
    device_ids: [],
  });
  isEdit.value = false;
  taskId.value = null;
  taskDetail.value = null;
  executions.value = [];
  iterations.value = [];
  requirements.value = [];
  suiteTree.value = [];
  selectedSuiteName.value = "";
  suitePopoverVisible.value = false;
  selectedFolderPath.value = "";
  folderPopoverVisible.value = false;
  taskFolderTreeData.value = [];
  initialFolderId.value = null;
  initialFolderPath.value = "";

  // 关闭对话框时刷新列表
  emit("refresh");
};

const open = (id = null, options = {}) => {
  visible.value = true;

  if (id) {
    isEdit.value = true;
    taskId.value = id;
    loadTaskDetail();
  } else {
    isEdit.value = false;
    if (options.folder_id != null && options.folder_id !== "") {
      form.folder_id = options.folder_id;
    } else {
      form.folder_id = null;
    }
    if (options.task_type) {
      form.task_type = options.task_type;
    }
    loadFolderOptions(form.task_type);
    loadProjects();
    loadUsers();
    loadSuites();
    loadDevices();
  }
};

// 刷新页面数据
const refreshDevices = async () => {
  // 加载项目列表
  await loadProjects();

  // 加载用户列表
  await loadUsers();

  // 加载测试套件树
  await loadSuites();

  // 加载设备列表
  await loadDevices();

  // 如果有选择项目，加载迭代列表
  if (form.project_id) {
    await loadIterations();

    // 如果有选择迭代，加载需求列表
    if (form.iteration_id) {
      await loadRequirements();
    }
  }

  ElMessage.success("页面数据已刷新");
};

// 下载脚本文件
const downloadScriptFile = () => {
  if (form.file_path) {
    // 构建完整的下载URL，包含原始文件名作为查询参数
    const downloadUrl = `/api/files/${form.file_path}?filename=${encodeURIComponent(form.script_file || "script_file")}`;


    // 创建下载链接并触发下载
    const a = document.createElement("a");
    a.href = downloadUrl;
    a.download = form.script_file || "script_file";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  } else {
    ElMessage.warning("脚本文件路径不存在");
  }
};

defineExpose({
  open,
});
</script>

<style lang="scss" scoped>
:deep(.el-dialog__body) {
  max-height: 70vh;
  overflow-y: auto;
}

:deep(.el-statistic) {
  text-align: center;
}

:deep(.el-statistic__head) {
  font-size: 14px;
  color: #909399;
}

:deep(.el-statistic__content) {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.suite-selector-wrapper {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
}

.suite-link-wrapper {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.suite-link-wrapper.suite-readonly {
  margin-right: 0;
}

.suite-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 6px;
}

.form-item-hint {
  font-size: 12px;
  color: var(--el-color-warning);
  margin-top: 4px;
}


.task-folder-selector {
  width: 100%;
}

.task-folder-input-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.task-folder-input {
  flex: 1;
  min-width: 360px;
}

.task-folder-clear-btn {
  height: 32px;
  flex-shrink: 0;
}

.task-folder-tree-popover {
  width: 360px;
  padding: 4px 0;

  .task-folder-tree {
    max-height: 320px;
    overflow-y: auto;
  }
}

.clear-icon {
  position: absolute;
  right: -20px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  color: #909399;
  transition: color 0.3s;
  padding: 2px;

  &:hover {
    color: #f56c6c;
  }
}

.suite-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #409eff;
  cursor: pointer;
  text-decoration: none;
  transition: color 0.3s;
  font-size: 14px;
  padding: 5px 12px;
  background-color: #ecf5ff;
  border-radius: 4px;
  border: 1px solid #b3d8ff;
  line-height: 1.5;
}

.suite-link:hover {
  color: #66b1ff;
  background-color: #d9ecff;
  border-color: #a0cfff;
}

.suite-link .el-icon {
  font-size: 14px;
}

.suite-tree-popover {
  padding: 10px;
}

.tree-node-content {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.node-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.folder-icon {
  opacity: 0.5;
}

.node-label {
  flex: 1;
}

.case-count {
  color: #909399;
  font-size: 12px;
  margin-left: 4px;
}

.no-suite {
  color: #909399;
  font-size: 14px;
  padding: 5px 12px;
  line-height: 1.5;
}

.file-input-wrapper {
  display: flex;
  gap: 10px;
  width: 100%;

  .el-input {
    flex: 1;
  }
}

.file-link-wrapper {
  display: flex;
  gap: 10px;
  align-items: center;
}

.script-file-link {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #409eff;
  cursor: pointer;
  text-decoration: underline;
  font-size: 14px;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.3s;

  &:hover {
    color: #66b1ff;
    background-color: #ecf5ff;
  }
}

.stats-detail-section {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 20px;
}

.stats-detail-section .stats-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  font-size: 14px;
}

.stats-detail-section .stats-rate {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stats-detail-section .stats-label {
  color: #606266;
  font-weight: 500;
}

.stats-detail-section .stats-percentage {
  font-size: 20px;
  font-weight: 700;
}

.stats-detail-section .stats-total {
  color: #409eff;
  font-weight: 600;
}

.stats-detail-section .stats-detail {
  display: flex;
  justify-content: space-around;
  margin-top: 15px;
  gap: 16px;
}

.stats-detail-section .stats-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  flex: 1;
  padding: 12px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.stats-detail-section .item-label {
  color: #909399;
  font-size: 13px;
}

.stats-detail-section .item-value {
  font-size: 24px;
  font-weight: 700;
}

.stats-detail-section .stats-item.pass .item-value {
  color: #67c23a;
}

.stats-detail-section .stats-item.fail .item-value {
  color: #f56c6c;
}

.stats-detail-section .stats-item.blocked .item-value {
  color: #e6a23c;
}

.stats-detail-section .stats-item.not-executed .item-value {
  color: #909399;
}
</style>
