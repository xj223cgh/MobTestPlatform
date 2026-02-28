import os
import re
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# 固定从 backend 目录加载 .env（config 在 backend/app/config/ 下，向上两级到 backend）
_backend_dir = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=_backend_dir / '.env')


def _cors_origins():
    """构建 CORS 允许的 origin 列表：本机 + 环境变量中的配置 + 内网网段（供同局域网他人访问）"""
    base = [
        "http://localhost:3000", "http://127.0.0.1:3000",
        "http://localhost:5000", "http://127.0.0.1:5000",
        "http://localhost:8080", "http://127.0.0.1:8080",
        "http://localhost:8081", "http://127.0.0.1:8081",
    ]
    extra = os.environ.get("CORS_ORIGINS", "")
    if extra:
        base.extend(origin.strip() for origin in extra.split(",") if origin.strip())
    # 内网网段：192.168.x.x、10.x.x.x（任意端口），便于同公司内网访问
    base.extend([
        re.compile(r"^http://192\.168\.\d{1,3}\.\d{1,3}(:\d+)?$"),
        re.compile(r"^http://10\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d+)?$"),
    ])
    return base


def is_origin_allowed(origin, allowed_origins=None):
    """
    判断请求的 origin 是否在允许列表中。
    支持字符串精确匹配和正则匹配（用于 Socket.IO 等只接受简单列表的库）。
    """
    if not origin:
        return False
    origins = allowed_origins if allowed_origins is not None else _cors_origins()
    for allowed in origins:
        if hasattr(allowed, "match"):  # 正则
            if allowed.match(origin):
                return True
        elif allowed == "*" or allowed == origin:
            return True
    return False


class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT') or 3306)
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or '123456'
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE') or 'mobile_test_platform'
    
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'MobTestPlatform:'
    SESSION_FILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../flask_session')
    SESSION_FILE_THRESHOLD = 50  # 降低阈值，增加清理频率
    SESSION_FILE_MODE = 0o600  # 设置文件权限
    # 会话超时（分钟），管理后台「安全设置」可覆盖此默认值
    SESSION_TIMEOUT_MINUTES = int(os.environ.get('SESSION_TIMEOUT_MINUTES') or 1440)  # 默认 24 小时
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=int(os.environ.get('SESSION_TIMEOUT_MINUTES') or 1440))
    
    # CORS 配置（含本机 + .env 中的 CORS_ORIGINS + 内网 192.168.x.x / 10.x.x.x）
    CORS_ORIGINS = _cors_origins()
    
    # QQ 邮箱 SMTP（用于登录验证码、找回密码）
    SMTP_HOST = os.environ.get('SMTP_HOST') or 'smtp.qq.com'
    SMTP_PORT = int(os.environ.get('SMTP_PORT') or 465)
    SMTP_USE_SSL = os.environ.get('SMTP_USE_SSL', 'true').lower() in ('1', 'true', 'yes')
    SMTP_USER = os.environ.get('SMTP_USER') or ''
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD') or ''  # QQ 邮箱为授权码
    SMTP_FROM_NAME = os.environ.get('SMTP_FROM_NAME') or '移动测试平台'
    # 前端重置密码页地址（用于邮件中的链接）
    FRONTEND_RESET_PASSWORD_URL = os.environ.get('FRONTEND_RESET_PASSWORD_URL') or 'http://localhost:8080/reset-password'

    # 分页配置（管理后台「系统设置」可覆盖默认每页条数）
    DEFAULT_PAGE_SIZE = int(os.environ.get('DEFAULT_PAGE_SIZE') or 20)
    MAX_PAGE_SIZE = int(os.environ.get('MAX_PAGE_SIZE') or 100)

    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or 'logs/app.log'

    # 文件存储配置（不配则使用 backend 下相对路径）
    _default_storage = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../storage')
    STORAGE_PATH = os.environ.get('STORAGE_PATH') or _default_storage
    SCRIPT_STORAGE_PATH = os.path.join(STORAGE_PATH, 'device_scripts')
    LOGO_STORAGE_PATH = os.path.join(STORAGE_PATH, 'logos')  # 系统 Logo 存放目录
    MAX_SCRIPT_SIZE = int(os.environ.get('MAX_SCRIPT_SIZE') or 0) or (10 * 1024 * 1024)  # 默认 10MB
    MAX_LOGO_SIZE = int(os.environ.get('MAX_LOGO_SIZE') or 0) or (2 * 1024 * 1024)  # 默认 2MB
    ALLOWED_SCRIPT_EXTENSIONS = ['.sh', '.py']
    ALLOWED_LOGO_EXTENSIONS = ['.jpg', '.jpeg', '.png']
    
    @staticmethod
    def init_app(app):
        """初始化应用配置"""
        pass


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = False
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    LOG_LEVEL = 'WARNING'


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}