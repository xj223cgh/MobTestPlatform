<template>
  <div class="test-case-execution">
    <!-- 页面标题和按钮区域 -->
    <div class="page-header-container">
      <div class="title-section">
        <h1>执行任务：{{ taskInfo.task_name }}</h1>
      </div>
      <div class="buttons-section">
        <el-button
          type="primary"
          :loading="loading.completeTask"
          @click="handleCompleteTask"
        >
          <el-icon><Check /></el-icon>
          完成任务
        </el-button>
        <el-button
          :loading="loading.navigate"
          @click="handleBack"
        >
          <el-icon><ArrowLeft /></el-icon>
          返回任务列表
        </el-button>
      </div>
    </div>

    <div class="main-content">
      <!-- 左侧：用例列表 -->
      <div
        class="left-panel"
        :class="{ collapsed: isCaseTreeCollapsed }"
      >
        <div
          v-if="!isCaseTreeCollapsed"
          class="filter-section"
        >
          <div style="display: flex; align-items: center; flex: 1;">
            <el-input
              v-model="filterForm.search"
              placeholder="搜索名称/描述"
              clearable
              @input="handleFilter"
              @clear="handleFilter"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>

            <el-select
              v-model="filterForm.status"
              placeholder="筛选状态"
              clearable
              multiple
              style="margin-left: 10px; flex: 1;"
              @change="handleFilter"
            >
              <el-option
                label="通过"
                value="pass"
              />
              <el-option
                label="失败"
                value="fail"
              />
              <el-option
                label="阻塞"
                value="blocked"
              />
              <el-option
                label="不适用"
                value="not_applicable"
              />
              <el-option
                label="未执行"
                value=""
              />
            </el-select>
          </div>
          <div style="margin-left: 5px;">
            <el-button
              size="small"
              circle
              :title="isCaseTreeCollapsed ? '展开用例树' : '收起用例树'"
              @click="toggleCaseTree"
            >
              <el-icon v-if="isCaseTreeCollapsed">
                <ArrowRight />
              </el-icon>
              <el-icon v-else>
                <ArrowLeft />
              </el-icon>
            </el-button>
          </div>
        </div>
        <div
          v-else
          class="collapsed-header"
        >
          <el-button
            size="small"
            circle
            :title="isCaseTreeCollapsed ? '展开用例树' : '收起用例树'"
            @click="toggleCaseTree"
          >
            <el-icon v-if="isCaseTreeCollapsed">
              <ArrowRight />
            </el-icon>
            <el-icon v-else>
              <ArrowLeft />
            </el-icon>
          </el-button>
        </div>

        <div
          v-if="!isCaseTreeCollapsed"
          class="case-list"
        >
          <el-tree
            ref="caseTreeRef"
            :data="testCaseTree"
            :props="treeProps"
            node-key="id"
            :default-expand-all="true"
            :highlight-current="true"
            @node-click="handleCaseClick"
          >
            <template #default="{ node, data }">
              <div
                v-if="data.type === 'suite'"
                class="tree-node-content"
              >
                <span>{{ node.label }}</span>
                <span class="suite-count">
                  (通过: {{ data.pass_count || 0 }} / 失败:
                  {{ data.fail_count || 0 }} / 阻塞:
                  {{ data.block_count || 0 }} / 不适用:
                  {{ data.not_applicable_count || 0 }})
                </span>
              </div>
              <div
                v-else
                class="tree-node-content"
              >
                <span class="case-name">
                  {{ node.label }}
                  <span class="case-number">({{ data.case_number || "无编号" }})</span>
                </span>
                <el-tag
                  :type="getStatusType(data.status)"
                  size="small"
                >
                  {{ getStatusText(data.status || "") }}
                </el-tag>
              </div>
            </template>
          </el-tree>
        </div>
      </div>

      <!-- 中间：用例详情和执行区域 -->
      <div class="middle-panel">
        <!-- 左侧导航区域 -->
        <div class="nav-area left-nav-area">
          <el-button
            v-if="hasPreviousCase"
            :disabled="!hasPreviousCase"
            circle
            class="nav-button left-button"
            title="上一条"
            @click="previousCase"
          >
            <el-icon><ArrowLeft /></el-icon>
          </el-button>
          <!-- 当没有上一条用例时，显示占位元素 -->
          <div
            v-else
            class="nav-button placeholder"
          />
        </div>

        <!-- 用例内容区域 -->
        <div class="content-area">
          <el-card
            v-if="selectedCase"
            shadow="hover"
          >
            <template #header>
              <div class="card-header">
                <div class="case-main-info">
                  <h3>{{ selectedCase.case_name }}</h3>
                </div>
                <div class="case-meta">
                  <div class="meta-item">
                    <span class="meta-label">编号：</span>
                    <span class="meta-value">
                      {{ selectedCase.case_number || "-" }}
                    </span>
                  </div>
                  <div class="meta-item">
                    <span class="meta-label">优先级：</span>
                    <el-tag
                      size="small"
                      :type="getPriorityType(selectedCase.priority)"
                    >
                      {{ selectedCase.priority }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </template>

            <div class="case-detail">
              <!-- 用例描述 -->
              <el-descriptions
                title="用例描述"
                :column="1"
              >
                <el-descriptions-item>
                  {{ selectedCase.case_description || "-" }}
                </el-descriptions-item>
              </el-descriptions>

              <!-- 测试数据 -->
              <el-descriptions
                title="测试数据"
                :column="1"
              >
                <el-descriptions-item>
                  {{ selectedCase.test_data || "-" }}
                </el-descriptions-item>
              </el-descriptions>

              <!-- 前置条件 -->
              <el-descriptions
                title="前置条件"
                :column="1"
              >
                <el-descriptions-item>
                  {{ selectedCase.preconditions || "-" }}
                </el-descriptions-item>
              </el-descriptions>

              <!-- 测试步骤 -->
              <el-descriptions
                title="测试步骤"
                :column="1"
              >
                <el-descriptions-item>
                  <div
                    v-for="(step, index) in parseSteps(selectedCase.steps)"
                    :key="index"
                    class="step-item"
                  >
                    <div class="step-content">
                      {{ step }}
                    </div>
                  </div>
                </el-descriptions-item>
              </el-descriptions>

              <!-- 预期结果 -->
              <el-descriptions
                title="预期结果"
                :column="1"
              >
                <el-descriptions-item>
                  {{ selectedCase.expected_result || "-" }}
                </el-descriptions-item>
              </el-descriptions>

              <!-- 实际结果 -->
              <el-descriptions
                title="实际结果"
                :column="1"
              >
                <el-descriptions-item>
                  <el-input
                    v-model="executionForm.actual_result"
                    type="textarea"
                    :rows="4"
                    placeholder="请输入实际执行结果"
                    style="width: 100%"
                    @input="debouncedSaveActualResult"
                  />
                </el-descriptions-item>
              </el-descriptions>

              <!-- 执行区域 -->
              <div class="execution-section">
                <div class="status-buttons">
                  <el-button
                    type="success"
                    :disabled="loading.updateStatus"
                    @click="updateCaseStatus('pass')"
                  >
                    <el-icon><CircleCheck /></el-icon>
                    通过
                  </el-button>
                  <el-button
                    type="danger"
                    :disabled="loading.updateStatus"
                    @click="updateCaseStatus('fail')"
                  >
                    <el-icon><CircleClose /></el-icon>
                    失败
                  </el-button>
                  <el-button
                    type="warning"
                    :disabled="loading.updateStatus"
                    @click="updateCaseStatus('blocked')"
                  >
                    <el-icon><Warning /></el-icon>
                    阻塞
                  </el-button>
                  <el-button
                    :disabled="loading.updateStatus"
                    @click="updateCaseStatus('not_applicable')"
                  >
                    <el-icon><Close /></el-icon>
                    不适用
                  </el-button>
                  <el-button
                    type="primary"
                    :disabled="loading.updateStatus"
                    @click="updateCaseStatus('')"
                  >
                    <el-icon><RefreshRight /></el-icon>
                    重置
                  </el-button>
                </div>
              </div>
            </div>
          </el-card>
          <div
            v-else
            class="no-selection"
          >
            <el-empty description="请选择一个测试用例进行执行" />
          </div>
        </div>

        <!-- 右侧导航区域 -->
        <div class="nav-area right-nav-area">
          <el-button
            v-if="hasNextCase"
            :disabled="!hasNextCase"
            circle
            class="nav-button right-button"
            title="下一条"
            @click="nextCase"
          >
            <el-icon><ArrowRight /></el-icon>
          </el-button>
          <!-- 当没有下一条用例时，显示占位元素 -->
          <div
            v-else
            class="nav-button placeholder"
          />
        </div>
      </div>

      <!-- 右侧：执行结果统计 -->
      <div class="right-panel">
        <el-card shadow="hover">
          <template #header>
            <h3>执行统计</h3>
          </template>

          <div class="stats-content">
            <div class="total-stats">
              <div class="total-number">
                {{ totalCases }}
              </div>
              <div class="total-label">
                总用例数
              </div>
            </div>

            <div class="status-stats">
              <div
                class="stat-item"
                :class="['status-pass']"
              >
                <div class="stat-number">
                  {{ passCount }}
                </div>
                <div class="stat-label">
                  通过
                </div>
              </div>
              <div
                class="stat-item"
                :class="['status-fail']"
              >
                <div class="stat-number">
                  {{ failCount }}
                </div>
                <div class="stat-label">
                  失败
                </div>
              </div>
              <div
                class="stat-item"
                :class="['status-blocked']"
              >
                <div class="stat-number">
                  {{ blockedCount }}
                </div>
                <div class="stat-label">
                  阻塞
                </div>
              </div>
              <div
                class="stat-item"
                :class="['status-not-applicable']"
              >
                <div class="stat-number">
                  {{ notApplicableCount }}
                </div>
                <div class="stat-label">
                  不适用
                </div>
              </div>
              <div
                class="stat-item"
                :class="['status-not-executed']"
              >
                <div class="stat-number">
                  {{ notExecutedCount }}
                </div>
                <div class="stat-label">
                  未执行
                </div>
              </div>
            </div>

            <el-progress
              :percentage="executionProgress"
              :color="getProgressColor(executionProgress)"
              :stroke-width="10"
            >
              <template #default>
                <div class="progress-text">
                  <span>{{ executionProgress }}%</span>
                  <span>已执行</span>
                </div>
              </template>
            </el-progress>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  Check,
  CircleCheck,
  CircleClose,
  Warning,
  Close,
  Search,
  ArrowLeft,
  ArrowRight
} from "@element-plus/icons-vue";
import testTaskApi from "@/api/testTask";
import { updateTestCase } from "@/api/testCase";

const route = useRoute();
const router = useRouter();

const taskId = route.params.id;
const taskInfo = ref({});
const testCases = ref([]);
const testCaseTree = ref([]);
const caseTreeRef = ref(null);
const selectedCase = ref(null);
const loading = reactive({
  getTaskInfo: false,
  getTestCases: false,
  updateStatus: false,
  completeTask: false,
  navigate: false,
  updateTaskStatus: false,
});

const filterForm = reactive({
  search: "",
  status: [],
});

const executionForm = reactive({
  actual_result: "",
});

// 用例树收起/展开状态
const isCaseTreeCollapsed = ref(false);

// 切换用例树收起/展开状态
const toggleCaseTree = () => {
  isCaseTreeCollapsed.value = !isCaseTreeCollapsed.value;
  // 当展开用例树时，重新设置选中状态
  if (!isCaseTreeCollapsed.value && selectedCase.value) {
    // 确保DOM更新完成后再设置选中状态
    setTimeout(() => {
      if (caseTreeRef.value) {
        caseTreeRef.value.setCurrentKey(selectedCase.value.id);
      }
    }, 0);
  }
};

// 防抖函数，避免频繁保存
const debounce = (func, delay) => {
  let timer;
  return function(...args) {
    clearTimeout(timer);
    timer = setTimeout(() => func.apply(this, args), delay);
  };
};

// 实时保存实际结果
const saveActualResult = async () => {
  if (!selectedCase.value) return;
  
  try {
    await updateTestCase(selectedCase.value.id, {
      actual_result: executionForm.actual_result,
    });
    // 更新本地数据
    selectedCase.value.actual_result = executionForm.actual_result;
    // 显示保存成功提示
    ElMessage.success("保存成功");
  } catch (error) {
    console.error("保存实际结果失败:", error);
    ElMessage.error("保存失败");
  }
};

// 防抖处理后的保存函数
const debouncedSaveActualResult = debounce(saveActualResult, 500);

const treeProps = {
  label: "case_name",
  children: "children",
  isLeaf: (data) => data.type !== "suite",
};

// 解析测试步骤为数组
const parseSteps = (steps) => {
  if (!steps) return [];
  return steps.split("\n").filter((step) => step.trim());
};

// 处理返回 - 关闭当前标签页，用户自然回到原任务列表标签页
const handleBack = () => {
  loading.navigate = true;
  try {
    // 关闭当前标签页
    window.close();
  } catch (error) {
    console.error("关闭标签页失败:", error);
    // 如果关闭失败，退而求其次，在当前标签页跳转回任务列表
    router.push("/test-tasks");
  } finally {
    loading.navigate = false;
  }
};

// 获取任务信息
const getTaskInfo = async () => {
  loading.getTaskInfo = true;
  try {
    const response = await testTaskApi.getTestTaskDetail(taskId);
    taskInfo.value = response.data.test_task;
  } catch (error) {
    console.error("获取任务信息失败:", error);
    ElMessage.error("获取任务信息失败");
  } finally {
    loading.getTaskInfo = false;
  }
};

// 获取任务关联的测试用例
const getTestCases = async () => {
  loading.getTestCases = true;
  try {
    const response = await testTaskApi.getTaskTestCases(taskId);
    testCases.value = response.data.test_cases;
    buildTestCaseTree();
  } catch (error) {
    console.error("获取测试用例失败:", error);
    ElMessage.error("获取测试用例失败");
  } finally {
    loading.getTestCases = false;
  }
};

// 更新任务状态为执行中
const updateTaskToRunning = async () => {
  loading.updateTaskStatus = true;
  try {
    // API只允许执行待执行或已完成状态的任务
      // 如果任务已经处于运行中状态，或者不是待执行/已完成状态，就不需要再次调用API
      if (
        taskInfo.value.status === "running" ||
        (taskInfo.value.status !== "pending" &&
          taskInfo.value.status !== "completed")
      ) {
        return;
      }

    await testTaskApi.executeTestTask(taskId);
    // 重新获取任务信息，更新状态
    await getTaskInfo();
  } catch (error) {
    console.error("更新任务状态失败:", error);
    // 忽略错误，继续执行
  } finally {
    loading.updateTaskStatus = false;
  }
};

// 获取优先级类型
const getPriorityType = (priority) => {
  const priorityMap = {
    P0: "danger",
    P1: "danger",
    P2: "warning",
    P3: "info",
    P4: "info",
  };
  return priorityMap[priority] || "info";
};

// 构建用例树形结构
const buildTestCaseTree = () => {
  const suiteMap = new Map();
  const tree = [];

  // 获取筛选后的用例
  const casesToUse = filteredCases.value;

  // 先处理测试套件
  casesToUse.forEach((caseItem) => {
    if (!suiteMap.has(caseItem.suite_id)) {
      suiteMap.set(caseItem.suite_id, {
        id: caseItem.suite_id,
        case_name: caseItem.suite_name,
        type: "suite",
        children: [],
        pass_count: 0,
        fail_count: 0,
        block_count: 0,
        not_applicable_count: 0,
      });
    }
  });

  // 处理测试用例
  casesToUse.forEach((caseItem) => {
    const suite = suiteMap.get(caseItem.suite_id);
    suite.children.push(caseItem);

    // 更新套件统计
    switch (caseItem.status) {
      case "pass":
        suite.pass_count++;
        break;
      case "fail":
        suite.fail_count++;
        break;
      case "blocked":
        suite.block_count++;
        break;
      case "not_applicable":
        suite.not_applicable_count++;
        break;
    }
  });

  // 转换为数组
  suiteMap.forEach((suite) => {
    tree.push(suite);
  });

  testCaseTree.value = tree;
};

// 处理用例点击
const handleCaseClick = (data) => {
  if (data.type !== "suite") {
    selectedCase.value = data;
    executionForm.actual_result = data.actual_result || "";
  }
};

// 当前选中用例的索引
const currentCaseIndex = computed(() => {
  if (!selectedCase.value) return -1;
  return filteredCases.value.findIndex(
    (caseItem) => caseItem.id === selectedCase.value.id,
  );
});

// 是否有上一条用例
const hasPreviousCase = computed(() => {
  return currentCaseIndex.value > 0;
});

// 是否有下一条用例
const hasNextCase = computed(() => {
  return currentCaseIndex.value < filteredCases.value.length - 1;
});

// 上一条用例
const previousCase = () => {
  if (hasPreviousCase.value) {
    selectedCase.value = filteredCases.value[currentCaseIndex.value - 1];
    executionForm.actual_result = selectedCase.value.actual_result || "";
    // 更新左侧用例列表的选中效果
    if (caseTreeRef.value) {
      caseTreeRef.value.setCurrentKey(selectedCase.value.id);
    }
  }
};

// 下一条用例
const nextCase = () => {
  if (hasNextCase.value) {
    selectedCase.value = filteredCases.value[currentCaseIndex.value + 1];
    executionForm.actual_result = selectedCase.value.actual_result || "";
    // 更新左侧用例列表的选中效果
    if (caseTreeRef.value) {
      caseTreeRef.value.setCurrentKey(selectedCase.value.id);
    }
  }
};

// 筛选用例
const filteredCases = computed(() => {
  return testCases.value.filter((caseItem) => {
    const matchesSearch =
      !filterForm.search ||
      caseItem.case_name.includes(filterForm.search) ||
      (caseItem.case_description &&
        caseItem.case_description.includes(filterForm.search));
    const matchesStatus =
      !filterForm.status ||
      filterForm.status.length === 0 ||
      filterForm.status.includes(caseItem.status);
    return matchesSearch && matchesStatus;
  });
});

// 处理筛选
const handleFilter = () => {
  // 根据筛选条件重新构建树
  buildTestCaseTree();
};

// 获取状态类型
const getStatusType = (status) => {
  const typeMap = {
    pass: "success",
    fail: "danger",
    blocked: "warning",
    not_applicable: "info",
  };
  return typeMap[status] || "";
};

// 获取状态文本
const getStatusText = (status) => {
  const textMap = {
    pass: "通过",
    fail: "失败",
    blocked: "阻塞",
    not_applicable: "不适用",
  };
  return textMap[status] || "";
};

// 更新用例状态
const updateCaseStatus = async (status) => {
  if (!selectedCase.value) {
    ElMessage.warning("请先选择一个测试用例");
    return;
  }

  loading.updateStatus = true;
  try {
    await updateTestCase(selectedCase.value.id, {
      status: status,
      actual_result: executionForm.actual_result,
    });

    // 更新本地数据
    selectedCase.value.status = status;
    selectedCase.value.actual_result = executionForm.actual_result;

    // 重新构建树以更新统计信息
    buildTestCaseTree();

    ElMessage.success("用例状态更新成功");
  } catch (error) {
    console.error("更新用例状态失败:", error);
    ElMessage.error("更新用例状态失败");
  } finally {
    loading.updateStatus = false;
  }
};

// 完成任务
const handleCompleteTask = async () => {
  try {
    await ElMessageBox.confirm("确认完成该测试任务吗？", "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    });

    loading.completeTask = true;
    // 调用API完成任务，更新任务状态
    await testTaskApi.completeTestTask(taskId);
    ElMessage.success("任务完成成功");
    
    // 等待API调用完全完成，然后再关闭标签页
    // 使用更可靠的方式，先刷新当前任务状态，确保任务已完成
    await getTaskInfo();
    
    // 关闭当前标签页
    window.close();
    
    // 如果关闭失败（如从其他页面打开），则跳转回任务列表页面
    setTimeout(() => {
      router.push("/test-task");
    }, 100);
  } catch (error) {
    if (error !== "cancel") {
      console.error("完成任务失败:", error);
      ElMessage.error("完成任务失败");
    }
  } finally {
    loading.completeTask = false;
  }
};

// 统计数据
const totalCases = computed(() => {
  return testCases.value.length;
});

const passCount = computed(() => {
  return testCases.value.filter((caseItem) => caseItem.status === "pass")
    .length;
});

const failCount = computed(() => {
  return testCases.value.filter((caseItem) => caseItem.status === "fail")
    .length;
});

const blockedCount = computed(() => {
  return testCases.value.filter((caseItem) => caseItem.status === "blocked")
    .length;
});

const notApplicableCount = computed(() => {
  return testCases.value.filter(
    (caseItem) => caseItem.status === "not_applicable",
  ).length;
});

const notExecutedCount = computed(() => {
  return testCases.value.filter((caseItem) => !caseItem.status).length;
});

const executionProgress = computed(() => {
  if (totalCases.value === 0) return 0;
  const executed =
    passCount.value +
    failCount.value +
    blockedCount.value +
    notApplicableCount.value;
  return Math.round((executed / totalCases.value) * 100);
});

// 获取进度条颜色
const getProgressColor = (percentage) => {
  if (percentage >= 80) return "#67c23a";
  if (percentage >= 60) return "#e6a23c";
  return "#f56c6c";
};

// 初始化
onMounted(async () => {
  await getTaskInfo();
  // 将任务状态更新为执行中
  await updateTaskToRunning();
  await getTestCases();
});
</script>

<style lang="scss" scoped>
.test-case-execution {
  min-height: 100vh;
  background-color: #f5f7fa;

  // 页面标题和按钮区域样式
  .page-header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    background-color: white;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);

    .title-section {
      flex: 1;

      h1 {
        font-size: 18px;
        font-weight: 600;
        color: #303133;
        margin: 0;
      }
    }

    .buttons-section {
      display: flex;
      gap: 10px;
      align-items: center;

      .el-button {
        font-size: 14px;
        padding: 8px 16px;
      }
    }
  }

  // 主内容区域
  .main-content {
    display: flex;
    padding: 20px;
    gap: 20px;
    align-items: stretch;

    // 左侧用例列表
    .left-panel {
      width: 430px;
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
      display: flex;
      flex-direction: column;
      transition: width 0.3s ease;
      // 固定高度，确保折叠时高度不变
      height: calc(100vh - 160px);

      // 折叠状态样式
      &.collapsed {
        width: 50px;
        // 折叠时保持相同高度
        height: calc(100vh - 160px);
      }

      .filter-section {
        padding: 14px;
        border-bottom: 1px solid #e4e7ed;
        display: flex;
        align-items: center;
        gap: 10px;
        box-sizing: border-box;
        width: 100%;

        .el-input {
          flex: 1;
          width: auto;
          max-width: 200px;
        }

        .el-select {
          flex: 1;
          width: auto;
          max-width: 250px;
        }
      }

      // 折叠状态下的头部样式
      .collapsed-header {
        padding: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
      }

      .case-list {
        flex: 1;
        overflow-y: auto;
        padding: 10px;
        // 设置最大高度，确保内容超出时显示滚动条
        max-height: calc(100vh - 220px);
        // 优化滚动条样式
        scrollbar-width: thin;
        scrollbar-color: #c0c4cc #f5f7fa;

        // Webkit滚动条样式
        &::-webkit-scrollbar {
          width: 6px;
        }

        &::-webkit-scrollbar-track {
          background: #f5f7fa;
        }

        &::-webkit-scrollbar-thumb {
          background-color: #c0c4cc;
          border-radius: 3px;
        }

        &::-webkit-scrollbar-thumb:hover {
          background-color: #909399;
        }

        .tree-node-content {
          display: flex;
          justify-content: space-between;
          align-items: center;
          width: 100%;

          .suite-count {
            font-size: 12px;
            color: #909399;
          }

          .case-name {
            display: flex;
            align-items: center;
            gap: 5px;
          }

          .case-number {
            font-size: 12px;
            color: #909399;
            font-weight: normal;
          }
        }
      }
    }

    // 中间用例详情和执行区域
    .middle-panel {
      flex: 1;
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
      display: flex;
      overflow: hidden;
      // 固定高度，确保折叠时高度不变
      height: calc(100vh - 160px);

      // 导航区域
      .nav-area {
        width: 50px;
        background-color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        // 移除过渡和悬浮效果
        transition: none;

        &:hover {
          background-color: white; // 保持原有背景色，无悬浮效果
        }

        // 移除边框，实现无缝衔接
        &.left-nav-area {
          border-right: none;
        }

        &.right-nav-area {
          border-left: none;
        }
      }

      // 导航按钮
      .nav-button {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background-color: rgba(255, 255, 255, 0.9);
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
        transition: none;
        // 按钮垂直往上移动一点
        margin-top: -50px;

        &:hover {
          background-color: rgba(255, 255, 255, 0.9);
          color: inherit;
        }

        // 左侧按钮增加左外边距
        &.left-button {
          margin-left: 10px;
        }

        // 右侧按钮增加右外边距
        &.right-button {
          margin-right: 10px;
        }

        // 占位元素样式，保持与按钮相同大小
        &.placeholder {
          background: transparent;
          box-shadow: none;
          margin: 0 5px;
          margin-top: -50px;
        }
      }

      // 内容区域
      .content-area {
        flex: 1;
        overflow-y: auto;
        padding: 0;
        display: flex;
        flex-direction: column;

        // 让卡片占满内容区域的高度
        .el-card {
          flex: 1;
          margin: 0;
          border-radius: 0;
          border: none;

          &__header {
            padding: 20px;
            border-bottom: 1px solid #e4e7ed;
          }

          &__body {
            padding: 0;
            flex: 1;
            display: flex;
            flex-direction: column;
          }
        }
      }

      // 卡片头部样式
      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
        padding: 0;
        margin: 0;

        .case-main-info {
          flex: 1;

          h3 {
            font-size: 18px;
            font-weight: 600;
            color: #303133;
            margin: 0;
          }
        }

        .case-meta {
          display: flex;
          gap: 20px;
          align-items: center;

          .meta-item {
            display: flex;
            align-items: center;
            gap: 8px;

            .meta-label {
              font-size: 15px;
              color: #606266;
            }

            .meta-value {
              font-size: 16px;
              color: #303133;
              font-weight: 600;
            }

            .el-tag {
              font-size: 14px;
            }
          }
        }
      }

      .case-detail {
          padding: 20px 20px 0 20px;
          flex: 1;
          display: flex;
          flex-direction: column;

          .el-descriptions {
            margin-bottom: 15px;

            &__title {
              font-size: 15px;
              font-weight: 600;
              margin-bottom: 8px;
            }

            &__item-label {
              font-weight: 500;
            }

            // 调整描述内容字体大小和行高
            &__item-content {
              font-size: 14px;
              line-height: 20px;
              color: #606266;
            }
          }

          // 测试步骤样式，移除序号
          .step-item {
            margin-bottom: 8px;
            padding-left: 10px;
            border-left: 3px solid #ecf5ff;

            .step-content {
              color: #606266;
              line-height: 20px;
              font-size: 14px;
            }
          }

        .execution-section {
          margin-top: 15px;
          padding-top: 15px;
          border-top: 1px solid #e4e7ed;

          .status-buttons {
            display: flex;
            gap: 10px;

            .el-button {
              min-width: 80px;
            }
          }
        }
      }

      .no-selection {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        flex: 1;
      }
    }

    // 右侧执行统计
    .right-panel {
      width: 200px;
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
      // 确保高度与其他区域同步
      display: flex;
      flex-direction: column;

      .el-card {
        flex: 1;
        margin: 0;
        border-radius: 8px;
        border: none;
        box-shadow: none;
      }

      .stats-content {
        padding: 12px;

        // 总用例数统计
        .total-stats {
          text-align: center;
          margin-bottom: 18px;

          .total-number {
            font-size: 30px;
            font-weight: 700;
            color: #303133;
          }

          .total-label {
            font-size: 14px;
            color: #909399;
            margin-top: 4px;
          }
        }

        // 状态统计，添加颜色区分
        .status-stats {
          display: grid;
          grid-template-columns: 1fr;
          gap: 10px;
          margin-bottom: 18px;

          .stat-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 10px;
            background-color: #f5f7fa;
            border-radius: 7px;
            transition: all 0.3s;

            &:hover {
              transform: translateY(-1px);
              box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }

            .stat-number {
              font-size: 20px;
              font-weight: 600;
              color: #303133;
            }

            .stat-label {
              font-size: 12px;
              color: #909399;
              margin-top: 3px;
              font-weight: 500;
            }

            // 状态颜色区分
            &.status-pass {
              background-color: rgba(103, 194, 58, 0.1);

              .stat-label {
                color: #67c23a;
              }
            }

            &.status-fail {
              background-color: rgba(245, 108, 108, 0.1);

              .stat-label {
                color: #f56c6c;
              }
            }

            &.status-blocked {
              background-color: rgba(230, 162, 60, 0.1);

              .stat-label {
                color: #e6a23c;
              }
            }

            &.status-not-applicable {
              background-color: rgba(144, 147, 153, 0.1);

              .stat-label {
                color: #909399;
              }
            }

            &.status-not-executed {
              background-color: rgba(64, 158, 255, 0.1);

              .stat-label {
                color: #409eff;
              }
            }
          }
        }

        // 进度条样式
        .progress-text {
          display: flex;
          flex-direction: column;
          align-items: center;
          font-size: 14px;
          color: #606266;

          span:first-child {
            font-size: 18px;
            font-weight: 600;
            color: #303133;
          }
        }
      }
    }
  }
}
</style>
