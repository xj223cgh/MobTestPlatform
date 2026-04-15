/** 设备 API：列表、ADB 操作、镜像、Agent 绑定。 */
import request from "@/utils/request";

// ---------- 基础 CRUD ----------

export function getDeviceList(params) {
  return request({
    url: "/devices",
    method: "get",
    params,
  });
}

export function getDeviceDetail(id) {
  return request({
    url: `/devices/${id}`,
    method: "get",
  });
}

export function createDevice(data) {
  return request({
    url: "/devices",
    method: "post",
    data,
  });
}

export function updateDevice(id, data) {
  return request({
    url: `/devices/${id}`,
    method: "put",
    data,
  });
}

export function deleteDevice(id) {
  return request({
    url: `/devices/${id}`,
    method: "delete",
  });
}

export function getDeviceStats() {
  return request({
    url: "/devices/stats",
    method: "get",
  });
}

// ---------- 连接与状态 ----------

export function connectDevice(id) {
  return request({
    url: `/devices/${id}/connect`,
    method: "post",
  });
}

export function disconnectDevice(id) {
  return request({
    url: `/devices/${id}/disconnect`,
    method: "post",
  });
}

export function getDeviceStatus(id) {
  return request({
    url: `/devices/${id}/status`,
    method: "get",
  });
}

export function refreshDeviceStatus(id) {
  return request({
    url: `/devices/${id}/refresh`,
    method: "post",
  });
}

export function batchRefreshDeviceStatus() {
  return request({
    url: "/devices/refresh-all",
    method: "post",
  });
}

// ---------- 应用与远程操作 ----------

export function installAppToDevice(deviceId, appPath) {
  return request({
    url: `/devices/${deviceId}/install-app`,
    method: "post",
    data: { app_path: appPath },
  });
}

export function uninstallAppFromDevice(deviceId, packageName) {
  return request({
    url: `/devices/${deviceId}/uninstall-app`,
    method: "post",
    data: { package_name: packageName },
  });
}

export function getDeviceApps(deviceId) {
  return request({
    url: `/devices/${deviceId}/apps`,
    method: "get",
  });
}

export function getDeviceScreenshot(deviceId) {
  return request({
    url: `/devices/${deviceId}/screenshot`,
    method: "get",
    responseType: "blob",
  });
}

export function executeDeviceCommand(deviceId, command) {
  return request({
    url: `/devices/${deviceId}/execute`,
    method: "post",
    data: { command },
  });
}

export function getDeviceLogs(deviceId, params) {
  return request({
    url: `/devices/${deviceId}/logs`,
    method: "get",
    params,
  });
}

export function clearDeviceLogs(deviceId) {
  return request({
    url: `/devices/${deviceId}/logs/clear`,
    method: "post",
  });
}

export function getDevicePerformance(deviceId, params) {
  return request({
    url: `/devices/${deviceId}/performance`,
    method: "get",
    params,
  });
}

export function restartDevice(deviceId) {
  return request({
    url: `/devices/${deviceId}/restart`,
    method: "post",
  });
}

export function lockDevice(deviceId) {
  return request({
    url: `/devices/${deviceId}/lock`,
    method: "post",
  });
}

export function unlockDevice(deviceId) {
  return request({
    url: `/devices/${deviceId}/unlock`,
    method: "post",
  });
}

export function getDeviceInfo(deviceId) {
  return request({
    url: `/devices/${deviceId}/info`,
    method: "get",
  });
}

// ---------- 批量操作与导入导出 ----------

export function searchDevices(keyword) {
  return request({
    url: "/devices/search",
    method: "get",
    params: { keyword },
  });
}

export function batchDeleteDevices(ids) {
  return request({
    url: "/devices/batch-delete",
    method: "post",
    data: { ids },
  });
}

export function exportDevices(params) {
  return request({
    url: "/devices/export",
    method: "get",
    params,
    responseType: "blob",
  });
}

export function importDevices(file) {
  const formData = new FormData();
  formData.append("file", file);

  return request({
    url: "/devices/import",
    method: "post",
    data: formData,
  });
}

// ---------- 设备分组 ----------

export function getDeviceGroups() {
  return request({
    url: "/devices/groups",
    method: "get",
  });
}

export function createDeviceGroup(data) {
  return request({
    url: "/devices/groups",
    method: "post",
    data,
  });
}

export function updateDeviceGroup(id, data) {
  return request({
    url: `/devices/groups/${id}`,
    method: "put",
    data,
  });
}

export function deleteDeviceGroup(id) {
  return request({
    url: `/devices/groups/${id}`,
    method: "delete",
  });
}

export function addDeviceToGroup(deviceId, groupId) {
  return request({
    url: `/devices/${deviceId}/groups/${groupId}`,
    method: "post",
  });
}

export function removeDeviceFromGroup(deviceId, groupId) {
  return request({
    url: `/devices/${deviceId}/groups/${groupId}`,
    method: "delete",
  });
}

// ---------- ADB 与任务执行 ----------

export function getAdbDevices() {
  return request({
    url: "/devices/adb/devices",
    method: "get",
  });
}

export function executeAdbCommand(command, options = {}) {
  return request({
    url: "/devices/adb/command",
    method: "post",
    data: { command },
    isHovering: options.isHovering,
  });
}

export function executeDeviceTask(deviceId, data) {
  return request({
    url: `/devices/${deviceId}/tasks`,
    method: "post",
    data,
  });
}

export function executeBatchTasks(data) {
  return request({
    url: "/devices/batch-tasks",
    method: "post",
    data,
  });
}

export function scheduleBatchTasks(data) {
  return request({
    url: "/devices/schedule-batch-tasks",
    method: "post",
    data,
  });
}

export default {
  getDeviceList,
  getDeviceDetail,
  createDevice,
  updateDevice,
  deleteDevice,
  getDeviceStats,
  connectDevice,
  disconnectDevice,
  getDeviceStatus,
  refreshDeviceStatus,
  batchRefreshDeviceStatus,
  installAppToDevice,
  uninstallAppFromDevice,
  getDeviceApps,
  getDeviceScreenshot,
  executeDeviceCommand,
  getDeviceLogs,
  clearDeviceLogs,
  getDevicePerformance,
  restartDevice,
  lockDevice,
  unlockDevice,
  getDeviceInfo,
  searchDevices,
  batchDeleteDevices,
  exportDevices,
  importDevices,
  getDeviceGroups,
  createDeviceGroup,
  updateDeviceGroup,
  deleteDeviceGroup,
  addDeviceToGroup,
  removeDeviceFromGroup,
  getAdbDevices,
  executeAdbCommand,
  executeDeviceTask,
  executeBatchTasks,
  scheduleBatchTasks,
};
