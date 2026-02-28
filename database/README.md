# 数据库操作说明

本文档说明数据库脚本的用途、执行顺序及造数方式，便于在新环境中快速完成数据库初始化。

---

## 1. 环境与配置

- **Python**：3.8+
- **依赖**：`pymysql`、`werkzeug`（造数脚本中用于密码哈希）
- **数据库**：MySQL 5.7+ / MariaDB 10.2+，字符集 `utf8mb4`

连接配置位于 `database/config.py`：

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'mobile_test_platform',
    'charset': 'utf8mb4'
}
```

新环境请根据实际情况修改 `host`、`user`、`password`。

---

## 2. 脚本说明

| 脚本 | 说明 |
|------|------|
| `01_create_database.py` | 创建数据库（若不存在） |
| `02_drop_database.py` | 删除整个数据库（需确认，慎用） |
| `03_create_tables.py` | 创建全部 24 张数据表 |
| `04_drop_tables.py` | 删除所有表（需确认，慎用） |
| `05_insert_test_data.py` | 通用测试数据：多项目、多迭代、多需求、用例库、测试任务、评审等 |
| `06_clear_table_data.py` | 清空所有表数据（保留表结构，需确认） |
| `07_test_connection.py` | 测试数据库连接 |
| `08_seed_wps_email_data.py` | WPS 邮箱业务模拟数据（保留用户，替换业务数据） |
| `config.py` | 数据库连接配置 |
| `init_database.py` | 一键初始化（依次执行 01 → 03 → 05） |

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

脚本会先清空相关表再插入测试数据。

### 切换到 WPS 邮箱业务数据

```bash
python database/08_seed_wps_email_data.py
```

该脚本保留用户数据，仅替换业务数据（项目、迭代、需求、用例、任务、评审、报告等）。

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

`03_create_tables.py` 创建以下 24 张表：

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

---

## 5. 造数内容说明

### 通用测试数据（05_insert_test_data.py）

| 数据类型 | 说明 |
|----------|------|
| **用户** | 特殊账号：Lethe（超级管理员）、Manager（管理员）、Tester（测试人员）、Admin（普通成员）；测试用户：赵敏、陈静、杨帆、周杰、吴磊、郑丽、孙浩。密码统一 `123321` |
| **项目** | 12 个移动端应用测试项目（电商、金融、社交、游戏等） |
| **迭代** | 每项目 4~6 个迭代，状态覆盖 planning / active / completed / cancelled |
| **需求** | 每项目 5~8 个版本需求，优先级 P0~P4 |
| **用例库** | 每项目：根文件夹 → 功能测试/专项测试 → 登录与权限/核心流程/兼容性测试/性能测试用例集 |
| **测试用例** | 按用例集类型生成 35~50 条，步骤/预期/前置等字段完整 |
| **测试任务** | 用例执行任务 + 设备脚本任务，状态含待执行/执行中/已完成 |
| **评审** | 所有用户均有发起与参与评审记录，含完整评审历史 |
| **设备** | 9 台 Android 模拟设备（华为/小米/OPPO/vivo/三星等） |

### WPS 邮箱业务数据（08_seed_wps_email_data.py）

单一 WPS 邮箱业务项目，包含 6 个迭代、16 条需求、14 个功能模块用例集、用例评审、测试任务及报告。

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
├── email_verify_codes（无外键）
└── role_permissions（无外键）
```
