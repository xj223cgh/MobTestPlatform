# -*- coding: utf-8 -*-
"""Agent WebSocket 连接管理与请求转发：/agent 命名空间，后端向已连接 Agent 下发任务并等待响应"""
import uuid
import threading
from flask import current_app, request

# agent_uid -> sid（/agent 命名空间下）
_agent_sids = {}
_sid_to_agent_uid = {}
_lock = threading.Lock()

# request_id -> {'event': Event(), 'result': dict | None}
_pending = {}
_pending_lock = threading.Lock()


def get_agent_sid(agent_uid):
    """获取已连接 Agent 的 sid，未连接返回 None"""
    with _lock:
        return _agent_sids.get(agent_uid)


def request_agent(agent_uid, action, payload=None, timeout=15):
    """
    向指定 Agent 下发任务并等待响应。
    返回 (success: bool, data: dict)。
    success=False 时 data 可能含 error 信息；超时或未连接时 success=False。
    """
    sid = get_agent_sid(agent_uid)
    if not sid:
        return False, {'error': '本机 Agent 未连接'}
    req_id = str(uuid.uuid4())
    ev = threading.Event()
    with _pending_lock:
        _pending[req_id] = {'event': ev, 'result': None}
    try:
        sio = getattr(current_app, 'socketio', None)
        if not sio:
            return False, {'error': '服务不可用'}
        sio.emit('agent_request', {
            'request_id': req_id,
            'action': action,
            'payload': payload or {},
        }, room=sid, namespace='/agent')
        if not ev.wait(timeout=timeout):
            with _pending_lock:
                _pending.pop(req_id, None)
            return False, {'error': 'Agent 响应超时'}
        with _pending_lock:
            entry = _pending.pop(req_id, None)
        if not entry or not entry.get('result'):
            return False, {'error': '无响应'}
        res = entry['result']
        return res.get('success', False), res.get('data') or res
    except Exception as e:
        with _pending_lock:
            _pending.pop(req_id, None)
        return False, {'error': str(e)}


def register_agent_handlers(socketio):
    """注册 /agent 命名空间的 connect、disconnect、agent_response"""
    from app.models.models import Agent

    @socketio.on('connect', namespace='/agent')
    def agent_connect(auth=None):
        auth = auth or {}
        agent_uid = (auth.get('agent_uid') or '').strip()
        token = (auth.get('token') or '').strip()
        if not agent_uid or not token:
            current_app.logger.warning('Agent connect: missing agent_uid or token')
            return False
        with current_app.app_context():
            agent = Agent.query.filter_by(agent_uid=agent_uid, token=token).first()
        if not agent:
            current_app.logger.warning('Agent connect: invalid agent_uid or token')
            return False
        sid_val = request.sid
        with _lock:
            _agent_sids[agent_uid] = sid_val
            _sid_to_agent_uid[sid_val] = agent_uid
        current_app.logger.info('Agent connected: %s', agent_uid[:8])

    @socketio.on('disconnect', namespace='/agent')
    def agent_disconnect():
        sid_val = request.sid
        with _lock:
            agent_uid = _sid_to_agent_uid.pop(sid_val, None)
            if agent_uid:
                _agent_sids.pop(agent_uid, None)
        if agent_uid:
            current_app.logger.info('Agent disconnected: %s', agent_uid[:8])

    @socketio.on('agent_response', namespace='/agent')
    def on_agent_response(data):
        req_id = (data or {}).get('request_id')
        if not req_id:
            return
        with _pending_lock:
            entry = _pending.get(req_id)
        if entry:
            entry['result'] = data
            entry['event'].set()
