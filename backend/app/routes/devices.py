import subprocess
import os
import re
import shlex
import uuid
from datetime import datetime
from flask import Blueprint, request
from flask_login import login_required, current_user

from app.models.models import Device, db, TestTask
from app.utils.helpers import (
    success_response, error_response, get_pagination_params, log_user_action,
    validate_json_data
)
from app.utils.scheduler import add_scheduled_task, remove_scheduled_task, get_scheduled_tasks

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


@bp.route('/<device_id>/tasks', methods=['POST'])
@login_required
def execute_task(device_id):
    """执行测试任务"""
    data = request.get_json()

    task_type = data.get('task_type')  # 'shell', 'python', or 'install'
    command = data.get('command', '')
    file_path = data.get('file_path', '')
    file_content = data.get('file_content', '')

    try:
        # 计算项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

        if task_type == 'install' and (file_path or file_content):
            # 安装 APK
            adb_path = os.path.join(
                project_root,
                'escrcpy', 'electron', 'resources', 'extra', 'win', 'scrcpy', 'adb.exe'
            )

            # 构建环境变量
            env = os.environ.copy()
            env['ADB'] = adb_path

            # 如果有文件内容，先保存到临时文件
            if file_content:
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.apk', delete=False, encoding='utf-8') as f:
                    f.write(file_content)
                    file_path = f.name

            # 构建完整的命令
            command_parts = [adb_path, '-s', str(device_id), 'install', '-r', file_path]

            # 执行安装命令
            result = subprocess.run(
                command_parts,
                capture_output=True,
                text=True,
                check=False,
                env=env,
                encoding='utf-8',
                errors='ignore'
            )

            # 清理临时文件
            if file_content and os.path.exists(file_path):
                os.unlink(file_path)

            # 检查安装是否成功
            if result.returncode == 0:
                return success_response({
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'exit_code': result.returncode,
                    'message': '应用安装成功'
                })
            else:
                error_message = result.stderr or result.stdout or "应用安装失败"
                return error_response(500, f"应用安装失败: {error_message}")

        elif task_type == 'shell':
            # 执行 Shell 脚本
            adb_path = os.path.join(
                project_root,
                'escrcpy', 'electron', 'resources', 'extra', 'win', 'scrcpy', 'adb.exe'
            )

            # 构建环境变量
            env = os.environ.copy()
            env['ADB'] = adb_path

            if file_content:
                # 执行脚本内容
                command_parts = [adb_path, '-s', str(device_id), 'shell', file_content]
            elif file_path:
                # 执行脚本文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    script_content = f.read()
                command_parts = [adb_path, '-s', str(device_id), 'shell', script_content]
            elif command:
                # 执行命令
                command_parts = [adb_path, '-s', str(device_id), 'shell'] + command.split()
            else:
                return error_response(400, "请提供脚本文件或命令")

            # 执行 Shell 命令
            result = subprocess.run(
                command_parts,
                capture_output=True,
                text=True,
                check=False,
                env=env,
                encoding='utf-8',
                errors='ignore'
            )

            # 检查命令是否成功
            if result.returncode == 0:
                return success_response({
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'exit_code': result.returncode,
                    'message': '命令执行成功'
                })
            else:
                error_message = result.stderr or result.stdout or "命令执行失败"
                return error_response(500, f"命令执行失败: {error_message}")

        elif task_type == 'python':
            # 执行 Python 脚本（使用本地Python解释器）
            import tempfile
            import sys
            
            if file_content:
                # 执行 Python 脚本内容
                script_content = file_content
            elif file_path:
                # 执行 Python 脚本文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    script_content = f.read()
            else:
                # 直接执行 Python 命令
                script_content = command

            # 保存到临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(script_content)
                temp_script_path = f.name

            try:
                # 设置环境变量，传递设备ID
                env = os.environ.copy()
                env['DEVICE_ID'] = str(device_id)
                env['ADB_PATH'] = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                    'escrcpy', 'electron', 'resources', 'extra', 'win', 'scrcpy', 'adb.exe'
                )

                # 添加参数
                python_args = [temp_script_path]
                if command:
                    python_args.extend(command.split())

                # 使用字节流捕获输出，避免编码问题
                result = subprocess.run(
                    [sys.executable] + python_args,
                    capture_output=True,
                    check=False,
                    env=env
                )

                # 尝试多种编码方式解码输出
                def decode_output(data):
                    for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                        try:
                            return data.decode(encoding)
                        except (UnicodeDecodeError, LookupError):
                            continue
                    # 如果所有编码都失败，使用 replace 模式
                    return data.decode('utf-8', errors='replace')

                stdout = decode_output(result.stdout)
                stderr = decode_output(result.stderr)

                # 检查命令是否成功
                if result.returncode == 0:
                    return success_response({
                        'stdout': stdout,
                        'stderr': stderr,
                        'exit_code': result.returncode,
                        'message': 'Python 脚本执行成功'
                    })
                else:
                    error_message = stderr or stdout or "Python 脚本执行失败"
                    return error_response(500, f"Python 脚本执行失败: {error_message}")
            except Exception as e:
                # 清理临时文件
                if os.path.exists(temp_script_path):
                    os.unlink(temp_script_path)
                raise e
            finally:
                # 清理临时文件
                if os.path.exists(temp_script_path):
                    os.unlink(temp_script_path)

        else:
            return error_response(400, "不支持的任务类型")

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
            return error_response(500, "任务执行失败")
    except FileNotFoundError:
        return error_response(500, "执行任务失败: 找不到可执行文件")
    except Exception as e:
        error_str = str(e).lower()
        # 检查是否是设备断开连接导致的错误
        if "disconnected" in error_str or "offline" in error_str:
            return error_response(500, "设备已断开连接")
        elif "device not found" in error_str or "no devices/emulators found" in error_str:
            return error_response(500, "找不到设备")
        else:
            return error_response(500, "任务执行失败")


@bp.route('/batch-tasks', methods=['POST'])
@login_required
def execute_batch_tasks():
    """批量执行测试任务"""
    data = request.get_json()

    device_ids = data.get('device_ids', [])
    task_type = data.get('task_type', '')
    command = data.get('command', '')
    file_path = data.get('file_path', '')
    file_content = data.get('file_content', '')

    if not device_ids:
        return error_response(400, "请选择设备")

    results = []

    for device_id in device_ids:
        try:
            # 计算项目根目录路径
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

            if task_type == 'install' and (file_path or file_content):
                # 安装 APK
                adb_path = os.path.join(
                    project_root,
                    'escrcpy', 'electron', 'resources', 'extra', 'win', 'scrcpy', 'adb.exe'
                )

                # 构建环境变量
                env = os.environ.copy()
                env['ADB'] = adb_path

                # 如果有文件内容，先保存到临时文件
                if file_content:
                    import tempfile
                    import base64
                    # 解码base64数据
                    if file_content.startswith('data:application/vnd.android.package-archive;base64,'):
                        file_data = base64.b64decode(file_content.split(',')[1])
                        with tempfile.NamedTemporaryFile(mode='wb', suffix='.apk', delete=False) as f:
                            f.write(file_data)
                            file_path = f.name

                # 构建完整的命令
                command_parts = [adb_path, '-s', str(device_id), 'install', '-r', file_path]

                # 执行安装命令
                result = subprocess.run(
                    command_parts,
                    capture_output=True,
                    text=True,
                    check=False,
                    env=env,
                    encoding='utf-8',
                    errors='ignore'
                )

                # 清理临时文件
                if file_content and os.path.exists(file_path):
                    os.unlink(file_path)

                results.append({
                    'device_id': device_id,
                    'success': result.returncode == 0,
                    'message': '应用安装成功' if result.returncode == 0 else '应用安装失败',
                    'output': result.stdout or result.stderr
                })

            elif task_type == 'shell':
                # 执行 Shell 脚本
                adb_path = os.path.join(
                    project_root,
                    'escrcpy', 'electron', 'resources', 'extra', 'win', 'scrcpy', 'adb.exe'
                )

                # 构建环境变量
                env = os.environ.copy()
                env['ADB'] = adb_path

                if file_content:
                    # 执行脚本内容
                    command_parts = [adb_path, '-s', str(device_id), 'shell', file_content]
                elif file_path:
                    # 执行脚本文件
                    with open(file_path, 'r', encoding='utf-8') as f:
                        script_content = f.read()
                    command_parts = [adb_path, '-s', str(device_id), 'shell', script_content]
                elif command:
                    # 执行命令
                    command_parts = [adb_path, '-s', str(device_id), 'shell'] + command.split()
                else:
                    results.append({
                        'device_id': device_id,
                        'success': False,
                        'message': '请提供脚本文件或命令',
                        'output': ''
                    })
                    continue

                # 执行 Shell 命令
                result = subprocess.run(
                    command_parts,
                    capture_output=True,
                    text=True,
                    check=False,
                    env=env,
                    encoding='utf-8',
                    errors='ignore'
                )

                results.append({
                    'device_id': device_id,
                    'success': result.returncode == 0,
                    'message': '命令执行成功' if result.returncode == 0 else '命令执行失败',
                    'output': result.stdout or result.stderr
                })

            elif task_type == 'python':
                # 执行 Python 脚本（使用本地Python解释器）
                import tempfile
                import sys
                
                if file_content:
                    # 执行 Python 脚本内容
                    script_content = file_content
                elif file_path:
                    # 执行 Python 脚本文件
                    with open(file_path, 'r', encoding='utf-8') as f:
                        script_content = f.read()
                else:
                    # 直接执行 Python 命令
                    script_content = command

                # 保存到临时文件
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                    f.write(script_content)
                    temp_script_path = f.name

                try:
                    # 设置环境变量，传递设备ID
                    env = os.environ.copy()
                    env['DEVICE_ID'] = str(device_id)
                    env['ADB_PATH'] = os.path.join(
                        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                        'escrcpy', 'electron', 'resources', 'extra', 'win', 'scrcpy', 'adb.exe'
                    )

                    # 添加参数
                    python_args = [temp_script_path]
                    if command and not file_content and not file_path:
                        python_args.extend(command.split())

                    # 使用字节流捕获输出，避免编码问题
                    result = subprocess.run(
                        [sys.executable] + python_args,
                        capture_output=True,
                        check=False,
                        env=env
                    )

                    # 尝试多种编码方式解码输出
                    def decode_output(data):
                        for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                            try:
                                return data.decode(encoding)
                            except (UnicodeDecodeError, LookupError):
                                continue
                        return data.decode('utf-8', errors='replace')

                    stdout = decode_output(result.stdout)
                    stderr = decode_output(result.stderr)

                    results.append({
                        'device_id': device_id,
                        'success': result.returncode == 0,
                        'message': 'Python 脚本执行成功' if result.returncode == 0 else 'Python 脚本执行失败',
                        'output': stdout or stderr
                    })
                except Exception as e:
                    # 清理临时文件
                    if os.path.exists(temp_script_path):
                        os.unlink(temp_script_path)
                    results.append({
                        'device_id': device_id,
                        'success': False,
                        'message': f'任务执行失败: {str(e)}',
                        'output': ''
                    })
                finally:
                    # 清理临时文件
                    if os.path.exists(temp_script_path):
                        os.unlink(temp_script_path)

        except Exception as e:
            results.append({
                'device_id': device_id,
                'success': False,
                'message': f'任务执行失败: {str(e)}',
                'output': ''
            })

    return success_response({
        'results': results,
        'total': len(results),
        'success_count': sum(1 for r in results if r['success']),
        'failed_count': sum(1 for r in results if not r['success'])
    })


def execute_batch_task_wrapper(device_ids, task_type, command, file_path, file_content=None):
    """批量执行任务的包装函数，用于定时任务调用"""
    results = []

    for device_id in device_ids:
        try:
            # 计算项目根目录路径
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

            if task_type == 'install' and (file_path or file_content):
                # 安装 APK
                adb_path = os.path.join(
                    project_root,
                    'escrcpy', 'electron', 'resources', 'extra', 'win', 'scrcpy', 'adb.exe'
                )

                env = os.environ.copy()
                env['ADB'] = adb_path

                # 如果有文件内容，先保存到临时文件
                if file_content:
                    import tempfile
                    import base64
                    # 解码base64数据
                    if file_content.startswith('data:application/vnd.android.package-archive;base64,'):
                        file_data = base64.b64decode(file_content.split(',')[1])
                        with tempfile.NamedTemporaryFile(mode='wb', suffix='.apk', delete=False) as f:
                            f.write(file_data)
                            file_path = f.name

                command_parts = [adb_path, '-s', str(device_id), 'install', '-r', file_path]

                result = subprocess.run(
                    command_parts,
                    capture_output=True,
                    text=True,
                    check=False,
                    env=env,
                    encoding='utf-8',
                    errors='ignore'
                )

                # 清理临时文件
                if file_content and os.path.exists(file_path):
                    os.unlink(file_path)

                results.append({
                    'device_id': device_id,
                    'success': result.returncode == 0,
                    'message': '应用安装成功' if result.returncode == 0 else '应用安装失败',
                    'output': result.stdout or result.stderr
                })

            elif task_type == 'shell':
                # 执行 Shell 脚本
                adb_path = os.path.join(
                    project_root,
                    'escrcpy', 'electron', 'resources', 'extra', 'win', 'scrcpy', 'adb.exe'
                )

                env = os.environ.copy()
                env['ADB'] = adb_path

                if file_content:
                    # 执行脚本内容
                    command_parts = [adb_path, '-s', str(device_id), 'shell', file_content]
                elif file_path:
                    # 执行脚本文件
                    with open(file_path, 'r', encoding='utf-8') as f:
                        script_content = f.read()
                    command_parts = [adb_path, '-s', str(device_id), 'shell', script_content]
                elif command:
                    # 执行命令
                    command_parts = [adb_path, '-s', str(device_id), 'shell'] + command.split()
                else:
                    results.append({
                        'device_id': device_id,
                        'success': False,
                        'message': '请提供脚本文件或命令',
                        'output': ''
                    })
                    continue

                result = subprocess.run(
                    command_parts,
                    capture_output=True,
                    text=True,
                    check=False,
                    env=env,
                    encoding='utf-8',
                    errors='ignore'
                )

                results.append({
                    'device_id': device_id,
                    'success': result.returncode == 0,
                    'message': '命令执行成功' if result.returncode == 0 else '命令执行失败',
                    'output': result.stdout or result.stderr
                })

            elif task_type == 'python':
                # 执行 Python 脚本（使用本地Python解释器）
                import tempfile
                import sys
                
                if file_content:
                    # 执行 Python 脚本内容
                    script_content = file_content
                elif file_path:
                    # 执行 Python 脚本文件
                    with open(file_path, 'r', encoding='utf-8') as f:
                        script_content = f.read()
                else:
                    # 直接执行 Python 命令
                    script_content = command

                # 保存到临时文件
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                    f.write(script_content)
                    temp_script_path = f.name

                try:
                    # 设置环境变量，传递设备ID
                    env = os.environ.copy()
                    env['DEVICE_ID'] = str(device_id)
                    env['ADB_PATH'] = os.path.join(
                        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                        'escrcpy', 'electron', 'resources', 'extra', 'win', 'scrcpy', 'adb.exe'
                    )

                    # 添加参数
                    python_args = [temp_script_path]
                    if command and not file_content and not file_path:
                        python_args.extend(command.split())

                    # 使用字节流捕获输出，避免编码问题
                    result = subprocess.run(
                        [sys.executable] + python_args,
                        capture_output=True,
                        check=False,
                        env=env
                    )

                    # 尝试多种编码方式解码输出
                    def decode_output(data):
                        for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                            try:
                                return data.decode(encoding)
                            except (UnicodeDecodeError, LookupError):
                                continue
                        return data.decode('utf-8', errors='replace')

                    stdout = decode_output(result.stdout)
                    stderr = decode_output(result.stderr)

                    results.append({
                        'device_id': device_id,
                        'success': result.returncode == 0,
                        'message': 'Python 脚本执行成功' if result.returncode == 0 else 'Python 脚本执行失败',
                        'output': stdout or stderr
                    })
                finally:
                    # 清理临时文件
                    if os.path.exists(temp_script_path):
                        os.unlink(temp_script_path)

        except Exception as e:
            results.append({
                'device_id': device_id,
                'success': False,
                'message': f'任务执行失败: {str(e)}',
                'output': ''
            })

    return results


@bp.route('/schedule-batch-tasks', methods=['POST'])
@login_required
def schedule_batch_tasks():
    """定时批量执行测试任务"""
    data = request.get_json()

    device_ids = data.get('device_ids', [])
    task_type = data.get('task_type', '')
    command = data.get('command', '')
    file_path = data.get('file_path', '')
    script_file = data.get('script_file', '')
    file_hash = data.get('file_hash', '')
    file_content = data.get('file_content', '')
    scheduled_time_str = data.get('scheduled_time', '')

    if not device_ids:
        return error_response(400, "请选择设备")

    if not scheduled_time_str:
        return error_response(400, "请指定执行时间")

    try:
        # 解析执行时间
        scheduled_time = datetime.strptime(scheduled_time_str, '%Y-%m-%d %H:%M:%S')

        # 检查时间是否在未来
        if scheduled_time <= datetime.now():
            return error_response(400, "执行时间必须在未来")
        
        # 获取前端传递的任务名称，若无则生成默认名称
        task_name = data.get('task_name')
        if not task_name:
            task_name = f"设备脚本任务_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 获取前端传递的任务描述和优先级
        task_description = data.get('task_description', f"设备脚本任务，计划执行时间：{scheduled_time_str}")
        priority = data.get('priority', 'medium')
        
        # 创建设备脚本测试任务
        # 优先使用前端传递的script_file参数，否则从file_path中提取
        script_filename = script_file if script_file else (file_path.split('/')[-1] if file_path else '')
        
        test_task = TestTask(
            task_name=task_name,
            task_description=task_description,
            task_type='device_script',
            status='pending',
            priority=priority,
            creator_id=current_user.id,
            executor_id=current_user.id,  # 负责人自动设置为当前登录用户
            scheduled_time=scheduled_time,
            command=command,
            script_file=script_filename,
            file_path=file_path,
            file_hash=file_hash,
        )
        
        # 关联设备
        for device_id in device_ids:
            # 注意：前端传递的device_id实际上是设备序列号，不是数据库中的ID
            device = Device.query.filter_by(device_id=device_id).first()
            if device:
                test_task.devices.append(device)
            else:
                # 如果根据设备序列号查询不到，尝试根据数据库ID查询
                try:
                    device = Device.query.get(device_id)
                    if device:
                        test_task.devices.append(device)
                except:
                    pass
        
        db.session.add(test_task)
        db.session.commit()

        log_user_action("创建定时任务", f"测试任务ID: {test_task.id}, 执行时间: {scheduled_time_str}, 设备数量: {len(device_ids)}")

        return success_response({
            'task_id': test_task.id,
            'scheduled_time': scheduled_time_str,
            'device_count': len(device_ids)
        }, "定时任务创建成功")

    except ValueError as e:
        return error_response(400, "时间格式错误，请使用格式：YYYY-MM-DD HH:mm:ss")
    except Exception as e:
        db.session.rollback()
        return error_response(500, f"创建定时任务失败: {str(e)}")


