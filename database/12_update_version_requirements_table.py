#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库更新脚本 - 更新version_requirements表，添加新字段
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

def update_version_requirements_table():
    """更新version_requirements表，添加新字段"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            # 1. 检查并添加module字段
            cursor.execute("SHOW COLUMNS FROM version_requirements LIKE 'module'")
            result = cursor.fetchone()
            if not result:
                print("开始添加module字段到version_requirements表...")
                cursor.execute("""
                    ALTER TABLE version_requirements 
                    ADD COLUMN module VARCHAR(100) NULL COMMENT '所属模块' AFTER requirement_description
                """)
                print("module字段添加成功！")
            else:
                print("module字段已存在，检查并修改为允许NULL...")
                cursor.execute("""
                    ALTER TABLE version_requirements 
                    MODIFY COLUMN module VARCHAR(100) NULL COMMENT '所属模块'
                """)
                print("module字段修改为允许NULL成功！")
            
            # 2. 检查并添加start_date字段
            cursor.execute("SHOW COLUMNS FROM version_requirements LIKE 'start_date'")
            result = cursor.fetchone()
            if not result:
                print("开始添加start_date字段到version_requirements表...")
                cursor.execute("""
                    ALTER TABLE version_requirements 
                    ADD COLUMN start_date TIMESTAMP COMMENT '开始时间' AFTER assigned_to
                """)
                print("start_date字段添加成功！")
            else:
                print("start_date字段已存在，跳过添加操作！")
            
            # 3. 检查并添加end_date字段
            cursor.execute("SHOW COLUMNS FROM version_requirements LIKE 'end_date'")
            result = cursor.fetchone()
            if not result:
                print("开始添加end_date字段到version_requirements表...")
                cursor.execute("""
                    ALTER TABLE version_requirements 
                    ADD COLUMN end_date TIMESTAMP COMMENT '结束时间' AFTER start_date
                """)
                print("end_date字段添加成功！")
            else:
                print("end_date字段已存在，跳过添加操作！")
            
            # 4. 检查并添加is_deleted字段
            cursor.execute("SHOW COLUMNS FROM version_requirements LIKE 'is_deleted'")
            result = cursor.fetchone()
            if not result:
                print("开始添加is_deleted字段到version_requirements表...")
                cursor.execute("""
                    ALTER TABLE version_requirements 
                    ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE COMMENT '是否逻辑删除' AFTER completed_at
                """)
                print("is_deleted字段添加成功！")
            else:
                print("is_deleted字段已存在，跳过添加操作！")
            
            # 5. 检查并添加created_at字段（如果不存在）
            cursor.execute("SHOW COLUMNS FROM version_requirements LIKE 'created_at'")
            result = cursor.fetchone()
            if not result:
                print("开始添加created_at字段到version_requirements表...")
                cursor.execute("""
                    ALTER TABLE version_requirements 
                    ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间' AFTER end_date
                """)
                print("created_at字段添加成功！")
            else:
                print("created_at字段已存在，跳过添加操作！")
        
        connection.commit()
        print("version_requirements表更新完成！")
        return True
        
    except Exception as e:
        print(f"更新version_requirements表失败: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()

def main():
    """主函数"""
    print("开始更新version_requirements表...")
    
    if update_version_requirements_table():
        print("version_requirements表更新成功！")
        return 0
    else:
        print("version_requirements表更新失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main())
