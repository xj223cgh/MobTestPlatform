from flask import Blueprint, request, jsonify
from app.models.models import (
    db, Project, ProjectMember, User, VersionRequirement, Iteration,
    TestSuite, TestCase, TestTask, TestCaseExecution, Report,
)
from flask_login import login_required, current_user
from datetime import datetime
import json
from app.services.permission_service import permission_required

# 项目状态常量 - 与models.py保持一致
PROJECT_STATUS = ('not_started', 'in_progress', 'paused', 'completed', 'closed')

bp = Blueprint('projects', __name__)


@bp.route('/', methods=['POST'])
@login_required
@permission_required('project.create')
def create_project():
    """创建新项目"""
    try:
        data = request.get_json()
        
        required_fields = ['project_name', 'description', 'start_date', 'end_date', 'owner_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'code': 400, 'message': f'缺少必要字段: {field}'}), 400
        
        owner = User.query.get(data['owner_id'])
        if not owner:
            return jsonify({'code': 400, 'message': '项目负责人不存在'}), 400
        
        if len(data['description']) > 100:
            return jsonify({'code': 400, 'message': '项目描述不能超过100个字符'}), 400
        
        try:
            start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'code': 400, 'message': '日期格式错误，请使用有效的日期格式'}), 400
        
        if start_date > end_date:
            return jsonify({'code': 400, 'message': '开始日期不能晚于结束日期'}), 400
        
        import json
        tags = json.dumps(data.get('tags', [])) if data.get('tags') else None
        
        new_project = Project(
            project_name=data['project_name'],
            description=data['description'],
            start_date=start_date,
            end_date=end_date,
            status=data.get('status', 'not_started'),
            tags=tags,
            priority=data.get('priority', 'medium'),
            doc_url=data.get('doc_url'),
            pipeline_url=data.get('pipeline_url'),
            owner_id=data['owner_id'],  # 使用前端传递的项目负责人ID
            creator_id=current_user.id  # 始终使用当前登录用户作为创建人
        )
        db.session.add(new_project)
        db.session.flush()
        
        project_member = ProjectMember(
            project_id=new_project.id,
            user_id=current_user.id,
            role='owner'
        )
        db.session.add(project_member)
        
        if 'members' in data:
            for member in data['members']:
                if 'user_id' in member and 'role' in member:
                    user = User.query.get(member['user_id'])
                    if user:
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
        # 通知：负责人若非当前用户则 project_created；新加入的成员（不含当前用户、不含 owner）project_member_added
        from app.services.notification_service import notify_users
        creator_name = current_user.real_name or current_user.username
        owner_id = new_project.owner_id
        if owner_id and owner_id != current_user.id:
            notify_users([owner_id], 'project_created', '项目负责人',
                         f'{creator_name} 创建了项目「{new_project.project_name}」并指定你为负责人',
                         'project', new_project.id, exclude_user_id=current_user.id)
        member_ids = []
        if 'members' in data:
            for member in data['members']:
                uid = member.get('user_id')
                if uid and uid != current_user.id and uid != owner_id:
                    member_ids.append(uid)
        if member_ids:
            notify_users(member_ids, 'project_member_added', '加入项目',
                         f'{creator_name} 将你加入了项目「{new_project.project_name}」',
                         'project', new_project.id, exclude_user_id=current_user.id)
        return jsonify({'code': 200, 'message': '项目创建成功', 'data': new_project.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'创建项目失败: {str(e)}'}), 500

@bp.route('/', methods=['GET'])
@login_required
@permission_required('project.list')
def get_projects():
    """获取所有项目列表，支持分页和搜索筛选"""
    try:
        # 获取查询参数（size 上限 10000，保证下拉等场景可一次拉全量）
        page = request.args.get('page', 1, type=int)
        size = min(request.args.get('size', 10, type=int), 10000)
        search = request.args.get('search', '', type=str)
        status = request.args.get('status', '', type=str)
        priority = request.args.get('priority', '', type=str)
        
        query = Project.query
        
        if search:
            # BINARY 实现区分大小写搜索
            query = query.filter(db.text("BINARY project_name LIKE :search_pattern")).params(search_pattern=f"%{search}%")
        
        if status and status in PROJECT_STATUS:
            query = query.filter(Project.status == status)
        
        if priority:
            query = query.filter(Project.priority == priority)
        
        # 默认排序：最近更新在前，符合用户「最近在用的项目」习惯
        query = query.order_by(Project.updated_at.desc(), Project.id.desc())
        
        pagination = query.paginate(page=page, per_page=size, error_out=False)
        project_list = [project.to_dict() for project in pagination.items]
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'items': project_list,
                'total': pagination.total,
                'page': page,
                'size': size
            }
        }), 200
    except Exception as e:
        return jsonify({'error': f'获取项目列表失败: {str(e)}'}), 500

@bp.route('/<int:project_id>', methods=['GET'])
@login_required
def get_project(project_id):
    """获取项目详情"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': '项目不存在'}), 404
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'project': project.to_dict()
            }
        }), 200
    except Exception as e:
        return jsonify({'error': f'获取项目详情失败: {str(e)}'}), 500

@bp.route('/<int:project_id>', methods=['PUT'])
@login_required
@permission_required('project.edit')
def update_project(project_id):
    """更新项目信息"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'code': 404, 'message': '项目不存在'}), 404
        
        data = request.get_json()
        if 'project_name' in data:
            project.project_name = data['project_name']
        if 'description' in data:
            if len(data['description']) > 100:
                return jsonify({'code': 400, 'message': '项目描述不能超过100个字符'}), 400
            project.description = data['description']
        if 'status' in data:
            project.status = data['status']
        if 'start_date' in data:
            try:
                project.start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'code': 400, 'message': '开始日期格式错误，请使用有效的日期格式'}), 400
        if 'end_date' in data:
            try:
                project.end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'code': 400, 'message': '结束日期格式错误，请使用有效的日期格式'}), 400
        if 'tags' in data:
            import json
            project.tags = json.dumps(data['tags']) if data['tags'] else None
        if 'priority' in data:
            project.priority = data['priority']
        if 'owner_id' in data:
            owner = User.query.get(data['owner_id'])
            if owner:
                new_owner_id = data['owner_id']
                if new_owner_id != project.owner_id and new_owner_id != current_user.id:
                    from app.services.notification_service import notify_users
                    operator_name = current_user.real_name or current_user.username
                    notify_users([new_owner_id], 'project_owner_changed', '项目负责人变更',
                                 f'{operator_name} 将项目「{project.project_name}」的负责人变更为你',
                                 'project', project_id, exclude_user_id=current_user.id)
                project.owner_id = new_owner_id
            else:
                return jsonify({'error': '项目负责人不存在'}), 400
        if 'doc_url' in data:
            project.doc_url = data['doc_url']
        if 'pipeline_url' in data:
            project.pipeline_url = data['pipeline_url']
        if 'creator_id' in data:
            new_creator = ProjectMember.query.filter_by(
                project_id=project_id,
                user_id=data['creator_id']
            ).first()
            if new_creator:
                project.creator_id = data['creator_id']
            else:
                return jsonify({'code': 400, 'message': '新创建者必须是项目成员'}), 400
        
        if 'members' in data:
            current_owner_id = project.owner_id
            current_members = ProjectMember.query.filter_by(project_id=project_id).all()
            current_member_ids = {member.user_id: member for member in current_members}
            
            for member in data['members']:
                user_id = member.get('user_id')
                role = member.get('role')
                
                if user_id and role:
                    user = User.query.get(user_id)
                    if user:
                        if user_id in current_member_ids:
                            current_member = current_member_ids[user_id]
                            current_member.role = role
                            del current_member_ids[user_id]  # 标记为已处理
                        else:
                            project_member = ProjectMember(
                                project_id=project_id,
                                user_id=user_id,
                                role=role
                            )
                            db.session.add(project_member)
                            from app.services.notification_service import notify_users
                            operator_name = current_user.real_name or current_user.username
                            notify_users([user_id], 'project_member_added', '加入项目',
                                         f'{operator_name} 将你加入了项目「{project.project_name}」',
                                         'project', project_id, exclude_user_id=current_user.id)
            
            for member in current_member_ids.values():
                if member.user_id != current_owner_id:
                    db.session.delete(member)
        
        db.session.commit()
        return jsonify({'code': 200, 'message': '项目更新成功', 'data': project.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'更新项目失败: {str(e)}'}), 500


@bp.route('/<int:project_id>', methods=['DELETE'])
@login_required
@permission_required('project.delete')
def delete_project(project_id):
    """删除项目。如有关联引用则拒绝删除并返回引用信息。"""
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'code': 404, 'message': '项目不存在'}), 404

    # 仅校验业务实体引用；成员关联为单向绑定，不阻止删除（删除时由 cascade 清理）
    refs = []
    n = Iteration.query.filter_by(project_id=project_id).count()
    if n > 0:
        refs.append(f"迭代({n})")
    n = VersionRequirement.query.filter_by(project_id=project_id).count()
    if n > 0:
        refs.append(f"版本需求({n})")
    n = TestSuite.query.filter_by(project_id=project_id).count()
    if n > 0:
        refs.append(f"测试套件({n})")
    n = TestCase.query.filter_by(project_id=project_id).count()
    if n > 0:
        refs.append(f"测试用例({n})")
    n = TestTask.query.filter(TestTask.project_id.isnot(None), TestTask.project_id == project_id).count()
    if n > 0:
        refs.append(f"测试任务({n})")
    n = TestCaseExecution.query.filter(TestCaseExecution.project_id.isnot(None), TestCaseExecution.project_id == project_id).count()
    if n > 0:
        refs.append(f"用例执行记录({n})")
    n = Report.query.filter(Report.project_id.isnot(None), Report.project_id == project_id).count()
    if n > 0:
        refs.append(f"测试报告({n})")

    if refs:
        return jsonify({
            'code': 400,
            'message': '该项目存在关联数据，无法删除。当前引用：' + '、'.join(refs) + '。请先解除或删除上述关联后再试。',
        }), 400

    try:
        db.session.delete(project)
        db.session.commit()
        return jsonify({'code': 200, 'message': '项目删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'删除项目失败: {str(e)}'}), 500


@bp.route('/<int:project_id>/members', methods=['GET'])
@login_required
def get_project_members(project_id):
    """获取项目成员列表（不做权限鉴别）"""
    try:
        members = ProjectMember.query.filter_by(project_id=project_id).all()
        
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
    """添加项目成员（不做权限鉴别）"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': '项目不存在'}), 404
        
        data = request.get_json()
        if 'user_id' not in data or 'role' not in data:
            return jsonify({'error': '缺少必要字段: user_id, role'}), 400
        
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        existing_member = ProjectMember.query.filter_by(
            project_id=project_id,
            user_id=data['user_id']
        ).first()
        
        if existing_member:
            return jsonify({'error': '该用户已经是项目成员'}), 400
        
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
        member_to_remove = ProjectMember.query.filter_by(
            id=member_id,
            project_id=project_id
        ).first()
        
        if not member_to_remove:
            return jsonify({'code': 404, 'message': '成员不存在或不属于该项目'}), 404
        
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'code': 404, 'message': '项目不存在'}), 404
        
        if member_to_remove.user_id == project.owner_id:
            return jsonify({'code': 403, 'message': '不能移除项目负责人'}), 403
        
        db.session.delete(member_to_remove)
        db.session.commit()
        
        return jsonify({'code': 200, 'message': '成员移除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'移除项目成员失败: {str(e)}'}), 500

@bp.route('/<int:project_id>/version-requirements', methods=['GET'])
@login_required
@permission_required('requirement.list')
def get_project_version_requirements(project_id):
    """获取项目的版本需求列表"""
    try:
        # 按优先级 P0→P4，再按最近更新排序
        requirements = (
            VersionRequirement.query.filter_by(project_id=project_id)
            .order_by(
                db.case((VersionRequirement.priority == 'P0', 0), (VersionRequirement.priority == 'P1', 1),
                        (VersionRequirement.priority == 'P2', 2), (VersionRequirement.priority == 'P3', 3),
                        (VersionRequirement.priority == 'P4', 4), else_=5),
                VersionRequirement.updated_at.desc(),
                VersionRequirement.id.desc()
            )
            .all()
        )
        
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
        return jsonify({'error': f'获取版本需求列表失败: {str(e)}'}), 500

@bp.route('/version-requirements', methods=['GET'])
@login_required
@permission_required('requirement.list')
def get_all_version_requirements():
    """获取所有版本需求列表"""
    try:
        requirements = (
            VersionRequirement.query
            .order_by(
                db.case((VersionRequirement.priority == 'P0', 0), (VersionRequirement.priority == 'P1', 1),
                        (VersionRequirement.priority == 'P2', 2), (VersionRequirement.priority == 'P3', 3),
                        (VersionRequirement.priority == 'P4', 4), else_=5),
                VersionRequirement.updated_at.desc(),
                VersionRequirement.id.desc()
            )
            .all()
        )
        
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
        return jsonify({'error': f'获取版本需求列表失败: {str(e)}'}), 500

@bp.route('/<int:project_id>/version-requirements', methods=['POST'])
@login_required
@permission_required('requirement.create')
def create_project_version_requirement(project_id):
    """创建版本需求（不做权限鉴别）"""
    try:
        data = request.get_json()
        
        required_fields = ['requirement_name', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({'code': 400, 'message': f'缺少必要字段: {field}'}), 400
        
        new_requirement = VersionRequirement(
            requirement_name=data['requirement_name'],
            requirement_description=data['description'],
            status=data.get('status', 'new'),
            project_id=project_id,
            iteration_id=data.get('iteration_id'),
            priority=data.get('priority') or 'P1',
            environment=data.get('environment', 'test'),
            estimated_hours=data.get('estimated_hours'),
            actual_hours=data.get('actual_hours'),
            created_by=current_user.id,
            assigned_to=data.get('assigned_to')
        )
        
        if 'start_date' in data and data['start_date']:
            try:
                new_requirement.start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'code': 400, 'message': '开始日期格式错误，请使用有效的日期格式'}), 400
        
        if 'end_date' in data and data['end_date']:
            try:
                new_requirement.end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'code': 400, 'message': '结束日期格式错误，请使用有效的日期格式'}), 400
        db.session.add(new_requirement)
        db.session.commit()
        # 通知被指派人（若存在且非当前用户）
        if new_requirement.assigned_to and new_requirement.assigned_to != current_user.id:
            from app.services.notification_service import notify_users
            assigner_name = current_user.real_name or current_user.username
            project = Project.query.get(project_id)
            project_label = f'（项目「{project.project_name}」）' if project else ''
            notify_users([new_requirement.assigned_to], 'requirement_assigned', '需求指派',
                         f'{assigner_name} 将需求「{new_requirement.requirement_name}」{project_label}分配给你',
                         'version_requirement', new_requirement.id, exclude_user_id=current_user.id)
        return jsonify({'code': 200, 'message': '版本需求创建成功', 'data': new_requirement.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'创建版本需求失败: {str(e)}'}), 500

@bp.route('/<int:project_id>/version-requirements/<int:requirement_id>', methods=['PUT'])
@login_required
@permission_required('requirement.edit')
def update_project_version_requirement(project_id, requirement_id):
    """更新版本需求（不做权限鉴别）"""
    try:
        requirement = VersionRequirement.query.filter_by(
            id=requirement_id,
            project_id=project_id
        ).first()
        
        if not requirement:
            return jsonify({'code': 404, 'message': '版本需求不存在或不属于该项目'}), 404
        
        data = request.get_json()
        
        if 'requirement_name' in data:
            requirement.requirement_name = data['requirement_name']
        if 'description' in data:
            requirement.requirement_description = data['description']
        if 'status' in data:
            requirement.status = data['status']
        if 'iteration_id' in data:
            requirement.iteration_id = data['iteration_id']
        if 'priority' in data:
            requirement.priority = data['priority'] if data['priority'] in ('P0', 'P1', 'P2', 'P3', 'P4') else requirement.priority
        if 'environment' in data:
            requirement.environment = data['environment']
        if 'estimated_hours' in data:
            requirement.estimated_hours = data['estimated_hours']
        if 'actual_hours' in data:
            requirement.actual_hours = data['actual_hours']
        if 'assigned_to' in data:
            new_assigned = data['assigned_to']
            if new_assigned != requirement.assigned_to and new_assigned and new_assigned != current_user.id:
                from app.services.notification_service import notify_users
                assigner_name = current_user.real_name or current_user.username
                project = Project.query.get(project_id)
                project_label = f'（项目「{project.project_name}」）' if project else ''
                notify_users([new_assigned], 'requirement_assigned', '需求指派',
                             f'{assigner_name} 将需求「{requirement.requirement_name}」{project_label}重新分配给你',
                             'version_requirement', requirement.id, exclude_user_id=current_user.id)
            requirement.assigned_to = new_assigned
        if 'start_date' in data:
            try:
                requirement.start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'code': 400, 'message': '开始日期格式错误，请使用有效的日期格式'}), 400
        if 'end_date' in data:
            try:
                requirement.end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'code': 400, 'message': '结束日期格式错误，请使用有效的日期格式'}), 400
        if 'completed_at' in data and data['completed_at']:
            try:
                requirement.completed_at = datetime.fromisoformat(data['completed_at'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'code': 400, 'message': '完成日期格式错误，请使用有效的日期格式'}), 400
        
        db.session.commit()
        
        return jsonify({'code': 200, 'message': '版本需求更新成功', 'data': requirement.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'更新版本需求失败: {str(e)}'}), 500

@bp.route('/<int:project_id>/version-requirements/<int:requirement_id>', methods=['DELETE'])
@login_required
@permission_required('requirement.delete')
def delete_project_version_requirement(project_id, requirement_id):
    """删除版本需求。仅校验关联引用，有关联则提示无法删除；不做权限鉴别。"""
    requirement_to_delete = VersionRequirement.query.filter_by(
        id=requirement_id,
        project_id=project_id
    ).first()

    if not requirement_to_delete:
        return jsonify({'code': 404, 'message': '版本需求不存在或不属于该项目'}), 404

    refs = []
    n = TestSuite.query.filter_by(version_requirement_id=requirement_id).count()
    if n > 0:
        refs.append(f"测试套件({n})")
    n = TestCase.query.filter_by(version_requirement_id=requirement_id).count()
    if n > 0:
        refs.append(f"测试用例({n})")
    n = TestTask.query.filter(
        TestTask.version_requirement_id.isnot(None),
        TestTask.version_requirement_id == requirement_id,
    ).count()
    if n > 0:
        refs.append(f"测试任务({n})")

    if refs:
        return jsonify({
            'code': 400,
            'message': '该需求存在关联数据，无法删除。当前引用：' + '、'.join(refs) + '。请先解除或删除上述关联后再试。',
        }), 400

    try:
        db.session.delete(requirement_to_delete)
        db.session.commit()
        return jsonify({'code': 200, 'message': '版本需求删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'删除版本需求失败: {str(e)}'}), 500

@bp.route('/<int:project_id>/iterations', methods=['GET'])
@login_required
@permission_required('iteration.list')
def get_project_iterations(project_id):
    """获取项目的迭代列表"""
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        
        project_iterations = Iteration.query.filter_by(project_id=project_id)
        total = project_iterations.count()
        paginated_iterations = project_iterations.offset((page - 1) * page_size).limit(page_size).all()
        iteration_list = [iteration.to_dict() for iteration in paginated_iterations]
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'items': iteration_list,
                'total': total
            }
        }), 200
    except Exception as e:
        return jsonify({'error': f'获取迭代列表失败: {str(e)}'}), 500