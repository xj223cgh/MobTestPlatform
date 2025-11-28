import request from '../utils/request'

// 获取测试任务列表
export const getTestTaskList = (params) => {
  return request({
    url: '/test-tasks',
    method: 'get',
    params
  })
}

// 根据测试套件ID获取测试任务
export const getTestTasksBySuite = (suiteId, params = {}) => {
  return request({
    url: `/test-tasks/suite/${suiteId}`,
    method: 'get',
    params
  })
}

// 获取测试任务详情
export const getTestTaskDetail = (id) => {
  return request({
    url: `/test-tasks/${id}`,
    method: 'get'
  })
}

// 创建测试任务
export const createTestTask = (data) => {
  return request({
    url: '/test-tasks',
    method: 'post',
    data
  })
}

// 更新测试任务
export const updateTestTask = (id, data) => {
  return request({
    url: `/test-tasks/${id}`,
    method: 'put',
    data
  })
}

// 删除测试任务
export const deleteTestTask = (id) => {
  return request({
    url: `/test-tasks/${id}`,
    method: 'delete'
  })
}

// 批量删除测试任务
export const batchDeleteTestTasks = (ids) => {
  return request({
    url: '/test-tasks/batch-delete',
    method: 'post',
    data: { ids }
  })
}

// 获取测试任务统计
export const getTestTaskStats = () => {
  return request({
    url: '/test-tasks/stats',
    method: 'get'
  })
}

// 启动测试任务
export const startTestTask = (id, params = {}) => {
  return request({
    url: `/test-tasks/${id}/start`,
    method: 'post',
    data: params
  })
}

// 停止测试任务
export const stopTestTask = (id) => {
  return request({
    url: `/test-tasks/${id}/stop`,
    method: 'post'
  })
}

// 暂停测试任务
export const pauseTestTask = (id) => {
  return request({
    url: `/test-tasks/${id}/pause`,
    method: 'post'
  })
}

// 恢复测试任务
export const resumeTestTask = (id) => {
  return request({
    url: `/test-tasks/${id}/resume`,
    method: 'post'
  })
}

// 重新执行测试任务
export const rerunTestTask = (id, params = {}) => {
  return request({
    url: `/test-tasks/${id}/rerun`,
    method: 'post',
    data: params
  })
}

// 批量启动测试任务
export const batchStartTestTasks = (ids, params = {}) => {
  return request({
    url: '/test-tasks/batch-start',
    method: 'post',
    data: { ids, ...params }
  })
}

// 批量停止测试任务
export const batchStopTestTasks = (ids) => {
  return request({
    url: '/test-tasks/batch-stop',
    method: 'post',
    data: { ids }
  })
}

// 批量暂停测试任务
export const batchPauseTestTasks = (ids) => {
  return request({
    url: '/test-tasks/batch-pause',
    method: 'post',
    data: { ids }
  })
}

// 批量恢复测试任务
export const batchResumeTestTasks = (ids) => {
  return request({
    url: '/test-tasks/batch-resume',
    method: 'post',
    data: { ids }
  })
}

// 获取测试任务执行日志
export const getTestTaskLogs = (id, params = {}) => {
  return request({
    url: `/test-tasks/${id}/logs`,
    method: 'get',
    params
  })
}

// 获取测试任务执行结果
export const getTestTaskResults = (id, params = {}) => {
  return request({
    url: `/test-tasks/${id}/results`,
    method: 'get',
    params
  })
}

// 获取测试任务执行报告
export const getTestTaskReport = (id, format = 'json') => {
  return request({
    url: `/test-tasks/${id}/report`,
    method: 'get',
    params: { format },
    responseType: format === 'pdf' ? 'blob' : 'json'
  })
}

// 获取测试任务执行进度
export const getTestTaskProgress = (id) => {
  return request({
    url: `/test-tasks/${id}/progress`,
    method: 'get'
  })
}

// 获取测试任务执行状态
export const getTestTaskStatus = (id) => {
  return request({
    url: `/test-tasks/${id}/status`,
    method: 'get'
  })
}

// 获取测试任务执行统计
export const getTestTaskExecutionStats = (id) => {
  return request({
    url: `/test-tasks/${id}/execution-stats`,
    method: 'get'
  })
}

// 获取所有测试任务的执行统计
export const getAllTestTaskExecutionStats = (params = {}) => {
  return request({
    url: '/test-tasks/execution-stats',
    method: 'get',
    params
  })
}

// 获取测试任务执行时间线
export const getTestTaskTimeline = (id) => {
  return request({
    url: `/test-tasks/${id}/timeline`,
    method: 'get'
  })
}

// 获取测试任务截图
export const getTestTaskScreenshots = (id, params = {}) => {
  return request({
    url: `/test-tasks/${id}/screenshots`,
    method: 'get',
    params
  })
}

// 获取测试任务性能数据
export const getTestTaskPerformance = (id) => {
  return request({
    url: `/test-tasks/${id}/performance`,
    method: 'get'
  })
}

// 获取测试任务错误信息
export const getTestTaskErrors = (id, params = {}) => {
  return request({
    url: `/test-tasks/${id}/errors`,
    method: 'get',
    params
  })
}

// 获取测试任务执行步骤
export const getTestTaskSteps = (id) => {
  return request({
    url: `/test-tasks/${id}/steps`,
    method: 'get'
  })
}

// 获取测试任务设备状态
export const getTestTaskDeviceStatus = (id) => {
  return request({
    url: `/test-tasks/${id}/device-status`,
    method: 'get'
  })
}

// 获取测试任务用例状态
export const getTestTaskCaseStatus = (id) => {
  return request({
    url: `/test-tasks/${id}/case-status`,
    method: 'get'
  })
}

// 导出测试任务
export const exportTestTasks = (params = {}) => {
  return request({
    url: '/test-tasks/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}

// 导入测试任务
export const importTestTasks = (formData) => {
  return request({
    url: '/test-tasks/import',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 获取测试任务模板
export const getTestTaskTemplate = () => {
  return request({
    url: '/test-tasks/template',
    method: 'get',
    responseType: 'blob'
  })
}

// 复制测试任务
export const copyTestTask = (id, data = {}) => {
  return request({
    url: `/test-tasks/${id}/copy`,
    method: 'post',
    data
  })
}

// 克隆测试任务
export const cloneTestTask = (id, data = {}) => {
  return request({
    url: `/test-tasks/${id}/clone`,
    method: 'post',
    data
  })
}

// 获取测试任务配置
export const getTestTaskConfig = () => {
  return request({
    url: '/test-tasks/config',
    method: 'get'
  })
}

// 获取测试任务的用例执行结果
export const getTaskExecutions = (taskId, params = {}) => {
  return request({
    url: `/test-tasks/${taskId}/executions`,
    method: 'get',
    params
  })
}

// 更新测试用例在任务中的执行状态
export const updateCaseExecution = (taskId, caseId, data) => {
  return request({
    url: `/test-tasks/${taskId}/executions/${caseId}`,
    method: 'post',
    data
  })
}

// 获取测试任务的统计信息
export const getTaskStatistics = (taskId) => {
  return request({
    url: `/test-tasks/${taskId}/statistics`,
    method: 'get'
  })
}

// 获取任务的思维导图视图数据
export const getTaskXmindView = (taskId) => {
  return request({
    url: `/test-tasks/${taskId}/xmind-view`,
    method: 'get'
  })
}

// 获取测试任务选项（状态、优先级、执行状态）
export const getTaskOptions = () => {
  return request({
    url: '/test-tasks/options',
    method: 'get'
  })
}

// 更新测试任务配置
export const updateTestTaskConfig = (data) => {
  return request({
    url: '/test-tasks/config',
    method: 'put',
    data
  })
}

// 获取测试任务环境列表
export const getTestTaskEnvironments = () => {
  return request({
    url: '/test-tasks/environments',
    method: 'get'
  })
}

// 创建测试任务环境
export const createTestTaskEnvironment = (data) => {
  return request({
    url: '/test-tasks/environments',
    method: 'post',
    data
  })
}

// 更新测试任务环境
export const updateTestTaskEnvironment = (id, data) => {
  return request({
    url: `/test-tasks/environments/${id}`,
    method: 'put',
    data
  })
}

// 删除测试任务环境
export const deleteTestTaskEnvironment = (id) => {
  return request({
    url: `/test-tasks/environments/${id}`,
    method: 'delete'
  })
}

// 获取测试任务调度
export const getTestTaskSchedule = (id) => {
  return request({
    url: `/test-tasks/${id}/schedule`,
    method: 'get'
  })
}

// 创建测试任务调度
export const createTestTaskSchedule = (id, data) => {
  return request({
    url: `/test-tasks/${id}/schedule`,
    method: 'post',
    data
  })
}

// 更新测试任务调度
export const updateTestTaskSchedule = (id, data) => {
  return request({
    url: `/test-tasks/${id}/schedule`,
    method: 'put',
    data
  })
}

// 删除测试任务调度
export const deleteTestTaskSchedule = (id) => {
  return request({
    url: `/test-tasks/${id}/schedule`,
    method: 'delete'
  })
}

// 获取测试任务依赖
export const getTestTaskDependencies = (id) => {
  return request({
    url: `/test-tasks/${id}/dependencies`,
    method: 'get'
  })
}

// 添加测试任务依赖
export const addTestTaskDependency = (id, data) => {
  return request({
    url: `/test-tasks/${id}/dependencies`,
    method: 'post',
    data
  })
}

// 移除测试任务依赖
export const removeTestTaskDependency = (id, dependencyId) => {
  return request({
    url: `/test-tasks/${id}/dependencies/${dependencyId}`,
    method: 'delete'
  })
}

// 获取测试任务通知
export const getTestTaskNotifications = (id) => {
  return request({
    url: `/test-tasks/${id}/notifications`,
    method: 'get'
  })
}

// 创建测试任务通知
export const createTestTaskNotification = (id, data) => {
  return request({
    url: `/test-tasks/${id}/notifications`,
    method: 'post',
    data
  })
}

// 更新测试任务通知
export const updateTestTaskNotification = (id, notificationId, data) => {
  return request({
    url: `/test-tasks/${id}/notifications/${notificationId}`,
    method: 'put',
    data
  })
}

// 删除测试任务通知
export const deleteTestTaskNotification = (id, notificationId) => {
  return request({
    url: `/test-tasks/${id}/notifications/${notificationId}`,
    method: 'delete'
  })
}

// 获取测试任务标签
export const getTestTaskTags = () => {
  return request({
    url: '/test-tasks/tags',
    method: 'get'
  })
}

// 创建测试任务标签
export const createTestTaskTag = (data) => {
  return request({
    url: '/test-tasks/tags',
    method: 'post',
    data
  })
}

// 更新测试任务标签
export const updateTestTaskTag = (id, data) => {
  return request({
    url: `/test-tasks/tags/${id}`,
    method: 'put',
    data
  })
}

// 删除测试任务标签
export const deleteTestTaskTag = (id) => {
  return request({
    url: `/test-tasks/tags/${id}`,
    method: 'delete'
  })
}

// 获取测试任务评论
export const getTestTaskComments = (id, params = {}) => {
  return request({
    url: `/test-tasks/${id}/comments`,
    method: 'get',
    params
  })
}

// 创建测试任务评论
export const createTestTaskComment = (id, data) => {
  return request({
    url: `/test-tasks/${id}/comments`,
    method: 'post',
    data
  })
}

// 更新测试任务评论
export const updateTestTaskComment = (id, commentId, data) => {
  return request({
    url: `/test-tasks/${id}/comments/${commentId}`,
    method: 'put',
    data
  })
}

// 删除测试任务评论
export const deleteTestTaskComment = (id, commentId) => {
  return request({
    url: `/test-tasks/${id}/comments/${commentId}`,
    method: 'delete'
  })
}

// 获取测试任务附件
export const getTestTaskAttachments = (id) => {
  return request({
    url: `/test-tasks/${id}/attachments`,
    method: 'get'
  })
}

// 上传测试任务附件
export const uploadTestTaskAttachment = (id, formData) => {
  return request({
    url: `/test-tasks/${id}/attachments`,
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 删除测试任务附件
export const deleteTestTaskAttachment = (id, attachmentId) => {
  return request({
    url: `/test-tasks/${id}/attachments/${attachmentId}`,
    method: 'delete'
  })
}

// 获取测试任务版本
export const getTestTaskVersions = (id) => {
  return request({
    url: `/test-tasks/${id}/versions`,
    method: 'get'
  })
}

// 恢复测试任务版本
export const restoreTestTaskVersion = (id, versionId) => {
  return request({
    url: `/test-tasks/${id}/versions/${versionId}/restore`,
    method: 'post'
  })
}

// 分享测试任务
export const shareTestTask = (id, data) => {
  return request({
    url: `/test-tasks/${id}/share`,
    method: 'post',
    data
  })
}

// 取消分享测试任务
export const unshareTestTask = (id, shareId) => {
  return request({
    url: `/test-tasks/${id}/share/${shareId}`,
    method: 'delete'
  })
}

// 获取测试任务分享链接
export const getTestTaskShareLinks = (id) => {
  return request({
    url: `/test-tasks/${id}/share`,
    method: 'get'
  })
}

// 验证测试任务
export const validateTestTask = (data) => {
  return request({
    url: '/test-tasks/validate',
    method: 'post',
    data
  })
}

// 获取测试任务执行历史
export const getTestTaskExecutionHistory = (id, params = {}) => {
  return request({
    url: `/test-tasks/${id}/history`,
    method: 'get',
    params
  })
}

// 比较测试任务执行结果
export const compareTestTaskExecutions = (executionIds) => {
  return request({
    url: '/test-tasks/compare',
    method: 'post',
    data: { executionIds }
  })
}

// 获取测试任务执行趋势
export const getTestTaskExecutionTrends = (params = {}) => {
  return request({
    url: '/test-tasks/execution-trends',
    method: 'get',
    params
  })
}

// 获取测试任务执行分布
export const getTestTaskExecutionDistribution = (params = {}) => {
  return request({
    url: '/test-tasks/execution-distribution',
    method: 'get',
    params
  })
}

// 获取测试任务执行热力图
export const getTestTaskExecutionHeatmap = (params = {}) => {
  return request({
    url: '/test-tasks/execution-heatmap',
    method: 'get',
    params
  })
}

// 获取测试任务执行排行榜
export const getTestTaskExecutionLeaderboard = (params = {}) => {
  return request({
    url: '/test-tasks/execution-leaderboard',
    method: 'get',
    params
  })
}

// 获取测试任务执行失败分析
export const getTestTaskExecutionFailureAnalysis = (params = {}) => {
  return request({
    url: '/test-tasks/execution-failure-analysis',
    method: 'get',
    params
  })
}

// 获取测试任务执行建议
export const getTestTaskExecutionRecommendations = (params = {}) => {
  return request({
    url: '/test-tasks/execution-recommendations',
    method: 'get',
    params
  })
}

// 获取测试任务执行警报
export const getTestTaskExecutionAlerts = (params = {}) => {
  return request({
    url: '/test-tasks/execution-alerts',
    method: 'get',
    params
  })
}

// 设置测试任务执行警报
export const setTestTaskExecutionAlert = (data) => {
  return request({
    url: '/test-tasks/execution-alerts',
    method: 'post',
    data
  })
}

// 删除测试任务执行警报
export const deleteTestTaskExecutionAlert = (alertId) => {
  return request({
    url: `/test-tasks/execution-alerts/${alertId}`,
    method: 'delete'
  })
}

// 测试任务API对象
export const testTaskApi = {
  getTestTaskList,
  getTestTaskDetail,
  createTestTask,
  updateTestTask,
  deleteTestTask,
  batchDeleteTestTasks,
  getTestTaskStats,
  startTestTask,
  stopTestTask,
  pauseTestTask,
  resumeTestTask,
  rerunTestTask,
  batchStartTestTasks,
  batchStopTestTasks,
  batchPauseTestTasks,
  batchResumeTestTasks,
  getTestTaskLogs,
  getTestTaskResults,
  getTestTaskReport,
  getTestTaskProgress,
  getTestTaskStatus,
  getTestTaskExecutionStats,
  getAllTestTaskExecutionStats,
  getTestTaskTimeline,
  getTestTaskScreenshots,
  getTestTaskPerformance,
  getTestTaskErrors,
  getTestTaskSteps,
  getTestTaskDeviceStatus,
  getTestTaskCaseStatus,
  exportTestTasks,
  importTestTasks,
  getTestTaskTemplate,
  copyTestTask,
  cloneTestTask,
  getTestTaskConfig,
  updateTestTaskConfig,
  getTestTaskEnvironments,
  createTestTaskEnvironment,
  updateTestTaskEnvironment,
  deleteTestTaskEnvironment,
  getTestTaskSchedule,
  createTestTaskSchedule,
  updateTestTaskSchedule,
  deleteTestTaskSchedule,
  getTestTaskDependencies,
  addTestTaskDependency,
  removeTestTaskDependency,
  getTestTaskNotifications,
  createTestTaskNotification,
  updateTestTaskNotification,
  deleteTestTaskNotification,
  getTestTaskTags,
  createTestTaskTag,
  updateTestTaskTag,
  deleteTestTaskTag,
  getTestTaskComments,
  createTestTaskComment,
  updateTestTaskComment,
  deleteTestTaskComment,
  getTestTaskAttachments,
  uploadTestTaskAttachment,
  deleteTestTaskAttachment,
  getTestTaskVersions,
  restoreTestTaskVersion,
  shareTestTask,
  unshareTestTask,
  getTestTaskShareLinks,
  validateTestTask,
  getTestTaskExecutionHistory,
  compareTestTaskExecutions,
  getTestTaskExecutionTrends,
  getTestTaskExecutionDistribution,
  getTestTaskExecutionHeatmap,
  getTestTaskExecutionLeaderboard,
  getTestTaskExecutionFailureAnalysis,
  getTestTaskExecutionRecommendations,
  getTestTaskExecutionAlerts,
  setTestTaskExecutionAlert,
  deleteTestTaskExecutionAlert,
  // 新增API
  getTestTasksBySuite,
  getTaskExecutions,
  updateCaseExecution,
  getTaskStatistics,
  getTaskXmindView,
  getTaskOptions
}