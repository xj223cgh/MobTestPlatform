#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本 - 插入测试数据
"""

import pymysql
import json
from werkzeug.security import generate_password_hash
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='mobile_test_platform',
            charset='utf8mb4'
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
            cursor.execute("DELETE FROM project_members")
            cursor.execute("DELETE FROM projects")
            cursor.execute("DELETE FROM users WHERE id > 4")  # 保留前4个原始用户
            print("现有数据清空完成！")
            
            # 2. 插入用户测试数据（按字母排序）
            print("开始插入用户数据...")
            # 生成密码哈希
            password = "123321"
            password_hash = generate_password_hash(password)
            
            # 插入用户数据，用户名按字母排序
            users_data = [
                ('DDD', '13800138004', '赵六', 'male', '测试部', password_hash, 'tester'),
                ('EEE', '13800138005', '孙七', 'female', '测试部', password_hash, 'tester'),
                ('FFF', '13800138006', '周八', 'male', '开发部', password_hash, 'manager'),
                ('GGG', '13800138007', '吴九', 'female', '产品部', password_hash, 'admin'),
                ('HHH', '13800138008', '郑十', 'male', '测试部', password_hash, 'tester'),
                ('III', '13800138009', '钱一', 'female', '测试部', password_hash, 'tester'),
                ('JJJ', '13800138010', '孙二', 'male', '开发部', password_hash, 'manager')
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
                # 生产环境项目
                ('移动应用测试平台', '核心测试项目，包含自动化测试框架', 'in_progress', user_ids[0], '2023-01-01 00:00:00', '2023-12-31 23:59:59', 'production', '["移动端", "自动化", "核心项目"]', 'high', 'https://docs.example.com/mobile-test-platform', 'https://pipeline.example.com/mobile-test-platform'),
                ('电商APP测试', '电商应用功能测试，包含支付模块', 'completed', user_ids[1], '2023-02-01 00:00:00', '2023-05-31 23:59:59', 'production', '["移动端", "Web", "电商"]', 'medium', 'https://docs.example.com/ecommerce-app', 'https://pipeline.example.com/ecommerce-app'),
                ('金融应用测试', '金融应用安全测试，包含风控模块', 'in_progress', user_ids[2], '2023-03-15 00:00:00', '2023-09-15 23:59:59', 'production', '["移动端", "安全测试", "金融"]', 'high', 'https://docs.example.com/finance-app', 'https://pipeline.example.com/finance-app'),
                ('社交软件测试', '社交应用性能测试，包含实时聊天', 'paused', user_ids[3], '2023-04-01 00:00:00', '2023-07-31 23:59:59', 'production', '["移动端", "性能测试", "社交"]', 'medium', 'https://docs.example.com/social-app', 'https://pipeline.example.com/social-app'),
                
                # 预发环境项目
                ('游戏APP测试', '游戏应用功能测试，包含关卡系统', 'in_progress', user_ids[0], '2023-05-01 00:00:00', '2023-08-31 23:59:59', 'staging', '["移动端", "游戏", "功能测试"]', 'medium', 'https://docs.example.com/game-app', 'https://pipeline.example.com/game-app'),
                ('教育平台测试', '在线教育平台测试，包含直播功能', 'not_started', user_ids[1], '2023-06-01 00:00:00', '2023-12-01 23:59:59', 'staging', '["Web", "教育", "直播"]', 'high', 'https://docs.example.com/education-platform', 'https://pipeline.example.com/education-platform'),
                ('医疗应用测试', '医疗健康应用测试，包含预约功能', 'in_progress', user_ids[2], '2023-07-01 00:00:00', '2023-10-31 23:59:59', 'staging', '["移动端", "医疗", "功能测试"]', 'high', 'https://docs.example.com/healthcare-app', 'https://pipeline.example.com/healthcare-app'),
                
                # 测试环境项目
                ('短视频APP测试', '短视频应用测试，包含推荐算法', 'in_progress', user_ids[3], '2023-08-01 00:00:00', '2023-11-30 23:59:59', 'test', '["移动端", "短视频", "算法"]', 'medium', 'https://docs.example.com/short-video-app', 'https://pipeline.example.com/short-video-app'),
                ('外卖平台测试', '外卖应用测试，包含配送系统', 'not_started', user_ids[0], '2023-09-01 00:00:00', '2024-02-29 23:59:59', 'test', '["移动端", "外卖", "配送"]', 'medium', 'https://docs.example.com/food-delivery-app', 'https://pipeline.example.com/food-delivery-app'),
                ('旅游应用测试', '旅游应用测试，包含预订功能', 'completed', user_ids[1], '2023-10-01 00:00:00', '2023-12-31 23:59:59', 'test', '["移动端", "旅游", "预订"]', 'low', 'https://docs.example.com/travel-app', 'https://pipeline.example.com/travel-app'),
                ('新闻应用测试', '新闻应用测试，包含资讯推送', 'in_progress', user_ids[2], '2023-11-01 00:00:00', '2024-04-30 23:59:59', 'test', '["移动端", "新闻", "推送"]', 'low', 'https://docs.example.com/news-app', 'https://pipeline.example.com/news-app'),
                ('音乐APP测试', '音乐应用测试，包含播放功能', 'paused', user_ids[3], '2023-12-01 00:00:00', '2024-03-31 23:59:59', 'test', '["移动端", "音乐", "播放"]', 'medium', 'https://docs.example.com/music-app', 'https://pipeline.example.com/music-app')
            ]
            
            cursor.executemany("""
                INSERT INTO projects (project_name, description, status, owner_id, start_date, end_date, environment, tags, priority, doc_url, pipeline_url) 
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
            
            # 5. 插入版本需求测试数据
            print("开始插入版本需求数据...")
            # 获取所有迭代ID
            cursor.execute("SELECT id FROM iterations")
            iteration_ids = [row[0] for row in cursor.fetchall()]
            
            # 版本需求数据
            requirements_data = []
            requirement_statuses = ['new', 'in_progress', 'completed', 'cancelled']
            priorities = ['high', 'medium', 'low']
            
            # 为每个项目添加版本需求
            for i, project_id in enumerate(project_ids):
                # 为每个项目添加3-5个版本需求
                for j in range(3 + i % 3):
                    requirement_name = f"{i+1}项目需求{j+1}"
                    requirement_description = f"这是第{i+1}个项目的第{j+1}个版本需求，用于测试系统功能"
                    status = requirement_statuses[(i + j) % len(requirement_statuses)]
                    iteration_id = iteration_ids[(i + j) % len(iteration_ids)] if iteration_ids else None
                    priority = priorities[(i + j) % len(priorities)]
                    created_by = user_ids[(i + j) % len(user_ids)]
                    assigned_to = user_ids[(i + j + 1) % len(user_ids)]
                    
                    requirements_data.append((
                        requirement_name,
                        requirement_description,
                        status,
                        project_id,
                        iteration_id,
                        priority,
                        8.0 + j,
                        None if status != 'completed' else 8.0 + j * 0.8,
                        created_by,
                        assigned_to
                    ))
            
            cursor.executemany("""
                INSERT INTO version_requirements (requirement_name, requirement_description, status, project_id, iteration_id, priority, estimated_hours, actual_hours, created_by, assigned_to) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, requirements_data)
            print("版本需求测试数据插入成功！")
            
            connection.commit()
            print("所有测试数据插入成功！")
            print("测试账号信息：")
            print("   - 原始用户：Lethe (超级管理员), Manager (管理员), Tester (测试人员), Admin (实习生)")
            print("   - 新增用户：DDD, EEE, FFF, GGG, HHH, III, JJJ")
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