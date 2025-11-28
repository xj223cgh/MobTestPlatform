# API 文档

## 概述

移动测试平台 API 提供完整的设备管理、测试用例管理、任务执行和报告生成功能。所有 API 都基于 RESTful 设计原则，使用 JSON 格式进行数据交换。

## 基础信息

- **Base URL**: `http://localhost:8000/api`
- **API 版本**: v1
- **认证方式**: JWT Token
- **数据格式**: JSON
- **字符编码**: UTF-8

## 认证

### 登录获取 Token
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
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "role": "admin"
    },
    "expires_in": 3600
  }
}
```

### 使用 Token 访问 API
```http
GET /api/devices
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

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
  "message": "请求参数错误",
  "error": "详细错误信息"
}
```

### 分页响应
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "items": [
      // 数据列表
    ],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 100,
      "pages": 5
    }
  }
}
```

## 设备管理 API

### 获取设备列表
```http
GET /api/devices?page=1&size=20&status=online&device_type=android
```

**查询参数:**
- `page`: 页码 (默认: 1)
- `size`: 每页数量 (默认: 20)
- `status`: 设备状态 (online/offline/error)
- `device_type`: 设备类型 (android/ios)
- `search`: 搜索关键词

**响应:**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "iPhone 12",
        "device_id": "iPhone12-001",
        "device_type": "ios",
        "status": "online",
        "os_version": "15.0",
        "brand": "Apple",
        "model": "iPhone12",
        "screen_resolution": "1170x2532",
        "ip_address": "192.168.1.100",
        "last_seen": "2023-12-01T10:30:00Z",
        "created_at": "2023-11-01T08:00:00Z",
        "updated_at": "2023-12-01T10:30:00Z"
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

### 获取设备详情
```http
GET /api/devices/{device_id}
```

**响应:**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": 1,
    "name": "iPhone 12",
    "device_id": "iPhone12-001",
    "device_type": "ios",
    "status": "online",
    "os_version": "15.0",
    "brand": "Apple",
    "model": "iPhone12",
    "screen_resolution": "1170x2532",
    "ip_address": "192.168.1.100",
    "cpu_usage": 15.5,
    "memory_usage": 68.2,
    "battery_level": 85,
    "storage_info": {
      "total": 256000000000,
      "used": 128000000000,
      "available": 128000000000
    },
    "installed_apps": [
      {
        "package_name": "com.example.app",
        "version": "1.0.0",
        "size": 50000000
      }
    ],
    "last_seen": "2023-12-01T10:30:00Z",
    "created_at": "2023-11-01T08:00:00Z",
    "updated_at": "2023-12-01T10:30:00Z"
  }
}
```

### 添加设备
```http
POST /api/devices
Content-Type: application/json

{
  "name": "Samsung Galaxy S21",
  "device_id": "S21-001",
  "device_type": "android",
  "ip_address": "192.168.1.101",
  "port": 5555,
  "description": "测试设备"
}
```

### 更新设备
```http
PUT /api/devices/{device_id}
Content-Type: application/json

{
  "name": "Samsung Galaxy S21 Updated",
  "description": "更新后的描述"
}
```

### 删除设备
```http
DELETE /api/devices/{device_id}
```

### 连接设备
```http
POST /api/devices/{device_id}/connect
```

### 断开设备
```http
POST /api/devices/{device_id}/disconnect
```

### 获取设备截图
```http
GET /api/devices/{device_id}/screenshot
```

**响应:**
```json
{
  "code": 200,
  "message": "截图成功",
  "data": {
    "screenshot_url": "/api/devices/1/screenshot.png",
    "timestamp": "2023-12-01T10:30:00Z"
  }
}
```

### 安装应用
```http
POST /api/devices/{device_id}/install-app
Content-Type: multipart/form-data

file: [应用文件路径]
package_name: com.example.app (可选)
```

### 卸载应用
```http
DELETE /api/devices/{device_id}/apps/{package_name}
```

## 测试用例管理 API

### 获取测试用例列表
```http
GET /api/testcases?page=1&size=20&module=login&priority=high
```

**查询参数:**
- `page`: 页码
- `size`: 每页数量
- `module`: 模块名称
- `priority`: 优先级 (high/medium/low)
- `status`: 状态 (draft/active/archived)
- `search`: 搜索关键词

### 获取测试用例详情
```http
GET /api/testcases/{case_id}
```

**响应:**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": 1,
    "title": "用户登录功能测试",
    "description": "测试用户登录功能的各种场景",
    "module": "authentication",
    "priority": "high",
    "status": "active",
    "preconditions": "用户已注册",
    "steps": [
      {
        "step_number": 1,
        "action": "打开登录页面",
        "expected": "显示登录表单"
      },
      {
        "step_number": 2,
        "action": "输入用户名和密码",
        "expected": "输入框显示正确内容"
      },
      {
        "step_number": 3,
        "action": "点击登录按钮",
        "expected": "登录成功，跳转到首页"
      }
    ],
    "tags": ["登录", "核心功能"],
    "author": {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com"
    },
    "created_at": "2023-11-01T08:00:00Z",
    "updated_at": "2023-12-01T10:30:00Z"
  }
}
```

### 创建测试用例
```http
POST /api/testcases
Content-Type: application/json

{
  "title": "用户注册功能测试",
  "description": "测试用户注册流程",
  "module": "authentication",
  "priority": "medium",
  "preconditions": "用户未注册",
  "steps": [
    {
      "step_number": 1,
      "action": "打开注册页面",
      "expected": "显示注册表单"
    },
    {
      "step_number": 2,
      "action": "填写注册信息",
      "expected": "表单验证通过"
    },
    {
      "step_number": 3,
      "action": "提交注册",
      "expected": "注册成功，显示成功提示"
    }
  ],
  "tags": ["注册", "用户管理"]
}
```

### 更新测试用例
```http
PUT /api/testcases/{case_id}
Content-Type: application/json

{
  "title": "更新后的测试用例标题",
  "priority": "high"
}
```

### 删除测试用例
```http
DELETE /api/testcases/{case_id}
```

### 执行测试用例
```http
POST /api/testcases/{case_id}/execute
Content-Type: application/json

{
  "device_ids": [1, 2],
  "execution_config": {
    "timeout": 300,
    "retry_count": 3,
    "capture_screenshot": true
  }
}
```

## 测试任务管理 API

### 获取测试任务列表
```http
GET /api/test-tasks?page=1&size=20&status=running
```

### 获取测试任务详情
```http
GET /api/test-tasks/{task_id}
```

**响应:**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": 1,
    "name": "回归测试任务",
    "description": "每月回归测试",
    "status": "running",
    "progress": {
      "total": 100,
      "completed": 45,
      "failed": 5,
      "pending": 50,
      "percentage": 45.0
    },
    "test_cases": [
      {
        "id": 1,
        "title": "用户登录测试",
        "status": "completed",
        "result": "passed"
      }
    ],
    "devices": [
      {
        "id": 1,
        "name": "iPhone 12",
        "status": "online"
      }
    ],
    "schedule": {
      "type": "cron",
      "expression": "0 2 1 * *",
      "next_run": "2023-12-01T02:00:00Z"
    },
    "created_at": "2023-11-01T08:00:00Z",
    "updated_at": "2023-12-01T10:30:00Z"
  }
}
```

### 创建测试任务
```http
POST /api/test-tasks
Content-Type: application/json

{
  "name": "新功能测试任务",
  "description": "测试新功能",
  "test_case_ids": [1, 2, 3],
  "device_ids": [1, 2],
  "schedule": {
    "type": "manual"
  },
  "notification_config": {
    "email": true,
    "webhook": "https://example.com/webhook"
  }
}
```

### 启动测试任务
```http
POST /api/test-tasks/{task_id}/start
```

### 停止测试任务
```http
POST /api/test-tasks/{task_id}/stop
```

### 重新执行测试任务
```http
POST /api/test-tasks/{task_id}/rerun
```

## 报告管理 API

### 获取报告列表
```http
GET /api/reports?page=1&size=20&task_id=1
```

### 获取报告详情
```http
GET /api/reports/{report_id}
```

**响应:**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": 1,
    "task_id": 1,
    "task_name": "回归测试任务",
    "status": "completed",
    "summary": {
      "total_cases": 100,
      "passed_cases": 85,
      "failed_cases": 10,
      "skipped_cases": 5,
      "pass_rate": 85.0,
      "execution_time": 3600
    },
    "devices": [
      {
        "device_id": 1,
        "device_name": "iPhone 12",
        "passed": 42,
        "failed": 5,
        "skipped": 3
      }
    ],
    "test_results": [
      {
        "case_id": 1,
        "case_title": "用户登录测试",
        "status": "passed",
        "execution_time": 15,
        "error_message": null,
        "screenshots": [
          "/uploads/screenshots/login_1.png"
        ]
      }
    ],
    "charts": {
      "pass_rate_chart": {
        "labels": ["登录", "注册", "主页"],
        "data": [90, 85, 80]
      },
      "execution_time_chart": {
        "labels": ["设备1", "设备2"],
        "data": [1800, 2400]
      }
    },
    "created_at": "2023-12-01T12:00:00Z",
    "updated_at": "2023-12-01T12:30:00Z"
  }
}
```

### 生成报告
```http
POST /api/reports/generate
Content-Type: application/json

{
  "task_id": 1,
  "format": "pdf",
  "template": "standard",
  "include_charts": true,
  "include_screenshots": true
}
```

### 下载报告
```http
GET /api/reports/{report_id}/download?format=pdf
```

### 分享报告
```http
POST /api/reports/{report_id}/share
Content-Type: application/json

{
  "share_type": "link",
  "expires_in": 86400,
  "password": "optional_password"
}
```

## 用户管理 API

### 获取用户列表
```http
GET /api/users?page=1&size=20&role= tester
```

### 获取用户详情
```http
GET /api/users/{user_id}
```

### 创建用户
```http
POST /api/users
Content-Type: application/json

{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "password123",
  "role": "tester",
  "permissions": ["device:read", "testcase:read", "testcase:execute"]
}
```

### 更新用户
```http
PUT /api/users/{user_id}
Content-Type: application/json

{
  "email": "updated@example.com",
  "role": "admin"
}
```

### 删除用户
```http
DELETE /api/users/{user_id}
```

## 系统设置 API

### 获取系统设置
```http
GET /api/system/settings
```

**响应:**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "basic": {
      "system_name": "移动测试平台",
      "version": "1.0.0",
      "timezone": "Asia/Shanghai",
      "language": "zh-CN"
    },
    "security": {
      "password_min_length": 8,
      "session_timeout": 3600,
      "max_login_attempts": 5
    },
    "email": {
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "sender_email": "noreply@example.com"
    },
    "storage": {
      "upload_path": "/uploads",
      "max_file_size": 10485760,
      "allowed_extensions": [".apk", ".ipa", ".zip"]
    }
  }
}
```

### 更新系统设置
```http
PUT /api/system/settings
Content-Type: application/json

{
  "basic": {
    "system_name": "更新后的系统名称"
  },
  "security": {
    "password_min_length": 10
  }
}
```

### 获取系统信息
```http
GET /api/system/info
```

**响应:**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "version": "1.0.0",
    "build_time": "2023-12-01T08:00:00Z",
    "python_version": "3.9.0",
    "database_version": "MySQL 8.0",
    "uptime": 86400,
    "memory_usage": {
      "total": 8589934592,
      "used": 4294967296,
      "percentage": 50.0
    },
    "cpu_usage": 25.5,
    "disk_usage": {
      "total": 107374182400,
      "used": 53687091200,
      "percentage": 50.0
    }
  }
}
```

## WebSocket API

### 连接 WebSocket
```
ws://localhost:8000/ws
```

### 认证
连接时需要在查询参数中提供 token：
```
ws://localhost:8000/ws?token=your_jwt_token
```

### 消息格式

**设备状态更新:**
```json
{
  "type": "device_status",
  "data": {
    "device_id": 1,
    "status": "online",
    "timestamp": "2023-12-01T10:30:00Z"
  }
}
```

**任务进度更新:**
```json
{
  "type": "task_progress",
  "data": {
    "task_id": 1,
    "progress": 75.5,
    "current_case": "用户登录测试",
    "timestamp": "2023-12-01T10:30:00Z"
  }
}
```

**系统通知:**
```json
{
  "type": "notification",
  "data": {
    "title": "测试完成",
    "message": "回归测试任务已完成",
    "level": "info",
    "timestamp": "2023-12-01T10:30:00Z"
  }
}
```

## 错误代码

| 错误代码 | 说明 |
|---------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 422 | 数据验证失败 |
| 429 | 请求频率限制 |
| 500 | 服务器内部错误 |
| 503 | 服务不可用 |

## 速率限制

- 普通用户: 100 请求/分钟
- 高级用户: 500 请求/分钟
- 管理员: 1000 请求/分钟

## SDK 和示例代码

### Python SDK
```python
from mob_test_platform import MobTestClient

client = MobTestClient(
    base_url="http://localhost:8000/api",
    token="your_jwt_token"
)

# 获取设备列表
devices = client.devices.list()

# 执行测试用例
result = client.test_cases.execute(1, device_ids=[1, 2])
```

### JavaScript SDK
```javascript
import { MobTestClient } from 'mob-test-platform-js';

const client = new MobTestClient({
  baseURL: 'http://localhost:8000/api',
  token: 'your_jwt_token'
});

// 获取设备列表
const devices = await client.devices.list();

// 执行测试用例
const result = await client.testCases.execute(1, [1, 2]);
```

### cURL 示例
```bash
# 登录获取 token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password123"}'

# 获取设备列表
curl -X GET http://localhost:8000/api/devices \
  -H "Authorization: Bearer your_jwt_token"
```

## 更新日志

### v1.0.0 (2023-12-01)
- 初始版本发布
- 支持设备管理、测试用例管理、任务执行、报告生成
- 提供 RESTful API 和 WebSocket 实时通信
- 支持多用户权限管理

### v1.1.0 (计划中)
- 增加性能测试 API
- 支持测试用例版本控制
- 增强报告定制功能
- 添加更多设备操作 API

## 支持

如有问题或建议，请联系：
- 邮箱: api-support@mobtestplatform.com
- 文档: https://docs.mobtestplatform.com
- GitHub: https://github.com/your-org/mob-test-platform/issues