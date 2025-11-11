# EHS系统数据库配置信息

## 数据库连接信息

### PostgreSQL数据库配置

- **数据库类型**: PostgreSQL
- **数据库名称**: `ehs`
- **用户名**: `postgres`
- **密码**: `postgres`
- **主机地址**: `localhost`
- **端口号**: `5432`
- **连接URL**: `postgresql+asyncpg://postgres:postgres@localhost:5432/ehs`

### Docker容器信息

如果使用Docker运行PostgreSQL数据库：

```bash
# 启动数据库容器
docker-compose up -d

# 停止数据库容器
docker-compose down

# 查看容器状态
docker ps

# 进入数据库容器
docker exec -it <container_name> psql -U postgres -d ehs
```

### 连接池配置

应用程序使用SQLAlchemy异步引擎，连接池配置如下：

- **pool_size**: 10 (连接池大小)
- **max_overflow**: 20 (最大溢出连接数)
- **pool_timeout**: 30秒 (连接超时时间)
- **pool_recycle**: 1800秒 (连接回收时间，30分钟)

### 环境变量配置

在项目根目录创建 `.env` 文件，配置以下环境变量：

```env
# 数据库连接
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ehs

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

### 数据库管理工具

推荐使用以下工具管理PostgreSQL数据库：

1. **pgAdmin 4** - 官方图形化管理工具
2. **DBeaver** - 通用数据库管理工具
3. **DataGrip** - JetBrains出品的数据库IDE
4. **psql** - PostgreSQL命令行工具

### 连接示例

#### 使用psql命令行连接

```bash
psql -h localhost -p 5432 -U postgres -d ehs
```

#### 使用Python连接（同步）

```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="ehs",
    user="postgres",
    password="postgres"
)
```

#### 使用Python连接（异步）

```python
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    "postgresql+asyncpg://postgres:postgres@localhost:5432/ehs",
    echo=True
)
```

### 数据库备份与恢复

#### 备份数据库

```bash
# 备份整个数据库
pg_dump -h localhost -U postgres -d ehs -F c -f ehs_backup.dump

# 备份为SQL文件
pg_dump -h localhost -U postgres -d ehs -f ehs_backup.sql
```

#### 恢复数据库

```bash
# 从dump文件恢复
pg_restore -h localhost -U postgres -d ehs ehs_backup.dump

# 从SQL文件恢复
psql -h localhost -U postgres -d ehs -f ehs_backup.sql
```

### 数据库维护

#### 查看数据库大小

```sql
SELECT pg_size_pretty(pg_database_size('ehs'));
```

#### 查看表大小

```sql
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

#### 清理和优化

```sql
-- 清理死元组
VACUUM ANALYZE;

-- 完全清理
VACUUM FULL;

-- 重建索引
REINDEX DATABASE ehs;
```

### 安全建议

1. **生产环境**：
   - 修改默认密码
   - 使用强密码策略
   - 限制数据库访问IP
   - 启用SSL连接
   - 定期备份数据

2. **开发环境**：
   - 使用独立的开发数据库
   - 不要在代码中硬编码密码
   - 使用环境变量管理敏感信息

3. **权限管理**：
   - 为不同用途创建不同的数据库用户
   - 遵循最小权限原则
   - 定期审查用户权限

### 监控与日志

#### 启用查询日志

修改PostgreSQL配置文件 `postgresql.conf`：

```conf
logging_collector = on
log_directory = 'pg_log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_statement = 'all'
log_duration = on
log_min_duration_statement = 1000  # 记录执行时间超过1秒的查询
```

#### 查看活动连接

```sql
SELECT * FROM pg_stat_activity WHERE datname = 'ehs';
```

#### 查看慢查询

```sql
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### 故障排查

#### 连接失败

1. 检查PostgreSQL服务是否运行
2. 检查防火墙设置
3. 验证连接参数
4. 查看PostgreSQL日志

#### 性能问题

1. 检查慢查询日志
2. 分析查询执行计划（EXPLAIN ANALYZE）
3. 检查索引使用情况
4. 监控连接池状态

#### 数据不一致

1. 检查事务隔离级别
2. 验证外键约束
3. 检查触发器逻辑
4. 查看错误日志

---

**最后更新时间**: 2025-11-11
**维护人员**: EHS系统开发团队
