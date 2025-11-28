import request from '@/utils/request'

/**
 * 获取项目列表
 * @param {Object} params 查询参数
 * @returns {Promise}
 */
export function getProjects(params) {
  return request({
    url: '/projects',
    method: 'get',
    params
  })
}

/**
 * 获取项目详情
 * @param {number} projectId 项目ID
 * @returns {Promise}
 */
export function getProject(projectId) {
  return request({
    url: `/projects/${projectId}`,
    method: 'get'
  })
}

/**
 * 创建项目
 * @param {Object} data 项目数据
 * @returns {Promise}
 */
export function createProject(data) {
  return request({
    url: '/projects',
    method: 'post',
    data
  })
}

/**
 * 更新项目
 * @param {number} projectId 项目ID
 * @param {Object} data 项目数据
 * @returns {Promise}
 */
export function updateProject(projectId, data) {
  return request({
    url: `/projects/${projectId}`,
    method: 'put',
    data
  })
}

/**
 * 删除项目
 * @param {number} projectId 项目ID
 * @returns {Promise}
 */
export function deleteProject(projectId) {
  return request({
    url: `/projects/${projectId}`,
    method: 'delete'
  })
}

/**
 * 获取项目成员列表
 * @param {number} projectId 项目ID
 * @returns {Promise}
 */
export function getProjectMembers(projectId) {
  return request({
    url: `/projects/${projectId}/members`,
    method: 'get'
  })
}

/**
 * 添加项目成员
 * @param {number} projectId 项目ID
 * @param {Object} data 成员数据
 * @returns {Promise}
 */
export function addProjectMember(projectId, data) {
  return request({
    url: `/projects/${projectId}/members`,
    method: 'post',
    data
  })
}

/**
 * 更新项目成员角色
 * @param {number} projectId 项目ID
 * @param {number} userId 用户ID
 * @param {Object} data 角色数据
 * @returns {Promise}
 */
export function updateProjectMemberRole(projectId, userId, data) {
  return request({
    url: `/projects/${projectId}/members/${userId}`,
    method: 'put',
    data
  })
}

/**
 * 移除项目成员
 * @param {number} projectId 项目ID
 * @param {number} userId 用户ID
 * @returns {Promise}
 */
export function removeProjectMember(projectId, userId) {
  return request({
    url: `/projects/${projectId}/members/${userId}`,
    method: 'delete'
  })
}

/**
 * 获取用户可访问的项目列表
 * @returns {Promise}
 */
export function getUserProjects() {
  return request({
    url: '/projects/my',
    method: 'get'
  })
}

/**
 * 获取项目的版本需求列表
 * @param {number} projectId 项目ID
 * @returns {Promise}
 */
export function getProjectVersionRequirements(projectId) {
  return request({
    url: `/projects/${projectId}/version-requirements`,
    method: 'get'
  })
}

/**
 * 创建版本需求
 * @param {number} projectId 项目ID
 * @param {Object} data 需求数据
 * @returns {Promise}
 */
export function createVersionRequirement(projectId, data) {
  return request({
    url: `/projects/${projectId}/version-requirements`,
    method: 'post',
    data
  })
}

/**
 * 更新版本需求
 * @param {number} projectId 项目ID
 * @param {number} requirementId 需求ID
 * @param {Object} data 需求数据
 * @returns {Promise}
 */
export function updateVersionRequirement(projectId, requirementId, data) {
  return request({
    url: `/projects/${projectId}/version-requirements/${requirementId}`,
    method: 'put',
    data
  })
}

/**
 * 删除版本需求
 * @param {number} projectId 项目ID
 * @param {number} requirementId 需求ID
 * @returns {Promise}
 */
export function deleteVersionRequirement(projectId, requirementId) {
  return request({
    url: `/projects/${projectId}/version-requirements/${requirementId}`,
    method: 'delete'
  })
}

/**
 * 获取项目的迭代列表
 * @param {number} projectId 项目ID
 * @returns {Promise}
 */
export function getProjectIterations(projectId) {
  return request({
    url: `/projects/${projectId}/iterations`,
    method: 'get'
  })
}

// 默认导出所有方法
export default {
  getProjects,
  getProject,
  createProject,
  updateProject,
  deleteProject,
  getProjectMembers,
  addProjectMember,
  updateProjectMemberRole,
  removeProjectMember,
  getUserProjects,
  getProjectVersionRequirements,
  createVersionRequirement,
  updateVersionRequirement,
  deleteVersionRequirement,
  getProjectIterations
}