<template>
  <div class="test-task-management">
    <div class="main-layout" :class="{ 'left-collapsed': isLeftPanelCollapsed }">
      <!-- 左侧：任务类型下拉 + 任务文件夹树 -->
      <div class="left-panel" :class="{ collapsed: isLeftPanelCollapsed }">
        <div class="panel-header">
          <span class="panel-title">任务目录</span>
          <div class="header-actions">
            <el-button
              type="primary"
              size="small"
              circle
              title="新建文件夹"
              @click="handleAddFolder"
            >
              <el-icon><Plus /></el-icon>
            </el-button>
            <el-button
              size="small"
              circle
              :icon="isLeftPanelCollapsed ? 'ArrowRight' : 'ArrowLeft'"
              :title="isLeftPanelCollapsed ? '展开目录' : '收起目录'"
              @click="toggleLeftPanel"
            />
          </div>
        </div>
        <div class="task-type-select-wrap">
          <el-select
            v-model="activeTab"
            class="task-type-select"
            placeholder="选择任务类型"
            @change="handleTaskTypeChange"
          >
            <el-option label="测试用例任务" value="test_case" />
            <el-option label="设备脚本任务" value="device_script" />
          </el-select>
        </div>
        <div ref="folderTreeWrapRef" class="folder-tree-wrap">
          <div class="folder-tree-inner">
          <el-tree
            ref="folderTreeRef"
            :key="'folder-tree-' + taskFolderMountKey"
            :data="folderTreeData"
            :props="{ label: 'name', children: 'children' }"
            node-key="id"
            :current-node-key="selectedFolderId === null ? '__all__' : selectedFolderId"
            highlight-current
            :default-expanded-keys="taskFolderExpandedKeys"
            :draggable="true"
            :allow-drop="allowFolderDrop"
            :allow-drag="allowFolderDrag"
            @node-click="(data, node, ev) => handleFolderClick(data, ev?.target?.closest?.('.el-tree-node') ?? node?.$el)"
            @node-expand="handleFolderNodeExpand"
            @node-collapse="handleFolderNodeCollapse"
            @node-contextmenu="handleFolderContextMenu"
            @node-drop="handleFolderNodeDrop"
          >
            <template #default="{ node, data }">
              <span class="folder-tree-node" :data-folder-id="data.id">
                <el-icon v-if="data.id === '__all__'"><FolderOpened /></el-icon>
                <el-icon v-else><Folder /></el-icon>
                <span
                  v-if="data.id === '__all__' || (editingFolderId !== data.id)"
                  class="node-label"
                  @dblclick.stop="data.id !== '__all__' && startFolderRename(data)"
                >
                  {{ node.label }}
                </span>
                <el-input
                  v-else
                  ref="folderEditInputRef"
                  v-model="editingFolderName"
                  size="small"
                  class="folder-rename-input"
                  @blur="saveFolderRename(data)"
                  @keyup.enter="saveFolderRename(data)"
                  @keyup.esc="cancelFolderRename"
                />
              </span>
            </template>
          </el-tree>
          </div>
        </div>
        <!-- 右键菜单 -->
        <div
          v-show="folderContextMenuVisible"
          ref="folderContextMenuRef"
          :style="folderContextMenuStyle"
          class="context-menu"
        >
          <div class="menu-item" @click="handleAddSubFolderFromMenu">
            <el-icon><Plus /></el-icon> 新建子文件夹
          </div>
          <div
            v-if="contextMenuFolderId && contextMenuFolderId !== '__all__'"
            class="menu-item"
            @click="handleDeleteFolderFromMenu"
          >
            <el-icon><Delete /></el-icon> 删除文件夹
          </div>
        </div>
      </div>

      <!-- 右侧：列表工具栏 + 筛选 + 任务列表 -->
      <div class="right-content">
        <div class="list-toolbar">
          <div class="toolbar-left">
            <el-input
              v-model="filterForm.search"
              placeholder="搜索任务名称/描述"
              clearable
              style="width: 200px"
              @clear="handleSearch"
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-select
              v-model="filterForm.status"
              placeholder="状态"
              clearable
              style="width: 110px"
              @change="handleSearch"
            >
              <el-option label="待执行" value="pending" />
              <el-option label="执行中" value="running" />
              <el-option label="已暂停" value="paused" />
              <el-option label="已完成" value="completed" />
            </el-select>
            <el-select
              v-model="filterForm.priority"
              placeholder="优先级"
              clearable
              style="width: 100px"
              @change="handleSearch"
            >
              <el-option label="高" value="high" />
              <el-option label="中" value="medium" />
              <el-option label="低" value="low" />
            </el-select>
            <el-select
              v-model="filterForm.executor_id"
              placeholder="负责人"
              clearable
              filterable
              style="width: 120px"
              @change="handleSearch"
            >
              <el-option
                v-for="u in userOptions"
                :key="u.id"
                :label="u.real_name"
                :value="u.id"
              />
            </el-select>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="handleReset">重置</el-button>
          </div>
          <div class="toolbar-right">
            <el-button
              circle
              title="刷新列表"
              @click="loadTasks"
            >
              <el-icon><Refresh /></el-icon>
            </el-button>
            <el-button type="primary" @click="handleCreate">
              <el-icon><Plus /></el-icon>
              创建任务
            </el-button>
          </div>
        </div>

    <!-- 任务列表：仅由左侧任务类型下拉控制，无类型 Tab -->
    <div class="task-tabs-section">
      <div class="table-section">
        <div class="table-scroll-viewport">
          <el-table
            v-loading="currentLoading"
            :data="currentTaskList"
            stripe
            border
            style="width: 100%"
            fit
          >
            <el-table-column
              prop="task_name"
              label="任务名称"
              min-width="200"
              show-overflow-tooltip
              align="center"
            />
            <el-table-column
              prop="executor_name"
              label="负责人"
              min-width="100"
              show-overflow-tooltip
              align="center"
            >
              <template #default="{ row }">
                {{ row.executor_name || "-" }}
              </template>
            </el-table-column>
            <el-table-column
              prop="priority"
              label="优先级"
              min-width="70"
              align="center"
            >
              <template #default="{ row }">
                <el-tag :type="getPriorityType(row.priority)" size="small">
                  {{ getPriorityText(row.priority) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column
              prop="status"
              label="状态"
              min-width="80"
              align="center"
            >
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <!-- 测试用例任务：统计列 -->
            <el-table-column
              v-if="activeTab === 'test_case'"
              label="统计"
              min-width="230"
              align="center"
            >
              <template #default="{ row }">
                <div v-if="row.statistics" class="stats-mini">
                  <div class="stats-header">
                    <span class="stats-rate">
                      <span class="stats-label">通过率:</span>
                      <span
                        class="stats-percentage"
                        :style="{ color: getProgressColor(row.statistics.pass_rate) }"
                      >
                        {{ row.statistics.pass_rate }}%
                      </span>
                    </span>
                    <span class="stats-total">总数: {{ row.statistics.total_cases }}</span>
                  </div>
                  <el-progress
                    :percentage="row.statistics.pass_rate"
                    :color="getProgressColor(row.statistics.pass_rate)"
                    :stroke-width="6"
                    :show-text="false"
                  />
                  <div class="stats-detail">
                    <div class="stats-item pass"><span class="item-label">通过</span><span class="item-value">{{ row.statistics.pass_count }}</span></div>
                    <div class="stats-item fail"><span class="item-label">失败</span><span class="item-value">{{ row.statistics.fail_count }}</span></div>
                    <div class="stats-item blocked"><span class="item-label">阻塞</span><span class="item-value">{{ row.statistics.blocked_count }}</span></div>
                    <div class="stats-item not-applicable"><span class="item-label">不适用</span><span class="item-value">{{ row.statistics.not_applicable_count }}</span></div>
                  </div>
                </div>
                <span v-else class="no-data">-</span>
              </template>
            </el-table-column>
            <!-- 设备脚本任务：脚本文件列 -->
            <el-table-column
              v-if="activeTab === 'device_script'"
              prop="script_file"
              label="脚本文件"
              min-width="180"
              align="center"
            >
              <template #default="{ row }">
                <template v-if="row.script_file">
                  <div class="script-file-link-wrapper">
                    <a class="script-file-link" @click.prevent="handleDownloadScript(row)">
                      <el-icon><Download /></el-icon>
                      <span>{{ row.script_file }}</span>
                    </a>
                  </div>
                </template>
                <span v-else class="no-data">-</span>
              </template>
            </el-table-column>
            <el-table-column
              label="计划时间"
              min-width="165"
              align="center"
            >
              <template #default="{ row }">
                <div v-if="row.scheduled_time || row.scheduled_end_time" class="time-range">
                  <div class="time-item">
                    <span class="time-label">开始:</span>
                    <span class="time-value">{{ formatDateTime(row.scheduled_time) }}</span>
                  </div>
                  <div class="time-item">
                    <span class="time-label">结束:</span>
                    <span class="time-value">{{ formatDateTime(row.scheduled_end_time) }}</span>
                  </div>
                </div>
                <span v-else class="no-data">-</span>
              </template>
            </el-table-column>
            <el-table-column
              label="操作"
              min-width="160"
              fixed="right"
              align="center"
            >
              <template #default="{ row }">
                <div class="action-btns">
                  <el-button v-if="row.status === 'pending'" size="small" circle title="开始执行" @click="handleExecute(row)">
                    <el-icon color="#67c23a"><VideoPlay /></el-icon>
                  </el-button>
                  <el-button v-if="row.status === 'running'" size="small" circle title="继续执行" @click="handleExecute(row)">
                    <el-icon color="#409eff"><VideoPlay /></el-icon>
                  </el-button>
                  <el-button v-if="row.status === 'running'" size="small" circle title="终止" @click="handleStopTask(row)">
                    <el-icon color="#f56c6c"><VideoPause /></el-icon>
                  </el-button>
                  <el-button v-if="row.status === 'completed'" size="small" circle title="重新执行" @click="handleReExecute(row)">
                    <el-icon color="#409eff"><RefreshRight /></el-icon>
                  </el-button>
                  <el-button v-if="row.status === 'completed' && reportAutoGenerate !== 'auto'" size="small" circle title="生成报告" @click="handleGenerateReport(row)">
                    <el-icon color="#409eff"><Document /></el-icon>
                  </el-button>
                  <el-button size="small" circle title="详情" @click="handleView(row)">
                    <el-icon color="#909399"><View /></el-icon>
                  </el-button>
                  <el-button size="small" circle title="删除" @click="handleDelete(row)">
                    <el-icon color="#f56c6c"><Delete /></el-icon>
                  </el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div class="pagination-container">
          <el-pagination
            :current-page="currentPagination.page"
            :page-size="currentPagination.size"
            :page-sizes="[10, 20, 50, 100]"
            :total="currentPagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="(size) => handleSizeChange(size, activeTab.value === 'test_case' ? 'testCase' : 'deviceScript')"
            @current-change="handlePageChange"
          />
        </div>
      </div>
    </div>
      </div>
    </div>

    <TaskDialog
      ref="taskDialogRef"
      @refresh="loadTasks"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from "vue";
import { useRouter, useRoute } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  Plus,
  Search,
  VideoPlay,
  View,
  Delete,
  RefreshRight,
  VideoPause,
  Refresh,
  Download,
  Document,
  Folder,
  FolderOpened,
} from "@element-plus/icons-vue";
import testTaskApi from "@/api/testTask";
import projectApi from "@/api/project";
import { getUserList } from "@/api/user";
import deviceApi from "@/api/device";
import { manualGenerateReport } from "@/api/report";
import { getUserSettings } from "@/api/settings";
import TaskDialog from "./components/TaskDialog.vue";

const activeTab = ref("test_case");
/** 报告生成方式：auto 时任务列表不显示「生成报告」按钮 */
const reportAutoGenerate = ref("manual");
const loading = reactive({
  testCase: false,
  deviceScript: false,
});
const taskList = reactive({
  testCase: [],
  deviceScript: [],
});
const userOptions = ref([]);
const taskDialogRef = ref(null);
const router = useRouter();
const route = useRoute();

// 任务目录：按任务类型分开的文件夹树
const folderTreeRef = ref(null);
const folderTreeWrapRef = ref(null); // 目录滚动容器，用于横向定位到当前选中项
const folderTreeRaw = ref([]); // 当前任务类型下的文件夹树（从接口来）
const selectedFolderId = ref(null); // null 表示「全部」，数字为文件夹 id
const folderTreeData = ref([
  { id: "__all__", name: "全部", children: [] },
]);
const isLeftPanelCollapsed = ref(false);
const folderContextMenuVisible = ref(false);
const folderContextMenuStyle = ref({ left: "0px", top: "0px", zIndex: 10000 });
const contextMenuFolderId = ref(null);
const folderContextMenuRef = ref(null);
const editingFolderId = ref(null);
const editingFolderName = ref("");
const folderEditInputRef = ref(null);
const lastDropDeniedHintTime = ref(0);

// 任务目录树展开状态（与用例管理页套件树逻辑一致：记录用户手动展开的节点，持久化到 localStorage）
const taskFolderExpandedKeys = ref([]);
const taskFolderMountKey = ref(0);

const STORAGE_KEY_TASK_FOLDER_EXPANDED = "testTaskFolderExpandedKeys";

function loadTaskFolderExpandedKeysFromStorage() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY_TASK_FOLDER_EXPANDED);
    if (!raw) return [];
    const obj = JSON.parse(raw);
    const list = obj[activeTab.value];
    return Array.isArray(list) ? list : [];
  } catch {
    return [];
  }
}

function saveTaskFolderExpandedKeysToStorage() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY_TASK_FOLDER_EXPANDED);
    const obj = raw ? JSON.parse(raw) : {};
    obj[activeTab.value] = taskFolderExpandedKeys.value;
    localStorage.setItem(STORAGE_KEY_TASK_FOLDER_EXPANDED, JSON.stringify(obj));
  } catch (e) {
    console.error("保存任务目录展开状态失败:", e);
  }
}

function findNodeInFolderTree(nodes, id) {
  if (!nodes || !nodes.length) return null;
  for (const n of nodes) {
    if (n.id === id) return n;
    const found = findNodeInFolderTree(n.children, id);
    if (found) return found;
  }
  return null;
}

function collectFolderNodeAndDescendantIds(nodeOrId) {
  const node =
    typeof nodeOrId === "object" && nodeOrId != null
      ? nodeOrId
      : findNodeInFolderTree(folderTreeData.value, nodeOrId);
  const id = node ? node.id : nodeOrId;
  if (!node) return [id].filter((x) => x != null);
  const ids = [node.id];
  function walk(list) {
    if (!list || !list.length) return;
    for (const n of list) {
      ids.push(n.id);
      if (n.children?.length) walk(n.children);
    }
  }
  walk(node.children);
  return ids;
}

function handleFolderNodeExpand(data) {
  if (data.id == null) return;
  if (!taskFolderExpandedKeys.value.includes(data.id)) {
    taskFolderExpandedKeys.value = [...taskFolderExpandedKeys.value, data.id];
    saveTaskFolderExpandedKeysToStorage();
  }
  scrollFolderTreeToCurrent();
}

function handleFolderNodeCollapse(data) {
  const toRemove = collectFolderNodeAndDescendantIds(data);
  const set = new Set(taskFolderExpandedKeys.value);
  toRemove.forEach((id) => set.delete(id));
  taskFolderExpandedKeys.value = Array.from(set);
  saveTaskFolderExpandedKeysToStorage();
  taskFolderMountKey.value += 1;
}

const loadFolderTree = async () => {
  try {
    const res = await testTaskApi.getTaskFolderTree(activeTab.value);
    const list = res.data?.folders ?? [];
    folderTreeRaw.value = list;
    folderTreeData.value = [
      { id: "__all__", name: "全部", children: list },
    ];
    const saved = loadTaskFolderExpandedKeysFromStorage();
    taskFolderExpandedKeys.value = saved.length ? saved : ["__all__"];
    taskFolderMountKey.value += 1;
    scrollFolderTreeToCurrent();
  } catch (e) {
    console.error("加载任务文件夹树失败:", e);
    ElMessage.error("加载任务目录失败");
    folderTreeData.value = [{ id: "__all__", name: "全部", children: [] }];
    taskFolderExpandedKeys.value = ["__all__"];
  }
};

/** 点击文件夹后：仅通过设置 scrollLeft/scrollTop 定位到该节点并完整显示名称，避免 scrollIntoView 引起抖动。
 * 在布局稳定后执行一次（双 rAF + 一次微延迟），最底层节点单次点击即可生效。 */
const FOLDER_SCROLL_RIGHT_GAP = 12;

function scrollFolderTreeToCurrent(clickedFolderId, clickedNodeEl) {
  const wrap = folderTreeWrapRef.value;
  if (!wrap) return;

  const run = () => {
    if (!wrap) return;
    let nodeEl = null;
    if (clickedNodeEl && wrap.contains(clickedNodeEl)) nodeEl = clickedNodeEl;
    if (!nodeEl && clickedFolderId != null && clickedFolderId !== "__all__") {
      const marker = wrap.querySelector(`[data-folder-id="${clickedFolderId}"]`);
      nodeEl = marker ? marker.closest(".el-tree-node") : null;
    }
    if (!nodeEl) nodeEl = wrap.querySelector(".el-tree-node.is-current");
    if (!nodeEl) return;

    const wrapRect = wrap.getBoundingClientRect();
    const nodeRect = nodeEl.getBoundingClientRect();
    const nodeLeftInContent = nodeRect.left - wrapRect.left + wrap.scrollLeft;
    const nodeRightInContent = nodeLeftInContent + nodeRect.width;
    const nodeTopInContent = nodeRect.top - wrapRect.top + wrap.scrollTop;
    const nodeBottomInContent = nodeTopInContent + nodeRect.height;

    let scrollLeft = wrap.scrollLeft;
    if (nodeLeftInContent < scrollLeft) {
      scrollLeft = nodeLeftInContent;
    } else if (nodeRightInContent > scrollLeft + wrap.clientWidth - FOLDER_SCROLL_RIGHT_GAP) {
      scrollLeft = nodeRightInContent - (wrap.clientWidth - FOLDER_SCROLL_RIGHT_GAP);
    }

    let scrollTop = wrap.scrollTop;
    if (nodeTopInContent < scrollTop) {
      scrollTop = nodeTopInContent;
    } else if (nodeBottomInContent > scrollTop + wrap.clientHeight) {
      scrollTop = nodeBottomInContent - wrap.clientHeight;
    }

    wrap.scrollLeft = scrollLeft;
    wrap.scrollTop = scrollTop;
  };

  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      setTimeout(run, 80);
    });
  });
}

const handleTaskTypeChange = () => {
  selectedFolderId.value = null;
  loadFolderTree();
  pagination.testCase.page = 1;
  pagination.deviceScript.page = 1;
  loadTasks();
};

const handleFolderClick = (data, nodeEl) => {
  closeFolderContextMenu();
  if (data.id === "__all__") {
    selectedFolderId.value = null;
  } else {
    selectedFolderId.value = data.id;
  }
  if (activeTab.value === "test_case") {
    pagination.testCase.page = 1;
  } else {
    pagination.deviceScript.page = 1;
  }
  loadTasks();
  scrollFolderTreeToCurrent(data.id, nodeEl);
};

const toggleLeftPanel = () => {
  isLeftPanelCollapsed.value = !isLeftPanelCollapsed.value;
};

const handleFolderContextMenu = (event, data) => {
  event.preventDefault();
  contextMenuFolderId.value = data.id;
  const x = event.clientX + window.scrollX;
  const y = event.clientY + window.scrollY;
  folderContextMenuStyle.value = { left: `${x}px`, top: `${y}px`, zIndex: 10000 };
  folderContextMenuVisible.value = true;
};

const closeFolderContextMenu = () => {
  folderContextMenuVisible.value = false;
};

const handleAddSubFolderFromMenu = () => {
  const parentId = contextMenuFolderId.value && contextMenuFolderId.value !== "__all__" ? contextMenuFolderId.value : null;
  if (parentId) {
    const depth = getFolderDepthById(folderTreeRaw.value, parentId);
    if (depth >= TASK_FOLDER_MAX_DEPTH) {
      ElMessage.warning(`任务目录最多 ${TASK_FOLDER_MAX_DEPTH} 层，无法在此层级下新建子文件夹（将形成第四级）`);
      closeFolderContextMenu();
      return;
    }
  }
  selectedFolderId.value = parentId;
  closeFolderContextMenu();
  handleAddFolder();
};

const handleDeleteFolderFromMenu = async () => {
  const folderId = contextMenuFolderId.value;
  if (!folderId || folderId === "__all__") return;
  closeFolderContextMenu();
  try {
    await ElMessageBox.confirm("确定删除该文件夹吗？其下任务将变为未归类。", "删除文件夹", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    });
    await testTaskApi.deleteTaskFolder(folderId);
    ElMessage.success("已删除");
    if (selectedFolderId.value === folderId) selectedFolderId.value = null;
    loadFolderTree();
    loadTasks();
  } catch (e) {
    if (e !== "cancel") ElMessage.error(e?.message || "删除失败");
  }
};

const allowFolderDrag = (node) => {
  if (node.data?.id === "__all__") return false;
  if (editingFolderId.value) return false;
  return true;
};

const startFolderRename = (data) => {
  if (data.id === "__all__") return;
  editingFolderId.value = data.id;
  editingFolderName.value = data.name || "";
  setTimeout(() => {
    folderEditInputRef.value?.focus();
  }, 80);
};

const saveFolderRename = async (data) => {
  const name = editingFolderName.value.trim();
  if (!name) {
    ElMessage.warning("文件夹名称不能为空");
    editingFolderId.value = null;
    return;
  }
  if (name === (data.name || "")) {
    editingFolderId.value = null;
    return;
  }
  try {
    await testTaskApi.updateTaskFolder(data.id, { name });
    ElMessage.success("已重命名");
    editingFolderId.value = null;
    loadFolderTree();
  } catch (e) {
    ElMessage.error(e?.message || "重命名失败");
  }
};

const cancelFolderRename = () => {
  editingFolderId.value = null;
};

const allowFolderDrop = (draggingNode, dropNode, type) => {
  if (dropNode.data?.id === "__all__") return true;
  if (type === "inner") {
    const dropDepth = dropNode.data?.depth ?? 1;
    if (dropDepth >= TASK_FOLDER_MAX_DEPTH) {
      if (Date.now() - lastDropDeniedHintTime.value > 2000) {
        ElMessage.warning(`任务目录最多 ${TASK_FOLDER_MAX_DEPTH} 层，无法拖入该文件夹（将形成第四级）`);
        lastDropDeniedHintTime.value = Date.now();
      }
      return false;
    }
  }
  return true;
};

const handleFolderNodeDrop = async (draggingNode, dropNode, dropType) => {
  const dragId = draggingNode.data?.id;
  if (!dragId || dragId === "__all__") return;
  try {
    let parentId = null;
    let sortOrder = 0;
    // 拖到根节点「全部」内（列表最下方）：视为放到根级末尾
    if (dropNode.data?.id === "__all__" && dropType === "inner") {
      parentId = null;
      const rootChildren = dropNode.data.children || [];
      const maxOrder = rootChildren.length
        ? Math.max(...rootChildren.map((c) => c.sort_order ?? 0), 0)
        : -1;
      sortOrder = maxOrder + 1;
    } else if (dropType === "inner") {
      parentId = dropNode.data.id;
      const children = dropNode.data.children || [];
      const last = children.length ? [...children].sort((a, b) => (b.sort_order ?? 0) - (a.sort_order ?? 0))[0] : null;
      sortOrder = last ? (last.sort_order ?? 0) + 1 : 0;
    } else {
      parentId = dropNode.data.parent_id ?? null;
      const baseOrder = dropNode.data.sort_order ?? 0;
      sortOrder = dropType === "before" ? baseOrder : baseOrder + 1;
    }
    await testTaskApi.updateTaskFolder(dragId, { parent_id: parentId, sort_order: sortOrder });
    ElMessage.success("顺序已更新");
    loadFolderTree();
  } catch (e) {
    ElMessage.error(e?.message || "更新顺序失败");
  }
};

const TASK_FOLDER_MAX_DEPTH = 3;

/** 从树中根据 id 查找节点深度，未找到返回 0 */
function getFolderDepthById(nodes, id) {
  if (!nodes || !id) return 0;
  for (const n of nodes) {
    if (n.id === id) return n.depth ?? 1;
    const d = getFolderDepthById(n.children, id);
    if (d) return d;
  }
  return 0;
}

const handleAddFolder = () => {
  const parentId = selectedFolderId.value && selectedFolderId.value !== "__all__" ? selectedFolderId.value : null;
  if (parentId) {
    const depth = getFolderDepthById(folderTreeRaw.value, parentId);
    if (depth >= TASK_FOLDER_MAX_DEPTH) {
      ElMessage.warning(`任务目录最多 ${TASK_FOLDER_MAX_DEPTH} 层，无法在此层级下新建子文件夹（将形成第四级）`);
      return;
    }
  }
  ElMessageBox.prompt("请输入文件夹名称", "新建文件夹", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    inputPattern: /\S+/,
    inputErrorMessage: "名称不能为空",
  })
    .then(({ value }) => {
      return testTaskApi.createTaskFolder({
        name: value.trim(),
        task_type: activeTab.value,
        parent_id: parentId,
      });
    })
    .then(() => {
      ElMessage.success("创建成功");
      loadFolderTree();
    })
    .catch((err) => {
      if (err !== "cancel") ElMessage.error(err?.message || "创建失败");
    });
};

// 当前任务类型对应的列表、分页、加载状态（仅由左侧任务类型下拉控制）
const currentTaskList = computed(() =>
  activeTab.value === "test_case" ? taskList.testCase : taskList.deviceScript
);
const currentPagination = computed(() =>
  activeTab.value === "test_case" ? pagination.testCase : pagination.deviceScript
);
const currentLoading = computed(() =>
  activeTab.value === "test_case" ? loading.testCase : loading.deviceScript
);

const filterForm = reactive({
  search: "",
  status: "",
  priority: "",
  task_type: "",
  executor_id: "",
});

const pagination = reactive({
  testCase: {
    page: 1,
    size: 10,
    total: 0,
  },
  deviceScript: {
    page: 1,
    size: 10,
    total: 0,
  },
});

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

const getPriorityType = (priority) => {
  const typeMap = {
    high: "danger",
    medium: "warning",
    low: "info",
  };
  return typeMap[priority] || "info";
};

const getPriorityText = (priority) => {
  const textMap = {
    high: "高",
    medium: "中",
    low: "低",
  };
  return textMap[priority] || priority;
};

const getProgressColor = (percentage) => {
  if (percentage >= 80) return "#67c23a";
  if (percentage >= 60) return "#e6a23c";
  return "#f56c6c";
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

const formatDateTime = (dateString) => {
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

const loadTasks = async () => {
  const folderIdParam =
    selectedFolderId.value != null && selectedFolderId.value !== "__all__"
      ? selectedFolderId.value
      : undefined;

  if (activeTab.value === "test_case") {
    const params = {
      ...filterForm,
      page: pagination.testCase.page,
      size: pagination.testCase.size,
      task_type: "test_case",
    };
    if (folderIdParam !== undefined) params.folder_id = folderIdParam;
    loading.testCase = true;
    try {
      const res = await testTaskApi.getTestTaskList(params);
      taskList.testCase = res.data.test_tasks;
      pagination.testCase.total = res.data.pagination.total;
    } catch (error) {
      console.error("加载测试用例任务列表失败:", error);
      ElMessage.error("加载测试用例任务列表失败");
    } finally {
      loading.testCase = false;
    }
  } else {
    const params = {
      ...filterForm,
      page: pagination.deviceScript.page,
      size: pagination.deviceScript.size,
      task_type: "device_script",
    };
    if (folderIdParam !== undefined) params.folder_id = folderIdParam;
    loading.deviceScript = true;
    try {
      const res = await testTaskApi.getTestTaskList(params);
      taskList.deviceScript = res.data.test_tasks;
      pagination.deviceScript.total = res.data.pagination.total;
    } catch (error) {
      console.error("加载设备脚本任务列表失败:", error);
      ElMessage.error("加载设备脚本任务列表失败");
    } finally {
      loading.deviceScript = false;
    }
  }
};

const loadUsers = async () => {
  try {
    const response = await getUserList({ page: 1, size: 1000 });
    userOptions.value = response.data?.items || response.data?.users || [];
  } catch (error) {
    console.error("加载用户列表失败:", error);
  }
};

const handleSearch = () => {
  pagination.testCase.page = 1;
  pagination.deviceScript.page = 1;
  loadTasks();
};

const handleReset = () => {
  Object.assign(filterForm, {
    search: "",
    status: "",
    priority: "",
    task_type: "",
    executor_id: "",
  });
  pagination.testCase.page = 1;
  pagination.deviceScript.page = 1;
  loadTasks();
};

const handleCreate = () => {
  const folderId =
    selectedFolderId.value != null && selectedFolderId.value !== "__all__"
      ? selectedFolderId.value
      : null;
  taskDialogRef.value?.open(null, {
    folder_id: folderId,
    task_type: activeTab.value,
  });
};

const handleExecute = async (row) => {
  try {
    // 对于测试用例任务，在新标签页中打开用例执行页面
    if (row.task_type === "test_case") {
      const url = `${window.location.origin}/test-tasks/${row.id}/execute`;
      window.open(url, "_blank");
      return;
    }
    // 对于设备脚本任务，跳转到设备脚本执行页，实时显示终端输出
    if (row.task_type === "device_script") {
      if (row.status !== "pending" && row.status !== "completed") {
        ElMessage.warning("当前任务状态不支持此操作");
        return;
      }
      const taskDevicesResponse = await testTaskApi.getTaskDevices(row.id);
      const taskDevices = taskDevicesResponse.data?.devices || [];
      if (taskDevices.length === 0) {
        ElMessage.warning("任务未关联任何设备，无法执行");
        return;
      }
      router.push({ name: "DeviceScriptExecution", params: { id: row.id } });
    }
  } catch (error) {
    if (error !== "cancel") {
      console.error("执行测试任务失败:", error);
      ElMessage.error(
        "执行测试任务失败：" + (error.response?.data?.message || error.message),
      );
    }
  }
};

const handleStopTask = async (row) => {
  try {
    await ElMessageBox.confirm("请选择要执行的操作：", "停止任务", {
      distinguishCancelAndClose: true,
      confirmButtonText: "结束任务",
      cancelButtonText: "取消操作",
      type: "warning",
    });

    await testTaskApi.completeTestTask(row.id);
    ElMessage.success("任务已结束");
    loadTasks();
  } catch (error) {
    if (error !== "cancel" && error !== "close") {
      console.error("停止任务失败:", error);
      ElMessage.error(
        "停止任务失败：" + (error.response?.data?.message || error.message),
      );
    }
  }
};

const handleReExecute = async (row) => {
  try {
    await testTaskApi.executeTestTask(row.id);
    ElMessage.success("任务已重置为待执行");
    loadTasks();
  } catch (error) {
    if (error !== "cancel") {
      console.error("重新执行任务失败:", error);
      ElMessage.error(
        "重新执行任务失败：" + (error.response?.data?.message || error.message),
      );
    }
  }
};

const handleGenerateReport = async (row) => {
  try {
    await ElMessageBox.confirm("确认为该任务生成报告？生成后将跳转到报告详情。", "生成报告", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "info",
    });
  } catch {
    return;
  }
  try {
    const res = await manualGenerateReport(row.id);
    if (res?.success && res?.data?.report_id) {
      ElMessage.success("报告已生成");
      router.push(`/report/record/${res.data.report_id}`);
    } else {
      ElMessage.error(res?.message || "生成报告失败");
    }
  } catch (e) {
    ElMessage.error(e?.response?.data?.message || e?.message || "生成报告失败");
  }
};

const handleView = (row) => {
  taskDialogRef.value?.open(row.id);
};

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      "确认删除该测试任务吗？删除后无法恢复！",
      "提示",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      },
    );

    await testTaskApi.deleteTestTask(row.id);
    ElMessage.success("测试任务删除成功");
    loadTasks();
  } catch (error) {
    if (error !== "cancel") {
      console.error("删除测试任务失败:", error);
      ElMessage.error(
        "删除测试任务失败：" + (error.response?.data?.message || error.message),
      );
    }
  }
};

// 下载脚本文件
const handleDownloadScript = (row) => {
  if (row.file_path) {
    // 构建完整的下载URL，包含原始文件名作为查询参数
    const downloadUrl = `/api/files/${row.file_path}?filename=${encodeURIComponent(row.script_file || "script_file")}`;


    // 创建下载链接并触发下载
    const a = document.createElement("a");
    a.href = downloadUrl;
    a.download = row.script_file || "script_file";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  } else {
    ElMessage.warning("脚本文件路径不存在");
  }
};

const handleSizeChange = (size, taskType) => {
  pagination[taskType].size = size;
  pagination[taskType].page = 1;
  loadTasks();
};

const handlePageChange = (page) => {
  const key = activeTab.value === "test_case" ? "testCase" : "deviceScript";
  pagination[key].page = page;
  loadTasks();
};


// 拉取报告设置（自动时隐藏「生成报告」按钮）
const loadReportSetting = async () => {
  try {
    const res = await getUserSettings();
    if (res?.data && res.data.report_auto_generate === "auto") reportAutoGenerate.value = "auto";
    else reportAutoGenerate.value = "manual";
  } catch (_) {
    reportAutoGenerate.value = "manual";
  }
};

const onFolderContextMenuMousedown = (e) => {
  if (e.button === 0 && folderContextMenuRef.value && !folderContextMenuRef.value.contains(e.target)) {
    closeFolderContextMenu();
  }
};

onMounted(() => {
  loadFolderTree();
  loadTasks();
  loadUsers();
  loadReportSetting();
  document.addEventListener('visibilitychange', handleVisibilityChange);
  document.addEventListener('mousedown', onFolderContextMenuMousedown);
});

onUnmounted(() => {
  document.removeEventListener('mousedown', onFolderContextMenuMousedown);
});

// 选中目录变化时，将目录区横向滚动到当前节点
watch(selectedFolderId, () => scrollFolderTreeToCurrent());

// 监听路由变化，当导航到任务列表页面时刷新任务列表并重新拉取报告设置
watch(
  () => route.path,
  (newPath) => {
    if (newPath === "/test-tasks") {
      loadTasks();
      loadReportSetting();
    }
  }
);

// 页面可见性变化处理
const handleVisibilityChange = () => {
  if (document.visibilityState === 'visible') {
    loadTasks();
    loadReportSetting();
  }
};
</script>

<style lang="scss" scoped>
.test-task-management {
  padding: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: #fff;
}

.main-layout {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: row;
  gap: 0;
}

.left-panel {
  width: 230px;
  min-width: 230px;
  flex-shrink: 0;
  background: var(--el-bg-color, #fff);
  border-radius: 0;
  box-shadow: none;
  border-right: 1px solid var(--el-border-color-light, #e4e7ed);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: width 0.2s ease;
  box-sizing: border-box;
}
.left-panel.collapsed {
  min-width: 50px;
  width: 50px;
  overflow: hidden;
}
.left-panel.collapsed .panel-header {
  justify-content: center;
  padding: 12px 8px;
}
.left-panel.collapsed .panel-title,
.left-panel.collapsed .task-type-select-wrap,
.left-panel.collapsed .folder-tree-wrap {
  display: none;
}
.left-panel.collapsed .header-actions .el-button:first-child {
  display: none;
}

.left-panel .panel-header {
  padding: 12px 15px;
  border-bottom: 1px solid var(--el-border-color-lighter, #f0f2f5);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  background-color: var(--el-bg-color, #fff);
  flex-shrink: 0;
}
.left-panel .panel-title {
  font-weight: 600;
  font-size: 14px;
  color: var(--el-text-color-primary, #303133);
}
.left-panel .header-actions {
  display: flex;
  align-items: center;
  flex-shrink: 0;
  gap: 3px;
}
.left-panel .header-actions .el-button {
  padding: 1px;
  margin: 0 !important;
  min-width: 24px;
  height: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.task-type-select-wrap {
  padding: 10px 12px;
  border-bottom: 1px solid #ebeef5;
}
.task-type-select {
  width: 100%;
}

.folder-tree-wrap {
  flex: 1;
  min-height: 0;
  min-width: 0;
  overflow-x: scroll;
  overflow-y: auto;
  padding: 8px;
  display: block;
}
.folder-tree-inner {
  display: inline-block;
  width: max-content;
  min-width: calc(100% + 1px);
  overflow: visible;
  vertical-align: top;
}
.folder-tree-wrap :deep(.el-tree) {
  background: transparent;
  width: max-content;
  min-width: 100%;
  overflow: visible !important;
}
.folder-tree-wrap :deep(.el-tree-node) {
  overflow: visible;
}
.folder-tree-wrap :deep(.el-tree-node__content) {
  height: 32px;
  min-width: min-content;
}
.folder-tree-wrap :deep(.el-tree-node.is-current > .el-tree-node__content) {
  padding-right: 12px;
}
.folder-tree-node {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-width: min-content; /* 宽度不足时由横向滚动条展示完整名称，不截断 */
}
.folder-tree-node .node-label {
  white-space: nowrap;
  min-width: min-content;
}
.folder-tree-node .folder-rename-input {
  width: 100%;
  min-width: 80px;
}
.folder-tree-node :deep(.folder-rename-input .el-input__wrapper) {
  padding: 2px 8px;
}

.right-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.list-toolbar {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--el-border-color-light, #e4e7ed);
  background: var(--el-bg-color, #fff);
  min-width: 0;
}
.list-toolbar .toolbar-left {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}
.list-toolbar .toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.context-menu {
  position: fixed;
  background: var(--el-bg-color, #fff);
  border: 1px solid var(--el-border-color-light, #e4e7ed);
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 5px 0;
}
.context-menu .menu-item {
  padding: 8px 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}
.context-menu .menu-item:hover {
  background: var(--el-fill-color-light, #f5f7fa);
}

/* 任务标签页区域填满剩余高度 */
.task-tabs-section {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.task-tabs-section :deep(.el-tabs) {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.task-tabs-section :deep(.el-tabs__header) {
  padding-left: 16px;
}

.task-tabs-section :deep(.el-tabs__content) {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.task-tabs-section :deep(.el-tabs__panel) {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.task-tabs-section :deep(.el-tab-pane) {
  height: 100%;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.table-section {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: var(--el-bg-color, #fff);
  border-radius: 0;
  overflow: hidden;
  margin-bottom: 56px;
}

/* 表格视口填满高度，不出现横向滚动条，表格列自适应宽度 */
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

.table-section .table-scroll-viewport :deep(.el-table__body-wrapper) {
  overflow-x: hidden !important;
}

.table-section {
  :deep(.el-button.is-circle) {
    padding: 12px;
    background-color: transparent !important;
    border: 1px solid #dcdfe6;

    &:hover {
      background-color: #f5f7fa !important;
    }

    .el-icon {
      font-size: 16px;
    }
  }

  /* 操作列：更小按钮与间距，避免横向滚动 */
  :deep(.action-btns) {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: center;
    gap: 4px;

    .el-button.is-circle {
      padding: 6px;
      min-width: 28px;
      height: 28px;

      .el-icon {
        font-size: 14px;
      }
    }

    .el-button + .el-button {
      margin-left: 0;
    }
  }

  :deep(.el-button + .el-button) {
    margin-left: 10px;
  }

  .time-range {
    font-size: 13px;
    line-height: 2;

    .time-item {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;

      .time-label {
        color: #909399;
        font-size: 12px;
        min-width: 32px;
      }

      .time-value {
        color: #303133;
        font-size: 13px;
        font-weight: 500;
      }
    }
  }

  .no-data {
    color: #c0c4cc;
    font-size: 13px;
  }

  .stats-mini {
    .stats-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 6px;

      .stats-rate {
        display: flex;
        align-items: center;
        gap: 4px;

        .stats-label {
          color: #606266;
          font-size: 11px;
          font-weight: 500;
        }

        .stats-percentage {
          font-size: 13px;
          font-weight: 700;
        }
      }

      .stats-total {
        font-size: 11px;
        color: #409eff;
        font-weight: 600;
      }
    }

    .stats-detail {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-top: 6px;

      .stats-item {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 11px;
        font-weight: 500;

        .item-label {
          font-size: 11px;
          color: #909399;
        }

        .item-value {
          font-size: 12px;
          font-weight: 600;
        }

        &.pass {
          .item-value {
            color: #67c23a;
          }
        }

        &.fail {
          .item-value {
            color: #f56c6c;
          }
        }

        &.blocked {
          .item-value {
            color: #e6a23c;
          }
        }

        &.not-applicable {
          .item-value {
            color: #909399;
          }
        }
      }
    }
  }
}

.pagination-container {
  position: fixed;
  bottom: 0;
  left: 230px;
  right: 0;
  z-index: 100;
  transition: left 0.2s ease;
  display: flex;
  justify-content: center;
  align-items: center;
  background: var(--el-bg-color, white);
  padding: 15px 20px;
  border-top: 1px solid #e4e7ed;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.1);
}

.main-layout.left-collapsed .pagination-container {
  left: 50px;
}

.pagination-container .el-pagination {
  margin: 0;
  text-align: center;
}

.script-file-link-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
}

.script-file-link {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #409eff;
  cursor: pointer;
  text-decoration: none;
  font-size: 14px;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.3s;
}

.script-file-link:hover {
  color: #66b1ff;
  background-color: #ecf5ff;
}
</style>
