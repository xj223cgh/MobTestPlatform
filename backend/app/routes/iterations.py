from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models.models import db, Project, ProjectMember, Iteration
from datetime import datetime
import json

bp = Blueprint('iterations', __name__)

@bp.route('/api/projects/<int:project_id>/iterations', methods=['POST'])
@login_required
def create_iteration(project_id):
    """创建迭代"""
    try:
        # 检查用户是否有权限访问该项目
        project_member = ProjectMember.query.filter_by(
            project_id=project_id,
            user_id=current_user.id
        ).first()
        
        if not project_member or project_member.role not in ['owner', 'manager']:
            return jsonify({'error': '无权在该项目中创建迭代'}), 403
        
        # 获取项目
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': '项目不存在'}), 404
        
        # 验证必要字段
        data = request.get_json()
        required_fields = ['iteration_name', 'start_date', 'end_date', 'version_info']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必要字段: {field}'}), 400
        
        # 验证日期格式
        try:
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': '日期格式错误，请使用YYYY-MM-DD格式'}), 400
        
        # 验证日期逻辑
        if start_date > end_date:
            return jsonify({'error': '开始日期不能晚于结束日期'}), 400
        
        # 验证迭代日期是否在项目日期范围内
        if start_date < project.start_date or end_date > project.end_date:
            return jsonify({'error': '迭代日期必须在项目日期范围内'}), 400
        
        # 创建迭代
        new_iteration = Iteration(
            project_id=project_id,
            iteration_name=data['iteration_name'],
            start_date=start_date,
            end_date=end_date,
            version=data['version_info'],
            goal=data.get('goal', ''),
            status=data.get('status', 'planning'),
            created_by=current_user.id,
            updated_by=current_user.id
        )
        
        db.session.add(new_iteration)
        db.session.commit()
        
        return jsonify({'message': '迭代创建成功', 'iteration': new_iteration.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'创建迭代失败: {str(e)}'}), 500

@bp.route('/api/projects/<int:project_id>/iterations', methods=['GET'])
@login_required
def get_iterations(project_id):
    """获取项目的迭代列表"""
    try:
        # 检查用户是否有权限访问该项目
        project_member = ProjectMember.query.filter_by(
            project_id=project_id,
            user_id=current_user.id
        ).first()
        
        if not project_member:
            return jsonify({'error': '无权访问该项目'}), 403
        
        # 获取迭代列表
        iterations = Iteration.query.filter_by(project_id=project_id).order_by(Iteration.start_date.desc()).all()
        
        # 转换为字典列表
        iteration_list = [iteration.to_dict() for iteration in iterations]
        
        return jsonify({'iterations': iteration_list}), 200
    except Exception as e:
        return jsonify({'error': f'获取迭代列表失败: {str(e)}'}), 500

@bp.route('/api/iterations/<int:iteration_id>', methods=['GET'])
@login_required
def get_iteration(iteration_id):
    """获取迭代详情"""
    try:
        # 获取迭代
        iteration = Iteration.query.get(iteration_id)
        if not iteration:
            return jsonify({'error': '迭代不存在'}), 404
        
        # 检查用户是否有权限访问该项目
        project_member = ProjectMember.query.filter_by(
            project_id=iteration.project_id,
            user_id=current_user.id
        ).first()
        
        if not project_member:
            return jsonify({'error': '无权访问该迭代'}), 403
        
        return jsonify({'iteration': iteration.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': f'获取迭代详情失败: {str(e)}'}), 500

@bp.route('/api/iterations/<int:iteration_id>', methods=['PUT'])
@login_required
def update_iteration(iteration_id):
    """更新迭代信息"""
    try:
        # 获取迭代
        iteration = Iteration.query.get(iteration_id)
        if not iteration:
            return jsonify({'error': '迭代不存在'}), 404
        
        # 检查用户是否有权限更新该迭代
        project_member = ProjectMember.query.filter_by(
            project_id=iteration.project_id,
            user_id=current_user.id
        ).first()
        
        if not project_member or project_member.role not in ['owner', 'manager']:
            return jsonify({'error': '无权更新该迭代'}), 403
        
        # 更新迭代信息
        data = request.get_json()
        if 'iteration_name' in data:
            iteration.iteration_name = data['iteration_name']
        if 'goal' in data:
            iteration.goal = data['goal']
        if 'status' in data:
            iteration.status = data['status']
        if 'version_info' in data:
            iteration.version_info = data['version_info']
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
        
        iteration.updated_by = current_user.id
        iteration.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'message': '迭代更新成功', 'iteration': iteration.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新迭代失败: {str(e)}'}), 500

@bp.route('/api/iterations/<int:iteration_id>', methods=['DELETE'])
@login_required
def delete_iteration(iteration_id):
    """删除迭代"""
    try:
        # 获取迭代
        iteration = Iteration.query.get(iteration_id)
        if not iteration:
            return jsonify({'error': '迭代不存在'}), 404
        
        # 检查用户是否有权限删除该迭代
        project_member = ProjectMember.query.filter_by(
            project_id=iteration.project_id,
            user_id=current_user.id
        ).first()
        
        if not project_member or project_member.role not in ['owner', 'manager']:
            return jsonify({'error': '无权删除该迭代'}), 403
        
        # 检查迭代是否有相关的测试计划或测试任务
        if iteration.test_plans or iteration.test_tasks:
            return jsonify({'error': '该迭代下存在测试计划或测试任务，无法删除'}), 400
        
        # 删除迭代
        db.session.delete(iteration)
        db.session.commit()
        
        return jsonify({'message': '迭代删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'删除迭代失败: {str(e)}'}), 500

@bp.route('/api/iterations/<int:iteration_id>/copy', methods=['POST'])
@login_required
def copy_iteration(iteration_id):
    """复制迭代"""
    try:
        # 获取要复制的迭代
        source_iteration = Iteration.query.get(iteration_id)
        if not source_iteration:
            return jsonify({'error': '源迭代不存在'}), 404
        
        # 检查用户是否有权限访问该项目
        project_member = ProjectMember.query.filter_by(
            project_id=source_iteration.project_id,
            user_id=current_user.id
        ).first()
        
        if not project_member or project_member.role not in ['owner', 'manager']:
            return jsonify({'error': '无权复制该迭代'}), 403
        
        # 获取项目
        project = Project.query.get(source_iteration.project_id)
        if not project:
            return jsonify({'error': '项目不存在'}), 404
        
        # 获取复制参数
        data = request.get_json() or {}
        new_iteration_name = data.get('iteration_name', f'{source_iteration.iteration_name} (副本)')
        
        # 计算新的日期范围（向后偏移）
        # 计算迭代时长
        iteration_duration = (source_iteration.end_date - source_iteration.start_date).days + 1
        # 获取最近的迭代结束日期
        latest_iteration = Iteration.query.filter_by(
            project_id=source_iteration.project_id
        ).order_by(Iteration.end_date.desc()).first()
        
        if latest_iteration:
            # 从最近迭代结束日期的后一天开始
            new_start_date = latest_iteration.end_date + datetime.timedelta(days=1)
        else:
            # 使用原迭代的开始日期
            new_start_date = source_iteration.start_date
        
        new_end_date = new_start_date + datetime.timedelta(days=iteration_duration - 1)
        
        # 验证新的迭代日期是否在项目日期范围内
        if new_start_date < project.start_date or new_end_date > project.end_date:
            return jsonify({'error': '新迭代日期必须在项目日期范围内，请手动设置日期'}), 400
        
        # 创建新迭代
        new_iteration = Iteration(
            project_id=source_iteration.project_id,
            iteration_name=new_iteration_name,
            start_date=new_start_date,
            end_date=new_end_date,
            version=data.get('version_info', source_iteration.version),
            goal=data.get('goal', source_iteration.goal),
            status=data.get('status', 'planning'),
            created_by=current_user.id,
            updated_by=current_user.id
        )
        
        db.session.add(new_iteration)
        db.session.commit()
        
        return jsonify({'message': '迭代复制成功', 'iteration': new_iteration.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'复制迭代失败: {str(e)}'}), 500