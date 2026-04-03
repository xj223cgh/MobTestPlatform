# AI 用例生成配置说明（可选功能）

## 功能概述

在用例管理中**异步生成**测试用例：前端提交需求文档文本 → 后端后台线程调用 **OpenAI 兼容 Chat Completions API** → 解析 JSON 结果写库 → 前端约每 **3 秒**轮询任务状态。API Key 仅在后端配置，不暴露给浏览器。

---

## 完整调用链路

```
前端 aiTasks.js
  └─ POST /api/ai-tasks/generate-cases（suite_id + 文档文本 + 项目/迭代/需求元数据）
        └─ routes/ai_tasks.py  generate_cases()
              └─ task_manager.create_task()  →  daemon Thread
                    └─ generate_test_cases_task()
                          ├─ build_test_case_prompt()       构建 system + user 提示词
                          ├─ call_ai_api()                  POST 到 AI_BASE_URL/chat/completions
                          ├─ parse_ai_response()            解析 JSON → test_cases 列表
                          ├─ TestCase 批量写库              编号格式 项目缩写-x.y.z-需求缩写001
                          └─ notify_users()                 站内通知发起人（成功/失败均推送）

前端轮询（约 3s 间隔）
  └─ GET /api/ai-tasks/task-status/{task_id}
```

---

## 涉及文件

| 文件 | 职责 |
|------|------|
| `backend/app/routes/ai_tasks.py` | 所有 AI 任务逻辑：接口、提示词构建、API 调用、解析入库、编号生成 |
| `backend/app/utils/task_manager.py` | 异步任务调度（内存 dict + daemon Thread，进程重启后任务状态丢失） |
| `backend/.env` | AI 配置环境变量 |
| `frontend/src/api/aiTasks.js` | 前端 API 封装：提交任务、查询状态、脑图页生成状态检测 |

---

## 环境变量（`backend/.env`）

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `AI_API_KEY` | 是 | — | 服务商密钥 |
| `AI_BASE_URL` | 否 | `https://api.siliconflow.cn/v1` | OpenAI 兼容接口根地址 |
| `AI_MODEL` | 否 | `Qwen/Qwen2.5-7B-Instruct` | 模型名，按服务商文档填写 |
| `AI_TEMPERATURE` | 否 | `0.3` | 0～2，越高越发散；测例场景建议 0.2～0.5 |
| `AI_MAX_TOKENS` | 否 | `4096` | 见下方「Token 配置说明」 |

示例（SiliconFlow）：

```env
AI_BASE_URL=https://api.siliconflow.cn/v1
AI_API_KEY=sk-xxxxxxxx
AI_MODEL=Qwen/Qwen2.5-7B-Instruct
AI_TEMPERATURE=0.3
AI_MAX_TOKENS=4096
```

其他兼容服务：将 `AI_BASE_URL` 改为对应 `/v1` 根地址即可（如 OpenAI：`https://api.openai.com/v1`）。

---

## Token 配置说明（重要）

### max_tokens 动态上调逻辑

`AI_MAX_TOKENS` 是输出 token **基础上限**，代码会按文档长度动态抬高，但存在硬上限：

```python
# backend/app/routes/ai_tasks.py
base_max    = ai_config.get('maxTokens', 4096)          # 读 AI_MAX_TOKENS
extra_tokens = min(12288, (doc_len // 1000) * 500)       # 每 1000 字符 +500，最多 +12288
dynamic_max_tokens = min(16384, base_max + extra_tokens) # 代码硬上限 16384
```

**注意**：代码中存在 `min(16384, ...)` 硬上限，因此 `AI_MAX_TOKENS` 设置超过 16384 时**实际无效**，最终输出上限始终被钉在 16384 tokens。若需放开此限制，修改 `ai_tasks.py` 中的硬上限值。

### 上下文窗口 vs max_tokens

| 概念 | 控制方 | 当前值 |
|------|--------|--------|
| 上下文窗口（输入+输出总量） | 模型本身 | Qwen2.5-7B-Instruct ≈ 32768 tokens |
| max_tokens（单次输出上限） | 代码+配置 | 实际最大 16384（受硬上限限制） |

### 提示词 Token 占用估算

两段提示词均计入上下文（消耗**输入** token）：

| 内容 | 估算 token 数 |
|------|--------------|
| `SYSTEM_ROLE_CONTENT`（系统角色提示） | ~150～200 |
| `build_test_case_prompt` 模板（不含文档） | ~300～400 |
| 文档内容 | 中文约 1字≈1token；英文约 4字≈1token |

**计算示例**：文档 5000 字（中文） → 文档 ~5000 tokens + 模板 ~500 tokens = **输入约 5500 tokens**；剩余上下文空间 ≈ 32768 - 5500 = 27268 tokens，但输出实际受 max_tokens 上限约束（最大 16384）。

建议 `AI_MAX_TOKENS` 保持默认（4096）或按实测结果调整，不需要超过 16384。

---

## 用例数量建议逻辑

```python
# backend/app/routes/ai_tasks.py  _suggest_case_count()
suggested = max(8, min(80, (text_len // 300) * 3))
# 最少 8 条，最多 80 条，约每 300 字建议若干条
# 实际生成数由模型自行决定，该值仅作为提示词中的建议区间
```

---

## 使用步骤

1. 配置 `.env` 后重启后端。
2. 用例管理 → 新增用例集 → 选择自动生成 → 填写项目/迭代/需求 → 可上传文本类需求（`.txt`/`.md`） → 提交后可在后台继续其他操作。
3. 生成进度在用例集详情页轮询显示；脑图页进入时若检测到正在生成会提示等待。
4. 生成完成或失败均会推送站内通知。

---

## 常见问题

| 现象 | 排查方向 |
|------|---------|
| 进度不动 / 失败 | 查后端日志；确认 `AI_API_KEY` 有效；检查服务商限流与模型名 |
| JSON 解析失败 | 可能被截断：检查文档长度是否导致输出超 max_tokens；可尝试缩短文档或分段提交 |
| 用例条数远少于预期 | 文档内容过短或功能点描述不清；模型在建议区间内自行决定条数 |
| 质量不理想 | 补充需求描述结构（加验收标准/步骤列表）；略降 `AI_TEMPERATURE` |
| 401 认证失败 | API Key 过期或格式错误；到服务商控制台重新获取 |
| 进程重启后任务状态消失 | task_manager 使用内存存储，重启后历史任务状态不保留（已知限制） |

勿将 `.env` 提交仓库（应在 `.gitignore` 中）。

---

## 相关文档

- [AI测试用例生成方案说明.md](./AI测试用例生成方案说明.md) — 生成质量与策略
- 交互式 API 文档：[Scalar](http://127.0.0.1:5000/api-docs/)（需先启动后端）
- 环境与库：根目录 [README.md](../../README.md)
