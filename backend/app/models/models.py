from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# 定义枚举类型的常量
TEST_CASE_STATUS = ('draft', 'active', 'deprecated')
TEST_CASE_PRIORITY = ('high', 'medium', 'low')
TEST_SUITE_STATUS = ('active', 'inactive')
TEST_TASK_STATUS = ('pending', 'running', 'completed', 'paused')
TEST_EXECUTION_STATUS = ('pass', 'fail', 'blocked', 'not_applicable')
PROJECT_STATUS = ('not_started', 'in_progress', 'paused', 'completed', 'closed')
PROJECT_ROLE = ('owner', 'manager', 'tester', 'viewer')
PROJECT_ENVIRONMENT = ('test', 'staging', 'production')
PROJECT_PRIORITY = ('high', 'medium', 'low')
ITERATION_STATUS = ('planning', 'active', 'completed', 'cancelled')
TEST_PLAN_STATUS = ('draft', 'active', 'completed', 'cancelled')
VERSION_REQUIREMENT_STATUS = ('new', 'in_progress', 'completed', 'cancelled')


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
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系
    created_devices = db.relationship('Device', backref='owner', lazy='dynamic', foreign_keys='Device.owner_id')
    created_cases = db.relationship('TestCase', backref='case_creator', lazy='dynamic')
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
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='项目负责人ID')
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='项目创建者ID')
    start_date = db.Column(db.DateTime, comment='开始日期')
    end_date = db.Column(db.DateTime, comment='结束日期')
    tags = db.Column(db.Text, comment='项目标签，JSON格式存储')
    priority = db.Column(db.Enum(*PROJECT_PRIORITY), default='medium', comment='项目优先级')
    doc_url = db.Column(db.String(500), comment='项目文档链接')
    pipeline_url = db.Column(db.String(500), comment='流水线链接')
    is_deleted = db.Column(db.Boolean, default=False, comment='是否逻辑删除')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系
    owner = db.relationship('User', backref='owned_projects', foreign_keys=[owner_id])
    creator = db.relationship('User', backref='created_projects', foreign_keys=[creator_id])
    project_members = db.relationship('ProjectMember', backref='project', cascade='all, delete-orphan')
    iterations = db.relationship('Iteration', backref='project', cascade='all, delete-orphan')
    test_plans = db.relationship('TestPlan', backref='project', cascade='all, delete-orphan')
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
        
        # 计算用例按类型划分
        case_stats = {
            'total': total_cases,
            'draft': sum(1 for case in self.test_cases if case.status == 'draft'),
            'active': sum(1 for case in self.test_cases if case.status == 'active'),
            'deprecated': sum(1 for case in self.test_cases if case.status == 'deprecated'),
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
            'test_plan_count': len(self.test_plans),
            'requirement_count': total_requirements,
            'bug_stats': bug_stats,
            'case_stats': case_stats,
            'iteration_stats': iteration_stats,
            'requirement_stats': requirement_stats,
            'iterations': [iteration.iteration_name for iteration in self.iterations]
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
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='创建者ID')
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), comment='分配给ID')
    start_date = db.Column(db.DateTime, comment='开始时间')
    end_date = db.Column(db.DateTime, comment='结束时间')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    is_deleted = db.Column(db.Boolean, default=False, comment='是否逻辑删除')
    
    # 关系
    project = db.relationship('Project', backref='version_requirements')
    iteration = db.relationship('Iteration', back_populates='version_requirements')
    creator = db.relationship('User', backref='created_requirements', foreign_keys=[created_by])
    assignee = db.relationship('User', backref='assigned_requirements', foreign_keys=[assigned_to])
    test_case = db.relationship('TestCase', backref='version_requirement', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'requirement_name': self.requirement_name,
            'requirement_description': self.requirement_description,
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
            'has_test_case': self.test_case is not None
        }


class ProjectMember(db.Model):
    """项目成员模型"""
    __tablename__ = 'project_members'
    
    id = db.Column(db.Integer, primary_key=True, comment='成员ID')
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, comment='项目ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    role = db.Column(db.Enum(*PROJECT_ROLE), default='tester', comment='项目角色')
    joined_at = db.Column(db.DateTime, default=datetime.utcnow, comment='加入时间')
    
    # 唯一约束，确保用户在项目中只有一个角色
    __table_args__ = (db.UniqueConstraint('project_id', 'user_id', name='_project_user_uc'),)
    
    # 关系
    user = db.relationship('User', backref='project_memberships')
    
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
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), comment='创建者ID')
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), comment='更新者ID')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系
    test_plans = db.relationship('TestPlan', backref='iteration', cascade='all, delete-orphan')
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
        executions = [exec for req in self.version_requirements if req.test_case for exec in req.test_case.executions]
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
            'test_plan_count': len(self.test_plans),
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


class TestPlan(db.Model):
    """测试计划模型"""
    __tablename__ = 'test_plans'
    
    id = db.Column(db.Integer, primary_key=True, comment='测试计划编号')
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, comment='所属项目ID')
    iteration_id = db.Column(db.Integer, db.ForeignKey('iterations.id'), nullable=True, comment='所属迭代ID')
    plan_name = db.Column(db.String(200), nullable=False, comment='测试计划名称')
    description = db.Column(db.Text, comment='测试计划描述')
    status = db.Column(db.Enum(*TEST_PLAN_STATUS), default='draft', comment='测试计划状态')
    scope = db.Column(db.Text, comment='测试范围')
    test_environment = db.Column(db.Text, comment='测试环境')
    risk = db.Column(db.Text, comment='风险评估')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='创建者ID')
    start_date = db.Column(db.DateTime, comment='开始日期')
    end_date = db.Column(db.DateTime, comment='结束日期')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系
    created_by_user = db.relationship('User', backref='created_test_plans')
    test_tasks = db.relationship('TestTask', backref='test_plan', cascade='all, delete-orphan')
    # 与测试用例的多对多关系
    test_cases = db.relationship('TestCase', secondary='plan_case_relation', backref='test_plans')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'project_name': self.project.project_name if self.project else None,
            'iteration_id': self.iteration_id,
            'iteration_name': self.iteration.iteration_name if self.iteration else None,
            'plan_name': self.plan_name,
            'description': self.description,
            'status': self.status,
            'scope': self.scope,
            'test_environment': self.test_environment,
            'risk': self.risk,
            'created_by': self.created_by,
            'created_by_name': self.created_by_user.real_name if self.created_by_user else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'task_count': len(self.test_tasks),
            'case_count': len(self.test_cases)
        }


# 测试计划和测试用例的关联表
plan_case_relation = db.Table('plan_case_relation',
    db.Column('plan_id', db.Integer, db.ForeignKey('test_plans.id'), primary_key=True),
    db.Column('case_id', db.Integer, db.ForeignKey('test_cases.id'), primary_key=True)
)


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
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), comment='设备负责人ID')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
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
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='创建者ID')
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, comment='所属项目ID')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系
    # 自引用关系，用于构建目录树结构
    parent = db.relationship('TestSuite', remote_side=[id], backref='children')
    # 与测试用例的一对多关系
    test_cases = db.relationship('TestCase', backref='suite', lazy='dynamic')
    # 与用户的多对一关系
    creator = db.relationship('User', backref='created_suites')
    # 移除重复的关系定义，因为Project模型中已经定义了完整的关系
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'suite_name': self.suite_name,
            'description': self.description,
            'parent_id': self.parent_id,
            'status': self.status,
            'creator_id': self.creator_id,
            'creator_name': self.creator.real_name if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'children_count': self.children.count(),
            'cases_count': self.test_cases.count()
        }


class TestCase(db.Model):
    """测试用例模型"""
    __tablename__ = 'test_cases'
    
    id = db.Column(db.Integer, primary_key=True, comment='用例编号')
    case_name = db.Column(db.String(200), nullable=False, comment='用例名称')
    case_description = db.Column(db.Text, comment='用例描述')
    module = db.Column(db.String(100), nullable=False, comment='所属模块')
    priority = db.Column(db.Enum(*TEST_CASE_PRIORITY), default='medium', comment='优先级')
    status = db.Column(db.Enum(*TEST_CASE_STATUS), default='draft', comment='状态')
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='创建者ID')
    suite_id = db.Column(db.Integer, db.ForeignKey('test_suites.id'), nullable=True, comment='所属套件ID')
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, comment='所属项目ID')
    version_requirement_id = db.Column(db.Integer, db.ForeignKey('version_requirements.id'), unique=True, nullable=True, comment='关联的版本需求ID')
    # 添加支持xmind形式的字段
    xmind_data = db.Column(db.Text, comment='xmind格式的用例数据（JSON字符串）')
    preconditions = db.Column(db.Text, comment='前置条件')
    precondition = db.Column(db.Text, comment='前置条件')
    steps = db.Column(db.Text, comment='测试步骤')
    expected_result = db.Column(db.Text, comment='预期结果')
    actual_result = db.Column(db.Text, comment='实际结果')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    # 添加缺失的字段
    test_data = db.Column(db.Text, nullable=True, comment='测试数据')
    iteration_id = db.Column(db.Integer, db.ForeignKey('iterations.id'), nullable=True, comment='所属迭代ID')
    version_info = db.Column(db.String(100), nullable=True, comment='版本信息')
    assignee = db.Column(db.String(50), nullable=True, comment='负责人')
    test_plan_id = db.Column(db.Integer, db.ForeignKey('test_plans.id'), nullable=True, comment='所属测试计划ID')
    author = db.Column(db.String(50), nullable=True, comment='作者')
    
    # 关系
    test_tasks = db.relationship('TestTask', secondary='task_case_relation', backref='test_cases')
    bugs = db.relationship('Bug', backref='test_case', lazy='dynamic')
    # 与用户的多对一关系
    # 使用User模型中已定义的关系，避免重复定义
    # creator = db.relationship('User', backref='created_cases')  # 已在User模型中定义，避免冲突
    # 与项目的多对一关系
    # 使用Project模型中已定义的关系，避免重复定义
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'case_name': self.case_name,
            'case_description': self.case_description,
            'module': self.module,
            'priority': self.priority,
            'status': self.status,
            'creator_id': self.creator_id,
            'creator_name': self.creator.real_name if self.creator else None,
            'suite_id': self.suite_id,
            'suite_name': self.suite.suite_name if self.suite else None,
            'version_requirement_id': self.version_requirement_id,
            'version_requirement_name': self.version_requirement.requirement_name if self.version_requirement else None,
            'xmind_data': self.xmind_data,
            'preconditions': self.preconditions,
            'steps': self.steps,
            'expected_result': self.expected_result,
            'actual_result': self.actual_result,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
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
    executor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, comment='执行人ID')
    execution_time = db.Column(db.DateTime, default=datetime.utcnow, comment='执行时间')
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
                'case_name': self.test_case.case_name,
                'module': self.test_case.module
            } if self.test_case else None
        }


class TestTask(db.Model):
    """测试任务模型"""
    __tablename__ = 'test_tasks'
    
    id = db.Column(db.Integer, primary_key=True, comment='任务编号')
    task_name = db.Column(db.String(200), nullable=False, comment='任务名称')
    task_description = db.Column(db.Text, comment='任务描述')
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False, comment='测试设备ID')
    # 添加项目、迭代和测试计划关联
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True, comment='所属项目ID')
    iteration_id = db.Column(db.Integer, db.ForeignKey('iterations.id'), nullable=True, comment='所属迭代ID')
    test_plan_id = db.Column(db.Integer, db.ForeignKey('test_plans.id'), nullable=True, comment='所属测试计划ID')
    status = db.Column(db.Enum(*TEST_TASK_STATUS), default='pending', comment='任务状态')
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='创建者ID')
    executor_id = db.Column(db.Integer, db.ForeignKey('users.id'), comment='执行者ID')
    # 添加与测试套件的关联
    suite_id = db.Column(db.Integer, db.ForeignKey('test_suites.id'), nullable=True, comment='关联的测试套件ID')
    # 添加任务相关信息
    documentation_url = db.Column(db.Text, comment='相关文档链接')
    version_info = db.Column(db.String(100), comment='版本信息')
    scheduled_time = db.Column(db.DateTime, comment='计划执行时间')
    started_time = db.Column(db.DateTime, comment='开始执行时间')
    completed_time = db.Column(db.DateTime, comment='完成时间')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
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
            'test_plan_id': self.test_plan_id,
            'test_plan_name': self.test_plan.plan_name if self.test_plan else None,
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
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='报告者ID')
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'), comment='分配给ID')
    # 添加与项目和迭代的关联
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True, comment='所属项目ID')
    iteration_id = db.Column(db.Integer, db.ForeignKey('iterations.id'), nullable=True, comment='所属迭代ID')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    resolved_at = db.Column(db.DateTime, comment='解决时间')
    
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
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='创建者ID')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    
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


class TestExecution(db.Model):
    """测试执行模型"""
    __tablename__ = 'test_executions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='执行编号')
    task_id = db.Column(db.Integer, db.ForeignKey('test_tasks.id'), nullable=False, comment='测试任务ID')
    environment_id = db.Column(db.Integer, nullable=True, comment='环境ID')
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False, comment='设备ID')
    execution_status = db.Column(db.String(20), nullable=False, comment='执行状态')
    start_time = db.Column(db.DateTime, nullable=True, comment='开始时间')
    end_time = db.Column(db.DateTime, nullable=True, comment='结束时间')
    executor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, comment='执行人ID')
    
    # 关系
    task = db.relationship('TestTask', backref='executions')
    device = db.relationship('Device', backref='test_executions')
    executor = db.relationship('User', backref='executed_tests')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'environment_id': self.environment_id,
            'device_id': self.device_id,
            'execution_status': self.execution_status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'executor_id': self.executor_id,
            'executor_name': self.executor.real_name if self.executor else None
        }