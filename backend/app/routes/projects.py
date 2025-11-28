from flask import Blueprint, request, jsonify
from app.models.models import db, Project, ProjectMember, User
from flask_login import login_required, current_user
from datetime import datetime
import json

# 项目状态常量 - 与models.py保持一致
PROJECT_STATUS = ('not_started', 'in_progress', 'paused', 'completed', 'closed')

bp = Blueprint('projects', __name__)

@bp.route('/', methods=['POST'])
@login_required
def create_project():
    """创建新项目"""
    try:
        # 获取请求数据
        data = request.get_json()
        
        # 验证必要字段
        required_fields = ['project_name', 'description', 'start_date', 'end_date']
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
        
        # 处理标签字段
        import json
        tags = json.dumps(data.get('tags', [])) if data.get('tags') else None
        
        # 创建项目
        new_project = Project(
            project_name=data['project_name'],
            description=data['description'],
            start_date=start_date,
            end_date=end_date,
            status=data.get('status', 'not_started'),
            environment=data.get('environment', 'test'),
            tags=tags,
            priority=data.get('priority', 'medium'),
            doc_url=data.get('doc_url'),
            pipeline_url=data.get('pipeline_url')
        )
        db.session.add(new_project)
        db.session.flush()  # 获取项目ID
        
        # 添加创建者为项目成员
        project_member = ProjectMember(
            project_id=new_project.id,
            user_id=current_user.id,
            role='owner'
        )
        db.session.add(project_member)
        
        # 添加其他成员
        if 'members' in data:
            for member in data['members']:
                if 'user_id' in member and 'role' in member:
                    # 检查用户是否存在
                    user = User.query.get(member['user_id'])
                    if user:
                        # 检查是否已经是项目成员
                        existing_member = ProjectMember.query.filter_by(
                            project_id=new_project.id,
                            user_id=member['user_id']
                        ).first()
                        if not existing_member:
                            project_member = ProjectMember(
                                project_id=new_project.id,
                                user_id=member['user_id'],
                                role=member['role']
                            )
                            db.session.add(project_member)
        
        db.session.commit()
        return jsonify({'message': '项目创建成功', 'project': new_project.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'创建项目失败: {str(e)}'}), 500

@bp.route('/', methods=['GET'])
@login_required
def get_projects():
    """获取所有项目列表，支持分页和搜索筛选"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 10, type=int)
        search = request.args.get('search', '', type=str)
        status = request.args.get('status', '', type=str)
        environment = request.args.get('environment', '', type=str)
        priority = request.args.get('priority', '', type=str)
        
        # 构建基础查询，返回所有项目
        query = Project.query
        
        # 应用搜索条件，使用二进制比较实现严格区分大小写
        if search:
            # 使用参数化查询避免SQL注入，同时实现区分大小写搜索
            query = query.filter(db.text("BINARY project_name LIKE :search_pattern")).params(search_pattern=f"%{search}%")
        
        # 应用状态筛选
        if status and status in PROJECT_STATUS:
            query = query.filter(Project.status == status)
        
        # 应用环境筛选
        if environment:
            query = query.filter(Project.environment == environment)
        
        # 应用优先级筛选
        if priority:
            query = query.filter(Project.priority == priority)
        
        # 执行分页查询
        pagination = query.paginate(page=page, per_page=size, error_out=False)
        
        # 转换为字典列表
        project_list = [project.to_dict() for project in pagination.items]
        
        # 返回包含分页信息的结果
        return jsonify({
            'projects': project_list,
            'total': pagination.total,
            'page': page,
            'size': size
        }), 200
    except Exception as e:
        return jsonify({'error': f'获取项目列表失败: {str(e)}'}), 500

@bp.route('/<int:project_id>', methods=['GET'])
@login_required
def get_project(project_id):
    """获取项目详情"""
    try:
        # 获取项目详情
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': '项目不存在'}), 404
        
        return jsonify({'project': project.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': f'获取项目详情失败: {str(e)}'}), 500

@bp.route('/<int:project_id>', methods=['PUT'])
@login_required
def update_project(project_id):
    """更新项目信息"""
    try:
        # 检查用户是否有权限更新该项目
        project_member = ProjectMember.query.filter_by(
            project_id=project_id,
            user_id=current_user.id
        ).first()
        
        if not project_member or project_member.role not in ['owner', 'manager']:
            return jsonify({'error': '无权更新该项目'}), 403
        
        # 获取项目
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': '项目不存在'}), 404
        
        # 更新项目信息
        data = request.get_json()
        if 'project_name' in data:
            project.project_name = data['project_name']
        if 'description' in data:
            project.description = data['description']
        if 'status' in data:
            project.status = data['status']
        if 'start_date' in data:
            try:
                project.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
            except ValueError:
                return jsonify({'error': '开始日期格式错误，请使用YYYY-MM-DD格式'}), 400
        if 'end_date' in data:
            try:
                project.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
            except ValueError:
                return jsonify({'error': '结束日期格式错误，请使用YYYY-MM-DD格式'}), 400
        if 'environment' in data:
            project.environment = data['environment']
        if 'tags' in data:
            import json
            project.tags = json.dumps(data['tags']) if data['tags'] else None
        if 'priority' in data:
            project.priority = data['priority']
        if 'doc_url' in data:
            project.doc_url = data['doc_url']
        if 'pipeline_url' in data:
            project.pipeline_url = data['pipeline_url']
        
        project.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'message': '项目更新成功', 'project': project.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新项目失败: {str(e)}'}), 500

@bp.route('/<int:project_id>/members', methods=['GET'])
@login_required
def get_project_members(project_id):
    """获取项目成员列表"""
    try:
        # 检查用户是否有权限访问该项目
        project_member = ProjectMember.query.filter_by(
            project_id=project_id,
            user_id=current_user.id
        ).first()
        
        if not project_member:
            return jsonify({'error': '无权访问该项目'}), 403
        
        # 获取项目成员
        members = ProjectMember.query.filter_by(project_id=project_id).all()
        
        # 转换为字典列表
        member_list = []
        for member in members:
            member_dict = {
                'id': member.id,
                'user_id': member.user_id,
                'user_name': member.user.real_name if member.user else None,
                'role': member.role,
                'joined_at': member.joined_at.isoformat() if member.joined_at else None
            }
            member_list.append(member_dict)
        
        return jsonify({'members': member_list}), 200
    except Exception as e:
        return jsonify({'error': f'获取项目成员失败: {str(e)}'}), 500

@bp.route('/<int:project_id>/members', methods=['POST'])
@login_required
def add_project_member(project_id):
    """添加项目成员"""
    try:
        # 检查用户是否有权限添加成员
        project_member = ProjectMember.query.filter_by(
            project_id=project_id,
            user_id=current_user.id
        ).first()
        
        if not project_member or project_member.role not in ['owner', 'manager']:
            return jsonify({'error': '无权添加项目成员'}), 403
        
        # 获取项目
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': '项目不存在'}), 404
        
        # 添加成员
        data = request.get_json()
        if 'user_id' not in data or 'role' not in data:
            return jsonify({'error': '缺少必要字段: user_id, role'}), 400
        
        # 检查用户是否存在
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 检查是否已经是项目成员
        existing_member = ProjectMember.query.filter_by(
            project_id=project_id,
            user_id=data['user_id']
        ).first()
        
        if existing_member:
            return jsonify({'error': '该用户已经是项目成员'}), 400
        
        # 添加成员
        new_member = ProjectMember(
            project_id=project_id,
            user_id=data['user_id'],
            role=data['role']
        )
        db.session.add(new_member)
        db.session.commit()
        
        return jsonify({'message': '成员添加成功', 'member': new_member.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'添加项目成员失败: {str(e)}'}), 500

@bp.route('/<int:project_id>/members/<int:member_id>', methods=['DELETE'])
@login_required
def remove_project_member(project_id, member_id):
    """移除项目成员"""
    try:
        # 检查用户是否有权限移除成员
        project_member = ProjectMember.query.filter_by(
            project_id=project_id,
            user_id=current_user.id
        ).first()
        
        if not project_member or project_member.role not in ['owner', 'manager']:
            return jsonify({'error': '无权移除项目成员'}), 403
        
        # 获取要移除的成员
        member_to_remove = ProjectMember.query.filter_by(
            id=member_id,
            project_id=project_id
        ).first()
        
        if not member_to_remove:
            return jsonify({'error': '成员不存在或不属于该项目'}), 404
        
        # 不能移除项目所有者
        if member_to_remove.role == 'owner':
            return jsonify({'error': '不能移除项目所有者'}), 403
        
        # 移除成员
        db.session.delete(member_to_remove)
        db.session.commit()
        
        return jsonify({'message': '成员移除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'移除项目成员失败: {str(e)}'}), 500