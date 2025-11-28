<template>
  <div class="iteration-management">
    <div class="management-header">
      <h2>迭代管理</h2>
      <div class="header-actions">
        <el-select v-model="selectedProjectId" placeholder="选择项目" style="width: 200px; margin-right: 15px;" @change="handleProjectChange">
          <el-option
            v-for="project in projects"
            :key="project.id"
            :label="project.name"
            :value="project.id"
          ></el-option>
        </el-select>
        <el-button type="primary" @click="showCreateIterationDialog">
          <i class="el-icon-plus"></i> 创建迭代
        </el-button>
      </div>
    </div>

    <!-- 视图切换 -->
    <div class="view-tabs">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="甘特图" name="gantt"></el-tab-pane>
        <el-tab-pane label="列表视图" name="list"></el-tab-pane>
      </el-tabs>
    </div>

    <!-- 甘特图视图 -->
    <el-card v-if="activeTab === 'gantt'" class="list-card">
      <div class="gantt-container">
        <v-chart :option="ganttChartOption" autoresize />
      </div>
    </el-card>

    <!-- 列表视图 -->
    <el-card v-else class="list-card">
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索迭代名称"
          prefix-icon="el-icon-search"
          style="width: 300px; margin-right: 10px;"
        ></el-input>
        <el-select v-model="statusFilter" placeholder="状态筛选" style="width: 150px; margin-right: 10px;">
          <el-option label="全部状态" value=""></el-option>
          <el-option label="计划中" value="planning"></el-option>
          <el-option label="进行中" value="active"></el-option>
          <el-option label="已完成" value="completed"></el-option>
          <el-option label="已取消" value="cancelled"></el-option>
        </el-select>
        <el-button type="primary" @click="loadIterations">查询</el-button>
      </div>

      <el-table :data="iterationsData" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80"></el-table-column>
        <el-table-column prop="name" label="迭代名称">
          <template slot-scope="scope">
            <a href="#" @click.stop="showIterationDetail(scope.row)">{{ scope.row.name }}</a>
          </template>
        </el-table-column>
        <el-table-column prop="project_name" label="所属项目" width="180"></el-table-column>
        <el-table-column prop="target" label="迭代目标" show-overflow-tooltip></el-table-column>
        <el-table-column prop="version" label="测试版本" width="120"></el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template slot-scope="scope">
            <el-tag
              :type="getTagTypeByStatus(scope.row.status)"
              :effect="'light'"
            >
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="start_date" label="开始日期" width="120"></el-table-column>
        <el-table-column prop="end_date" label="结束日期" width="120"></el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template slot-scope="scope">
            <el-button size="small" type="primary" icon="el-icon-edit" @click="editIteration(scope.row)">编辑</el-button>
            <el-button size="small" type="info" icon="el-icon-document-copy" @click="copyIterationDialog(scope.row)">复制</el-button>
            <el-button size="small" type="danger" icon="el-icon-delete" @click="deleteIteration(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          background
          layout="prev, pager, next, jumper"
          :total="total"
          :page-size="pageSize"
          :current-page="currentPage"
          @current-change="handleCurrentChange"
          @size-change="handleSizeChange"
        ></el-pagination>
      </div>
    </el-card>

    <!-- 创建/编辑迭代对话框 -->
    <el-dialog
      :title="iterationDialogTitle"
      :visible.sync="iterationDialogVisible"
      width="600px"
      @close="resetIterationForm"
    >
      <el-form ref="iterationForm" :model="iterationForm" :rules="iterationRules" label-width="120px">
        <el-form-item label="项目" prop="project_id">
          <el-select v-model="iterationForm.project_id" placeholder="选择项目" disabled>
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="迭代名称" prop="name">
          <el-input v-model="iterationForm.name" placeholder="请输入迭代名称"></el-input>
        </el-form-item>
        <el-form-item label="迭代目标" prop="target">
          <el-input v-model="iterationForm.target" type="textarea" placeholder="请输入迭代目标" :rows="3"></el-input>
        </el-form-item>
        <el-form-item label="测试版本" prop="version">
          <el-input v-model="iterationForm.version" placeholder="请输入测试版本"></el-input>
        </el-form-item>
        <el-form-item label="开始日期" prop="start_date">
          <el-date-picker
            v-model="iterationForm.start_date"
            type="date"
            placeholder="选择开始日期"
            style="width: 100%;"
          ></el-date-picker>
        </el-form-item>
        <el-form-item label="结束日期" prop="end_date">
          <el-date-picker
            v-model="iterationForm.end_date"
            type="date"
            placeholder="选择结束日期"
            style="width: 100%;"
          ></el-date-picker>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="iterationForm.status" placeholder="选择状态">
            <el-option label="计划中" value="planning"></el-option>
            <el-option label="进行中" value="active"></el-option>
            <el-option label="已完成" value="completed"></el-option>
            <el-option label="已取消" value="cancelled"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="备注" prop="description">
          <el-input v-model="iterationForm.description" type="textarea" placeholder="请输入备注信息" :rows="3"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="closeIterationDialog">取消</el-button>
        <el-button type="primary" @click="submitIterationForm">确定</el-button>
      </div>
    </el-dialog>

    <!-- 复制迭代对话框 -->
    <el-dialog
      title="复制迭代"
      :visible.sync="copyDialogVisible"
      width="500px"
    >
      <el-form ref="copyForm" :model="copyForm" :rules="copyRules" label-width="120px">
        <el-form-item label="新迭代名称" prop="name">
          <el-input v-model="copyForm.name" placeholder="请输入新迭代名称"></el-input>
        </el-form-item>
        <el-form-item label="开始日期" prop="start_date">
          <el-date-picker
            v-model="copyForm.start_date"
            type="date"
            placeholder="选择开始日期"
            style="width: 100%;"
          ></el-date-picker>
        </el-form-item>
        <el-form-item label="结束日期" prop="end_date">
          <el-date-picker
            v-model="copyForm.end_date"
            type="date"
            placeholder="选择结束日期"
            style="width: 100%;"
          ></el-date-picker>
        </el-form-item>
        <el-form-item label="复制测试计划">
          <el-switch v-model="copyForm.copy_test_plans"></el-switch>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="copyDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCopyForm">确定</el-button>
      </div>
    </el-dialog>

    <!-- 迭代详情对话框 -->
    <el-dialog
      title="迭代详情"
      :visible.sync="detailDialogVisible"
      width="700px"
    >
      <div v-if="currentIteration" class="iteration-detail">
        <el-descriptions border column="1" label-align="left">
          <el-descriptions-item label="迭代名称">{{ currentIteration.name }}</el-descriptions-item>
          <el-descriptions-item label="所属项目">{{ currentIteration.project_name }}</el-descriptions-item>
          <el-descriptions-item label="迭代目标">{{ currentIteration.target }}</el-descriptions-item>
          <el-descriptions-item label="测试版本">{{ currentIteration.version }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getTagTypeByStatus(currentIteration.status)">
              {{ getStatusText(currentIteration.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="开始日期">{{ currentIteration.start_date }}</el-descriptions-item>
          <el-descriptions-item label="结束日期">{{ currentIteration.end_date }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(currentIteration.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="创建人">{{ currentIteration.created_by_name }}</el-descriptions-item>
          <el-descriptions-item label="备注">{{ currentIteration.description || '-' }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <div slot="footer" class="dialog-footer">
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted, watch } from 'vue'
import { getProjectIterations, createIteration, updateIteration, deleteIteration, copyIteration, getIteration } from '@/api/iteration'
import { getProjects, getProjectVersionRequirements } from '@/api/project'
import dayjs from 'dayjs'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import VChart from 'vue-echarts'

// 注册必要的组件
use([CanvasRenderer, PieChart, BarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

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
      
      // 甘特图配置
      ganttChartOption: {
        title: {
          text: '',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          formatter: function(params) {
            let result = params[0].name + '<br/>';
            params.forEach(param => {
              const start = dayjs(param.data[0]).format('YYYY-MM-DD HH:mm');
              const end = dayjs(param.data[1]).format('YYYY-MM-DD HH:mm');
              result += `${param.marker} ${param.seriesName}: ${start} - ${end}<br/>`;
            });
            return result;
          }
        },
        legend: {
          data: ['迭代', '需求'],
          top: 10
        },
        grid: {
          left: '10%',
          right: '10%',
          bottom: '15%',
          top: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'time',
          axisLabel: {
            formatter: '{yyyy}-{MM}-{dd}'
          }
        },
        yAxis: {
          type: 'category',
          data: [],
          axisLabel: {
            fontSize: 12
          }
        },
        series: [
          {
            name: '迭代',
            type: 'bar',
            stack: 'total',
            itemStyle: {
              color: '#5470c6'
            },
            data: [],
            barWidth: 20
          },
          {
            name: '需求',
            type: 'bar',
            stack: 'total',
            itemStyle: {
              color: '#91cc75'
            },
            data: [],
            barWidth: 10
          }
        ]
      },
      
      // 创建/编辑迭代表单
      iterationDialogVisible: false,
      iterationDialogTitle: '创建迭代',
      iterationForm: {
        id: null,
        project_id: null,
        name: '',
        target: '',
        version: '',
        start_date: '',
        end_date: '',
        status: 'planning',
        description: ''
      },
      iterationRules: {
        project_id: [{ required: true, message: '请选择项目', trigger: 'blur' }],
        name: [{ required: true, message: '请输入迭代名称', trigger: 'blur' }],
        start_date: [{ required: true, message: '请选择开始日期', trigger: 'blur' }],
        end_date: [{ required: true, message: '请选择结束日期', trigger: 'blur' }]
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
      currentIteration: null
    }
  },
  mounted() {
    this.initProjects()
  },
  watch: {
    searchQuery() {
      this.filterIterations()
    },
    statusFilter() {
      this.filterIterations()
    }
  },
  methods: {
    // 初始化项目列表
    async initProjects() {
      try {
        const response = await getProjects()
        this.projects = response.data.items || []
        if (this.projects.length > 0) {
          this.selectedProjectId = this.projects[0].id
          this.loadIterations()
          this.loadVersionRequirements()
        }
      } catch (error) {
        this.$message.error('获取项目列表失败: ' + (error.message || '未知错误'))
      }
    },
    
    // 加载迭代列表
    async loadIterations() {
      if (!this.selectedProjectId) return
      
      try {
        this.$loading.show()
        const params = {
          page: this.currentPage,
          page_size: this.pageSize
        }
        const response = await getProjectIterations(this.selectedProjectId, params)
        this.iterations = response.data.items || []
        this.total = response.data.total || 0
        this.filterIterations()
        this.updateGanttChart()
      } catch (error) {
        this.$message.error('获取迭代列表失败: ' + (error.message || '未知错误'))
      } finally {
        this.$loading.hide()
      }
    },
    
    // 加载版本需求数据
    async loadVersionRequirements() {
      if (!this.selectedProjectId) return
      
      try {
        const response = await getProjectVersionRequirements(this.selectedProjectId)
        this.versionRequirements = response.version_requirements || []
        this.updateGanttChart()
      } catch (error) {
        console.error('获取版本需求列表失败:', error)
        this.$message.error('获取版本需求列表失败: ' + (error.message || '未知错误'))
        this.versionRequirements = []
      }
    },
    
    // 更新甘特图数据
    updateGanttChart() {
      // 准备甘特图数据
      const iterationData = []
      const requirementData = []
      const yAxisData = []
      
      // 处理迭代数据
      this.iterations.forEach(iteration => {
        yAxisData.push(iteration.name)
        iterationData.push({
          name: iteration.name,
          value: [
            iteration.start_date,
            iteration.end_date
          ]
        })
      })
      
      // 处理需求数据，按所属迭代分组
      const requirementsByIteration = {}
      this.versionRequirements.forEach(requirement => {
        const iterationName = requirement.iteration_name || '未分配'
        if (!requirementsByIteration[iterationName]) {
          requirementsByIteration[iterationName] = []
        }
        requirementsByIteration[iterationName].push(requirement)
      })
      
      // 将需求添加到对应迭代下
      this.iterations.forEach(iteration => {
        const iterationRequirements = requirementsByIteration[iteration.name] || []
        iterationRequirements.forEach(requirement => {
          requirementData.push({
            name: iteration.name,
            value: [
              requirement.start_date || iteration.start_date,
              requirement.end_date || iteration.end_date
            ]
          })
        })
      })
      
      // 更新甘特图配置
      this.ganttChartOption.yAxis.data = yAxisData
      this.ganttChartOption.series[0].data = iterationData
      this.ganttChartOption.series[1].data = requirementData
    },
    
    // 处理标签切换
    handleTabChange(tab) {
      if (tab === 'gantt') {
        // 确保数据已加载
        if (this.iterations.length === 0) {
          this.loadIterations()
        }
        if (this.versionRequirements.length === 0) {
          this.loadVersionRequirements()
        }
      }
    },
    
    // 筛选迭代
    filterIterations() {
      let filtered = [...this.iterations]
      
      // 按名称搜索
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(iteration => 
          iteration.name.toLowerCase().includes(query)
        )
      }
      
      // 按状态筛选
      if (this.statusFilter) {
        filtered = filtered.filter(iteration => 
          iteration.status === this.statusFilter
        )
      }
      
      this.iterationsData = filtered
    },
    
    // 处理项目切换
    handleProjectChange() {
      this.currentPage = 1
      this.loadIterations()
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
        name: '',
        target: '',
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
          try {
            // 验证日期
            if (new Date(this.iterationForm.start_date) > new Date(this.iterationForm.end_date)) {
              this.$message.warning('开始日期不能晚于结束日期')
              return
            }
            
            this.$loading.show()
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
            this.$loading.hide()
          }
        }
      })
    },
    
    // 显示复制迭代对话框
    copyIterationDialog(iteration) {
      this.copiedIterationId = iteration.id
      this.copyForm = {
        name: `${iteration.name}_副本`,
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
          try {
            // 验证日期
            if (new Date(this.copyForm.start_date) > new Date(this.copyForm.end_date)) {
              this.$message.warning('开始日期不能晚于结束日期')
              return
            }
            
            this.$loading.show()
            await copyIteration(this.copiedIterationId, this.copyForm)
            this.$message.success('迭代复制成功')
            this.copyDialogVisible = false
            this.loadIterations()
          } catch (error) {
            this.$message.error('复制失败: ' + (error.message || '未知错误'))
          } finally {
            this.$loading.hide()
          }
        }
      })
    },
    
    // 删除迭代
    async deleteIteration(iteration) {
      this.$confirm(`确定要删除迭代「${iteration.name}」吗？`, '确认删除', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          this.$loading.show()
          await deleteIteration(iteration.id)
          this.$message.success('迭代删除成功')
          this.loadIterations()
        } catch (error) {
          this.$message.error('删除失败: ' + (error.message || '未知错误'))
        } finally {
          this.$loading.hide()
        }
      })
    },
    
    // 显示迭代详情
    async showIterationDetail(iteration) {
      try {
        this.$loading.show()
        const response = await getIteration(iteration.id)
        this.currentIteration = response.data
        this.detailDialogVisible = true
      } catch (error) {
        this.$message.error('获取迭代详情失败: ' + (error.message || '未知错误'))
      } finally {
        this.$loading.hide()
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
</style>