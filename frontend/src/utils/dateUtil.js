/**
 * 日期格式化工具函数
 * @module dateUtil
 */

/**
 * 将ISO格式日期转换为年月日 时分秒格式
 * @param {string|Date} date - ISO格式日期字符串或Date对象
 * @returns {string} 格式化后的日期字符串，如：2023-01-01 00:00:00
 */
export const formatDateTime = (date) => {
  if (!date) return "";

  const d = typeof date === "string" ? new Date(date) : date;

  // 检查日期是否有效
  if (isNaN(d.getTime())) return "";

  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  const hours = String(d.getHours()).padStart(2, "0");
  const minutes = String(d.getMinutes()).padStart(2, "0");
  const seconds = String(d.getSeconds()).padStart(2, "0");

  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
};

/**
 * 将ISO格式日期转换为年月日格式
 * @param {string|Date} date - ISO格式日期字符串或Date对象
 * @returns {string} 格式化后的日期字符串，如：2023-01-01
 */
export const formatDate = (date) => {
  if (!date) return "";

  const d = typeof date === "string" ? new Date(date) : date;

  // 检查日期是否有效
  if (isNaN(d.getTime())) return "";

  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");

  return `${year}-${month}-${day}`;
};

/**
 * 将ISO格式日期转换为时分秒格式
 * @param {string|Date} date - ISO格式日期字符串或Date对象
 * @returns {string} 格式化后的时间字符串，如：00:00:00
 */
export const formatTime = (date) => {
  if (!date) return "";

  const d = typeof date === "string" ? new Date(date) : date;

  // 检查日期是否有效
  if (isNaN(d.getTime())) return "";

  const hours = String(d.getHours()).padStart(2, "0");
  const minutes = String(d.getMinutes()).padStart(2, "0");
  const seconds = String(d.getSeconds()).padStart(2, "0");

  return `${hours}:${minutes}:${seconds}`;
};
