#!/bin/bash

echo "========================================"
echo " 公路巡检飞行管理系统 - 后端启动脚本"
echo "========================================"
echo ""

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "[错误] 未找到虚拟环境！"
    echo "请先运行以下命令创建虚拟环境："
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# 激活虚拟环境
echo "[1/3] 激活虚拟环境..."
source venv/bin/activate

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo ""
    echo "[警告] 未找到 .env 文件！"
    echo "正在从 env.example 复制..."
    cp env.example .env
    echo ""
    echo "[重要] 请编辑 .env 文件，配置数据库连接信息！"
    echo ""
    read -p "按任意键继续..."
fi

# 设置环境变量
export FLASK_APP=run.py
export FLASK_ENV=development

# 启动服务
echo ""
echo "[2/3] 检查依赖..."
if ! pip list | grep -q Flask; then
    echo "[警告] 依赖未安装，正在安装..."
    pip install -r requirements.txt
fi

echo ""
echo "[3/3] 启动后端服务..."
echo ""
python run.py

