import request from '@/utils/request'

/**
 * 创建AI生成测试用例的异步任务
 * @param {Object} data - 任务参数
 * @returns {Promise}
 */
export const createGenerateCasesTask = (data) => {
  return request({
    url: '/ai-tasks/generate-cases',
    method: 'post',
    data
  })
}

/**
 * 查询任务状态
 * @param {string} taskId - 任务ID
 * @returns {Promise}
 */
export const getTaskStatus = (taskId) => {
  return request({
    url: `/ai-tasks/task-status/${taskId}`,
    method: 'get'
  })
}

/**
 * 获取所有任务列表
 * @returns {Promise}
 */
export const getAllTasks = () => {
  return request({
    url: '/ai-tasks/tasks',
    method: 'get'
  })
}
