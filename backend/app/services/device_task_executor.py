"""
设备脚本/任务执行实现，供 HTTP 路由与后台异步任务共用。
需在 Flask 应用上下文中调用（如 with app.app_context():）。
"""
import os
import subprocess
import sys
import tempfile
from flask import current_app

from app.models.models import Device


def _get_project_root():
    """项目根目录（与 devices 路由一致）。"""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


def _resolve_device(device_id):
    """
    将 device_id（数据库主键或设备序列号）解析为 Device 实例。
    找不到时返回 None。
    """
    device = None
    try:
        if isinstance(device_id, int) or (isinstance(device_id, str) and device_id.isdigit()):
            device = Device.query.get(int(device_id))
        if not device:
            device = Device.query.filter_by(device_id=str(device_id).strip()).first()
    except (TypeError, ValueError):
        pass
    return device


def execute_device_task_impl(device_id, data):
    """
    在指定设备上执行任务（shell/python/install），不更新测试任务状态。
    供单设备 HTTP 接口与后台设备脚本任务调用。

    :param device_id: 设备主键 id 或设备序列号
    :param data: dict，需含 task_type；以及 command/file_path/script_file/file_content 等
    :return: dict with keys stdout, stderr, exit_code（成功时）
    :raises: Exception 失败时抛出，消息可供前端展示
    """
    device = _resolve_device(device_id)
    if not device:
        raise RuntimeError("设备不存在")

    task_type = data.get('task_type', 'shell')
    command = data.get('command', '')
    file_path = data.get('file_path', '')
    script_file = data.get('script_file', '')
    file_content = data.get('file_content', '')
    project_root = _get_project_root()
    script_storage = current_app.config.get('SCRIPT_STORAGE_PATH', '')
    # 与 devices 路由一致：file_path 为相对 SCRIPT_STORAGE_PATH 的路径
    rel_path = file_path or script_file or ''
    full_script_path = os.path.normpath(os.path.join(script_storage, rel_path)) if script_storage and rel_path else (file_path or '')

    adb_path = os.path.join(
        project_root,
        'escrcpy', 'electron', 'resources', 'extra', 'win', 'scrcpy', 'adb.exe'
    )
    env = os.environ.copy()
    env['ADB'] = adb_path

    if task_type == 'install' and (file_path or file_content):
        if file_content:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.apk', delete=False, encoding='utf-8') as f:
                f.write(file_content)
                file_path = f.name
        install_flags = []
        if data.get('install_replace', True):
            install_flags.append('-r')
        if data.get('install_downgrade', False):
            install_flags.append('-d')
        cmd = [adb_path, '-s', device.device_id, 'install'] + install_flags + [file_path]
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=False, env=env, encoding='utf-8', errors='ignore'
        )
        if file_content and os.path.exists(file_path):
            try:
                os.unlink(file_path)
            except OSError:
                pass
        if result.returncode != 0:
            raise RuntimeError(result.stderr or result.stdout or "应用安装失败")
        return {'stdout': result.stdout or '', 'stderr': result.stderr or '', 'exit_code': result.returncode}

    if task_type == 'shell':
        if file_content:
            command_parts = [adb_path, '-s', device.device_id, 'shell', file_content]
        elif full_script_path and os.path.isfile(full_script_path):
            with open(full_script_path, 'r', encoding='utf-8') as f:
                script_content = f.read()
            command_parts = [adb_path, '-s', device.device_id, 'shell', script_content]
        elif command:
            command_parts = [adb_path, '-s', device.device_id, 'shell'] + command.split()
        else:
            raise ValueError("请提供脚本文件或命令")
        result = subprocess.run(
            command_parts,
            capture_output=True,
            text=True,
            check=False,
            env=env,
            encoding='utf-8',
            errors='ignore'
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr or result.stdout or "命令执行失败")
        return {'stdout': result.stdout or '', 'stderr': result.stderr or '', 'exit_code': result.returncode}

    if task_type == 'python':
        if file_content:
            script_content = file_content
        elif full_script_path and os.path.isfile(full_script_path):
            with open(full_script_path, 'r', encoding='utf-8') as f:
                script_content = f.read()
        elif command:
            script_content = command
        else:
            raise ValueError("请提供 Python 脚本或命令")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(script_content)
            temp_script_path = f.name
        try:
            env['DEVICE_ID'] = device.device_id
            env['ADB_PATH'] = adb_path
            python_args = [temp_script_path]
            if command and not file_content and not (full_script_path and os.path.isfile(full_script_path)):
                python_args.extend(command.split())
            result = subprocess.run(
                [sys.executable] + python_args,
                capture_output=True,
                check=False,
                env=env
            )

            def decode_output(data):
                if data is None:
                    return ''
                for enc in ('utf-8', 'gbk', 'gb2312', 'latin-1'):
                    try:
                        return data.decode(enc)
                    except (UnicodeDecodeError, LookupError):
                        continue
                return data.decode('utf-8', errors='replace')

            stdout = decode_output(result.stdout)
            stderr = decode_output(result.stderr)
            if result.returncode != 0:
                raise RuntimeError(stderr or stdout or "Python 脚本执行失败")
            return {'stdout': stdout, 'stderr': stderr, 'exit_code': result.returncode}
        finally:
            if os.path.exists(temp_script_path):
                try:
                    os.unlink(temp_script_path)
                except OSError:
                    pass

    raise ValueError("不支持的任务类型: %s" % task_type)
