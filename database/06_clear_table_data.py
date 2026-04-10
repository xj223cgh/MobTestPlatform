#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本 - 清空表数据
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

def clear_table_data():
    """清空所有表数据"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            # 按照外键依赖关系倒序清空表数据
            tables = [
                'reports',
                'notifications',
                'user_settings',
                'system_settings',
                'test_case_review_history',
                'test_suite_review_history',
                'test_case_review_details',
                'test_suite_review_tasks',
                'task_case_snapshots',
                'task_device_relation',
                'task_case_relation',
                'test_case_executions',
                'test_tasks',
                'task_folders',
                'case_tags',
                'case_markers',
                'test_cases',
                'mindmap_versions',
                'test_suites',
                'version_requirements',
                'iterations',
                'project_members',
                'projects',
                'devices',
                'agent_binding_codes',
                'user_agent_bindings',
                'agents',
                'role_permissions',
                'email_verify_codes',
                'users'
            ]
            
            # 禁用外键检查
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            for table in tables:
                cursor.execute(f"TRUNCATE TABLE {table}")
                print(f"✅ 表 {table} 数据清空成功")
            
            # 重新启用外键检查
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            
            connection.commit()
            print("✅ 所有表数据清空成功！")
            return True
            
    except Exception as e:
        print(f"❌ 清空表数据失败: {e}")
        return False
    finally:
        connection.close()

def main():
    """主函数"""
    print("⚠️  开始清空所有表数据...")
    print("⚠️  这将删除所有数据但保留表结构，请确认操作！")
    
    confirm = input("确认清空所有表数据？(y/N): ").lower().strip()
    if confirm != 'y':
        print("❌ 操作已取消")
        return 0
    
    if clear_table_data():
        print("🎉 表数据清空完成！")
        return 0
    else:
        print("💥 表数据清空失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main())