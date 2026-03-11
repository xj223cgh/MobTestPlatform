from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.models.models import db, User, Device, TestCase, TestTask, Project, Iteration, VersionRequirement
from app.utils.helpers import success_response, error_response
import traceback, logging

logger = logging.getLogger(__name__)

bp = Blueprint('home', __name__)


@bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    """获取首页统计数据"""
    try:
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
        per_type = max(limit // 6, 3)

        activities = []

        # 已完成的测试任务
        for task in db.session.query(TestTask).filter_by(status='completed') \
                .order_by(TestTask.updated_at.desc()).limit(per_type).all():
            activities.append({
                'id': f'task_{task.id}',
                'type': 'task',
                'title': '测试任务完成',
                'description': f'{task.task_name} 已成功完成',
                'created_at': (task.updated_at or datetime.now()).isoformat(),
                'related_type': 'test_task',
                'related_id': task.id,
            })

        # 在线设备
        for device in db.session.query(Device).filter_by(status='online') \
                .order_by(Device.updated_at.desc()).limit(per_type).all():
            activities.append({
                'id': f'device_{device.id}',
                'type': 'device',
                'title': '设备上线',
                'description': f'设备 {device.device_name or "未知设备"} 已连接并上线',
                'created_at': (device.updated_at or datetime.now()).isoformat(),
                'related_type': 'device',
                'related_id': device.id,
            })

        # 最近注册用户
        for user in db.session.query(User).order_by(User.created_at.desc()).limit(per_type).all():
            activities.append({
                'id': f'user_{user.id}',
                'type': 'user',
                'title': '新用户注册',
                'description': f'{user.username} 已注册账号',
                'created_at': (user.created_at or datetime.now()).isoformat(),
                'related_type': 'user',
                'related_id': user.id,
            })

        # 最近更新的项目
        for project in db.session.query(Project).order_by(Project.updated_at.desc()).limit(per_type).all():
            activities.append({
                'id': f'project_{project.id}',
                'type': 'project',
                'title': '项目动态',
                'description': f'项目「{project.project_name}」有新进展',
                'created_at': (project.updated_at or datetime.now()).isoformat(),
                'related_type': 'project',
                'related_id': project.id,
            })

        # 最近创建的迭代
        for iteration in db.session.query(Iteration).order_by(Iteration.created_at.desc()).limit(per_type).all():
            activities.append({
                'id': f'iteration_{iteration.id}',
                'type': 'iteration',
                'title': '新建迭代',
                'description': f'迭代「{iteration.iteration_name}」已创建',
                'created_at': (iteration.created_at or datetime.now()).isoformat(),
                'related_type': 'iteration',
                'related_id': iteration.id,
            })

        # 最近指派的需求
        for req in db.session.query(VersionRequirement).filter(
                VersionRequirement.assigned_to.isnot(None)) \
                .order_by(VersionRequirement.updated_at.desc()).limit(per_type).all():
            activities.append({
                'id': f'req_{req.id}',
                'type': 'requirement',
                'title': '需求指派',
                'description': f'需求「{req.requirement_name}」已指派',
                'created_at': (req.updated_at or datetime.now()).isoformat(),
                'related_type': 'version_requirement',
                'related_id': req.id,
            })

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
        
        if period == '7d':
            days = 7
        elif period == '30d':
            days = 30
        elif period == '90d':
            days = 90
        else:
            days = 7
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days-1)
        
        dates = []
        completed_data = []
        paused_data = []
        running_data = []
        
        current_date = start_date
        
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            
            completed_count = db.session.query(TestTask).filter(
                TestTask.updated_at >= current_date,
                TestTask.updated_at < next_date,
                TestTask.status == 'completed'
            ).count()
            
            paused_count = db.session.query(TestTask).filter(
                TestTask.updated_at >= current_date,
                TestTask.updated_at < next_date,
                TestTask.status == 'paused'
            ).count()
            
            running_count = db.session.query(TestTask).filter(
                TestTask.updated_at >= current_date,
                TestTask.updated_at < next_date,
                TestTask.status == 'running'
            ).count()
            
            dates.append(current_date.strftime('%m-%d'))
            completed_data.append(completed_count)
            paused_data.append(paused_count)
            running_data.append(running_count)
            
            current_date = next_date
        
        trend_data = {
            'dates': dates,
            'completed': completed_data,
            'paused': paused_data,
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
        paused_count = db.session.query(TestTask).filter_by(status='paused').count()
        
        distribution = [
            { 'name': '待执行', 'value': pending_count },
            { 'name': '执行中', 'value': running_count },
            { 'name': '已完成', 'value': completed_count },
            { 'name': '已暂停', 'value': paused_count }
        ]
        
        return success_response(data=distribution)
    except Exception as e:
        error_msg = f"获取任务状态分布失败: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        return error_response(500, error_msg)