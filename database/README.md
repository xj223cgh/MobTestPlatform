# 数据库操作说明

本文档说明数据库脚本的用途、执行顺序及造数方式，便于在**新环境**快速完成数据库初始化。

**约定**：`database/` 下脚本仅负责**空库/标准建表**与造数，**不包含**对已有生产库的 ALTER、补列等迁移逻辑；旧库升级请自行备份并编写迁移。

---

## 1. 环境与配置

- **Python**：3.8+
- **依赖**：`pymysql`、`werkzeug`（造数脚本密码哈希）、`python-dotenv`（与后端一致，用于读取 `backend/.env`）
- **数据库**：MySQL 5.7+ / 8.x / MariaDB 10.2+，字符集 `utf8mb4`

连接由 `database/config.py` 读取环境变量（`MYSQL_HOST`、`MYSQL_USER`、`MYSQL_PASSWORD`、`MYSQL_DATABASE` 等），缺省与本地开发一致。存在 `backend/.env` 时会自动加载。

---

## 2. 脚本说明

| 脚本 | 说明 |
|------|------|
| `01_create_database.py` | 创建数据库（若不存在） |
| `02_drop_database.py` | 删除整个数据库（需确认，慎用） |
| `03_create_tables.py` | 创建全部数据表（当前约 27 张，结构以脚本内 DDL 为准） |
| `04_drop_tables.py` | 删除所有表（需确认，慎用） |
| `05_insert_test_data.py` | 用户 + WPS 邮箱业务 + WPS 会议业务测试数据（项目、迭代、需求、用例库、任务、评审、设备、报告等） |
| `06_clear_table_data.py` | 清空所有表数据（保留表结构，需确认） |
| `07_test_connection.py` | 测试数据库连接 |
| `config.py` | 数据库连接配置 |
| `init_database.py` | 一键初始化（依次执行 01 → 03 → 05） |

`03_create_tables.py` 中 DDL 使用 `CREATE TABLE IF NOT EXISTS`，在**空库**或**重复执行**时不会报错；若需在已有表上强制重建，请先执行 `04_drop_tables.py` 或使用新库。

---

## 3. 推荐执行顺序

### 新环境首次建库

```bash
# 在项目根目录执行
python database/01_create_database.py
python database/03_create_tables.py
python database/05_insert_test_data.py
```

或使用一键初始化：

```bash
python database/init_database.py
```

### 仅重新造数（表已存在）

```bash
python database/05_insert_test_data.py
```

脚本会先清空相关表，再插入用户与 WPS 邮箱业务数据。

### 清空数据（不插数据）

```bash
python database/06_clear_table_data.py
```

### 重建表结构（慎用，会丢数据）

```bash
python database/04_drop_tables.py
python database/03_create_tables.py
```

---

## 4. 数据表一览

`03_create_tables.py` 创建以下 27 张表：

| 表名 | 说明 |
|------|------|
| `users` | 用户表 |
| `email_verify_codes` | 邮箱验证码表 |
| `role_permissions` | 角色权限配置表 |
| `projects` | 项目表 |
| `project_members` | 项目成员表 |
| `devices` | 设备表 |
| `iterations` | 迭代表 |
| `version_requirements` | 版本需求表 |
| `test_suites` | 测试套件表（文件夹 + 用例集） |
| `test_cases` | 测试用例表 |
| `task_folders` | 任务文件夹表 |
| `test_tasks` | 测试任务表（用例执行 + 设备脚本） |
| `test_case_executions` | 用例执行记录表 |
| `task_case_relation` | 任务-用例关联表 |
| `task_device_relation` | 任务-设备关联表 |
| `task_case_snapshots` | 任务用例快照表 |
| `test_suite_review_tasks` | 用例集评审任务表 |
| `test_case_review_details` | 用例评审详情表 |
| `test_suite_review_history` | 评审历史记录表 |
| `test_case_review_history` | 用例评审历史表 |
| `system_settings` | 系统设置表 |
| `user_settings` | 用户设置表 |
| `reports` | 报告表 |
| `notifications` | 消息通知表 |
| `agents` | 本机 Agent 表（设备管理用 Agent 注册与心跳） |
| `user_agent_bindings` | 用户与本机 Agent 绑定表（一用户绑定一台 Agent） |
| `agent_binding_codes` | Agent 绑定码表（短期绑定码，供一键绑定或手动输入） |

### 4.1 角色默认权限（`role_permissions` 无记录时）

各角色在权限配置页上的**初始勾选**由后端代码决定：见 **`backend/app/constants/permissions.py`** 中的 **`DEFAULT_ROLE_PERMISSIONS`**。

- **`manager`**：五类模块全开（含权限配置、用户管理）。
- **`tester`（测试人员）**：项目管理（入口 + 新建 + 编辑）、迭代与需求四类操作全开（含删除迭代/需求）；**不含** `project.delete`、**不含** 权限配置与用户管理相关埋点。
- **`admin`（普通成员，业务上常给实习生等账号）**：项目管理（入口 + 新建 + 编辑）、迭代（入口 + 新建 + 编辑）、需求（入口 + 新建 + 编辑 + 删除）；**不含** `project.delete`、`iteration.delete` 及权限/用户模块。

> **已有环境**：若表 `role_permissions` 里已有 `tester` / `admin` 的行，修改上述 Python 默认值**不会自动覆盖**库内数据。需要新默认值时，可在权限配置页重新保存该角色，或删除对应角色的 `role_permissions` 记录后由系统按默认值重新生效。

---

## 5. 造数内容说明

### 测试数据（05_insert_test_data.py）

| 数据类型 | 说明 |
|----------|------|
| **用户** | 特殊账号：Lethe（超级管理员）、Manager（管理员）、Tester（测试人员）、Admin（普通成员）；测试用户：赵敏、陈静、杨帆、周杰、吴磊、郑丽、孙浩。密码统一 `123321` |
| **业务数据** | WPS 邮箱业务：6 个迭代、16 条需求、14 个功能模块用例集、用例评审、测试任务、设备脚本任务及报告等；WPS 会议业务：1 个项目、3 个迭代、5 条需求、4 个功能模块用例集、用例与任务、报告等 |

---

## 6. 表依赖关系

清空或删除表时需考虑外键依赖（脚本中已处理），主要依赖链：

```
users（无依赖）
├── projects → users
│   ├── project_members → projects, users
│   ├── iterations → projects, users
│   ├── version_requirements → projects, iterations, users
│   ├── test_suites → projects, users, version_requirements
│   │   ├── test_cases → test_suites, projects, users
│   │   ├── test_suite_review_tasks → test_suites, users
│   │   │   ├── test_case_review_details → review_tasks, test_cases, users
│   │   │   └── test_suite_review_history → review_tasks, test_suites, users
│   │   │       └── test_case_review_history → review_history, test_cases, users
│   │   └── test_tasks → projects, iterations, test_suites, users
│   │       ├── task_case_relation → test_tasks, test_cases
│   │       ├── task_device_relation → test_tasks, devices
│   │       ├── task_case_snapshots → test_tasks, test_cases
│   │       ├── test_case_executions → test_tasks, test_cases, users
│   │       └── reports → test_tasks, users
├── devices → users
├── notifications → users
├── agents（无外键，本机 Agent 注册）
├── user_agent_bindings → users, agents
├── agent_binding_codes → users
├── email_verify_codes（无外键）
└── role_permissions（无外键）
```
