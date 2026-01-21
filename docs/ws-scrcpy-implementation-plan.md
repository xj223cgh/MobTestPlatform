# ws-scrcpy 二次开发方案规划

## 一、方案概述

### 1.1 目标
在设备详情页面中内嵌显示设备投屏，支持在浏览器中直接查看和控制Android设备屏幕。

### 1.2 技术选型
- **后端框架**：ws-scrcpy（基于 scrcpy 的 Web 客户端）
- **前端技术**：WebSocket + Canvas/Video 元素
- **视频编码**：H.264
- **传输协议**：WebSocket

### 1.3 核心功能
1. 设备屏幕实时镜像显示
2. 鼠标/触摸事件映射
3. 键盘输入处理
4. 多设备并发支持
5. 进程生命周期管理

---

## 二、技术架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────┐
│                      前端（Vue 3）                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │         设备详情页面 (DeviceDetail.vue)          │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │     投屏组件 (MirrorComponent.vue)         │  │  │
│  │  │  ┌──────────────────────────────────────┐  │  │  │
│  │  │  │  WebSocket 客户端                    │  │  │  │
│  │  │  │  - 接收视频流                        │  │  │  │
│  │  │  │  - 发送控制事件                      │  │  │  │
│  │  │  └──────────────────────────────────────┘  │  │  │
│  │  │  ┌──────────────────────────────────────┐  │  │  │
│  │  │  │  视频渲染器                          │  │  │  │
│  │  │  │  - H.264 解码                        │  │  │  │
│  │  │  │  - Canvas/Video 渲染                 │  │  │  │
│  │  │  └──────────────────────────────────────┘  │  │  │
│  │  │  ┌──────────────────────────────────────┐  │  │  │
│  │  │  │  事件处理器                          │  │  │  │
│  │  │  │  - 鼠标/触摸事件映射                 │  │  │  │
│  │  │  │  - 键盘输入处理                      │  │  │  │
│  │  │  └──────────────────────────────────────┘  │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↕ WebSocket
┌─────────────────────────────────────────────────────────┐
│                    后端（Flask + ws-scrcpy）             │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Flask API 路由                           │  │
│  │  - POST /devices/{id}/mirror/start              │  │
│  │  - POST /devices/{id}/mirror/stop               │  │
│  │  - GET  /devices/{id}/mirror/status            │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │         进程管理器                              │  │
│  │  - 启动/停止 ws-scrcpy 进程                     │  │
│  │  - 端口分配和管理                              │  │
│  │  - 进程生命周期监控                            │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │         ws-scrcpy 服务实例                       │  │
│  │  (每个设备一个独立实例)                          │  │
│  │  - scrcpy 视频采集                              │  │
│  │  - H.264 编码                                  │  │
│  │  - WebSocket 服务                              │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↕ ADB
┌─────────────────────────────────────────────────────────┐
│                    Android 设备                          │
│  - 屏幕内容采集                                           │
│  - 控制指令接收                                           │
└─────────────────────────────────────────────────────────┘
```

### 2.2 数据流

#### 2.2.1 视频流（设备 → 浏览器）
```
Android 设备屏幕
    ↓ (scrcpy 采集)
H.264 编码视频流
    ↓ (WebSocket)
Flask 后端
    ↓ (WebSocket)
前端 WebSocket 客户端
    ↓ (H.264 解码)
Canvas/Video 元素
    ↓ (渲染)
用户看到设备屏幕
```

#### 2.2.2 控制流（浏览器 → 设备）
```
用户鼠标/触摸操作
    ↓ (事件捕获)
前端事件处理器
    ↓ (转换为控制指令)
WebSocket 客户端
    ↓ (WebSocket)
Flask 后端
    ↓ (ADB)
Android 设备
    ↓ (执行操作)
设备响应
```

---

## 三、后端实现方案

### 3.1 项目结构

```
backend/
├── app/
│   ├── routes/
│   │   └── devices.py              # 设备相关 API
│   ├── services/
│   │   └── mirror_service.py       # 投屏服务
│   └── utils/
│       └── port_manager.py         # 端口管理器
├── ws_scrcpy/                       # ws-scrcpy 集成目录
│   ├── server/                      # ws-scrcpy 服务端
│   │   ├── __init__.py
│   │   ├── scrcpy_server.py         # scrcpy 服务
│   │   └── websocket_handler.py    # WebSocket 处理
│   └── client/                      # 前端客户端代码
│       └── ws-scrcpy.js
└── requirements.txt
```

### 3.2 核心模块设计

#### 3.2.1 端口管理器 (port_manager.py)

```python
class PortManager:
    """端口管理器，负责分配和回收 WebSocket 端口"""

    def __init__(self, start_port=8000, end_port=9000):
        self.start_port = start_port
        self.end_port = end_port
        self.used_ports = set()
        self.port_device_map = {}  # port -> device_id

    def allocate_port(self, device_id):
        """为设备分配一个可用端口"""
        for port in range(self.start_port, self.end_port):
            if port not in self.used_ports:
                self.used_ports.add(port)
                self.port_device_map[port] = device_id
                return port
        raise Exception("No available ports")

    def release_port(self, port):
        """释放端口"""
        if port in self.used_ports:
            self.used_ports.remove(port)
            if port in self.port_device_map:
                del self.port_device_map[port]

    def get_device_id(self, port):
        """根据端口获取设备ID"""
        return self.port_device_map.get(port)
```

#### 3.2.2 投屏服务 (mirror_service.py)

```python
class MirrorService:
    """投屏服务，管理 ws-scrcpy 进程"""

    def __init__(self):
        self.port_manager = PortManager()
        self.processes = {}  # device_id -> process
        self.status = {}     # device_id -> status

    def start_mirror(self, device_id):
        """启动设备投屏"""
        if device_id in self.processes:
            raise Exception("Mirror already started")

        # 分配端口
        port = self.port_manager.allocate_port(device_id)

        # 启动 ws-scrcpy 进程
        process = subprocess.Popen([
            'python', 'ws_scrcpy_server.py',
            '--device', device_id,
            '--port', str(port)
        ])

        self.processes[device_id] = {
            'process': process,
            'port': port,
            'start_time': time.time()
        }
        self.status[device_id] = 'starting'

        return {
            'device_id': device_id,
            'port': port,
            'ws_url': f'ws://localhost:{port}'
        }

    def stop_mirror(self, device_id):
        """停止设备投屏"""
        if device_id not in self.processes:
            raise Exception("Mirror not found")

        process_info = self.processes[device_id]
        process_info['process'].terminate()

        # 释放端口
        self.port_manager.release_port(process_info['port'])

        # 清理
        del self.processes[device_id]
        del self.status[device_id]

    def get_mirror_status(self, device_id):
        """获取投屏状态"""
        if device_id not in self.processes:
            return {'status': 'stopped'}

        process_info = self.processes[device_id]
        return {
            'status': self.status.get(device_id, 'unknown'),
            'port': process_info['port'],
            'ws_url': f'ws://localhost:{process_info["port"]}',
            'start_time': process_info['start_time']
        }
```

#### 3.2.3 API 路由 (devices.py)

```python
@bp.route('/<int:device_id>/mirror/start', methods=['POST'])
@login_required
def start_mirror(device_id):
    """启动设备投屏"""
    try:
        result = mirror_service.start_mirror(device_id)
        return success_response(result, "投屏启动成功")
    except Exception as e:
        return error_response(500, str(e))

@bp.route('/<int:device_id>/mirror/stop', methods=['POST'])
@login_required
def stop_mirror(device_id):
    """停止设备投屏"""
    try:
        mirror_service.stop_mirror(device_id)
        return success_response(message="投屏停止成功")
    except Exception as e:
        return error_response(500, str(e))

@bp.route('/<int:device_id>/mirror/status', methods=['GET'])
@login_required
def get_mirror_status(device_id):
    """获取投屏状态"""
    try:
        status = mirror_service.get_mirror_status(device_id)
        return success_response(status)
    except Exception as e:
        return error_response(500, str(e))
```

### 3.3 ws-scrcpy 集成

#### 3.3.1 依赖安装
```bash
# 安装 ws-scrcpy 相关依赖
pip install scrcpy-client
pip install websockets
pip install opencv-python
```

#### 3.3.2 ws-scrcpy 服务端 (scrcpy_server.py)

```python
import asyncio
import websockets
import scrcpy
from scrcpy import Client

async def handle_client(websocket, path, device_id):
    """处理 WebSocket 客户端连接"""

    # 连接到 Android 设备
    client = Client(device=device_id)
    client.start(threaded=True)

    # 发送视频流
    async def send_video():
        for frame in client.stream:
            # 将 H.264 帧发送到 WebSocket
            await websocket.send(frame.tobytes())

    # 接收控制事件
    async def receive_control():
        async for message in websocket:
            # 处理控制事件（点击、滑动等）
            handle_control_event(client, message)

    # 并发运行
    await asyncio.gather(send_video(), receive_control())

    client.stop()

def handle_control_event(client, event):
    """处理控制事件"""
    # 解析事件类型和参数
    # 调用 scrcpy 客户端方法执行操作
    pass

async def start_server(port, device_id):
    """启动 WebSocket 服务器"""
    async with websockets.serve(
        lambda ws, path: handle_client(ws, path, device_id),
        "localhost",
        port
    ):
        await asyncio.Future()  # 永久运行
```

---

## 四、前端实现方案

### 4.1 项目结构

```
frontend/src/
├── views/
│   └── device/
│       ├── DeviceDetail.vue       # 设备详情页
│       └── components/
│           └── MirrorComponent.vue # 投屏组件
├── components/
│   └── mirror/
│       ├── WebSocketClient.js     # WebSocket 客户端
│       ├── VideoRenderer.js       # 视频渲染器
│       └── EventHandler.js        # 事件处理器
└── utils/
    └── h264Decoder.js             # H.264 解码器
```

### 4.2 核心组件设计

#### 4.2.1 投屏组件 (MirrorComponent.vue)

```vue
<template>
  <div class="mirror-component">
    <div class="mirror-toolbar">
      <el-button @click="startMirror" :disabled="isRunning">
        启动投屏
      </el-button>
      <el-button @click="stopMirror" :disabled="!isRunning">
        停止投屏
      </el-button>
      <el-select v-model="quality" @change="changeQuality">
        <el-option label="高清" value="high"></el-option>
        <el-option label="标清" value="medium"></el-option>
        <el-option label="流畅" value="low"></el-option>
      </el-select>
    </div>

    <div class="mirror-container" ref="container">
      <canvas ref="canvas" v-show="isRunning"></canvas>
      <div v-if="!isRunning" class="placeholder">
        <el-empty description="点击启动投屏"></el-empty>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { WebSocketClient } from '@/components/mirror/WebSocketClient'
import { VideoRenderer } from '@/components/mirror/VideoRenderer'
import { EventHandler } from '@/components/mirror/EventHandler'

const props = defineProps({
  deviceId: String
})

const container = ref(null)
const canvas = ref(null)
const isRunning = ref(false)
const quality = ref('medium')

let wsClient = null
let renderer = null
let eventHandler = null

const startMirror = async () => {
  try {
    // 调用后端 API 启动投屏
    const response = await deviceApi.startMirror(props.deviceId)
    const { ws_url } = response.data

    // 初始化 WebSocket 客户端
    wsClient = new WebSocketClient(ws_url)
    await wsClient.connect()

    // 初始化视频渲染器
    renderer = new VideoRenderer(canvas.value)
    renderer.start()

    // 初始化事件处理器
    eventHandler = new EventHandler(canvas.value, wsClient)

    // 接收视频流
    wsClient.onMessage((data) => {
      renderer.decodeAndRender(data)
    })

    isRunning.value = true
  } catch (error) {
    console.error('启动投屏失败:', error)
  }
}

const stopMirror = async () => {
  try {
    // 调用后端 API 停止投屏
    await deviceApi.stopMirror(props.deviceId)

    // 断开 WebSocket
    if (wsClient) {
      wsClient.disconnect()
    }

    // 停止渲染器
    if (renderer) {
      renderer.stop()
    }

    isRunning.value = false
  } catch (error) {
    console.error('停止投屏失败:', error)
  }
}

const changeQuality = (value) => {
  // 切换视频质量
  // 调用后端 API 更新 scrcpy 参数
}

onUnmounted(() => {
  if (isRunning.value) {
    stopMirror()
  }
})
</script>
```

#### 4.2.2 WebSocket 客户端 (WebSocketClient.js)

```javascript
export class WebSocketClient {
  constructor(url) {
    this.url = url
    this.ws = null
    this.messageHandlers = []
  }

  async connect() {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.url)

      this.ws.onopen = () => {
        console.log('WebSocket connected')
        resolve()
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        reject(error)
      }

      this.ws.onmessage = (event) => {
        this.messageHandlers.forEach(handler => handler(event.data))
      }

      this.ws.onclose = () => {
        console.log('WebSocket closed')
      }
    })
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
    }
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(data)
    }
  }

  onMessage(handler) {
    this.messageHandlers.push(handler)
  }
}
```

#### 4.2.3 视频渲染器 (VideoRenderer.js)

```javascript
import { H264Decoder } from '@/utils/h264Decoder'

export class VideoRenderer {
  constructor(canvas) {
    this.canvas = canvas
    this.ctx = canvas.getContext('2d')
    this.decoder = new H264Decoder()
    this.isRunning = false
  }

  start() {
    this.isRunning = true
    this.renderLoop()
  }

  stop() {
    this.isRunning = false
  }

  decodeAndRender(h264Data) {
    if (!this.isRunning) return

    // 解码 H.264 数据
    const frame = this.decoder.decode(h264Data)

    if (frame) {
      // 渲染到 Canvas
      this.ctx.drawImage(frame, 0, 0)
    }
  }

  renderLoop() {
    if (!this.isRunning) return

    requestAnimationFrame(() => this.renderLoop())
  }
}
```

#### 4.2.4 事件处理器 (EventHandler.js)

```javascript
export class EventHandler {
  constructor(canvas, wsClient) {
    this.canvas = canvas
    this.wsClient = wsClient
    this.setupEventListeners()
  }

  setupEventListeners() {
    // 鼠标事件
    this.canvas.addEventListener('mousedown', this.handleMouseDown.bind(this))
    this.canvas.addEventListener('mousemove', this.handleMouseMove.bind(this))
    this.canvas.addEventListener('mouseup', this.handleMouseUp.bind(this))
    this.canvas.addEventListener('click', this.handleClick.bind(this))

    // 触摸事件
    this.canvas.addEventListener('touchstart', this.handleTouchStart.bind(this))
    this.canvas.addEventListener('touchmove', this.handleTouchMove.bind(this))
    this.canvas.addEventListener('touchend', this.handleTouchEnd.bind(this))

    // 键盘事件
    document.addEventListener('keydown', this.handleKeyDown.bind(this))
    document.addEventListener('keyup', this.handleKeyUp.bind(this))
  }

  handleMouseDown(event) {
    const { x, y } = this.getCoordinates(event)
    const controlEvent = {
      type: 'mousedown',
      x,
      y,
      button: event.button
    }
    this.wsClient.send(JSON.stringify(controlEvent))
  }

  handleMouseMove(event) {
    const { x, y } = this.getCoordinates(event)
    const controlEvent = {
      type: 'mousemove',
      x,
      y
    }
    this.wsClient.send(JSON.stringify(controlEvent))
  }

  handleClick(event) {
    const { x, y } = this.getCoordinates(event)
    const controlEvent = {
      type: 'click',
      x,
      y
    }
    this.wsClient.send(JSON.stringify(controlEvent))
  }

  handleTouchStart(event) {
    event.preventDefault()
    const touch = event.touches[0]
    const { x, y } = this.getCoordinates(touch)
    const controlEvent = {
      type: 'touchstart',
      x,
      y
    }
    this.wsClient.send(JSON.stringify(controlEvent))
  }

  handleTouchMove(event) {
    event.preventDefault()
    const touch = event.touches[0]
    const { x, y } = this.getCoordinates(touch)
    const controlEvent = {
      type: 'touchmove',
      x,
      y
    }
    this.wsClient.send(JSON.stringify(controlEvent))
  }

  handleTouchEnd(event) {
    event.preventDefault()
    const controlEvent = {
      type: 'touchend'
    }
    this.wsClient.send(JSON.stringify(controlEvent))
  }

  handleKeyDown(event) {
    const controlEvent = {
      type: 'keydown',
      keyCode: event.keyCode,
      key: event.key
    }
    this.wsClient.send(JSON.stringify(controlEvent))
  }

  handleKeyUp(event) {
    const controlEvent = {
      type: 'keyup',
      keyCode: event.keyCode,
      key: event.key
    }
    this.wsClient.send(JSON.stringify(controlEvent))
  }

  getCoordinates(event) {
    const rect = this.canvas.getBoundingClientRect()
    return {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top
    }
  }
}
```

---

## 五、实现步骤

### 5.1 第一阶段：环境搭建（2-3天）

1. **下载和配置 ws-scrcpy**
   - 克隆 ws-scrcpy 项目
   - 安装 Python 依赖
   - 配置开发环境

2. **创建项目结构**
   - 创建后端服务模块
   - 创建前端组件目录
   - 配置路由和 API

### 5.2 第二阶段：后端开发（3-4天）

1. **实现端口管理器**
   - 端口分配和回收
   - 端口冲突检测

2. **实现投屏服务**
   - 启动/停止 ws-scrcpy 进程
   - 进程生命周期管理
   - 状态监控

3. **实现 API 路由**
   - 启动投屏接口
   - 停止投屏接口
   - 状态查询接口

4. **集成 ws-scrcpy**
   - 封装 scrcpy 客户端
   - 实现 WebSocket 服务
   - 视频流传输

### 5.3 第三阶段：前端开发（3-4天）

1. **创建投屏组件**
   - WebSocket 客户端
   - 视频渲染器
   - 事件处理器

2. **集成到设备详情页**
   - 嵌入投屏组件
   - 实现启动/停止控制
   - 状态显示

3. **实现交互功能**
   - 鼠标事件映射
   - 触摸事件映射
   - 键盘输入处理

### 5.4 第四阶段：测试和优化（2-3天）

1. **功能测试**
   - 单设备测试
   - 多设备并发测试
   - 边界情况测试

2. **性能优化**
   - 视频解码优化
   - 延迟优化
   - 内存优化

3. **错误处理**
   - 连接失败处理
   - 进程崩溃恢复
   - 用户友好的错误提示

---

## 六、技术难点和解决方案

### 6.1 视频解码性能

**问题**：H.264 解码在浏览器中性能较差

**解决方案**：
1. 使用 WebAssembly 加速解码
2. 使用硬件解码（如果浏览器支持）
3. 降低视频分辨率和帧率
4. 使用多线程解码

### 6.2 延迟优化

**问题**：WebSocket 传输 + 浏览器解码导致延迟较高

**解决方案**：
1. 使用二进制数据传输（减少序列化开销）
2. 优化视频编码参数（降低码率、调整GOP）
3. 使用 UDP 替代 TCP（如果允许丢包）
4. 实现预测渲染

### 6.3 多设备并发

**问题**：同时管理多个设备的投屏进程

**解决方案**：
1. 使用进程池管理
2. 合理分配系统资源
3. 实现设备优先级调度
4. 限制最大并发数

### 6.4 浏览器兼容性

**问题**：不同浏览器对 WebSocket 和 Canvas 支持不同

**解决方案**：
1. 使用 polyfill 兼容旧浏览器
2. 提供多种解码方案（Canvas、Video、WebGL）
3. 浏览器特性检测和降级处理
4. 提供最低浏览器版本要求

---

## 七、风险评估

### 7.1 技术风险

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|---------|
| ws-scrcpy 集成复杂 | 中 | 高 | 提前进行技术验证，准备备选方案 |
| 视频解码性能不足 | 高 | 中 | 使用 WebAssembly 加速，降低分辨率 |
| 延迟过高 | 中 | 中 | 优化传输协议，使用硬件解码 |
| 浏览器兼容性问题 | 低 | 中 | 提供兼容性检测和降级方案 |

### 7.2 资源风险

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|---------|
| CPU 占用过高 | 高 | 中 | 限制并发数，优化编码参数 |
| 内存占用过高 | 中 | 中 | 实现资源回收机制 |
| 端口耗尽 | 低 | 高 | 扩大端口范围，实现端口复用 |

---

## 八、预期效果

### 8.1 功能指标

- ✅ 支持设备屏幕实时镜像
- ✅ 支持鼠标/触摸控制
- ✅ 支持键盘输入
- ✅ 支持多设备并发（最多 5 台）
- ✅ 延迟控制在 100-150ms 以内
- ✅ 视频分辨率支持 720p/1080p

### 8.2 性能指标

- 视频帧率：30-60 fps
- 延迟：100-150ms
- CPU 占用：单设备 < 30%
- 内存占用：单设备 < 200MB

### 8.3 用户体验

- 启动时间：< 3 秒
- 连接成功率：> 95%
- 操作响应时间：< 150ms
- 视频流畅度：无明显卡顿

---

## 九、后续优化方向

### 9.1 功能增强

1. 支持音频传输
2. 支持文件拖拽传输
3. 支持屏幕录制
4. 支持多画面分屏显示

### 9.2 性能优化

1. 使用 WebRTC 替代 WebSocket
2. 实现自适应码率
3. 使用 GPU 加速渲染
4. 优化视频编码算法

### 9.3 用户体验

1. 提供快捷键支持
2. 实现手势识别
3. 支持自定义主题
4. 提供操作历史记录

---

## 十、总结

本方案基于 ws-scrcpy 框架进行二次开发，通过 WebSocket 传输 H.264 视频流，在浏览器中实现设备投屏和控制功能。整体架构清晰，模块化设计，易于扩展和维护。

预计开发周期为 10-14 天，技术风险可控，预期效果良好。建议先进行技术验证，确认可行性后再全面开发。
