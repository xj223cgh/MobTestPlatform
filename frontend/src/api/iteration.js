import request from "@/utils/request";

/**
 * 获取迭代列表
 * @param {Object} params 查询参数
 * @returns {Promise}
 */
export function getIterations(params) {
  return request({
    url: "/iterations",
    method: "get",
    params,
  });
}

/**
 * 获取项目的迭代列表
 * @param {number} projectId 项目ID
 * @param {Object} params 查询参数
 * @returns {Promise}
 */
export function getProjectIterations(projectId, params) {
  return request({
    url: `/projects/${projectId}/iterations`,
    method: "get",
    params,
  });
}

/**
 * 获取迭代详情
 * @param {number} iterationId 迭代ID
 * @returns {Promise}
 */
export function getIteration(iterationId) {
  return request({
    url: `/iterations/${iterationId}`,
    method: "get",
  });
}

/**
 * 创建迭代
 * @param {Object} data 迭代数据
 * @returns {Promise}
 */
export function createIteration(data) {
  return request({
    url: "/iterations",
    method: "post",
    data,
  });
}

/**
 * 更新迭代
 * @param {number} iterationId 迭代ID
 * @param {Object} data 迭代数据
 * @returns {Promise}
 */
export function updateIteration(iterationId, data) {
  return request({
    url: `/iterations/${iterationId}`,
    method: "put",
    data,
  });
}

/**
 * 删除迭代
 * @param {number} iterationId 迭代ID
 * @returns {Promise}
 */
export function deleteIteration(iterationId) {
  return request({
    url: `/iterations/${iterationId}`,
    method: "delete",
  });
}

/**
 * 复制迭代
 * @param {number} iterationId 迭代ID
 * @param {Object} data 复制选项
 * @returns {Promise}
 */
export function copyIteration(iterationId, data) {
  return request({
    url: `/iterations/${iterationId}/copy`,
    method: "post",
    data,
  });
}

/**
 * 获取迭代统计信息
 * @param {number} iterationId 迭代ID
 * @returns {Promise}
 */
export function getIterationStats(iterationId) {
  return request({
    url: `/iterations/${iterationId}/stats`,
    method: "get",
  });
}

// 默认导出所有方法
export default {
  getIterations,
  getProjectIterations,
  getIteration,
  createIteration,
  updateIteration,
  deleteIteration,
  copyIteration,
  getIterationStats,
};
