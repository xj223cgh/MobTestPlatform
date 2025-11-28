from flask import Blueprint, request
from flask_login import login_required, current_user

from app.models.models import Device, db
from app.utils.helpers import (
    success_response, error_response, get_pagination_params, log_user_action,
    validate_json_data
)

bp = Blueprint('devices', __name__)


@bp.route('', methods=['GET'])
@login_required
def get_devices():
    """获取设备列表"""
    page, size = get_pagination_params()
    search = request.args.get('search', '').strip()
    os_type = request.args.get('os_type', '').strip()
    status = request.args.get('status', '').strip()
    
    # 构建查询
    query = Device.query
    
    # 搜索过滤
    if search:
        query = query.filter(
            Device.device_name.contains(search) |
            Device.device_model.contains(search) |
            Device.device_id.contains(search)
        )
    
    # 操作系统类型过滤
    if os_type:
        query = query.filter(Device.os_type == os_type)
    
    # 状态过滤
    if status:
        query = query.filter(Device.status == status)
    
    # 分页
    pagination = query.paginate(
        page=page, per_page=size, error_out=False
    )
    
    devices = [device.to_dict() for device in pagination.items]
    
    return success_response({
        'devices': devices,
        'pagination': {
            'page': page,
            'size': size,
            'total': pagination.total,
            'pages': pagination.pages
        }
    })


@bp.route('/<int:device_id>', methods=['GET'])
@login_required
def get_device(device_id):
    """获取设备详情"""
    device = Device.query.get_or_404(device_id)
    return success_response({
        'device': device.to_dict()
    })


@bp.route('', methods=['POST'])
@login_required
@validate_json_data(['device_name', 'device_model', 'os_type', 'os_version', 'device_id'])
def create_device():
    """创建设备"""
    data = request.get_json()
    
    # 检查设备ID是否已存在
    if Device.query.filter_by(device_id=data['device_id']).first():
        return error_response(400, "设备ID已存在")
    
    device = Device(
        device_name=data['device_name'],
        device_model=data['device_model'],
        os_type=data['os_type'],
        os_version=data['os_version'],
        device_id=data['device_id'],
        status=data.get('status', 'offline'),
        owner_id=data.get('owner_id')
    )
    
    try:
        db.session.add(device)
        db.session.commit()
        
        log_user_action("创建设备", f"设备名称: {device.device_name}")
        
        return success_response({
            'device': device.to_dict()
        }, "设备创建成功")
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, "设备创建失败，请稍后重试")


@bp.route('/<int:device_id>', methods=['PUT'])
@login_required
def update_device(device_id):
    """更新设备信息"""
    device = Device.query.get_or_404(device_id)
    data = request.get_json()
    
    # 更新字段
    if 'device_name' in data:
        device.device_name = data['device_name']
    
    if 'device_model' in data:
        device.device_model = data['device_model']
    
    if 'os_version' in data:
        device.os_version = data['os_version']
    
    if 'status' in data:
        device.status = data['status']
    
    if 'owner_id' in data:
        device.owner_id = data['owner_id']
    
    try:
        db.session.commit()
        
        log_user_action("更新设备", f"设备ID: {device_id}")
        
        return success_response({
            'device': device.to_dict()
        }, "设备信息更新成功")
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, "设备信息更新失败，请稍后重试")


@bp.route('/<int:device_id>', methods=['DELETE'])
@login_required
def delete_device(device_id):
    """删除设备"""
    device = Device.query.get_or_404(device_id)
    
    try:
        db.session.delete(device)
        db.session.commit()
        
        log_user_action("删除设备", f"设备名称: {device.device_name}")
        
        return success_response(message="设备删除成功")
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, "设备删除失败，请稍后重试")


@bp.route('/os-types', methods=['GET'])
@login_required
def get_os_types():
    """获取操作系统类型列表"""
    os_types = [
        {'value': 'android', 'label': 'Android'},
        {'value': 'ios', 'label': 'iOS'}
    ]
    
    return success_response({
        'os_types': os_types
    })


@bp.route('/status-options', methods=['GET'])
@login_required
def get_status_options():
    """获取设备状态选项"""
    status_options = [
        {'value': 'online', 'label': '在线'},
        {'value': 'offline', 'label': '离线'},
        {'value': 'busy', 'label': '忙碌'},
        {'value': 'maintenance', 'label': '维护中'}
    ]
    
    return success_response({
        'status_options': status_options
    })