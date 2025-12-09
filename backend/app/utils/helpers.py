import re
import json
from functools import wraps
from flask import request, jsonify, session, abort
from flask_login import current_user
from app.models.models import User


def validate_phone(phone):
    """验证手机号格式"""
    pattern = r'^1[3-9]\d{9}$'
    return re.match(pattern, phone) is not None


def validate_username(username):
    """验证用户名格式（3-14个字节长度限制）"""
    if not username or len(username.encode('utf-8')) < 3 or len(username.encode('utf-8')) > 14:
        return False
    return True


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


def get_pagination_params():
    """获取分页参数"""
    page = request.args.get('page', 1, type=int)
    # 同时支持size和page_size参数
    # 确保两个参数都使用int类型
    size_param = request.args.get('size', type=int)
    page_size_param = request.args.get('page_size', type=int)
    # 使用第一个有效的参数，如果都无效则使用默认值20
    size = size_param if size_param is not None else (page_size_param if page_size_param is not None else 20)
    
    # 限制每页最大数量
    size = min(size, 100)
    
    # 确保页码最小为1
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
    if current_user.is_authenticated:
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