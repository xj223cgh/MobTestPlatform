#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
移动端测试平台启动脚本
使用multiprocessing管理前后端服务进程
"""

import os
import sys
import subprocess
import platform
from multiprocessing import Process
import time
from pathlib import Path


def run_backend():
    """运行后端服务"""
    try:
        print("🔧 启动后端服务...")
        backend_dir = Path(__file__).parent / "backend"
        os.chdir(backend_dir)
        
        cmd = [sys.executable, 'run.py']
        
        process = subprocess.Popen(
            cmd,
            stdout=sys.stdout,
            stderr=sys.stderr,
            shell=False
        )
        
        print(f"✅ 后端服务已启动 (PID: {process.pid})")
        process.wait()
    except Exception as e:
        print(f"❌ 启动后端服务时出错: {e}")
        sys.exit(1)


def run_frontend():
    """运行前端服务"""
    try:
        print("📱 启动前端服务...")
        frontend_dir = Path(__file__).parent / "frontend"
        os.chdir(frontend_dir)

        cmd = ['npm', 'run', 'dev']
        # Windows环境下使用shell=True来确保npm命令能正确执行
        shell_mode = platform.system() == 'Windows'

        process = subprocess.Popen(
            cmd,
            stdout=sys.stdout,
            stderr=sys.stderr,
            shell=shell_mode
        )
        
        print(f"✅ 前端服务已启动 (PID: {process.pid})")
        process.wait()
    except Exception as e:
        print(f"❌ 启动前端服务时出错: {e}")
        sys.exit(1)


def main():
    """主函数，同时启动后端和前端服务"""
    # 保存当前工作目录
    original_dir = os.getcwd()
    
    print("🚀 正在启动移动端测试平台服务...")
    print(f"📁 当前工作目录: {original_dir}")
    print("=" * 50)
    
    # 检查目录是否存在
    project_root = Path(__file__).parent
    frontend_dir = project_root / "frontend"
    backend_dir = project_root / "backend"
    
    if not frontend_dir.exists():
        print("❌ 前端目录不存在")
        return
    
    if not backend_dir.exists():
        print("❌ 后端目录不存在")
        return
    
    try:
        # 创建并启动后端进程
        backend_process = Process(target=run_backend)
        backend_process.daemon = True
        backend_process.start()

        time.sleep(3)  # 等待后端服务启动
        
        # 创建并启动前端进程
        frontend_process = Process(target=run_frontend)
        frontend_process.daemon = True
        frontend_process.start()
        
        # 等待前端启动
        time.sleep(3)
        
        # 服务已全部启动
        print("\n✅ 服务已全部启动！")
        print("=" * 50)

        # 无限循环以保持主进程运行，直到通过编辑器按钮停止
        while True:
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n🛑 收到停止信号，正在停止服务...")
    except Exception as e:
        print(f"❌ 运行服务时发生错误: {e}")
    finally:
        # 确保所有进程都被终止
        try:
            if 'backend_process' in locals() and backend_process.is_alive():
                backend_process.terminate()
                backend_process.join(timeout=3)
            
            if 'frontend_process' in locals() and frontend_process.is_alive():
                frontend_process.terminate()
                frontend_process.join(timeout=3)
        except Exception as e:
            print(f"⚠️ 停止服务时发生错误: {e}")
        
        print("✅ 所有服务已停止")


if __name__ == "__main__":
    main()
