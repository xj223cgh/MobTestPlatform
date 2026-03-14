# -*- coding: utf-8 -*-
"""本机 Agent 相关接口：注册、心跳、绑定、绑定码、解绑、平台启动 Agent"""
import os
import secrets
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone, timedelta
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

from flask import Blueprint, request, current_app, send_file
from flask_login import login_required, current_user

from app.models.models import db, Agent, UserAgentBinding, AgentBindingCode
from app.utils.helpers import success_response, error_response
from app.utils.request_helpers import is_platform_host

bp = Blueprint('agent', __name__, url_prefix='/api/agent')

# 绑定码有效时间（分钟）
BINDING_CODE_EXPIRE_MINUTES = 5
# 本机 Agent 本地服务端口（与 agent/main.py 中 AGENT_BIND_PORT 一致）
AGENT_LOCAL_PORT = 8765


def _agent_from_request():
    """从请求头 X-Agent-Token 或 body 中校验并返回 Agent，未认证返回 None"""
    token = request.headers.get('X-Agent-Token') or (request.get_json(silent=True) or {}).get('token')
    if not token:
        return None
    return Agent.query.filter_by(token=token).first()


@bp.route('/register', methods=['POST'])
def register():
    """Agent 注册：创建设备代理记录，返回 agent_uid 与 token（仅 Agent 调用）"""
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip() or None
    hostname = (data.get('hostname') or '').strip() or None

    agent_uid = str(uuid.uuid4())
    token = secrets.token_urlsafe(32)

    agent = Agent(
        agent_uid=agent_uid,
        name=name,
        hostname=hostname,
        token=token,
        last_heartbeat_at=datetime.now(timezone(timedelta(hours=8))),
    )
    db.session.add(agent)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return error_response(500, "注册失败")
    return success_response({
        'agent_uid': agent_uid,
        'token': token,
        'agent_id': agent.id,
    })


@bp.route('/heartbeat', methods=['POST'])
def heartbeat():
    """Agent 心跳：更新 last_heartbeat_at（需 X-Agent-Token 或 body.token）"""
    agent = _agent_from_request()
    if not agent:
        return error_response(401, "未授权")
    agent.last_heartbeat_at = datetime.now(timezone(timedelta(hours=8)))
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return error_response(500, "心跳更新失败")
    return success_response({'ok': True})


@bp.route('/bind', methods=['POST'])
def bind():
    """Agent 端绑定：用绑定码或 binding_token 将当前用户与该 Agent 绑定（需 Agent token + body.code 或 binding_token）"""
    agent = _agent_from_request()
    if not agent:
        return error_response(401, "未授权")
    data = request.get_json(silent=True) or {}
    code = (data.get('code') or '').strip()
    binding_token = (data.get('binding_token') or '').strip()
    if not code and not binding_token:
        return error_response(400, "缺少绑定码或 binding_token")

    now = datetime.now(timezone(timedelta(hours=8)))
    if binding_token:
        binding_code = AgentBindingCode.query.filter_by(binding_token=binding_token).filter(AgentBindingCode.expires_at > now).first()
    else:
        binding_code = AgentBindingCode.query.filter_by(code=code).filter(AgentBindingCode.expires_at > now).first()
    if not binding_code:
        return error_response(400, "绑定码无效或已过期")

    user_id = binding_code.user_id
    # 同一用户已有绑定则更新为当前 Agent
    existing = UserAgentBinding.query.filter_by(user_id=user_id).first()
    if existing:
        existing.agent_id = agent.id
        existing.bound_at = now
    else:
        db.session.add(UserAgentBinding(user_id=user_id, agent_id=agent.id))

    db.session.delete(binding_code)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return error_response(500, "绑定失败")
    return success_response({'message': '绑定成功', 'user_id': user_id})


@bp.route('/binding', methods=['GET'])
@login_required
def get_binding():
    """获取当前用户的 Agent 绑定状态（含是否在线）"""
    try:
        binding = UserAgentBinding.query.filter_by(user_id=current_user.id).first()
        if not binding:
            return success_response({'bound': False, 'binding': None})

        agent = binding.agent
        if not agent:
            return success_response({'bound': False, 'binding': None})

        # 约 45 秒内心跳视为在线，便于关闭 Agent 后状态较快更新（统一为 timezone-aware 再比较）
        tz8 = timezone(timedelta(hours=8))
        now = datetime.now(tz8)
        online = False
        if agent.last_heartbeat_at:
            hb = agent.last_heartbeat_at
            if hb.tzinfo is None:
                hb = hb.replace(tzinfo=tz8)
            threshold = hb + timedelta(seconds=45)
            online = now <= threshold

        return success_response({
            'bound': True,
            'binding': binding.to_dict(),
            'agent_online': online,
        })
    except Exception as e:
        current_app.logger.exception('get_binding error: %s', e)
        return success_response({'bound': False, 'binding': None})


def _do_create_binding_code():
    """执行创建绑定码的数据库操作（内层，便于死锁重试）"""
    code = ''.join(secrets.choice('0123456789') for _ in range(6))
    binding_token = secrets.token_urlsafe(32)
    now = datetime.now(timezone(timedelta(hours=8)))
    expires_at = now + timedelta(minutes=BINDING_CODE_EXPIRE_MINUTES)
    AgentBindingCode.query.filter_by(user_id=current_user.id).delete()
    binding_code = AgentBindingCode(
        user_id=current_user.id,
        code=code,
        binding_token=binding_token,
        expires_at=expires_at,
    )
    db.session.add(binding_code)
    db.session.commit()
    return code, binding_token, binding_code


@bp.route('/binding-code', methods=['POST'])
@login_required
def create_binding_code():
    """生成短期绑定码与 binding_token，供本机一键绑定或手动输入完成绑定"""
    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            code, binding_token, binding_code = _do_create_binding_code()
            return success_response({
                'code': code,
                'binding_token': binding_token,
                'expires_at': binding_code.expires_at.isoformat(),
                'expires_in_seconds': BINDING_CODE_EXPIRE_MINUTES * 60,
            })
        except Exception as e:
            db.session.rollback()
            err_orig = getattr(e, 'orig', e)
            is_deadlock = getattr(err_orig, 'args', None) and len(err_orig.args) > 0 and err_orig.args[0] == 1213
            if is_deadlock and attempt < max_retries:
                current_app.logger.warning('create_binding_code deadlock, retry %s', attempt + 1)
                continue
            current_app.logger.exception('create_binding_code error: %s', e)
            return error_response(500, "生成绑定码失败，请检查数据库是否已创建 agent_binding_codes 表")


def _agent_exe_available():
    """检查是否配置了可用的 Agent 安装包路径"""
    path = current_app.config.get('AGENT_EXE_PATH')
    return path and os.path.isfile(path)


def _check_agent_local_running(timeout=2):
    """检测本机 127.0.0.1:8765 是否有 Agent 在运行"""
    try:
        req = urlopen(Request('http://127.0.0.1:%s/status' % AGENT_LOCAL_PORT), timeout=timeout)
        if req.status == 200:
            import json
            data = json.loads(req.read().decode('utf-8'))
            return data.get('status') == 'ok'
    except (URLError, HTTPError, OSError, ValueError):
        pass
    return False


def _request_local_bind(binding_token, timeout=5):
    """请求本机 Agent 8765 完成绑定，返回 (success, message)"""
    try:
        from urllib.parse import quote
        url = 'http://127.0.0.1:%s/bind?token=%s' % (AGENT_LOCAL_PORT, quote(binding_token, safe=''))
        req = urlopen(Request(url), timeout=timeout)
        if req.status == 200:
            import json
            data = json.loads(req.read().decode('utf-8'))
            return bool(data.get('success')), data.get('error') or data.get('message') or ''
    except Exception as e:
        return False, str(e)
    return False, 'unknown'


@bp.route('/launch-info', methods=['GET'])
@login_required
def launch_info():
    """返回是否支持「平台启动 Agent」、当前是否本机、以及供展示的平台地址（.env 配置）"""
    is_host = is_platform_host()
    # 平台地址：请求时从环境变量读取，确保 .env 修改后生效（重启后端后）
    platform_base_url = (os.environ.get('AGENT_PLATFORM_BASE_URL') or '').strip()
    if not platform_base_url:
        platform_base_url = (current_app.config.get('AGENT_PLATFORM_BASE_URL') or '') if isinstance(current_app.config.get('AGENT_PLATFORM_BASE_URL'), str) else ''
    platform_base_url = (platform_base_url or '').strip()
    if not _agent_exe_available():
        return success_response({
            'can_launch': False,
            'is_platform_host': is_host,
            'platform_base_url': platform_base_url,
            'message': '未配置 Agent 可执行文件，无法由平台启动',
        })
    return success_response({
        'can_launch': True,
        'is_platform_host': is_host,
        'platform_base_url': platform_base_url,
        'message': '可由平台在服务器本机启动 Agent 并自动绑定当前用户',
    })


@bp.route('/launch', methods=['POST'])
@login_required
def launch():
    """在服务器本机启动 Agent（若未运行）并自动绑定当前用户。适用于平台与 Agent 同机部署。"""
    if not _agent_exe_available():
        return error_response(400, '未配置 Agent 可执行文件，无法由平台启动')
    exe_path = current_app.config.get('AGENT_EXE_PATH')
    exe_dir = os.path.dirname(os.path.abspath(exe_path))
    base_url = (request.url_root or '').rstrip('/') or 'http://127.0.0.1:5000'
    if not base_url.startswith('http'):
        base_url = 'http://' + (request.host or '127.0.0.1:5000')
    already_running = _check_agent_local_running()
    if not already_running:
        env = os.environ.copy()
        env['AGENT_BASE_URL'] = base_url
        try:
            if sys.platform == 'win32':
                subprocess.Popen(
                    [exe_path, '--base-url', base_url],
                    cwd=exe_dir,
                    env=env,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if hasattr(subprocess, 'CREATE_NEW_PROCESS_GROUP') else 0,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                subprocess.Popen(
                    [exe_path, '--base-url', base_url],
                    cwd=exe_dir,
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
        except Exception as e:
            current_app.logger.exception('launch agent error: %s', e)
            return error_response(500, '启动 Agent 失败：%s' % str(e))
        for _ in range(15):
            time.sleep(1)
            if _check_agent_local_running(timeout=3):
                break
        else:
            return error_response(504, 'Agent 已启动但未在约定时间内就绪，请稍后在「本机 Agent」中点击绑定本机')
    try:
        code, binding_token, _ = _do_create_binding_code()
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception('launch create_binding_code error: %s', e)
        return error_response(500, '生成绑定码失败')
    ok, msg = _request_local_bind(binding_token)
    if not ok:
        return error_response(500, '绑定失败：%s' % (msg or '本机 Agent 未响应'))
    return success_response({
        'success': True,
        'already_running': already_running,
        'bound': True,
        'message': 'Agent 已启动并已绑定当前用户' if not already_running else 'Agent 已在运行，已绑定当前用户',
    })


@bp.route('/download-info', methods=['GET'])
@login_required
def download_info():
    """查询当前是否支持下载 Agent 安装包（下载路径可选，未配置则不可用）"""
    if not _agent_exe_available():
        return success_response({'available': False})
    path = current_app.config.get('AGENT_EXE_PATH')
    return success_response({
        'available': True,
        'filename': os.path.basename(path),
    })


@bp.route('/download', methods=['GET'])
@login_required
def download_agent():
    """下载本机 Agent 安装包，需登录；仅当配置了 AGENT_EXE_PATH 且文件存在时可用"""
    if not _agent_exe_available():
        return error_response(404, "Agent 安装包暂不可用，请联系管理员")
    path = current_app.config.get('AGENT_EXE_PATH')
    return send_file(
        path,
        as_attachment=True,
        download_name=os.path.basename(path),
        mimetype='application/octet-stream',
    )


@bp.route('/unbind', methods=['POST'])
@login_required
def unbind():
    """解除当前用户与本机 Agent 的绑定"""
    binding = UserAgentBinding.query.filter_by(user_id=current_user.id).first()
    if not binding:
        return success_response({'message': '当前未绑定'})
    try:
        db.session.delete(binding)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return error_response(500, "解绑失败")
    return success_response({'message': '已解绑'})
