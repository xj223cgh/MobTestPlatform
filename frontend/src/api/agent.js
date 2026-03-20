/** Agent API：绑定状态、绑定码、解绑、下载。 */
import request from "@/utils/request";

/** 获取当前用户的 Agent 绑定状态（带时间戳避免缓存，确保手动刷新拿到最新状态） */
export function getAgentBinding() {
  return request({
    url: "/agent/binding",
    method: "get",
    params: { _: Date.now() },
  });
}

/** 生成绑定码（供本机 Agent 输入完成绑定） */
export function createBindingCode() {
  return request({
    url: "/agent/binding-code",
    method: "post",
  });
}

/** 解除当前用户与本机 Agent 的绑定 */
export function unbindAgent() {
  return request({
    url: "/agent/unbind",
    method: "post",
  });
}

/** 查询是否支持下载 Agent 安装包（下载路径可选时使用） */
export function getAgentDownloadInfo() {
  return request({
    url: "/agent/download-info",
    method: "get",
  });
}

/** 查询是否支持由平台在服务器本机启动 Agent */
export function getAgentLaunchInfo() {
  return request({
    url: "/agent/launch-info",
    method: "get",
  });
}

/** 由平台在服务器本机启动 Agent 并自动绑定当前用户 */
export function launchAgent() {
  return request({
    url: "/agent/launch",
    method: "post",
  });
}

export default {
  getAgentBinding,
  createBindingCode,
  unbindAgent,
  getAgentDownloadInfo,
  getAgentLaunchInfo,
  launchAgent,
};
