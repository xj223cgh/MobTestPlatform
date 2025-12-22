from datetime import datetime, timezone, timedelta

# 设置本地时区为UTC+8
LOCAL_TIMEZONE = timezone(timedelta(hours=8))
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# 定义枚举类型的常量
TEST_CASE_STATUS = ('', 'pass', 'fail', 'blocked', 'not_applicable')
TEST_CASE_PRIORITY = ('P0', 'P1', 'P2', 'P3', 'P4')
TEST_SUITE_STATUS = ('active', 'inactive')
TEST_SUITE_TYPE = ('folder', 'suite')  # folder: 用例文件夹, suite: 用例集
TEST_SUITE_REVIEW_STATUS = ('not_submitted', 'pending', 'approved', 'rejected')  # 评审状态：未提交、待审核、已通过、已拒绝
TEST_TASK_STATUS = ('pending', 'running', 'completed', 'paused')
TEST_EXECUTION_STATUS = ('pass', 'fail', 'blocked', 'not_applicable')
PROJECT_STATUS = ('not_started', 'in_progress', 'paused', 'completed', 'closed')
PROJECT_ROLE = ('owner', 'manager', 'tester', 'viewer')
PROJECT_ENVIRONMENT = ('test', 'staging', 'production')
PROJECT_PRIORITY = ('high', 'medium', 'low')
ITERATION_STATUS = ('planning', 'active', 'completed', 'cancelled')

VERSION_REQUIREMENT_STATUS = ('new', 'in_progress', 'completed', 'cancelled')
REVIEW_TASK_STATUS = ('pending', 'in_review', 'completed', 'rejected')  # 评审任务状态：待处理、评审中、已完成、已拒绝
CASE_REVIEW_STATUS = ('pending', 'approved', 'rejected')  # 用例评审状态：待审核、已通过、已拒绝


class User(UserMixin, db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, comment='用户编号')
    username = db.Column(db.String(14), unique=True, nullable=False, comment='用户名（3-14个字节长度限制）')
    phone = db.Column(db.String(11), unique=True, nullable=False, comment='手机号（需要格式验证）')
    real_name = db.Column(db.String(50), nullable=False, comment='真实姓名')
    gender = db.Column(db.Enum('male', 'female', 'other'), default='other', comment='性别')
    department = db.Column(db.String(100), default='', comment='所属部门')
    password_hash = db.Column(db.String(255), nullable=False, comment='密码（哈希存储）')
    role = db.Column(db.Enum('super', 'manager', 'tester', 'admin'), nullable=False, default='admin', comment='角色类型')
    is_active = db.Column(db.Boolean, default=True, comment='是否激活')
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TIMEZONE), comment='创建时间')
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TIMEZONE), onupdate=lambda: datetime.now(LOCAL_TIMEZONE), comment='更新时间')
    
    # 关系
    created_devices = db.relationship('Device', backref='owner', lazy='dynamic', foreign_keys='Device.owner_id')
    created_cases = db.relationship('TestCase', lazy='dynamic', foreign_keys='TestCase.creator_id')
    created_tasks = db.relationship('TestTask', backref='creator', lazy='dynamic', foreign_keys='TestTask.creator_id')
    executed_tasks = db.relationship('TestTask', backref='executor', lazy='dynamic', foreign_keys='TestTask.executor_id')
    reported_bugs = db.relationship('Bug', backref='reporter', lazy='dynamic', foreign_keys='Bug.reporter_id')
    assigned_bugs = db.relationship('Bug', backref='assignee', lazy='dynamic', foreign_keys='Bug.assignee_id')
    created_tools = db.relationship('Tool', backref='creator', lazy='dynamic')
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'phone': self.phone,
            'real_name': self.real_name,
            'gender': self.gender,
            'department': self.department,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Project(db.Model):
    """项目模型"""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True, comment='项目编号')
    project_name = db.Column(db.String(200), nullable=False, unique=True, comment='项目名称')
    description = db.Column(db.Text, comment='项目描述')
    status = db.Column(db.Enum(*PROJECT_STATUS), default='not_started', comment='项目状态')
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment='项目负责人ID')
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment='项目创建者ID')
    start_date = db.Column(db.DateTime, comment='开始日期')
    end_date = db.Column(db.DateTime, comment='结束日期')
    tags = db.Column(db.Text, comment='项目标签，JSON格式存储')
    priority = db.Column(db.Enum(*PROJECT_PRIORITY), default='medium', comment='项目优先级')
    doc_url = db.Column(db.String(500), comment='项目文档链接')
    pipeline_url = db.Column(db.String(500), comment='流水线链接')
    is_deleted = db.Column(db.Boolean, default=False, comment='是否逻辑删除')
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TIMEZONE), comment='创建时间')
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TIMEZONE), onupdate=lambda: datetime.now(LOCAL_TIMEZONE), comment='更新时间')
    
    # 关系
    owner = db.relationship('User', backref='owned_projects', foreign_keys=[owner_id])
    creator = db.relationship('User', backref='created_projects', foreign_keys=[creator_id])
    project_members = db.relationship('ProjectMember', backref='project', cascade='all, delete-orphan')
    iterations = db.relationship('Iteration', backref='project', cascade='all, delete-orphan')
    test_suites = db.relationship('TestSuite', backref='project', cascade='all, delete-orphan')
    test_cases = db.relationship('TestCase', backref='project', cascade='all, delete-orphan')
    bugs = db.relationship('Bug', backref='project', cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典"""
        import json
        
        # 计算缺陷统计
        total_bugs = len(self.bugs)
        bug_stats = {
            'total': total_bugs,
            'open': sum(1 for bug in self.bugs if bug.status == 'open'),
            'in_progress': sum(1 for bug in self.bugs if bug.status == 'in_progress'),
            'resolved': sum(1 for bug in self.bugs if bug.status == 'resolved'),
            'closed': sum(1 for bug in self.bugs if bug.status == 'closed')
        }
        
        # 计算用例统计
        total_cases = len(self.test_cases)
        executed_cases = sum(1 for case in self.test_cases if hasattr(case, 'executions') and case.executions)
        passed_cases = sum(1 for case in self.test_cases if hasattr(case, 'executions') and any(exec.status == 'pass' for exec in case.executions))
        
        # 计算通过率和执行进度
        pass_rate = (passed_cases / executed_cases * 100) if executed_cases > 0 else 0
        execution_progress = (executed_cases / total_cases * 100) if total_cases > 0 else 0
        
        # 计算用例按状态划分
        case_stats = {
            'total': total_cases,
            'pass': sum(1 for case in self.test_cases if case.status == 'pass'),
            'fail': sum(1 for case in self.test_cases if case.status == 'fail'),
            'blocked': sum(1 for case in self.test_cases if case.status == 'blocked'),
            'not_applicable': sum(1 for case in self.test_cases if case.status == 'not_applicable'),
            'pass_rate': round(pass_rate, 2),
            'execution_progress': round(execution_progress, 2)
        }
        
        # 计算迭代统计
        total_iterations = len(self.iterations)
        iteration_stats = {
            'total': total_iterations,
            'planning': sum(1 for iter in self.iterations if iter.status == 'planning'),
            'active': sum(1 for iter in self.iterations if iter.status == 'active'),
            'completed': sum(1 for iter in self.iterations if iter.status == 'completed'),
            'cancelled': sum(1 for iter in self.iterations if iter.status == 'cancelled')
        }
        
        # 计算版本需求统计
        total_requirements = len(self.version_requirements)
        requirement_stats = {
            'total': total_requirements,
            'new': sum(1 for req in self.version_requirements if req.status == 'new'),
            'in_progress': sum(1 for req in self.version_requirements if req.status == 'in_progress'),
            'completed': sum(1 for req in self.version_requirements if req.status == 'completed'),
            'cancelled': sum(1 for req in self.version_requirements if req.status == 'cancelled')
        }
        
        # 处理项目成员，将user_id为NULL的成员显示为"未知用户"
        members = [{
            'user_id': member.user_id,
            'user_name': member.user.real_name if member.user else "未知用户",
            'role': member.role
        } for member in self.project_members]
        
        return {
            'id': self.id,
            'project_name': self.project_name,
            'description': self.description,
            'status': self.status,
            'owner_id': self.owner_id,
            'owner_name': self.owner.real_name if self.owner else None,
            'creator_id': self.creator_id,
            'creator_name': self.creator.real_name if self.creator else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'tags': json.loads(self.tags) if self.tags else [],
            'priority': self.priority,
            'doc_url': self.doc_url,
            'pipeline_url': self.pipeline_url,
            'is_deleted': self.is_deleted,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'member_count': len(self.project_members),
            'iteration_count': len(self.iterations),
            'requirement_count': total_requirements,
            'bug_stats': bug_stats,
            'case_stats': case_stats,
            'iteration_stats': iteration_stats,
            'requirement_stats': requirement_stats,
            'iterations': [iteration.iteration_name for iteration in self.iterations],
            'members': members
        }


class VersionRequirement(db.Model):
    """版本需求模型"""
    __tablename__ = 'version_requirements'
    
    id = db.Column(db.Integer, primary_key=True, comment='需求编号')
    requirement_name = db.Column(db.String(200), nullable=False, comment='需求名称')
    requirement_description = db.Column(db.Text, comment='需求描述')
    module = db.Column(db.String(100), nullable=True, comment='所属模块')
    status = db.Column(db.Enum(*VERSION_REQUIREMENT_STATUS), default='new', comment='需求状态')
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, comment='所属项目ID')
    iteration_id = db.Column(db.Integer, db.ForeignKey('iterations.id'), nullable=True, comment='所属迭代ID')
    priority = db.Column(db.Enum(*TEST_CASE_PRIORITY), default='medium', comment='优先级')
    environment = db.Column(db.Enum(*PROJECT_ENVIRONMENT), default='test', comment='需求环境')
    estimated_hours = db.Column(db.Float, comment='预估工时')
    actual_hours = db.Column(db.Float, comment='实际工时')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment='创建者ID')
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment='分配给ID')
    start_date = db.Column(db.DateTime, comment='开始时间')
    end_date = db.Column(db.DateTime, comment='结束时间')
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TIMEZONE), comment='创建时间')
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TIMEZONE), onupdate=lambda: datetime.now(LOCAL_TIMEZONE), comment='更新时间')
    is_deleted = db.Column(db.Boolean, default=False, comment='是否逻辑删除')
    
    # 关系
    project = db.relationship('Project', backref='version_requirements')
    iteration = db.relationship('Iteration', back_populates='version_requirements')
    creator = db.relationship('User', backref='created_requirements', foreign_keys=[created_by])
    assignee = db.relationship('User', backref='assigned_requirements', foreign_keys=[assigned_to])
    test_cases = db.relationship('TestCase', backref='version_requirement', uselist=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'requirement_name': self.requirement_name,
            'requirement_description': self.requirement_description,
            'module': self.module,
            'status': self.status,
            'project_id': self.project_id,
            'project_name': self.project.project_name if self.project else None,
            'iteration_id': self.iteration_id,
            'iteration_name': self.iteration.iteration_name if self.iteration else None,
            'priority': self.priority,
            'environment': self.environment,
            'estimated_hours': self.estimated_hours,
            'actual_hours': self.actual_hours,
            'created_by': self.created_by,
            'created_by_name': self.creator.real_name if self.creator else None,
            'assigned_to': self.assigned_to,
            'assigned_to_name': self.assignee.real_name if self.assignee else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_deleted': self.is_deleted,
            'has_test_cases': len(self.test_cases) > 0 if hasattr(self, 'test_cases') else False,
            'test_cases_count': len(self.test_cases) if hasattr(self, 'test_cases') else 0
        }


class ProjectMember(db.Model):
    """项目成员模型"""
    __tablename__ = 'project_members'
    
    id = db.Column(db.Integer, primary_key=True, comment='成员ID')
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, comment='项目ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment='用户ID')
    role = db.Column(db.Enum(*PROJECT_ROLE), default='tester', comment='项目角色')
    joined_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TIMEZONE), comment='加入时间')
    
    # 唯一约束，确保用户在项目中只有一个角色
    # 注意：MySQL不支持NULL值的唯一约束，所以这个约束只在user_id不为NULL时生效
    __table_args__ = (db.UniqueConstraint('project_id', 'user_id', name='_project_user_uc'),)
    
    # 关系
    user = db.relationship('User', backref=db.backref('project_memberships', cascade='all, delete-orphan'))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'user_id': self.user_id,
            'user_name': self.user.real_name if self.user else None,
            'user_username': self.user.username if self.user else None,
            'user_department': self.user.department if self.user else None,
            'role': self.role,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None
        }


class Iteration(db.Model):
    """迭代模型"""
    __tablename__ = 'iterations'
    
    id = db.Column(db.Integer, primary_key=True, comment='迭代编号')
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, comment='所属项目ID')
    iteration_name = db.Column(db.String(200), nullable=False, comment='迭代名称')
    description = db.Column(db.Text, comment='迭代描述')
    goal = db.Column(db.Text, comment='迭代目标')
    status = db.Column(db.Enum(*ITERATION_STATUS), default='planning', comment='迭代状态')
    start_date = db.Column(db.DateTime, nullable=False, comment='开始日期')
    end_date = db.Column(db.DateTime, nullable=False, comment='结束日期')
    version = db.Column(db.String(100), comment='版本信息')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment='创建者ID')
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment='更新者ID')
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TIMEZONE), comment='创建时间')
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TIMEZONE), onupdate=lambda: datetime.now(LOCAL_TIMEZONE), comment='更新时间')
    
    # 关系

    test_tasks = db.relationship('TestTask', backref='iteration', cascade='all, delete-orphan')
    version_requirements = db.relationship('VersionRequirement', back_populates='iteration', cascade='all, delete-orphan')
    case_executions = db.relationship('TestCaseExecution', back_populates='iteration', cascade='all, delete-orphan')
    bugs = db.relationship('Bug', backref='iteration', cascade='all, delete-orphan')
    creator = db.relationship('User', backref='created_iterations', foreign_keys=[created_by])
    updater = db.relationship('User', backref='updated_iterations', foreign_keys=[updated_by])
    
    def to_dict(self):
        """转换为字典"""
        # 计算需求统计
        requirement_stats = {
            'total': len(self.version_requirements),
            'new': sum(1 for req in self.version_requirements if req.status == 'new'),
            'in_progress': sum(1 for req in self.version_requirements if req.status == 'in_progress'),
            'completed': sum(1 for req in self.version_requirements if req.status == 'completed'),
            'cancelled': sum(1 for req in self.version_requirements if req.status == 'cancelled')
        }
        
        # 计算用例执行统计
        executions = []
        for req in self.version_requirements:
            if req.test_cases:
                for test_case in req.test_cases:
                    if test_case.executions:
                        executions.extend(test_case.executions)
        execution_stats = {
            'total': len(executions),
            'pass': sum(1 for exec in executions if exec.status == 'pass'),
            'fail': sum(1 for exec in executions if exec.status == 'fail'),
            'blocked': sum(1 for exec in executions if exec.status == 'blocked'),
            'not_applicable': sum(1 for exec in executions if exec.status == 'not_applicable')
        }
        
        # 计算缺陷统计
        bug_stats = {
            'total': len(self.bugs),
            'open': sum(1 for bug in self.bugs if bug.status == 'open'),
            'in_progress': sum(1 for bug in self.bugs if bug.status == 'in_progress'),
            'resolved': sum(1 for bug in self.bugs if bug.status == 'resolved'),
            'closed': sum(1 for bug in self.bugs if bug.status == 'closed')
        }
        
        return {
            'id': self.id,
            'project_id': self.project_id,
            'project_name': self.project.project_name if self.project else None,
            'iteration_name': self.iteration_name,
            'description': self.description,
            'goal': self.goal,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'version': self.version,
            'created_by': self.created_by,
            'created_by_name': self.creator.real_name if self.creator else None,
            'updated_by': self.updated_by,
            'updated_by_name': self.updater.real_name if self.updater else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'test_task_count': len(self.test_tasks),
            'requirement_count': len(self.version_requirements),
            'bug_count': len(self.bugs),
            'requirement_stats': requirement_stats,
            'execution_stats': execution_stats,
            'bug_stats': bug_stats,
            # 返回完整的列表数据
            'version_requirements': [req.to_dict() for req in self.version_requirements],
            'test_tasks': [task.to_dict() for task in self.test_tasks],
            'bugs': [bug.to_dict() for bug in self.bugs]
        }





class Device(db.Model):
    """设备模型"""
    __tablename__ = 'devices'
    
    id = db.Column(db.Integer, primary_key=True, comment='设备编号')
    device_name = db.Column(db.String(100), nullable=False, comment='设备名称')
    device_model = db.Column(db.String(100), nullable=False, comment='设备型号')
    os_type = db.Column(db.Enum('android', 'ios'), nullable=False, comment='操作系统类型')
    os_version = db.Column(db.String(50), nullable=False, comment='操作系统版本')
    device_id = db.Column(db.String(100), unique=True, nullable=False, comment='设备唯一标识')
    status = db.Column(db.Enum('online', 'offline', 'busy', 'maintenance'), default='offline', comment='设备状态')
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment='设备负责人ID')
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TIMEZONE), comment='创建时间')
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TIMEZONE), onupdate=lambda: datetime.now(LOCAL_TIMEZONE), comment='更新时间')
    
    # 关系
    test_tasks = db.relationship('TestTask', backref='device', lazy='dynamic')
    bugs = db.relationship('Bug', backref='device', lazy='dynamic')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'device_name': self.device_name,
            'device_model': self.device_model,
            'os_type': self.os_type,
            'os_version': self.os_version,
            'device_id': self.device_id,
            'status': self.status,
            'owner_id': self.owner_id,
            'owner_name': self.owner.real_name if self.owner else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class TestSuite(db.Model):
    """测试套件/用例集模型"""
    __tablename__ = 'test_suites'
    
    id = db.Column(db.Integer, primary_key=True, comment='套件编号')
    suite_name = db.Column(db.String(200), nullable=False, comment='套件名称')
    description = db.Column(db.Text, comment='套件描述')
    parent_id = db.Column(db.Integer, db.ForeignKey('test_suites.id'), nullable=True, comment='父套件ID，用于构建目录结构')
    status = db.Column(db.Enum(*TEST_SUITE_STATUS), default='active', comment='状态')
    type = db.Column(db.Enum(*TEST_SUITE_TYPE), default='folder', comment='类型：folder-用例文件夹, suite-用例集')
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment='创建者ID')
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, comment='所属项目ID')
    version_requirement_id = db.Column(db.Integer, db.ForeignKey('version_requirements.id'), nullable=True, comment='关联的版本需求ID')
    iteration_id = db.Column(db.Integer, db.ForeignKey('iterations.id'), nullable=True, comment='所属迭代ID')
    sort_order = db.Column(db.Integer, default=0, comment='排序顺序')
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TIMEZONE), comment='创建时间')
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TIMEZONE), onupdate=lambda: datetime.now(LOCAL_TIMEZONE), comment='更新时间')
    
    # 关系
    # 自引用关系，用于构建目录树结构
    parent = db.relationship('TestSuite', remote_side=[id], backref=db.backref('children', order_by='TestSuite.sort_order'))
    # 与测试用例的一对多关系
    test_cases = db.relationship('TestCase', backref='suite', lazy='dynamic')
    # 与用户的多对一关系
    creator = db.relationship('User', backref='created_suites', foreign_keys=[creator_id])
    # 与版本需求的多对一关系
    version_requirement = db.relationship('VersionRequirement', backref='test_suites')
    # 与迭代的多对一关系
    iteration = db.relationship('Iteration', backref='test_suites')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'suite_name': self.suite_name,
            'description': self.description,
            'parent_id': self.parent_id,
            'status': self.status,
            'type': self.type,
            'creator_id': self.creator_id,
            'creator_name': self.creator.real_name if self.creator else None,
            'project_id': self.project_id,
            'project_name': self.project.project_name if self.project else None,
            'version_requirement_id': self.version_requirement_id,
            'version_requirement_name': self.version_requirement.requirement_name if self.version_requirement else None,
            'iteration_id': self.iteration_id,
            'iteration_name': self.iteration.iteration_name if self.iteration else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'sort_order': self.sort_order,
            'children_count': len(self.children),
            'cases_count': self.test_cases.count()
        }


class TestSuiteReviewTask(db.Model):
    """用例集评审任务模型"""
    __tablename__ = 'test_suite_review_tasks'
    
    id = db.Column(db.Integer, primary_key=True, comment='评审任务ID')
    suite_id = db.Column(db.Integer, db.ForeignKey('test_suites.id', ondelete='CASCADE'), nullable=False, comment='关联用例集ID')
    initiator_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment='发起人ID')
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment='评审人ID')
    status = db.Column(db.Enum(*REVIEW_TASK_STATUS), default='pending', comment='评审任务状态：pending-待处理, in_review-评审中, completed-已完成')
    start_time = db.Column(db.DateTime(timezone=True), nullable=True, comment='评审开始时间')
    end_time = db.Column(db.DateTime(timezone=True), nullable=True, comment='评审结束时间')
    overall_comments = db.Column(db.Text, comment='整体评审意见')
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TIMEZONE), comment='创建时间')
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TIMEZONE), onupdate=lambda: datetime.now(LOCAL_TIMEZONE), comment='更新时间')
    
    # 关系
    suite = db.relationship('TestSuite', backref='review_tasks')
    initiator = db.relationship('User', backref='initiated_review_tasks', foreign_keys=[initiator_id])
    reviewer = db.relationship('User', backref='assigned_review_tasks', foreign_keys=[reviewer_id])
    case_reviews = db.relationship('TestCaseReviewDetail', backref='review_task', cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'suite_id': self.suite_id,
            'initiator_id': self.initiator_id,
            'initiator_name': self.initiator.real_name if self.initiator else None,
            'reviewer_id': self.reviewer_id,
            'reviewer_name': self.reviewer.real_name if self.reviewer else None,
            'status': self.status,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S') if self.start_time else None,
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else None,
            'overall_comments': self.overall_comments,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class TestCaseReviewDetail(db.Model):
    """用例评审详情模型"""
    __tablename__ = 'test_case_review_details'
    
    id = db.Column(db.Integer, primary_key=True, comment='评审详情ID')
    review_task_id = db.Column(db.Integer, db.ForeignKey('test_suite_review_tasks.id', ondelete='CASCADE'), nullable=False, comment='关联评审任务ID')
    case_id = db.Column(db.Integer, db.ForeignKey('test_cases.id', ondelete='CASCADE'), nullable=False, comment='关联测试用例ID')
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment='评审人ID')
    review_status = db.Column(db.Enum(*CASE_REVIEW_STATUS), default='pending', comment='单条用例评审状态：pending-待审核, approved-已通过, rejected-已拒绝')
    comments = db.Column(db.Text, comment='用例评审意见')
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TIMEZONE), comment='创建时间')
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TIMEZONE), onupdate=lambda: datetime.now(LOCAL_TIMEZONE), comment='更新时间')
    
    # 关系
    reviewer = db.relationship('User', backref='case_reviews', foreign_keys=[reviewer_id])
    test_case = db.relationship('TestCase', backref='review_details')
    
    # 唯一约束，确保每条用例在一个评审任务中只有一条记录
    __table_args__ = (db.UniqueConstraint('review_task_id', 'case_id', name='_review_task_case_uc'),)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'review_task_id': self.review_task_id,
            'case_id': self.case_id,
            'reviewer_id': self.reviewer_id,
            'reviewer_name': self.reviewer.real_name if self.reviewer else None,
            'review_status': self.review_status,
            'comments': self.comments,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# 评审历史记录相关模型
# 评审历史记录类型枚举
REVIEW_HISTORY_TYPE = ('complete', 'reject')  # 评审历史记录类型：complete-完成评审, reject-打回评审


class TestSuiteReviewHistory(db.Model):
    """评审历史记录模型"""
    __tablename__ = 'test_suite_review_history'
    
    id = db.Column(db.Integer, primary_key=True, comment='评审历史ID')
    review_task_id = db.Column(db.Integer, db.ForeignKey('test_suite_review_tasks.id', ondelete='SET NULL'), nullable=True, comment='关联评审任务ID')
    suite_id = db.Column(db.Integer, db.ForeignKey('test_suites.id', ondelete='SET NULL'), nullable=True, comment='关联用例集ID')
    initiator_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment='发起人ID')
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment='评审人ID')
    status = db.Column(db.Enum(*REVIEW_TASK_STATUS), comment='评审任务状态')
    start_time = db.Column(db.DateTime(timezone=True), nullable=True, comment='评审开始时间')
    end_time = db.Column(db.DateTime(timezone=True), nullable=True, comment='评审结束时间')
    overall_comments = db.Column(db.Text, comment='整体评审意见')
    history_type = db.Column(db.Enum(*REVIEW_HISTORY_TYPE), comment='历史记录类型：complete-完成评审, reject-打回评审')
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TIMEZONE), comment='创建时间')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment='创建人ID')
    version = db.Column(db.Integer, default=1, comment='评审版本号')
    
    # 关系
    review_task = db.relationship('TestSuiteReviewTask', backref='review_history')
    suite = db.relationship('TestSuite', backref='review_history')
    initiator = db.relationship('User', backref='initiated_review_history', foreign_keys=[initiator_id])
    reviewer = db.relationship('User', backref='assigned_review_history', foreign_keys=[reviewer_id])
    created_user = db.relationship('User', foreign_keys=[created_by])
    case_review_history = db.relationship('TestCaseReviewHistory', backref='review_history', cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'review_task_id': self.review_task_id,
            'suite_id': self.suite_id,
            'initiator_id': self.initiator_id,
            'initiator_name': self.initiator.real_name if self.initiator else None,
            'reviewer_id': self.reviewer_id,
            'reviewer_name': self.reviewer.real_name if self.reviewer else None,
            'status': self.status,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S') if self.start_time else None,
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else None,
            'overall_comments': self.overall_comments,
            'history_type': self.history_type,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'created_by': self.created_by,
            'created_by_name': self.created_user.real_name if self.created_user else None,
            'version': self.version
        }


class TestCaseReviewHistory(db.Model):
    """用例评审历史记录模型"""
    __tablename__ = 'test_case_review_history'
    
    id = db.Column(db.Integer, primary_key=True, comment='用例评审历史ID')
    review_history_id = db.Column(db.Integer, db.ForeignKey('test_suite_review_history.id', ondelete='CASCADE'), nullable=False, comment='关联评审历史ID')
    review_task_id = db.Column(db.Integer, nullable=True, comment='关联评审任务ID')
    case_id = db.Column(db.Integer, db.ForeignKey('test_cases.id', ondelete='SET NULL'), nullable=True, comment='关联测试用例ID')
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment='评审人ID')
    review_status = db.Column(db.Enum(*CASE_REVIEW_STATUS), default='pending', comment='单条用例评审状态')
    comments = db.Column(db.Text, comment='用例评审意见')
    # 用例属性快照
    case_number = db.Column(db.String(50), nullable=True, comment='用例编号')
    case_name = db.Column(db.String(200), nullable=True, comment='用例名称')
    priority = db.Column(db.Enum(*TEST_CASE_PRIORITY), default='P1', comment='优先级')
    test_data = db.Column(db.Text, nullable=True, comment='测试数据')
    preconditions = db.Column(db.Text, comment='前置条件')
    steps = db.Column(db.Text, comment='测试步骤')
    expected_result = db.Column(db.Text, comment='预期结果')
    actual_result = db.Column(db.Text, comment='实际结果')
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TIMEZONE), comment='创建时间')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment='创建人ID')
    
    # 关系
    reviewer = db.relationship('User', foreign_keys=[reviewer_id])
    test_case = db.relationship('TestCase', backref='review_history')
    created_user = db.relationship('User', foreign_keys=[created_by])
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'review_history_id': self.review_history_id,
            'review_task_id': self.review_task_id,
            'case_id': self.case_id,
            'reviewer_id': self.reviewer_id,
            'reviewer_name': self.reviewer.real_name if self.reviewer else None,
            'review_status': self.review_status,
            'comments': self.comments,
            'case_number': self.case_number,
            'case_name': self.case_name,
            'priority': self.priority,
            'test_data': self.test_data,
            'preconditions': self.preconditions,
            'steps': self.steps,
            'expected_result': self.expected_result,
            'actual_result': self.actual_result,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'created_by': self.created_by,
            'created_by_name': self.created_user.real_name if self.created_user else None
        }


class TestCase(db.Model):
    """测试用例模型"""
    __tablename__ = 'test_cases'
    
    id = db.Column(db.Integer, primary_key=True, comment='数据库自增ID')
    case_number = db.Column(db.String(50), nullable=True, comment='测试用例编号')
    case_name = db.Column(db.String(200), nullable=False, comment='用例名称')
    case_description = db.Column(db.Text, comment='用例描述')
    priority = db.Column(db.Enum(*TEST_CASE_PRIORITY), default='P1', comment='优先级')
    status = db.Column(db.Enum(*TEST_CASE_STATUS), default='', comment='状态')
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment='创建者ID')
    suite_id = db.Column(db.Integer, db.ForeignKey('test_suites.id'), nullable=False, comment='所属套件ID（用于模块树）')
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, comment='所属项目ID')
    version_requirement_id = db.Column(db.Integer, db.ForeignKey('version_requirements.id'), nullable=True, comment='关联的版本需求ID')
    iteration_id = db.Column(db.Integer, db.ForeignKey('iterations.id'), nullable=True, comment='所属迭代ID')
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment='负责人ID')
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment='审核人ID')
    
    # 用例内容
    preconditions = db.Column(db.Text, comment='前置条件')
    steps = db.Column(db.Text, comment='测试步骤')
    expected_result = db.Column(db.Text, comment='预期结果')
    actual_result = db.Column(db.Text, comment='实际结果')
    test_data = db.Column(db.Text, nullable=True, comment='测试数据')
    
    # 时间字段
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TIMEZONE), comment='创建时间')
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TIMEZONE), onupdate=lambda: datetime.now(LOCAL_TIMEZONE), comment='更新时间')
    executed_at = db.Column(db.DateTime(timezone=True), nullable=True, comment='最后执行时间')
    last_reviewed_at = db.Column(db.DateTime(timezone=True), nullable=True, comment='最后评审时间')
    
    # 审核信息
    review_comments = db.Column(db.Text, comment='审核意见')
    
    # 关系
    test_tasks = db.relationship('TestTask', secondary='task_case_relation', backref='test_cases')
    bugs = db.relationship('Bug', backref='test_case', lazy='dynamic')
    # 移除backref参数，避免与User模型中的created_cases冲突
    creator = db.relationship('User', foreign_keys=[creator_id], overlaps="created_cases")
    assignee = db.relationship('User', backref='assigned_cases', foreign_keys=[assignee_id])
    reviewer = db.relationship('User', foreign_keys=[reviewer_id])
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'case_number': self.case_number,
            'case_name': self.case_name,
            'case_description': self.case_description,
            'priority': self.priority,
            'status': self.status,
            'creator_id': self.creator_id,
            'creator_name': self.creator.real_name if self.creator else None,
            'suite_id': self.suite_id,
            'suite_name': self.suite.suite_name if self.suite else None,
            # 从套件继承项目、需求、迭代信息
            'project_id': self.suite.project_id if self.suite else self.project_id,
            'project_name': self.suite.project.project_name if self.suite and self.suite.project else None,
            'version_requirement_id': self.suite.version_requirement_id if self.suite else self.version_requirement_id,
            'version_requirement_name': self.suite.version_requirement.requirement_name if self.suite and self.suite.version_requirement else None,
            'iteration_id': self.suite.iteration_id if self.suite else self.iteration_id,
            'iteration_name': self.suite.iteration.iteration_name if self.suite and self.suite.iteration else None,
            'assignee_id': self.assignee_id,
            'assignee_name': self.assignee.real_name if hasattr(self, 'assignee') and self.assignee else None,
            'reviewer_id': self.reviewer_id,
            'reviewer_name': self.reviewer.real_name if hasattr(self, 'reviewer') and self.reviewer else None,
            'preconditions': self.preconditions,
            'steps': self.steps,
            'expected_result': self.expected_result,
            'actual_result': self.actual_result,
            'test_data': self.test_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'last_reviewed_at': self.last_reviewed_at.isoformat() if self.last_reviewed_at else None,
            'review_comments': self.review_comments
        }


# 测试任务和测试用例的关联表
task_case_relation = db.Table('task_case_relation',
    db.Column('task_id', db.Integer, db.ForeignKey('test_tasks.id'), primary_key=True),
    db.Column('case_id', db.Integer, db.ForeignKey('test_cases.id'), primary_key=True)
)


class TestCaseExecution(db.Model):
    """测试用例执行结果模型"""
    __tablename__ = 'test_case_executions'
    
    id = db.Column(db.Integer, primary_key=True, comment='执行记录ID')
    task_id = db.Column(db.Integer, db.ForeignKey('test_tasks.id'), nullable=False, comment='测试任务ID')
    case_id = db.Column(db.Integer, db.ForeignKey('test_cases.id'), nullable=False, comment='测试用例ID')
    # 添加项目和迭代关联
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True, comment='所属项目ID')
    iteration_id = db.Column(db.Integer, db.ForeignKey('iterations.id'), nullable=True, comment='所属迭代ID')
    status = db.Column(db.Enum(*TEST_EXECUTION_STATUS), comment='执行状态：通过、失败、阻塞、不适用')
    executor_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment='执行人ID')
    execution_time = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TIMEZONE), comment='执行时间')
    notes = db.Column(db.Text, comment='执行备注')
    
    # 关系
    task = db.relationship('TestTask', backref='case_executions')
    test_case = db.relationship('TestCase', backref='executions')
    executor = db.relationship('User', backref='executed_cases')
    # 与项目的多对一关系
    project = db.relationship('Project', backref='executions')
    # 与迭代的多对一关系
    iteration = db.relationship('Iteration', back_populates='case_executions')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'case_id': self.case_id,
            'project_id': self.project_id,
            'project_name': self.project.project_name if self.project else None,
            'iteration_id': self.iteration_id,
            'iteration_name': self.iteration.iteration_name if self.iteration else None,
            'status': self.status,
            'executor': {
                'id': self.executor.id,
                'username': self.executor.username
            } if self.executor else None,
            'execution_time': self.execution_time.isoformat() if self.execution_time else None,
            'notes': self.notes,
            'case_info': {
                'id': self.test_case.id,
                'case_name': self.test_case.case_name
            } if self.test_case else None
        }


class TestTask(db.Model):
    """测试任务模型"""
    __tablename__ = 'test_tasks'
    
    id = db.Column(db.Integer, primary_key=True, comment='任务编号')
    task_name = db.Column(db.String(200), nullable=False, comment='任务名称')
    task_description = db.Column(db.Text, comment='任务描述')
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False, comment='测试设备ID')
    # 添加项目和迭代关联
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True, comment='所属项目ID')
    iteration_id = db.Column(db.Integer, db.ForeignKey('iterations.id'), nullable=True, comment='所属迭代ID')
    status = db.Column(db.Enum(*TEST_TASK_STATUS), default='pending', comment='任务状态')
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment='创建者ID')
    executor_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment='执行者ID')
    # 添加与测试套件的关联
    suite_id = db.Column(db.Integer, db.ForeignKey('test_suites.id'), nullable=True, comment='关联的测试套件ID')
    # 添加任务相关信息
    documentation_url = db.Column(db.Text, comment='相关文档链接')
    version_info = db.Column(db.String(100), comment='版本信息')
    scheduled_time = db.Column(db.DateTime(timezone=True), comment='计划执行时间')
    started_time = db.Column(db.DateTime(timezone=True), comment='开始执行时间')
    completed_time = db.Column(db.DateTime(timezone=True), comment='完成时间')
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TIMEZONE), comment='创建时间')
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TIMEZONE), onupdate=lambda: datetime.now(LOCAL_TIMEZONE), comment='更新时间')
    # 添加缺失的字段
    case_ids = db.Column(db.Text, nullable=False, comment='测试用例ID列表，JSON格式存储')
    
    # 关系
    bugs = db.relationship('Bug', backref='test_task', lazy='dynamic')
    # 与测试套件的多对一关系
    suite = db.relationship('TestSuite', backref='test_tasks')
    # 与项目的多对一关系
    project = db.relationship('Project', backref='test_tasks')
    
    def to_dict(self):
        """转换为字典"""
        # 统计执行结果
        executions = self.case_executions.all() if hasattr(self, 'case_executions') else []
        pass_count = sum(1 for e in executions if e.status == 'pass')
        fail_count = sum(1 for e in executions if e.status == 'fail')
        blocked_count = sum(1 for e in executions if e.status == 'blocked')
        not_applicable_count = sum(1 for e in executions if e.status == 'not_applicable')
        total_executed = len(executions)
        
        # 计算通过率
        pass_rate = (pass_count / total_executed * 100) if total_executed > 0 else 0
        
        return {
            'id': self.id,
            'task_name': self.task_name,
            'task_description': self.task_description,
            'device_id': self.device_id,
            'device_name': self.device.device_name if self.device else None,
            'project_id': self.project_id,
            'project_name': self.project.project_name if self.project else None,
            'iteration_id': self.iteration_id,
            'iteration_name': self.iteration.iteration_name if self.iteration else None,
            'status': self.status,
            'creator_id': self.creator_id,
            'creator_name': self.creator.real_name if self.creator else None,
            'executor_id': self.executor_id,
            'executor_name': self.executor.real_name if self.executor else None,
            'suite_id': self.suite_id,
            'suite_name': self.suite.suite_name if self.suite else None,
            'documentation_url': self.documentation_url,
            'version_info': self.version_info,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'started_time': self.started_time.isoformat() if self.started_time else None,
            'completed_time': self.completed_time.isoformat() if self.completed_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            # 统计信息
            'statistics': {
                'pass_count': pass_count,
                'fail_count': fail_count,
                'blocked_count': blocked_count,
                'not_applicable_count': not_applicable_count,
                'total_executed': total_executed,
                'pass_rate': round(pass_rate, 2)
            }
        }


class Bug(db.Model):
    """缺陷模型"""
    __tablename__ = 'bugs'
    
    id = db.Column(db.Integer, primary_key=True, comment='缺陷编号')
    bug_title = db.Column(db.String(200), nullable=False, comment='缺陷标题')
    bug_description = db.Column(db.Text, nullable=False, comment='缺陷描述')
    severity = db.Column(db.Enum('critical', 'high', 'medium', 'low'), default='medium', comment='严重程度')
    priority = db.Column(db.Enum('high', 'medium', 'low'), default='medium', comment='优先级')
    status = db.Column(db.Enum('open', 'in_progress', 'resolved', 'closed', 'reopened'), default='open', comment='状态')
    module = db.Column(db.String(100), nullable=False, comment='所属模块')
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), comment='相关设备ID')
    case_id = db.Column(db.Integer, db.ForeignKey('test_cases.id'), comment='相关用例ID')
    task_id = db.Column(db.Integer, db.ForeignKey('test_tasks.id'), comment='相关任务ID')
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment='报告者ID')
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment='分配给ID')
    # 添加与项目和迭代的关联
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True, comment='所属项目ID')
    iteration_id = db.Column(db.Integer, db.ForeignKey('iterations.id'), nullable=True, comment='所属迭代ID')
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TIMEZONE), comment='创建时间')
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TIMEZONE), onupdate=lambda: datetime.now(LOCAL_TIMEZONE), comment='更新时间')
    resolved_at = db.Column(db.DateTime(timezone=True), comment='解决时间')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'bug_title': self.bug_title,
            'bug_description': self.bug_description,
            'severity': self.severity,
            'priority': self.priority,
            'status': self.status,
            'module': self.module,
            'device_id': self.device_id,
            'device_name': self.device.device_name if self.device else None,
            'case_id': self.case_id,
            'case_name': self.test_case.case_name if self.test_case else None,
            'task_id': self.task_id,
            'task_name': self.test_task.task_name if self.test_task else None,
            'reporter_id': self.reporter_id,
            'reporter_name': self.reporter.real_name if self.reporter else None,
            'assignee_id': self.assignee_id,
            'assignee_name': self.assignee.real_name if self.assignee else None,
            'project_id': self.project_id,
            'project_name': self.project.project_name if hasattr(self, 'project') and self.project else None,
            'iteration_id': self.iteration_id,
            'iteration_name': self.iteration.iteration_name if hasattr(self, 'iteration') and self.iteration else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }


class Tool(db.Model):
    """工具模型"""
    __tablename__ = 'tools'
    
    id = db.Column(db.Integer, primary_key=True, comment='工具编号')
    tool_name = db.Column(db.String(100), nullable=False, comment='工具名称')
    tool_description = db.Column(db.Text, comment='工具描述')
    tool_type = db.Column(db.Enum('automation', 'performance', 'monitoring', 'debugging', 'utility'), nullable=False, comment='工具类型')
    tool_path = db.Column(db.String(500), nullable=False, comment='工具路径')
    tool_config = db.Column(db.Text, comment='工具配置（JSON格式）')
    status = db.Column(db.Enum('active', 'inactive', 'maintenance'), default='active', comment='状态')
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment='创建者ID')
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TIMEZONE), comment='创建时间')
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TIMEZONE), onupdate=lambda: datetime.now(LOCAL_TIMEZONE), comment='更新时间')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'tool_name': self.tool_name,
            'tool_description': self.tool_description,
            'tool_type': self.tool_type,
            'tool_path': self.tool_path,
            'tool_config': self.tool_config,
            'status': self.status,
            'creator_id': self.creator_id,
            'creator_name': self.creator.real_name if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ExecutionBugRelation(db.Model):
    """执行记录与缺陷关联模型"""
    __tablename__ = 'execution_bug_relations'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='关联编号')
    execution_id = db.Column(db.Integer, db.ForeignKey('test_case_executions.id'), nullable=False, comment='执行记录ID')
    bug_id = db.Column(db.Integer, db.ForeignKey('bugs.id'), nullable=False, comment='缺陷ID')
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TIMEZONE), comment='创建时间')
    
    # 关系
    execution = db.relationship('TestCaseExecution', backref='bug_relations')
    bug = db.relationship('Bug', backref='execution_relations')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'execution_id': self.execution_id,
            'bug_id': self.bug_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


