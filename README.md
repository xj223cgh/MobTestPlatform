# MobTestPlatform - 移动测试平台

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.8%2B-blue?logo=python&logoColor=white" alt="Python" /></a>
  <a href="https://nodejs.org/"><img src="https://img.shields.io/badge/node.js-16%2B-339933?logo=node.js&logoColor=white" alt="Node.js" /></a>
  <a href="https://vuejs.org/"><img src="https://img.shields.io/badge/vue-3.x-4FC08D?logo=vue.js&logoColor=white" alt="Vue 3" /></a>
  <a href="https://flask.palletsprojects.com/"><img src="https://img.shields.io/badge/flask-2.x-000000?logo=flask&logoColor=white" alt="Flask" /></a>
  <a href="https://www.mysql.com/"><img src="https://img.shields.io/badge/mysql-5.7%2B-4479A1?logo=mysql&logoColor=white" alt="MySQL" /></a>
</p>

面向移动端测试团队的综合测试管理平台，覆盖用例管理（含 AI 生成与脑图编辑）、用例评审、设备管理与 Agent 桥接、测试任务执行、报告管理及消息通知等完整测试流程。通过浏览器访问管理端，适合多人协作与多项目并行。

---

## 功能概览

| 模块 | 说明 |
|------|------|
| **首页看板** | 平台统计（项目/用例/设备/任务）、近期活动流、任务趋势图、设备在线状态、近期项目快捷入口 |
| **用例管理** | 树形用例库（文件夹 + 用例集）、脑图编辑（simple-mind-map）与版本回滚、标签与标记、批量导入导出、回收站 |
| **AI 用例生成** | 上传需求文档异步生成用例（RAG 知识库增强 + 长文档 Map-Reduce + Excel 自动归档），知识库管理（ChromaDB + Embedding 向量检索），可选 |
| **用例评审** | 发起评审 / 执行评审、逐条通过或驳回及意见记录、评审历史追溯、评审中心 |
| **测试任务** | 用例执行任务与设备脚本任务、任务文件夹分类、任务级用例快照、暂停 / 继续 / 取消 / 完成、异步调度 |
| **报告管理** | 按任务聚合结果、任务完成自动生成报告、详情视图、导出 Word / Excel、批量删除 |
| **设备管理** | 设备 CRUD、ADB 设备发现与指令下发、设备脚本执行、投屏（Escrcpy） |
| **Agent 桥接** | 本机 Agent 注册 / 心跳 / 绑定与解绑、Agent 下载入口、跨机 ADB 代理（Socket.IO 通信） |
| **项目管理** | 项目创建与维护、成员管理、迭代规划与状态统计 |
| **需求管理** | 需求录入、状态流转、关联迭代与项目 |
| **消息通知** | WebSocket 实时推送、消息中心（已读 / 未读 / 置顶 / 清空）、通知路由与跳转业务页 |
| **用户与权限** | 四级角色（超管 / 管理员 / 测试人员 / 普通成员）、功能埋点权限可视化配置 |
| **认证** | 账号密码登录、邮箱验证码登录、注册、忘记密码 / 重置密码、邮箱验证 |
| **系统设置** | 安全策略（会话超时、登录锁定）、分页设置、自动报告、个人设置 |

---

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Vue 3 + Element Plus + Vite + Pinia + Axios + ECharts + Socket.IO Client + simple-mind-map |
| 后端 | Flask + Flask-SQLAlchemy + Flask-Login + Flask-SocketIO + APScheduler + PyMySQL |
| 数据库 | MySQL 5.7+（utf8mb4），30 张表 |
| 通信 | RESTful API + WebSocket（Socket.IO） |
| 认证 | 基于 Cookie 的会话（`withCredentials`） |
| Agent | Python Socket.IO 客户端，本机 ADB 桥接，打包为 MobTestAgent.exe |

---

## 环境要求

- **Python** 3.8+（推荐 3.11）
- **Node.js** 16+（npm 8+）
- **MySQL** 5.7+ / 8.x

---

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/xj223cgh/MobTestPlatform.git
cd MobTestPlatform
```

### 2. 安装依赖

```bash
# 后端依赖
cd backend
pip install -r requirements.txt

# 前端依赖
cd ../frontend
npm install
```

### 3. 配置环境变量

```bash
cp backend/.env.example backend/.env    # Linux/Mac
copy backend\.env.example backend\.env  # Windows
```

编辑 `backend/.env`，最小必填项：

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

> **注意**：`.env` 包含密钥等敏感信息，已在 `.gitignore` 中排除。完整配置项与说明见 [`backend/.env.example`](backend/.env.example)。

### 4. 初始化数据库

确认 `.env` 中的数据库配置正确后执行：

```bash
# 一键初始化（创建库 → 建表 → 造数）
python database/init_database.py
```

也可分步执行：

```bash
python database/01_create_database.py   # 创建数据库
python database/03_create_tables.py     # 创建表结构（30 张表）
python database/05_insert_test_data.py  # 插入演示数据（可选）
```

> 数据库脚本与表结构详见 [database/README.md](database/README.md)。

### 5. 启动服务

#### 一键启动（推荐）

```bash
python start.py
```

该脚本会同时启动后端（Flask，端口 5000）和前端（Vite，端口 8081）。

#### 手动启动

```bash
# 终端 1 - 启动后端
cd backend
python run.py

# 终端 2 - 启动前端
cd frontend
npm run dev
```

### 6. 访问应用

| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:8081 |
| 后端 API | http://localhost:5000/api |
| 接口文档（Scalar） | http://localhost:5000/api-docs/ |

> 前端开发服务器已配置代理，`/api` 请求自动转发至 `localhost:5000`。

演示账号（执行演示数据脚本后可用，密码均为 `123321`）：

| 账号 | 角色 |
|------|------|
| Lethe | 超级管理员 |
| Manager | 管理员 |
| Tester | 测试人员 |
| Admin | 普通成员 |

---

## 项目结构

```
MobTestPlatform/
├── backend/                    # 后端（Flask）
│   ├── app/
│   │   ├── __init__.py         # 应用工厂 & 蓝图注册
│   │   ├── ai/                 # AI 用例生成模块（统一目录）
│   │   │   ├── ai_config.yaml  #   角色、行为、知识检索策略、质量标准
│   │   │   ├── knowledge/      #   知识库（分类文档 + ChromaDB 向量库）
│   │   │   ├── prompts/        #   提示词 YAML 模板（Jinja2）
│   │   │   ├── workspace/      #   需求文档、提取图片、Excel 用例归档
│   │   │   └── excel_exporter.py
│   │   ├── config/config.py    # 配置（数据库、SMTP、CORS 等）
│   │   ├── models/models.py    # SQLAlchemy 数据模型
│   │   ├── routes/             # API 路由
│   │   ├── services/           # 业务逻辑（邮件、通知、权限、知识库、Agent）
│   │   ├── utils/              # 工具函数（认证、辅助函数、调度器）
│   │   └── constants/          # 常量（权限编码）
│   ├── scripts/                # Agent 路径配置脚本
│   ├── storage/                # 文件存储（设备脚本等）
│   ├── .env.example            # 环境变量示例（复制为 .env 后填写实际值）
│   ├── run.py                  # 后端启动入口
│   └── requirements.txt        # Python 依赖
├── frontend/                   # 前端（Vue 3 + Element Plus）
│   ├── src/
│   │   ├── api/                # API 调用封装
│   │   ├── components/         # 公共组件（布局、脑图等）
│   │   ├── router/             # 路由配置
│   │   ├── stores/             # Pinia 状态管理
│   │   ├── utils/              # 工具（请求封装）
│   │   └── views/              # 页面视图
│   ├── vite.config.js          # Vite 构建配置（代理 /api → localhost:5000）
│   └── package.json            # 前端依赖
├── database/                   # 数据库脚本（30 张表）
│   ├── config.py               # 数据库连接配置（读取 backend/.env）
│   ├── 01_create_database.py   # 创建数据库
│   ├── 03_create_tables.py     # 创建所有表结构
│   ├── 05_insert_test_data.py  # 插入演示数据
│   ├── init_database.py        # 一键初始化
│   └── README.md               # 数据库操作说明
├── agent/                      # 设备 Agent：跨机场景下本机 ADB 桥接（可选）
├── escrcpy/                    # 投屏工具（Electron，第三方开源组件，许可见 escrcpy/LICENSE）
├── docs/                       # 项目文档
│   ├── 方案/                   # 部署、AI、内网、消息通知、脑图协作等设计文档
│   ├── 项目文档/               # 文档索引、功能地图
│   └── images/                 # 界面截图
├── start.py                    # 一键启动脚本（前后端同时启动）
└── README.md
```

---

## 数据库初始化

详见 [`database/README.md`](database/README.md)，主要脚本：

| 脚本 | 说明 |
|------|------|
| `01_create_database.py` | 创建 `mobile_test_platform` 数据库 |
| `02_drop_database.py` | 删除数据库（**慎用**） |
| `03_create_tables.py` | 创建全部 30 张数据表 |
| `04_drop_tables.py` | 删除所有表（**慎用**） |
| `05_insert_test_data.py` | 插入演示数据（用户、项目、用例等） |
| `06_clear_table_data.py` | 清空所有表数据（保留表结构） |
| `07_test_connection.py` | 测试数据库连接 |
| `init_database.py` | 一键初始化（创建库 → 建表 → 造数） |

---

## 系统架构

```
┌─────────────┐     REST / WebSocket      ┌─────────────────────────────┐
│  浏览器      │ ────────────────────────► │  Flask（API + Socket.IO）    │
│  Vue 3      │                           │  端口 5000                  │
└─────────────┘                           └──────────────┬──────────────┘
                                                         │
                                            ┌────────────┼────────────┐
                                            ▼                         ▼
                                       ┌─────────┐          ┌──────────────┐
                                       │  MySQL  │          │  本机 Agent   │
                                       └─────────┘          │  Socket.IO   │
                                                            │  ADB / scrcpy│
                                                            └──────────────┘
```

- **浏览器 → 后端**：REST API + WebSocket（消息推送、Agent 通信）
- **后端 → MySQL**：SQLAlchemy ORM，30 张业务表
- **后端 ↔ Agent**：Socket.IO 双向通信，Agent 运行在测试人员本机，代理 ADB 与投屏指令

---

## 可选功能配置

### 邮箱验证码（QQ 邮箱 SMTP）

用于邮箱验证码登录和找回密码。不配置则相关功能不可用。

1. 登录 [QQ 邮箱](https://mail.qq.com) → **设置** → **账户** → 开启 **IMAP/SMTP 服务** → 获取 **授权码**
2. 在 `backend/.env` 中填写：

```env
SMTP_USER=你的QQ邮箱@qq.com
SMTP_PASSWORD=授权码
```

配置后用户绑定 QQ 邮箱即可使用邮箱验证码登录和找回密码。

### AI 用例生成

支持通过 AI 大模型自动生成测试用例，上传需求文档（.docx / .pdf / .txt）辅助生成。主要能力：

- **RAG 知识库增强**：基于 ChromaDB 向量检索，自动引入业务知识、测试标准等上下文
- **分类知识库**：5 大类 18 篇文档（核心业务 / 测试标准 / 配置说明 / 历史问题 / 测试指南）
- **长文档 Map-Reduce**：超长需求按段拆分生成后合并，避免遗漏
- **需求图片提取**：从 docx 提取图片并持久化存储，一个需求文档对应一个图片目录
- **Excel 自动归档**：每次生成的用例同时写入数据库和 Excel 文件
- **需求文档存入知识库**：生成完成后自动将需求文档存入知识库，持续丰富上下文

统一目录位于 `backend/app/ai/`，配置方式见 [AI 用例生成配置说明](docs/方案/AI用例生成配置说明.md)。

涉及环境变量：`AI_API_KEY`、`AI_BASE_URL`、`AI_MODEL`、`EMBEDDING_MODEL`、`EMBEDDING_API_KEY`、`CHROMA_PERSIST_DIR` 等。

### 设备 Agent

若部署形态为「平台在服务器、设备接在用户本机」，需配置本机 ADB 桥接。

- 部署与流程：[平台访问与 Agent 流程说明](docs/方案/平台访问与Agent流程说明.md)
- Agent 使用方法：[agent/README.md](agent/README.md)

### 内网访问

局域网内其他设备访问平台，需配置 `CORS_ORIGINS`，详见 [内网访问说明](docs/方案/内网访问说明.md)。

---

## 接口文档

后端启动后访问：

- **交互式文档**：[http://127.0.0.1:5000/api-docs/](http://127.0.0.1:5000/api-docs/)（[Scalar](https://github.com/scalar/scalar)，由 OpenAPI 动态生成）
- **OpenAPI JSON**：[http://127.0.0.1:5000/api-docs/openapi.json](http://127.0.0.1:5000/api-docs/openapi.json)

调试需登录的接口时，请先在同一浏览器完成平台登录，或在该页调用 `POST /api/auth/login` 后再试。

---

## 文档

| 文档 | 说明 |
|------|------|
| [docs/项目文档/README.md](docs/项目文档/README.md) | 文档索引、功能地图、第三方组件说明 |
| [database/README.md](database/README.md) | 数据库脚本与 30 张表说明 |
| [agent/README.md](agent/README.md) | 本机 Agent 使用、清理与打包 |
| [docs/方案/平台访问与Agent流程说明.md](docs/方案/平台访问与Agent流程说明.md) | 部署、网络、多用户及设备跨机说明 |
| [docs/方案/AI用例生成配置说明.md](docs/方案/AI用例生成配置说明.md) | AI 环境变量与流程（可选） |
| [docs/方案/AI测试用例生成方案说明.md](docs/方案/AI测试用例生成方案说明.md) | AI 生成质量与策略 |
| [docs/方案/内网访问说明.md](docs/方案/内网访问说明.md) | 局域网与防火墙 |
| [docs/方案/消息通知机制设计方案.md](docs/方案/消息通知机制设计方案.md) | 消息中心与 WebSocket 推送设计 |
| [docs/方案/脑图多人协作设计方案.md](docs/方案/脑图多人协作设计方案.md) | 脑图版本与冲突处理策略 |
