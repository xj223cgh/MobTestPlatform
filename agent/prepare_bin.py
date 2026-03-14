# -*- coding: utf-8 -*-
"""从项目 escrcpy 目录复制 adb、scrcpy 及依赖到 agent/bin，便于封装或直接运行。"""
import os
import shutil

# 本脚本所在目录即 agent/
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BIN_DIR = os.path.join(SCRIPT_DIR, 'bin')

# 项目根：向上查找包含 escrcpy/electron/resources/extra/win/scrcpy 的目录
def _find_scrcpy_src():
    candidate = os.path.dirname(SCRIPT_DIR)  # agent 的上级
    for _ in range(5):
        path = os.path.join(candidate, 'escrcpy', 'electron', 'resources', 'extra', 'win', 'scrcpy')
        if os.path.isdir(path):
            return path
        candidate = os.path.dirname(candidate)
        if not candidate or candidate == os.path.dirname(candidate):
            break
    return None

SCRCPY_SRC = _find_scrcpy_src()


def main():
    if not SCRCPY_SRC or not os.path.isdir(SCRCPY_SRC):
        print('未找到 escrcpy/electron/resources/extra/win/scrcpy/')
        print('请确认项目内存在该目录，或设置环境变量 AGENT_SCRCPY_SRC 指向该路径。')
        return 1
    # 支持环境变量覆盖
    src_dir = os.environ.get('AGENT_SCRCPY_SRC') or SCRCPY_SRC
    if not os.path.isdir(src_dir):
        src_dir = SCRCPY_SRC
    os.makedirs(BIN_DIR, exist_ok=True)
    # 复制 adb.exe、scrcpy.exe 及 scrcpy 运行所需的 DLL、scrcpy-server
    required = [
        'adb.exe', 'scrcpy.exe', 'scrcpy-server',
        'AdbWinApi.dll', 'AdbWinUsbApi.dll',
        'avcodec-61.dll', 'avformat-61.dll', 'avutil-59.dll',
        'libusb-1.0.dll', 'SDL2.dll', 'swresample-5.dll',
    ]
    for name in required:
        src = os.path.join(src_dir, name)
        dst = os.path.join(BIN_DIR, name)
        if not os.path.isfile(src):
            print(f'跳过（不存在）: {name}')
            continue
        shutil.copy2(src, dst)
        print(f'已复制: {name}')
    print('完成。agent/bin 已就绪。')
    return 0


if __name__ == '__main__':
    exit(main())
