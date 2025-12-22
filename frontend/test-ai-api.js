#!/usr/bin/env node

/**
 * AI API测试脚本
 * 用于直接在命令行测试AI接口调用
 */

const axios = require('axios');
const fs = require('fs');
const path = require('path');

// 读取.env文件中的配置
const envPath = path.join(__dirname, '.env');
let envConfig = {};

if (fs.existsSync(envPath)) {
  const envContent = fs.readFileSync(envPath, 'utf-8');
  envContent.split('\n').forEach(line => {
    if (line && !line.startsWith('#')) {
      const [key, value] = line.split('=').map(item => item.trim());
      envConfig[key] = value;
    }
  });
}

// 测试配置
const config = {
  baseUrl: envConfig.VITE_AI_API_BASE_URL || 'https://api.siliconflow.cn/v1',
  apiKey: envConfig.VITE_AI_API_KEY || '',
  model: 'deepseek-ai/DeepSeek-R1-0528-Qwen3-8B',
  prompt: '请生成一个某东app的登录/注册功能的测试用例',
  temperature: 0.3,
  maxTokens: 4096,
  timeout: 60000,
};

// 显示配置信息
console.log('=== AI API测试配置 ===');
console.log(`API基础URL: ${config.baseUrl}`);
console.log(`API密钥: ${config.apiKey ? '已配置 (****' + config.apiKey.slice(-4) + ')' : '未配置'}`);
console.log(`模型名称: ${config.model}`);
console.log(`提示词: ${config.prompt.slice(0, 50)}${config.prompt.length > 50 ? '...' : ''}`);
console.log(`温度: ${config.temperature}`);
console.log(`最大令牌数: ${config.maxTokens}`);
console.log(`超时时间: ${config.timeout}ms`);
console.log('====================\n');

// 测试AI接口
const testAI = async () => {
  try {
    console.log('开始测试AI接口...');
    const startTime = Date.now();

    // 创建axios实例
    const aiRequest = axios.create({
      baseURL: config.baseUrl,
      timeout: config.timeout,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${config.apiKey}`,
      },
    });

    // 发送请求
    const response = await aiRequest.post('/chat/completions', {
      model: config.model,
      messages: [
        {
          role: 'system',
          content: '你是一位资深的软件测试工程师，请严格按照要求生成测试用例。',
        },
        {
          role: 'user',
          content: config.prompt,
        },
      ],
      temperature: config.temperature,
      max_tokens: config.maxTokens,
      response_format: { type: 'json_object' },
    });

    // 计算耗时
    const endTime = Date.now();
    const duration = endTime - startTime;

    console.log('\n=== 测试成功 ===');
    console.log(`耗时: ${duration}ms`);
    console.log('\n响应状态码:', response.status);
    console.log('\n响应数据:');
    console.log(JSON.stringify(response.data, null, 2));
    
  } catch (error) {
    console.error('\n=== 测试失败 ===');
    
    if (error.response) {
      // 服务器返回错误
      console.error('响应状态码:', error.response.status);
      console.error('错误数据:');
      console.error(JSON.stringify(error.response.data, null, 2));
    } else if (error.request) {
      // 请求发出但没有收到响应
      console.error('错误类型: 请求超时或网络错误');
      console.error('错误信息: 没有收到服务器响应，请检查网络连接或API配置');
    } else {
      // 请求配置错误
      console.error('错误类型: 请求配置错误');
      console.error('错误信息:', error.message);
    }
    
    console.error('\n完整错误:');
    console.error(error);
  }
};

// 执行测试
testAI();
