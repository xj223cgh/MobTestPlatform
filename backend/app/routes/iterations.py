from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models.models import (
    db, Project, ProjectMember, Iteration, VersionRequirement,
    TestSuite, TestCase, TestTask, TestCaseExecution,
)
from app.services.permission_service import permission_required
from datetime import datetime
import json

bp = Blueprint('iterations', __name__)


@bp.route('/', methods=['POST'])
@login_required
@permission_required('iteration.create')
def create_iteration_new():
    """创建迭代（通用路由）"""
    try:
        data = request.get_json()
        
        if 'project_id' not in data:
            return jsonify({'error': '缺少必要字段: project_id'}), 400
        
        project_id = data['project_id']
        
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': '项目不存在'}), 404
        
        required_fields = ['iteration_name', 'start_date', 'end_date', 'version']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'缺少必要字段: {field}'}), 400
        
        try:
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
        except ValueError as e:
            return jsonify({'error': f'日期格式错误，请使用YYYY-MM-DD格式: {str(e)}'}), 400
        
        if start_date > end_date:
            return jsonify({'error': '开始日期不能晚于结束日期'}), 400
        
        if project.start_date and project.end_date:
            ps = project.start_date.date() if hasattr(project.start_date, 'date') else project.start_date
            pe = project.end_date.date() if hasattr(project.end_date, 'date') else project.end_date
            if start_date.date() < ps or end_date.date() > pe:
                range_str = f"{ps.strftime('%Y-%m-%d')} 至 {pe.strftime('%Y-%m-%d')}"
                return jsonify({'error': f'迭代的开始、结束日期需在项目日期范围内（{range_str}），请调整后重试'}), 400
        
        new_iteration = Iteration(
            project_id=project_id,
            iteration_name=data['iteration_name'],
            start_date=start_date,
            end_date=end_date,
            version=data['version'],
            goal=data.get('goal', ''),
            description=data.get('description', '') or '',
            status=data.get('status', 'planning'),
            created_by=current_user.id,
            updated_by=current_user.id
        )
        
        db.session.add(new_iteration)
        db.session.commit()
        if project.owner_id and project.owner_id != current_user.id:
            from app.services.notification_service import notify_users
            creator_name = current_user.real_name or current_user.username
            date_range = ''
            if new_iteration.start_date and new_iteration.end_date:
                date_range = f'，周期 {new_iteration.start_date.strftime("%Y-%m-%d")} ~ {new_iteration.end_date.strftime("%Y-%m-%d")}'
            notify_users([project.owner_id], 'iteration_created', '新建迭代',
                         f'{creator_name} 在项目「{project.project_name}」下创建了迭代「{new_iteration.iteration_name}」{date_range}',
                         'iteration', new_iteration.id, exclude_user_id=current_user.id)
        return jsonify({
            'code': 201,
            'message': '迭代创建成功',
            'data': new_iteration.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'创建迭代失败: {str(e)}'}), 500

@bp.route('/projects/<int:project_id>/iterations', methods=['POST'])
@login_required
@permission_required('iteration.create')
def create_iteration(project_id):
    """创建迭代（不做权限鉴别）"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': '项目不存在'}), 404
        
        data = request.get_json()
        required_fields = ['iteration_name', 'start_date', 'end_date', 'version']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必要字段: {field}'}), 400
        
        try:
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': '日期格式错误，请使用YYYY-MM-DD格式'}), 400
        
        if start_date > end_date:
            return jsonify({'error': '开始日期不能晚于结束日期'}), 400
        
        if project.start_date and project.end_date:
            ps = project.start_date.date() if hasattr(project.start_date, 'date') else project.start_date
            pe = project.end_date.date() if hasattr(project.end_date, 'date') else project.end_date
            if start_date.date() < ps or end_date.date() > pe:
                range_str = f"{ps.strftime('%Y-%m-%d')} 至 {pe.strftime('%Y-%m-%d')}"
                return jsonify({'error': f'迭代的开始、结束日期需在项目日期范围内（{range_str}），请调整后重试'}), 400
        
        new_iteration = Iteration(
            project_id=project_id,
            iteration_name=data['iteration_name'],
            start_date=start_date,
            end_date=end_date,
            version=data['version'],
            goal=data.get('goal', ''),
            description=data.get('description', '') or '',
            status=data.get('status', 'planning'),
            created_by=current_user.id,
            updated_by=current_user.id
        )
        
        db.session.add(new_iteration)
        db.session.commit()
        if project.owner_id and project.owner_id != current_user.id:
            from app.services.notification_service import notify_users
            creator_name = current_user.real_name or current_user.username
            date_range = ''
            if new_iteration.start_date and new_iteration.end_date:
                date_range = f'，周期 {new_iteration.start_date.strftime("%Y-%m-%d")} ~ {new_iteration.end_date.strftime("%Y-%m-%d")}'
            notify_users([project.owner_id], 'iteration_created', '新建迭代',
                         f'{creator_name} 在项目「{project.project_name}」下创建了迭代「{new_iteration.iteration_name}」{date_range}',
                         'iteration', new_iteration.id, exclude_user_id=current_user.id)
        return jsonify({
            'code': 201,
            'message': '迭代创建成功',
            'data': new_iteration.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'创建迭代失败: {str(e)}'}), 500

@bp.route('/projects/<int:project_id>/iterations', methods=['GET'])
@login_required
@permission_required('iteration.list')
def get_iterations(project_id):
    """获取项目的迭代列表"""
    try:
        iterations = Iteration.query.filter_by(project_id=project_id).order_by(Iteration.start_date.desc()).all()
        iteration_list = [iteration.to_dict() for iteration in iterations]
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'items': iteration_list,
                'total': len(iteration_list)
            }
        }), 200
    except Exception as e:
        return jsonify({'error': f'获取迭代列表失败: {str(e)}'}), 500

@bp.route('/<int:iteration_id>', methods=['GET'])
@login_required
def get_iteration(iteration_id):
    """获取迭代详情"""
    try:
        iteration = Iteration.query.get(iteration_id)
        if not iteration:
            return jsonify({'error': '迭代不存在'}), 404
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': iteration.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': f'获取迭代详情失败: {str(e)}'}), 500

@bp.route('/<int:iteration_id>', methods=['PUT'])
@login_required
@permission_required('iteration.edit')
def update_iteration(iteration_id):
    """更新迭代信息"""
    try:
        iteration = Iteration.query.get(iteration_id)
        if not iteration:
            return jsonify({'error': '迭代不存在'}), 404
        
        data = request.get_json()
        if 'iteration_name' in data:
            iteration.iteration_name = data['iteration_name']
        if 'goal' in data:
            iteration.goal = data['goal']
        if 'status' in data:
            iteration.status = data['status']
        if 'version' in data:
            iteration.version = data['version']
        if 'description' in data:
            iteration.description = data['description'] or ''
        if 'start_date' in data:
            try:
                iteration.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
            except ValueError:
                return jsonify({'error': '开始日期格式错误，请使用YYYY-MM-DD格式'}), 400
        if 'end_date' in data:
            try:
                iteration.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
            except ValueError:
                return jsonify({'error': '结束日期格式错误，请使用YYYY-MM-DD格式'}), 400

        # 若修改了日期，校验是否在项目日期范围内（只比较日期部分）
        project = Project.query.get(iteration.project_id)
        if project and project.start_date and project.end_date:
            ps = project.start_date.date() if hasattr(project.start_date, 'date') else project.start_date
            pe = project.end_date.date() if hasattr(project.end_date, 'date') else project.end_date
            sd = iteration.start_date.date() if hasattr(iteration.start_date, 'date') else iteration.start_date
            ed = iteration.end_date.date() if hasattr(iteration.end_date, 'date') else iteration.end_date
            if sd < ps or ed > pe:
                range_str = f"{ps.strftime('%Y-%m-%d')} 至 {pe.strftime('%Y-%m-%d')}"
                return jsonify({'error': f'迭代的开始、结束日期需在项目日期范围内（{range_str}），请调整后重试'}), 400

        iteration.updated_by = current_user.id
        
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': '迭代更新成功',
            'data': iteration.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新迭代失败: {str(e)}'}), 500

@bp.route('/<int:iteration_id>', methods=['DELETE'])
@login_required
@permission_required('iteration.delete')
def delete_iteration(iteration_id):
    """删除迭代。仅校验关联引用，有关联则提示无法删除；不做权限鉴别。"""
    iteration = Iteration.query.get(iteration_id)
    if not iteration:
        return jsonify({'code': 404, 'message': '迭代不存在'}), 404

    # 先校验关联引用：有关联则直接返回 400，与项目删除逻辑一致
    refs = []
    n = VersionRequirement.query.filter_by(iteration_id=iteration_id).count()
    if n > 0:
        refs.append(f"版本需求({n})")
    n = TestSuite.query.filter_by(iteration_id=iteration_id).count()
    if n > 0:
        refs.append(f"测试套件({n})")
    n = TestCase.query.filter_by(iteration_id=iteration_id).count()
    if n > 0:
        refs.append(f"测试用例({n})")
    n = TestTask.query.filter(
        TestTask.iteration_id.isnot(None),
        TestTask.iteration_id == iteration_id,
    ).count()
    if n > 0:
        refs.append(f"测试任务({n})")
    n = TestCaseExecution.query.filter(
        TestCaseExecution.iteration_id.isnot(None),
        TestCaseExecution.iteration_id == iteration_id,
    ).count()
    if n > 0:
        refs.append(f"用例执行记录({n})")

    if refs:
        return jsonify({
            'code': 400,
            'message': '该迭代存在关联数据，无法删除。当前引用：' + '、'.join(refs) + '。请先解除或删除上述关联后再试。',
        }), 400

    try:
        db.session.delete(iteration)
        db.session.commit()
        return jsonify({'code': 200, 'message': '迭代删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'删除迭代失败: {str(e)}'}), 500

@bp.route('/<int:iteration_id>/copy', methods=['POST'])
@login_required
def copy_iteration(iteration_id):
    """复制迭代"""
    try:
        source_iteration = Iteration.query.get(iteration_id)
        if not source_iteration:
            return jsonify({'error': '源迭代不存在'}), 404
        
        project = Project.query.get(source_iteration.project_id)
        if not project:
            return jsonify({'error': '项目不存在'}), 404
        
        data = request.get_json() or {}
        new_iteration_name = data.get('iteration_name', f'{source_iteration.iteration_name} (副本)')
        
        iteration_duration = (source_iteration.end_date - source_iteration.start_date).days + 1
        latest_iteration = Iteration.query.filter_by(
            project_id=source_iteration.project_id
        ).order_by(Iteration.end_date.desc()).first()
        
        if latest_iteration:
            new_start_date = latest_iteration.end_date + datetime.timedelta(days=1)
        else:
            new_start_date = source_iteration.start_date
        
        new_end_date = new_start_date + datetime.timedelta(days=iteration_duration - 1)

        if project.start_date and project.end_date:
            ps = project.start_date.date() if hasattr(project.start_date, 'date') else project.start_date
            pe = project.end_date.date() if hasattr(project.end_date, 'date') else project.end_date
            ns = new_start_date.date() if hasattr(new_start_date, 'date') else new_start_date
            ne = new_end_date.date() if hasattr(new_end_date, 'date') else new_end_date
            if ns < ps or ne > pe:
                return jsonify({'error': '新迭代日期必须在项目日期范围内，请手动设置日期'}), 400
        
        new_iteration = Iteration(
            project_id=source_iteration.project_id,
            iteration_name=new_iteration_name,
            start_date=new_start_date,
            end_date=new_end_date,
            version=data.get('version', source_iteration.version),
            goal=data.get('goal', source_iteration.goal),
            status=data.get('status', 'planning'),
            created_by=current_user.id,
            updated_by=current_user.id
        )
        
        db.session.add(new_iteration)
        db.session.commit()
        
        return jsonify({
            'code': 201,
            'message': '迭代复制成功',
            'data': new_iteration.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'复制迭代失败: {str(e)}'}), 500

@bp.route('/<int:iteration_id>/stats', methods=['GET'])
@login_required
def get_iteration_stats(iteration_id):
    """获取迭代统计信息"""
    try:
        iteration = Iteration.query.get(iteration_id)
        if not iteration:
            return jsonify({'error': '迭代不存在'}), 404
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'iteration': iteration.to_dict(),
                'stats': {
                    'requirement_stats': iteration.requirement_stats,
                    'execution_stats': iteration.execution_stats
                }
            }
        }), 200
    except Exception as e:
        return jsonify({'error': f'获取迭代统计信息失败: {str(e)}'}), 500

@bp.route('/<int:iteration_id>/requirements', methods=['GET'])
@login_required
def get_iteration_requirements(iteration_id):
    """获取迭代下的需求列表"""
    try:
        iteration = Iteration.query.get(iteration_id)
        if not iteration:
            return jsonify({'error': '迭代不存在'}), 404
        
        requirements = VersionRequirement.query.filter_by(iteration_id=iteration_id).all()
        requirement_list = [req.to_dict() for req in requirements]
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'items': requirement_list,
                'total': len(requirement_list)
            }
        }), 200
    except Exception as e:
        return jsonify({'error': f'获取迭代需求列表失败: {str(e)}'}), 500