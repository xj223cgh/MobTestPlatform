import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_login import LoginManager, current_user
from flask_cors import CORS
from flask_session import Session
from flask_socketio import SocketIO, join_room, disconnect

from app.config.config import config
from app.models.models import db, User


login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please login first'
login_manager.login_message_category = 'info'


@login_manager.unauthorized_handler
def unauthorized_handler():
    """API 请求直接返回 401，非 API 请求走 Flask-Login 默认重定向"""
    from flask import request
    from app.utils.helpers import error_response
    if request.path.startswith('/api/'):
        return error_response(401, "Unauthorized")
    return login_manager.unauthorized()


@login_manager.user_loader
def load_user(user_id):
    """加载用户。session 无效或 user_id 非数字时返回 None，避免 500。"""
    if user_id is None:
        return None
    try:
        uid = int(user_id)
    except (TypeError, ValueError):
        return None
    return User.query.get(uid)


def create_app(config_name='default'):
    """创建Flask应用"""
    app = Flask(__name__)
    
    # 禁用严格斜杠，允许/projects和/projects/访问相同的路由
    app.url_map.strict_slashes = False
    
    # 设置默认编码为UTF-8，解决中文响应问题
    app.config['JSON_AS_ASCII'] = False
    app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'
    
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    db.init_app(app)
    login_manager.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    Session(app)
    setup_logging(app)
    
    from app.utils.scheduler import init_scheduler
    init_scheduler()
    
    register_blueprints(app)
    register_error_handlers(app)
    
    with app.app_context():
        db.create_all()
    
    # WebSocket：Flask-SocketIO。engineio 只支持字符串列表或 '*'，不支持正则；
    # 开发环境用 '*' 以允许内网 IP（如 http://10.13.254.75:8081）访问
    _cors = app.config.get('CORS_ORIGINS') or []
    if app.debug:
        cors_socket = '*'
    else:
        cors_socket = [o for o in _cors if isinstance(o, str)] if isinstance(_cors, list) else _cors
    # Windows 下 eventlet 不兼容（管道不支持非阻塞 I/O），使用 threading；非 Windows 下优先 eventlet 避免 WebSocket write() before start_response
    import sys
    if sys.platform == "win32":
        async_mode = "threading"
    else:
        try:
            import eventlet
            async_mode = "eventlet"
        except ImportError:
            async_mode = "threading"
    socketio = SocketIO(app, cors_allowed_origins=cors_socket or "*", async_mode=async_mode)
    app.socketio = socketio

    @socketio.on('connect')
    def on_connect():
        if current_user is None or not getattr(current_user, 'is_authenticated', False):
            disconnect()
            return
        join_room(f'user:{current_user.id}')
        app.logger.debug('SocketIO: user %s joined room user:%s', current_user.id, current_user.id)
    
    return app


def setup_logging(app):
    """配置日志"""
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
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
    from app.routes import auth, users, devices, test_cases, test_tasks, home, projects, iterations, suite_case_relations, test_suites, review_tasks, files, reports, settings_routes, ai_tasks, notifications, roles, mindmap

    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(roles.bp)
    app.register_blueprint(settings_routes.bp)
    app.register_blueprint(notifications.bp)
    app.register_blueprint(users.bp, url_prefix='/api/users')
    app.register_blueprint(devices.bp, url_prefix='/api/devices')
    app.register_blueprint(test_cases.bp, url_prefix='/api/test-cases')
    app.register_blueprint(test_tasks.bp, url_prefix='/api/test-tasks')
    app.register_blueprint(home.bp, url_prefix='/api/home')
    app.register_blueprint(projects.bp, url_prefix='/api/projects')
    app.register_blueprint(iterations.bp, url_prefix='/api/iterations')
    app.register_blueprint(suite_case_relations.bp, url_prefix='/api/suite-case-relations')
    app.register_blueprint(test_suites.bp)
    app.register_blueprint(review_tasks.bp)
    app.register_blueprint(files.files_bp, url_prefix='/api/files')
    app.register_blueprint(reports.bp)
    app.register_blueprint(ai_tasks.bp)  # AI异步任务接口
    app.register_blueprint(mindmap.bp)  # 脑图数据接口


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