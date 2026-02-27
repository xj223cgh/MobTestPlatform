from flask import Blueprint, request
from flask_login import login_required, current_user

from app.models.models import User, ProjectMember, db
from app.utils.helpers import (
    success_response, error_response, validate_phone,
    validate_username, get_pagination_params, log_user_action,
    validate_json_data
)
from app.services.permission_service import permission_required

bp = Blueprint('users', __name__)


@bp.route('', methods=['GET'])
@login_required
@permission_required('user.list')
def get_users():
    """获取用户列表"""
    page, size = get_pagination_params()
    search = request.args.get('search', '').strip()
    role = request.args.get('role', '').strip()
    is_active_param = request.args.get('is_active', '').strip()
    
    # 构建查询
    query = User.query
    
    # 搜索过滤
    if search:
        # 用户名查询使用BINARY关键字确保严格区分大小写
        # 真实姓名和手机号保持不区分大小写的contains查询
        query = query.filter(
            db.or_(
                db.text(f'BINARY "username" LIKE :username_pattern').params(username_pattern=f'%{search}%'),
                User.real_name.contains(search),
                User.phone.contains(search)
            )
        )
    
    # 角色过滤
    if role:
        query = query.filter(User.role == role)
    
    # 状态过滤
    if is_active_param:
        # 将字符串转换为布尔值
        is_active = is_active_param.lower() == 'true'
        query = query.filter(User.is_active == is_active)
    
    # 分页
    pagination = query.paginate(
        page=page, per_page=size, error_out=False
    )
    
    users = [user.to_dict() for user in pagination.items]
    
    return success_response({
        'users': users,
        'pagination': {
            'page': page,
            'size': size,
            'total': pagination.total,
            'pages': pagination.pages
        }
    })


@bp.route('/options', methods=['GET'])
@login_required
def get_user_options():
    """获取用户选项列表（id、姓名等），用于评审人/负责人/执行人等下拉。仅需登录，不做 user.list 权限校验。"""
    size = min(request.args.get('size', 1000, type=int), 5000)
    users = User.query.filter_by(is_active=True).order_by(User.real_name, User.username).limit(size).all()
    items = [
        {'id': u.id, 'username': u.username, 'real_name': u.real_name or u.username}
        for u in users
    ]
    return success_response({'items': items, 'total': len(items)})


@bp.route('/<int:user_id>', methods=['GET'])
@login_required
@permission_required('user.list')
def get_user(user_id):
    """获取用户详情"""
    user = User.query.get_or_404(user_id)
    return success_response({
        'user': user.to_dict()
    })


@bp.route('', methods=['POST'])
@login_required
@permission_required('user.create')
@validate_json_data(['username', 'phone', 'password', 'real_name', 'role'])
def create_user():
    """创建用户"""
    data = request.get_json()
    username = data.get('username', '').strip()
    phone = data.get('phone', '').strip()
    password = data.get('password', '')
    real_name = data.get('real_name', '').strip()
    role = data.get('role', 'admin')
    gender = data.get('gender', 'other')
    department = data.get('department', '').strip()
    
    # 验证输入
    if not validate_username(username):
        return error_response(400, "用户名长度必须在3-14个字节之间")
    
    if not validate_phone(phone):
        return error_response(400, "手机号格式不正确")
    
    if len(password) < 6:
        return error_response(400, "密码长度不能少于6位")
    
    if not real_name:
        return error_response(400, "真实姓名不能为空")
    
    if role not in ['super', 'manager', 'tester', 'admin']:
        return error_response(400, "无效的角色类型")
    if role == 'super' and username != 'Lethe':
        return error_response(400, "仅 Lethe 账号可设为超级管理员")
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return error_response(400, "用户名已存在")
    
    # 检查手机号是否已存在
    if User.query.filter_by(phone=phone).first():
        return error_response(400, "手机号已注册")
    
    # 创建新用户
    user = User(
        username=username,
        phone=phone,
        real_name=real_name,
        gender=gender,
        department=department,
        role=role
    )
    user.set_password(password)
    
    try:
        db.session.add(user)
        db.session.commit()
        
        log_user_action("创建用户", f"用户名: {username}, 角色: {role}")
        
        return success_response({
            'user': user.to_dict()
        }, "用户创建成功")
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, "用户创建失败，请稍后重试")


@bp.route('/<int:user_id>', methods=['PUT'])
@login_required
@permission_required('user.edit')
@validate_json_data(['real_name'])
def update_user(user_id):
    """更新用户信息"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    # 更新字段
    if 'real_name' in data:
        real_name = data['real_name'].strip()
        if not real_name:
            return error_response(400, "真实姓名不能为空")
        user.real_name = real_name
    
    if 'gender' in data:
        gender = data['gender']
        if gender in ['male', 'female', 'other']:
            user.gender = gender
    
    if 'department' in data:
        user.department = data['department'].strip()
    
    if 'phone' in data:
        phone = data['phone'].strip()
        if not validate_phone(phone):
            return error_response(400, "手机号格式不正确")
        
        # 检查手机号是否已被其他用户使用
        existing_user = User.query.filter(
            User.phone == phone, User.id != user_id
        ).first()
        if existing_user:
            return error_response(400, "手机号已被其他用户使用")
        
        user.phone = phone
    
    if 'role' in data:
        role = data['role']
        if role not in ['super', 'manager', 'tester', 'admin']:
            return error_response(400, "无效的角色类型")
        # 仅 Lethe 可拥有或保持超级管理员
        if role == 'super' and user.username != 'Lethe':
            return error_response(400, "仅 Lethe 账号可设为超级管理员")
        if user.username == 'Lethe':
            pass  # Lethe 角色固定，不应用修改，保持 super
        else:
            user.role = role
    
    if 'is_active' in data:
        user.is_active = data['is_active']
    
    try:
        db.session.commit()
        
        log_user_action("更新用户", f"用户ID: {user_id}")
        
        return success_response({
            'user': user.to_dict()
        }, "用户信息更新成功")
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, "用户信息更新失败，请稍后重试")


@bp.route('/<int:user_id>', methods=['DELETE'])
@login_required
@permission_required('user.delete')
def delete_user(user_id):
    """删除用户。如有关联引用则拒绝删除并返回引用信息。"""
    user = User.query.get_or_404(user_id)
    if user.username == 'Lethe':
        return error_response(400, "不可删除超级管理员账号")

    from app.models.models import (
        Project, ProjectMember, VersionRequirement, Iteration,
        TestSuite, TestCase, TestTask, TestCaseExecution,
        Device, TestSuiteReviewTask, TestCaseReviewDetail,
        TestSuiteReviewHistory, TestCaseReviewHistory,
    )

    refs = []
    n = Project.query.filter_by(owner_id=user_id).count()
    if n > 0:
        refs.append(f"项目负责人({n})")
    n = Project.query.filter_by(creator_id=user_id).count()
    if n > 0:
        refs.append(f"项目创建者({n})")
    n = ProjectMember.query.filter_by(user_id=user_id).count()
    if n > 0:
        refs.append(f"项目成员({n})")
    n = VersionRequirement.query.filter_by(created_by=user_id).count()
    if n > 0:
        refs.append(f"需求创建者({n})")
    n = VersionRequirement.query.filter_by(assigned_to=user_id).count()
    if n > 0:
        refs.append(f"需求负责人({n})")
    n = Iteration.query.filter_by(created_by=user_id).count()
    if n > 0:
        refs.append(f"迭代创建者({n})")
    n = Iteration.query.filter_by(updated_by=user_id).count()
    if n > 0:
        refs.append(f"迭代更新者({n})")
    n = TestSuite.query.filter_by(creator_id=user_id).count()
    if n > 0:
        refs.append(f"测试套件创建者({n})")
    n = TestCase.query.filter_by(creator_id=user_id).count()
    if n > 0:
        refs.append(f"测试用例创建者({n})")
    n = TestCase.query.filter_by(assignee_id=user_id).count()
    if n > 0:
        refs.append(f"测试用例负责人({n})")
    n = TestCase.query.filter_by(reviewer_id=user_id).count()
    if n > 0:
        refs.append(f"测试用例审核人({n})")
    n = TestTask.query.filter_by(creator_id=user_id).count()
    if n > 0:
        refs.append(f"测试任务创建者({n})")
    n = TestTask.query.filter_by(executor_id=user_id).count()
    if n > 0:
        refs.append(f"测试任务执行人({n})")
    n = TestCaseExecution.query.filter_by(executor_id=user_id).count()
    if n > 0:
        refs.append(f"用例执行记录执行人({n})")
    n = Device.query.filter_by(owner_id=user_id).count()
    if n > 0:
        refs.append(f"设备负责人({n})")
    n = TestSuiteReviewTask.query.filter_by(initiator_id=user_id).count()
    if n > 0:
        refs.append(f"用例集评审发起人({n})")
    n = TestSuiteReviewTask.query.filter_by(reviewer_id=user_id).count()
    if n > 0:
        refs.append(f"用例集评审人({n})")
    n = TestCaseReviewDetail.query.filter_by(reviewer_id=user_id).count()
    if n > 0:
        refs.append(f"用例集评审详情评审人({n})")
    n = TestSuiteReviewHistory.query.filter(
        db.or_(
            TestSuiteReviewHistory.initiator_id == user_id,
            TestSuiteReviewHistory.reviewer_id == user_id,
            TestSuiteReviewHistory.created_by == user_id,
        )
    ).count()
    if n > 0:
        refs.append(f"用例集评审历史({n})")
    n = TestCaseReviewHistory.query.filter(
        db.or_(
            TestCaseReviewHistory.reviewer_id == user_id,
            TestCaseReviewHistory.created_by == user_id,
        )
    ).count()
    if n > 0:
        refs.append(f"用例评审历史({n})")

    if refs:
        return error_response(
            400,
            "该用户存在关联数据，无法删除。当前引用：" + "、".join(refs) + "。请先解除或转移上述关联后再试。",
        )

    try:
        db.session.delete(user)
        db.session.commit()
        log_user_action("删除用户", f"用户名: {user.username}")
        return success_response(message="用户删除成功")
    except Exception as e:
        import traceback
        db.session.rollback()
        print(f"删除用户失败，详细错误: {traceback.format_exc()}")
        return error_response(500, f"用户删除失败: {str(e)}")


@bp.route('/<int:user_id>/reset-password', methods=['POST'])
@login_required
@permission_required('user.edit')
@validate_json_data(['new_password'])
def reset_user_password(user_id):
    """重置用户密码（需具备编辑用户权限）"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    new_password = data.get('new_password', '')
    
    if len(new_password) < 6:
        return error_response(400, "新密码长度不能少于6位")
    
    user.set_password(new_password)
    
    try:
        db.session.commit()
        
        log_user_action("重置密码", f"用户ID: {user_id}")
        
        return success_response(message="密码重置成功")
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, "密码重置失败，请稍后重试")


@bp.route('/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@permission_required('user.edit')
def toggle_user_status(user_id):
    """切换用户状态（启用/禁用）"""
    user = User.query.get_or_404(user_id)
    if user.username == 'Lethe':
        return error_response(400, "不可禁用超级管理员账号")
    # 切换用户状态
    user.is_active = not user.is_active
    
    try:
        db.session.commit()
        
        action = "禁用" if not user.is_active else "启用"
        log_user_action(f"{action}用户", f"用户ID: {user_id}, 用户名: {user.username}")
        
        return success_response({
            'user': user.to_dict()
        }, f"用户{action}成功")
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, "用户状态切换失败，请稍后重试")


@bp.route('/roles', methods=['GET'])
@login_required
def get_roles():
    """获取角色列表（下拉用），任意登录用户可调"""
    """获取角色列表"""
    roles = [
        {'value': 'super', 'label': '超级管理员'},
        {'value': 'manager', 'label': '管理员'},
        {'value': 'tester', 'label': '测试人员'},
        {'value': 'admin', 'label': '普通成员'}
    ]
    
    return success_response({
        'roles': roles
    })