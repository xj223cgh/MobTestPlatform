#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设备信息获取脚本
用于通过ADB获取设备的详细信息
支持：
1. 命令行参数：--device-id, --adb-path
2. 环境变量：DEVICE_ID, ADB_PATH
3. 默认值：ADB_PATH默认为系统PATH中的'adb'
"""

import subprocess
import os
import sys
import argparse
import shutil
from pathlib import Path


def get_device_info(device_id, adb_path):
    """
    获取设备详细信息
    """
    print("=" * 60)
    print("设备信息获取")
    print("=" * 60)
    print(f"设备ID: {device_id}")
    print(f"ADB路径: {adb_path}")
    print()

    commands = {
        "设备型号": f"-s {device_id} shell getprop ro.product.model",
        "设备制造商": f"-s {device_id} shell getprop ro.product.manufacturer",
        "Android版本": f"-s {device_id} shell getprop ro.build.version.release",
        "SDK版本": f"-s {device_id} shell getprop ro.build.version.sdk",
        "CPU架构": f"-s {device_id} shell getprop ro.product.cpu.abi",
        "屏幕分辨率": f"-s {device_id} shell wm size",
        "屏幕密度": f"-s {device_id} shell wm density",
        "设备序列号": f"-s {device_id} shell getprop ro.serialno",
        "总内存": f"-s {device_id} shell cat /proc/meminfo | grep MemTotal",
        "可用内存": f"-s {device_id} shell cat /proc/meminfo | grep MemAvailable",
        "存储信息": f"-s {device_id} shell df -h /data",
        "电池状态": f"-s {device_id} shell dumpsys battery | grep level"
    }

    device_info = {}

    for info_name, command in commands.items():
        try:
            # 使用字节流捕获输出，避免编码问题
            result = subprocess.run(
                [adb_path] + command.split(),
                capture_output=True,
                check=False
            )

            # 尝试多种编码方式解码输出
            stdout = result.stdout
            
            # 尝试解码
            decoded_stdout = None
            for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                try:
                    decoded_stdout = stdout.decode(encoding)
                    break
                except (UnicodeDecodeError, LookupError):
                    continue
            
            if decoded_stdout is None:
                # 如果所有编码都失败，使用 replace 模式
                decoded_stdout = stdout.decode('utf-8', errors='replace')

            stdout = decoded_stdout.strip()

            if info_name == "屏幕分辨率":
                device_info[info_name] = stdout.split(':')[-1].strip() if ':' in stdout else stdout
            elif info_name == "屏幕密度":
                device_info[info_name] = stdout.split(':')[-1].strip() if ':' in stdout else stdout
            elif info_name == "总内存":
                device_info[info_name] = stdout.split(':')[-1].strip() if ':' in stdout else stdout
            elif info_name == "可用内存":
                device_info[info_name] = stdout.split(':')[-1].strip() if ':' in stdout else stdout
            elif info_name == "电池状态":
                device_info[info_name] = stdout.split(':')[-1].strip() if ':' in stdout else stdout
            else:
                device_info[info_name] = stdout

        except Exception as e:
            print(f"获取 {info_name} 时发生错误: {str(e)}")

    print("\n设备信息:")
    print("-" * 60)
    for key, value in device_info.items():
        if value and len(value) < 100:
            print(f"  {key}: {value}")
        elif value:
            print(f"  {key}: {len(value)} 字符")

    print("\n" + "=" * 60)
    print("获取完成")
    print("=" * 60)

    return len(device_info) > 0


def main():
    """
    主函数
    """
    # 创建参数解析器
    parser = argparse.ArgumentParser(description='设备信息获取脚本')
    
    # 添加命令行参数
    parser.add_argument('--device-id', '-d', type=str, help='设备ID')
    parser.add_argument('--adb-path', '-a', type=str, help='ADB路径，默认为系统PATH中的adb')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 优先级顺序：命令行参数 > 环境变量 > 默认值
    # 获取设备ID
    device_id = args.device_id or os.environ.get('DEVICE_ID')
    
    # 获取ADB路径
    adb_path = args.adb_path or os.environ.get('ADB_PATH')
    
    # 如果ADB路径未指定，尝试从系统PATH中查找
    if not adb_path:
        adb_path = shutil.which('adb') or 'adb'
    
    # 检查设备ID
    if not device_id:
        print("错误: 未提供设备ID")
        print("请通过以下方式之一提供设备ID:")
        print("1. 命令行参数: --device-id <device_id> 或 -d <device_id>")
        print("2. 环境变量: DEVICE_ID=<device_id>")
        parser.print_help()
        return 1
    
    # 检查ADB路径
    if not os.path.exists(adb_path) and not shutil.which(adb_path):
        print(f"错误: ADB路径不存在或不在系统PATH中: {adb_path}")
        print("请通过以下方式之一提供正确的ADB路径:")
        print("1. 命令行参数: --adb-path <adb_path> 或 -a <adb_path>")
        print("2. 环境变量: ADB_PATH=<adb_path>")
        parser.print_help()
        return 1
    
    # 获取设备信息
    success = get_device_info(device_id, adb_path)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
