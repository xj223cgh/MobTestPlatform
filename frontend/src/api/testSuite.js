/** 用例集 API：目录树、CRUD、回收站、导入导出。 */
import request from "@/utils/request";

export const getTestSuiteList = (params) => {
  return request({
    url: "/test-suites",
    method: "get",
    params,
  });
};

export const getTestSuiteTree = () => {
  return request({
    url: "/test-suites/tree",
    method: "get",
  });
};

export const getTestSuiteDetail = (id) => {
  return request({
    url: `/test-suites/${id}`,
    method: "get",
  });
};

export const createTestSuite = (data) => {
  return request({
    url: "/test-suites",
    method: "post",
    data,
  });
};

export const updateTestSuite = (id, data) => {
  return request({
    url: `/test-suites/${id}`,
    method: "put",
    data,
  });
};

// 逻辑删除入回收站 或 彻底删除
export const deleteTestSuite = (id, data = {}) => {
  return request({
    url: `/test-suites/${id}`,
    method: "delete",
    data: Object.keys(data).length ? data : undefined,
  });
};

export const batchDeleteTestSuites = (ids) => {
  return request({
    url: "/test-suites/batch-delete",
    method: "post",
    data: { ids },
  });
};

export const getTestSuiteOptions = () => {
  return request({
    url: "/test-suites/options",
    method: "get",
  });
};

export const moveTestSuite = (id, data) => {
  return request({
    url: `/test-suites/${id}/move`,
    method: "post",
    data,
  });
};

export const copyTestSuite = (id, data = {}) => {
  return request({
    url: `/test-suites/${id}/copy`,
    method: "post",
    data,
  });
};

export const getSuiteCases = (suiteId, params = {}) => {
  return request({
    url: `/test-suites/${suiteId}/test-cases`,
    method: "get",
    params,
  });
};

// 不含用例集，支持 project_id 筛选
export const getFolderTree = (params = {}) => {
  return request({
    url: "/test-suites/folder-tree",
    method: "get",
    params,
  });
};

// 支持 project_id 筛选
export const getCaseSets = (folderId, params = {}) => {
  return request({
    url: `/test-suites/${folderId}/case-sets`,
    method: "get",
    params,
  });
};

export const getRecycledSuites = (params = {}) => {
  return request({
    url: "/test-suites/recycled",
    method: "get",
    params,
  });
};

export const restoreRecycledSuite = (suiteId) => {
  return request({
    url: `/test-suites/recycled/${suiteId}/restore`,
    method: "post",
  });
};

export const batchPermanentDeleteRecycledSuites = (ids) => {
  return request({
    url: "/test-suites/recycled/batch-permanent-delete",
    method: "post",
    data: { ids },
  });
};

export const importTestSuite = (formData) => {
  return request({
    url: "/test-suites/import",
    method: "post",
    data: formData,
  });
};

/** 下载用例导入 Excel 模板（.xlsx blob，走 Cookie 鉴权） */
export const downloadTestSuiteImportTemplate = () => {
  return request({
    url: "/test-suites/import-template",
    method: "get",
    responseType: "blob",
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
