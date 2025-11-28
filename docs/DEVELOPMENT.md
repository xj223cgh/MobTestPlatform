# 开发指南

## 项目架构

### 技术栈
- **后端**: Python 3.8+ + Flask + SQLAlchemy + Redis
- **前端**: Vue 3 + Vite + Element Plus + Pinia
- **数据库**: MySQL 5.7+ / PostgreSQL 10+
- **缓存**: Redis 6.0+
- **任务队列**: Celery + Redis
- **WebSocket**: Flask-SocketIO

### 系统架构图
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端 (Vue3)   │────│  后端 (Flask)   │────│  数据库 (MySQL) │
│                 │    │                 │    │                 │
│ - 用户界面      │    │ - RESTful API   │    │ - 业务数据      │
│ - 状态管理      │    │ - WebSocket     │    │ - 用户数据      │
│ - 路由管理      │    │ - 任务队列      │    │ - 测试数据      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                       ┌─────────────────┐
                       │   缓存 (Redis)  │
                       │                 │
                       │ - 会话存储      │
                       │ - 任务队列      │
                       │ - 实时数据      │
                       └─────────────────┘
```

## 开发环境搭建

### 1. 克隆项目
```bash
git clone https://github.com/your-org/mob-test-platform.git
cd mob-test-platform
```

### 2. 后端开发环境

#### 创建虚拟环境
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

#### 安装依赖
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖
```

#### 配置开发环境
创建 `.env.development` 文件：
```env
# 开发环境配置
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=mysql://root:password@localhost:3306/mob_test_platform_dev
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=dev-secret-key
LOG_LEVEL=DEBUG
```

#### 初始化数据库
```bash
# 运行开发数据库初始化
python init_backend.py --env=development

# 或者使用 Flask-Migrate
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

#### 启动开发服务器
```bash
# 使用 Flask 开发服务器
flask run --host=0.0.0.0 --port=8000 --reload

# 或使用提供的启动脚本
python run.py
```

### 3. 前端开发环境

#### 安装依赖
```bash
cd frontend
npm install
```

#### 配置开发环境
创建 `.env.development` 文件：
```env
# 开发环境 API 地址
VITE_API_BASE_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/ws

# 开发环境配置
VITE_APP_TITLE=移动测试平台 (开发)
VITE_APP_VERSION=1.0.0-dev
VITE_MOCK_API=false
```

#### 启动开发服务器
```bash
npm run dev
```

## 代码规范

### Python 代码规范

#### 遵循 PEP 8
```python
# 好的示例
class DeviceService:
    """设备服务类"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    def get_device_by_id(self, device_id: int) -> Optional[Device]:
        """根据ID获取设备
        
        Args:
            device_id: 设备ID
            
        Returns:
            Device对象或None
        """
        return self.db.query(Device).filter(Device.id == device_id).first()
    
    def create_device(self, device_data: dict) -> Device:
        """创建新设备
        
        Args:
            device_data: 设备数据字典
            
        Returns:
            创建的Device对象
            
        Raises:
            ValidationError: 数据验证失败
        """
        # 验证数据
        self._validate_device_data(device_data)
        
        # 创建设备
        device = Device(**device_data)
        self.db.add(device)
        self.db.commit()
        
        return device
```

#### 使用类型注解
```python
from typing import List, Optional, Dict, Any
from datetime import datetime

def process_test_results(
    results: List[Dict[str, Any]], 
    device_id: int,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """处理测试结果"""
    pass
```

#### 异常处理
```python
try:
    device = device_service.get_device_by_id(device_id)
    if not device:
        raise DeviceNotFoundError(f"Device {device_id} not found")
    
    result = device_service.connect_device(device)
    return {"success": True, "data": result}
    
except DeviceNotFoundError as e:
    logger.error(f"Device not found: {e}")
    return {"success": False, "error": str(e)}
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return {"success": False, "error": "Internal server error"}
```

### JavaScript 代码规范

#### 使用 ESLint + Prettier
```javascript
// 好的示例
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getDevices, connectDevice } from '@/api/device'

export default {
  name: 'DeviceList',
  setup() {
    const devices = ref([])
    const loading = ref(false)
    
    const onlineDevices = computed(() => 
      devices.value.filter(device => device.status === 'online')
    )
    
    const fetchDevices = async () => {
      try {
        loading.value = true
        const response = await getDevices()
        devices.value = response.data.items
      } catch (error) {
        ElMessage.error('获取设备列表失败')
        console.error('Failed to fetch devices:', error)
      } finally {
        loading.value = false
      }
    }
    
    const handleConnect = async (device) => {
      try {
        await connectDevice(device.id)
        ElMessage.success('设备连接成功')
        await fetchDevices()
      } catch (error) {
        ElMessage.error('设备连接失败')
      }
    }
    
    onMounted(() => {
      fetchDevices()
    })
    
    return {
      devices,
      loading,
      onlineDevices,
      handleConnect
    }
  }
}
```

#### 组件命名规范
```javascript
// 页面组件 - 使用 PascalCase
DeviceManagement.vue
TestCaseManagement.vue

// 通用组件 - 使用 PascalCase，前缀表示类型
BaseButton.vue
BaseModal.vue
DeviceCard.vue
TestCaseForm.vue
```

## 数据库设计

### 表结构设计原则
1. 使用统一的命名规范 (snake_case)
2. 每个表都有 id、created_at、updated_at 字段
3. 使用外键约束保证数据完整性
4. 为常用查询字段添加索引

### 模型定义示例
```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class DeviceStatus(enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"

class Device(Base):
    __tablename__ = 'devices'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    device_id = Column(String(100), unique=True, nullable=False)
    device_type = Column(String(20), nullable=False)  # android, ios
    status = Column(Enum(DeviceStatus), default=DeviceStatus.OFFLINE)
    ip_address = Column(String(45))
    os_version = Column(String(50))
    brand = Column(String(50))
    model = Column(String(100))
    screen_resolution = Column(String(20))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    test_results = relationship("TestResult", back_populates="device")
    
    def __repr__(self):
        return f"<Device(id={self.id}, name='{self.name}', status='{self.status.value}')>"
```

### 数据库迁移
```bash
# 创建迁移文件
flask db migrate -m "Add device table"

# 应用迁移
flask db upgrade

# 回滚迁移
flask db downgrade
```

## API 开发

### RESTful API 设计原则

#### URL 设计
```
GET    /api/devices           # 获取设备列表
POST   /api/devices           # 创建设备
GET    /api/devices/{id}      # 获取设备详情
PUT    /api/devices/{id}      # 更新设备
DELETE /api/devices/{id}      # 删除设备

POST   /api/devices/{id}/connect     # 连接设备
POST   /api/devices/{id}/disconnect  # 断开设备
GET    /api/devices/{id}/screenshot  # 获取截图
```

#### 响应格式
```python
from flask import jsonify

def success_response(data=None, message="操作成功"):
    """成功响应格式"""
    response = {
        "code": 200,
        "message": message
    }
    if data is not None:
        response["data"] = data
    return jsonify(response)

def error_response(code, message, error=None):
    """错误响应格式"""
    response = {
        "code": code,
        "message": message
    }
    if error:
        response["error"] = error
    return jsonify(response), code
```

#### 路由定义
```python
from flask import Blueprint, request, jsonify
from app.services.device_service import DeviceService
from app.utils.decorators import require_auth, validate_json

device_bp = Blueprint('devices', __name__, url_prefix='/api/devices')
device_service = DeviceService()

@device_bp.route('', methods=['GET'])
@require_auth
def get_devices():
    """获取设备列表"""
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 20, type=int)
    status = request.args.get('status')
    
    devices, total = device_service.get_devices(page, size, status)
    
    return success_response({
        'items': devices,
        'pagination': {
            'page': page,
            'size': size,
            'total': total,
            'pages': (total + size - 1) // size
        }
    })

@device_bp.route('', methods=['POST'])
@require_auth
@validate_json
def create_device():
    """创建设备"""
    data = request.get_json()
    device = device_service.create_device(data)
    return success_response(device.to_dict(), "设备创建成功")

@device_bp.route('/<int:device_id>/connect', methods=['POST'])
@require_auth
def connect_device(device_id):
    """连接设备"""
    try:
        result = device_service.connect_device(device_id)
        return success_response(result, "设备连接成功")
    except DeviceNotFoundError:
        return error_response(404, "设备不存在")
    except DeviceConnectionError as e:
        return error_response(400, str(e))
```

### 服务层设计
```python
from typing import List, Tuple, Optional
from app.models.device import Device, DeviceStatus
from app.utils.exceptions import DeviceNotFoundError, DeviceConnectionError

class DeviceService:
    def __init__(self):
        self.db = db.session
    
    def get_devices(
        self, 
        page: int = 1, 
        size: int = 20, 
        status: Optional[str] = None
    ) -> Tuple[List[Device], int]:
        """获取设备列表"""
        query = self.db.query(Device)
        
        if status:
            query = query.filter(Device.status == status)
        
        total = query.count()
        devices = query.offset((page - 1) * size).limit(size).all()
        
        return devices, total
    
    def get_device_by_id(self, device_id: int) -> Device:
        """根据ID获取设备"""
        device = self.db.query(Device).filter(Device.id == device_id).first()
        if not device:
            raise DeviceNotFoundError(f"Device {device_id} not found")
        return device
    
    def connect_device(self, device_id: int) -> dict:
        """连接设备"""
        device = self.get_device_by_id(device_id)
        
        try:
            # 实际连接逻辑
            result = self._perform_connection(device)
            
            # 更新设备状态
            device.status = DeviceStatus.ONLINE
            device.last_seen = datetime.utcnow()
            self.db.commit()
            
            return result
        except Exception as e:
            device.status = DeviceStatus.ERROR
            self.db.commit()
            raise DeviceConnectionError(f"Failed to connect device: {e}")
```

## 前端开发

### 组件设计原则
1. 单一职责原则
2. 可复用性
3. Props 验证
4. 事件处理规范

### 组件示例
```vue
<template>
  <div class="device-card">
    <el-card 
      :class="['device-status-' + device.status]" 
      shadow="hover"
    >
      <template #header>
        <div class="card-header">
          <span class="device-name">{{ device.name }}</span>
          <el-tag :type="statusTagType" size="small">
            {{ statusText }}
          </el-tag>
        </div>
      </template>
      
      <div class="device-info">
        <div class="info-item">
          <span class="label">设备类型:</span>
          <span class="value">{{ device.device_type }}</span>
        </div>
        <div class="info-item">
          <span class="label">IP地址:</span>
          <span class="value">{{ device.ip_address }}</span>
        </div>
        <div class="info-item">
          <span class="label">系统版本:</span>
          <span class="value">{{ device.os_version }}</span>
        </div>
      </div>
      
      <div class="device-actions">
        <el-button 
          v-if="device.status === 'offline'" 
          type="primary" 
          size="small"
          @click="handleConnect"
          :loading="connecting"
        >
          连接
        </el-button>
        <el-button 
          v-else-if="device.status === 'online'" 
          type="danger" 
          size="small"
          @click="handleDisconnect"
        >
          断开
        </el-button>
        <el-button 
          type="info" 
          size="small"
          @click="handleViewDetails"
        >
          详情
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { connectDevice, disconnectDevice } from '@/api/device'

const props = defineProps({
  device: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['refresh', 'view-details'])

const connecting = ref(false)

const statusTagType = computed(() => {
  const statusMap = {
    online: 'success',
    offline: 'info',
    error: 'danger'
  }
  return statusMap[props.device.status] || 'info'
})

const statusText = computed(() => {
  const textMap = {
    online: '在线',
    offline: '离线',
    error: '错误'
  }
  return textMap[props.device.status] || '未知'
})

const handleConnect = async () => {
  try {
    connecting.value = true
    await connectDevice(props.device.id)
    ElMessage.success('设备连接成功')
    emit('refresh')
  } catch (error) {
    ElMessage.error('设备连接失败')
  } finally {
    connecting.value = false
  }
}

const handleDisconnect = async () => {
  try {
    await disconnectDevice(props.device.id)
    ElMessage.success('设备断开成功')
    emit('refresh')
  } catch (error) {
    ElMessage.error('设备断开失败')
  }
}

const handleViewDetails = () => {
  emit('view-details', props.device)
}
</script>

<style scoped>
.device-card {
  margin-bottom: 16px;
}

.device-status-online {
  border-left: 4px solid #67c23a;
}

.device-status-offline {
  border-left: 4px solid #909399;
}

.device-status-error {
  border-left: 4px solid #f56c6c;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.device-name {
  font-weight: bold;
  font-size: 16px;
}

.device-info {
  margin-bottom: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.label {
  color: #909399;
  font-size: 14px;
}

.value {
  color: #303133;
  font-size: 14px;
}

.device-actions {
  display: flex;
  gap: 8px;
}
</style>
```

### 状态管理
```javascript
// stores/device.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getDevices, connectDevice, disconnectDevice } from '@/api/device'

export const useDeviceStore = defineStore('device', () => {
  const devices = ref([])
  const loading = ref(false)
  const selectedDevice = ref(null)
  
  const onlineDevices = computed(() => 
    devices.value.filter(device => device.status === 'online')
  )
  
  const offlineDevices = computed(() => 
    devices.value.filter(device => device.status === 'offline')
  )
  
  const deviceCount = computed(() => ({
    total: devices.value.length,
    online: onlineDevices.value.length,
    offline: offlineDevices.value.length
  }))
  
  const fetchDevices = async () => {
    try {
      loading.value = true
      const response = await getDevices()
      devices.value = response.data.items
    } catch (error) {
      console.error('Failed to fetch devices:', error)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  const connectToDevice = async (deviceId) => {
    try {
      await connectDevice(deviceId)
      await fetchDevices() // 刷新列表
    } catch (error) {
      console.error('Failed to connect device:', error)
      throw error
    }
  }
  
  const disconnectFromDevice = async (deviceId) => {
    try {
      await disconnectDevice(deviceId)
      await fetchDevices() // 刷新列表
    } catch (error) {
      console.error('Failed to disconnect device:', error)
      throw error
    }
  }
  
  const selectDevice = (device) => {
    selectedDevice.value = device
  }
  
  return {
    devices,
    loading,
    selectedDevice,
    onlineDevices,
    offlineDevices,
    deviceCount,
    fetchDevices,
    connectToDevice,
    disconnectFromDevice,
    selectDevice
  }
})
```

## 测试

### 后端测试

#### 单元测试
```python
# tests/test_device_service.py
import pytest
from app.services.device_service import DeviceService
from app.models.device import Device, DeviceStatus
from app.utils.exceptions import DeviceNotFoundError

class TestDeviceService:
    def setup_method(self):
        self.service = DeviceService()
        
    def test_get_device_by_id_success(self, db_session, sample_device):
        """测试根据ID获取设备 - 成功"""
        device = self.service.get_device_by_id(sample_device.id)
        assert device.id == sample_device.id
        assert device.name == sample_device.name
    
    def test_get_device_by_id_not_found(self, db_session):
        """测试根据ID获取设备 - 未找到"""
        with pytest.raises(DeviceNotFoundError):
            self.service.get_device_by_id(999)
    
    @pytest.mark.asyncio
    async def test_connect_device_success(self, db_session, sample_device):
        """测试连接设备 - 成功"""
        result = await self.service.connect_device(sample_device.id)
        assert result['status'] == 'connected'
        
        # 验证设备状态更新
        updated_device = self.service.get_device_by_id(sample_device.id)
        assert updated_device.status == DeviceStatus.ONLINE
```

#### API 测试
```python
# tests/test_device_api.py
import pytest
from app import create_app

class TestDeviceAPI:
    def setup_method(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def teardown_method(self):
        self.app_context.pop()
    
    def test_get_devices_success(self, auth_headers):
        """测试获取设备列表 - 成功"""
        response = self.client.get('/api/devices', headers=auth_headers)
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['code'] == 200
        assert 'items' in data['data']
        assert 'pagination' in data['data']
    
    def test_create_device_success(self, auth_headers):
        """测试创建设备 - 成功"""
        device_data = {
            'name': 'Test Device',
            'device_id': 'TEST-001',
            'device_type': 'android',
            'ip_address': '192.168.1.100'
        }
        
        response = self.client.post(
            '/api/devices',
            json=device_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['code'] == 200
        assert data['data']['name'] == device_data['name']
```

### 前端测试

#### 组件测试
```javascript
// tests/components/DeviceCard.test.js
import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
import DeviceCard from '@/components/DeviceCard.vue'

describe('DeviceCard.vue', () => {
  const mockDevice = {
    id: 1,
    name: 'Test Device',
    status: 'offline',
    device_type: 'android',
    ip_address: '192.168.1.100',
    os_version: '10'
  }
  
  it('renders device information correctly', () => {
    const wrapper = mount(DeviceCard, {
      props: { device: mockDevice }
    })
    
    expect(wrapper.find('.device-name').text()).toBe('Test Device')
    expect(wrapper.text()).toContain('android')
    expect(wrapper.text()).toContain('192.168.1.100')
  })
  
  it('shows connect button when device is offline', () => {
    const wrapper = mount(DeviceCard, {
      props: { device: mockDevice }
    })
    
    const connectButton = wrapper.find('button')
    expect(connectButton.text()).toBe('连接')
  })
  
  it('emits connect event when connect button is clicked', async () => {
    const wrapper = mount(DeviceCard, {
      props: { device: mockDevice }
    })
    
    await wrapper.find('button').trigger('click')
    
    // 验证事件触发
    expect(wrapper.emitted('connect')).toBeTruthy()
    expect(wrapper.emitted('connect')[0]).toEqual([mockDevice])
  })
})
```

## 部署

### Docker 部署
```dockerfile
# backend/Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "run:app"]
```

```dockerfile
# frontend/Dockerfile
FROM node:16-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### CI/CD 配置
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        cd backend
        pytest --cov=app tests/
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1

  test-frontend:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '16'
    
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Run tests
      run: |
        cd frontend
        npm run test:unit
    
    - name: Build
      run: |
        cd frontend
        npm run build
```

## 贡献指南

### 提交规范
```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
test: 测试相关
chore: 构建过程或辅助工具的变动
```

### Pull Request 流程
1. Fork 项目
2. 创建功能分支
3. 编写代码和测试
4. 提交代码 (遵循提交规范)
5. 创建 Pull Request
6. 代码审查
7. 合并代码

### 代码审查清单
- [ ] 代码符合项目规范
- [ ] 包含必要的测试
- [ ] 文档已更新
- [ ] 没有引入安全漏洞
- [ ] 性能影响可接受

## 常见问题

### 开发环境问题
1. **端口冲突**: 修改配置文件中的端口设置
2. **数据库连接失败**: 检查数据库服务和连接配置
3. **依赖安装失败**: 清理缓存或使用镜像源

### 调试技巧
1. 使用断点调试
2. 查看日志文件
3. 使用浏览器开发者工具
4. 使用网络抓包工具

### 性能优化
1. 数据库查询优化
2. 前端代码分割
3. 缓存策略
4. 异步处理

## 资源链接

- [Vue.js 官方文档](https://vuejs.org/)
- [Flask 官方文档](https://flask.palletsprojects.com/)
- [Element Plus 文档](https://element-plus.org/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [Docker 文档](https://docs.docker.com/)