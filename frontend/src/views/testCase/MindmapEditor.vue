<template>
  <div class="mindmap-editor" @click="hideCtxMenu">
    <!-- 顶部工具栏 -->
    <div class="editor-toolbar">
      <div class="toolbar-left">
        <el-button text @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          <span class="suite-name-text">{{ suiteName }}</span>
        </el-button>
        <el-divider direction="vertical" />
        <el-dropdown trigger="click" @command="handleStatusChange">
          <span class="status-badge" :class="caseEditStatus">
            {{ statusLabel }}
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="drafting">编写中</el-dropdown-item>
              <el-dropdown-item command="completed">已完成</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <span class="case-count">{{ caseCount }} 个</span>
      </div>
      <div class="toolbar-right">
        <el-button size="small" :type="showSearch ? 'primary' : ''" @click="toggleSearchReplace">
          搜索与替换
        </el-button>
        <el-dropdown trigger="click" @command="handleExpandCollapseCommand">
          <el-button size="small">
            展开/收起 <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="expand">全部展开</el-dropdown-item>
              <el-dropdown-item command="collapse">全部折叠</el-dropdown-item>
              <el-dropdown-item command="expand-2">展开至 2 层</el-dropdown-item>
              <el-dropdown-item command="expand-3">展开至 3 层</el-dropdown-item>
              <el-dropdown-item command="collapse-1">收起至 1 层</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button size="small" @click="showVersionDrawer = true">版本记录</el-button>
      </div>
    </div>

    <!-- 搜索替换面板 -->
    <div v-if="showSearch" class="search-panel">
      <el-input v-model="searchKeyword" placeholder="搜索节点内容" size="small" clearable
        style="width: 200px" @keyup.enter="doSearch(false)" @input="searchResults = []; searchIdx = 0" />
      <el-button size="small" :disabled="!searchKeyword" @click="doSearch(false)">查找</el-button>
      <span v-if="searchResults.length" class="search-nav">
        <el-button size="small" text @click="doSearch(true, -1)">上一个</el-button>
        <span class="search-index">{{ searchIdx + 1 }} / {{ searchResults.length }}</span>
        <el-button size="small" text @click="doSearch(true, 1)">下一个</el-button>
      </span>
      <el-input v-model="replaceKeyword" placeholder="替换为" size="small" clearable
        style="width: 160px; margin-left: 8px" />
      <el-button size="small" :disabled="!searchKeyword" @click="doReplace">替换当前</el-button>
      <el-button size="small" :disabled="!searchKeyword" @click="doReplaceAll">全部替换</el-button>
      <el-button size="small" text @click="showSearch = false">
        <el-icon><Close /></el-icon>
      </el-button>
    </div>

    <!-- 生成中的全屏加载遮罩 -->
    <div v-if="isGenerating" class="generating-overlay">
      <div class="generating-content">
        <el-icon class="is-loading generating-spinner"><Loading /></el-icon>
        <p class="generating-text">{{ generatingMessage }}</p>
        <p class="generating-sub">生成完成后页面将自动刷新</p>
      </div>
    </div>

    <!-- 主体区域 -->
    <div v-show="!isGenerating" class="editor-body">
      <div ref="mindmapContainer" class="mindmap-canvas" tabindex="0" />

      <!-- 右侧属性面板 -->
      <div class="property-panel" :class="{ hidden: selectedNodes.length === 0 }">
        <!-- 优先级 -->
        <div class="prop-section">
          <div class="prop-label">优先级</div>
          <div class="priority-btns">
            <button v-for="p in priorities" :key="p.value"
              class="pri-btn" :class="{ active: currentPriority === p.value, [p.cls]: true }"
              @click="setPriority(p.value)">
              {{ p.value }}
            </button>
          </div>
        </div>

        <!-- 标记 -->
        <div class="prop-section">
          <div class="prop-label">标记</div>
          <el-select :model-value="currentMarkers" multiple collapse-tags collapse-tags-tooltip
            placeholder="选择标记" size="small" style="width: 100%" @change="setMarkers">
            <el-option v-for="m in markerOptions" :key="m.marker_name"
              :label="m.marker_name" :value="m.marker_name" />
            <template #footer>
              <div class="select-footer">
                <el-input v-model="newMarkerName" size="small" placeholder="自定义标记" />
                <el-button size="small" type="primary" :disabled="!newMarkerName.trim()"
                  @click="createCustomMarker">添加</el-button>
              </div>
            </template>
          </el-select>
        </div>

        <!-- 节点属性 -->
        <div class="prop-section">
          <div class="prop-label">节点属性</div>
          <div class="attr-grid">
            <button v-for="a in attrOptions" :key="a.value"
              class="attr-btn" :class="{ active: currentAttribute === a.value }"
              @click="setAttribute(a.value)">
              {{ a.label }}
            </button>
          </div>
        </div>

        <!-- 标签 -->
        <div class="prop-section">
          <div class="prop-label">标签</div>
          <el-select :model-value="currentTags" multiple filterable allow-create
            default-first-option collapse-tags collapse-tags-tooltip
            placeholder="搜索或创建标签" size="small" style="width: 100%"
            :no-data-text="'按回车创建该标签'" :no-match-text="'按回车创建该标签'"
            @change="setTags">
            <el-option v-for="t in tagOptions" :key="t.tag_name"
              :label="t.tag_name" :value="t.tag_name" />
          </el-select>
        </div>

      </div>
    </div>

    <!-- 版本记录抽屉（仅保存时记录） -->
    <el-drawer v-model="showVersionDrawer" title="脑图版本记录" size="400" direction="rtl">
      <div class="version-tip">仅在点击保存时记录版本，用于回退</div>
      <div v-loading="versionLoading" class="version-list">
        <div v-for="v in mindmapVersions" :key="v.id" class="version-item">
          <span class="version-meta">{{ v.created_at }} {{ v.created_by_name ? `· ${v.created_by_name}` : '' }}</span>
          <el-button size="small" type="primary" text @click="rollbackToVersion(v.id)">回退到此版本</el-button>
        </div>
        <el-empty v-if="!versionLoading && !mindmapVersions.length" description="暂无版本记录，保存后会自动记录" />
      </div>
    </el-drawer>

    <!-- 右键菜单 -->
    <Teleport to="body">
      <div v-if="ctxMenu.visible" class="ctx-menu"
        :style="{ top: ctxMenu.y + 'px', left: ctxMenu.x + 'px' }"
        @click.stop>
        <div class="ctx-item" :class="{ disabled: !ctxCanAddChild }" @click="addChildNode">
          新增子节点 <span class="shortcut">Tab</span>
        </div>
        <div class="ctx-item" :class="{ disabled: !ctxCanAddParent }" @click="addParentNode">
          新增父节点 <span class="shortcut">Shift+Tab</span>
        </div>
        <div class="ctx-item" :class="{ disabled: !ctxCanAddSibling }" @click="addSiblingNode">
          新增同级节点 <span class="shortcut">Enter</span>
        </div>
        <div class="ctx-divider" />
        <div class="ctx-item danger" @click="deleteNode">
          删除节点 <span class="shortcut">Delete</span>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onBeforeUnmount, nextTick } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ArrowLeft, ArrowDown, Close, Check, Loading } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  getMindmap, saveMindmap, validateMindmap, updateEditStatus,
  getMindmapVersions, rollbackMindmapVersion,
  getTags, getMarkers, createTag, createMarker,
} from "@/api/mindmap";
import { getTaskStatus, getSuiteGeneratingStatus } from "@/api/aiTasks";
import MindMap from "simple-mind-map";

const MAX_DEPTH = 10;
/** 用例链上的节点类型，链上节点不能添加同级；预期结果还不能添加子节点 */
const CHAIN_ATTRS = ["case_title", "test_data", "precondition", "step", "expected_result"];
/** 只能有一个子节点的链节点类型（有子节点后不能再添加） */
const ONE_CHILD_ATTRS = ["case_title", "test_data", "precondition", "step"];
/** 链上标签顺序：父节点为该标签且无子节点时，新子节点自动设为下一项 */
const CHAIN_NEXT_ATTR = { case_title: "test_data", test_data: "precondition", precondition: "step", step: "expected_result" };
const ATTR_LABEL = {
  case_title: "用例标题", test_data: "测试数据",
  precondition: "前置条件", step: "操作步骤", expected_result: "预期结果",
};
const ATTR_COLOR = { case_title: "#e6f7ff", test_data: "#f0f5ff", precondition: "#fff7e6", step: "#f6ffed", expected_result: "#fff1f0" };
const ATTR_BORDER = { case_title: "#91d5ff", test_data: "#adc6ff", precondition: "#ffd591", step: "#b7eb8f", expected_result: "#ffa39e" };
const PRI_COLOR = { P0: "#f5222d", P1: "#fa8c16", P2: "#fadb14", P3: "#1890ff" };

const route = useRoute();
const router = useRouter();

const suiteId = computed(() => Number(route.query.suite_id));
const suiteName = ref(decodeURIComponent(route.query.suite_name || "用例集"));
const mindmapContainer = ref(null);
let mindMapInstance = null;

const caseEditStatus = ref("drafting");
const caseCount = ref(0);
const projectId = ref(null);
const statusLabel = computed(() => caseEditStatus.value === "drafting" ? "编写中" : "已完成");

const showSearch = ref(false);
const searchKeyword = ref("");
const replaceKeyword = ref("");
let searchResults = [];
let searchIdx = 0;

const selectedNodes = ref([]);
const currentPriority = ref("");
const currentAttribute = ref("");
const currentMarkers = ref([]);
const currentTags = ref([]);
const newMarkerName = ref("");

const tagOptions = ref([]);
const markerOptions = ref([]);

const priorities = [
  { value: "P0", cls: "p0" },
  { value: "P1", cls: "p1" },
  { value: "P2", cls: "p2" },
  { value: "P3", cls: "p3" },
];
const attrOptions = [
  { label: "用例标题", value: "case_title" },
  { label: "测试数据", value: "test_data" },
  { label: "前置条件", value: "precondition" },
  { label: "操作步骤", value: "step" },
  { label: "预期结果", value: "expected_result" },
];

const ctxMenuChildCount = ref(0);
const ctxCanAddChild = computed(() => {
  if (currentAttribute.value === "expected_result") return false;
  if (ONE_CHILD_ATTRS.includes(currentAttribute.value) && ctxMenuChildCount.value >= 1) return false;
  return true;
});
const ctxCanAddSibling = computed(() => !CHAIN_ATTRS.includes(currentAttribute.value));
const ctxCanAddParent = computed(() => !ctxMenuIsRoot && !CHAIN_ATTRS.includes(currentAttribute.value));

const ctxMenu = reactive({ visible: false, x: 0, y: 0 });
const ctxMenuIsRoot = ref(false);
const ctxMenuTargetNode = ref(null);
let saveTimer = null;
let saving = false;
let generatingPollTimer = null;

const isGenerating = ref(route.query.generating === '1');
const generatingTaskId = ref(route.query.task_id || '');
/** 从 URL 带 generating=1 进入为“正在生成”；从列表进入发现生成中为“等待生成后查看” */
const generatingMessage = ref('AI 正在生成用例，请稍候...');
const showVersionDrawer = ref(false);
const versionLoading = ref(false);
const mindmapVersions = ref([]);
watch(showVersionDrawer, (open) => {
  if (open && suiteId.value) loadMindmapVersions();
});

async function loadMindmapVersions() {
  versionLoading.value = true;
  try {
    const res = await getMindmapVersions(suiteId.value);
    mindmapVersions.value = res.data || [];
  } catch {
    mindmapVersions.value = [];
  } finally {
    versionLoading.value = false;
  }
}

async function rollbackToVersion(versionId) {
  try {
    await ElMessageBox.confirm("回退后将用该版本替换当前脑图，是否继续？", "确认回退", { type: "warning" });
    const res = await rollbackMindmapVersion(suiteId.value, versionId);
    const data = res.data?.mindmap_data;
    if (data && mindMapInstance) {
      const smmData = toSMM(data.root || data);
      mindMapInstance.setData(smmData);
      mindMapInstance.render();
      countCases();
      showVersionDrawer.value = false;
      ElMessage.success("已回退到该版本");
    }
  } catch (e) {
    if (e !== "cancel") ElMessage.error("回退失败");
  }
}

// ── 生命周期 ──

function preventBrowserZoom(e) {
  if (e.ctrlKey || e.metaKey) {
    e.preventDefault();
    e.stopPropagation();
    if (!mindMapInstance) return;
    const cx = e.clientX;
    const cy = e.clientY;
    if (e.deltaY < 0) {
      mindMapInstance.view.enlarge(cx, cy);
    } else {
      mindMapInstance.view.narrow(cx, cy);
    }
  }
}

function preventBrowserZoomKeydown(e) {
  if ((e.ctrlKey || e.metaKey) && (e.key === '+' || e.key === '-' || e.key === '=' || e.key === '0')) {
    e.preventDefault();
  }
}

onMounted(async () => {
  // 先于脑图库注册 keydown（capture），确保 Tab/Enter 先经我们校验，不通过则拦截并提示、不创建节点
  window.addEventListener("keydown", onKeydown, true);
  document.addEventListener("keydown", preventBrowserZoomKeydown, true);
  window.addEventListener("beforeunload", onBeforeUnload);

  if (isGenerating.value) {
    startGeneratingPoll();
  } else if (suiteId.value) {
    try {
      const res = await getSuiteGeneratingStatus(suiteId.value);
      if (res.data?.generating && res.data?.task_id) {
        isGenerating.value = true;
        generatingTaskId.value = res.data.task_id;
        generatingMessage.value = '等待生成完成后查看';
        startGeneratingPoll();
      }
    } catch { /* ignore */ }
  }
  loadMindmap();

  nextTick(() => {
    const el = mindmapContainer.value;
    if (el) el.addEventListener("wheel", preventBrowserZoom, { passive: false, capture: true });
  });
});

onBeforeUnmount(() => {
  clearTimeout(saveTimer);
  clearInterval(generatingPollTimer);
  window.removeEventListener("keydown", onKeydown, true);
  document.removeEventListener("keydown", preventBrowserZoomKeydown, true);
  window.removeEventListener("beforeunload", onBeforeUnload);
  const el = mindmapContainer.value;
  if (el) el.removeEventListener("wheel", preventBrowserZoom, { capture: true });
  if (mindMapInstance) { mindMapInstance.destroy(); mindMapInstance = null; }
});

// ── 数据加载 ──

async function loadMindmap() {
  if (!suiteId.value) return;
  try {
    const res = await getMindmap(suiteId.value);
    const d = res.data || {};
    suiteName.value = d.suite_name || suiteName.value;
    caseEditStatus.value = d.case_edit_status || "drafting";
    caseCount.value = d.case_count || 0;
    projectId.value = d.project_id;
    initMindmap(d.mindmap_data);
    loadTagsAndMarkers(d.project_id);
  } catch (e) {
    if (!isGenerating.value) ElMessage.error("加载脑图数据失败");
    console.error(e);
  }
}

function startGeneratingPoll() {
  if (!generatingTaskId.value) {
    isGenerating.value = false;
    return;
  }
  generatingPollTimer = setInterval(async () => {
    try {
      const res = await getTaskStatus(generatingTaskId.value);
      const status = res.data?.status;
      if (status === 'completed') {
        clearInterval(generatingPollTimer);
        isGenerating.value = false;
        window.location.replace(
          `/mindmap-editor?suite_id=${suiteId.value}&suite_name=${encodeURIComponent(suiteName.value)}`
        );
      } else if (status === 'failed') {
        clearInterval(generatingPollTimer);
        isGenerating.value = false;
        ElMessage.error(res.data?.error || "用例生成失败");
      }
    } catch { /* keep polling */ }
  }, 3000);
}

async function loadTagsAndMarkers(pid) {
  if (!pid) return;
  try {
    const [t, m] = await Promise.all([getTags(pid), getMarkers(pid)]);
    tagOptions.value = t.data || [];
    markerOptions.value = m.data || [];
  } catch { /* silent */ }
}

// ── 节点前置标签（显示在文本左侧） ──

const BADGE_STYLES = {
  case_title: { text: '用例标题', bg: '#e6f7ff', border: '#91d5ff', color: '#1890ff' },
  test_data: { text: '测试数据', bg: '#f0f5ff', border: '#adc6ff', color: '#2f54eb' },
  precondition: { text: '前置条件', bg: '#fff7e6', border: '#ffd591', color: '#d48806' },
  step: { text: '操作步骤', bg: '#f6ffed', border: '#b7eb8f', color: '#389e0d' },
  expected_result: { text: '预期结果', bg: '#fff1f0', border: '#ffa39e', color: '#cf1322' },
};
const PRI_BADGE = {
  P0: { bg: '#fff1f0', border: '#f5222d', color: '#f5222d' },
  P1: { bg: '#fff7e6', border: '#fa8c16', color: '#fa8c16' },
  P2: { bg: '#fffbe6', border: '#d4b106', color: '#d4b106' },
  P3: { bg: '#e6f7ff', border: '#1890ff', color: '#1890ff' },
};

function buildPrefixBadges(node) {
  const d = node.getData();
  const badges = [];
  if (d.attribute && BADGE_STYLES[d.attribute]) badges.push(BADGE_STYLES[d.attribute]);
  if (d.priority && PRI_BADGE[d.priority]) badges.push({ text: d.priority, ...PRI_BADGE[d.priority] });
  if (!badges.length) return null;

  const FONT_SIZE = 11;
  const PAD_X = 5;
  const PAD_Y = 2;
  const BD = 1;
  const GAP = 4;
  const MR = 6;
  const BADGE_H = FONT_SIZE + PAD_Y * 2 + BD * 2;
  const TOTAL_H = BADGE_H + 6;

  const container = document.createElement('div');
  container.style.cssText = `display:inline-flex;align-items:center;gap:${GAP}px;margin-right:${MR}px;height:${TOTAL_H}px;`;

  let totalW = 0;
  const canvas = buildPrefixBadges._c || (buildPrefixBadges._c = document.createElement('canvas'));
  const ctx = canvas.getContext('2d');
  ctx.font = `500 ${FONT_SIZE}px sans-serif`;

  badges.forEach((b) => {
    const span = document.createElement('span');
    span.textContent = b.text;
    span.style.cssText =
      `display:inline-flex;align-items:center;justify-content:center;box-sizing:border-box;` +
      `padding:${PAD_Y}px ${PAD_X}px;border-radius:3px;font-size:${FONT_SIZE}px;line-height:1;` +
      `white-space:nowrap;background:${b.bg};border:${BD}px solid ${b.border};color:${b.color};font-weight:500;`;
    container.appendChild(span);
    totalW += Math.ceil(ctx.measureText(b.text).width) + PAD_X * 2 + BD * 2;
  });

  totalW += (badges.length - 1) * GAP + MR;
  return { el: container, width: Math.ceil(totalW), height: TOTAL_H };
}

// ── 脑图初始化 ──

function initMindmap(data) {
  if (!mindmapContainer.value) return;
  if (mindMapInstance) { mindMapInstance.destroy(); mindMapInstance = null; }

  const rootData = data?.root || { id: "root", text: suiteName.value, children: [] };
  const smmData = toSMM(rootData);

  mindMapInstance = new MindMap({
    el: mindmapContainer.value,
    data: smmData,
    theme: "classic4",
    layout: "logicalStructure",
    readonly: false,
    isDisableDrag: false,
    beforeDragStart(nodes) {
      if (!nodes?.length) return false;
      for (const node of nodes) {
        const attr = node.getData?.().attribute;
        if (CHAIN_ATTRS.includes(attr) && attr !== "case_title") {
          ElMessage.warning("仅支持拖拽「用例标题」节点，整条用例链会一起移动；链上其他节点不可单独拖拽");
          return true;
        }
      }
      return false;
    },
    createNodePrefixContent: buildPrefixBadges,
    isLimitMindMapInCanvas: false,
    enableShortcutOnlyWhenMouseInSvg: false,
    customQuickCreateChildBtnClick(node) {
      const attr = node.getData().attribute;
      if (attr === "expected_result") {
        ElMessage.warning("预期结果节点下不能添加子节点");
        return;
      }
      if (ONE_CHILD_ATTRS.includes(attr) && (node.children?.length ?? 0) >= 1) {
        ElMessage.warning("用例链节点（用例标题、测试数据、前置条件、操作步骤）只能有一个子节点，已有子节点时不可再添加");
        return;
      }
      const nextAttr = CHAIN_NEXT_ATTR[attr];
      const appointData = nextAttr ? { attribute: nextAttr } : null;
      node.mindMap.execCommand("INSERT_CHILD_NODE", true, [node], appointData);
      if (nextAttr) countCases();
    },
    marginX: 60,
    marginY: 30,
    themeConfig: {
      marginX: 60,
      marginY: 30,
      root: {
        fillColor: 'transparent',
        color: '#303133',
        borderColor: '#549688',
        borderWidth: 2,
        marginX: 60,
        marginY: 30,
      },
      second: {
        fillColor: 'transparent',
        color: '#303133',
        borderColor: '#909399',
        borderWidth: 1,
        marginX: 50,
        marginY: 26,
      },
      node: {
        fillColor: 'transparent',
        color: '#303133',
        borderColor: '#c0c4cc',
        borderWidth: 1,
        marginX: 40,
        marginY: 22,
      },
    },
  });

  // 移除库内置的 Tab/Enter/Shift+Tab/Del 快捷键，完全由我们接管
  mindMapInstance.keyCommand.removeShortcut("Tab");
  mindMapInstance.keyCommand.removeShortcut("Enter");
  mindMapInstance.keyCommand.removeShortcut("Shift+Tab");
  mindMapInstance.keyCommand.removeShortcut("Insert");
  mindMapInstance.keyCommand.removeShortcut("Del|Backspace");
  mindMapInstance.keyCommand.removeShortcut("Shift+Backspace");

  mindMapInstance.on("node_active", (_node, list) => {
    selectedNodes.value = list || [];
    if (list?.length === 1) {
      const nd = list[0].getData();
      currentPriority.value = nd.priority || "";
      currentAttribute.value = nd.attribute || "";
      currentMarkers.value = nd.markers || [];
      currentTags.value = nd.userTags || [];
    } else if (list?.length > 1) {
      currentPriority.value = "";
      currentAttribute.value = "";
      currentMarkers.value = [];
      currentTags.value = [];
    }
  });

  mindMapInstance.on("data_change", () => { countCases(); debounceSave(); });
  mindMapInstance.on("node_contextmenu", (e, node) => {
    e.preventDefault?.(); e.stopPropagation?.();
    ctxMenuTargetNode.value = node || null;
    ctxMenuIsRoot.value = node ? !!node.isRoot : false;
    ctxMenuChildCount.value = node?.children?.length ?? 0;
    if (node) {
      const nd = node.getData();
      currentAttribute.value = nd.attribute || "";
      currentPriority.value = nd.priority || "";
      currentMarkers.value = nd.markers || [];
      currentTags.value = nd.userTags || [];
    }
    ctxMenu.visible = true;
    ctxMenu.x = e.clientX ?? e.pageX ?? 0;
    ctxMenu.y = e.clientY ?? e.pageY ?? 0;
  });
  mindMapInstance.on("node_click", () => {
    ctxMenu.visible = false;
    ctxMenuTargetNode.value = null;
    ctxMenuChildCount.value = 0;
    mindmapContainer.value?.focus();
  });
  mindMapInstance.on("draw_click", () => {
    ctxMenu.visible = false;
    ctxMenuTargetNode.value = null;
    ctxMenuChildCount.value = 0;
    selectedNodes.value = [];
    mindmapContainer.value?.focus();
  });

  countCases();
}

function toSMM(node) {
  const d = {
    text: node.text || "",
    uid: node.id || undefined,
    attribute: node.attribute || undefined,
    priority: node.priority || undefined,
    markers: node.markers || undefined,
    userTags: node.tags || undefined,
    expand: node.collapsed !== true,
  };
  return { data: d, children: (node.children || []).map(toSMM) };
}

function fromSMM(smmNode) {
  const d = smmNode.data || {};
  const r = { id: d.uid || d.id || genId(), text: d.text || "" };
  if (d.expand === false) r.collapsed = true;
  if (d.attribute) r.attribute = d.attribute;
  if (d.priority) r.priority = d.priority;
  if (d.markers?.length) r.markers = d.markers;
  if (d.userTags?.length) r.tags = d.userTags;
  if (smmNode.children?.length) r.children = smmNode.children.map(fromSMM);
  return r;
}

function genId() { return "n-" + Math.random().toString(36).slice(2, 10) + Date.now().toString(36); }

// ── 用例计数 ──

function countCases() {
  if (!mindMapInstance) return;
  const data = mindMapInstance.getData();
  let n = 0;
  const walk = (node) => {
    const a = node.data?.attribute;
    if (a === "case_title") { n++; }
    else if (a === "precondition") {
      let parentAttr;
      // simple-mind-map getData 的 children 没有 parent，通过遍历判断
      // precondition 如果不在 case_title 下则独立计为一条
      n++;
    }
    (node.children || []).forEach(walk);
  };
  // 通过属性链统计：case_title 或独立 precondition
  const walkSmart = (node, parentAttr) => {
    const a = node.data?.attribute;
    if (a === "case_title") n++;
    else if (a === "precondition" && parentAttr !== "case_title") n++;
    (node.children || []).forEach((c) => walkSmart(c, a));
  };
  (data.children || []).forEach((c) => walkSmart(c, undefined));
  caseCount.value = n;
}

// ── 节点操作（链节点禁用同级/父级创建，预期结果禁用子节点创建） ──

function ensureActiveNodeForCtxMenu() {
  if (!mindMapInstance) return null;
  let nodes = mindMapInstance.renderer.activeNodeList;
  if (nodes?.length) return nodes;
  const target = ctxMenuTargetNode.value;
  if (target) {
    mindMapInstance.renderer.clearActiveNodeList();
    mindMapInstance.renderer.addNodeToActiveList(target, true);
    nodes = mindMapInstance.renderer.activeNodeList;
  }
  ctxMenuTargetNode.value = null;
  return nodes;
}

function canAddChild(nodes) {
  if (!nodes?.length) return false;
  const node = nodes[0];
  const attr = node.getData().attribute;
  if (attr === "expected_result") return false;
  if (ONE_CHILD_ATTRS.includes(attr) && (node.children?.length ?? 0) >= 1) return false;
  if (getDepth(node) >= MAX_DEPTH - 1) return false;
  return true;
}

/** 不可添加子节点时返回提示文案，否则返回 null */
function getAddChildBlockMessage(nodes) {
  if (!nodes?.length) return "请先选中节点";
  const node = nodes[0];
  const attr = node.getData().attribute;
  if (attr === "expected_result") return "预期结果节点下不能添加子节点";
  if (ONE_CHILD_ATTRS.includes(attr) && (node.children?.length ?? 0) >= 1)
    return "用例链节点（用例标题、测试数据、前置条件、操作步骤）只能有一个子节点，已有子节点时不可再添加";
  if (getDepth(node) >= MAX_DEPTH - 1) return `已达到最大层级限制（${MAX_DEPTH} 层）`;
  return null;
}

function canAddSibling(nodes) {
  if (!nodes?.length) return false;
  if (nodes[0].isRoot) return false;
  return !CHAIN_ATTRS.includes(nodes[0].getData().attribute);
}

/** 不可添加同级节点时返回提示文案，否则返回 null */
function getAddSiblingBlockMessage(nodes) {
  if (!nodes?.length) return "请先选中节点";
  if (nodes[0].isRoot) return "根节点不能添加同级节点";
  if (CHAIN_ATTRS.includes(nodes[0].getData().attribute))
    return "用例链上的节点（用例标题、测试数据、前置条件、操作步骤、预期结果）不能添加同级节点";
  return null;
}

function canAddParent(nodes) {
  if (!nodes?.length) return false;
  if (nodes[0].isRoot) return false;
  return !CHAIN_ATTRS.includes(nodes[0].getData().attribute);
}

/** 不可添加父节点时返回提示文案，否则返回 null */
function getAddParentBlockMessage(nodes) {
  if (!nodes?.length) return "请先选中节点";
  if (nodes[0].isRoot) return "根节点不能添加父节点";
  if (CHAIN_ATTRS.includes(nodes[0].getData().attribute))
    return "用例链上的节点不能添加父节点";
  return null;
}

function addChildNode() {
  ctxMenu.visible = false;
  const nodes = ensureActiveNodeForCtxMenu();
  if (!nodes?.length) return;
  const blockMsg = getAddChildBlockMessage(nodes);
  if (blockMsg) {
    ElMessage.warning(blockMsg);
    return;
  }
  const parentAttr = nodes[0].getData().attribute;
  const nextAttr = CHAIN_NEXT_ATTR[parentAttr];
  const appointData = nextAttr ? { attribute: nextAttr } : null;
  mindMapInstance.execCommand("INSERT_CHILD_NODE", true, [], appointData);
  if (nextAttr) countCases();
}

function addParentNode() {
  ctxMenu.visible = false;
  const nodes = ensureActiveNodeForCtxMenu();
  if (!nodes?.length) return;
  const blockMsg = getAddParentBlockMessage(nodes);
  if (blockMsg) {
    ElMessage.warning(blockMsg);
    return;
  }

  const node = nodes[0];
  const fullData = mindMapInstance.getData();
  const uid = node.getData().uid;
  const wrapped = wrapNode(fullData, uid);
  if (wrapped) {
    mindMapInstance.setData(fullData);
    mindMapInstance.render();
  }
}

function wrapNode(parent, targetUid) {
  if (!parent.children) return false;
  for (let i = 0; i < parent.children.length; i++) {
    const child = parent.children[i];
    if (child.data?.uid === targetUid) {
      parent.children[i] = {
        data: { text: "新节点", uid: genId(), expand: true },
        children: [child],
      };
      return true;
    }
    if (wrapNode(child, targetUid)) return true;
  }
  return false;
}

function addSiblingNode() {
  ctxMenu.visible = false;
  const nodes = ensureActiveNodeForCtxMenu();
  if (!nodes?.length) return;
  const blockMsg = getAddSiblingBlockMessage(nodes);
  if (blockMsg) {
    ElMessage.warning(blockMsg);
    return;
  }
  mindMapInstance.execCommand("INSERT_NODE");
}

function deleteNode() {
  ctxMenu.visible = false;
  const nodes = ensureActiveNodeForCtxMenu();
  if (!nodes?.length) return;
  if (nodes[0].isRoot) return;
  mindMapInstance.execCommand("REMOVE_NODE");
}

function getDepth(node) {
  let d = 0, n = node;
  while (n?.parent) { d++; n = n.parent; }
  return d;
}

// ── 属性 / 优先级 / 标记 / 标签 ──

function setPriority(p) {
  if (!mindMapInstance) return;
  const nodes = mindMapInstance.renderer.activeNodeList;
  if (!nodes?.length) return;
  const toggle = nodes.length === 1 && nodes[0].getData().priority === p;
  const val = toggle ? undefined : p;
  nodes.forEach((n) => {
    n.setData({ priority: val });
    rebuildTag(n);
  });
  currentPriority.value = val || "";
  mindMapInstance.render();
}

function setAttribute(attr) {
  if (!mindMapInstance) return;
  const nodes = mindMapInstance.renderer.activeNodeList;
  if (!nodes?.length) return;
  nodes.forEach((n) => {
    const cur = n.getData().attribute;
    n.setData({ attribute: cur === attr ? undefined : attr });
  });
  currentAttribute.value = nodes.length === 1 ? (nodes[0].getData().attribute || "") : "";
  mindMapInstance.render();
  countCases();
}

function setMarkers(val) {
  if (!mindMapInstance) return;
  mindMapInstance.renderer.activeNodeList?.forEach((n) => n.setData({ markers: [...val] }));
  currentMarkers.value = [...val];
  mindMapInstance.render();
}

function setTags(val) {
  if (!mindMapInstance) return;
  mindMapInstance.renderer.activeNodeList?.forEach((n) => n.setData({ userTags: [...val] }));
  currentTags.value = [...val];

  val.forEach((t) => {
    if (!tagOptions.value.some((o) => o.tag_name === t)) {
      tagOptions.value.push({ tag_name: t, tag_color: "#409EFF" });
      if (projectId.value) createTag({ tag_name: t, project_id: projectId.value }).catch(() => {});
    }
  });
  mindMapInstance.render();
}

async function createCustomMarker() {
  const name = newMarkerName.value.trim();
  if (!name || !projectId.value) return;
  try {
    await createMarker({ marker_name: name, project_id: projectId.value });
    markerOptions.value.push({ marker_name: name, marker_type: "custom" });
    newMarkerName.value = "";
  } catch { ElMessage.error("创建标记失败"); }
}

function rebuildTag() {
  // prefix badges via createNodePrefixContent handle visual display
}

// ── 状态 ──

async function handleStatusChange(status) {
  caseEditStatus.value = status;
  try { await updateEditStatus(suiteId.value, { case_edit_status: status }); } catch {}
}

// ── 展开/收起 n 层 ──

function handleExpandCollapseCommand(cmd) {
  if (!mindMapInstance) return;
  if (cmd === "expand") {
    mindMapInstance.execCommand("EXPAND_ALL");
    return;
  }
  if (cmd === "collapse") {
    mindMapInstance.execCommand("UNEXPAND_ALL");
    return;
  }
  const expandMatch = /^expand-(\d+)$/.exec(cmd);
  const collapseMatch = /^collapse-(\d+)$/.exec(cmd);
  const level = expandMatch ? parseInt(expandMatch[1], 10) : collapseMatch ? parseInt(collapseMatch[1], 10) : 0;
  if (level >= 1) mindMapInstance.execCommand("UNEXPAND_TO_LEVEL", level);
}

// ── 搜索替换 ──

function toggleSearchReplace() { showSearch.value = !showSearch.value; }

/** goNext: 是否在已有结果中上/下一个；delta: -1 上一个，1 下一个 */
function doSearch(goNext, delta) {
  if (!mindMapInstance || !searchKeyword.value) return;
  const keyword = searchKeyword.value;
  if (!goNext || !searchResults.length) {
    searchResults = [];
    searchIdx = 0;
    const walk = (node) => {
      if (node.getData?.() && (node.getData().text || "").includes(keyword)) searchResults.push(node);
      (node.children || []).forEach(walk);
    };
    walk(mindMapInstance.renderer.root);
  }
  if (!searchResults.length) {
    ElMessage.info("未找到匹配项");
    return;
  }
  if (goNext && delta) {
    searchIdx = (searchIdx + delta + searchResults.length) % searchResults.length;
  }
  mindMapInstance.execCommand("GO_TARGET_NODE", searchResults[searchIdx]);
  ElMessage.success(`找到 ${searchResults.length} 个匹配，当前 ${searchIdx + 1}/${searchResults.length}`);
}

function doReplace() {
  if (!mindMapInstance || !searchKeyword.value) return;
  const nodes = mindMapInstance.renderer.activeNodeList;
  if (!nodes?.length) return;
  let count = 0;
  nodes.forEach((n) => {
    const t = n.getData().text || "";
    if (t.includes(searchKeyword.value)) {
      n.setData({ text: t.replace(searchKeyword.value, replaceKeyword.value) });
      count++;
    }
  });
  if (count) mindMapInstance.render();
  ElMessage.success(`替换了 ${count} 处`);
}

function doReplaceAll() {
  if (!mindMapInstance || !searchKeyword.value) return;
  let count = 0;
  const walk = (node) => {
    const t = node.getData?.()?.text || "";
    if (t.includes(searchKeyword.value)) {
      node.setData({ text: t.replaceAll(searchKeyword.value, replaceKeyword.value) });
      count++;
    }
    node.children?.forEach(walk);
  };
  walk(mindMapInstance.renderer.root);
  if (count) mindMapInstance.render();
  ElMessage.success(`全部替换了 ${count} 个节点`);
}

// ── 保存 ──

function debounceSave() {
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => doSave(true), 3000);
}

async function handleSave() {
  clearTimeout(saveTimer);

  const smmData = mindMapInstance?.getData();
  if (!smmData) return;
  const json = { version: "2.0", root: fromSMM(smmData), metadata: {} };
  const res = await validateMindmap(suiteId.value, { mindmap_data: json }).catch(() => null);
  if (res?.data?.valid === false && res.data.errors?.length) {
    ElMessageBox.alert(
      res.data.errors.map((e, i) => `${i + 1}. ${e}`).join("\n"),
      "用例不符合规范，请检查用例后再保存",
      { type: "warning", confirmButtonText: "知道了", dangerouslyUseHTMLString: false }
    );
    return;
  }
  await doSave(false);
}

async function doSave(silent) {
  if (!mindMapInstance || !suiteId.value || saving) return;
  saving = true;
  const smmData = mindMapInstance.getData();
  const json = { version: "2.0", root: fromSMM(smmData), metadata: {} };
  try {
    const res = await saveMindmap(suiteId.value, { mindmap_data: json, case_edit_status: caseEditStatus.value });
    if (!silent) ElMessage.success("保存成功");
    caseCount.value = res.data?.case_count ?? caseCount.value;
  } catch (e) {
    if (!silent) ElMessage.error("保存失败");
    console.error(e);
  } finally { saving = false; }
}

// ── 键盘快捷键 ──

function onKeydown(e) {
  if ((e.ctrlKey || e.metaKey) && e.key === "s") { e.preventDefault(); handleSave(); return; }

  if (!mindMapInstance) return;
  // 仅当焦点在脑图画布内时响应快捷键，避免在工具栏输入框等处误触发
  const el = mindmapContainer.value;
  if (el && document.activeElement && !el.contains(document.activeElement)) return;

  // Ctrl+Z 撤回 / Ctrl+Y 或 Ctrl+Shift+Z 重做
  if (e.ctrlKey || e.metaKey) {
    if (e.key === "z" && !e.shiftKey) {
      e.preventDefault();
      e.stopPropagation();
      mindMapInstance.execCommand("BACK");
      return;
    }
    if (e.key === "z" && e.shiftKey || e.key === "y") {
      e.preventDefault();
      e.stopPropagation();
      mindMapInstance.execCommand("FORWARD");
      return;
    }
  }

  const active = mindMapInstance.renderer.activeNodeList;
  if (!active?.length) return;

  // 正在编辑节点文本时不拦截
  if (mindMapInstance.renderer?.textEditNode) return;

  if (e.key === "Tab") {
    e.preventDefault();
    e.stopPropagation();
    if (e.shiftKey) {
      addParentNode();
    } else {
      addChildNode();
    }
    return;
  }
  if (e.key === "Enter" && !e.shiftKey && !e.ctrlKey) {
    e.preventDefault();
    e.stopPropagation();
    addSiblingNode();
    return;
  }
  if (e.key === "Delete" || e.key === "Backspace") {
    if (!active[0].isRoot) {
      e.preventDefault();
      e.stopPropagation();
      deleteNode();
    }
  }
}

function onBeforeUnload() {
  if (mindMapInstance && suiteId.value) doSave(true);
}

function goBack() {
  window.close();
  if (!window.closed) router.push("/test-cases");
}

function hideCtxMenu() {
  ctxMenu.visible = false;
  ctxMenuTargetNode.value = null;
  ctxMenuChildCount.value = 0;
}
</script>

<style scoped>
.mindmap-editor {
  position: fixed;
  inset: 0;
  z-index: 100;
  background: #fff;
  display: flex;
  flex-direction: column;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* ── 工具栏 ── */
.editor-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 16px;
  border-bottom: 1px solid #e4e7ed;
  background: #fff;
  flex-shrink: 0;
  height: 44px;
}
.toolbar-left, .toolbar-right { display: flex; align-items: center; gap: 8px; }
.suite-name-text { font-size: 14px; font-weight: 500; margin-left: 2px; }
.status-badge {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 2px 12px; border-radius: 12px; font-size: 13px;
  cursor: pointer; user-select: none; line-height: 22px;
}
.status-badge.drafting { background: #e6f7ff; color: #1890ff; }
.status-badge.completed { background: #f6ffed; color: #52c41a; }
.case-count { font-size: 13px; color: #909399; white-space: nowrap; }

/* ── 搜索面板 ── */
.search-panel {
  display: flex; align-items: center; gap: 6px;
  padding: 8px 16px; background: #fafafa;
  border-bottom: 1px solid #e4e7ed; flex-shrink: 0;
}
.search-nav { display: inline-flex; align-items: center; gap: 4px; margin-left: 4px; }
.search-index { font-size: 12px; color: #909399; min-width: 48px; text-align: center; }

/* ── 版本记录 ── */
.version-tip { font-size: 12px; color: #909399; padding: 8px 12px; border-bottom: 1px solid #ebeef5; }
.version-list { padding: 0 8px; }
.version-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 12px; border-bottom: 1px solid #ebeef5;
}
.version-meta { font-size: 13px; color: #606266; }

/* ── 主体 ── */
.editor-body { flex: 1; display: flex; min-height: 0; overflow: visible; }
.mindmap-canvas { flex: 1; min-width: 0; background: #f5f5f5; overflow: visible; outline: none; }

/* ── 右侧属性面板 ── */
.property-panel {
  width: 220px; min-width: 220px;
  border-left: 1px solid #e4e7ed;
  padding: 16px 14px; overflow-y: auto;
  background: #fff; transition: width .2s;
}
.property-panel.hidden { width: 0; min-width: 0; padding: 0; border: none; overflow: hidden; }

.prop-section { margin-bottom: 18px; }
.prop-label { font-size: 13px; font-weight: 600; color: #303133; margin-bottom: 8px; }

.priority-btns { display: flex; gap: 6px; }
.pri-btn {
  width: 40px; height: 30px; border: 1px solid #dcdfe6; border-radius: 4px;
  background: #fff; cursor: pointer; font-size: 12px; font-weight: 600;
  transition: all .15s;
}
.pri-btn:hover { border-color: #409eff; }
.pri-btn.active.p0 { background: #f5222d; color: #fff; border-color: #f5222d; }
.pri-btn.active.p1 { background: #fa8c16; color: #fff; border-color: #fa8c16; }
.pri-btn.active.p2 { background: #fadb14; color: #333; border-color: #fadb14; }
.pri-btn.active.p3 { background: #1890ff; color: #fff; border-color: #1890ff; }

.attr-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.attr-btn {
  padding: 6px 0; border: 1px solid #dcdfe6; border-radius: 4px;
  background: #fff; cursor: pointer; font-size: 12px; text-align: center;
  transition: all .15s;
}
.attr-btn:hover { border-color: #409eff; color: #409eff; }
.attr-btn.active { background: #ecf5ff; border-color: #409eff; color: #409eff; }

.select-footer { display: flex; gap: 6px; padding: 6px 8px; }

/* ── 右键菜单 ── */
.ctx-menu {
  position: fixed; z-index: 10000; background: #fff;
  border: 1px solid #e4e7ed; border-radius: 6px;
  box-shadow: 0 4px 16px rgba(0,0,0,.12); padding: 4px 0; min-width: 210px;
}
.ctx-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 8px 16px; cursor: pointer; font-size: 13px;
}
.ctx-item:not(.disabled):hover { background: #ecf5ff; color: #409eff; }
.ctx-item.danger:not(.disabled):hover { background: #fef0f0; color: #f56c6c; }
.ctx-item.disabled { color: #c0c4cc; cursor: not-allowed; }
.ctx-divider { height: 1px; background: #e4e7ed; margin: 4px 0; }
.shortcut { color: #c0c4cc; font-size: 12px; }
</style>

<style>
/* 全局覆盖 simple-mind-map 节点样式（库内部 SVG/DOM 不受 scoped 影响） */

/* 节点文本编辑框 — 透明背景，仅显示光标 */
.smm-node-edit-wrap,
.smm-node-text-edit-wrap,
.smm-richtext-node-edit-wrap {
  background: transparent !important;
  box-shadow: none !important;
  outline: none !important;
}

/* 编辑框内的 contenteditable 区域 */
.smm-node-edit-wrap [contenteditable],
.smm-richtext-node-edit-wrap [contenteditable] {
  background: transparent !important;
  caret-color: #303133;
}

/* 节点形状 SVG — 不做 transition 避免闪烁 */
.smm-node .smm-node-shape {
  transition: none !important;
}
</style>

<style scoped>
/* ── 生成中遮罩 ── */
.generating-overlay {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
}
.generating-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}
.generating-spinner {
  font-size: 48px;
  color: #e6a23c;
}
.generating-text {
  font-size: 18px;
  font-weight: 500;
  color: #303133;
  margin: 0;
}
.generating-sub {
  font-size: 14px;
  color: #909399;
  margin: 0;
}
</style>
