/** 知识库 API：文档上传、列表、删除、检索。 */
import request from '@/utils/request'

export const uploadKnowledgeDocument = (formData) => {
  return request({
    url: '/knowledge/upload',
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const listKnowledgeDocuments = () => {
  return request({
    url: '/knowledge/list',
    method: 'get'
  })
}

export const deleteKnowledgeDocument = (docId) => {
  return request({
    url: `/knowledge/delete/${docId}`,
    method: 'delete'
  })
}

export const searchKnowledge = (data) => {
  return request({
    url: '/knowledge/search',
    method: 'post',
    data
  })
}
