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
  // 脑图数据
  data: {
    type: Object,
    default: () => ({}),
  },
  // 是否显示脑图
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

const onPanStart = (e) => {
  if (e.button !== 0) return;
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

// 固定为节点在右侧展开（kityminder Layout right）
function applyRightLayout() {
  if (!minder) return;
  const tryLayout = () => {
    try {
      if (typeof minder.execCommand === "function") {
        const tried = [
          ["Layout", "right"],
          ["layout", "right"],
          ["Layout", "Right"],
        ];
        for (const [cmd, arg] of tried) {
          try {
            minder.execCommand(cmd, arg);
            if (typeof minder.render === "function") minder.render();
            return true;
          } catch (_) {}
        }
      }
      if (typeof minder.setLayout === "function") {
        minder.setLayout("right");
        if (typeof minder.render === "function") minder.render();
        return true;
      }
      if (typeof minder.layout === "function") {
        minder.layout("right");
        if (typeof minder.render === "function") minder.render();
        return true;
      }
    } catch (e) {
      console.warn("脑图布局设置失败:", e);
    }
    return false;
  };
  tryLayout();
  setTimeout(tryLayout, 150);
}

// 初始化脑图
const initMindMap = () => {
  if (!mindmapRef.value || !window.kityminder) return;

  // 销毁现有实例
  if (minder) {
    try {
      // 手动添加 clearSelect 方法，避免销毁时出错
      if (typeof minder.clearSelect !== "function") {
        minder.clearSelect = function () {};
      }
      minder.destroy();
    } catch (error) {
      console.warn("销毁脑图实例时发生错误:", error);
    }
    minder = null;
  }

  // 创建新实例，禁用编辑功能
  minder = new window.kityminder.Minder({
    renderTo: mindmapRef.value,
    enableSvgBackground: true,
    // 禁用编辑功能
    enableHotbox: false,
    enableContextMenu: false,
    editable: false,
  });

  // 加载数据
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
    // 注意：KityMinder的exportData('json')可能已经返回JavaScript对象，不需要再解析
    const data = minder.exportData("json");
    emit("content-change", data);
  });
};

// 监听数据变化
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

// 监听显示状态变化
watch(
  () => props.visible,
  (newVisible) => {
    if (newVisible) {
      // 延迟初始化，确保DOM已渲染
      setTimeout(initMindMap, 100);
    }
  },
);

// 组件挂载时初始化
onMounted(() => {
  if (props.visible) {
    setTimeout(initMindMap, 100);
  }
});

// 组件卸载时清理
onBeforeUnmount(() => {
  if (minder) {
    try {
      // 手动添加 clearSelect 方法，避免销毁时出错
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
  width: 400%;
  height: 400%;
  min-width: 3000px;
  min-height: 2000px;
  will-change: transform;
  overflow: visible;
}

.mindmap-wrapper {
  width: 100%;
  height: 100%;
  min-width: 2800px;
  min-height: 1800px;
  overflow: visible;
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
