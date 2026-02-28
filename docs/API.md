# API 文档

## 概述

移动测试平台 API 提供设备管理、测试用例管理、测试任务执行、报告生成等功能。所有 API 基于 RESTful 设计，使用 JSON 格式进行数据交换。

## 基础信息

- **Base URL**: `http://localhost:8081/api`（开发模式，Vite 代理到后端）
- **后端直连**: `http://127.0.0.1:5000/api`
- **认证方式**: 基于 Session 的 Cookie 认证（Flask-Login）
- **数据格式**: JSON
- **字符编码**: UTF-8

## 认证机制

本系统使用 Flask-Login 基于 Session 的认证方式，登录成功后服务端通过 `Set-Cookie` 设置会话 Cookie，后续请求浏览器自动携带 Cookie 完成身份验证。

### 登录

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "password123"
}
```

**响应:**
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "user": {
      "id": 1,
      "username": "admin",
      "real_name": "管理员",
      "phone": "13800138000",
      "email": "admin@qq.com",
      "role": "super",
      "gender": "male",
      "department": "技术部",
      "is_active": true
    },
    "permissions": ["user.list", "user.create", "project.list", "..."]
  }
}
```

### 登录失败示例

```json
{
  "code": 401,
  "message": "用户名或密码错误"
}
```

### 使用 Cookie 访问 API

登录成功后，后续请求自动携带 Cookie，无需额外设置 Header：

```http
GET /api/users
Cookie: session=<自动携带>
```

未登录访问需认证的接口会返回 401。

## 通用响应格式

### 成功响应

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    // 具体数据
  }
}
```

### 错误响应

```json
{
  "code": 400,
  "message": "请求参数错误"
}
```

### 分页响应

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 100,
      "pages": 5
    }
  }
}
```

## 错误代码

| 错误代码 | 说明 |
|---------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 / 登录失败 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 认证相关 API

**前缀**: `/api/auth`

| 方法 | 路径 | 说明 | 需认证 |
|------|------|------|--------|
| POST/GET | `/login` | 用户登录 | 否 |
| POST | `/register` | 用户注册 | 否 |
| POST/GET | `/logout` | 用户登出 | 否 |
| GET | `/current-user` | 获取当前登录用户信息 | 是 |
| GET | `/check-session` | 检查会话状态 | 否 |
| POST | `/change-password` | 修改密码 | 是 |
| POST | `/forgot-password` | 忘记密码（发送重置邮件） | 否 |
| POST | `/reset-password` | 重置密码（使用令牌） | 否 |
| GET | `/permissions` | 获取当前用户权限列表 | 是 |

### 邮箱登录

| 方法 | 路径 | 说明 | 需认证 |
|------|------|------|--------|
| POST | `/send-login-code` | 发送 QQ 邮箱登录验证码 | 否 |
| POST | `/login-by-email` | 邮箱验证码登录 | 否 |

### 邮箱绑定/解绑

| 方法 | 路径 | 说明 | 需认证 |
|------|------|------|--------|
| POST | `/send-bind-email-code` | 发送邮箱绑定验证码 | 否 |
| POST | `/confirm-email-binding` | 确认邮箱绑定 | 是 |
| POST | `/send-unbind-email-code` | 发送解绑邮箱验证码 | 是 |
| POST | `/unbind-email` | 解除邮箱绑定 | 是 |

### 双因素认证（2FA）

| 方法 | 路径 | 说明 | 需认证 |
|------|------|------|--------|
| POST | `/enable-2fa` | 启用双因素认证 | 是 |
| POST | `/verify-2fa` | 验证双因素认证 | 是 |
| POST | `/disable-2fa` | 禁用双因素认证 | 是 |

### 注册

```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "testuser",
  "phone": "13800138001",
  "password": "123456",
  "real_name": "测试用户",
  "gender": "male",
  "department": "测试部"
}
```

### 修改密码

```http
POST /api/auth/change-password
Content-Type: application/json

{
  "old_password": "旧密码",
  "new_password": "新密码"
}
```

### 忘记密码

```http
POST /api/auth/forgot-password
Content-Type: application/json

{
  "email": "123456789@qq.com"
}
```

### 重置密码

```http
POST /api/auth/reset-password
Content-Type: application/json

{
  "token": "重置令牌",
  "password": "新密码"
}
```

---

## 用户管理 API

**前缀**: `/api/users`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/` | 获取用户列表（支持搜索、角色、状态筛选） | user.list |
| GET | `/options` | 获取用户选项列表（下拉用，仅需登录） | 仅登录 |
| GET | `/<user_id>` | 获取用户详情 | user.list |
| POST | `/` | 创建用户 | user.create |
| PUT | `/<user_id>` | 更新用户信息 | user.edit |
| DELETE | `/<user_id>` | 删除用户 | user.delete |
| POST | `/<user_id>/reset-password` | 重置用户密码 | user.edit |
| POST | `/<user_id>/toggle-status` | 切换用户启用/禁用状态 | user.edit |
| POST | `/<user_id>/confirm-email` | 管理员为用户绑定邮箱 | user.edit |
| GET | `/roles` | 获取角色列表 | 仅登录 |

### 获取用户列表

```http
GET /api/users?page=1&size=20&search=test&role=tester&is_active=true
```

**响应:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "users": [
      {
        "id": 1,
        "username": "admin",
        "real_name": "管理员",
        "phone": "13800138000",
        "email": "admin@qq.com",
        "role": "super",
        "gender": "male",
        "department": "技术部",
        "is_active": true
      }
    ],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 1,
      "pages": 1
    }
  }
}
```

### 创建用户

```http
POST /api/users
Content-Type: application/json

{
  "username": "newuser",
  "phone": "13800138002",
  "password": "123456",
  "real_name": "新用户",
  "role": "tester",
  "gender": "male",
  "department": "测试部"
}
```

### 角色类型

| 角色值 | 说明 |
|--------|------|
| super | 超级管理员 |
| manager | 管理员 |
| tester | 测试人员 |
| admin | 普通成员 |

---

## 项目管理 API

**前缀**: `/api/projects`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/` | 获取项目列表（支持搜索、状态、优先级筛选） | project.list |
| GET | `/<project_id>` | 获取项目详情 | 仅登录 |
| POST | `/` | 创建项目 | project.create |
| PUT | `/<project_id>` | 更新项目 | project.edit |
| DELETE | `/<project_id>` | 删除项目 | project.delete |
| GET | `/<project_id>/members` | 获取项目成员列表 | 仅登录 |
| POST | `/<project_id>/members` | 添加项目成员 | 仅登录 |
| DELETE | `/<project_id>/members/<member_id>` | 移除项目成员 | 仅登录 |

### 版本需求

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/<project_id>/version-requirements` | 获取项目版本需求列表 | requirement.list |
| GET | `/version-requirements` | 获取所有版本需求列表 | requirement.list |
| POST | `/<project_id>/version-requirements` | 创建版本需求 | requirement.create |
| PUT | `/<project_id>/version-requirements/<id>` | 更新版本需求 | requirement.edit |
| DELETE | `/<project_id>/version-requirements/<id>` | 删除版本需求 | requirement.delete |

### 项目迭代

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/<project_id>/iterations` | 获取项目迭代列表 | iteration.list |

### 创建项目

```http
POST /api/projects/
Content-Type: application/json

{
  "project_name": "测试项目",
  "description": "项目描述（不超过100字）",
  "start_date": "2025-01-01",
  "end_date": "2025-06-30",
  "owner_id": 1,
  "priority": "medium",
  "status": "not_started",
  "tags": ["标签1", "标签2"],
  "members": [
    {"user_id": 2, "role": "developer"},
    {"user_id": 3, "role": "tester"}
  ]
}
```

---

## 迭代管理 API

**前缀**: `/api/iterations`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/` | 创建迭代 | iteration.create |
| POST | `/projects/<project_id>/iterations` | 在指定项目下创建迭代 | iteration.create |
| GET | `/projects/<project_id>/iterations` | 获取项目迭代列表 | iteration.list |
| GET | `/<iteration_id>` | 获取迭代详情 | 仅登录 |
| PUT | `/<iteration_id>` | 更新迭代 | iteration.edit |
| DELETE | `/<iteration_id>` | 删除迭代 | iteration.delete |
| POST | `/<iteration_id>/copy` | 复制迭代 | iteration.create |
| GET | `/<iteration_id>/stats` | 获取迭代统计 | 仅登录 |
| GET | `/<iteration_id>/requirements` | 获取迭代关联需求 | 仅登录 |

---

## 设备管理 API

**前缀**: `/api/devices`

### 设备 CRUD

| 方法 | 路径 | 说明 | 需认证 |
|------|------|------|--------|
| GET | `/` | 获取设备列表（支持搜索、系统类型、状态筛选） | 是 |
| GET | `/<device_id>` | 获取设备详情 | 是 |
| POST | `/` | 创建设备 | 是 |
| PUT | `/<device_id>` | 更新设备信息 | 是 |
| DELETE | `/<device_id>` | 删除设备 | 是 |

### 设备状态与选项

| 方法 | 路径 | 说明 | 需认证 |
|------|------|------|--------|
| GET | `/<device_id>/status` | 获取设备 ADB 连接状态 | 是 |
| GET | `/os-types` | 获取操作系统类型选项 | 是 |
| GET | `/status-options` | 获取设备状态选项 | 是 |

### ADB 操作

| 方法 | 路径 | 说明 | 需认证 |
|------|------|------|--------|
| GET | `/adb/devices` | 获取当前 ADB 连接的设备列表 | 是 |
| POST | `/adb/command` | 执行 ADB 命令（含投屏 scrcpy） | 是 |

### 任务执行

| 方法 | 路径 | 说明 | 需认证 |
|------|------|------|--------|
| POST | `/<device_id>/tasks` | 在指定设备上执行任务（shell/python/install） | 是 |
| POST | `/batch-tasks` | 批量执行测试任务 | 是 |
| POST | `/schedule-batch-tasks` | 定时批量执行测试任务 | 是 |

### 获取设备列表

```http
GET /api/devices?page=1&size=20&search=pixel&os_type=android&status=online
```

### 创建设备

```http
POST /api/devices
Content-Type: application/json

{
  "device_name": "Pixel 6",
  "device_model": "Pixel 6",
  "os_type": "android",
  "os_version": "14",
  "device_id": "设备序列号",
  "status": "offline",
  "owner_id": 1
}
```

### 执行 ADB 命令

```http
POST /api/devices/adb/command
Content-Type: application/json

{
  "command": "-s 设备序列号 shell pm list packages"
}
```

---

## 测试用例管理 API

**前缀**: `/api/test-cases`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/` | 获取测试用例列表 | testcase.list |
| GET | `/suite/<suite_id>` | 获取指定套件下的用例列表 | testcase.list |
| GET | `/<case_id>` | 获取测试用例详情 | testcase.list |
| POST | `/` | 创建测试用例 | testcase.create |
| PUT | `/<case_id>` | 更新测试用例 | testcase.edit |
| DELETE | `/<case_id>` | 删除测试用例 | testcase.delete |
| POST | `/batch-delete` | 批量删除测试用例 | testcase.delete |
| GET | `/priority-options` | 获取优先级选项 | 仅登录 |
| GET | `/status-options` | 获取状态选项 | 仅登录 |

---

## 测试套件管理 API

**前缀**: `/api/test-suites`

| 方法 | 路径 | 说明 | 需认证 |
|------|------|------|--------|
| GET | `/` | 获取测试套件列表 | 是 |
| GET | `/<suite_id>` | 获取测试套件详情 | 是 |
| POST | `/` | 创建测试套件 | 是 |
| PUT | `/<suite_id>` | 更新测试套件 | 是 |
| DELETE | `/<suite_id>` | 删除测试套件 | 是 |
| GET | `/tree` | 获取套件树结构 | 是 |
| GET | `/<suite_id>/tree` | 获取指定套件子树 | 是 |
| GET | `/options` | 获取套件选项列表 | 是 |
| GET | `/<suite_id>/test-cases` | 获取套件下的用例列表 | 是 |

---

## 套件-用例关联 API

**前缀**: `/api/suite-case-relations`

| 方法 | 路径 | 说明 | 需认证 |
|------|------|------|--------|
| GET | `/<suite_id>/cases` | 获取套件关联的用例列表 | 是 |
| POST | `/<suite_id>/add-cases` | 向套件添加用例 | 是 |
| POST | `/<suite_id>/remove-cases` | 从套件移除用例 | 是 |
| GET | `/<suite_id>/available-cases` | 获取可添加到套件的用例 | 是 |
| POST | `/<suite_id>/move-cases` | 移动用例到其他套件 | 是 |

---

## 测试任务管理 API

**前缀**: `/api/test-tasks`

### 任务 CRUD

| 方法 | 路径 | 说明 | 需认证 |
|------|------|------|--------|
| GET | `/` | 获取测试任务列表 | 是 |
| GET | `/<task_id>` | 获取测试任务详情 | 是 |
| POST | `/` | 创建测试任务 | 是 |
| PUT | `/<task_id>` | 更新测试任务 | 是 |
| DELETE | `/<task_id>` | 删除测试任务 | 是 |
| GET | `/options` | 获取任务选项列表 | 是 |

### 任务目录

| 方法 | 路径 | 说明 | 需认证 |
|------|------|------|--------|
| GET | `/task-folders` | 获取任务目录列表 | 是 |
| POST | `/task-folders` | 创建任务目录 | 是 |
| PATCH | `/task-folders/<folder_id>` | 更新任务目录 | 是 |
| DELETE | `/task-folders/<folder_id>` | 删除任务目录 | 是 |

### 任务执行流程

| 方法 | 路径 | 说明 | 需认证 |
|------|------|------|--------|
| POST | `/<task_id>/execute` | 开始执行任务 | 是 |
| POST | `/<task_id>/pause` | 暂停任务 | 是 |
| POST | `/<task_id>/resume` | 恢复任务 | 是 |
| POST | `/<task_id>/complete` | 完成任务 | 是 |
| POST | `/<task_id>/cancel` | 取消任务 | 是 |

### 任务关联数据

| 方法 | 路径 | 说明 | 需认证 |
|------|------|------|--------|
| GET | `/<task_id>/executions` | 获取任务用例执行记录 | 是 |
| POST | `/<task_id>/executions/<case_id>` | 提交用例执行结果 | 是 |
| GET | `/<task_id>/statistics` | 获取任务统计数据 | 是 |
| GET | `/<task_id>/devices` | 获取任务关联设备 | 是 |
| GET | `/<task_id>/test-cases` | 获取任务关联用例 | 是 |

---

## 报告管理 API

**前缀**: `/api/reports`

| 方法 | 路径 | 说明 | 需认证 |
|------|------|------|--------|
| GET | `/` | 获取报告列表 | 是 |
| GET | `/record/<report_id>` | 获取报告详情 | 是 |
| DELETE | `/<report_id>` | 删除报告 | 是 |
| POST | `/batch-delete` | 批量删除报告 | 是 |
| POST | `/generate/<task_id>` | 生成测试报告 | 是 |
| GET | `/task/<task_id>/data` | 获取任务报告数据 | 是 |
| GET | `/<task_id>/data` | 获取任务报告数据（别名） | 是 |

---

## 评审任务管理 API

**前缀**: `/api/review-tasks`

### 评审操作

| 方法 | 路径 | 说明 | 需认证 |
|------|------|------|--------|
| POST | `/test-suites/<suite_id>/initiate-review` | 发起用例集评审 | 是 |
| GET | `/<task_id>` | 获取评审任务详情 | 是 |
| PUT | `/<task_id>/case-reviews/<case_id>` | 提交单条用例评审结果 | 是 |
| POST | `/<task_id>/complete` | 完成评审 | 是 |
| GET | `/<task_id>/case-reviews` | 获取评审任务下的用例评审列表 | 是 |
| POST | `/<task_id>/restart-review` | 重新开始评审 | 是 |
| POST | `/<task_id>/reinitiate-review` | 重新发起评审 | 是 |
| POST | `/<task_id>/reject-review` | 驳回评审 | 是 |
| GET | `/test-suites/<suite_id>/review-status` | 获取套件评审状态 | 是 |

### 评审中心

| 方法 | 路径 | 说明 | 需认证 |
|------|------|------|--------|
| GET | `/review-center/my-tasks` | 我的待评审任务 | 是 |
| GET | `/review-center/my-initiated` | 我发起的评审 | 是 |
| GET | `/review-center/recent-history` | 最近评审历史 | 是 |

### 评审历史

| 方法 | 路径 | 说明 | 需认证 |
|------|------|------|--------|
| GET | `/<task_id>/review-history` | 获取评审任务历史记录 | 是 |
| GET | `/review-history/<history_id>` | 获取评审历史详情 | 是 |

---

## 通知管理 API

**前缀**: `/api/notifications`

| 方法 | 路径 | 说明 | 需认证 |
|------|------|------|--------|
| GET | `/` | 获取通知列表 | 是 |
| GET | `/unread-count` | 获取未读通知数量 | 是 |
| PATCH/PUT | `/<notification_id>/read` | 标记单条通知为已读 | 是 |
| DELETE | `/<notification_id>` | 删除通知 | 是 |
| PATCH/PUT | `/<notification_id>/pin` | 置顶/取消置顶通知 | 是 |
| PUT | `/read` | 批量标记已读 | 是 |
| POST | `/read-all` | 全部标记已读 | 是 |
| POST | `/unread-all` | 全部标记未读 | 是 |
| POST/DELETE | `/clear` | 清空通知 | 是 |

---

## 角色权限管理 API

**前缀**: `/api/roles`

| 方法 | 路径 | 说明 | 需认证 |
|------|------|------|--------|
| GET | `/permissions` | 获取所有权限定义 | 是 |
| GET | `/<role>/permissions` | 获取指定角色的权限列表 | 是 |
| PUT | `/<role>/permissions` | 更新指定角色的权限 | 是 |
| GET | `/list` | 获取角色列表 | 是 |

---

## 系统设置 API

**前缀**: `/api/settings`

| 方法 | 路径 | 说明 | 需认证 |
|------|------|------|--------|
| GET | `/system` | 获取系统设置 | 是 |
| PUT | `/system` | 更新系统设置 | 是 |
| GET | `/user` | 获取用户个人设置 | 是 |
| PUT | `/user` | 更新用户个人设置 | 是 |

---

## 首页数据 API

**前缀**: `/api/home`

| 方法 | 路径 | 说明 | 需认证 |
|------|------|------|--------|
| GET | `/stats` | 获取首页统计数据 | 是 |
| GET | `/activities` | 获取最近活动记录 | 是 |
| GET | `/task-trend` | 获取任务趋势数据 | 是 |
| GET | `/device-status` | 获取设备状态统计 | 是 |
| GET | `/recent-projects` | 获取最近项目 | 是 |
| GET | `/task-status-distribution` | 获取任务状态分布 | 是 |

---

## AI 用例生成 API

**前缀**: `/api/ai-tasks`

| 方法 | 路径 | 说明 | 需认证 |
|------|------|------|--------|
| POST | `/generate-cases` | AI 生成测试用例 | 是 |
| GET | `/task-status/<task_id>` | 查询 AI 任务状态 | 是 |
| GET | `/tasks` | 获取 AI 任务列表 | 是 |

---

## 文件管理 API

**前缀**: `/api/files`

用于设备脚本文件、系统 Logo 等文件的上传和管理。

---

## WebSocket

本系统使用 Flask-SocketIO 实现实时通信，客户端通过 Socket.IO 协议连接。

### 连接地址

开发模式下通过 Vite 代理：

```
http://localhost:8081/socket.io
```

直连后端：

```
http://127.0.0.1:5000/socket.io
```

### 功能

- 实时通知推送
- 设备状态更新
- 任务进度更新

---

## cURL 示例

### 登录

```bash
curl -X POST http://localhost:8081/api/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"username":"admin","password":"password123"}'
```

### 获取用户列表（携带 Cookie）

```bash
curl -X GET "http://localhost:8081/api/users?page=1&size=20" \
  -b cookies.txt
```

### 获取设备列表

```bash
curl -X GET "http://localhost:8081/api/devices?page=1&size=20" \
  -b cookies.txt
```

### 创建项目

```bash
curl -X POST http://localhost:8081/api/projects/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "project_name": "测试项目",
    "description": "项目描述",
    "start_date": "2025-01-01",
    "end_date": "2025-06-30",
    "owner_id": 1
  }'
```
