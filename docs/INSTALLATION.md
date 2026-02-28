# 安装部署指南

## 环境要求

### 系统要求
- **操作系统**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **内存**: 最低 4GB，推荐 8GB+
- **存储**: 最低 10GB 可用空间
- **网络**: 稳定的互联网连接

### 软件依赖

- **Python**: 3.8 或更高版本
- **Node.js**: 16.0 或更高版本
- **npm**: 8.0 或更高版本
- **MySQL**: 5.7 或更高版本
- **Git**: 用于版本控制（可选）

### 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Element Plus + Vite |
| 后端 | Flask + SQLAlchemy + PyMySQL |
| 数据库 | MySQL 5.7+ |
| WebSocket | Flask-SocketIO + eventlet |
| 认证 | Flask-Login（基于 session） |
| 会话存储 | Flask-Session（filesystem） |

## 详细安装步骤

### 1. Python 环境安装

#### Windows
1. 访问 [Python 官网](https://www.python.org/downloads/)
2. 下载 Python 3.8+ 安装包
3. 运行安装程序，勾选 "Add Python to PATH"
4. 验证安装：
```cmd
python --version
pip --version
```

#### macOS
```bash
brew install python3
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### 2. Node.js 环境安装

#### Windows
1. 访问 [Node.js 官网](https://nodejs.org/)
2. 下载 LTS 版本安装包
3. 运行安装程序，按默认设置完成安装
4. 验证安装：
```cmd
node --version
npm --version
```

#### macOS
```bash
brew install node
```

#### Linux (Ubuntu/Debian)
```bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 3. MySQL 安装

#### Windows
1. 下载 [MySQL Installer](https://dev.mysql.com/downloads/installer/)
2. 选择 "Server only" 或 "Developer Default"
3. 设置 root 密码，记住该密码
4. 配置字符集为 utf8mb4

#### macOS
```bash
brew install mysql
brew services start mysql
mysql_secure_installation
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation
```

#### 创建数据库
```sql
mysql -u root -p

CREATE DATABASE mobile_test_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 项目部署

### 1. 获取项目代码

```bash
git clone <仓库地址>
cd MobTestPlatform
```

### 2. 后端部署

#### 安装依赖
```bash
pip install -r backend/requirements.txt
```

> 如果安装较慢，可使用国内镜像源：
> ```bash
> pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r backend/requirements.txt
> ```

#### 配置环境变量

编辑 `backend/.env` 文件，根据实际环境修改以下配置：

```env
# Flask 启动
FLASK_ENV=development
PORT=5000

# 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=你的数据库密码
MYSQL_DATABASE=mobile_test_platform

# 安全密钥（生产环境务必改为随机强密钥）
SECRET_KEY=your-secret-key-here

# CORS 允许的域名（逗号分隔，会自动合并本机及内网地址）
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# 邮件配置（QQ 邮箱：用于登录验证码、找回密码、绑定/解绑邮箱）
SMTP_USER=你的QQ邮箱
SMTP_PASSWORD=QQ邮箱授权码
```

可选配置项（不配置则使用默认值）：

```env
# 会话超时（分钟），默认 1440（24 小时）
# SESSION_TIMEOUT_MINUTES=1440

# 分页设置
# DEFAULT_PAGE_SIZE=20
# MAX_PAGE_SIZE=100

# 日志
# LOG_LEVEL=INFO
# LOG_FILE=logs/app.log

# SMTP 高级配置（默认 QQ 邮箱）
# SMTP_HOST=smtp.qq.com
# SMTP_PORT=465
# SMTP_USE_SSL=true
# SMTP_FROM_NAME=移动测试平台

# 前端重置密码页地址
# FRONTEND_RESET_PASSWORD_URL=http://localhost:8080/reset-password
```

#### 初始化数据库

按顺序执行以下脚本：

```bash
# 1. 创建数据库（如果上面已手动创建，可跳过）
python database/01_create_database.py

# 2. 创建数据表
python database/03_create_tables.py

# 3. 插入测试数据（可选）
python database/05_insert_test_data.py
```

#### 启动后端服务

```bash
cd backend
python run.py
```

后端服务将在 `http://127.0.0.1:5000` 启动。

### 3. 前端部署

#### 安装依赖
```bash
cd frontend
npm install
```

> 如果安装较慢，可使用国内镜像源：
> ```bash
> npm config set registry https://registry.npmmirror.com/
> npm install
> ```

#### 开发模式启动
```bash
npm run dev
```

前端开发服务器将在 `http://localhost:8081` 启动，`/api` 和 `/socket.io` 请求会自动代理到后端 `http://127.0.0.1:5000`。

#### 生产环境构建
```bash
npm run build
```

构建产物输出到 `frontend/dist/` 目录。

### 4. 一键启动（推荐）

项目提供了统一启动脚本，可同时启动前后端服务：

```bash
python start.py
```

该脚本会使用 `multiprocessing` 同时启动后端（`python run.py`）和前端（`npm run dev`）。按 `Ctrl+C` 可停止所有服务。

## 端口说明

| 服务 | 端口 | 说明 |
|------|------|------|
| 前端 Vite Dev Server | 8081 | 开发模式前端服务 |
| 后端 Flask | 5000 | API 服务及 WebSocket |
| MySQL | 3306 | 数据库服务 |

前端 Vite 配置了代理规则：
- `/api/*` → `http://127.0.0.1:5000`
- `/socket.io/*` → `http://127.0.0.1:5000`（支持 WebSocket）

## 故障排除

### 1. 端口被占用

**Windows:**
```cmd
netstat -ano | findstr :5000
netstat -ano | findstr :8081
```

**macOS/Linux:**
```bash
lsof -i :5000
lsof -i :8081
```

解决方法：关闭占用端口的进程，或修改配置文件中的端口号：
- 后端端口：`backend/.env` 中的 `PORT`
- 前端端口：`frontend/vite.config.js` 中的 `server.port`

### 2. 数据库连接失败

- 确认 MySQL 服务已启动
- 确认 `backend/.env` 中的数据库连接信息（MYSQL_HOST、MYSQL_PORT、MYSQL_USER、MYSQL_PASSWORD、MYSQL_DATABASE）正确
- 确认数据库 `mobile_test_platform` 已创建
- 确认数据库字符集为 utf8mb4

### 3. 后端依赖安装失败

```bash
# 升级 pip
python -m pip install --upgrade pip

# 使用国内镜像源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r backend/requirements.txt
```

如果 `cryptography` 或 `bcrypt` 安装失败，可能需要安装 C 编译工具：
- Windows: 安装 [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- macOS: `xcode-select --install`
- Linux: `sudo apt install build-essential libssl-dev libffi-dev`

### 4. 前端依赖安装失败

```bash
# 清理缓存
npm cache clean --force

# 删除 node_modules 重新安装
rm -rf node_modules package-lock.json
npm install

# 使用国内镜像源
npm config set registry https://registry.npmmirror.com/
npm install
```

### 5. 邮件发送失败

- 确认 `backend/.env` 中的 `SMTP_USER` 和 `SMTP_PASSWORD` 配置正确
- `SMTP_PASSWORD` 应填写 QQ 邮箱的授权码（非登录密码），在 QQ 邮箱「设置 → 账户 → POP3/IMAP」中生成
- 确认发件邮箱已开启 POP3/SMTP 服务

### 6. WebSocket 连接失败

- 确认后端已正常启动（Flask-SocketIO 依赖 eventlet）
- 检查浏览器控制台是否有 CORS 错误
- 确认前端代理配置正确（`/socket.io` 代理到后端）

## 日志查看

### 后端日志

开发模式下日志直接输出到终端。日志文件默认位置：`backend/logs/app.log`。

可通过 `backend/.env` 配置日志级别：
```env
LOG_LEVEL=DEBUG
LOG_FILE=logs/app.log
```

### 前端日志

开发模式下日志输出到终端和浏览器控制台。

## 备份与恢复

### 数据库备份

```bash
mysqldump -u root -p mobile_test_platform > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 数据库恢复

```bash
mysql -u root -p mobile_test_platform < backup_file.sql
```
