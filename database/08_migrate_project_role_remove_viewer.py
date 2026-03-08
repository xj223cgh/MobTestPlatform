#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迁移脚本：从项目成员表 project_members 的 role 枚举中移除 viewer（访客）。
执行前请备份数据库。仅需在已存在 project_members 表且曾含 viewer 的库上执行一次。
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from database.config import DB_CONFIG

def main():
    try:
        import pymysql
    except ImportError:
        print("请先安装 pymysql: pip install pymysql")
        return 1
    conn = pymysql.connect(
        host=DB_CONFIG['host'],
        port=int(os.environ.get('MYSQL_PORT', 3306)),
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        charset=DB_CONFIG['charset'],
    )
    try:
        with conn.cursor() as cursor:
            # 若存在 role='viewer' 的记录，先改为 'tester'
            cursor.execute("UPDATE project_members SET role = 'tester' WHERE role = 'viewer'")
            updated = cursor.rowcount
            if updated:
                print(f"已将 {updated} 条 role=viewer 的记录改为 tester")
            # 修改 role 列枚举，去掉 viewer
            cursor.execute("""
                ALTER TABLE project_members
                MODIFY COLUMN role ENUM('owner','manager','tester') DEFAULT 'tester' COMMENT '项目角色'
            """)
            print("project_members.role 枚举已更新为 owner, manager, tester")
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"迁移失败: {e}")
        return 1
    finally:
        conn.close()
    return 0

if __name__ == '__main__':
    sys.exit(main())
