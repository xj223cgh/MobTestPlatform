#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本 - 创建数据表
"""

import pymysql
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

def create_tables():
    """创建所有数据表"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            # 创建users表
            cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户编号',
                username VARCHAR(14) NOT NULL UNIQUE COMMENT '用户名（3-14个字节长度限制）',
                phone VARCHAR(11) NOT NULL UNIQUE COMMENT '手机号（需要格式验证）',
                real_name VARCHAR(50) NOT NULL COMMENT '真实姓名',
                gender ENUM('male', 'female', 'other') DEFAULT 'other' COMMENT '性别',
                department VARCHAR(100) DEFAULT '' COMMENT '所属部门',
                password_hash VARCHAR(255) NOT NULL COMMENT '密码（哈希存储）',
                role ENUM('super', 'manager', 'tester', 'admin') NOT NULL DEFAULT 'admin' COMMENT '角色类型',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
                INDEX idx_username (username),
                INDEX idx_phone (phone),
                INDEX idx_role (role)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表'""")
            
            # 创建projects表
            cursor.execute("""CREATE TABLE IF NOT EXISTS projects (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '项目编号',
                project_name VARCHAR(200) NOT NULL UNIQUE COMMENT '项目名称',
                description TEXT COMMENT '项目描述',
                status ENUM('not_started', 'in_progress', 'paused', 'completed', 'closed') DEFAULT 'not_started' COMMENT '项目状态',
                owner_id INT NOT NULL COMMENT '项目负责人ID',
                start_date DATETIME NULL COMMENT '开始日期',
                end_date DATETIME NULL COMMENT '结束日期',
                tags TEXT COMMENT '标签',
                priority ENUM('high', 'medium', 'low') DEFAULT 'medium' COMMENT '优先级',
                doc_url VARCHAR(500) COMMENT '文档链接',
                pipeline_url VARCHAR(500) COMMENT '流水线链接',
                is_deleted BOOLEAN DEFAULT FALSE COMMENT '是否删除',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                creator_id INT NOT NULL COMMENT '创建者ID',
                FOREIGN KEY (owner_id) REFERENCES users(id),
                FOREIGN KEY (creator_id) REFERENCES users(id),
                INDEX idx_project_name (project_name),
                INDEX idx_owner_id (owner_id),
                INDEX idx_creator_id (creator_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='项目表'""")
            
            # 创建project_members表
            cursor.execute("""CREATE TABLE IF NOT EXISTS project_members (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '成员ID',
                project_id INT NOT NULL COMMENT '项目ID',
                user_id INT NOT NULL COMMENT '用户ID',
                role ENUM('owner', 'manager', 'tester', 'viewer') DEFAULT 'tester' COMMENT '项目角色',
                joined_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '加入时间',
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE KEY idx_project_user (project_id, user_id),
                INDEX idx_user_id (user_id),
                INDEX idx_project_id_user_id (project_id, user_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='项目成员表'""")
            
            # 创建devices表
            cursor.execute("""CREATE TABLE IF NOT EXISTS devices (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '设备编号',
                device_name VARCHAR(100) NOT NULL COMMENT '设备名称',
                device_model VARCHAR(100) NOT NULL COMMENT '设备型号',
                os_type ENUM('android', 'ios') NOT NULL COMMENT '操作系统类型',
                os_version VARCHAR(50) NOT NULL COMMENT '操作系统版本',
                device_id VARCHAR(100) UNIQUE NOT NULL COMMENT '设备唯一标识',
                status ENUM('online', 'offline', 'busy', 'maintenance') DEFAULT 'offline' COMMENT '设备状态',
                owner_id INT COMMENT '设备负责人ID',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE SET NULL,
                INDEX idx_device_id (device_id),
                INDEX idx_status (status),
                INDEX idx_os_type (os_type),
                INDEX idx_owner_id (owner_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='设备表'""")
            
            # 创建iterations表
            cursor.execute("""CREATE TABLE IF NOT EXISTS iterations (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '迭代编号',
                project_id INT NOT NULL COMMENT '所属项目ID',
                iteration_name VARCHAR(200) NOT NULL COMMENT '迭代名称',
                description TEXT COMMENT '迭代描述',
                goal TEXT COMMENT '迭代目标',
                status ENUM('planning', 'active', 'completed', 'cancelled') DEFAULT 'planning' COMMENT '迭代状态',
                start_date DATETIME NOT NULL COMMENT '开始日期',
                end_date DATETIME NOT NULL COMMENT '结束日期',
                version VARCHAR(100) COMMENT '版本信息',
                created_by INT COMMENT '创建者ID',
                updated_by INT COMMENT '更新者ID',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (created_by) REFERENCES users(id),
                FOREIGN KEY (updated_by) REFERENCES users(id),
                INDEX idx_project_id (project_id),
                INDEX idx_created_by (created_by),
                INDEX idx_updated_by (updated_by)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='迭代表'""")
            
            # 创建version_requirements表
            cursor.execute("""CREATE TABLE IF NOT EXISTS version_requirements (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '需求编号',
                requirement_name VARCHAR(200) NOT NULL COMMENT '需求名称',
                requirement_description TEXT COMMENT '需求描述',
                module VARCHAR(100) NULL COMMENT '所属模块',
                status ENUM('new', 'in_progress', 'completed', 'cancelled') DEFAULT 'new' COMMENT '需求状态',
                project_id INT NOT NULL COMMENT '所属项目ID',
                iteration_id INT COMMENT '所属迭代ID',
                priority ENUM('high', 'medium', 'low') DEFAULT 'medium' COMMENT '优先级',
                estimated_hours FLOAT COMMENT '预估工时',
                actual_hours FLOAT COMMENT '实际工时',
                created_by INT NOT NULL COMMENT '创建者ID',
                assigned_to INT COMMENT '分配给ID',
                start_date DATETIME COMMENT '开始时间',
                end_date DATETIME COMMENT '结束时间',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                is_deleted BOOLEAN DEFAULT FALSE COMMENT '是否逻辑删除',
                environment ENUM('test', 'staging', 'production') DEFAULT 'test' COMMENT '环境',
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (iteration_id) REFERENCES iterations(id) ON DELETE SET NULL,
                FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL,
                INDEX idx_project_id (project_id),
                INDEX idx_iteration_id (iteration_id),
                INDEX idx_created_by (created_by),
                INDEX idx_assigned_to (assigned_to)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='版本需求表'""")
            
            # 创建test_suites表
            cursor.execute("""CREATE TABLE IF NOT EXISTS test_suites (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '套件编号',
                suite_name VARCHAR(200) NOT NULL COMMENT '套件名称',
                description TEXT COMMENT '套件描述',
                parent_id INT COMMENT '父套件ID，用于构建目录结构',
                status ENUM('active', 'inactive') DEFAULT 'active' COMMENT '状态',
                type ENUM('folder', 'suite') DEFAULT 'folder' COMMENT '类型：folder-用例文件夹, suite-用例集',
                creator_id INT NOT NULL COMMENT '创建者ID',
                project_id INT NULL COMMENT '所属项目ID',
                version_requirement_id INT NULL COMMENT '关联的版本需求ID',
                iteration_id INT NULL COMMENT '所属迭代ID',
                sort_order INT DEFAULT 0 COMMENT '排序顺序',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                FOREIGN KEY (parent_id) REFERENCES test_suites(id) ON DELETE SET NULL,
                FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL,
                FOREIGN KEY (version_requirement_id) REFERENCES version_requirements(id) ON DELETE SET NULL,
                FOREIGN KEY (iteration_id) REFERENCES iterations(id) ON DELETE SET NULL,
                INDEX idx_parent_id (parent_id),
                INDEX idx_creator_id (creator_id),
                INDEX idx_project_id (project_id),
                INDEX idx_version_requirement_id (version_requirement_id),
                INDEX idx_iteration_id (iteration_id),
                INDEX idx_type (type),
                INDEX idx_sort_order (sort_order)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='测试套件表'""")
            
            # 创建test_cases表
            cursor.execute("""CREATE TABLE IF NOT EXISTS test_cases (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用例编号',
                case_number VARCHAR(50) NULL COMMENT '测试用例编号',
                case_name VARCHAR(200) NOT NULL COMMENT '用例名称',
                case_description TEXT COMMENT '用例描述',
                priority ENUM('P0', 'P1', 'P2', 'P3', 'P4') DEFAULT 'P1' COMMENT '优先级',
                status ENUM('', 'pass', 'fail', 'blocked', 'not_applicable') DEFAULT '' COMMENT '状态',
                creator_id INT NOT NULL COMMENT '创建者ID',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                project_id INT NOT NULL COMMENT '所属项目ID',
                version_requirement_id INT COMMENT '关联的版本需求ID',
                iteration_id INT COMMENT '所属迭代ID',
                suite_id INT NOT NULL COMMENT '所属套件ID',
                preconditions TEXT COMMENT '前置条件',
                steps TEXT COMMENT '测试步骤',
                expected_result TEXT COMMENT '预期结果',
                actual_result TEXT COMMENT '实际结果',
                test_data TEXT COMMENT '测试数据',
                executed_at DATETIME NULL COMMENT '最后执行时间',
                assignee_id INT COMMENT '负责人ID',
                reviewer_id INT COMMENT '审核人ID',
                review_comments TEXT COMMENT '审核意见',
                last_reviewed_at TIMESTAMP NULL COMMENT '最后评审时间',
                FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (version_requirement_id) REFERENCES version_requirements(id) ON DELETE SET NULL,
                FOREIGN KEY (iteration_id) REFERENCES iterations(id) ON DELETE SET NULL,
                FOREIGN KEY (suite_id) REFERENCES test_suites(id) ON DELETE CASCADE,
                FOREIGN KEY (assignee_id) REFERENCES users(id) ON DELETE SET NULL,
                FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE SET NULL,
                INDEX idx_case_name (case_name),
                INDEX idx_priority (priority),
                INDEX idx_status (status),
                INDEX idx_creator_id (creator_id),
                INDEX idx_project_id (project_id),
                INDEX idx_iteration_id (iteration_id),
                INDEX idx_suite_id (suite_id),
                INDEX idx_version_requirement_id (version_requirement_id),
                INDEX idx_assignee_id (assignee_id),
                INDEX idx_reviewer_id (reviewer_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用例表'""")
            

            
            # 创建test_tasks表
            cursor.execute("""CREATE TABLE IF NOT EXISTS test_tasks (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '任务编号',
                task_name VARCHAR(200) NOT NULL COMMENT '任务名称',
                task_description TEXT COMMENT '任务描述',
                task_type ENUM('test_case', 'device_script') DEFAULT 'test_case' COMMENT '任务类型',
                priority ENUM('high', 'medium', 'low') DEFAULT 'medium' COMMENT '任务优先级',
                status ENUM('pending', 'running', 'completed', 'paused') DEFAULT 'pending' COMMENT '任务状态',
                creator_id INT NOT NULL COMMENT '创建者ID',
                executor_id INT COMMENT '执行者ID',
                scheduled_time TIMESTAMP NULL COMMENT '计划执行时间',
                scheduled_end_time TIMESTAMP NULL COMMENT '计划结束时间',
                started_time TIMESTAMP NULL COMMENT '开始执行时间',
                completed_time TIMESTAMP NULL COMMENT '完成时间',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                project_id INT NULL COMMENT '所属项目ID',
                iteration_id INT NULL COMMENT '所属迭代ID',
                suite_id INT NULL COMMENT '关联的测试套件ID',
                version_requirement_id INT NULL COMMENT '关联的版本需求ID',
                documentation_url TEXT COMMENT '相关文档链接',
                version_info VARCHAR(100) COMMENT '版本信息',
                result TEXT NULL COMMENT '任务执行结果，JSON格式存储',
                # 设备脚本任务专用字段
                script_file VARCHAR(200) NULL COMMENT '脚本文件名',
                file_path VARCHAR(500) NULL COMMENT '服务器上的相对存储路径',
                file_hash VARCHAR(100) NULL COMMENT '文件哈希值（用于验证文件完整性）',
                command TEXT NULL COMMENT '完整执行命令',
                FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (executor_id) REFERENCES users(id) ON DELETE SET NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL,
                FOREIGN KEY (iteration_id) REFERENCES iterations(id) ON DELETE SET NULL,
                FOREIGN KEY (suite_id) REFERENCES test_suites(id) ON DELETE SET NULL,
                FOREIGN KEY (version_requirement_id) REFERENCES version_requirements(id) ON DELETE SET NULL,
                INDEX idx_task_name (task_name),
                INDEX idx_status (status),
                INDEX idx_creator_id (creator_id),
                INDEX idx_executor_id (executor_id),
                INDEX idx_scheduled_time (scheduled_time),
                INDEX idx_project_id (project_id),
                INDEX idx_iteration_id (iteration_id),
                INDEX idx_suite_id (suite_id),
                INDEX idx_version_requirement_id (version_requirement_id),
                INDEX idx_task_type (task_type)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='测试任务表'""")
            
            # 创建test_case_executions表
            cursor.execute("""CREATE TABLE IF NOT EXISTS test_case_executions (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '执行记录ID',
                task_id INT NOT NULL COMMENT '任务ID',
                case_id INT NOT NULL COMMENT '用例ID',
                project_id INT NULL COMMENT '所属项目ID',
                iteration_id INT NULL COMMENT '所属迭代ID',
                status ENUM('pass', 'fail', 'blocked', 'not_applicable') DEFAULT 'not_applicable' COMMENT '执行状态',
                executor_id INT NULL COMMENT '执行人ID（允许为空）',
                execution_time DATETIME NULL COMMENT '执行时间',
                notes TEXT COMMENT '备注',
                FOREIGN KEY (task_id) REFERENCES test_tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (case_id) REFERENCES test_cases(id) ON DELETE CASCADE,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL,
                FOREIGN KEY (iteration_id) REFERENCES iterations(id) ON DELETE SET NULL,
                FOREIGN KEY (executor_id) REFERENCES users(id) ON DELETE SET NULL,
                INDEX idx_task_id (task_id),
                INDEX idx_case_id (case_id),
                INDEX idx_executor_id (executor_id),
                INDEX idx_project_id (project_id),
                INDEX idx_iteration_id (iteration_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='测试用例执行记录表'""")
            
            # 创建tools表
            cursor.execute("""CREATE TABLE IF NOT EXISTS tools (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '工具编号',
                tool_name VARCHAR(100) NOT NULL COMMENT '工具名称',
                tool_description TEXT COMMENT '工具描述',
                tool_type ENUM('automation', 'performance', 'monitoring', 'debugging', 'utility') NOT NULL COMMENT '工具类型',
                tool_path VARCHAR(500) NOT NULL COMMENT '工具路径',
                tool_config TEXT COMMENT '工具配置（JSON格式）',
                status ENUM('active', 'inactive', 'maintenance') DEFAULT 'active' COMMENT '状态',
                creator_id INT NOT NULL COMMENT '创建者ID',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_tool_name (tool_name),
                INDEX idx_tool_type (tool_type),
                INDEX idx_status (status),
                INDEX idx_creator_id (creator_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='工具表'""")
            
            # 创建task_case_relation表
            cursor.execute("""CREATE TABLE IF NOT EXISTS task_case_relation (
                task_id INT NOT NULL COMMENT '任务ID',
                case_id INT NOT NULL COMMENT '用例ID',
                PRIMARY KEY (task_id, case_id),
                FOREIGN KEY (task_id) REFERENCES test_tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (case_id) REFERENCES test_cases(id) ON DELETE CASCADE,
                INDEX idx_case_id (case_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='任务用例关联表'""")
            
            # 创建task_device_relation表
            cursor.execute("""CREATE TABLE IF NOT EXISTS task_device_relation (
                task_id INT NOT NULL COMMENT '任务ID',
                device_id INT NOT NULL COMMENT '设备ID',
                PRIMARY KEY (task_id, device_id),
                FOREIGN KEY (task_id) REFERENCES test_tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
                INDEX idx_device_id (device_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='任务设备关联表'""")
            
            # 创建test_suite_review_tasks表
            cursor.execute("""CREATE TABLE IF NOT EXISTS test_suite_review_tasks (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '评审任务ID',
                suite_id INT NOT NULL COMMENT '关联用例集ID',
                initiator_id INT COMMENT '发起人ID',
                reviewer_id INT COMMENT '评审人ID',
                status ENUM('pending', 'in_review', 'completed', 'rejected') DEFAULT 'pending' COMMENT '评审任务状态：pending-待处理, in_review-评审中, completed-已完成, rejected-已拒绝',
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '评审开始时间',
                end_time TIMESTAMP NULL COMMENT '评审结束时间',
                overall_comments TEXT COMMENT '整体评审意见',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                FOREIGN KEY (suite_id) REFERENCES test_suites(id) ON DELETE CASCADE,
                FOREIGN KEY (initiator_id) REFERENCES users(id) ON DELETE SET NULL,
                FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE SET NULL,
                INDEX idx_suite_id (suite_id),
                INDEX idx_initiator_id (initiator_id),
                INDEX idx_reviewer_id (reviewer_id),
                INDEX idx_status (status)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用例集评审任务表'""")
            
            # 创建test_case_review_details表
            cursor.execute("""CREATE TABLE IF NOT EXISTS test_case_review_details (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '评审详情ID',
                review_task_id INT NOT NULL COMMENT '关联评审任务ID',
                case_id INT NOT NULL COMMENT '关联测试用例ID',
                reviewer_id INT COMMENT '评审人ID',
                review_status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending' COMMENT '单条用例评审状态：pending-待审核, approved-已通过, rejected-已拒绝',
                comments TEXT COMMENT '用例评审意见',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                FOREIGN KEY (review_task_id) REFERENCES test_suite_review_tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (case_id) REFERENCES test_cases(id) ON DELETE CASCADE,
                FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE SET NULL,
                UNIQUE KEY idx_review_task_case (review_task_id, case_id),
                INDEX idx_review_task_id (review_task_id),
                INDEX idx_case_id (case_id),
                INDEX idx_reviewer_id (reviewer_id),
                INDEX idx_review_status (review_status)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用例评审详情表'""")
            
            # 创建test_suite_review_history表
            cursor.execute("""CREATE TABLE IF NOT EXISTS test_suite_review_history (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '评审历史ID',
                review_task_id INT COMMENT '关联评审任务ID',
                suite_id INT COMMENT '关联用例集ID',
                initiator_id INT COMMENT '发起人ID',
                reviewer_id INT COMMENT '评审人ID',
                status ENUM('pending', 'in_review', 'completed', 'rejected') COMMENT '评审任务状态',
                start_time TIMESTAMP NULL COMMENT '评审开始时间',
                end_time TIMESTAMP NULL COMMENT '评审结束时间',
                overall_comments TEXT COMMENT '整体评审意见',
                history_type ENUM('complete', 'reject') COMMENT '历史记录类型：complete-完成评审, reject-打回评审',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                created_by INT COMMENT '创建人ID',
                version INT DEFAULT 1 COMMENT '评审版本号',
                FOREIGN KEY (review_task_id) REFERENCES test_suite_review_tasks(id) ON DELETE SET NULL,
                FOREIGN KEY (suite_id) REFERENCES test_suites(id) ON DELETE SET NULL,
                FOREIGN KEY (initiator_id) REFERENCES users(id) ON DELETE SET NULL,
                FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE SET NULL,
                FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='评审历史记录模型'""")
            
            # 创建test_case_review_history表
            cursor.execute("""CREATE TABLE IF NOT EXISTS test_case_review_history (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用例评审历史ID',
                review_history_id INT NOT NULL COMMENT '关联评审历史ID',
                review_task_id INT COMMENT '关联评审任务ID',
                case_id INT COMMENT '关联测试用例ID',
                reviewer_id INT COMMENT '评审人ID',
                review_status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending' COMMENT '单条用例评审状态',
                comments TEXT COMMENT '用例评审意见',
                case_number VARCHAR(50) NULL COMMENT '用例编号',
                case_name VARCHAR(200) NULL COMMENT '用例名称',
                priority ENUM('P0', 'P1', 'P2', 'P3', 'P4') DEFAULT 'P1' COMMENT '优先级',
                test_data TEXT NULL COMMENT '测试数据',
                preconditions TEXT COMMENT '前置条件',
                steps TEXT COMMENT '测试步骤',
                expected_result TEXT COMMENT '预期结果',
                actual_result TEXT COMMENT '实际结果',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                created_by INT COMMENT '创建人ID',
                FOREIGN KEY (review_history_id) REFERENCES test_suite_review_history(id) ON DELETE CASCADE,
                FOREIGN KEY (case_id) REFERENCES test_cases(id) ON DELETE SET NULL,
                FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE SET NULL,
                FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用例评审历史记录模型'""")

            # 创建system_settings表（系统级设置，全局生效）
            cursor.execute("""CREATE TABLE IF NOT EXISTS system_settings (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '设置ID',
                setting_key VARCHAR(100) NOT NULL UNIQUE COMMENT '设置键，如 auto_generate_report',
                setting_value TEXT COMMENT '设置值，可为字符串或JSON',
                description VARCHAR(255) DEFAULT NULL COMMENT '设置说明',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                INDEX idx_setting_key (setting_key)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统设置表'""")

            # 创建user_settings表（用户个人设置，按用户隔离）
            cursor.execute("""CREATE TABLE IF NOT EXISTS user_settings (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '设置ID',
                user_id INT NOT NULL COMMENT '用户ID',
                setting_key VARCHAR(100) NOT NULL COMMENT '设置键，如 auto_generate_report',
                setting_value TEXT COMMENT '设置值，可为字符串或JSON',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY uk_user_setting (user_id, setting_key),
                INDEX idx_user_id (user_id),
                INDEX idx_setting_key (setting_key)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户个人设置表'""")

            # 创建reports表（报告落库，关联任务）
            cursor.execute("""CREATE TABLE IF NOT EXISTS reports (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '报告ID',
                task_id INT NOT NULL COMMENT '关联任务ID',
                report_type ENUM('test_case', 'device_script') NOT NULL COMMENT '报告类型',
                task_name VARCHAR(200) NOT NULL COMMENT '任务名称（冗余）',
                project_id INT NULL COMMENT '项目ID（冗余）',
                project_name VARCHAR(200) NULL COMMENT '项目名称（冗余）',
                summary JSON COMMENT '报告摘要',
                details JSON COMMENT '报告明细',
                completed_at TIMESTAMP NULL COMMENT '任务完成时间',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '报告生成时间',
                creator_id INT NULL COMMENT '创建人ID',
                FOREIGN KEY (task_id) REFERENCES test_tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE SET NULL,
                INDEX idx_task_id (task_id),
                INDEX idx_report_type (report_type),
                INDEX idx_completed_at (completed_at),
                INDEX idx_created_at (created_at),
                INDEX idx_creator_id (creator_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='报告表'""")
            
            connection.commit()
            print("所有数据表创建成功！")
            return True
            
    except Exception as e:
        print(f"创建数据表失败: {e}")
        return False
    finally:
        connection.close()

def main():
    """主函数"""
    print("开始创建数据表...")
    
    if create_tables():
        print("数据表创建完成！")
        return 0
    else:
        print("数据表创建失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main())
