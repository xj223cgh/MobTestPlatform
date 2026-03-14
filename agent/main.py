# -*- coding: utf-8 -*-
"""
本机 Agent：在访问平台的电脑上运行，执行 adb/scrcpy，与后端 WebSocket 通信。
分发形态：打包为 MobTestAgent.exe（见 README 打包步骤），用户直接运行 exe 并绑定即可。
"""
import os
import re
import sys
import shlex
import socket
import shutil
import threading
import subprocess
import argparse
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None
try:
    import socketio
except ImportError:
    socketio = None

# 默认后端地址（可通过环境变量 AGENT_BASE_URL 或 --base-url 覆盖）
DEFAULT_BASE_URL = os.environ.get('AGENT_BASE_URL', 'http://127.0.0.1:5000')
# 心跳间隔（秒）
HEARTBEAT_INTERVAL = 25


def _exe_dir():
    """可执行文件所在目录（打包后为 exe 所在目录）。"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _bundled_bin_dir():
    """封装在一起的 adb/scrcpy 所在目录（打包后为 _MEIPASS/bin）。"""
    if getattr(sys, 'frozen', False):
        return os.path.join(getattr(sys, '_MEIPASS', ''), 'bin')
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin')


def find_adb():
    adb_env = os.environ.get('ADB_PATH') or os.environ.get('ADB')
    if adb_env and os.path.isfile(adb_env):
        return adb_env
    for exe_name in ('adb.exe', 'adb'):
        p = os.path.join(_bundled_bin_dir(), exe_name)
        if os.path.isfile(p):
            return p
    exe_dir = _exe_dir()
    for exe_name in ('adb.exe', 'adb'):
        p = os.path.join(exe_dir, exe_name)
        if os.path.isfile(p):
            return p
    return shutil.which('adb') or 'adb'


def find_scrcpy():
    scrcpy_env = os.environ.get('SCRCPY_PATH') or os.environ.get('SCRCPY')
    if scrcpy_env and os.path.isfile(scrcpy_env):
        return scrcpy_env
    for exe_name in ('scrcpy.exe', 'scrcpy'):
        p = os.path.join(_bundled_bin_dir(), exe_name)
        if os.path.isfile(p):
            return p
    exe_dir = _exe_dir()
    for exe_name in ('scrcpy.exe', 'scrcpy'):
        p = os.path.join(exe_dir, exe_name)
        if os.path.isfile(p):
            return p
    return shutil.which('scrcpy') or 'scrcpy'


def run_adb(adb_path, args, timeout=15, env=None):
    cmd = [adb_path] + (args if isinstance(args, list) else args.split())
    env = env or os.environ.copy()
    env['ADB'] = adb_path
    r = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        encoding='utf-8',
        errors='replace',
        env=env,
    )
    return r.returncode, r.stdout or '', r.stderr or ''


def parse_devices_output(stdout):
    devices = []
    lines = (stdout or '').strip().split('\n')[1:]
    for line in lines:
        if not line.strip():
            continue
        m = re.match(r'(\S+)\s+(device|unauthorized|offline)(.*)', line)
        if m:
            serial, status, info = m.group(1), m.group(2), m.group(3).strip()
            dev = {'id': serial, 'status': status, 'name': '', 'wifi': False, 'remark': ''}
            if ':' in serial and not serial.startswith('emulator-'):
                dev['wifi'] = True
            model = re.search(r'model:(\S+)', info)
            if model:
                dev['name'] = model.group(1)
            devices.append(dev)
    return devices


def do_get_devices(adb_path):
    code, out, err = run_adb(adb_path, ['devices', '-l'], timeout=10)
    if code != 0:
        return False, {'error': err or out or 'adb devices 执行失败'}
    return True, {'devices': parse_devices_output(out)}


def do_get_device_status(adb_path, device_id):
    code, out, err = run_adb(adb_path, ['-s', device_id, 'get-state'], timeout=5)
    adb_status = (out or '').strip()
    if code == 0 and adb_status == 'device':
        return True, {'status': 'connected', 'adb_status': adb_status}
    return True, {'status': 'disconnected', 'adb_status': adb_status, 'error': err or out}


def do_adb_command(adb_path, scrcpy_path, command, timeout=15):
    cmd = (command or '').strip()
    if not cmd:
        return False, {'error': '命令为空'}
    if cmd.startswith('scrcpy'):
        parts = shlex.split(cmd)
        scrcpy_cmd = [scrcpy_path] + parts[1:]
        env = os.environ.copy()
        env['ADB'] = adb_path
        try:
            popen_kw = {'stdout': subprocess.DEVNULL, 'stderr': subprocess.DEVNULL, 'env': env}
            if hasattr(subprocess, 'CREATE_NEW_PROCESS_GROUP'):
                popen_kw['creationflags'] = subprocess.CREATE_NEW_PROCESS_GROUP
            subprocess.Popen(scrcpy_cmd, **popen_kw)
            return True, {'message': '投屏已启动', 'command': scrcpy_cmd}
        except Exception as e:
            return False, {'error': str(e)}
    parts = shlex.split(cmd)
    code, out, err = run_adb(adb_path, parts, timeout=timeout)
    error_keywords = [
        'cannot connect', 'unable to connect', 'no devices/emulators found',
        'device not found', 'offline', 'disconnected',
    ]
    out_lower = (out or '').lower()
    has_err = any(k in out_lower for k in error_keywords)
    if code == 0 and not has_err:
        return True, {'stdout': out, 'stderr': err, 'exit_code': code, 'command': [adb_path] + parts}
    return False, {'stdout': out, 'stderr': err, 'exit_code': code, 'error': err or out or '执行失败'}


def register_agent(base_url, name=None, hostname=None):
    if not requests:
        raise RuntimeError('需要安装 requests: pip install requests')
    url = base_url.rstrip('/') + '/api/agent/register'
    data = {}
    if name:
        data['name'] = name
    if hostname:
        data['hostname'] = hostname or socket.gethostname()
    r = requests.post(url, json=data, timeout=10)
    r.raise_for_status()
    body = r.json()
    if body.get('code') != 200:
        raise RuntimeError(body.get('message', '注册失败'))
    return body.get('data', {})


def heartbeat_agent(base_url, token):
    if not requests:
        return
    url = base_url.rstrip('/') + '/api/agent/heartbeat'
    try:
        requests.post(url, json={'token': token}, headers={'X-Agent-Token': token}, timeout=5)
    except Exception:
        pass


def bind_agent(base_url, token, code=None, binding_token=None):
    if not requests:
        raise RuntimeError('需要安装 requests: pip install requests')
    url = base_url.rstrip('/') + '/api/agent/bind'
    payload = {'token': token}
    if binding_token:
        payload['binding_token'] = binding_token
    else:
        payload['code'] = code
    r = requests.post(
        url,
        json=payload,
        headers={'X-Agent-Token': token},
        timeout=10,
    )
    r.raise_for_status()
    body = r.json()
    if body.get('code') != 200:
        raise RuntimeError(body.get('message', '绑定失败'))
    return body.get('data', {})


# 本机一键绑定服务端口（前端请求此端口完成绑定、检测运行状态）
AGENT_BIND_PORT = int(os.environ.get('AGENT_BIND_PORT', '8765'))


def _agent_local_status_url():
    return f'http://127.0.0.1:{AGENT_BIND_PORT}/status'


def check_agent_already_running():
    """若本机已有 Agent 在运行（8765 可访问），返回 True"""
    if not requests:
        return False
    try:
        r = requests.get(_agent_local_status_url(), timeout=2)
        if r.status_code == 200 and (r.json() or {}).get('status') == 'ok':
            return True
    except Exception:
        pass
    return False


def _register_protocol_windows():
    """Windows：注册 mobtestagent:// 协议，供浏览器「启动 Agent」一键拉起本程序（仅打包为 exe 时生效）"""
    if sys.platform != 'win32' or not getattr(sys, 'frozen', False):
        return
    try:
        import winreg
        exe = os.path.abspath(sys.executable)
        key = winreg.CreateKey(
            winreg.HKEY_CURRENT_USER,
            r'Software\Classes\mobtestagent',
        )
        winreg.SetValue(key, '', winreg.REG_SZ, 'URL:MobTest Agent')
        winreg.SetValueEx(key, 'URL Protocol', 0, winreg.REG_SZ, '')
        winreg.CloseKey(key)
        cmd_key = winreg.CreateKey(
            winreg.HKEY_CURRENT_USER,
            r'Software\Classes\mobtestagent\shell\open\command',
        )
        winreg.SetValue(cmd_key, '', winreg.REG_SZ, f'"{exe}" "%1"')
        winreg.CloseKey(cmd_key)
    except Exception:
        pass


def _unregister_protocol_windows():
    """Windows：删除 mobtestagent:// 协议注册，用于不再使用平台时的清理（仅打包为 exe 时生效）"""
    if sys.platform != 'win32' or not getattr(sys, 'frozen', False):
        return
    try:
        import winreg
        for sub in (r'Software\Classes\mobtestagent\shell\open\command',
                    r'Software\Classes\mobtestagent\shell\open',
                    r'Software\Classes\mobtestagent\shell',
                    r'Software\Classes\mobtestagent'):
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, sub)
            except FileNotFoundError:
                pass
        print('已移除「启动 Agent」协议注册。')
    except Exception as e:
        print('移除协议注册时出错:', e)


def do_clean_local():
    """一键清理本机 Agent 相关数据：协议注册（Windows）+ 本地配置文件。不再使用平台时执行一次即可。"""
    print('正在清理本机 Agent 数据…')
    # 1. Windows 下移除协议注册
    _unregister_protocol_windows()
    # 2. 删除 exe 同目录下的 agent_config.txt
    config_path = Path(_exe_dir()) / 'agent_config.txt'
    if config_path.exists():
        try:
            config_path.unlink()
            print('已删除本地配置文件 agent_config.txt。')
        except Exception as e:
            print('删除配置文件时出错:', e)
    else:
        print('未发现本地配置文件。')
    print('清理完成。本机已无 Agent 相关数据；若需再用，重新运行本程序并绑定即可。')


def _run_bind_server(base_url, agent_token):
    """在 127.0.0.1:AGENT_BIND_PORT 提供 GET /bind?token=xxx，供平台前端一键绑定"""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from urllib.parse import urlparse, parse_qs

    class BindHandler(BaseHTTPRequestHandler):
        def _send_cors_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')

        def do_OPTIONS(self):
            """支持 CORS 预检，避免浏览器拦截跨域请求（localhost 页请求 127.0.0.1:8765）"""
            self.send_response(204)
            self._send_cors_headers()
            self.end_headers()

        def do_GET(self):
            import json
            parsed = urlparse(self.path)
            path = (parsed.path or '/').rstrip('/') or '/'
            # 供前端检测本机 Agent 是否在运行
            if path == '/' or path == '/status':
                self._send(200, {'status': 'ok', 'service': 'MobTestAgent'})
                return
            # 供平台「清理本机 Agent」入口触发：执行清理后退出进程
            if path == '/clean':
                do_clean_local()
                self._send(200, {'success': True, 'message': '已清理'})
                try:
                    self.wfile.flush()
                except Exception:
                    pass
                threading.Timer(1.0, lambda: os._exit(0)).start()
                return
            if path != '/bind':
                self._send(404, {'success': False, 'error': 'Not Found'})
                return
            qs = parse_qs(parsed.query)
            token = (qs.get('token') or [''])[0].strip()
            if not token:
                self._send(400, {'success': False, 'error': '缺少 token'})
                return
            try:
                bind_agent(base_url, agent_token, binding_token=token)
                self._send(200, {'success': True, 'message': '绑定成功'})
            except Exception as e:
                self._send(200, {'success': False, 'error': str(e)})

        def _send(self, status, data):
            import json
            body = json.dumps(data, ensure_ascii=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', len(body))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            pass

    try:
        server = HTTPServer(('127.0.0.1', AGENT_BIND_PORT), BindHandler)
        server.serve_forever()
    except Exception:
        pass

def start_bind_server_thread(base_url, agent_token):
    t = threading.Thread(
        target=_run_bind_server,
        args=(base_url, agent_token),
        daemon=True,
    )
    t.start()


def run_agent(base_url, agent_uid, token):
    if not socketio:
        raise RuntimeError('需要安装 python-socketio[client]: pip install "python-socketio[client]"')

    start_bind_server_thread(base_url, token)

    adb_path = find_adb()
    scrcpy_path = find_scrcpy()
    ws_url = base_url.rstrip('/').replace('http://', 'ws://').replace('https://', 'wss://')

    sio = socketio.Client()

    def on_connect():
        print('已连接平台，等待任务…')

    def on_disconnect():
        print('与平台连接断开')

    @sio.on('agent_request', namespace='/agent')
    def on_request(data):
        req_id = (data or {}).get('request_id')
        action = (data or {}).get('action')
        payload = (data or {}).get('payload') or {}
        if not req_id:
            return
        success, result = False, {}
        try:
            if action == 'get_devices':
                success, result = do_get_devices(adb_path)
            elif action == 'get_device_status':
                success, result = do_get_device_status(adb_path, payload.get('device_id', ''))
            elif action == 'adb_command':
                success, result = do_adb_command(
                    adb_path, scrcpy_path,
                    payload.get('command', ''),
                    timeout=payload.get('timeout', 15),
                )
            else:
                result = {'error': f'未知操作: {action}'}
        except Exception as e:
            result = {'error': str(e)}
        sio.emit('agent_response', {
            'request_id': req_id,
            'success': success,
            'data': result,
        }, namespace='/agent')

    sio.on('connect', on_connect, namespace='/agent')
    sio.on('disconnect', on_disconnect, namespace='/agent')

    stop_heartbeat = threading.Event()

    def heartbeat_loop():
        while not stop_heartbeat.wait(HEARTBEAT_INTERVAL):
            heartbeat_agent(base_url, token)

    t = threading.Thread(target=heartbeat_loop, daemon=True)
    t.start()

    try:
        sio.connect(
            ws_url,
            namespaces=['/agent'],
            auth={'agent_uid': agent_uid, 'token': token},
            wait_timeout=10,
        )
        sio.wait()
    except KeyboardInterrupt:
        pass
    finally:
        stop_heartbeat.set()


def _pause_if_frozen():
    """Windows 下以 exe 运行时，出错后暂停以便查看输出，避免窗口一闪而过"""
    if sys.platform == 'win32' and getattr(sys, 'frozen', False):
        try:
            input('\n按回车键退出...')
        except Exception:
            pass


def _err_exit(msg, code=1):
    """打印错误并退出；exe 运行时先暂停以便用户看到"""
    print(msg)
    _pause_if_frozen()
    sys.exit(code)


def main():
    parser = argparse.ArgumentParser(description='移动测试平台 - 本机 Agent')
    parser.add_argument('--base-url', default=DEFAULT_BASE_URL, help='平台后端地址')
    parser.add_argument('--bind-code', type=str, help='绑定码（6 位），从平台「绑定本机」获取')
    parser.add_argument('--name', type=str, help='本机名称（可选）')
    parser.add_argument('--unregister-protocol', action='store_true',
                        help='仅移除 Windows 下「启动 Agent」协议注册后退出')
    parser.add_argument('--clean', action='store_true',
                        help='一键清理：移除协议注册（Windows）并删除本地配置文件后退出，不再使用平台时使用')
    args = parser.parse_args()

    if getattr(args, 'unregister_protocol', False):
        _unregister_protocol_windows()
        sys.exit(0)
    if getattr(args, 'clean', False):
        do_clean_local()
        sys.exit(0)

    base_url = args.base_url.rstrip('/')

    if not requests or not socketio:
        _err_exit('请安装依赖: pip install requests "python-socketio[client]"', 1)

    # 若存在本地配置文件则读取 agent_uid 与 token（可选实现）
    config_path = Path(_exe_dir()) / 'agent_config.txt'
    agent_uid, token = None, None
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('agent_uid='):
                        agent_uid = line.split('=', 1)[1].strip()
                    elif line.startswith('token='):
                        token = line.split('=', 1)[1].strip()
        except Exception:
            pass

    if not agent_uid or not token:
        print('首次运行，正在注册…')
        try:
            data = register_agent(base_url, name=args.name, hostname=socket.gethostname())
        except Exception as e:
            err_msg = str(e)
            if '10061' in err_msg or 'ConnectionRefusedError' in err_msg or 'ConnectionError' in err_msg or 'Failed to establish' in err_msg:
                print('无法连接到平台（连接被拒绝）。')
                if '127.0.0.1' in base_url or 'localhost' in base_url:
                    print('您可能是在其他电脑运行 Agent，请指定平台地址后再运行，例如：')
                    print('  MobTestAgent.exe --base-url http://服务器IP:5000')
                    print('（将 服务器IP 替换为部署平台的电脑在内网的 IP，如 192.168.1.100）')
            raise
        agent_uid = data.get('agent_uid')
        token = data.get('token')
        if not agent_uid or not token:
            _err_exit('注册失败', 1)
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(f'agent_uid={agent_uid}\ntoken={token}\n')
        except Exception:
            pass
        print(f'注册成功。agent_uid: {agent_uid[:8]}...')

    if args.bind_code:
        print('正在绑定…')
        try:
            bind_agent(base_url, token, code=args.bind_code.strip())
            print('绑定成功')
        except Exception as e:
            _err_exit(f'绑定失败: {e}', 1)

    # 单实例：若本机已有 Agent 在运行，不再启动（便于浏览器「启动 Agent」不重复开窗口）
    if check_agent_already_running():
        print('本机 Agent 已在运行，无需重复启动。')
        _pause_if_frozen()
        sys.exit(0)

    # Windows 下注册 mobtestagent://，便于平台页「启动 Agent」一键拉起
    _register_protocol_windows()

    print('启动 Agent，连接平台…')
    try:
        run_agent(base_url, agent_uid, token)
    except Exception as e:
        import traceback
        print('运行出错:', e)
        traceback.print_exc()
        _err_exit('', 1)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        import traceback
        print('启动出错:', e)
        traceback.print_exc()
        _pause_if_frozen()
        sys.exit(1)
