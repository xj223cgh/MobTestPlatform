<template>
  <div class="test-ai-page">
    <h1>AI接口测试页面</h1>
    <div class="test-form">
      <h2>测试配置</h2>
      <el-form
        :model="testForm"
        label-width="120px"
      >
        <el-form-item label="API基础URL">
          <el-input
            v-model="testForm.baseUrl"
            placeholder="请输入API基础URL"
          />
        </el-form-item>
        <el-form-item label="API密钥">
          <el-input
            v-model="testForm.apiKey"
            type="password"
            placeholder="请输入API密钥"
          />
        </el-form-item>
        <el-form-item label="模型名称">
          <el-input
            v-model="testForm.model"
            placeholder="请输入模型名称"
          />
        </el-form-item>
        <el-form-item label="测试提示词">
          <el-input
            v-model="testForm.prompt"
            type="textarea"
            :rows="3"
            placeholder="请输入测试提示词"
          />
        </el-form-item>
        <el-form-item label="温度">
          <el-input-number
            v-model="testForm.temperature"
            :min="0"
            :max="1"
            :step="0.1"
            placeholder="请输入温度"
          />
        </el-form-item>
        <el-form-item label="最大令牌数">
          <el-input-number
            v-model="testForm.maxTokens"
            :min="100"
            :max="32768"
            :step="100"
            placeholder="请输入最大令牌数"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            :loading="isLoading"
            :disabled="isLoading"
            @click="testAI"
          >
            {{ isLoading ? '测试中...' : '测试AI接口' }}
          </el-button>
          <el-button
            type="default"
            @click="resetForm"
          >
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>
    <div class="test-result">
      <h2>测试结果</h2>
      <div
        v-if="result.success"
        class="success"
      >
        <div class="result-header">
          <el-tag type="success">
            调用成功
          </el-tag>
          <span class="time">耗时: {{ result.time }}ms</span>
        </div>
        <div class="result-content">
          <h3>响应内容:</h3>
          <pre>{{ result.data }}</pre>
        </div>
      </div>
      <div
        v-else-if="result.error"
        class="error"
      >
        <div class="result-header">
          <el-tag type="danger">
            调用失败
          </el-tag>
          <span class="time">耗时: {{ result.time }}ms</span>
        </div>
        <div class="result-content">
          <h3>错误信息:</h3>
          <pre>{{ result.error }}</pre>
        </div>
      </div>
      <div
        v-else
        class="empty"
      >
        <p>请点击"测试AI接口"按钮开始测试</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import axios from 'axios';

// 测试表单数据
const testForm = reactive({
  baseUrl: import.meta.env.VITE_AI_API_BASE_URL || 'https://api.siliconflow.cn/v1',
  apiKey: import.meta.env.VITE_AI_API_KEY || '',
  model: 'deepseek-ai/DeepSeek-R1-0528-Qwen3-8B',
  prompt: '请生成一个某东app的登录/注册功能的测试用例',
  temperature: 0.3,
  maxTokens: 4096,
});

// 测试状态
const isLoading = ref(false);
const result = ref({
  success: false,
  error: null,
  data: '',
  time: 0,
});

// 测试AI接口
const testAI = async () => {
  try {
    isLoading.value = true;
    result.value = {
      success: false,
      error: null,
      data: '',
      time: 0,
    };

    // 记录开始时间
    const startTime = Date.now();

    // 创建axios实例
    const aiRequest = axios.create({
      baseURL: testForm.baseUrl,
      timeout: 60000,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${testForm.apiKey}`,
      },
    });

    // 发送请求
    const response = await aiRequest.post('/chat/completions', {
      model: testForm.model,
      messages: [
        {
          role: 'system',
          content: '你是一位专业的测试用例生成专家，请严格按照要求生成测试用例。',
        },
        {
          role: 'user',
          content: testForm.prompt,
        },
      ],
      temperature: testForm.temperature,
      max_tokens: testForm.maxTokens,
      response_format: { type: 'json_object' },
    });

    // 记录结束时间
    const endTime = Date.now();
    const duration = endTime - startTime;

    // 处理响应
    result.value = {
      success: true,
      error: null,
      data: JSON.stringify(response.data, null, 2),
      time: duration,
    };
  } catch (error) {
    // 记录结束时间
    const endTime = Date.now();
    const duration = endTime - startTime;

    // 处理错误
    let errorMessage = '未知错误';
    if (error.response) {
      // 服务器返回错误
      errorMessage = `HTTP ${error.response.status}: ${JSON.stringify(error.response.data, null, 2)}`;
    } else if (error.request) {
      // 请求发出但没有收到响应
      errorMessage = '没有收到服务器响应，请检查网络连接或API配置';
    } else {
      // 请求配置错误
      errorMessage = `请求配置错误: ${error.message}`;
    }

    result.value = {
      success: false,
      error: errorMessage,
      data: '',
      time: duration,
    };
  } finally {
    isLoading.value = false;
  }
};

// 重置表单
const resetForm = () => {
  Object.assign(testForm, {
    baseUrl: import.meta.env.VITE_AI_API_BASE_URL || 'https://api.siliconflow.cn/v1',
    apiKey: import.meta.env.VITE_AI_API_KEY || '',
    model: 'deepseek-ai/DeepSeek-R1-0528-Qwen3-8B',
    prompt: '请生成一个某东app的登录/注册功能的测试用例',
    temperature: 0.3,
    maxTokens: 4096,
  });
  result.value = {
    success: false,
    error: null,
    data: '',
    time: 0,
  };
};
</script>

<style scoped>
.test-ai-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}

.test-form {
  background-color: #f5f7fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.test-result {
  background-color: #f5f7fa;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

h2 {
  color: #409eff;
  margin-bottom: 15px;
  border-bottom: 1px solid #e4e7ed;
  padding-bottom: 10px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.time {
  color: #909399;
  font-size: 14px;
}

.result-content {
  background-color: white;
  padding: 15px;
  border-radius: 4px;
  overflow-x: auto;
}

pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  line-height: 1.5;
  color: #333;
}

.success .result-header {
  color: #67c23a;
}

.error .result-header {
  color: #f56c6c;
}

.empty {
  text-align: center;
  color: #909399;
  padding: 20px;
}

.el-form {
  max-width: 800px;
}

.el-form-item {
  margin-bottom: 20px;
}
</style>
