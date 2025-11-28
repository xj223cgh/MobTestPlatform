#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库更新脚本 - 为test_cases表添加缺失的字段
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

def update_test_cases_table():
    """更新test_cases表结构，添加缺失的字段"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            # 添加project_id字段
            if not check_column_exists(cursor, 'test_cases', 'project_id'):
                try:
                    cursor.execute("""
                        ALTER TABLE test_cases
                        ADD COLUMN project_id INT NULL COMMENT '所属项目ID'
                    """)
                    print("成功添加project_id字段")
                    
                    # 添加索引
                    if not check_index_exists(cursor, 'test_cases', 'idx_case_project_id'):
                        cursor.execute("ALTER TABLE test_cases ADD INDEX idx_case_project_id (project_id)")
                        print("成功添加project_id索引")
                    
                    # 添加外键约束
                    cursor.execute("""
                        ALTER TABLE test_cases
                        ADD CONSTRAINT fk_case_project
                        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
                    """)
                    print("成功添加project_id外键约束")
                    
                except Exception as e:
                    print(f"添加project_id相关操作失败: {e}")
            else:
                print("project_id字段已存在，跳过")
            
            # 添加iteration_id字段
            if not check_column_exists(cursor, 'test_cases', 'iteration_id'):
                try:
                    cursor.execute("""
                        ALTER TABLE test_cases
                        ADD COLUMN iteration_id INT NULL COMMENT '所属迭代ID'
                    """)
                    print("成功添加iteration_id字段")
                    
                    # 添加索引
                    if not check_index_exists(cursor, 'test_cases', 'idx_case_iteration_id'):
                        cursor.execute("ALTER TABLE test_cases ADD INDEX idx_case_iteration_id (iteration_id)")
                        print("成功添加iteration_id索引")
                    
                    # 添加外键约束
                    cursor.execute("""
                        ALTER TABLE test_cases
                        ADD CONSTRAINT fk_case_iteration
                        FOREIGN KEY (iteration_id) REFERENCES iterations(id) ON DELETE SET NULL
                    """)
                    print("成功添加iteration_id外键约束")
                    
                except Exception as e:
                    print(f"添加iteration_id相关操作失败: {e}")
            else:
                print("iteration_id字段已存在，跳过")
            
            # 添加test_plan_id字段
            if not check_column_exists(cursor, 'test_cases', 'test_plan_id'):
                try:
                    cursor.execute("""
                        ALTER TABLE test_cases
                        ADD COLUMN test_plan_id INT NULL COMMENT '所属测试计划ID'
                    """)
                    print("成功添加test_plan_id字段")
                    
                    # 添加索引
                    if not check_index_exists(cursor, 'test_cases', 'idx_case_test_plan_id'):
                        cursor.execute("ALTER TABLE test_cases ADD INDEX idx_case_test_plan_id (test_plan_id)")
                        print("成功添加test_plan_id索引")
                    
                    # 添加外键约束
                    cursor.execute("""
                        ALTER TABLE test_cases
                        ADD CONSTRAINT fk_case_test_plan
                        FOREIGN KEY (test_plan_id) REFERENCES test_plans(id) ON DELETE SET NULL
                    """)
                    print("成功添加test_plan_id外键约束")
                    
                except Exception as e:
                    print(f"添加test_plan_id相关操作失败: {e}")
            else:
                print("test_plan_id字段已存在，跳过")
            
            # 添加suite_id字段
            if not check_column_exists(cursor, 'test_cases', 'suite_id'):
                try:
                    cursor.execute("""
                        ALTER TABLE test_cases
                        ADD COLUMN suite_id INT NULL COMMENT '所属测试套件ID'
                    """)
                    print("成功添加suite_id字段")
                    
                    # 添加索引
                    if not check_index_exists(cursor, 'test_cases', 'idx_case_suite_id'):
                        cursor.execute("ALTER TABLE test_cases ADD INDEX idx_case_suite_id (suite_id)")
                        print("成功添加suite_id索引")
                    
                    # 添加外键约束
                    cursor.execute("""
                        ALTER TABLE test_cases
                        ADD CONSTRAINT fk_case_suite
                        FOREIGN KEY (suite_id) REFERENCES test_suites(id) ON DELETE SET NULL
                    """)
                    print("成功添加suite_id外键约束")
                    
                except Exception as e:
                    print(f"添加suite_id相关操作失败: {e}")
            else:
                print("suite_id字段已存在，跳过")
            
            # 添加precondition字段
            if not check_column_exists(cursor, 'test_cases', 'precondition'):
                try:
                    cursor.execute("""
                        ALTER TABLE test_cases
                        ADD COLUMN precondition TEXT COMMENT '前置条件'
                    """)
                    print("成功添加precondition字段")
                except Exception as e:
                    print(f"添加precondition字段失败: {e}")
            else:
                print("precondition字段已存在，跳过")
            
            # 添加test_data字段
            if not check_column_exists(cursor, 'test_cases', 'test_data'):
                try:
                    cursor.execute("""
                        ALTER TABLE test_cases
                        ADD COLUMN test_data TEXT COMMENT '测试数据'
                    """)
                    print("成功添加test_data字段")
                except Exception as e:
                    print(f"添加test_data字段失败: {e}")
            else:
                print("test_data字段已存在，跳过")
            
            # 添加expected_result字段
            if not check_column_exists(cursor, 'test_cases', 'expected_result'):
                try:
                    cursor.execute("""
                        ALTER TABLE test_cases
                        ADD COLUMN expected_result TEXT COMMENT '预期结果'
                    """)
                    print("成功添加expected_result字段")
                except Exception as e:
                    print(f"添加expected_result字段失败: {e}")
            else:
                print("expected_result字段已存在，跳过")
            
            # 添加actual_result字段
            if not check_column_exists(cursor, 'test_cases', 'actual_result'):
                try:
                    cursor.execute("""
                        ALTER TABLE test_cases
                        ADD COLUMN actual_result TEXT COMMENT '实际结果'
                    """)
                    print("成功添加actual_result字段")
                except Exception as e:
                    print(f"添加actual_result字段失败: {e}")
            else:
                print("actual_result字段已存在，跳过")
            
            # 添加status字段
            if not check_column_exists(cursor, 'test_cases', 'status'):
                try:
                    cursor.execute("""
                        ALTER TABLE test_cases
                        ADD COLUMN status VARCHAR(20) DEFAULT 'draft' COMMENT '用例状态'
                    """)
                    print("成功添加status字段")
                except Exception as e:
                    print(f"添加status字段失败: {e}")
            else:
                print("status字段已存在，跳过")
            
            # 添加priority字段
            if not check_column_exists(cursor, 'test_cases', 'priority'):
                try:
                    cursor.execute("""
                        ALTER TABLE test_cases
                        ADD COLUMN priority VARCHAR(20) DEFAULT 'medium' COMMENT '优先级'
                    """)
                    print("成功添加priority字段")
                except Exception as e:
                    print(f"添加priority字段失败: {e}")
            else:
                print("priority字段已存在，跳过")
            
            # 添加author字段
            if not check_column_exists(cursor, 'test_cases', 'author'):
                try:
                    cursor.execute("""
                        ALTER TABLE test_cases
                        ADD COLUMN author VARCHAR(50) COMMENT '编写人'
                    """)
                    print("成功添加author字段")
                except Exception as e:
                    print(f"添加author字段失败: {e}")
            else:
                print("author字段已存在，跳过")
            
            # 添加assignee字段
            if not check_column_exists(cursor, 'test_cases', 'assignee'):
                try:
                    cursor.execute("""
                        ALTER TABLE test_cases
                        ADD COLUMN assignee VARCHAR(50) COMMENT '执行人'
                    """)
                    print("成功添加assignee字段")
                except Exception as e:
                    print(f"添加assignee字段失败: {e}")
            else:
                print("assignee字段已存在，跳过")
            
            # 添加version_info字段
            if not check_column_exists(cursor, 'test_cases', 'version_info'):
                try:
                    cursor.execute("""
                        ALTER TABLE test_cases
                        ADD COLUMN version_info VARCHAR(100) COMMENT '版本信息'
                    """)
                    print("成功添加version_info字段")
                except Exception as e:
                    print(f"添加version_info字段失败: {e}")
            else:
                print("version_info字段已存在，跳过")
            
            # 添加xmind_data字段
            if not check_column_exists(cursor, 'test_cases', 'xmind_data'):
                try:
                    cursor.execute("""
                        ALTER TABLE test_cases
                        ADD COLUMN xmind_data LONGTEXT COMMENT 'XMind数据'
                    """)
                    print("成功添加xmind_data字段")
                except Exception as e:
                    print(f"添加xmind_data字段失败: {e}")
            else:
                print("xmind_data字段已存在，跳过")
            
            # 添加preconditions字段
            if not check_column_exists(cursor, 'test_cases', 'preconditions'):
                try:
                    cursor.execute("""
                        ALTER TABLE test_cases
                        ADD COLUMN preconditions TEXT COMMENT '前置条件'
                    """)
                    print("成功添加preconditions字段")
                except Exception as e:
                    print(f"添加preconditions字段失败: {e}")
            else:
                print("preconditions字段已存在，跳过")
            
            # 添加steps字段
            if not check_column_exists(cursor, 'test_cases', 'steps'):
                try:
                    cursor.execute("""
                        ALTER TABLE test_cases
                        ADD COLUMN steps TEXT COMMENT '测试步骤'
                    """)
                    print("成功添加steps字段")
                except Exception as e:
                    print(f"添加steps字段失败: {e}")
            else:
                print("steps字段已存在，跳过")
            
            # 添加created_at和updated_at字段
            if not check_column_exists(cursor, 'test_cases', 'created_at'):
                try:
                    cursor.execute("""
                        ALTER TABLE test_cases
                        ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
                    """)
                    print("成功添加created_at字段")
                except Exception as e:
                    print(f"添加created_at字段失败: {e}")
            else:
                print("created_at字段已存在，跳过")
            
            if not check_column_exists(cursor, 'test_cases', 'updated_at'):
                try:
                    cursor.execute("""
                        ALTER TABLE test_cases
                        ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
                    """)
                    print("成功添加updated_at字段")
                except Exception as e:
                    print(f"添加updated_at字段失败: {e}")
            else:
                print("updated_at字段已存在，跳过")
            
            connection.commit()
            print("\n测试用例表结构更新完成！")
            return True
            
    except Exception as e:
        print(f"更新数据表失败: {e}")
        return False
    finally:
        connection.close()

def main():
    """主函数"""
    print("开始更新测试用例表结构...")
    print("=" * 50)
    
    if update_test_cases_table():
        print("=" * 50)
        print("数据表更新完成！")
        return 0
    else:
        print("=" * 50)
        print("数据表更新失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main())