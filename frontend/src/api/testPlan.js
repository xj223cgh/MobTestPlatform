import request from '@/utils/request';

// 获取项目的测试计划列表
export const getProjectTestPlans = (projectId) => {
  return request({
    url: `/projects/${projectId}/test-plans`,
    method: 'get'
  });
};

// 获取迭代的测试计划列表
export const getIterationTestPlans = (iterationId) => {
  return request({
    url: `/iterations/${iterationId}/test-plans`,
    method: 'get'
  });
};

// 获取测试计划详情
export const getTestPlanDetail = (planId) => {
  return request({
    url: `/test-plans/${planId}`,
    method: 'get'
  });
};

// 创建测试计划
export const createTestPlan = (data) => {
  return request({
    url: '/test-plans',
    method: 'post',
    data
  });
};

// 更新测试计划
export const updateTestPlan = (planId, data) => {
  return request({
    url: `/test-plans/${planId}`,
    method: 'put',
    data
  });
};

// 删除测试计划
export const deleteTestPlan = (planId) => {
  return request({
    url: `/test-plans/${planId}`,
    method: 'delete'
  });
};

// 向测试计划添加测试用例
export const addTestCasesToPlan = (planId, data) => {
  return request({
    url: `/test-plans/${planId}/test-cases`,
    method: 'post',
    data
  });
};

// 从测试计划移除测试用例
export const removeTestCaseFromPlan = (planId, caseId) => {
  return request({
    url: `/test-plans/${planId}/test-cases/${caseId}`,
    method: 'delete'
  });
};

// 获取测试计划可用的测试用例列表
export const getAvailableTestCases = (planId, params) => {
  return request({
    url: `/test-plans/${planId}/available-test-cases`,
    method: 'get',
    params
  });
};

// 导出测试计划
export const exportTestPlan = (planId, format = 'excel') => {
  return request({
    url: `/test-plans/${planId}/export`,
    method: 'get',
    params: { format },
    responseType: 'blob'
  });
};

// 获取测试计划状态统计
export const getTestPlanStats = (planId) => {
  return request({
    url: `/test-plans/${planId}/stats`,
    method: 'get'
  });
};

export default {
  getProjectTestPlans,
  getIterationTestPlans,
  getTestPlanDetail,
  createTestPlan,
  updateTestPlan,
  deleteTestPlan,
  addTestCasesToPlan,
  removeTestCaseFromPlan,
  getAvailableTestCases,
  exportTestPlan,
  getTestPlanStats
};