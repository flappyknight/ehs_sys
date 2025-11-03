# PostgreSQL Docker 数据库设置指南

## 🚨 问题说明

错误信息：
```
Error: Database is uninitialized and superuser password is not specified.
You must specify POSTGRES_PASSWORD to a non-empty value for the superuser.
```

**原因**：PostgreSQL Docker 镜像首次启动时必须设置 `POSTGRES_PASSWORD` 环境变量。

---

## ✅ 解决方案

### 方法 1：使用启动脚本（最简单）

```bash
# 在项目根目录执行
./start-docker-db.sh
```

这个脚本会自动：
- ✅ 清理旧容器
- ✅ 启动新的 PostgreSQL 容器
- ✅ 设置所有必需的环境变量
- ✅ 创建数据卷持久化数据
- ✅ 显示连接信息

---

### 方法 2：使用 Docker Compose（推荐生产环境）

```bash
# 启动数据库
docker-compose up -d

# 查看日志
docker-compose logs -f postgres

# 停止数据库
docker-compose down

# 停止并删除数据（谨慎使用）
docker-compose down -v
```

---

### 方法 3：使用 Docker Desktop 图形界面

#### 步骤 1：删除旧容器
1. 打开 Docker Desktop
2. 进入 "Containers" 标签
3. 找到 PostgreSQL 容器
4. 点击 "Stop" 停止容器
5. 点击 "Delete" 删除容器

#### 步骤 2：创建新容器
1. 进入 "Images" 标签
2. 找到 `postgres` 镜像
3. 点击 "Run" 按钮
4. 点击 "Optional settings" 展开设置

#### 步骤 3：配置环境变量
在 "Environment variables" 部分添加：

| Key | Value |
|-----|-------|
| `POSTGRES_PASSWORD` | `postgres` |
| `POSTGRES_USER` | `postgres` |
| `POSTGRES_DB` | `ehs` |

#### 步骤 4：配置端口映射
在 "Ports" 部分设置：

| Host port | Container port |
|-----------|----------------|
| `5432` | `5432` |

#### 步骤 5：配置数据卷（可选但推荐）
在 "Volumes" 部分添加：

| Host path | Container path |
|-----------|----------------|
| `ehs-postgres-data` | `/var/lib/postgresql/data` |

#### 步骤 6：启动容器
点击 "Run" 按钮启动容器

---

### 方法 4：使用命令行

```bash
# 完整命令
docker run -d \
  --name ehs-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=ehs \
  -p 5432:5432 \
  -v ehs-postgres-data:/var/lib/postgresql/data \
  postgres:14
```

**参数说明：**
- `-d`: 后台运行
- `--name ehs-postgres`: 容器名称
- `-e POSTGRES_PASSWORD=postgres`: 设置密码（必需）
- `-e POSTGRES_USER=postgres`: 设置用户名
- `-e POSTGRES_DB=ehs`: 自动创建数据库
- `-p 5432:5432`: 端口映射
- `-v ehs-postgres-data:/var/lib/postgresql/data`: 数据持久化

---

## 📊 数据库连接信息

启动成功后，使用以下信息连接数据库：

```
主机 (Host):     localhost
端口 (Port):     5432
数据库 (DB):     ehs
用户名 (User):   postgres
密码 (Password): postgres
```

**连接字符串：**
```
postgresql://postgres:postgres@localhost:5432/ehs
```

这与项目 `.env` 文件中的配置完全匹配：
```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ehs
```

---

## 🔧 常用 Docker 命令

### 容器管理
```bash
# 查看运行中的容器
docker ps

# 查看所有容器（包括停止的）
docker ps -a

# 启动容器
docker start ehs-postgres

# 停止容器
docker stop ehs-postgres

# 重启容器
docker restart ehs-postgres

# 删除容器
docker rm ehs-postgres

# 删除容器和数据卷
docker rm -v ehs-postgres
```

### 日志查看
```bash
# 查看实时日志
docker logs -f ehs-postgres

# 查看最后 100 行日志
docker logs --tail 100 ehs-postgres
```

### 进入容器
```bash
# 进入 PostgreSQL 命令行
docker exec -it ehs-postgres psql -U postgres -d ehs

# 进入容器 bash
docker exec -it ehs-postgres bash
```

### 数据库操作
```bash
# 在容器中执行 SQL
docker exec -it ehs-postgres psql -U postgres -d ehs -c "SELECT version();"

# 备份数据库
docker exec ehs-postgres pg_dump -U postgres ehs > backup.sql

# 恢复数据库
docker exec -i ehs-postgres psql -U postgres ehs < backup.sql
```

---

## 🔍 故障排查

### 1. 端口已被占用
**错误信息：**
```
Error: bind: address already in use
```

**解决方法：**
```bash
# 查找占用 5432 端口的进程
lsof -i :5432

# 停止占用端口的进程
kill -9 <PID>

# 或使用不同的端口
docker run -d \
  --name ehs-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5433:5432 \
  postgres:14

# 然后修改 .env 文件
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/ehs
```

### 2. 容器无法启动
```bash
# 查看详细日志
docker logs ehs-postgres

# 检查容器状态
docker inspect ehs-postgres
```

### 3. 无法连接数据库
```bash
# 测试容器内部连接
docker exec -it ehs-postgres psql -U postgres -d ehs -c "SELECT 1;"

# 测试外部连接
psql -h localhost -p 5432 -U postgres -d ehs

# 检查防火墙设置
```

### 4. 数据丢失
确保使用了数据卷：
```bash
# 检查数据卷
docker volume ls

# 查看数据卷详情
docker volume inspect ehs-postgres-data
```

---

## 🛡️ 安全建议

### 开发环境
当前配置适用于开发环境，密码简单便于测试。

### 生产环境
**强烈建议修改密码：**

```bash
# 使用强密码启动
docker run -d \
  --name ehs-postgres \
  -e POSTGRES_PASSWORD='YourStrongPassword123!' \
  -e POSTGRES_USER=ehs_user \
  -e POSTGRES_DB=ehs \
  -p 5432:5432 \
  -v ehs-postgres-data:/var/lib/postgresql/data \
  postgres:14

# 更新 .env 文件
DATABASE_URL=postgresql+asyncpg://ehs_user:YourStrongPassword123!@localhost:5432/ehs
```

---

## 📝 验证安装

### 1. 检查容器运行状态
```bash
docker ps | grep ehs-postgres
```

应该看到类似输出：
```
CONTAINER ID   IMAGE         STATUS         PORTS                    NAMES
abc123def456   postgres:14   Up 2 minutes   0.0.0.0:5432->5432/tcp   ehs-postgres
```

### 2. 测试数据库连接
```bash
docker exec -it ehs-postgres psql -U postgres -d ehs -c "SELECT version();"
```

### 3. 启动 FastAPI 应用
```bash
conda activate ehs_env
uvicorn main:app --reload
```

应该看到：
```
INFO:     Application startup complete.
admin user already exists
```

---

## 🎯 快速启动流程

```bash
# 1. 启动数据库
./start-docker-db.sh

# 2. 激活 Python 环境
conda activate ehs_env

# 3. 启动应用
uvicorn main:app --reload

# 4. 访问 API 文档
# 浏览器打开: http://localhost:8000/docs
```

---

## 📚 相关文档

- [PostgreSQL Docker 官方文档](https://hub.docker.com/_/postgres)
- [Docker Compose 文档](https://docs.docker.com/compose/)
- [PostgreSQL 认证方法](https://www.postgresql.org/docs/current/auth-methods.html)

---

## 💡 提示

- ✅ 数据会持久化保存在 Docker 数据卷中
- ✅ 容器重启后数据不会丢失
- ✅ 可以随时停止/启动容器
- ⚠️ 删除数据卷会永久删除所有数据
- 🔒 生产环境务必使用强密码

