@echo off
chcp 65001 >nul
title 清理本机 Agent

:: 本脚本需与 MobTestAgent.exe 放在同一目录，双击即可一键清理
cd /d "%~dp0"

echo 正在结束已运行的 Agent 进程…
taskkill /IM MobTestAgent.exe /F >nul 2>&1

echo.
if not exist "MobTestAgent.exe" (
    echo 未找到 MobTestAgent.exe，请将此脚本与 exe 放在同一目录后重试。
    pause
    exit /b 1
)

MobTestAgent.exe --clean
echo.
pause
