import request from '@/utils/request'

// 获取用户列表
export function getUserList(params) {
  return request({
    url: '/users',
    method: 'get',
    params
  })
}

// 获取用户详情
export function getUserDetail(id) {
  return request({
    url: `/users/${id}`,
    method: 'get'
  })
}

// 创建用户
export function createUser(data) {
  return request({
    url: '/users',
    method: 'post',
    data
  })
}

// 更新用户
export function updateUser(id, data) {
  return request({
    url: `/users/${id}`,
    method: 'put',
    data
  })
}

// 删除用户
export function deleteUser(id) {
  return request({
    url: `/users/${id}`,
    method: 'delete'
  })
}

// 切换用户状态
export function toggleUserStatus(id) {
  return request({
    url: `/users/${id}/toggle-status`,
    method: 'post'
  })
}

// 重置用户密码
export function resetUserPassword(id, data) {
  return request({
    url: `/users/${id}/reset-password`,
    method: 'post',
    data
  })
}

// 批量删除用户
export function batchDeleteUsers(ids) {
  return request({
    url: '/users/batch-delete',
    method: 'post',
    data: { ids }
  })
}

// 导出用户数据
export function exportUsers(params) {
  return request({
    url: '/users/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}

// 导入用户数据
export function importUsers(file) {
  const formData = new FormData()
  formData.append('file', file)
  
  return request({
    url: '/users/import',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 获取用户统计信息
export function getUserStats() {
  return request({
    url: '/users/stats',
    method: 'get'
  })
}

// 搜索用户
export function searchUsers(keyword) {
  return request({
    url: '/users/search',
    method: 'get',
    params: { keyword }
  })
}

// 默认导出所有方法
export default {
  getUserList,
  getUserDetail,
  createUser,
  updateUser,
  deleteUser,
  toggleUserStatus,
  resetUserPassword,
  batchDeleteUsers,
  exportUsers,
  importUsers,
  getUserStats,
  searchUsers
}