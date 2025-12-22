import request from "../utils/request";

// 获取报告列表
export const getReportList = (params) => {
  return request({
    url: "/reports",
    method: "get",
    params,
  });
};

// 获取报告详情
export const getReportDetail = (id) => {
  return request({
    url: `/reports/${id}`,
    method: "get",
  });
};

// 创建报告
export const createReport = (data) => {
  return request({
    url: "/reports",
    method: "post",
    data,
  });
};

// 更新报告
export const updateReport = (id, data) => {
  return request({
    url: `/reports/${id}`,
    method: "put",
    data,
  });
};

// 删除报告
export const deleteReport = (id) => {
  return request({
    url: `/reports/${id}`,
    method: "delete",
  });
};

// 批量删除报告
export const batchDeleteReports = (ids) => {
  return request({
    url: "/reports/batch-delete",
    method: "post",
    data: { ids },
  });
};

// 获取报告统计
export const getReportStats = () => {
  return request({
    url: "/reports/stats",
    method: "get",
  });
};

// 生成报告
export const generateReport = (data) => {
  return request({
    url: "/reports/generate",
    method: "post",
    data,
  });
};

// 下载报告
export const downloadReport = (id, format = "pdf") => {
  return request({
    url: `/reports/${id}/download`,
    method: "get",
    params: { format },
    responseType: "blob",
  });
};

// 导出报告
export const exportReports = (params = {}) => {
  return request({
    url: "/reports/export",
    method: "get",
    params,
    responseType: "blob",
  });
};

// 分享报告
export const shareReport = (id, data = {}) => {
  return request({
    url: `/reports/${id}/share`,
    method: "post",
    data,
  });
};

// 取消分享报告
export const unshareReport = (id, shareId) => {
  return request({
    url: `/reports/${id}/share/${shareId}`,
    method: "delete",
  });
};

// 获取报告分享链接
export const getReportShareLinks = (id) => {
  return request({
    url: `/reports/${id}/shares`,
    method: "get",
  });
};

// 获取报告模板
export const getReportTemplate = () => {
  return request({
    url: "/reports/template",
    method: "get",
    responseType: "blob",
  });
};

// 获取报告配置
export const getReportConfig = () => {
  return request({
    url: "/reports/config",
    method: "get",
  });
};

// 更新报告配置
export const updateReportConfig = (data) => {
  return request({
    url: "/reports/config",
    method: "put",
    data,
  });
};

// 获取报告类型列表
export const getReportTypes = () => {
  return request({
    url: "/reports/types",
    method: "get",
  });
};

// 创建报告类型
export const createReportType = (data) => {
  return request({
    url: "/reports/types",
    method: "post",
    data,
  });
};

// 更新报告类型
export const updateReportType = (id, data) => {
  return request({
    url: `/reports/types/${id}`,
    method: "put",
    data,
  });
};

// 删除报告类型
export const deleteReportType = (id) => {
  return request({
    url: `/reports/types/${id}`,
    method: "delete",
  });
};

// 获取报告格式列表
export const getReportFormats = () => {
  return request({
    url: "/reports/formats",
    method: "get",
  });
};

// 获取报告内容模板
export const getReportContentTemplate = (type) => {
  return request({
    url: `/reports/content-template/${type}`,
    method: "get",
  });
};

// 更新报告内容模板
export const updateReportContentTemplate = (type, data) => {
  return request({
    url: `/reports/content-template/${type}`,
    method: "put",
    data,
  });
};

// 获取报告图表配置
export const getReportChartConfig = (type) => {
  return request({
    url: `/reports/chart-config/${type}`,
    method: "get",
  });
};

// 更新报告图表配置
export const updateReportChartConfig = (type, data) => {
  return request({
    url: `/reports/chart-config/${type}`,
    method: "put",
    data,
  });
};

// 获取报告样式配置
export const getReportStyleConfig = (type) => {
  return request({
    url: `/reports/style-config/${type}`,
    method: "get",
  });
};

// 更新报告样式配置
export const updateReportStyleConfig = (type, data) => {
  return request({
    url: `/reports/style-config/${type}`,
    method: "put",
    data,
  });
};

// 获取报告数据
export const getReportData = (id, params = {}) => {
  return request({
    url: `/api/reports/${id}/data`,
    method: "get",
    params,
  });
};

// 获取报告图表数据
export const getReportChartData = (id, chartType, params = {}) => {
  return request({
    url: `/api/reports/${id}/chart-data/${chartType}`,
    method: "get",
    params,
  });
};

// 获取报告日志
export const getReportLogs = (id, params = {}) => {
  return request({
    url: `/api/reports/${id}/logs`,
    method: "get",
    params,
  });
};

// 获取报告截图
export const getReportScreenshots = (id, params = {}) => {
  return request({
    url: `/api/reports/${id}/screenshots`,
    method: "get",
    params,
  });
};

// 获取报告附件
export const getReportAttachments = (id) => {
  return request({
    url: `/api/reports/${id}/attachments`,
    method: "get",
  });
};

// 上传报告附件
export const uploadReportAttachment = (id, formData) => {
  return request({
    url: `/api/reports/${id}/attachments`,
    method: "post",
    data: formData,
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};

// 删除报告附件
export const deleteReportAttachment = (id, attachmentId) => {
  return request({
    url: `/api/reports/${id}/attachments/${attachmentId}`,
    method: "delete",
  });
};

// 获取报告评论
export const getReportComments = (id, params = {}) => {
  return request({
    url: `/api/reports/${id}/comments`,
    method: "get",
    params,
  });
};

// 创建报告评论
export const createReportComment = (id, data) => {
  return request({
    url: `/api/reports/${id}/comments`,
    method: "post",
    data,
  });
};

// 更新报告评论
export const updateReportComment = (id, commentId, data) => {
  return request({
    url: `/api/reports/${id}/comments/${commentId}`,
    method: "put",
    data,
  });
};

// 删除报告评论
export const deleteReportComment = (id, commentId) => {
  return request({
    url: `/api/reports/${id}/comments/${commentId}`,
    method: "delete",
  });
};

// 获取报告版本历史
export const getReportVersions = (id) => {
  return request({
    url: `/api/reports/${id}/versions`,
    method: "get",
  });
};

// 恢复报告版本
export const restoreReportVersion = (id, versionId) => {
  return request({
    url: `/api/reports/${id}/versions/${versionId}/restore`,
    method: "post",
  });
};

// 获取报告依赖关系
export const getReportDependencies = (id) => {
  return request({
    url: `/api/reports/${id}/dependencies`,
    method: "get",
  });
};

// 添加报告依赖关系
export const addReportDependency = (id, data) => {
  return request({
    url: `/api/reports/${id}/dependencies`,
    method: "post",
    data,
  });
};

// 删除报告依赖关系
export const removeReportDependency = (id, dependencyId) => {
  return request({
    url: `/api/reports/${id}/dependencies/${dependencyId}`,
    method: "delete",
  });
};

// 获取报告标签列表
export const getReportTags = () => {
  return request({
    url: "/api/reports/tags",
    method: "get",
  });
};

// 创建报告标签
export const createReportTag = (data) => {
  return request({
    url: "/api/reports/tags",
    method: "post",
    data,
  });
};

// 更新报告标签
export const updateReportTag = (id, data) => {
  return request({
    url: `/api/reports/tags/${id}`,
    method: "put",
    data,
  });
};

// 删除报告标签
export const deleteReportTag = (id) => {
  return request({
    url: `/api/reports/tags/${id}`,
    method: "delete",
  });
};

// 获取报告通知设置
export const getReportNotifications = (id) => {
  return request({
    url: `/api/reports/${id}/notifications`,
    method: "get",
  });
};

// 创建报告通知设置
export const createReportNotification = (id, data) => {
  return request({
    url: `/api/reports/${id}/notifications`,
    method: "post",
    data,
  });
};

// 更新报告通知设置
export const updateReportNotification = (id, notificationId, data) => {
  return request({
    url: `/api/reports/${id}/notifications/${notificationId}`,
    method: "put",
    data,
  });
};

// 删除报告通知设置
export const deleteReportNotification = (id, notificationId) => {
  return request({
    url: `/api/reports/${id}/notifications/${notificationId}`,
    method: "delete",
  });
};

// 获取报告权限设置
export const getReportPermissions = (id) => {
  return request({
    url: `/api/reports/${id}/permissions`,
    method: "get",
  });
};

// 更新报告权限设置
export const updateReportPermissions = (id, data) => {
  return request({
    url: `/api/reports/${id}/permissions`,
    method: "put",
    data,
  });
};

// 获取报告访问日志
export const getReportAccessLogs = (id, params = {}) => {
  return request({
    url: `/api/reports/${id}/access-logs`,
    method: "get",
    params,
  });
};

// 获取报告统计图表
export const getReportStatsCharts = (params = {}) => {
  return request({
    url: "/api/reports/stats-charts",
    method: "get",
    params,
  });
};

// 获取报告趋势分析
export const getReportTrendAnalysis = (params = {}) => {
  return request({
    url: "/api/reports/trend-analysis",
    method: "get",
    params,
  });
};

// 获取报告对比分析
export const getReportComparisonAnalysis = (reportIds) => {
  return request({
    url: "/api/reports/comparison-analysis",
    method: "post",
    data: { report_ids: reportIds },
  });
};

// 获取报告质量分析
export const getReportQualityAnalysis = (params = {}) => {
  return request({
    url: "/api/reports/quality-analysis",
    method: "get",
    params,
  });
};

// 获取报告性能分析
export const getReportPerformanceAnalysis = (params = {}) => {
  return request({
    url: "/api/reports/performance-analysis",
    method: "get",
    params,
  });
};

// 获取报告覆盖率分析
export const getReportCoverageAnalysis = (params = {}) => {
  return request({
    url: "/api/reports/coverage-analysis",
    method: "get",
    params,
  });
};

// 获取报告错误分析
export const getReportErrorAnalysis = (params = {}) => {
  return request({
    url: "/api/reports/error-analysis",
    method: "get",
    params,
  });
};

// 获取报告建议
export const getReportRecommendations = (params = {}) => {
  return request({
    url: "/api/reports/recommendations",
    method: "get",
    params,
  });
};

// 获取报告预警
export const getReportAlerts = (params = {}) => {
  return request({
    url: "/api/reports/alerts",
    method: "get",
    params,
  });
};

// 设置报告预警
export const setReportAlert = (data) => {
  return request({
    url: "/api/reports/alerts",
    method: "post",
    data,
  });
};

// 删除报告预警
export const deleteReportAlert = (alertId) => {
  return request({
    url: `/api/reports/alerts/${alertId}`,
    method: "delete",
  });
};

// 获取报告自动化配置
export const getReportAutomationConfig = () => {
  return request({
    url: "/api/reports/automation-config",
    method: "get",
  });
};

// 更新报告自动化配置
export const updateReportAutomationConfig = (data) => {
  return request({
    url: "/api/reports/automation-config",
    method: "put",
    data,
  });
};

// 获取报告集成配置
export const getReportIntegrationConfig = () => {
  return request({
    url: "/api/reports/integration-config",
    method: "get",
  });
};

// 更新报告集成配置
export const updateReportIntegrationConfig = (data) => {
  return request({
    url: "/api/reports/integration-config",
    method: "put",
    data,
  });
};

// 测试报告连接
export const testReportConnection = (config) => {
  return request({
    url: "/api/reports/test-connection",
    method: "post",
    data: config,
  });
};

// 同步报告数据
export const syncReportData = (params = {}) => {
  return request({
    url: "/api/reports/sync-data",
    method: "post",
    data: params,
  });
};

// 备份报告
export const backupReport = (id, params = {}) => {
  return request({
    url: `/api/reports/${id}/backup`,
    method: "post",
    data: params,
  });
};

// 恢复报告
export const restoreReport = (backupId) => {
  return request({
    url: `/api/reports/restore/${backupId}`,
    method: "post",
  });
};

// 获取报告备份列表
export const getReportBackups = (params = {}) => {
  return request({
    url: "/api/reports/backups",
    method: "get",
    params,
  });
};

// 删除报告备份
export const deleteReportBackup = (backupId) => {
  return request({
    url: `/api/reports/backups/${backupId}`,
    method: "delete",
  });
};

// 验证报告
export const validateReport = (data) => {
  return request({
    url: "/api/reports/validate",
    method: "post",
    data,
  });
};

// 预览报告
export const previewReport = (data) => {
  return request({
    url: "/api/reports/preview",
    method: "post",
    data,
  });
};

// 获取报告模板列表
export const getReportTemplates = (params = {}) => {
  return request({
    url: "/api/reports/templates",
    method: "get",
    params,
  });
};

// 创建报告模板
export const createReportTemplate = (data) => {
  return request({
    url: "/api/reports/templates",
    method: "post",
    data,
  });
};

// 更新报告模板
export const updateReportTemplate = (id, data) => {
  return request({
    url: `/api/reports/templates/${id}`,
    method: "put",
    data,
  });
};

// 删除报告模板
export const deleteReportTemplate = (id) => {
  return request({
    url: `/api/reports/templates/${id}`,
    method: "delete",
  });
};

// 复制报告模板
export const copyReportTemplate = (id, data = {}) => {
  return request({
    url: `/api/reports/templates/${id}/copy`,
    method: "post",
    data,
  });
};

// 应用报告模板
export const applyReportTemplate = (id, templateId) => {
  return request({
    url: `/api/reports/${id}/apply-template/${templateId}`,
    method: "post",
  });
};

// 导出为reportApi对象
export const reportApi = {
  getReportList,
  getReportDetail,
  createReport,
  updateReport,
  deleteReport,
  batchDeleteReports,
  getReportStats,
  generateReport,
  downloadReport,
  exportReports,
  shareReport,
  unshareReport,
  getReportShareLinks,
  getReportTemplate,
  getReportConfig,
  updateReportConfig,
  getReportTypes,
  createReportType,
  updateReportType,
  deleteReportType,
  getReportFormats,
  getReportContentTemplate,
  updateReportContentTemplate,
  getReportChartConfig,
  updateReportChartConfig,
  getReportStyleConfig,
  updateReportStyleConfig,
  getReportData,
  getReportChartData,
  getReportLogs,
  getReportScreenshots,
  getReportAttachments,
  uploadReportAttachment,
  deleteReportAttachment,
  getReportComments,
  createReportComment,
  updateReportComment,
  deleteReportComment,
  getReportVersions,
  restoreReportVersion,
  getReportDependencies,
  addReportDependency,
  removeReportDependency,
  getReportTags,
  createReportTag,
  updateReportTag,
  deleteReportTag,
  getReportNotifications,
  createReportNotification,
  updateReportNotification,
  deleteReportNotification,
  getReportPermissions,
  updateReportPermissions,
  getReportAccessLogs,
  getReportStatsCharts,
  getReportTrendAnalysis,
  getReportComparisonAnalysis,
  getReportQualityAnalysis,
  getReportPerformanceAnalysis,
  getReportCoverageAnalysis,
  getReportErrorAnalysis,
  getReportRecommendations,
  getReportAlerts,
  setReportAlert,
  deleteReportAlert,
  getReportAutomationConfig,
  updateReportAutomationConfig,
  getReportIntegrationConfig,
  updateReportIntegrationConfig,
  testReportConnection,
  syncReportData,
  backupReport,
  restoreReport,
  getReportBackups,
  deleteReportBackup,
  validateReport,
  previewReport,
  getReportTemplates,
  createReportTemplate,
  updateReportTemplate,
  deleteReportTemplate,
  copyReportTemplate,
  applyReportTemplate,
};
