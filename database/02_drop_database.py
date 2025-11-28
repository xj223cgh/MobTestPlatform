#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本 - 删除数据库
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

def drop_database():
    """删除数据库"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            # 删除数据库
            cursor.execute("DROP DATABASE IF EXISTS mobile_test_platform")
            
            connection.commit()
            print("✅ 数据库 mobile_test_platform 删除成功！")
            return True
            
    except Exception as e:
        print(f"❌ 删除数据库失败: {e}")
        return False
    finally:
        connection.close()

def main():
    """主函数"""
    print("⚠️  开始删除数据库...")
    print("⚠️  这将删除所有数据，请确认操作！")
    
    confirm = input("确认删除数据库？(y/N): ").lower().strip()
    if confirm != 'y':
        print("❌ 操作已取消")
        return 0
    
    if drop_database():
        print("🎉 数据库删除完成！")
        return 0
    else:
        print("💥 数据库删除失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main())