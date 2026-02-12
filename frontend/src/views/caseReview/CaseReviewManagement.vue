<template>
  <div class="case-review-management">
    <el-card class="review-card">
      <!-- 评审中心选项卡 -->
      <el-tabs
        v-model="activeTab"
        class="review-tabs"
      >
        <!-- 待我评审 -->
        <el-tab-pane
          label="待我评审"
          name="my-tasks"
        >
          <div class="review-section">
            <div class="section-header">
              <h3>待我评审的用例集</h3>
            </div>

            <div class="review-table-wrapper">
              <el-table
                v-loading="loading.myTasks"
                :data="myTasks"
                class="review-list-table"
                style="width: 100%; min-width: 1080px"
                row-key="id"
                header-align="center"
                align="center"
                @row-click="handleTaskClick"
              >
              <el-table-column
                prop="suite_name"
                label="用例集名称"
                min-width="200"
                header-align="center"
                align="center"
              >
                <template #default="scope">
                  <el-popover
                    placement="top-start"
                    trigger="hover"
                    :show-after="200"
                    width="280"
                    popper-class="suite-info-popover"
                  >
                    <template #reference>
                      <span
                        class="suite-name-trigger"
                        @click.stop="handleGoToSuite(scope.row)"
                      >{{ scope.row.suite_name || '-' }}</span>
                    </template>
                    <div class="suite-info-tags">
                      <div class="suite-info-tag">
                        <span class="tag-label">所属项目：</span>
                        <span class="tag-value">{{ scope.row.project_name || '-' }}</span>
                      </div>
                      <div class="suite-info-tag">
                        <span class="tag-label">所属迭代：</span>
                        <span class="tag-value">{{ scope.row.iteration_name || '-' }}</span>
                      </div>
                      <div class="suite-info-tag">
                        <span class="tag-label">关联需求：</span>
                        <span class="tag-value">{{ scope.row.requirement_name || '-' }}</span>
                      </div>
                    </div>
                  </el-popover>
                </template>
              </el-table-column>
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
          </div>
        </el-tab-pane>

        <!-- 我发起的评审 -->
        <el-tab-pane
          label="我发起的评审"
          name="my-initiated"
        >
          <div class="review-section">
            <div class="section-header">
              <h3>我发起的评审</h3>
            </div>

            <div class="review-table-wrapper">
            <el-table
              v-loading="loading.myInitiated"
              :data="myInitiated"
              class="review-list-table"
              style="width: 100%; min-width: 1080px"
              row-key="id"
              header-align="center"
              align="center"
              @row-click="handleTaskClick"
            >
              <el-table-column
                prop="suite_name"
                label="用例集名称"
                min-width="200"
                header-align="center"
                align="center"
              >
                <template #default="scope">
                  <el-popover
                    placement="top-start"
                    trigger="hover"
                    :show-after="200"
                    width="280"
                    popper-class="suite-info-popover"
                  >
                    <template #reference>
                      <span
                        class="suite-name-trigger"
                        @click.stop="handleGoToSuite(scope.row)"
                      >{{ scope.row.suite_name || '-' }}</span>
                    </template>
                    <div class="suite-info-tags">
                      <div class="suite-info-tag">
                        <span class="tag-label">所属项目：</span>
                        <span class="tag-value">{{ scope.row.project_name || '-' }}</span>
                      </div>
                      <div class="suite-info-tag">
                        <span class="tag-label">所属迭代：</span>
                        <span class="tag-value">{{ scope.row.iteration_name || '-' }}</span>
                      </div>
                      <div class="suite-info-tag">
                        <span class="tag-label">关联需求：</span>
                        <span class="tag-value">{{ scope.row.requirement_name || '-' }}</span>
                      </div>
                    </div>
                  </el-popover>
                </template>
              </el-table-column>
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
          </div>
        </el-tab-pane>

        <!-- 评审历史 -->
        <el-tab-pane
          label="评审历史"
          name="review-history"
        >
          <div class="review-section">
            <div class="section-header">
              <h3>用例集评审历史记录</h3>
            </div>

            <!-- 用例集选择器（与用例管理页样式统一） -->
            <div class="suite-selector">
              <el-form
                :inline="true"
                class="suite-form"
              >
                <el-form-item label="目标用例集">
                  <div class="case-suite-selector">
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
                          style="width: 100%; min-width: 280px"
                          clearable
                          @click="suitePopoverVisible = !suitePopoverVisible"
                          @clear="handleClearSuiteSelection"
                        />
                      </template>
                      <div
                        class="suite-tree-popover"
                        style="width: 100%; min-width: 300px; max-width: 400px"
                      >
                        <el-tree
                          :current-node-key="selectedSuiteId"
                          :data="suiteTreeData"
                          :props="defaultProps"
                          node-key="id"
                          style="max-height: 300px; overflow-y: auto; width: 100%; padding-right: 10px;"
                          :expand-on-click-node="true"
                          :filter-node-method="filterSuiteType"
                          @node-click="handleSuiteTreeNodeClick"
                        >
                          <template #default="{ node, data }">
                            <span
                              class="tree-node-content"
                              :class="{
                                'current-node': node.key === selectedSuiteId,
                                'folder-node': data.type === 'folder',
                              }"
                            >
                              <el-icon class="node-icon">
                                <Document v-if="data.type === 'suite'" />
                                <Folder v-else />
                              </el-icon>
                              <span class="node-label">{{ node.label }}</span>
                              <span
                                v-if="data.type === 'suite' && data.cases_count > 0"
                                class="case-count"
                              >({{ data.cases_count }})</span>
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
                prop="end_time"
                label="评审时间"
                min-width="160"
                header-align="center"
                align="center"
              >
                <template #default="scope">
                  {{ formatDate(scope.row.end_time || scope.row.created_at) }}
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
      :fullscreen="true"
      :before-close="handleDialogClose"
    >
      <div
        v-if="currentReviewTask"
        class="review-dialog-content"
      >
        <!-- 评审任务基本信息 -->
        <div class="dialog-section">
          <h4>评审任务信息</h4>
          <el-descriptions
            :column="2"
            border
          >
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
              :span="1"
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
            <el-descriptions-item label="更新时间">
              {{ formatDate(currentReviewTask?.updated_at) || "-" }}
            </el-descriptions-item>

          </el-descriptions>
        </div>

        <!-- 用例评审列表 -->
        <div class="dialog-section case-list-section">
          <h4>用例评审列表</h4>
          <p v-if="isReviewer && !currentReviewTask?.version" class="review-save-hint">
            评审状态与意见会即时保存，可随时关闭页面，下次继续评审。
          </p>
          <!-- 筛选条件栏 -->
          <div class="case-review-filter-bar">
            <div class="filter-bar-left">
              <el-input
                v-model="caseReviewKeyword"
                placeholder="关键字筛选（名称、步骤、意见等）"
                clearable
                style="width: 280px"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
              <el-select
                v-model="caseReviewPriorityFilter"
                placeholder="优先级"
                multiple
                collapse-tags
                collapse-tags-tooltip
                clearable
                style="width: 160px"
              >
                <el-option label="P0" value="P0" />
                <el-option label="P1" value="P1" />
                <el-option label="P2" value="P2" />
                <el-option label="P3" value="P3" />
                <el-option label="P4" value="P4" />
              </el-select>
              <el-select
                v-model="caseReviewStatusFilter"
                placeholder="评审状态"
                multiple
                collapse-tags
                collapse-tags-tooltip
                clearable
                style="width: 180px"
              >
                <el-option label="待审核" value="pending" />
                <el-option label="已通过" value="approved" />
                <el-option label="已拒绝" value="rejected" />
              </el-select>
            </div>
            <div class="filter-bar-right">
              <el-button size="default" @click="resetCaseReviewFilter">重置条件</el-button>
              <el-button
                v-if="isReviewer"
                type="success"
                size="default"
                @click="handleSetAllApproved"
              >
                全部通过
              </el-button>
              <el-button
                v-if="isReviewer"
                size="default"
                @click="handleResetAllStatus"
              >
                重置状态
              </el-button>
              <span class="filter-result-tip">共 {{ filteredCaseReviews.length }} 条</span>
            </div>
          </div>
          <el-table
            v-loading="loading.caseReviews"
            :data="filteredCaseReviews"
            class="review-case-table"
            style="width: 100%"
            row-key="id"
            :row-style="{ height: 'auto' }"
            :cell-style="{
              'white-space': 'pre-wrap',
              'word-break': 'break-word',
              'line-height': '1.5',
            }"
          >
            <el-table-column
              label="用例编号"
              width="7%"
              min-width="80"
            >
              <template #default="scope">
                {{
                  scope.row.case_number ||
                    scope.row.test_case?.case_number ||
                    "-"
                }}
              </template>
            </el-table-column>
            <el-table-column
              label="用例名称"
              width="10%"
              min-width="100"
            >
              <template #default="scope">
                {{
                  scope.row.case_name || scope.row.test_case?.case_name || "-"
                }}
              </template>
            </el-table-column>
            <el-table-column
              label="优先级"
              width="5%"
              min-width="70"
            >
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

            <el-table-column
              label="测试数据"
              width="9%"
              min-width="90"
            >
              <template #default="scope">
                <div class="text-with-newlines">
                  {{
                    scope.row.test_data || scope.row.test_case?.test_data || "-"
                  }}
                </div>
              </template>
            </el-table-column>
            <el-table-column
              label="前置条件"
              width="10%"
              min-width="90"
            >
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
            <el-table-column
              label="测试步骤"
              width="11%"
              min-width="90"
            >
              <template #default="scope">
                <div class="text-with-newlines">
                  {{ scope.row.steps || scope.row.test_case?.steps || "-" }}
                </div>
              </template>
            </el-table-column>
            <el-table-column
              label="预期结果"
              width="10%"
              min-width="90"
            >
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
            <el-table-column
              label="实际结果"
              width="10%"
              min-width="90"
            >
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
            <el-table-column
              prop="review_status"
              label="评审状态"
              width="9%"
              min-width="90"
            >
              <template #default="scope">
                <!-- 如果是评审人，显示可编辑的单选按钮组 -->
                <el-radio-group
                  v-if="isReviewer"
                  v-model="scope.row.review_status"
                  size="small"
                  class="case-review-status-group"
                  @change="handleReviewStatusChange(scope.row)"
                >
                  <el-radio-button label="pending" class="status-pending">待审核</el-radio-button>
                  <el-radio-button label="approved" class="status-approved">已通过</el-radio-button>
                  <el-radio-button label="rejected" class="status-rejected">已拒绝</el-radio-button>
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
            <el-table-column
              prop="comments"
              label="评审意见"
              width="12%"
              min-width="120"
            >
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
                  @blur="handleCommentsChange(scope.row)"
                />
                <!-- 如果是发起人或其他用户，显示只读的评审意见 -->
                <div
                  v-else
                  class="read-only-comments"
                >
                  {{ scope.row.comments || "-" }}
                </div>
              </template>
            </el-table-column>
            <el-table-column
              prop="updated_at"
              label="评审时间"
              width="7%"
              min-width="120"
              :formatter="formatDate"
            >
              <template #default="scope">
                {{ formatDate(scope.row.updated_at || scope.row.created_at) || "-" }}
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
          <div
            v-else
            class="read-only-comments"
          >
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
              <!-- 如果评审未完成且没有被拒绝的用例，显示完成评审按钮 -->
              <el-button
                v-if="
                  currentReviewTask &&
                    currentReviewTask.status !== 'completed' &&
                    currentReviewTask.status !== 'rejected' &&
                    !hasRejectedCases
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
              <!-- 如果是评审人且评审状态不是待处理，或者有被拒绝的用例，显示打回评审按钮 -->
              <el-button
                v-if="
                  currentReviewTask &&
                    (currentReviewTask.status !== 'pending' && currentReviewTask.status !== 'rejected') ||
                    hasRejectedCases
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
import { useRoute, useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import * as reviewApi from "@/api/reviewTask";
import * as testSuiteApi from "@/api/testSuite";
import { useUserStore } from "@/stores/user";
import { Folder, Document, Search } from "@element-plus/icons-vue";

// 状态管理
const userStore = useUserStore();
const route = useRoute();
const router = useRouter();
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

// 用例评审列表筛选条件（评审详情弹窗内）
const caseReviewKeyword = ref("");
const caseReviewPriorityFilter = ref([]);
const caseReviewStatusFilter = ref([]);
const caseReviewPriorityFilterAll = ref(true);
const caseReviewStatusFilterAll = ref(true);

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

// 检查是否有被拒绝的用例
const hasRejectedCases = computed(() => {
  return caseReviews.value.some((cr) => cr.review_status === "rejected");
});

// 用例评审列表筛选结果（关键字 + 优先级 + 评审状态）
const filteredCaseReviews = computed(() => {
  let list = caseReviews.value || [];
  const kw = (caseReviewKeyword.value || "").trim().toLowerCase();
  if (kw) {
    list = list.filter((row) => {
      const caseName = (row.case_name || row.test_case?.case_name || "").toLowerCase();
      const comments = (row.comments || "").toLowerCase();
      const steps = (row.steps || row.test_case?.steps || "").toLowerCase();
      const preconditions = (row.preconditions || row.test_case?.preconditions || "").toLowerCase();
      const expected = (row.expected_result || row.test_case?.expected_result || "").toLowerCase();
      const actual = (row.actual_result || row.test_case?.actual_result || "").toLowerCase();
      const testData = (row.test_data || row.test_case?.test_data || "").toLowerCase();
      return [caseName, comments, steps, preconditions, expected, actual, testData].some(
        (s) => s && s.includes(kw)
      );
    });
  }
  if (caseReviewPriorityFilter.value && caseReviewPriorityFilter.value.length > 0) {
    list = list.filter((row) => {
      const p = row.priority || row.test_case?.priority;
      return p && caseReviewPriorityFilter.value.includes(p);
    });
  }
  if (caseReviewStatusFilter.value && caseReviewStatusFilter.value.length > 0) {
    list = list.filter((row) =>
      row.review_status && caseReviewStatusFilter.value.includes(row.review_status)
    );
  }
  return list;
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

// 点击用例集名称：跳转到用例管理页并定位到对应用例集
const handleGoToSuite = (row) => {
  if (!row?.suite_id) return;
  router.push({ path: "/test-cases", query: { suite_id: row.suite_id } });
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

// 清空目标用例集选择（评审历史）
const handleClearSuiteSelection = () => {
  selectedSuiteId.value = null;
  selectedSuitePath.value = "";
  reviewHistory.value = [];
};

// 树节点点击：文件夹仅展开/收起，用例集则选中
const handleSuiteTreeNodeClick = (data) => {
  if (data.type === "suite") {
    handleSuiteSelect(data);
  }
  // 文件夹由 el-tree 的 expand-on-click-node 处理展开/收起，此处不处理
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

// 重置用例评审列表筛选条件
const resetCaseReviewFilter = () => {
  caseReviewKeyword.value = "";
  caseReviewPriorityFilter.value = [];
  caseReviewStatusFilter.value = [];
  caseReviewPriorityFilterAll.value = true;
  caseReviewStatusFilterAll.value = true;
};

const handleCaseReviewPriorityAllChange = (val) => {
  caseReviewPriorityFilter.value = val ? ["P0", "P1", "P2", "P3", "P4"] : [];
};

const handleCaseReviewPriorityFilterChange = () => {
  caseReviewPriorityFilterAll.value =
    caseReviewPriorityFilter.value.length === 5;
};

const handleCaseReviewPriorityReset = () => {
  caseReviewPriorityFilter.value = [];
  caseReviewPriorityFilterAll.value = true;
};

const handleCaseReviewStatusAllChange = (val) => {
  caseReviewStatusFilter.value = val ? ["pending", "approved", "rejected"] : [];
};

const handleCaseReviewStatusFilterChange = () => {
  caseReviewStatusFilterAll.value =
    caseReviewStatusFilter.value.length === 3;
};

const handleCaseReviewStatusReset = () => {
  caseReviewStatusFilter.value = [];
  caseReviewStatusFilterAll.value = true;
};

// 全部通过：将所有用例评审状态设为已通过
const handleSetAllApproved = async () => {
  if (!currentReviewTask.value || !caseReviews.value.length) return;
  await ElMessageBox.confirm("确定将所有用例设置为已通过？", "提示", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  });
  loading.value.updateReview = true;
  try {
    for (const row of caseReviews.value) {
      await reviewApi.updateCaseReview(row.review_task_id, row.case_id, {
        review_status: "approved",
        comments: row.comments || "",
      });
      row.review_status = "approved";
    }
    ElMessage.success("已全部设置为通过");
    if (activeTab.value === "my-tasks") getMyTasks();
    else getMyInitiated();
  } catch (e) {
    ElMessage.error("操作失败");
  } finally {
    loading.value.updateReview = false;
  }
};

// 重置状态：将所有用例评审状态设为待审核
const handleResetAllStatus = async () => {
  if (!currentReviewTask.value || !caseReviews.value.length) return;
  await ElMessageBox.confirm("确定将所有用例重置为待审核？", "提示", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  });
  loading.value.updateReview = true;
  try {
    for (const row of caseReviews.value) {
      await reviewApi.updateCaseReview(row.review_task_id, row.case_id, {
        review_status: "pending",
        comments: row.comments || "",
      });
      row.review_status = "pending";
    }
    ElMessage.success("已全部重置为待审核");
    if (activeTab.value === "my-tasks") getMyTasks();
    else getMyInitiated();
  } catch (e) {
    ElMessage.error("操作失败");
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
  resetCaseReviewFilter();
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
onMounted(async () => {
  // 初始加载数据
  await getMyTasks();
  await getMyInitiated();
  // 获取可用用例集列表，用于评审历史查询
  await getAvailableSuites();
  
  // 处理从用例集页面跳转过来的情况
  const suiteId = route.query.suiteId;
  if (suiteId) {
    try {
      // 查找对应套件的最新评审任务
      const tasks = myInitiated.value;
      const suiteTask = tasks.find(task => task.suite_id === parseInt(suiteId));
      if (suiteTask) {
        // 显示评审详情
        await getReviewTaskDetail(suiteTask.id);
        reviewDialogTitle.value = "评审详情";
        reviewDialogVisible.value = true;
      } else {
        console.log('未找到对应套件的评审任务:', suiteId);
      }
      
      // 移除URL中的suiteId参数，避免刷新页面时再次触发
      router.replace({
        query: {
          activeTab: route.query.activeTab || "my-initiated"
        }
      });
    } catch (error) {
      console.error('处理套件ID跳转失败:', error);
      ElMessage.error('处理跳转失败，请手动查找评审任务');
      
      // 即使出错也移除URL中的suiteId参数
      router.replace({
        query: {
          activeTab: route.query.activeTab || "my-initiated"
        }
      });
    }
  }
});
</script>

<style lang="scss" scoped>
.case-review-management {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.review-card {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.review-card :deep(.el-card__body) {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 20px;
}

.review-tabs {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.review-tabs :deep(.el-tabs__content) {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.review-tabs :deep(.el-tabs__panel) {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.review-tabs :deep(.el-tab-pane) {
  height: 100%;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
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

/* 文件夹节点：可点击展开/收起 */
.folder-node {
  color: #909399;
  cursor: pointer;
}

.folder-node .node-label,
.folder-node .node-icon {
  cursor: pointer;
}

.review-tabs :deep(.el-tabs__header) {
  margin-bottom: 20px;
  flex-shrink: 0;
}

.review-section {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: #fafafa;
  padding: 20px;
  border-radius: 8px;
  overflow: hidden;
}

/* 表格外层滚动容器：解决 flex 布局下横向滚动无法滚到头的问题 */
.review-table-wrapper {
  flex: 1;
  min-height: 0;
  overflow: auto;
}

.review-list-table {
  /* 表格不参与 flex 收缩，由 wrapper 负责横向滚动 */
  flex: none;
}

/* 用例集名称列：悬浮触发样式 */
.suite-name-trigger {
  cursor: pointer;
  color: #409eff;
  text-decoration: none;
  border-bottom: 1px dashed #409eff;
}
.suite-name-trigger:hover {
  color: #66b1ff;
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
  max-height: calc(100vh - 120px);
  overflow-y: auto;
  overflow-x: hidden;
}

/* 用例评审列表：百分比列宽铺满容器，不出现横向滚动 */
.review-case-table {
  table-layout: fixed;
}
.review-case-table :deep(.el-table__body),
.review-case-table :deep(.el-table__header) {
  width: 100% !important;
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

/* 用例评审列表区域：右侧留出间距，避免与垂直滚动条贴紧 */
.case-list-section {
  padding-right: 20px;
}

.review-save-hint {
  margin: -4px 0 10px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

/* 用例评审列表筛选栏 */
.case-review-filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  row-gap: 14px;
  column-gap: 16px;
  margin-bottom: 14px;
  padding: 10px 0 4px;
}
.filter-bar-left {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 14px;
}
.filter-bar-right {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-left: auto;
}
.filter-bar-right .el-button {
  margin: 0;
  min-width: 72px;
}
.filter-bar-right .filter-result-tip {
  margin-left: 4px;
  padding-left: 12px;
  border-left: 1px solid #e4e7ed;
}
.filter-result-tip {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
}

/* 用例评审状态单选按钮：与页面 el-tag size="small" 风格统一 */
.review-case-table :deep(.case-review-status-group) {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 6px;
  border: none;
  box-shadow: none;
  outline: none;
}
.review-case-table :deep(.case-review-status-group .el-radio-button) {
  margin-right: 0;
}
.review-case-table :deep(.case-review-status-group .el-radio-button__original) {
  outline: none;
}
.review-case-table :deep(.case-review-status-group .el-radio-button__inner) {
  padding: 4px 10px;
  font-size: 12px;
  border-radius: 4px;
  border: 1px solid #e9e9eb;
  border-left: 1px solid #e9e9eb;
  box-shadow: none !important;
  transition: all 0.2s;
  outline: none;
}
.review-case-table :deep(.case-review-status-group .el-radio-button__inner::before) {
  display: none;
}
.review-case-table :deep(.case-review-status-group .el-radio-button:focus-visible .el-radio-button__inner),
.review-case-table :deep(.case-review-status-group .el-radio-button__original-radio:focus-visible + .el-radio-button__inner) {
  box-shadow: none !important;
  outline: none;
  border-left-color: #e9e9eb;
}
/* 未选中：统一中性样式，不区分颜色 */
.review-case-table :deep(.case-review-status-group .el-radio-button__inner) {
  background-color: #f4f4f5;
  border-color: #e9e9eb;
  color: #606266;
}
.review-case-table :deep(.case-review-status-group .el-radio-button:not(.is-active):hover .el-radio-button__inner) {
  background-color: #e9e9eb;
  color: #303133;
}
/* 选中后按状态区分颜色（覆盖 Element 默认的左侧蓝色 box-shadow） */
.review-case-table :deep(.status-pending.is-active .el-radio-button__inner) {
  background-color: #909399;
  border-color: #909399;
  border-left-color: #909399;
  box-shadow: none !important;
  color: #fff;
}
.review-case-table :deep(.status-approved.is-active .el-radio-button__inner) {
  background-color: #67c23a;
  border-color: #67c23a;
  border-left-color: #67c23a;
  box-shadow: none !important;
  color: #fff;
}
.review-case-table :deep(.status-rejected.is-active .el-radio-button__inner) {
  background-color: #f56c6c;
  border-color: #f56c6c;
  border-left-color: #f56c6c;
  box-shadow: none !important;
  color: #fff;
}
.header-filter-trigger {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  cursor: pointer;
}
.header-filter-trigger .el-icon {
  color: #409eff;
}
.filter-panel {
  padding: 4px 0;
}
.filter-panel .el-checkbox-group {
  display: flex;
  flex-direction: column;
  margin-top: 6px;
}
.filter-panel .el-checkbox {
  display: block;
  margin: 4px 0;
}
.filter-panel-footer {
  margin-top: 8px;
  padding-top: 6px;
  border-top: 1px solid #e4e7ed;
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

<style lang="scss">
/* 用例集信息悬浮层（挂载到 body，故不使用 scoped） */
.suite-info-popover {
  .suite-info-tags {
    padding: 4px 0;
  }
  .suite-info-tag {
    display: flex;
    align-items: flex-start;
    margin-bottom: 10px;
    font-size: 13px;
    line-height: 1.5;
    &:last-child {
      margin-bottom: 0;
    }
  }
  .tag-label {
    flex-shrink: 0;
    color: #909399;
    margin-right: 8px;
  }
  .tag-value {
    color: #303133;
    word-break: break-all;
  }
}
</style>
