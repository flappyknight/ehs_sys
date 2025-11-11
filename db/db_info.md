# EHS系统数据库表结构文档

## 目录

1. [企业信息表 (enterprise_info)](#1-企业信息表-enterprise_info)
2. [承包商信息表 (contractor_info)](#2-承包商信息表-contractor_info)
3. [用户表 (users)](#3-用户表-users)
4. [公司表 (company)](#4-公司表-company)
5. [企业用户表 (enterprise_user)](#5-企业用户表-enterprise_user)
6. [承包商用户表 (contractor_user)](#6-承包商用户表-contractor_user)
7. [部门表 (department)](#7-部门表-department)
8. [承包商项目表 (contractor_project)](#8-承包商项目表-contractor_project)
9. [进场计划表 (entry_plan)](#9-进场计划表-entry_plan)
10. [进场计划人员表 (entry_plan_user)](#10-进场计划人员表-entry_plan_user)
11. [进场登记表 (entry_register)](#11-进场登记表-entry_register)
12. [区域表 (area)](#12-区域表-area)
13. [作业票表 (ticket)](#13-作业票表-ticket)
14. [作业设备表 (work_equipment)](#14-作业设备表-work_equipment)
15. [受限空间表 (confined_space)](#15-受限空间表-confined_space)
16. [临时用电表 (temporary_power)](#16-临时用电表-temporary_power)
17. [交叉作业表 (cross_work)](#17-交叉作业表-cross_work)

---

## 数据库重建说明

由于企业信息表和承包商信息表结构发生重大变更，需要先删除旧表再创建新表。

### 删除旧表SQL语句

```sql
-- 删除旧的承包商表（已废弃）
DROP TABLE IF EXISTS contractor CASCADE;

-- 如果之前存在旧版本的企业信息表和承包商信息表，也需要删除
-- DROP TABLE IF EXISTS enterprise_info CASCADE;
-- DROP TABLE IF EXISTS contractor_info CASCADE;
```

---

## 1. 企业信息表 (enterprise_info)

### 表说明

存储企业的基本信息、组织关系及合作承包商信息。支持企业层级关系（母公司-子公司）和承包商白名单管理。

### 字段说明

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|---------|------|--------|------|
| enterprise_id | INTEGER | PRIMARY KEY | AUTO | 企业唯一标识（主键） |
| license_file | VARCHAR(255) | NOT NULL | - | 营业执照文件路径 |
| company_name | VARCHAR(255) | NOT NULL | - | 企业名称 |
| company_type | VARCHAR(100) | NULL | - | 企业类型（如：有限责任公司、股份有限公司等） |
| legal_person | VARCHAR(100) | NULL | - | 法定代表人姓名 |
| establish_date | DATE | NULL | - | 成立日期 |
| registered_capital | NUMERIC | NULL | - | 注册资本（单位：万元） |
| applicant_name | VARCHAR(100) | NULL | - | 申请人姓名 |
| business_status | VARCHAR(50) | NOT NULL | '续存' | 营业状态（续存/注销/吊销等） |
| is_deleted | BOOLEAN | NOT NULL | false | 是否已删除（软删除标记） |
| parent_enterprise_id | INTEGER | NULL | - | 上级公司ID（母公司ID，NULL表示顶级公司） |
| subsidiary_ids | JSONB | NOT NULL | [] | 下级公司ID列表（子公司ID数组） |
| allowed_contractor_ids | JSONB | NOT NULL | [] | 允许合作的承包商ID列表（白名单） |
| modification_log | JSONB | NOT NULL | [] | 修改记录日志（记录所有变更历史） |
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL | NOW() | 最后修改时间 |

### 创建表SQL语句

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
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_parent_enterprise FOREIGN KEY (parent_enterprise_id) 
        REFERENCES enterprise_info(enterprise_id) ON DELETE SET NULL
);

-- 创建索引
CREATE INDEX idx_enterprise_company_name ON enterprise_info(company_name);
CREATE INDEX idx_enterprise_business_status ON enterprise_info(business_status);
CREATE INDEX idx_enterprise_is_deleted ON enterprise_info(is_deleted);
CREATE INDEX idx_enterprise_parent_id ON enterprise_info(parent_enterprise_id);
CREATE INDEX idx_enterprise_subsidiary_ids ON enterprise_info USING GIN(subsidiary_ids);
CREATE INDEX idx_enterprise_allowed_contractor_ids ON enterprise_info USING GIN(allowed_contractor_ids);

-- 创建更新时间触发器
CREATE OR REPLACE FUNCTION update_enterprise_info_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_enterprise_info_updated_at
    BEFORE UPDATE ON enterprise_info
    FOR EACH ROW
    EXECUTE FUNCTION update_enterprise_info_updated_at();

-- 添加表注释
COMMENT ON TABLE enterprise_info IS '企业信息表 - 存储企业基本信息、组织关系及合作承包商信息';
COMMENT ON COLUMN enterprise_info.enterprise_id IS '企业唯一标识';
COMMENT ON COLUMN enterprise_info.license_file IS '营业执照文件路径';
COMMENT ON COLUMN enterprise_info.company_name IS '企业名称';
COMMENT ON COLUMN enterprise_info.company_type IS '企业类型';
COMMENT ON COLUMN enterprise_info.legal_person IS '法定代表人';
COMMENT ON COLUMN enterprise_info.establish_date IS '成立日期';
COMMENT ON COLUMN enterprise_info.registered_capital IS '注册资本（万元）';
COMMENT ON COLUMN enterprise_info.applicant_name IS '申请人姓名';
COMMENT ON COLUMN enterprise_info.business_status IS '营业状态（续存/注销/吊销等）';
COMMENT ON COLUMN enterprise_info.is_deleted IS '是否已删除（软删除标记）';
COMMENT ON COLUMN enterprise_info.parent_enterprise_id IS '上级公司ID（母公司）';
COMMENT ON COLUMN enterprise_info.subsidiary_ids IS '下级公司ID列表（子公司数组）';
COMMENT ON COLUMN enterprise_info.allowed_contractor_ids IS '允许合作的承包商ID列表';
COMMENT ON COLUMN enterprise_info.modification_log IS '修改记录日志';
COMMENT ON COLUMN enterprise_info.created_at IS '创建时间';
COMMENT ON COLUMN enterprise_info.updated_at IS '最后修改时间';
```

### JSONB字段结构说明

#### subsidiary_ids 字段结构

```json
[
    123,
    456,
    789
]
```

#### allowed_contractor_ids 字段结构

```json
[
    10,
    20,
    30
]
```

#### modification_log 字段结构

```json
[
    {
        "timestamp": "2025-11-11T10:30:00",
        "operator_id": 1,
        "operator_name": "张三",
        "operation": "update",
        "field": "company_name",
        "old_value": "旧公司名称",
        "new_value": "新公司名称",
        "reason": "公司更名"
    },
    {
        "timestamp": "2025-11-10T15:20:00",
        "operator_id": 2,
        "operator_name": "李四",
        "operation": "add_contractor",
        "contractor_id": 10,
        "contractor_name": "XX承包商",
        "reason": "新增合作承包商"
    }
]
```

---

## 2. 承包商信息表 (contractor_info)

### 表说明

存储承包商的基本信息、合作状态及合作企业详情。支持承包商与多个企业的合作关系管理。

### 字段说明

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|---------|------|--------|------|
| contractor_id | INTEGER | PRIMARY KEY | AUTO | 承包商唯一标识（主键） |
| license_file | VARCHAR(255) | NOT NULL | - | 营业执照文件路径 |
| company_name | VARCHAR(255) | NOT NULL | - | 承包商公司名称 |
| company_type | VARCHAR(100) | NULL | - | 公司类型 |
| legal_person | VARCHAR(100) | NULL | - | 法定代表人姓名 |
| establish_date | DATE | NULL | - | 成立日期 |
| registered_capital | NUMERIC | NULL | - | 注册资本（单位：万元） |
| applicant_name | VARCHAR(100) | NULL | - | 申请人姓名 |
| business_status | VARCHAR(50) | NOT NULL | '续存' | 营业状态（续存/注销/吊销等） |
| is_deleted | BOOLEAN | NOT NULL | false | 是否已删除（软删除标记） |
| active_enterprise_ids | JSONB | NOT NULL | [] | 合作状态企业ID列表（当前正在合作的企业） |
| inactive_enterprise_ids | JSONB | NOT NULL | [] | 已失效合作企业ID列表（曾经合作但已终止） |
| cooperation_detail_log | JSONB | NOT NULL | [] | 合作企业详情日志（记录合作历史） |
| modification_log | JSONB | NOT NULL | [] | 修改记录日志（记录所有变更历史） |
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL | NOW() | 最后修改时间 |

### 创建表SQL语句

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

-- 创建索引
CREATE INDEX idx_contractor_company_name ON contractor_info(company_name);
CREATE INDEX idx_contractor_business_status ON contractor_info(business_status);
CREATE INDEX idx_contractor_is_deleted ON contractor_info(is_deleted);
CREATE INDEX idx_contractor_active_enterprise_ids ON contractor_info USING GIN(active_enterprise_ids);
CREATE INDEX idx_contractor_inactive_enterprise_ids ON contractor_info USING GIN(inactive_enterprise_ids);

-- 创建更新时间触发器
CREATE OR REPLACE FUNCTION update_contractor_info_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_contractor_info_updated_at
    BEFORE UPDATE ON contractor_info
    FOR EACH ROW
    EXECUTE FUNCTION update_contractor_info_updated_at();

-- 添加表注释
COMMENT ON TABLE contractor_info IS '承包商信息表 - 存储承包商基本信息、合作状态及合作企业详情';
COMMENT ON COLUMN contractor_info.contractor_id IS '承包商唯一标识';
COMMENT ON COLUMN contractor_info.license_file IS '营业执照文件路径';
COMMENT ON COLUMN contractor_info.company_name IS '承包商公司名称';
COMMENT ON COLUMN contractor_info.company_type IS '公司类型';
COMMENT ON COLUMN contractor_info.legal_person IS '法定代表人';
COMMENT ON COLUMN contractor_info.establish_date IS '成立日期';
COMMENT ON COLUMN contractor_info.registered_capital IS '注册资本（万元）';
COMMENT ON COLUMN contractor_info.applicant_name IS '申请人姓名';
COMMENT ON COLUMN contractor_info.business_status IS '营业状态';
COMMENT ON COLUMN contractor_info.is_deleted IS '是否已删除（软删除标记）';
COMMENT ON COLUMN contractor_info.active_enterprise_ids IS '合作状态企业ID列表';
COMMENT ON COLUMN contractor_info.inactive_enterprise_ids IS '已失效合作企业ID列表';
COMMENT ON COLUMN contractor_info.cooperation_detail_log IS '合作企业详情日志';
COMMENT ON COLUMN contractor_info.modification_log IS '修改记录日志';
COMMENT ON COLUMN contractor_info.created_at IS '创建时间';
COMMENT ON COLUMN contractor_info.updated_at IS '最后修改时间';
```

### JSONB字段结构说明

#### active_enterprise_ids 字段结构

```json
[
    1,
    5,
    10
]
```

#### inactive_enterprise_ids 字段结构

```json
[
    2,
    3,
    7
]
```

#### cooperation_detail_log 字段结构

```json
[
    {
        "enterprise_id": 1,
        "enterprise_name": "XX企业",
        "start_date": "2024-01-01",
        "end_date": null,
        "status": "active",
        "projects": [
            {
                "project_id": 100,
                "project_name": "XX项目",
                "start_date": "2024-01-15",
                "end_date": "2024-12-31"
            }
        ],
        "contract_amount": 1000000.00,
        "notes": "合作顺利"
    },
    {
        "enterprise_id": 2,
        "enterprise_name": "YY企业",
        "start_date": "2023-06-01",
        "end_date": "2024-05-31",
        "status": "inactive",
        "projects": [
            {
                "project_id": 50,
                "project_name": "YY项目",
                "start_date": "2023-06-01",
                "end_date": "2024-05-31"
            }
        ],
        "contract_amount": 500000.00,
        "termination_reason": "合同到期",
        "notes": "合作愉快"
    }
]
```

#### modification_log 字段结构

```json
[
    {
        "timestamp": "2025-11-11T14:20:00",
        "operator_id": 5,
        "operator_name": "王五",
        "operation": "update",
        "field": "business_status",
        "old_value": "续存",
        "new_value": "注销",
        "reason": "公司注销"
    },
    {
        "timestamp": "2025-11-10T09:15:00",
        "operator_id": 3,
        "operator_name": "赵六",
        "operation": "add_enterprise",
        "enterprise_id": 1,
        "enterprise_name": "XX企业",
        "reason": "新增合作企业"
    }
]
```

---

## 3. 用户表 (users)

### 表说明

系统用户主表，存储所有用户的登录凭证和基本信息。通过外键关联到企业用户或承包商用户详细信息。

### 字段说明

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|---------|------|--------|------|
| user_id | INTEGER | PRIMARY KEY | AUTO | 用户唯一标识 |
| username | VARCHAR(50) | UNIQUE, NOT NULL | - | 用户名（登录账号） |
| password_hash | VARCHAR(255) | NOT NULL | - | 密码哈希值 |
| user_type | VARCHAR(20) | NOT NULL | - | 用户类型（enterprise/contractor/admin） |
| enterprise_staff_id | INTEGER | FK, NULL | - | 企业员工ID（外键关联enterprise_user） |
| contractor_staff_id | INTEGER | FK, NULL | - | 承包商员工ID（外键关联contractor_user） |
| created_at | TIMESTAMP | NOT NULL | NOW() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL | NOW() | 最后修改时间 |

### 创建表SQL语句

```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('enterprise', 'contractor', 'admin')),
    enterprise_staff_id INTEGER,
    contractor_staff_id INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_enterprise_staff FOREIGN KEY (enterprise_staff_id) 
        REFERENCES enterprise_user(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_contractor_staff FOREIGN KEY (contractor_staff_id) 
        REFERENCES contractor_user(user_id) ON DELETE SET NULL
);

-- 创建索引
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_user_type ON users(user_type);
CREATE INDEX idx_users_enterprise_staff_id ON users(enterprise_staff_id);
CREATE INDEX idx_users_contractor_staff_id ON users(contractor_staff_id);

-- 添加表注释
COMMENT ON TABLE users IS '系统用户主表';
COMMENT ON COLUMN users.user_type IS '用户类型：enterprise-企业用户, contractor-承包商用户, admin-管理员';
```

---

## 4. 公司表 (company)

### 表说明

公司基本信息表，用于存储企业和承包商的基本公司信息。

### 创建表SQL语句

```sql
CREATE TABLE company (
    company_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('enterprise', 'contractor')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_company_name ON company(name);
CREATE INDEX idx_company_type ON company(type);

-- 添加表注释
COMMENT ON TABLE company IS '公司基本信息表';
COMMENT ON COLUMN company.type IS '公司类型：enterprise-企业, contractor-承包商';
```

---

## 5. 企业用户表 (enterprise_user)

### 表说明

企业员工详细信息表，存储企业员工的个人信息、职位、部门等。

### 创建表SQL语句

```sql
CREATE TABLE enterprise_user (
    user_id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL,
    dept_id INTEGER,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL,
    position VARCHAR(100),
    role_type VARCHAR(100) NOT NULL,
    approval_level INTEGER NOT NULL DEFAULT 4,
    status BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_enterprise_company FOREIGN KEY (company_id) 
        REFERENCES company(company_id) ON DELETE CASCADE,
    CONSTRAINT fk_enterprise_dept FOREIGN KEY (dept_id) 
        REFERENCES department(dept_id) ON DELETE SET NULL
);

-- 创建索引
CREATE INDEX idx_enterprise_user_company_id ON enterprise_user(company_id);
CREATE INDEX idx_enterprise_user_dept_id ON enterprise_user(dept_id);
CREATE INDEX idx_enterprise_user_phone ON enterprise_user(phone);
CREATE INDEX idx_enterprise_user_status ON enterprise_user(status);

-- 添加表注释
COMMENT ON TABLE enterprise_user IS '企业用户详细信息表';
COMMENT ON COLUMN enterprise_user.approval_level IS '审批级别（1-4级）';
COMMENT ON COLUMN enterprise_user.status IS '用户状态（true-启用, false-禁用）';
```

---

## 6. 承包商用户表 (contractor_user)

### 表说明

承包商员工详细信息表，存储承包商员工的个人信息、工种、证件等。

### 创建表SQL语句

```sql
CREATE TABLE contractor_user (
    user_id SERIAL PRIMARY KEY,
    contractor_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    id_number VARCHAR(50) NOT NULL,
    work_type VARCHAR(100) NOT NULL,
    role_type VARCHAR(10) NOT NULL DEFAULT 'normal',
    personal_photo VARCHAR(255) NOT NULL,
    status BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_contractor FOREIGN KEY (contractor_id) 
        REFERENCES contractor(contractor_id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX idx_contractor_user_contractor_id ON contractor_user(contractor_id);
CREATE INDEX idx_contractor_user_phone ON contractor_user(phone);
CREATE INDEX idx_contractor_user_id_number ON contractor_user(id_number);
CREATE INDEX idx_contractor_user_status ON contractor_user(status);

-- 添加表注释
COMMENT ON TABLE contractor_user IS '承包商用户详细信息表';
COMMENT ON COLUMN contractor_user.work_type IS '工种类型';
COMMENT ON COLUMN contractor_user.role_type IS '角色类型（normal-普通员工, leader-负责人）';
```

---

## 7. 部门表 (department)

### 表说明

部门组织结构表，支持树形层级结构。

### 创建表SQL语句

```sql
CREATE TABLE department (
    dept_id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    parent_id INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_dept_company FOREIGN KEY (company_id) 
        REFERENCES company(company_id) ON DELETE CASCADE,
    CONSTRAINT fk_dept_parent FOREIGN KEY (parent_id) 
        REFERENCES department(dept_id) ON DELETE SET NULL
);

-- 创建索引
CREATE INDEX idx_department_company_id ON department(company_id);
CREATE INDEX idx_department_parent_id ON department(parent_id);

-- 添加表注释
COMMENT ON TABLE department IS '部门组织结构表';
COMMENT ON COLUMN department.parent_id IS '上级部门ID（NULL表示顶级部门）';
```

---

## 8. 承包商项目表 (contractor_project)

### 创建表SQL语句

```sql
CREATE TABLE contractor_project (
    project_id SERIAL PRIMARY KEY,
    contractor_id INTEGER NOT NULL,
    enterprise_id INTEGER NOT NULL,
    project_name VARCHAR(255) NOT NULL,
    leader_name VARCHAR(100) NOT NULL,
    leader_phone VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_project_contractor FOREIGN KEY (contractor_id) 
        REFERENCES contractor(contractor_id) ON DELETE CASCADE,
    CONSTRAINT fk_project_enterprise FOREIGN KEY (enterprise_id) 
        REFERENCES company(company_id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX idx_contractor_project_contractor_id ON contractor_project(contractor_id);
CREATE INDEX idx_contractor_project_enterprise_id ON contractor_project(enterprise_id);

COMMENT ON TABLE contractor_project IS '承包商项目表';
```

---

## 9. 进场计划表 (entry_plan)

### 创建表SQL语句

```sql
CREATE TABLE entry_plan (
    plan_id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    plan_date DATE NOT NULL,
    status INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_plan_project FOREIGN KEY (project_id) 
        REFERENCES contractor_project(project_id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX idx_entry_plan_project_id ON entry_plan(project_id);
CREATE INDEX idx_entry_plan_plan_date ON entry_plan(plan_date);
CREATE INDEX idx_entry_plan_status ON entry_plan(status);

COMMENT ON TABLE entry_plan IS '进场计划表';
COMMENT ON COLUMN entry_plan.status IS '计划状态（0-待执行, 1-执行中, 2-已完成）';
```

---

## 10. 进场计划人员表 (entry_plan_user)

### 创建表SQL语句

```sql
CREATE TABLE entry_plan_user (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    plan_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_plan_user_project FOREIGN KEY (project_id) 
        REFERENCES contractor_project(project_id) ON DELETE CASCADE,
    CONSTRAINT fk_plan_user_plan FOREIGN KEY (plan_id) 
        REFERENCES entry_plan(plan_id) ON DELETE CASCADE,
    CONSTRAINT fk_plan_user_user FOREIGN KEY (user_id) 
        REFERENCES contractor_user(user_id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX idx_entry_plan_user_plan_id ON entry_plan_user(plan_id);
CREATE INDEX idx_entry_plan_user_user_id ON entry_plan_user(user_id);

COMMENT ON TABLE entry_plan_user IS '进场计划人员表';
```

---

## 11. 进场登记表 (entry_register)

### 创建表SQL语句

```sql
CREATE TABLE entry_register (
    register_id SERIAL PRIMARY KEY,
    plan_user_id INTEGER NOT NULL,
    actual_time TIMESTAMP NOT NULL,
    photo_path VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_register_plan_user FOREIGN KEY (plan_user_id) 
        REFERENCES entry_plan_user(id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX idx_entry_register_plan_user_id ON entry_register(plan_user_id);
CREATE INDEX idx_entry_register_actual_time ON entry_register(actual_time);

COMMENT ON TABLE entry_register IS '进场登记表';
```

---

## 12. 区域表 (area)

### 创建表SQL语句

```sql
CREATE TABLE area (
    area_id SERIAL PRIMARY KEY,
    enterprise_id INTEGER NOT NULL,
    area_name VARCHAR(64) NOT NULL,
    dept_id INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_area_enterprise FOREIGN KEY (enterprise_id) 
        REFERENCES company(company_id) ON DELETE CASCADE,
    CONSTRAINT fk_area_dept FOREIGN KEY (dept_id) 
        REFERENCES department(dept_id) ON DELETE SET NULL
);

-- 创建索引
CREATE INDEX idx_area_enterprise_id ON area(enterprise_id);
CREATE INDEX idx_area_dept_id ON area(dept_id);

COMMENT ON TABLE area IS '作业区域表';
```

---

## 13. 作业票表 (ticket)

### 创建表SQL语句

```sql
CREATE TABLE ticket (
    ticket_id SERIAL PRIMARY KEY,
    apply_date DATE NOT NULL,
    applicant INTEGER NOT NULL,
    area_id INTEGER NOT NULL,
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
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_ticket_applicant FOREIGN KEY (applicant) 
        REFERENCES enterprise_user(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_ticket_area FOREIGN KEY (area_id) 
        REFERENCES area(area_id) ON DELETE CASCADE,
    CONSTRAINT fk_ticket_worker FOREIGN KEY (worker) 
        REFERENCES contractor_user(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_ticket_custodian FOREIGN KEY (custodians) 
        REFERENCES enterprise_user(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_ticket_confined_space FOREIGN KEY (confined_space_id) 
        REFERENCES confined_space(confined_space_id) ON DELETE SET NULL,
    CONSTRAINT fk_ticket_temp_power FOREIGN KEY (temp_power_id) 
        REFERENCES temporary_power(temp_power_id) ON DELETE SET NULL
);

-- 创建索引
CREATE INDEX idx_ticket_apply_date ON ticket(apply_date);
CREATE INDEX idx_ticket_applicant ON ticket(applicant);
CREATE INDEX idx_ticket_area_id ON ticket(area_id);
CREATE INDEX idx_ticket_worker ON ticket(worker);
CREATE INDEX idx_ticket_hot_work ON ticket(hot_work);

COMMENT ON TABLE ticket IS '作业票表';
COMMENT ON COLUMN ticket.hot_work IS '动火等级：-1-未动火, 0-特级动火, 1-一级动火, 2-二级动火';
COMMENT ON COLUMN ticket.work_height_level IS '作业高度等级：0-4级';
```

---

## 14. 作业设备表 (work_equipment)

### 创建表SQL语句

```sql
CREATE TABLE work_equipment (
    equipment_id SERIAL PRIMARY KEY,
    equipment_name VARCHAR(100) NOT NULL,
    equipment_power VARCHAR(50) NOT NULL,
    work_voltage VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_work_equipment_name ON work_equipment(equipment_name);

COMMENT ON TABLE work_equipment IS '作业设备表';
```

---

## 15. 受限空间表 (confined_space)

### 创建表SQL语句

```sql
CREATE TABLE confined_space (
    confined_space_id SERIAL PRIMARY KEY,
    ticket_id INTEGER NOT NULL,
    space_level INTEGER NOT NULL,
    space_name VARCHAR(50) NOT NULL,
    original_medium VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_confined_space_ticket FOREIGN KEY (ticket_id) 
        REFERENCES ticket(ticket_id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX idx_confined_space_ticket_id ON confined_space(ticket_id);

COMMENT ON TABLE confined_space IS '受限空间表';
COMMENT ON COLUMN confined_space.space_level IS '受限空间等级（1-一级, 2-二级）';
```

---

## 16. 临时用电表 (temporary_power)

### 创建表SQL语句

```sql
CREATE TABLE temporary_power (
    temp_power_id SERIAL PRIMARY KEY,
    ticket_id INTEGER NOT NULL,
    equipment_id INTEGER NOT NULL,
    power_access_point VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_temp_power_ticket FOREIGN KEY (ticket_id) 
        REFERENCES ticket(ticket_id) ON DELETE CASCADE,
    CONSTRAINT fk_temp_power_equipment FOREIGN KEY (equipment_id) 
        REFERENCES work_equipment(equipment_id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX idx_temporary_power_ticket_id ON temporary_power(ticket_id);

COMMENT ON TABLE temporary_power IS '临时用电表';
```

---

## 17. 交叉作业表 (cross_work)

### 创建表SQL语句

```sql
CREATE TABLE cross_work (
    id SERIAL PRIMARY KEY,
    group_id VARCHAR(50) NOT NULL,
    area_id INTEGER NOT NULL,
    ticket_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cross_work_area FOREIGN KEY (area_id) 
        REFERENCES area(area_id) ON DELETE CASCADE,
    CONSTRAINT fk_cross_work_ticket FOREIGN KEY (ticket_id) 
        REFERENCES ticket(ticket_id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX idx_cross_work_group_id ON cross_work(group_id);
CREATE INDEX idx_cross_work_ticket_id ON cross_work(ticket_id);

COMMENT ON TABLE cross_work IS '交叉作业表';
COMMENT ON COLUMN cross_work.group_id IS '交叉作业组ID（同一组内的作业票为交叉作业）';
```

---

## 完整建表脚本执行顺序

由于表之间存在外键依赖关系，建议按以下顺序执行建表语句：

1. 删除旧表（如果存在）
2. company
3. enterprise_info
4. contractor_info
5. contractor (旧表，保持向后兼容)
6. department
7. enterprise_user
8. contractor_user
9. users
10. contractor_project
11. entry_plan
12. entry_plan_user
13. entry_register
14. area
15. work_equipment
16. ticket
17. confined_space
18. temporary_power
19. cross_work

---

## 数据迁移建议

如果系统中已有数据，需要进行数据迁移：

### 1. 备份现有数据

```sql
-- 备份contractor表数据
CREATE TABLE contractor_backup AS SELECT * FROM contractor;
```

### 2. 迁移数据到新表

```sql
-- 将contractor表数据迁移到contractor_info表
INSERT INTO contractor_info (
    contractor_id,
    license_file,
    company_name,
    company_type,
    legal_person,
    establish_date,
    registered_capital,
    applicant_name,
    business_status,
    is_deleted,
    created_at,
    updated_at
)
SELECT 
    contractor_id,
    license_file,
    company_name,
    company_type,
    legal_person,
    establish_date,
    registered_capital,
    applicant_name,
    '续存' as business_status,
    false as is_deleted,
    created_at,
    updated_at
FROM contractor_backup;
```

---

**文档版本**: v1.0  
**最后更新**: 2025-11-11  
**维护人员**: EHS系统开发团队
