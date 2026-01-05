import subprocess
import os
import re
import shlex
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


@bp.route('/adb/devices', methods=['GET'])
@login_required
def get_adb_devices():
    """获取当前连接的设备列表"""
    try:
        # 计算项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        
        # 使用escrcpy中的adb
        adb_path = os.path.join(
            project_root,
            'escrcpy', 'electron', 'resources', 'extra', 'win', 'scrcpy', 'adb.exe'
        )
        
        # 执行adb命令获取设备列表
        result = subprocess.run([adb_path, 'devices', '-l'], capture_output=True, text=True, check=True, encoding='utf-8', errors='ignore')
        
        # 解析adb输出
        devices = []
        lines = result.stdout.strip().split('\n')[1:]  # 跳过第一行 "List of devices attached"
        
        for line in lines:
            if not line.strip():
                continue
                
            # 使用正则表达式解析设备信息
            match = re.match(r'(\S+)\s+(device|unauthorized|offline)(.*)', line)
            if match:
                serial = match.group(1)
                status = match.group(2)
                info = match.group(3).strip()
                
                # 解析设备详情
                device_info = {
                    'id': serial,
                    'status': status,
                    'name': '',
                    'wifi': False,
                    'remark': ''
                }
                
                # 检查是否为WiFi设备
                if ':' in serial and not serial.startswith('emulator-'):
                    device_info['wifi'] = True
                
                # 提取设备名称
                model_match = re.search(r'model:(\S+)', info)
                if model_match:
                    device_info['name'] = model_match.group(1)
                
                devices.append(device_info)
        
        return success_response({
            'devices': devices
        })
    except subprocess.CalledProcessError as e:
        return error_response(500, f"执行adb命令失败: {e.stderr}")
    except Exception as e:
        return error_response(500, f"获取设备列表失败: {str(e)}")


@bp.route('/adb/command', methods=['POST'])
@login_required
def execute_adb_command():
    """执行adb命令"""
    data = request.get_json()
    command = data.get('command')
    
    if not command:
        return error_response(400, "命令不能为空")
    
    try:
        # 计算项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        
        # 检查是否是scrcpy命令
        if command.startswith('scrcpy'):
            # 使用本地的scrcpy可执行文件
            scrcpy_path = os.path.join(
                project_root,
                'escrcpy', 'electron', 'resources', 'extra', 'win', 'scrcpy', 'scrcpy.exe'
            )
            
            # 设置ADB环境变量
            adb_path = os.path.join(
                project_root,
                'escrcpy', 'electron', 'resources', 'extra', 'win', 'scrcpy', 'adb.exe'
            )
            
            # 构建环境变量
            env = os.environ.copy()
            env['ADB'] = adb_path
            
            # 构建完整的命令
            command_parts = shlex.split(command)
            command_parts[0] = scrcpy_path
            
            # 执行scrcpy命令，不使用check=True，避免命令失败时抛出异常
            result = subprocess.run(command_parts, capture_output=True, text=True, check=False, env=env, encoding='utf-8', errors='ignore')
            
            # 根据退出码判断命令是否成功
            if result.returncode == 0:
                # 命令执行成功
                return success_response({
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'exit_code': result.returncode,
                    'command': command_parts
                })
            else:
                # 命令执行失败，返回错误响应
                error_message = result.stderr or "命令执行失败"
                return error_response(500, f"命令执行失败: {error_message}")
        else:
            # 使用escrcpy中的adb
            adb_path = os.path.join(
                project_root,
                'escrcpy', 'electron', 'resources', 'extra', 'win', 'scrcpy', 'adb.exe'
            )
            
            # 构建完整的命令
            command_parts = shlex.split(command)
            full_command = [adb_path] + command_parts
            
            # 执行命令，避免check=True导致的立即退出
            result = subprocess.run(full_command, capture_output=True, text=True, shell=False, encoding='utf-8', errors='ignore')
            
            # 检查stdout中是否包含错误信息
            stdout_lower = result.stdout.lower() if result.stdout else ''
            error_keywords = ['cannot connect', 'unable to connect', 'connection refused', '由于目标计算机积极拒绝', 'no devices/emulators found', 'device not found', 'offline', 'disconnected']
            
            # 检查是否包含错误关键词
            has_error = any(keyword in stdout_lower for keyword in error_keywords)
            
            # 根据退出码和stdout判断命令是否成功
            if result.returncode == 0 and not has_error:
                # 命令执行成功
                return success_response({
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'exit_code': result.returncode,
                    'command': full_command
                })
            else:
                # 命令执行失败，返回错误响应
                error_message = result.stderr or result.stdout or "命令执行失败"
                print(f"DEBUG: Command failed with exit code {result.returncode}, has_error: {has_error}, message: {error_message}")
                return error_response(500, f"命令执行失败: {error_message}")
        
    except subprocess.CalledProcessError as e:
        stderr = e.stderr or ""
        # 检查是否是设备断开连接导致的错误
        if "disconnected" in stderr.lower() or "offline" in stderr.lower():
            return error_response(500, "设备已断开连接")
        # 检查是否是找不到设备导致的错误
        elif "device not found" in stderr.lower() or "no devices/emulators found" in stderr.lower():
            return error_response(500, "找不到设备")
        # 其他错误返回简化的错误信息
        else:
            return error_response(500, "命令执行失败")
    except FileNotFoundError:
        return error_response(500, "执行命令失败: 找不到可执行文件")
    except Exception as e:
        error_str = str(e).lower()
        # 检查是否是设备断开连接导致的错误
        if "disconnected" in error_str or "offline" in error_str:
            return error_response(500, "设备已断开连接")
        elif "device not found" in error_str or "no devices/emulators found" in error_str:
            return error_response(500, "找不到设备")
        else:
            return error_response(500, "执行命令失败")