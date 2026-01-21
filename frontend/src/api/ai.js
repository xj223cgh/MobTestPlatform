import axios from "axios";
import { aiConfig } from "@/config/aiConfig";

// 创建AI专用axios实例
const aiRequest = axios.create({
  baseURL: aiConfig.baseURL,
  timeout: aiConfig.timeout,
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${aiConfig.apiKey}`,
  },
});

// 重试请求函数
const retryRequest = async (
  fn,
  retries = aiConfig.retryCount,
  requestName = "未知请求",
) => {
  try {
    console.log(`[AI API] 开始执行${requestName}，重试次数:`, retries);
    const result = await fn();
    console.log(`[AI API] ${requestName}执行成功`);
    return result;
  } catch (error) {
    if (retries <= 0) {
      console.error(
        `[AI API] ${requestName}所有重试均失败:`,
        error.response?.data || error.message || error,
      );
      throw error;
    }

    const retryNumber = aiConfig.retryCount - retries + 1;
    console.log(
      `[AI API] ${requestName}请求失败，正在重试... (${retryNumber}/${aiConfig.retryCount})`,
      error.response?.data || error.message || error,
    );

    // 指数退避策略
    const delay = 1000 * Math.pow(2, aiConfig.retryCount - retries);
    console.log(`[AI API] 重试延迟:`, delay, "ms");
    await new Promise((resolve) => setTimeout(resolve, delay));

    return retryRequest(fn, retries - 1, requestName);
  }
};

// 生成测试用例
export const generateTestCases = async (prompt) => {
  return retryRequest(
    async () => {
      console.log("[AI API] 生成测试用例请求参数:", {
        model: aiConfig.model,
        temperature: aiConfig.temperature,
        max_tokens: aiConfig.maxTokens,
        response_format: { type: "json_object" },
      });

      const response = await aiRequest.post("/chat/completions", {
        model: aiConfig.model,
        messages: [
          {
            role: "system",
            content:
              "你是一位专业的测试用例生成专家，擅长根据需求文档生成高质量、全面的测试用例。请严格按照要求的JSON格式输出，不要添加任何额外的解释或说明。",
          },
          { role: "user", content: prompt },
        ],
        temperature: aiConfig.temperature,
        max_tokens: aiConfig.maxTokens,
        response_format: { type: "json_object" },
      });

      console.log(
        "[AI API] 生成测试用例响应状态:",
        response.status,
        "耗时:",
        response.config?.meta?.requestStartTime
          ? `${Date.now() - response.config.meta.requestStartTime}ms`
          : "未知",
      );
      console.log(
        "[AI API] 响应数据包含choices:",
        response.data?.choices?.length > 0,
      );

      return response.data;
    },
    aiConfig.retryCount,
    "生成测试用例",
  );
};

// 生成单个测试用例
export const generateSingleTestCase = async (prompt) => {
  return retryRequest(
    async () => {
      console.log("[AI API] 生成单个测试用例请求参数:", {
        model: aiConfig.model,
        temperature: aiConfig.temperature,
        max_tokens: 2048,
        response_format: { type: "json_object" },
      });

      const response = await aiRequest.post("/chat/completions", {
        model: aiConfig.model,
        messages: [
          {
            role: "system",
            content:
              "你是一位专业的测试用例生成专家，擅长根据需求生成高质量的单个测试用例。请严格按照要求的JSON格式输出，不要添加任何额外的解释或说明。",
          },
          { role: "user", content: prompt },
        ],
        temperature: aiConfig.temperature,
        max_tokens: 2048,
        response_format: { type: "json_object" },
      });

      console.log(
        "[AI API] 生成单个测试用例响应状态:",
        response.status,
        "耗时:",
        response.config?.meta?.requestStartTime
          ? `${Date.now() - response.config.meta?.requestStartTime}ms`
          : "未知",
      );
      console.log(
        "[AI API] 响应数据包含choices:",
        response.data?.choices?.length > 0,
      );

      return response.data;
    },
    aiConfig.retryCount,
    "生成单个测试用例",
  );
};

// 请求拦截器 - 添加请求开始时间
aiRequest.interceptors.request.use((config) => {
  config.meta = config.meta || {};
  config.meta.requestStartTime = Date.now();
  console.log(
    "[AI API] 请求开始:",
    config.url,
    "方法:",
    config.method.toUpperCase(),
  );
  return config;
});

// 响应拦截器 - 添加响应耗时
aiRequest.interceptors.response.use((response) => {
  const duration = Date.now() - response.config.meta.requestStartTime;
  response.config.meta.duration = duration;
  console.log(
    "[AI API] 请求结束:",
    response.config.url,
    "耗时:",
    duration,
    "ms",
  );
  return response;
});
