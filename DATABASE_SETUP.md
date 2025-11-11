# 数据库设置说明

## 数据库信息

- **数据库名称**: `ehs`
- **用户名**: `postgres`
- **密码**: `postgres`
- **主机**: `localhost`
- **端口**: `5432`

## 已创建的表

以下8个表已成功在数据库中创建：

1. **users** - 用户表
2. **enterprise_user** - 企业用户表
3. **contractor_user** - 承包商用户表
4. **enterprise_info** - 企业信息表（包含JSONB字段）
5. **contractor_info** - 承包商信息表（包含JSONB字段）
6. **contractor** - 承包商表（旧表，保持兼容）
7. **contractor_project** - 承包商项目表
8. **ticket** - 作业票表

## 数据库连接字符串

```
postgresql+asyncpg://postgres:postgres@localhost:5432/ehs
```

## 常用命令

### 连接数据库
```bash
psql -U postgres -d ehs
```

### 查看所有表
```bash
psql -U postgres -d ehs -c "\dt"
```

### 查看表结构
```bash
psql -U postgres -d ehs -c "\d 表名"
```

### 查看enterprise_info表
```bash
psql -U postgres -d ehs -c "\d enterprise_info"
```

### 查看contractor_info表
```bash
psql -U postgres -d ehs -c "\d contractor_info"
```

### 创建所有表
```bash
psql -U postgres -d ehs -f db/create_tables.sql
```

### 删除数据库（谨慎使用）
```bash
psql -U postgres -c "DROP DATABASE ehs;"
```

## 注意事项

1. 所有表都包含了适当的主键、外键约束和索引
2. 时间戳字段使用 `TIMESTAMP WITHOUT TIME ZONE` 类型
3. 字符串字段都设置了最大长度限制
4. 外键关系已正确建立，确保数据完整性
5. `enterprise_info` 和 `contractor_info` 表使用JSONB字段存储复杂关系数据

## 核心表说明

### enterprise_info（企业信息表）
- 支持企业层级关系（母公司-子公司）
- 使用JSONB字段存储子公司列表和承包商白名单
- 包含完整的修改记录日志
- 支持软删除

### contractor_info（承包商信息表）
- 管理承包商与企业的合作关系
- 使用JSONB字段存储合作企业列表和详情
- 包含完整的合作历史记录
- 支持软删除

## 数据库改造说明

### 2025-11-11 改造
- 添加了 `enterprise_info` 表（企业信息表，包含JSONB字段）
- 添加了 `contractor_info` 表（承包商信息表，包含JSONB字段）
- 删除了不需要的表：company, department, area, entry_plan, entry_plan_user, entry_register, work_equipment, confined_space, temporary_power, cross_work
- 保留了 `contractor` 表以保持向后兼容
- 简化了数据库结构，保持项目精简

### 原始创建时间
2025-11-03

## 详细文档

更多详细信息请查看：
- `db/README.md` - 数据库文档导航
- `db/db_info.md` - 完整表结构文档
- `db/create_tables.sql` - 建表SQL语句
