# EHS数据库实施总结

## 最后更新时间
2025-11-11

## 数据库信息

- **数据库名**: `ehs`
- **主机**: localhost:5432
- **用户**: postgres
- **总表数**: 8个

## 当前表结构

### 核心表列表

1. **users** - 用户表
2. **enterprise_user** - 企业用户表
3. **contractor_user** - 承包商用户表
4. **enterprise_info** - 企业信息表（JSONB）
5. **contractor_info** - 承包商信息表（JSONB）
6. **contractor** - 承包商表（旧表，兼容）
7. **contractor_project** - 承包商项目表
8. **ticket** - 作业票表

### 表关系图

```
users
├── enterprise_user (外键)
└── contractor_user (外键)

enterprise_info
├── parent_enterprise_id (自引用)
├── subsidiary_ids (JSONB数组)
└── allowed_contractor_ids (JSONB数组)

contractor_info
├── active_enterprise_ids (JSONB数组)
├── inactive_enterprise_ids (JSONB数组)
└── cooperation_detail_log (JSONB对象)

contractor
└── contractor_project (外键)

ticket
├── applicant → enterprise_user
├── worker → contractor_user
└── custodians → enterprise_user
```

## 核心功能

### enterprise_info（企业信息表）

**特性**：
- 企业基本信息管理
- 企业层级关系（母公司-子公司）
- 承包商白名单管理
- 完整审计日志
- 软删除支持

**JSONB字段**：
- `subsidiary_ids` - 子公司ID列表
- `allowed_contractor_ids` - 允许合作的承包商ID列表
- `modification_log` - 修改记录日志

### contractor_info（承包商信息表）

**特性**：
- 承包商基本信息管理
- 合作企业状态管理
- 合作历史详细记录
- 完整审计日志
- 软删除支持

**JSONB字段**：
- `active_enterprise_ids` - 当前合作企业ID列表
- `inactive_enterprise_ids` - 已失效合作企业ID列表
- `cooperation_detail_log` - 合作详情日志
- `modification_log` - 修改记录日志

## 数据库文件

### SQL文件
- `create_tables.sql` - 完整的建表语句（唯一的SQL文件）

### 文档文件
- `README.md` - 文档导航
- `db_config_info.md` - 数据库配置信息
- `db_info.md` - 完整表结构文档
- `TABLE_RELATIONSHIPS.md` - 表关系详细说明
- `USAGE_GUIDE.md` - 使用指南和示例
- `IMPLEMENTATION_SUMMARY.md` - 本文档

### 代码文件
- `models.py` - SQLModel数据库模型
- `connection.py` - 数据库连接管理
- `crud.py` - CRUD操作
- `encode_data.py` - 数据编码工具

## 使用方法

### 连接数据库
```bash
psql -h localhost -p 5432 -U postgres -d ehs
```

### 查看所有表
```sql
\dt
```

### 创建所有表
```bash
psql -U postgres -d ehs -f db/create_tables.sql
```

### Python代码示例
```python
from db.models import EnterpriseInfo, ContractorInfo
from sqlmodel import select

# 查询所有企业
async def get_all_enterprises(session):
    statement = select(EnterpriseInfo).where(
        EnterpriseInfo.is_deleted == False
    )
    result = await session.execute(statement)
    return result.scalars().all()
```

## 重要注意事项

### 1. 数据库名称
⚠️ 数据库名是 `ehs`，不是 `ehs_sys`

### 2. JSONB字段操作
```sql
-- 检查是否包含某个ID
WHERE allowed_contractor_ids @> '10'::jsonb

-- 添加元素
UPDATE enterprise_info 
SET allowed_contractor_ids = allowed_contractor_ids || '10'::jsonb
WHERE enterprise_id = 1;

-- 删除元素
UPDATE enterprise_info 
SET allowed_contractor_ids = allowed_contractor_ids - '10'
WHERE enterprise_id = 1;
```

### 3. 软删除
查询时必须过滤已删除的记录：
```sql
WHERE is_deleted = false
```

### 4. 自动触发器
`updated_at` 字段会在UPDATE时自动更新，无需手动维护。

## 索引策略

### GIN索引（JSONB字段）
- `idx_enterprise_subsidiary_ids`
- `idx_enterprise_allowed_contractor_ids`
- `idx_contractor_info_active_enterprise_ids`
- `idx_contractor_info_inactive_enterprise_ids`

### B-Tree索引（常规字段）
- 公司名称、营业状态、删除标记等

## 技术栈

- **数据库**: PostgreSQL 14+
- **ORM**: SQLModel (基于SQLAlchemy 2.0)
- **异步驱动**: asyncpg
- **API框架**: FastAPI
- **数据验证**: Pydantic

## 改造历史

### 2025-11-11 简化改造
- ✅ 删除了10个不需要的表
- ✅ 从8个表简化到8个核心表
- ✅ 删除了所有.sh脚本文件
- ✅ 只保留一个create_tables.sql文件
- ✅ 更新了所有相关文档
- ✅ 清理了db/models.py和api/model.py

### 2025-11-11 初始改造
- 添加了enterprise_info和contractor_info表
- 修复了JSONB字段类型定义
- 更新了数据库名为ehs

### 2025-11-03 原始创建
- 创建了基础表结构

## 文档导航

| 文档 | 说明 |
|------|------|
| [README.md](./README.md) | 数据库文档导航 |
| [db_config_info.md](./db_config_info.md) | 数据库配置信息 |
| [db_info.md](./db_info.md) | 完整表结构文档 |
| [USAGE_GUIDE.md](./USAGE_GUIDE.md) | 使用指南 |
| [TABLE_RELATIONSHIPS.md](./TABLE_RELATIONSHIPS.md) | 表关系图 |
| [create_tables.sql](./create_tables.sql) | 建表SQL语句 |

---

**状态**: ✅ 已完成并简化  
**维护团队**: EHS系统开发团队
