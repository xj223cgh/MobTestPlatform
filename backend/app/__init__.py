import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS
from flask_session import Session

from app.config.config import config
from app.models.models import db, User


# 创建登录管理器
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please login first'
login_manager.login_message_category = 'info'


# 自定义未授权处理器，针对API请求直接返回401而不是重定向
@login_manager.unauthorized_handler
def unauthorized_handler():
    from flask import request
    from app.utils.helpers import error_response
    # 检查是否是API请求
    if request.path.startswith('/api/'):
        # API请求直接返回401
        return error_response(401, "Unauthorized")
    # 非API请求返回重定向
    return login_manager.unauthorized()


@login_manager.user_loader
def load_user(user_id):
    """加载用户"""
    return User.query.get(int(user_id))


def create_app(config_name='default'):
    """创建Flask应用"""
    app = Flask(__name__)
    
    # 禁用严格斜杠，允许/projects和/projects/访问相同的路由
    app.url_map.strict_slashes = False
    
    # 设置默认编码为UTF-8，解决中文响应问题
    app.config['JSON_AS_ASCII'] = False
    app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'
    
    # 加载配置
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    
    # 配置Session
    Session(app)
    
    # 配置日志
    setup_logging(app)
    
    # 初始化定时任务调度器
    from app.utils.scheduler import init_scheduler
    init_scheduler()
    
    # 注册蓝图
    register_blueprints(app)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app


def setup_logging(app):
    """配置日志"""
    if not app.debug and not app.testing:
        # 确保日志目录存在
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # 配置文件日志处理器
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'],
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('MobTestPlatform startup')


def register_blueprints(app):
    """注册蓝图"""
    from app.routes import auth, users, devices, test_cases, test_tasks, tools, home, projects, iterations, suite_case_relations, test_suites, review_tasks, files, reports
    
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(users.bp, url_prefix='/api/users')
    app.register_blueprint(devices.bp, url_prefix='/api/devices')
    app.register_blueprint(test_cases.bp, url_prefix='/api/test-cases')
    app.register_blueprint(test_tasks.bp, url_prefix='/api/test-tasks')
    app.register_blueprint(tools.bp, url_prefix='/api/tools')
    app.register_blueprint(home.bp, url_prefix='/api/home')
    app.register_blueprint(projects.bp, url_prefix='/api/projects')
    app.register_blueprint(iterations.bp, url_prefix='/api/iterations')
    app.register_blueprint(suite_case_relations.bp, url_prefix='/api/suite-case-relations')
    app.register_blueprint(test_suites.bp)
    app.register_blueprint(review_tasks.bp)
    app.register_blueprint(files.files_bp, url_prefix='/api/files')
    app.register_blueprint(reports.bp)


def register_error_handlers(app):
    """注册错误处理器"""
    
    @app.errorhandler(400)
    def bad_request(error):
        from app.utils.helpers import error_response
        return error_response(400, "Bad Request")
    
    @app.errorhandler(401)
    def unauthorized(error):
        from app.utils.helpers import error_response
        return error_response(401, "Unauthorized")
    
    @app.errorhandler(403)
    def forbidden(error):
        from app.utils.helpers import error_response
        return error_response(403, "Forbidden")
    
    @app.errorhandler(404)
    def not_found(error):
        from app.utils.helpers import error_response
        return error_response(404, "Not Found")
    
    @app.errorhandler(500)
    def internal_error(error):
        from app.utils.helpers import error_response
        app.logger.error(f'Server Error: {error}')
        return error_response(500, "Internal Server Error")
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        from app.utils.helpers import error_response
        app.logger.error(f'Unhandled Exception: {error}', exc_info=True)
        return error_response(500, "Internal Server Error")