# EHS系统数据库表结构说明

## 1. users - 用户表

存储所有用户的登录凭证

```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('enterprise', 'contractor', 'admin')),
    enterprise_staff_id INTEGER,
    contractor_staff_id INTEGER,
    phone VARCHAR(20),
    email VARCHAR(100),
    user_level INTEGER,
    audit_status INTEGER,
    temp_token VARCHAR(500),
    sys_only_id BIGINT UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### 字段说明

| 字段名 | 类型 | 说明 |
|--------|------|------|
| user_id | SERIAL | 用户ID，主键 |
| username | VARCHAR(50) | 用户名，唯一 |
| password_hash | VARCHAR(255) | 密码哈希值 |
| user_type | VARCHAR(20) | 用户类型：enterprise/contractor/admin |
| enterprise_staff_id | INTEGER | 关联企业员工ID |
| contractor_staff_id | INTEGER | 关联承包商员工ID |
| phone | VARCHAR(20) | 用户电话 |
| email | VARCHAR(100) | 用户邮箱 |
| user_level | INTEGER | 用户等级 |
| audit_status | INTEGER | 审核状态 |
| temp_token | VARCHAR(500) | 临时token存储值 |
| sys_only_id | BIGINT | 系统唯一标识ID，用于系统中其他表关联查询 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

---

## 2. enterprise_user - 企业用户表

存储企业员工详细信息

```sql
CREATE TABLE enterprise_user (
    user_id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL,
    dept_id INTEGER,
    name_str VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL,
    position VARCHAR(100),
    role_type VARCHAR(100) NOT NULL,
    role_id INTEGER,
    approval_level INTEGER NOT NULL DEFAULT 4,
    status INTEGER NOT NULL DEFAULT 1,
    sys_only_id BIGINT UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### 字段说明

| 字段名 | 类型 | 说明 |
|--------|------|------|
| user_id | SERIAL | 员工ID，主键 |
| company_id | INTEGER | 所属公司ID |
| dept_id | INTEGER | 部门ID |
| name_str | VARCHAR(100) | 姓名 |
| phone | VARCHAR(20) | 电话 |
| email | VARCHAR(100) | 邮箱 |
| position | VARCHAR(100) | 职位 |
| role_type | VARCHAR(100) | 角色类型 |
| role_id | INTEGER | 角色ID，用于绑定用户权限 |
| approval_level | INTEGER | 审批级别，默认4 |
| status | INTEGER | 状态，默认1 |
| sys_only_id | BIGINT | 系统唯一标识ID |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

---

## 3. contractor_user - 承包商用户表

存储承包商员工详细信息

```sql
CREATE TABLE contractor_user (
    user_id SERIAL PRIMARY KEY,
    contractor_id INTEGER NOT NULL,
    name_str VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    id_number VARCHAR(50) NOT NULL,
    work_type VARCHAR(100) NOT NULL,
    role_type VARCHAR(10) NOT NULL DEFAULT 'normal',
    personal_photo VARCHAR(255) NOT NULL,
    status INTEGER NOT NULL DEFAULT 0,
    sys_only_id BIGINT UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### 字段说明

| 字段名 | 类型 | 说明 |
|--------|------|------|
| user_id | SERIAL | 员工ID，主键 |
| contractor_id | INTEGER | 所属承包商ID |
| name_str | VARCHAR(100) | 姓名 |
| phone | VARCHAR(20) | 电话 |
| id_number | VARCHAR(50) | 身份证号 |
| work_type | VARCHAR(100) | 工种 |
| role_type | VARCHAR(10) | 角色类型，默认normal |
| personal_photo | VARCHAR(255) | 个人照片路径 |
| status | INTEGER | 状态，默认0 |
| sys_only_id | BIGINT | 系统唯一标识ID |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

---

## 4. enterprise_info - 企业信息表

存储企业基本信息、组织关系及合作承包商信息

```sql
CREATE TABLE enterprise_info (
    enterprise_id SERIAL PRIMARY KEY,
    license_file VARCHAR(255) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    company_type VARCHAR(100),
    legal_person VARCHAR(100),
    establish_date DATE,
    registered_capital NUMERIC(15, 2),
    applicant_name VARCHAR(100),
    business_status VARCHAR(50) NOT NULL DEFAULT '续存',
    is_deleted BOOLEAN NOT NULL DEFAULT false,
    parent_enterprise_id INTEGER,
    subsidiary_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    allowed_contractor_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    modification_log JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### 字段说明

| 字段名 | 类型 | 说明 |
|--------|------|------|
| enterprise_id | SERIAL | 企业ID，主键 |
| license_file | VARCHAR(255) | 营业执照文件路径 |
| company_name | VARCHAR(255) | 公司名称 |
| company_type | VARCHAR(100) | 公司类型 |
| legal_person | VARCHAR(100) | 法人 |
| establish_date | DATE | 成立日期 |
| registered_capital | NUMERIC(15, 2) | 注册资本 |
| applicant_name | VARCHAR(100) | 申请人姓名 |
| business_status | VARCHAR(50) | 经营状态，默认"续存" |
| is_deleted | BOOLEAN | 是否删除，默认false |
| parent_enterprise_id | INTEGER | 父企业ID |
| subsidiary_ids | JSONB | 子公司ID数组 |
| allowed_contractor_ids | JSONB | 允许合作的承包商ID数组 |
| modification_log | JSONB | 修改日志 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

---

## 5. contractor_info - 承包商信息表

存储承包商基本信息、合作状态及合作企业详情

```sql
CREATE TABLE contractor_info (
    contractor_id SERIAL PRIMARY KEY,
    license_file VARCHAR(255) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    company_type VARCHAR(100),
    legal_person VARCHAR(100),
    establish_date DATE,
    registered_capital NUMERIC(15, 2),
    applicant_name VARCHAR(100),
    business_status VARCHAR(50) NOT NULL DEFAULT '续存',
    is_deleted BOOLEAN NOT NULL DEFAULT false,
    active_enterprise_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    inactive_enterprise_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    cooperation_detail_log JSONB NOT NULL DEFAULT '[]'::jsonb,
    modification_log JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### 字段说明

| 字段名 | 类型 | 说明 |
|--------|------|------|
| contractor_id | SERIAL | 承包商ID，主键 |
| license_file | VARCHAR(255) | 营业执照文件路径 |
| company_name | VARCHAR(255) | 公司名称 |
| company_type | VARCHAR(100) | 公司类型 |
| legal_person | VARCHAR(100) | 法人 |
| establish_date | DATE | 成立日期 |
| registered_capital | NUMERIC(15, 2) | 注册资本 |
| applicant_name | VARCHAR(100) | 申请人姓名 |
| business_status | VARCHAR(50) | 经营状态，默认"续存" |
| is_deleted | BOOLEAN | 是否删除，默认false |
| active_enterprise_ids | JSONB | 活跃合作企业ID数组 |
| inactive_enterprise_ids | JSONB | 非活跃合作企业ID数组 |
| cooperation_detail_log | JSONB | 合作详情日志 |
| modification_log | JSONB | 修改日志 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

---

## 6. contractor_project - 承包商项目表

存储承包商项目信息

```sql
CREATE TABLE contractor_project (
    project_id SERIAL PRIMARY KEY,
    contractor_id INTEGER NOT NULL,
    enterprise_id INTEGER NOT NULL,
    project_name VARCHAR(255) NOT NULL,
    leader_name_str VARCHAR(100) NOT NULL,
    leader_phone VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### 字段说明

| 字段名 | 类型 | 说明 |
|--------|------|------|
| project_id | SERIAL | 项目ID，主键 |
| contractor_id | INTEGER | 承包商ID |
| enterprise_id | INTEGER | 企业ID |
| project_name | VARCHAR(255) | 项目名称 |
| leader_name_str | VARCHAR(100) | 负责人姓名 |
| leader_phone | VARCHAR(20) | 负责人电话 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

---

## 7. ticket - 作业票表

存储作业票信息

```sql
CREATE TABLE ticket (
    ticket_id SERIAL PRIMARY KEY,
    apply_date DATE NOT NULL,
    applicant INTEGER NOT NULL,
    area_id INTEGER,
    working_content VARCHAR(1024) NOT NULL,
    pre_st TIMESTAMP NOT NULL,
    pre_et TIMESTAMP NOT NULL,
    tools INTEGER NOT NULL DEFAULT 0,
    worker INTEGER NOT NULL,
    custodians INTEGER NOT NULL,
    danger INTEGER NOT NULL DEFAULT 0,
    protection INTEGER NOT NULL DEFAULT 0,
    hot_work INTEGER NOT NULL DEFAULT -1,
    work_height_level INTEGER NOT NULL DEFAULT 0,
    confined_space_id INTEGER,
    temp_power_id INTEGER,
    cross_work_group_id VARCHAR(50),
    signature VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### 字段说明

| 字段名 | 类型 | 说明 |
|--------|------|------|
| ticket_id | SERIAL | 作业票ID，主键 |
| apply_date | DATE | 申请日期 |
| applicant | INTEGER | 申请人ID（企业用户） |
| area_id | INTEGER | 作业区域ID |
| working_content | VARCHAR(1024) | 作业内容 |
| pre_st | TIMESTAMP | 预计开始时间 |
| pre_et | TIMESTAMP | 预计结束时间 |
| tools | INTEGER | 工具标识，默认0 |
| worker | INTEGER | 作业人员ID（承包商用户） |
| custodians | INTEGER | 监护人ID（企业用户） |
| danger | INTEGER | 危险标识，默认0 |
| protection | INTEGER | 防护标识，默认0 |
| hot_work | INTEGER | 动火作业标识，默认-1 |
| work_height_level | INTEGER | 高处作业等级，默认0 |
| confined_space_id | INTEGER | 受限空间ID |
| temp_power_id | INTEGER | 临时用电ID |
| cross_work_group_id | VARCHAR(50) | 交叉作业组ID |
| signature | VARCHAR(255) | 签名文件路径 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

---

## 表关系说明

### 外键约束

- `users.enterprise_staff_id` → `enterprise_user.user_id`
- `users.contractor_staff_id` → `contractor_user.user_id`
- `enterprise_info.parent_enterprise_id` → `enterprise_info.enterprise_id`
- `ticket.applicant` → `enterprise_user.user_id`
- `ticket.worker` → `contractor_user.user_id`
- `ticket.custodians` → `enterprise_user.user_id`

### 索引

**users表:**
- `idx_users_username` (username)
- `idx_users_user_type` (user_type)

**enterprise_info表:**
- `idx_enterprise_company_name` (company_name)
- `idx_enterprise_business_status` (business_status)
- `idx_enterprise_is_deleted` (is_deleted)
- `idx_enterprise_parent_id` (parent_enterprise_id)
- `idx_enterprise_subsidiary_ids` (subsidiary_ids) - GIN索引
- `idx_enterprise_allowed_contractor_ids` (allowed_contractor_ids) - GIN索引

**contractor_info表:**
- `idx_contractor_info_company_name` (company_name)
- `idx_contractor_info_business_status` (business_status)
- `idx_contractor_info_is_deleted` (is_deleted)
- `idx_contractor_info_active_enterprise_ids` (active_enterprise_ids) - GIN索引
- `idx_contractor_info_inactive_enterprise_ids` (inactive_enterprise_ids) - GIN索引

**contractor_project表:**
- `idx_contractor_project_contractor_id` (contractor_id)
- `idx_contractor_project_enterprise_id` (enterprise_id)

**ticket表:**
- `idx_ticket_apply_date` (apply_date)
- `idx_ticket_applicant` (applicant)
- `idx_ticket_worker` (worker)

### 触发器

- `trigger_update_enterprise_info_updated_at` - 自动更新enterprise_info表的updated_at字段
- `trigger_update_contractor_info_updated_at` - 自动更新contractor_info表的updated_at字段

---

**最后更新时间**: 2025-11-11

