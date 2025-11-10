# EHS系统数据库设计与业务流程PRD文档

## 文档信息

- **文档名称**：EHS系统数据库设计与业务流程PRD
- **版本号**：v2.0
- **创建日期**：2025-01-04
- **最后更新**：2025-01-04
- **文档状态**：正式版

---

## 一、项目概述

### 1.1 项目背景

本项目是一个企业环境健康安全(EHS)管理系统，主要用于管理甲方企业与承包商企业之间的作业工单流程。系统需要支持复杂的工单审批流程、灵活的权限管理、以及完整的操作审计功能。

### 1.2 核心目标

1. **主体独立管理**：甲方企业、承包商企业、企业人员、承包商人员完全独立管理
2. **多对多合作关系**：一个承包商可以与多个甲方企业合作，一个甲方企业可以与多个承包商合作
3. **灵活的工单流程**：支持复杂的审批流程、步骤流转、回退机制、加签(当事人通知)、移交(当事人选择)、暂存(临时存储-创建工单阶段)
4. **细粒度权限控制**：角色与权限分离，企业可自定义角色和权限
5. **企业数据隔离**：确保企业间数据安全隔离，不能跨企业审批
6. **完整的操作审计**：记录所有关键操作的历史记录

### 1.3 系统主体架构

```
系统主体架构
├── 1. 系统管理员（admin_account）
│   └── 系统最高权限，管理所有资源
│
├── 2. 甲方企业（enterprise）
│   ├── 部门（department）
│   ├── 厂区（area）（可视化地图识别）
│   └── 工单流程定义（workflow_definitions）固定流程
|   |--对自己承包商服务管理（添加企业可视、合作状态、合作时效手动设定）
│
├── 3. 企业人员（enterprise_staff + enterprise_staff_account）
│   ├── 所属甲方企业
│   ├── 创建工单
│
├── 4. 承包商企业（contractor）
│   └── 与多个甲方企业合作（多对多关系）
│
└── 5. 承包商人员（contractor_staff + contractor_staff_account）
    ├── 所属承包商企业
    ├── 登记进场
    └── 执行作业（允许承包商看到工单状态）
```

---

## 二、核心业务流程

### 2.1 工单流程核心规则

#### 2.1.1 工单生命周期(工单存在可执行时效-当时效出现溢出工单自动终止)

工单具有以下状态：

1. **in_progress**：进行中（默认状态）
2. **completed**：已完成（流程正常结束）
3. **terminated**：已终止（人为中止）

**重要说明**：
- 工单本身不能回退，只能创建、完成、终止
- 可以回退的是工单中的步骤
- 步骤回退只能回退到上一步或重新开始

#### 2.1.2 步骤流转规则

```
步骤流转规则：
1. 每步流转必须上一步已完成
2. 部分步骤需要审批通过才能流转
3. 流转前验证条件（审核状态、完成状态、权限等）
4. 步骤可以回退到上一步或重新开始
5. 回退后的步骤记录标记为"已回退"状态
6. 重新流转时创建新的步骤记录
```

#### 2.1.3 回退机制

**回退类型**：
1. **回退到上一步**（`rollback_to_previous`）：返回到上一个步骤
2. **回退到开始**（`rollback_to_start`）：返回到流程起点

**权限控制**：
- 工单创建者：可回退步骤到上一步或开始
- 工单审核人员：可回退步骤到上一步或开始
- 当前步骤操作人员：可回退步骤到上一步或开始

**回退处理逻辑**：
1. 将当前步骤实例状态标记为 `rolled_back`（假删除）
2. 恢复上一步骤实例状态为 `in_progress`
3. 更新工单的 `current_step_id` 为上一步骤ID
4. 记录回退操作日志

**重新流转逻辑**：
1. 从回退后的步骤重新流转时，创建新的步骤实例记录
2. 原有的回退记录保持 `rolled_back` 状态
3. 新记录与原记录通过 `previous_instance_id` 关联

#### 2.1.4 审批机制

系统支持两种审批模式：

1. **任一审批通过**（`approval_type='any'`）：
   - 指定多个审批人
   - 任意一人审批通过即可进入下一步骤
   - 所有审批记录都需要保留

2. **全部审批通过**（`approval_type='all'`）：
   - 指定多个审批人
   - 必须所有人都审批通过才能进入下一步骤
   - 任意一人拒绝则审批失败
   - 所有审批记录都需要保留

**审批流程**：
```
步骤到达 → 创建审批记录（为每个审批人创建一条记录）
         ↓
      审批人审批
         ↓
   检查审批模式
         ↓
   ┌─────┴─────┐
   │           │
any模式      all模式
任一通过      全部通过
   │           │
   └─────┬─────┘
         ↓
   进入下一步骤
```

#### 2.1.5 终止工单

**权限**：仅工单创建者和审核人员（`can_approve_ticket=TRUE`）

**效果**：
- 工单状态变为 `terminated`
- 保留所有历史记录
- 记录终止原因和终止人
- 不可恢复（除非数据库操作）

#### 2.1.6 删除工单

**权限**：仅工单创建者和审核人员

**效果**：
- 软删除（`is_deleted=TRUE`）
- 保留所有数据
- 不在列表中显示
- 可通过数据库恢复

### 2.2 企业数据隔离

**核心原则**：企业人员只能审批本企业的工单，不能跨企业审批

**实现方式**：
1. 工单创建时关联 `enterprise_id`
2. 审批人员必须属于同一 `enterprise_id`
3. 查询工单时自动过滤 `enterprise_id`
4. API层面强制验证企业归属

### 2.3 角色与权限分离

**设计原则**：
1. 角色（Role）与权限（Permission）完全分离
2. 系统提供基础权限列表
3. 企业可自定义角色
4. 企业为角色绑定权限
5. 人员分配角色后自动获得权限

**权限管理流程**：
```
1. 系统预定义权限列表（permissions表）
   ↓
2. 企业创建自定义角色（roles表）
   ↓
3. 企业为角色绑定权限（role_permissions表）
   ↓
4. 为人员分配角色（enterprise_staff.role_id）
   ↓
5. 人员自动获得角色的所有权限
```

---

## 三、数据库表结构设计

### 3.1 主体管理表

#### 3.1.1 甲方企业表（enterprise）

**用途**：管理甲方企业信息

```sql
CREATE TABLE enterprise (
    enterprise_id INT PRIMARY KEY AUTO_INCREMENT,
    enterprise_name VARCHAR(255) NOT NULL COMMENT '企业名称',
    enterprise_code VARCHAR(100) UNIQUE NULL COMMENT '企业编码',
    
    -- 企业信息
    legal_person VARCHAR(100) NULL COMMENT '法定代表人',
    establish_date DATE NULL COMMENT '成立日期',
    registered_capital DECIMAL(15,2) NULL COMMENT '注册资本（万元）',
    business_scope TEXT NULL COMMENT '经营范围',
    
    -- 联系信息
    contact_person VARCHAR(100) NULL COMMENT '联系人',
    contact_phone VARCHAR(20) NULL COMMENT '联系电话',
    contact_email VARCHAR(100) NULL COMMENT '联系邮箱',
    address VARCHAR(500) NULL COMMENT '企业地址',
    
    -- 状态管理
    status ENUM('active', 'inactive', 'deleted') DEFAULT 'active' NOT NULL COMMENT '状态',
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL COMMENT '软删除标记',
    
    -- 审计字段
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NULL COMMENT '创建人账号ID',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT NULL COMMENT '最后更新人账号ID',
    deleted_at DATETIME NULL COMMENT '删除时间',
    deleted_by INT NULL COMMENT '删除人账号ID',
    
    INDEX idx_enterprise_name (enterprise_name),
    INDEX idx_enterprise_code (enterprise_code),
    INDEX idx_status (status),
    INDEX idx_is_deleted (is_deleted)
) COMMENT='甲方企业表';
```

#### 3.1.2 承包商企业表（contractor）

**用途**：管理承包商企业信息

```sql
CREATE TABLE contractor (
    contractor_id INT PRIMARY KEY AUTO_INCREMENT,
    company_name VARCHAR(255) NOT NULL COMMENT '承包商企业名称',
    company_code VARCHAR(100) UNIQUE NULL COMMENT '企业编码/统一社会信用代码',
    
    -- 企业资质信息
    license_file VARCHAR(255) NOT NULL COMMENT '营业执照文件路径',
    company_type VARCHAR(100) NULL COMMENT '企业类型',
    legal_person VARCHAR(100) NOT NULL COMMENT '法定代表人',
    establish_date DATE NULL COMMENT '成立日期',
    registered_capital DECIMAL(15,2) NULL COMMENT '注册资本（万元）',
    business_scope TEXT NULL COMMENT '经营范围',
    
    -- 资质证书
    qualification_certificates TEXT NULL COMMENT '资质证书（JSON数组：[{cert_name, cert_no, cert_file, expire_date}]）',
    safety_license VARCHAR(255) NULL COMMENT '安全生产许可证文件',
    safety_license_no VARCHAR(100) NULL COMMENT '安全生产许可证编号',
    safety_license_expire DATE NULL COMMENT '安全生产许可证有效期',
    
    -- 联系信息
    applicant_name VARCHAR(100) NULL COMMENT '申请人姓名',
    contact_person VARCHAR(100) NULL COMMENT '联系人',
    contact_phone VARCHAR(20) NOT NULL COMMENT '联系电话',
    contact_email VARCHAR(100) NULL COMMENT '联系邮箱',
    address VARCHAR(500) NULL COMMENT '企业地址',
    
    -- 状态管理
    status ENUM('active', 'inactive', 'blacklist', 'deleted') DEFAULT 'active' NOT NULL COMMENT '状态：active=正常, inactive=停用, blacklist=黑名单',
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL COMMENT '软删除标记',
    
    -- 审计字段
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NULL COMMENT '创建人账号ID',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT NULL COMMENT '最后更新人账号ID',
    deleted_at DATETIME NULL COMMENT '删除时间',
    deleted_by INT NULL COMMENT '删除人账号ID',
    
    -- 备注
    remarks TEXT NULL COMMENT '备注信息',
    
    INDEX idx_company_name (company_name),
    INDEX idx_company_code (company_code),
    INDEX idx_status (status),
    INDEX idx_is_deleted (is_deleted),
    INDEX idx_safety_license_expire (safety_license_expire)
) COMMENT='承包商企业表';
```

#### 3.1.3 企业承包商合作关系表（enterprise_contractor_relation）

**用途**：管理甲方企业与承包商企业的多对多合作关系

**重要说明**：这是新增的表，用于解决多对多关系

```sql
CREATE TABLE enterprise_contractor_relation (
    relation_id INT PRIMARY KEY AUTO_INCREMENT,
    enterprise_id INT NOT NULL COMMENT '甲方企业ID',
    contractor_id INT NOT NULL COMMENT '承包商企业ID',
    
    -- 合作信息
    cooperation_start_date DATE NOT NULL COMMENT '合作开始日期',
    cooperation_end_date DATE NULL COMMENT '合作结束日期（NULL表示长期合作）',
    contract_no VARCHAR(100) NULL COMMENT '合同编号',
    contract_file VARCHAR(255) NULL COMMENT '合同文件路径',
    
    -- 合作范围
    cooperation_scope TEXT NULL COMMENT '合作范围描述',
    authorized_areas TEXT NULL COMMENT '授权作业区域（JSON数组：[area_id1, area_id2, ...]）',
    
    -- 状态管理
    status ENUM('active', 'inactive', 'expired', 'terminated') DEFAULT 'active' NOT NULL COMMENT '状态：active=合作中, inactive=暂停, expired=已过期, terminated=已终止',
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL COMMENT '软删除标记',
    
    -- 审计字段
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NULL COMMENT '创建人账号ID',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT NULL COMMENT '最后更新人账号ID',
    deleted_at DATETIME NULL COMMENT '删除时间',
    deleted_by INT NULL COMMENT '删除人账号ID',
    
    -- 备注
    remarks TEXT NULL COMMENT '备注信息',
    
    UNIQUE KEY uk_enterprise_contractor (enterprise_id, contractor_id),
    INDEX idx_enterprise_id (enterprise_id),
    INDEX idx_contractor_id (contractor_id),
    INDEX idx_status (status),
    INDEX idx_is_deleted (is_deleted),
    INDEX idx_cooperation_end_date (cooperation_end_date),
    
    FOREIGN KEY (enterprise_id) REFERENCES enterprise(enterprise_id),
    FOREIGN KEY (contractor_id) REFERENCES contractor(contractor_id)
) COMMENT='企业承包商合作关系表（多对多）';
```

**业务说明**：
- 一个甲方企业可以与多个承包商合作
- 一个承包商可以与多个甲方企业合作
- 每个合作关系独立管理，有独立的合作期限和授权范围
- 支持合作关系的暂停、终止、过期管理

### 3.2 账号管理表

#### 3.2.1 系统管理员账号表（admin_account）

```sql
CREATE TABLE admin_account (
    account_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '登录用户名',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    admin_name VARCHAR(100) NOT NULL COMMENT '管理员姓名',
    admin_level INT DEFAULT 1 COMMENT '管理员级别（1=超级管理员，2=普通管理员）',
    
    -- 状态管理
    status ENUM('active', 'inactive', 'locked', 'deleted') DEFAULT 'active' NOT NULL COMMENT '账号状态',
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL COMMENT '软删除标记',
    
    -- 安全信息
    last_login_at DATETIME NULL COMMENT '最后登录时间',
    login_attempts INT DEFAULT 0 COMMENT '登录失败次数',
    locked_until DATETIME NULL COMMENT '锁定截止时间',
    
    -- 审计字段
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NULL COMMENT '创建人账号ID',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT NULL COMMENT '最后更新人账号ID',
    deleted_at DATETIME NULL COMMENT '删除时间',
    deleted_by INT NULL COMMENT '删除人账号ID',
    
    INDEX idx_username (username),
    INDEX idx_status (status),
    INDEX idx_is_deleted (is_deleted)
) COMMENT='系统管理员账号表';
```

#### 3.2.2 企业人员账号表（enterprise_staff_account）

```sql
CREATE TABLE enterprise_staff_account (
    account_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '登录用户名（通常使用手机号）',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    staff_id INT NOT NULL COMMENT '关联的企业人员ID',
    
    -- 状态管理
    status ENUM('active', 'inactive', 'locked', 'deleted') DEFAULT 'active' NOT NULL COMMENT '账号状态',
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL COMMENT '软删除标记',
    
    -- 安全信息
    last_login_at DATETIME NULL COMMENT '最后登录时间',
    last_login_ip VARCHAR(50) NULL COMMENT '最后登录IP',
    login_attempts INT DEFAULT 0 COMMENT '登录失败次数',
    locked_until DATETIME NULL COMMENT '锁定截止时间',
    
    -- 审计字段
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NULL COMMENT '创建人账号ID',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT NULL COMMENT '最后更新人账号ID',
    deleted_at DATETIME NULL COMMENT '删除时间',
    deleted_by INT NULL COMMENT '删除人账号ID',
    
    INDEX idx_username (username),
    INDEX idx_staff_id (staff_id),
    INDEX idx_status (status),
    INDEX idx_is_deleted (is_deleted),
    
    FOREIGN KEY (staff_id) REFERENCES enterprise_staff(staff_id)
) COMMENT='企业人员账号表';
```

#### 3.2.3 承包商人员账号表（contractor_staff_account）

```sql
CREATE TABLE contractor_staff_account (
    account_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '登录用户名（通常使用手机号）',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    staff_id INT NOT NULL COMMENT '关联的承包商人员ID',
    
    -- 状态管理
    status ENUM('active', 'inactive', 'locked', 'deleted') DEFAULT 'active' NOT NULL COMMENT '账号状态',
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL COMMENT '软删除标记',
    
    -- 安全信息
    last_login_at DATETIME NULL COMMENT '最后登录时间',
    last_login_ip VARCHAR(50) NULL COMMENT '最后登录IP',
    login_attempts INT DEFAULT 0 COMMENT '登录失败次数',
    locked_until DATETIME NULL COMMENT '锁定截止时间',
    
    -- 审计字段
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NULL COMMENT '创建人账号ID',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT NULL COMMENT '最后更新人账号ID',
    deleted_at DATETIME NULL COMMENT '删除时间',
    deleted_by INT NULL COMMENT '删除人账号ID',
    
    INDEX idx_username (username),
    INDEX idx_staff_id (staff_id),
    INDEX idx_status (status),
    INDEX idx_is_deleted (is_deleted),
    
    FOREIGN KEY (staff_id) REFERENCES contractor_staff(staff_id)
) COMMENT='承包商人员账号表';
```

#### 3.2.4 账号变更日志表（account_change_logs）

```sql
CREATE TABLE account_change_logs (
    log_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    account_id INT NOT NULL COMMENT '被操作的账号ID',
    account_type ENUM('admin', 'enterprise_staff', 'contractor_staff') NOT NULL COMMENT '账号类型',
    operation_type ENUM('create', 'update', 'delete', 'lock', 'unlock', 'reset_password', 'status_change', 'login_success', 'login_failed') NOT NULL COMMENT '操作类型',
    
    -- 操作人信息
    operator_id INT NULL COMMENT '操作人账号ID（登录操作时为NULL）',
    operator_name VARCHAR(100) NULL COMMENT '操作人姓名',
    operator_type ENUM('admin', 'enterprise_staff', 'contractor_staff') NULL COMMENT '操作人类型',
    
    -- 变更内容
    field_name VARCHAR(100) NULL COMMENT '变更字段名',
    old_value TEXT NULL COMMENT '旧值（JSON格式）',
    new_value TEXT NULL COMMENT '新值（JSON格式）',
    change_reason VARCHAR(500) NULL COMMENT '变更原因',
    
    -- 操作信息
    operation_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    ip_address VARCHAR(50) NULL COMMENT '操作IP地址',
    user_agent VARCHAR(500) NULL COMMENT '用户代理',
    
    INDEX idx_account_id (account_id),
    INDEX idx_account_type (account_type),
    INDEX idx_operator_id (operator_id),
    INDEX idx_operation_type (operation_type),
    INDEX idx_operation_time (operation_time)
) COMMENT='账号变更日志表';
```

### 3.3 人员管理表

#### 3.3.1 企业人员信息表（enterprise_staff）

```sql
CREATE TABLE enterprise_staff (
    staff_id INT PRIMARY KEY AUTO_INCREMENT,
    enterprise_id INT NOT NULL COMMENT '所属企业ID',
    dept_id INT NULL COMMENT '所属部门ID',
    
    -- 基本信息
    name VARCHAR(100) NOT NULL COMMENT '姓名',
    phone VARCHAR(20) NOT NULL COMMENT '手机号',
    email VARCHAR(100) NULL COMMENT '邮箱',
    position VARCHAR(100) NULL COMMENT '职位',
    id_number VARCHAR(50) NULL COMMENT '身份证号',
    
    -- 角色权限
    role_id INT NOT NULL COMMENT '角色ID',
    
    -- 工单权限标识（快速判断，实际权限以role_permissions为准）
    can_create_ticket BOOLEAN DEFAULT TRUE COMMENT '是否可以创建工单',
    can_approve_ticket BOOLEAN DEFAULT FALSE COMMENT '是否可以审批工单',
    can_terminate_ticket BOOLEAN DEFAULT FALSE COMMENT '是否可以终止工单',
    
    -- 状态管理
    status ENUM('active', 'inactive', 'deleted') DEFAULT 'active' NOT NULL COMMENT '状态',
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL COMMENT '软删除标记',
    
    -- 审计字段
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NULL COMMENT '创建人账号ID',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT NULL COMMENT '最后更新人账号ID',
    deleted_at DATETIME NULL COMMENT '删除时间',
    deleted_by INT NULL COMMENT '删除人账号ID',
    
    INDEX idx_enterprise_id (enterprise_id),
    INDEX idx_dept_id (dept_id),
    INDEX idx_role_id (role_id),
    INDEX idx_phone (phone),
    INDEX idx_is_deleted (is_deleted),
    
    FOREIGN KEY (enterprise_id) REFERENCES enterprise(enterprise_id),
    FOREIGN KEY (dept_id) REFERENCES department(dept_id),
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
) COMMENT='企业人员信息表';
```

#### 3.3.2 承包商人员信息表（contractor_staff）

```sql
CREATE TABLE contractor_staff (
    staff_id INT PRIMARY KEY AUTO_INCREMENT,
    contractor_id INT NOT NULL COMMENT '所属承包商企业ID',
    
    -- 基本信息
    name VARCHAR(100) NOT NULL COMMENT '姓名',
    phone VARCHAR(20) NOT NULL COMMENT '手机号',
    id_number VARCHAR(50) NOT NULL COMMENT '身份证号',
    work_type VARCHAR(100) NOT NULL COMMENT '工种',
    personal_photo VARCHAR(255) NULL COMMENT '个人照片路径',
    
    -- 资质信息
    work_certificate VARCHAR(255) NULL COMMENT '工作证书文件',
    certificate_no VARCHAR(100) NULL COMMENT '证书编号',
    certificate_expire DATE NULL COMMENT '证书有效期',
    safety_training_date DATE NULL COMMENT '安全培训日期',
    safety_training_certificate VARCHAR(255) NULL COMMENT '安全培训证书',
    
    -- 角色权限
    role_id INT NOT NULL COMMENT '角色ID',
    
    -- 状态管理
    status ENUM('active', 'inactive', 'deleted') DEFAULT 'active' NOT NULL COMMENT '状态',
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL COMMENT '软删除标记',
    
    -- 审计字段
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NULL COMMENT '创建人账号ID',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT NULL COMMENT '最后更新人账号ID',
    deleted_at DATETIME NULL COMMENT '删除时间',
    deleted_by INT NULL COMMENT '删除人账号ID',
    
    INDEX idx_contractor_id (contractor_id),
    INDEX idx_role_id (role_id),
    INDEX idx_phone (phone),
    INDEX idx_id_number (id_number),
    INDEX idx_is_deleted (is_deleted),
    INDEX idx_certificate_expire (certificate_expire),
    
    FOREIGN KEY (contractor_id) REFERENCES contractor(contractor_id),
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
) COMMENT='承包商人员信息表';
```

### 3.4 组织结构表

#### 3.4.1 部门表（department）

```sql
CREATE TABLE department (
    dept_id INT PRIMARY KEY AUTO_INCREMENT,
    enterprise_id INT NOT NULL COMMENT '所属企业ID',
    name VARCHAR(255) NOT NULL COMMENT '部门名称',
    parent_id INT NULL COMMENT '父部门ID（支持多级部门）',
    
    -- 状态管理
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL COMMENT '软删除标记',
    
    -- 审计字段
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NULL COMMENT '创建人账号ID',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT NULL COMMENT '最后更新人账号ID',
    deleted_at DATETIME NULL COMMENT '删除时间',
    deleted_by INT NULL COMMENT '删除人账号ID',
    
    INDEX idx_enterprise_id (enterprise_id),
    INDEX idx_parent_id (parent_id),
    INDEX idx_is_deleted (is_deleted),
    
    FOREIGN KEY (enterprise_id) REFERENCES enterprise(enterprise_id),
    FOREIGN KEY (parent_id) REFERENCES department(dept_id)
) COMMENT='部门表';
```

#### 3.4.2 厂区表（area）

```sql
CREATE TABLE area (
    area_id INT PRIMARY KEY AUTO_INCREMENT,
    enterprise_id INT NOT NULL COMMENT '所属企业ID',
    area_name VARCHAR(64) NOT NULL COMMENT '厂区名称',
    dept_id INT NULL COMMENT '所属部门ID',
    area_code VARCHAR(50) NULL COMMENT '厂区编码',
    
    -- 状态管理
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL COMMENT '软删除标记',
    
    -- 审计字段
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NULL COMMENT '创建人账号ID',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT NULL COMMENT '最后更新人账号ID',
    deleted_at DATETIME NULL COMMENT '删除时间',
    deleted_by INT NULL COMMENT '删除人账号ID',
    
    INDEX idx_enterprise_id (enterprise_id),
    INDEX idx_dept_id (dept_id),
    INDEX idx_is_deleted (is_deleted),
    
    FOREIGN KEY (enterprise_id) REFERENCES enterprise(enterprise_id),
    FOREIGN KEY (dept_id) REFERENCES department(dept_id)
) COMMENT='厂区表';
```

### 3.5 权限管理表

#### 3.5.1 权限定义表（permissions）

**用途**：系统预定义的权限列表

```sql
CREATE TABLE permissions (
    permission_id INT PRIMARY KEY AUTO_INCREMENT,
    permission_code VARCHAR(100) UNIQUE NOT NULL COMMENT '权限编码（如：ticket.create）',
    permission_name VARCHAR(100) NOT NULL COMMENT '权限名称',
    resource_type VARCHAR(50) NOT NULL COMMENT '资源类型（如：ticket, user, project等）',
    action VARCHAR(50) NOT NULL COMMENT '操作类型（如：create, read, update, delete, approve等）',
    description VARCHAR(500) NULL COMMENT '权限描述',
    
    -- 分类
    category VARCHAR(50) NOT NULL COMMENT '权限分类（如：工单管理、用户管理、系统管理）',
    
    -- 状态
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    
    -- 审计字段
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_permission_code (permission_code),
    INDEX idx_resource_type (resource_type),
    INDEX idx_category (category)
) COMMENT='权限定义表（系统预定义）';
```

**权限编码示例**：
```sql
-- 工单权限
INSERT INTO permissions (permission_code, permission_name, resource_type, action, category, description) VALUES
('ticket.create', '创建工单', 'ticket', 'create', '工单管理', '允许创建新工单'),
('ticket.read', '查看工单', 'ticket', 'read', '工单管理', '允许查看工单详情'),
('ticket.update', '更新工单', 'ticket', 'update', '工单管理', '允许更新工单信息'),
('ticket.delete', '删除工单', 'ticket', 'delete', '工单管理', '允许删除工单'),
('ticket.approve', '审批工单', 'ticket', 'approve', '工单管理', '允许审批工单步骤'),
('ticket.terminate', '终止工单', 'ticket', 'terminate', '工单管理', '允许终止工单'),
('ticket.rollback', '回退步骤', 'ticket', 'rollback', '工单管理', '允许回退工单步骤');

-- 用户管理权限
INSERT INTO permissions (permission_code, permission_name, resource_type, action, category, description) VALUES
('user.create', '创建用户', 'user', 'create', '用户管理', '允许创建新用户'),
('user.read', '查看用户', 'user', 'read', '用户管理', '允许查看用户信息'),
('user.update', '更新用户', 'user', 'update', '用户管理', '允许更新用户信息'),
('user.delete', '删除用户', 'user', 'delete', '用户管理', '允许删除用户');

-- 角色管理权限
INSERT INTO permissions (permission_code, permission_name, resource_type, action, category, description) VALUES
('role.create', '创建角色', 'role', 'create', '角色管理', '允许创建新角色'),
('role.read', '查看角色', 'role', 'read', '角色管理', '允许查看角色信息'),
('role.update', '更新角色', 'role', 'update', '角色管理', '允许更新角色信息'),
('role.delete', '删除角色', 'role', 'delete', '角色管理', '允许删除角色'),
('role.assign_permission', '分配权限', 'role', 'assign_permission', '角色管理', '允许为角色分配权限');
```

#### 3.5.2 角色表（roles）

**用途**：企业自定义的角色

```sql
CREATE TABLE roles (
    role_id INT PRIMARY KEY AUTO_INCREMENT,
    role_code VARCHAR(50) NOT NULL COMMENT '角色编码',
    role_name VARCHAR(100) NOT NULL COMMENT '角色名称',
    role_type ENUM('system', 'enterprise', 'contractor') NOT NULL COMMENT '角色类型',
    
    -- 关联信息
    enterprise_id INT NULL COMMENT '所属企业ID（企业自定义角色时使用）',
    contractor_id INT NULL COMMENT '所属承包商ID（承包商自定义角色时使用）',
    
    -- 描述信息
    description VARCHAR(500) NULL COMMENT '角色描述',
    
    -- 状态管理
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    is_system BOOLEAN DEFAULT FALSE COMMENT '是否系统内置角色（不可删除）',
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL COMMENT '软删除标记',
    
    -- 审计字段
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NULL COMMENT '创建人账号ID',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT NULL COMMENT '最后更新人账号ID',
    deleted_at DATETIME NULL COMMENT '删除时间',
    deleted_by INT NULL COMMENT '删除人账号ID',
    
    UNIQUE KEY uk_role_code_enterprise (role_code, enterprise_id, contractor_id),
    INDEX idx_role_code (role_code),
    INDEX idx_role_type (role_type),
    INDEX idx_enterprise_id (enterprise_id),
    INDEX idx_contractor_id (contractor_id),
    INDEX idx_is_deleted (is_deleted),
    
    FOREIGN KEY (enterprise_id) REFERENCES enterprise(enterprise_id),
    FOREIGN KEY (contractor_id) REFERENCES contractor(contractor_id)
) COMMENT='角色表（企业可自定义）';
```

**系统预置角色示例**：
```sql
-- 管理员角色
INSERT INTO roles (role_code, role_name, role_type, is_system, description) 
VALUES ('system_admin', '系统管理员', 'system', TRUE, '系统最高权限');

-- 企业角色（系统预置，企业可自定义）
INSERT INTO roles (role_code, role_name, role_type, is_system, description) 
VALUES 
('enterprise_admin', '企业管理员', 'enterprise', TRUE, '企业最高权限，可管理企业所有资源'),
('enterprise_approver', '企业审批员', 'enterprise', TRUE, '可审批工单'),
('enterprise_staff', '企业普通员工', 'enterprise', TRUE, '可查看和创建工单');

-- 承包商角色（系统预置，承包商可自定义）
INSERT INTO roles (role_code, role_name, role_type, is_system, description) 
VALUES 
('contractor_admin', '承包商管理员', 'contractor', TRUE, '承包商最高权限'),
('contractor_worker', '承包商普通员工', 'contractor', TRUE, '普通作业人员');
```

#### 3.5.3 角色权限关联表（role_permissions）

**用途**：定义角色具体拥有的权限

```sql
CREATE TABLE role_permissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    role_id INT NOT NULL COMMENT '角色ID',
    permission_id INT NOT NULL COMMENT '权限ID',
    
    -- 审计字段
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NULL COMMENT '创建人账号ID',
    
    UNIQUE KEY uk_role_permission (role_id, permission_id),
    INDEX idx_role_id (role_id),
    INDEX idx_permission_id (permission_id),
    
    FOREIGN KEY (role_id) REFERENCES roles(role_id),
    FOREIGN KEY (permission_id) REFERENCES permissions(permission_id)
) COMMENT='角色权限关联表';
```

**业务流程说明**：
1. 企业管理员创建自定义角色（如："安全主管"）
2. 从权限列表中选择权限绑定到该角色
3. 为企业人员分配该角色
4. 人员自动获得该角色的所有权限

### 3.6 工单流程表

#### 3.6.1 工单流程定义表（workflow_definitions）

```sql
CREATE TABLE workflow_definitions (
    workflow_id INT PRIMARY KEY AUTO_INCREMENT,
    workflow_code VARCHAR(50) NOT NULL COMMENT '流程编码',
    workflow_name VARCHAR(100) NOT NULL COMMENT '流程名称',
    workflow_type VARCHAR(50) NOT NULL COMMENT '流程类型（如：ticket_approval）',
    
    -- 关联信息
    enterprise_id INT NULL COMMENT '所属企业ID（NULL表示系统通用流程）',
    
    -- 流程配置
    description VARCHAR(500) NULL COMMENT '流程描述',
    version INT DEFAULT 1 COMMENT '流程版本号',
    
    -- 状态管理
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL COMMENT '软删除标记',
    
    -- 审计字段
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NULL COMMENT '创建人账号ID',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT NULL COMMENT '最后更新人账号ID',
    deleted_at DATETIME NULL COMMENT '删除时间',
    deleted_by INT NULL COMMENT '删除人账号ID',
    
    UNIQUE KEY uk_workflow_code_enterprise (workflow_code, enterprise_id),
    INDEX idx_workflow_code (workflow_code),
    INDEX idx_enterprise_id (enterprise_id),
    INDEX idx_is_active (is_active),
    INDEX idx_is_deleted (is_deleted),
    
    FOREIGN KEY (enterprise_id) REFERENCES enterprise(enterprise_id)
) COMMENT='工单流程定义表';
```

#### 3.6.2 工单流程步骤表（workflow_steps）

**重要改进**：增加 `previous_step_id` 字段，用于回退机制

```sql
CREATE TABLE workflow_steps (
    step_id INT PRIMARY KEY AUTO_INCREMENT,
    workflow_id INT NOT NULL COMMENT '所属流程ID',
    step_code VARCHAR(50) NOT NULL COMMENT '步骤编码',
    step_name VARCHAR(100) NOT NULL COMMENT '步骤名称',
    step_order INT NOT NULL COMMENT '步骤顺序',
    
    -- 步骤类型
    step_type ENUM('start', 'operation', 'approval', 'notify', 'end') NOT NULL COMMENT '步骤类型：start=开始, operation=操作步骤, approval=审批步骤, notify=通知步骤, end=结束',
    
    -- 步骤链接（重要：用于回退）
    previous_step_id INT NULL COMMENT '上一步骤ID（用于回退）',
    next_step_id INT NULL COMMENT '下一步骤ID（非分支时使用）',
    
    -- 审批配置
    require_approval BOOLEAN DEFAULT FALSE COMMENT '是否需要审批',
    approver_role_ids TEXT NULL COMMENT '审批角色ID列表（JSON数组：[role_id1, role_id2, ...]）',
    approval_type ENUM('any', 'all') DEFAULT 'any' COMMENT '审批类型：any=任一审批人通过即可, all=所有审批人都必须通过',
    
    -- 流转条件配置
    require_previous_completed BOOLEAN DEFAULT TRUE COMMENT '是否要求上一步已完成',
    require_previous_approved BOOLEAN DEFAULT FALSE COMMENT '是否要求上一步已审批通过',
    condition_expression TEXT NULL COMMENT '流转条件表达式（JSON格式，支持复杂条件）',
    
    -- 回退配置
    can_rollback BOOLEAN DEFAULT TRUE COMMENT '是否允许回退',
    can_rollback_to_start BOOLEAN DEFAULT TRUE COMMENT '是否可以回退到开始',
    
    -- 分支配置
    is_branch_point BOOLEAN DEFAULT FALSE COMMENT '是否为分支点',
    branch_conditions TEXT NULL COMMENT '分支条件（JSON格式：[{condition, next_step_id}]）',
    
    -- 超时配置
    timeout_hours INT NULL COMMENT '超时时间（小时）',
    timeout_warning_hours INT NULL COMMENT '超时预警时间（小时）',
    
    -- 操作配置
    required_fields TEXT NULL COMMENT '必填字段（JSON数组）',
    allowed_operations TEXT NULL COMMENT '允许的操作（JSON数组：[edit, upload, sign等]）',
    
    -- 描述信息
    description VARCHAR(500) NULL COMMENT '步骤描述',
    operation_guide TEXT NULL COMMENT '操作指南',
    
    -- 审计字段
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NULL COMMENT '创建人账号ID',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT NULL COMMENT '最后更新人账号ID',
    
    UNIQUE KEY uk_workflow_step (workflow_id, step_code),
    INDEX idx_workflow_id (workflow_id),
    INDEX idx_step_order (step_order),
    INDEX idx_previous_step_id (previous_step_id),
    INDEX idx_next_step_id (next_step_id),
    
    FOREIGN KEY (workflow_id) REFERENCES workflow_definitions(workflow_id),
    FOREIGN KEY (previous_step_id) REFERENCES workflow_steps(step_id),
    FOREIGN KEY (next_step_id) REFERENCES workflow_steps(step_id)
) COMMENT='工单流程步骤表（支持回退机制）';
```

**关键字段说明**：

1. **previous_step_id**：
   - 记录上一步骤的ID
   - 用于回退时定位目标步骤
   - 开始步骤的 `previous_step_id` 为 NULL

2. **approval_type**：
   - `any`：任一审批人通过即可
   - `all`：所有审批人都必须通过

3. **approver_role_ids**：
   - JSON数组格式：`[1, 2, 3]`
   - 存储可以审批此步骤的角色ID列表
   - 系统会从这些角色中找出所有符合条件的人员

### 3.7 工单管理表

#### 3.7.1 工单表（ticket）

```sql
CREATE TABLE ticket (
    ticket_id INT PRIMARY KEY AUTO_INCREMENT,
    ticket_no VARCHAR(50) UNIQUE NOT NULL COMMENT '工单编号（唯一，如：TK20250104001）',
    
    -- 流程信息
    workflow_id INT NOT NULL COMMENT '关联的流程定义ID',
    current_step_id INT NULL COMMENT '当前步骤ID',
    
    -- 工单状态
    status ENUM('in_progress', 'completed', 'terminated') DEFAULT 'in_progress' NOT NULL COMMENT '工单状态：in_progress=进行中, completed=已完成, terminated=已终止',
    
    -- 基本信息
    apply_date DATE NOT NULL COMMENT '申请日期',
    creator_account_id INT NOT NULL COMMENT '创建者账号ID（企业人员）',
    creator_staff_id INT NOT NULL COMMENT '创建者人员ID',
    enterprise_id INT NOT NULL COMMENT '所属企业ID（用于数据隔离）',
    area_id INT NOT NULL COMMENT '作业区域ID',
    
    -- 作业信息
    working_content VARCHAR(1024) NOT NULL COMMENT '作业内容',
    pre_st DATETIME NOT NULL COMMENT '预计开始时间',
    pre_et DATETIME NOT NULL COMMENT '预计结束时间',
    actual_st DATETIME NULL COMMENT '实际开始时间',
    actual_et DATETIME NULL COMMENT '实际结束时间',
    
    -- 人员信息
    worker_staff_id INT NOT NULL COMMENT '作业人员ID（承包商人员）',
    custodian_staff_id INT NOT NULL COMMENT '监护人ID（企业人员）',
    
    -- 作业配置（二进制编码）
    tools INT DEFAULT 0 COMMENT '主要工具（二进制编码）',
    danger INT DEFAULT 0 COMMENT '危险识别（二进制编码）',
    protection INT DEFAULT 0 COMMENT '防护措施（二进制编码）',
    
    -- 特殊作业
    hot_work INT DEFAULT -1 COMMENT '动火等级：-1=未动火, 0=特级动火, 1=一级动火, 2=二级动火',
    work_height_level INT DEFAULT 0 COMMENT '作业高度等级：0-4级，数字越大危险程度越高',
    confined_space_id INT NULL COMMENT '受限空间ID',
    temp_power_id INT NULL COMMENT '临时用电ID',
    cross_work_group_id VARCHAR(50) NULL COMMENT '交叉作业组ID',
    
    -- 签字信息
    signatures TEXT NULL COMMENT '签字信息（JSON数组：[{staff_id, name, role, signature_file, signed_at}]）',
    
    -- 完成信息
    completion_notes VARCHAR(1000) NULL COMMENT '完成备注',
    completion_photos TEXT NULL COMMENT '完成照片（JSON数组）',
    completion_time DATETIME NULL COMMENT '完成时间',
    
    -- 终止信息
    is_terminated BOOLEAN DEFAULT FALSE NOT NULL COMMENT '是否已终止',
    terminated_at DATETIME NULL COMMENT '终止时间',
    terminated_by_account_id INT NULL COMMENT '终止人账号ID',
    terminated_by_staff_id INT NULL COMMENT '终止人人员ID',
    termination_reason VARCHAR(500) NULL COMMENT '终止原因',
    
    -- 软删除（仅创建者和审核人员可删除）
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL COMMENT '软删除标记',
    deleted_at DATETIME NULL COMMENT '删除时间',
    deleted_by_account_id INT NULL COMMENT '删除人账号ID',
    deleted_by_staff_id INT NULL COMMENT '删除人人员ID',
    deletion_reason VARCHAR(500) NULL COMMENT '删除原因',
    
    -- 审计字段
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by_account_id INT NULL COMMENT '最后更新人账号ID',
    
    INDEX idx_ticket_no (ticket_no),
    INDEX idx_workflow_id (workflow_id),
    INDEX idx_current_step_id (current_step_id),
    INDEX idx_status (status),
    INDEX idx_creator_staff_id (creator_staff_id),
    INDEX idx_enterprise_id (enterprise_id),
    INDEX idx_apply_date (apply_date),
    INDEX idx_is_deleted (is_deleted),
    INDEX idx_is_terminated (is_terminated),
    
    FOREIGN KEY (workflow_id) REFERENCES workflow_definitions(workflow_id),
    FOREIGN KEY (current_step_id) REFERENCES workflow_steps(step_id),
    FOREIGN KEY (creator_staff_id) REFERENCES enterprise_staff(staff_id),
    FOREIGN KEY (enterprise_id) REFERENCES enterprise(enterprise_id),
    FOREIGN KEY (area_id) REFERENCES area(area_id),
    FOREIGN KEY (worker_staff_id) REFERENCES contractor_staff(staff_id),
    FOREIGN KEY (custodian_staff_id) REFERENCES enterprise_staff(staff_id)
) COMMENT='工单表';
```

#### 3.7.2 工单步骤实例表（ticket_step_instances）

**重要改进**：增加 `previous_instance_id` 字段，用于关联回退前的记录

```sql
CREATE TABLE ticket_step_instances (
    instance_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    ticket_id INT NOT NULL COMMENT '工单ID',
    step_id INT NOT NULL COMMENT '步骤ID',
    step_name VARCHAR(100) NOT NULL COMMENT '步骤名称',
    step_order INT NOT NULL COMMENT '步骤顺序',
    
    -- 实例关联（用于回退后重新流转）
    previous_instance_id BIGINT NULL COMMENT '上一个实例ID（回退后重新流转时关联原实例）',
    
    -- 状态信息
    status ENUM('pending', 'in_progress', 'completed', 'rejected', 'skipped', 'rolled_back') DEFAULT 'pending' COMMENT '步骤状态',
    
    -- 处理人信息
    assignee_account_id INT NULL COMMENT '当前处理人账号ID',
    assignee_staff_id INT NULL COMMENT '当前处理人人员ID',
    assignee_name VARCHAR(100) NULL COMMENT '当前处理人姓名',
    assignee_role VARCHAR(100) NULL COMMENT '当前处理人角色',
    
    -- 时间信息
    arrived_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '到达时间',
    started_at DATETIME NULL COMMENT '开始处理时间',
    completed_at DATETIME NULL COMMENT '完成时间',
    deadline DATETIME NULL COMMENT '截止时间',
    is_timeout BOOLEAN DEFAULT FALSE COMMENT '是否超时',
    
    -- 处理结果
    result ENUM('pending', 'approved', 'rejected', 'completed', 'rolled_back') NULL COMMENT '处理结果',
    comments VARCHAR(1000) NULL COMMENT '处理意见',
    
    -- 审批信息（如果是审批步骤）
    require_approval BOOLEAN DEFAULT FALSE COMMENT '是否需要审批',
    approval_status ENUM('pending', 'approved', 'rejected') NULL COMMENT '审批状态',
    
    -- 附件信息
    attachments TEXT NULL COMMENT '附件（JSON数组）',
    
    -- 审计字段
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_ticket_id (ticket_id),
    INDEX idx_step_id (step_id),
    INDEX idx_status (status),
    INDEX idx_assignee_staff_id (assignee_staff_id),
    INDEX idx_deadline (deadline),
    INDEX idx_previous_instance_id (previous_instance_id),
    
    FOREIGN KEY (ticket_id) REFERENCES ticket(ticket_id),
    FOREIGN KEY (step_id) REFERENCES workflow_steps(step_id),
    FOREIGN KEY (assignee_staff_id) REFERENCES enterprise_staff(staff_id),
    FOREIGN KEY (previous_instance_id) REFERENCES ticket_step_instances(instance_id)
) COMMENT='工单步骤实例表';
```

**步骤状态说明**：
- `pending`：待处理
- `in_progress`：处理中
- `completed`：已完成
- `rejected`：已拒绝
- `skipped`：已跳过
- `rolled_back`：已回退（假删除状态）

**回退处理示例**：
```
原始流程：
Instance 1 (step 1) -> Instance 2 (step 2) -> Instance 3 (step 3)

回退到step 2：
Instance 3 状态变为 rolled_back

重新流转：
Instance 3 (rolled_back) -> Instance 4 (step 3, previous_instance_id=3)
```

#### 3.7.3 工单审批记录表（ticket_approval_records）

**重要改进**：支持多人审批，每个审批人一条记录

```sql
CREATE TABLE ticket_approval_records (
    approval_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    ticket_id INT NOT NULL COMMENT '工单ID',
    ticket_no VARCHAR(50) NOT NULL COMMENT '工单编号',
    step_id INT NOT NULL COMMENT '步骤ID',
    step_name VARCHAR(100) NOT NULL COMMENT '步骤名称',
    instance_id BIGINT NOT NULL COMMENT '步骤实例ID',
    
    -- 审批人信息
    approver_account_id INT NOT NULL COMMENT '审批人账号ID',
    approver_staff_id INT NOT NULL COMMENT '审批人人员ID',
    approver_name VARCHAR(100) NOT NULL COMMENT '审批人姓名',
    approver_role VARCHAR(100) NOT NULL COMMENT '审批人角色',
    
    -- 审批结果
    approval_result ENUM('pending', 'approved', 'rejected') DEFAULT 'pending' NOT NULL COMMENT '审批结果',
    approval_comments VARCHAR(1000) NULL COMMENT '审批意见',
    approval_time DATETIME NULL COMMENT '审批时间',
    
    -- 审批类型（从步骤配置复制）
    approval_type ENUM('any', 'all') NOT NULL COMMENT '审批类型：any=任一通过, all=全部通过',
    
    -- 附件信息
    attachments TEXT NULL COMMENT '附件（JSON数组）',
    
    -- 审计字段
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间（提交审批时间）',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_ticket_id (ticket_id),
    INDEX idx_ticket_no (ticket_no),
    INDEX idx_step_id (step_id),
    INDEX idx_instance_id (instance_id),
    INDEX idx_approver_staff_id (approver_staff_id),
    INDEX idx_approval_result (approval_result),
    INDEX idx_approval_time (approval_time),
    
    FOREIGN KEY (ticket_id) REFERENCES ticket(ticket_id),
    FOREIGN KEY (step_id) REFERENCES workflow_steps(step_id),
    FOREIGN KEY (instance_id) REFERENCES ticket_step_instances(instance_id),
    FOREIGN KEY (approver_staff_id) REFERENCES enterprise_staff(staff_id)
) COMMENT='工单审批记录表（支持多人审批）';
```

**审批逻辑说明**：

1. **any模式（任一通过）**：
   - 为每个审批人创建一条记录
   - 任意一人审批通过，步骤即可流转
   - 其他人的审批记录保持pending状态

2. **all模式（全部通过）**：
   - 为每个审批人创建一条记录
   - 必须所有人都审批通过才能流转
   - 任意一人拒绝，审批失败

#### 3.7.4 工单流转日志表（ticket_flow_logs）

```sql
CREATE TABLE ticket_flow_logs (
    log_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    ticket_id INT NOT NULL COMMENT '工单ID',
    ticket_no VARCHAR(50) NOT NULL COMMENT '工单编号',
    
    -- 流转信息
    from_step_id INT NULL COMMENT '来源步骤ID',
    from_step_name VARCHAR(100) NULL COMMENT '来源步骤名称',
    to_step_id INT NOT NULL COMMENT '目标步骤ID',
    to_step_name VARCHAR(100) NOT NULL COMMENT '目标步骤名称',
    
    -- 实例信息
    from_instance_id BIGINT NULL COMMENT '来源步骤实例ID',
    to_instance_id BIGINT NULL COMMENT '目标步骤实例ID',
    
    -- 操作信息
    action ENUM('forward', 'rollback_to_previous', 'rollback_to_start', 'terminate', 'complete') NOT NULL COMMENT '操作类型：forward=向前流转, rollback_to_previous=回退到上一步, rollback_to_start=回退到开始, terminate=终止, complete=完成',
    operator_account_id INT NOT NULL COMMENT '操作人账号ID',
    operator_staff_id INT NOT NULL COMMENT '操作人人员ID',
    operator_name VARCHAR(100) NOT NULL COMMENT '操作人姓名',
    operator_role VARCHAR(100) NOT NULL COMMENT '操作人角色',
    operator_type ENUM('creator', 'approver', 'operator') NOT NULL COMMENT '操作人类型：creator=创建者, approver=审核人员, operator=操作人员',
    
    -- 流转验证
    validation_passed BOOLEAN DEFAULT TRUE COMMENT '流转验证是否通过',
    validation_errors TEXT NULL COMMENT '验证失败原因（JSON数组）',
    conditions_checked TEXT NULL COMMENT '检查的条件（JSON数组）',
    
    -- 审批信息（如果涉及审批）
    require_approval BOOLEAN DEFAULT FALSE COMMENT '是否需要审批',
    approval_passed BOOLEAN NULL COMMENT '审批是否通过',
    
    -- 操作说明
    operation_comments VARCHAR(1000) NULL COMMENT '操作说明/原因',
    
    -- 时间信息
    operation_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    duration_minutes INT NULL COMMENT '在当前步骤停留时长（分钟）',
    
    -- 附加信息
    ip_address VARCHAR(50) NULL COMMENT '操作IP',
    user_agent VARCHAR(500) NULL COMMENT '用户代理',
    attachments TEXT NULL COMMENT '附件（JSON数组）',
    
    INDEX idx_ticket_id (ticket_id),
    INDEX idx_ticket_no (ticket_no),
    INDEX idx_operator_staff_id (operator_staff_id),
    INDEX idx_operation_time (operation_time),
    INDEX idx_action (action),
    INDEX idx_from_step_id (from_step_id),
    INDEX idx_to_step_id (to_step_id),
    
    FOREIGN KEY (ticket_id) REFERENCES ticket(ticket_id),
    FOREIGN KEY (from_step_id) REFERENCES workflow_steps(step_id),
    FOREIGN KEY (to_step_id) REFERENCES workflow_steps(step_id),
    FOREIGN KEY (operator_staff_id) REFERENCES enterprise_staff(staff_id)
) COMMENT='工单流转日志表';
```

---

## 四、核心业务流程详解

### 4.1 工单创建流程

```
1. 企业人员登录系统
   ↓
2. 选择工单类型（对应workflow_definitions）
   ↓
3. 填写工单信息
   - 作业内容
   - 作业时间
   - 作业区域
   - 作业人员（承包商人员）
   - 监护人员（企业人员）
   ↓
4. 系统生成工单编号（TK + YYYYMMDD + 序号）
   ↓
5. 创建工单记录（ticket表）
   - status = 'in_progress'
   - current_step_id = 流程第一步
   ↓
6. 创建第一个步骤实例（ticket_step_instances表）
   ↓
7. 如果第一步需要审批，创建审批记录
   ↓
8. 记录流转日志
```

### 4.2 工单审批流程

#### 4.2.1 any模式（任一审批通过）

```
步骤到达
   ↓
系统查找审批角色对应的所有人员
   ↓
为每个审批人创建一条审批记录（approval_result='pending'）
   ↓
审批人A登录 → 查看工单 → 审批通过
   ↓
更新审批人A的记录（approval_result='approved'）
   ↓
检查审批模式：approval_type='any'
   ↓
任一通过即可 → 步骤状态变为'completed'
   ↓
可以流转到下一步
   ↓
其他审批人的记录保持'pending'（留作记录）
```

#### 4.2.2 all模式（全部审批通过）

```
步骤到达
   ↓
系统查找审批角色对应的所有人员
   ↓
为每个审批人创建一条审批记录（approval_result='pending'）
   ↓
审批人A登录 → 审批通过
审批人B登录 → 审批通过
审批人C登录 → 审批通过
   ↓
检查审批模式：approval_type='all'
   ↓
检查所有审批记录是否都为'approved'
   ↓
是 → 步骤状态变为'completed' → 可以流转
否 → 继续等待其他人审批
   ↓
如果任意一人拒绝 → 审批失败 → 步骤状态变为'rejected'
```

### 4.3 步骤回退流程

#### 4.3.1 回退到上一步

```
1. 操作人发起回退请求
   ↓
2. 验证权限
   - 创建者：允许
   - 审核人员：允许
   - 当前步骤操作人：允许
   ↓
3. 获取当前步骤的previous_step_id
   ↓
4. 更新当前步骤实例状态为'rolled_back'
   ↓
5. 查找上一步骤实例，恢复为'in_progress'
   ↓
6. 更新工单的current_step_id为上一步骤
   ↓
7. 记录流转日志（action='rollback_to_previous'）
   ↓
8. 如果上一步需要审批，恢复审批记录状态
```

#### 4.3.2 回退到开始

```
1. 操作人发起回退到开始请求
   ↓
2. 验证权限
   ↓
3. 将当前步骤及之后所有步骤实例状态设为'rolled_back'
   ↓
4. 查找流程的开始步骤（step_type='start'）
   ↓
5. 创建新的开始步骤实例
   ↓
6. 更新工单的current_step_id为开始步骤
   ↓
7. 记录流转日志（action='rollback_to_start'）
```

#### 4.3.3 回退后重新流转

```
从回退后的步骤重新开始
   ↓
操作人完成当前步骤
   ↓
流转到下一步
   ↓
创建新的步骤实例（previous_instance_id指向被回退的实例）
   ↓
原有的rolled_back记录保持不变
   ↓
新记录状态为'in_progress'
```

### 4.4 工单终止流程

```
1. 操作人发起终止请求
   ↓
2. 验证权限
   - 仅创建者和审核人员可终止
   ↓
3. 更新工单状态
   - status = 'terminated'
   - is_terminated = TRUE
   - terminated_at = 当前时间
   - terminated_by_staff_id = 操作人ID
   - termination_reason = 终止原因
   ↓
4. 当前步骤实例状态不变（保留现场）
   ↓
5. 记录流转日志（action='terminate'）
   ↓
6. 工单不可再流转（除非修改数据库）
```

### 4.5 企业数据隔离验证

```
用户登录
   ↓
获取用户的enterprise_id
   ↓
查询工单列表
   ↓
WHERE enterprise_id = 用户的enterprise_id
   ↓
审批工单
   ↓
验证：工单的enterprise_id == 用户的enterprise_id
   ↓
不匹配 → 拒绝操作
匹配 → 允许操作
```

---

## 五、权限管理详解

### 5.1 权限体系架构

```
系统预定义权限（permissions表）
   ↓
企业创建自定义角色（roles表）
   ↓
企业为角色绑定权限（role_permissions表）
   ↓
为人员分配角色（enterprise_staff.role_id）
   ↓
人员获得角色的所有权限
```

### 5.2 权限检查流程

```python
def check_permission(user, permission_code):
    """
    检查用户是否有指定权限
    
    参数:
        user: 用户对象
        permission_code: 权限编码（如：'ticket.approve'）
    
    返回:
        Boolean: True=有权限, False=无权限
    """
    # 1. 获取用户的角色
    role = get_role(user.role_id)
    
    # 2. 获取角色的所有权限
    permissions = get_role_permissions(role.role_id)
    
    # 3. 检查是否包含指定权限
    return permission_code in [p.permission_code for p in permissions]
```

### 5.3 企业自定义角色示例

```sql
-- 企业A创建自定义角色："安全主管"
INSERT INTO roles (role_code, role_name, role_type, enterprise_id, description)
VALUES ('safety_supervisor', '安全主管', 'enterprise', 1, '负责安全审批');

-- 为该角色绑定权限
INSERT INTO role_permissions (role_id, permission_id)
SELECT 
    (SELECT role_id FROM roles WHERE role_code='safety_supervisor' AND enterprise_id=1),
    permission_id
FROM permissions
WHERE permission_code IN (
    'ticket.read',
    'ticket.approve',
    'ticket.terminate',
    'ticket.rollback'
);

-- 为人员分配角色
UPDATE enterprise_staff
SET role_id = (SELECT role_id FROM roles WHERE role_code='safety_supervisor' AND enterprise_id=1)
WHERE staff_id = 100;
```

---

## 六、数据迁移方案

### 6.1 迁移策略

1. **阶段一：新表创建**
   - 创建所有新表结构
   - 不影响现有业务

2. **阶段二：数据迁移**
   - 迁移企业数据
   - 迁移人员数据
   - 迁移工单数据

3. **阶段三：验证测试**
   - 数据完整性验证
   - 业务功能测试

4. **阶段四：切换上线**
   - 停止旧系统
   - 启用新系统
   - 保留旧表备份

### 6.2 企业承包商关系迁移

```sql
-- 从contractor_project表迁移到enterprise_contractor_relation表
INSERT INTO enterprise_contractor_relation (
    enterprise_id,
    contractor_id,
    cooperation_start_date,
    contract_no,
    status,
    created_at
)
SELECT 
    company_id as enterprise_id,
    contractor_id,
    COALESCE(start_date, CURRENT_DATE) as cooperation_start_date,
    project_name as contract_no,
    'active' as status,
    created_at
FROM contractor_project
WHERE is_deleted = FALSE;
```

### 6.3 权限数据迁移

```sql
-- 1. 创建系统预定义权限
-- （见3.5.1节）

-- 2. 创建系统预置角色
-- （见3.5.2节）

-- 3. 为系统角色分配默认权限
-- 企业管理员角色
INSERT INTO role_permissions (role_id, permission_id)
SELECT 
    (SELECT role_id FROM roles WHERE role_code='enterprise_admin'),
    permission_id
FROM permissions
WHERE category IN ('工单管理', '用户管理', '角色管理');

-- 企业审批员角色
INSERT INTO role_permissions (role_id, permission_id)
SELECT 
    (SELECT role_id FROM roles WHERE role_code='enterprise_approver'),
    permission_id
FROM permissions
WHERE permission_code IN ('ticket.read', 'ticket.approve', 'ticket.rollback', 'ticket.terminate');

-- 企业普通员工角色
INSERT INTO role_permissions (role_id, permission_id)
SELECT 
    (SELECT role_id FROM roles WHERE role_code='enterprise_staff'),
    permission_id
FROM permissions
WHERE permission_code IN ('ticket.read', 'ticket.create');
```

---

## 七、API接口设计

### 7.1 工单管理接口

#### 7.1.1 创建工单

```
POST /api/tickets/

Request Body:
{
    "workflow_id": 1,
    "area_id": 10,
    "working_content": "设备维修",
    "pre_st": "2025-01-05 08:00:00",
    "pre_et": "2025-01-05 18:00:00",
    "worker_staff_id": 100,
    "custodian_staff_id": 200,
    ...
}

Response:
{
    "code": 200,
    "message": "success",
    "data": {
        "ticket_id": 1001,
        "ticket_no": "TK20250105001",
        "status": "in_progress",
        "current_step": {
            "step_id": 1,
            "step_name": "填写工单"
        }
    }
}
```

#### 7.1.2 工单流转

```
POST /api/tickets/{ticket_id}/flow/

Request Body:
{
    "action": "forward",  // forward, rollback_to_previous, rollback_to_start
    "comments": "审批通过"
}

Response:
{
    "code": 200,
    "message": "success",
    "data": {
        "ticket_id": 1001,
        "current_step": {
            "step_id": 2,
            "step_name": "部门审批"
        }
    }
}
```

#### 7.1.3 审批工单

```
POST /api/tickets/{ticket_id}/approve/

Request Body:
{
    "approval_result": "approved",  // approved, rejected
    "approval_comments": "同意"
}

Response:
{
    "code": 200,
    "message": "success",
    "data": {
        "approval_id": 5001,
        "approval_result": "approved",
        "can_flow_next": true  // 是否可以流转到下一步
    }
}
```

#### 7.1.4 终止工单

```
POST /api/tickets/{ticket_id}/terminate/

Request Body:
{
    "termination_reason": "作业条件不满足"
}

Response:
{
    "code": 200,
    "message": "success",
    "data": {
        "ticket_id": 1001,
        "status": "terminated",
        "terminated_at": "2025-01-05 10:30:00"
    }
}
```

### 7.2 角色权限接口

#### 7.2.1 创建角色

```
POST /api/roles/

Request Body:
{
    "role_code": "safety_supervisor",
    "role_name": "安全主管",
    "description": "负责安全审批"
}

Response:
{
    "code": 200,
    "message": "success",
    "data": {
        "role_id": 101,
        "role_code": "safety_supervisor",
        "role_name": "安全主管"
    }
}
```

#### 7.2.2 为角色分配权限

```
POST /api/roles/{role_id}/permissions/

Request Body:
{
    "permission_ids": [1, 2, 3, 5, 7]
}

Response:
{
    "code": 200,
    "message": "success",
    "data": {
        "role_id": 101,
        "permissions_count": 5
    }
}
```

#### 7.2.3 获取权限列表

```
GET /api/permissions/?category=工单管理

Response:
{
    "code": 200,
    "message": "success",
    "data": [
        {
            "permission_id": 1,
            "permission_code": "ticket.create",
            "permission_name": "创建工单",
            "category": "工单管理"
        },
        {
            "permission_id": 2,
            "permission_code": "ticket.approve",
            "permission_name": "审批工单",
            "category": "工单管理"
        },
        ...
    ]
}
```

---

## 八、实施计划

### 8.1 实施阶段

#### 阶段一：数据库改造（2周）

**任务**：
1. 创建新表结构
2. 添加索引和外键
3. 初始化系统数据（权限、角色）

**交付物**：
- SQL建表脚本
- 数据初始化脚本
- 数据库设计文档

#### 阶段二：后端开发（4周）

**任务**：
1. 实现工单流程引擎
2. 实现审批机制
3. 实现回退机制
4. 实现权限验证
5. 实现数据隔离

**交付物**：
- API接口代码
- 单元测试
- 接口文档

#### 阶段三：数据迁移（1周）

**任务**：
1. 编写数据迁移脚本
2. 测试环境迁移
3. 数据验证

**交付物**：
- 数据迁移脚本
- 迁移验证报告

#### 阶段四：测试上线（2周）

**任务**：
1. 功能测试
2. 性能测试
3. 生产环境部署
4. 用户培训

**交付物**：
- 测试报告
- 部署文档
- 用户手册

### 8.2 风险控制

#### 风险1：数据迁移失败

**应对措施**：
- 完整备份现有数据
- 在测试环境多次演练
- 准备回滚方案

#### 风险2：性能问题

**应对措施**：
- 添加必要索引
- 优化查询语句
- 实施数据分区

#### 风险3：业务中断

**应对措施**：
- 选择业务低峰期迁移
- 准备应急预案
- 保留旧系统备份

---

## 九、附录

### 9.1 工单编号生成规则

```python
def generate_ticket_no(apply_date):
    """
    生成工单编号
    
    格式：TK + YYYYMMDD + 6位序号
    示例：TK20250105000001
    """
    date_str = apply_date.strftime('%Y%m%d')
    
    # 查询当天最大序号
    max_no = db.query(
        "SELECT MAX(CAST(SUBSTRING(ticket_no, 11) AS UNSIGNED)) as max_seq "
        "FROM ticket "
        f"WHERE ticket_no LIKE 'TK{date_str}%'"
    )
    
    next_seq = (max_no['max_seq'] or 0) + 1
    
    return f"TK{date_str}{next_seq:06d}"
```

### 9.2 审批通过判断逻辑

```python
def check_approval_passed(ticket_id, step_id, instance_id):
    """
    检查审批是否通过
    
    返回:
        (Boolean, String): (是否通过, 原因)
    """
    # 1. 获取步骤配置
    step = get_workflow_step(step_id)
    
    if not step.require_approval:
        return True, "不需要审批"
    
    # 2. 获取所有审批记录
    approvals = get_approval_records(ticket_id, step_id, instance_id)
    
    if step.approval_type == 'any':
        # 任一通过模式
        approved_count = sum(1 for a in approvals if a.approval_result == 'approved')
        if approved_count > 0:
            return True, "任一审批通过"
        else:
            return False, "等待审批"
    
    elif step.approval_type == 'all':
        # 全部通过模式
        total_count = len(approvals)
        approved_count = sum(1 for a in approvals if a.approval_result == 'approved')
        rejected_count = sum(1 for a in approvals if a.approval_result == 'rejected')
        
        if rejected_count > 0:
            return False, "审批被拒绝"
        elif approved_count == total_count:
            return True, "全部审批通过"
        else:
            return False, f"等待审批（{approved_count}/{total_count}）"
```

### 9.3 回退逻辑实现

```python
async def rollback_ticket_step(ticket_id, action, operator):
    """
    回退工单步骤
    
    参数:
        ticket_id: 工单ID
        action: 'rollback_to_previous' 或 'rollback_to_start'
        operator: 操作人对象
    """
    # 1. 获取工单
    ticket = await get_ticket(ticket_id)
    current_step = await get_workflow_step(ticket.current_step_id)
    
    # 2. 验证权限
    if not check_rollback_permission(ticket, operator):
        raise PermissionError("没有回退权限")
    
    # 3. 获取当前步骤实例
    current_instance = await get_current_step_instance(ticket_id)
    
    if action == 'rollback_to_previous':
        # 回退到上一步
        if not current_step.previous_step_id:
            raise ValueError("已经是第一步，无法回退")
        
        # 标记当前实例为rolled_back
        current_instance.status = 'rolled_back'
        current_instance.result = 'rolled_back'
        
        # 获取上一步骤
        previous_step = await get_workflow_step(current_step.previous_step_id)
        
        # 查找上一步骤实例
        previous_instance = await get_step_instance(ticket_id, previous_step.step_id)
        
        # 恢复上一步骤实例状态
        previous_instance.status = 'in_progress'
        previous_instance.completed_at = None
        
        # 更新工单当前步骤
        ticket.current_step_id = previous_step.step_id
        
        # 记录日志
        await log_ticket_flow(
            ticket_id=ticket_id,
            from_step=current_step,
            to_step=previous_step,
            from_instance_id=current_instance.instance_id,
            to_instance_id=previous_instance.instance_id,
            action='rollback_to_previous',
            operator=operator
        )
        
    elif action == 'rollback_to_start':
        # 回退到开始
        # 获取开始步骤
        start_step = await get_start_step(ticket.workflow_id)
        
        # 标记当前及后续所有实例为rolled_back
        await mark_instances_rolled_back(ticket_id, current_step.step_order)
        
        # 创建新的开始步骤实例
        new_instance = await create_step_instance(
            ticket_id=ticket_id,
            step_id=start_step.step_id,
            status='in_progress'
        )
        
        # 更新工单当前步骤
        ticket.current_step_id = start_step.step_id
        
        # 记录日志
        await log_ticket_flow(
            ticket_id=ticket_id,
            from_step=current_step,
            to_step=start_step,
            from_instance_id=current_instance.instance_id,
            to_instance_id=new_instance.instance_id,
            action='rollback_to_start',
            operator=operator
        )
    
    await session.commit()
```

### 9.4 企业数据隔离中间件

```python
class EnterpriseIsolationMiddleware:
    """
    企业数据隔离中间件
    确保用户只能访问本企业的数据
    """
    
    async def __call__(self, request, call_next):
        # 获取当前用户
        user = request.state.user
        
        # 如果是管理员，跳过隔离
        if user.user_type == 'admin':
            return await call_next(request)
        
        # 如果是企业用户，添加enterprise_id过滤
        if user.user_type == 'enterprise_staff':
            request.state.enterprise_id = user.enterprise_id
        
        response = await call_next(request)
        return response

# 在查询中使用
async def get_tickets(request):
    """获取工单列表"""
    query = select(Ticket).where(Ticket.is_deleted == False)
    
    # 应用企业隔离
    if hasattr(request.state, 'enterprise_id'):
        query = query.where(Ticket.enterprise_id == request.state.enterprise_id)
    
    tickets = await session.execute(query)
    return tickets.scalars().all()
```

---

## 十、总结

### 10.1 核心改进点

1. ✅ **多对多关系**：通过 `enterprise_contractor_relation` 表实现企业与承包商的多对多合作关系
2. ✅ **步骤回退机制**：只能回退到上一步或开始，通过 `previous_step_id` 实现
3. ✅ **多人审批**：支持any和all两种模式，每个审批人独立记录
4. ✅ **角色权限分离**：企业可自定义角色并绑定权限
5. ✅ **企业数据隔离**：确保企业间数据安全隔离
6. ✅ **完整的审计日志**：记录所有关键操作

### 10.2 技术优势

1. **灵活性**：流程可配置，角色可定制
2. **可扩展性**：支持未来业务扩展
3. **安全性**：数据隔离，权限控制
4. **可追溯性**：完整的操作日志
5. **易维护性**：表结构清晰，职责明确

### 10.3 业务价值

1. **提升效率**：自动化流程，减少人工干预
2. **降低风险**：审批流程规范，责任可追溯
3. **增强管控**：企业数据隔离，权限精细化
4. **便于管理**：角色自定义，灵活适配业务

---

**文档结束**

**版本**：v2.0  
**日期**：2025-01-04  
**作者**：AI Assistant

