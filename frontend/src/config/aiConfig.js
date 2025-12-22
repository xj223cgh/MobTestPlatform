// AI接口配置
export const aiConfig = {
  // AI服务商配置
  provider: "openai", // 支持 openai, anthropic, azure, 国内模型等

  // API配置
  baseURL: import.meta.env.VITE_AI_API_BASE_URL || "https://api.openai.com/v1",
  apiKey: import.meta.env.VITE_AI_API_KEY || "",

  // 模型配置
  model: "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B",
  temperature: 0.3,
  maxTokens: 4096,

  // 超时配置
  timeout: 120000, // 增加超时时间到120秒，适应大型模型响应较慢的情况
  retryCount: 2, // 减少重试次数到2次
};
