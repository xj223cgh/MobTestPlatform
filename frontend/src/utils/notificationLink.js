/** 通知跳转：根据通知类型生成路由路径与展示格式。 */
/**
 * 校验并规范化关联 ID（DB 为整数；避免用 !id 误判 0）
 */
function parseRelatedId(raw) {
  if (raw === null || raw === undefined || raw === "") return null;
  const n = Number(raw);
  return Number.isFinite(n) ? n : null;
}

/**
 * 根据通知的 related_type、related_id 解析跳转路由。
 *
 * 与后端 notify_users(related_type, related_id) 约定对齐：
 * - project / iteration / version_requirement：实体主键 → 列表页 highlight
 * - user：users.id → user_id
 * - device：devices 表主键 → highlight_device_id（非 ADB 串号）
 * - review_task：test_suite_review_tasks.id → case-reviews?taskId=
 * - test_task：test_tasks.id → test-tasks?highlight_id=
 * - report：reports.id → 须 name=ReportDetailByRecord（勿用 /report/:id，否则会被当成 task_id）
 * - suite：test_suites.id（套件 type=suite）→ test-cases?suite_id=
 */
export function getNotificationRoute(notification) {
  const type = notification?.related_type;
  const id = parseRelatedId(notification?.related_id);
  if (id === null) return null;
  switch (type) {
    case "project":
      return { path: "/projects", query: { highlight_id: id } };
    case "iteration":
      return { path: "/iterations", query: { highlight_id: id } };
    case "version_requirement":
      return { path: "/requirements", query: { highlight_id: id } };
    case "user":
      return { path: "/users", query: { user_id: id } };
    case "device":
      return { path: "/devices", query: { highlight_device_id: id } };
    case "review_task":
      return { path: "/case-reviews", query: { taskId: id } };
    case "test_task":
      return { path: "/test-tasks", query: { highlight_id: id } };
    case "report":
      return { name: "ReportDetailByRecord", params: { id: String(id) } };
    case "suite":
      return { path: "/test-cases", query: { suite_id: id } };
    default:
      return null;
  }
}

/** 消息类型显示文案 */
export const NOTIFICATION_TYPE_LABELS = {
  ai_case_generated: "AI 用例生成",
  review_pending: "待评审",
  review_completed: "评审已完成",
  review_rejected: "评审被拒绝",
  review_restarted: "重新评审",
  task_started: "任务开始",
  task_completed: "任务完成",
  task_failed: "任务失败",
  report_generated: "报告已生成",
  user_registered: "用户注册",
  project_created: "项目负责人",
  project_owner_changed: "负责人变更",
  project_member_added: "加入项目",
  iteration_created: "新建迭代",
  iteration_updated: "迭代更新",
  requirement_created: "需求创建",
  requirement_assigned: "需求指派",
};

/** 评审相关状态英文 -> 中文（用于消息摘要展示） */
const REVIEW_STATUS_ZH = {
  pending: "待处理",
  in_review: "评审中",
  completed: "已完成",
  rejected: "已拒绝",
  approved: "通过",
};

/**
 * 格式化消息展示文案：评审类消息将状态等映射为中文并补充详情
 */
export function formatNotificationDisplay(row) {
  const type = row?.type || "";
  const summary = row?.summary || "";
  const extra = row?.extra || {};
  if (type.startsWith("review_")) {
    let text = summary;
    Object.entries(REVIEW_STATUS_ZH).forEach(([en, zh]) => {
      text = text.replace(new RegExp(en, "gi"), zh);
    });
    if (extra.suite_review_status) {
      const statusZh = REVIEW_STATUS_ZH[extra.suite_review_status] || extra.suite_review_status;
      if (!text.includes(statusZh)) text += `，结果：${statusZh}`;
    }
    return text;
  }
  return summary;
}
