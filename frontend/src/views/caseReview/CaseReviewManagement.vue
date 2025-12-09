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
            
            <el-table 
              v-loading="loading.myTasks"
              :data="myTasks"
              style="width: 100%"
              row-key="id"
              @row-click="handleTaskClick"
              header-align="center"
              align="center"
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
                      :color="progressColor(scope.row.review_progress.progress_percent)"
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
                    @click.stop="scope.row.status === 'completed' ? handleViewDetail(scope.row) : handleReview(scope.row)"
                  >
                    {{ scope.row.status === 'completed' ? '查看评审' : '开始评审' }}
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
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
            
            <el-table 
              v-loading="loading.myInitiated"
              :data="myInitiated"
              style="width: 100%"
              row-key="id"
              @row-click="handleTaskClick"
              header-align="center"
              align="center"
            >
              <el-table-column
                prop="project_name"
                label="所属项目"
                width="200"
              />
              <el-table-column
                prop="iteration_name"
                label="所属迭代"
                width="180"
              />
              <el-table-column
                prop="requirement_name"
                label="关联需求"
                width="200"
              />
              <el-table-column
                prop="suite_name"
                label="用例集名称"
                min-width="200"
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
                      :color="progressColor(scope.row.review_progress.progress_percent)"
                    />
                  </div>
                </template>
              </el-table-column>
              <el-table-column
                prop="status"
                label="评审状态"
                width="180"
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
              >
                <template #default="scope">
                  {{ formatDate(scope.row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column
                label="操作"
                width="160"
                fixed="right"
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
      </el-tabs>
    </el-card>
    
    <!-- 评审详情弹窗 -->
    <el-dialog
      v-model="reviewDialogVisible"
      :title="reviewDialogTitle"
      :width="'90%'"
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
              {{ currentReviewTask?.suite?.suite_name || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="发起人">
              {{ currentReviewTask?.initiator_name || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="评审人">
              {{ currentReviewTask?.reviewer_name || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ formatDate(currentReviewTask?.created_at) || '-' }}
            </el-descriptions-item>
            <el-descriptions-item
              label="状态"
              :span="2"
            >
              <el-tag :type="getStatusTagType(currentReviewTask?.status)">
                {{ getStatusText(currentReviewTask?.status) }}
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
            row-key="case_id"
            :row-style="{ height: 'auto' }"
            :cell-style="{ 'white-space': 'pre-wrap', 'word-break': 'break-word', 'line-height': '1.5' }"
          >
          <el-table-column
              prop="test_case.case_number"
              label="用例编号"
              min-width="130"
            >
              <template #default="scope">
                {{ scope.row.test_case.case_number || '-' }}
              </template>
            </el-table-column>
          <el-table-column
              prop="test_case.case_name"
              label="用例名称"
              min-width="140"
            >
              <template #default="scope">
                {{ scope.row.test_case.case_name || '-' }}
              </template>
            </el-table-column>
            <el-table-column
              prop="test_case.priority"
              label="优先级"
              width="90"
            >
              <template #default="scope">
                <el-tag 
                  :type="getPriorityTagType(scope.row.test_case.priority || 'P3')"
                  size="small"
                >
                  {{ scope.row.test_case.priority || '-' }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column
              prop="test_case.test_data"
              label="测试数据"
              min-width="120"
            >
              <template #default="scope">
                <div class="text-with-newlines">{{ scope.row.test_case.test_data || '-' }}</div>
              </template>
            </el-table-column>
            <el-table-column
              prop="test_case.preconditions"
              label="前置条件"
              min-width="160"
            >
              <template #default="scope">
                <div class="text-with-newlines">{{ scope.row.test_case.preconditions || '-' }}</div>
              </template>
            </el-table-column>
            <el-table-column
              prop="test_case.steps"
              label="测试步骤"
              min-width="170"
            >
              <template #default="scope">
                <div class="text-with-newlines">{{ scope.row.test_case.steps || '-' }}</div>
              </template>
            </el-table-column>
            <el-table-column
              prop="test_case.expected_result"
              label="预期结果"
              min-width="160"
            >
              <template #default="scope">
                <div class="text-with-newlines">{{ scope.row.test_case.expected_result || '-' }}</div>
              </template>
            </el-table-column>
            <el-table-column
              prop="test_case.actual_result"
              label="实际结果"
              min-width="160"
            >
              <template #default="scope">
                <div class="text-with-newlines">{{ scope.row.test_case.actual_result || '-' }}</div>
              </template>
            </el-table-column>
            <el-table-column
              prop="review_status"
              label="评审状态"
              width="100"
            >
              <template #default="scope">
                <!-- 如果是评审人，显示可编辑的单选按钮组 -->
                <el-radio-group 
                  v-if="isReviewer"
                  v-model="scope.row.review_status" 
                  size="small"
                  @change="handleReviewStatusChange(scope.row)"
                >
                  <el-radio-button label="pending">待审核</el-radio-button>
                  <el-radio-button label="approved">已通过</el-radio-button>
                  <el-radio-button label="rejected">已拒绝</el-radio-button>
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
              min-width="200"
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
                  @change="handleCommentsChange(scope.row)"
                />
                <!-- 如果是发起人或其他用户，显示只读的评审意见 -->
                <div 
                  v-else
                  class="read-only-comments"
                >
                  {{ scope.row.comments || '-' }}
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
                {{ formatDate(scope.row.updated_at) || '-' }}
              </template>
            </el-table-column>
          </el-table>
        </div>
        
        <!-- 整体评审意见 -->
        <div
          v-if="isReviewer || isInitiator"
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
          <!-- 如果是发起人，显示只读的评审意见 -->
          <div 
            v-else
            class="read-only-comments"
          >
            {{ overallComments || '暂无整体评审意见' }}
          </div>
        </div>
      </div>
      
      <!-- 对话框底部按钮 -->
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="reviewDialogVisible = false">关闭</el-button>
          <!-- 如果评审未完成，显示完成评审按钮 -->
          <el-button 
            v-if="isReviewer && currentReviewTask && currentReviewTask.status !== 'completed'" 
            type="primary"
            :disabled="!canCompleteReview"
            @click="handleCompleteReview"
          >
            完成评审
          </el-button>
          <!-- 如果评审已完成，显示重新评审按钮 -->
          <el-button 
            v-else-if="isReviewer && currentReviewTask && currentReviewTask.status === 'completed'" 
            type="warning"
            @click="handleReinitiateReview"
          >
            重新评审
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as reviewApi from '@/api/reviewTask'
import { useUserStore } from '@/stores/user'



// 状态管理
const userStore = useUserStore()
const activeTab = ref('my-tasks')
const loading = ref({
  myTasks: false,
  myInitiated: false,
  caseReviews: false,
  updateReview: false
})

// 数据
const myTasks = ref([])
const myInitiated = ref([])
const caseReviews = ref([])
const currentReviewTask = ref(null)
const reviewDialogVisible = ref(false)
const reviewDialogTitle = ref('')
const overallComments = ref('')

// 计算属性
const isReviewer = computed(() => {
  // 根据当前登录用户和评审任务的评审人信息判断是否为评审人
  if (!userStore.userInfo || !currentReviewTask.value) return false
  // 确保类型一致，转换为字符串进行比较
  const currentUserId = String(userStore.userInfo.id)
  const reviewerId = String(currentReviewTask.value.reviewer_id)
  return currentUserId === reviewerId
})

const isInitiator = computed(() => {
  // 根据当前登录用户和评审任务的发起人信息判断是否为发起人
  if (!userStore.userInfo || !currentReviewTask.value) return false
  // 确保类型一致，转换为字符串进行比较
  const currentUserId = String(userStore.userInfo.id)
  const initiatorId = String(currentReviewTask.value.initiator_id)
  return currentUserId === initiatorId
})

const canCompleteReview = computed(() => {
  // 如果没有用例，允许完成评审
  if (!caseReviews.value.length) return true
  // 检查是否所有用例都已评审
  return caseReviews.value.every(cr => cr.review_status !== 'pending')
})

// 方法
// 获取我的评审任务
const getMyTasks = async () => {
  loading.value.myTasks = true
  try {
    const response = await reviewApi.getMyReviewTasks()
    myTasks.value = response.data.items || []
  } catch (error) {
    ElMessage.error('获取我的评审任务失败')
  } finally {
    loading.value.myTasks = false
  }
}

// 获取我发起的评审
const getMyInitiated = async () => {
  loading.value.myInitiated = true
  try {
    const response = await reviewApi.getMyInitiatedReviews()
    myInitiated.value = response.data.items || []
  } catch (error) {
    ElMessage.error('获取我发起的评审失败')
  } finally {
    loading.value.myInitiated = false
  }
}

// 获取评审任务详情
const getReviewTaskDetail = async (taskId) => {
  loading.value.caseReviews = true
  try {
    const response = await reviewApi.getReviewTask(taskId)
    currentReviewTask.value = response.data
    
    // 获取用例评审详情
    const caseResponse = await reviewApi.getCaseReviews(taskId)
    caseReviews.value = caseResponse.data.case_reviews || []
    
    // 获取整体评审意见
    overallComments.value = response.data.overall_comments || ''
  } catch (error) {
    ElMessage.error('获取评审任务详情失败')
  } finally {
    loading.value.caseReviews = false
  }
}

// 处理任务点击
const handleTaskClick = (row) => {
  reviewDialogTitle.value = '评审详情'
  reviewDialogVisible.value = true
  getReviewTaskDetail(row.id)
}

// 处理开始评审
const handleReview = (row) => {
  reviewDialogTitle.value = '开始评审'
  reviewDialogVisible.value = true
  getReviewTaskDetail(row.id)
}

// 处理查看详情
const handleViewDetail = (row) => {
  reviewDialogTitle.value = '评审详情'
  reviewDialogVisible.value = true
  getReviewTaskDetail(row.id)
}



// 处理评审状态变化
const handleReviewStatusChange = async (row) => {
  loading.value.updateReview = true
  try {
    const response = await reviewApi.updateCaseReview(
      row.review_task_id,
      row.case_id,
      {
        review_status: row.review_status,
        comments: row.comments || ''
      }
    )
    
    // 更新本地数据，保留原来的test_case信息
    const index = caseReviews.value.findIndex(cr => cr.id === row.id)
    if (index > -1) {
      // 合并数据，保留原来的test_case信息
      caseReviews.value[index] = {
        ...response.data,
        test_case: caseReviews.value[index].test_case
      }
    }
    
    ElMessage.success('评审状态更新成功')
    
    // 刷新任务列表
    if (activeTab.value === 'my-tasks') {
      getMyTasks()
    } else {
      getMyInitiated()
    }
  } catch (error) {
    ElMessage.error('更新评审状态失败')
  } finally {
    loading.value.updateReview = false
  }
}

// 处理评审意见变化
const handleCommentsChange = async (row) => {
  loading.value.updateReview = true
  try {
    // 确保review_status有值
    const status = row.review_status || 'pending'
    const response = await reviewApi.updateCaseReview(
      row.review_task_id,
      row.case_id,
      {
        review_status: status,
        comments: row.comments || ''
      }
    )
    
    // 更新本地数据，保留原来的test_case信息
    const index = caseReviews.value.findIndex(cr => cr.id === row.id)
    if (index > -1) {
      // 合并数据，保留原来的test_case信息
      caseReviews.value[index] = {
        ...response.data,
        test_case: caseReviews.value[index].test_case
      }
    }
    
    ElMessage.success('评审意见更新成功')
  } catch (error) {
    console.error('更新评审意见失败:', error)
    ElMessage.error('更新评审意见失败: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value.updateReview = false
  }
}

// 处理完成评审
const handleCompleteReview = async () => {
  if (!currentReviewTask.value) return
  
  await ElMessageBox.confirm('确定要完成评审并通知发起人吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
  
  loading.value.updateReview = true
  try {
    await reviewApi.completeReview(currentReviewTask.value.id, {
      overall_comments: overallComments.value
    })
    
    ElMessage.success('评审完成成功')
    reviewDialogVisible.value = false
    
    // 刷新列表
    if (activeTab.value === 'my-tasks') {
      getMyTasks()
    } else {
      getMyInitiated()
    }
  } catch (error) {
    ElMessage.error('完成评审失败')
  } finally {
    loading.value.updateReview = false
  }
}

// 处理重新评审
const handleReinitiateReview = async () => {
  if (!currentReviewTask.value) return
  
  await ElMessageBox.confirm('确定重新发起评审吗？将重置评审任务状态，但保留用例评审结果。', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
  
  loading.value.updateReview = true
  try {
    await reviewApi.reinitiateReview(currentReviewTask.value.id)
    
    ElMessage.success('重新发起评审成功')
    
    // 重新获取评审任务详情，更新本地数据
    await getReviewTaskDetail(currentReviewTask.value.id)
    
    // 刷新列表
    if (activeTab.value === 'my-tasks') {
      getMyTasks()
    } else {
      getMyInitiated()
    }
  } catch (error) {
    ElMessage.error('重新发起评审失败')
  } finally {
    loading.value.updateReview = false
  }
}

// 处理对话框关闭
const handleDialogClose = () => {
  // 重置数据
  currentReviewTask.value = null
  caseReviews.value = []
  overallComments.value = ''
  reviewDialogVisible.value = false
}

// 辅助方法
const formatDate = (time) => {
  if (!time) return '-'
  try {
    // 处理各种格式的时间字符串，确保浏览器能够正确解析
    let date
    if (typeof time === 'string') {
      // 如果已经是YYYY-MM-DD HH:mm:ss格式，直接返回
      if (/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/.test(time)) {
        return time
      }
      
      // 尝试直接解析
      date = new Date(time)
      // 如果解析失败，尝试处理不同的日期格式
      if (isNaN(date.getTime())) {
        // 处理后端返回的 '%Y-%m-%d %H:%M:%S' 格式
        const parts = time.split(/[- :]/)
        if (parts.length >= 6) {
          date = new Date(parts[0], parts[1]-1, parts[2], parts[3], parts[4], parts[5])
        } else {
          return '-'
        }
      }
    } else {
      date = new Date(time)
    }
    if (isNaN(date.getTime())) {
      return '-'
    }
    
    // 手动构建固定格式的时间字符串：YYYY-MM-DD HH:mm:ss
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    const seconds = String(date.getSeconds()).padStart(2, '0')
    
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
  } catch (error) {
    console.error('时间格式化失败:', error)
    return '-'
  }
}

const getStatusText = (status) => {
  const statusMap = {
    pending: '待处理',
    in_review: '评审中',
    completed: '已完成'
  }
  return statusMap[status] || status
}

const getStatusTagType = (status) => {
  const typeMap = {
    pending: 'info',
    in_review: 'primary',
    completed: 'success'
  }
  return typeMap[status] || 'info'
}

const getCaseReviewStatusText = (status) => {
  const statusMap = {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝'
  }
  return statusMap[status] || status
}

const getCaseReviewStatusTagType = (status) => {
  const typeMap = {
    pending: 'info',
    approved: 'success',
    rejected: 'danger'
  }
  return typeMap[status] || 'info'
}



const getPriorityTagType = (priority) => {
  const typeMap = {
    P0: 'danger',
    P1: 'warning',
    P2: 'info',
    P3: 'success',
    P4: 'success'
  }
  return typeMap[priority] || 'info'
}

const progressColor = (percentage) => {
  if (percentage === 100) return '#67c23a'
  if (percentage >= 50) return '#409eff'
  return '#e6a23c'
}

// 生命周期
onMounted(() => {
  // 初始加载数据
  getMyTasks()
  getMyInitiated()
})
</script>

<style lang="scss" scoped>
.case-review-management {
  padding: 20px;
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