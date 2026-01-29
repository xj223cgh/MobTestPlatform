#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本 - 测试数据库连接
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

def test_connection():
    """测试数据库连接"""
    try:
        connection = get_db_connection()
        if not connection:
            return False
        
        with connection.cursor() as cursor:
            # 测试查询
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            
            if result and result[0] == 1:
                print("数据库连接成功！")
                
                # 检查表是否存在
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                
                if tables:
                    print(f"发现 {len(tables)} 个数据表：")
                    for table in tables:
                        print(f"   - {table[0]}")
                else:
                    print("数据库中暂无数据表")
                
                return True
            else:
                print("数据库连接测试失败")
                return False
                
    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}")
        return False
    finally:
        if 'connection' in locals() and connection:
            connection.close()

def main():
    """主函数"""
    print("开始测试数据库连接...")
    
    if test_connection():
        print("数据库连接测试成功！")
        return 0
    else:
        print("数据库连接测试失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main())