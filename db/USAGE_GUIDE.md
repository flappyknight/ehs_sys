# 企业信息表和承包商信息表使用指南

## 快速开始

### 1. 执行数据库重建

在执行之前，请确保：
- PostgreSQL服务正在运行
- 已备份重要数据

```bash
cd /Users/dubin/work/ehs_sys/db
./execute_rebuild.sh
```

或者手动执行SQL脚本：

```bash
psql -h localhost -p 5432 -U postgres -d ehs_sys -f rebuild_tables.sql
```

### 2. 验证表创建

连接到数据库并验证表结构：

```bash
psql -h localhost -p 5432 -U postgres -d ehs_sys
```

在psql中执行：

```sql
-- 查看所有表
\dt

-- 查看企业信息表结构
\d enterprise_info

-- 查看承包商信息表结构
\d contractor_info
```

---

## 企业信息表 (enterprise_info) 使用示例

### 创建企业信息

```sql
-- 创建一个顶级企业
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

### 创建子公司

```sql
-- 假设母公司ID为1，创建子公司
INSERT INTO enterprise_info (
    license_file,
    company_name,
    company_type,
    legal_person,
    establish_date,
    registered_capital,
    applicant_name,
    parent_enterprise_id
) VALUES (
    '/uploads/licenses/enterprise_002.jpg',
    '示例科技（分公司）',
    '有限责任公司',
    '王五',
    '2021-06-20',
    1000.00,
    '赵六',
    1  -- 母公司ID
) RETURNING enterprise_id;
```

### 更新企业信息 - 添加子公司ID

```sql
-- 将子公司ID添加到母公司的subsidiary_ids列表
UPDATE enterprise_info
SET 
    subsidiary_ids = subsidiary_ids || '2'::jsonb,
    modification_log = modification_log || jsonb_build_object(
        'timestamp', CURRENT_TIMESTAMP,
        'operator_id', 1,
        'operator_name', '管理员',
        'operation', 'add_subsidiary',
        'subsidiary_id', 2,
        'subsidiary_name', '示例科技（分公司）',
        'reason', '新增子公司'
    )
WHERE enterprise_id = 1;
```

### 添加允许合作的承包商

```sql
-- 将承包商ID添加到企业的allowed_contractor_ids白名单
UPDATE enterprise_info
SET 
    allowed_contractor_ids = allowed_contractor_ids || '10'::jsonb,
    modification_log = modification_log || jsonb_build_object(
        'timestamp', CURRENT_TIMESTAMP,
        'operator_id', 1,
        'operator_name', '管理员',
        'operation', 'add_contractor',
        'contractor_id', 10,
        'contractor_name', 'XX承包商',
        'reason', '新增合作承包商'
    )
WHERE enterprise_id = 1;
```

### 查询企业信息

```sql
-- 查询所有未删除的企业
SELECT 
    enterprise_id,
    company_name,
    business_status,
    parent_enterprise_id,
    jsonb_array_length(subsidiary_ids) as subsidiary_count,
    jsonb_array_length(allowed_contractor_ids) as contractor_count
FROM enterprise_info
WHERE is_deleted = false
ORDER BY created_at DESC;

-- 查询某个企业的所有子公司
SELECT 
    e2.*
FROM enterprise_info e1
CROSS JOIN jsonb_array_elements_text(e1.subsidiary_ids) AS sub_id
JOIN enterprise_info e2 ON e2.enterprise_id = sub_id::integer
WHERE e1.enterprise_id = 1;

-- 查询企业允许的承包商列表
SELECT 
    c.*
FROM enterprise_info e
CROSS JOIN jsonb_array_elements_text(e.allowed_contractor_ids) AS contractor_id
JOIN contractor_info c ON c.contractor_id = contractor_id::integer
WHERE e.enterprise_id = 1;
```

### 软删除企业

```sql
UPDATE enterprise_info
SET 
    is_deleted = true,
    modification_log = modification_log || jsonb_build_object(
        'timestamp', CURRENT_TIMESTAMP,
        'operator_id', 1,
        'operator_name', '管理员',
        'operation', 'delete',
        'reason', '企业注销'
    )
WHERE enterprise_id = 1;
```

---

## 承包商信息表 (contractor_info) 使用示例

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

### 添加合作企业

```sql
-- 将企业ID添加到承包商的active_enterprise_ids列表
UPDATE contractor_info
SET 
    active_enterprise_ids = active_enterprise_ids || '1'::jsonb,
    cooperation_detail_log = cooperation_detail_log || jsonb_build_object(
        'enterprise_id', 1,
        'enterprise_name', '示例科技有限公司',
        'start_date', '2024-01-01',
        'end_date', null,
        'status', 'active',
        'projects', jsonb_build_array(),
        'contract_amount', 1000000.00,
        'notes', '合作顺利'
    ),
    modification_log = modification_log || jsonb_build_object(
        'timestamp', CURRENT_TIMESTAMP,
        'operator_id', 10,
        'operator_name', '承包商管理员',
        'operation', 'add_enterprise',
        'enterprise_id', 1,
        'enterprise_name', '示例科技有限公司',
        'reason', '新增合作企业'
    )
WHERE contractor_id = 10;
```

### 终止合作关系

```sql
-- 将企业从active_enterprise_ids移到inactive_enterprise_ids
UPDATE contractor_info
SET 
    active_enterprise_ids = active_enterprise_ids - '1',
    inactive_enterprise_ids = inactive_enterprise_ids || '1'::jsonb,
    cooperation_detail_log = jsonb_set(
        cooperation_detail_log,
        '{0,status}',
        '"inactive"'
    ),
    cooperation_detail_log = jsonb_set(
        cooperation_detail_log,
        '{0,end_date}',
        to_jsonb(CURRENT_DATE::text)
    ),
    modification_log = modification_log || jsonb_build_object(
        'timestamp', CURRENT_TIMESTAMP,
        'operator_id', 10,
        'operator_name', '承包商管理员',
        'operation', 'terminate_cooperation',
        'enterprise_id', 1,
        'enterprise_name', '示例科技有限公司',
        'reason', '合同到期'
    )
WHERE contractor_id = 10;
```

### 查询承包商信息

```sql
-- 查询所有未删除的承包商
SELECT 
    contractor_id,
    company_name,
    business_status,
    jsonb_array_length(active_enterprise_ids) as active_enterprise_count,
    jsonb_array_length(inactive_enterprise_ids) as inactive_enterprise_count
FROM contractor_info
WHERE is_deleted = false
ORDER BY created_at DESC;

-- 查询承包商的所有合作企业（活跃）
SELECT 
    e.*
FROM contractor_info c
CROSS JOIN jsonb_array_elements_text(c.active_enterprise_ids) AS ent_id
JOIN enterprise_info e ON e.enterprise_id = ent_id::integer
WHERE c.contractor_id = 10;

-- 查询承包商的合作历史详情
SELECT 
    contractor_id,
    company_name,
    jsonb_pretty(cooperation_detail_log) as cooperation_history
FROM contractor_info
WHERE contractor_id = 10;
```

### 更新营业状态

```sql
UPDATE contractor_info
SET 
    business_status = '注销',
    modification_log = modification_log || jsonb_build_object(
        'timestamp', CURRENT_TIMESTAMP,
        'operator_id', 1,
        'operator_name', '系统管理员',
        'operation', 'update',
        'field', 'business_status',
        'old_value', '续存',
        'new_value', '注销',
        'reason', '公司注销'
    )
WHERE contractor_id = 10;
```

---

## JSONB字段查询技巧

### 查询包含特定ID的记录

```sql
-- 查询允许某个承包商的所有企业
SELECT *
FROM enterprise_info
WHERE allowed_contractor_ids @> '10'::jsonb;

-- 查询与某个企业合作的所有承包商
SELECT *
FROM contractor_info
WHERE active_enterprise_ids @> '1'::jsonb;
```

### 查询数组长度

```sql
-- 查询拥有子公司的企业
SELECT 
    enterprise_id,
    company_name,
    jsonb_array_length(subsidiary_ids) as subsidiary_count
FROM enterprise_info
WHERE jsonb_array_length(subsidiary_ids) > 0;
```

### 查询修改日志

```sql
-- 查询最近的修改记录
SELECT 
    enterprise_id,
    company_name,
    log_entry->>'timestamp' as modify_time,
    log_entry->>'operator_name' as operator,
    log_entry->>'operation' as operation,
    log_entry->>'reason' as reason
FROM enterprise_info,
     jsonb_array_elements(modification_log) as log_entry
ORDER BY log_entry->>'timestamp' DESC
LIMIT 10;
```

### 格式化输出JSONB

```sql
-- 以美化格式显示JSONB字段
SELECT 
    enterprise_id,
    company_name,
    jsonb_pretty(modification_log) as modification_history
FROM enterprise_info
WHERE enterprise_id = 1;
```

---

## Python代码示例

### 使用SQLModel查询

```python
from sqlmodel import select
from db.models import EnterpriseInfo, ContractorInfo

# 查询企业信息
async def get_enterprise_info(session, enterprise_id: int):
    statement = select(EnterpriseInfo).where(
        EnterpriseInfo.enterprise_id == enterprise_id,
        EnterpriseInfo.is_deleted == False
    )
    result = await session.execute(statement)
    return result.scalar_one_or_none()

# 查询企业的子公司
async def get_subsidiaries(session, enterprise_id: int):
    enterprise = await get_enterprise_info(session, enterprise_id)
    if not enterprise or not enterprise.subsidiary_ids:
        return []
    
    statement = select(EnterpriseInfo).where(
        EnterpriseInfo.enterprise_id.in_(enterprise.subsidiary_ids)
    )
    result = await session.execute(statement)
    return result.scalars().all()

# 添加承包商到企业白名单
async def add_contractor_to_whitelist(
    session, 
    enterprise_id: int, 
    contractor_id: int,
    operator_id: int,
    operator_name: str
):
    enterprise = await get_enterprise_info(session, enterprise_id)
    if not enterprise:
        return None
    
    # 添加承包商ID
    if contractor_id not in enterprise.allowed_contractor_ids:
        enterprise.allowed_contractor_ids.append(contractor_id)
    
    # 添加修改日志
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "operator_id": operator_id,
        "operator_name": operator_name,
        "operation": "add_contractor",
        "contractor_id": contractor_id,
        "reason": "新增合作承包商"
    }
    enterprise.modification_log.append(log_entry)
    
    await session.commit()
    await session.refresh(enterprise)
    return enterprise
```

### 使用Pydantic模型

```python
from api.model import EnterpriseInfoCreate, ContractorInfoCreate

# 创建企业信息
enterprise_data = EnterpriseInfoCreate(
    license_file="/uploads/licenses/enterprise_001.jpg",
    company_name="示例科技有限公司",
    company_type="有限责任公司",
    legal_person="张三",
    establish_date="2020-01-15",
    registered_capital=5000.00,
    applicant_name="李四"
)

# 创建承包商信息
contractor_data = ContractorInfoCreate(
    license_file="/uploads/licenses/contractor_001.jpg",
    company_name="优质建筑承包有限公司",
    company_type="有限责任公司",
    legal_person="孙七",
    establish_date="2018-03-10",
    registered_capital=3000.00,
    applicant_name="周八"
)
```

---

## 常见问题

### Q1: 如何备份数据？

```bash
# 备份整个数据库
pg_dump -h localhost -U postgres -d ehs_sys -F c -f ehs_sys_backup.dump

# 只备份特定表
pg_dump -h localhost -U postgres -d ehs_sys -t contractor -F c -f contractor_backup.dump
```

### Q2: 如何恢复数据？

```bash
# 恢复整个数据库
pg_restore -h localhost -U postgres -d ehs_sys ehs_sys_backup.dump

# 恢复特定表
pg_restore -h localhost -U postgres -d ehs_sys -t contractor contractor_backup.dump
```

### Q3: JSONB数组操作慢怎么办？

确保已创建GIN索引：

```sql
CREATE INDEX idx_enterprise_subsidiary_ids ON enterprise_info USING GIN(subsidiary_ids);
CREATE INDEX idx_contractor_active_enterprise_ids ON contractor_info USING GIN(active_enterprise_ids);
```

### Q4: 如何查看表的大小？

```sql
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename IN ('enterprise_info', 'contractor_info')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## 注意事项

1. **JSONB字段默认值**：创建记录时，JSONB数组字段会自动初始化为空数组`[]`
2. **软删除**：使用`is_deleted`字段标记删除，不直接删除记录
3. **修改日志**：所有重要操作都应记录到`modification_log`字段
4. **外键约束**：`parent_enterprise_id`有外键约束，删除母公司会将子公司的该字段设为NULL
5. **时间戳**：`updated_at`字段通过触发器自动更新
6. **数据一致性**：修改关联关系时（如添加子公司），需要同时更新两端的记录

---

**文档版本**: v1.0  
**最后更新**: 2025-11-11  
**维护人员**: EHS系统开发团队

