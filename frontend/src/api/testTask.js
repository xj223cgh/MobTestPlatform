import request from "@/utils/request";

// 获取测试任务列表
export function getTestTaskList(params) {
  return request({
    url: "/test-tasks",
    method: "get",
    params,
  });
}

// 获取测试任务详情
export function getTestTaskDetail(id) {
  return request({
    url: `/test-tasks/${id}`,
    method: "get",
  });
}

// 创建测试任务
export function createTestTask(data) {
  return request({
    url: "/test-tasks",
    method: "post",
    data,
  });
}

// 更新测试任务
export function updateTestTask(id, data) {
  return request({
    url: `/test-tasks/${id}`,
    method: "put",
    data,
  });
}

// 删除测试任务
export function deleteTestTask(id) {
  return request({
    url: `/test-tasks/${id}`,
    method: "delete",
  });
}

// 执行测试任务
export function executeTestTask(id) {
  return request({
    url: `/test-tasks/${id}/execute`,
    method: "post",
  });
}

// 暂停测试任务
export function pauseTestTask(id) {
  return request({
    url: `/test-tasks/${id}/pause`,
    method: "post",
  });
}

// 恢复测试任务
export function resumeTestTask(id) {
  return request({
    url: `/test-tasks/${id}/resume`,
    method: "post",
  });
}

// 完成测试任务
export function completeTestTask(id) {
  return request({
    url: `/test-tasks/${id}/complete`,
    method: "post",
  });
}

// 取消测试任务
export function cancelTestTask(id) {
  return request({
    url: `/test-tasks/${id}/cancel`,
    method: "post",
  });
}

// 获取测试任务的执行结果列表
export function getTaskExecutions(taskId, params) {
  return request({
    url: `/test-tasks/${taskId}/executions`,
    method: "get",
    params,
  });
}

// 更新测试用例在任务中的执行状态
export function updateCaseExecution(taskId, caseId, data) {
  return request({
    url: `/test-tasks/${taskId}/executions/${caseId}`,
    method: "post",
    data,
  });
}

// 获取测试任务的统计信息
export function getTaskStatistics(taskId) {
  return request({
    url: `/test-tasks/${taskId}/statistics`,
    method: "get",
  });
}

// 获取测试任务关联的设备列表
export function getTaskDevices(taskId) {
  return request({
    url: `/test-tasks/${taskId}/devices`,
    method: "get",
  });
}

// 获取测试任务关联的测试用例列表
export function getTaskTestCases(taskId) {
  return request({
    url: `/test-tasks/${taskId}/test-cases`,
    method: "get",
  });
}

// 获取测试任务选项
export function getTaskOptions() {
  return request({
    url: "/test-tasks/options",
    method: "get",
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
};
