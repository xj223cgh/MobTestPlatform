/** AI 任务 API：用例生成、状态查询。 */
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
 * 查询指定用例集是否正在AI生成中（脑图页进入时用于显示“等待生成后查看”）
 * @param {number} suiteId - 用例集ID
 * @returns {Promise<{ data: { generating: boolean, task_id?: string } }>}
 */
export const getSuiteGeneratingStatus = (suiteId) => {
  return request({
    url: `/ai-tasks/suite/${suiteId}/generating`,
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
