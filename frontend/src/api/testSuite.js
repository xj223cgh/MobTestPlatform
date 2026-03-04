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

// 删除测试套件（逻辑删除入回收站 或 彻底删除）
export const deleteTestSuite = (id, data = {}) => {
  return request({
    url: `/test-suites/${id}`,
    method: "delete",
    data: Object.keys(data).length ? data : undefined,
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

// 获取测试套件中的测试用例
export const getSuiteCases = (suiteId, params = {}) => {
  return request({
    url: `/test-suites/${suiteId}/test-cases`,
    method: "get",
    params,
  });
};

// 获取纯文件夹树（不含用例集），支持 project_id 筛选
export const getFolderTree = (params = {}) => {
  return request({
    url: "/test-suites/folder-tree",
    method: "get",
    params,
  });
};

// 获取文件夹下的用例集列表，支持 project_id 筛选
export const getCaseSets = (folderId, params = {}) => {
  return request({
    url: `/test-suites/${folderId}/case-sets`,
    method: "get",
    params,
  });
};

// 回收站：获取已逻辑删除的套件列表
export const getRecycledSuites = (params = {}) => {
  return request({
    url: "/test-suites/recycled",
    method: "get",
    params,
  });
};

// 回收站：恢复
export const restoreRecycledSuite = (suiteId) => {
  return request({
    url: `/test-suites/recycled/${suiteId}/restore`,
    method: "post",
  });
};

// 回收站：批量彻底删除
export const batchPermanentDeleteRecycledSuites = (ids) => {
  return request({
    url: "/test-suites/recycled/batch-permanent-delete",
    method: "post",
    data: { ids },
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
  getFolderTree,
  getCaseSets,
};
