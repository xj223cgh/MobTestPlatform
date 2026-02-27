# -*- coding: utf-8 -*-
"""消息通知 REST API：列表、未读数、已读、按时间范围清理已读"""
from datetime import datetime, timedelta, timezone

from flask import Blueprint, request
from flask_login import login_required, current_user

from app.models.models import db, Notification
from app.utils.helpers import success_response, error_response, get_pagination_params
from app.services.notification_service import (
    TIME_RANGE_1D_HOURS,
    TIME_RANGE_1W_DAYS,
    TIME_RANGE_1M_DAYS,
    TIME_RANGE_3M_DAYS,
)

LOCAL_TZ = timezone(timedelta(hours=8))

bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')

# 时间范围合法值
TIME_RANGE_VALUES = ('1d', '1w', '1m', '3m', 'older')


def _time_range_bounds(time_range: str):
    """
    返回 (start, end) 或 (None, end) 表示 created_at 应满足的区间。
    - 1d: 过去 24 小时
    - 1w: 过去 7 天
    - 1m: 过去 30 天
    - 3m: 过去 90 天
    - older: created_at 早于 90 天前（只返回 end 边界，start 无限制）
    """
    now = datetime.now(LOCAL_TZ)
    if time_range == '1d':
        start = now - timedelta(hours=TIME_RANGE_1D_HOURS)
        return start, now
    if time_range == '1w':
        start = now - timedelta(days=TIME_RANGE_1W_DAYS)
        return start, now
    if time_range == '1m':
        start = now - timedelta(days=TIME_RANGE_1M_DAYS)
        return start, now
    if time_range == '3m':
        start = now - timedelta(days=TIME_RANGE_3M_DAYS)
        return start, now
    if time_range == 'older':
        end = now - timedelta(days=TIME_RANGE_3M_DAYS)
        return None, end
    return None, None


@bp.route('', methods=['GET'])
@login_required
def list_notifications():
    """GET /api/notifications：分页列表，支持 type、is_read、time_range"""
    try:
        page, per_page = get_pagination_params()
        ntype = request.args.get('type', '').strip()
        is_read_param = request.args.get('is_read')
        time_range = request.args.get('time_range', '').strip() or None

        query = Notification.query.filter_by(user_id=current_user.id).filter(Notification.deleted_at.is_(None))

        if ntype:
            query = query.filter_by(type=ntype)
        if is_read_param is not None and is_read_param != '':
            is_read = str(is_read_param).lower() in ('true', '1', 'yes')
            query = query.filter_by(is_read=is_read)
        if time_range and time_range in TIME_RANGE_VALUES:
            start, end = _time_range_bounds(time_range)
            if start is not None:
                query = query.filter(Notification.created_at >= start, Notification.created_at <= end)
            else:
                query = query.filter(Notification.created_at < end)

        query = query.order_by(Notification.is_pinned.desc(), Notification.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        items = [n.to_dict() for n in pagination.items]

        return success_response({
            'items': items,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages,
        })
    except Exception as e:
        return error_response(500, str(e))


@bp.route('/unread-count', methods=['GET'])
@login_required
def unread_count():
    """GET /api/notifications/unread-count：当前用户未读数量"""
    try:
        count = Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False,
        ).filter(Notification.deleted_at.is_(None)).count()
        return success_response({'count': count})
    except Exception as e:
        return error_response(500, str(e))


@bp.route('/<int:notification_id>/read', methods=['PATCH', 'PUT'])
@login_required
def mark_read(notification_id):
    """单条已读或切换已读状态。PATCH body 可传 { "is_read": true/false }，不传则设为已读"""
    try:
        n = Notification.query.filter_by(
            id=notification_id,
            user_id=current_user.id,
        ).filter(Notification.deleted_at.is_(None)).first()
        if not n:
            return error_response(404, '通知不存在')
        data = request.get_json() or {}
        if 'is_read' in data:
            n.is_read = bool(data['is_read'])
        else:
            n.is_read = True
        db.session.commit()
        return success_response(n.to_dict())
    except Exception as e:
        db.session.rollback()
        return error_response(500, str(e))


@bp.route('/<int:notification_id>', methods=['DELETE'])
@login_required
def delete_notification(notification_id):
    """单条删除（软删除）"""
    try:
        n = Notification.query.filter_by(
            id=notification_id,
            user_id=current_user.id,
        ).filter(Notification.deleted_at.is_(None)).first()
        if not n:
            return error_response(404, '通知不存在')
        n.deleted_at = datetime.now(LOCAL_TZ)
        db.session.commit()
        return success_response({'message': '已删除'})
    except Exception as e:
        db.session.rollback()
        return error_response(500, str(e))


@bp.route('/<int:notification_id>/pin', methods=['PATCH', 'PUT'])
@login_required
def pin_notification(notification_id):
    """置顶/取消置顶。body: { "is_pinned": true/false }"""
    try:
        n = Notification.query.filter_by(
            id=notification_id,
            user_id=current_user.id,
        ).filter(Notification.deleted_at.is_(None)).first()
        if not n:
            return error_response(404, '通知不存在')
        data = request.get_json() or {}
        n.is_pinned = bool(data.get('is_pinned', True))
        db.session.commit()
        return success_response(n.to_dict())
    except Exception as e:
        db.session.rollback()
        return error_response(500, str(e))


@bp.route('/read', methods=['PUT'])
@login_required
def mark_read_batch():
    """批量已读，body: { "ids": [1,2,3] }"""
    try:
        data = request.get_json() or {}
        ids = data.get('ids') or []
        if not ids:
            return error_response(400, '请提供 ids 数组')
        Notification.query.filter(
            Notification.user_id == current_user.id,
            Notification.id.in_(ids),
            Notification.deleted_at.is_(None),
        ).update({'is_read': True}, synchronize_session=False)
        db.session.commit()
        return success_response({'message': '已标记为已读'})
    except Exception as e:
        db.session.rollback()
        return error_response(500, str(e))


@bp.route('/read-all', methods=['POST'])
@login_required
def mark_read_all():
    """全部已读"""
    try:
        Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False,
        ).filter(Notification.deleted_at.is_(None)).update({'is_read': True}, synchronize_session=False)
        db.session.commit()
        return success_response({'message': '已全部标记为已读'})
    except Exception as e:
        db.session.rollback()
        return error_response(500, str(e))


@bp.route('/clear', methods=['POST', 'DELETE'])
@login_required
def clear_read():
    """按时间范围清理当前用户已读消息（软删除）。body 或 query: time_range=1d|1w|1m|3m|older"""
    try:
        time_range = (request.get_json() or {}).get('time_range') or request.args.get('time_range', '').strip()
        if not time_range or time_range not in TIME_RANGE_VALUES:
            return error_response(400, '请提供有效的 time_range: 1d, 1w, 1m, 3m, older')

        start, end = _time_range_bounds(time_range)
        now = datetime.now(LOCAL_TZ)

        q = Notification.query.filter_by(user_id=current_user.id, is_read=True).filter(Notification.deleted_at.is_(None))
        if start is not None:
            q = q.filter(Notification.created_at >= start, Notification.created_at <= end)
        else:
            q = q.filter(Notification.created_at < end)

        count = q.update({'deleted_at': now}, synchronize_session=False)
        db.session.commit()
        return success_response({'message': f'已清理 {count} 条已读消息', 'cleared': count})
    except Exception as e:
        db.session.rollback()
        return error_response(500, str(e))
