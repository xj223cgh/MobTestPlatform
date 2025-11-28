import request from '@/utils/request'

// 系统设置相关API
export const systemApi = {
  // 基础设置
  getBasicSettings() {
    return request({
      url: '/system/settings/basic',
      method: 'get'
    })
  },

  updateBasicSettings(data) {
    return request({
      url: '/system/settings/basic',
      method: 'put',
      data
    })
  },

  // 安全设置
  getSecuritySettings() {
    return request({
      url: '/system/settings/security',
      method: 'get'
    })
  },

  updateSecuritySettings(data) {
    return request({
      url: '/system/settings/security',
      method: 'put',
      data
    })
  },

  // 邮件设置
  getEmailSettings() {
    return request({
      url: '/system/settings/email',
      method: 'get'
    })
  },

  updateEmailSettings(data) {
    return request({
      url: '/system/settings/email',
      method: 'put',
      data
    })
  },

  testEmailSettings() {
    return request({
      url: '/system/settings/email/test',
      method: 'post'
    })
  },

  // 存储设置
  getStorageSettings() {
    return request({
      url: '/system/settings/storage',
      method: 'get'
    })
  },

  updateStorageSettings(data) {
    return request({
      url: '/system/settings/storage',
      method: 'put',
      data
    })
  },

  testStorageSettings(data) {
    return request({
      url: '/system/settings/storage/test',
      method: 'post',
      data
    })
  },

  // 备份设置
  getBackupSettings() {
    return request({
      url: '/system/settings/backup',
      method: 'get'
    })
  },

  updateBackupSettings(data) {
    return request({
      url: '/system/settings/backup',
      method: 'put',
      data
    })
  },

  getBackupHistory(params) {
    return request({
      url: '/system/backup/history',
      method: 'get',
      params
    })
  },

  createBackup(data) {
    return request({
      url: '/system/backup/create',
      method: 'post',
      data
    })
  },

  downloadBackup(id) {
    return request({
      url: `/system/backup/download/${id}`,
      method: 'get',
      responseType: 'blob'
    })
  },

  deleteBackup(id) {
    return request({
      url: `/system/backup/delete/${id}`,
      method: 'delete'
    })
  },

  // 日志设置
  getLogSettings() {
    return request({
      url: '/system/settings/log',
      method: 'get'
    })
  },

  updateLogSettings(data) {
    return request({
      url: '/system/settings/log',
      method: 'put',
      data
    })
  },

  getLogs(params) {
    return request({
      url: '/system/logs',
      method: 'get',
      params
    })
  },

  clearLogs() {
    return request({
      url: '/system/logs/clear',
      method: 'post'
    })
  },

  downloadLogs(params) {
    return request({
      url: '/system/logs/download',
      method: 'get',
      params,
      responseType: 'blob'
    })
  },

  // 通知设置
  getNotificationSettings() {
    return request({
      url: '/system/settings/notification',
      method: 'get'
    })
  },

  updateNotificationSettings(data) {
    return request({
      url: '/system/settings/notification',
      method: 'put',
      data
    })
  },

  testNotification(data) {
    return request({
      url: '/system/notification/test',
      method: 'post',
      data
    })
  },

  // 系统信息
  getSystemInfo() {
    return request({
      url: '/system/info',
      method: 'get'
    })
  },

  getSystemStatus() {
    return request({
      url: '/system/status',
      method: 'get'
    })
  },

  getSystemMetrics() {
    return request({
      url: '/system/metrics',
      method: 'get'
    })
  },

  // 系统操作
  restartSystem() {
    return request({
      url: '/system/restart',
      method: 'post'
    })
  },

  shutdownSystem() {
    return request({
      url: '/system/shutdown',
      method: 'post'
    })
  },

  clearCache() {
    return request({
      url: '/system/cache/clear',
      method: 'post'
    })
  },

  optimizeDatabase() {
    return request({
      url: '/system/database/optimize',
      method: 'post'
    })
  },

  // 性能监控
  getPerformanceMetrics(params) {
    return request({
      url: '/system/performance/metrics',
      method: 'get',
      params
    })
  },

  getErrorLogs(params) {
    return request({
      url: '/system/errors/logs',
      method: 'get',
      params
    })
  },

  getAccessLogs(params) {
    return request({
      url: '/system/access/logs',
      method: 'get',
      params
    })
  },

  // 系统配置
  getSystemConfig() {
    return request({
      url: '/system/config',
      method: 'get'
    })
  },

  updateSystemConfig(data) {
    return request({
      url: '/system/config',
      method: 'put',
      data
    })
  },

  resetSystemConfig() {
    return request({
      url: '/system/config/reset',
      method: 'post'
    })
  },

  // 系统更新
  checkUpdate() {
    return request({
      url: '/system/update/check',
      method: 'get'
    })
  },

  downloadUpdate() {
    return request({
      url: '/system/update/download',
      method: 'get',
      responseType: 'blob'
    })
  },

  installUpdate() {
    return request({
      url: '/system/update/install',
      method: 'post'
    })
  },

  getUpdateHistory() {
    return request({
      url: '/system/update/history',
      method: 'get'
    })
  },

  // 安全管理
  getSecurityLogs(params) {
    return request({
      url: '/system/security/logs',
      method: 'get',
      params
    })
  },

  getSecurityAlerts(params) {
    return request({
      url: '/system/security/alerts',
      method: 'get',
      params
    })
  },

  resolveSecurityAlert(id) {
    return request({
      url: `/system/security/alerts/${id}/resolve`,
      method: 'post'
    })
  },

  // 统计信息
  getSystemStats(params) {
    return request({
      url: '/system/stats',
      method: 'get',
      params
    })
  },

  getUsageStats(params) {
    return request({
      url: '/system/usage/stats',
      method: 'get',
      params
    })
  },

  getPerformanceStats(params) {
    return request({
      url: '/system/performance/stats',
      method: 'get',
      params
    })
  },

  // 配置验证
  validateConfig(data) {
    return request({
      url: '/system/config/validate',
      method: 'post',
      data
    })
  },

  // 配置导入导出
  exportConfig() {
    return request({
      url: '/system/config/export',
      method: 'get',
      responseType: 'blob'
    })
  },

  importConfig(data) {
    return request({
      url: '/system/config/import',
      method: 'post',
      data,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 系统诊断
  runDiagnostics() {
    return request({
      url: '/system/diagnostics/run',
      method: 'post'
    })
  },

  getDiagnosticResults() {
    return request({
      url: '/system/diagnostics/results',
      method: 'get'
    })
  },

  fixDiagnosticIssue(id) {
    return request({
      url: `/system/diagnostics/issues/${id}/fix`,
      method: 'post'
    })
  },

  // 系统任务
  getSystemTasks(params) {
    return request({
      url: '/system/tasks',
      method: 'get',
      params
    })
  },

  createSystemTask(data) {
    return request({
      url: '/system/tasks/create',
      method: 'post',
      data
    })
  },

  updateSystemTask(id, data) {
    return request({
      url: `/system/tasks/${id}`,
      method: 'put',
      data
    })
  },

  deleteSystemTask(id) {
    return request({
      url: `/system/tasks/${id}`,
      method: 'delete'
    })
  },

  executeSystemTask(id) {
    return request({
      url: `/system/tasks/${id}/execute`,
      method: 'post'
    })
  },

  getSystemTaskLogs(id) {
    return request({
      url: `/system/tasks/${id}/logs`,
      method: 'get'
    })
  },

  // 系统通知
  getSystemNotifications(params) {
    return request({
      url: '/system/notifications',
      method: 'get',
      params
    })
  },

  markNotificationAsRead(id) {
    return request({
      url: `/system/notifications/${id}/read`,
      method: 'put'
    })
  },

  markAllNotificationsAsRead() {
    return request({
      url: '/system/notifications/read-all',
      method: 'put'
    })
  },

  deleteNotification(id) {
    return request({
      url: `/system/notifications/${id}`,
      method: 'delete'
    })
  },

  // 审计日志
  getAuditLogs(params) {
    return request({
      url: '/system/audit/logs',
      method: 'get',
      params
    })
  },

  exportAuditLogs(params) {
    return request({
      url: '/system/audit/logs/export',
      method: 'get',
      params,
      responseType: 'blob'
    })
  },

  // 健康检查
  getHealthCheck() {
    return request({
      url: '/system/health/check',
      method: 'get'
    })
  },

  getDetailedHealthCheck() {
    return request({
      url: '/system/health/detailed',
      method: 'get'
    })
  },

  // 资源使用
  getResourceUsage() {
    return request({
      url: '/system/resources/usage',
      method: 'get'
    })
  },

  getResourceHistory(params) {
    return request({
      url: '/system/resources/history',
      method: 'get',
      params
    })
  },

  // 备份恢复
  restoreBackup(data) {
    return request({
      url: '/system/backup/restore',
      method: 'post',
      data,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  verifyBackup(id) {
    return request({
      url: `/system/backup/verify/${id}`,
      method: 'post'
    })
  },

  // 清理操作
  cleanupTempFiles() {
    return request({
      url: '/system/cleanup/temp',
      method: 'post'
    })
  },

  cleanupOldLogs() {
    return request({
      url: '/system/cleanup/logs',
      method: 'post'
    })
  },

  cleanupOldBackups() {
    return request({
      url: '/system/cleanup/backups',
      method: 'post'
    })
  },

  // 监控告警
  getMonitoringAlerts(params) {
    return request({
      url: '/system/monitoring/alerts',
      method: 'get',
      params
    })
  },

  createMonitoringAlert(data) {
    return request({
      url: '/system/monitoring/alerts/create',
      method: 'post',
      data
    })
  },

  updateMonitoringAlert(id, data) {
    return request({
      url: `/system/monitoring/alerts/${id}`,
      method: 'put',
      data
    })
  },

  deleteMonitoringAlert(id) {
    return request({
      url: `/system/monitoring/alerts/${id}`,
      method: 'delete'
    })
  },

  // API统计
  getApiStats(params) {
    return request({
      url: '/system/api/stats',
      method: 'get',
      params
    })
  },

  getApiErrors(params) {
    return request({
      url: '/system/api/errors',
      method: 'get',
      params
    })
  },

  getApiLatency(params) {
    return request({
      url: '/system/api/latency',
      method: 'get',
      params
    })
  }
}