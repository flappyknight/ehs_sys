#!/bin/bash

# EHS 系统服务器启动脚本
# 使用 conda ehs_env 环境

set -e

PORT=8100
LOG_FILE="server.log"

echo "=== EHS 系统服务器启动脚本 ==="
echo ""

# 检查端口是否被占用
if lsof -ti:$PORT > /dev/null 2>&1; then
    echo "⚠️  端口 $PORT 已被占用，正在关闭占用进程..."
    lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
    sleep 1
    echo "✅ 端口已释放"
fi

# 激活 conda 环境
echo "🔧 激活 conda ehs_env 环境..."
source /opt/anaconda3/bin/activate ehs_env

# 启动服务器
echo "🚀 启动服务器 (端口: $PORT)..."
nohup uvicorn main:app --reload --host 0.0.0.0 --port $PORT > $LOG_FILE 2>&1 &
SERVER_PID=$!

# 等待服务器启动
echo "⏳ 等待服务器启动..."
sleep 3

# 检查服务器是否成功启动
if ps -p $SERVER_PID > /dev/null; then
    echo ""
    echo "✅ 服务器启动成功！"
    echo ""
    echo "📋 服务器信息："
    echo "   - PID: $SERVER_PID"
    echo "   - 端口: $PORT"
    echo "   - 日志文件: $LOG_FILE"
    echo "   - API 文档: http://localhost:$PORT/docs"
    echo ""
    echo "📝 查看日志："
    echo "   tail -f $LOG_FILE"
    echo ""
    echo "🛑 停止服务器："
    echo "   kill $SERVER_PID"
    echo "   或"
    echo "   lsof -ti:$PORT | xargs kill -9"
    echo ""
else
    echo ""
    echo "❌ 服务器启动失败！"
    echo "请查看日志文件: $LOG_FILE"
    exit 1
fi

