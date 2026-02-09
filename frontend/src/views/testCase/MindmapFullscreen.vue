<template>
  <div class="mindmap-fullscreen">
    <div class="mindmap-fullscreen-toolbar">
      <span class="mindmap-fullscreen-title">{{ suiteName || '脑图全屏' }}</span>
      <el-button
        type="primary"
        link
        :icon="Close"
        @click="closeFullscreen"
      >
        关闭
      </el-button>
    </div>
    <div class="mindmap-fullscreen-body">
      <MindMap
        v-if="Object.keys(mindMapData).length > 0"
        :data="mindMapData"
        :visible="true"
      />
      <div
        v-else-if="!loading && !errorMsg"
        class="mindmap-fullscreen-empty"
      >
        当前用例集下暂无测试用例
      </div>
      <div
        v-else-if="errorMsg"
        class="mindmap-fullscreen-error"
      >
        {{ errorMsg }}
      </div>
      <div
        v-else
        class="mindmap-fullscreen-loading"
      >
        <el-icon class="is-loading">
          <Loading />
        </el-icon>
        加载中...
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { Close, Loading } from "@element-plus/icons-vue";
import MindMap from "@/components/MindMap.vue";
import { getSuiteCases } from "@/api/testSuite";

const route = useRoute();
const loading = ref(true);
const errorMsg = ref("");
const cases = ref([]);
const suiteName = computed(() => route.query.suite_name || "脑图");

const mindMapData = ref({});

function buildMindMapData(suiteNameVal, casesList) {
  const mindMapRoot = {
    root: {
      data: {
        text: suiteNameVal,
        type: "suite",
      },
      children: [],
    },
  };
  if (!casesList || casesList.length === 0) {
    mindMapRoot.root.children.push({
      id: "no-cases",
      data: { text: "当前用例集下暂无测试用例" },
    });
    return mindMapRoot;
  }
  const priorityIconMap = {
    P0: "🔴P0",
    P1: "🔴P1",
    P2: "🟡P2",
    P3: "🔵P3",
    P4: "🟢P4",
  };
  const statusIconMap = {
    "": "⏳ 未执行",
    pass: "✅通过",
    fail: "❌失败",
    blocked: "🚫阻塞",
    not_applicable: "⚠️不适用",
  };
  casesList.forEach((testCase) => {
    const priority = testCase.priority || "P3";
    const status = testCase.status || "";
    const priorityIcon = priorityIconMap[priority] || `🔵 ${(priority || "").replace("P", "")}`;
    const statusIcon = statusIconMap[status] || statusIconMap[""];
    const caseNameNode = {
      id: `case-name-${testCase.id}`,
      data: {
        text: `${priorityIcon} ${testCase.case_name} ${statusIcon}`,
        type: "case-name",
      },
      children: [],
    };
    const caseIdNode = {
      id: `case-id-${testCase.id}`,
      data: { text: `用例ID: ${testCase.id}`, type: "case-id" },
      children: [],
    };
    const caseProperties = [
      { key: "test_data", label: "测试数据", value: testCase.test_data || "-" },
      { key: "preconditions", label: "前置条件", value: testCase.preconditions || "-" },
      { key: "steps", label: "测试步骤", value: testCase.steps || "-" },
      { key: "expected_result", label: "预期结果", value: testCase.expected_result || "-" },
      { key: "actual_result", label: "实际结果", value: testCase.actual_result || "-" },
    ];
    caseProperties.forEach((prop) => {
      caseIdNode.children.push({
        id: `case-prop-${testCase.id}-${prop.key}`,
        data: { text: `${prop.label}: ${prop.value}`, type: "case-prop" },
      });
    });
    caseNameNode.children.push(caseIdNode);
    mindMapRoot.root.children.push(caseNameNode);
  });
  return mindMapRoot;
}

async function loadCases() {
  const suiteId = route.query.suite_id;
  if (!suiteId) {
    errorMsg.value = "缺少用例集参数";
    loading.value = false;
    return;
  }
  try {
    loading.value = true;
    errorMsg.value = "";
    const response = await getSuiteCases(suiteId, {
      page: 1,
      page_size: 10000,
    });
    const items = response.data?.items || [];
    cases.value = items;
    mindMapData.value = buildMindMapData(
      decodeURIComponent(route.query.suite_name || "用例集"),
      items
    );
  } catch (e) {
    console.error(e);
    errorMsg.value = "加载用例失败，请关闭后重试";
  } finally {
    loading.value = false;
  }
}

function closeFullscreen() {
  window.close();
  if (!window.closed) {
    window.history.back();
  }
}

onMounted(() => {
  loadCases();
});
</script>

<style scoped>
.mindmap-fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  background: #fff;
  display: flex;
  flex-direction: column;
}

.mindmap-fullscreen-toolbar {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  border-bottom: 1px solid #e4e7ed;
  background: #fff;
}

.mindmap-fullscreen-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.mindmap-fullscreen-body {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.mindmap-fullscreen-body :deep(.mindmap-container) {
  height: 100%;
  border: none;
}

.mindmap-fullscreen-empty,
.mindmap-fullscreen-error,
.mindmap-fullscreen-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
  font-size: 14px;
}

.mindmap-fullscreen-error {
  color: #f56c6c;
}

.mindmap-fullscreen-loading {
  gap: 8px;
}
</style>
