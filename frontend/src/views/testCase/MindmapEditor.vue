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
        <el-tooltip content="撤销" placement="bottom">
          <el-button size="small" :disabled="!canUndo" @click="handleUndo">
            <el-icon><RefreshLeft /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="前进" placement="bottom">
          <el-button size="small" :disabled="!canRedo" @click="handleRedo">
            <el-icon><RefreshRight /></el-icon>
          </el-button>
        </el-tooltip>
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
        <el-tooltip content="检查更新" placement="bottom">
          <el-button size="small" @click="handleCheckUpdate">
            <el-icon><Upload /></el-icon>
          </el-button>
        </el-tooltip>
        <el-button size="small" @click="openNumberSetting">编号设置</el-button>
        <el-button size="small" @click="showVersionDrawer = true">版本记录</el-button>
      </div>
    </div>

    <!-- 用例编号设置对话框 -->
    <el-dialog v-model="showNumberSettingDialog" title="用例编号设置" width="420px" :close-on-click-modal="false">
      <div class="number-setting-body">
        <div class="number-setting-tip">
          设置用例编号前缀，新增用例将自动以该前缀递增编号（如 TC-001、TC-002）；
          已有编号的用例不会被覆盖。
        </div>
        <div class="number-setting-row">
          <span class="number-setting-label">编号前缀</span>
          <el-input
            v-model="tempCaseNumberPrefix"
            placeholder="如 TC-、MOB-、TEST_"
            size="small"
            style="width: 180px"
            maxlength="20"
            show-word-limit
            clearable
          />
        </div>
        <div class="number-setting-preview">
          预览：<strong>{{ (tempCaseNumberPrefix || 'TC-').trim() || 'TC-' }}001</strong>、
          <strong>{{ (tempCaseNumberPrefix || 'TC-').trim() || 'TC-' }}002</strong> …
        </div>
      </div>
      <template #footer>
        <el-button @click="showNumberSettingDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmNumberSetting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 搜索替换与高级筛选面板 -->
    <div v-if="showSearch" class="search-panel">
      <div class="search-row">
        <el-input v-model="searchKeyword" placeholder="按关键词筛选" size="small" clearable
          style="width: 200px" @keyup.enter="doSearch(false)"
          @input="searchResults = []; searchIdx = 0"
          @clear="searchResults = []; searchIdx = 0" />
        <el-button size="small" :disabled="!searchKeyword" @click="doSearch(false)">查找</el-button>
        <span v-if="searchResults.length" class="search-nav">
          <el-button size="small" text @click="doSearch(true, -1)">上一个</el-button>
          <span class="search-index">{{ searchIdx + 1 }} / {{ searchResults.length }}</span>
          <el-button size="small" text @click="doSearch(true, 1)">下一个</el-button>
        </span>
        <el-popover :visible="showAdvancedFilter" placement="bottom-start" :width="420" trigger="click"
          @update:visible="(v) => (showAdvancedFilter = v)">
          <template #reference>
            <el-button size="small" :type="hasAdvancedFilterActive ? 'primary' : ''">
              更多筛选 {{ showAdvancedFilter ? '▲' : '▼' }}
            </el-button>
          </template>
          <div class="advanced-filter-popover">
            <div class="filter-group">
              <div class="filter-group-label">节点类型</div>
              <div class="filter-tags">
                <el-check-tag v-for="a in filterNodeTypeOptions" :key="a.value"
                  :checked="advancedFilter.nodeType.includes(a.value)"
                  @change="(checked) => toggleFilterNodeType(a.value, checked)">
                  {{ a.label }}
                </el-check-tag>
              </div>
            </div>
            <div class="filter-group">
              <div class="filter-group-label">优先级</div>
              <div class="filter-tags">
                <el-check-tag v-for="p in priorities" :key="p.value"
                  :checked="advancedFilter.priority === p.value"
                  @change="(checked) => advancedFilter.priority = checked ? p.value : ''">
                  {{ p.value }}
                </el-check-tag>
              </div>
            </div>
            <div class="filter-group">
              <div class="filter-group-label">标记</div>
              <div class="filter-tags wrap">
                <el-check-tag v-for="m in markerOptions" :key="m.marker_name"
                  :checked="advancedFilter.markers.includes(m.marker_name)"
                  @change="(checked) => toggleFilterArr(advancedFilter.markers, m.marker_name, checked)">
                  {{ m.marker_name }}
                </el-check-tag>
              </div>
            </div>
            <div class="filter-group">
              <div class="filter-group-label">标签</div>
              <div class="filter-tags wrap">
                <el-check-tag v-for="t in tagOptions" :key="t.tag_name"
                  :checked="advancedFilter.tags.includes(t.tag_name)"
                  @change="(checked) => toggleFilterArr(advancedFilter.tags, t.tag_name, checked)">
                  {{ t.tag_name }}
                </el-check-tag>
              </div>
            </div>
            <div class="filter-group">
              <div class="filter-group-label">涉及自动化</div>
              <div class="filter-tags">
                <el-check-tag v-for="opt in automationOptions" :key="opt.value"
                  :checked="advancedFilter.automation === opt.value"
                  @change="(checked) => advancedFilter.automation = checked ? opt.value : ''">
                  {{ opt.label }}
                </el-check-tag>
              </div>
            </div>
            <div class="filter-group">
              <div class="filter-group-label">用例覆盖端</div>
              <div class="filter-tags wrap">
                <el-check-tag v-for="opt in coverageOptions" :key="opt.value"
                  :checked="advancedFilter.coverage.includes(opt.value)"
                  @change="(checked) => toggleFilterArr(advancedFilter.coverage, opt.value, checked)">
                  {{ opt.label }}
                </el-check-tag>
              </div>
            </div>
            <div class="filter-group">
              <div class="filter-group-label">公私网海外</div>
              <div class="filter-tags wrap">
                <el-check-tag v-for="opt in networkOptions" :key="opt.value"
                  :checked="advancedFilter.network.includes(opt.value)"
                  @change="(checked) => toggleFilterArr(advancedFilter.network, opt.value, checked)">
                  {{ opt.label }}
                </el-check-tag>
              </div>
            </div>
            <div class="filter-actions">
              <el-button size="small" @click="clearAdvancedFilter">清除筛选</el-button>
              <el-button size="small" type="primary" @click="applyAdvancedFilter">筛选查找</el-button>
            </div>
          </div>
        </el-popover>
        <span v-if="filterResults.length" class="search-nav">
          <el-button size="small" text @click="goFilterResult(-1)">上一个</el-button>
          <span class="search-index">{{ filterIdx + 1 }} / {{ filterResults.length }}</span>
          <el-button size="small" text @click="goFilterResult(1)">下一个</el-button>
        </span>
        <el-input v-model="replaceKeyword" placeholder="替换为" size="small" clearable
          style="width: 160px; margin-left: 8px" />
        <el-button size="small" :disabled="!searchKeyword" @click="doReplace">替换当前</el-button>
        <el-button size="small" :disabled="!searchKeyword" @click="doReplaceAll">全部替换</el-button>
        <el-button size="small" text @click="showSearch = false">
          <el-icon><Close /></el-icon>
        </el-button>
      </div>
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
      <div class="mindmap-wrap">
        <div ref="mindmapContainer" class="mindmap-canvas" tabindex="0" />
      </div>

      <!-- 右侧属性面板：固定后始终显示面板组件，未选中节点时也显示（空状态） -->
      <div class="property-panel" :class="{ hidden: !isPropertyPanelVisible }">
        <div class="property-panel-header">
          <el-tooltip :content="propertyPanelPinned ? '取消固定' : '固定面板（固定后不随节点选中关闭）'" placement="bottom">
            <el-button size="small" :type="propertyPanelPinned ? 'primary' : ''" text
              @click="propertyPanelPinned = !propertyPanelPinned">
              <el-icon><Unlock v-if="propertyPanelPinned" /><Lock v-else /></el-icon>
            </el-button>
          </el-tooltip>
        </div>
        <div class="property-panel-body">
          <!-- 未选中节点：固定面板时仍显示完整面板组件，但不显示任何选中节点的值，控件为占位/禁用 -->
          <template v-if="selectedNodes.length === 0">
            <div class="prop-section prop-section-first">
              <div class="prop-label">节点内容</div>
              <el-input :model-value="''" placeholder="未选中节点" size="small" disabled class="node-content-textarea" />
            </div>
            <div class="prop-section">
              <div class="prop-label">优先级 <span class="prop-hint">（仅用例标题）</span></div>
              <div class="priority-btns">
                <button v-for="p in priorities" :key="p.value" class="pri-btn" :class="[p.cls]" disabled>{{ p.value }}</button>
              </div>
            </div>
            <div class="prop-section">
              <div class="prop-label">标记 <span class="prop-hint">（非自定义标记唯一）</span></div>
              <el-select model-value="[]" placeholder="未选中节点" size="small" style="width: 100%" disabled />
            </div>
            <div class="prop-section">
              <div class="prop-label">节点属性</div>
              <div class="attr-readonly">—</div>
            </div>
            <div class="prop-section">
              <div class="prop-label">标签</div>
              <el-select model-value="[]" placeholder="未选中节点" size="small" style="width: 100%" disabled />
            </div>
          </template>
          <template v-else>
            <!-- 节点内容：单行显示，可拖拽右下角变为多行（仅单选时可编辑） -->
            <div v-if="selectedNodes.length === 1" class="prop-section prop-section-first">
              <div class="prop-label">节点内容</div>
              <el-input
                v-model="currentNodeText"
                type="textarea"
                placeholder="修改节点文字"
                :autosize="{ minRows: 1, maxRows: 8 }"
                size="small"
                clearable
                class="node-content-textarea"
                @blur="applyNodeText"
                @keyup.enter.exact.prevent="applyNodeText"
              />
            </div>
            <div class="prop-section">
              <div class="prop-label">优先级 <span v-if="!canSetPriority" class="prop-hint">（仅用例标题）</span></div>
              <div class="priority-btns">
                <button v-for="p in priorities" :key="p.value"
                  class="pri-btn" :class="{ active: currentPriority === p.value, [p.cls]: true }"
                  :disabled="!canSetPriority"
                  @click="setPriority(p.value)">
                  {{ p.value }}
                </button>
              </div>
            </div>
            <div class="prop-section">
              <div class="prop-label">标记 <span class="prop-hint">（非自定义标记唯一）</span></div>
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
            <div class="prop-section">
              <div class="prop-label">节点属性</div>
              <div v-if="canChangeAttribute" class="attr-grid">
                <button v-for="a in attributeOptionsForChainChild" :key="a.value"
                  class="attr-btn" :class="{ active: currentAttribute === a.value }"
                  @click="setAttribute(a.value)">
                  {{ a.label }}
                </button>
              </div>
              <div v-else-if="isChainNodeAttrReadonly" class="attr-readonly">
                {{ ATTR_LABEL[currentAttribute] || '—' }}
              </div>
              <div v-else class="attr-grid">
                <button v-for="a in attrOptions" :key="a.value"
                  class="attr-btn" :class="{ active: currentAttribute === a.value }"
                  @click="setAttribute(a.value)">
                  {{ a.label }}
                </button>
              </div>
            </div>
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
            <!-- 用例编号：仅用例标题节点可设置 -->
            <div v-if="selectedNodes.length === 1 && currentAttribute === 'case_title'" class="prop-section">
              <div class="prop-label">
                用例编号
                <span class="prop-hint">（留空则自动生成）</span>
              </div>
              <el-input
                v-model="currentCaseNumber"
                placeholder="如 TC-001，留空自动生成"
                size="small"
                clearable
                @blur="applyCaseNumber"
                @keyup.enter.exact.prevent="applyCaseNumber"
              />
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- 版本记录抽屉（仅保存时记录） -->
    <el-drawer v-model="showVersionDrawer" title="脑图版本记录" size="400" direction="rtl">
      <div class="version-tip">仅在点击保存时记录版本，用于回退</div>
      <div v-loading="versionLoading" class="version-list">
        <div v-for="v in mindmapVersions" :key="v.id" class="version-item">
          <span class="version-meta">{{ formatVersionTime(v.created_at) }} {{ v.created_by_name ? `· ${v.created_by_name}` : '' }}</span>
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
import { ArrowLeft, ArrowDown, Close, Check, Loading, RefreshRight, RefreshLeft, Upload, Lock, Unlock } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  getMindmap, getMindmapVersion, saveMindmap, validateMindmap, updateEditStatus,
  getMindmapVersions, rollbackMindmapVersion,
  getTags, getMarkers, createTag, createMarker,
} from "@/api/mindmap";
import { getTaskStatus, getSuiteGeneratingStatus } from "@/api/aiTasks";
import MindMap from "simple-mind-map";
import Drag from "simple-mind-map/src/plugins/Drag.js";

MindMap.usePlugin(Drag);

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
const caseNumberPrefix = ref("TC-");
const currentCaseNumber = ref("");
const showNumberSettingDialog = ref(false);
const tempCaseNumberPrefix = ref("TC-");
const statusLabel = computed(() => caseEditStatus.value === "drafting" ? "编写中" : "已完成");

const showSearch = ref(false);
const searchKeyword = ref("");
const replaceKeyword = ref("");
const searchResults = ref([]);
const searchIdx = ref(0);
const filterTags = ref([]);
const filterMarkers = ref([]);
const filterPriority = ref("");
const filterResults = ref([]);
const filterIdx = ref(0);

const showAdvancedFilter = ref(false);
const advancedFilter = reactive({
  nodeType: [],
  priority: "",
  markers: [],
  tags: [],
  automation: "",
  coverage: [],
  network: [],
});
const filterNodeTypeOptions = [
  { label: "用例标题", value: "case_title" },
  { label: "测试数据", value: "test_data" },
  { label: "前置条件", value: "precondition" },
  { label: "操作步骤", value: "step" },
  { label: "预期结果", value: "expected_result" },
];
const automationOptions = [
  { label: "接口自动化", value: "api" },
  { label: "UI自动化", value: "ui" },
  { label: "不涉及", value: "none" },
];
const coverageOptions = [
  { label: "三端", value: "all" },
  { label: "仅PC", value: "pc" },
  { label: "仅移动端", value: "mobile" },
  { label: "Web", value: "web" },
  { label: "Pad", value: "pad" },
  { label: "仅Android", value: "android" },
  { label: "仅IOS", value: "ios" },
];
const networkOptions = [
  { label: "仅公网", value: "public" },
  { label: "仅私网", value: "private" },
  { label: "仅海外", value: "overseas" },
  { label: "无差异", value: "none" },
  { label: "公私网实现不一致", value: "inconsistent" },
];
const hasAdvancedFilterActive = computed(() =>
  advancedFilter.nodeType.length > 0 || advancedFilter.priority ||
  advancedFilter.markers.length > 0 || advancedFilter.tags.length > 0 ||
  advancedFilter.automation || advancedFilter.coverage.length > 0 || advancedFilter.network.length > 0
);

const canUndo = ref(false);
const canRedo = ref(false);
const currentNodeText = ref("");

const selectedNodes = ref([]);
/** 固定节点编辑面板：为 true 时面板始终显示，不随节点选中/取消而关闭 */
const propertyPanelPinned = ref(false);
/** 是否显示右侧属性面板：固定时始终显示，未固定时仅选中节点时显示 */
const isPropertyPanelVisible = computed(() => propertyPanelPinned.value || selectedNodes.value.length > 0);
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

const canSetPriority = computed(() => selectedNodes.value.length === 1 && currentAttribute.value === "case_title");

/** 仅当选中「用例标题」的直接子节点且为测试数据/前置条件时，允许在二者间切换；其他用例链节点属性固定不可改 */
const canChangeAttribute = computed(() => {
  const list = mindMapInstance?.renderer?.activeNodeList;
  if (!list?.length || list.length > 1) return false;
  const node = list[0];
  const attr = node.getData?.().attribute;
  const parentAttr = node.parent?.getData?.().attribute;
  return parentAttr === "case_title" && (attr === "test_data" || attr === "precondition");
});

const attributeOptionsForChainChild = [
  { label: "测试数据", value: "test_data" },
  { label: "前置条件", value: "precondition" },
];

/** 用例链节点且不可改属性时显示为只读文案 */
const isChainNodeAttrReadonly = computed(() => {
  if (selectedNodes.value.length !== 1) return false;
  const attr = currentAttribute.value;
  return CHAIN_ATTRS.includes(attr) && !canChangeAttribute.value;
});

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
/** 脑图版本号，用于多人编辑冲突检测与轮询 */
const mindmapVersion = ref(0);
/** 多人编辑：轮询检测他人是否已保存（30 秒一次） */
const VERSION_POLL_INTERVAL = 30 * 1000;
let versionPollTimer = null;
const showVersionDrawer = ref(false);
const versionLoading = ref(false);
const mindmapVersions = ref([]);
watch(showVersionDrawer, (open) => {
  if (open && suiteId.value) loadMindmapVersions();
});

/** 版本记录时间显示：将 ISO 中的 T 改为空格，如 2026-03-05 15:33:39 */
function formatVersionTime(createdAt) {
  if (!createdAt) return "";
  return String(createdAt).replace("T", " ");
}

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
    const resData = res.data;
    const data = resData?.mindmap_data;
    if (data && mindMapInstance) {
      const smmData = toSMM(data.root || data);
      mindMapInstance.setData(smmData);
      mindMapInstance.render();
      countCases();
      // 同步本地版本号，避免回退后保存时触发误判版本冲突
      if (resData?.mindmap_version !== undefined) {
        mindmapVersion.value = resData.mindmap_version;
      }
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

  versionPollTimer = setInterval(async () => {
    if (!suiteId.value || saving) return;
    try {
      const res = await getMindmapVersion(suiteId.value);
      const v = res.data?.mindmap_version;
      if (v != null && v !== mindmapVersion.value) {
        try {
          await ElMessageBox.confirm("脑图已有新版本，是否刷新？", "提示", {
            confirmButtonText: "刷新",
            cancelButtonText: "暂不",
          });
          await loadMindmap();
        } catch {
          /* 用户选择暂不 */
        }
      }
    } catch {
      /* 轮询失败忽略 */
    }
  }, VERSION_POLL_INTERVAL);

  nextTick(() => {
    const el = mindmapContainer.value;
    if (el) el.addEventListener("wheel", preventBrowserZoom, { passive: false, capture: true });
  });
});

onBeforeUnmount(() => {
  clearTimeout(saveTimer);
  clearInterval(generatingPollTimer);
  if (versionPollTimer) clearInterval(versionPollTimer);
  versionPollTimer = null;
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
  if (isGenerating.value) return;
  try {
    const res = await getMindmap(suiteId.value);
    const d = res.data || {};
    suiteName.value = d.suite_name || suiteName.value;
    caseEditStatus.value = d.case_edit_status || "drafting";
    caseCount.value = d.case_count || 0;
    projectId.value = d.project_id;
    caseNumberPrefix.value = d.case_number_prefix || "TC-";
    mindmapVersion.value = d.mindmap_version ?? 0;
    await ensureContainerSizeAndInit(d.mindmap_data);
    loadTagsAndMarkers(d.project_id);
  } catch (e) {
    if (!isGenerating.value) ElMessage.error("加载脑图数据失败");
    console.error(e);
  }
}

/** 等待容器有宽高后再初始化脑图，避免 simple-mind-map 报「宽高不能为 0」 */
function ensureContainerSizeAndInit(mindmapData) {
  const MAX_TRIES = 50;
  let tries = 0;
  return new Promise((resolve) => {
    const tryInit = () => {
      tries += 1;
      const el = mindmapContainer.value;
      if (!el) {
        if (tries >= MAX_TRIES) {
          resolve();
          return;
        }
        nextTick(tryInit);
        return;
      }
      const w = el.offsetWidth || 0;
      const h = el.offsetHeight || 0;
      if (w > 0 && h > 0) {
        initMindmap(mindmapData);
        resolve();
        return;
      }
      if (tries >= MAX_TRIES) {
        resolve();
        return;
      }
      nextTick(() => {
        requestAnimationFrame(tryInit);
      });
    };
    tryInit();
  });
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

const MARKER_BADGE = { bg: "#f5f5f5", border: "#d9d9d9", color: "#595959" };
const TAG_BADGE = { bg: "#e6f7ff", border: "#91d5ff", color: "#1890ff" };

function buildPrefixBadges(node) {
  const d = node.getData();
  const badges = [];
  if (d.attribute && BADGE_STYLES[d.attribute]) badges.push(BADGE_STYLES[d.attribute]);
  if (d.priority && PRI_BADGE[d.priority]) badges.push({ text: d.priority, ...PRI_BADGE[d.priority] });
  (d.markers || []).forEach((m) => badges.push({ text: m, ...MARKER_BADGE }));
  (d.userTags || []).forEach((t) => badges.push({ text: t, ...TAG_BADGE }));
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

  const isReadonly = caseEditStatus.value === "completed";
  mindMapInstance = new MindMap({
    el: mindmapContainer.value,
    data: smmData,
    theme: "classic4",
    layout: "logicalStructure",
    readonly: isReadonly,
    isDisableDrag: isReadonly,
    beforeDragStart() {
      return false;
    },
    async beforeDragEnd(dragInfo) {
      const { overlapNodeUid, prevNodeUid, nextNodeUid, beingDragNodeList } = dragInfo || {};
      const renderer = mindMapInstance.renderer;
      const dragged = beingDragNodeList && beingDragNodeList.length ? beingDragNodeList : renderer?.activeNodeList || [];
      if (!dragged.length) return false;
      const find = (uid) => (uid && renderer?.findNodeByUid) ? renderer.findNodeByUid(uid) : null;
      const getUid = (n) => n?.getData?.()?.uid ?? n?.uid;
      const getAttr = (n) => n?.getData?.()?.attribute;

      if (overlapNodeUid) {
        const toNode = find(overlapNodeUid);
        if (!toNode) return false;
        const toAttr = getAttr(toNode);
        const draggedAttrs = dragged.map(getAttr).filter(Boolean);
        if (CHAIN_ATTRS.includes(toAttr) && draggedAttrs.some((a) => CHAIN_ATTRS.includes(a))) {
          ElMessage.warning("用例链节点不允许拖拽到其他节点下作为子节点");
          return true;
        }
        return false;
      }

      if (prevNodeUid || nextNodeUid) {
        const refNode = find(prevNodeUid) || find(nextNodeUid);
        if (!refNode?.parent) return false;
        const parent = refNode.parent;
        const siblings = [...(parent.children || [])];
        const draggedSet = new Set(dragged.map(getUid));
        const withoutDragged = siblings.filter((c) => !draggedSet.has(getUid(c)));
        const refUid = getUid(refNode);
        let insertIdx = prevNodeUid
          ? withoutDragged.findIndex((c) => getUid(c) === refUid) + 1
          : withoutDragged.findIndex((c) => getUid(c) === refUid);
        if (insertIdx < 0) insertIdx = 0;
        const newOrder = [...withoutDragged];
        dragged.forEach((n) => newOrder.splice(insertIdx++, 0, n));
        const chainIndices = CHAIN_ATTRS.reduce((acc, a, i) => {
          acc[a] = i;
          return acc;
        }, {});
        const attrs = newOrder.map(getAttr).filter((a) => CHAIN_ATTRS.includes(a));
        for (let i = 1; i < attrs.length; i++) {
          if (chainIndices[attrs[i]] < chainIndices[attrs[i - 1]]) {
            ElMessage.warning("用例链子节点顺序须为：用例标题 → 测试数据 → 前置条件 → 操作步骤 → 预期结果");
            return true;
          }
        }
      }
      return false;
    },
    createNodePrefixContent: buildPrefixBadges,
    isLimitMindMapInCanvas: false,
    enableShortcutOnlyWhenMouseInSvg: false,
    /** 编辑节点时隐藏原节点文字，只显示编辑框，避免旧内容与新内容重叠 */
    openRealtimeRenderOnNodeTextEdit: true,
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
    marginX: 96,
    marginY: 56,
    themeConfig: {
      marginX: 96,
      marginY: 56,
      root: {
        fillColor: 'transparent',
        color: '#303133',
        borderColor: '#549688',
        borderWidth: 2,
        marginX: 96,
        marginY: 56,
      },
      second: {
        fillColor: 'transparent',
        color: '#303133',
        borderColor: '#909399',
        borderWidth: 1,
        marginX: 80,
        marginY: 48,
      },
      node: {
        fillColor: 'transparent',
        color: '#303133',
        borderColor: '#c0c4cc',
        borderWidth: 1,
        marginX: 64,
        marginY: 40,
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
      currentNodeText.value = nd.text ?? "";
      currentCaseNumber.value = nd.caseNumber || "";
    } else if (list?.length > 1) {
      currentPriority.value = "";
      currentAttribute.value = "";
      currentMarkers.value = [];
      currentTags.value = [];
      currentNodeText.value = "";
      currentCaseNumber.value = "";
    }
  });
  mindMapInstance.on("back_forward", (index, length) => {
    canUndo.value = index > 0;
    canRedo.value = length > 0 && index < length - 1;
    const cmd = mindMapInstance.command;
    if (cmd && cmd.history && cmd.history[index]) {
      try {
        const data = JSON.parse(cmd.history[index]);
        mindMapInstance.renderer.setData(data);
        mindMapInstance.render();
      } catch (_) {}
    }
  });
  canUndo.value = mindMapInstance.command?.activeHistoryIndex > 0;
  canRedo.value = false;

  mindMapInstance.on("data_change", () => {
    countCases();
    debounceSave();
    const cmd = mindMapInstance.command;
    if (cmd) {
      canUndo.value = cmd.activeHistoryIndex > 0;
      canRedo.value = cmd.activeHistoryIndex < cmd.history.length - 1;
    }
  });
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
      currentNodeText.value = nd.text ?? "";
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
    caseNumber: node.case_number || undefined,
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
  if (d.caseNumber) r.case_number = d.caseNumber;
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
  const caseTitleNodes = nodes.filter((n) => n.getData().attribute === "case_title");
  if (!caseTitleNodes.length) {
    ElMessage.warning("仅「用例标题」节点可设置优先级");
    return;
  }
  const toggle = caseTitleNodes.length === 1 && caseTitleNodes[0].getData().priority === p;
  const val = toggle ? undefined : p;
  caseTitleNodes.forEach((n) => {
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
  if (CHAIN_ATTRS.includes(nodes[0].getData().attribute)) {
    if (!canChangeAttribute.value) return;
    if (attr !== "test_data" && attr !== "precondition") return;
  }
  nodes.forEach((n) => {
    const cur = n.getData().attribute;
    n.setData({ attribute: cur === attr ? undefined : attr });
  });
  currentAttribute.value = nodes.length === 1 ? (nodes[0].getData().attribute || "") : "";
  mindMapInstance.render();
  countCases();
}

/** 现成（系统）标记只能选一个，自定义标记可多选 */
function setMarkers(val) {
  if (!mindMapInstance) return;
  const systemNames = markerOptions.value.filter((m) => m.marker_type === "system").map((m) => m.marker_name);
  const isSystem = (name) => systemNames.includes(name);
  const systemSelected = (val || []).filter(isSystem);
  const customSelected = (val || []).filter((n) => !isSystem(n));
  const normalized = [...customSelected, ...(systemSelected.length ? [systemSelected[systemSelected.length - 1]] : [])];
  mindMapInstance.renderer.activeNodeList?.forEach((n) => n.setData({ markers: [...normalized] }));
  currentMarkers.value = [...normalized];
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

function applyCaseNumber() {
  if (!mindMapInstance) return;
  const nodes = mindMapInstance.renderer.activeNodeList;
  if (!nodes?.length) return;
  const node = nodes[0];
  if (node.getData().attribute !== "case_title") return;
  const raw = currentCaseNumber.value.trim();
  if (!raw) {
    node.setData({ caseNumber: undefined });
    mindMapInstance.render();
    return;
  }
  const prefix = (caseNumberPrefix.value || "TC-").trim();
  const digitStr = raw.startsWith(prefix)
    ? raw.slice(prefix.length).replace(/\D/g, "")
    : raw.replace(/\D/g, "");
  const seq = parseInt(digitStr, 10);
  if (isNaN(seq) || seq < 1 || seq > 999) {
    ElMessage.warning("用例编号序号需在 1～999 之间");
    currentCaseNumber.value = node.getData().caseNumber || "";
    return;
  }
  // 统一规范化为「前缀 + 3 位补零」格式，如 TC-WPS-008
  const normalized = `${prefix}${String(seq).padStart(3, "0")}`;
  currentCaseNumber.value = normalized;
  node.setData({ caseNumber: normalized });
  mindMapInstance.render();
}

function openNumberSetting() {
  tempCaseNumberPrefix.value = caseNumberPrefix.value || "TC-";
  showNumberSettingDialog.value = true;
}

function confirmNumberSetting() {
  const prefix = (tempCaseNumberPrefix.value || "TC-").trim() || "TC-";
  caseNumberPrefix.value = prefix;
  showNumberSettingDialog.value = false;
  ElMessage.success(`编号前缀已更新为「${prefix}」，下次保存后生效`);
}

/**
 * 保存后把后端分配/确认的编号写回脑图节点，并同步刷新右侧属性面板的输入框。
 * caseNumberMap: { [mindmap_node_id]: case_number }
 */
function applyGeneratedCaseNumbers(caseNumberMap) {
  if (!mindMapInstance || !caseNumberMap || !Object.keys(caseNumberMap).length) return;

  // 遍历脑图树，按节点 uid 写入 caseNumber
  const walkAndApply = (node) => {
    const uid = node.getData?.()?.uid;
    if (uid && caseNumberMap[uid] != null) {
      node.setData({ caseNumber: caseNumberMap[uid] });
    }
    node.children?.forEach(walkAndApply);
  };
  walkAndApply(mindMapInstance.renderer.root);

  // 如果当前选中的节点恰好是 case_title，刷新输入框显示
  const active = mindMapInstance.renderer.activeNodeList;
  if (active?.length === 1) {
    const nd = active[0].getData();
    if (nd.attribute === "case_title") {
      currentCaseNumber.value = nd.caseNumber || "";
    }
  }
}

function rebuildTag() {
  // prefix badges via createNodePrefixContent handle visual display
}

// ── 状态 ──

async function handleStatusChange(status) {
  caseEditStatus.value = status;
  try { await updateEditStatus(suiteId.value, { case_edit_status: status }); } catch {}
  if (mindMapInstance?.setMode) {
    mindMapInstance.setMode(status === "completed" ? "readonly" : "edit");
  }
}

function handleUndo() {
  if (!mindMapInstance?.command || caseEditStatus.value === "completed") return;
  mindMapInstance.execCommand("BACK");
}
function handleRedo() {
  if (!mindMapInstance?.command || caseEditStatus.value === "completed") return;
  mindMapInstance.execCommand("FORWARD");
}

/** 检查脑图是否被他人更新：拉取服务端版本，若更新则提示并可选拉取最新数据 */
async function handleCheckUpdate() {
  if (!suiteId.value) return;
  try {
    const res = await getMindmapVersion(suiteId.value);
    const serverVersion = res.data?.mindmap_version ?? 0;
    const localVersion = mindmapVersion.value ?? 0;
    if (serverVersion > localVersion) {
      try {
        await ElMessageBox.confirm(
          "脑图已被他人更新保存，是否拉取最新内容？未保存的本地修改将丢失。",
          "检查更新",
          { confirmButtonText: "拉取最新", cancelButtonText: "取消" }
        );
        await loadMindmap();
        ElMessage.success("已拉取最新脑图数据");
      } catch {
        // 用户取消
      }
    } else {
      ElMessage.success("当前已是最新状态");
    }
  } catch (e) {
    ElMessage.error("检查更新失败");
    console.error(e);
  }
}

function applyNodeText() {
  if (!mindMapInstance || selectedNodes.value.length !== 1) return;
  const node = selectedNodes.value[0];
  const text = (currentNodeText.value ?? "").trim();
  if (node.getData().text === text) return;
  node.setData({ text: text || " " });
  mindMapInstance.render();
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
  if (!goNext || !searchResults.value.length) {
    searchResults.value = [];
    searchIdx.value = 0;
    const walk = (node) => {
      if (node.getData?.() && (node.getData().text || "").includes(keyword)) searchResults.value.push(node);
      (node.children || []).forEach(walk);
    };
    walk(mindMapInstance.renderer.root);
  }
  if (!searchResults.value.length) {
    ElMessage.info("未找到匹配项");
    return;
  }
  if (goNext && delta) {
    searchIdx.value = (searchIdx.value + delta + searchResults.value.length) % searchResults.value.length;
  }
  mindMapInstance.execCommand("GO_TARGET_NODE", searchResults.value[searchIdx.value]);
  ElMessage.success(`找到 ${searchResults.value.length} 个匹配，当前 ${searchIdx.value + 1}/${searchResults.value.length}`);
}

function toggleFilterNodeType(value, checked) {
  const arr = advancedFilter.nodeType;
  if (checked) arr.push(value);
  else advancedFilter.nodeType = arr.filter((v) => v !== value);
}
function toggleFilterArr(arr, value, checked) {
  if (checked) arr.push(value);
  else arr.splice(arr.indexOf(value), 1);
}
function clearAdvancedFilter() {
  advancedFilter.nodeType = [];
  advancedFilter.priority = "";
  advancedFilter.markers = [];
  advancedFilter.tags = [];
  advancedFilter.automation = "";
  advancedFilter.coverage = [];
  advancedFilter.network = [];
  filterResults.value = [];
  showAdvancedFilter.value = false;
}
function applyAdvancedFilter() {
  if (!mindMapInstance) return;
  const a = advancedFilter;
  const hasAny =
    a.nodeType.length > 0 || a.priority || a.markers.length > 0 || a.tags.length > 0 ||
    a.automation || a.coverage.length > 0 || a.network.length > 0;
  if (!hasAny) {
    ElMessage.info("请至少选择一项筛选条件");
    return;
  }
  const list = [];
  const walk = (node) => {
    if (!node || node.isRoot) {
      (node?.children || []).forEach(walk);
      return;
    }
    const d = node.getData?.() || {};
    const matchNodeType = !a.nodeType.length || a.nodeType.includes(d.attribute);
    const matchPri = !a.priority || d.priority === a.priority;
    const nodeMarkers = d.markers || [];
    const matchMarker = !a.markers.length || a.markers.some((m) => nodeMarkers.includes(m));
    const nodeTags = d.userTags || [];
    const matchTag = !a.tags.length || a.tags.some((t) => nodeTags.includes(t));
    const nodeAutomation = d.automation_type || d.automation;
    const matchAutomation = !a.automation || nodeAutomation === a.automation;
    const nodeCoverage = d.coverage_platform || d.coverage || [];
    const covArr = Array.isArray(nodeCoverage) ? nodeCoverage : [nodeCoverage];
    const matchCoverage = !a.coverage.length || a.coverage.some((c) => covArr.includes(c));
    const nodeNetwork = d.network_type || d.network || [];
    const netArr = Array.isArray(nodeNetwork) ? nodeNetwork : [nodeNetwork];
    const matchNetwork = !a.network.length || a.network.some((n) => netArr.includes(n));
    if (matchNodeType && matchPri && matchMarker && matchTag && matchAutomation && matchCoverage && matchNetwork) list.push(node);
    (node.children || []).forEach(walk);
  };
  walk(mindMapInstance.renderer.root);
  filterResults.value = list;
  filterIdx.value = 0;
  showAdvancedFilter.value = false;
  if (!list.length) {
    ElMessage.info("未找到符合筛选条件的节点");
    return;
  }
  mindMapInstance.execCommand("GO_TARGET_NODE", list[0]);
  ElMessage.success(`找到 ${list.length} 个匹配，当前 1/${list.length}`);
}

function doFilterSearch() {
  applyAdvancedFilter();
}

function goFilterResult(delta) {
  if (!mindMapInstance || !filterResults.value.length) return;
  filterIdx.value = (filterIdx.value + delta + filterResults.value.length) % filterResults.value.length;
  mindMapInstance.execCommand("GO_TARGET_NODE", filterResults.value[filterIdx.value]);
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
  const payload = {
    mindmap_data: json,
    case_edit_status: caseEditStatus.value,
    mindmap_version: mindmapVersion.value,
    case_number_prefix: caseNumberPrefix.value || "TC-",
  };
  try {
    const res = await saveMindmap(suiteId.value, payload);
    if (res.data?.mindmap_version != null) mindmapVersion.value = res.data.mindmap_version;
    if (!silent) ElMessage.success("保存成功");
    caseCount.value = res.data?.case_count ?? caseCount.value;
    applyGeneratedCaseNumbers(res.data?.case_number_map);
  } catch (e) {
    if (e?.response?.status === 409) {
      try {
        const action = await ElMessageBox.confirm(
          "脑图已被他人更新，请刷新后重新编辑再保存，或选择强制覆盖（将覆盖他人最新内容）。",
          "版本冲突",
          {
            confirmButtonText: "刷新并放弃本地修改",
            cancelButtonText: "强制覆盖",
            type: "warning",
            distinguishCancelAndClose: true,
          }
        );
        if (action === "confirm") {
          await loadMindmap();
          if (!silent) ElMessage.success("已刷新为最新版本");
        }
      } catch (userChoice) {
        if (userChoice === "cancel") {
          await doSaveForceOverwrite(silent);
        }
      }
      return;
    }
    if (!silent) ElMessage.error("保存失败");
    console.error(e);
  } finally {
    saving = false;
  }
}

async function doSaveForceOverwrite(silent) {
  if (!mindMapInstance || !suiteId.value || saving) return;
  saving = true;
  const smmData = mindMapInstance.getData();
  const json = { version: "2.0", root: fromSMM(smmData), metadata: {} };
  try {
    const res = await saveMindmap(suiteId.value, {
      mindmap_data: json,
      case_edit_status: caseEditStatus.value,
      mindmap_version: mindmapVersion.value,
      force_overwrite: true,
      case_number_prefix: caseNumberPrefix.value || "TC-",
    });
    if (res.data?.mindmap_version != null) mindmapVersion.value = res.data.mindmap_version;
    if (!silent) ElMessage.success("已强制覆盖保存");
    caseCount.value = res.data?.case_count ?? caseCount.value;
    applyGeneratedCaseNumbers(res.data?.case_number_map);
  } catch (e) {
    if (!silent) ElMessage.error("保存失败");
    console.error(e);
  } finally {
    saving = false;
  }
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
  display: flex; flex-direction: column; gap: 8px;
  padding: 8px 16px; background: #fafafa;
  border-bottom: 1px solid #e4e7ed; flex-shrink: 0;
}
.search-row, .filter-row { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.filter-label { font-size: 12px; color: #606266; white-space: nowrap; }
.search-nav { display: inline-flex; align-items: center; gap: 4px; margin-left: 4px; }
.search-index { font-size: 12px; color: #909399; min-width: 48px; text-align: center; }
.prop-hint { font-size: 11px; color: #909399; font-weight: normal; }

.advanced-filter-popover { padding: 4px; max-height: 70vh; overflow-y: auto; }
.filter-group { margin-bottom: 14px; }
.filter-group-label { font-size: 12px; color: #606266; margin-bottom: 6px; font-weight: 600; }
.filter-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.filter-tags.wrap { flex-wrap: wrap; }
.filter-actions { margin-top: 12px; padding-top: 12px; border-top: 1px solid #ebeef5; display: flex; gap: 8px; }
.prop-section-first { margin-top: 0; }
/* 节点内容：单行起，可拖拽变多行 */
.node-content-textarea { width: 100%; }
.node-content-textarea .el-textarea__inner { resize: vertical; min-height: 32px; }

/* ── 版本记录 ── */
.version-tip { font-size: 12px; color: #909399; padding: 8px 12px; border-bottom: 1px solid #ebeef5; }
.version-list { padding: 0 8px; }
.version-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 12px; border-bottom: 1px solid #ebeef5;
}
.version-meta { font-size: 13px; color: #606266; }

/* ── 主体 ── */
.editor-body { flex: 1; display: flex; min-height: 0; overflow: hidden; }
.mindmap-wrap {
  flex: 1; min-width: 0; min-height: 0; overflow: visible;
  display: flex; flex-direction: column;
}
.mindmap-canvas {
  flex: 1; min-width: 0; min-height: 0;
  background: #f5f5f5; overflow: visible; outline: none;
  /* 非编辑状态下节点文字不可拖拽选中，避免误选 */
  user-select: none;
}

/* ── 右侧属性面板 ── */
.property-panel {
  width: 260px; min-width: 260px;
  border-left: 1px solid #e4e7ed;
  padding: 12px 14px 16px; overflow-y: auto;
  background: #fff; transition: width .2s;
  display: flex; flex-direction: column;
}
.property-panel-header {
  flex-shrink: 0; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #ebeef5;
}
.property-panel-body {
  flex: 1; min-height: 0; overflow-y: auto;
}
.property-panel-empty {
  display: flex; align-items: center; justify-content: center; padding: 24px 0; min-height: 80px;
}
.property-panel.hidden { width: 0; min-width: 0; padding: 0; border: none; overflow: hidden; }
.property-panel.hidden .property-panel-header,
.property-panel.hidden .property-panel-body { display: none; }

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
.attr-readonly { font-size: 13px; color: #606266; padding: 6px 0; }

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

/* ── 用例编号设置对话框 ── */
.number-setting-body { display: flex; flex-direction: column; gap: 14px; }
.number-setting-tip { font-size: 13px; color: #606266; line-height: 1.6; background: #f4f8ff; border-radius: 4px; padding: 8px 10px; }
.number-setting-row { display: flex; align-items: center; gap: 10px; }
.number-setting-label { font-size: 13px; color: #303133; white-space: nowrap; min-width: 56px; }
.number-setting-preview { font-size: 13px; color: #909399; }
.number-setting-preview strong { color: #409eff; }
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

/* 编辑框内的 contenteditable 区域：仅在此处允许拖拽选中文字 */
.smm-node-edit-wrap [contenteditable],
.smm-node-text-edit-wrap [contenteditable],
.smm-richtext-node-edit-wrap [contenteditable] {
  background: transparent !important;
  caret-color: #303133;
  user-select: text;
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
