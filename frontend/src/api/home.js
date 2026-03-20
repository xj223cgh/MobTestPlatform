/** 首页 API：统计数据、最近活动。 */
import request from "@/utils/request";

export function getHomeStats() {
  return request({
    url: "/home/stats",
    method: "get",
  });
}

export function getRecentActivities(params = {}) {
  return request({
    url: "/home/activities",
    method: "get",
    params,
  });
}

export function getTaskTrendData(params = {}) {
  return request({
    url: "/home/task-trend",
    method: "get",
    params,
  });
}

export function getDeviceStatusData() {
  return request({
    url: "/home/device-status",
    method: "get",
  });
}

export function getRecentProjects(params = {}) {
  return request({
    url: "/home/recent-projects",
    method: "get",
    params,
  });
}

export function getTaskStatusDistribution() {
  return request({
    url: "/home/task-status-distribution",
    method: "get",
  });
}
