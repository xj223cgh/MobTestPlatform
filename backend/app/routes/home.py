from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.models.models import db, User, Device, TestCase, TestTask
from app.utils.helpers import success_response, error_response
import traceback, logging

# 设置日志
logger = logging.getLogger(__name__)

bp = Blueprint('home', __name__)


@bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    """获取首页统计数据"""
    try:
        # 获取基础统计数据
        stats = {
            'users': db.session.query(User).count(),
            'devices': db.session.query(Device).count(),
            'testCases': db.session.query(TestCase).count(),
            'testTasks': db.session.query(TestTask).count()
        }
        
        return success_response(data=stats)
    except Exception as e:
        error_msg = f"获取统计数据失败: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        return error_response(500, error_msg)


@bp.route('/activities', methods=['GET'])
@login_required
def get_activities():
    """获取最近活动"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        activities = []
        
        # 获取最近完成的测试任务
        recent_tasks = db.session.query(TestTask).filter_by(status='completed')\
            .order_by(TestTask.updated_at.desc())\
            .limit(limit // 4)\
            .all()
        
        for task in recent_tasks:
            activities.append({
                'id': f'task_{task.id}',
                'type': 'task',
                'title': '测试任务完成',
                'description': f'{task.task_name} 已成功完成',
                'created_at': task.updated_at.isoformat() if task.updated_at else datetime.now().isoformat()
            })
        
        # 获取最近上线的设备
        recent_devices = db.session.query(Device).filter_by(status='online')\
            .order_by(Device.updated_at.desc())\
            .limit(limit // 4)\
            .all()
        
        for device in recent_devices:
            activities.append({
                'id': f'device_{device.id}',
                'type': 'device',
                'title': '设备上线',
                'description': f'设备 {device.device_name or "未知设备"} 已连接并上线',
                'created_at': device.updated_at.isoformat() if device.updated_at else datetime.now().isoformat()
            })
        
        # 获取最近注册的用户
        recent_users = db.session.query(User).order_by(User.created_at.desc())\
            .limit(limit // 4)\
            .all()
        
        for user in recent_users:
            activities.append({
                'id': f'user_{user.id}',
                'type': 'user',
                'title': '新用户注册',
                'description': f'{user.username} 已注册账号',
                'created_at': user.created_at.isoformat() if user.created_at else datetime.now().isoformat()
            })
        
        # 按时间排序
        activities.sort(key=lambda x: x['created_at'], reverse=True)
        activities = activities[:limit]
        
        return success_response(data=activities)
    except Exception as e:
        error_msg = f"获取活动数据失败: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        return error_response(500, error_msg)


@bp.route('/task-trend', methods=['GET'])
@login_required
def get_task_trend():
    """获取测试任务趋势数据"""
    try:
        days = request.args.get('days', 7, type=int)
        
        # 生成日期范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days-1)
        
        trend_data = []
        current_date = start_date
        
        while current_date <= end_date:
            # 查询当天创建的任务数量
            daily_tasks = db.session.query(TestTask).filter(
                TestTask.created_at >= current_date.date(),
                TestTask.created_at < (current_date + timedelta(days=1)).date()
            ).count()
            
            trend_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'count': daily_tasks
            })
            
            current_date += timedelta(days=1)
        
        return success_response(data=trend_data)
    except Exception as e:
        error_msg = f"获取趋势数据失败: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        return error_response(500, error_msg)


@bp.route('/device-status', methods=['GET'])
@login_required
def get_device_status():
    """获取设备状态分布数据"""
    try:
        # 统计各状态设备数量
        online_count = db.session.query(Device).filter_by(status='online').count()
        offline_count = db.session.query(Device).filter_by(status='offline').count()
        busy_count = db.session.query(Device).filter_by(status='busy').count()
        
        status_data = [
            { 'name': '在线', 'value': online_count },
            { 'name': '离线', 'value': offline_count },
            { 'name': '忙碌', 'value': busy_count }
        ]
        
        return success_response(data=status_data)
    except Exception as e:
        error_msg = f"获取设备状态数据失败: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        return error_response(500, error_msg)