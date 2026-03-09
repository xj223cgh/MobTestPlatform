<template>
  <div class="case-review-management">
    <el-card class="review-card">
      <!-- 评审中心选项卡 -->
      <el-tabs
        v-model="activeTab"
        class="review-tabs"
      >
        <el-tab-pane
          label="待我评审"
          name="my-tasks"
        >
          <div class="review-section">
            <div class="section-header">
              <h3>待我评审的用例集</h3>
            </div>
            <div class="list-filter-bar">
              <el-input
                v-model="filterSuiteNameMyTasks"
                placeholder="用例集名称"
                clearable
                style="width: 180px"
                @clear="getMyTasks"
                @keyup.enter="getMyTasks"
              />
              <el-select
                v-model="filterStatusMyTasks"
                placeholder="评审状态"
                clearable
                style="width: 140px"
                @change="getMyTasks"
              >
                <el-option label="待处理" value="pending" />
                <el-option label="评审中" value="in_review" />
                <el-option label="已完成" value="completed" />
                <el-option label="已拒绝" value="rejected" />
              </el-select>
              <el-date-picker
                v-model="filterDateRangeMyTasks"
                type="daterange"
                range-separator="至"
                start-placeholder="创建开始"
                end-placeholder="创建结束"
                value-format="YYYY-MM-DD"
                style="width: 240px"
                @change="getMyTasks"
              />
              <el-button type="primary" @click="getMyTasks">查询</el-button>
              <el-button @click="resetFilterMyTasks">重置</el-button>
            </div>
            <div class="review-table-wrapper">
              <el-table
                v-loading="loading.myTasks"
                :data="myTasks"
                class="review-list-table"
                style="width: 100%; min-width: 1080px"
                row-key="id"
                :row-class-name="getReviewRowClassName"
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
            <el-pagination
              v-if="paginationMyTasks.total > 0"
              class="review-list-pagination"
              :current-page="paginationMyTasks.page"
              :page-size="paginationMyTasks.size"
              :page-sizes="[10, 20, 50, 100]"
              :total="paginationMyTasks.total"
              layout="total, sizes, prev, pager, next"
              @current-change="onMyTasksPageChange"
              @size-change="onMyTasksSizeChange"
            />
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
            <div class="list-filter-bar">
              <el-input
                v-model="filterSuiteNameMyInitiated"
                placeholder="用例集名称"
                clearable
                style="width: 180px"
                @clear="getMyInitiated"
                @keyup.enter="getMyInitiated"
              />
              <el-select
                v-model="filterStatusMyInitiated"
                placeholder="评审状态"
                clearable
                style="width: 140px"
                @change="getMyInitiated"
              >
                <el-option label="待处理" value="pending" />
                <el-option label="评审中" value="in_review" />
                <el-option label="已完成" value="completed" />
                <el-option label="已拒绝" value="rejected" />
              </el-select>
              <el-date-picker
                v-model="filterDateRangeMyInitiated"
                type="daterange"
                range-separator="至"
                start-placeholder="创建开始"
                end-placeholder="创建结束"
                value-format="YYYY-MM-DD"
                style="width: 240px"
                @change="getMyInitiated"
              />
              <el-button type="primary" @click="getMyInitiated">查询</el-button>
              <el-button @click="resetFilterMyInitiated">重置</el-button>
            </div>
            <div class="review-table-wrapper">
            <el-table
              v-loading="loading.myInitiated"
              :data="myInitiated"
              class="review-list-table"
              style="width: 100%; min-width: 1080px"
              row-key="id"
              :row-class-name="getReviewRowClassName"
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
            <el-pagination
              v-if="paginationMyInitiated.total > 0"
              class="review-list-pagination"
              :current-page="paginationMyInitiated.page"
              :page-size="paginationMyInitiated.size"
              :page-sizes="[10, 20, 50, 100]"
              :total="paginationMyInitiated.total"
              layout="total, sizes, prev, pager, next"
              @current-change="onMyInitiatedPageChange"
              @size-change="onMyInitiatedSizeChange"
            />
          </div>
        </el-tab-pane>

        <el-tab-pane
          label="评审历史"
          name="review-history"
        >
          <div class="review-section">
            <el-tabs v-model="reviewHistorySubTab" type="card" class="review-history-sub-tabs">
              <el-tab-pane label="全部最近历史" name="recent">
                <div class="section-header">
                  <h3>全部最近历史</h3>
                  <p class="section-tip">按时间倒序显示您作为发起人或评审人的评审记录，点击「查看详情」可查看该次历史。</p>
                </div>
                <el-table
                  v-loading="loading.recentHistory"
                  :data="paginatedRecentHistory"
                  style="width: 100%"
                  row-key="id"
                  max-height="400"
                >
                  <el-table-column prop="end_time" label="评审时间" min-width="160">
                    <template #default="scope">
                      {{ formatDate(scope.row.end_time || scope.row.created_at) }}
                    </template>
                  </el-table-column>
                  <el-table-column prop="suite_name" label="用例集" min-width="160" show-overflow-tooltip />
                  <el-table-column prop="initiator_name" label="发起人" min-width="100" />
                  <el-table-column prop="reviewer_name" label="评审人" min-width="100" />
                  <el-table-column label="类型" min-width="90">
                    <template #default="scope">
                      <el-tag :type="scope.row.history_type === 'reject' ? 'danger' : 'success'" size="small">
                        {{ scope.row.history_type === 'reject' ? '打回' : '完成' }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="case_stats.total" label="总用例数" width="90" align="center" />
                  <el-table-column prop="case_stats.approved" label="通过" width="70" align="center" />
                  <el-table-column prop="case_stats.rejected" label="拒绝" width="70" align="center" />
                  <el-table-column label="操作" width="100" align="center" fixed="right">
                    <template #default="scope">
                      <el-button type="primary" link size="small" @click="handleViewReviewHistory(scope.row)">查看详情</el-button>
                    </template>
                  </el-table-column>
                </el-table>
                <el-pagination
                  v-if="paginationRecent.total > 0"
                  class="review-list-pagination"
                  :current-page="paginationRecent.page"
                  :page-size="paginationRecent.size"
                  :page-sizes="[10, 20, 50, 100]"
                  :total="paginationRecent.total"
                  layout="total, sizes, prev, pager, next"
                  @current-change="(p) => { paginationRecent.page = p; }"
                  @size-change="(s) => { paginationRecent.size = s; paginationRecent.page = 1; }"
                />
              </el-tab-pane>
              <el-tab-pane label="按用例集查看历史" name="by-suite">
                <div class="by-suite-layout">
                  <div class="section-header">
                    <h3>按用例集查看历史</h3>
                    <p class="section-tip">选择目标用例集后，可查看该用例集的全部评审历史记录。</p>
                  </div>
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
                  <div class="review-table-wrapper">
                <el-table
                  v-loading="loading.reviewHistory"
                  :data="paginatedReviewHistory"
                  class="review-list-table"
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
                <el-pagination
                  v-if="paginationBySuite.total > 0"
                  class="review-list-pagination"
                  :current-page="paginationBySuite.page"
                  :page-size="paginationBySuite.size"
                  :page-sizes="[10, 20, 50, 100]"
                  :total="paginationBySuite.total"
                  layout="total, sizes, prev, pager, next"
                  @current-change="(p) => { paginationBySuite.page = p; }"
                  @size-change="(s) => { paginationBySuite.size = s; paginationBySuite.page = 1; }"
                />
                </div>
              </el-tab-pane>
            </el-tabs>
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

        <div class="dialog-section case-list-section">
          <h4>用例评审列表</h4>
          <p v-if="isReviewer && !currentReviewTask?.version" class="review-save-hint">
            评审状态与意见会即时保存，可随时关闭页面，下次继续评审。
          </p>
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
                v-if="isReviewerAndCanEdit"
                type="success"
                size="default"
                @click="handleSetAllApproved"
              >
                全部通过
              </el-button>
              <el-button
                v-if="isReviewerAndCanEdit"
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
            :data="paginatedFilteredCaseReviews"
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
                <el-radio-group
                  v-if="isReviewerAndCanEdit"
                  v-model="scope.row.review_status"
                  size="small"
                  class="case-review-status-group"
                  @change="handleReviewStatusChange(scope.row)"
                >
                  <el-radio-button label="pending" class="status-pending">待审核</el-radio-button>
                  <el-radio-button label="approved" class="status-approved">已通过</el-radio-button>
                  <el-radio-button label="rejected" class="status-rejected">已拒绝</el-radio-button>
                </el-radio-group>
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
                <el-input
                  v-if="isReviewerAndCanEdit"
                  v-model="scope.row.comments"
                  type="textarea"
                  :rows="2"
                  placeholder="请输入评审意见"
                  resize="none"
                  size="small"
                  @blur="handleCommentsChange(scope.row)"
                />
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
          <el-pagination
            v-if="filteredCaseReviews.length > 0"
            class="review-list-pagination"
            :current-page="paginationCaseReview.page"
            :page-size="paginationCaseReview.size"
            :page-sizes="[10, 20, 50, 100]"
            :total="filteredCaseReviews.length"
            layout="total, sizes, prev, pager, next"
            @current-change="(p) => { paginationCaseReview.page = p; }"
            @size-change="(s) => { paginationCaseReview.size = s; paginationCaseReview.page = 1; }"
          />
        </div>

        <div
          v-if="isReviewer || isInitiator || currentReviewTask?.version"
          class="dialog-section"
        >
          <h4>整体评审意见</h4>
          <el-input
            v-if="isReviewerAndCanEdit"
            v-model="overallComments"
            type="textarea"
            :rows="4"
            placeholder="请输入整体评审意见"
          />
          <div
            v-else
            class="read-only-comments"
          >
            {{ overallComments || "暂无整体评审意见" }}
          </div>
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="reviewDialogVisible = false">关闭</el-button>

          <template v-if="!currentReviewTask?.version">
            <template v-if="isReviewer">
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
              <el-button
                v-else-if="
                  currentReviewTask &&
                  (currentReviewTask.status === 'completed' || currentReviewTask.status === 'rejected')
                "
                type="warning"
                @click="handleRestartReview"
              >
                重新评审
              </el-button>
              <el-button
                v-if="
                  currentReviewTask &&
                  currentReviewTask.status !== 'rejected' &&
                  ((currentReviewTask.status !== 'pending') || hasRejectedCases)
                "
                type="danger"
                @click="handleRejectReview"
              >
                打回评审
              </el-button>
            </template>

            <el-button
              v-if="
                isInitiator &&
                  currentReviewTask &&
                  (currentReviewTask.status === 'rejected' || currentReviewTask.status === 'completed')
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
import { ref, onMounted, computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import * as reviewApi from "@/api/reviewTask";
import * as testSuiteApi from "@/api/testSuite";
import { isPermissionError } from "@/utils/request";
import { useUserStore } from "@/stores/user";
import { useSystemSettingsStore } from "@/stores/systemSettings";
import { Folder, Document, Search } from "@element-plus/icons-vue";

const userStore = useUserStore();
const systemSettingsStore = useSystemSettingsStore();
const defaultPageSize = computed(() => systemSettingsStore.defaultPageSize || 10);
const route = useRoute();
const router = useRouter();
const activeTab = ref(route.query.activeTab || "my-tasks");
const reviewHistorySubTab = ref("recent");
// 消息跳转时的短暂闪烁行（2.5s 后清除）
const flashTaskId = ref(null);
let flashClearTimer = null;
// 从消息带 taskId 进入时是否已自动打开过详情弹窗（避免重复打开）
const hasOpenedDialogForFlashTask = ref(false);
/** 从用例管理点击「评审」带 suiteId 跳转时，对应任务行的 id，用于蓝色选中样式 */
const highlightedSuiteTaskId = ref(null);
const getReviewRowClassName = ({ row }) => {
  if (flashTaskId.value && row.id === flashTaskId.value) return "notification-flash-row";
  if (highlightedSuiteTaskId.value && row.id === highlightedSuiteTaskId.value) return "review-row-selected";
  return "";
};
const loading = ref({
  myTasks: false,
  myInitiated: false,
  caseReviews: false,
  updateReview: false,
  reviewHistory: false,
  recentHistory: false,
  suites: false,
});

const myTasks = ref([]);
const myInitiated = ref([]);
const paginationMyTasks = ref({ page: 1, size: 10, total: 0 });
const paginationMyInitiated = ref({ page: 1, size: 10, total: 0 });
const filterSuiteNameMyTasks = ref("");
const filterStatusMyTasks = ref("");
const filterDateRangeMyTasks = ref(null);
const filterSuiteNameMyInitiated = ref("");
const filterStatusMyInitiated = ref("");
const filterDateRangeMyInitiated = ref(null);
const caseReviews = ref([]);
const originalCaseReviews = ref([]);
const currentReviewTask = ref(null);
const reviewDialogVisible = ref(false);
const reviewDialogTitle = ref("");
const overallComments = ref("");

const selectedSuiteId = ref(null);
const selectedSuitePath = ref("");
const suitePopoverVisible = ref(false);
const suiteTreeData = ref([]);
const defaultProps = ref({
  label: "suite_name",
  children: "children",
});
const reviewHistory = ref([]);
const recentHistory = ref([]);
const paginationRecent = ref({ page: 1, size: 10, total: 0 });
const paginationBySuite = ref({ page: 1, size: 10, total: 0 });
const paginationCaseReview = ref({ page: 1, size: 10 });

const caseReviewKeyword = ref("");
const caseReviewPriorityFilter = ref([]);
const caseReviewStatusFilter = ref([]);
const caseReviewPriorityFilterAll = ref(true);
const caseReviewStatusFilterAll = ref(true);

const isReviewer = computed(() => {
  if (currentReviewTask.value?.version) return false;
  if (!userStore.userInfo || !currentReviewTask.value) return false;
  const currentUserId = String(userStore.userInfo.id);
  const reviewerId = String(currentReviewTask.value.reviewer_id);
  return currentUserId === reviewerId;
});

const isReviewerAndCanEdit = computed(() => {
  if (!isReviewer.value) return false;
  if (currentReviewTask.value?.status === "rejected") return false;
  return true;
});

const isInitiator = computed(() => {
  if (!userStore.userInfo || !currentReviewTask.value) return false;
  const currentUserId = String(userStore.userInfo.id);
  const initiatorId = String(currentReviewTask.value.initiator_id);
  return currentUserId === initiatorId;
});

const canCompleteReview = computed(() => {
  if (currentReviewTask.value?.version) {
    return false;
  }

  if (currentReviewTask.value?.status === "rejected") {
    return false;
  }

  if (!caseReviews.value.length) return true;
  return caseReviews.value.every((cr) => cr.review_status !== "pending");
});

const hasRejectedCases = computed(() => {
  return caseReviews.value.some((cr) => cr.review_status === "rejected");
});

const paginatedRecentHistory = computed(() => {
  const list = recentHistory.value || [];
  const { page, size } = paginationRecent.value;
  const start = (page - 1) * size;
  return list.slice(start, start + size);
});
const paginatedReviewHistory = computed(() => {
  const list = reviewHistory.value || [];
  const { page, size } = paginationBySuite.value;
  const start = (page - 1) * size;
  return list.slice(start, start + size);
});
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
const paginatedFilteredCaseReviews = computed(() => {
  const list = filteredCaseReviews.value || [];
  const { page, size } = paginationCaseReview.value;
  const start = (page - 1) * size;
  return list.slice(start, start + size);
});

const getMyTasks = async () => {
  loading.value.myTasks = true;
  try {
    const params = {
      page: paginationMyTasks.value.page,
      size: paginationMyTasks.value.size,
    };
    if (filterStatusMyTasks.value) params.status = filterStatusMyTasks.value;
    if (filterSuiteNameMyTasks.value?.trim()) params.suite_name = filterSuiteNameMyTasks.value.trim();
    if (filterDateRangeMyTasks.value?.length === 2) {
      params.created_after = filterDateRangeMyTasks.value[0];
      params.created_before = filterDateRangeMyTasks.value[1];
    }
    const response = await reviewApi.getMyReviewTasks(params);
    myTasks.value = response.data.items || [];
    paginationMyTasks.value.total = response.data.total ?? 0;
  } catch (error) {
    if (isPermissionError(error)) return;
    ElMessage.error("获取我的评审任务失败");
  } finally {
    loading.value.myTasks = false;
  }
};

const getMyInitiated = async () => {
  loading.value.myInitiated = true;
  try {
    const params = {
      page: paginationMyInitiated.value.page,
      size: paginationMyInitiated.value.size,
    };
    if (filterStatusMyInitiated.value) params.status = filterStatusMyInitiated.value;
    if (filterSuiteNameMyInitiated.value?.trim()) params.suite_name = filterSuiteNameMyInitiated.value.trim();
    if (filterDateRangeMyInitiated.value?.length === 2) {
      params.created_after = filterDateRangeMyInitiated.value[0];
      params.created_before = filterDateRangeMyInitiated.value[1];
    }
    const response = await reviewApi.getMyInitiatedReviews(params);
    myInitiated.value = response.data.items || [];
    paginationMyInitiated.value.total = response.data.total ?? 0;
  } catch (error) {
    if (isPermissionError(error)) return;
    ElMessage.error("获取我发起的评审失败");
  } finally {
    loading.value.myInitiated = false;
  }
};

const resetFilterMyTasks = () => {
  filterSuiteNameMyTasks.value = "";
  filterStatusMyTasks.value = "";
  filterDateRangeMyTasks.value = null;
  paginationMyTasks.value.page = 1;
  getMyTasks();
};

const resetFilterMyInitiated = () => {
  filterSuiteNameMyInitiated.value = "";
  filterStatusMyInitiated.value = "";
  filterDateRangeMyInitiated.value = null;
  paginationMyInitiated.value.page = 1;
  getMyInitiated();
};

const onMyTasksPageChange = (page) => {
  paginationMyTasks.value.page = page;
  getMyTasks();
};
const onMyTasksSizeChange = (size) => {
  paginationMyTasks.value.size = size;
  paginationMyTasks.value.page = 1;
  getMyTasks();
};
const onMyInitiatedPageChange = (page) => {
  paginationMyInitiated.value.page = page;
  getMyInitiated();
};
const onMyInitiatedSizeChange = (size) => {
  paginationMyInitiated.value.size = size;
  paginationMyInitiated.value.page = 1;
  getMyInitiated();
};

const getReviewTaskDetail = async (taskId) => {
  loading.value.caseReviews = true;
  paginationCaseReview.value.page = 1;
  paginationCaseReview.value.size = defaultPageSize.value;
  try {
    const response = await reviewApi.getReviewTask(taskId);
    currentReviewTask.value = response.data;

    const caseResponse = await reviewApi.getCaseReviews(taskId);
    caseReviews.value = caseResponse.data.case_reviews || [];

    originalCaseReviews.value = JSON.parse(JSON.stringify(caseReviews.value));

    overallComments.value = response.data.overall_comments || "";
  } catch (error) {
    if (isPermissionError(error)) {
      if (route.query.taskId) {
        flashTaskId.value = null;
        hasOpenedDialogForFlashTask.value = false;
        reviewDialogVisible.value = false;
        const q = { ...route.query };
        delete q.taskId;
        router.replace({ path: route.path, query: Object.keys(q).length ? q : undefined });
      }
      return;
    }
    const status = error.response?.status;
    if (status === 404) {
      ElMessage.warning("该评审任务可能已被删除或您无权限查看");
      if (route.query.taskId) {
        flashTaskId.value = null;
        hasOpenedDialogForFlashTask.value = false;
        reviewDialogVisible.value = false;
        const q = { ...route.query };
        delete q.taskId;
        router.replace({ path: route.path, query: Object.keys(q).length ? q : undefined });
      }
    } else {
      ElMessage.error("获取评审任务详情失败");
    }
  } finally {
    loading.value.caseReviews = false;
  }
};

const handleTaskClick = (row) => {
  reviewDialogTitle.value = "评审详情";
  reviewDialogVisible.value = true;
  getReviewTaskDetail(row.id);
};

// 点击用例集名称：跳转到用例管理页并定位到对应用例集（带 fromReview 便于用例管理页刷新评审状态）
const handleGoToSuite = (row) => {
  if (!row?.suite_id) return;
  router.push({ path: "/test-cases", query: { suite_id: row.suite_id, fromReview: "1" } });
};

const handleReview = async (row) => {
  reviewDialogTitle.value = "开始评审";
  reviewDialogVisible.value = true;
  await getReviewTaskDetail(row.id);

  if (currentReviewTask.value && currentReviewTask.value.status === "pending") {
    try {
      if (caseReviews.value.length > 0) {
        const firstCase = caseReviews.value[0];
        await reviewApi.updateCaseReview(
          firstCase.review_task_id,
          firstCase.case_id,
          {
            review_status: firstCase.review_status,
            comments: firstCase.comments || "",
          },
        );
        await getReviewTaskDetail(row.id);
      }
    } catch (error) {
      if (isPermissionError(error)) return;
      console.error("更新评审状态失败:", error);
      ElMessage.error("更新评审状态失败");
    }
  }
};

const handleViewDetail = (row) => {
  reviewDialogTitle.value = "评审详情";
  reviewDialogVisible.value = true;
  getReviewTaskDetail(row.id);
};

const getAvailableSuites = async () => {
  loading.value.suites = true;
  try {
    const response = await testSuiteApi.getTestSuiteTree();
    suiteTreeData.value = response.data || [];
  } catch (error) {
    if (isPermissionError(error)) return;
    ElMessage.error("获取用例集列表失败");
    console.error("获取用例集列表失败:", error);
  } finally {
    loading.value.suites = false;
  }
};

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

const handleSuiteSelect = (data) => {
  if (data.type === "suite") {
    selectedSuiteId.value = data.id;
    selectedSuitePath.value = buildSuitePath(data);
    suitePopoverVisible.value = false;
    handleGetReviewHistory();
  }
};

const filterSuiteType = (value, data) => {
  return true;
};

const buildSuitePath = (data) => {
  return data.suite_name;
};

const getRecentReviewHistory = async () => {
  loading.value.recentHistory = true;
  try {
    const response = await reviewApi.getRecentReviewHistory({ limit: 500 });
    recentHistory.value = response.data.items || [];
    paginationRecent.value.total = recentHistory.value.length;
    paginationRecent.value.page = 1;
  } catch (error) {
    if (isPermissionError(error)) return;
    ElMessage.error("获取最近评审历史失败");
  } finally {
    loading.value.recentHistory = false;
  }
};

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
    paginationBySuite.value.total = reviewHistory.value.length;
    paginationBySuite.value.page = 1;
  } catch (error) {
    if (isPermissionError(error)) return;
    ElMessage.error("获取评审历史记录失败");
    console.error("获取评审历史记录失败:", error);
  } finally {
    loading.value.reviewHistory = false;
  }
};

const handleViewReviewHistory = async (row) => {
  reviewDialogTitle.value = "评审历史详情";
  reviewDialogVisible.value = true;
  loading.value.caseReviews = true;
  try {
    const response = await reviewApi.getReviewHistoryDetail(row.id);

    currentReviewTask.value = {
      ...response.data,
      suite_name: response.data.suite?.suite_name || "",
      initiator_name: response.data.initiator_name || "",
      reviewer_name: response.data.reviewer_name || "",
      created_at: response.data.created_at,
      status: response.data.status,
    };

    caseReviews.value = response.data.case_reviews || [];

    originalCaseReviews.value = JSON.parse(JSON.stringify(caseReviews.value));

    overallComments.value = response.data.overall_comments || "";
  } catch (error) {
    if (isPermissionError(error)) return;
    ElMessage.error("获取评审历史详情失败");
  } finally {
    loading.value.caseReviews = false;
  }
};

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

    const index = caseReviews.value.findIndex((cr) => cr.id === row.id);
    if (index > -1) {
      caseReviews.value[index] = {
        ...response.data,
        test_case: caseReviews.value[index].test_case,
      };
    }

    ElMessage.success("评审状态更新成功");

    if (activeTab.value === "my-tasks") {
      getMyTasks();
    } else {
      getMyInitiated();
    }
  } catch (error) {
    if (isPermissionError(error)) return;
    ElMessage.error("更新评审状态失败");
  } finally {
    loading.value.updateReview = false;
  }
};

const handleCommentsChange = async (row) => {
  loading.value.updateReview = true;
  try {
    const status = row.review_status || "pending";
    const response = await reviewApi.updateCaseReview(
      row.review_task_id,
      row.case_id,
      {
        review_status: status,
        comments: row.comments || "",
      },
    );

    const index = caseReviews.value.findIndex((cr) => cr.id === row.id);
    if (index > -1) {
      caseReviews.value[index] = {
        ...response.data,
        test_case: caseReviews.value[index].test_case,
      };
    }

    ElMessage.success("评审意见更新成功");
  } catch (error) {
    if (isPermissionError(error)) return;
    console.error("更新评审意见失败:", error);
    ElMessage.error(
      "更新评审意见失败: " + (error.response?.data?.message || error.message),
    );
  } finally {
    loading.value.updateReview = false;
  }
};

const handleCompleteReview = async () => {
  if (!currentReviewTask.value) return;

  await ElMessageBox.confirm("确定要完成评审并通知发起人吗？", "提示", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  });

  loading.value.updateReview = true;
  try {
    const modifiedCaseReviews = [];

    for (const currentReview of caseReviews.value) {
      const originalReview = originalCaseReviews.value.find(
        (orig) => orig.id === currentReview.id,
      );

      if (originalReview) {
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

    await reviewApi.completeReview(currentReviewTask.value.id, {
      overall_comments: overallComments.value,
    });

    ElMessage.success("评审完成成功");
    reviewDialogVisible.value = false;

    if (activeTab.value === "my-tasks") {
      getMyTasks();
    } else {
      getMyInitiated();
    }
  } catch (error) {
    if (isPermissionError(error)) return;
    ElMessage.error("完成评审失败");
  } finally {
    loading.value.updateReview = false;
  }
};

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

    await getReviewTaskDetail(currentReviewTask.value.id);

    if (activeTab.value === "my-tasks") {
      getMyTasks();
    } else {
      getMyInitiated();
    }
  } catch (error) {
    if (isPermissionError(error)) return;
    ElMessage.error("重新评审失败");
  } finally {
    loading.value.updateReview = false;
  }
};

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
    reviewDialogVisible.value = false;

    if (activeTab.value === "my-tasks") {
      getMyTasks();
    } else {
      getMyInitiated();
    }
  } catch (error) {
    if (isPermissionError(error)) return;
    ElMessage.error("重新发起评审失败");
  } finally {
    loading.value.updateReview = false;
  }
};

const handleRejectReview = async () => {
  if (!currentReviewTask.value) return;

  const pendingCount = caseReviews.value.filter((cr) => cr.review_status === "pending").length;
  const message =
    pendingCount > 0
      ? `当前还有 ${pendingCount} 条用例未填写评审结果，确定连同未填项一起打回吗？此操作将保存当前编辑并重置评审状态。`
      : "确定要打回评审吗？此操作将保存当前评审编辑并重置评审状态。";

  await ElMessageBox.confirm(message, "提示", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  });

  loading.value.updateReview = true;
  try {
    const modifiedCaseReviews = [];

    for (const currentReview of caseReviews.value) {
      const originalReview = originalCaseReviews.value.find(
        (orig) => orig.id === currentReview.id,
      );

      if (originalReview) {
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

    await reviewApi.rejectReview(currentReviewTask.value.id, {
      overall_comments: overallComments.value,
    });

    ElMessage.success("打回评审成功");

    reviewDialogVisible.value = false;

    if (activeTab.value === "my-tasks") {
      getMyTasks();
    } else {
      getMyInitiated();
    }
  } catch (error) {
    if (isPermissionError(error)) return;
    console.error("打回评审失败:", error);
    ElMessage.error(
      "打回评审失败: " + (error.response?.data?.message || error.message),
    );
  } finally {
    loading.value.updateReview = false;
  }
};

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

const handleSetAllApproved = async () => {
  if (!currentReviewTask.value || !caseReviews.value.length) return;
  await ElMessageBox.confirm("确定将所有用例设置为已通过？", "提示", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  });
  loading.value.updateReview = true;
  try {
    await Promise.all(
      caseReviews.value.map((row) =>
        reviewApi.updateCaseReview(row.review_task_id, row.case_id, {
          review_status: "approved",
          comments: row.comments || "",
        })
      )
    );
    caseReviews.value.forEach((row) => (row.review_status = "approved"));
    ElMessage.success("已全部设置为通过");
    if (activeTab.value === "my-tasks") getMyTasks();
    else getMyInitiated();
  } catch (e) {
    ElMessage.error("操作失败");
  } finally {
    loading.value.updateReview = false;
  }
};

const handleResetAllStatus = async () => {
  if (!currentReviewTask.value || !caseReviews.value.length) return;
  await ElMessageBox.confirm("确定将所有用例重置为待审核？", "提示", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  });
  loading.value.updateReview = true;
  try {
    await Promise.all(
      caseReviews.value.map((row) =>
        reviewApi.updateCaseReview(row.review_task_id, row.case_id, {
          review_status: "pending",
          comments: row.comments || "",
        })
      )
    );
    caseReviews.value.forEach((row) => (row.review_status = "pending"));
    ElMessage.success("已全部重置为待审核");
    if (activeTab.value === "my-tasks") getMyTasks();
    else getMyInitiated();
  } catch (e) {
    ElMessage.error("操作失败");
  } finally {
    loading.value.updateReview = false;
  }
};

const handleDialogClose = () => {
  currentReviewTask.value = null;
  caseReviews.value = [];
  overallComments.value = "";
  resetCaseReviewFilter();
  reviewDialogVisible.value = false;

  if (activeTab.value === "my-tasks") {
    getMyTasks();
  } else if (activeTab.value === "my-initiated") {
    getMyInitiated();
  }
};

const formatDate = (time) => {
  if (!time) return "-";
  try {
    let date;
    if (typeof time === "string") {
      if (/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/.test(time)) {
        return time;
      }

      date = new Date(time);
      if (isNaN(date.getTime())) {
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

const getStatusText = (status, historyType = null) => {
  if (historyType) {
    if (historyType === "reject") {
      return "已打回";
    } else if (historyType === "complete") {
      return "已完成";
    }
  }

  const statusMap = {
    pending: "待处理",
    in_review: "评审中",
    completed: "已完成",
    rejected: "已拒绝",
  };
  return statusMap[status] || status;
};

const getStatusTagType = (status, historyType = null) => {
  if (historyType) {
    if (historyType === "reject") {
      return "danger";
    } else if (historyType === "complete") {
      return "success";
    }
  }

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

watch(activeTab, (tab) => {
  if (tab === "review-history") getRecentReviewHistory();
});

watch([caseReviewKeyword, caseReviewPriorityFilter, caseReviewStatusFilter], () => {
  paginationCaseReview.value.page = 1;
});

// 消息跳转：taskId 时设置要闪烁的行，等列表有数据后再启动 2.5s 清除定时器，并可选自动打开详情
watch(
  () => route.query?.taskId,
  (taskIdVal) => {
    if (flashClearTimer) {
      clearTimeout(flashClearTimer);
      flashClearTimer = null;
    }
    if (!taskIdVal) {
      flashTaskId.value = null;
      hasOpenedDialogForFlashTask.value = false;
      return;
    }
    flashTaskId.value = Number(taskIdVal);
    hasOpenedDialogForFlashTask.value = false;
  },
  { immediate: true }
);

watch(
  () => [myTasks.value, myInitiated.value, flashTaskId.value, activeTab.value],
  async () => {
    const tid = flashTaskId.value;
    if (!tid) return;
    const inMyTasks = myTasks.value.some((t) => t.id === tid);
    const inMyInitiated = myInitiated.value.some((t) => t.id === tid);
    if (inMyTasks) activeTab.value = "my-tasks";
    else if (inMyInitiated) activeTab.value = "my-initiated";
    const list = activeTab.value === "my-tasks" ? myTasks.value : myInitiated.value;
    const hasRow = list.some((t) => t.id === tid);
    if (!hasRow) return;
    // 从消息带 taskId 进入时，自动打开该任务的评审详情弹窗（仅一次）
    if (!hasOpenedDialogForFlashTask.value) {
      hasOpenedDialogForFlashTask.value = true;
      reviewDialogTitle.value = "评审详情";
      reviewDialogVisible.value = true;
      await getReviewTaskDetail(tid);
    }
    if (flashClearTimer) return;
    flashClearTimer = setTimeout(() => {
      flashTaskId.value = null;
      const q = { ...route.query };
      delete q.taskId;
      router.replace({ path: route.path, query: Object.keys(q).length ? q : undefined });
      flashClearTimer = null;
    }, 2600);
  },
  { flush: "post" }
);

onMounted(async () => {
  systemSettingsStore.load();
  const size = defaultPageSize.value;
  paginationMyTasks.value.size = size;
  paginationMyInitiated.value.size = size;
  paginationRecent.value.size = size;
  paginationBySuite.value.size = size;
  paginationCaseReview.value.size = size;
  await getMyTasks();
  await getMyInitiated();
  await getAvailableSuites();
  const suiteId = route.query.suiteId;
  if (suiteId && !route.query.taskId) {
    try {
      const sid = parseInt(suiteId, 10);
      const inMyTasks = myTasks.value.find((t) => t.suite_id === sid);
      const inMyInitiated = myInitiated.value.find((t) => t.suite_id === sid);
      const suiteTask = inMyTasks || inMyInitiated;
      if (suiteTask) {
        highlightedSuiteTaskId.value = suiteTask.id;
        if (inMyTasks) activeTab.value = "my-tasks";
        else activeTab.value = "my-initiated";
        reviewDialogTitle.value = "评审详情";
        reviewDialogVisible.value = true;
        await getReviewTaskDetail(suiteTask.id);
      }
      const nextQuery = { ...route.query };
      delete nextQuery.suiteId;
      if (!nextQuery.activeTab) nextQuery.activeTab = inMyTasks ? "my-tasks" : "my-initiated";
      router.replace({ path: route.path, query: Object.keys(nextQuery).length ? nextQuery : undefined });
    } catch (error) {
      if (isPermissionError(error)) {
        const nextQuery = { ...route.query };
        delete nextQuery.suiteId;
        if (!nextQuery.activeTab) nextQuery.activeTab = "my-initiated";
        router.replace({ path: route.path, query: Object.keys(nextQuery).length ? nextQuery : undefined });
        return;
      }
      console.error("处理套件ID跳转失败:", error);
      ElMessage.error("处理跳转失败，请手动查找评审任务");
      const nextQuery = { ...route.query };
      delete nextQuery.suiteId;
      if (!nextQuery.activeTab) nextQuery.activeTab = "my-initiated";
      router.replace({ path: route.path, query: Object.keys(nextQuery).length ? nextQuery : undefined });
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
  background-color: var(--el-bg-color, #fff);
  border-color: var(--el-border-color-light, #ebeef5);
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
  color: var(--el-text-color-secondary, #909399);
  font-size: 12px;
  margin-left: 4px;
}

.folder-node {
  color: var(--el-text-color-secondary, #909399);
  cursor: pointer;
}

.folder-node .node-label,
.folder-node .node-icon {
  cursor: pointer;
}

.review-tabs :deep(.el-tabs__header) {
  margin-bottom: 20px;
  flex-shrink: 0;
  padding-left: 16px;
}

.review-section {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: var(--el-fill-color-light, #fafafa);
  padding: 20px;
  border-radius: 8px;
  overflow: hidden;

  .section-header,
  .list-filter-bar,
  .review-list-pagination {
    flex-shrink: 0;
  }
}

.review-history-sub-tabs {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}
.review-history-sub-tabs :deep(.el-tabs__content) {
  flex: 1;
  min-height: 0;
  overflow: auto;
}
.review-history-sub-tabs :deep(.el-tab-pane) {
  height: 100%;
}

/* 按用例集查看历史：列表与分页布局，分页固定在容器底部 */
.by-suite-layout {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
}
.by-suite-layout .section-header,
.by-suite-layout .suite-selector,
.by-suite-layout .review-list-pagination {
  flex-shrink: 0;
}
.by-suite-layout .review-table-wrapper {
  flex: 1;
  min-height: 0;
  overflow: auto;
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

/* 从用例管理点击「评审」跳转过来时，对应任务行的蓝色选中样式 */
.review-list-table :deep(tr.review-row-selected) {
  background-color: var(--el-color-primary-light-9, #ecf5ff) !important;
}
.review-list-table :deep(tr.review-row-selected:hover) {
  background-color: var(--el-color-primary-light-8, #d9ecff) !important;
}

.suite-name-trigger {
  cursor: pointer;
  color: var(--el-color-primary);
  text-decoration: none;
  border-bottom: 1px dashed var(--el-color-primary);
}
.suite-name-trigger:hover {
  color: var(--el-color-primary-light-3);
}

.section-header {
  margin-bottom: 15px;

  h3 {
    margin: 0;
    font-size: 16px;
  }

  .section-tip {
    margin: 6px 0 0;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }
}

.list-filter-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;

  .el-input,
  .el-select {
    margin: 0;
  }
}

.review-list-pagination {
  margin-top: 12px;
  justify-content: flex-end;
  flex-shrink: 0;
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
