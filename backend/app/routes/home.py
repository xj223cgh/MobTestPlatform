from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.models.models import db, User, Device, TestCase, TestTask, Project, Iteration, VersionRequirement
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
        projects_count = db.session.query(Project).count()
        test_cases_count = db.session.query(TestCase).count()
        test_tasks_count = db.session.query(TestTask).count()
        devices_count = db.session.query(Device).count()
        iterations_count = db.session.query(Iteration).count()
        requirements_count = db.session.query(VersionRequirement).count()
        
        # 计算30天前的统计数据用于对比
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        old_projects_count = db.session.query(Project).filter(Project.created_at < thirty_days_ago).count()
        old_test_cases_count = db.session.query(TestCase).filter(TestCase.created_at < thirty_days_ago).count()
        old_test_tasks_count = db.session.query(TestTask).filter(TestTask.created_at < thirty_days_ago).count()
        old_devices_count = db.session.query(Device).filter(Device.created_at < thirty_days_ago).count()
        
        # 计算增长率
        def calc_growth(current, old):
            if old == 0:
                return 100 if current > 0 else 0
            return round((current - old) / old * 100, 1)
        
        stats = {
            'projects': projects_count,
            'projectsGrowth': calc_growth(projects_count, old_projects_count),
            'testCases': test_cases_count,
            'testCasesGrowth': calc_growth(test_cases_count, old_test_cases_count),
            'testTasks': test_tasks_count,
            'testTasksGrowth': calc_growth(test_tasks_count, old_test_tasks_count),
            'devices': devices_count,
            'devicesGrowth': calc_growth(devices_count, old_devices_count),
            'iterations': iterations_count,
            'requirements': requirements_count
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
        period = request.args.get('period', '7d')
        
        # 解析时间段
        if period == '7d':
            days = 7
        elif period == '30d':
            days = 30
        elif period == '90d':
            days = 90
        else:
            days = 7
        
        # 生成日期范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days-1)
        
        dates = []
        completed_data = []
        failed_data = []
        running_data = []
        
        current_date = start_date
        
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            
            # 查询当天不同状态的任务数量
            completed_count = db.session.query(TestTask).filter(
                TestTask.updated_at >= current_date,
                TestTask.updated_at < next_date,
                TestTask.status == 'completed'
            ).count()
            
            failed_count = db.session.query(TestTask).filter(
                TestTask.updated_at >= current_date,
                TestTask.updated_at < next_date,
                TestTask.status == 'failed'
            ).count()
            
            running_count = db.session.query(TestTask).filter(
                TestTask.updated_at >= current_date,
                TestTask.updated_at < next_date,
                TestTask.status == 'running'
            ).count()
            
            dates.append(current_date.strftime('%m-%d'))
            completed_data.append(completed_count)
            failed_data.append(failed_count)
            running_data.append(running_count)
            
            current_date = next_date
        
        trend_data = {
            'dates': dates,
            'completed': completed_data,
            'failed': failed_data,
            'running': running_data
        }
        
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
        maintenance_count = db.session.query(Device).filter_by(status='maintenance').count()
        
        status_data = [
            { 'name': '在线', 'value': online_count },
            { 'name': '离线', 'value': offline_count },
            { 'name': '忙碌', 'value': busy_count },
            { 'name': '维护', 'value': maintenance_count }
        ]
        
        return success_response(data=status_data)
    except Exception as e:
        error_msg = f"获取设备状态数据失败: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        return error_response(500, error_msg)


@bp.route('/recent-projects', methods=['GET'])
@login_required
def get_recent_projects():
    """获取最近访问的项目"""
    try:
        limit = request.args.get('limit', 5, type=int)
        
        # 获取最近更新的项目
        projects = db.session.query(Project)\
            .order_by(Project.updated_at.desc())\
            .limit(limit)\
            .all()
        
        projects_data = [{
            'id': p.id,
            'project_name': p.project_name,
            'status': p.status,
            'updated_at': p.updated_at.isoformat() if p.updated_at else None,
            'owner_name': p.owner.real_name if p.owner else None
        } for p in projects]
        
        return success_response(data=projects_data)
    except Exception as e:
        error_msg = f"获取最近项目失败: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        return error_response(500, error_msg)


@bp.route('/task-status-distribution', methods=['GET'])
@login_required
def get_task_status_distribution():
    """获取任务状态分布"""
    try:
        pending_count = db.session.query(TestTask).filter_by(status='pending').count()
        running_count = db.session.query(TestTask).filter_by(status='running').count()
        completed_count = db.session.query(TestTask).filter_by(status='completed').count()
        failed_count = db.session.query(TestTask).filter_by(status='failed').count()
        cancelled_count = db.session.query(TestTask).filter_by(status='cancelled').count()
        
        distribution = [
            { 'name': '待执行', 'value': pending_count },
            { 'name': '执行中', 'value': running_count },
            { 'name': '已完成', 'value': completed_count },
            { 'name': '失败', 'value': failed_count },
            { 'name': '已取消', 'value': cancelled_count }
        ]
        
        return success_response(data=distribution)
    except Exception as e:
        error_msg = f"获取任务状态分布失败: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        return error_response(500, error_msg)