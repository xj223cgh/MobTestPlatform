# -*- coding: utf-8 -*-
"""系统设置与用户个人设置 API"""
from flask import Blueprint, request
from flask_login import login_required, current_user

from app.models.models import db, SystemSetting, UserSetting
from app.utils.helpers import success_response, error_response

bp = Blueprint('settings', __name__, url_prefix='/api/settings')


@bp.route('/system', methods=['GET'])
@login_required
def get_system_settings():
    """获取系统设置（key-value 字典）"""
    try:
        items = SystemSetting.query.all()
        data = {item.setting_key: item.setting_value for item in items}
        return success_response(data)
    except Exception as e:
        return error_response(500, str(e))


@bp.route('/system', methods=['PUT'])
@login_required
def update_system_settings():
    """更新系统设置（传入 key-value 对象，仅更新存在的 key）"""
    try:
        data = request.get_json() or {}
        for key, value in data.items():
            item = SystemSetting.query.filter_by(setting_key=key).first()
            if item:
                item.setting_value = value if value is None else str(value)
            else:
                db.session.add(SystemSetting(setting_key=key, setting_value=str(value) if value is not None else None))
        db.session.commit()
        items = SystemSetting.query.all()
        result = {item.setting_key: item.setting_value for item in items}
        return success_response(result)
    except Exception as e:
        db.session.rollback()
        return error_response(500, str(e))


@bp.route('/user', methods=['GET'])
@login_required
def get_user_settings():
    """获取当前用户个人设置（key-value 字典）"""
    try:
        items = UserSetting.query.filter_by(user_id=current_user.id).all()
        data = {item.setting_key: item.setting_value for item in items}
        return success_response(data)
    except Exception as e:
        return error_response(500, str(e))


@bp.route('/user', methods=['PUT'])
@login_required
def update_user_settings():
    """更新当前用户个人设置（传入 key-value 对象）"""
    try:
        data = request.get_json() or {}
        user_id = current_user.id
        for key, value in data.items():
            item = UserSetting.query.filter_by(user_id=user_id, setting_key=key).first()
            val_str = value if value is None else str(value)
            if item:
                item.setting_value = val_str
            else:
                db.session.add(UserSetting(user_id=user_id, setting_key=key, setting_value=val_str))
        db.session.commit()
        items = UserSetting.query.filter_by(user_id=user_id).all()
        result = {item.setting_key: item.setting_value for item in items}
        return success_response(result)
    except Exception as e:
        db.session.rollback()
        return error_response(500, str(e))
