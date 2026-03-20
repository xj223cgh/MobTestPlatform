/** 报告 API：列表、详情、生成、删除。 */
import request from "@/utils/request";

export const getReportList = (params) => {
  return request({
    url: "/reports",
    method: "get",
    params,
  });
};

export const getReportByRecordId = (reportId) => {
  return request({
    url: `/reports/record/${reportId}`,
    method: "get",
  });
};

export const manualGenerateReport = (taskId) => {
  return request({
    url: `/reports/generate/${taskId}`,
    method: "post",
  });
};

export const getReportData = (taskId, params = {}) => {
  return request({
    url: `/reports/${taskId}/data`,
    method: "get",
    params,
  });
};

export const deleteReport = (id) => {
  return request({
    url: `/reports/${id}`,
    method: "delete",
  });
};

export const batchDeleteReports = (ids) => {
  return request({
    url: "/reports/batch-delete",
    method: "post",
    data: { ids },
  });
};
