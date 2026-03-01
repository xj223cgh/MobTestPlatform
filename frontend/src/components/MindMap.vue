<template>
  <div
    ref="containerRef"
    class="mindmap-container"
    :class="{ 'mindmap-panning': isPanning }"
    @mousedown="onPanStart"
    @mousemove="onPanMove"
    @mouseup="onPanEnd"
    @mouseleave="onPanEnd"
  >
    <div
      class="mindmap-pan-layer"
      :style="{ transform: `translate(calc(-50% + ${panX}px), calc(-50% + ${panY}px))` }"
    >
      <div
        ref="mindmapRef"
        class="mindmap-wrapper"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from "vue";

const props = defineProps({
  data: {
    type: Object,
    default: () => ({}),
  },
  visible: {
    type: Boolean,
    default: true,
  },
});

const emit = defineEmits(["node-select", "content-change"]);

const mindmapRef = ref(null);
const containerRef = ref(null);
let minder = null;

// 鼠标拖拽平移（使用 transform，不依赖滚动条）
const isPanning = ref(false);
const panX = ref(0);
const panY = ref(0);
const panStart = ref({ x: null, y: null, panX: 0, panY: 0 });
const DRAG_THRESHOLD = 4;

// 判断点击目标是否为 KityMinder 节点（SVG 元素有 km-node / km-expand-button 类名）
const isKityMinderNode = (target) => {
  let el = target;
  while (el && el !== containerRef.value) {
    // SVG 元素的 className 是 SVGAnimatedString，需用 getAttribute 获取
    const rawCls = (typeof el.getAttribute === "function" ? el.getAttribute("class") : null)
      ?? (typeof el.className === "string" ? el.className : (el.className?.baseVal ?? ""));
    if (rawCls && (rawCls.includes("km-node") || rawCls.includes("km-expand-button"))) {
      return true;
    }
    el = el.parentElement;
  }
  return false;
};

const onPanStart = (e) => {
  if (e.button !== 0) return;
  // 点击在 KityMinder 节点上时，不触发画布平移，让 KityMinder 内部处理节点拖拽
  if (isKityMinderNode(e.target)) return;
  panStart.value = {
    x: e.clientX,
    y: e.clientY,
    panX: panX.value,
    panY: panY.value,
  };
};

const onPanMove = (e) => {
  if (panStart.value.x === null) return;
  const dx = e.clientX - panStart.value.x;
  const dy = e.clientY - panStart.value.y;
  if (!isPanning.value) {
    const dist = Math.sqrt(dx * dx + dy * dy);
    if (dist < DRAG_THRESHOLD) return;
    isPanning.value = true;
  }
  e.preventDefault();
  panX.value = panStart.value.panX + dx;
  panY.value = panStart.value.panY + dy;
};

const onPanEnd = () => {
  if (isPanning.value) {
    justFinishedPanning.value = true;
    setTimeout(() => {
      justFinishedPanning.value = false;
    }, 50);
  }
  isPanning.value = false;
  panStart.value = { x: null, y: null, panX: 0, panY: 0 };
};

const justFinishedPanning = ref(false);

// 获取节点在脑图树中的深度（根节点深度为 0，用例名称节点深度为 1）
const getNodeDepth = (node) => {
  let d = 0;
  let n = node;
  while (n && n.parent) {
    d++;
    n = n.parent;
  }
  return d;
};

// 固定为节点全部向右展开（kityminder Template right）
// 注意：此函数在 execCommand 拦截补丁安装后调用，但 Template 命令不在拦截黑名单内，可正常穿透
function applyRightLayout() {
  if (!minder) return;
  const tryLayout = () => {
    try {
      if (typeof minder.execCommand === "function") {
        const tried = [
          ["Template", "right"],
          ["template", "right"],
        ];
        for (const [cmd, arg] of tried) {
          try {
            minder.execCommand(cmd, arg);
            if (typeof minder.render === "function") minder.render();
            return true;
          } catch (e) {
            console.debug("脑图模板命令未支持:", cmd, arg, e?.message ?? String(e));
          }
        }
      }
    } catch (e) {
      console.warn("脑图布局设置失败:", e);
    }
    return false;
  };
  tryLayout();
  setTimeout(tryLayout, 200);
}

const initMindMap = () => {
  if (!mindmapRef.value || !window.kityminder) return;

  if (minder) {
    try {
      if (typeof minder.clearSelect !== "function") {
        minder.clearSelect = function () {};
      }
      minder.destroy();
    } catch (error) {
      console.warn("销毁脑图实例时发生错误:", error);
    }
    minder = null;
  }

  // 开启 editable 以启用节点拖拽；通过 execCommand 拦截限制操作范围
  minder = new window.kityminder.Minder({
    renderTo: mindmapRef.value,
    enableSvgBackground: true,
    enableHotbox: false,
    enableContextMenu: false,
    editable: true,
  });

  // ---- execCommand 拦截：限制操作范围 ----
  // 完全禁止的命令：新增节点、删除节点、文本编辑、撤销/重做等
  const BLOCKED_CMDS = new Set([
    "editnode", "startediting", "stopediting",
    "appendchildnode", "appendsiblingnode",
    "insertchildnode", "insertsiblingnode",
    "removenode", "undo", "redo",
    "cut", "paste", "copy",
    "priority", "progress", "resource",
  ]);

  const origExecCommand = minder.execCommand.bind(minder);
  minder.execCommand = function (cmdName, ...args) {
    const nameLower = (cmdName || "").toLowerCase();

    // 拦截：禁止所有编辑/新增/删除类命令
    if (BLOCKED_CMDS.has(nameLower)) return;

    // 拦截：拖拽/移动命令只允许深度=1 的节点（用例名称节点）执行
    if (nameLower.includes("move") || nameLower.includes("drag")) {
      const node = minder.getSelectedNode?.();
      if (!node || getNodeDepth(node) !== 1) return;
    }

    return origExecCommand(cmdName, ...args);
  };
  // ---- 拦截结束 ----

  // 禁止双击进入文本编辑模式
  minder.on("dblclick", () => {
    try {
      if (typeof minder.setStatus === "function") minder.setStatus("normal");
    } catch (_) {}
  });

  // 禁止键盘编辑快捷键（Tab 添加子节点、Enter 添加兄弟节点、Delete/Backspace 删除）
  minder.on("keydown", (e) => {
    const key = e.originEvent?.keyCode ?? e.keyCode;
    const EDIT_KEYS = [9 /* Tab */, 13 /* Enter */, 46 /* Delete */, 8 /* Backspace */, 113 /* F2 */];
    if (EDIT_KEYS.includes(key)) {
      e.originEvent?.preventDefault?.();
      e.originEvent?.stopPropagation?.();
    }
  });

  if (props.data && Object.keys(props.data).length > 0) {
    minder.importData("json", JSON.stringify(props.data));
  }

  requestAnimationFrame(() => {
    applyRightLayout();
  });

  // 绑定事件（拖拽结束后短时内不触发节点选择，避免误触）
  minder.on("nodeselect", (event) => {
    if (justFinishedPanning.value) return;
    emit("node-select", event.node);
  });

  minder.on("contentchange", () => {
    const data = minder.exportData("json");
    emit("content-change", data);
  });
};

watch(
  () => props.data,
  (newData) => {
    if (minder && props.visible) {
      minder.importData("json", JSON.stringify(newData));
      applyRightLayout();
    }
  },
  { deep: true },
);

watch(
  () => props.visible,
  (newVisible) => {
    if (newVisible) {
      setTimeout(initMindMap, 100);
    }
  },
);

onMounted(() => {
  if (props.visible) {
    setTimeout(initMindMap, 100);
  }
});

onBeforeUnmount(() => {
  if (minder) {
    try {
      if (typeof minder.clearSelect !== "function") {
        minder.clearSelect = function () {};
      }
      minder.destroy();
    } catch (error) {
      console.warn("销毁脑图实例时发生错误:", error);
    }
    minder = null;
  }
});
</script>

<style scoped>
.mindmap-container {
  width: 100%;
  height: 100%;
  overflow: hidden;
  position: relative;
  background-color: #f5f5f5;
  border: 1px solid #e0e0e0;
  cursor: grab;
}

.mindmap-container.mindmap-panning {
  cursor: grabbing;
  user-select: none;
}

.mindmap-pan-layer {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 600%;
  height: 600%;
  min-width: 6000px;
  min-height: 4000px;
  will-change: transform;
  overflow: visible;
}

.mindmap-wrapper {
  width: 100%;
  height: 100%;
  min-width: 5800px;
  min-height: 3800px;
  overflow: visible;
}

/* Issue 1 修复：让 KityMinder 生成的 SVG 允许内容溢出，不裁剪超出边界的节点 */
.mindmap-container :deep(svg) {
  overflow: visible !important;
}

.mindmap-container :deep(.km-render-container) {
  overflow: visible !important;
}

/* 让 kityminder 节点文字完整显示，不截断 */
.mindmap-container :deep(.km-node),
.mindmap-container :deep(.km-nodelabel),
.mindmap-container :deep(.km-label) {
  overflow: visible !important;
  white-space: normal !important;
  word-break: break-word;
  max-width: 420px;
}

.mindmap-container :deep(.km-node-inner) {
  overflow: visible !important;
  max-width: none;
}
</style>
