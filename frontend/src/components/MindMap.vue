<template>
  <div class="mindmap-container">
    <div ref="mindmapRef" class="mindmap-wrapper" />
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
let minder = null;

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
    // 将JavaScript对象转换为JSON字符串
    minder.importData("json", JSON.stringify(props.data));
  }

  // 绑定事件
  minder.on("nodeselect", (event) => {
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
      // 将JavaScript对象转换为JSON字符串
      minder.importData("json", JSON.stringify(newData));
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
  overflow: auto;
  background-color: #f5f5f5;
  border: 1px solid #e0e0e0;
}

.mindmap-wrapper {
  width: 100%;
  height: 100%;
  min-height: 600px;
}
</style>
