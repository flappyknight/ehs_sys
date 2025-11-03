# 数据库设置说明

## 数据库信息

- **数据库名称**: `ehs_sys`
- **用户名**: `postgres`
- **密码**: `postgres`
- **主机**: `localhost`
- **端口**: `5432`

## 已创建的表

以下16个表已成功在数据库中创建：

1. **users** - 用户表
2. **company** - 公司表
3. **contractor** - 承包商表
4. **contractor_project** - 承包商项目表
5. **contractor_user** - 承包商用户表
6. **department** - 部门表
7. **enterprise_user** - 企业用户表
8. **entry_plan** - 入场计划表
9. **entry_plan_user** - 入场计划用户表
10. **entry_register** - 入场登记表
11. **area** - 区域表
12. **work_equipment** - 作业设备表
13. **confined_space** - 受限空间表
14. **temporary_power** - 临时用电表
15. **cross_work** - 交叉作业表
16. **ticket** - 作业票表

## 数据库连接字符串

```
postgresql+asyncpg://postgres:postgres@localhost:5432/ehs_sys
```

## 常用命令

### 连接数据库
```bash
psql -U postgres -d ehs_sys
```

### 查看所有表
```bash
psql -U postgres -d ehs_sys -c "\dt"
```

### 查看表结构
```bash
psql -U postgres -d ehs_sys -c "\d 表名"
```

### 删除数据库（谨慎使用）
```bash
psql -U postgres -c "DROP DATABASE ehs_sys;"
```

## 注意事项

1. 所有表都包含了适当的主键、外键约束和索引
2. 时间戳字段使用 `TIMESTAMP WITHOUT TIME ZONE` 类型
3. 字符串字段都设置了最大长度限制
4. 外键关系已正确建立，确保数据完整性

## 创建时间

2025-11-03

