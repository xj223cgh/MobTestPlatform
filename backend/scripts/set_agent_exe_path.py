# -*- coding: utf-8 -*-
"""
Agent 安装包下载路径的快捷配置/清理脚本。
在部署项目的服务器上运行，用于开启或关闭平台「下载 Agent」入口。

用法（在项目根目录或 backend 目录下执行）：
  配置：python backend/scripts/set_agent_exe_path.py set "D:\\path\\to\\MobTestAgent.exe"
  清理：python backend/scripts/set_agent_exe_path.py clear

也可先 cd backend/scripts 再：python set_agent_exe_path.py set "路径"
"""
import os
import sys
from pathlib import Path

# 定位 backend 目录（脚本在 backend/scripts/ 下）
_script_dir = Path(__file__).resolve().parent
_backend_dir = _script_dir.parent
_agent_exe_path_file = _backend_dir / 'agent_exe_path.txt'


def cmd_set(path: str) -> None:
    path = (path or '').strip()
    if not path:
        print('请提供 exe 绝对路径，例如：')
        print('  python set_agent_exe_path.py set "D:\\deploy\\MobTestAgent.exe"')
        sys.exit(1)
    path = os.path.abspath(os.path.expanduser(path))
    if not os.path.isfile(path):
        print(f'路径不存在或不是文件：{path}')
        sys.exit(1)
    try:
        _agent_exe_path_file.write_text(path, encoding='utf-8')
        print(f'已配置 Agent 下载路径：{path}')
        print('重启后端后，平台使用引导将显示「下载 Agent」按钮。')
    except Exception as e:
        print(f'写入失败：{e}')
        sys.exit(1)


def cmd_clear() -> None:
    if not _agent_exe_path_file.exists():
        print('当前未使用配置文件中的路径（可能由环境变量 AGENT_EXE_PATH 指定），无需清理。')
        return
    try:
        _agent_exe_path_file.unlink()
        print('已清理 Agent 下载路径配置。')
        print('重启后端后，平台将不再提供「下载 Agent」入口（显示请联系管理员获取）。')
    except Exception as e:
        print(f'删除失败：{e}')
        sys.exit(1)


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__.strip())
        print()
        print('  set <路径>  配置 exe 路径（写入 backend/agent_exe_path.txt）')
        print('  clear       清除配置文件中的路径')
        sys.exit(0)
    sub = (sys.argv[1] or '').strip().lower()
    if sub == 'set':
        cmd_set(sys.argv[2] if len(sys.argv) > 2 else '')
    elif sub == 'clear':
        cmd_clear()
    else:
        print('未知命令，请使用 set <路径> 或 clear')
        sys.exit(1)


if __name__ == '__main__':
    main()
