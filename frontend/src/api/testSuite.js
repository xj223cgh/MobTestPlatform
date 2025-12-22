import request from "../utils/request";

// 获取测试套件列表
export const getTestSuiteList = (params) => {
  return request({
    url: "/test-suites",
    method: "get",
    params,
  });
};

// 获取测试套件树形结构
export const getTestSuiteTree = () => {
  return request({
    url: "/test-suites/tree",
    method: "get",
  });
};

// 获取测试套件详情
export const getTestSuiteDetail = (id) => {
  return request({
    url: `/test-suites/${id}`,
    method: "get",
  });
};

// 创建测试套件
export const createTestSuite = (data) => {
  return request({
    url: "/test-suites",
    method: "post",
    data,
  });
};

// 更新测试套件
export const updateTestSuite = (id, data) => {
  return request({
    url: `/test-suites/${id}`,
    method: "put",
    data,
  });
};

// 删除测试套件
export const deleteTestSuite = (id) => {
  return request({
    url: `/test-suites/${id}`,
    method: "delete",
  });
};

// 批量删除测试套件
export const batchDeleteTestSuites = (ids) => {
  return request({
    url: "/test-suites/batch-delete",
    method: "post",
    data: { ids },
  });
};

// 获取测试套件选项列表
export const getTestSuiteOptions = () => {
  return request({
    url: "/test-suites/options",
    method: "get",
  });
};

// 移动测试套件
export const moveTestSuite = (id, data) => {
  return request({
    url: `/test-suites/${id}/move`,
    method: "post",
    data,
  });
};

// 复制测试套件
export const copyTestSuite = (id, data = {}) => {
  return request({
    url: `/test-suites/${id}/copy`,
    method: "post",
    data,
  });
};

// Xmind相关功能已移除，暂时不再支持脑图实现

// 获取测试套件中的测试用例
export const getSuiteCases = (suiteId, params = {}) => {
  return request({
    url: `/test-suites/${suiteId}/test-cases`,
    method: "get",
    params,
  });
};

// 向测试套件添加测试用例
export const addCasesToSuite = (suiteId, caseIds) => {
  return request({
    url: `/test-suites/${suiteId}/test-cases`,
    method: "post",
    data: { caseIds },
  });
};

// 从测试套件移除测试用例
export const removeCasesFromSuite = (suiteId, caseIds) => {
  return request({
    url: `/test-suites/${suiteId}/test-cases`,
    method: "delete",
    data: { caseIds },
  });
};

// 获取可添加到测试套件的测试用例
export const getAvailableCases = (suiteId, params = {}) => {
  return request({
    url: `/test-suites/${suiteId}/available-test-cases`,
    method: "get",
    params,
  });
};

// 在测试套件之间移动测试用例
export const moveCasesBetweenSuites = (
  sourceSuiteId,
  caseIds,
  targetSuiteId,
) => {
  return request({
    url: `/test-suites/${sourceSuiteId}/move-to/${targetSuiteId}`,
    method: "post",
    data: { caseIds },
  });
};

// 获取测试套件的模块列表
export const getSuiteModules = (suiteId) => {
  return request({
    url: `/test-suites/${suiteId}/modules`,
    method: "get",
  });
};

// 获取项目的模块列表
export const getProjectModules = (projectId) => {
  return request({
    url: `/projects/${projectId}/modules`,
    method: "get",
  });
};

export const testSuiteApi = {
  getTestSuiteList,
  getTestSuiteTree,
  getTestSuiteDetail,
  createTestSuite,
  updateTestSuite,
  deleteTestSuite,
  batchDeleteTestSuites,
  getTestSuiteOptions,
  moveTestSuite,
  copyTestSuite,
  getSuiteCases,
  addCasesToSuite,
  removeCasesFromSuite,
  getAvailableCases,
  moveCasesBetweenSuites,
  getSuiteModules,
  getProjectModules,
};
