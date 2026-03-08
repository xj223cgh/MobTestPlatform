import re
import json
from functools import wraps
from flask import request, jsonify, session, abort, current_app
from flask_login import current_user
from app.models.models import User, SystemSetting


def validate_phone(phone):
    """验证手机号格式"""
    pattern = r'^1[3-9]\d{9}$'
    return re.match(pattern, phone) is not None


def validate_username(username):
    """验证用户名格式（3-14个字节长度限制）"""
    if not username or len(username.encode('utf-8')) < 3 or len(username.encode('utf-8')) > 14:
        return False
    return True


# QQ 邮箱格式：仅支持 @qq.com，本地部分为 5～11 位数字（QQ 号规则）
QQ_EMAIL_PATTERN = re.compile(r"^[1-9]\d{4,10}@qq\.com$", re.IGNORECASE)


def validate_qq_email(email):
    """验证是否为合法的 QQ 邮箱格式（不验证邮箱是否真实存在）。"""
    if not email or not isinstance(email, str):
        return False
    return QQ_EMAIL_PATTERN.match(email.strip().lower()) is not None


def success_response(data=None, message="Operation successful"):
    """统一成功响应格式"""
    from datetime import datetime
    # 创建响应对象，确保HTTP响应行使用英文状态消息
    response = jsonify({
        'code': 200,
        'message': message,
        'data': data,
        'timestamp': datetime.now().isoformat()
    })
    # 明确设置状态码，使用Flask内置的英文状态消息
    response.status_code = 200
    return response


def error_response(code, message, data=None):
    """统一错误响应格式"""
    from datetime import datetime
    # 创建响应对象，确保HTTP响应行使用英文状态消息
    response = jsonify({
        'code': code,
        'message': message,
        'data': data,
        'timestamp': datetime.now().isoformat()
    })
    # 明确设置状态码，使用Flask内置的英文状态消息
    response.status_code = code
    return response


def _get_default_page_size():
    """从系统设置读取默认每页条数，无则用 .env 的 DEFAULT_PAGE_SIZE（默认 20）"""
    try:
        s = SystemSetting.query.filter_by(setting_key='default_page_size').first()
        if s and s.setting_value:
            v = int(s.setting_value)
            max_size = current_app.config.get('MAX_PAGE_SIZE', 100)
            if 5 <= v <= max_size:
                return v
    except (ValueError, TypeError):
        pass
    return current_app.config.get('DEFAULT_PAGE_SIZE', 20)


def get_pagination_params():
    """获取分页参数"""
    page = request.args.get('page', 1, type=int)
    size_param = request.args.get('size', type=int)
    page_size_param = request.args.get('page_size', type=int)
    default_size = _get_default_page_size()
    size = size_param if size_param is not None else (page_size_param if page_size_param is not None else default_size)
    size = min(size, current_app.config.get('MAX_PAGE_SIZE', 100))
    page = max(page, 1)
    return page, size


def parse_json_field(field_value):
    """解析JSON字段"""
    if not field_value:
        return None
    try:
        return json.loads(field_value)
    except (json.JSONDecodeError, TypeError):
        return None


def format_json_field(data):
    """格式化JSON字段"""
    if data is None:
        return None
    try:
        return json.dumps(data, ensure_ascii=False)
    except (TypeError, ValueError):
        return str(data)


def log_user_action(action, details=None):
    """记录用户操作日志"""
    if current_user is not None and getattr(current_user, 'is_authenticated', False):
        import logging
        logger = logging.getLogger(__name__)
        log_message = f"用户 {current_user.username} 执行了 {action}"
        if details:
            log_message += f" - 详情: {details}"
        logger.info(log_message)


def validate_json_data(required_fields=None):
    """验证JSON数据"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return error_response(400, "请求必须是JSON格式")
            
            data = request.get_json()
            if not data:
                return error_response(400, "请求体不能为空")
            
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return error_response(400, f"缺少必需字段: {', '.join(missing_fields)}")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def search_query(query, search_term, search_fields):
    """构建搜索查询"""
    if not search_term or not search_fields:
        return query
    
    search_filter = []
    for field in search_fields:
        search_filter.append(getattr(query.column_descriptions[0]['type'], field).like(f'%{search_term}%'))
    
    return query.filter(*search_filter)