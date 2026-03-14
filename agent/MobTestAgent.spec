# -*- mode: python ; coding: utf-8 -*-
# 打包时会将 agent/bin 下的 adb.exe、scrcpy.exe 一并封装，用户无需单独安装。
# 使用前请先运行 prepare_bin.bat 或 prepare_bin.py，再执行: pyinstaller MobTestAgent.spec

import os

block_cipher = None
# 请在 agent 目录下执行 pyinstaller MobTestAgent.spec，当前目录即 script_dir
script_dir = os.getcwd()
bin_dir = os.path.join(script_dir, 'bin')

datas = []
if os.path.isdir(bin_dir):
    for name in os.listdir(bin_dir):
        p = os.path.join(bin_dir, name)
        if os.path.isfile(p):
            datas.append((p, 'bin'))
            print('Bundling: %s' % name)
else:
    print('Warning: bin dir not found: %s' % bin_dir)

a = Analysis(
    ['main.py'],
    pathex=[script_dir],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MobTestAgent',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
