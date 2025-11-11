# EHS系统数据库文档中心

欢迎来到EHS系统数据库文档中心！本目录包含了所有与数据库相关的文档和脚本。

## 📚 文档导航

### 核心文档

| 文档 | 说明 | 用途 |
|------|------|------|
| [db_config_info.md](./db_config_info.md) | 数据库配置信息 | 查看连接信息、环境配置、备份恢复等 |
| [db_info.md](./db_info.md) | 数据库表结构详细文档 | 查看所有表的结构、字段说明、SQL语句 |
| [USAGE_GUIDE.md](./USAGE_GUIDE.md) | 使用指南 | 学习如何使用企业信息表和承包商信息表 |
| [TABLE_RELATIONSHIPS.md](./TABLE_RELATIONSHIPS.md) | 表关系图 | 理解表之间的关系和数据流转 |
| [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) | 实施总结 | 了解完成的工作和后续建议 |

### 脚本文件

| 文件 | 说明 | 使用方法 |
|------|------|----------|
| [rebuild_tables.sql](./rebuild_tables.sql) | 表重建SQL脚本 | 包含删除旧表和创建新表的完整SQL |
| [execute_rebuild.sh](./execute_rebuild.sh) | 执行脚本 | 一键执行表重建：`./execute_rebuild.sh` |

### 代码文件

| 文件 | 说明 |
|------|------|
| [models.py](./models.py) | SQLModel数据库模型 |
| [connection.py](./connection.py) | 数据库连接管理 |
| [crud.py](./crud.py) | 数据库CRUD操作 |

---

## 🚀 快速开始

### 1. 查看数据库配置

```bash
# 查看数据库连接信息
cat db_config_info.md
```

**关键信息**：
- 数据库名：`ehs_sys`
- 用户名：`postgres`
- 密码：`postgres`
- 主机：`localhost`
- 端口：`5432`

### 2. 执行表重建

```bash
# 方式一：使用执行脚本（推荐）
cd /Users/dubin/work/ehs_sys/db
./execute_rebuild.sh

# 方式二：手动执行SQL
psql -h localhost -p 5432 -U postgres -d ehs_sys -f rebuild_tables.sql
```

### 3. 验证表结构

```bash
# 连接数据库
psql -h localhost -p 5432 -U postgres -d ehs_sys

# 查看表结构
\d enterprise_info
\d contractor_info
```

### 4. 学习使用

阅读 [USAGE_GUIDE.md](./USAGE_GUIDE.md) 学习如何使用新表。

---

## 📊 新增表说明

### enterprise_info（企业信息表）

**用途**：存储企业的基本信息、组织关系及合作承包商信息

**核心功能**：
- ✅ 企业基本信息（营业执照、公司名称、法人等）
- ✅ 企业层级关系（支持母公司-子公司树形结构）
- ✅ 承包商白名单管理
- ✅ 完整的修改记录日志
- ✅ 软删除支持
- ✅ 自动更新时间戳

**关键字段**：
- `parent_enterprise_id`: 上级公司ID（支持自引用）
- `subsidiary_ids`: 下级公司ID列表（JSONB数组）
- `allowed_contractor_ids`: 允许合作的承包商ID列表（JSONB数组）
- `modification_log`: 修改记录日志（JSONB数组）

### contractor_info（承包商信息表）

**用途**：存储承包商的基本信息、合作状态及合作企业详情

**核心功能**：
- ✅ 承包商基本信息（营业执照、公司名称、法人等）
- ✅ 合作企业管理（活跃/失效状态）
- ✅ 详细的合作历史记录
- ✅ 完整的修改记录日志
- ✅ 软删除支持
- ✅ 自动更新时间戳

**关键字段**：
- `active_enterprise_ids`: 合作状态企业ID列表（JSONB数组）
- `inactive_enterprise_ids`: 已失效合作企业ID列表（JSONB数组）
- `cooperation_detail_log`: 合作企业详情日志（JSONB数组）
- `modification_log`: 修改记录日志（JSONB数组）

---

## 🎯 主要特性

### 1. JSONB字段支持

使用PostgreSQL的JSONB类型存储复杂数据结构：
- 灵活的数据存储
- 高效的查询性能（GIN索引）
- 支持嵌套结构
- 原生JSON操作

### 2. 企业层级关系

支持企业组织架构的树形结构：
- 自引用外键（`parent_enterprise_id`）
- 子公司列表（`subsidiary_ids`）
- 递归查询支持
- 层级关系维护

### 3. 合作关系管理

双向关系验证机制：
- 企业白名单（`allowed_contractor_ids`）
- 承包商合作列表（`active_enterprise_ids`）
- 状态流转（活跃→失效）
- 详细历史记录

### 4. 审计追踪

完整的操作日志记录：
- 操作时间戳
- 操作人信息
- 操作类型
- 变更内容
- 变更原因

### 5. 软删除

数据安全保护：
- 使用`is_deleted`标记
- 不直接删除记录
- 支持数据恢复
- 历史数据保留

### 6. 自动触发器

时间戳自动维护：
- `created_at`：创建时自动设置
- `updated_at`：更新时自动更新
- 无需手动维护
- 保证数据一致性

---

## 📖 使用示例

### 创建企业信息

```sql
INSERT INTO enterprise_info (
    license_file,
    company_name,
    company_type,
    legal_person,
    establish_date,
    registered_capital,
    applicant_name
) VALUES (
    '/uploads/licenses/enterprise_001.jpg',
    '示例科技有限公司',
    '有限责任公司',
    '张三',
    '2020-01-15',
    5000.00,
    '李四'
) RETURNING enterprise_id;
```

### 创建承包商信息

```sql
INSERT INTO contractor_info (
    license_file,
    company_name,
    company_type,
    legal_person,
    establish_date,
    registered_capital,
    applicant_name
) VALUES (
    '/uploads/licenses/contractor_001.jpg',
    '优质建筑承包有限公司',
    '有限责任公司',
    '孙七',
    '2018-03-10',
    3000.00,
    '周八'
) RETURNING contractor_id;
```

### 查询企业的子公司

```sql
SELECT e2.*
FROM enterprise_info e1
CROSS JOIN jsonb_array_elements_text(e1.subsidiary_ids) AS sub_id
JOIN enterprise_info e2 ON e2.enterprise_id = sub_id::integer
WHERE e1.enterprise_id = 1;
```

### 查询承包商的合作企业

```sql
SELECT e.*
FROM contractor_info c
CROSS JOIN jsonb_array_elements_text(c.active_enterprise_ids) AS ent_id
JOIN enterprise_info e ON e.enterprise_id = ent_id::integer
WHERE c.contractor_id = 10;
```

更多示例请参考 [USAGE_GUIDE.md](./USAGE_GUIDE.md)

---

## 🔧 技术栈

- **数据库**: PostgreSQL 14+
- **特性**: JSONB、GIN索引、触发器、递归查询
- **ORM**: SQLModel (基于SQLAlchemy 2.0)
- **异步驱动**: asyncpg
- **API框架**: FastAPI
- **数据验证**: Pydantic

---

## 📋 检查清单

执行表重建后，请验证以下内容：

- [ ] 表创建成功（`enterprise_info`, `contractor_info`, `contractor`）
- [ ] 索引创建成功（7个索引 for enterprise_info, 5个索引 for contractor_info）
- [ ] 触发器创建成功（2个触发器）
- [ ] 可以成功插入测试数据
- [ ] JSONB字段查询正常
- [ ] 触发器自动更新`updated_at`字段

---

## 🆘 常见问题

### Q: 如何备份数据？

```bash
pg_dump -h localhost -U postgres -d ehs_sys -F c -f backup.dump
```

### Q: 如何恢复数据？

```bash
pg_restore -h localhost -U postgres -d ehs_sys backup.dump
```

### Q: JSONB查询慢怎么办？

确保已创建GIN索引：
```sql
CREATE INDEX idx_name ON table_name USING GIN(jsonb_column);
```

### Q: 如何查看表大小？

```sql
SELECT pg_size_pretty(pg_total_relation_size('enterprise_info'));
```

更多问题请参考 [USAGE_GUIDE.md](./USAGE_GUIDE.md) 的常见问题部分。

---

## 📞 联系方式

如有问题或建议，请联系：
- **项目**: EHS系统
- **团队**: EHS系统开发团队
- **更新时间**: 2025-11-11

---

## 📝 更新日志

### v1.0 (2025-11-11)

**新增**：
- ✨ 创建`enterprise_info`表（企业信息表）
- ✨ 创建`contractor_info`表（承包商信息表）
- ✨ 添加JSONB字段支持企业层级和合作关系
- ✨ 添加GIN索引优化JSONB查询
- ✨ 添加自动更新时间戳触发器
- ✨ 完整的文档和使用指南

**保留**：
- 🔄 保留旧的`contractor`表以保持向后兼容

**文档**：
- 📚 数据库配置信息文档
- 📚 表结构详细文档
- 📚 使用指南
- 📚 表关系图
- 📚 实施总结

---

## 🎉 开始使用

1. 阅读 [db_config_info.md](./db_config_info.md) 了解数据库配置
2. 执行 [execute_rebuild.sh](./execute_rebuild.sh) 重建表
3. 阅读 [USAGE_GUIDE.md](./USAGE_GUIDE.md) 学习使用方法
4. 查看 [TABLE_RELATIONSHIPS.md](./TABLE_RELATIONSHIPS.md) 理解表关系
5. 参考 [db_info.md](./db_info.md) 查询详细的表结构

**祝您使用愉快！** 🚀

