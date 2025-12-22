import request from "@/utils/request";

/**
 * 用例评审相关API
 */

// 发起用例集评审
export const initiateReview = (suiteId, data) => {
  return request({
    url: `/review-tasks/test-suites/${suiteId}/initiate-review`,
    method: "post",
    data,
  });
};

// 获取评审任务详情
export const getReviewTask = (taskId) => {
  return request({
    url: `/review-tasks/${taskId}`,
    method: "get",
  });
};

// 更新单条用例评审意见
export const updateCaseReview = (taskId, caseId, data) => {
  return request({
    url: `/review-tasks/${taskId}/case-reviews/${caseId}`,
    method: "put",
    data,
  });
};

// 完成用例集评审
export const completeReview = (taskId, data) => {
  return request({
    url: `/review-tasks/${taskId}/complete`,
    method: "post",
    data,
  });
};

// 获取评审任务下的所有用例评审详情
export const getCaseReviews = (taskId) => {
  return request({
    url: `/review-tasks/${taskId}/case-reviews`,
    method: "get",
  });
};

// 获取当前用户的评审任务
export const getMyReviewTasks = (params) => {
  return request({
    url: "/review-tasks/review-center/my-tasks",
    method: "get",
    params,
  });
};

// 获取当前用户发起的评审
export const getMyInitiatedReviews = (params) => {
  return request({
    url: "/review-tasks/review-center/my-initiated",
    method: "get",
    params,
  });
};

// 获取用例集的评审状态和历史
export const getSuiteReviewStatus = (suiteId) => {
  return request({
    url: `/review-tasks/test-suites/${suiteId}/review-status`,
    method: "get",
  });
};

// 重新发起评审
export const reinitiateReview = (taskId) => {
  return request({
    url: `/review-tasks/${taskId}/reinitiate-review`,
    method: "post",
  });
};

// 打回评审
export const rejectReview = (taskId, data) => {
  return request({
    url: `/review-tasks/${taskId}/reject-review`,
    method: "post",
    data,
  });
};

// 重新评审
export const restartReview = (taskId) => {
  return request({
    url: `/review-tasks/${taskId}/restart-review`,
    method: "post",
  });
};

// 获取评审历史记录列表
export const getReviewHistoryList = (taskId) => {
  return request({
    url: `/review-tasks/${taskId}/review-history`,
    method: "get",
  });
};

// 获取评审历史详情
export const getReviewHistoryDetail = (historyId) => {
  return request({
    url: `/review-tasks/review-history/${historyId}`,
    method: "get",
  });
};
