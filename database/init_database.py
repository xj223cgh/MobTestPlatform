#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库一键初始化脚本
按顺序执行：创建数据库 -> 创建表 -> 插入测试数据
"""

import subprocess
import sys
import os

def run_script(script_name):
    """运行Python脚本"""
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    try:
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, text=True, encoding='gbk')
        
        if result.returncode == 0:
            print(f"{script_name} 执行成功")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"{script_name} 执行失败")
            if result.stderr:
                print(f"错误信息: {result.stderr}")
            if result.stdout:
                print(result.stdout)
            return False
    except Exception as e:
        print(f"执行 {script_name} 时发生异常: {e}")
        return False

def main():
    """主函数"""
    print("开始数据库一键初始化...")
    print("=" * 50)
    
    # 1. 创建数据库
    print("步骤 1/3: 创建数据库")
    if not run_script("01_create_database.py"):
        print("数据库创建失败，初始化中止")
        return 1
    
    print("-" * 50)
    
    # 2. 创建表
    print("步骤 2/3: 创建数据表")
    if not run_script("03_create_tables.py"):
        print("数据表创建失败，初始化中止")
        return 1
    
    print("-" * 50)
    
    # 3. 插入测试数据
    print("步骤 3/3: 插入测试数据")
    if not run_script("05_insert_test_data.py"):
        print("测试数据插入失败，初始化中止")
        return 1
    
    print("=" * 50)
    print("数据库初始化完成！")
    print("测试账号信息：")
    print("   - Lethe (超级管理员): 123321")
    print("   - Manager (管理员): 12345678")
    print("   - Tester (测试人员): 12345678")
    print("   - Admin (实习生): 12345678")
    print("=" * 50)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())