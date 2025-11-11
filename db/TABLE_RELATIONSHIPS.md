# 企业信息表和承包商信息表关系图

## 表关系概览

```
┌─────────────────────────────────────────────────────────────────┐
│                    EHS系统核心表关系图                           │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│  enterprise_info     │  企业信息表（新）
├──────────────────────┤
│ PK enterprise_id     │
│    license_file      │  营业执照
│    company_name      │  企业名称
│    company_type      │  企业类型
│    legal_person      │  法定代表人
│    establish_date    │  成立日期
│    registered_capital│  注册资本
│    applicant_name    │  申请人
│    business_status   │  营业状态
│    is_deleted        │  软删除标记
│ FK parent_enterprise_id │ ──┐ 自引用：上级公司
│    subsidiary_ids    │  JSONB: [子公司ID列表]
│    allowed_contractor_ids │ JSONB: [允许的承包商ID]
│    modification_log  │  JSONB: 修改记录
│    created_at        │
│    updated_at        │
└──────────────────────┘
         │
         └──────┐ 自引用关系
                ↓
         ┌──────────────┐
         │ 支持企业层级  │
         │ 母公司-子公司 │
         └──────────────┘


┌──────────────────────┐
│  contractor_info     │  承包商信息表（新）
├──────────────────────┤
│ PK contractor_id     │
│    license_file      │  营业执照
│    company_name      │  承包商名称
│    company_type      │  公司类型
│    legal_person      │  法定代表人
│    establish_date    │  成立日期
│    registered_capital│  注册资本
│    applicant_name    │  申请人
│    business_status   │  营业状态
│    is_deleted        │  软删除标记
│    active_enterprise_ids │ JSONB: [合作中的企业ID]
│    inactive_enterprise_ids │ JSONB: [已失效企业ID]
│    cooperation_detail_log │ JSONB: 合作详情
│    modification_log  │  JSONB: 修改记录
│    created_at        │
│    updated_at        │
└──────────────────────┘


┌──────────────────────┐
│  contractor          │  承包商表（旧，保持兼容）
├──────────────────────┤
│ PK contractor_id     │
│    license_file      │
│    company_name      │
│    company_type      │
│    legal_person      │
│    establish_date    │
│    registered_capital│
│    applicant_name    │
│    created_at        │
│    updated_at        │
└──────────────────────┘
         │
         │ FK
         ↓
┌──────────────────────┐
│ contractor_project   │  承包商项目表
├──────────────────────┤
│ PK project_id        │
│ FK contractor_id     │
│ FK enterprise_id     │
│    project_name      │
│    leader_name       │
│    leader_phone      │
└──────────────────────┘
         │
         │ FK
         ↓
┌──────────────────────┐
│  entry_plan          │  进场计划表
├──────────────────────┤
│ PK plan_id           │
│ FK project_id        │
│    plan_date         │
│    status            │
└──────────────────────┘
```

---

## 企业层级关系示例

```
企业A (enterprise_id: 1)
├── parent_enterprise_id: NULL (顶级企业)
├── subsidiary_ids: [2, 3, 4]
└── allowed_contractor_ids: [10, 20]

    ├─→ 企业B (enterprise_id: 2)
    │   ├── parent_enterprise_id: 1
    │   ├── subsidiary_ids: [5]
    │   └── allowed_contractor_ids: [10]
    │
    │       └─→ 企业E (enterprise_id: 5)
    │           ├── parent_enterprise_id: 2
    │           ├── subsidiary_ids: []
    │           └── allowed_contractor_ids: [10, 30]
    │
    ├─→ 企业C (enterprise_id: 3)
    │   ├── parent_enterprise_id: 1
    │   ├── subsidiary_ids: []
    │   └── allowed_contractor_ids: [20]
    │
    └─→ 企业D (enterprise_id: 4)
        ├── parent_enterprise_id: 1
        ├── subsidiary_ids: []
        └── allowed_contractor_ids: [10, 20, 30]
```

---

## 承包商合作关系示例

```
承包商X (contractor_id: 10)
├── active_enterprise_ids: [1, 2, 5]
├── inactive_enterprise_ids: [6, 7]
└── cooperation_detail_log: [
    {
        enterprise_id: 1,
        enterprise_name: "企业A",
        status: "active",
        start_date: "2024-01-01",
        end_date: null,
        projects: [
            {project_id: 100, project_name: "项目1"},
            {project_id: 101, project_name: "项目2"}
        ],
        contract_amount: 1000000.00
    },
    {
        enterprise_id: 6,
        enterprise_name: "企业F",
        status: "inactive",
        start_date: "2023-01-01",
        end_date: "2023-12-31",
        projects: [...],
        termination_reason: "合同到期"
    }
]
```

---

## 企业-承包商白名单关系

```
┌─────────────┐                    ┌──────────────┐
│  企业A      │                    │  承包商X     │
│ allowed:    │◄──────────────────►│ active:      │
│ [10, 20]    │   双向关系验证      │ [1, 2, 5]    │
└─────────────┘                    └──────────────┘
      │                                    │
      │ 白名单包含承包商X(10)              │ 合作企业包含企业A(1)
      │                                    │
      └────────────┬───────────────────────┘
                   │
                   ↓
            ┌─────────────┐
            │  允许合作    │
            └─────────────┘

验证逻辑：
1. 企业A的allowed_contractor_ids包含10
2. 承包商X的active_enterprise_ids包含1
3. 双向验证通过，允许合作
```

---

## 数据流转图

### 新增企业流程

```
1. 创建企业信息
   ↓
2. 插入enterprise_info表
   ↓
3. 如果有母公司，更新母公司的subsidiary_ids
   ↓
4. 记录modification_log
   ↓
5. 返回enterprise_id
```

### 新增承包商流程

```
1. 创建承包商信息
   ↓
2. 插入contractor_info表
   ↓
3. 记录modification_log
   ↓
4. 返回contractor_id
```

### 建立合作关系流程

```
1. 企业添加承包商到白名单
   ↓
2. 更新enterprise_info.allowed_contractor_ids
   ↓
3. 承包商添加企业到合作列表
   ↓
4. 更新contractor_info.active_enterprise_ids
   ↓
5. 更新contractor_info.cooperation_detail_log
   ↓
6. 双方记录modification_log
```

### 终止合作关系流程

```
1. 从企业白名单移除承包商
   ↓
2. 更新enterprise_info.allowed_contractor_ids
   ↓
3. 承包商将企业从active移到inactive
   ↓
4. 更新contractor_info.active_enterprise_ids
5. 更新contractor_info.inactive_enterprise_ids
   ↓
6. 更新cooperation_detail_log中的状态和结束日期
   ↓
7. 双方记录modification_log
```

---

## JSONB字段关系图

### enterprise_info表的JSONB字段

```
enterprise_info
│
├── subsidiary_ids: JSONB Array
│   └── [2, 3, 4] ──→ 指向其他enterprise_info记录
│
├── allowed_contractor_ids: JSONB Array
│   └── [10, 20] ──→ 指向contractor_info记录
│
└── modification_log: JSONB Array of Objects
    └── [
        {
            timestamp: "2025-11-11T10:30:00",
            operator_id: 1,
            operation: "add_contractor",
            ...
        },
        ...
    ]
```

### contractor_info表的JSONB字段

```
contractor_info
│
├── active_enterprise_ids: JSONB Array
│   └── [1, 2, 5] ──→ 指向enterprise_info记录
│
├── inactive_enterprise_ids: JSONB Array
│   └── [6, 7] ──→ 指向enterprise_info记录
│
├── cooperation_detail_log: JSONB Array of Objects
│   └── [
│       {
│           enterprise_id: 1,
│           enterprise_name: "企业A",
│           status: "active",
│           projects: [
│               {project_id: 100, ...},
│               ...
│           ],
│           ...
│       },
│       ...
│   ]
│
└── modification_log: JSONB Array of Objects
    └── [...]
```

---

## 索引策略

### enterprise_info表索引

```
1. PRIMARY KEY (enterprise_id)
   - 主键索引，自动创建

2. idx_enterprise_company_name (company_name)
   - B-Tree索引
   - 用于：按公司名称查询

3. idx_enterprise_business_status (business_status)
   - B-Tree索引
   - 用于：按营业状态筛选

4. idx_enterprise_is_deleted (is_deleted)
   - B-Tree索引
   - 用于：过滤已删除记录

5. idx_enterprise_parent_id (parent_enterprise_id)
   - B-Tree索引
   - 用于：查询子公司

6. idx_enterprise_subsidiary_ids (subsidiary_ids) USING GIN
   - GIN索引
   - 用于：JSONB数组查询（包含特定子公司）

7. idx_enterprise_allowed_contractor_ids (allowed_contractor_ids) USING GIN
   - GIN索引
   - 用于：JSONB数组查询（白名单查询）
```

### contractor_info表索引

```
1. PRIMARY KEY (contractor_id)
   - 主键索引，自动创建

2. idx_contractor_company_name (company_name)
   - B-Tree索引
   - 用于：按公司名称查询

3. idx_contractor_business_status (business_status)
   - B-Tree索引
   - 用于：按营业状态筛选

4. idx_contractor_is_deleted (is_deleted)
   - B-Tree索引
   - 用于：过滤已删除记录

5. idx_contractor_active_enterprise_ids (active_enterprise_ids) USING GIN
   - GIN索引
   - 用于：JSONB数组查询（查找合作企业）

6. idx_contractor_inactive_enterprise_ids (inactive_enterprise_ids) USING GIN
   - GIN索引
   - 用于：JSONB数组查询（查找历史合作企业）
```

---

## 触发器说明

### enterprise_info表触发器

```sql
CREATE TRIGGER trigger_update_enterprise_info_updated_at
    BEFORE UPDATE ON enterprise_info
    FOR EACH ROW
    EXECUTE FUNCTION update_enterprise_info_updated_at();
```

**功能**：自动更新`updated_at`字段为当前时间

**触发时机**：每次UPDATE操作之前

### contractor_info表触发器

```sql
CREATE TRIGGER trigger_update_contractor_info_updated_at
    BEFORE UPDATE ON contractor_info
    FOR EACH ROW
    EXECUTE FUNCTION update_contractor_info_updated_at();
```

**功能**：自动更新`updated_at`字段为当前时间

**触发时机**：每次UPDATE操作之前

---

## 查询性能优化建议

### 1. 企业层级查询优化

```sql
-- 使用递归CTE查询整个企业树
WITH RECURSIVE enterprise_tree AS (
    -- 基础查询：顶级企业
    SELECT 
        enterprise_id,
        company_name,
        parent_enterprise_id,
        1 as level
    FROM enterprise_info
    WHERE parent_enterprise_id IS NULL
    
    UNION ALL
    
    -- 递归查询：子公司
    SELECT 
        e.enterprise_id,
        e.company_name,
        e.parent_enterprise_id,
        et.level + 1
    FROM enterprise_info e
    INNER JOIN enterprise_tree et ON e.parent_enterprise_id = et.enterprise_id
)
SELECT * FROM enterprise_tree ORDER BY level, company_name;
```

### 2. 承包商合作关系查询优化

```sql
-- 使用GIN索引快速查询
SELECT c.*
FROM contractor_info c
WHERE c.active_enterprise_ids @> '1'::jsonb
  AND c.is_deleted = false;
```

### 3. 白名单验证查询优化

```sql
-- 验证企业是否允许承包商合作
SELECT 
    e.enterprise_id,
    e.company_name,
    c.contractor_id,
    c.company_name as contractor_name,
    CASE 
        WHEN e.allowed_contractor_ids @> to_jsonb(c.contractor_id)
         AND c.active_enterprise_ids @> to_jsonb(e.enterprise_id)
        THEN '允许合作'
        ELSE '不允许合作'
    END as cooperation_status
FROM enterprise_info e
CROSS JOIN contractor_info c
WHERE e.enterprise_id = 1 AND c.contractor_id = 10;
```

---

## 数据一致性维护

### 双向关系一致性

当建立企业-承包商合作关系时，需要同时更新：

1. **enterprise_info.allowed_contractor_ids** ← 添加contractor_id
2. **contractor_info.active_enterprise_ids** ← 添加enterprise_id
3. **contractor_info.cooperation_detail_log** ← 添加合作详情
4. 双方的 **modification_log** ← 记录操作

### 层级关系一致性

当建立企业层级关系时，需要同时更新：

1. **子公司.parent_enterprise_id** ← 设置为母公司ID
2. **母公司.subsidiary_ids** ← 添加子公司ID
3. 双方的 **modification_log** ← 记录操作

---

## 注意事项

1. **JSONB数组操作**：使用`||`操作符添加元素，使用`-`操作符删除元素
2. **GIN索引**：JSONB字段必须使用GIN索引才能高效查询
3. **软删除**：使用`is_deleted`标记，不直接DELETE记录
4. **外键约束**：`parent_enterprise_id`有外键约束，注意级联操作
5. **事务处理**：修改关联关系时使用事务保证一致性
6. **日志记录**：所有重要操作都应记录到`modification_log`

---

**文档版本**: v1.0  
**最后更新**: 2025-11-11  
**维护人员**: EHS系统开发团队

