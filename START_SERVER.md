# EHS系统服务器启动指南

## 快速启动

### 使用conda环境启动

```bash
# 进入项目目录
cd /Users/dubin/work/ehs_sys

# 激活conda环境
source /opt/anaconda3/etc/profile.d/conda.sh
conda activate ehs_env

# 启动服务器
uvicorn main:app --host 0.0.0.0 --port 8100 --reload
```

### 使用启动脚本

```bash
# 进入项目目录
cd /Users/dubin/work/ehs_sys

# 执行启动脚本
./start-server.sh
```

## 验证服务器状态

### 检查服务器是否运行

```bash
# 方法1：检查端口
lsof -i:8100

# 方法2：访问健康检查端点
curl http://localhost:8100/
```

### 查看服务器日志

```bash
# 如果使用启动脚本，查看日志文件
tail -f server.log

# 如果直接启动，日志会输出到终端
```

## 停止服务器

### 方法1：使用Ctrl+C

如果服务器在前台运行，直接按 `Ctrl+C`

### 方法2：使用停止脚本

```bash
./stop-server.sh
```

### 方法3：手动停止

```bash
# 查找进程ID
lsof -ti:8100

# 停止进程
kill $(lsof -ti:8100)

# 强制停止（如果需要）
kill -9 $(lsof -ti:8100)
```

## 常见问题

### Q1: 端口8100已被占用

**错误信息：**
```
ERROR: [Errno 48] Address already in use
```

**解决方案：**
```bash
# 查看占用端口的进程
lsof -i:8100

# 停止该进程
kill $(lsof -ti:8100)

# 或强制停止
kill -9 $(lsof -ti:8100)
```

### Q2: conda环境未激活

**错误信息：**
```
ModuleNotFoundError: No module named 'fastapi'
```

**解决方案：**
```bash
# 激活conda环境
source /opt/anaconda3/etc/profile.d/conda.sh
conda activate ehs_env

# 验证环境
which python
# 应该输出: /opt/anaconda3/envs/ehs_env/bin/python
```

### Q3: 数据库连接失败

**错误信息：**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**解决方案：**
```bash
# 检查PostgreSQL是否运行
pg_isready -h localhost -p 5432

# 如果使用Docker，启动数据库容器
docker-compose up -d

# 或使用启动脚本
./start-docker-db.sh
```

### Q4: 模型导入错误

**错误信息：**
```
ValueError: <class 'dict'> has no matching SQLAlchemy type
```

**解决方案：**
这个问题已经修复。如果仍然遇到，请查看 `db/BUGFIX_JSONB.md` 文档。

## 开发模式 vs 生产模式

### 开发模式（推荐用于本地开发）

```bash
uvicorn main:app --host 0.0.0.0 --port 8100 --reload
```

特点：
- ✅ 自动重载（代码修改后自动重启）
- ✅ 详细的错误信息
- ✅ 调试友好

### 生产模式

```bash
uvicorn main:app --host 0.0.0.0 --port 8100 --workers 4
```

特点：
- ✅ 多进程（更好的性能）
- ✅ 不自动重载（更稳定）
- ✅ 适合生产环境

## 环境变量

确保 `.env` 文件配置正确：

```env
# 数据库连接
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ehs_sys

# 管理员账户
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password

# JWT配置
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MIN=30

# 调试模式
DEBUG=false
```

## 访问API文档

服务器启动后，可以访问以下URL：

- **Swagger UI**: http://localhost:8100/docs
- **ReDoc**: http://localhost:8100/redoc
- **OpenAPI JSON**: http://localhost:8100/openapi.json

## 性能监控

### 查看进程资源使用

```bash
# 查看CPU和内存使用
ps aux | grep uvicorn

# 实时监控
top -pid $(lsof -ti:8100)
```

### 查看数据库连接

```bash
# 连接到数据库
psql -h localhost -p 5432 -U postgres -d ehs_sys

# 查看活动连接
SELECT * FROM pg_stat_activity WHERE datname = 'ehs_sys';
```

## 日志管理

### 日志级别

修改 `main.py` 中的日志配置：

```python
import logging

# 设置日志级别
logging.basicConfig(level=logging.INFO)

# 或更详细的调试日志
logging.basicConfig(level=logging.DEBUG)
```

### 日志输出到文件

```bash
# 启动时重定向日志
uvicorn main:app --host 0.0.0.0 --port 8100 > server.log 2>&1 &

# 查看日志
tail -f server.log
```

## 健康检查

### 简单健康检查

```bash
curl http://localhost:8100/
```

### 数据库连接检查

```bash
curl http://localhost:8100/health
```

## 备份与恢复

### 启动前备份数据库

```bash
# 备份数据库
pg_dump -h localhost -U postgres -d ehs_sys -F c -f backup_$(date +%Y%m%d_%H%M%S).dump

# 如果需要恢复
pg_restore -h localhost -U postgres -d ehs_sys backup_20251111_193000.dump
```

## 完整启动流程

```bash
# 1. 进入项目目录
cd /Users/dubin/work/ehs_sys

# 2. 启动数据库（如果使用Docker）
docker-compose up -d

# 3. 等待数据库启动
sleep 3

# 4. 激活conda环境
source /opt/anaconda3/etc/profile.d/conda.sh
conda activate ehs_env

# 5. 验证环境
python -c "from db.models import EnterpriseInfo; print('✓ Environment OK')"

# 6. 启动服务器
uvicorn main:app --host 0.0.0.0 --port 8100 --reload
```

## 故障排查清单

启动失败时，按以下顺序检查：

- [ ] PostgreSQL服务是否运行？
- [ ] conda环境是否激活？
- [ ] 端口8100是否被占用？
- [ ] .env文件是否存在且配置正确？
- [ ] 数据库连接信息是否正确？
- [ ] 所有Python依赖是否已安装？
- [ ] 数据库表是否已创建？

## 获取帮助

如遇到问题，请查看：

1. **错误日志**: `server.log` 或终端输出
2. **数据库日志**: PostgreSQL日志文件
3. **文档目录**: `db/` 目录下的所有文档
4. **修复说明**: `db/BUGFIX_JSONB.md`

---

**最后更新**: 2025-11-11  
**维护团队**: EHS系统开发团队

