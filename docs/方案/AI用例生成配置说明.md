# AI 用例生成配置说明（可选功能）

## 作用与流程

- 在用例管理中**异步生成**用例：先创建用例集，后台线程调用 **OpenAI 兼容 API** 写库；前端约每 **3 秒**轮询任务状态。
- **API Key 仅在后端**配置，不暴露给浏览器。

```
前端发起任务 → 后端 task_manager + ai_tasks → AI HTTP API → 落库
                    ↑
              轮询 GET task-status
```

**主要代码**：`backend/app/utils/task_manager.py`、`backend/app/routes/ai_tasks.py`；前端 `frontend/src/api/aiTasks.js`、用例管理页中的生成弹窗。需求文档：优先使用 **`.txt` / `.md`** 由前端读成文本再提交（与当前实现一致；若扩展 Word/PDF 需另接解析库）。

## 环境变量（`backend/.env`）

| 变量 | 说明 |
|------|------|
| `AI_API_KEY` | 必填，服务商密钥 |
| `AI_BASE_URL` | 默认可用 SiliconFlow：`https://api.siliconflow.cn/v1` |
| `AI_MODEL` | 模型名，按服务商文档填写 |
| `AI_TEMPERATURE` | 可选，默认约 `0.3`（更稳） |
| `AI_MAX_TOKENS` | 可选；长文档时后端会按长度动态抬高上限（见 `ai_tasks.py`） |

示例（SiliconFlow，模型名以控制台为准）：

```env
AI_BASE_URL=https://api.siliconflow.cn/v1
AI_API_KEY=sk-xxxxxxxx
AI_MODEL=Qwen/Qwen2.5-7B-Instruct
AI_TEMPERATURE=0.3
```

其他兼容服务：将 `AI_BASE_URL` 改为对应 `/v1` 根地址即可（如 OpenAI：`https://api.openai.com/v1`）。

## 使用要点

1. 配置 `.env` 后重启后端。
2. 用例管理 → 新增用例集 → 选择自动生成 → 填项目/迭代/需求等 → 可上传文本类需求 → 提交后可在后台继续其他操作。
3. 生成条数、提示词与 `max_tokens` 策略见 `build_test_case_prompt`、`_suggest_case_count`、`call_ai_api`。

## 常见问题

- **进度不动 / 失败**：查后端日志、`AI_API_KEY` 与网络；确认服务商限流与模型名正确。
- **质量不理想**：补充需求描述与文档；略降 `AI_TEMPERATURE`；检查需求是否歧义。
- **勿将 `.env` 提交仓库**（应在 `.gitignore` 中）。

## 相关文档

- 交互式 API：[Scalar](http://127.0.0.1:5000/api-docs/)（需先启动后端）
- 环境与库：根目录 [README.md](../../README.md)、[database/README.md](../../database/README.md)
