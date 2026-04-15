/** 用例评审 API：发起、审批、历史。 */
import request from "@/utils/request";

// ---------- 发起与完成 ----------

export const initiateReview = (suiteId, data) => {
  return request({
    url: `/review-tasks/test-suites/${suiteId}/initiate-review`,
    method: "post",
    data,
  });
};

export const getReviewTask = (taskId) => {
  return request({
    url: `/review-tasks/${taskId}`,
    method: "get",
  });
};

export const updateCaseReview = (taskId, caseId, data) => {
  return request({
    url: `/review-tasks/${taskId}/case-reviews/${caseId}`,
    method: "put",
    data,
  });
};

export const completeReview = (taskId, data) => {
  return request({
    url: `/review-tasks/${taskId}/complete`,
    method: "post",
    data,
  });
};

export const getCaseReviews = (taskId) => {
  return request({
    url: `/review-tasks/${taskId}/case-reviews`,
    method: "get",
  });
};

// ---------- 评审中心（我的任务 / 我发起的） ----------

export const getMyReviewTasks = (params) => {
  return request({
    url: "/review-tasks/review-center/my-tasks",
    method: "get",
    params,
  });
};

export const getMyInitiatedReviews = (params) => {
  return request({
    url: "/review-tasks/review-center/my-initiated",
    method: "get",
    params,
  });
};

export const getSuiteReviewStatus = (suiteId) => {
  return request({
    url: `/review-tasks/test-suites/${suiteId}/review-status`,
    method: "get",
  });
};

export const reinitiateReview = (taskId) => {
  return request({
    url: `/review-tasks/${taskId}/reinitiate-review`,
    method: "post",
  });
};

export const rejectReview = (taskId, data) => {
  return request({
    url: `/review-tasks/${taskId}/reject-review`,
    method: "post",
    data,
  });
};

export const restartReview = (taskId) => {
  return request({
    url: `/review-tasks/${taskId}/restart-review`,
    method: "post",
  });
};

// ---------- 评审历史 ----------

export const getRecentReviewHistory = (params) => {
  return request({
    url: "/review-tasks/review-center/recent-history",
    method: "get",
    params,
  });
};

export const getReviewHistoryList = (taskId) => {
  return request({
    url: `/review-tasks/${taskId}/review-history`,
    method: "get",
  });
};

export const getReviewHistoryDetail = (historyId) => {
  return request({
    url: `/review-tasks/review-history/${historyId}`,
    method: "get",
  });
};
