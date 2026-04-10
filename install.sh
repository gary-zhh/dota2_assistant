#!/bin/bash
# Dota 2 AI Assistant 安装脚本

echo "=== Dota 2 AI Assistant 安装 ==="
echo ""

# 检查Python版本
echo "检查Python版本..."
python3 --version || { echo "错误: 需要Python 3.8+"; exit 1; }

# 安装依赖
echo ""
echo "安装Python依赖..."
pip3 install -r requirements.txt || { echo "错误: 依赖安装失败"; exit 1; }

# 检测操作系统并复制GSI配置
echo ""
echo "配置Game State Integration..."

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    GSI_DIR="$HOME/Library/Application Support/Steam/steamapps/common/dota 2 beta/game/dota/cfg/gamestate_integration"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    GSI_DIR="$HOME/.steam/steam/steamapps/common/dota 2 beta/game/dota/cfg/gamestate_integration"
else
    echo "警告: 无法自动检测Dota 2路径（Windows系统）"
    echo "请手动复制 config/gamestate_integration_ai.cfg 到:"
    echo "C:\\Program Files (x86)\\Steam\\steamapps\\common\\dota 2 beta\\game\\dota\\cfg\\gamestate_integration\\"
    exit 0
fi

# 创建目录并复制配置
if [ -d "$(dirname "$GSI_DIR")" ]; then
    mkdir -p "$GSI_DIR"
    cp config/gamestate_integration_ai.cfg "$GSI_DIR/"
    echo "✓ GSI配置已复制到: $GSI_DIR"
else
    echo "警告: 未找到Dota 2安装目录"
    echo "请手动复制 config/gamestate_integration_ai.cfg 到:"
    echo "$GSI_DIR"
fi

echo ""
echo "=== 安装完成 ==="
echo ""
echo "使用方法:"
echo "1. 启动AI助手: python3 main.py"
echo "2. 启动Dota 2并进入游戏"
echo "3. 观察终端输出的游戏状态信息"
echo ""
echo "详细文档请查看 README.md"
