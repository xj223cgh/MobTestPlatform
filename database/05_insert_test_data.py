#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本 - 插入测试数据
"""

import pymysql
import json
import uuid
import hashlib
import shutil
from werkzeug.security import generate_password_hash
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入配置
from database.config import DB_CONFIG

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            charset=DB_CONFIG['charset']
        )
        return connection
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None

def insert_test_data():
    """插入测试数据"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            # 1. 清空现有数据
            print("开始清空现有数据...")
            # 禁用外键检查以允许截断表
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            # 清空所有表数据（含 reports：造数后报告为空；自动生成仅在「任务状态变更为已完成」且用户设置「自动生成报告」时触发）
            tables = [
                'reports', 'user_settings', 'system_settings',
                'version_requirements', 'test_cases', 'test_tasks', 
                'iterations', 'project_members', 'projects', 
                'devices', 'test_suites', 'test_case_review_details',
                'test_case_review_history', 'test_suite_review_history',
                'test_suite_review_tasks', 'task_case_relation',
                'task_device_relation', 'test_case_executions',
                'users'
            ]
            
            for table in tables:
                cursor.execute(f"TRUNCATE TABLE {table}")
                
            # 启用外键检查
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            print("现有数据清空完成！")
            
            # 2. 插入用户数据
            print("开始插入用户数据...")
            # 生成密码哈希
            password = "123321"
            password_hash = generate_password_hash(password)
            
            # 插入初始特殊账号 (ID 1-4)，保留 Lethe/Manager/Tester/Admin
            initial_users = [
                ('Lethe', '13800138000', '超级管理员', 'male', '管理部', password_hash, 'super'),
                ('Manager', '13800138001', '项目经理', 'male', '项目部', password_hash, 'manager'),
                ('Tester', '13800138002', '测试主管', 'female', '测试部', password_hash, 'tester'),
                ('Admin', '13800138003', '实习生', 'female', '测试部', password_hash, 'admin')
            ]
            
            cursor.executemany("""
                INSERT INTO users (username, phone, real_name, gender, department, password_hash, role) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, initial_users)
            
            # 插入测试用户 (ID 5+)，使用真实人名
            users_data = [
                ('zhaomin', '13800138004', '赵敏', 'female', '测试部', password_hash, 'tester'),
                ('chenjing', '13800138005', '陈静', 'female', '测试部', password_hash, 'tester'),
                ('yangfan', '13800138006', '杨帆', 'male', '开发部', password_hash, 'manager'),
                ('zhoujie', '13800138007', '周杰', 'male', '产品部', password_hash, 'admin'),
                ('wulei', '13800138008', '吴磊', 'male', '测试部', password_hash, 'tester'),
                ('zhengli', '13800138009', '郑丽', 'female', '测试部', password_hash, 'tester'),
                ('sunhao', '13800138010', '孙浩', 'male', '开发部', password_hash, 'manager')
            ]
            
            cursor.executemany("""
                INSERT INTO users (username, phone, real_name, gender, department, password_hash, role) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, users_data)
            print("用户测试数据插入成功！")
            
            # 3. 插入项目测试数据
            print("开始插入项目数据...")
            # 先获取所有用户ID，确保owner_id有效
            cursor.execute("SELECT id FROM users")
            user_ids = [row[0] for row in cursor.fetchall()]
            
            # 插入项目测试数据，各个参数做好分类区分
            # 只使用有效的用户ID作为owner_id
            # 添加合理的开始日期和结束日期
            from datetime import datetime, timedelta
            
            # 获取当前日期
            current_date = datetime.now()
            
            projects_data = [
                # 移动端应用测试项目（不涉及自动化字眼，采用应用名、功能模块、专项测试）
                ('移动应用测试平台', '移动端核心测试项目，包含功能与专项测试', 'in_progress', user_ids[0], '2023-01-01 00:00:00', '2023-12-31 23:59:59', '["移动端", "功能测试", "专项测试"]', 'high', 'https://docs.example.com/mobile-test-platform', 'https://pipeline.example.com/mobile-test-platform', user_ids[0]),
                ('电商APP测试', '电商应用功能测试，包含支付模块', 'completed', user_ids[1], '2023-02-01 00:00:00', '2023-05-31 23:59:59', '["移动端", "电商", "支付"]', 'medium', 'https://docs.example.com/ecommerce-app', 'https://pipeline.example.com/ecommerce-app', user_ids[1]),
                ('金融应用测试', '金融应用安全与风控模块测试', 'in_progress', user_ids[2], '2023-03-15 00:00:00', '2023-09-15 23:59:59', '["移动端", "安全", "金融"]', 'high', 'https://docs.example.com/finance-app', 'https://pipeline.example.com/finance-app', user_ids[2]),
                ('社交软件测试', '社交应用功能与性能测试，包含实时聊天', 'paused', user_ids[3], '2023-04-01 00:00:00', '2023-07-31 23:59:59', '["移动端", "社交", "性能测试"]', 'medium', 'https://docs.example.com/social-app', 'https://pipeline.example.com/social-app', user_ids[3]),
                ('游戏APP测试', '游戏应用功能测试，包含关卡系统', 'in_progress', user_ids[0], '2023-05-01 00:00:00', '2023-08-31 23:59:59', '["移动端", "游戏", "功能测试"]', 'medium', 'https://docs.example.com/game-app', 'https://pipeline.example.com/game-app', user_ids[0]),
                ('教育平台测试', '在线教育移动端测试，包含直播功能', 'not_started', user_ids[1], '2023-06-01 00:00:00', '2023-12-01 23:59:59', '["移动端", "教育", "直播"]', 'high', 'https://docs.example.com/education-platform', 'https://pipeline.example.com/education-platform', user_ids[1]),
                ('医疗应用测试', '医疗健康应用测试，包含预约功能', 'in_progress', user_ids[2], '2023-07-01 00:00:00', '2023-10-31 23:59:59', '["移动端", "医疗", "功能测试"]', 'high', 'https://docs.example.com/healthcare-app', 'https://pipeline.example.com/healthcare-app', user_ids[2]),
                ('短视频APP测试', '短视频应用测试，包含推荐与播放', 'in_progress', user_ids[3], '2023-08-01 00:00:00', '2023-11-30 23:59:59', '["移动端", "短视频", "专项测试"]', 'medium', 'https://docs.example.com/short-video-app', 'https://pipeline.example.com/short-video-app', user_ids[3]),
                ('外卖平台测试', '外卖应用测试，包含下单与配送', 'not_started', user_ids[0], '2023-09-01 00:00:00', '2024-02-29 23:59:59', '["移动端", "外卖", "配送"]', 'medium', 'https://docs.example.com/food-delivery-app', 'https://pipeline.example.com/food-delivery-app', user_ids[0]),
                ('旅游应用测试', '旅游应用测试，包含预订功能', 'completed', user_ids[1], '2023-10-01 00:00:00', '2023-12-31 23:59:59', '["移动端", "旅游", "预订"]', 'low', 'https://docs.example.com/travel-app', 'https://pipeline.example.com/travel-app', user_ids[1]),
                ('新闻应用测试', '新闻应用测试，包含资讯推送', 'in_progress', user_ids[2], '2023-11-01 00:00:00', '2024-04-30 23:59:59', '["移动端", "新闻", "推送"]', 'low', 'https://docs.example.com/news-app', 'https://pipeline.example.com/news-app', user_ids[2]),
                ('音乐APP测试', '音乐应用测试，包含播放与歌单', 'paused', user_ids[3], '2023-12-01 00:00:00', '2024-03-31 23:59:59', '["移动端", "音乐", "播放"]', 'medium', 'https://docs.example.com/music-app', 'https://pipeline.example.com/music-app', user_ids[3])
            ]
            
            cursor.executemany("""
                INSERT INTO projects (project_name, description, status, owner_id, start_date, end_date, tags, priority, doc_url, pipeline_url, creator_id) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, projects_data)
            print("项目测试数据插入成功！")
            
            # 4. 插入项目成员测试数据
            print("开始插入项目成员数据...")
            # 插入项目成员测试数据
            project_members_data = []
            
            # 获取所有用户ID
            cursor.execute("SELECT id FROM users")
            user_ids = [row[0] for row in cursor.fetchall()]
            
            # 获取所有项目ID
            cursor.execute("SELECT id FROM projects")
            project_ids = [row[0] for row in cursor.fetchall()]
            
            # 为每个项目添加成员
            for i, project_id in enumerate(project_ids):
                # 项目负责人 - 从user_ids列表中直接获取，确保有效
                owner_id = user_ids[i % len(user_ids)]
                project_members_data.append((project_id, owner_id, 'owner'))
                
                # 添加其他成员
                for user_id in user_ids[:5]:  # 为每个项目添加前5个用户
                    if user_id != owner_id:
                        role = 'tester' if user_id % 2 == 0 else 'viewer'
                        project_members_data.append((project_id, user_id, role))
            
            cursor.executemany("""
                INSERT INTO project_members (project_id, user_id, role) 
                VALUES (%s, %s, %s)
            """, project_members_data)
            print("项目成员测试数据插入成功！")

            # 4.5 插入设备数据（模拟数据，仅 Android，状态均为离线）
            print("开始插入设备数据...")
            devices_data = [
                ('华为 P40', 'P40', 'android', '10', 'emulator-5554', 'offline', user_ids[0]),
                ('小米 11', 'MI 11', 'android', '11', 'emulator-5556', 'offline', user_ids[1]),
                ('OPPO Find X3', 'PEDM00', 'android', '12', 'emulator-5558', 'offline', user_ids[2]),
                ('vivo X60', 'V2055A', 'android', '11', 'emulator-5560', 'offline', user_ids[3]),
                ('三星 S21', 'SM-G9910', 'android', '12', 'emulator-5562', 'offline', user_ids[0]),
                ('一加 9', 'LE2110', 'android', '11', 'emulator-5564', 'offline', user_ids[1]),
                ('真我 GT', 'RMX2202', 'android', '11', 'emulator-5566', 'offline', user_ids[2]),
                ('红米 K40', 'M2012K11AC', 'android', '11', 'emulator-5568', 'offline', user_ids[3]),
                ('Pixel 5 模拟器', 'Pixel 5', 'android', '13', 'emulator-5570', 'offline', user_ids[1]),
            ]
            cursor.executemany("""
                INSERT INTO devices (device_name, device_model, os_type, os_version, device_id, status, owner_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, devices_data)
            print("设备测试数据插入成功！")
            
            # 5. 插入迭代数据
            print("开始插入迭代数据...")
            # 迭代数据
            iterations_data = []
            iteration_statuses = ['planning', 'active', 'completed', 'cancelled']
            
            for i, project_id in enumerate(project_ids):
                # 获取项目信息，用于设置合理的时间范围
                cursor.execute("SELECT start_date, end_date FROM projects WHERE id = %s", (project_id,))
                project_info = cursor.fetchone()
                project_start = project_info[0]
                project_end = project_info[1]
                
                # 为每个项目添加2-4个迭代
                for j in range(2 + i % 3):
                    iteration_name = f"{i+1}项目迭代{j+1}"
                    description = f"这是第{i+1}个项目的第{j+1}个迭代，用于测试系统功能"
                    goal = f"完成{iteration_name}的所有需求开发和测试"
                    status = iteration_statuses[(i + j) % len(iteration_statuses)]
                    created_by = user_ids[(i + j) % len(user_ids)]
                    updated_by = user_ids[(i + j + 1) % len(user_ids)]
                    version = f"v{j+1}.0"
                    
                    # 计算合理的迭代开始时间和结束时间
                    # 开始时间：项目开始时间 + j * 30天
                    start_date = project_start + timedelta(days=j * 30)
                    # 结束时间：开始时间 + 20-45天
                    end_date = start_date + timedelta(days=20 + j * 5)
                    
                    # 确保结束时间不超过项目结束时间
                    if end_date > project_end:
                        end_date = project_end
                    
                    iterations_data.append((
                        project_id,
                        iteration_name,
                        description,
                        goal,
                        status,
                        start_date.strftime('%Y-%m-%d %H:%M:%S'),
                        end_date.strftime('%Y-%m-%d %H:%M:%S'),
                        version,
                        created_by,
                        updated_by
                    ))
            
            cursor.executemany("""
                INSERT INTO iterations (project_id, iteration_name, description, goal, status, start_date, end_date, version, created_by, updated_by) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, iterations_data)
            print("迭代数据插入成功！")
            
            # 6. 插入版本需求测试数据
            print("开始插入版本需求数据...")
            # 获取所有迭代ID
            cursor.execute("SELECT id FROM iterations")
            iteration_ids = [row[0] for row in cursor.fetchall()]
            
            # 版本需求数据
            requirements_data = []
            requirement_statuses = ['new', 'in_progress', 'completed', 'cancelled']
            priorities = ['high', 'medium', 'low']
            modules = ['登录模块', '首页模块', '用户管理', '权限管理', '测试管理', '报告管理', '设备管理']
            
            # 为每个项目添加版本需求
            for i, project_id in enumerate(project_ids):
                # 获取项目信息，用于设置合理的时间范围
                cursor.execute("SELECT start_date, end_date FROM projects WHERE id = %s", (project_id,))
                project_info = cursor.fetchone()
                project_start = project_info[0]  # 已经是datetime对象
                project_end = project_info[1]  # 已经是datetime对象
                
                # 为每个项目添加3-5个版本需求
                for j in range(3 + i % 3):
                    requirement_name = f"{i+1}项目需求{j+1}"
                    requirement_description = f"这是第{i+1}个项目的第{j+1}个版本需求，用于测试系统功能"
                    status = requirement_statuses[(i + j) % len(requirement_statuses)]
                    iteration_id = iteration_ids[(i + j) % len(iteration_ids)] if iteration_ids else None
                    priority = priorities[(i + j) % len(priorities)]
                    created_by = user_ids[(i + j) % len(user_ids)]
                    assigned_to = user_ids[(i + j + 1) % len(user_ids)]
                    environment = ['test', 'staging', 'production'][(i + j) % 3]
                    module = modules[j % len(modules)]
                    
                    # 计算合理的开始时间和结束时间
                    # 开始时间：项目开始时间 + 随机天数
                    start_date = project_start + timedelta(days=j * 7)
                    # 结束时间：开始时间 + 随机天数（3-14天）
                    end_date = start_date + timedelta(days=3 + j * 2)
                    
                    # 确保结束时间不超过项目结束时间
                    if end_date > project_end:
                        end_date = project_end
                    
                    requirements_data.append((
                        requirement_name,
                        requirement_description,
                        module,
                        status,
                        project_id,
                        iteration_id,
                        priority,
                        8.0 + j,
                        None if status != 'completed' else 8.0 + j * 0.8,
                        created_by,
                        assigned_to,
                        start_date.strftime('%Y-%m-%d %H:%M:%S'),
                        end_date.strftime('%Y-%m-%d %H:%M:%S'),
                        environment,
                        False  # is_deleted
                    ))
            
            cursor.executemany("""
                INSERT INTO version_requirements (requirement_name, requirement_description, module, status, project_id, iteration_id, priority, estimated_hours, actual_hours, created_by, assigned_to, start_date, end_date, environment, is_deleted) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, requirements_data)
            print("版本需求测试数据插入成功！")
            
            # 7. 插入测试套件数据（文件夹 + 测试集：文件夹为目录，测试集下挂用例）
            print("开始插入测试套件数据...")
            cursor.execute("SELECT id, project_id FROM version_requirements")
            req_rows = cursor.fetchall()
            project_reqs = {}
            for req_id, proj_id in req_rows:
                project_reqs.setdefault(proj_id, []).append(req_id)
            creator_id = user_ids[0]

            # 7.1 每个项目一个根文件夹（type=folder, parent_id=NULL）
            for project_id in project_ids:
                cursor.execute("""
                    INSERT INTO test_suites (suite_name, description, parent_id, `type`, creator_id, project_id, version_requirement_id, sort_order)
                    VALUES (%s, %s, NULL, 'folder', %s, %s, NULL, 0)
                """, (f"项目{project_id}-用例库", f"项目{project_id}的用例根目录", creator_id, project_id))
            cursor.execute("SELECT id, project_id FROM test_suites WHERE `type` = 'folder' AND parent_id IS NULL ORDER BY id")
            root_rows = cursor.fetchall()
            project_to_root = {proj_id: rid for rid, proj_id in root_rows}

            # 7.2 每个根目录下 2 个子文件夹（功能测试、专项测试）- 移动端应用测试业务
            sub_folder_names = ['功能测试', '专项测试']
            for project_id in project_ids:
                root_id = project_to_root.get(project_id)
                if not root_id:
                    continue
                for idx, name in enumerate(sub_folder_names):
                    cursor.execute("""
                        INSERT INTO test_suites (suite_name, description, parent_id, `type`, creator_id, project_id, version_requirement_id, sort_order)
                        VALUES (%s, %s, %s, 'folder', %s, %s, NULL, %s)
                    """, (name, f"项目{project_id}-{name}", root_id, creator_id, project_id, idx))
            cursor.execute("SELECT id, parent_id, project_id FROM test_suites WHERE `type` = 'folder' AND parent_id IS NOT NULL ORDER BY id")
            sub_folder_rows = cursor.fetchall()
            # 按项目归组子文件夹 id：project_id -> [folder_id, ...]
            project_to_sub_folders = {}
            for fid, _pid, proj_id in sub_folder_rows:
                project_to_sub_folders.setdefault(proj_id, []).append(fid)

            # 7.3 每个子文件夹下 2 个测试集（type=suite）：功能测试→登录与权限、核心流程；专项测试→兼容性测试、性能测试
            # 先查询迭代数据，用于关联测试集
            cursor.execute("SELECT id, project_id FROM iterations ORDER BY project_id, id")
            project_iterations_for_suite = {}
            for iter_id, proj_id in cursor.fetchall():
                project_iterations_for_suite.setdefault(proj_id, []).append(iter_id)
            
            suite_rows = []  # (suite_id, project_id, version_requirement_id, category)
            folder_suite_categories = [
                ['登录与权限', '核心流程'],   # 功能测试
                ['兼容性测试', '性能测试'],   # 专项测试（移动端）
            ]
            suite_counter = 0  # 用于循环分配迭代
            for project_id in project_ids:
                req_ids = project_reqs.get(project_id, [])
                iter_ids = project_iterations_for_suite.get(project_id, [])
                sub_folders = project_to_sub_folders.get(project_id, [])
                for folder_idx, folder_id in enumerate(sub_folders):
                    cats = folder_suite_categories[folder_idx % len(folder_suite_categories)]
                    for k, cat in enumerate(cats):
                        suite_name = f"{cat}用例集"
                        desc = f"项目{project_id} - {cat}，用例内容与用例集对应"
                        req_id = req_ids[(folder_idx * 2 + k) % len(req_ids)] if req_ids else None
                        # 分配迭代ID
                        iteration_id = iter_ids[suite_counter % len(iter_ids)] if iter_ids else None
                        cursor.execute("""
                            INSERT INTO test_suites (suite_name, description, parent_id, `type`, creator_id, project_id, version_requirement_id, iteration_id, sort_order)
                            VALUES (%s, %s, %s, 'suite', %s, %s, %s, %s, %s)
                        """, (suite_name, desc, folder_id, creator_id, project_id, req_id, iteration_id, k))
                        suite_id = cursor.lastrowid
                        suite_rows.append((suite_id, project_id, req_id, cat))
                        suite_counter += 1
            print("测试套件数据插入成功（含文件夹与测试集）！")

            # 8. 插入测试用例数据：按用例集类型（登录与权限/核心流程/兼容性测试/性能测试）生成对应数量与内容，每份用例集不少于 6 条
            print("开始插入测试用例数据...")
            cursor.execute("SELECT id, project_id FROM iterations ORDER BY project_id, id")
            project_iterations = {}
            for iter_id, proj_id in cursor.fetchall():
                project_iterations.setdefault(proj_id, []).append(iter_id)

            # 按用例集类型定义用例条数与内容（移动端应用测试，不涉及自动化字眼）
            CASE_TEMPLATES_BY_CATEGORY = {
                '登录与权限': [
                    {'name': '正常登录', 'desc': '验证正确账号密码可登录', 'pre': '应用已安装、网络正常、存在有效账号', 'steps': '1. 打开登录页\n2. 输入用户名和密码\n3. 点击登录', 'expected': '登录成功进入首页，显示用户信息', 'data': '账号 test01 / 密码 Test@123'},
                    {'name': '错误密码登录', 'desc': '验证错误密码有正确提示', 'pre': '应用已安装、存在有效账号', 'steps': '1. 打开登录页\n2. 输入正确用户名与错误密码\n3. 点击登录', 'expected': '提示用户名或密码错误，不跳转', 'data': '账号 test01 / 错误密码 wrong'},
                    {'name': '登出与会话', 'desc': '验证登出后会话清除', 'pre': '用户已登录', 'steps': '1. 进入个人中心\n2. 点击登出\n3. 返回首页', 'expected': '登出成功，再次进入需重新登录', 'data': None},
                    {'name': '记住登录状态', 'desc': '勾选记住登录后再次打开免登录', 'pre': '应用已安装', 'steps': '1. 登录时勾选记住登录\n2. 退出应用后重新打开', 'expected': '仍处于登录状态', 'data': None},
                    {'name': '多端登录互踢', 'desc': '同账号多端登录时旧端会话失效', 'pre': '已有账号', 'steps': '1. 设备A登录\n2. 设备B同账号登录\n3. 设备A操作', 'expected': '设备A提示会话失效需重新登录', 'data': None},
                    {'name': '权限校验', 'desc': '无权限功能入口不可见或不可用', 'pre': '已登录低权限账号', 'steps': '1. 进入各功能入口\n2. 尝试访问受限功能', 'expected': '无权限时隐藏或提示无权限', 'data': None},
                ],
                '核心流程': [
                    {'name': '主流程正向', 'desc': '完整主流程从进入到提交', 'pre': '用户已登录', 'steps': '1. 进入功能模块\n2. 按流程填写并提交\n3. 刷新校验', 'expected': '提交成功，数据持久化正确', 'data': '参考业务示例数据'},
                    {'name': '必填校验', 'desc': '必填项为空时拦截', 'pre': '用户已登录', 'steps': '1. 进入表单\n2. 必填项留空提交', 'expected': '提示必填项，不提交', 'data': None},
                    {'name': '边界值', 'desc': '边界值与长度限制', 'pre': '环境就绪', 'steps': '1. 输入边界合法值\n2. 输入超长/非法格式', 'expected': '边界内通过，超限有提示', 'data': '长度 1、最大长度、超长字符串'},
                    {'name': '列表与详情', 'desc': '列表分页与详情一致性', 'pre': '已有数据', 'steps': '1. 打开列表\n2. 分页切换\n3. 进入详情', 'expected': '列表与详情数据一致', 'data': None},
                    {'name': '搜索与筛选', 'desc': '搜索框与筛选条件生效', 'pre': '列表有数据', 'steps': '1. 输入关键词搜索\n2. 切换筛选条件', 'expected': '结果符合搜索与筛选', 'data': None},
                    {'name': '提交后跳转', 'desc': '提交成功后跳转与状态更新', 'pre': '用户已登录', 'steps': '1. 提交表单\n2. 观察跳转与列表状态', 'expected': '跳转正确，列表已更新', 'data': None},
                    {'name': '取消与返回', 'desc': '取消或返回不保存草稿', 'pre': '已填写部分表单', 'steps': '1. 点击取消或返回\n2. 再次进入', 'expected': '未保存内容不保留', 'data': None},
                    {'name': '空状态展示', 'desc': '无数据时展示空状态与引导', 'pre': '新用户或清空数据', 'steps': '1. 进入列表/首页', 'expected': '展示空状态与操作引导', 'data': None},
                ],
                '兼容性测试': [
                    {'name': '不同机型适配', 'desc': '主流机型分辨率与导航栏适配', 'pre': '多台测试机', 'steps': '1. 在不同机型安装\n2. 检查布局与关键操作', 'expected': '无遮挡、无错位，功能可用', 'data': 'Android/iOS 多机型'},
                    {'name': '系统版本兼容', 'desc': '最低支持系统版本至当前版本', 'pre': '多系统版本设备', 'steps': '1. 在最低支持版本安装\n2. 在最新版本安装并操作', 'expected': '安装与核心流程正常', 'data': None},
                    {'name': '深色模式', 'desc': '跟随系统深色模式切换', 'pre': '系统支持深色模式', 'steps': '1. 切换系统深色模式\n2. 打开应用检查各页', 'expected': '主题切换正确、文字可读', 'data': None},
                    {'name': '横竖屏切换', 'desc': '横竖屏切换不崩溃、布局合理', 'pre': '应用支持横屏', 'steps': '1. 竖屏进入关键页\n2. 旋转为横屏', 'expected': '不闪退，布局自适应', 'data': None},
                    {'name': '多语言切换', 'desc': '切换语言后文案更新', 'pre': '应用支持多语言', 'steps': '1. 在设置中切换语言\n2. 浏览各页', 'expected': '文案为所选语言，无乱码', 'data': None},
                    {'name': '大字体与无障碍', 'desc': '系统大字体下布局不重叠', 'pre': '系统设置大字号', 'steps': '1. 设置系统字体放大\n2. 打开应用', 'expected': '文字完整显示、可操作', 'data': None},
                ],
                '性能测试': [
                    {'name': '首页加载', 'desc': '首页首屏可正常加载', 'pre': '应用已安装、网络正常', 'steps': '1. 冷启动应用\n2. 等待首页加载', 'expected': '首页无白屏、无崩溃', 'data': None},
                    {'name': '关键路径可点击', 'desc': '主要入口可点击进入', 'pre': '首页已加载', 'steps': '1. 点击主导航\n2. 进入各主要页', 'expected': '页面可进入、无闪退', 'data': None},
                    {'name': '列表滑动流畅度', 'desc': '长列表滑动不卡顿', 'pre': '列表有较多数据', 'steps': '1. 打开列表页\n2. 快速滑动到底部', 'expected': '滑动流畅、无白屏', 'data': None},
                    {'name': '内存占用', 'desc': '长时间使用内存无持续增长', 'pre': '已安装应用', 'steps': '1. 重复进入各模块 10 次\n2. 查看内存占用', 'expected': '内存无异常增长', 'data': None},
                    {'name': '弱网与断网', 'desc': '弱网下加载与断网提示', 'pre': '可模拟弱网', 'steps': '1. 弱网下打开应用\n2. 断网后操作', 'expected': '有加载态与错误提示', 'data': None},
                    {'name': '后台恢复', 'desc': '切后台再回来状态正确', 'pre': '已进入某功能页', 'steps': '1. 切到后台 2 分钟\n2. 切回应用', 'expected': '页面恢复或提示重新加载', 'data': None},
                ],
            }
            # 每份用例集 30～80 条，保证数据量充足
            CASE_COUNT_BY_CATEGORY = {'登录与权限': 35, '核心流程': 50, '兼容性测试': 40, '性能测试': 35}
            priorities = ['P0', 'P1', 'P2']
            cases_data = []
            case_seq = 0
            for suite_id, project_id, req_id, category in suite_rows:
                iters = project_iterations.get(project_id, [])
                iteration_id = iters[0] if iters else None
                assignee_id = user_ids[1]
                reviewer_id = user_ids[2] if len(user_ids) > 2 else None
                templates = CASE_TEMPLATES_BY_CATEGORY.get(category, CASE_TEMPLATES_BY_CATEGORY['核心流程'])
                n_cases = CASE_COUNT_BY_CATEGORY.get(category, 4)
                for m in range(n_cases):
                    case_seq += 1
                    tpl = templates[m % len(templates)]
                    case_number = f"TC-P{project_id}-{case_seq:04d}"
                    base_name = f"{category}-{tpl['name']}"
                    case_name = base_name if m < len(templates) else f"{base_name}({m // len(templates) + 1})"
                    description = tpl['desc']
                    preconditions = tpl['pre']
                    steps = tpl['steps']
                    expected_result = tpl['expected']
                    test_data = tpl.get('data')
                    priority = priorities[m % len(priorities)]
                    cases_data.append((
                        case_number,
                        case_name,
                        description,
                        priority,
                        user_ids[1],
                        project_id,
                        req_id,
                        iteration_id,
                        suite_id,
                        preconditions,
                        steps,
                        expected_result,
                        None,
                        test_data,
                        assignee_id,
                        reviewer_id,
                    ))
            cursor.executemany("""
                INSERT INTO test_cases (
                    case_number, case_name, case_description, priority, creator_id,
                    project_id, version_requirement_id, iteration_id, suite_id,
                    preconditions, steps, expected_result, actual_result, test_data,
                    assignee_id, reviewer_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, cases_data)
            print("测试用例数据插入成功！")

            # 9. 插入用例执行类型测试任务（完整数据：项目/迭代/需求/用例集关联及可读描述）
            print("开始插入测试任务数据...")
            cursor.execute("SELECT id, project_id FROM iterations ORDER BY project_id, id")
            project_iterations = {}
            for iter_id, proj_id in cursor.fetchall():
                project_iterations.setdefault(proj_id, []).append(iter_id)
            cursor.execute("SELECT id, project_name FROM projects")
            project_id_to_name = {row[0]: row[1] for row in cursor.fetchall()}
            cursor.execute("SELECT id, iteration_name FROM iterations")
            iteration_id_to_name = {row[0]: row[1] for row in cursor.fetchall()}
            cursor.execute("SELECT id, suite_name FROM test_suites WHERE `type` = 'suite'")
            suite_id_to_name = {row[0]: row[1] for row in cursor.fetchall()}
            cursor.execute("SELECT id, requirement_name FROM version_requirements")
            req_id_to_name = {row[0]: row[1] for row in cursor.fetchall()}

            tasks_data = []
            task_statuses = ['pending', 'running', 'completed', 'completed', 'pending']
            priorities = ['high', 'medium', 'low']
            now = datetime.now()
            time_fmt = '%Y-%m-%d %H:%M:%S'

            for idx, (suite_id, project_id, req_id, category) in enumerate(suite_rows):
                iteration_id = None
                if project_id and project_id in project_iterations:
                    iteration_id = project_iterations[project_id][idx % len(project_iterations[project_id])]
                status = task_statuses[idx % len(task_statuses)]
                creator_id = user_ids[2]   # 创建人使用用户表中的真实用户（如杨帆）
                executor_id = user_ids[1] if status == 'completed' else (user_ids[3] if status == 'running' else None)  # 负责人为真实用户（赵敏等）
                suite_name = suite_id_to_name.get(suite_id, f'套件{suite_id}')
                task_name = f"【用例执行】{suite_name}"
                proj_name = project_id_to_name.get(project_id, '')
                iter_name = iteration_id_to_name.get(iteration_id, '') if iteration_id else ''
                req_name = req_id_to_name.get(req_id, '') if req_id else ''
                description = f"所属项目：{proj_name}。迭代：{iter_name}。关联用例集：{suite_name}，类型：{category}。任务类型：用例执行。"

                # 计划时间：每条任务都有完整的计划开始/结束时间
                scheduled_start = (now - timedelta(days=1) + timedelta(hours=idx % 24)).strftime(time_fmt)
                scheduled_end = (now + timedelta(days=1) + timedelta(hours=(idx + 2) % 24)).strftime(time_fmt)
                started_time = None
                completed_time = None
                if status == 'completed':
                    started_time = (now - timedelta(hours=2)).strftime(time_fmt)
                    completed_time = (now - timedelta(minutes=30)).strftime(time_fmt)
                elif status == 'running':
                    started_time = (now - timedelta(hours=1)).strftime(time_fmt)

                tasks_data.append((
                    task_name, description, 'test_case', priorities[idx % 3], status,
                    creator_id, executor_id, project_id, iteration_id, suite_id, req_id,
                    scheduled_start, scheduled_end, started_time, completed_time
                ))

            cursor.executemany("""
                INSERT INTO test_tasks (task_name, task_description, task_type, priority, status, creator_id, executor_id, project_id, iteration_id, suite_id, version_requirement_id, scheduled_time, scheduled_end_time, started_time, completed_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, tasks_data)
            print("测试任务数据插入成功！")

            # 10. 任务-用例关联（task_case_relation）：按套件关联该套件下全部用例
            print("开始插入任务-用例关联...")
            cursor.execute("SELECT id, suite_id, project_id, iteration_id, status FROM test_tasks WHERE task_type = 'test_case' ORDER BY id")
            task_rows = cursor.fetchall()
            cursor.execute("SELECT id, suite_id FROM test_cases")
            case_suite = [(row[0], row[1]) for row in cursor.fetchall()]
            suite_to_cases = {}
            for case_id, sid in case_suite:
                suite_to_cases.setdefault(sid, []).append(case_id)

            task_case_pairs = []
            for task_id, suite_id, _proj_id, _iter_id, _status in task_rows:
                if suite_id and suite_id in suite_to_cases:
                    for case_id in suite_to_cases[suite_id]:
                        task_case_pairs.append((task_id, case_id))
            if task_case_pairs:
                cursor.executemany("""
                    INSERT INTO task_case_relation (task_id, case_id) VALUES (%s, %s)
                """, task_case_pairs)
            print(f"任务-用例关联插入成功，共 {len(task_case_pairs)} 条！")

            # 11. 已完成任务的用例执行记录（test_case_executions），便于报告有数据
            print("开始插入用例执行记录...")
            exec_statuses = ['pass', 'fail', 'blocked', 'not_applicable']
            executions_data = []
            for task_id, suite_id, project_id, iteration_id, status in task_rows:
                if status != 'completed' or not suite_id or suite_id not in suite_to_cases:
                    continue
                case_ids = suite_to_cases[suite_id]
                exec_time = (now - timedelta(minutes=45)).strftime(time_fmt)
                for i, case_id in enumerate(case_ids):
                    st = exec_statuses[i % len(exec_statuses)]
                    executions_data.append((
                        task_id, case_id, project_id, iteration_id, st,
                        user_ids[1], exec_time, f"执行备注_{task_id}_{case_id}"
                    ))
            if executions_data:
                cursor.executemany("""
                    INSERT INTO test_case_executions (task_id, case_id, project_id, iteration_id, status, executor_id, execution_time, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, executions_data)
                # 同步到 test_cases.status（按用例最新一条执行记录），便于报告统计展示
                cursor.execute("""
                    UPDATE test_cases tc
                    INNER JOIN (
                        SELECT case_id, status FROM test_case_executions e1
                        WHERE id = (SELECT MAX(id) FROM test_case_executions e2 WHERE e2.case_id = e1.case_id)
                    ) latest ON latest.case_id = tc.id
                    SET tc.status = latest.status
                """)
            print(f"用例执行记录插入成功，共 {len(executions_data)} 条！")

            # 11.5 插入报告数据（为已完成任务生成报告，含创建人、时间等完整属性，基于真实执行记录）
            print("开始插入报告数据...")
            # 兼容旧表：若 reports 表无 creator_id 则添加
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'reports' AND COLUMN_NAME = 'creator_id'
            """)
            if cursor.fetchone()[0] == 0:
                cursor.execute("ALTER TABLE reports ADD COLUMN creator_id INT NULL COMMENT '创建人ID' AFTER created_at")
                cursor.execute("ALTER TABLE reports ADD INDEX idx_creator_id (creator_id)")
                cursor.execute("ALTER TABLE reports ADD CONSTRAINT fk_reports_creator FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE SET NULL")
            cursor.execute("SELECT id, project_name FROM projects")
            project_id_to_name = {row[0]: row[1] for row in cursor.fetchall()}
            cursor.execute("""
                SELECT t.id, t.task_name, t.task_type, t.project_id, t.creator_id, t.completed_time
                FROM test_tasks t
                WHERE t.status = 'completed' AND t.task_type = 'test_case'
            """)
            completed_tasks = cursor.fetchall()
            reports_data = []
            for task_id, task_name, task_type, project_id, creator_id, completed_time in completed_tasks:
                proj_name = project_id_to_name.get(project_id) if project_id else None
                
                # 从执行记录中生成真实的 summary 和 details
                cursor.execute("""
                    SELECT tc.id, tc.case_name, tce.status, u.real_name, tce.execution_time, tce.notes
                    FROM test_case_executions tce
                    INNER JOIN test_cases tc ON tce.case_id = tc.id
                    LEFT JOIN users u ON tce.executor_id = u.id
                    WHERE tce.task_id = %s
                    ORDER BY tce.id
                """, (task_id,))
                exec_records = cursor.fetchall()
                
                # 统计 summary
                total_cases = len(exec_records)
                pass_count = sum(1 for r in exec_records if r[2] == 'pass')
                fail_count = sum(1 for r in exec_records if r[2] == 'fail')
                blocked_count = sum(1 for r in exec_records if r[2] == 'blocked')
                not_applicable_count = sum(1 for r in exec_records if r[2] == 'not_applicable')
                executed_cases = total_cases
                pass_rate = round(pass_count / executed_cases * 100, 1) if executed_cases > 0 else 0
                
                summary = {
                    'total_cases': total_cases,
                    'executed_cases': executed_cases,
                    'pass_count': pass_count,
                    'fail_count': fail_count,
                    'blocked_count': blocked_count,
                    'not_applicable_count': not_applicable_count,
                    'pass_rate': pass_rate
                }
                
                # 构建 details
                details = []
                for case_id, case_name, status, executor_name, exec_time, notes in exec_records:
                    details.append({
                        'case_id': case_id,
                        'case_title': case_name or '',
                        'status': status or '',
                        'actual_result': notes or None,
                        'executed_by': executor_name or None,
                        'executed_at': exec_time.isoformat() if exec_time else None,
                        'remarks': notes or None
                    })
                
                summary_json = json.dumps(summary, ensure_ascii=False)
                details_json = json.dumps(details, ensure_ascii=False)
                completed_str = completed_time.strftime('%Y-%m-%d %H:%M:%S') if completed_time and hasattr(completed_time, 'strftime') else (str(completed_time) if completed_time else None)
                created_str = (completed_time or now).strftime('%Y-%m-%d %H:%M:%S') if (completed_time and hasattr(completed_time, 'strftime')) else now.strftime('%Y-%m-%d %H:%M:%S')
                reports_data.append((
                    task_id, task_type, task_name, project_id, proj_name,
                    summary_json, details_json, completed_str, created_str, creator_id
                ))
            if reports_data:
                cursor.executemany("""
                    INSERT INTO reports (task_id, report_type, task_name, project_id, project_name, summary, details, completed_at, created_at, creator_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, reports_data)
            print(f"报告数据插入成功，共 {len(reports_data)} 条，包含真实执行记录！")

            # 12. 设备脚本任务：复制 get_device_info.py 到 storage/device_scripts/日期/uuid.py，并插入任务与任务-设备关联
            print("开始插入设备脚本任务数据...")
            backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
            script_src = os.path.join(backend_dir, 'get_device_info.py')
            storage_base = os.path.join(backend_dir, 'storage', 'device_scripts')
            date_str = now.strftime('%Y%m%d')
            script_date_dir = os.path.join(storage_base, date_str)
            os.makedirs(script_date_dir, exist_ok=True)
            cursor.execute("SELECT id FROM devices ORDER BY id LIMIT 10")
            device_ids = [row[0] for row in cursor.fetchall()]
            cursor.execute("SELECT id, project_name FROM projects ORDER BY id LIMIT 3")
            project_rows = cursor.fetchall()
            script_tasks_data = []
            task_device_script_relations = []
            for i in range(5):
                unique_name = f"{uuid.uuid4()}.py"
                dest_path = os.path.join(script_date_dir, unique_name)
                if os.path.exists(script_src):
                    shutil.copy2(script_src, dest_path)
                relative_path = f"{date_str}/{unique_name}"
                with open(dest_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                task_name = f"设备信息采集任务_{i+1}"
                proj_id = project_rows[i % len(project_rows)][0] if project_rows else None
                creator_id = user_ids[i % len(user_ids)]
                command = f"python {relative_path} --device-id $DEVICE_ID --adb-path adb"
                script_tasks_data.append((
                    task_name, f"使用 get_device_info 脚本采集设备信息（任务{i+1}）", 'device_script', 'medium', 'pending',
                    creator_id, None, proj_id, None, None, None,
                    'get_device_info.py', relative_path, file_hash, command
                ))
            if script_tasks_data:
                cursor.executemany("""
                    INSERT INTO test_tasks (task_name, task_description, task_type, priority, status, creator_id, executor_id, project_id, iteration_id, suite_id, version_requirement_id, script_file, file_path, file_hash, command)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, script_tasks_data)
                cursor.execute("SELECT id FROM test_tasks WHERE task_type = 'device_script' ORDER BY id DESC LIMIT %s", (len(script_tasks_data),))
                script_task_ids = [row[0] for row in cursor.fetchall()]
                for i in range(len(script_tasks_data)):
                    task_id = script_task_ids[len(script_tasks_data) - 1 - i]
                    if device_ids:
                        task_device_script_relations.append((task_id, device_ids[i % len(device_ids)]))
                if task_device_script_relations:
                    cursor.executemany("""
                        INSERT IGNORE INTO task_device_relation (task_id, device_id) VALUES (%s, %s)
                    """, task_device_script_relations)
            print(f"设备脚本任务插入成功，共 {len(script_tasks_data)} 条；任务-设备关联 {len(task_device_script_relations)} 条！")

            connection.commit()
            print("所有测试数据插入成功！")
            print("测试账号信息：")
            print("   - 特殊账号（保留）：Lethe(超级管理员), Manager(项目经理), Tester(测试主管), Admin(系统管理员)")
            print("   - 测试用户：赵敏、陈静、杨帆、周杰、吴磊、郑丽、孙浩")
            print("   - 密码统一为：123321")
            return True
            
    except Exception as e:
        print(f"插入测试数据失败: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()

def main():
    """主函数"""
    print("开始插入测试数据...")
    
    if insert_test_data():
        print("测试数据插入完成！")
        return 0
    else:
        print("测试数据插入失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main())