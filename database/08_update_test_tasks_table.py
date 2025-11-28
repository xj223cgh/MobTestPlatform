#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库更新脚本 - 为test_tasks表添加缺失的字段
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

def check_column_exists(cursor, table, column):
    """检查字段是否存在"""
    cursor.execute("""
        SELECT COLUMN_NAME FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s
    """, (table, column))
    return cursor.fetchone() is not None

def check_index_exists(cursor, table, index):
    """检查索引是否存在"""
    cursor.execute("""
        SELECT INDEX_NAME FROM information_schema.STATISTICS 
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND INDEX_NAME = %s
    """, (table, index))
    return cursor.fetchone() is not None

def update_test_tasks_table():
    """更新test_tasks表结构，添加缺失的字段"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            # 添加project_id字段
            if not check_column_exists(cursor, 'test_tasks', 'project_id'):
                try:
                    cursor.execute("""
                        ALTER TABLE test_tasks
                        ADD COLUMN project_id INT NULL COMMENT '所属项目ID'
                    """)
                    print("成功添加project_id字段")
                    
                    # 添加索引
                    if not check_index_exists(cursor, 'test_tasks', 'idx_project_id'):
                        cursor.execute("ALTER TABLE test_tasks ADD INDEX idx_project_id (project_id)")
                        print("成功添加project_id索引")
                    
                    # 添加外键约束
                    cursor.execute("""
                        ALTER TABLE test_tasks
                        ADD CONSTRAINT fk_task_project
                        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
                    """)
                    print("成功添加project_id外键约束")
                    
                except Exception as e:
                    print(f"添加project_id相关操作失败: {e}")
            else:
                print("project_id字段已存在，跳过")
            
            # 添加iteration_id字段
            if not check_column_exists(cursor, 'test_tasks', 'iteration_id'):
                try:
                    cursor.execute("""
                        ALTER TABLE test_tasks
                        ADD COLUMN iteration_id INT NULL COMMENT '所属迭代ID'
                    """)
                    print("成功添加iteration_id字段")
                    
                    # 添加索引
                    if not check_index_exists(cursor, 'test_tasks', 'idx_iteration_id'):
                        cursor.execute("ALTER TABLE test_tasks ADD INDEX idx_iteration_id (iteration_id)")
                        print("成功添加iteration_id索引")
                    
                    # 添加外键约束
                    cursor.execute("""
                        ALTER TABLE test_tasks
                        ADD CONSTRAINT fk_task_iteration
                        FOREIGN KEY (iteration_id) REFERENCES iterations(id) ON DELETE SET NULL
                    """)
                    print("成功添加iteration_id外键约束")
                    
                except Exception as e:
                    print(f"添加iteration_id相关操作失败: {e}")
            else:
                print("iteration_id字段已存在，跳过")
            
            # 添加test_plan_id字段
            if not check_column_exists(cursor, 'test_tasks', 'test_plan_id'):
                try:
                    cursor.execute("""
                        ALTER TABLE test_tasks
                        ADD COLUMN test_plan_id INT NULL COMMENT '所属测试计划ID'
                    """)
                    print("成功添加test_plan_id字段")
                    
                    # 添加索引
                    if not check_index_exists(cursor, 'test_tasks', 'idx_test_plan_id'):
                        cursor.execute("ALTER TABLE test_tasks ADD INDEX idx_test_plan_id (test_plan_id)")
                        print("成功添加test_plan_id索引")
                    
                    # 添加外键约束
                    cursor.execute("""
                        ALTER TABLE test_tasks
                        ADD CONSTRAINT fk_task_test_plan
                        FOREIGN KEY (test_plan_id) REFERENCES test_plans(id) ON DELETE SET NULL
                    """)
                    print("成功添加test_plan_id外键约束")
                    
                except Exception as e:
                    print(f"添加test_plan_id相关操作失败: {e}")
            else:
                print("test_plan_id字段已存在，跳过")
            
            # 添加suite_id字段
            if not check_column_exists(cursor, 'test_tasks', 'suite_id'):
                try:
                    cursor.execute("""
                        ALTER TABLE test_tasks
                        ADD COLUMN suite_id INT NULL COMMENT '关联的测试套件ID'
                    """)
                    print("成功添加suite_id字段")
                    
                    # 添加索引
                    if not check_index_exists(cursor, 'test_tasks', 'idx_suite_id'):
                        cursor.execute("ALTER TABLE test_tasks ADD INDEX idx_suite_id (suite_id)")
                        print("成功添加suite_id索引")
                    
                    # 添加外键约束
                    cursor.execute("""
                        ALTER TABLE test_tasks
                        ADD CONSTRAINT fk_task_suite
                        FOREIGN KEY (suite_id) REFERENCES test_suites(id) ON DELETE SET NULL
                    """)
                    print("成功添加suite_id外键约束")
                    
                except Exception as e:
                    print(f"添加suite_id相关操作失败: {e}")
            else:
                print("suite_id字段已存在，跳过")
            
            # 添加documentation_url字段
            if not check_column_exists(cursor, 'test_tasks', 'documentation_url'):
                try:
                    cursor.execute("""
                        ALTER TABLE test_tasks
                        ADD COLUMN documentation_url TEXT COMMENT '相关文档链接'
                    """)
                    print("成功添加documentation_url字段")
                except Exception as e:
                    print(f"添加documentation_url字段失败: {e}")
            else:
                print("documentation_url字段已存在，跳过")
            
            # 添加version_info字段
            if not check_column_exists(cursor, 'test_tasks', 'version_info'):
                try:
                    cursor.execute("""
                        ALTER TABLE test_tasks
                        ADD COLUMN version_info VARCHAR(100) COMMENT '版本信息'
                    """)
                    print("成功添加version_info字段")
                except Exception as e:
                    print(f"添加version_info字段失败: {e}")
            else:
                print("version_info字段已存在，跳过")
            
            # 修改字段名：将description改为task_description
            if check_column_exists(cursor, 'test_tasks', 'description') and not check_column_exists(cursor, 'test_tasks', 'task_description'):
                try:
                    # 先添加新字段
                    cursor.execute("""
                        ALTER TABLE test_tasks
                        ADD COLUMN task_description TEXT COMMENT '任务描述'
                    """)
                    print("成功添加task_description字段")
                    
                    # 复制数据
                    cursor.execute("UPDATE test_tasks SET task_description = description")
                    print("成功复制description数据到task_description")
                    
                    # 删除旧字段
                    cursor.execute("ALTER TABLE test_tasks DROP COLUMN description")
                    print("成功删除旧的description字段")
                    
                except Exception as e:
                    print(f"修改description字段名失败: {e}")
            else:
                print("description字段已处理，跳过")
            
            connection.commit()
            print("\n测试任务表结构更新完成！")
            return True
            
    except Exception as e:
        print(f"更新数据表失败: {e}")
        return False
    finally:
        connection.close()

def main():
    """主函数"""
    print("开始更新测试任务表结构...")
    print("=" * 50)
    
    if update_test_tasks_table():
        print("=" * 50)
        print("数据表更新完成！")
        return 0
    else:
        print("=" * 50)
        print("数据表更新失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main())