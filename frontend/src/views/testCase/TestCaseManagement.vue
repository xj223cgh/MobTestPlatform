<template>
  <div class="test-case-management">
    <div class="page-header">
      <div class="header-content">
        <h1>用例管理</h1>
      </div>
      <div class="header-actions">
        <el-button type="warning" icon="MagicStick" :loading="isGeneratingAny" @click="handleGenerateCases">
          AI生成用例
        </el-button>
        <el-button type="primary" icon="Plus" @click="handleAddFolder">
          新建文件夹
        </el-button>
        <el-button
          v-if="selectedFolder && selectedFolder.id !== 0"
          type="success"
          icon="Plus"
          @click="handleAddSuite"
        >
          新建用例集
        </el-button>
        <el-select
          v-model="filterProjectId"
          placeholder="所属项目"
          filterable
          class="header-project-select"
          @change="onProjectFilterChange"
        >
          <el-option
            v-for="p in projectOptions"
            :key="p.id"
            :label="p.project_name"
            :value="p.id"
          />
        </el-select>
      </div>
    </div>

    <div class="main-content">
      <!-- 收起状态下的展开按钮 -->
      <div v-if="isLeftPanelCollapsed" class="collapsed-expand-btn" @click="isLeftPanelCollapsed = false">
        <el-icon><DArrowRight /></el-icon>
      </div>

      <!-- 左侧：文件夹目录树 -->
      <div class="left-panel" :class="{ collapsed: isLeftPanelCollapsed }">
        <div class="panel-header">
          <el-input
            v-model="searchText"
            placeholder="搜索文件夹"
            prefix-icon="Search"
            clearable
            size="small"
          />
          <el-tooltip content="折叠面板">
            <el-button
              size="small"
              text
              icon="DArrowLeft"
              @click="isLeftPanelCollapsed = true"
            />
          </el-tooltip>
          </div>
        <div class="tree-container">
          <el-tree
            ref="folderTreeRef"
            :data="folderTree"
            :props="treeProps"
            node-key="id"
            highlight-current
            :expand-on-click-node="false"
            :filter-node-method="filterNode"
            default-expand-all
            draggable
            :allow-drag="allowFolderDrag"
            :allow-drop="allowFolderDrop"
            @node-click="handleFolderClick"
            @node-contextmenu="handleFolderContextMenu"
            @node-drop="handleFolderDrop"
          >
            <template #default="{ node, data }">
              <span class="tree-node-label">
                <el-icon><Folder /></el-icon>
                <span>{{ data.suite_name }}{{ (data._virtual || data.id === 0) ? '' : `（${data.suite_count ?? 0}）` }}</span>
              </span>
            </template>
          </el-tree>
        </div>
        <div class="recycle-trigger" @click="showRecycleDrawer = true">
          <el-icon><Delete /></el-icon>
          <span>回收站</span>
        </div>
      </div>

      <!-- 右侧：用例集列表  -->
      <div class="right-panel">
        <div v-if="selectedFolder" class="panel-content">
          <div class="table-toolbar">
            <div class="toolbar-left-area">
            <el-input
                v-model="caseSetSearch"
                placeholder="搜索用例集名称"
                prefix-icon="Search"
              clearable
                style="width: 260px"
                @clear="loadCaseSets"
                @keyup.enter="loadCaseSets"
              />
              <el-select
                v-model="reviewStatusFilter"
                placeholder="评审状态"
                clearable
                style="width: 140px; margin-left: 10px"
                @change="loadCaseSets"
              >
                <el-option label="未评审" value="not_reviewed" />
                <el-option label="待评审" value="pending" />
                <el-option label="评审中" value="in_review" />
                <el-option label="已通过" value="completed" />
                <el-option label="已拒绝" value="rejected" />
              </el-select>
            </div>
        </div>

            <el-table
            :data="caseSets"
            v-loading="tableLoading"
              border
            stripe
            style="width: 100%"
            @row-click="handleRowClick"
          >
            <el-table-column prop="suite_name" label="用例集名称" min-width="150" align="center">
                <template #default="{ row }">
                <div class="suite-name-cell" :class="{ 'suite-name-cell--editing': editingSuiteId === row.id }">
                  <template v-if="editingSuiteId === row.id">
                    <el-input
                      ref="suiteNameInputRef"
                      v-model="editingSuiteName"
                      size="small"
                      maxlength="30"
                      show-word-limit
                      placeholder="用例集名称"
                      @click.stop
                      @blur="saveSuiteNameEdit"
                      @keyup.enter="saveSuiteNameEdit"
                      @keyup.esc="cancelSuiteNameEdit"
                    />
                  </template>
                  <template v-else>
                    <el-link type="primary" :underline="false" @click.stop="openMindmap(row)">
                      {{ row.suite_name }}
                    </el-link>
                    <el-button
                      type="primary"
                      link
                      class="suite-name-edit-btn"
                      :disabled="!!generatingMap[row.id]"
                      @click.stop="startEditSuiteName(row)"
                    >
                      <el-icon><EditPen /></el-icon>
                    </el-button>
                    <el-icon v-if="generatingMap[row.id]" class="is-loading generating-icon">
                      <Loading />
                    </el-icon>
                  </template>
                </div>
                </template>
              </el-table-column>
            <el-table-column prop="case_count" label="用例数量" width="85" align="center" />
            <el-table-column prop="review_status" label="状态" width="85" align="center">
                <template #default="{ row }">
                <el-tag :type="reviewStatusType(row.review_status)" size="small">
                  {{ reviewStatusLabel(row.review_status) }}
                  </el-tag>
                </template>
              </el-table-column>
            <el-table-column prop="creator_name" label="创建人" width="95" align="center" />
            <el-table-column prop="updated_at" label="更新时间" width="110" sortable align="center">
                <template #default="{ row }">
                {{ formatTime(row.updated_at) }}
                </template>
              </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="110" sortable align="center">
                <template #default="{ row }">
                {{ formatTime(row.created_at) }}
                </template>
              </el-table-column>
            <el-table-column prop="version_requirement_name" label="所属需求" min-width="140" align="center">
                <template #default="{ row }">
                {{ row.version_requirement_name || '-' }}
                </template>
              </el-table-column>
            <el-table-column label="操作" width="195" fixed="right" align="center">
                <template #default="{ row }">
                <div class="action-btns">
                  <template v-if="generatingMap[row.id]">
                    <el-icon class="is-loading generating-icon" style="margin-right: 8px"><Loading /></el-icon>
                    <el-button size="small" text type="danger" @click.stop="handleDeleteSuite(row)">删除</el-button>
                  </template>
                  <template v-else>
                    <el-tooltip :content="getReviewButtonTooltip(row)" placement="top">
                      <el-button size="small" text type="primary" @click.stop="handleReviewSuite(row)">评审</el-button>
                    </el-tooltip>
                    <el-button size="small" text type="primary" @click.stop="handleMoveSuite(row)">移动</el-button>
                    <el-button size="small" text type="success" @click.stop="handleCopySuite(row)">复制</el-button>
                    <el-button size="small" text type="danger" @click.stop="handleDeleteSuite(row)">删除</el-button>
                  </template>
                </div>
                </template>
              </el-table-column>
            </el-table>

          <div class="pagination-bar">
            <el-pagination
              v-model:current-page="pagination.page"
              v-model:page-size="pagination.pageSize"
              :total="pagination.total"
              :page-sizes="[10, 20, 50]"
              layout="total, sizes, prev, pager, next"
              @size-change="loadCaseSets"
              @current-change="loadCaseSets"
            />
          </div>
        </div>

        <div v-else class="empty-tip">
          <el-empty description="请在左侧选择一个文件夹" />
      </div>
    </div>
    </div>

    <!-- 新建文件夹对话框 -->
    <el-dialog v-model="folderDialogVisible" :title="folderDialogTitle" width="440px">
      <el-alert
        v-if="!folderForm.id && (folderForm.parentId || selectedFolder)"
        :title="`将在「${folderParentName}」下创建文件夹`"
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 16px"
      />
      <el-form :model="folderForm" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="folderForm.name" placeholder="请输入文件夹名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="folderDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitFolder">确定</el-button>
      </template>
    </el-dialog>

    <!-- 新建用例集对话框 -->
    <el-dialog v-model="suiteDialogVisible" title="新建用例集" width="560px" @open="onSuiteDialogOpen">
      <el-form :model="suiteForm" label-width="100px">
        <el-form-item label="所属项目" required>
          <el-select
            v-model="suiteForm.project_id"
            placeholder="选择项目"
            filterable
            style="width: 100%"
            @change="onSuiteFormProjectChange"
          >
            <el-option
              v-for="p in projectOptions"
              :key="p.id"
              :label="p.project_name"
              :value="p.id"
            />
          </el-select>
          <div class="form-item-hint">新建时默认当前页所选项目；若选择某文件夹下创建，用例集将归属该文件夹所在项目。</div>
        </el-form-item>
        <el-form-item label="所属文件夹" required>
          <el-tree-select
            v-model="suiteForm.parentId"
            :data="suiteFormFolderTree"
            :props="{ label: 'suite_name', value: 'id' }"
            node-key="id"
            placeholder="选择存放位置（默认当前选中文件夹）"
            style="width: 100%"
            check-strictly
            :render-after-expand="false"
            default-expand-all
            filterable
            clearable
          />
        </el-form-item>
        <el-form-item label="用例集名称" required>
          <el-input v-model="suiteForm.suite_name" placeholder="请输入用例集名称" maxlength="30" show-word-limit />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="suiteForm.description" type="textarea" :rows="3" placeholder="选填，用于说明用例集用途或范围" />
        </el-form-item>
        <el-form-item label="关联需求">
          <el-select
            v-model="suiteForm.version_requirement_id"
            placeholder="选择关联需求（可选）"
            clearable
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="r in requirementOptions"
              :key="r.id"
              :label="r.requirement_name"
              :value="r.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="suiteDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitSuite">确定</el-button>
      </template>
    </el-dialog>

    <!-- 移动用例集对话框 -->
    <el-dialog v-model="moveDialogVisible" title="移动用例集" width="440px">
      <p style="margin-bottom: 12px">选择目标文件夹：</p>
                  <el-tree
        :data="folderTree"
        :props="treeProps"
                    node-key="id"
        highlight-current
        default-expand-all
        @node-click="(data) => (moveTargetId = data.id)"
      >
        <template #default="{ data }">
          <span><el-icon><Folder /></el-icon> {{ data.suite_name }}</span>
                    </template>
                  </el-tree>
      <template #footer>
        <el-button @click="moveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmMove">确定</el-button>
      </template>
    </el-dialog>

    <!-- AI生成用例对话框 -->
    <el-dialog v-model="generateDialogVisible" title="AI 生成用例" width="600px" @open="onGenerateDialogOpen">
      <el-form :model="generateForm" label-width="110px">
        <el-form-item label="生成方式" required>
          <el-radio-group v-model="generateForm.mode">
            <el-radio value="append">追加到已有用例集</el-radio>
            <el-radio value="new">创建新用例集并生成</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="目标文件夹" required>
          <el-tree-select
            v-model="generateForm.folderId"
            :data="generateFolderTree"
            :props="{ label: 'suite_name', value: 'id' }"
            node-key="id"
            placeholder="先选择目录（全部或文件夹）"
            style="width: 100%"
            clearable
            check-strictly
            :render-after-expand="false"
            default-expand-all
            filterable
            @change="onGenerateFolderChange"
          />
        </el-form-item>
        <el-form-item v-if="generateForm.mode === 'append'" label="用例集选择" required>
          <el-select
            v-model="generateForm.suiteId"
            placeholder="选择该目录下的用例集"
            style="width: 100%"
            clearable
            filterable
            :disabled="generateForm.folderId == null"
          >
            <el-option
              v-for="s in generateSuiteOptions"
              :key="s.id"
              :label="s.suite_name"
              :value="s.id"
            />
          </el-select>
          <div v-if="generateForm.folderId != null && !generateSuiteOptions.length" class="form-tip">该目录下暂无用例集</div>
        </el-form-item>
        <el-form-item v-if="generateForm.mode === 'new'" label="新用例集名称" required>
          <el-input v-model="generateForm.newSuiteName" placeholder="请输入新用例集名称" maxlength="30" show-word-limit clearable />
        </el-form-item>
        <el-form-item label="需求文档" required>
          <el-upload
            ref="generateUploadRef"
            :auto-upload="false"
            :limit="1"
            accept=".txt,.md,.doc,.docx"
            :on-change="onGenerateFileChange"
            :on-remove="onGenerateFileRemove"
          >
            <el-button type="primary" plain>上传需求文档</el-button>
            <template #tip>
              <div class="upload-tip">支持 .txt、.md、.doc、.docx，上传后将读取文档内容用于生成用例</div>
            </template>
          </el-upload>
          <div v-if="generateForm.documentContent" class="document-preview">
            已加载 {{ (generateForm.documentContent || '').length }} 字，可重新上传替换
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="generateDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="isGeneratingAny"
          :disabled="!canSubmitGenerate"
          @click="submitGenerate"
        >
          开始生成
        </el-button>
      </template>
    </el-dialog>

    <!-- 右键菜单遮罩：点击任意空白处关闭菜单 -->
    <div
      v-if="contextMenu.visible"
      class="context-menu-overlay"
      @click="hideContextMenu"
    />
    <!-- 右键菜单 -->
    <div
      v-if="contextMenu.visible"
      class="context-menu"
      :style="{ top: contextMenu.y + 'px', left: contextMenu.x + 'px' }"
      @click.stop
    >
      <div class="context-menu-item" @click="handleRenameFolder">重命名</div>
      <div class="context-menu-item" @click="handleNewUnderNode">新建</div>
      <div class="context-menu-item danger" @click="handleDeleteFolder">删除</div>
    </div>

    <!-- 新建类型对话框：选择文件夹/用例集后展示对应表单 -->
    <el-dialog v-model="createTypeDialogVisible" title="新建" width="520px" @close="resetCreateTypeForm">
      <el-form :model="createTypeForm" label-width="100px">
        <el-form-item label="创建类型">
          <el-radio-group v-model="createTypeForm.createType">
            <el-radio value="folder">文件夹</el-radio>
            <el-radio value="suite">用例集</el-radio>
          </el-radio-group>
        </el-form-item>
        <template v-if="createTypeForm.createType === 'folder'">
          <el-form-item label="名称" required>
            <el-input v-model="createTypeForm.folderName" placeholder="请输入文件夹名称" />
          </el-form-item>
        </template>
        <template v-else>
          <el-form-item label="关联项目" required>
            <el-select v-model="createTypeForm.project_id" placeholder="选择项目" filterable style="width: 100%" @change="onCreateTypeProjectChange">
              <el-option v-for="p in projectOptions" :key="p.id" :label="p.project_name" :value="p.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="所属文件夹" required>
            <el-tree-select
              v-model="createTypeForm.parentId"
              :data="createTypeFolderTree"
              :props="{ label: 'suite_name', value: 'id' }"
              node-key="id"
              placeholder="选择存放位置"
              style="width: 100%"
              check-strictly
              default-expand-all
              filterable
              clearable
            />
          </el-form-item>
          <el-form-item label="用例集名称" required>
            <el-input v-model="createTypeForm.suite_name" placeholder="请输入用例集名称" maxlength="30" show-word-limit />
          </el-form-item>
          <el-form-item label="描述">
            <el-input v-model="createTypeForm.description" type="textarea" :rows="2" placeholder="选填" />
          </el-form-item>
          <el-form-item label="关联需求">
            <el-select v-model="createTypeForm.version_requirement_id" placeholder="可选" clearable filterable style="width: 100%">
              <el-option v-for="r in requirementOptions" :key="r.id" :label="r.requirement_name" :value="r.id" />
            </el-select>
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="createTypeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCreateType">确定</el-button>
      </template>
    </el-dialog>

    <!-- 回收站抽屉（仅用例集，按当前所属项目区分） -->
    <el-drawer v-model="showRecycleDrawer" :title="recycleDrawerTitle" size="960" direction="rtl" class="recycle-drawer">
      <div class="recycle-toolbar">
        <el-button
          type="danger"
          plain
          :disabled="!recycleSelectedIds.length"
          @click="batchPermanentDeleteRecycled"
        >
          全选删除
        </el-button>
      </div>
      <div v-loading="recycleLoading" class="recycle-list">
        <table class="recycle-table recycle-table-center" v-if="recycledList.length">
          <thead>
            <tr>
              <th class="col-check"><el-checkbox v-model="recycleSelectAll" @change="onRecycleSelectAllChange" /></th>
              <th class="col-path">文件夹路径</th>
              <th class="col-name">用例集名称</th>
              <th class="col-time">删除时间</th>
              <th class="col-operator">操作人</th>
              <th class="col-actions">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in recycledList" :key="item.id">
              <td class="col-check">
                <el-checkbox :model-value="recycleSelectedIds.includes(item.id)" @update:model-value="(v) => toggleRecycleSelected(item.id, v)" />
              </td>
              <td class="col-path">
                <el-tooltip v-if="(item.parent_path || '').length" :content="item.parent_path" placement="top" :show-after="300">
                  <span class="cell-text">{{ item.parent_path || '—' }}</span>
                </el-tooltip>
                <span v-else class="cell-text">—</span>
              </td>
              <td class="col-name">
                <el-tooltip v-if="getRecycleRowTooltip(item)" :content="getRecycleRowTooltip(item)" placement="top" :show-after="300" popper-class="recycle-name-tooltip-multiline">
                  <span class="cell-text">{{ item.suite_name }}</span>
                </el-tooltip>
                <span v-else class="cell-text">{{ item.suite_name }}</span>
              </td>
              <td class="col-time">{{ item.deleted_at ? formatRecycleTimeFull(item.deleted_at) : '—' }}</td>
              <td class="col-operator">{{ item.creator_name || '—' }}</td>
              <td class="col-actions">
                <el-button size="small" type="primary" link @click="restoreRecycled(item.id)">恢复</el-button>
                <el-button size="small" type="danger" link @click="permanentDeleteRecycled(item)">彻底删除</el-button>
              </td>
            </tr>
          </tbody>
        </table>
        <el-empty v-if="!recycleLoading && !recycledList.length" description="回收站为空" />
      </div>
      <div v-if="recycledList.length || recyclePagination.total" class="recycle-pagination">
        <el-pagination
          v-model:current-page="recyclePagination.page"
          v-model:page-size="recyclePagination.pageSize"
          :page-sizes="[10, 20, 50]"
          :total="recyclePagination.total"
          layout="total, sizes, prev, pager, next"
          @current-change="loadRecycled"
          @size-change="loadRecycled"
        />
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onBeforeUnmount, nextTick } from "vue";
import { useRouter } from "vue-router";
import { Folder, DArrowRight, DArrowLeft, Loading, Delete, EditPen } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { useUserStore } from "@/stores/user";
import {
  getFolderTree,
  getCaseSets,
  createTestSuite,
  updateTestSuite,
  deleteTestSuite,
  getRecycledSuites,
  restoreRecycledSuite,
  batchPermanentDeleteRecycledSuites,
} from "@/api/testSuite";
import { moveTestSuite, copyTestSuite } from "@/api/testSuite";
import { getProjects, getProjectVersionRequirements } from "@/api/project";
import { createGenerateCasesTask, getTaskStatus } from "@/api/aiTasks";

const router = useRouter();
const userStore = useUserStore();
const folderTreeRef = ref(null);
const searchText = ref("");
const isLeftPanelCollapsed = ref(false);
const selectedFolder = ref(null);
const folderTree = ref([]);

const treeProps = { children: "children", label: "suite_name" };

const caseSets = ref([]);
const tableLoading = ref(false);
const caseSetSearch = ref("");
const reviewStatusFilter = ref("");
const pagination = reactive({ page: 1, pageSize: 20, total: 0 });

const folderDialogVisible = ref(false);
const folderDialogTitle = ref("新建文件夹");
const folderForm = reactive({ name: "", id: null, parentId: null });

const suiteDialogVisible = ref(false);
const suiteFormFolderTree = ref([]);
const suiteForm = reactive({
  suite_name: "",
  description: "",
  version_requirement_id: null,
  project_id: null,
  parentId: null,
});

const moveDialogVisible = ref(false);
const moveTargetId = ref(null);
const movingSuite = ref(null);

const requirementOptions = ref([]);

const contextMenu = reactive({ visible: false, x: 0, y: 0, data: null });
const filterProjectId = ref(null);
const projectOptions = ref([]);
const showRecycleDrawer = ref(false);
const recycleLoading = ref(false);
const recycledList = ref([]);
const recyclePagination = reactive({ page: 1, pageSize: 10, total: 0 });
const recycleSelectedIds = ref([]);
const recycleSelectAll = ref(false);
const createTypeDialogVisible = ref(false);
const createTypeFolderTree = ref([]);
const createTypeForm = reactive({
  createType: "folder",
  folderName: "",
  parentFolderName: "",
  parentId: null,
  project_id: null,
  suite_name: "",
  description: "",
  version_requirement_id: null,
});

const generateDialogVisible = ref(false);
const generateForm = reactive({
  mode: "append",
  folderId: null,
  suiteId: null,
  newSuiteName: "",
  documentContent: "",
});
const generateFolderTree = ref([]);
const generateSuiteOptions = ref([]);
const generateUploadRef = ref(null);
const editingSuiteId = ref(null);
const editingSuiteName = ref("");
const suiteNameInputRef = ref(null);

const canSubmitGenerate = computed(() => {
  if (!generateForm.documentContent?.trim()) return false;
  if (generateForm.mode === "append") return !!generateForm.suiteId;
  return generateForm.folderId != null && !!generateForm.newSuiteName?.trim();
});

const generatingMap = reactive({});
const isGeneratingAny = computed(() => Object.keys(generatingMap).length > 0);

const folderParentName = computed(() => {
  if (folderForm.parentId) {
    const find = (nodes) => {
      for (const n of nodes) {
        if (n.id === folderForm.parentId) return n.suite_name;
        if (n.children?.length) { const r = find(n.children); if (r) return r; }
      }
      return null;
    };
    return find(folderTree.value) || '全部';
  }
  return selectedFolder.value?.suite_name || '全部';
});

const recycleDrawerTitle = computed(() => {
  if (!filterProjectId.value) return "回收站";
  const p = projectOptions.value?.find((x) => x.id === filterProjectId.value);
  return p ? `回收站（${p.project_name}）` : "回收站";
});

watch(searchText, (val) => {
  folderTreeRef.value?.filter(val);
});

function filterNode(value, data) {
  if (!value) return true;
  return data.suite_name?.toLowerCase().includes(value.toLowerCase());
}

async function loadFolderTree() {
  try {
    const params = filterProjectId.value ? { project_id: filterProjectId.value } : {};
    const res = await getFolderTree(params);
    const payload = res.data || {};
    const tree = payload.tree || payload || [];
    const rootSuiteCount = payload.root_suite_count || 0;

    const treeArr = Array.isArray(tree) ? tree : [];
    // 「全部」作为唯一根节点，其 children 为所有根级文件夹，便于拖拽到「全部」下（即移为根级）
    folderTree.value = [
      {
        id: 0,
        suite_name: "全部",
        type: "folder",
        parent_id: null,
        suite_count: rootSuiteCount,
        children: treeArr,
        _virtual: true,
      },
    ];
  } catch {
    ElMessage.error("加载文件夹目录失败");
  }
}

async function loadCaseSets() {
  if (!selectedFolder.value) return;
  tableLoading.value = true;
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      search: caseSetSearch.value,
      review_status: reviewStatusFilter.value || undefined,
    };
    if (filterProjectId.value) params.project_id = filterProjectId.value;
    const res = await getCaseSets(selectedFolder.value.id, params);
    const d = res.data || {};
    caseSets.value = d.items || [];
    pagination.total = d.total || 0;
  } catch {
    ElMessage.error("加载用例集列表失败");
  } finally {
    tableLoading.value = false;
  }
}

async function loadProjects() {
  try {
    const res = await getProjects({ page: 1, size: 10000 });
    projectOptions.value = res.data?.items ?? (Array.isArray(res.data) ? res.data : []) ?? [];
    if (projectOptions.value.length && filterProjectId.value == null) {
      filterProjectId.value = projectOptions.value[0].id;
      loadFolderTree();
    }
  } catch {
    projectOptions.value = [];
  }
}

function onProjectFilterChange() {
  loadFolderTree();
  selectedFolder.value = null;
  caseSets.value = [];
}

async function loadRecycled() {
  recycleLoading.value = true;
  recycleSelectedIds.value = [];
  recycleSelectAll.value = false;
  try {
    const params = {
      page: recyclePagination.page,
      page_size: recyclePagination.pageSize,
      ...(filterProjectId.value ? { project_id: filterProjectId.value } : {}),
    };
    const res = await getRecycledSuites(params);
    const data = res.data || {};
    recycledList.value = data.items || [];
    recyclePagination.total = data.total ?? 0;
  } catch {
    recycledList.value = [];
    recyclePagination.total = 0;
  } finally {
    recycleLoading.value = false;
  }
}

function toggleRecycleSelected(id, checked) {
  if (checked) {
    if (!recycleSelectedIds.value.includes(id)) recycleSelectedIds.value = [...recycleSelectedIds.value, id];
  } else {
    recycleSelectedIds.value = recycleSelectedIds.value.filter((x) => x !== id);
  }
  recycleSelectAll.value = recycledList.value.length > 0 && recycleSelectedIds.value.length === recycledList.value.length;
}

function onRecycleSelectAllChange(checked) {
  if (checked) {
    recycleSelectedIds.value = recycledList.value.map((x) => x.id);
  } else {
    recycleSelectedIds.value = [];
  }
}

async function batchPermanentDeleteRecycled() {
  if (!recycleSelectedIds.value.length) return;
  try {
    await ElMessageBox.confirm(
      `确定彻底删除选中的 ${recycleSelectedIds.value.length} 项吗？删除后不可恢复。`,
      "批量彻底删除",
      { type: "warning" }
    );
    await batchPermanentDeleteRecycledSuites(recycleSelectedIds.value);
    ElMessage.success("已彻底删除");
    await loadRecycled();
    await loadFolderTree();
  } catch (e) {
    if (e !== "cancel" && !e?._messageShown) {
      const msg = e?.response?.data?.message || e?.message || "批量彻底删除失败";
      ElMessage.error(msg);
    }
  }
}

async function restoreRecycled(id) {
  try {
    await restoreRecycledSuite(id);
    ElMessage.success("已恢复");
    await loadRecycled();
    await loadFolderTree();
    if (selectedFolder.value) await loadCaseSets();
  } catch (err) {
    if (!err?._messageShown) {
      const msg = err?.response?.data?.message || err?.message || "恢复失败";
      ElMessage.error(msg);
    }
  }
}

async function permanentDeleteRecycled(item) {
  try {
    await ElMessageBox.confirm(`确定彻底删除"${item.suite_name}"吗？删除后不可恢复。`, "确认彻底删除", { type: "warning" });
    await deleteTestSuite(item.id, { permanent: true });
    ElMessage.success("已彻底删除");
    await loadRecycled();
    await loadFolderTree();
  } catch { /* cancelled */ }
}

async function loadRequirements() {
  try {
    const { default: request } = await import("@/utils/request");
    const res = await request({ url: "/test-suites", method: "get", params: { all: true } });
    // Attempt to load requirements from a dedicated API if available
    try {
      const reqRes = await request({ url: "/iterations", method: "get", params: { page: 1, page_size: 1000 } });
      // We need version requirements - try to get them
      const vrRes = await request({ url: "/test-suites/options", method: "get" });
    } catch { /* ignore */ }
  } catch { /* ignore */ }
}

function handleFolderClick(data) {
  selectedFolder.value = data;
  pagination.page = 1;
  loadCaseSets();
}

function handleRowClick(row) {
  if (editingSuiteId.value != null) return;
  openMindmap(row);
}

function openMindmap(row) {
  const taskId = generatingMap[row.id];
  let url = `/mindmap-editor?suite_id=${row.id}&suite_name=${encodeURIComponent(row.suite_name)}`;
  if (taskId && typeof taskId === 'string') {
    url += `&generating=1&task_id=${encodeURIComponent(taskId)}`;
  }
  window.open(url, "_blank");
}

function startEditSuiteName(row) {
  if (generatingMap[row.id]) return;
  editingSuiteId.value = row.id;
  editingSuiteName.value = row.suite_name || "";
  nextTick(() => suiteNameInputRef.value?.focus());
}

async function saveSuiteNameEdit() {
  const id = editingSuiteId.value;
  if (id == null) return;
  const name = (editingSuiteName.value || "").trim();
  editingSuiteId.value = null;
  editingSuiteName.value = "";
  if (name === "") return;
  const row = caseSets.value.find((r) => r.id === id);
  if (row && row.suite_name === name) return;
  try {
    await updateTestSuite(id, { suite_name: name });
    ElMessage.success("名称已更新");
    await loadCaseSets();
    await loadFolderTree();
  } catch (err) {
    editingSuiteId.value = id;
    editingSuiteName.value = name;
    const msg = err?.response?.data?.message || err?.message || "更新失败";
    ElMessage.error(msg);
  }
}

function cancelSuiteNameEdit() {
  editingSuiteId.value = null;
  editingSuiteName.value = "";
}

function handleAddFolder() {
  folderDialogTitle.value = "新建文件夹";
  folderForm.name = "";
  folderForm.id = null;
  folderForm.parentId = selectedFolder.value?.id || null;
  folderDialogVisible.value = true;
}

function handleAddSubFolder() {
  contextMenu.visible = false;
  folderDialogTitle.value = "新建子文件夹";
  folderForm.name = "";
  folderForm.id = null;
  folderForm.parentId = contextMenu.data?.id;
  folderDialogVisible.value = true;
}

function handleNewUnderNode() {
  contextMenu.visible = false;
  const parent = contextMenu.data;
  createTypeForm.createType = "folder";
  createTypeForm.folderName = "";
  createTypeForm.parentFolderName = parent?.suite_name ?? "全部";
  createTypeForm.parentId = (parent?.id !== undefined && parent?.id !== null) ? parent.id : 0;
  createTypeForm.project_id = filterProjectId.value ?? projectOptions.value[0]?.id ?? null;
  createTypeForm.suite_name = "";
  createTypeForm.description = "";
  createTypeForm.version_requirement_id = null;
  createTypeFolderTree.value = folderTree.value;
  if (createTypeForm.project_id) loadRequirementOptionsByProject(createTypeForm.project_id);
  createTypeDialogVisible.value = true;
}

function onCreateTypeProjectChange(projectId) {
  loadRequirementOptionsByProject(projectId);
}

function resetCreateTypeForm() {
  createTypeForm.createType = "folder";
  createTypeForm.folderName = "";
  createTypeForm.parentFolderName = "";
  createTypeForm.parentId = null;
  createTypeForm.project_id = null;
  createTypeForm.suite_name = "";
  createTypeForm.description = "";
  createTypeForm.version_requirement_id = null;
}

async function submitCreateType() {
  if (createTypeForm.createType === "folder") {
    if (!createTypeForm.folderName.trim()) {
      ElMessage.warning("文件夹名称不能为空");
      return;
    }
    try {
      await createTestSuite({
        suite_name: createTypeForm.folderName.trim(),
        type: "folder",
        parent_id: createTypeForm.parentId || null,
      });
      ElMessage.success("文件夹创建成功");
      createTypeDialogVisible.value = false;
      await loadFolderTree();
    } catch {
      ElMessage.error("创建文件夹失败");
    }
    return;
  }
  if (!createTypeForm.suite_name.trim()) {
    ElMessage.warning("用例集名称不能为空");
    return;
  }
  if (!createTypeForm.project_id) {
    ElMessage.warning("请选择关联项目");
    return;
  }
  const parentId = (createTypeForm.parentId === 0 || createTypeForm.parentId === null || createTypeForm.parentId === undefined) ? null : createTypeForm.parentId;
  try {
    const res = await createTestSuite({
      suite_name: createTypeForm.suite_name.trim(),
      description: createTypeForm.description || "",
      type: "suite",
      parent_id: parentId,
      status: "active",
      version_requirement_id: createTypeForm.version_requirement_id || null,
      project_id: createTypeForm.project_id,
    });
    ElMessage.success("用例集创建成功");
    createTypeDialogVisible.value = false;
    await loadFolderTree();
    await loadCaseSets();
    if (res.data?.id) nextTick(() => openMindmap(res.data));
  } catch {
    ElMessage.error("创建用例集失败");
  }
}

function handleRenameFolder() {
  contextMenu.visible = false;
  if (contextMenu.data?._virtual || contextMenu.data?.id === 0) {
    ElMessage.warning("「全部」不能重命名");
    return;
  }
  folderDialogTitle.value = "重命名文件夹";
  folderForm.name = contextMenu.data?.suite_name || "";
  folderForm.id = contextMenu.data?.id;
  folderForm.parentId = contextMenu.data?.parent_id;
  folderDialogVisible.value = true;
}

async function submitFolder() {
  if (!folderForm.name.trim()) {
    ElMessage.warning("文件夹名称不能为空");
    return;
  }
  try {
    if (folderForm.id) {
      await updateTestSuite(folderForm.id, { suite_name: folderForm.name.trim() });
      ElMessage.success("重命名成功");
    } else {
      await createTestSuite({
        suite_name: folderForm.name.trim(),
        type: "folder",
        parent_id: folderForm.parentId || null,
        project_id: folderForm.parentId ? undefined : (filterProjectId.value || undefined),
      });
      ElMessage.success("文件夹创建成功");
    }
    folderDialogVisible.value = false;
    await loadFolderTree();
  } catch {
    ElMessage.error("操作失败");
  }
}

async function handleDeleteFolder() {
  contextMenu.visible = false;
  const folder = contextMenu.data;
  if (!folder) return;
  if (folder._virtual || folder.id === 0) {
    ElMessage.warning("「全部」不能删除");
    return;
  }
  try {
    await ElMessageBox.confirm(
      `确定删除文件夹"${folder.suite_name}"吗？其下用例集将移入回收站，文件夹将从目录中移除。`,
      "确认删除",
      { type: "warning" }
    );
    await deleteTestSuite(folder.id, { logical: true });
    ElMessage.success("已删除，其下用例集已移入回收站");
    if (selectedFolder.value?.id === folder.id) {
      selectedFolder.value = null;
      caseSets.value = [];
    }
    await loadFolderTree();
    if (showRecycleDrawer.value) await loadRecycled();
  } catch { /* cancelled */ }
}

function handleAddSuite() {
  suiteForm.suite_name = "";
  suiteForm.description = "";
  suiteForm.version_requirement_id = null;
  suiteForm.project_id = filterProjectId.value ?? projectOptions.value[0]?.id ?? null;
  suiteForm.parentId = selectedFolder.value?.id !== undefined && selectedFolder.value?.id !== null ? selectedFolder.value.id : 0;
  suiteFormFolderTree.value = folderTree.value;
  suiteDialogVisible.value = true;
}

async function onSuiteDialogOpen() {
  suiteFormFolderTree.value = folderTree.value;
  await loadRequirementOptionsByProject(suiteForm.project_id ?? filterProjectId.value);
}

async function onSuiteFormProjectChange(projectId) {
  loadRequirementOptionsByProject(projectId);
  if (projectId) {
    try {
      const res = await getFolderTree({ project_id: projectId });
      const payload = res.data || {};
      const tree = payload.tree || payload || [];
      const rootSuiteCount = payload.root_suite_count || 0;
      const treeArr = Array.isArray(tree) ? tree : [];
      suiteFormFolderTree.value = [
        { id: 0, suite_name: "全部", type: "folder", parent_id: null, suite_count: rootSuiteCount, children: treeArr, _virtual: true },
      ];
    } catch {
      suiteFormFolderTree.value = [{ id: 0, suite_name: "全部", type: "folder", children: [], _virtual: true }];
    }
  } else {
    suiteFormFolderTree.value = [];
  }
}

async function loadRequirementOptionsByProject(projectId) {
  if (!projectId) {
    requirementOptions.value = [];
    return;
  }
  try {
    const res = await getProjectVersionRequirements(projectId);
    const data = res.data || res;
    requirementOptions.value = data.items || data || [];
  } catch {
    requirementOptions.value = [];
  }
}

async function submitSuite() {
  if (!suiteForm.suite_name.trim()) {
    ElMessage.warning("用例集名称不能为空");
    return;
  }
  if (!suiteForm.project_id) {
    ElMessage.warning("请选择所属项目");
    return;
  }
  const parentId = (suiteForm.parentId === 0 || suiteForm.parentId === null || suiteForm.parentId === undefined) ? null : suiteForm.parentId;
  try {
    const res = await createTestSuite({
      suite_name: suiteForm.suite_name.trim(),
      description: suiteForm.description || "",
      type: "suite",
      parent_id: parentId,
      status: "active",
      version_requirement_id: suiteForm.version_requirement_id || null,
      project_id: suiteForm.project_id,
      iteration_id: null,
    });
    ElMessage.success("用例集创建成功");
    suiteDialogVisible.value = false;
    await loadFolderTree();
    await loadCaseSets();

    if (res.data?.id) {
      nextTick(() => openMindmap(res.data));
    }
  } catch {
    ElMessage.error("创建用例集失败");
  }
}

function handleMoveSuite(row) {
  movingSuite.value = row;
  moveTargetId.value = null;
  moveDialogVisible.value = true;
}

async function confirmMove() {
  if (!moveTargetId.value) {
    ElMessage.warning("请选择目标文件夹");
    return;
  }
  try {
    await moveTestSuite(movingSuite.value.id, { target_folder_id: moveTargetId.value });
    ElMessage.success("移动成功");
    moveDialogVisible.value = false;
    await loadFolderTree();
    await loadCaseSets();
  } catch {
    ElMessage.error("移动失败");
  }
}

async function handleCopySuite(row) {
  try {
    await ElMessageBox.confirm(`确定复制用例集"${row.suite_name}"吗？`, "确认复制");
    await copyTestSuite(row.id, { target_folder_id: selectedFolder.value?.id });
    ElMessage.success("复制成功");
    await loadFolderTree();
    await loadCaseSets();
  } catch { /* cancelled */ }
}

async function handleDeleteSuite(row) {
  const isGenerating = !!generatingMap[row.id];
  const message = isGenerating
    ? `用例集"${row.suite_name}"正在AI生成中。确定终止生成并移至回收站吗？`
    : `确定将用例集"${row.suite_name}"移至回收站吗？`;
  try {
    await ElMessageBox.confirm(message, "确认删除", { type: "warning" });
    await deleteTestSuite(row.id, { logical: true });
    delete generatingMap[row.id];
    ElMessage.success("已移至回收站");
    await loadFolderTree();
    await loadCaseSets();
    if (showRecycleDrawer.value) await loadRecycled();
  } catch { /* cancelled */ }
}

/** 评审按钮悬浮文案：按当前用户角色与用例集评审状态显示 */
function getReviewButtonTooltip(row) {
  const status = row.review_status || "not_reviewed";
  const me = userStore.userInfo?.id != null ? String(userStore.userInfo.id) : null;
  const creatorId = row.creator_id != null ? String(row.creator_id) : null;
  const initiatorId = row.review_initiator_id != null ? String(row.review_initiator_id) : null;
  const reviewerId = row.review_reviewer_id != null ? String(row.review_reviewer_id) : null;

  if (status === "not_reviewed") {
    return me === creatorId ? "创建者未发起评审" : "未发起评审";
  }
  if (status === "pending") {
    if (me === reviewerId) return "待我评审";
    if (me === initiatorId) return "待评审人评审";
    return "待评审";
  }
  if (status === "in_review") {
    if (me === reviewerId) return "我评审中";
    if (me === initiatorId) return "评审人评审中";
    return "评审人评审中";
  }
  if (status === "completed") return "评审已完成（已通过）";
  if (status === "rejected") return "评审已完成（已拒绝）";
  return "评审";
}

function handleReviewSuite(row) {
  router.push({ path: "/case-reviews", query: { suiteId: row.id } });
}

function handleGenerateCases() {
  generateForm.mode = "append";
  generateForm.folderId = null;
  generateForm.suiteId = null;
  generateForm.newSuiteName = "";
  generateForm.documentContent = "";
  generateFolderTree.value = [];
  generateSuiteOptions.value = [];
  generateDialogVisible.value = true;
}

async function onGenerateDialogOpen() {
  generateFolderTree.value = await loadGenerateFolderTree();
  if (generateForm.folderId != null) {
    try {
      const res = await getCaseSets(generateForm.folderId);
      generateSuiteOptions.value = res.data?.items || [];
    } catch {
      generateSuiteOptions.value = [];
    }
  }
}

/** 加载目录树（仅文件夹），供「用例集目录定位」使用 */
async function loadGenerateFolderTree() {
  try {
    const res = await getFolderTree();
    const payload = res.data || {};
    const tree = payload.tree || [];
    return [
      {
        id: 0,
        suite_name: "全部",
        type: "folder",
        children: tree,
      },
    ];
  } catch (e) {
    console.error("加载目录失败", e);
    ElMessage.error("加载目录失败，请重试");
    return [];
  }
}

/** 目录变更时加载该目录下用例集，并清空已选用例集 */
async function onGenerateFolderChange() {
  generateForm.suiteId = null;
  if (generateForm.folderId == null) {
    generateSuiteOptions.value = [];
    return;
  }
  try {
    const res = await getCaseSets(generateForm.folderId);
    generateSuiteOptions.value = res.data?.items || [];
  } catch {
    generateSuiteOptions.value = [];
  }
}

function onGenerateFileChange(file) {
  const raw = file.raw;
  if (!raw) return;
  const ext = (raw.name || "").toLowerCase().split(".").pop();
  if (ext === "txt" || ext === "md") {
    const reader = new FileReader();
    reader.onload = () => {
      generateForm.documentContent = reader.result ?? "";
    };
    reader.readAsText(raw, "UTF-8");
  } else {
    ElMessage.warning("请上传 .txt 或 .md 格式的需求文档，以便正确读取内容");
  }
}

function onGenerateFileRemove() {
  generateForm.documentContent = "";
}

function handleGenerateForSuite(row) {
  generateForm.folderId = row.parent_id ?? 0;
  generateForm.suiteId = row.id;
  generateForm.documentContent = "";
  generateSuiteOptions.value = [];
  generateDialogVisible.value = true;
}

async function submitGenerate() {
  if (!generateForm.documentContent?.trim()) {
    ElMessage.warning("需求文档内容不能为空");
    return;
  }
  generateDialogVisible.value = false;
  if (generateForm.mode === "append") {
    if (!generateForm.suiteId) {
      ElMessage.warning("请选择目标用例集");
      return;
    }
    await startGenerateForSuite(generateForm.suiteId, generateForm.documentContent);
    return;
  }
  // 创建新用例集并生成
  const parentId = generateForm.folderId === 0 ? null : generateForm.folderId;
  try {
    const createRes = await createTestSuite({
      suite_name: generateForm.newSuiteName.trim(),
      description: "",
      type: "suite",
      parent_id: parentId,
      status: "active",
      version_requirement_id: null,
      project_id: null,
      iteration_id: null,
    });
    const newSuite = createRes.data;
    if (!newSuite?.id) {
      ElMessage.error("创建用例集失败");
      return;
    }
    await startGenerateForSuite(newSuite.id, generateForm.documentContent);
    selectFolderById(newSuite.parent_id ?? 0);
    await loadCaseSets();
  } catch (e) {
    ElMessage.error(e?.response?.data?.message || "创建用例集失败");
  }
}

/** 在目录树中根据 id 选中文件夹（用于创建新用例集后定位） */
function selectFolderById(folderId) {
  const find = (nodes) => {
    for (const n of nodes) {
      if (n.id === folderId) return n;
      if (n.children?.length) { const r = find(n.children); if (r) return r; }
    }
    return null;
  };
  const node = find(folderTree.value);
  if (node) selectedFolder.value = node;
  else selectedFolder.value = folderTree.value[0] || null;
}

async function startGenerateForSuite(suiteId, documentContent) {
  try {
    generatingMap[suiteId] = 'pending';
    const res = await createGenerateCasesTask({
      suite_id: suiteId,
      documentContent,
    });
    const taskId = res.data?.task_id;
    if (taskId) {
      generatingMap[suiteId] = taskId;
      ElMessage.success("任务已创建，正在后台生成用例...");
      pollTaskStatus(taskId, suiteId);
    } else {
      delete generatingMap[suiteId];
    }
  } catch (e) {
    delete generatingMap[suiteId];
    ElMessage.error("创建生成任务失败");
  }
}

function pollTaskStatus(taskId, suiteId) {
  let interval = setInterval(async () => {
    try {
      const res = await getTaskStatus(taskId);
      const status = res.data?.status;
      if (status === 'completed') {
        clearInterval(interval);
        delete generatingMap[suiteId];
        ElMessage.success("用例生成完成！");
        await loadFolderTree();
        await loadCaseSets();
      } else if (status === 'failed') {
        clearInterval(interval);
        delete generatingMap[suiteId];
        ElMessage.error(res.data?.error || "用例生成失败");
      }
    } catch {
      clearInterval(interval);
      delete generatingMap[suiteId];
    }
  }, 3000);
}

function handleFolderContextMenu(event, data) {
  event.preventDefault();
  contextMenu.visible = true;
  contextMenu.x = event.clientX;
  contextMenu.y = event.clientY;
  contextMenu.data = data;
}

function hideContextMenu() {
  contextMenu.visible = false;
}

/** 仅允许拖拽真实文件夹节点，不允许拖拽「全部」虚拟节点 */
function allowFolderDrag(node) {
  const data = node.data;
  return data && !data._virtual && data.id !== 0;
}

/** 允许放入文件夹或「全部」下；不允许放入用例集或拖入自身及子孙内（type 为 prev/next/inner） */
function allowFolderDrop(draggingNode, dropNode, type) {
  const dropData = dropNode.data;
  if (dropData._virtual || dropData.id === 0) {
    return type === "inner";
  }
  if (dropData.type !== "folder") return false;
  if (type === "inner") {
    let p = dropNode;
    while (p) {
      if (p.data && p.data.id === draggingNode.data.id) return false;
      p = p.parent;
    }
  }
  return true;
}

/**
 * 文件夹拖拽放下后同步到后端并刷新树。
 * 参数：draggingNode/dropNode 为 el-tree 的 Node，dropType 为 'before'|'after'|'inner'。
 * 根据 dropType 与 dropNode 计算新 parent_id 与 sort_order。
 */
async function handleFolderDrop(draggingNode, dropNode, dropType) {
  const dragData = draggingNode?.data;
  if (!dragData || dragData._virtual || dragData.id === 0) return;
  const dragId = dragData.id;

  let parentId = null;
  let sortOrder = 1;

  if (dropType === "inner") {
    const dropData = dropNode?.data;
    if (!dropData) return;
    parentId = dropData.id === 0 ? null : dropData.id;
    const childNodes = dropNode.childNodes || [];
    const idx = childNodes.findIndex((n) => n.data && n.data.id === dragId);
    sortOrder = idx >= 0 ? idx + 1 : childNodes.length || 1;
  } else {
    const parent = dropNode?.parent;
    const parentData = parent?.data;
    parentId =
      parentData != null && parentData.id != null && parentData.id !== 0
        ? parentData.id
        : null;
    const siblings = parent?.childNodes || [];
    const dropIdx = siblings.findIndex(
      (n) => n.data && n.data.id === dropNode?.data?.id
    );
    if (dropIdx >= 0) {
      sortOrder = dropType === "before" ? dropIdx + 1 : dropIdx + 2;
    }
  }

  try {
    await updateTestSuite(dragId, { parent_id: parentId, sort_order: sortOrder });
    ElMessage.success("排序已更新");
    await loadFolderTree();
  } catch (e) {
    ElMessage.error(e?.response?.data?.message || "排序更新失败");
    await loadFolderTree();
  }
}

function reviewStatusLabel(status) {
  const map = {
    not_reviewed: "未评审",
    pending: "待评审",
    in_review: "评审中",
    completed: "已通过",
    rejected: "已拒绝",
  };
  return map[status] || "未评审";
}

function reviewStatusType(status) {
  const map = {
    not_reviewed: "info",    // 灰蓝 - 未评审
    pending: "warning",      // 橙黄 - 待评审
    in_review: "primary",   // 蓝色 - 评审中
    completed: "success",   // 绿色 - 已通过
    rejected: "danger",     // 红色 - 已拒绝
  };
  return map[status] || "info";
}

function formatTime(iso) {
  if (!iso) return "-";
  return iso.replace("T", " ").slice(0, 19);
}

/** 回收站列表：删除时间友好显示 */
function formatRecycleTime(iso) {
  if (!iso) return "-";
  const s = iso.replace("T", " ").slice(0, 19);
  const d = new Date(iso);
  const now = new Date();
  const today = now.getFullYear() === d.getFullYear() && now.getMonth() === d.getMonth() && now.getDate() === d.getDate();
  if (today) return `今天 ${s.slice(11, 16)}`;
  const yesterday = new Date(now);
  yesterday.setDate(yesterday.getDate() - 1);
  if (d.getFullYear() === yesterday.getFullYear() && d.getMonth() === yesterday.getMonth() && d.getDate() === yesterday.getDate()) return `昨天 ${s.slice(11, 16)}`;
  return s.slice(0, 16);
}

/** 回收站删除时间完整显示：年月日 时分秒 */
function formatRecycleTimeFull(iso) {
  if (!iso) return "—";
  return iso.replace("T", " ").slice(0, 19);
}

/** 回收站行悬浮提示：三行显示 所属项目、所属需求、用例数 */
function getRecycleRowTooltip(item) {
  const project = item.project_name != null && item.project_name !== "" ? item.project_name : "—";
  const requirement = item.version_requirement_name != null && item.version_requirement_name !== "" ? item.version_requirement_name : "—";
  const count = item.case_count != null ? item.case_count : "—";
  return `所属项目：${project}\n所属需求：${requirement}\n用例数：${count}`;
}

watch(showRecycleDrawer, (open) => {
  if (open) {
    recyclePagination.page = 1;
    loadRecycled();
  }
});

onMounted(() => {
  loadProjects();
  loadFolderTree();
  document.addEventListener("click", hideContextMenu);
});

// 打开生成弹窗时清空上传列表
watch(generateDialogVisible, (visible) => {
  if (!visible && generateUploadRef.value) {
    generateUploadRef.value.clearFiles();
  }
});

onBeforeUnmount(() => {
  document.removeEventListener("click", hideContextMenu);
});
</script>

<style scoped>
.test-case-management {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
  background: #fff;
}

.page-header h1 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.header-project-select {
  width: 180px;
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

  .left-panel {
  width: 220px;
  min-width: 220px;
  border-right: 1px solid #e4e7ed;
  background: #fafafa;
    display: flex;
    flex-direction: column;
  transition: width 0.2s;
}

.left-panel.collapsed {
  width: 0;
        min-width: 0;
  overflow: hidden;
  border-right: none;
}

.collapsed-expand-btn {
        display: flex;
        align-items: center;
        justify-content: center;
      width: 24px;
  min-width: 24px;
  cursor: pointer;
  background: #f0f2f5;
  border-right: 1px solid #e4e7ed;
  color: #606266;
  transition: background 0.2s;
}
.collapsed-expand-btn:hover {
  background: #e6f7ff;
  color: #409eff;
}

    .panel-header {
      display: flex;
      align-items: center;
  padding: 10px 12px;
  gap: 6px;
  border-bottom: 1px solid #e4e7ed;
}

.tree-container {
        flex: 1;
  overflow: auto;
  padding: 8px 4px;
}

.recycle-trigger {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 12px;
  border-top: 1px solid #e4e7ed;
  cursor: pointer;
  font-size: 13px;
  color: #606266;
  background: #fafafa;
}
.recycle-trigger:hover {
  background: #f0f2f5;
  color: #409eff;
}

.tree-node-label {
        display: flex;
        align-items: center;
  gap: 6px;
  font-size: 13px;
}

.right-panel {
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

.panel-content {
      flex: 1;
  display: flex;
  flex-direction: column;
  padding: 16px;
      overflow: auto;
}

.form-item-hint {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 6px;
  line-height: 1.4;
}

.table-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}
.toolbar-left-area {
  display: flex;
  align-items: center;
}

.action-btns {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2px;
  padding: 0 1px;
}
.action-btns .el-button {
  margin-left: 0;
  padding-left: 6px;
  padding-right: 6px;
}
.action-btns .el-button + .el-button {
  margin-left: 0;
}

.suite-name-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
.suite-name-cell--editing {
  width: 100%;
  min-width: 0;
  margin: 0 -6px;
  padding: 0 2px;
  justify-content: stretch;
}
.suite-name-cell--editing .el-input {
  width: 100%;
  min-width: 0;
}
.suite-name-cell--editing .el-input :deep(.el-input__wrapper) {
  padding: 4px 10px;
  border-radius: 4px;
}
.suite-name-cell .suite-name-edit-btn {
  padding: 2px 4px;
  margin-left: 2px;
  color: var(--el-text-color-secondary);
}
.suite-name-cell .suite-name-edit-btn:hover {
  color: var(--el-color-primary);
}
.generating-icon {
  color: #e6a23c;
  font-size: 14px;
}

.pagination-bar {
  display: flex;
  justify-content: flex-end;
  padding: 12px 0 0;
}

.empty-tip {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.context-menu-overlay {
  position: fixed;
  inset: 0;
  z-index: 9998;
  background: transparent;
}

.context-menu {
  position: fixed;
  z-index: 9999;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.12);
  padding: 4px 0;
  min-width: 120px;
}

.context-menu-item {
  padding: 8px 16px;
  cursor: pointer;
  font-size: 13px;
}

.context-menu-item:hover {
  background: #ecf5ff;
  color: #409eff;
}

.context-menu-item.danger:hover {
  background: #fef0f0;
  color: #f56c6c;
}

.form-tip {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

.upload-tip {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

.document-preview {
  font-size: 12px;
  color: var(--el-color-success);
  margin-top: 8px;
}

.recycle-drawer :deep(.el-drawer__body) {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 16px;
  box-sizing: border-box;
}
.recycle-list {
  padding: 0;
  min-height: 120px;
  overflow-x: hidden;
  overflow-y: auto;
  flex: 1;
  min-width: 0;
}
.recycle-table {
  width: 100%;
  max-width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  table-layout: fixed;
  box-sizing: border-box;
}
.recycle-table th,
.recycle-table td {
  padding: 10px 8px;
  border-bottom: 1px solid #ebeef5;
  vertical-align: middle;
}
.recycle-table-center th,
.recycle-table-center td {
  text-align: center;
}
.recycle-table th {
  color: var(--el-text-color-secondary);
  font-weight: 600;
  font-size: 12px;
  background: #f5f7fa;
  padding: 10px 8px;
}
.recycle-table tbody tr:hover {
  background: #fafafa;
}
.recycle-table .col-path {
  width: 24%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.recycle-table .col-name {
  width: 22%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 500;
}
.recycle-table .col-time {
  width: 12%;
  white-space: nowrap;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}
.recycle-table .col-check {
  width: 40px;
  text-align: center;
}
.recycle-toolbar {
  margin-bottom: 12px;
  flex-shrink: 0;
}
.recycle-pagination {
  margin-top: 12px;
  flex-shrink: 0;
  display: flex;
  justify-content: flex-end;
}
.recycle-table .cell-text {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.recycle-table .col-operator {
  width: 12%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 12px;
}
.recycle-table .col-actions {
  width: 22%;
  white-space: nowrap;
}
.recycle-table .col-actions .el-button {
  padding: 0 6px;
  margin-left: 0;
}
</style>

<style>
/* 回收站用例集名称 tooltip 多行显示（popper 挂载到 body，需非 scoped） */
.recycle-name-tooltip-multiline {
  white-space: pre-line;
}
</style>
