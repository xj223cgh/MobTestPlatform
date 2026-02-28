# MobTestPlatform - 移动测试平台

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8%2B-blue?logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/node.js-16%2B-green?logo=node.js&logoColor=white" alt="Node.js" />
  <img src="https://img.shields.io/badge/vue-3.3-brightgreen?logo=vue.js&logoColor=white" alt="Vue 3" />
  <img src="https://img.shields.io/badge/flask-2.3-lightgrey?logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/mysql-5.7%2B-blue?logo=mysql&logoColor=white" alt="MySQL" />
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License" />
</p>

一个面向移动端测试团队的综合测试管理平台，覆盖项目管理、需求管理、用例管理（支持 AI 生成）、用例评审、测试任务执行、设备管理、报告管理及消息通知等完整测试流程。

---

## 功能概览

| 模块 | 说明 |
|------|------|
| **项目管理** | 项目创建与维护、成员管理、项目详情面板 |
| **迭代管理** | 迭代规划、状态追踪、迭代详情 |
| **需求管理** | 版本需求录入、状态流转、关联迭代与项目 |
| **用例管理** | 树形用例库（文件夹 + 用例集）、手动编写与 AI 自动生成、脑图视图、批量导入导出 |
| **用例评审** | 发起评审 / 执行评审、逐条审批、评审历史记录 |
| **测试任务** | 用例执行任务与设备脚本任务、任务文件夹分类、关联项目/迭代/用例集 |
| **设备管理** | Android 设备 ADB 连接管理、无线连接、设备投屏（Escrcpy）、设备详情 |
| **报告管理** | 自动 / 手动生成测试报告、报告详情、导出 Word / Excel |
| **消息通知** | WebSocket 实时推送、消息中心（已读/未读/置顶/清理） |
| **用户与权限** | 四级角色（超管/管理员/测试人员/普通成员）、功能埋点权限可视化配置 |
| **系统设置** | 安全策略（会话超时、登录锁定）、分页设置、自动报告等 |
| **认证** | 账号密码登录、QQ 邮箱验证码登录、注册、忘记密码 / 重置密码 |

---

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Vue 3 + Element Plus + Vite + Pinia + Axios + ECharts + Socket.IO Client |
| 后端 | Flask + Flask-SQLAlchemy + Flask-Login + Flask-SocketIO + APScheduler |
| 数据库 | MySQL 5.7+（utf8mb4） |
| 通信 | RESTful API + WebSocket（Socket.IO） |

---

## 环境要求

- **Python** 3.8+
- **Node.js** 16+（npm 8+）
- **MySQL** 5.7+ / MariaDB 10.2+

---

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-org/MobTestPlatform.git
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

### 3. 初始化数据库

修改 `database/config.py` 中的数据库连接信息，然后执行：

```bash
# 在项目根目录执行
python database/01_create_database.py   # 创建数据库
python database/03_create_tables.py     # 创建表结构
python database/05_insert_test_data.py  # 插入测试数据（可选）
```

> 也可使用一键初始化脚本：`python database/init_database.py`

### 4. 配置后端环境变量

在 `backend/` 目录下创建或编辑 `.env` 文件：

```env
# Flask
FLASK_ENV=development
FLASK_PORT=5000

# 数据库
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=123456
MYSQL_DATABASE=mobile_test_platform

# 安全
SECRET_KEY=your-secret-key

# QQ 邮箱 SMTP（用于邮箱验证码登录和找回密码，不配置则邮箱相关功能不可用）
SMTP_USER=你的QQ邮箱@qq.com
SMTP_PASSWORD=QQ邮箱授权码
```

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

- 前端地址：http://localhost:8081
- 后端 API：http://localhost:5000/api

测试账号（执行测试数据脚本后可用）：

| 账号 | 密码 | 角色 |
|------|------|------|
| Lethe | 123321 | 超级管理员 |
| Manager | 123321 | 管理员 |
| Tester | 123321 | 测试人员 |
| Admin | 123321 | 普通成员 |

---

## 项目结构

```
MobTestPlatform/
├── backend/                    # 后端（Flask）
│   ├── app/
│   │   ├── __init__.py         # 应用工厂 & 蓝图注册
│   │   ├── config/config.py    # 配置（数据库、SMTP、CORS 等）
│   │   ├── models/models.py    # SQLAlchemy 数据模型
│   │   ├── routes/             # API 路由（17 个模块）
│   │   ├── services/           # 业务逻辑（邮件、通知、权限）
│   │   ├── utils/              # 工具函数（认证、辅助函数、调度器）
│   │   └── constants/          # 常量（权限编码）
│   ├── storage/                # 文件存储（设备脚本、Logo）
│   ├── .env                    # 环境变量
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
│   ├── vite.config.js          # Vite 构建配置
│   └── package.json            # 前端依赖
├── database/                   # 数据库脚本
│   ├── config.py               # 数据库连接配置
│   ├── 01_create_database.py   # 创建数据库
│   ├── 03_create_tables.py     # 创建所有表结构
│   ├── 05_insert_test_data.py  # 通用测试数据
│   ├── 08_seed_wps_email_data.py # WPS 邮箱业务模拟数据
│   ├── init_database.py        # 一键初始化
│   └── README.md               # 数据库操作说明
├── docs/                       # 项目文档
├── escrcpy/                    # 设备投屏工具
├── start.py                    # 一键启动脚本
└── README.md
```

---

## 数据库初始化

详见 [`database/README.md`](database/README.md)，主要操作：

| 脚本 | 说明 |
|------|------|
| `01_create_database.py` | 创建 `mobile_test_platform` 数据库 |
| `02_drop_database.py` | 删除数据库（慎用） |
| `03_create_tables.py` | 创建全部 24 张数据表 |
| `04_drop_tables.py` | 删除所有表（慎用） |
| `05_insert_test_data.py` | 插入通用测试数据（多项目/迭代/需求/用例/任务） |
| `06_clear_table_data.py` | 清空所有表数据（保留表结构） |
| `07_test_connection.py` | 测试数据库连接 |
| `08_seed_wps_email_data.py` | 插入 WPS 邮箱业务模拟数据 |
| `init_database.py` | 一键初始化（创建库 → 建表 → 造数） |

---

## 邮箱配置（QQ 邮箱验证码登录 & 找回密码）

使用邮箱验证码登录和忘记密码功能前，需配置 QQ 邮箱 SMTP。

### 获取授权码

1. 登录 [QQ 邮箱](https://mail.qq.com) → **设置** → **账户**
2. 开启 **IMAP/SMTP 服务**
3. 按提示获取 **授权码**

### 配置环境变量

在 `backend/.env` 中填写：

```env
SMTP_USER=你的QQ邮箱@qq.com
SMTP_PASSWORD=授权码
```

配置完成后，用户在 **个人中心** 或 **用户管理** 中绑定 QQ 邮箱即可使用邮箱验证码登录和找回密码功能。

---

## AI 用例生成

平台支持通过 AI 大模型自动生成测试用例，支持上传需求文档（.docx / .pdf / .txt）辅助生成。

配置方式见 [`docs/AI_GENERATE_CASE_CONFIG.md`](docs/AI_GENERATE_CASE_CONFIG.md)。

---

## 内网访问

如需局域网内其他设备访问平台，请参考 [`docs/内网访问说明.md`](docs/内网访问说明.md)。

---

## 文档

| 文档 | 说明 |
|------|------|
| [安装部署指南](docs/INSTALLATION.md) | 环境搭建与部署 |
| [开发指南](docs/DEVELOPMENT.md) | 架构设计、代码规范、开发流程 |
| [用户手册](docs/USER_MANUAL.md) | 功能使用说明 |
| [API 文档](docs/API.md) | 接口说明 |
| [AI 用例生成配置](docs/AI_GENERATE_CASE_CONFIG.md) | AI 功能配置与使用 |
| [消息通知设计](docs/消息通知机制设计方案.md) | 消息中心设计方案 |
| [权限配置设计](docs/功能埋点与角色权限可视化配置设计方案.md) | 角色权限设计方案 |
| [内网访问说明](docs/内网访问说明.md) | 局域网访问配置 |

---

## 许可证

本项目采用 [MIT License](LICENSE)。
