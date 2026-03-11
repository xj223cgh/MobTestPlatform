import request from "../utils/request";

// 获取报告列表（从 reports 表，分页）
export const getReportList = (params) => {
  return request({
    url: "/reports",
    method: "get",
    params,
  });
};

// 按报告 ID 获取详情（落库报告）
export const getReportByRecordId = (reportId) => {
  return request({
    url: `/reports/record/${reportId}`,
    method: "get",
  });
};

// 手动生成报告（对已完成任务落库）
export const manualGenerateReport = (taskId) => {
  return request({
    url: `/reports/generate/${taskId}`,
    method: "post",
  });
};

// 获取报告数据（按任务 ID 实时计算）
export const getReportData = (taskId, params = {}) => {
  return request({
    url: `/reports/${taskId}/data`,
    method: "get",
    params,
  });
};

// 删除报告
export const deleteReport = (id) => {
  return request({
    url: `/reports/${id}`,
    method: "delete",
  });
};

// 批量删除报告
export const batchDeleteReports = (ids) => {
  return request({
    url: "/reports/batch-delete",
    method: "post",
    data: { ids },
  });
};
