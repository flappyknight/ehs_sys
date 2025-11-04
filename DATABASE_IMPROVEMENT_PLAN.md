# 数据库表结构改进方案

## 一、概述

本方案基于当前EHS系统的数据库设计，针对用户管理、角色权限、工单流程等核心功能提出全面的改进建议。

---

## 二、核心改进原则

1. **四个独立主体**：甲方企业、承包商企业、企业人员、承包商人员完全独立管理
2. **主体分离**：企业和承包商企业是两个不同的实体，各有独立的表结构
3. **账号体系独立**：管理员、企业人员、承包商人员各有独立的账号表
4. **软删除机制**：所有表采用软删除，保留历史数据
5. **操作审计**：关键操作记录完整的审计日志
6. **工单流程化**：支持复杂流程（长流程、分支、审核、多级回退）
7. **权限细粒度**：角色权限与主体关联，支持企业级权限定制
8. **流转条件验证**：每步流转前验证条件（审核状态、完成状态等），记录完整历史
9. **灵活回退机制**：支持回退到上一步、回退到开始、终止工单

---

## 三、业务主体说明

### 3.1 四个独立主体

```
系统主体架构
├── 1. 系统管理员（admin_account）
│   └── 系统最高权限，管理所有资源
│
├── 2. 甲方企业（enterprise）
│   ├── 部门（department）
│   ├── 厂区（area）
│   └── 工单流程定义（workflow_definitions）
│
├── 3. 企业人员（enterprise_staff + enterprise_staff_account）
│   ├── 所属甲方企业
│   ├── 创建工单
│   ├── 审批工单
│   ├── 流转工单
│   ├── 监护作业
│   └── 终止/删除工单（仅创建者和审核人员）
│
├── 4. 承包商企业（contractor）
│   ├── 与甲方企业合作（contractor_project）
│   └── 营业执照等企业资质
│
└── 5. 承包商人员（contractor_staff + contractor_staff_account）
    ├── 所属承包商企业
    ├── 登记进场
    ├── 执行作业
    └── 操作工单步骤
```

### 3.2 业务流程说明

**工单流程核心规则**：
1. **工单创建**：由企业人员创建，定义作业内容和流程
2. **工单流转**：
   - 每步流转必须上一步已完成
   - 部分步骤需要高级别人员审核通过才能流转
   - 流转前验证条件（审核状态、完成状态、权限等）
3. **回退机制**：
   - 工单创建者：可回退任意步骤、返回开始、终止工单
   - 工单审核人员：可回退任意步骤、返回开始、终止工单
   - 工单操作人员：可回退到上一步、返回开始
4. **工单状态**：
   - `in_progress`：进行中（默认状态）
   - `completed`：已完成
   - `terminated`：已终止（人为终止）
5. **权限控制**：
   - 终止工单：仅创建者和审核人员
   - 删除工单：仅创建者和审核人员
   - 回退工单：创建者、审核人员、当前操作人员

### 3.3 主体关系图

```
甲方企业（enterprise）
  ├── 企业人员（enterprise_staff）
  │     └── 账号（enterprise_staff_account）
  ├── 部门（department）
  ├── 厂区（area）
  └── 工单流程（workflow_definitions）
        └── 流程步骤（workflow_steps）

承包商企业（contractor）
  ├── 承包商人员（contractor_staff）
  │     └── 账号（contractor_staff_account）
  └── 合作项目（contractor_project）
        └── 进场计划（entry_plan）

工单（ticket）
  ├── 创建者：企业人员
  ├── 关联流程：workflow_definitions
  ├── 当前步骤：workflow_steps
  ├── 流转日志：ticket_flow_logs
  ├── 步骤实例：ticket_step_instances
  └── 审核记录：ticket_approval_records
```

**关键说明**：
1. 甲方企业和承包商企业是完全独立的两个实体
2. 企业人员和承包商人员各有独立的账号体系
3. 工单由企业人员创建和管理
4. 承包商人员按照企业定义的流程执行作业
5. 工单流程支持复杂的分支、审核、回退逻辑

---

## 四、表结构改进方案

### 4.1 甲方企业表（enterprise）- 新建

**目的**：管理甲方企业信息

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

---

### 4.2 承包商企业表（contractor）- 重构

**改进要点**：
- 独立管理承包商企业
- 添加完整的企业资质信息
- 添加软删除和审计字段

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

---

### 4.3 系统管理员账号表（admin_account）- 新增

**目的**：系统管理员独立的账号体系

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

---

### 4.4 企业人员账号表（enterprise_staff_account）- 新增

**目的**：企业人员独立的账号体系

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

---

### 4.5 承包商人员账号表（contractor_staff_account）- 新增

**目的**：承包商人员独立的账号体系

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

---

### 4.6 账号变更日志表（account_change_logs）- 新增

**目的**：记录所有账号的变更操作

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

---

### 4.7 企业人员信息表（enterprise_staff）- 改进

**改进要点**：
- 独立管理企业人员信息
- 关联角色表
- 添加软删除和审计字段

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
    approval_level INT DEFAULT 4 COMMENT '审批级别（1-4，数字越小权限越高，1=最高审批权）',
    
    -- 工单权限标识
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
    INDEX idx_approval_level (approval_level),
    
    FOREIGN KEY (enterprise_id) REFERENCES enterprise(enterprise_id),
    FOREIGN KEY (dept_id) REFERENCES department(dept_id),
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
) COMMENT='企业人员信息表';
```

---

### 4.8 承包商人员信息表（contractor_staff）- 改进

**改进要点**：
- 独立管理承包商人员信息
- 关联角色表
- 添加软删除和审计字段

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

---

### 4.9 部门表（department）- 改进

**改进要点**：
- 关联甲方企业
- 添加软删除

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

---

### 4.10 厂区表（area）- 改进

**改进要点**：
- 关联甲方企业和部门
- 添加软删除

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

---

### 4.11 角色表（roles）- 新增

**目的**：统一管理角色定义，支持企业级角色定制

```sql
CREATE TABLE roles (
    role_id INT PRIMARY KEY AUTO_INCREMENT,
    role_code VARCHAR(50) UNIQUE NOT NULL COMMENT '角色编码（系统唯一）',
    role_name VARCHAR(100) NOT NULL COMMENT '角色名称',
    role_type ENUM('system', 'enterprise', 'contractor') NOT NULL COMMENT '角色类型',
    
    -- 关联信息
    enterprise_id INT NULL COMMENT '所属企业ID（企业自定义角色时使用）',
    parent_role_id INT NULL COMMENT '父角色ID（继承权限）',
    
    -- 权限级别
    permission_level INT NOT NULL COMMENT '权限级别（数字越小权限越高）',
    
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
    
    INDEX idx_role_code (role_code),
    INDEX idx_role_type (role_type),
    INDEX idx_enterprise_id (enterprise_id),
    INDEX idx_is_deleted (is_deleted),
    
    FOREIGN KEY (enterprise_id) REFERENCES enterprise(enterprise_id),
    FOREIGN KEY (parent_role_id) REFERENCES roles(role_id)
) COMMENT='角色表';
```

**系统预置角色示例**：
```sql
-- 管理员角色
INSERT INTO roles (role_code, role_name, role_type, permission_level, is_system, description) 
VALUES ('admin', '系统管理员', 'system', 0, TRUE, '系统最高权限');

-- 企业角色
INSERT INTO roles (role_code, role_name, role_type, permission_level, is_system, description) 
VALUES 
('enterprise_manager', '企业管理员', 'enterprise', 1, TRUE, '企业最高权限，可管理企业所有资源'),
('enterprise_approver', '企业审批员', 'enterprise', 2, TRUE, '可审批工单'),
('enterprise_staff', '企业普通员工', 'enterprise', 3, TRUE, '可查看和创建工单');

-- 承包商角色
INSERT INTO roles (role_code, role_name, role_type, permission_level, is_system, description) 
VALUES 
('contractor_manager', '承包商管理员', 'contractor', 1, TRUE, '承包商最高权限'),
('contractor_approver', '承包商审批员', 'contractor', 2, TRUE, '可审批计划'),
('contractor_worker', '承包商普通员工', 'contractor', 3, TRUE, '普通作业人员');
```

---

### 3.6 角色权限表（role_permissions）- 新增

**目的**：定义角色具体拥有的权限

```sql
CREATE TABLE role_permissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    role_id INT NOT NULL COMMENT '角色ID',
    permission_code VARCHAR(100) NOT NULL COMMENT '权限编码',
    resource_type VARCHAR(50) NOT NULL COMMENT '资源类型（如：ticket, user, project等）',
    action VARCHAR(50) NOT NULL COMMENT '操作类型（如：create, read, update, delete, approve等）',
    
    -- 审计字段
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NULL,
    
    UNIQUE KEY uk_role_permission (role_id, permission_code),
    INDEX idx_role_id (role_id),
    INDEX idx_resource_type (resource_type),
    
    FOREIGN KEY (role_id) REFERENCES roles(role_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id)
) COMMENT='角色权限表';
```

**权限编码示例**：
```sql
-- 工单权限
INSERT INTO role_permissions (role_id, permission_code, resource_type, action) VALUES
(2, 'ticket.create', 'ticket', 'create'),
(2, 'ticket.read', 'ticket', 'read'),
(2, 'ticket.update', 'ticket', 'update'),
(2, 'ticket.delete', 'ticket', 'delete'),
(2, 'ticket.approve', 'ticket', 'approve'),
(2, 'ticket.reject', 'ticket', 'reject');
```

---

### 3.7 工单流程定义表（workflow_definitions）- 新增

**目的**：定义工单的流程模板

```sql
CREATE TABLE workflow_definitions (
    workflow_id INT PRIMARY KEY AUTO_INCREMENT,
    workflow_code VARCHAR(50) UNIQUE NOT NULL COMMENT '流程编码',
    workflow_name VARCHAR(100) NOT NULL COMMENT '流程名称',
    workflow_type VARCHAR(50) NOT NULL COMMENT '流程类型（如：ticket_approval）',
    
    -- 关联信息
    company_id INT NULL COMMENT '所属企业ID（NULL表示系统通用流程）',
    
    -- 流程配置
    description VARCHAR(500) NULL COMMENT '流程描述',
    version INT DEFAULT 1 COMMENT '流程版本号',
    
    -- 状态管理
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL COMMENT '软删除标记',
    
    -- 审计字段
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT NULL,
    deleted_at DATETIME NULL,
    deleted_by INT NULL,
    
    INDEX idx_workflow_code (workflow_code),
    INDEX idx_company_id (company_id),
    INDEX idx_is_active (is_active),
    INDEX idx_is_deleted (is_deleted),
    
    FOREIGN KEY (company_id) REFERENCES company(company_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id),
    FOREIGN KEY (updated_by) REFERENCES users(user_id),
    FOREIGN KEY (deleted_by) REFERENCES users(user_id)
) COMMENT='工单流程定义表';
```

---

### 4.14 工单流程步骤表（workflow_steps）- 新增

**目的**：定义流程的具体步骤，支持复杂流程、分支、审核、多级回退

```sql
CREATE TABLE workflow_steps (
    step_id INT PRIMARY KEY AUTO_INCREMENT,
    workflow_id INT NOT NULL COMMENT '所属流程ID',
    step_code VARCHAR(50) NOT NULL COMMENT '步骤编码',
    step_name VARCHAR(100) NOT NULL COMMENT '步骤名称',
    step_order INT NOT NULL COMMENT '步骤顺序',
    
    -- 步骤类型
    step_type ENUM('start', 'operation', 'approval', 'notify', 'end') NOT NULL COMMENT '步骤类型：start=开始, operation=操作步骤, approval=审批步骤, notify=通知步骤, end=结束',
    
    -- 审批配置
    require_approval BOOLEAN DEFAULT FALSE COMMENT '是否需要审批',
    approver_role_id INT NULL COMMENT '审批角色ID',
    approval_level INT NULL COMMENT '需要的审批级别（1-4，数字越小权限越高）',
    approval_type ENUM('any', 'all', 'sequential') DEFAULT 'any' COMMENT '审批类型：any=任一审批人, all=所有审批人, sequential=按顺序审批',
    
    -- 流转条件配置
    require_previous_completed BOOLEAN DEFAULT TRUE COMMENT '是否要求上一步已完成',
    require_previous_approved BOOLEAN DEFAULT FALSE COMMENT '是否要求上一步已审批通过',
    condition_expression TEXT NULL COMMENT '流转条件表达式（JSON格式，支持复杂条件）',
    
    -- 回退配置
    can_rollback BOOLEAN DEFAULT TRUE COMMENT '是否允许回退',
    rollback_to_previous BOOLEAN DEFAULT TRUE COMMENT '是否可以回退到上一步',
    rollback_to_start BOOLEAN DEFAULT TRUE COMMENT '是否可以回退到开始',
    rollback_allowed_roles TEXT NULL COMMENT '允许回退的角色ID列表（JSON数组）',
    
    -- 终止配置
    can_terminate BOOLEAN DEFAULT FALSE COMMENT '是否允许终止工单',
    terminate_allowed_roles TEXT NULL COMMENT '允许终止的角色ID列表（JSON数组）',
    
    -- 分支配置
    is_branch_point BOOLEAN DEFAULT FALSE COMMENT '是否为分支点',
    branch_conditions TEXT NULL COMMENT '分支条件（JSON格式：[{condition, next_step_id}]）',
    next_step_id INT NULL COMMENT '下一步骤ID（非分支时使用）',
    
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
    INDEX idx_approver_role_id (approver_role_id),
    INDEX idx_next_step_id (next_step_id),
    
    FOREIGN KEY (workflow_id) REFERENCES workflow_definitions(workflow_id),
    FOREIGN KEY (approver_role_id) REFERENCES roles(role_id),
    FOREIGN KEY (next_step_id) REFERENCES workflow_steps(step_id)
) COMMENT='工单流程步骤表（支持复杂流程、分支、审核、多级回退）';
```

**步骤类型说明**：
- `start`：开始步骤（流程起点）
- `operation`：操作步骤（需要人员执行操作）
- `approval`：审批步骤（需要审批人员审核）
- `notify`：通知步骤（自动通知相关人员）
- `end`：结束步骤（流程终点）

**流转条件示例**：
```json
{
  "require_fields": ["working_content", "worker_id"],
  "require_approval": true,
  "custom_conditions": [
    {"field": "hot_work", "operator": ">", "value": 0, "message": "动火作业需要特殊审批"}
  ]
}
```

**分支条件示例**：
```json
[
  {"condition": "hot_work > 0", "next_step_id": 10, "description": "动火作业流程"},
  {"condition": "work_height_level > 2", "next_step_id": 20, "description": "高空作业流程"},
  {"condition": "default", "next_step_id": 30, "description": "普通作业流程"}
]
```

---

### 4.15 工单表（ticket）- 重构

**改进要点**：
- 添加工单唯一编号
- 调整工单状态（只保留 in_progress 和 completed）
- 关联流程定义
- 添加当前步骤和上一步骤信息
- 记录工单创建者和审核人员
- 添加软删除和终止机制

```sql
CREATE TABLE ticket (
    ticket_id INT PRIMARY KEY AUTO_INCREMENT,
    ticket_no VARCHAR(50) UNIQUE NOT NULL COMMENT '工单编号（唯一，如：TK20250104001）',
    
    -- 流程信息
    workflow_id INT NOT NULL COMMENT '关联的流程定义ID',
    current_step_id INT NULL COMMENT '当前步骤ID',
    previous_step_id INT NULL COMMENT '上一步骤ID',
    
    -- 工单状态（简化为两种状态）
    status ENUM('in_progress', 'completed') DEFAULT 'in_progress' NOT NULL COMMENT '工单状态：in_progress=进行中, completed=已完成',
    
    -- 基本信息
    apply_date DATE NOT NULL COMMENT '申请日期',
    creator_account_id INT NOT NULL COMMENT '创建者账号ID（企业人员）',
    creator_staff_id INT NOT NULL COMMENT '创建者人员ID',
    enterprise_id INT NOT NULL COMMENT '所属企业ID',
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
    FOREIGN KEY (previous_step_id) REFERENCES workflow_steps(step_id),
    FOREIGN KEY (creator_staff_id) REFERENCES enterprise_staff(staff_id),
    FOREIGN KEY (enterprise_id) REFERENCES enterprise(enterprise_id),
    FOREIGN KEY (area_id) REFERENCES area(area_id),
    FOREIGN KEY (worker_staff_id) REFERENCES contractor_staff(staff_id),
    FOREIGN KEY (custodian_staff_id) REFERENCES enterprise_staff(staff_id)
) COMMENT='工单表（重构版：支持复杂流程、终止、软删除）';
```

**状态说明**：
- `in_progress`：进行中（默认状态，包含所有未完成的工单）
- `completed`：已完成（工单流程走完）

**终止与删除的区别**：
- **终止**：工单中途停止，保留所有记录，标记为 `is_terminated=TRUE`
- **删除**：软删除，标记为 `is_deleted=TRUE`，仅创建者和审核人员可操作

**权限控制**：
- 创建者：可回退、终止、删除工单
- 审核人员（`can_approve_ticket=TRUE`）：可回退、终止、删除工单
- 操作人员：可回退到上一步或开始

---

### 4.16 工单审批记录表（ticket_approval_records）- 新增

**目的**：记录工单每个步骤的审批情况

```sql
CREATE TABLE ticket_approval_records (
    approval_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    ticket_id INT NOT NULL COMMENT '工单ID',
    ticket_no VARCHAR(50) NOT NULL COMMENT '工单编号',
    step_id INT NOT NULL COMMENT '步骤ID',
    step_name VARCHAR(100) NOT NULL COMMENT '步骤名称',
    
    -- 审批人信息
    approver_account_id INT NOT NULL COMMENT '审批人账号ID',
    approver_staff_id INT NOT NULL COMMENT '审批人人员ID',
    approver_name VARCHAR(100) NOT NULL COMMENT '审批人姓名',
    approver_role VARCHAR(100) NOT NULL COMMENT '审批人角色',
    approval_level INT NOT NULL COMMENT '审批级别',
    
    -- 审批结果
    approval_result ENUM('pending', 'approved', 'rejected') DEFAULT 'pending' NOT NULL COMMENT '审批结果',
    approval_comments VARCHAR(1000) NULL COMMENT '审批意见',
    approval_time DATETIME NULL COMMENT '审批时间',
    
    -- 附件信息
    attachments TEXT NULL COMMENT '附件（JSON数组）',
    
    -- 审计字段
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间（提交审批时间）',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_ticket_id (ticket_id),
    INDEX idx_ticket_no (ticket_no),
    INDEX idx_step_id (step_id),
    INDEX idx_approver_staff_id (approver_staff_id),
    INDEX idx_approval_result (approval_result),
    INDEX idx_approval_time (approval_time),
    
    FOREIGN KEY (ticket_id) REFERENCES ticket(ticket_id),
    FOREIGN KEY (step_id) REFERENCES workflow_steps(step_id),
    FOREIGN KEY (approver_staff_id) REFERENCES enterprise_staff(staff_id)
) COMMENT='工单审批记录表';
```

---

### 4.17 工单流转日志表（ticket_flow_logs）- 新增

**目的**：记录工单的完整流转历史，包括流转验证结果

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
    
    -- 操作信息
    action ENUM('forward', 'rollback', 'rollback_to_start', 'terminate', 'complete', 'restart') NOT NULL COMMENT '操作类型：forward=向前流转, rollback=回退到上一步, rollback_to_start=回退到开始, terminate=终止, complete=完成, restart=重新开始',
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
    approval_record_id BIGINT NULL COMMENT '关联的审批记录ID',
    
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
    FOREIGN KEY (operator_staff_id) REFERENCES enterprise_staff(staff_id),
    FOREIGN KEY (approval_record_id) REFERENCES ticket_approval_records(approval_id)
) COMMENT='工单流转日志表（记录完整流转历史和验证结果）';
```

**流转验证示例**：
```json
{
  "validation_errors": [
    {"field": "approval", "message": "当前步骤需要审批通过才能流转"},
    {"field": "previous_step", "message": "上一步骤尚未完成"}
  ],
  "conditions_checked": [
    {"condition": "require_previous_completed", "result": false},
    {"condition": "require_previous_approved", "result": false},
    {"condition": "require_approval", "result": false}
  ]
}
```

---

### 4.18 工单实例步骤表（ticket_step_instances）- 新增

**目的**：记录工单在各个步骤的实时状态

```sql
CREATE TABLE ticket_step_instances (
    instance_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    ticket_id INT NOT NULL COMMENT '工单ID',
    step_id INT NOT NULL COMMENT '步骤ID',
    step_name VARCHAR(100) NOT NULL COMMENT '步骤名称',
    step_order INT NOT NULL COMMENT '步骤顺序',
    
    -- 状态信息
    status ENUM('pending', 'in_progress', 'completed', 'rejected', 'skipped', 'rolled_back') DEFAULT 'pending' COMMENT '步骤状态',
    
    -- 处理人信息
    assignee_account_id INT NULL COMMENT '当前处理人账号ID',
    assignee_staff_id INT NULL COMMENT '当前处理人人员ID',
    assignee_name VARCHAR(100) NULL COMMENT '当前处理人姓名',
    assignee_role VARCHAR(100) NULL COMMENT '当前处理人角色',
    
    -- 时间信息
    arrived_at DATETIME NULL COMMENT '到达时间',
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
    
    FOREIGN KEY (ticket_id) REFERENCES ticket(ticket_id),
    FOREIGN KEY (step_id) REFERENCES workflow_steps(step_id),
    FOREIGN KEY (assignee_staff_id) REFERENCES enterprise_staff(staff_id)
) COMMENT='工单实例步骤表（记录工单在各步骤的实时状态）';
```

**步骤状态说明**：
- `pending`：待处理（步骤已创建，等待处理）
- `in_progress`：处理中（已开始处理）
- `completed`：已完成（步骤完成）
- `rejected`：已拒绝（审批不通过）
- `skipped`：已跳过（条件不满足，跳过该步骤）
- `rolled_back`：已回退（工单回退，该步骤作废）

---

### 3.12 其他表的软删除改进

以下表需要添加软删除支持：

#### 3.12.1 Company表
```sql
ALTER TABLE company ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE NOT NULL COMMENT '软删除标记';
ALTER TABLE company ADD COLUMN deleted_at DATETIME NULL COMMENT '删除时间';
ALTER TABLE company ADD COLUMN deleted_by INT NULL COMMENT '删除人ID';
ALTER TABLE company ADD INDEX idx_is_deleted (is_deleted);
```

#### 3.12.2 Contractor表
```sql
ALTER TABLE contractor ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE NOT NULL COMMENT '软删除标记';
ALTER TABLE contractor ADD COLUMN deleted_at DATETIME NULL COMMENT '删除时间';
ALTER TABLE contractor ADD COLUMN deleted_by INT NULL COMMENT '删除人ID';
ALTER TABLE contractor ADD INDEX idx_is_deleted (is_deleted);
```

#### 3.12.3 Department表
```sql
ALTER TABLE department ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE NOT NULL COMMENT '软删除标记';
ALTER TABLE department ADD COLUMN deleted_at DATETIME NULL COMMENT '删除时间';
ALTER TABLE department ADD COLUMN deleted_by INT NULL COMMENT '删除人ID';
ALTER TABLE department ADD INDEX idx_is_deleted (is_deleted);
```

#### 3.12.4 Area表
```sql
ALTER TABLE area ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE NOT NULL COMMENT '软删除标记';
ALTER TABLE area ADD COLUMN deleted_at DATETIME NULL COMMENT '删除时间';
ALTER TABLE area ADD COLUMN deleted_by INT NULL COMMENT '删除人ID';
ALTER TABLE area ADD INDEX idx_is_deleted (is_deleted);
```

#### 3.12.5 ContractorProject表
```sql
ALTER TABLE contractor_project ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE NOT NULL COMMENT '软删除标记';
ALTER TABLE contractor_project ADD COLUMN deleted_at DATETIME NULL COMMENT '删除时间';
ALTER TABLE contractor_project ADD COLUMN deleted_by INT NULL COMMENT '删除人ID';
ALTER TABLE contractor_project ADD INDEX idx_is_deleted (is_deleted);
```

---

## 四、数据迁移策略

### 4.1 用户表数据迁移

```sql
-- 步骤1：创建新的users表（按照新结构）
-- 步骤2：从旧users表迁移数据
INSERT INTO users_new (user_id, username, password_hash, user_type, enterprise_user_id, contractor_user_id, status, created_at, updated_at)
SELECT 
    user_id,
    username,
    password_hash,
    user_type,
    enterprise_staff_id,
    contractor_staff_id,
    'active' as status,
    created_at,
    updated_at
FROM users_old
WHERE user_type IN ('admin', 'enterprise', 'contractor');

-- 步骤3：重命名表
RENAME TABLE users TO users_backup;
RENAME TABLE users_new TO users;
```

### 4.2 角色数据迁移

```sql
-- 步骤1：创建系统角色（见3.5节）
-- 步骤2：更新enterprise_user表，将role_type映射到role_id
UPDATE enterprise_user eu
JOIN roles r ON r.role_code = CONCAT('enterprise_', eu.role_type)
SET eu.role_id = r.role_id;

-- 步骤3：更新contractor_user表
UPDATE contractor_user cu
JOIN roles r ON r.role_code = CONCAT('contractor_', cu.role_type)
SET cu.role_id = r.role_id;
```

### 4.3 工单数据迁移

```sql
-- 步骤1：创建默认工单流程
INSERT INTO workflow_definitions (workflow_code, workflow_name, workflow_type, is_active)
VALUES ('default_ticket_workflow', '默认工单审批流程', 'ticket_approval', TRUE);

-- 步骤2：创建流程步骤（根据业务需求定义）
-- 步骤3：为现有工单生成工单编号
UPDATE ticket 
SET ticket_no = CONCAT('TK', DATE_FORMAT(created_at, '%Y%m%d'), LPAD(ticket_id, 6, '0'))
WHERE ticket_no IS NULL;

-- 步骤4：设置默认流程
UPDATE ticket 
SET workflow_id = (SELECT workflow_id FROM workflow_definitions WHERE workflow_code = 'default_ticket_workflow')
WHERE workflow_id IS NULL;
```

---

## 五、工单流程业务逻辑详解

### 5.1 工单流程核心规则

#### 5.1.1 流转前置条件验证

每次工单流转前，系统必须验证以下条件：

```python
def validate_ticket_flow(ticket, from_step, to_step, operator):
    """
    工单流转验证函数
    
    验证规则：
    1. 上一步必须已完成（如果配置要求）
    2. 上一步审批必须通过（如果配置要求）
    3. 必填字段必须填写完整
    4. 操作人必须有权限
    5. 自定义条件必须满足
    """
    errors = []
    
    # 1. 检查上一步是否完成
    if to_step.require_previous_completed:
        if from_step.status != 'completed':
            errors.append({
                "field": "previous_step",
                "message": f"上一步骤【{from_step.step_name}】尚未完成"
            })
    
    # 2. 检查上一步审批是否通过
    if to_step.require_previous_approved:
        approval_record = get_approval_record(ticket.ticket_id, from_step.step_id)
        if not approval_record or approval_record.approval_result != 'approved':
            errors.append({
                "field": "approval",
                "message": f"上一步骤【{from_step.step_name}】需要审批通过"
            })
    
    # 3. 检查必填字段
    if to_step.required_fields:
        required_fields = json.loads(to_step.required_fields)
        for field in required_fields:
            if not getattr(ticket, field):
                errors.append({
                    "field": field,
                    "message": f"必填字段【{field}】未填写"
                })
    
    # 4. 检查操作人权限
    if not check_operator_permission(operator, to_step):
        errors.append({
            "field": "permission",
            "message": "您没有权限执行此操作"
        })
    
    # 5. 检查自定义条件
    if to_step.condition_expression:
        conditions = json.loads(to_step.condition_expression)
        for condition in conditions.get('custom_conditions', []):
            if not evaluate_condition(ticket, condition):
                errors.append({
                    "field": condition['field'],
                    "message": condition['message']
                })
    
    return len(errors) == 0, errors
```

#### 5.1.2 回退机制

**回退类型**：
1. **回退到上一步**：`rollback`
2. **回退到开始**：`rollback_to_start`

**权限控制**：
```python
def check_rollback_permission(ticket, operator, rollback_type):
    """
    检查回退权限
    
    权限规则：
    1. 工单创建者：可回退任意步骤、返回开始
    2. 审核人员（can_approve_ticket=TRUE）：可回退任意步骤、返回开始
    3. 当前步骤操作人员：可回退到上一步、返回开始
    """
    # 检查是否为创建者
    if operator.staff_id == ticket.creator_staff_id:
        return True
    
    # 检查是否为审核人员
    if operator.can_approve_ticket:
        return True
    
    # 检查是否为当前步骤操作人员
    current_instance = get_current_step_instance(ticket.ticket_id)
    if current_instance.assignee_staff_id == operator.staff_id:
        # 操作人员只能回退到上一步或开始
        if rollback_type in ['rollback', 'rollback_to_start']:
            return True
    
    return False
```

#### 5.1.3 终止与删除

**终止工单**：
```python
def terminate_ticket(ticket, operator, reason):
    """
    终止工单
    
    权限：仅创建者和审核人员
    效果：工单中途停止，保留所有记录
    """
    # 检查权限
    if not (operator.staff_id == ticket.creator_staff_id or 
            operator.can_terminate_ticket):
        raise PermissionError("只有创建者和审核人员可以终止工单")
    
    # 终止工单
    ticket.is_terminated = True
    ticket.terminated_at = datetime.now()
    ticket.terminated_by_staff_id = operator.staff_id
    ticket.termination_reason = reason
    
    # 记录流转日志
    log_ticket_flow(
        ticket_id=ticket.ticket_id,
        action='terminate',
        operator=operator,
        comments=reason
    )
```

**删除工单**：
```python
def delete_ticket(ticket, operator, reason):
    """
    删除工单（软删除）
    
    权限：仅创建者和审核人员
    效果：标记为已删除，不在列表显示
    """
    # 检查权限
    if not (operator.staff_id == ticket.creator_staff_id or 
            operator.can_approve_ticket):
        raise PermissionError("只有创建者和审核人员可以删除工单")
    
    # 软删除
    ticket.is_deleted = True
    ticket.deleted_at = datetime.now()
    ticket.deleted_by_staff_id = operator.staff_id
    ticket.deletion_reason = reason
```

### 5.2 工单流程示例

#### 5.2.1 标准工单审批流程

```
开始 → 填写工单 → 部门审批 → 安全审批 → 最终审批 → 执行作业 → 完成
  ↓       ↓          ↓          ↓          ↓          ↓        ↓
终止    终止      退回/终止   退回/终止   退回/终止   退回/终止  完成
```

**流程说明**：
1. **填写工单**：企业人员创建工单，填写作业内容
2. **部门审批**：部门负责人审批（approval_level=3）
3. **安全审批**：安全部门审批（approval_level=2）
4. **最终审批**：企业管理员审批（approval_level=1）
5. **执行作业**：承包商人员执行作业
6. **完成**：工单完成

#### 5.2.2 流程步骤定义示例

```sql
-- 创建标准工单审批流程
INSERT INTO workflow_definitions (workflow_code, workflow_name, workflow_type, is_active)
VALUES ('standard_ticket_workflow', '标准工单审批流程', 'ticket_approval', TRUE);

SET @workflow_id = LAST_INSERT_ID();

-- 定义流程步骤
INSERT INTO workflow_steps (
    workflow_id, step_code, step_name, step_order, step_type,
    require_approval, approval_level, require_previous_completed,
    can_rollback, rollback_to_previous, rollback_to_start,
    can_terminate, next_step_id
) VALUES
-- 步骤1：开始
(@workflow_id, 'start', '开始', 1, 'start', FALSE, NULL, FALSE, FALSE, FALSE, FALSE, FALSE, NULL),

-- 步骤2：填写工单
(@workflow_id, 'fill_ticket', '填写工单', 2, 'operation', FALSE, NULL, TRUE, TRUE, TRUE, TRUE, TRUE, NULL),

-- 步骤3：部门审批
(@workflow_id, 'dept_approval', '部门审批', 3, 'approval', TRUE, 3, TRUE, TRUE, TRUE, TRUE, TRUE, NULL),

-- 步骤4：安全审批
(@workflow_id, 'safety_approval', '安全审批', 4, 'approval', TRUE, 2, TRUE, TRUE, TRUE, TRUE, TRUE, NULL),

-- 步骤5：最终审批
(@workflow_id, 'final_approval', '最终审批', 5, 'approval', TRUE, 1, TRUE, TRUE, TRUE, TRUE, TRUE, NULL),

-- 步骤6：执行作业
(@workflow_id, 'execute_work', '执行作业', 6, 'operation', FALSE, NULL, TRUE, TRUE, TRUE, TRUE, FALSE, NULL),

-- 步骤7：完成
(@workflow_id, 'complete', '完成', 7, 'end', FALSE, NULL, TRUE, FALSE, FALSE, FALSE, FALSE, NULL);

-- 设置next_step_id（建立步骤链）
UPDATE workflow_steps SET next_step_id = (
    SELECT step_id FROM workflow_steps WHERE workflow_id = @workflow_id AND step_code = 'fill_ticket'
) WHERE workflow_id = @workflow_id AND step_code = 'start';

UPDATE workflow_steps SET next_step_id = (
    SELECT step_id FROM workflow_steps WHERE workflow_id = @workflow_id AND step_code = 'dept_approval'
) WHERE workflow_id = @workflow_id AND step_code = 'fill_ticket';

UPDATE workflow_steps SET next_step_id = (
    SELECT step_id FROM workflow_steps WHERE workflow_id = @workflow_id AND step_code = 'safety_approval'
) WHERE workflow_id = @workflow_id AND step_code = 'dept_approval';

UPDATE workflow_steps SET next_step_id = (
    SELECT step_id FROM workflow_steps WHERE workflow_id = @workflow_id AND step_code = 'final_approval'
) WHERE workflow_id = @workflow_id AND step_code = 'safety_approval';

UPDATE workflow_steps SET next_step_id = (
    SELECT step_id FROM workflow_steps WHERE workflow_id = @workflow_id AND step_code = 'execute_work'
) WHERE workflow_id = @workflow_id AND step_code = 'final_approval';

UPDATE workflow_steps SET next_step_id = (
    SELECT step_id FROM workflow_steps WHERE workflow_id = @workflow_id AND step_code = 'complete'
) WHERE workflow_id = @workflow_id AND step_code = 'execute_work';
```

#### 5.2.3 复杂流程示例（含分支）

```sql
-- 创建动火作业专用流程
INSERT INTO workflow_definitions (workflow_code, workflow_name, workflow_type, is_active)
VALUES ('hot_work_workflow', '动火作业审批流程', 'ticket_approval', TRUE);

SET @workflow_id = LAST_INSERT_ID();

-- 步骤定义（含分支判断）
INSERT INTO workflow_steps (
    workflow_id, step_code, step_name, step_order, step_type,
    is_branch_point, branch_conditions
) VALUES
(@workflow_id, 'check_work_type', '判断作业类型', 2, 'operation', TRUE, 
 '[
    {"condition": "hot_work > 0", "next_step_id": 10, "description": "动火作业流程"},
    {"condition": "work_height_level > 2", "next_step_id": 20, "description": "高空作业流程"},
    {"condition": "default", "next_step_id": 30, "description": "普通作业流程"}
 ]');
```

### 5.3 工单流转完整流程

```python
async def flow_ticket_forward(ticket_id, operator, comments=None):
    """
    工单向前流转
    
    完整流程：
    1. 获取当前步骤
    2. 获取下一步骤
    3. 验证流转条件
    4. 更新工单状态
    5. 创建下一步骤实例
    6. 记录流转日志
    """
    # 1. 获取工单和当前步骤
    ticket = await get_ticket(ticket_id)
    current_step = await get_workflow_step(ticket.current_step_id)
    
    # 2. 确定下一步骤
    if current_step.is_branch_point:
        next_step = await evaluate_branch(ticket, current_step)
    else:
        next_step = await get_workflow_step(current_step.next_step_id)
    
    # 3. 验证流转条件
    validation_passed, errors = validate_ticket_flow(
        ticket, current_step, next_step, operator
    )
    
    if not validation_passed:
        # 记录验证失败日志
        await log_ticket_flow(
            ticket_id=ticket_id,
            from_step=current_step,
            to_step=next_step,
            action='forward',
            operator=operator,
            validation_passed=False,
            validation_errors=errors,
            comments=comments
        )
        raise ValidationError("流转条件不满足", errors)
    
    # 4. 更新工单状态
    ticket.previous_step_id = ticket.current_step_id
    ticket.current_step_id = next_step.step_id
    
    # 5. 更新当前步骤实例状态
    await update_step_instance(
        ticket_id=ticket_id,
        step_id=current_step.step_id,
        status='completed'
    )
    
    # 6. 创建下一步骤实例
    await create_step_instance(
        ticket_id=ticket_id,
        step_id=next_step.step_id,
        assignee=determine_assignee(next_step)
    )
    
    # 7. 如果下一步需要审批，创建审批记录
    if next_step.require_approval:
        await create_approval_record(
            ticket_id=ticket_id,
            step_id=next_step.step_id,
            approver=determine_approver(next_step)
        )
    
    # 8. 记录流转日志
    await log_ticket_flow(
        ticket_id=ticket_id,
        from_step=current_step,
        to_step=next_step,
        action='forward',
        operator=operator,
        validation_passed=True,
        comments=comments
    )
    
    # 9. 检查是否到达结束步骤
    if next_step.step_type == 'end':
        ticket.status = 'completed'
        ticket.completion_time = datetime.now()
    
    await session.commit()
    
    return {"success": True, "next_step": next_step.step_name}
```

---

## 六、实施建议

### 6.1 实施顺序

1. **第一阶段：基础表改造**（1-2周）
   - 添加软删除字段到现有表
   - 创建用户操作日志表
   - 创建角色相关表

2. **第二阶段：用户系统重构**（2-3周）
   - 重构用户表
   - 迁移现有用户数据
   - 实现用户变更日志功能
   - 测试用户管理功能

3. **第三阶段：工单流程系统**（3-4周）
   - 创建工单流程相关表
   - 重构工单表
   - 实现工单流转逻辑
   - 迁移现有工单数据
   - 测试工单流程

4. **第四阶段：权限系统完善**（1-2周）
   - 实现角色权限管理
   - 实现企业级权限定制
   - 测试权限控制

### 6.2 风险控制

1. **数据备份**：每次迁移前完整备份数据库
2. **灰度发布**：先在测试环境验证，再逐步上线
3. **回滚方案**：保留旧表结构，确保可以快速回滚
4. **监控告警**：添加数据一致性监控

### 6.3 性能优化建议

1. **索引优化**：
   - 为高频查询字段添加索引
   - 为外键添加索引
   - 定期分析慢查询

2. **分区策略**：
   - 日志表按时间分区
   - 工单表按年份分区

3. **归档策略**：
   - 定期归档历史日志（保留1年）
   - 归档已完成工单（保留2年）

---

## 七、API接口影响分析

### 7.1 需要修改的接口

1. **用户管理接口**
   - `/user-management/users/` - 需要适配新的用户表结构
   - `/user-management/users/{user_id}/` - 需要返回完整的用户信息
   - 添加用户变更日志查询接口

2. **角色管理接口**（新增）
   - `/user-management/roles/` - 角色列表
   - `/user-management/roles/{role_id}/` - 角色详情
   - `/user-management/roles/{role_id}/permissions/` - 角色权限管理

3. **工单管理接口**
   - `/tickets/` - 需要返回工单状态和流程信息
   - `/tickets/{ticket_id}/` - 需要返回流程步骤信息
   - `/tickets/{ticket_id}/flow/` - 工单流转（新增）
   - `/tickets/{ticket_id}/logs/` - 工单流转日志（新增）

### 7.2 兼容性处理

- 保持现有API接口路径不变
- 响应数据结构向后兼容
- 新增字段设置默认值
- 提供API版本控制

---

## 八、表结构汇总

### 8.1 核心表列表

| 序号 | 表名 | 用途 | 类型 |
|------|------|------|------|
| 1 | `enterprise` | 甲方企业信息 | 主体表 |
| 2 | `contractor` | 承包商企业信息 | 主体表 |
| 3 | `admin_account` | 系统管理员账号 | 账号表 |
| 4 | `enterprise_staff_account` | 企业人员账号 | 账号表 |
| 5 | `contractor_staff_account` | 承包商人员账号 | 账号表 |
| 6 | `account_change_logs` | 账号变更日志 | 日志表 |
| 7 | `enterprise_staff` | 企业人员信息 | 人员表 |
| 8 | `contractor_staff` | 承包商人员信息 | 人员表 |
| 9 | `department` | 部门信息 | 组织表 |
| 10 | `area` | 厂区信息 | 组织表 |
| 11 | `roles` | 角色定义 | 权限表 |
| 12 | `role_permissions` | 角色权限 | 权限表 |
| 13 | `workflow_definitions` | 工单流程定义 | 流程表 |
| 14 | `workflow_steps` | 工单流程步骤 | 流程表 |
| 15 | `ticket` | 工单信息 | 工单表 |
| 16 | `ticket_approval_records` | 工单审批记录 | 工单表 |
| 17 | `ticket_flow_logs` | 工单流转日志 | 工单表 |
| 18 | `ticket_step_instances` | 工单步骤实例 | 工单表 |
| 19 | `contractor_project` | 承包商合作项目 | 业务表 |
| 20 | `entry_plan` | 进场计划 | 业务表 |
| 21 | `entry_plan_user` | 进场计划人员 | 业务表 |
| 22 | `entry_register` | 进场登记 | 业务表 |
| 23 | `confined_space` | 受限空间 | 业务表 |
| 24 | `temporary_power` | 临时用电 | 业务表 |
| 25 | `cross_work` | 交叉作业 | 业务表 |
| 26 | `work_equipment` | 作业设备 | 业务表 |

### 8.2 关键改进点

#### 8.2.1 主体分离
- ✅ 甲方企业（`enterprise`）和承包商企业（`contractor`）完全独立
- ✅ 企业人员和承包商人员各有独立的账号体系和信息表
- ✅ 系统管理员独立管理

#### 8.2.2 账号体系
- ✅ 三套独立账号表：`admin_account`、`enterprise_staff_account`、`contractor_staff_account`
- ✅ 账号与人员信息分离，便于管理
- ✅ 完整的账号变更日志（`account_change_logs`）

#### 8.2.3 工单流程
- ✅ 支持复杂流程定义（`workflow_definitions` + `workflow_steps`）
- ✅ 支持流程分支、审核、多级回退
- ✅ 完整的流转验证机制
- ✅ 详细的流转日志和审批记录

#### 8.2.4 权限管理
- ✅ 灵活的角色定义（`roles`）
- ✅ 细粒度权限配置（`role_permissions`）
- ✅ 支持企业级权限定制

#### 8.2.5 数据安全
- ✅ 所有核心表支持软删除
- ✅ 完整的审计字段（created_by, updated_by, deleted_by）
- ✅ 操作日志完整记录

### 8.3 表关系总览

```
系统架构
├── 主体层
│   ├── enterprise（甲方企业）
│   └── contractor（承包商企业）
│
├── 账号层
│   ├── admin_account（管理员账号）
│   ├── enterprise_staff_account（企业人员账号）
│   └── contractor_staff_account（承包商人员账号）
│
├── 人员层
│   ├── enterprise_staff（企业人员信息）
│   └── contractor_staff（承包商人员信息）
│
├── 组织层
│   ├── department（部门）
│   └── area（厂区）
│
├── 权限层
│   ├── roles（角色）
│   └── role_permissions（权限）
│
├── 流程层
│   ├── workflow_definitions（流程定义）
│   └── workflow_steps（流程步骤）
│
├── 工单层
│   ├── ticket（工单）
│   ├── ticket_approval_records（审批记录）
│   ├── ticket_flow_logs（流转日志）
│   └── ticket_step_instances（步骤实例）
│
└── 业务层
    ├── contractor_project（合作项目）
    ├── entry_plan（进场计划）
    ├── confined_space（受限空间）
    ├── temporary_power（临时用电）
    └── cross_work（交叉作业）
```

---

## 九、总结

本改进方案主要解决以下问题：

1. ✅ **四个独立主体**：甲方企业、承包商企业、企业人员、承包商人员完全独立管理
2. ✅ **账号体系分离**：三套独立账号表，各司其职
3. ✅ **软删除机制**：保留历史数据，支持数据恢复
4. ✅ **操作审计**：完整记录账号变更和工单流转历史
5. ✅ **工单流程化**：支持复杂流程、分支、审核、多级回退
6. ✅ **流转条件验证**：每步流转前验证条件，给出明确失败原因
7. ✅ **灵活回退机制**：支持回退到上一步、回退到开始、终止工单
8. ✅ **权限细粒度**：支持企业级角色和权限定制
9. ✅ **数据隔离**：确保企业间数据安全隔离
10. ✅ **可扩展性**：支持未来业务扩展

### 核心优势

1. **业务逻辑清晰**：
   - 主体分离明确，甲方企业和承包商企业各自独立
   - 账号与人员信息分离，便于管理
   - 工单流程完全可配置

2. **流程灵活强大**：
   - 支持长流程、分支流程
   - 支持多级审批
   - 支持灵活回退（上一步、开始、终止）
   - 流转前自动验证条件

3. **权限控制精细**：
   - 工单创建者：可回退、终止、删除
   - 审核人员：可回退、终止、删除
   - 操作人员：可回退到上一步或开始

4. **数据安全可靠**：
   - 软删除机制，数据可恢复
   - 完整的操作审计
   - 详细的流转日志

5. **易于维护扩展**：
   - 表结构清晰，职责明确
   - 支持企业级定制
   - 预留扩展字段

---

## 九、附录

### 9.1 工单编号生成规则

```
格式：TK + YYYYMMDD + 6位序号
示例：TK20250104000001

生成逻辑：
1. TK：固定前缀（Ticket）
2. YYYYMMDD：申请日期
3. 6位序号：当天的流水号，从1开始
```

### 9.2 状态枚举定义

#### 用户状态
- `active`：启用
- `inactive`：停用
- `locked`：锁定
- `deleted`：已删除

#### 工单状态
- `draft`：草稿
- `in_progress`：进行中
- `completed`：已完成
- `cancelled`：已作废
- `rejected`：已拒绝

#### 步骤状态
- `pending`：待处理
- `in_progress`：处理中
- `completed`：已完成
- `rejected`：已拒绝
- `skipped`：已跳过

### 9.3 权限编码规范

```
格式：{resource}.{action}
示例：
- ticket.create：创建工单
- ticket.read：查看工单
- ticket.update：更新工单
- ticket.delete：删除工单
- ticket.approve：审批工单
- user.create：创建用户
- user.manage：管理用户
- role.assign：分配角色
```

---

**文档版本**：v1.0  
**创建日期**：2025-01-04  
**最后更新**：2025-01-04  
**作者**：AI Assistant

