#!/bin/bash

# EHS 系统 - PostgreSQL Docker 启动脚本

echo "🚀 启动 PostgreSQL Docker 容器..."

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ 错误: Docker 未运行，请先启动 Docker Desktop"
    exit 1
fi

# 停止并删除旧容器（如果存在）
echo "🔄 清理旧容器..."
docker stop ehs-postgres 2>/dev/null || true
docker rm ehs-postgres 2>/dev/null || true

# 启动新容器
echo "📦 启动新容器..."
docker run -d \
  --name ehs-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=ehs \
  -e TZ=Asia/Shanghai \
  -p 5432:5432 \
  -v ehs-postgres-data:/var/lib/postgresql/data \
  postgres:14

# 等待数据库启动
echo "⏳ 等待数据库启动..."
sleep 5

# 检查容器状态
if docker ps | grep -q ehs-postgres; then
    echo ""
    echo "✅ PostgreSQL 容器启动成功！"
    echo ""
    echo "📊 数据库连接信息："
    echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  主机 (Host):     localhost"
    echo "  端口 (Port):     5432"
    echo "  数据库 (DB):     ehs"
    echo "  用户名 (User):   postgres"
    echo "  密码 (Password): postgres"
    echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🔗 连接字符串："
    echo "  postgresql://postgres:postgres@localhost:5432/ehs"
    echo ""
    echo "💡 常用命令："
    echo "  查看日志: docker logs ehs-postgres"
    echo "  停止容器: docker stop ehs-postgres"
    echo "  启动容器: docker start ehs-postgres"
    echo "  进入容器: docker exec -it ehs-postgres psql -U postgres -d ehs"
    echo ""
else
    echo "❌ 容器启动失败，请检查日志："
    echo "   docker logs ehs-postgres"
    exit 1
fi

