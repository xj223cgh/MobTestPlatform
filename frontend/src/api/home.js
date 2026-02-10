import request from "@/utils/request";

// 获取首页统计数据
export function getHomeStats() {
  return request({
    url: "/home/stats",
    method: "get",
  });
}

// 获取最近活动
export function getRecentActivities(params = {}) {
  return request({
    url: "/home/activities",
    method: "get",
    params,
  });
}

// 获取测试任务趋势数据
export function getTaskTrendData(params = {}) {
  return request({
    url: "/home/task-trend",
    method: "get",
    params,
  });
}

// 获取设备状态分布数据
export function getDeviceStatusData() {
  return request({
    url: "/home/device-status",
    method: "get",
  });
}

// 获取最近访问的项目
export function getRecentProjects(params = {}) {
  return request({
    url: "/home/recent-projects",
    method: "get",
    params,
  });
}

// 获取任务状态分布
export function getTaskStatusDistribution() {
  return request({
    url: "/home/task-status-distribution",
    method: "get",
  });
}
