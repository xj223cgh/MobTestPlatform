# 安装部署指南

## 环境要求

### 系统要求
- **操作系统**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **内存**: 最低 4GB，推荐 8GB+
- **存储**: 最低 20GB 可用空间
- **网络**: 稳定的互联网连接

### 软件依赖

#### 必需依赖
- **Python**: 3.8 或更高版本
- **Node.js**: 16.0 或更高版本
- **npm**: 8.0 或更高版本 (或 yarn 1.22+)
- **数据库**: MySQL 5.7+ 或 PostgreSQL 10+

#### 可选依赖
- **Redis**: 6.0+ (用于缓存和任务队列)
- **Git**: 用于版本控制
- **Docker**: 用于容器化部署

## 详细安装步骤

### 1. Python 环境安装

#### Windows
1. 访问 [Python官网](https://www.python.org/downloads/)
2. 下载 Python 3.8+ 安装包
3. 运行安装程序，勾选 "Add Python to PATH"
4. 验证安装：
```cmd
python --version
pip --version
```

#### macOS
```bash
# 使用 Homebrew 安装
brew install python3

# 或者从官网下载安装包
# https://www.python.org/downloads/macos/
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### 2. Node.js 环境安装

#### Windows
1. 访问 [Node.js官网](https://nodejs.org/)
2. 下载 LTS 版本安装包
3. 运行安装程序，按默认设置完成安装
4. 验证安装：
```cmd
node --version
npm --version
```

#### macOS
```bash
# 使用 Homebrew 安装
brew install node

# 或者从官网下载安装包
# https://nodejs.org/
```

#### Linux (Ubuntu/Debian)
```bash
# 使用 NodeSource 仓库安装
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 3. 数据库安装

#### MySQL 安装

**Windows:**
1. 下载 [MySQL Installer](https://dev.mysql.com/downloads/installer/)
2. 选择 "Server only" 或 "Developer Default"
3. 设置 root 密码，记住该密码
4. 配置字符集为 utf8mb4

**macOS:**
```bash
# 使用 Homebrew 安装
brew install mysql

# 启动 MySQL 服务
brew services start mysql

# 安全配置
mysql_secure_installation
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation
```

#### 创建数据库
```sql
-- 登录 MySQL
mysql -u root -p

-- 创建数据库
CREATE DATABASE mob_test_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户 (可选)
CREATE USER 'mobtest'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON mob_test_platform.* TO 'mobtest'@'localhost';
FLUSH PRIVILEGES;
```

### 4. Redis 安装 (可选)

#### Windows
```bash
# 使用 Chocolatey 安装
choco install redis-64

# 或者下载预编译版本
# https://github.com/microsoftarchive/redis/releases
```

#### macOS
```bash
brew install redis
brew services start redis
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

## 项目部署

### 1. 获取项目代码

```bash
# 克隆项目
git clone https://github.com/your-org/mob-test-platform.git
cd mob-test-platform

# 或者下载 ZIP 压缩包并解压
```

### 2. 后端部署

#### 创建虚拟环境
```bash
cd backend

# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 安装依赖
```bash
pip install -r requirements.txt
```

#### 配置环境变量
创建 `.env` 文件：
```env
# 数据库配置
DATABASE_URL=mysql://username:password@localhost:3306/mob_test_platform

# Redis 配置 (可选)
REDIS_URL=redis://localhost:6379/0

# JWT 密钥
JWT_SECRET_KEY=your-secret-key-here

# 邮件配置 (可选)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# 文件上传配置
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216  # 16MB
```

#### 初始化数据库
```bash
# 运行数据库迁移脚本
python init_backend.py

# 或者手动执行 SQL 文件
mysql -u root -p mob_test_platform < database/03_create_tables.sql
mysql -u root -p mob_test_platform < database/05_insert_test_data.sql
```

#### 启动后端服务
```bash
# 开发模式
python run.py

# 生产模式 (推荐使用 Gunicorn)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

### 3. 前端部署

#### 安装依赖
```bash
cd frontend
npm install
```

#### 配置环境变量
创建 `.env.local` 文件：
```env
# API 基础地址
VITE_API_BASE_URL=http://localhost:8000/api

# 应用标题
VITE_APP_TITLE=移动测试平台

# 其他配置
VITE_APP_VERSION=1.0.0
```

#### 开发模式启动
```bash
npm run dev
```

#### 生产环境构建
```bash
# 构建生产版本
npm run build

# 构建结果在 dist/ 目录
```

### 4. 使用启动脚本 (推荐)

项目提供了便捷的启动脚本：

#### Windows
```cmd
# 双击运行 start.bat
# 或在命令行执行
start.bat
```

#### Linux/macOS
```bash
# 给脚本执行权限
chmod +x start.sh

# 运行启动脚本
./start.sh
```

#### 高级选项
```bash
# 仅启动前端
python start_platform.py --frontend-only

# 仅启动后端
python start_platform.py --backend-only

# 跳过依赖检查
python start_platform.py --no-deps

# 指定端口
python start_platform.py --port 3000 --backend-port 9000
```

## 生产环境部署

### 1. 使用 Docker 部署

#### 创建 Docker Compose 文件
```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: mob_test_platform
      MYSQL_USER: mobtest
      MYSQL_PASSWORD: userpassword
    volumes:
      - mysql_data:/var/lib/mysql
      - ./database:/docker-entrypoint-initdb.d
    ports:
      - "3306:3306"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    environment:
      DATABASE_URL: mysql://mobtest:userpassword@db:3306/mob_test_platform
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - db
      - redis
    ports:
      - "8000:8000"
    volumes:
      - ./uploads:/app/uploads

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  mysql_data:
```

#### 启动服务
```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 2. 传统部署方式

#### 使用 Nginx + Gunicorn

**安装 Nginx:**
```bash
# Ubuntu/Debian
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
```

**配置 Nginx:**
```nginx
# /etc/nginx/sites-available/mob-test-platform
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API 代理
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket 支持
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

**启用站点:**
```bash
sudo ln -s /etc/nginx/sites-available/mob-test-platform /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**使用 Gunicorn 启动后端:**
```bash
# 创建 Gunicorn 配置文件
cat > gunicorn.conf.py << EOF
bind = "127.0.0.1:8000"
workers = 4
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
EOF

# 启动服务
gunicorn -c gunicorn.conf.py run:app

# 使用 systemd 管理服务
sudo tee /etc/systemd/system/mob-test-platform.service << EOF
[Unit]
Description=Mobile Test Platform
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/backend
Environment=PATH=/path/to/backend/venv/bin
ExecStart=/path/to/backend/venv/bin/gunicorn -c gunicorn.conf.py run:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable mob-test-platform
sudo systemctl start mob-test-platform
```

## 故障排除

### 常见问题

#### 1. 端口冲突
```bash
# 查看端口占用
netstat -tulpn | grep :8000
lsof -i :8000

# 修改配置文件中的端口
# 后端: backend/config/config.py
# 前端: frontend/vite.config.js
```

#### 2. 数据库连接失败
- 检查数据库服务是否启动
- 验证连接字符串和凭据
- 检查防火墙设置

#### 3. 依赖安装失败
```bash
# 清理 npm 缓存
npm cache clean --force

# 使用国内镜像源
npm config set registry https://registry.npmmirror.com/

# Python 使用国内镜像源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

#### 4. 权限问题
```bash
# Linux/macOS 下给脚本执行权限
chmod +x start.sh

# 确保文件所有者正确
sudo chown -R $USER:$USER /path/to/project
```

### 日志查看

#### 后端日志
```bash
# 开发模式日志直接输出到终端

# 生产模式日志
tail -f /var/log/mob-test-platform.log
```

#### 前端日志
```bash
# 开发服务器日志
npm run dev

# 构建错误日志
npm run build 2>&1 | tee build.log
```

### 性能优化

#### 后端优化
- 使用连接池
- 启用 Redis 缓存
- 配置 Gunicorn worker 数量
- 使用 Nginx 反向代理

#### 前端优化
- 启用代码分割
- 使用 CDN 加速静态资源
- 开启 Gzip 压缩
- 配置浏览器缓存

## 安全配置

### 1. 数据库安全
- 使用强密码
- 限制数据库访问权限
- 定期备份数据
- 启用 SSL 连接

### 2. 应用安全
- 配置 HTTPS
- 设置安全的 JWT 密钥
- 启用 CORS 保护
- 定期更新依赖包

### 3. 服务器安全
- 配置防火墙
- 禁用不必要的服务
- 定期更新系统
- 监控异常访问

## 备份与恢复

### 数据库备份
```bash
# 备份数据库
mysqldump -u root -p mob_test_platform > backup_$(date +%Y%m%d_%H%M%S).sql

# 恢复数据库
mysql -u root -p mob_test_platform < backup_file.sql
```

### 文件备份
```bash
# 备份上传文件
tar -czf uploads_backup_$(date +%Y%m%d_%H%M%S).tar.gz uploads/

# 备份配置文件
cp .env .env.backup
```

### 自动备份脚本
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
mysqldump -u root -p mob_test_platform > $BACKUP_DIR/db_backup_$DATE.sql

# 备份文件
tar -czf $BACKUP_DIR/files_backup_$DATE.tar.gz uploads/

# 清理旧备份 (保留30天)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

添加到 crontab 实现自动备份：
```bash
# 每天凌晨2点执行备份
0 2 * * * /path/to/backup.sh
```