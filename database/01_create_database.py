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

# 导入配置
from database.config import DB_CONFIG, DB_NAME

def get_db_connection():
    """获取数据库连接（不指定数据库）"""
    try:
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            charset=DB_CONFIG['charset']
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
            cursor.execute(f"""
                CREATE DATABASE IF NOT EXISTS {DB_NAME} 
                DEFAULT CHARACTER SET utf8mb4 
                DEFAULT COLLATE utf8mb4_unicode_ci
            """)
            
            # 使用数据库
            cursor.execute(f"USE {DB_NAME}")
            
            connection.commit()
            print(f"数据库 {DB_NAME} 创建成功！")
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