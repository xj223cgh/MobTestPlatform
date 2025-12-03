from app import create_app
from app.models.models import db, Project, ProjectMember, User

# 创建应用实例
app = create_app()

# 添加应用上下文
with app.app_context():
    # 检查项目179
    project = Project.query.get(179)
    print('项目179存在吗？', project is not None)
    
    if project:
        print('项目名称：', project.project_name)
        print('项目成员数量：', len(project.project_members))
        print('项目成员列表：')
        for member in project.project_members:
            print(f'  - {member.user.real_name} (ID: {member.user.id})')
        
    # 检查所有项目
    print('\n所有项目列表：')
    projects = Project.query.all()
    for p in projects:
        print(f'  - 项目{p.id}: {p.project_name}')
    
    print('\n当前用户列表：')
    users = User.query.all()
    for user in users:
        print(f'  - {user.real_name} (ID: {user.id}, 用户名: {user.username})')
