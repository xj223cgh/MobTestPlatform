# -*- coding: utf-8 -*-
"""
统一通知服务：先持久化，再向对应用户 WebSocket 房间推送。
业务侧只调用 notify_users，不直接操作 SocketIO；emit 失败只打日志，不阻塞业务。
"""
import logging
from typing import List, Optional

from app.models.models import db, Notification

logger = logging.getLogger(__name__)

# 时间范围约定（与 REST 一致）
TIME_RANGE_1D_HOURS = 24
TIME_RANGE_1W_DAYS = 7
TIME_RANGE_1M_DAYS = 30
TIME_RANGE_3M_DAYS = 90


def notify_users(
    user_ids: List[int],
    type: str,
    title: str,
    summary: str,
    related_type: Optional[str] = None,
    related_id: Optional[int] = None,
    extra: Optional[dict] = None,
    exclude_user_id: Optional[int] = None,
) -> List[int]:
    """
    为多个用户创建通知并实时推送。
    - 去重：排除 exclude_user_id（如当前操作者）；同一 user_id 只写一条。
    - 先写库，再对每个 user_id 向房间 user:{user_id} emit('notification', payload)。
    - emit 失败只打日志，不阻塞、不抛异常。
    返回：本次写入的通知 id 列表。
    """
    if not user_ids:
        return []
    seen = set()
    ids_to_notify = []
    for uid in user_ids:
        if uid is None:
            continue
        uid = int(uid)
        if exclude_user_id is not None and uid == int(exclude_user_id):
            continue
        if uid in seen:
            continue
        seen.add(uid)
        ids_to_notify.append(uid)

    if not ids_to_notify:
        return []

    created_ids = []
    try:
        for user_id in ids_to_notify:
            n = Notification(
                user_id=user_id,
                type=type,
                title=title,
                summary=summary or '',
                is_read=False,
                related_type=related_type,
                related_id=related_id,
                extra=extra,
            )
            db.session.add(n)
            db.session.flush()
            created_ids.append((user_id, n.id))

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.exception("通知写库失败: %s", e)
        return []

    # 实时推送：向每个用户房间 emit，失败只打日志
    for user_id, notification_id in created_ids:
        try:
            _emit_notification(
                user_id=user_id,
                notification_id=notification_id,
                type=type,
                related_type=related_type,
                related_id=related_id,
                extra=extra,
            )
        except Exception as e:
            logger.warning("推送通知到 user:%s 失败（不影响业务）: %s", user_id, e)

    return [nid for _, nid in created_ids]


def _emit_notification(
    user_id: int,
    notification_id: int,
    type: str,
    related_type: Optional[str] = None,
    related_id: Optional[int] = None,
    extra: Optional[dict] = None,
):
    """向房间 user:{user_id} 发送 notification 事件。无 socketio 时静默跳过。"""
    try:
        from flask import current_app
        sio = getattr(current_app, 'socketio', None)
        if sio is None:
            return
        payload = {
            'notification_id': notification_id,
            'type': type,
            'related_type': related_type,
            'related_id': related_id,
        }
        if extra:
            payload['extra'] = extra
        sio.emit('notification', payload, room=f'user:{user_id}')
    except Exception as e:
        logger.warning("emit notification 失败: %s", e)
        raise
