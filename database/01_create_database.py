#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本 - 创建数据库
"""

import pymysql
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_db_connection():
    """获取数据库连接（不指定数据库）"""
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            charset='utf8mb4'
        )
        return connection
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None

def create_database():
    """创建数据库"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            # 创建数据库
            cursor.execute("""
                CREATE DATABASE IF NOT EXISTS mobile_test_platform 
                DEFAULT CHARACTER SET utf8mb4 
                DEFAULT COLLATE utf8mb4_unicode_ci
            """)
            
            # 使用数据库
            cursor.execute("USE mobile_test_platform")
            
            connection.commit()
            print("数据库 mobile_test_platform 创建成功！")
            return True
            
    except Exception as e:
        print(f"创建数据库失败: {e}")
        return False
    finally:
        connection.close()

def main():
    """主函数"""
    print("开始创建数据库...")
    
    if create_database():
        print("数据库创建完成！")
        return 0
    else:
        print("数据库创建失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main())