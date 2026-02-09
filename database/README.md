# 数据库操作说明

本文档说明本项目中与数据库相关的脚本、执行顺序及造数方式，便于在新设备或新环境中快速建库与造数。

---

## 1. 环境与配置

- **Python**：建议 3.8+
- **依赖**：`pymysql`、`werkzeug`（造数脚本中用于密码哈希）
- **数据库**：MySQL 5.7+ / MariaDB 10.2+，字符集 `utf8mb4`

连接配置在 `database/config.py` 中修改：

```python
DB_CONFIG = {
    'host': 'localhost',      # 数据库主机
    'user': 'root',
    'password': '123456',      # 密码
    'database': 'mobile_test_platform',
    'charset': 'utf8mb4'
}
```

新设备上请根据实际环境修改 `host`、`user`、`password`。

---

## 2. 脚本说明与执行顺序

| 脚本 | 说明 |
|------|------|
| `01_create_database.py` | 创建数据库（若不存在） |
| `02_drop_database.py` | 删除整个数据库（慎用） |
| `03_create_tables.py` | 创建所有表结构 |
| `04_drop_tables.py` | 删除所有表（不删库） |
| `05_insert_test_data.py` | **造数**：清空后插入测试数据（用户/项目/迭代/需求/用例集/用例/任务等） |
| `06_clear_table_data.py` | 仅清空所有表数据（不删表） |
| `07_test_connection.py` | 测试数据库连接 |

**说明**：`03_create_tables.py` 已包含完整表结构（含主键、枚举 rejected、executor_id 可空等），新环境只需按顺序执行 01 → 03 → 05 即可，无需额外修复脚本。

**推荐执行顺序：**

1. **首次在新设备/新环境建库并造数：**
   ```bash
   # 在项目根目录执行
   python database/01_create_database.py
   python database/03_create_tables.py
   python database/05_insert_test_data.py
   ```

2. **仅重新造数（表已存在）：**
   ```bash
   python database/05_insert_test_data.py
   ```
   会先清空相关表再插入测试数据。

3. **只清空数据、不插数据：**
   ```bash
   python database/06_clear_table_data.py
   ```

4. **重建表结构（慎用，会丢数据）：**
   ```bash
   python database/04_drop_tables.py
   python database/03_create_tables.py
   ```

---

## 3. 造数内容说明（05_insert_test_data.py）

### 3.1 清空范围

造数前会 **TRUNCATE** 以下表（含 `reports`）：

- 用户、项目、项目成员、迭代、版本需求、需求标准
- 设备、测试套件、测试用例、测试任务
- 任务-用例关联、任务-设备关联、用例执行记录
- 评审相关表、系统/用户设置、**报告表 reports**

即每次执行 05 都会清空测试报告数据；报告需通过「任务完成且开启自动生成」或「手动生成」重新产生。

### 3.2 测试报告与自动生成

- **报告表**：`reports` 在造数时会被清空，造数完成后报告列表为空。
- **自动生成规则**：仅当 **任务状态变更为「已完成」** 且当前用户设置了 **「自动生成报告」** 时，系统才会在该任务完成时自动生成一条报告并落库。
- 若未开启自动生成，可通过任务详情页的「生成报告」按钮手动生成。

### 3.3 插入数据概览

| 数据类型 | 说明 |
|----------|------|
| **用户** | 特殊账号（保留）：Lethe(超级管理员)、Manager(项目经理)、Tester(测试主管)、Admin(系统管理员)；测试用户真实人名：赵敏、陈静、杨帆、周杰、吴磊、郑丽、孙浩；密码统一为 `123321`。系统中创建人、负责人、更新人均关联上述用户，展示为真实姓名。 |
| **项目/成员/迭代/需求** | 多项目（移动端应用测试，如电商/金融/社交/游戏等）、多迭代、多需求，用于挂接用例与任务。 |
| **测试套件** | 每项目：根文件夹 → 子文件夹「功能测试」「专项测试」→ 各子文件夹下 2 个用例集（功能测试：登录与权限、核心流程；专项测试：兼容性测试、性能测试）。不涉及「自动化」字眼，业务为移动端应用测试。 |
| **测试用例** | 按用例集类型生成：登录与权限 6 条、核心流程 8 条、兼容性测试 6 条、性能测试 6 条，步骤/预期/前置等字段完整。 |
| **用例执行任务** | 每个用例集一条「用例执行」任务，关联项目、迭代、用例集；含计划开始/结束时间（scheduled_time、scheduled_end_time）、创建人/负责人为真实用户；状态含待执行/执行中/已完成。 |
| **任务-用例关联** | 按任务关联的用例集，将该套件下全部用例写入 `task_case_relation`。 |
| **用例执行记录** | 对状态为「已完成」的任务，写入 `test_case_executions`，并回写用例状态。 |

---

## 4. 新设备快捷造数步骤

1. 安装 MySQL/MariaDB，并创建好用于连接的账号。
2. 在项目根目录下修改 `database/config.py` 中的 `host`、`user`、`password`（如需）。
3. 在项目根目录依次执行：
   ```bash
   python database/01_create_database.py
   python database/03_create_tables.py
   python database/05_insert_test_data.py
   ```
4. 使用任意造数账号登录（如 Lethe 或 赵敏 / 123321），即可在系统中看到完整测试数据；报告需在完成任务或手动生成后才会出现。

---

## 5. 表依赖顺序（清空/删除时参考）

清空或删除表时需考虑外键，脚本中已按依赖顺序处理。主要依赖关系：

- `users` 无依赖
- `projects` → users
- `project_members` → projects, users
- `iterations` → projects, users
- `version_requirements` → projects, iterations, users
- `devices` 无依赖
- `test_suites` → projects, users, version_requirements
- `test_cases` → test_suites, projects, users, version_requirements, iterations
- `test_tasks` → users, projects, iterations, test_suites, version_requirements
- `task_case_relation` → test_tasks, test_cases
- `test_case_executions` → test_tasks, test_cases, projects, iterations, users
- `reports` → test_tasks
- 评审、设置等表见 `04_drop_tables.py` / `06_clear_table_data.py` 中的表列表
