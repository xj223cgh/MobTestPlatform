@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在从项目 escrcpy 复制 adb.exe、scrcpy.exe 到 agent\bin ...
python prepare_bin.py
if errorlevel 1 (
  echo 若未安装 Python，可手动将 adb.exe、scrcpy.exe 放入 agent\bin 目录。
  pause
  exit /b 1
)
echo 完成后可直接运行 Agent，或执行 build.bat 打包。
pause
