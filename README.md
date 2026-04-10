<div align="center">

# MobTestPlatform

**基于Flask开发的移动测试平台**

用例 · 评审 · 设备 · 任务 · 报告

[![Python](https://img.shields.io/badge/python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/node.js-16%2B-339933?logo=node.js&logoColor=white)](https://nodejs.org/)
[![Vue](https://img.shields.io/badge/vue-3.x-4FC08D?logo=vue.js&logoColor=white)](https://vuejs.org/)
[![Flask](https://img.shields.io/badge/flask-2.x-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/mysql-5.7%2B-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com/)

</div>

---

## 目录

- [项目简介](#项目简介)
- [核心能力](#核心能力)
- [技术栈](#技术栈)
- [界面预览](#界面预览)
- [系统架构](#系统架构)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [目录结构](#目录结构)
- [接口文档](#接口文档)

---

## 项目简介

> MobTestPlatform 聚焦 **测试资产与执行过程** 的线上化管理：在统一平台内完成用例设计、评审流转、设备接入与调度、测试任务执行，以及基于任务的结果汇总与报告导出，适合多人协作与多项目并行。  
> 名称中的「Web」指 **通过浏览器访问的管理端**，平台面向通用测试活动（如移动端等），**不是**「仅针对网站做 Web 专项测试」的工具。

平台采用前后端分离架构，浏览器访问 **Vue 3** 前端，通过 REST API 与 **Socket.IO** 与 **Flask** 后端交互，业务数据持久化在 **MySQL**。  
**项目管理**、**用户与权限**、**消息通知** 等为基础支撑；**AI 辅助生成用例** 为可选增强能力。

---

## 核心能力

以下四类为产品侧重点投入与文档叙述的主线。

### 用例管理

- 树形 **测试套件 / 用例集** 组织，支持文件夹与用例集类型
- **脑图** 编辑、版本与回滚，标签、标记等辅助信息
- 用例 **导入 / 导出**、回收站与批量操作
- （可选）基于需求文档的 **AI 异步生成用例**，配置方法见 [AI 用例生成配置说明](docs/方案/AI用例生成配置说明.md)

### 用例评审

- 针对用例集发起 **评审任务**，参与人处理待办
- 单条用例 **通过 / 拒绝** 及意见记录，支持 **评审历史** 追溯
- 评审中心：**我参与的 / 我发起的** 与状态聚合

### 设备管理

- 设备列表、状态与常用 **ADB** 能力（无线调试、指令执行等）
- **Escrcpy** 等投屏能力（`escrcpy/` 为引用的第三方开源客户端，许可见 `escrcpy/LICENSE`；说明见 [项目文档说明](docs/项目文档/README.md)）
- 脚本任务、批量与计划任务等与设备侧执行衔接
- 若部署形态为「平台在服务器、设备接在用户本机」，可按 [部署与 Agent 流程说明](docs/方案/平台访问与Agent流程说明.md) 配置本机 ADB 桥接（`agent/`），Agent 使用方法另见 [agent/README.md](agent/README.md)

### 测试任务与报告

- **测试任务**：用例执行任务与设备脚本任务、任务文件夹、任务级 **用例快照**（保证报告与当时用例一致）
- **执行过程**：任务状态、暂停 / 继续 / 完成、执行记录与统计
- **报告**：按任务聚合结果，支持 **Word / Excel** 导出；与任务完成流程联动

### 其他模块（支撑）

- **项目管理**：项目、迭代、需求、成员与角色  
- **用户与权限**：会话登录、QQ 邮箱验证码、四级角色 + 功能埋点权限 
- **消息通知**：站内通知与实时推送，设计方案见 [消息通知机制设计方案](docs/方案/消息通知机制设计方案.md)

---

## 技术栈

| | |
| --- | --- |
| **前端** | Vue 3、Vite、Element Plus、Pinia、Axios、ECharts、Socket.IO Client |
| **后端** | Python 3.8+、Flask、Flask-SQLAlchemy、Flask-Login、Flask-SocketIO、APScheduler、PyMySQL |
| **数据库** | MySQL 5.7+ / 8.x |
| **认证** | 基于 Cookie 的会话（`withCredentials`） |

---

## 界面预览

建议将对外展示用截图放入 [`docs/images/`](docs/images/)（命名与规范见 [`docs/images/README.md`](docs/images/README.md)）。推荐至少包含：

| 文件 | 建议内容 |
| --- | --- |
| `ui-home-dashboard.png` | 首页 / 仪表盘 |
| `ui-testcase.png` | **用例管理**（树或脑图） |
| `ui-device.png` | **设备管理**（列表与常用操作） |

可在本段下方自行插入 `![描述](docs/images/xxx.png)`（注意脱敏）。

---

## 系统架构

```
┌─────────────┐     REST / WebSocket      ┌─────────────────────────────┐
│  浏览器      │ ────────────────────────► │  Flask（API + Socket.IO）    │
│  Vue 3      │                           │                             │
└─────────────┘                           └──────────────┬──────────────┘
                                                         │
                                                         ▼
                                                    ┌─────────┐
                                                    │  MySQL  │
                                                    └─────────┘
```

业务主线（用例、评审、任务、报告）数据均经后端读写 MySQL；设备相关指令由后端编排，具体部署与网络见 [部署与 Agent 流程说明](docs/方案/平台访问与Agent流程说明.md)。

---

## 快速开始

### 环境要求

| 依赖 | 版本 |
| --- | --- |
| Python | 3.8+（推荐 3.11） |
| Node.js | 16+ |
| npm | 8+ |
| MySQL | 5.7+ 或 8.x |

### 安装与运行

```bash
# 1. 克隆仓库
git clone https://github.com/xj223cgh/MobTestPlatform.git
cd MobTestPlatform

# 2. 安装后端依赖
cd backend && pip install -r requirements.txt && cd ..

# 3. 安装前端依赖
cd frontend && npm install && cd ..

# 4. 配置环境变量（见下一节「配置说明」）
#    复制示例文件并填写实际值
cp backend/.env.example backend/.env

# 5. 初始化数据库（先确认 .env 中的数据库配置正确）
python database/init_database.py
# 可选：单独插入演示数据 python database/05_insert_test_data.py

# 6. 启动前后端
python start.py
```

数据库脚本与表结构详见 [database/README.md](database/README.md)。

启动成功后：

| 服务 | 地址 |
| --- | --- |
| 前端 | http://localhost:8081 |
| 后端 API | http://localhost:5000/api |
| 接口文档（Scalar） | http://localhost:5000/api-docs/ |

局域网/内网环境访问请参考 [内网访问说明](docs/方案/内网访问说明.md)。

### 演示账号

导入演示数据后可使用下列账号（密码均为 `123321`）：

| 用户名 | 角色 |
| --- | --- |
| Lethe | 超级管理员 |
| Manager | 管理员 |
| Tester | 测试人员 |
| Admin | 普通成员 |

---

## 配置说明

后端通过 `backend/.env` 文件加载环境变量，由 `backend/app/config/config.py` 读取。

> **重要**：`.env` 包含密钥等敏感信息，已在 `.gitignore` 中排除。首次部署请复制示例文件：
>
> ```bash
> cp backend/.env.example backend/.env    # Linux/Mac
> copy backend\.env.example backend\.env  # Windows
> ```
>
> 然后根据注释填写实际值。完整配置项与说明见 [`backend/.env.example`](backend/.env.example)。

最小必填项：

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=你的密码
MYSQL_DATABASE=mobile_test_platform

SECRET_KEY=请改为随机长字符串

SMTP_USER=你的QQ邮箱@qq.com
SMTP_PASSWORD=SMTP授权码
```

### 可选功能配置

| 功能 | 涉及配置项 | 参考文档 |
| --- | --- | --- |
| AI 用例生成 | `AI_API_KEY`、`AI_BASE_URL`、`AI_MODEL` 等 | [AI 用例生成配置说明](docs/方案/AI用例生成配置说明.md) |
| 知识库 RAG | `EMBEDDING_MODEL`、`CHROMA_PERSIST_DIR`、`KNOWLEDGE_TOP_K` | [AI 用例生成配置说明](docs/方案/AI用例生成配置说明.md) |
| 图片识别 | `AI_VISION_MODEL`、`AI_VISION_MAX_IMAGES` | `.env.example` 中的注释说明 |
| 设备 Agent | `AGENT_PLATFORM_BASE_URL`、`AGENT_EXE_PATH` | [部署与 Agent 流程说明](docs/方案/平台访问与Agent流程说明.md) |
| 邮件通知 | `SMTP_USER`、`SMTP_PASSWORD` 等 | `.env.example` 中的注释说明 |
| 局域网访问 | `CORS_ORIGINS` | [内网访问说明](docs/方案/内网访问说明.md) |

---

## 目录结构

```
MobTestPlatform/
├── backend/          # Flask 后端（REST、Socket.IO、定时任务）
│   ├── .env.example  # 环境变量示例（复制为 .env 后填写实际值）
│   └── app/          # 应用代码（routes/models/services/utils/config）
├── frontend/         # Vue 3 + Vite + Element Plus
├── database/         # MySQL 初始化与维护脚本（30 张表）
├── agent/            # 设备管理：跨机场景下本机 ADB 桥接（可选）
├── escrcpy/          # 投屏相关（Electron，第三方开源组件）
├── docs/             # 方案、论文、截图
│   ├── 方案/         # 部署、AI、内网、消息通知、脑图协作等设计文档
│   ├── 项目文档/     # 文档索引、功能地图、API 说明
│   └── images/       # 界面截图
├── start.py          # 本地同时启动前后端
└── README.md
```

后端路由位于 `backend/app/routes/`，模型在 `backend/app/models/models.py`；统一 JSON 响应见 `backend/app/utils/helpers.py`。

---

## 接口文档

后端启动后访问：

- **交互式文档**：[http://127.0.0.1:5000/api-docs/](http://127.0.0.1:5000/api-docs/)（[Scalar](https://github.com/scalar/scalar)，由 OpenAPI 动态生成）  
- **OpenAPI JSON**：[http://127.0.0.1:5000/api-docs/openapi.json](http://127.0.0.1:5000/api-docs/openapi.json)

调试需登录的接口时，请先在同一浏览器完成平台登录，或在该页调用 `POST /api/auth/login` 后再试。

---

## 更多文档

| 文档 | 说明 |
| --- | --- |
| [docs/项目文档/README.md](docs/项目文档/README.md) | 文档索引、功能地图、第三方组件说明 |
| [database/README.md](database/README.md) | 数据库脚本与 30 张表说明 |
| [agent/README.md](agent/README.md) | 本机 Agent 使用、清理与打包 |
| [docs/方案/平台访问与Agent流程说明.md](docs/方案/平台访问与Agent流程说明.md) | 部署、网络、多用户及设备跨机说明 |
| [docs/方案/AI用例生成配置说明.md](docs/方案/AI用例生成配置说明.md) | AI 环境变量与流程（可选） |
| [docs/方案/内网访问说明.md](docs/方案/内网访问说明.md) | 局域网与防火墙 |
| [docs/方案/消息通知机制设计方案.md](docs/方案/消息通知机制设计方案.md) | 消息中心与 WebSocket 推送设计 |
| [docs/方案/脑图多人协作设计方案.md](docs/方案/脑图多人协作设计方案.md) | 脑图版本与冲突处理策略 |
