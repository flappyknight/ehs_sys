#!/bin/bash

# EHS 系统服务器停止脚本

PORT=8100

echo "=== EHS 系统服务器停止脚本 ==="
echo ""

# 查找占用端口的进程
PIDS=$(lsof -ti:$PORT 2>/dev/null)

if [ -z "$PIDS" ]; then
    echo "ℹ️  端口 $PORT 没有被占用，服务器可能已经停止"
    exit 0
fi

echo "🔍 找到以下进程占用端口 $PORT："
for PID in $PIDS; do
    echo "   - PID: $PID"
    ps -p $PID -o command= | head -1 | sed 's/^/     /'
done

echo ""
echo "🛑 正在停止服务器..."
echo "$PIDS" | xargs kill -9 2>/dev/null

sleep 1

# 验证是否成功停止
if lsof -ti:$PORT > /dev/null 2>&1; then
    echo "❌ 停止失败，请手动检查"
    exit 1
else
    echo "✅ 服务器已成功停止"
fi

