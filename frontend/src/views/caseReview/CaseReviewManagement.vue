<template>
  <div class="case-review-management">
    <el-card class="review-card">
      <!-- 评审中心选项卡 -->
      <el-tabs v-model="activeTab" class="review-tabs">
        <!-- 待我评审 -->
        <el-tab-pane label="待我评审" name="my-tasks">
          <div class="review-section">
            <div class="section-header">
              <h3>待我评审的用例集</h3>
            </div>

            <el-table
              v-loading="loading.myTasks"
              :data="myTasks"
              style="width: 100%"
              row-key="id"
              header-align="center"
              align="center"
              @row-click="handleTaskClick"
            >
              <el-table-column
                prop="project_name"
                label="所属项目"
                width="200"
                header-align="center"
                align="center"
              />
              <el-table-column
                prop="iteration_name"
                label="所属迭代"
                width="180"
                header-align="center"
                align="center"
              />
              <el-table-column
                prop="requirement_name"
                label="关联需求"
                width="200"
                header-align="center"
                align="center"
              />
              <el-table-column
                prop="suite_name"
                label="用例集名称"
                min-width="200"
                header-align="center"
                align="center"
              />
              <el-table-column
                prop="initiator_name"
                label="发起人"
                width="180"
                header-align="center"
                align="center"
              />
              <el-table-column
                label="评审进度"
                width="180"
                header-align="center"
                align="center"
              >
                <template #default="scope">
                  <div class="progress-info">
                    <el-progress
                      :percentage="scope.row.review_progress.progress_percent"
                      :stroke-width="8"
                      :color="
                        progressColor(
                          scope.row.review_progress.progress_percent,
                        )
                      "
                    />
                  </div>
                </template>
              </el-table-column>
              <el-table-column
                prop="status"
                label="评审状态"
                width="180"
                header-align="center"
                align="center"
              >
                <template #default="scope">
                  <el-tag
                    :type="getStatusTagType(scope.row.status)"
                    size="small"
                  >
                    {{ getStatusText(scope.row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column
                label="创建时间"
                width="180"
                header-align="center"
                align="center"
              >
                <template #default="scope">
                  {{ formatDate(scope.row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column
                label="操作"
                width="160"
                fixed="right"
                header-align="center"
                align="center"
              >
                <template #default="scope">
                  <el-button
                    type="primary"
                    size="small"
                    @click.stop="
                      scope.row.status === 'completed' ||
                      scope.row.status === 'rejected'
                        ? handleViewDetail(scope.row)
                        : handleReview(scope.row)
                    "
                  >
                    {{
                      scope.row.status === "completed"
                        ? "查看评审"
                        : scope.row.status === "in_review"
                          ? "继续评审"
                          : scope.row.status === "rejected"
                            ? "查看评审"
                            : "开始评审"
                    }}
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 我发起的评审 -->
        <el-tab-pane label="我发起的评审" name="my-initiated">
          <div class="review-section">
            <div class="section-header">
              <h3>我发起的评审</h3>
            </div>

            <el-table
              v-loading="loading.myInitiated"
              :data="myInitiated"
              style="width: 100%"
              row-key="id"
              header-align="center"
              align="center"
              @row-click="handleTaskClick"
            >
              <el-table-column
                prop="project_name"
                label="所属项目"
                width="200"
                header-align="center"
                align="center"
              />
              <el-table-column
                prop="iteration_name"
                label="所属迭代"
                width="180"
                header-align="center"
                align="center"
              />
              <el-table-column
                prop="requirement_name"
                label="关联需求"
                width="200"
                header-align="center"
                align="center"
              />
              <el-table-column
                prop="suite_name"
                label="用例集名称"
                min-width="200"
                header-align="center"
                align="center"
              />
              <el-table-column
                prop="reviewer_name"
                label="评审人"
                width="180"
                header-align="center"
                align="center"
              />
              <el-table-column
                label="评审进度"
                width="180"
                header-align="center"
                align="center"
              >
                <template #default="scope">
                  <div class="progress-info">
                    <el-progress
                      :percentage="scope.row.review_progress.progress_percent"
                      :stroke-width="8"
                      :color="
                        progressColor(
                          scope.row.review_progress.progress_percent,
                        )
                      "
                    />
                  </div>
                </template>
              </el-table-column>
              <el-table-column
                prop="status"
                label="评审状态"
                width="180"
                header-align="center"
                align="center"
              >
                <template #default="scope">
                  <el-tag
                    :type="getStatusTagType(scope.row.status)"
                    size="small"
                  >
                    {{ getStatusText(scope.row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column
                label="创建时间"
                width="180"
                header-align="center"
                align="center"
              >
                <template #default="scope">
                  {{ formatDate(scope.row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column
                label="操作"
                width="160"
                fixed="right"
                header-align="center"
                align="center"
              >
                <template #default="scope">
                  <el-button
                    type="primary"
                    size="small"
                    @click.stop="handleViewDetail(scope.row)"
                  >
                    查看详情
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 评审历史 -->
        <el-tab-pane label="评审历史" name="review-history">
          <div class="review-section">
            <div class="section-header">
              <h3>用例集评审历史记录</h3>
            </div>

            <!-- 用例集选择器 -->
            <div class="suite-selector">
              <el-form :inline="true" class="suite-form">
                <el-form-item label="目标用例集">
                  <div class="case-suite-selector">
                    <!-- 显示当前选中的用例集路径 -->
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
                          v-model="selectedSuitePath"
                          placeholder="点击选择所属用例集"
                          readonly
                          style="width: 250px"
                          @click="suitePopoverVisible = !suitePopoverVisible"
                        />
                      </template>
                      <!-- 弹出的套件树 -->
                      <div
                        class="suite-tree-popover"
                        style="width: 100%; min-width: 300px; max-width: 400px"
                      >
                        <el-tree
                          :current-node-key="selectedSuiteId"
                          :data="suiteTreeData"
                          :props="defaultProps"
                          node-key="id"
                          style="
                            max-height: 300px;
                            overflow-y: auto;
                            width: 100%;
                            padding-right: 10px;
                          "
                          :expand-on-click-node="false"
                          :filter-node-method="filterSuiteType"
                          @node-click="handleSuiteSelect"
                        >
                          <template #default="{ node, data }">
                            <span
                              class="tree-node-content"
                              :class="{
                                'current-node': node.key === selectedSuiteId,
                                'disabled-folder': data.type === 'folder',
                              }"
                            >
                              <el-icon
                                class="node-icon"
                                @click.stop="
                                  data.type === 'suite' &&
                                  handleSuiteSelect(data)
                                "
                              >
                                <!-- 这里使用el-icon，需要确保已导入相关图标 -->
                                <span v-if="data.type === 'suite'">📄</span>
                                <span v-else>📁</span>
                              </el-icon>
                              <span
                                class="node-label"
                                @click.stop="
                                  data.type === 'suite' &&
                                  handleSuiteSelect(data)
                                "
                                >{{ node.label }}</span
                              >
                              <span
                                v-if="
                                  data.type === 'suite' && data.cases_count > 0
                                "
                                class="case-count"
                                >({{ data.cases_count }})</span
                              >
                            </span>
                          </template>
                        </el-tree>
                      </div>
                    </el-popover>
                  </div>
                </el-form-item>
              </el-form>
            </div>

            <!-- 评审历史列表 -->
            <el-table
              v-loading="loading.reviewHistory"
              :data="reviewHistory"
              style="width: 100%"
              row-key="id"
              header-align="center"
              align="center"
              fit
            >
              <el-table-column
                prop="created_at"
                label="评审时间"
                min-width="160"
                header-align="center"
                align="center"
              >
                <template #default="scope">
                  {{ formatDate(scope.row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column
                prop="initiator_name"
                label="发起人"
                min-width="120"
                header-align="center"
                align="center"
              />
              <el-table-column
                prop="reviewer_name"
                label="评审人"
                min-width="120"
                header-align="center"
                align="center"
              />
              <el-table-column
                prop="status"
                label="评审状态"
                min-width="120"
                header-align="center"
                align="center"
              >
                <template #default="scope">
                  <el-tag
                    :type="
                      getStatusTagType(scope.row.status, scope.row.history_type)
                    "
                    size="small"
                  >
                    {{
                      getStatusText(scope.row.status, scope.row.history_type)
                    }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column
                prop="case_stats.total"
                label="总用例数"
                min-width="80"
                header-align="center"
                align="center"
              />
              <el-table-column
                prop="case_stats.approved"
                label="通过数"
                min-width="80"
                header-align="center"
                align="center"
              />
              <el-table-column
                prop="case_stats.rejected"
                label="拒绝数"
                min-width="80"
                header-align="center"
                align="center"
              />
              <el-table-column
                label="操作"
                min-width="120"
                header-align="center"
                align="center"
              >
                <template #default="scope">
                  <el-button
                    type="primary"
                    size="small"
                    @click.stop="handleViewReviewHistory(scope.row)"
                  >
                    查看详情
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 评审详情弹窗 -->
    <el-dialog
      v-model="reviewDialogVisible"
      :title="reviewDialogTitle"
      :width="'90%'"
      :before-close="handleDialogClose"
    >
      <div v-if="currentReviewTask" class="review-dialog-content">
        <!-- 评审任务基本信息 -->
        <div class="dialog-section">
          <h4>评审任务信息</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="用例集名称">
              {{
                currentReviewTask?.suite?.suite_name ||
                currentReviewTask?.suite_name ||
                "-"
              }}
            </el-descriptions-item>
            <el-descriptions-item label="发起人">
              {{ currentReviewTask?.initiator_name || "-" }}
            </el-descriptions-item>
            <el-descriptions-item label="评审人">
              {{ currentReviewTask?.reviewer_name || "-" }}
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ formatDate(currentReviewTask?.created_at) || "-" }}
            </el-descriptions-item>
            <!-- 添加版本信息显示 -->
            <el-descriptions-item
              v-if="currentReviewTask?.version"
              label="版本号"
            >
              {{ currentReviewTask?.version }}
            </el-descriptions-item>
            <el-descriptions-item
              label="状态"
              :span="currentReviewTask?.version ? 1 : 2"
            >
              <el-tag
                :type="
                  getStatusTagType(
                    currentReviewTask?.status,
                    currentReviewTask?.history_type,
                  )
                "
              >
                {{
                  getStatusText(
                    currentReviewTask?.status,
                    currentReviewTask?.history_type,
                  )
                }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 用例评审列表 -->
        <div class="dialog-section">
          <h4>用例评审列表</h4>
          <el-table
            v-loading="loading.caseReviews"
            :data="caseReviews"
            style="width: 100%"
            row-key="id"
            :row-style="{ height: 'auto' }"
            :cell-style="{
              'white-space': 'pre-wrap',
              'word-break': 'break-word',
              'line-height': '1.5',
            }"
          >
            <el-table-column label="用例编号" min-width="130">
              <template #default="scope">
                {{
                  scope.row.case_number ||
                  scope.row.test_case?.case_number ||
                  "-"
                }}
              </template>
            </el-table-column>
            <el-table-column label="用例名称" min-width="140">
              <template #default="scope">
                {{
                  scope.row.case_name || scope.row.test_case?.case_name || "-"
                }}
              </template>
            </el-table-column>
            <el-table-column label="优先级" width="90">
              <template #default="scope">
                <el-tag
                  :type="
                    getPriorityTagType(
                      scope.row.priority ||
                        scope.row.test_case?.priority ||
                        'P3',
                    )
                  "
                  size="small"
                >
                  {{
                    scope.row.priority || scope.row.test_case?.priority || "-"
                  }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column label="测试数据" min-width="120">
              <template #default="scope">
                <div class="text-with-newlines">
                  {{
                    scope.row.test_data || scope.row.test_case?.test_data || "-"
                  }}
                </div>
              </template>
            </el-table-column>
            <el-table-column label="前置条件" min-width="160">
              <template #default="scope">
                <div class="text-with-newlines">
                  {{
                    scope.row.preconditions ||
                    scope.row.test_case?.preconditions ||
                    "-"
                  }}
                </div>
              </template>
            </el-table-column>
            <el-table-column label="测试步骤" min-width="170">
              <template #default="scope">
                <div class="text-with-newlines">
                  {{ scope.row.steps || scope.row.test_case?.steps || "-" }}
                </div>
              </template>
            </el-table-column>
            <el-table-column label="预期结果" min-width="160">
              <template #default="scope">
                <div class="text-with-newlines">
                  {{
                    scope.row.expected_result ||
                    scope.row.test_case?.expected_result ||
                    "-"
                  }}
                </div>
              </template>
            </el-table-column>
            <el-table-column label="实际结果" min-width="160">
              <template #default="scope">
                <div class="text-with-newlines">
                  {{
                    scope.row.actual_result ||
                    scope.row.test_case?.actual_result ||
                    "-"
                  }}
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="review_status" label="评审状态" width="100">
              <template #default="scope">
                <!-- 如果是评审人，显示可编辑的单选按钮组 -->
                <el-radio-group
                  v-if="isReviewer"
                  v-model="scope.row.review_status"
                  size="small"
                >
                  <el-radio-button label="pending"> 待审核 </el-radio-button>
                  <el-radio-button label="approved"> 已通过 </el-radio-button>
                  <el-radio-button label="rejected"> 已拒绝 </el-radio-button>
                </el-radio-group>
                <!-- 如果是发起人或其他用户，显示只读的状态标签 -->
                <el-tag
                  v-else
                  :type="getCaseReviewStatusTagType(scope.row.review_status)"
                >
                  {{ getCaseReviewStatusText(scope.row.review_status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="comments" label="评审意见" min-width="200">
              <template #default="scope">
                <!-- 如果是评审人，显示可编辑的输入框 -->
                <el-input
                  v-if="isReviewer"
                  v-model="scope.row.comments"
                  type="textarea"
                  :rows="2"
                  placeholder="请输入评审意见"
                  resize="none"
                  size="small"
                />
                <!-- 如果是发起人或其他用户，显示只读的评审意见 -->
                <div v-else class="read-only-comments">
                  {{ scope.row.comments || "-" }}
                </div>
              </template>
            </el-table-column>
            <el-table-column
              prop="updated_at"
              label="评审时间"
              width="150"
              :formatter="formatDate"
            >
              <template #default="scope">
                {{ formatDate(scope.row.updated_at) || "-" }}
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 整体评审意见 -->
        <div
          v-if="isReviewer || isInitiator || currentReviewTask?.version"
          class="dialog-section"
        >
          <h4>整体评审意见</h4>
          <!-- 如果是评审人，显示可编辑的输入框 -->
          <el-input
            v-if="isReviewer"
            v-model="overallComments"
            type="textarea"
            :rows="4"
            placeholder="请输入整体评审意见"
          />
          <!-- 如果是发起人或评审历史详情，显示只读的评审意见 -->
          <div v-else class="read-only-comments">
            {{ overallComments || "暂无整体评审意见" }}
          </div>
        </div>
      </div>

      <!-- 对话框底部按钮 -->
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="reviewDialogVisible = false">关闭</el-button>

          <!-- 只有当不是评审历史详情（即没有version属性）时，才显示操作按钮 -->
          <template v-if="!currentReviewTask?.version">
            <!-- 评审人操作按钮 -->
            <template v-if="isReviewer">
              <!-- 如果评审未完成，显示完成评审按钮 -->
              <el-button
                v-if="
                  currentReviewTask &&
                  currentReviewTask.status !== 'completed' &&
                  currentReviewTask.status !== 'rejected'
                "
                type="primary"
                :disabled="!canCompleteReview"
                @click="handleCompleteReview"
              >
                完成评审
              </el-button>
              <!-- 如果评审已完成，显示重新评审按钮 -->
              <el-button
                v-else-if="
                  currentReviewTask && currentReviewTask.status === 'completed'
                "
                type="warning"
                @click="handleRestartReview"
              >
                重新评审
              </el-button>
              <!-- 如果是评审人且评审状态不是待处理，显示打回评审按钮 -->
              <el-button
                v-if="
                  currentReviewTask &&
                  currentReviewTask.status !== 'pending' &&
                  currentReviewTask.status !== 'rejected'
                "
                type="danger"
                @click="handleRejectReview"
              >
                打回评审
              </el-button>
            </template>

            <!-- 发起人操作按钮：已拒绝的评审可以重新发起 -->
            <el-button
              v-if="
                isInitiator &&
                currentReviewTask &&
                currentReviewTask.status === 'rejected'
              "
              type="warning"
              @click="handleReinitiateReview"
            >
              重新发起评审
            </el-button>
          </template>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRoute } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import * as reviewApi from "@/api/reviewTask";
import * as testSuiteApi from "@/api/testSuite";
import { useUserStore } from "@/stores/user";

// 状态管理
const userStore = useUserStore();
const route = useRoute();
// 从路由参数中获取activeTab，默认值为'my-tasks'
const activeTab = ref(route.query.activeTab || "my-tasks");
const loading = ref({
  myTasks: false,
  myInitiated: false,
  caseReviews: false,
  updateReview: false,
  reviewHistory: false,
  suites: false,
});

// 数据
const myTasks = ref([]);
const myInitiated = ref([]);
const caseReviews = ref([]);
const originalCaseReviews = ref([]); // 保存原始的用例评审数据，用于判断哪些用例被修改了
const currentReviewTask = ref(null);
const reviewDialogVisible = ref(false);
const reviewDialogTitle = ref("");
const overallComments = ref("");

// 评审历史相关
const selectedSuiteId = ref(null);
const selectedSuitePath = ref("");
const suitePopoverVisible = ref(false);
const suiteTreeData = ref([]);
const defaultProps = ref({
  label: "suite_name",
  children: "children",
});
const reviewHistory = ref([]);

// 计算属性
const isReviewer = computed(() => {
  // 评审历史详情是只读的，无论用户是否为评审人
  if (currentReviewTask.value?.version) {
    return false;
  }

  // 已拒绝的评审，评审人无法编辑
  if (currentReviewTask.value?.status === "rejected") {
    return false;
  }

  // 根据当前登录用户和评审任务的评审人信息判断是否为评审人
  if (!userStore.userInfo || !currentReviewTask.value) return false;
  // 确保类型一致，转换为字符串进行比较
  const currentUserId = String(userStore.userInfo.id);
  const reviewerId = String(currentReviewTask.value.reviewer_id);
  return currentUserId === reviewerId;
});

const isInitiator = computed(() => {
  // 根据当前登录用户和评审任务的发起人信息判断是否为发起人
  if (!userStore.userInfo || !currentReviewTask.value) return false;
  // 确保类型一致，转换为字符串进行比较
  const currentUserId = String(userStore.userInfo.id);
  const initiatorId = String(currentReviewTask.value.initiator_id);
  return currentUserId === initiatorId;
});

const canCompleteReview = computed(() => {
  // 评审历史详情是只读的，不允许完成评审
  if (currentReviewTask.value?.version) {
    return false;
  }

  // 已拒绝的评审，不允许完成评审
  if (currentReviewTask.value?.status === "rejected") {
    return false;
  }

  // 如果没有用例，允许完成评审
  if (!caseReviews.value.length) return true;
  // 检查是否所有用例都已评审
  return caseReviews.value.every((cr) => cr.review_status !== "pending");
});

// 方法
// 获取我的评审任务
const getMyTasks = async () => {
  loading.value.myTasks = true;
  try {
    const response = await reviewApi.getMyReviewTasks();
    myTasks.value = response.data.items || [];
  } catch (error) {
    ElMessage.error("获取我的评审任务失败");
  } finally {
    loading.value.myTasks = false;
  }
};

// 获取我发起的评审
const getMyInitiated = async () => {
  loading.value.myInitiated = true;
  try {
    const response = await reviewApi.getMyInitiatedReviews();
    myInitiated.value = response.data.items || [];
  } catch (error) {
    ElMessage.error("获取我发起的评审失败");
  } finally {
    loading.value.myInitiated = false;
  }
};

// 获取评审任务详情
const getReviewTaskDetail = async (taskId) => {
  loading.value.caseReviews = true;
  try {
    const response = await reviewApi.getReviewTask(taskId);
    currentReviewTask.value = response.data;

    // 获取用例评审详情
    const caseResponse = await reviewApi.getCaseReviews(taskId);
    caseReviews.value = caseResponse.data.case_reviews || [];

    // 保存原始用例评审数据，用于判断哪些用例被修改了
    originalCaseReviews.value = JSON.parse(JSON.stringify(caseReviews.value));

    // 获取整体评审意见
    overallComments.value = response.data.overall_comments || "";
  } catch (error) {
    ElMessage.error("获取评审任务详情失败");
  } finally {
    loading.value.caseReviews = false;
  }
};

// 处理任务点击
const handleTaskClick = (row) => {
  reviewDialogTitle.value = "评审详情";
  reviewDialogVisible.value = true;
  getReviewTaskDetail(row.id);
};

// 处理开始评审
const handleReview = async (row) => {
  reviewDialogTitle.value = "开始评审";
  reviewDialogVisible.value = true;
  await getReviewTaskDetail(row.id);

  // 如果评审任务状态是待处理，将其改为评审中
  if (currentReviewTask.value && currentReviewTask.value.status === "pending") {
    try {
      // 获取第一个用例，用于触发评审开始
      if (caseReviews.value.length > 0) {
        const firstCase = caseReviews.value[0];
        // 调用更新用例评审API，不修改实际内容，只是触发评审任务状态更新
        await reviewApi.updateCaseReview(
          firstCase.review_task_id,
          firstCase.case_id,
          {
            review_status: firstCase.review_status,
            comments: firstCase.comments || "",
          },
        );
        // 重新获取评审任务详情，更新状态
        await getReviewTaskDetail(row.id);
      }
    } catch (error) {
      console.error("更新评审状态失败:", error);
      ElMessage.error("更新评审状态失败");
    }
  }
};

// 处理查看详情
const handleViewDetail = (row) => {
  reviewDialogTitle.value = "评审详情";
  reviewDialogVisible.value = true;
  getReviewTaskDetail(row.id);
};

// 评审历史相关方法
// 获取可用用例集树状结构
const getAvailableSuites = async () => {
  loading.value.suites = true;
  try {
    // 调用获取用例集树状结构的API
    const response = await testSuiteApi.getTestSuiteTree();
    suiteTreeData.value = response.data || [];
  } catch (error) {
    ElMessage.error("获取用例集列表失败");
    console.error("获取用例集列表失败:", error);
  } finally {
    loading.value.suites = false;
  }
};

// 处理用例集选择
const handleSuiteSelect = (data) => {
  // 确保只处理类型为suite的测试套件
  if (data.type === "suite") {
    selectedSuiteId.value = data.id;
    selectedSuitePath.value = buildSuitePath(data);
    suitePopoverVisible.value = false;

    // 自动查询评审历史
    handleGetReviewHistory();
  }
};

// 过滤节点方法：确保文件夹可展开，但不可选择
const filterSuiteType = (value, data) => {
  // 允许所有节点显示，包括文件夹
  return true;
};

// 构建用例集路径
const buildSuitePath = (data) => {
  // 简化实现：直接返回当前套件名称
  return data.suite_name;
};

// 获取评审历史记录
const handleGetReviewHistory = async () => {
  if (!selectedSuiteId.value) {
    ElMessage.warning("请先选择用例集");
    return;
  }

  loading.value.reviewHistory = true;
  try {
    const response = await reviewApi.getSuiteReviewStatus(
      selectedSuiteId.value,
    );
    reviewHistory.value = response.data.review_history || [];
  } catch (error) {
    ElMessage.error("获取评审历史记录失败");
    console.error("获取评审历史记录失败:", error);
  } finally {
    loading.value.reviewHistory = false;
  }
};

// 查看评审历史详情
const handleViewReviewHistory = async (row) => {
  reviewDialogTitle.value = "评审历史详情";
  reviewDialogVisible.value = true;
  loading.value.caseReviews = true;
  try {
    // 调用获取评审历史详情的API
    const response = await reviewApi.getReviewHistoryDetail(row.id);

    // 构建当前评审任务对象，适配现有的弹窗UI
    currentReviewTask.value = {
      ...response.data,
      suite_name: response.data.suite?.suite_name || "",
      initiator_name: response.data.initiator_name || "",
      reviewer_name: response.data.reviewer_name || "",
      created_at: response.data.created_at,
      status: response.data.status,
    };

    // 适配用例评审列表
    caseReviews.value = response.data.case_reviews || [];

    // 保存原始用例评审数据
    originalCaseReviews.value = JSON.parse(JSON.stringify(caseReviews.value));

    // 获取整体评审意见
    overallComments.value = response.data.overall_comments || "";
  } catch (error) {
    ElMessage.error("获取评审历史详情失败");
  } finally {
    loading.value.caseReviews = false;
  }
};

// 处理评审状态变化
const handleReviewStatusChange = async (row) => {
  loading.value.updateReview = true;
  try {
    const response = await reviewApi.updateCaseReview(
      row.review_task_id,
      row.case_id,
      {
        review_status: row.review_status,
        comments: row.comments || "",
      },
    );

    // 更新本地数据，保留原来的test_case信息
    const index = caseReviews.value.findIndex((cr) => cr.id === row.id);
    if (index > -1) {
      // 合并数据，保留原来的test_case信息
      caseReviews.value[index] = {
        ...response.data,
        test_case: caseReviews.value[index].test_case,
      };
    }

    ElMessage.success("评审状态更新成功");

    // 刷新任务列表
    if (activeTab.value === "my-tasks") {
      getMyTasks();
    } else {
      getMyInitiated();
    }
  } catch (error) {
    ElMessage.error("更新评审状态失败");
  } finally {
    loading.value.updateReview = false;
  }
};

// 处理评审意见变化
const handleCommentsChange = async (row) => {
  loading.value.updateReview = true;
  try {
    // 确保review_status有值
    const status = row.review_status || "pending";
    const response = await reviewApi.updateCaseReview(
      row.review_task_id,
      row.case_id,
      {
        review_status: status,
        comments: row.comments || "",
      },
    );

    // 更新本地数据，保留原来的test_case信息
    const index = caseReviews.value.findIndex((cr) => cr.id === row.id);
    if (index > -1) {
      // 合并数据，保留原来的test_case信息
      caseReviews.value[index] = {
        ...response.data,
        test_case: caseReviews.value[index].test_case,
      };
    }

    ElMessage.success("评审意见更新成功");
  } catch (error) {
    console.error("更新评审意见失败:", error);
    ElMessage.error(
      "更新评审意见失败: " + (error.response?.data?.message || error.message),
    );
  } finally {
    loading.value.updateReview = false;
  }
};

// 处理完成评审
const handleCompleteReview = async () => {
  if (!currentReviewTask.value) return;

  await ElMessageBox.confirm("确定要完成评审并通知发起人吗？", "提示", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  });

  loading.value.updateReview = true;
  try {
    // 1. 收集所有被修改的用例评审
    const modifiedCaseReviews = [];

    // 遍历当前用例评审列表
    for (const currentReview of caseReviews.value) {
      // 找到对应的原始评审数据
      const originalReview = originalCaseReviews.value.find(
        (orig) => orig.id === currentReview.id,
      );

      // 如果找到原始数据并且有修改，添加到修改列表中
      if (originalReview) {
        // 检查评审状态或评审意见是否有修改
        if (
          currentReview.review_status !== originalReview.review_status ||
          currentReview.comments !== originalReview.comments
        ) {
          modifiedCaseReviews.push({
            review_task_id: currentReview.review_task_id,
            case_id: currentReview.case_id,
            review_status: currentReview.review_status,
            comments: currentReview.comments || "",
          });
        }
      }
    }

    // 2. 批量更新被修改的用例评审
    for (const caseReview of modifiedCaseReviews) {
      await reviewApi.updateCaseReview(
        caseReview.review_task_id,
        caseReview.case_id,
        {
          review_status: caseReview.review_status,
          comments: caseReview.comments,
        },
      );
    }

    // 3. 完成评审任务，更新任务相关的时间属性
    await reviewApi.completeReview(currentReviewTask.value.id, {
      overall_comments: overallComments.value,
    });

    ElMessage.success("评审完成成功");
    reviewDialogVisible.value = false;

    // 刷新列表
    if (activeTab.value === "my-tasks") {
      getMyTasks();
    } else {
      getMyInitiated();
    }
  } catch (error) {
    ElMessage.error("完成评审失败");
  } finally {
    loading.value.updateReview = false;
  }
};

// 处理重新评审：评审人修改已完成的评审
const handleRestartReview = async () => {
  if (!currentReviewTask.value) return;

  await ElMessageBox.confirm(
    "确定要重新评审该任务吗？此操作将允许您修改评审结果。",
    "提示",
    {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    },
  );

  loading.value.updateReview = true;
  try {
    await reviewApi.restartReview(currentReviewTask.value.id);

    ElMessage.success("重新评审成功");

    // 重新获取评审任务详情，更新本地数据
    await getReviewTaskDetail(currentReviewTask.value.id);

    // 刷新列表
    if (activeTab.value === "my-tasks") {
      getMyTasks();
    } else {
      getMyInitiated();
    }
  } catch (error) {
    ElMessage.error("重新评审失败");
  } finally {
    loading.value.updateReview = false;
  }
};

// 处理重新发起评审：发起人重新发起已拒绝的评审
const handleReinitiateReview = async () => {
  if (!currentReviewTask.value) return;

  await ElMessageBox.confirm(
    "确定重新发起评审进入评审状态，并保留用例评审结果吗？",
    "提示",
    {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    },
  );

  loading.value.updateReview = true;
  try {
    await reviewApi.reinitiateReview(currentReviewTask.value.id);

    ElMessage.success("重新发起评审成功");

    // 重新获取评审任务详情，更新本地数据
    await getReviewTaskDetail(currentReviewTask.value.id);

    // 刷新列表
    if (activeTab.value === "my-tasks") {
      getMyTasks();
    } else {
      getMyInitiated();
    }
  } catch (error) {
    ElMessage.error("重新发起评审失败");
  } finally {
    loading.value.updateReview = false;
  }
};

// 处理打回评审
const handleRejectReview = async () => {
  if (!currentReviewTask.value) return;

  await ElMessageBox.confirm(
    "确定要打回评审吗？此操作将保存当前评审编辑并重置评审状态。",
    "提示",
    {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    },
  );

  loading.value.updateReview = true;
  try {
    // 1. 收集所有被修改的用例评审
    const modifiedCaseReviews = [];

    // 遍历当前用例评审列表
    for (const currentReview of caseReviews.value) {
      // 找到对应的原始评审数据
      const originalReview = originalCaseReviews.value.find(
        (orig) => orig.id === currentReview.id,
      );

      // 如果找到原始数据并且有修改，添加到修改列表中
      if (originalReview) {
        // 检查评审状态或评审意见是否有修改
        if (
          currentReview.review_status !== originalReview.review_status ||
          currentReview.comments !== originalReview.comments
        ) {
          modifiedCaseReviews.push({
            review_task_id: currentReview.review_task_id,
            case_id: currentReview.case_id,
            review_status: currentReview.review_status,
            comments: currentReview.comments || "",
          });
        }
      }
    }

    // 2. 批量更新被修改的用例评审
    for (const caseReview of modifiedCaseReviews) {
      await reviewApi.updateCaseReview(
        caseReview.review_task_id,
        caseReview.case_id,
        {
          review_status: caseReview.review_status,
          comments: caseReview.comments,
        },
      );
    }

    // 3. 调用打回评审API
    await reviewApi.rejectReview(currentReviewTask.value.id, {
      overall_comments: overallComments.value,
    });

    ElMessage.success("打回评审成功");

    // 关闭对话框
    reviewDialogVisible.value = false;

    // 刷新列表
    if (activeTab.value === "my-tasks") {
      getMyTasks();
    } else {
      getMyInitiated();
    }
  } catch (error) {
    console.error("打回评审失败:", error);
    ElMessage.error(
      "打回评审失败: " + (error.response?.data?.message || error.message),
    );
  } finally {
    loading.value.updateReview = false;
  }
};

// 处理对话框关闭
const handleDialogClose = () => {
  // 重置数据
  currentReviewTask.value = null;
  caseReviews.value = [];
  overallComments.value = "";
  reviewDialogVisible.value = false;

  // 刷新对应的列表数据
  if (activeTab.value === "my-tasks") {
    getMyTasks();
  } else if (activeTab.value === "my-initiated") {
    getMyInitiated();
  }
  // 不需要刷新评审历史列表，因为历史记录不会因为查看详情而改变
};

// 辅助方法
const formatDate = (time) => {
  if (!time) return "-";
  try {
    // 处理各种格式的时间字符串，确保浏览器能够正确解析
    let date;
    if (typeof time === "string") {
      // 如果已经是YYYY-MM-DD HH:mm:ss格式，直接返回
      if (/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/.test(time)) {
        return time;
      }

      // 尝试直接解析
      date = new Date(time);
      // 如果解析失败，尝试处理不同的日期格式
      if (isNaN(date.getTime())) {
        // 处理后端返回的 '%Y-%m-%d %H:%M:%S' 格式
        const parts = time.split(/[- :]/);
        if (parts.length >= 6) {
          date = new Date(
            parts[0],
            parts[1] - 1,
            parts[2],
            parts[3],
            parts[4],
            parts[5],
          );
        } else {
          return "-";
        }
      }
    } else {
      date = new Date(time);
    }
    if (isNaN(date.getTime())) {
      return "-";
    }

    // 手动构建固定格式的时间字符串：YYYY-MM-DD HH:mm:ss
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");
    const seconds = String(date.getSeconds()).padStart(2, "0");

    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  } catch (error) {
    console.error("时间格式化失败:", error);
    return "-";
  }
};

// 获取评审状态文本
const getStatusText = (status, historyType = null) => {
  // 如果是评审历史记录且有historyType，优先根据historyType显示
  if (historyType) {
    if (historyType === "reject") {
      return "已打回";
    } else if (historyType === "complete") {
      return "已完成";
    }
  }

  // 否则使用默认状态映射
  const statusMap = {
    pending: "待处理",
    in_review: "评审中",
    completed: "已完成",
    rejected: "已拒绝",
  };
  return statusMap[status] || status;
};

const getStatusTagType = (status, historyType = null) => {
  // 如果是评审历史记录且有historyType，优先根据historyType显示
  if (historyType) {
    if (historyType === "reject") {
      return "danger";
    } else if (historyType === "complete") {
      return "success";
    }
  }

  // 否则使用默认状态映射
  const typeMap = {
    pending: "info",
    in_review: "primary",
    completed: "success",
    rejected: "danger",
  };
  return typeMap[status] || "info";
};

const getCaseReviewStatusText = (status) => {
  const statusMap = {
    pending: "待审核",
    approved: "已通过",
    rejected: "已拒绝",
  };
  return statusMap[status] || status;
};

const getCaseReviewStatusTagType = (status) => {
  const typeMap = {
    pending: "info",
    approved: "success",
    rejected: "danger",
  };
  return typeMap[status] || "info";
};

const getPriorityTagType = (priority) => {
  const typeMap = {
    P0: "danger",
    P1: "warning",
    P2: "info",
    P3: "success",
    P4: "success",
  };
  return typeMap[priority] || "info";
};

const progressColor = (percentage) => {
  if (percentage === 100) return "#67c23a";
  if (percentage >= 50) return "#409eff";
  return "#e6a23c";
};

// 生命周期
onMounted(() => {
  // 初始加载数据
  getMyTasks();
  getMyInitiated();
  // 获取可用用例集列表，用于评审历史查询
  getAvailableSuites();
});
</script>

<style lang="scss" scoped>
.case-review-management {
  padding: 20px;
}

/* 树节点样式优化 */
.tree-node-content {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.node-icon {
  margin-right: 4px;
}

.node-label {
  flex: 1;
}

.case-count {
  color: #909399;
  font-size: 12px;
  margin-left: 4px;
}

/* 禁用文件夹样式 */
.disabled-folder {
  color: #909399;
  cursor: not-allowed;
}

.disabled-folder .node-label {
  cursor: not-allowed;
}

.disabled-folder .node-icon {
  cursor: pointer;
}

.review-card {
  margin-bottom: 20px;
}

.review-tabs {
  .el-tabs__header {
    margin-bottom: 20px;
  }
}

.review-section {
  background: #fafafa;
  padding: 20px;
  border-radius: 8px;
}

.section-header {
  margin-bottom: 15px;

  h3 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
  }
}

.review-dialog-content {
  max-height: 60vh;
  overflow-y: auto;
}

.text-with-newlines {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.5;
}

.dialog-section {
  margin-bottom: 20px;

  h4 {
    margin: 0 0 15px 0;
    font-size: 14px;
    font-weight: 600;
  }
}

.edit-review-content {
  max-height: 60vh;
  overflow-y: auto;
}

.case-detail-section,
.review-edit-section {
  margin-bottom: 20px;

  h4 {
    margin: 0 0 15px 0;
    font-size: 14px;
    font-weight: 600;
  }
}

.case-content {
  white-space: pre-wrap;
  margin: 0;
  font-family: inherit;
}

.dialog-footer {
  text-align: right;
}

.read-only-comments {
  background-color: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 8px 12px;
  min-height: 60px;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.5;
  color: #303133;
}
</style>
