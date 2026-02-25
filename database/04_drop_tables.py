#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本 - 删除数据表
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

def drop_tables():
    """删除所有数据表"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            # 按照外键依赖关系倒序删除表
            tables = [
                'reports',
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
                'test_cases',
                'test_suites',
                'version_requirements',
                'iterations',
                'project_members',
                'projects',
                'devices',
                'tools',
                'users'
            ]
            
            for table in tables:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
                print(f"✅ 表 {table} 删除成功")
            
            connection.commit()
            print("✅ 所有数据表删除成功！")
            return True
            
    except Exception as e:
        print(f"❌ 删除数据表失败: {e}")
        return False
    finally:
        connection.close()

def main():
    """主函数"""
    print("⚠️  开始删除数据表...")
    print("⚠️  这将删除所有表数据，请确认操作！")
    
    confirm = input("确认删除所有数据表？(y/N): ").lower().strip()
    if confirm != 'y':
        print("❌ 操作已取消")
        return 0
    
    if drop_tables():
        print("🎉 数据表删除完成！")
        return 0
    else:
        print("💥 数据表删除失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main())