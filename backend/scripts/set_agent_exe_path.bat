@echo off
chcp 65001 >nul
cd /d "%~dp0"
cd /d "%~dp0..\.."
if "%~1"=="" (
  echo 用法：set_agent_exe_path.bat set "exe的绝对路径"  或  set_agent_exe_path.bat clear
  echo 示例：set_agent_exe_path.bat set "D:\deploy\MobTestAgent.exe"
  exit /b 0
)
python backend\scripts\set_agent_exe_path.py %*
pause
