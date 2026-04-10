@echo off
chcp 65001 >nul
echo ================================================================================
echo                    Dota 2 AI Assistant - Windows 安装程序
echo ================================================================================
echo.

REM 检查Python
echo [1/5] 检查Python安装...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python
    echo.
    echo 请先安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/downloads/
    echo.
    echo 安装时务必勾选 "Add Python to PATH"
    pause
    exit /b 1
)
python --version
echo ✓ Python已安装
echo.

REM 检查pip
echo [2/5] 检查pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到pip
    echo 正在安装pip...
    python -m ensurepip --default-pip
)
echo ✓ pip已就绪
echo.

REM 安装依赖
echo [3/5] 安装Python依赖包...
echo 这可能需要几分钟，请耐心等待...
echo.
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ⚠️  使用国内镜像重试...
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
)
echo.
echo ✓ 依赖安装完成
echo.

REM 查找Dota 2路径
echo [4/5] 查找Dota 2安装路径...
set DOTA2_PATH=
set DOTA2_CFG=

REM 常见Steam路径
set "STEAM_PATHS[0]=C:\Program Files (x86)\Steam"
set "STEAM_PATHS[1]=C:\Program Files\Steam"
set "STEAM_PATHS[2]=D:\Steam"
set "STEAM_PATHS[3]=D:\SteamLibrary"
set "STEAM_PATHS[4]=E:\Steam"
set "STEAM_PATHS[5]=E:\SteamLibrary"

for /L %%i in (0,1,5) do (
    call set "STEAM_PATH=%%STEAM_PATHS[%%i]%%"
    if exist "!STEAM_PATH!\steamapps\common\dota 2 beta\game\dota" (
        set "DOTA2_PATH=!STEAM_PATH!\steamapps\common\dota 2 beta"
        set "DOTA2_CFG=!DOTA2_PATH!\game\dota\cfg\gamestate_integration"
        goto :found_dota2
    )
)

REM 如果没找到，让用户手动输入
echo.
echo ⚠️  未自动找到Dota 2安装路径
echo.
echo 请手动输入Dota 2安装路径（例如: C:\Program Files (x86)\Steam\steamapps\common\dota 2 beta）
echo 或按Ctrl+C取消，稍后手动配置
echo.
set /p DOTA2_PATH="Dota 2路径: "

if "%DOTA2_PATH%"=="" (
    echo.
    echo ⚠️  跳过GSI配置，请稍后手动配置
    echo 参考文档: README_WINDOWS.md
    goto :skip_gsi
)

set "DOTA2_CFG=%DOTA2_PATH%\game\dota\cfg\gamestate_integration"

:found_dota2
echo ✓ 找到Dota 2: %DOTA2_PATH%
echo.

REM 配置GSI
echo [5/5] 配置Game State Integration...

REM 创建GSI目录
if not exist "%DOTA2_CFG%" (
    mkdir "%DOTA2_CFG%"
    echo ✓ 创建GSI目录
)

REM 复制配置文件
copy /Y "config\gamestate_integration_ai.cfg" "%DOTA2_CFG%\" >nul
if errorlevel 1 (
    echo ❌ 错误: 无法复制GSI配置文件
    echo 请检查Dota 2路径是否正确
    echo 或以管理员身份运行此脚本
    pause
    exit /b 1
)

echo ✓ GSI配置文件已复制
echo.

:skip_gsi

REM 创建启动脚本
echo @echo off > run_assistant.bat
echo chcp 65001 ^>nul >> run_assistant.bat
echo cd /d "%%~dp0" >> run_assistant.bat
echo python main.py >> run_assistant.bat
echo pause >> run_assistant.bat

echo ✓ 创建启动脚本: run_assistant.bat
echo.

REM 完成
echo ================================================================================
echo                              ✅ 安装完成！
echo ================================================================================
echo.
echo 下一步:
echo.
echo 1. 启动AI助手:
echo    方法A: 双击 run_assistant.bat
echo    方法B: 在命令行运行 python main.py
echo.
echo 2. 启动Dota 2并进入游戏
echo.
echo 3. 选择任意英雄（支持全部123个英雄）
echo.
echo 4. 观察AI的决策！
echo.
echo ================================================================================
echo.
echo 📖 详细文档: README_WINDOWS.md
echo 🔧 配置文件: config\config.yaml
echo ⚠️  首次运行建议使用观察模式（executor.enabled: false）
echo.
echo ================================================================================
echo.
pause
