#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新迭代表结构，添加缺失的字段
"""

import sys
import os
import pymysql
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', '.env'))


def update_iterations_table():
    """更新迭代表结构"""
    try:
        # 连接数据库
        conn = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'mobtestplatform'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        cursor = conn.cursor()
        
        print("正在更新迭代表结构...")
        
        # 添加goal字段
        try:
            cursor.execute('ALTER TABLE iterations ADD COLUMN goal TEXT COMMENT \'迭代目标\'')
            print("✓ 添加goal字段成功")
        except pymysql.err.OperationalError as e:
            if e.args[0] == 1060:  # 字段已存在
                print("✓ goal字段已存在")
            else:
                raise
        
        # 添加created_by字段
        try:
            cursor.execute('ALTER TABLE iterations ADD COLUMN created_by INT COMMENT \'创建者ID\'')
            cursor.execute('ALTER TABLE iterations ADD CONSTRAINT fk_iterations_created_by FOREIGN KEY (created_by) REFERENCES users(id)')
            print("✓ 添加created_by字段成功")
        except pymysql.err.OperationalError as e:
            if e.args[0] == 1060:  # 字段已存在
                print("✓ created_by字段已存在")
            else:
                raise
        
        # 添加updated_by字段
        try:
            cursor.execute('ALTER TABLE iterations ADD COLUMN updated_by INT COMMENT \'更新者ID\'')
            cursor.execute('ALTER TABLE iterations ADD CONSTRAINT fk_iterations_updated_by FOREIGN KEY (updated_by) REFERENCES users(id)')
            print("✓ 添加updated_by字段成功")
        except pymysql.err.OperationalError as e:
            if e.args[0] == 1060:  # 字段已存在
                print("✓ updated_by字段已存在")
            else:
                raise
        
        # 提交事务
        conn.commit()
        
        print("\n🎉 迭代表结构更新完成！")
        
    except Exception as e:
        print(f"\n❌ 更新迭代表结构失败: {str(e)}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    
    return True


if __name__ == '__main__':
    update_iterations_table()
