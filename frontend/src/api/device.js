import request from '@/utils/request'

// 获取设备列表
export function getDeviceList(params) {
  return request({
    url: '/devices',
    method: 'get',
    params
  })
}

// 获取设备详情
export function getDeviceDetail(id) {
  return request({
    url: `/devices/${id}`,
    method: 'get'
  })
}

// 创建设备
export function createDevice(data) {
  return request({
    url: '/devices',
    method: 'post',
    data
  })
}

// 更新设备
export function updateDevice(id, data) {
  return request({
    url: `/devices/${id}`,
    method: 'put',
    data
  })
}

// 删除设备
export function deleteDevice(id) {
  return request({
    url: `/devices/${id}`,
    method: 'delete'
  })
}

// 获取设备统计信息
export function getDeviceStats() {
  return request({
    url: '/devices/stats',
    method: 'get'
  })
}

// 连接设备
export function connectDevice(id) {
  return request({
    url: `/devices/${id}/connect`,
    method: 'post'
  })
}

// 断开设备连接
export function disconnectDevice(id) {
  return request({
    url: `/devices/${id}/disconnect`,
    method: 'post'
  })
}

// 获取设备状态
export function getDeviceStatus(id) {
  return request({
    url: `/devices/${id}/status`,
    method: 'get'
  })
}

// 刷新设备状态
export function refreshDeviceStatus(id) {
  return request({
    url: `/devices/${id}/refresh`,
    method: 'post'
  })
}

// 批量刷新设备状态
export function batchRefreshDeviceStatus() {
  return request({
    url: '/devices/refresh-all',
    method: 'post'
  })
}

// 安装应用到设备
export function installAppToDevice(deviceId, appPath) {
  return request({
    url: `/devices/${deviceId}/install-app`,
    method: 'post',
    data: { app_path: appPath }
  })
}

// 卸载设备应用
export function uninstallAppFromDevice(deviceId, packageName) {
  return request({
    url: `/devices/${deviceId}/uninstall-app`,
    method: 'post',
    data: { package_name: packageName }
  })
}

// 获取设备已安装应用列表
export function getDeviceApps(deviceId) {
  return request({
    url: `/devices/${deviceId}/apps`,
    method: 'get'
  })
}

// 获取设备截图
export function getDeviceScreenshot(deviceId) {
  return request({
    url: `/devices/${deviceId}/screenshot`,
    method: 'get',
    responseType: 'blob'
  })
}

// 执行设备命令
export function executeDeviceCommand(deviceId, command) {
  return request({
    url: `/devices/${deviceId}/execute`,
    method: 'post',
    data: { command }
  })
}

// 获取设备日志
export function getDeviceLogs(deviceId, params) {
  return request({
    url: `/devices/${deviceId}/logs`,
    method: 'get',
    params
  })
}

// 清理设备日志
export function clearDeviceLogs(deviceId) {
  return request({
    url: `/devices/${deviceId}/logs/clear`,
    method: 'post'
  })
}

// 获取设备性能数据
export function getDevicePerformance(deviceId, params) {
  return request({
    url: `/devices/${deviceId}/performance`,
    method: 'get',
    params
  })
}

// 重启设备
export function restartDevice(deviceId) {
  return request({
    url: `/devices/${deviceId}/restart`,
    method: 'post'
  })
}

// 锁定设备
export function lockDevice(deviceId) {
  return request({
    url: `/devices/${deviceId}/lock`,
    method: 'post'
  })
}

// 解锁设备
export function unlockDevice(deviceId) {
  return request({
    url: `/devices/${deviceId}/unlock`,
    method: 'post'
  })
}

// 获取设备信息
export function getDeviceInfo(deviceId) {
  return request({
    url: `/devices/${deviceId}/info`,
    method: 'get'
  })
}

// 搜索设备
export function searchDevices(keyword) {
  return request({
    url: '/devices/search',
    method: 'get',
    params: { keyword }
  })
}

// 批量删除设备
export function batchDeleteDevices(ids) {
  return request({
    url: '/devices/batch-delete',
    method: 'post',
    data: { ids }
  })
}

// 导出设备数据
export function exportDevices(params) {
  return request({
    url: '/devices/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}

// 导入设备数据
export function importDevices(file) {
  const formData = new FormData()
  formData.append('file', file)
  
  return request({
    url: '/devices/import',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 获取设备组列表
export function getDeviceGroups() {
  return request({
    url: '/devices/groups',
    method: 'get'
  })
}

// 创建设备组
export function createDeviceGroup(data) {
  return request({
    url: '/devices/groups',
    method: 'post',
    data
  })
}

// 更新设备组
export function updateDeviceGroup(id, data) {
  return request({
    url: `/devices/groups/${id}`,
    method: 'put',
    data
  })
}

// 删除设备组
export function deleteDeviceGroup(id) {
  return request({
    url: `/devices/groups/${id}`,
    method: 'delete'
  })
}

// 将设备添加到组
export function addDeviceToGroup(deviceId, groupId) {
  return request({
    url: `/devices/${deviceId}/groups/${groupId}`,
    method: 'post'
  })
}

// 从组中移除设备
export function removeDeviceFromGroup(deviceId, groupId) {
  return request({
    url: `/devices/${deviceId}/groups/${groupId}`,
    method: 'delete'
  })
}