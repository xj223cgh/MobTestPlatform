#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
更新bugs表结构，添加缺失的字段和索引
"""

import pymysql
import pymysql.cursors
import os
import sys

# 添加项目根目录到Python路径
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

def check_column_exists(cursor, table_name, column_name):
    """检查列是否存在"""
    cursor.execute(
        "SELECT column_name FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = %s AND column_name = %s",
        (table_name, column_name)
    )
    return cursor.fetchone() is not None

def check_index_exists(cursor, table_name, index_name):
    """检查索引是否存在"""
    cursor.execute(
        "SELECT index_name FROM information_schema.statistics WHERE table_schema = DATABASE() AND table_name = %s AND index_name = %s",
        (table_name, index_name)
    )
    return cursor.fetchone() is not None

def update_bugs_table():
    """更新bugs表结构"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("开始更新缺陷表结构...")
        print("=" * 50)
        
        # 添加project_id字段
        if not check_column_exists(cursor, 'bugs', 'project_id'):
            try:
                cursor.execute("""
                    ALTER TABLE bugs
                    ADD COLUMN project_id INT COMMENT '所属项目ID',
                    ADD INDEX idx_project_id (project_id),
                    ADD CONSTRAINT fk_bugs_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
                """)
                print("成功添加project_id字段及相关索引和外键约束")
            except Exception as e:
                print(f"添加project_id字段失败: {e}")
        else:
            print("project_id字段已存在，跳过")
        
        # 添加iteration_id字段
        if not check_column_exists(cursor, 'bugs', 'iteration_id'):
            try:
                cursor.execute("""
                    ALTER TABLE bugs
                    ADD COLUMN iteration_id INT COMMENT '所属迭代ID',
                    ADD INDEX idx_iteration_id (iteration_id),
                    ADD CONSTRAINT fk_bugs_iteration FOREIGN KEY (iteration_id) REFERENCES iterations(id) ON DELETE SET NULL
                """)
                print("成功添加iteration_id字段及相关索引和外键约束")
            except Exception as e:
                print(f"添加iteration_id字段失败: {e}")
        else:
            print("iteration_id字段已存在，跳过")
        
        # 添加created_at字段
        if not check_column_exists(cursor, 'bugs', 'created_at'):
            try:
                cursor.execute("""
                    ALTER TABLE bugs
                    ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
                """)
                print("成功添加created_at字段")
            except Exception as e:
                print(f"添加created_at字段失败: {e}")
        else:
            print("created_at字段已存在，跳过")
        
        # 添加updated_at字段
        if not check_column_exists(cursor, 'bugs', 'updated_at'):
            try:
                cursor.execute("""
                    ALTER TABLE bugs
                    ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
                """)
                print("成功添加updated_at字段")
            except Exception as e:
                print(f"添加updated_at字段失败: {e}")
        else:
            print("updated_at字段已存在，跳过")
        
        # 添加resolved_at字段
        if not check_column_exists(cursor, 'bugs', 'resolved_at'):
            try:
                cursor.execute("""
                    ALTER TABLE bugs
                    ADD COLUMN resolved_at DATETIME COMMENT '解决时间'
                """)
                print("成功添加resolved_at字段")
            except Exception as e:
                print(f"添加resolved_at字段失败: {e}")
        else:
            print("resolved_at字段已存在，跳过")
        
        # 提交事务
        conn.commit()
        print("\n缺陷表结构更新完成！")
        print("=" * 50)
        
    except Exception as e:
        print(f"更新缺陷表结构时发生错误: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    update_bugs_table()
    print("数据表更新完成！")
