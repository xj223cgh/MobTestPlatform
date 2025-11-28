#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库更新脚本 - 更新test_cases表，添加version_requirement_id字段
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

def update_test_cases_table():
    """更新test_cases表，添加version_requirement_id字段"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            # 1. 检查test_cases表是否存在version_requirement_id字段
            cursor.execute("SHOW COLUMNS FROM test_cases LIKE 'version_requirement_id'")
            result = cursor.fetchone()
            
            if not result:
                # 2. 添加version_requirement_id字段
                print("开始添加version_requirement_id字段到test_cases表...")
                cursor.execute("""
                    ALTER TABLE test_cases 
                    ADD COLUMN version_requirement_id INT UNIQUE COMMENT '关联的版本需求ID' AFTER project_id,
                    ADD CONSTRAINT fk_test_cases_version_requirement 
                    FOREIGN KEY (version_requirement_id) 
                    REFERENCES version_requirements(id) 
                    ON DELETE SET NULL
                """)
                print("version_requirement_id字段添加成功！")
            else:
                print("version_requirement_id字段已存在，跳过添加操作！")
            
            # 3. 检查其他缺失的字段
            print("检查并添加其他缺失的字段...")
            
            # 检查并添加suite_id字段
            cursor.execute("SHOW COLUMNS FROM test_cases LIKE 'suite_id'")
            result = cursor.fetchone()
            if not result:
                cursor.execute("""
                    ALTER TABLE test_cases 
                    ADD COLUMN suite_id INT COMMENT '所属套件ID' AFTER creator_id,
                    ADD CONSTRAINT fk_test_cases_suite 
                    FOREIGN KEY (suite_id) 
                    REFERENCES test_suites(id) 
                    ON DELETE SET NULL
                """)
                print("suite_id字段添加成功！")
            else:
                print("suite_id字段已存在，跳过添加操作！")
            
            # 检查并添加project_id字段
            cursor.execute("SHOW COLUMNS FROM test_cases LIKE 'project_id'")
            result = cursor.fetchone()
            if not result:
                cursor.execute("""
                    ALTER TABLE test_cases 
                    ADD COLUMN project_id INT COMMENT '所属项目ID' AFTER suite_id,
                    ADD CONSTRAINT fk_test_cases_project 
                    FOREIGN KEY (project_id) 
                    REFERENCES projects(id) 
                    ON DELETE CASCADE
                """)
                print("project_id字段添加成功！")
            else:
                print("project_id字段已存在，跳过添加操作！")
            
            # 检查并添加xmind_data字段
            cursor.execute("SHOW COLUMNS FROM test_cases LIKE 'xmind_data'")
            result = cursor.fetchone()
            if not result:
                cursor.execute("""
                    ALTER TABLE test_cases 
                    ADD COLUMN xmind_data TEXT COMMENT 'xmind格式的用例数据（JSON字符串）' AFTER project_id
                """)
                print("xmind_data字段添加成功！")
            else:
                print("xmind_data字段已存在，跳过添加操作！")
            
            # 检查并添加preconditions字段
            cursor.execute("SHOW COLUMNS FROM test_cases LIKE 'preconditions'")
            result = cursor.fetchone()
            if not result:
                cursor.execute("""
                    ALTER TABLE test_cases 
                    ADD COLUMN preconditions TEXT COMMENT '前置条件' AFTER xmind_data
                """)
                print("preconditions字段添加成功！")
            else:
                print("preconditions字段已存在，跳过添加操作！")
            
            # 检查并添加steps字段
            cursor.execute("SHOW COLUMNS FROM test_cases LIKE 'steps'")
            result = cursor.fetchone()
            if not result:
                cursor.execute("""
                    ALTER TABLE test_cases 
                    ADD COLUMN steps TEXT COMMENT '测试步骤' AFTER preconditions
                """)
                print("steps字段添加成功！")
            else:
                print("steps字段已存在，跳过添加操作！")
            
            # 检查并添加expected_result字段
            cursor.execute("SHOW COLUMNS FROM test_cases LIKE 'expected_result'")
            result = cursor.fetchone()
            if not result:
                cursor.execute("""
                    ALTER TABLE test_cases 
                    ADD COLUMN expected_result TEXT COMMENT '预期结果' AFTER steps
                """)
                print("expected_result字段添加成功！")
            else:
                print("expected_result字段已存在，跳过添加操作！")
            
            # 检查并添加actual_result字段
            cursor.execute("SHOW COLUMNS FROM test_cases LIKE 'actual_result'")
            result = cursor.fetchone()
            if not result:
                cursor.execute("""
                    ALTER TABLE test_cases 
                    ADD COLUMN actual_result TEXT COMMENT '实际结果' AFTER expected_result
                """)
                print("actual_result字段添加成功！")
            else:
                print("actual_result字段已存在，跳过添加操作！")
        
        connection.commit()
        print("test_cases表更新完成！")
        return True
        
    except Exception as e:
        print(f"更新test_cases表失败: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()

def main():
    """主函数"""
    print("开始更新test_cases表...")
    
    if update_test_cases_table():
        print("test_cases表更新成功！")
        return 0
    else:
        print("test_cases表更新失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main())
