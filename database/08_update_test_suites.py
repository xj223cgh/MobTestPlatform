#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库更新脚本 - 为test_suites表添加type和sort_order字段
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

def update_test_suites_table():
    """更新test_suites表，添加type和sort_order字段"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            # 检查type字段是否存在
            cursor.execute("""SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                           WHERE TABLE_SCHEMA = 'mobile_test_platform' AND TABLE_NAME = 'test_suites' AND COLUMN_NAME = 'type'""")
            type_exists = cursor.fetchone() is not None
            
            # 检查sort_order字段是否存在
            cursor.execute("""SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                           WHERE TABLE_SCHEMA = 'mobile_test_platform' AND TABLE_NAME = 'test_suites' AND COLUMN_NAME = 'sort_order'""")
            sort_order_exists = cursor.fetchone() is not None
            
            # 添加type字段
            if not type_exists:
                cursor.execute("""ALTER TABLE test_suites 
                               ADD COLUMN type ENUM('folder', 'suite') DEFAULT 'folder' COMMENT '类型：folder-用例文件夹, suite-用例集'""")
                print("添加type字段成功！")
            else:
                print("type字段已存在，跳过添加！")
            
            # 添加sort_order字段
            if not sort_order_exists:
                cursor.execute("""ALTER TABLE test_suites 
                               ADD COLUMN sort_order INT DEFAULT 0 COMMENT '排序顺序'""")
                print("添加sort_order字段成功！")
            else:
                print("sort_order字段已存在，跳过添加！")
            
            # 检查idx_type索引是否存在
            cursor.execute("""SELECT INDEX_NAME FROM INFORMATION_SCHEMA.STATISTICS 
                           WHERE TABLE_SCHEMA = 'mobile_test_platform' AND TABLE_NAME = 'test_suites' AND INDEX_NAME = 'idx_type'""")
            idx_type_exists = cursor.fetchone() is not None
            
            # 检查idx_sort_order索引是否存在
            cursor.execute("""SELECT INDEX_NAME FROM INFORMATION_SCHEMA.STATISTICS 
                           WHERE TABLE_SCHEMA = 'mobile_test_platform' AND TABLE_NAME = 'test_suites' AND INDEX_NAME = 'idx_sort_order'""")
            idx_sort_order_exists = cursor.fetchone() is not None
            
            # 创建idx_type索引
            if not idx_type_exists:
                cursor.execute("""CREATE INDEX idx_type ON test_suites(type)""")
                print("创建idx_type索引成功！")
            else:
                print("idx_type索引已存在，跳过创建！")
            
            # 创建idx_sort_order索引
            if not idx_sort_order_exists:
                cursor.execute("""CREATE INDEX idx_sort_order ON test_suites(sort_order)""")
                print("创建idx_sort_order索引成功！")
            else:
                print("idx_sort_order索引已存在，跳过创建！")
            
            connection.commit()
            print("test_suites表更新成功！")
            return True
            
    except Exception as e:
        print(f"更新test_suites表失败: {e}")
        return False
    finally:
        connection.close()

def main():
    """主函数"""
    print("开始更新test_suites表...")
    
    if update_test_suites_table():
        print("test_suites表更新完成！")
        return 0
    else:
        print("test_suites表更新失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main())
