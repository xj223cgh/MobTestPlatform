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
                sort_order INT DEFAULT 0 COMMENT '排序顺序',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                FOREIGN KEY (parent_id) REFERENCES test_suites(id) ON DELETE SET NULL,
                FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL,
                INDEX idx_parent_id (parent_id),
                INDEX idx_creator_id (creator_id),
                INDEX idx_project_id (project_id),
                INDEX idx_type (type),
                INDEX idx_sort_order (sort_order)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='测试套件表'""")
            
            # 创建test_cases表
            cursor.execute("""CREATE TABLE IF NOT EXISTS test_cases (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用例编号',
                case_name VARCHAR(200) NOT NULL COMMENT '用例名称',
                case_description TEXT COMMENT '用例描述',
                module VARCHAR(100) NOT NULL COMMENT '所属模块',
                priority ENUM('high', 'medium', 'low') DEFAULT 'medium' COMMENT '优先级',
                status ENUM('draft', 'active', 'deprecated') DEFAULT 'draft' COMMENT '状态',
                creator_id INT NOT NULL COMMENT '创建者ID',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                project_id INT NOT NULL COMMENT '所属项目ID',
                version_requirement_id INT UNIQUE COMMENT '关联的版本需求ID',
                iteration_id INT COMMENT '所属迭代ID',
                test_plan_id INT COMMENT '所属测试计划ID',
                suite_id INT COMMENT '所属套件ID',
                precondition TEXT COMMENT '前置条件',
                test_data TEXT COMMENT '测试数据',
                expected_result TEXT COMMENT '预期结果',
                actual_result TEXT COMMENT '实际结果',
                author VARCHAR(50) DEFAULT '' COMMENT '作者',
                assignee VARCHAR(50) DEFAULT '' COMMENT '负责人',
                version_info VARCHAR(100) DEFAULT '' COMMENT '版本信息',
                xmind_data LONGTEXT COMMENT 'xmind格式的用例数据（JSON字符串）',
                preconditions TEXT COMMENT '前置条件',
                steps TEXT COMMENT '测试步骤',
                FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (version_requirement_id) REFERENCES version_requirements(id) ON DELETE SET NULL,
                FOREIGN KEY (iteration_id) REFERENCES iterations(id) ON DELETE SET NULL,
                FOREIGN KEY (test_plan_id) REFERENCES test_plans(id) ON DELETE SET NULL,
                FOREIGN KEY (suite_id) REFERENCES test_suites(id) ON DELETE SET NULL,
                INDEX idx_case_name (case_name),
                INDEX idx_module (module),
                INDEX idx_priority (priority),
                INDEX idx_status (status),
                INDEX idx_creator_id (creator_id),
                INDEX idx_project_id (project_id),
                INDEX idx_iteration_id (iteration_id),
                INDEX idx_test_plan_id (test_plan_id),
                INDEX idx_suite_id (suite_id),
                INDEX idx_version_requirement_id (version_requirement_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用例表'""")
            
            # 创建test_plans表
            cursor.execute("""CREATE TABLE IF NOT EXISTS test_plans (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '测试计划编号',
                project_id INT NOT NULL COMMENT '所属项目ID',
                iteration_id INT COMMENT '所属迭代ID',
                plan_name VARCHAR(200) NOT NULL COMMENT '计划名称',
                description TEXT COMMENT '计划描述',
                status ENUM('draft', 'active', 'completed', 'cancelled') DEFAULT 'draft' COMMENT '状态',
                scope TEXT COMMENT '测试范围',
                test_environment TEXT COMMENT '测试环境',
                risk TEXT COMMENT '风险评估',
                created_by INT NOT NULL COMMENT '创建者ID',
                start_date DATETIME NULL COMMENT '开始日期',
                end_date DATETIME NULL COMMENT '结束日期',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (iteration_id) REFERENCES iterations(id) ON DELETE SET NULL,
                FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_project_id (project_id),
                INDEX idx_iteration_id (iteration_id),
                INDEX idx_created_by (created_by)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='测试计划表'""")
            
            # 创建test_tasks表
            cursor.execute("""CREATE TABLE IF NOT EXISTS test_tasks (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '任务编号',
                task_name VARCHAR(200) NOT NULL COMMENT '任务名称',
                task_description TEXT COMMENT '任务描述',
                device_id INT NOT NULL COMMENT '测试设备ID',
                case_ids TEXT NOT NULL COMMENT '测试用例ID列表（JSON格式）',
                status ENUM('pending', 'running', 'completed', 'failed', 'cancelled') DEFAULT 'pending' COMMENT '任务状态',
                creator_id INT NOT NULL COMMENT '创建者ID',
                executor_id INT COMMENT '执行者ID',
                scheduled_time TIMESTAMP NULL COMMENT '计划执行时间',
                started_time TIMESTAMP NULL COMMENT '开始执行时间',
                completed_time TIMESTAMP NULL COMMENT '完成时间',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                project_id INT NULL COMMENT '所属项目ID',
                iteration_id INT NULL COMMENT '所属迭代ID',
                test_plan_id INT NULL COMMENT '所属测试计划ID',
                suite_id INT NULL COMMENT '关联的测试套件ID',
                documentation_url TEXT COMMENT '相关文档链接',
                version_info VARCHAR(100) COMMENT '版本信息',
                FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
                FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (executor_id) REFERENCES users(id) ON DELETE SET NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL,
                FOREIGN KEY (iteration_id) REFERENCES iterations(id) ON DELETE SET NULL,
                FOREIGN KEY (test_plan_id) REFERENCES test_plans(id) ON DELETE SET NULL,
                FOREIGN KEY (suite_id) REFERENCES test_suites(id) ON DELETE SET NULL,
                INDEX idx_task_name (task_name),
                INDEX idx_status (status),
                INDEX idx_creator_id (creator_id),
                INDEX idx_executor_id (executor_id),
                INDEX idx_scheduled_time (scheduled_time),
                INDEX idx_project_id (project_id),
                INDEX idx_iteration_id (iteration_id),
                INDEX idx_test_plan_id (test_plan_id),
                INDEX idx_suite_id (suite_id),
                INDEX idx_device_id (device_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='测试任务表'""")
            
            # 创建test_case_executions表
            cursor.execute("""CREATE TABLE IF NOT EXISTS test_case_executions (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '执行记录ID',
                task_id INT NOT NULL COMMENT '任务ID',
                case_id INT NOT NULL COMMENT '用例ID',
                project_id INT NULL COMMENT '所属项目ID',
                iteration_id INT NULL COMMENT '所属迭代ID',
                status ENUM('pass', 'fail', 'blocked', 'not_applicable') DEFAULT 'not_applicable' COMMENT '执行状态',
                executor_id INT NOT NULL COMMENT '执行者ID',
                execution_time DATETIME NULL COMMENT '执行时间',
                notes TEXT COMMENT '备注',
                FOREIGN KEY (task_id) REFERENCES test_tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (case_id) REFERENCES test_cases(id) ON DELETE CASCADE,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL,
                FOREIGN KEY (iteration_id) REFERENCES iterations(id) ON DELETE SET NULL,
                FOREIGN KEY (executor_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_task_id (task_id),
                INDEX idx_case_id (case_id),
                INDEX idx_executor_id (executor_id),
                INDEX idx_project_id (project_id),
                INDEX idx_iteration_id (iteration_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='测试用例执行记录表'""")
            
            # 创建test_executions表
            cursor.execute("""CREATE TABLE IF NOT EXISTS test_executions (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '执行ID',
                task_id INT NOT NULL COMMENT '任务ID',
                device_id INT NOT NULL COMMENT '设备ID',
                environment_id INT NULL COMMENT '环境ID',
                execution_status VARCHAR(20) DEFAULT 'pending' COMMENT '执行状态',
                start_time DATETIME NULL COMMENT '开始时间',
                end_time DATETIME NULL COMMENT '结束时间',
                executor_id INT NOT NULL COMMENT '执行人ID',
                FOREIGN KEY (task_id) REFERENCES test_tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
                FOREIGN KEY (executor_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_task_id (task_id),
                INDEX idx_device_id (device_id),
                INDEX idx_executor_id (executor_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='测试执行表'""")
            
            # 创建bugs表
            cursor.execute("""CREATE TABLE IF NOT EXISTS bugs (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '缺陷编号',
                bug_title VARCHAR(200) NOT NULL COMMENT '缺陷标题',
                bug_description TEXT NOT NULL COMMENT '缺陷描述',
                severity ENUM('critical', 'high', 'medium', 'low') DEFAULT 'medium' COMMENT '严重程度',
                priority ENUM('high', 'medium', 'low') DEFAULT 'medium' COMMENT '优先级',
                status ENUM('open', 'in_progress', 'resolved', 'closed', 'reopened') DEFAULT 'open' COMMENT '状态',
                module VARCHAR(100) NOT NULL COMMENT '所属模块',
                device_id INT DEFAULT NULL COMMENT '相关设备ID',
                case_id INT DEFAULT NULL COMMENT '相关用例ID',
                task_id INT DEFAULT NULL COMMENT '相关任务ID',
                reporter_id INT NOT NULL COMMENT '报告者ID',
                assignee_id INT DEFAULT NULL COMMENT '分配给ID',
                project_id INT DEFAULT NULL COMMENT '所属项目ID',
                iteration_id INT DEFAULT NULL COMMENT '所属迭代ID',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                resolved_at TIMESTAMP NULL COMMENT '解决时间',
                FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE SET NULL,
                FOREIGN KEY (case_id) REFERENCES test_cases(id) ON DELETE SET NULL,
                FOREIGN KEY (task_id) REFERENCES test_tasks(id) ON DELETE SET NULL,
                FOREIGN KEY (reporter_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (assignee_id) REFERENCES users(id) ON DELETE SET NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL,
                FOREIGN KEY (iteration_id) REFERENCES iterations(id) ON DELETE SET NULL,
                INDEX idx_bug_title (bug_title),
                INDEX idx_reporter_id (reporter_id),
                INDEX idx_assignee_id (assignee_id),
                INDEX idx_module (module),
                INDEX idx_status (status),
                INDEX idx_severity (severity),
                INDEX idx_priority (priority),
                INDEX idx_case_id (case_id),
                INDEX idx_task_id (task_id),
                INDEX idx_device_id (device_id),
                INDEX idx_project_id (project_id),
                INDEX idx_iteration_id (iteration_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='缺陷表'""")
            
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
            
            # 创建execution_bug_relations表
            cursor.execute("""CREATE TABLE IF NOT EXISTS execution_bug_relations (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '关系ID',
                execution_id INT NOT NULL COMMENT '执行ID',
                bug_id INT NOT NULL COMMENT '缺陷ID',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                FOREIGN KEY (execution_id) REFERENCES test_case_executions(id) ON DELETE CASCADE,
                FOREIGN KEY (bug_id) REFERENCES bugs(id) ON DELETE CASCADE,
                UNIQUE KEY idx_execution_bug (execution_id, bug_id),
                INDEX idx_bug_id (bug_id),
                INDEX idx_execution_bug_relation (bug_id, execution_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='执行缺陷关联表'""")
            
            # 创建plan_case_relation表
            cursor.execute("""CREATE TABLE IF NOT EXISTS plan_case_relation (
                plan_id INT NOT NULL COMMENT '测试计划ID',
                case_id INT NOT NULL COMMENT '测试用例ID',
                FOREIGN KEY (plan_id) REFERENCES test_plans(id) ON DELETE CASCADE,
                FOREIGN KEY (case_id) REFERENCES test_cases(id) ON DELETE CASCADE,
                UNIQUE KEY idx_plan_case (plan_id, case_id),
                INDEX idx_case_id (case_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='测试计划用例关联表'""")
            
            # 创建task_case_relation表
            cursor.execute("""CREATE TABLE IF NOT EXISTS task_case_relation (
                task_id INT NOT NULL COMMENT '任务ID',
                case_id INT NOT NULL COMMENT '用例ID',
                FOREIGN KEY (task_id) REFERENCES test_tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (case_id) REFERENCES test_cases(id) ON DELETE CASCADE,
                UNIQUE KEY idx_task_case (task_id, case_id),
                INDEX idx_case_id (case_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='任务用例关联表'""")
            
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
