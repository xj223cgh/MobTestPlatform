# AI自动生成测试用例功能配置说明

## 功能概述

本项目实现了基于AI的测试用例自动生成功能，支持通过上传需求文档、填写需求描述，由AI模型自动生成高质量的测试用例。

## 配置文件说明

### 1. 环境变量配置

在项目根目录创建 `.env` 文件（如果已存在则直接修改），添加以下AI接口配置：

```env
# AI接口配置
VITE_AI_API_BASE_URL=https://api.openai.com/v1
VITE_AI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx

# 可选：代理配置（如果需要）
# VITE_AI_PROXY_URL=http://localhost:7890
```

**配置说明：**
- `VITE_AI_API_BASE_URL`：AI模型API的基础URL，默认使用OpenAI API
- `VITE_AI_API_KEY`：AI模型的API密钥，需要从对应AI服务商获取
- `VITE_AI_PROXY_URL`：可选的代理地址，用于访问AI API

### 2. AI配置文件

文件路径：`src/config/aiConfig.js`

```javascript
// AI接口配置
export const aiConfig = {
  // AI服务商配置
  provider: "openai", // 支持 openai, anthropic, azure, 国内模型等
  
  // 模型配置
  model: "gpt-4o",
  temperature: 0.3,
  maxTokens: 4096,
  
  // 超时配置
  timeout: 60000,
  retryCount: 3,
};
```

**可调整参数：**
- `provider`：AI服务商，支持openai、anthropic、azure等
- `model`：使用的AI模型，如gpt-4o、gpt-3.5-turbo等
- `temperature`：生成多样性，0-1之间，值越小越确定
- `maxTokens`：最大生成 tokens 数
- `temperature`：生成温度，值越大越随机
- `maxTokens`：最大生成令牌数

## 支持的文档格式

当前支持的需求文档格式：
- 文本文件：`.txt`
- PDF文件：`.pdf`（需要额外配置pdf.js）
- Word文档：`.docx`（需要额外配置docx库）

### 文档解析配置

文件路径：`src/utils/documentParser.js`

**注意：** PDF和DOCX解析功能需要额外安装依赖：

```bash
# 安装PDF解析依赖
npm install pdfjs-dist

# 安装DOCX解析依赖
npm install docx
```

## AI提示词配置

文件路径：`src/prompts/testCase.js`

```javascript
// 测试用例生成提示词模板
export const testCasePromptTemplates = {
  // 基础测试用例生成
  basic: `# 测试用例生成任务
  ...
  `,
  
  // 功能测试专用提示词
  functional: `# 功能测试用例生成任务
  ...
  `,
  
  // 回归测试专用提示词
  regression: `# 回归测试用例生成任务
  ...
  `
};
```

**配置说明：**
- 可根据项目测试规范修改提示词模板
- 可添加新的提示词模板，如安全测试、性能测试等
- 提示词中使用 `{变量名}` 格式定义动态替换内容

## 使用流程

1. **配置AI参数**：在 `.env` 文件中配置API密钥和基础URL
2. **上传需求文档**：支持TXT、PDF、DOCX格式
3. **填写需求信息**：选择项目、迭代、需求，填写用例集描述
4. **生成测试用例**：点击"生成用例"按钮，等待AI生成结果
5. **编辑优化用例**：在生成结果中编辑、删除、调整用例
6. **保存用例**：点击"保存所有用例"，将生成的用例保存到系统

## AI模型选择建议

### 推荐模型
- **OpenAI**：gpt-4o（最佳效果）、gpt-3.5-turbo（成本较低）
- **Anthropic**：claude-3-opus（长文本处理优秀）
- **国内模型**：通义千问、文心一言、豆包等

### 模型参数调优建议
- **功能测试**：temperature=0.3（确定性高）
- **探索性测试**：temperature=0.7（多样性高）
- **长文档**：maxTokens=8192（增加生成长度）

## 常见问题与解决方案

### 1. AI API调用失败
- **原因**：API密钥错误或网络问题
- **解决**：检查.env文件中的API密钥，确保网络通畅

### 2. 生成用例质量不高
- **原因**：提示词不够具体或模型参数不合适
- **解决**：修改`src/prompts/testCase.js`中的提示词模板，调整temperature参数

### 3. 文档解析失败
- **原因**：缺少对应文档解析库
- **解决**：安装pdfjs-dist或docx库，参考"文档解析配置"部分

## 扩展功能

### 1. 支持多模型切换
修改`src/config/aiConfig.js`中的provider和model配置

### 2. 自定义提示词模板
在`src/prompts/testCase.js`中添加新的提示词模板

### 3. 批量生成优化
修改`src/services/aiService.js`中的生成逻辑，支持批量生成多个用例集

## 安全注意事项

1. **API密钥保护**：
   - 不要将API密钥直接硬编码到代码中
   - 定期轮换API密钥
   - 生产环境使用环境变量或密钥管理服务

2. **数据安全**：
   - 敏感需求文档建议本地解析后再上传
   - 生产环境考虑使用后端转发AI请求

3. **合规性**：
   - 确保使用AI生成内容符合相关法律法规
   - 对生成的用例进行人工审核

## 版本更新记录

### v1.0.0
- 实现AI自动生成测试用例功能
- 支持OpenAI模型
- 支持TXT文档解析
- 生成结果可视化编辑

### v1.1.0
- 支持PDF和DOCX文档解析
- 支持多模型切换
- 优化生成用例的质量

## 联系与支持

如有配置问题或功能需求，欢迎联系技术团队。
