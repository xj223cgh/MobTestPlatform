# AI自动生成测试用例功能配置说明

## 功能概述

本项目实现了基于AI的测试用例自动生成功能，采用**后端异步任务架构**，支持：

✅ **先创建用例集** - 点击生成后立即创建用例集  
✅ **显示生成进度** - 实时显示AI生成进度和状态  
✅ **后台异步生成** - 生成过程在后台执行，不影响使用其他功能  
✅ **安全性提升** - AI API Key保存在后端，更安全  
✅ **实时进度反馈** - 每3秒更新任务状态和进度  

## 架构设计

### 新架构（当前使用）

```
用户操作 → 前端 → 后端异步任务 → AI API → 后端数据库
           ↓
    立即返回，继续使用
           ↓
    每3秒轮询任务状态
```

**技术栈**：
- 后端：Flask + Python threading
- 前端：Vue 3 + Element Plus
- AI服务：OpenAI兼容接口（如SiliconFlow）

### 核心组件

#### 后端组件

1. **任务管理器** - `backend/app/utils/task_manager.py`
   - 管理后台异步任务
   - 支持任务状态查询和进度更新
   - 线程安全的状态管理

2. **AI异步任务接口** - `backend/app/routes/ai_tasks.py`
   - `POST /api/ai-tasks/generate-cases` - 创建生成任务
   - `GET /api/ai-tasks/task-status/<task_id>` - 查询任务状态
   - `GET /api/ai-tasks/tasks` - 获取所有任务列表

#### 前端组件

1. **AI任务API** - `frontend/src/api/aiTasks.js`
   - 调用后端AI任务接口

2. **用例管理页面** - `frontend/src/views/testCase/TestCaseManagement.vue`
   - 用例集创建和管理
   - 任务状态轮询
   - 进度显示组件

3. **文档解析工具** - `frontend/src/utils/documentParser.js`
   - 支持 .docx、.pdf、.txt 文件解析

## 配置说明

### 1. 后端配置（必须）

编辑 `backend/.env` 文件，添加AI配置：

```env
# AI配置
AI_BASE_URL=https://api.siliconflow.cn/v1
AI_API_KEY=sk-your-actual-api-key-here
AI_MODEL=deepseek-ai/DeepSeek-R1-0528-Qwen3-8B
AI_TEMPERATURE=0.3
AI_MAX_TOKENS=4096
```

**配置参数说明**：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `AI_BASE_URL` | AI服务的基础URL | `https://api.siliconflow.cn/v1` |
| `AI_API_KEY` | AI服务的API密钥 | ⚠️ 必须配置 |
| `AI_MODEL` | 使用的AI模型 | `deepseek-ai/DeepSeek-R1-0528-Qwen3-8B` |
| `AI_TEMPERATURE` | 生成温度（0-1，越低越确定） | `0.3` |
| `AI_MAX_TOKENS` | 最大生成token数 | `4096` |

> ⚠️ **重要**：请将 `AI_API_KEY` 替换为您实际的API密钥

### 2. 支持的AI服务商和模型

#### SiliconFlow（推荐，国内访问快，有免费额度）

**免费模型（适合调试展示）**：

1. **Qwen/Qwen2.5-7B-Instruct**（最推荐）⭐⭐⭐⭐⭐
```env
AI_BASE_URL=https://api.siliconflow.cn/v1
AI_MODEL=Qwen/Qwen2.5-7B-Instruct
AI_TEMPERATURE=0.3
AI_MAX_TOKENS=4096
```
**特点**：免费额度大，中文能力强，指令遵循好

2. **deepseek-ai/DeepSeek-R1-Distill-Qwen-7B**（低成本）⭐⭐⭐⭐
```env
AI_MODEL=deepseek-ai/DeepSeek-R1-Distill-Qwen-7B
```
**特点**：蒸馏版本，成本极低，响应快

3. **Qwen/Qwen2.5-Coder-7B-Instruct**（代码理解强）⭐⭐⭐⭐
```env
AI_MODEL=Qwen/Qwen2.5-Coder-7B-Instruct
```
**特点**：擅长结构化输出，测试用例格式规范

**付费高性能模型**：

```env
AI_MODEL=deepseek-ai/DeepSeek-V3  # 性能强，成本相对低
# 或
AI_MODEL=deepseek-ai/DeepSeek-R1-0528-Qwen3-8B  # 平衡性能和成本
```

#### OpenAI（国际标准，需付费）
```env
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-4o  # 或 gpt-3.5-turbo（更便宜）
```

#### 其他兼容OpenAI格式的服务
```env
AI_BASE_URL=https://your-ai-service.com/v1
AI_MODEL=your-model-name
```

## 使用流程

### 1. 打开生成用例对话框

1. 进入"用例管理"页面
2. 点击"新增用例"按钮
3. 选择创建方式为"自动生成"

### 2. 填写表单信息

按照以下顺序填写：

#### a. 所属文件夹（必填）
- 点击输入框，在弹出的树形结构中选择文件夹
- 只能选择"文件夹"类型，不能选择"用例集"

#### b. 用例集名称（必填）
- **左侧**：点击查看已有用例集，避免重名
- **右侧**：输入新的用例集名称
- **验证**：失焦时自动检测是否重名

#### c. 所属项目（必填）
- 下拉选择项目
- 加载时显示"数据加载中..."

#### d. 所属迭代（必填）
- 下拉选择迭代
- 需要先选择项目

#### e. 所属需求（必填）
- 下拉选择需求
- 需要先选择迭代

#### f. 用例集描述（可选）
- 输入详细的需求描述
- 将作为AI生成的上下文信息

#### g. 需求文档上传（可选）
- 支持格式：`.docx`、`.pdf`、`.txt`
- 最大10MB
- AI会根据文档内容生成更精准的用例

### 3. 生成用例

点击"生成用例"按钮后：

1. ✅ 系统立即创建用例集（显示在左侧树中）
2. ✅ 显示生成进度界面
3. ✅ 您可以继续使用系统其他功能
4. ✅ 后台异步生成测试用例
5. ✅ 生成完成后自动刷新用例列表

### 4. 查看生成进度

在用例集页面会显示：
- 🔄 旋转的加载图标
- 📊 动态进度条（0-100%）
- 💬 当前状态消息
- 💡 提示：可以继续使用系统其他功能

### 5. 查看生成结果

- 生成完成后自动刷新显示
- 弹出成功提示，显示生成的用例数量
- 可以对生成的用例进行编辑和调整

## 支持的文档格式

### 文档类型

| 格式 | 支持 | 依赖库 |
|------|------|--------|
| `.txt` | ✅ | 无需依赖 |
| `.docx` | ✅ | mammoth |
| `.pdf` | ✅ | pdfjs-dist |
| `.doc` | ❌ | 不支持，请转换为.docx |

### 安装文档解析依赖

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install mammoth pdfjs-dist
```

## AI生成效果优化

### 1. 用例数量与准确性（当前实现）

- **数量随需求规模调整**：根据需求文档与描述的总长度估算建议用例数（约每 300 字对应 3 条，最少 8 条、最多约 80 条），在提示词中告知 AI，避免固定“5～10 条”导致大需求覆盖不足。
- **准确性约束**：提示词与 system 角色均要求“严格依据需求文档、步骤与预期结果需可追溯、不编造”，以提高生成用例与需求的一致性。
- **长文档不截断**：根据文档长度动态提高本次调用的 `max_tokens`（基础值 + 按长度追加，上限 16384），减少因输出被截断而少生成用例的情况。

以上逻辑均在 `backend/app/routes/ai_tasks.py` 中实现（`build_test_case_prompt`、`_suggest_case_count`、`call_ai_api` 及任务中的 `dynamic_max_tokens`）。

### 2. 提示词与模板

后端提示词位置：`backend/app/routes/ai_tasks.py` 中的 `build_test_case_prompt()`。

前端曾使用的模板位置（当前由后端统一构建）：`frontend/src/prompts/testCase.js`（若存在）。支持的模板类型可包括：functional、regression、performance、security 等。

### 3. 参数调优

**生成确定性高的用例**（推荐）：
```env
AI_TEMPERATURE=0.3
```

**生成多样性高的用例**：
```env
AI_TEMPERATURE=0.7
```

**处理长文档**：
```env
AI_MAX_TOKENS=8192
```

### 4. 模型选择对比表

| 模型 | 免费额度 | 中文能力 | 输出质量 | 响应速度 | 推荐度 | 适用场景 |
|------|---------|---------|---------|---------|--------|---------|
| **Qwen/Qwen2.5-7B-Instruct** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **调试展示首选** |
| deepseek-ai/DeepSeek-R1-Distill-Qwen-7B | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 成本优先 |
| Qwen/Qwen2.5-Coder-7B-Instruct | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 技术文档 |
| THUDM/glm-4-9b-chat | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | 中文需求 |
| deepseek-ai/DeepSeek-V3 | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 生产环境 |
| gpt-4o | ❌ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 英文需求 |

**选择建议**：
- 🎯 **调试展示**：使用 `Qwen/Qwen2.5-7B-Instruct`（免费额度大）
- 💰 **成本优先**：使用 `DeepSeek-R1-Distill-Qwen-7B`（蒸馏版本）
- 📝 **技术文档**：使用 `Qwen2.5-Coder-7B-Instruct`（代码理解强）
- 🚀 **生产环境**：使用 `DeepSeek-V3`（性能强，成本低）
- 🌍 **英文需求**：使用 `gpt-4o`（需OpenAI Key）

## 技术实现细节

### 任务状态

```json
{
  "task_id": "任务UUID",
  "status": "pending|running|completed|failed",
  "progress": 0-100,
  "current": 5,
  "total": 10,
  "message": "正在保存第5/10条用例...",
  "result": {
    "suite_id": 123,
    "total_cases": 10
  },
  "error": null,
  "created_at": "2026-02-12T10:30:00",
  "completed_at": "2026-02-12T10:31:30"
}
```

### 进度阶段

1. **10%** - 解析需求文档
2. **20%** - 构建AI提示词
3. **30%** - 调用AI生成用例
4. **50%** - 解析AI返回结果
5. **60%** - 准备保存用例
6. **60-95%** - 批量保存用例（按比例增长）
7. **100%** - 完成

### 轮询机制

- **频率**：每3秒查询一次任务状态
- **触发条件**：创建任务后自动开始
- **停止条件**：任务完成或失败
- **清理**：组件卸载时自动清理定时器

## 常见问题

### Q: 如何配置AI API Key？

A: 编辑 `backend/.env` 文件，设置 `AI_API_KEY` 参数

### Q: 生成进度一直不动？

A: 请检查：
1. 后端 `.env` 文件中的 `AI_API_KEY` 是否配置正确
2. 网络连接是否正常
3. 查看后端日志是否有错误信息
4. 检查AI服务是否可用

### Q: 生成失败怎么办？

A: 请检查：
1. AI API Key 是否有效（查看后端日志）
2. AI服务是否正常运行
3. 网络连接是否稳定
4. 需求文档是否解析成功
5. 后端日志中的具体错误信息

### Q: 可以同时生成多个用例集吗？

A: 可以，系统支持后台异步生成，可以创建多个生成任务并行执行

### Q: 生成过程中可以关闭页面吗？

A: 不建议。虽然后端任务会继续执行，但关闭页面后无法查看进度。可以切换到其他页面，不要关闭浏览器。

### Q: 如何调整生成的用例数量？

A: 系统已支持**根据需求文档长度自动建议用例条数**（在 `build_test_case_prompt()` 中通过 `_suggest_case_count()` 计算）。需求文档越长、功能点越多，提示词中建议的用例数越多（约 8～80 条），AI 会据此生成并可按需超出该范围以完整覆盖。若需固定范围，可在 `backend/app/routes/ai_tasks.py` 的提示词中修改“建议本需求生成约 **N～M** 条”的表述。

### Q: 生成的用例质量不高？

A: 可以优化：
1. 提供更详细的需求描述，并上传完整的需求文档（AI 会严格依据文档内容生成，不编造）
2. 调整 `AI_TEMPERATURE` 参数（降低温度提高确定性，推荐 0.3）
3. 系统已使用 system 角色约束 AI“严格依据文档、步骤与预期结果可追溯”，若仍不准，可检查需求文档是否歧义或过简
4. 长文档时系统会自动提高 `max_tokens`，避免生成结果被截断导致用例不全

## 安全注意事项

### 🔒 API Key 安全

1. **不要提交到代码仓库**
   ```bash
   # .gitignore 中应包含
   backend/.env
   ```

2. **定期轮换密钥**
   - 建议每季度更换一次API密钥

3. **使用环境变量**
   - 生产环境从环境变量或密钥管理服务读取

### 🛡️ 数据安全

1. **敏感文档处理**
   - 敏感需求文档建议人工摘要后再上传
   - 文档内容仅用于生成，不会存储

2. **访问控制**
   - 需要登录才能使用AI生成功能
   - 生成的用例与当前用户关联

## 文件结构

### 后端文件

```
backend/
├── .env                              # AI配置
└── app/
    ├── utils/
    │   └── task_manager.py          # 任务管理器
    └── routes/
        └── ai_tasks.py              # AI异步任务接口
```

### 前端文件

```
frontend/
└── src/
    ├── api/
    │   └── aiTasks.js               # AI任务API封装
    ├── utils/
    │   └── documentParser.js        # 文档解析工具
    ├── prompts/
    │   └── testCase.js              # AI提示词模板
    └── views/
        └── testCase/
            └── TestCaseManagement.vue # 用例管理页面
```

## 依赖安装

### 后端依赖

```bash
cd backend
pip install requests  # AI接口调用
```

### 前端依赖

```bash
cd frontend
npm install mammoth pdfjs-dist  # 文档解析
```

## 性能优化建议

### 1. 任务清理

系统会自动清理24小时前完成的任务，可以在 `task_manager.py` 中调整：

```python
task_manager.clear_completed_tasks(older_than_hours=24)
```

### 2. 并发控制

建议不要同时创建过多生成任务，每个任务会占用一个线程

### 3. 超时设置

AI接口调用设置了120秒超时，可以在 `ai_tasks.py` 中调整：

```python
response = requests.post(url, headers=headers, json=data, timeout=120)
```

## 调试指南

### 前端调试

打开浏览器控制台，查看日志：

- `[前端AI调用]` - AI调用流程日志
- `[任务轮询]` - 任务状态轮询日志
- `[文件夹用例集]` - 已有用例集加载日志

### 后端调试

查看后端日志文件：

- 搜索 `[AI生成用例]` - AI生成流程日志
- 搜索 `[AI保存用例]` - 用例保存日志
- 查看错误堆栈信息

### 查看任务列表

使用API查看所有任务状态（用于调试）：

```bash
curl -X GET http://localhost:5000/api/ai-tasks/tasks \
  -H "Cookie: session=your-session-cookie"
```

## 版本更新记录

### v2.0.0（当前版本）- 2026-02-12
- ✅ 重构为后端异步任务架构
- ✅ 先创建用例集，再后台生成
- ✅ 实时进度反馈
- ✅ 后台运行，不阻塞用户
- ✅ API Key迁移到后端
- ✅ 优化用例集名称输入，显示已有用例集
- ✅ 加载状态优化
- ❌ 删除旧的前端AI实现

### v1.1.0
- 支持PDF和DOCX文档解析
- 支持多模型切换
- 优化生成用例的质量

### v1.0.0
- 实现AI自动生成测试用例功能
- 支持OpenAI模型
- 支持TXT文档解析
- 生成结果可视化编辑

## 扩展与定制

### 1. 自定义提示词

编辑 `frontend/src/prompts/testCase.js`，添加或修改提示词模板：

```javascript
export const testCasePromptTemplates = {
  functional: `你是一个专业的测试工程师...`,
  performance: `你是一个性能测试专家...`,
  security: `你是一个安全测试专家...`,
}
```

### 2. 添加新的AI模型

在 `backend/app/routes/ai_tasks.py` 的 `get_ai_config()` 中配置：

```python
def get_ai_config() -> dict:
    return {
        'baseURL': os.getenv('AI_BASE_URL'),
        'apiKey': os.getenv('AI_API_KEY'),
        'model': os.getenv('AI_MODEL', 'your-new-model'),
        ...
    }
```

### 3. 调整生成数量

修改 `backend/app/routes/ai_tasks.py` 的提示词：

```python
prompt = f"""...
要求：
4. 至少生成10-15个测试用例  # 调整这里
5. 只返回JSON格式，不要有其他文字说明
"""
```

## 获取帮助

如有问题，请查看：

- 📄 `docs/API.md` - API接口文档
- 📄 `docs/USER_MANUAL.md` - 用户手册
- 📄 `docs/DEVELOPMENT.md` - 开发文档
- 🔍 浏览器控制台日志
- 📋 后端日志文件

---

**文档版本**: v2.0.0  
**最后更新**: 2026-02-12  
**维护者**: 技术团队
