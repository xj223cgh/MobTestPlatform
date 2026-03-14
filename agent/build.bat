@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在安装依赖...
pip install -r requirements.txt
echo 正在准备封装 adb、scrcpy...
python prepare_bin.py
if not exist "bin\adb.exe" (
  echo 未找到 bin\adb.exe，请先运行 prepare_bin.bat 从项目 escrcpy 复制，或手动放入 bin 目录。
  pause
  exit /b 1
)
echo 正在使用 PyInstaller 打包（含 adb、scrcpy）...
pyinstaller MobTestAgent.spec
if exist "clean_agent.bat" copy /Y "clean_agent.bat" "dist\clean_agent.bat" >nul && echo 已复制 clean_agent.bat 到 dist，可与 exe 一并分发。
echo 打包完成，可执行文件在 dist\MobTestAgent.exe，已内含 adb 与 scrcpy；dist\clean_agent.bat 供用户一键清理使用。
pause
