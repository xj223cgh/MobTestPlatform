# AI 用例生成配置说明（可选功能）

## 功能概述

在用例管理中**异步生成**测试用例：前端提交需求文档文本 → 后端后台线程调用 **OpenAI 兼容 Chat Completions API** → 检索知识库（RAG）→ 解析 JSON 结果写库 → 自动导出 Excel → 前端约每 **3 秒**轮询任务状态。API Key 仅在后端配置，不暴露给浏览器。

---

## 完整调用链路

```
前端 aiTasks.js
  └─ POST /api/ai-tasks/generate-cases（suite_id + 文档文本/图片/docx + 项目/迭代/需求元数据）
        └─ routes/ai_tasks.py  generate_cases()
              └─ task_manager.create_task()  →  daemon Thread（内存队列，重启丢失）
                    └─ generate_test_cases_task()
                          ├─ _process_uploaded_images()       图片 Vision 识别（可选）
                          ├─ _retrieve_knowledge_context()    RAG 知识库检索
                          ├─ _generate_cases_from_document()  短文档单次 / 长文档 Map-Reduce
                          │     ├─ build_test_case_prompt()   Jinja2 模板渲染提示词
                          │     └─ call_ai_api()              POST Chat Completions API
                          ├─ parse_ai_response()              JSON 解析 → test_cases 列表
                          ├─ TestCase 批量写库                编号格式 项目缩写-x.y.z-需求缩写001
                          ├─ _save_requirement_document()     原始需求存档到 workspace
                          ├─ _save_generated_cases_excel()    用例导出 Excel
                          ├─ upload_document()                需求文档存入知识库（非调试模式）
                          └─ notify_users()                   站内通知（成功/失败均推送）

前端轮询（约 3s 间隔）
  └─ GET /api/ai-tasks/task-status/{task_id}
```

---

## AI 模块目录结构

所有 AI 相关的配置、知识库、提示词、工作区统一在 `backend/app/ai/` 下：

```
backend/app/ai/
├── ai_config.yaml                  # AI 角色、行为、知识检索策略中央配置
├── excel_exporter.py               # 用例 Excel 导出工具
├── __init__.py
├── knowledge/                      # 知识库
│   ├── docs/                       # 分类知识文档（18 篇）
│   │   ├── 01_core_business/       #   必读核心业务知识 (8 篇)
│   │   ├── 02_test_standards/      #   测试标准与规范   (3 篇)
│   │   ├── 03_platform_config/     #   平台配置说明     (3 篇)
│   │   ├── 04_issue_cases/         #   历史问题案例     (2 篇)
│   │   └── 05_test_guides/         #   测试指南         (2 篇)
│   ├── chroma_data/                #   ChromaDB 向量数据库
│   └── load_knowledge.py           #   知识库批量导入脚本
├── prompts/                        # 提示词模板
│   ├── system.yaml                 #   系统角色提示词
│   ├── generate_cases.yaml         #   单次生成用户提示词
│   └── generate_cases_chunk.yaml   #   Map-Reduce 分段提示词
└── workspace/                      # 文档工作区
    ├── requirements/
    │   ├── original/               #   原始需求文档自动存放
    │   └── converted/              #   转换后文档存放
    └── outputs/
        └── excel/                  #   生成的用例 Excel 自动存放
```

---

## 涉及文件

| 文件 | 职责 |
|------|------|
| `backend/app/ai/ai_config.yaml` | AI 角色定义、知识检索策略、用例质量标准、文档处理参数、Excel 列配置 |
| `backend/app/ai/prompts/*.yaml` | 提示词模板（Jinja2），运行时由 prompt_loader 加载渲染 |
| `backend/app/ai/knowledge/docs/` | 分类知识库文档，导入后用于 RAG 检索 |
| `backend/app/ai/knowledge/load_knowledge.py` | 批量导入知识库脚本，支持按分类导入 |
| `backend/app/ai/excel_exporter.py` | 生成用例后自动导出 Excel，列配置从 ai_config.yaml 读取 |
| `backend/app/routes/ai_tasks.py` | AI 任务路由：接口、生成逻辑、Map-Reduce、解析入库 |
| `backend/app/routes/knowledge.py` | 知识库 REST API（上传/列表/删除/搜索） |
| `backend/app/services/knowledge_service.py` | ChromaDB + Embedding 向量检索服务 |
| `backend/app/utils/prompt_loader.py` | YAML 提示词加载器（mtime 热重载 + Jinja2 渲染） |
| `backend/app/utils/doc_chunker.py` | 长文档分段工具（按标题和段落语义分块） |
| `backend/app/utils/task_manager.py` | 异步任务调度（内存 dict + daemon Thread） |
| `backend/.env` | AI 配置环境变量 |
| `frontend/src/api/aiTasks.js` | 前端 API 封装 |

---

## 环境变量（`backend/.env`）

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `AI_API_KEY` | 是 | — | 服务商密钥 |
| `AI_BASE_URL` | 否 | `https://api.siliconflow.cn/v1` | OpenAI 兼容接口根地址 |
| `AI_MODEL` | 否 | `Qwen/Qwen2.5-7B-Instruct` | 模型名，按服务商文档填写 |
| `AI_TEMPERATURE` | 否 | `0.3` | 0～2，越高越发散；测例场景建议 0.2～0.5 |
| `AI_MAX_TOKENS` | 否 | `4096` | 见下方「Token 配置说明」 |
| `EMBEDDING_MODEL` | 否 | `BAAI/bge-large-zh-v1.5` | 知识库向量化模型（不配置则跳过 RAG） |
| `CHROMA_PERSIST_DIR` | 否 | `./app/ai/knowledge/chroma_data` | ChromaDB 持久化目录 |
| `KNOWLEDGE_TOP_K` | 否 | `5` | 知识库检索返回条数 |
| `AI_VISION_MODEL` | 否 | — | 图片识别模型（不配置则跳过图片处理） |
| `AI_VISION_MAX_IMAGES` | 否 | 全部 | docx 内嵌图片最大识别数 |

示例（SiliconFlow）：

```env
AI_BASE_URL=https://api.siliconflow.cn/v1
AI_API_KEY=sk-xxxxxxxx
AI_MODEL=Qwen/Qwen2.5-7B-Instruct
AI_TEMPERATURE=0.3
AI_MAX_TOKENS=4096
EMBEDDING_MODEL=BAAI/bge-large-zh-v1.5
CHROMA_PERSIST_DIR=./app/ai/knowledge/chroma_data
```

---

## ai_config.yaml 配置说明

`ai_config.yaml` 是 AI 模块的中央配置文件，运行时被 `ai_tasks.py` 加载（mtime 缓存热重载）。

| 配置块 | 说明 | 影响范围 |
|--------|------|---------|
| `role` | AI 角色定义（身份、职责、约束） | 代码注释参考，不直接注入提示词 |
| `knowledge.retrieval` | top_k、相似度阈值、查询长度 | `_retrieve_knowledge_context()` |
| `knowledge.categories` | 知识库分类及优先级 | `load_knowledge.py` 导入时打标签 |
| `test_case_standards` | 命名规范、优先级分布、覆盖维度 | 代码注释参考 + 提示词模板引用 |
| `document_processing` | Map-Reduce 阈值、分段参数、用例数估算 | `_generate_cases_from_document()`、`_suggest_case_count()` |
| `output.excel_export` | Excel 列配置、sheet 名 | `excel_exporter.py` |

---

## Token 配置说明（重要）

### max_tokens 动态上调逻辑

`AI_MAX_TOKENS` 是输出 token **基础上限**，代码会按文档长度动态抬高，但存在硬上限：

```python
base_max    = ai_config.get('maxTokens', 4096)          # 读 AI_MAX_TOKENS
extra_tokens = min(12288, (doc_len // 1000) * 500)       # 每 1000 字符 +500，最多 +12288
dynamic_max_tokens = min(16384, base_max + extra_tokens) # 代码硬上限 16384
```

**注意**：`AI_MAX_TOKENS` 设置超过 16384 时实际无效，需修改 `ai_tasks.py` 中的硬上限值。

### 上下文窗口 vs max_tokens

| 概念 | 控制方 | 当前值 |
|------|--------|--------|
| 上下文窗口（输入+输出总量） | 模型本身 | Qwen2.5-7B-Instruct ≈ 32768 tokens |
| max_tokens（单次输出上限） | 代码+配置 | 实际最大 16384（受硬上限限制） |

---

## 用例数量建议逻辑

参数从 `ai_config.yaml → document_processing.case_count_estimation` 读取：

```python
# 默认值：min_per_1000_chars=3, base_minimum=8, max_cap=80
suggested = max(base_min, min(max_cap, (text_len // 1000) * min_per_1000 * 3))
```

---

## 知识库管理

### 批量导入

```bash
cd backend
python -m app.ai.knowledge.load_knowledge               # 导入所有分类文档
python -m app.ai.knowledge.load_knowledge --clear        # 清空后重新导入
python -m app.ai.knowledge.load_knowledge --category 01_core_business  # 只导入核心业务
```

### 知识库分类

| 分类目录 | 文档数 | 优先级 | 必读 | 说明 |
|----------|--------|--------|------|------|
| `01_core_business` | 8 | 1 | 是 | 平台业务总览、认证、项目、用例、任务、报告、消息、看板 |
| `02_test_standards` | 3 | 2 | 是 | 用例编写规范、优先级覆盖率标准、缺陷分类等级 |
| `03_platform_config` | 3 | 3 | 否 | 系统管理配置、设备管理、角色权限体系 |
| `04_issue_cases` | 2 | 4 | 否 | 历史问题经验总结、常见边界与异常场景 |
| `05_test_guides` | 2 | 5 | 否 | 功能测试指南、AI 用例生成使用指南 |

### RAG 检索流程

1. 取需求文档前 500 字符作为查询文本（可在 `ai_config.yaml` 配置）
2. 调用 Embedding API 转为向量
3. 在 ChromaDB 中检索 top_k 个最相似片段
4. 过滤掉余弦距离 > 0.5 的低相关结果
5. 将相关片段作为「业务背景知识」注入提示词

---

## 使用步骤

1. 配置 `.env` 后重启后端
2. 导入知识库：`python -m app.ai.knowledge.load_knowledge --clear`
3. 用例管理 → 新增用例集 → 选择自动生成 → 填写项目/迭代/需求 → 粘贴文本或上传文件（.txt/.md/.docx/图片）→ 提交
4. 生成进度在用例集详情页轮询显示；脑图页进入时若检测到正在生成会提示等待
5. 生成完成后：用例自动入库 + Excel 自动导出到 `app/ai/workspace/outputs/excel/`
6. 原始需求文档自动存档到 `app/ai/workspace/requirements/original/`
7. 生成完成或失败均会推送站内通知

---

## 常见问题

| 现象 | 排查方向 |
|------|---------|
| 进度不动 / 失败 | 查后端日志；确认 `AI_API_KEY` 有效；检查服务商限流与模型名 |
| JSON 解析失败 | 可能被截断：检查文档长度是否导致输出超 max_tokens；系统会自动重试一次 |
| 用例条数远少于预期 | 文档内容过短或功能点描述不清；可在 ai_config.yaml 调整 case_count_estimation |
| 质量不理想 | 补充需求描述结构（加验收标准/步骤列表）；略降 `AI_TEMPERATURE`；导入更多知识库文档 |
| 知识库检索无结果 | 检查 `EMBEDDING_MODEL` 是否配置；运行 `load_knowledge.py` 导入文档 |
| 401 认证失败 | API Key 过期或格式错误；到服务商控制台重新获取 |
| 进程重启后任务状态消失 | task_manager 使用内存存储，重启后历史任务状态不保留（已知限制） |

勿将 `.env` 提交仓库（应在 `.gitignore` 中）。

---

## 相关文档

- [AI测试用例生成方案说明.md](./AI测试用例生成方案说明.md) — 生成质量与策略
- 交互式 API 文档：[Scalar](http://127.0.0.1:5000/api-docs/)（需先启动后端）
- 环境与库：根目录 [README.md](../../README.md)
