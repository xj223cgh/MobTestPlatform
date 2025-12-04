<template>
  <div class="test-task-management">
    <div class="page-header">
      <div class="header-content">
        <h1>测试任务管理</h1>
        <p class="description">
          创建和管理测试任务
        </p>
      </div>
      <div class="header-actions">
        <el-button
          type="primary"
          @click="handleCreate"
        >
          <el-icon><Plus /></el-icon>
          创建任务
        </el-button>
        <el-button @click="handleBatchCreate">
          <el-icon><Operation /></el-icon>
          批量创建
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon total">
              <el-icon><List /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">
                {{ stats.total }}
              </div>
              <div class="stat-label">
                任务总数
              </div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon running">
              <el-icon><VideoPlay /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">
                {{ stats.running }}
              </div>
              <div class="stat-label">
                执行中
              </div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon completed">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">
                {{ stats.completed }}
              </div>
              <div class="stat-label">
                已完成
              </div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon failed">
              <el-icon><CircleClose /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">
                {{ stats.failed }}
              </div>
              <div class="stat-label">
                失败
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-section">
      <el-form
        :model="searchForm"
        inline
      >
        <el-form-item label="任务名称">
          <el-input
            v-model="searchForm.name"
            placeholder="请输入任务名称"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="所属套件">
          <el-select
            v-model="searchForm.suite_id"
            placeholder="选择测试套件"
            clearable
            filterable
            @clear="handleSearch"
            @change="handleSearch"
          >
            <el-option
              v-for="option in suiteOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="searchForm.status"
            placeholder="请选择状态"
            clearable
            @clear="handleSearch"
            @change="handleSearch"
          >
            <el-option
              label="待执行"
              value="pending"
            />
            <el-option
              label="执行中"
              value="running"
            />
            <el-option
              label="已完成"
              value="completed"
            />
            <el-option
              label="失败"
              value="failed"
            />
            <el-option
              label="已取消"
              value="cancelled"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select
            v-model="searchForm.priority"
            placeholder="请选择优先级"
            clearable
            @clear="handleSearch"
            @change="handleSearch"
          >
            <el-option
              label="高"
              value="high"
            />
            <el-option
              label="中"
              value="medium"
            />
            <el-option
              label="低"
              value="low"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="创建时间">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="handleSearch"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            @click="handleSearch"
          >
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 测试任务表格 -->
    <div class="table-section">
      <el-table
        v-loading="loading"
        :data="taskList"
        stripe
        border
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column
          type="selection"
          width="55"
        />
        <el-table-column
          prop="id"
          label="ID"
          width="80"
        />
        <el-table-column
          prop="name"
          label="任务名称"
          min-width="200"
          show-overflow-tooltip
        />
        <el-table-column
          prop="status"
          label="状态"
          width="100"
        >
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="priority"
          label="优先级"
          width="80"
        >
          <template #default="{ row }">
            <el-tag :type="getPriorityTagType(row.priority)">
              {{ getPriorityLabel(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="progress"
          label="进度"
          width="120"
        >
          <template #default="{ row }">
            <el-progress
              :percentage="row.progress"
              :status="getProgressStatus(row.status)"
              :stroke-width="6"
            />
          </template>
        </el-table-column>
        <el-table-column
          prop="device_count"
          label="设备数量"
          width="100"
        />
        <el-table-column
          prop="case_count"
          label="用例数量"
          width="100"
        />
        <el-table-column
          prop="creator"
          label="创建者"
          width="100"
        />
        <el-table-column
          prop="created_at"
          label="创建时间"
          width="160"
        >
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column
          prop="updated_at"
          label="更新时间"
          width="160"
        >
          <template #default="{ row }">
            {{ formatDateTime(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column
          label="操作"
          width="300"
          fixed="right"
        >
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="handleView(row)"
            >
              查看
            </el-button>
            <el-button
              v-if="row.status === 'pending'"
              type="success"
              size="small"
              @click="handleStart(row)"
            >
              启动
            </el-button>
            <el-button
              v-if="row.status === 'running'"
              type="warning"
              size="small"
              @click="handleStop(row)"
            >
              停止
            </el-button>
            <el-button
              v-if="row.status === 'completed' || row.status === 'failed'"
              type="info"
              size="small"
              @click="handleRerun(row)"
            >
              重新执行
            </el-button>
            <el-button
              type="warning"
              size="small"
              :disabled="row.status === 'running'"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              :disabled="row.status === 'running'"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 批量操作 -->
      <div
        v-if="selectedTasks.length > 0"
        class="batch-actions"
      >
        <span>已选择 {{ selectedTasks.length }} 项</span>
        <el-button
          type="success"
          @click="handleBatchStart"
        >
          批量启动
        </el-button>
        <el-button
          type="warning"
          @click="handleBatchStop"
        >
          批量停止
        </el-button>
        <el-button
          type="danger"
          @click="handleBatchDelete"
        >
          批量删除
        </el-button>
      </div>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          :current-page="pagination.page"
          :page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 创建/编辑测试任务对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="900px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="taskFormRef"
        :model="taskForm"
        :rules="taskRules"
        label-width="100px"
      >
        <el-form-item
          label="任务名称"
          prop="name"
        >
          <el-input
            v-model="taskForm.name"
            placeholder="请输入任务名称"
          />
        </el-form-item>
        <el-form-item
          label="测试套件"
          prop="suite_id"
        >
          <el-select
            v-model="taskForm.suite_id"
            placeholder="请选择测试套件"
            style="width: 100%"
          >
            <el-option
              v-for="suite in suiteOptions"
              :key="suite.id"
              :label="suite.name"
              :value="suite.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item
          label="任务描述"
          prop="description"
        >
          <el-input
            v-model="taskForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入任务描述"
          />
        </el-form-item>
        <el-form-item
          label="文档链接"
          prop="document_link"
        >
          <el-input
            v-model="taskForm.document_link"
            placeholder="请输入相关文档链接"
          />
        </el-form-item>
        <el-form-item
          label="版本信息"
          prop="version_info"
        >
          <el-input
            v-model="taskForm.version_info"
            placeholder="请输入版本信息"
          />
        </el-form-item>
        <el-form-item
          label="计划开始时间"
          prop="planned_start_time"
        >
          <el-date-picker
            v-model="taskForm.planned_start_time"
            type="datetime"
            placeholder="选择日期时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item
          label="计划结束时间"
          prop="planned_end_time"
        >
          <el-date-picker
            v-model="taskForm.planned_end_time"
            type="datetime"
            placeholder="选择日期时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item
          label="备注"
          prop="notes"
        >
          <el-input
            v-model="taskForm.notes"
            type="textarea"
            :rows="2"
            placeholder="请输入备注信息"
          />
        </el-form-item>
        <el-form-item
          label="优先级"
          prop="priority"
        >
          <el-radio-group v-model="taskForm.priority">
            <el-radio label="high">
              高
            </el-radio>
            <el-radio label="medium">
              中
            </el-radio>
            <el-radio label="low">
              低
            </el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item
          label="选择设备"
          prop="device_ids"
        >
          <el-select
            v-model="taskForm.device_ids"
            placeholder="请选择设备"
            multiple
            style="width: 100%"
          >
            <el-option
              v-for="device in deviceList"
              :key="device.id"
              :label="device.name"
              :value="device.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item
          label="测试用例"
          prop="case_ids"
        >
          <el-select
            v-model="taskForm.case_ids"
            placeholder="请选择测试用例"
            multiple
            style="width: 100%"
          >
            <el-option
              v-for="testCase in testCaseList"
              :key="testCase.id"
              :label="testCase.name"
              :value="testCase.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item
          label="执行环境"
          prop="environment"
        >
          <el-select
            v-model="taskForm.environment"
            placeholder="请选择执行环境"
          >
            <el-option
              label="开发环境"
              value="development"
            />
            <el-option
              label="测试环境"
              value="testing"
            />
            <el-option
              label="预生产环境"
              value="staging"
            />
            <el-option
              label="生产环境"
              value="production"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="执行配置">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item
                label="并发数"
                prop="concurrency"
              >
                <el-input-number
                  v-model="taskForm.concurrency"
                  :min="1"
                  :max="10"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item
                label="超时时间(秒)"
                prop="timeout"
              >
                <el-input-number
                  v-model="taskForm.timeout"
                  :min="60"
                  :max="3600"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form-item>
        <el-form-item
          label="失败重试"
          prop="retry_count"
        >
          <el-input-number
            v-model="taskForm.retry_count"
            :min="0"
            :max="5"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="通知设置">
          <el-checkbox-group v-model="taskForm.notification_types">
            <el-checkbox label="email">
              邮件通知
            </el-checkbox>
            <el-checkbox label="webhook">
              Webhook通知
            </el-checkbox>
            <el-checkbox label="sms">
              短信通知
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="submitLoading"
            @click="handleSubmit"
          >
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 任务详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="任务详情"
      width="1000px"
    >
      <div
        v-if="currentTask"
        class="task-detail"
      >
        <el-tabs v-model="activeTab">
          <el-tab-pane
            label="基本信息"
            name="basic"
          >
            <el-descriptions
              :column="2"
              border
            >
              <el-descriptions-item label="任务ID">
                {{ currentTask.id }}
              </el-descriptions-item>
              <el-descriptions-item label="任务名称">
                {{ currentTask.name }}
              </el-descriptions-item>
              <el-descriptions-item label="测试套件">
                {{ getSuiteName(currentTask.suite_id) }}
              </el-descriptions-item>
              <el-descriptions-item label="文档链接">
                <a
                  v-if="currentTask.document_link"
                  :href="currentTask.document_link"
                  target="_blank"
                >
                  {{ currentTask.document_link }}
                </a>
                <span v-else>-</span>
              </el-descriptions-item>
              <el-descriptions-item label="版本信息">
                {{ currentTask.version_info || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="计划时间">
                {{ formatDateRange(currentTask.planned_start_time, currentTask.planned_end_time) }}
              </el-descriptions-item>
              <el-descriptions-item
                label="备注"
                :span="2"
              >
                {{ currentTask.notes || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="getStatusTagType(currentTask.status)">
                  {{ getStatusLabel(currentTask.status) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="优先级">
                <el-tag :type="getPriorityTagType(currentTask.priority)">
                  {{ getPriorityLabel(currentTask.priority) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="进度">
                <el-progress
                  :percentage="currentTask.progress"
                  :status="getProgressStatus(currentTask.status)"
                />
              </el-descriptions-item>
              <el-descriptions-item label="执行环境">
                {{ currentTask.environment }}
              </el-descriptions-item>
              <el-descriptions-item label="创建者">
                {{ currentTask.creator }}
              </el-descriptions-item>
              <el-descriptions-item label="创建时间">
                {{ formatDateTime(currentTask.created_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="开始时间">
                {{ formatDateTime(currentTask.started_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="结束时间">
                {{ formatDateTime(currentTask.ended_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="设备数量">
                {{ currentTask.device_count }}
              </el-descriptions-item>
              <el-descriptions-item label="用例数量">
                {{ currentTask.case_count }}
              </el-descriptions-item>
              <el-descriptions-item label="通过数量">
                {{ currentTask.passed_count }}
              </el-descriptions-item>
              <el-descriptions-item label="失败数量">
                {{ currentTask.failed_count }}
              </el-descriptions-item>
              <el-descriptions-item label="阻塞数量">
                {{ currentTask.blocked_count || 0 }}
              </el-descriptions-item>
              <el-descriptions-item label="不适用数量">
                {{ currentTask.not_applicable_count || 0 }}
              </el-descriptions-item>
              <el-descriptions-item
                label="描述"
                :span="2"
              >
                {{ currentTask.description || '-' }}
              </el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>
          
          <el-tab-pane
            label="执行日志"
            name="logs"
          >
            <div class="logs-container">
              <el-timeline>
                <el-timeline-item
                  v-for="log in executionLogs"
                  :key="log.id"
                  :timestamp="formatDateTime(log.created_at)"
                  :type="getLogType(log.level)"
                >
                  <div class="log-content">
                    <strong>{{ log.level.toUpperCase() }}</strong>
                    <p>{{ log.message }}</p>
                  </div>
                </el-timeline-item>
              </el-timeline>
            </div>
          </el-tab-pane>
          
          <el-tab-pane
            label="执行结果"
            name="results"
          >
            <div class="results-container">
              <el-table 
                :data="executionResults" 
                stripe 
                border
                :row-style="{height: 'auto'}"
                :cell-style="{padding: '10px', whiteSpace: 'normal', wordBreak: 'break-word'}"
              >
                <el-table-column
                  prop="device_name"
                  label="设备名称"
                  min-width="120"
                />
                <el-table-column
                  prop="case_name"
                  label="用例名称"
                  min-width="200"
                />
                <el-table-column
                  prop="status"
                  label="状态"
                  width="100"
                >
                  <template #default="{ row }">
                    <el-tag :type="getStatusTagType(row.status)">
                      {{ getStatusLabel(row.status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column
                  prop="duration"
                  label="执行时长"
                  width="100"
                />
                <el-table-column
                  prop="error_message"
                  label="错误信息"
                  min-width="300"
                />
                <el-table-column
                  label="操作"
                  width="120"
                >
                  <template #default="{ row }">
                    <el-button
                      type="primary"
                      size="small"
                      @click="viewResultDetail(row)"
                    >
                      查看详情
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>
          
          <el-tab-pane
            label="思维导图视图"
            name="mindmap"
            @tab-click="refreshMindMap"
          >
            <div class="mindmap-container">
              <div class="filter-controls">
                <el-checkbox-group
                  v-model="statusFilter"
                  @change="filterMindMap"
                >
                  <el-checkbox label="passed">
                    通过
                  </el-checkbox>
                  <el-checkbox label="failed">
                    失败
                  </el-checkbox>
                  <el-checkbox label="blocked">
                    阻塞
                  </el-checkbox>
                  <el-checkbox label="not_applicable">
                    不适用
                  </el-checkbox>
                </el-checkbox-group>
                <el-button
                  type="primary"
                  size="small"
                  @click="refreshMindMap"
                >
                  刷新
                </el-button>
                <el-button
                  size="small"
                  @click="exportMindMap"
                >
                  导出
                </el-button>
              </div>
              <div class="stats-summary">
                <!-- 详细统计卡片 -->
                <el-card
                  shadow="hover"
                  class="stat-card stat-passed"
                >
                  <div class="stat-value">
                    {{ executionStats.passed?.count || 0 }}
                  </div>
                  <div class="stat-label">
                    通过
                  </div>
                </el-card>
                <el-card
                  shadow="hover"
                  class="stat-card stat-failed"
                >
                  <div class="stat-value">
                    {{ executionStats.failed?.count || 0 }}
                  </div>
                  <div class="stat-label">
                    失败
                  </div>
                </el-card>
                <el-card
                  shadow="hover"
                  class="stat-card stat-blocked"
                >
                  <div class="stat-value">
                    {{ executionStats.blocked?.count || 0 }}
                  </div>
                  <div class="stat-label">
                    阻塞
                  </div>
                </el-card>
                <el-card
                  shadow="hover"
                  class="stat-card stat-not-applicable"
                >
                  <div class="stat-value">
                    {{ executionStats.not_applicable?.count || 0 }}
                  </div>
                  <div class="stat-label">
                    不适用
                  </div>
                </el-card>
                <el-card
                  shadow="hover"
                  class="stat-card stat-total"
                >
                  <div class="stat-value">
                    {{ totalTestCases }}
                  </div>
                  <div class="stat-label">
                    总用例数
                  </div>
                </el-card>
                <el-card
                  shadow="hover"
                  class="stat-card stat-pass-rate"
                >
                  <div class="stat-value">
                    {{ executionStats.pass_rate || 0 }}%
                  </div>
                  <div class="stat-label">
                    通过率
                  </div>
                </el-card>
              </div>
              
              <!-- 图表统计 -->
              <div class="chart-section">
                <el-card
                  shadow="hover"
                  class="chart-card"
                >
                  <template #header>
                    <div class="card-header">
                      <span>测试结果分布</span>
                      <el-button
                        size="small"
                        @click="refreshStats"
                      >
                        刷新
                      </el-button>
                    </div>
                  </template>
                  <div class="chart-container">
                    <div class="chart-placeholder">
                      <el-progress 
                        v-for="(stat, key) in filteredExecutionStats" 
                        :key="key"
                        :percentage="calculatePercentage(stat?.count)" 
                        :format="() => `${stat?.label}: ${stat?.count}`" 
                        :color="getProgressColor(key)"
                        class="progress-bar"
                      />
                    </div>
                  </div>
                </el-card>
              </div>
              <div class="mindmap-content">
                <!-- 这里将集成思维导图组件 -->
                <div
                  v-if="mindmapLoading"
                  class="loading-container"
                >
                  <el-icon class="is-loading">
                    <loading />
                  </el-icon>
                  <span>加载思维导图中...</span>
                </div>
                <div
                  v-else-if="!taskMindMapData"
                  class="empty-state"
                >
                  <el-empty description="暂无思维导图数据" />
                </div>
                <div
                  v-else
                  class="mindmap-container"
                >
                  <el-tree
                    ref="mindmapTreeRef"
                    :data="filteredMindMapData"
                    :props="{ label: 'name', children: 'children' }"
                    :highlight-current="true"
                    :default-expand-all="true"
                    @node-click="handleMindmapNodeClick"
                    @node-contextmenu="handleMindmapContextMenu"
                  >
                    <template #default="{ data }">
                      <div
                        class="mindmap-node"
                        :class="`node-status-${data.status}`"
                      >
                        <span class="node-name">{{ data.name }}</span>
                        <span
                          v-if="data.status"
                          class="node-status-badge"
                          :class="`badge-${data.status}`"
                        >{{ getMindmapStatusLabel(data.status) }}</span>
                      </div>
                    </template>
                  </el-tree>
                  
                  <!-- 右键菜单 -->
                  <div 
                    v-if="contextMenuVisible" 
                    class="context-menu"
                    :style="{ left: contextMenuPosition.x + 'px', top: contextMenuPosition.y + 'px' }"
                    @click="contextMenuVisible = false"
                  >
                    <div
                      class="context-menu-item"
                      @click.stop="setNodeStatus('passed')"
                    >
                      <span class="status-indicator passed" />通过
                    </div>
                    <div
                      class="context-menu-item"
                      @click.stop="setNodeStatus('failed')"
                    >
                      <span class="status-indicator failed" />失败
                    </div>
                    <div
                      class="context-menu-item"
                      @click.stop="setNodeStatus('blocked')"
                    >
                      <span class="status-indicator blocked" />阻塞
                    </div>
                    <div
                      class="context-menu-item"
                      @click.stop="setNodeStatus('not_applicable')"
                    >
                      <span class="status-indicator not-applicable" />不适用
                    </div>
                    <div
                      class="context-menu-item"
                      @click.stop="setNodeStatus(null)"
                    >
                      <span class="status-indicator clear" />清除状态
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, Operation, List, VideoPlay, CircleCheck, CircleClose, Loading } from '@element-plus/icons-vue'
import { getTestTaskList, createTestTask, updateTestTask, deleteTestTask, getTestTaskStats, startTestTask, stopTestTask, rerunTestTask, batchDeleteTestTasks, batchStartTestTasks, batchStopTestTasks, getTaskOptions, getTaskXmindView } from '@/api/testTask'
import { getDeviceList } from '@/api/device'
import { getTestCaseList } from '@/api/testCase'
import { getTestSuiteOptions } from '@/api/testSuite'
import dayjs from 'dayjs'

// 响应式数据
const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const isEdit = ref(false)
const dialogTitle = ref('')
const taskFormRef = ref()
const currentTask = ref(null)
const selectedTasks = ref([])
const activeTab = ref('basic')
const mindmapTreeRef = ref(null)
const contextMenuVisible = ref(false)
const contextMenuPosition = ref({ x: 0, y: 0 })
const selectedMindmapNode = ref(null)
// 思维导图相关数据
const mindmapLoading = ref(false)
const taskMindMapData = ref(null)
const filteredMindMapData = ref(null)
const statusFilter = ref(['passed', 'failed', 'blocked', 'not_applicable'])
const executionStats = ref({
  passed: { type: 'passed', label: '通过', count: 0 },
  failed: { type: 'failed', label: '失败', count: 0 },
  blocked: { type: 'blocked', label: '阻塞', count: 0 },
  not_applicable: { type: 'not_applicable', label: '不适用', count: 0 },
  pass_rate: 0
})

// 计算属性 - 过滤后的执行统计数据（排除pass_rate且count>0）
const filteredExecutionStats = computed(() => {
  const result = {}
  for (const [key, stat] of Object.entries(executionStats.value)) {
    if (key !== 'pass_rate' && stat?.count > 0) {
      result[key] = stat
    }
  }
  return result
})

// 计算属性 - 总用例数
const totalTestCases = computed(() => {
  let total = 0
  const countNodes = (nodes) => {
    if (!nodes || !nodes.length) return 0
    
    nodes.forEach(node => {
      // 只统计有状态的叶子节点
      if (node.status && (!node.children || node.children.length === 0)) {
        total++
      }
      if (node.children && node.children.length > 0) {
        countNodes(node.children)
      }
    })
    return total
  }
  
  if (taskMindMapData.value) {
    countNodes(taskMindMapData.value)
  }
  return total
})

// 统计数据
const stats = reactive({
  total: 0,
  running: 0,
  completed: 0,
  failed: 0
})

// 搜索表单
const searchForm = reactive({
  name: '',
  suite_id: '',
  status: '',
  priority: '',
  dateRange: []
})

// 测试任务表单
const taskForm = reactive({
  id: null,
  name: '',
  description: '',
  suite_id: '',
  document_link: '',
  version_info: '',
  planned_start_time: '',
  planned_end_time: '',
  notes: '',
  priority: 'medium',
  device_ids: [],
  case_ids: [],
  environment: 'testing',
  concurrency: 1,
  timeout: 300,
  retry_count: 0,
  notification_types: []
})

// 表单验证规则
const taskRules = {
  name: [
    { required: true, message: '请输入任务名称', trigger: 'blur' }
  ],
  suite_id: [
    { required: true, message: '请选择测试套件', trigger: 'change' }
  ],
  device_ids: [
    { required: true, message: '请选择设备', trigger: 'change' }
  ],
  case_ids: [
    { required: true, message: '请选择测试用例', trigger: 'change' }
  ],
  environment: [
    { required: true, message: '请选择执行环境', trigger: 'change' }
  ]
}

// 数据列表
const taskList = ref([])
const deviceList = ref([])
const testCaseList = ref([])
const executionLogs = ref([])
const executionResults = ref([])
const suiteOptions = ref([])

// 分页
const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

// 获取测试任务列表
const fetchTaskList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      ...searchForm
    }
    if (searchForm.dateRange && searchForm.dateRange.length === 2) {
      params.start_date = searchForm.dateRange[0]
      params.end_date = searchForm.dateRange[1]
    }
    const response = await getTestTaskList(params)
    if (response.success) {
      taskList.value = response.data.list
      pagination.total = response.data.total
    } else {
      ElMessage.error(response.message || '获取测试任务列表失败')
    }
  } catch (error) {
    console.error('获取测试任务列表失败:', error)
    ElMessage.error('获取测试任务列表失败')
  } finally {
    loading.value = false
  }
}

// 获取套件名称
const getSuiteName = (suiteId) => {
  const suite = suiteOptions.value.find(item => item.id === suiteId)
  return suite ? suite.name : '-'}

// 格式化日期范围
const formatDateRange = (start, end) => {
  if (!start && !end) return '-'
  const startStr = start ? formatDateTime(start) : '未设置'
  const endStr = end ? formatDateTime(end) : '未设置'
  return `${startStr} 至 ${endStr}`
}

// 筛选思维导图
const filterMindMap = () => {
  if (!taskMindMapData.value) return []
  
  const filterData = (data, filters) => {
    if (!data || !data.children || !data.children.length) return data
    
    const filteredChildren = data.children.filter(child => {
      // 如果节点有状态并且不在筛选列表中，且没有子节点，则过滤掉
      if (child.status && !filters.includes(child.status) && (!child.children || !child.children.length)) {
        return false
      }
      
      // 递归过滤子节点
      if (child.children && child.children.length > 0) {
        child.children = filterData(child, filters).children
      }
      
      // 如果节点没有状态但有子节点，或者子节点经过过滤后仍有内容，则保留
      return !child.status || filters.includes(child.status) || (child.children && child.children.length > 0)
    })
    
    return { ...data, children: filteredChildren }
  }
  
  filteredMindMapData.value = filterData(taskMindMapData.value, statusFilter.value)
}

// 更新节点状态
const updateNodeStatus = (node, status) => {
  node.status = status
  updateExecutionStats(taskMindMapData.value)
  filterMindMap() // 重新筛选以更新视图
  ElMessage.success('状态更新成功')
}

// 获取思维导图节点状态标签
const getMindmapStatusLabel = (status) => {
  const statusMap = {
    passed: '通过',
    failed: '失败',
    blocked: '阻塞',
    not_applicable: '不适用'
  }
  return statusMap[status] || ''
}

// 刷新思维导图
const refreshMindMap = async () => {
  if (!currentTask.value) return
  
  mindmapLoading.value = true
  try {
    // 调用getTaskXmindView API
    try {
      const response = await getTaskXmindView(currentTask.value.id)
      if (response.success) {
        taskMindMapData.value = response.data
        updateExecutionStats(response.data)
        filterMindMap() // 应用过滤
        mindmapLoading.value = false
        return
      }
    } catch (apiError) {
      console.log('API调用失败，使用模拟数据:', apiError)
    }
    
    // 模拟数据（当API不可用时）
    setTimeout(() => {
      taskMindMapData.value = {
        name: currentTask.value.name,
        children: [
          { 
            name: '功能模块1', 
            children: [
              { name: '用例1-1', status: 'passed' },
              { name: '用例1-2', status: 'failed' },
              { name: '用例1-3', status: 'blocked' }
            ]
          },
          { 
            name: '功能模块2', 
            children: [
              { name: '用例2-1', status: 'passed' },
              { name: '用例2-2', status: 'not_applicable' }
            ]
          }
        ]
      }
      // 模拟统计数据
      executionStats.value.passed.count = Math.floor(Math.random() * 50)
      executionStats.value.failed.count = Math.floor(Math.random() * 10)
      executionStats.value.blocked.count = Math.floor(Math.random() * 5)
      executionStats.value.not_applicable.count = Math.floor(Math.random() * 3)
      
      const total = executionStats.value.passed.count + executionStats.value.failed.count
      executionStats.value.pass_rate = total > 0 ? Math.round((executionStats.value.passed.count / total) * 100) : 0
      
      filterMindMap() // 应用过滤
      mindmapLoading.value = false
    }, 1000)
  } catch (error) {
    console.error('获取思维导图失败:', error)
    mindmapLoading.value = false
  }
}

// 导出思维导图
const exportMindMap = async () => {
  if (!currentTask.value || !taskMindMapData.value) return
  
  try {
    // 实现简单的导出功能
    const dataStr = JSON.stringify(taskMindMapData.value, null, 2)
    const blob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${currentTask.value.name}_思维导图.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出思维导图失败:', error)
    ElMessage.error('导出失败')
  }
}

// 处理思维导图节点点击
const handleMindmapNodeClick = (data) => {
  selectedMindmapNode.value = data
  // 可以在这里添加点击节点后的逻辑
}

// 处理思维导图右键菜单
const handleMindmapContextMenu = (event, data) => {
  event.preventDefault()
  selectedMindmapNode.value = data
  
  // 设置右键菜单位置并显示
  contextMenuPosition.value = { x: event.pageX, y: event.pageY }
  contextMenuVisible.value = true
}

// 设置节点状态
const setNodeStatus = (status) => {
  if (selectedMindmapNode.value) {
    updateNodeStatus(selectedMindmapNode.value, status)
    contextMenuVisible.value = false
  }
}

// 生命周期钩子中添加点击外部关闭右键菜单
onMounted(() => {
  // 初始化代码...
  
  // 添加点击外部关闭右键菜单的事件监听
  document.addEventListener('click', (e) => {
    // 检查点击的是否是右键菜单或其内部元素
    const contextMenu = document.querySelector('.context-menu')
    if (contextMenu && !contextMenu.contains(e.target) && 
        !e.target.closest('.mindmap-node')) {
      contextMenuVisible.value = false
    }
  })
  
  // 监听ESC键关闭右键菜单
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      contextMenuVisible.value = false
    }
  })
})

// 更新执行统计
const updateExecutionStats = (data) => {
  // 重置统计数据
  executionStats.value = {
    passed: { type: 'passed', label: '通过', count: 0 },
    failed: { type: 'failed', label: '失败', count: 0 },
    blocked: { type: 'blocked', label: '阻塞', count: 0 },
    not_applicable: { type: 'not_applicable', label: '不适用', count: 0 },
    pass_rate: 0
  }
  
  // 递归统计各状态节点数量
  const countNodes = (nodes) => {
    if (!nodes || !nodes.length) return 0
    
    let total = 0
    nodes.forEach(node => {
      // 只统计有状态的叶子节点
      if (node.status && (!node.children || node.children.length === 0)) {
        executionStats.value[node.status].count++
        total++
      }
      if (node.children && node.children.length > 0) {
        total += countNodes(node.children)
      }
    })
    return total
  }
  
  const total = countNodes(data)
  const passedCount = executionStats.value.passed.count
  executionStats.value.pass_rate = total > 0 ? Math.round((passedCount / total) * 100) : 0
}

// 计算百分比
const calculatePercentage = (count) => {
  const total = totalTestCases.value
  return total > 0 ? Math.round((count / total) * 100) : 0
}

// 获取进度条颜色
const getProgressColor = (status) => {
  const colorMap = {
    passed: '#67c23a',
    failed: '#f56c6c',
    blocked: '#e6a23c',
    not_applicable: '#909399'
  }
  return colorMap[status] || '#409eff'
}

// 刷新统计信息
const refreshStats = () => {
  updateExecutionStats(taskMindMapData.value)
  ElMessage.success('统计信息已刷新')
}

// 查看用例详情
const viewTestCaseDetail = (row) => {
  // 实现用例详情查看
  console.log('查看用例详情:', row)
}

// 获取任务统计
const fetchTaskStats = async () => {
  try {
    const response = await getTestTaskStats()
    if (response.success) {
      Object.assign(stats, response.data)
    }
  } catch (error) {
    console.error('获取测试任务统计失败:', error)
  }
}

// 获取测试套件选项
const fetchSuiteOptions = async () => {
  try {
    const response = await getTaskOptions()
    if (response.success) {
      suiteOptions.value = response.data.suite_options || []
    }
  } catch (error) {
    console.error('获取测试套件选项失败:', error)
  }
}

// 获取设备列表
const fetchDeviceList = async () => {
  try {
    const response = await getDeviceList({ page: 1, size: 1000 })
    if (response.success) {
      deviceList.value = response.data.list
    }
  } catch (error) {
    console.error('获取设备列表失败:', error)
  }
}

// 获取测试用例列表
const fetchTestCaseList = async () => {
  try {
    const response = await getTestCaseList({ page: 1, size: 1000 })
    if (response.success) {
      testCaseList.value = response.data.list
    }
  } catch (error) {
    console.error('获取测试用例列表失败:', error)
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchTaskList()
}

// 重置搜索
const handleReset = () => {
  Object.assign(searchForm, {
    name: '',
    suite_id: '',
    status: '',
    priority: '',
    dateRange: []
  })
  handleSearch()
}

// 创建测试任务
const handleCreate = () => {
  isEdit.value = false
  dialogTitle.value = '创建测试任务'
  dialogVisible.value = true
  resetForm()
}

// 批量创建测试任务
const handleBatchCreate = () => {
  ElMessage.info('批量创建功能开发中...')
}

// 编辑测试任务
const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑测试任务'
  dialogVisible.value = true
  Object.assign(taskForm, {
    id: row.id,
    name: row.name,
    description: row.description,
    suite_id: row.suite_id || '',
    document_link: row.document_link || '',
    version_info: row.version_info || '',
    planned_start_time: row.planned_start_time || '',
    planned_end_time: row.planned_end_time || '',
    notes: row.notes || '',
    priority: row.priority,
    device_ids: row.device_ids,
    case_ids: row.case_ids,
    environment: row.environment,
    concurrency: row.concurrency,
    timeout: row.timeout,
    retry_count: row.retry_count,
    notification_types: row.notification_types || []
  })
}

// 查看任务详情
const handleView = async (row) => {
  currentTask.value = row
  detailDialogVisible.value = true
  activeTab.value = 'basic'
  
  // 获取执行日志和结果
  try {
    // 这里应该调用相应的API获取日志和结果
    executionLogs.value = []
    executionResults.value = []
    
    // 预加载思维导图数据
    setTimeout(() => {
      if (activeTab.value === 'mindmap') {
        refreshMindMap()
      }
    }, 500)
  } catch (error) {
    console.error('获取任务详情失败:', error)
  }
}

// 启动任务
const handleStart = async (row) => {
  try {
    const response = await startTestTask(row.id)
    if (response.success) {
      ElMessage.success('任务启动成功')
      fetchTaskList()
      fetchTaskStats()
    } else {
      ElMessage.error(response.message || '启动任务失败')
    }
  } catch (error) {
    console.error('启动任务失败:', error)
    ElMessage.error('启动任务失败')
  }
}

// 停止任务
const handleStop = async (row) => {
  try {
    const response = await stopTestTask(row.id)
    if (response.success) {
      ElMessage.success('任务停止成功')
      fetchTaskList()
      fetchTaskStats()
    } else {
      ElMessage.error(response.message || '停止任务失败')
    }
  } catch (error) {
    console.error('停止任务失败:', error)
    ElMessage.error('停止任务失败')
  }
}

// 重新执行任务
const handleRerun = async (row) => {
  try {
    const response = await rerunTestTask(row.id)
    if (response.success) {
      ElMessage.success('任务重新执行成功')
      fetchTaskList()
      fetchTaskStats()
    } else {
      ElMessage.error(response.message || '重新执行任务失败')
    }
  } catch (error) {
    console.error('重新执行任务失败:', error)
    ElMessage.error('重新执行任务失败')
  }
}

// 删除任务
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除测试任务 "${row.name}" 吗？此操作不可恢复。`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const response = await deleteTestTask(row.id)
      if (response.success) {
        ElMessage.success('删除成功')
        fetchTaskList()
        fetchTaskStats()
      } else {
        ElMessage.error(response.message || '删除失败')
      }
    } catch (error) {
      console.error('删除测试任务失败:', error)
      ElMessage.error('删除失败')
    }
  })
}

// 选择变化
const handleSelectionChange = (selection) => {
  selectedTasks.value = selection
}

// 批量启动
const handleBatchStart = async () => {
  if (selectedTasks.value.length === 0) {
    ElMessage.warning('请选择要启动的任务')
    return
  }
  
  try {
    const ids = selectedTasks.value.map(item => item.id)
    const response = await batchStartTestTasks(ids)
    if (response.success) {
      ElMessage.success('批量启动成功')
      fetchTaskList()
      fetchTaskStats()
    } else {
      ElMessage.error(response.message || '批量启动失败')
    }
  } catch (error) {
    console.error('批量启动失败:', error)
    ElMessage.error('批量启动失败')
  }
}

// 批量停止
const handleBatchStop = async () => {
  if (selectedTasks.value.length === 0) {
    ElMessage.warning('请选择要停止的任务')
    return
  }
  
  try {
    const ids = selectedTasks.value.map(item => item.id)
    const response = await batchStopTestTasks(ids)
    if (response.success) {
      ElMessage.success('批量停止成功')
      fetchTaskList()
      fetchTaskStats()
    } else {
      ElMessage.error(response.message || '批量停止失败')
    }
  } catch (error) {
    console.error('批量停止失败:', error)
    ElMessage.error('批量停止失败')
  }
}

// 批量删除
const handleBatchDelete = () => {
  if (selectedTasks.value.length === 0) {
    ElMessage.warning('请选择要删除的任务')
    return
  }
  
  ElMessageBox.confirm(
    `确定要删除选中的 ${selectedTasks.value.length} 个测试任务吗？此操作不可恢复。`,
    '确认批量删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const ids = selectedTasks.value.map(item => item.id)
      const response = await batchDeleteTestTasks(ids)
      if (response.success) {
        ElMessage.success('批量删除成功')
        fetchTaskList()
        fetchTaskStats()
      } else {
        ElMessage.error(response.message || '批量删除失败')
      }
    } catch (error) {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  })
}

// 提交表单
const handleSubmit = async () => {
  if (!taskFormRef.value) return
  
  try {
    await taskFormRef.value.validate()
    submitLoading.value = true
    
    // 构建提交参数，只包含需要的字段
    const params = {
      id: taskForm.id,
      name: taskForm.name,
      description: taskForm.description,
      suite_id: taskForm.suite_id,
      document_link: taskForm.document_link,
      version_info: taskForm.version_info,
      planned_start_time: taskForm.planned_start_time,
      planned_end_time: taskForm.planned_end_time,
      notes: taskForm.notes,
      priority: taskForm.priority,
      device_ids: taskForm.device_ids,
      case_ids: taskForm.case_ids,
      environment: taskForm.environment,
      concurrency: taskForm.concurrency,
      timeout: taskForm.timeout,
      retry_count: taskForm.retry_count,
      notification_types: taskForm.notification_types
    }
    
    let response
    if (isEdit.value) {
      response = await updateTestTask(taskForm.id, params)
    } else {
      response = await createTestTask(params)
    }
    
    if (response.success) {
      ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
      dialogVisible.value = false
      fetchTaskList()
      fetchTaskStats()
    } else {
      ElMessage.error(response.message || '操作失败')
    }
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('操作失败')
  } finally {
    submitLoading.value = false
  }
}

// 重置表单
const resetForm = () => {
  Object.assign(taskForm, {
    id: null,
    name: '',
    description: '',
    suite_id: '',
    document_link: '',
    version_info: '',
    planned_start_time: '',
    planned_end_time: '',
    notes: '',
    priority: 'medium',
    device_ids: [],
    case_ids: [],
    environment: 'testing',
    concurrency: 1,
    timeout: 300,
    retry_count: 0,
    notification_types: []
  })
  Object.assign(taskForm, {
    id: null,
    name: '',
    description: '',
    priority: 'medium',
    device_ids: [],
    case_ids: [],
    environment: 'testing',
    concurrency: 1,
    timeout: 300,
    retry_count: 0,
    notification_types: []
  })
  if (taskFormRef.value) {
    taskFormRef.value.resetFields()
  }
}

// 分页处理
const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  fetchTaskList()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  fetchTaskList()
}

// 查看结果详情
const viewResultDetail = (row) => {
  ElMessage.info('查看结果详情功能开发中...')
}

// 工具函数
const getStatusLabel = (status) => {
  const statusMap = {
    pending: '待执行',
    running: '执行中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消'
  }
  return statusMap[status] || status
}

const getStatusTagType = (status) => {
  const typeMap = {
    pending: 'info',
    running: 'primary',
    completed: 'success',
    failed: 'danger',
    cancelled: 'warning'
  }
  return typeMap[status] || 'info'
}

const getPriorityLabel = (priority) => {
  const priorityMap = {
    high: '高',
    medium: '中',
    low: '低'
  }
  return priorityMap[priority] || priority
}

const getPriorityTagType = (priority) => {
  const typeMap = {
    high: 'danger',
    medium: 'warning',
    low: 'success'
  }
  return typeMap[priority] || 'info'
}

const getProgressStatus = (status) => {
  const statusMap = {
    completed: 'success',
    failed: 'exception',
    running: '',
    pending: '',
    cancelled: 'warning'
  }
  return statusMap[status] || ''
}

const getLogType = (level) => {
  const typeMap = {
    error: 'danger',
    warning: 'warning',
    info: 'primary',
    debug: 'info'
  }
  return typeMap[level] || 'info'
}

const formatDateTime = (dateTime) => {
  return dateTime ? dayjs(dateTime).format('YYYY-MM-DD HH:mm:ss') : '-'
}

// 初始化
onMounted(() => {
  fetchTaskList()
  fetchTaskStats()
  fetchDeviceList()
  fetchTestCaseList()
  fetchSuiteOptions()
})
</script>

<style lang="scss" scoped>
.test-task-management {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
  
  .header-content {
    h1 {
      margin: 0 0 8px 0;
      font-size: 24px;
      font-weight: 600;
      color: #303133;
    }
    
    .description {
      margin: 0;
      color: #909399;
      font-size: 14px;
    }
  }
}

.stats-section {
  margin-bottom: 20px;
  
  .stat-card {
    display: flex;
    align-items: center;
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease;
    
    &:hover {
      transform: translateY(-2px);
    }
    
    .stat-icon {
      width: 50px;
      height: 50px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 15px;
      font-size: 24px;
      color: white;
      
      &.total {
        background: linear-gradient(135deg, #409eff, #66b1ff);
      }
      
      &.running {
        background: linear-gradient(135deg, #e6a23c, #ebb563);
      }
      
      &.completed {
        background: linear-gradient(135deg, #67c23a, #85ce61);
      }
      
      &.failed {
        background: linear-gradient(135deg, #f56c6c, #f78989);
      }
    }
    
    .stat-content {
      .stat-number {
        font-size: 28px;
        font-weight: 600;
        color: #303133;
        line-height: 1;
      }
      
      .stat-label {
        font-size: 14px;
        color: #909399;
        margin-top: 5px;
      }
    }
  }
}

.search-section {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 10px;
  
  .el-form {
    margin: 0;
  }
}

.table-section {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  
  .batch-actions {
    padding: 15px 20px;
    background: #f5f7fa;
    border-top: 1px solid #e4e7ed;
    display: flex;
    align-items: center;
    gap: 10px;
    
    span {
      color: #606266;
      font-size: 14px;
    }
  }
  
  .pagination {
    padding: 20px;
    text-align: right;
    border-top: 1px solid #e4e7ed;
  }
}

.task-detail {
  .el-descriptions {
    margin: 0;
  }
}

.logs-container {
  max-height: 400px;
  overflow-y: auto;
  
  .log-content {
    strong {
      color: #409eff;
    }
    
    p {
      margin: 5px 0 0 0;
      color: #606266;
    }
  }
}

.results-container {
  .el-table {
    margin: 0;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

// 思维导图样式
.mindmap-container {
  height: 500px;
  display: flex;
  flex-direction: column;
  
  .filter-controls {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    padding: 10px;
    background: #f5f7fa;
    border-radius: 4px;
  }
  
  .stats-summary {
    display: flex;
    gap: 15px;
    margin-bottom: 15px;
    flex-wrap: wrap;
    
    .stat-card {
      flex: 1;
      min-width: 120px;
      text-align: center;
      padding: 15px;
      transition: all 0.3s;
      
      &:hover {
        transform: translateY(-2px);
      }
      
      .stat-value {
        font-size: 24px;
        font-weight: 600;
        margin-bottom: 5px;
      }
      
      .stat-label {
        font-size: 14px;
        color: #606266;
      }
      
      // 不同状态卡片的颜色
      &.stat-passed .stat-value {
        color: #67c23a;
      }
      
      &.stat-failed .stat-value {
        color: #f56c6c;
      }
      
      &.stat-blocked .stat-value {
        color: #e6a23c;
      }
      
      &.stat-not-applicable .stat-value {
        color: #909399;
      }
      
      &.stat-total .stat-value {
        color: #409eff;
      }
      
      &.stat-pass-rate .stat-value {
        color: #1890ff;
      }
    }
    
    // 图表区域样式
    .chart-section {
      margin-bottom: 20px;
      width: 100%;
      
      .chart-card {
        .card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        
        .chart-container {
          padding: 20px 0;
          
          .progress-bar {
            margin-bottom: 15px;
          }
        }
      }
    }
  }
  
  .mindmap-content {
    flex: 1;
    position: relative;
    overflow: auto;
    border: 1px solid #ebeef5;
    border-radius: 4px;
    
    .loading-container,
    .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100%;
      color: #909399;
    }
    
    .mindmap-placeholder {
      padding: 30px;
      color: #606266;
      
      p {
        margin-bottom: 15px;
        font-weight: 500;
      }
      
      ul {
        margin-top: 0;
        padding-left: 20px;
      }
      
      li {
        margin-bottom: 8px;
      }
    }
  }
}

/* 思维导图节点样式 */
.mindmap-node {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 8px;
  border-radius: 4px;
  transition: all 0.3s;
}

.mindmap-node:hover {
  background-color: #f5f7fa;
  cursor: pointer;
}

.node-status-passed {
  background-color: #f0f9eb;
  border-left: 3px solid #67c23a;
}

.node-status-failed {
  background-color: #fef0f0;
  border-left: 3px solid #f56c6c;
}

.node-status-blocked {
  background-color: #fdf6ec;
  border-left: 3px solid #e6a23c;
}

.node-status-not_applicable {
  background-color: #f4f4f5;
  border-left: 3px solid #909399;
}

.node-name {
  flex: 1;
}

.node-status-badge {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
}

/* 状态按钮样式 */
.status-btn {
  padding: 8px 16px;
  margin: 5px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.status-btn:hover {
  opacity: 0.8;
}

.status-passed {
  background-color: #67c23a;
  color: white;
}

.status-failed {
  background-color: #f56c6c;
  color: white;
}

.status-blocked {
  background-color: #e6a23c;
  color: white;
}

.status-not-applicable {
  background-color: #909399;
  color: white;
}

/* 右键菜单样式 */
.context-menu {
  position: fixed;
  background: white;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  z-index: 1000;
  min-width: 120px;
}

.context-menu-item {
  padding: 10px 20px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.context-menu-item:hover {
    background-color: #f5f7fa;
  }

  /* 右键菜单中的状态指示器 */
  .status-indicator {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 8px;
    vertical-align: middle;
  }

  .status-indicator.passed {
    background-color: #67c23a;
  }

  .status-indicator.failed {
    background-color: #f56c6c;
  }

  .status-indicator.blocked {
    background-color: #e6a23c;
  }

  .status-indicator.not-applicable {
    background-color: #909399;
  }

  .status-indicator.clear {
    background-color: #dcdfe6;
  }

  /* 状态徽章样式 */
  .badge-passed {
    background-color: #67c23a;
    color: white;
  }

  .badge-failed {
    background-color: #f56c6c;
    color: white;
  }

  .badge-blocked {
    background-color: #e6a23c;
    color: white;
  }

  .badge-not_applicable {
    background-color: #909399;
    color: white;
  }

  /* 思维导图容器样式 */
  .mindmap-container {
    height: 500px;
    overflow: auto;
    border: 1px solid #ebeef5;
    border-radius: 4px;
    padding: 10px;
    background-color: #fafafa;
  }

  /* 响应式设计 */
  @media (max-width: 768px) {
  .test-task-management {
    padding: 10px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .stats-section {
    .el-col {
      margin-bottom: 10px;
    }
  }
  
  .search-section {
    padding: 15px;
    
    .el-form {
      .el-form-item {
        margin-bottom: 15px;
        margin-right: 0;
        width: 100%;
        
        .el-input,
        .el-select,
        .el-date-picker {
          width: 100%;
        }
      }
    }
  }
  
  .mindmap-container {
      height: 300px;
      
      .filter-controls {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
      }
      
      .stats-summary {
        flex-direction: column;
      }
      
      .status-filter {
        .el-checkbox-group {
          display: flex;
          flex-wrap: wrap;
          gap: 10px;
        }
      }
    }
    
    .mindmap-content {
      padding: 10px;
    }
  }
</style>