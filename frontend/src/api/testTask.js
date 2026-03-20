/** 测试任务 API：CRUD、目录、执行。 */
import request from "@/utils/request";

export function getTestTaskList(params) {
  return request({
    url: "/test-tasks",
    method: "get",
    params,
  });
}

export function getTestTaskDetail(id) {
  return request({
    url: `/test-tasks/${id}`,
    method: "get",
  });
}

export function createTestTask(data) {
  return request({
    url: "/test-tasks",
    method: "post",
    data,
  });
}

export function updateTestTask(id, data) {
  return request({
    url: `/test-tasks/${id}`,
    method: "put",
    data,
  });
}

export function deleteTestTask(id) {
  return request({
    url: `/test-tasks/${id}`,
    method: "delete",
  });
}

export function executeTestTask(id) {
  return request({
    url: `/test-tasks/${id}/execute`,
    method: "post",
  });
}

export function pauseTestTask(id) {
  return request({
    url: `/test-tasks/${id}/pause`,
    method: "post",
  });
}

export function resumeTestTask(id) {
  return request({
    url: `/test-tasks/${id}/resume`,
    method: "post",
  });
}

// 设备脚本任务可传 data.result 写入执行结果供报告使用
export function completeTestTask(id, data) {
  return request({
    url: `/test-tasks/${id}/complete`,
    method: "post",
    data: data || undefined,
  });
}

export function cancelTestTask(id) {
  return request({
    url: `/test-tasks/${id}/cancel`,
    method: "post",
  });
}

export function getTaskExecutions(taskId, params) {
  return request({
    url: `/test-tasks/${taskId}/executions`,
    method: "get",
    params,
  });
}

export function updateCaseExecution(taskId, caseId, data) {
  return request({
    url: `/test-tasks/${taskId}/executions/${caseId}`,
    method: "post",
    data,
  });
}

export function getTaskStatistics(taskId) {
  return request({
    url: `/test-tasks/${taskId}/statistics`,
    method: "get",
  });
}

export function getTaskDevices(taskId) {
  return request({
    url: `/test-tasks/${taskId}/devices`,
    method: "get",
  });
}

// ---------- 设备脚本异步执行（后端驱动，关闭页面任务继续执行） ----------

// 发起异步执行，返回 async task_id
export function startDeviceScriptExecution(taskId) {
  return request({
    url: `/test-tasks/${taskId}/execute-device-script-async`,
    method: "post",
  });
}

// 轮询异步任务状态（进度、终端日志、完成结果）
export function getDeviceScriptTaskStatus(taskId) {
  return request({
    url: `/test-tasks/${taskId}/device-script-task-status`,
    method: "get",
  });
}

export function getTaskTestCases(taskId) {
  return request({
    url: `/test-tasks/${taskId}/test-cases`,
    method: "get",
  });
}

export function getTaskOptions() {
  return request({
    url: "/test-tasks/options",
    method: "get",
  });
}

// ---------- 任务文件夹（按任务类型分开） ----------

export function getTaskFolderTree(taskType) {
  return request({
    url: "/test-tasks/task-folders",
    method: "get",
    params: { task_type: taskType },
  });
}

export function createTaskFolder(data) {
  return request({
    url: "/test-tasks/task-folders",
    method: "post",
    data,
  });
}

export function updateTaskFolder(id, data) {
  return request({
    url: `/test-tasks/task-folders/${id}`,
    method: "patch",
    data,
  });
}

export function deleteTaskFolder(id) {
  return request({
    url: `/test-tasks/task-folders/${id}`,
    method: "delete",
  });
}

export default {
  getTestTaskList,
  getTestTaskDetail,
  createTestTask,
  updateTestTask,
  deleteTestTask,
  executeTestTask,
  pauseTestTask,
  resumeTestTask,
  completeTestTask,
  cancelTestTask,
  getTaskExecutions,
  updateCaseExecution,
  getTaskStatistics,
  getTaskDevices,
  getTaskTestCases,
  getTaskOptions,
  startDeviceScriptExecution,
  getDeviceScriptTaskStatus,
  getTaskFolderTree,
  createTaskFolder,
  updateTaskFolder,
  deleteTaskFolder,
};
