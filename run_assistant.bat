@echo off
chcp 65001 >nul
title Dota 2 AI Assistant

echo ================================================================================
echo                          Dota 2 AI Assistant
echo ================================================================================
echo.
echo 正在启动AI助手...
echo.
echo 提示:
echo - 确保Dota 2已启动并进入游戏
echo - 当前模式: 观察模式（安全）
echo - 按 Ctrl+C 停止程序
echo.
echo ================================================================================
echo.

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 运行主程序
python main.py

REM 如果程序异常退出，暂停以查看错误信息
if errorlevel 1 (
    echo.
    echo ================================================================================
    echo                              程序异常退出
    echo ================================================================================
    echo.
    echo 常见问题:
    echo 1. 检查Python是否正确安装
    echo 2. 检查依赖是否完整安装: pip install -r requirements.txt
    echo 3. 查看错误信息并参考 README_WINDOWS.md
    echo.
)

pause
