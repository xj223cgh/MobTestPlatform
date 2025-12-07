<template>
  <div class="iteration-management">
    <div class="management-header">
      <h2>迭代管理</h2>
      <div class="header-actions">
        <el-select
          v-model="selectedProjectId"
          placeholder="选择项目"
          style="width: 200px; margin-right: 15px;"
          @change="handleProjectChange"
        >
          <el-option
            v-for="project in projects"
            :key="project.id"
            :label="project.name"
            :value="project.id"
          />
        </el-select>
        <el-button
          type="primary"
          @click="showCreateIterationDialog"
        >
          <i class="el-icon-plus" /> 创建迭代
        </el-button>
      </div>
    </div>

    <!-- 视图切换 -->
    <div class="view-tabs">
      <el-tabs
        v-model="activeTab"
        @tab-change="handleTabChange"
      >
        <el-tab-pane
          label="甘特图"
          name="gantt"
        />
        <el-tab-pane
          label="列表视图"
          name="list"
        />
      </el-tabs>
    </div>

    <!-- 甘特图视图 -->
    <el-card
      v-if="activeTab === 'gantt'"
      class="list-card"
    >
      <div class="gantt-container">
        <v-chart :option="ganttChartOption" />
      </div>
    </el-card>

    <!-- 测试经理视图 -->
    <el-card
      v-if="activeTab === 'list'"
      class="list-card"
    >
      <!-- 搜索和筛选 -->
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索迭代名称"
          prefix-icon="el-icon-search"
          style="width: 300px; margin-right: 10px;"
        />
        <el-select
          v-model="statusFilter"
          placeholder="状态筛选"
          style="width: 150px; margin-right: 10px;"
        >
          <el-option
            label="全部状态"
            value=""
          />
          <el-option
            label="计划中"
            value="planning"
          />
          <el-option
            label="进行中"
            value="active"
          />
          <el-option
            label="已完成"
            value="completed"
          />
          <el-option
            label="已取消"
            value="cancelled"
          />
        </el-select>
        <el-button
          type="primary"
          @click="loadIterations"
        >
          查询
        </el-button>
      </div>

      <!-- 概览卡片 -->
      <div class="overview-cards">
        <el-card class="overview-card">
          <div class="overview-content">
            <div class="overview-title">
              进行中迭代
            </div>
            <div class="overview-value">
              {{ activeIterationsCount }}
            </div>
          </div>
        </el-card>
        <el-card class="overview-card">
          <div class="overview-content">
            <div class="overview-title">
              已完成迭代
            </div>
            <div class="overview-value">
              {{ completedIterationsCount }}
            </div>
          </div>
        </el-card>
        <el-card class="overview-card">
          <div class="overview-content">
            <div class="overview-title">
              缺陷总数
            </div>
            <div class="overview-value">
              {{ totalBugsCount }}
            </div>
          </div>
        </el-card>
        <el-card class="overview-card">
          <div class="overview-content">
            <div class="overview-title">
              平均通过率
            </div>
            <div class="overview-value">
              {{ averagePassRate }}%
            </div>
          </div>
        </el-card>
      </div>

      <!-- 迭代进度看板 -->
      <el-card class="section-card">
        <template #header>
          <div class="section-header">
            <span>迭代进度看板</span>
          </div>
        </template>
        <div class="kanban-container">
          <div class="kanban-column">
            <div class="kanban-column-header">
              计划中
            </div>
            <div class="kanban-items">
              <div
                v-for="iteration in plannedIterations"
                :key="iteration.id"
                class="kanban-item planning"
              >
                <div class="kanban-item-title">
                  {{ iteration.iteration_name }}
                </div>
                <div class="kanban-item-meta">
                  <span class="kanban-item-date">{{ iteration.start_date }} - {{ iteration.end_date }}</span>
                </div>
              </div>
            </div>
          </div>
          <div class="kanban-column">
            <div class="kanban-column-header">
              进行中
            </div>
            <div class="kanban-items">
              <div
                v-for="iteration in activeIterations"
                :key="iteration.id"
                class="kanban-item active"
              >
                <div class="kanban-item-title">
                  {{ iteration.iteration_name }}
                </div>
                <div class="kanban-item-progress">
                  <el-progress
                    :percentage="calculateRequirementProgress(iteration.requirement_stats)"
                    :stroke-width="4"
                  />
                </div>
                <div class="kanban-item-meta">
                  <span class="kanban-item-date">{{ iteration.start_date }} - {{ iteration.end_date }}</span>
                  <span class="kanban-item-pass-rate">通过率: {{ calculatePassRate(iteration.execution_stats) }}%</span>
                </div>
              </div>
            </div>
          </div>
          <div class="kanban-column">
            <div class="kanban-column-header">
              已完成
            </div>
            <div class="kanban-items">
              <div
                v-for="iteration in completedIterations"
                :key="iteration.id"
                class="kanban-item completed"
              >
                <div class="kanban-item-title">
                  {{ iteration.iteration_name }}
                </div>
                <div class="kanban-item-meta">
                  <span class="kanban-item-date">{{ iteration.start_date }} - {{ iteration.end_date }}</span>
                  <span class="kanban-item-pass-rate">通过率: {{ calculatePassRate(iteration.execution_stats) }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 图表容器 -->
      <div class="charts-container">
        <!-- 质量趋势图表 -->
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>质量趋势</span>
            </div>
          </template>
          <div class="chart-wrapper">
            <v-chart
              :option="qualityTrendOption"
              autoresize
            />
          </div>
        </el-card>

        <!-- 缺陷统计图表 -->
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>缺陷统计</span>
            </div>
          </template>
          <div class="chart-wrapper">
            <v-chart
              :option="bugStatsOption"
              autoresize
            />
          </div>
        </el-card>
      </div>

      <!-- 迭代详情列表 -->
      <el-card class="section-card">
        <template #header>
          <div class="section-header">
            <span>迭代详情</span>
          </div>
        </template>
        <el-table
          :data="iterationsData || []"
          stripe
          style="width: 100%; max-height: 800px; overflow-y: auto;"
        >
          <el-table-column
            prop="iteration_name"
            label="迭代名称"
            min-width="180"
          >
            <template #default="scope">
              <a
                href="#"
                @click.stop="showIterationDetail(scope.row)"
              >{{ scope.row?.iteration_name || '-' }}</a>
            </template>
          </el-table-column>
          <el-table-column
            label="所属项目"
            min-width="120"
            align="center"
          >
            <template #default="scope">
              {{ scope.row?.project_name || '-' }}
            </template>
          </el-table-column>
          <el-table-column
            label="状态"
            min-width="100"
            align="center"
          >
            <template #default="scope">
              <el-tag
                :type="getTagTypeByStatus(scope.row?.status || 'planning')"
                :effect="'light'"
              >
                {{ getStatusText(scope.row?.status || 'planning') }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            label="开始日期"
            min-width="120"
            align="center"
          >
            <template #default="scope">
              {{ scope.row?.start_date || '-' }}
            </template>
          </el-table-column>
          <el-table-column
            label="结束日期"
            min-width="120"
            align="center"
          >
            <template #default="scope">
              {{ scope.row?.end_date || '-' }}
            </template>
          </el-table-column>
          <el-table-column
            label="需求进度"
            min-width="150"
            align="center"
          >
            <template #default="scope">
              <el-progress
                :percentage="calculateRequirementProgress(scope.row?.requirement_stats)"
                :stroke-width="8"
                :color="getProgressColor(calculateRequirementProgress(scope.row?.requirement_stats))"
              />
            </template>
          </el-table-column>
          <el-table-column
            label="通过率"
            min-width="100"
            align="center"
          >
            <template #default="scope">
              <div class="pass-rate">
                {{ calculatePassRate(scope.row?.execution_stats) }}%
              </div>
            </template>
          </el-table-column>
          <el-table-column
            label="缺陷数"
            min-width="100"
            align="center"
          >
            <template #default="scope">
              <div class="bug-count">
                {{ scope.row?.bug_stats?.total || 0 }}
              </div>
            </template>
          </el-table-column>
          <el-table-column
            label="操作"
            min-width="180"
            fixed="right"
            align="center"
          >
            <template #default="scope">
              <div class="operation-buttons">
                <el-button
                  size="small"
                  type="primary"
                  icon="el-icon-edit"
                  @click="editIteration(scope.row)"
                >
                  编辑
                </el-button>
                <el-button
                  size="small"
                  type="info"
                  icon="el-icon-document-copy"
                  @click="copyIterationDialog(scope.row)"
                >
                  复制
                </el-button>
                <el-button
                  size="small"
                  type="danger"
                  icon="el-icon-delete"
                  @click="deleteIteration(scope.row)"
                >
                  删除
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </el-card>

    <!-- 创建/编辑迭代对话框 -->
    <el-dialog
      :visible="iterationDialogVisible"
      :title="iterationDialogTitle"
      width="600px"
      @close="resetIterationForm"
    >
      <el-form
        ref="iterationForm"
        :model="iterationForm"
        :rules="iterationRules"
        label-width="120px"
      >
        <el-form-item
          label="项目"
          prop="project_id"
        >
          <el-select
            v-model="iterationForm.project_id"
            placeholder="选择项目"
            disabled
          >
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item
          label="迭代名称"
          prop="iteration_name"
        >
          <el-input
            v-model="iterationForm.iteration_name"
            placeholder="请输入迭代名称"
          />
        </el-form-item>
        <el-form-item
          label="迭代目标"
          prop="goal"
        >
          <el-input
            v-model="iterationForm.goal"
            type="textarea"
            placeholder="请输入迭代目标"
            :rows="3"
          />
        </el-form-item>
        <el-form-item
          label="测试版本"
          prop="version"
        >
          <el-input
            v-model="iterationForm.version"
            placeholder="请输入测试版本"
          />
        </el-form-item>
        <el-form-item
          label="开始日期"
          prop="start_date"
        >
          <el-date-picker
            v-model="iterationForm.start_date"
            type="date"
            placeholder="选择开始日期"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item
          label="结束日期"
          prop="end_date"
        >
          <el-date-picker
            v-model="iterationForm.end_date"
            type="date"
            placeholder="选择结束日期"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item
          label="状态"
          prop="status"
        >
          <el-select
            v-model="iterationForm.status"
            placeholder="选择状态"
          >
            <el-option
              label="计划中"
              value="planning"
            />
            <el-option
              label="进行中"
              value="active"
            />
            <el-option
              label="已完成"
              value="completed"
            />
            <el-option
              label="已取消"
              value="cancelled"
            />
          </el-select>
        </el-form-item>
        <el-form-item
          label="备注"
          prop="description"
        >
          <el-input
            v-model="iterationForm.description"
            type="textarea"
            placeholder="请输入备注信息"
            :rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="closeIterationDialog">
            取消
          </el-button>
          <el-button
            type="primary"
            @click="submitIterationForm"
          >
            确定
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 复制迭代对话框 -->
    <el-dialog
      :visible="copyDialogVisible"
      title="复制迭代"
      width="500px"
    >
      <el-form
        ref="copyForm"
        :model="copyForm"
        :rules="copyRules"
        label-width="120px"
      >
        <el-form-item
          label="新迭代名称"
          prop="name"
        >
          <el-input
            v-model="copyForm.name"
            placeholder="请输入新迭代名称"
          />
        </el-form-item>
        <el-form-item
          label="开始日期"
          prop="start_date"
        >
          <el-date-picker
            v-model="copyForm.start_date"
            type="date"
            placeholder="选择开始日期"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item
          label="结束日期"
          prop="end_date"
        >
          <el-date-picker
            v-model="copyForm.end_date"
            type="date"
            placeholder="选择结束日期"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="复制测试计划">
          <el-switch v-model="copyForm.copy_test_plans" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="copyDialogVisible = false">
            取消
          </el-button>
          <el-button
            type="primary"
            @click="submitCopyForm"
          >
            确定
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 迭代详情对话框 -->
    <el-dialog
      :visible="detailDialogVisible"
      title="迭代详情"
      width="900px"
      :before-close="handleDetailDialogClose"
    >
      <div
        v-if="currentIteration"
        class="iteration-detail"
      >
        <!-- 基本信息 -->
        <el-descriptions
          border
          column="2"
          label-align="left"
          class="basic-info"
        >
          <el-descriptions-item label="迭代名称">
            {{ currentIteration.iteration_name }}
          </el-descriptions-item>
          <el-descriptions-item label="所属项目">
            {{ currentIteration.project_name }}
          </el-descriptions-item>
          <el-descriptions-item label="迭代目标">
            {{ currentIteration.goal }}
          </el-descriptions-item>
          <el-descriptions-item label="测试版本">
            {{ currentIteration.version }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getTagTypeByStatus(currentIteration.status)">
              {{ getStatusText(currentIteration.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="开始日期">
            {{ currentIteration.start_date }}
          </el-descriptions-item>
          <el-descriptions-item label="结束日期">
            {{ currentIteration.end_date }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(currentIteration.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="创建人">
            {{ currentIteration.created_by_name || '未知用户' }}
          </el-descriptions-item>
          <el-descriptions-item label="更新人">
            {{ currentIteration.updated_by_name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item
            label="备注"
            :span="2"
          >
            {{ currentIteration.description || '-' }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 统计卡片 -->
        <div class="stats-cards">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-title">
                需求统计
              </div>
              <div class="stat-value">
                {{ currentIteration.requirement_count }}
              </div>
              <div class="stat-detail">
                <span class="stat-item">已完成: {{ currentIteration.requirement_stats?.completed || 0 }}</span>
                <span class="stat-item">进行中: {{ currentIteration.requirement_stats?.in_progress || 0 }}</span>
                <span class="stat-item">未开始: {{ currentIteration.requirement_stats?.new || 0 }}</span>
              </div>
              <el-progress
                :percentage="calculateRequirementProgress(currentIteration.requirement_stats)"
                :stroke-width="6"
                :color="getProgressColor(calculateRequirementProgress(currentIteration.requirement_stats))"
                style="margin-top: 10px"
              />
            </div>
          </el-card>

          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-title">
                用例执行
              </div>
              <div class="stat-value">
                {{ currentIteration.execution_stats?.total || 0 }}
              </div>
              <div class="stat-detail">
                <span class="stat-item pass">通过: {{ currentIteration.execution_stats?.pass || 0 }}</span>
                <span class="stat-item fail">失败: {{ currentIteration.execution_stats?.fail || 0 }}</span>
                <span class="stat-item blocked">阻塞: {{ currentIteration.execution_stats?.blocked || 0 }}</span>
              </div>
              <el-progress
                :percentage="calculatePassRate(currentIteration.execution_stats)"
                :stroke-width="6"
                :color="getPassRateColor(calculatePassRate(currentIteration.execution_stats))"
                style="margin-top: 10px"
              />
            </div>
          </el-card>

          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-title">
                缺陷统计
              </div>
              <div class="stat-value">
                {{ currentIteration.bug_count }}
              </div>
              <div class="stat-detail">
                <span class="stat-item critical">严重: {{ currentIteration.bug_stats?.critical || 0 }}</span>
                <span class="stat-item high">高: {{ currentIteration.bug_stats?.high || 0 }}</span>
                <span class="stat-item medium">中: {{ currentIteration.bug_stats?.medium || 0 }}</span>
                <span class="stat-item low">低: {{ currentIteration.bug_stats?.low || 0 }}</span>
              </div>
              <div class="stat-status">
                <span class="stat-item open">未解决: {{ (currentIteration.bug_stats?.open || 0) + (currentIteration.bug_stats?.in_progress || 0) }}</span>
                <span class="stat-item resolved">已解决: {{ currentIteration.bug_stats?.resolved || 0 }}</span>
                <span class="stat-item closed">已关闭: {{ currentIteration.bug_stats?.closed || 0 }}</span>
              </div>
            </div>
          </el-card>
        </div>

        <!-- 相关数据标签页 -->
        <el-tabs
          v-model="detailActiveTab"
          class="detail-tabs"
        >
          <el-tab-pane
            label="需求列表"
            name="requirements"
          >
            <el-table
              :data="currentIteration?.version_requirements || []"
              stripe
              style="width: 100%"
              size="small"
            >
              <el-table-column
                prop="id"
                label="ID"
                width="80"
              />
              <el-table-column
                prop="requirement_name"
                label="需求名称"
              />
              <el-table-column
                prop="status"
                label="状态"
                width="100"
              >
                <template #default="scope">
                  <el-tag :type="getRequirementStatusType(scope.row?.status || 'new')">
                    {{ getRequirementStatusText(scope.row?.status || 'new') }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column
                prop="priority"
                label="优先级"
                width="100"
              />
              <el-table-column
                prop="assigned_to_name"
                label="负责人"
                width="120"
              >
                <template #default="scope">
                  {{ scope.row.assigned_to_name || '未知用户' }}
                </template>
              </el-table-column>
              <el-table-column
                prop="start_date"
                label="开始日期"
                width="120"
              />
              <el-table-column
                prop="end_date"
                label="结束日期"
                width="120"
              />
            </el-table>
          </el-tab-pane>

          <el-tab-pane
            label="测试任务"
            name="tasks"
          >
            <el-table
              :data="currentIteration?.test_tasks || []"
              stripe
              style="width: 100%"
              size="small"
            >
              <el-table-column
                prop="id"
                label="ID"
                width="80"
              />
              <el-table-column
                prop="task_name"
                label="任务名称"
              />
              <el-table-column
                prop="status"
                label="状态"
                width="100"
              >
                <template #default="scope">
                  <el-tag :type="getTaskStatusType(scope.row?.status || 'pending')">
                    {{ scope.row?.status || 'pending' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column
                prop="executor_name"
                label="执行人"
                width="120"
              />
              <el-table-column
                prop="scheduled_time"
                label="计划时间"
                width="150"
              />
              <el-table-column
                prop="statistics.pass_rate"
                label="通过率"
                width="100"
              />
            </el-table>
          </el-tab-pane>

          <el-tab-pane
            label="缺陷列表"
            name="bugs"
          >
            <el-table
              :data="currentIteration?.bugs || []"
              stripe
              style="width: 100%"
              size="small"
            >
              <el-table-column
                prop="id"
                label="ID"
                width="80"
              />
              <el-table-column
                prop="bug_title"
                label="缺陷标题"
              />
              <el-table-column
                prop="severity"
                label="严重程度"
                width="120"
              >
                <template #default="scope">
                  <el-tag :type="getBugSeverityType(scope.row?.severity || 'medium')">
                    {{ scope.row?.severity || 'medium' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column
                prop="status"
                label="状态"
                width="100"
              >
                <template #default="scope">
                  <el-tag :type="getBugStatusType(scope.row?.status || 'open')">
                    {{ scope.row?.status || 'open' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column
                prop="reporter_name"
                label="报告人"
                width="120"
              />
              <el-table-column
                prop="created_at"
                label="创建时间"
                width="150"
              />
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="detailDialogVisible = false">
            关闭
          </el-button>
          <el-button
            type="primary"
            @click="generateIterationReport"
          >
            生成报告
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted, watch } from 'vue'
import { getProjectIterations, createIteration, updateIteration, deleteIteration, copyIteration, getIteration, getIterationStats } from '@/api/iteration'
import { getProjects, getProjectVersionRequirements } from '@/api/project'
import dayjs from 'dayjs'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart, LineChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent, ToolboxComponent, DataZoomComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { ElLoading } from 'element-plus'

// 注册必要的组件
use([CanvasRenderer, PieChart, BarChart, LineChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent, ToolboxComponent, DataZoomComponent])

export default {
  name: 'IterationManagement',
  components: {
    VChart
  },
  data() {
    return {
      // 项目相关
      projects: [],
      selectedProjectId: null,
      
      // 视图切换
      activeTab: 'gantt',
      
      // 迭代列表数据
      iterations: [],
      iterationsData: [],
      total: 0,
      currentPage: 1,
      pageSize: 10,
      searchQuery: '',
      statusFilter: '',
      
      // 版本需求数据
      versionRequirements: [],
      
      // 图表数据
      activeIterationsCount: 0,
      completedIterationsCount: 0,
      totalBugsCount: 0,
      averagePassRate: 0,
      plannedIterations: [],
      activeIterations: [],
      completedIterations: [],
      
      // 甘特图配置
      ganttChartOption: {
        title: {
          text: '迭代甘特图',
          left: 'center',
          textStyle: {
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          },
          formatter: function(params) {
            let result = `<strong>${params[0].name}</strong><br/>`;
            params.forEach(param => {
              const start = dayjs(param.data[0]).format('YYYY-MM-DD');
              const end = dayjs(param.data[1]).format('YYYY-MM-DD');
              const status = param.data[2] || '';
              const progress = param.data[3] || 0;
              result += `${param.marker} <strong>${param.seriesName}</strong>: ${start} - ${end}<br/>`;
              if (status) {
                result += `状态: ${status}<br/>`;
              }
              if (progress > 0) {
                result += `进度: ${progress}%<br/>`;
              }
            });
            return result;
          }
        },
        legend: {
          data: ['迭代', '需求'],
          top: 10,
          textStyle: {
            fontSize: 12
          }
        },
        grid: {
          left: '15%',
          right: '10%',
          bottom: '15%',
          top: '20%',
          containLabel: true
        },
        xAxis: {
          type: 'time',
          axisLabel: {
            formatter: '{yyyy}-{MM}-{dd}',
            fontSize: 11
          },
          splitLine: {
            show: true,
            lineStyle: {
              type: 'dashed'
            }
          }
        },
        yAxis: {
          type: 'category',
          data: [],
          axisLabel: {
            fontSize: 12,
            interval: 0
          },
          axisTick: {
            alignWithLabel: true
          }
        },
        series: [
          {
            name: '迭代',
            type: 'bar',
            stack: 'total',
            itemStyle: {
              color: '#5470c6',
              borderRadius: [4, 4, 0, 0]
            },
            data: [],
            barWidth: 25,
            emphasis: {
              focus: 'series'
            },
            label: {
              show: true,
              position: 'insideTop',
              formatter: '{b}',
              fontSize: 10,
              color: '#fff'
            }
          },
          {
            name: '需求',
            type: 'bar',
            stack: 'total',
            itemStyle: {
              color: '#91cc75',
              borderRadius: [2, 2, 0, 0]
            },
            data: [],
            barWidth: 15,
            emphasis: {
              focus: 'series'
            },
            label: {
              show: false
            }
          }
        ],
        toolbox: {
          feature: {
            saveAsImage: {
              pixelRatio: 2
            },
            dataZoom: {
              yAxisIndex: 'none'
            },
            restore: {}
          },
          top: 10,
          right: 10
        },
        dataZoom: [
          {
            type: 'inside',
            xAxisIndex: 0,
            start: 0,
            end: 100
          },
          {
            start: 0,
            end: 100,
            handleIcon: 'path://M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z',
            handleSize: '80%',
            handleStyle: {
              color: '#fff',
              shadowBlur: 3,
              shadowColor: 'rgba(0, 0, 0, 0.6)',
              shadowOffsetX: 2,
              shadowOffsetY: 2
            }
          }
        ]
      },
    
      // 迭代进度概览图表配置
      progressOverviewOption: {
        title: {
          text: '',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          },
          formatter: '{b}: {c}%'
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: [],
          axisLabel: {
            interval: 0,
            rotate: 45
          }
        },
        yAxis: {
          type: 'value',
          max: 100,
          axisLabel: {
            formatter: '{value}%'
          }
        },
        series: [
          {
            name: '进度',
            type: 'bar',
            data: [],
            itemStyle: {
              color: function(params) {
                const colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de'];
                return colors[params.dataIndex % colors.length];
              },
              borderRadius: [4, 4, 0, 0]
            },
            label: {
              show: true,
              position: 'top',
              formatter: '{c}%'
            }
          }
        ]
      },
      
      // 迭代与需求关联图表配置
      iterationRequirementOption: {
        title: {
          text: '',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          }
        },
        legend: {
          data: ['总需求数', '已完成需求数'],
          top: 10
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: [],
          axisLabel: {
            interval: 0,
            rotate: 45
          }
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '总需求数',
            type: 'bar',
            data: [],
            itemStyle: {
              color: '#5470c6'
            }
          },
          {
            name: '已完成需求数',
            type: 'bar',
            data: [],
            itemStyle: {
              color: '#91cc75'
            }
          }
        ]
      },
      
      // 迭代缺陷统计图表配置
      bugStatsOption: {
        title: {
          text: '',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          }
        },
        legend: {
          data: ['严重', '高', '中', '低'],
          top: 10
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: [],
          axisLabel: {
            interval: 0,
            rotate: 45
          }
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '严重',
            type: 'bar',
            stack: 'bug',
            data: [],
            itemStyle: {
              color: '#ee6666'
            }
          },
          {
            name: '高',
            type: 'bar',
            stack: 'bug',
            data: [],
            itemStyle: {
              color: '#fac858'
            }
          },
          {
            name: '中',
            type: 'bar',
            stack: 'bug',
            data: [],
            itemStyle: {
              color: '#73c0de'
            }
          },
          {
            name: '低',
            type: 'bar',
            stack: 'bug',
            data: [],
            itemStyle: {
              color: '#91cc75'
            }
          }
        ]
      },
      
        // 质量趋势图表配置
      qualityTrendOption: {
        title: {
          text: '',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          }
        },
        legend: {
          data: ['通过率', '缺陷密度'],
          top: 10
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: [],
          axisLabel: {
            interval: 0,
            rotate: 45
          }
        },
        yAxis: [
          {
            type: 'value',
            name: '通过率',
            max: 100,
            axisLabel: {
              formatter: '{value}%'
            }
          },
          {
            type: 'value',
            name: '缺陷密度',
            axisLabel: {
              formatter: '{value}'
            }
          }
        ],
        series: [
          {
            name: '通过率',
            type: 'line',
            data: [],
            smooth: true,
            itemStyle: {
              color: '#91cc75'
            },
            lineStyle: {
              width: 3
            },
            symbol: 'circle',
            symbolSize: 8,
            label: {
              show: true,
              position: 'top',
              formatter: '{c}%'
            }
          },
          {
            name: '缺陷密度',
            type: 'line',
            yAxisIndex: 1,
            data: [],
            smooth: true,
            itemStyle: {
              color: '#ee6666'
            },
            lineStyle: {
              width: 3
            },
            symbol: 'circle',
            symbolSize: 8,
            label: {
              show: true,
              position: 'top',
              formatter: '{c}'
            }
          }
        ]
      },
      
      // 创建/编辑迭代表单
      iterationDialogVisible: false,
      iterationDialogTitle: '创建迭代',
      iterationForm: {
        id: null,
        project_id: null,
        iteration_name: '',
        goal: '',
        version: '',
        start_date: '',
        end_date: '',
        status: 'planning',
        description: ''
      },
      iterationRules: {
        project_id: [{ required: true, message: '请选择项目', trigger: 'blur' }],
        iteration_name: [
          { required: true, message: '请输入迭代名称', trigger: 'blur' },
          { min: 2, max: 50, message: '迭代名称长度在 2 到 50 个字符', trigger: 'blur' }
        ],
        goal: [
          { required: true, message: '请输入迭代目标', trigger: 'blur' },
          { min: 5, max: 200, message: '迭代目标长度在 5 到 200 个字符', trigger: 'blur' }
        ],
        version: [
          { required: true, message: '请输入测试版本', trigger: 'blur' },
          { min: 1, max: 30, message: '测试版本长度在 1 到 30 个字符', trigger: 'blur' }
        ],
        start_date: [
          { required: true, message: '请选择开始日期', trigger: 'change' }
        ],
        end_date: [
          { required: true, message: '请选择结束日期', trigger: 'change' },
          {
            validator: (rule, value, callback) => {
              if (this.iterationForm.start_date && value < this.iterationForm.start_date) {
                callback(new Error('结束日期不能早于开始日期'))
              } else {
                callback()
              }
            },
            trigger: 'change'
          }
        ],
        status: [
          { required: true, message: '请选择状态', trigger: 'change' }
        ]
      },
      
      // 复制迭代表单
      copyDialogVisible: false,
      copyForm: {
        name: '',
        start_date: '',
        end_date: '',
        copy_test_plans: false
      },
      copyRules: {
        name: [{ required: true, message: '请输入新迭代名称', trigger: 'blur' }],
        start_date: [{ required: true, message: '请选择开始日期', trigger: 'blur' }],
        end_date: [{ required: true, message: '请选择结束日期', trigger: 'blur' }]
      },
      copiedIterationId: null,
      
      // 迭代详情
      detailDialogVisible: false,
      currentIteration: null,
      detailActiveTab: 'requirements' // 详情页默认标签
    }
  },
  watch: {
    searchQuery() {
      this.filterIterations()
    },
    statusFilter() {
      this.filterIterations()
    }
  },
  mounted() {
    this.initProjects()
  },
  methods: {
    // 初始化项目列表
    async initProjects() {
      try {
        const response = await getProjects()
        this.projects = response.data?.items || []
        console.log('Projects loaded:', this.projects)
        if (this.projects.length > 0) {
          this.selectedProjectId = this.projects[0].id
          console.log('Selected project ID:', this.selectedProjectId)
          this.loadIterations()
          this.loadVersionRequirements()
        }
      } catch (error) {
        console.error('获取项目列表失败:', error)
        this.$message.error('获取项目列表失败: ' + (error?.message || '未知错误'))
      }
    },
    
    // 加载迭代列表
    async loadIterations() {
      console.log('loadIterations called')
      if (!this.selectedProjectId) {
        console.log('No project selected, returning')
        return
      }
      
      const loadingInstance = ElLoading.service()
      try {
        const params = {
          page: this.currentPage,
          page_size: this.pageSize
        }
        console.log('Calling getProjectIterations with params:', params)
        const response = await getProjectIterations(this.selectedProjectId, params)
        
        console.log('getProjectIterations response:', response)
        
        // 检查API返回格式
        if (response && response.code === 200 && response.data) {
          console.log('API returned', response.data?.items?.length || 0, 'iterations, total:', response.data?.total || 0)
          this.iterations = response.data?.items || []
          this.total = response.data?.total || 0
          this.filterIterations()
          this.updateCharts()
        } else {
          console.error('Invalid API response format:', response)
          this.iterations = []
          this.total = 0
          this.filterIterations()
          this.updateCharts()
        }
      } catch (error) {
        console.error('Error in getProjectIterations:', error)
        this.$message.error('获取迭代列表失败: ' + (error?.message || '未知错误'))
        this.iterations = []
        this.total = 0
        this.filterIterations()
        this.updateCharts()
      } finally {
        loadingInstance.close()
      }
    },
    
    // 加载版本需求数据
    async loadVersionRequirements() {
      if (!this.selectedProjectId) return
      
      try {
        const response = await getProjectVersionRequirements(this.selectedProjectId)
        this.versionRequirements = response.data?.items || []
        this.updateGanttChart()
      } catch (error) {
        console.error('获取版本需求列表失败:', error)
        this.$message.error('获取版本需求列表失败: ' + (error?.message || '未知错误'))
        this.versionRequirements = []
      }
    },
    
    // 更新甘特图数据
    updateGanttChart() {
      // 只有在甘特图视图时才更新数据
      if (this.activeTab !== 'gantt') {
        return
      }
      
      // 确保iterations和versionRequirements是数组
      const iterations = Array.isArray(this.iterations) ? this.iterations : []
      const versionRequirements = Array.isArray(this.versionRequirements) ? this.versionRequirements : []
      
      // 准备甘特图数据
      const iterationData = []
      const requirementData = []
      const yAxisData = []
      
      // 处理迭代数据
      iterations.forEach(iteration => {
        if (iteration && typeof iteration === 'object') {
          yAxisData.push(iteration.iteration_name)
          
          // 计算迭代进度
          const iterationProgress = this.calculateRequirementProgress(iteration.requirement_stats)
          
          iterationData.push({
            name: iteration.iteration_name,
            value: [
              iteration.start_date,
              iteration.end_date,
              this.getStatusText(iteration.status),
              iterationProgress
            ]
          })
        }
      })
      
      // 处理需求数据，按所属迭代分组
      const requirementsByIteration = {}
      versionRequirements.forEach(requirement => {
        if (requirement && typeof requirement === 'object') {
          const iterationName = requirement.iteration_name || '未分配'
          if (!requirementsByIteration[iterationName]) {
            requirementsByIteration[iterationName] = []
          }
          requirementsByIteration[iterationName].push(requirement)
        }
      })
      
      // 将需求添加到对应迭代下
      iterations.forEach(iteration => {
        if (iteration && typeof iteration === 'object') {
          const iterationRequirements = requirementsByIteration[iteration.iteration_name] || []
          iterationRequirements.forEach(requirement => {
            if (requirement && typeof requirement === 'object') {
              // 需求状态转换
              const requirementStatus = this.getRequirementStatusText(requirement.status)
              
              requirementData.push({
                name: iteration.iteration_name,
                value: [
                  requirement.start_date || iteration.start_date,
                  requirement.end_date || iteration.end_date,
                  requirementStatus,
                  0 // 需求进度暂不计算
                ]
              })
            }
          })
        }
      })
      
      // 更新甘特图配置
      this.ganttChartOption.yAxis.data = yAxisData
      this.ganttChartOption.series[0].data = iterationData
      this.ganttChartOption.series[1].data = requirementData
    },
    
    // 计算概览数据
    calculateOverviewData() {
      // 确保iterations是数组
      const iterations = Array.isArray(this.iterations) ? this.iterations : []
      
      // 计算概览卡片数据
      this.activeIterationsCount = iterations.filter(iteration => iteration?.status === 'active').length
      this.completedIterationsCount = iterations.filter(iteration => iteration?.status === 'completed').length
      
      // 计算缺陷总数
      this.totalBugsCount = iterations.reduce((total, iteration) => {
        return total + (iteration?.bug_stats?.total || 0)
      }, 0)
      
      // 计算平均通过率
      const passRates = iterations.map(iteration => {
        if (iteration && typeof iteration === 'object') {
          return this.calculatePassRate(iteration.execution_stats)
        }
        return 0
      }).filter(rate => rate > 0)
      
      this.averagePassRate = passRates.length > 0 
        ? Math.round(passRates.reduce((sum, rate) => sum + rate, 0) / passRates.length)
        : 0
      
      // 计算看板数据
      this.plannedIterations = iterations.filter(iteration => iteration?.status === 'planning')
      this.activeIterations = iterations.filter(iteration => iteration?.status === 'active')
      this.completedIterations = iterations.filter(iteration => iteration?.status === 'completed')
    },
    
    // 更新所有图表数据
    updateCharts() {
      // 确保iterations是数组
      const iterations = Array.isArray(this.iterations) ? this.iterations : []
      
      // 计算概览数据
      this.calculateOverviewData()
      
      // 更新质量趋势图表
      const iterationNames = iterations.map(iteration => iteration?.iteration_name || '').filter(Boolean)
      const passRates = iterations.map(iteration => {
        if (iteration && typeof iteration === 'object') {
          return this.calculatePassRate(iteration.execution_stats)
        }
        return 0
      })
      
      // 计算缺陷密度（每个迭代的缺陷数）
      const bugDensity = iterations.map(iteration => {
        if (iteration && typeof iteration === 'object') {
          return iteration.bug_stats?.total || 0
        }
        return 0
      })
      
      this.qualityTrendOption.xAxis.data = iterationNames
      this.qualityTrendOption.series[0].data = passRates
      this.qualityTrendOption.series[1].data = bugDensity
      
      // 更新缺陷统计图表
      const criticalBugs = iterations.map(iteration => {
        if (iteration && typeof iteration === 'object') {
          return iteration.bug_stats?.critical || 0
        }
        return 0
      })
      
      const highBugs = iterations.map(iteration => {
        if (iteration && typeof iteration === 'object') {
          return iteration.bug_stats?.high || 0
        }
        return 0
      })
      
      const mediumBugs = iterations.map(iteration => {
        if (iteration && typeof iteration === 'object') {
          return iteration.bug_stats?.medium || 0
        }
        return 0
      })
      
      const lowBugs = iterations.map(iteration => {
        if (iteration && typeof iteration === 'object') {
          return iteration.bug_stats?.low || 0
        }
        return 0
      })
      
      this.bugStatsOption.xAxis.data = iterationNames
      this.bugStatsOption.series[0].data = criticalBugs
      this.bugStatsOption.series[1].data = highBugs
      this.bugStatsOption.series[2].data = mediumBugs
      this.bugStatsOption.series[3].data = lowBugs
    },
    
    // 处理标签切换
    handleTabChange(activeName) {
      // 直接使用activeName更新当前激活标签，避免v-model绑定延迟
      this.activeTab = activeName
      
      // 确保数据已加载，但使用setTimeout避免阻塞标签切换
      setTimeout(() => {
        // 无论当前迭代列表是否为空，都重新加载数据，确保列表视图有数据
        this.loadIterations()
        if (this.versionRequirements.length === 0) {
          this.loadVersionRequirements()
        }
      }, 0)
    },
    
    // 筛选迭代
    filterIterations() {
      console.log('filterIterations called, original iterations count:', this.iterations.length)
      
      // 先过滤掉无效数据，只保留有效的iteration对象
      let filtered = this.iterations.filter(iteration => iteration && typeof iteration === 'object')
      console.log('After filtering invalid data, count:', filtered.length)
      
      // 按名称搜索
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        console.log('Searching with query:', query)
        filtered = filtered.filter(iteration => 
          iteration.iteration_name?.toLowerCase().includes(query)
        )
        console.log('After name filter, count:', filtered.length)
      }
      
      // 按状态筛选
      if (this.statusFilter) {
        console.log('Filtering by status:', this.statusFilter)
        filtered = filtered.filter(iteration => 
          iteration.status === this.statusFilter
        )
        console.log('After status filter, count:', filtered.length)
      }
      
      this.iterationsData = filtered
      console.log('Final iterationsData count:', this.iterationsData.length)
      
      // 不要修改total，保持原始数据总数用于分页
    },
    
    // 处理项目切换
    handleProjectChange() {
      this.currentPage = 1
      this.loadIterations()
      this.loadVersionRequirements()
    },
    
    // 分页处理
    handleCurrentChange(page) {
      this.currentPage = page
      this.loadIterations()
    },
    handleSizeChange(size) {
      this.pageSize = size
      this.loadIterations()
    },
    
    // 显示创建迭代对话框
    showCreateIterationDialog() {
      this.iterationDialogTitle = '创建迭代'
      this.resetIterationForm()
      this.iterationForm.project_id = this.selectedProjectId
      this.iterationDialogVisible = true
    },
    
    // 编辑迭代
    editIteration(iteration) {
      if (!iteration) {
        this.$message.warning('无效的迭代数据')
        return
      }
      this.iterationDialogTitle = '编辑迭代'
      this.iterationForm = { ...iteration }
      this.iterationDialogVisible = true
    },
    
    // 重置迭代表单
    resetIterationForm() {
      if (this.$refs.iterationForm) {
        this.$refs.iterationForm.resetFields()
      }
      this.iterationForm = {
        id: null,
        project_id: this.selectedProjectId,
        iteration_name: '',
        goal: '',
        version: '',
        start_date: '',
        end_date: '',
        status: 'planning',
        description: ''
      }
    },
    
    // 关闭迭代对话框
    closeIterationDialog() {
      this.resetIterationForm()
      this.iterationDialogVisible = false
    },
    
    // 提交迭代表单
    async submitIterationForm() {
      this.$refs.iterationForm.validate(async (valid) => {
        if (valid) {
          // 验证日期
          if (new Date(this.iterationForm.start_date) > new Date(this.iterationForm.end_date)) {
            this.$message.warning('开始日期不能晚于结束日期')
            return
          }
          
          const loadingInstance = ElLoading.service()
          try {
            if (this.iterationForm.id) {
              // 更新迭代
              await updateIteration(this.iterationForm.id, this.iterationForm)
              this.$message.success('迭代更新成功')
            } else {
              // 创建迭代
              await createIteration(this.iterationForm)
              this.$message.success('迭代创建成功')
            }
            this.iterationDialogVisible = false
            this.loadIterations()
          } catch (error) {
            this.$message.error('操作失败: ' + (error.message || '未知错误'))
          } finally {
            loadingInstance.close()
          }
        }
      })
    },
    
    // 显示复制迭代对话框
    copyIterationDialog(iteration) {
      if (!iteration || !iteration.id) {
        this.$message.warning('无效的迭代数据')
        return
      }
      this.copiedIterationId = iteration.id
      this.copyForm = {
        name: `${iteration.iteration_name || '迭代'}_副本`,
        start_date: '',
        end_date: '',
        copy_test_plans: false
      }
      this.copyDialogVisible = true
    },
    
    // 提交复制表单
    async submitCopyForm() {
      this.$refs.copyForm.validate(async (valid) => {
        if (valid) {
          // 验证日期
          if (new Date(this.copyForm.start_date) > new Date(this.copyForm.end_date)) {
            this.$message.warning('开始日期不能晚于结束日期')
            return
          }
          
          const loadingInstance = ElLoading.service()
          try {
            await copyIteration(this.copiedIterationId, this.copyForm)
            this.$message.success('迭代复制成功')
            this.copyDialogVisible = false
            this.loadIterations()
          } catch (error) {
            this.$message.error('复制失败: ' + (error.message || '未知错误'))
          } finally {
            loadingInstance.close()
          }
        }
      })
    },
    
    // 删除迭代
    async deleteIteration(iteration) {
      if (!iteration || !iteration.id) {
        this.$message.warning('无效的迭代数据')
        return
      }
      this.$confirm(`确定要删除迭代「${iteration.iteration_name || '未知迭代'}」吗？`, '确认删除', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        const loadingInstance = ElLoading.service()
        try {
          await deleteIteration(iteration.id)
          this.$message.success('迭代删除成功')
          this.loadIterations()
        } catch (error) {
          this.$message.error('删除失败: ' + (error?.message || '未知错误'))
        } finally {
          loadingInstance.close()
        }
      })
    },
    
    // 显示迭代详情
    async showIterationDetail(iteration) {
      console.log('showIterationDetail called with:', iteration)
      if (!iteration || !iteration.id) {
        this.$message.warning('无效的迭代数据')
        return
      }
      
      const loadingInstance = ElLoading.service()
      try {
        console.log('Calling getIteration with id:', iteration.id)
        const response = await getIteration(iteration.id)
        console.log('getIteration response:', response)
        
        // 响应拦截器已经处理了错误情况，直接使用response
        this.currentIteration = response
        this.detailDialogVisible = true
        console.log('currentIteration set to:', this.currentIteration)
      } catch (error) {
        console.error('Error in getIteration:', error)
        // 错误信息已由响应拦截器处理，这里不需要重复显示
      } finally {
        loadingInstance.close()
      }
    },
    
    // 根据状态获取标签类型
    getTagTypeByStatus(status) {
      const typeMap = {
        planning: 'info',
        active: 'success',
        completed: 'warning',
        cancelled: 'danger'
      }
      return typeMap[status] || 'info'
    },
    
    // 获取状态文本
    getStatusText(status) {
      const statusMap = {
        planning: '计划中',
        active: '进行中',
        completed: '已完成',
        cancelled: '已取消'
      }
      return statusMap[status] || status
    },
    
    // 计算需求进度百分比
    calculateRequirementProgress(requirementStats) {
      if (!requirementStats || requirementStats.total === 0) {
        return 0
      }
      return Math.round((requirementStats.completed / requirementStats.total) * 100)
    },
    
    // 计算通过率
    calculatePassRate(executionStats) {
      if (!executionStats || executionStats.total === 0) {
        return 0
      }
      return Math.round((executionStats.pass / executionStats.total) * 100)
    },
    
    // 根据进度获取颜色
    getProgressColor(progress) {
      if (progress >= 90) {
        return '#67C23A'
      } else if (progress >= 60) {
        return '#E6A23C'
      } else {
        return '#F56C6C'
      }
    },
    
    // 根据通过率获取颜色
    getPassRateColor(passRate) {
      if (passRate >= 95) {
        return '#67C23A'
      } else if (passRate >= 80) {
        return '#E6A23C'
      } else {
        return '#F56C6C'
      }
    },
    
    // 处理详情对话框关闭
    handleDetailDialogClose() {
      this.detailActiveTab = 'requirements' // 重置标签页
      this.detailDialogVisible = false
    },
    
    // 生成迭代报告
    async generateIterationReport() {
      if (!this.currentIteration) return
      
      const loadingInstance = ElLoading.service()
      try {
        // 调用后端API生成报告
        const response = await getIterationStats(this.currentIteration.id)
        this.$message.success('迭代报告生成成功')
        
        // 这里可以添加下载报告的逻辑
        // 例如：window.open(response.data.report_url, '_blank')
      } catch (error) {
        console.error('生成迭代报告失败:', error)
        this.$message.error('生成迭代报告失败: ' + (error?.message || '未知错误'))
      } finally {
        loadingInstance.close()
      }
    },
    
    // 获取需求状态类型
    getRequirementStatusType(status) {
      const typeMap = {
        new: 'info',
        in_progress: 'success',
        completed: 'warning',
        cancelled: 'danger'
      }
      return typeMap[status] || 'info'
    },
    
    // 获取需求状态文本
    getRequirementStatusText(status) {
      const statusMap = {
        new: '未开始',
        in_progress: '进行中',
        completed: '已完成',
        cancelled: '已取消'
      }
      return statusMap[status] || status
    },
    
    // 获取任务状态类型
    getTaskStatusType(status) {
      const typeMap = {
        pending: 'info',
        running: 'success',
        completed: 'warning',
        paused: 'danger'
      }
      return typeMap[status] || 'info'
    },
    
    // 获取缺陷严重程度类型
    getBugSeverityType(severity) {
      const typeMap = {
        critical: 'danger',
        high: 'warning',
        medium: 'info',
        low: 'success'
      }
      return typeMap[severity] || 'info'
    },
    
    // 获取缺陷状态类型
    getBugStatusType(status) {
      const typeMap = {
        open: 'danger',
        in_progress: 'warning',
        resolved: 'info',
        closed: 'success',
        reopened: 'warning'
      }
      return typeMap[status] || 'info'
    },
    
    // 格式化日期
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString()
    }
  }
}
</script>

<style scoped>
.iteration-management {
  padding: 20px;
}

.management-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.management-header h2 {
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
}

.view-tabs {
  margin-bottom: 20px;
}

.list-card {
  margin-bottom: 20px;
}

.search-bar {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.iteration-detail {
  padding: 10px 0;
}

/* 甘特图容器样式 */
.gantt-container {
  height: 500px;
  width: 100%;
}

/* 进度文本样式 */
.progress-text {
  font-size: 12px;
  color: #606266;
  text-align: center;
  margin-top: 4px;
}

/* 缺陷统计样式 */
.bug-stats {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 12px;
}

.bug-item {
  display: inline-block;
  padding: 2px 4px;
  border-radius: 3px;
  color: #fff;
}

.bug-item.critical {
  background-color: #F56C6C;
}

.bug-item.high {
  background-color: #E6A23C;
}

.bug-item.medium {
  background-color: #909399;
}

.bug-item.low {
  background-color: #67C23A;
}

/* 迭代详情样式 */
.iteration-detail {
  padding: 10px 0;
}

.basic-info {
  margin-bottom: 20px;
}

.stats-cards {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.stat-card {
  flex: 1;
  min-width: 200px;
}

.stat-content {
  text-align: center;
}

.stat-title {
  font-size: 14px;
  color: #606266;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 10px;
}

.stat-detail {
  display: flex;
  justify-content: center;
  gap: 15px;
  font-size: 12px;
  color: #606266;
  margin-bottom: 5px;
  flex-wrap: wrap;
}

.stat-status {
  display: flex;
  justify-content: center;
  gap: 15px;
  font-size: 12px;
  color: #606266;
  flex-wrap: wrap;
}

.stat-item {
  display: inline-block;
}

.stat-item.pass {
  color: #67C23A;
}

.stat-item.fail {
  color: #F56C6C;
}

.stat-item.blocked {
  color: #E6A23C;
}

.stat-item.critical {
  color: #F56C6C;
}

.stat-item.high {
  color: #E6A23C;
}

.stat-item.medium {
  color: #909399;
}

.stat-item.low {
  color: #67C23A;
}

.stat-item.open {
  color: #F56C6C;
}

.stat-item.resolved {
  color: #E6A23C;
}

.stat-item.closed {
  color: #67C23A;
}

.detail-tabs {
  margin-top: 20px;
}

/* 图表容器样式 */
.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

/* 图表卡片样式 */
.chart-card {
  margin-bottom: 20px;
}

/* 图表卡片头部样式 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 图表包装器样式 */
.chart-wrapper {
  height: 300px;
  width: 100%;
}

/* 概览卡片样式 */
.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.overview-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.overview-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.15);
}

.overview-content {
  text-align: center;
  padding: 20px 0;
}

.overview-title {
  font-size: 14px;
  color: #606266;
  margin-bottom: 10px;
}

.overview-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

/* 看板样式 */
.kanban-container {
  display: flex;
  gap: 20px;
  overflow-x: auto;
  padding: 10px 0;
}

.kanban-column {
  flex: 1;
  min-width: 300px;
  background-color: #f5f7fa;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.kanban-column-header {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #303133;
  text-align: center;
  padding-bottom: 10px;
  border-bottom: 2px solid #e6e6e6;
}

.kanban-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.kanban-item {
  background-color: #fff;
  border-radius: 6px;
  padding: 15px;
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  cursor: pointer;
}

.kanban-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.12);
}

.kanban-item.planning {
  border-left: 4px solid #909399;
}

.kanban-item.active {
  border-left: 4px solid #67c23a;
}

.kanban-item.completed {
  border-left: 4px solid #e6a23c;
}

.kanban-item-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 10px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.kanban-item-progress {
  margin-bottom: 10px;
}

.kanban-item-meta {
  display: flex;
  flex-direction: column;
  gap: 5px;
  font-size: 12px;
  color: #606266;
}

.kanban-item-date {
  display: inline-block;
}

.kanban-item-pass-rate {
  display: inline-block;
  margin-top: 5px;
  color: #67c23a;
  font-weight: bold;
}

/* 通过率样式 */
.pass-rate {
  font-size: 14px;
  font-weight: bold;
  color: #67c23a;
  text-align: center;
}

/* 缺陷数样式 */
.bug-count {
  font-size: 14px;
  font-weight: bold;
  color: #f56c6c;
  text-align: center;
}

/* 部分卡片样式 */
.section-card {
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

/* 操作按钮样式 */
.operation-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
  align-items: center;
}
</style>