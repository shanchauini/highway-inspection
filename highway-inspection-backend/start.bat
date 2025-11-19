@echo off
echo ========================================
echo  公路巡检飞行管理系统 - 后端启动脚本
echo ========================================
echo.

REM 检查虚拟环境是否存在
if not exist "venv\" (
    echo [错误] 未找到虚拟环境！
    echo 请先运行以下命令创建虚拟环境：
    echo   python -m venv venv
    echo   .\venv\Scripts\activate
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

REM 激活虚拟环境
echo [1/3] 激活虚拟环境...
call venv\Scripts\activate.bat

REM 检查 .env 文件
if not exist ".env" (
    echo.
    echo [警告] 未找到 .env 文件！
    echo 正在从 env.example 复制...
    copy env.example .env
    echo.
    echo [重要] 请编辑 .env 文件，配置数据库连接信息！
    echo.
    pause
)

REM 设置环境变量
set FLASK_APP=run.py
set FLASK_ENV=development

REM 启动服务
echo.
echo [2/3] 检查依赖...
pip list | findstr Flask > nul
if errorlevel 1 (
    echo [警告] 依赖未安装，正在安装...
    pip install -r requirements.txt
)

echo.
echo [3/3] 启动后端服务...
echo.
python run.py

pause

