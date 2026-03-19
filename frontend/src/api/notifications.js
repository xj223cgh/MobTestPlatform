import request from "@/utils/request";

const BASE = "/notifications";

/** 分页列表，支持 type、is_read、time_range(1d|1w|1m|3m|older) */
export function getNotifications(params) {
  return request({
    url: BASE,
    method: "get",
    params: {
      page: params?.page ?? 1,
      size: params?.size ?? 10,
      type: params?.type ?? undefined,
      is_read: params?.is_read,
      time_range: params?.time_range,
    },
  });
}

export function getUnreadCount() {
  return request({
    url: `${BASE}/unread-count`,
    method: "get",
  });
}

/** 单条已读或切换已读。body: { is_read: true|false }，不传则设为已读 */
export function markRead(id, body) {
  return request({
    url: `${BASE}/${id}/read`,
    method: "patch",
    data: body !== undefined ? body : {},
  });
}

/** 单条删除（软删除） */
export function deleteNotification(id) {
  return request({
    url: `${BASE}/${id}`,
    method: "delete",
  });
}

/** 置顶/取消置顶。body: { is_pinned: true|false } */
export function pinNotification(id, body) {
  return request({
    url: `${BASE}/${id}/pin`,
    method: "patch",
    data: body,
  });
}

export function markReadAll() {
  return request({
    url: `${BASE}/read-all`,
    method: "post",
  });
}

export function markUnreadAll() {
  return request({
    url: `${BASE}/unread-all`,
    method: "post",
  });
}

/** 按时间范围清理已读（软删除） */
export function clearRead(timeRange) {
  return request({
    url: `${BASE}/clear`,
    method: "post",
    data: { time_range: timeRange },
  });
}
