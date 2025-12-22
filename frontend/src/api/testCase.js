import request from "../utils/request";

// 测试用例与测试套件相关API

// 获取测试用例列表
export const getTestCaseList = (params) => {
  return request({
    url: "/test-cases",
    method: "get",
    params,
  });
};

// 根据测试套件ID获取测试用例
export const getTestCasesBySuite = (suiteId, params = {}) => {
  return request({
    url: `/test-cases/suite/${suiteId}`,
    method: "get",
    params,
  });
};

// 获取测试用例详情
export const getTestCaseDetail = (id) => {
  return request({
    url: `/test-cases/${id}`,
    method: "get",
  });
};

// 创建测试用例
export const createTestCase = (data) => {
  return request({
    url: "/test-cases",
    method: "post",
    data,
  });
};

// 更新测试用例
export const updateTestCase = (id, data) => {
  return request({
    url: `/test-cases/${id}`,
    method: "put",
    data,
  });
};

// 删除测试用例
export const deleteTestCase = (id) => {
  return request({
    url: `/test-cases/${id}`,
    method: "delete",
  });
};

// 批量删除测试用例
export const batchDeleteTestCases = (ids) => {
  return request({
    url: "/test-cases/batch-delete",
    method: "post",
    data: { ids },
  });
};

// 获取测试用例统计
export const getTestCaseStats = () => {
  return request({
    url: "/test-cases/stats",
    method: "get",
  });
};

// 执行测试用例
export const executeTestCase = (id, params = {}) => {
  return request({
    url: `/test-cases/${id}/execute`,
    method: "post",
    data: params,
  });
};

// Xmind相关功能已移除，暂时不再支持脑图实现

// 批量执行测试用例
export const batchExecuteTestCases = (ids, params = {}) => {
  return request({
    url: "/test-cases/batch-execute",
    method: "post",
    data: { ids, ...params },
  });
};

// 获取测试用例执行历史
export const getTestCaseExecutionHistory = (id, params = {}) => {
  return request({
    url: `/test-cases/${id}/executions`,
    method: "get",
    params,
  });
};

// 获取测试用例执行详情
export const getTestCaseExecutionDetail = (executionId) => {
  return request({
    url: `/test-cases/executions/${executionId}`,
    method: "get",
  });
};

// 停止测试用例执行
export const stopTestCaseExecution = (executionId) => {
  return request({
    url: `/test-cases/executions/${executionId}/stop`,
    method: "post",
  });
};

// 重新运行测试用例执行
export const rerunTestCaseExecution = (executionId) => {
  return request({
    url: `/test-cases/executions/${executionId}/rerun`,
    method: "post",
  });
};

// 导出测试用例
export const exportTestCases = (params = {}) => {
  return request({
    url: "/test-cases/export",
    method: "get",
    params,
    responseType: "blob",
  });
};

// 导入测试用例
export const importTestCases = (formData) => {
  return request({
    url: "/test-cases/import",
    method: "post",
    data: formData,
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};

// 获取测试用例模板
export const getTestCaseTemplate = () => {
  return request({
    url: "/test-cases/template",
    method: "get",
    responseType: "blob",
  });
};

// 复制测试用例
export const copyTestCase = (id, data = {}) => {
  return request({
    url: `/test-cases/${id}/copy`,
    method: "post",
    data,
  });
};

// 移动测试用例
export const moveTestCase = (id, data) => {
  return request({
    url: `/test-cases/${id}/move`,
    method: "post",
    data,
  });
};

// 获取测试用例模块列表
export const getTestCaseModules = () => {
  return request({
    url: "/test-cases/modules",
    method: "get",
  });
};

// 创建测试用例模块
export const createTestCaseModule = (data) => {
  return request({
    url: "/test-cases/modules",
    method: "post",
    data,
  });
};

// 更新测试用例模块
export const updateTestCaseModule = (id, data) => {
  return request({
    url: `/test-cases/modules/${id}`,
    method: "put",
    data,
  });
};

// 删除测试用例模块
export const deleteTestCaseModule = (id) => {
  return request({
    url: `/test-cases/modules/${id}`,
    method: "delete",
  });
};

// 获取测试用例标签列表
export const getTestCaseTags = () => {
  return request({
    url: "/test-cases/tags",
    method: "get",
  });
};

// 创建测试用例标签
export const createTestCaseTag = (data) => {
  return request({
    url: "/test-cases/tags",
    method: "post",
    data,
  });
};

// 更新测试用例标签
export const updateTestCaseTag = (id, data) => {
  return request({
    url: `/test-cases/tags/${id}`,
    method: "put",
    data,
  });
};

// 删除测试用例标签
export const deleteTestCaseTag = (id) => {
  return request({
    url: `/test-cases/tags/${id}`,
    method: "delete",
  });
};

// 获取测试用例评论
export const getTestCaseComments = (id, params = {}) => {
  return request({
    url: `/test-cases/${id}/comments`,
    method: "get",
    params,
  });
};

// 创建测试用例评论
export const createTestCaseComment = (id, data) => {
  return request({
    url: `/test-cases/${id}/comments`,
    method: "post",
    data,
  });
};

// 更新测试用例评论
export const updateTestCaseComment = (id, commentId, data) => {
  return request({
    url: `/test-cases/${id}/comments/${commentId}`,
    method: "put",
    data,
  });
};

// 删除测试用例评论
export const deleteTestCaseComment = (id, commentId) => {
  return request({
    url: `/test-cases/${id}/comments/${commentId}`,
    method: "delete",
  });
};

// 获取测试用例附件
export const getTestCaseAttachments = (id) => {
  return request({
    url: `/test-cases/${id}/attachments`,
    method: "get",
  });
};

// 上传测试用例附件
export const uploadTestCaseAttachment = (id, formData) => {
  return request({
    url: `/test-cases/${id}/attachments`,
    method: "post",
    data: formData,
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};

// 删除测试用例附件
export const deleteTestCaseAttachment = (id, attachmentId) => {
  return request({
    url: `/test-cases/${id}/attachments/${attachmentId}`,
    method: "delete",
  });
};

// 获取测试用例版本历史
export const getTestCaseVersions = (id) => {
  return request({
    url: `/test-cases/${id}/versions`,
    method: "get",
  });
};

// 恢复测试用例版本
export const restoreTestCaseVersion = (id, versionId) => {
  return request({
    url: `/test-cases/${id}/versions/${versionId}/restore`,
    method: "post",
  });
};

// 获取测试用例依赖
export const getTestCaseDependencies = (id) => {
  return request({
    url: `/test-cases/${id}/dependencies`,
    method: "get",
  });
};

// 添加测试用例依赖
export const addTestCaseDependency = (id, data) => {
  return request({
    url: `/test-cases/${id}/dependencies`,
    method: "post",
    data,
  });
};

// 移除测试用例依赖
export const removeTestCaseDependency = (id, dependencyId) => {
  return request({
    url: `/test-cases/${id}/dependencies/${dependencyId}`,
    method: "delete",
  });
};

// 获取测试用例覆盖率
export const getTestCaseCoverage = (id) => {
  return request({
    url: `/test-cases/${id}/coverage`,
    method: "get",
  });
};

// 获取测试用例执行报告
export const getTestCaseExecutionReport = (executionId, format = "json") => {
  return request({
    url: `/test-cases/executions/${executionId}/report`,
    method: "get",
    params: { format },
    responseType: format === "json" ? "json" : "blob",
  });
};

// 分享测试用例
export const shareTestCase = (id, data) => {
  return request({
    url: `/test-cases/${id}/share`,
    method: "post",
    data,
  });
};

// 取消分享测试用例
export const unshareTestCase = (id, shareId) => {
  return request({
    url: `/test-cases/${id}/share/${shareId}`,
    method: "delete",
  });
};

// 获取测试用例分享链接
export const getTestCaseShareLinks = (id) => {
  return request({
    url: `/test-cases/${id}/share`,
    method: "get",
  });
};

// 验证测试用例
export const validateTestCase = (data) => {
  return request({
    url: "/test-cases/validate",
    method: "post",
    data,
  });
};

// 获取测试用例执行日志
export const getTestCaseExecutionLogs = (executionId, params = {}) => {
  return request({
    url: `/test-cases/executions/${executionId}/logs`,
    method: "get",
    params,
  });
};

// 获取测试用例执行截图
export const getTestCaseExecutionScreenshots = (executionId) => {
  return request({
    url: `/test-cases/executions/${executionId}/screenshots`,
    method: "get",
  });
};

// 获取测试用例执行性能数据
export const getTestCaseExecutionPerformance = (executionId) => {
  return request({
    url: `/test-cases/executions/${executionId}/performance`,
    method: "get",
  });
};

// 获取测试用例执行错误
export const getTestCaseExecutionErrors = (executionId) => {
  return request({
    url: `/test-cases/executions/${executionId}/errors`,
    method: "get",
  });
};

// 获取测试用例执行步骤
export const getTestCaseExecutionSteps = (executionId) => {
  return request({
    url: `/test-cases/executions/${executionId}/steps`,
    method: "get",
  });
};

// 重试测试用例执行步骤
export const retryTestCaseExecutionStep = (executionId, stepId) => {
  return request({
    url: `/test-cases/executions/${executionId}/steps/${stepId}/retry`,
    method: "post",
  });
};

// 跳过测试用例执行步骤
export const skipTestCaseExecutionStep = (executionId, stepId) => {
  return request({
    url: `/test-cases/executions/${executionId}/steps/${stepId}/skip`,
    method: "post",
  });
};

// 获取测试用例执行时间线
export const getTestCaseExecutionTimeline = (executionId) => {
  return request({
    url: `/test-cases/executions/${executionId}/timeline`,
    method: "get",
  });
};

// 获取测试用例执行摘要
export const getTestCaseExecutionSummary = (executionId) => {
  return request({
    url: `/test-cases/executions/${executionId}/summary`,
    method: "get",
  });
};

// 比较测试用例执行
export const compareTestCaseExecutions = (executionIds) => {
  return request({
    url: "/test-cases/executions/compare",
    method: "post",
    data: { executionIds },
  });
};

// 获取测试用例执行统计
export const getTestCaseExecutionStats = (params = {}) => {
  return request({
    url: "/test-cases/executions/stats",
    method: "get",
    params,
  });
};

// 获取测试用例执行趋势
export const getTestCaseExecutionTrends = (params = {}) => {
  return request({
    url: "/test-cases/executions/trends",
    method: "get",
    params,
  });
};

// 获取测试用例执行分布
export const getTestCaseExecutionDistribution = (params = {}) => {
  return request({
    url: "/test-cases/executions/distribution",
    method: "get",
    params,
  });
};

// 获取测试用例执行热力图
export const getTestCaseExecutionHeatmap = (params = {}) => {
  return request({
    url: "/test-cases/executions/heatmap",
    method: "get",
    params,
  });
};

// 获取测试用例执行排行榜
export const getTestCaseExecutionLeaderboard = (params = {}) => {
  return request({
    url: "/test-cases/executions/leaderboard",
    method: "get",
    params,
  });
};

// 获取测试用例执行失败分析
export const getTestCaseExecutionFailureAnalysis = (params = {}) => {
  return request({
    url: "/test-cases/executions/failure-analysis",
    method: "get",
    params,
  });
};

// 获取测试用例执行建议
export const getTestCaseExecutionRecommendations = (params = {}) => {
  return request({
    url: "/test-cases/executions/recommendations",
    method: "get",
    params,
  });
};

// 获取测试用例执行警报
export const getTestCaseExecutionAlerts = (params = {}) => {
  return request({
    url: "/test-cases/executions/alerts",
    method: "get",
    params,
  });
};

// 设置测试用例执行警报
export const setTestCaseExecutionAlert = (data) => {
  return request({
    url: "/test-cases/executions/alerts",
    method: "post",
    data,
  });
};

// 删除测试用例执行警报
export const deleteTestCaseExecutionAlert = (alertId) => {
  return request({
    url: `/test-cases/executions/alerts/${alertId}`,
    method: "delete",
  });
};

// 获取测试用例执行配置
export const getTestCaseExecutionConfig = () => {
  return request({
    url: "/test-cases/executions/config",
    method: "get",
  });
};

// 更新测试用例执行配置
export const updateTestCaseExecutionConfig = (data) => {
  return request({
    url: "/test-cases/executions/config",
    method: "put",
    data,
  });
};

// 获取测试用例执行环境列表
export const getTestCaseExecutionEnvironments = () => {
  return request({
    url: "/test-cases/executions/environments",
    method: "get",
  });
};

// 创建测试用例执行环境
export const createTestCaseExecutionEnvironment = (data) => {
  return request({
    url: "/test-cases/executions/environments",
    method: "post",
    data,
  });
};

// 更新测试用例执行环境
export const updateTestCaseExecutionEnvironment = (id, data) => {
  return request({
    url: `/test-cases/executions/environments/${id}`,
    method: "put",
    data,
  });
};

// 删除测试用例执行环境
export const deleteTestCaseExecutionEnvironment = (id) => {
  return request({
    url: `/test-cases/executions/environments/${id}`,
    method: "delete",
  });
};

// 获取测试用例执行环境变量
export const getTestCaseExecutionEnvironmentVariables = (environmentId) => {
  return request({
    url: `/test-cases/executions/environments/${environmentId}/variables`,
    method: "get",
  });
};

// 创建测试用例执行环境变量
export const createTestCaseExecutionEnvironmentVariable = (
  environmentId,
  data,
) => {
  return request({
    url: `/test-cases/executions/environments/${environmentId}/variables`,
    method: "post",
    data,
  });
};

// 更新测试用例执行环境变量
export const updateTestCaseExecutionEnvironmentVariable = (
  environmentId,
  variableId,
  data,
) => {
  return request({
    url: `/test-cases/executions/environments/${environmentId}/variables/${variableId}`,
    method: "put",
    data,
  });
};

// 删除测试用例执行环境变量
export const deleteTestCaseExecutionEnvironmentVariable = (
  environmentId,
  variableId,
) => {
  return request({
    url: `/test-cases/executions/environments/${environmentId}/variables/${variableId}`,
    method: "delete",
  });
};
