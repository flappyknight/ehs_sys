# 数据库改进实施检查清单

## 📋 总览

本文档提供数据库改进方案的实施步骤检查清单，帮助您按部就班地完成数据库重构。

---

## 🎯 实施前准备

### ✅ 环境准备
- [ ] 完整备份当前数据库
- [ ] 准备测试环境（与生产环境配置一致）
- [ ] 确认Python虚拟环境（ehs_env）可用
- [ ] 安装必要的数据库迁移工具（Alembic）
- [ ] 准备回滚方案文档

### ✅ 团队准备
- [ ] 评审改进方案，确认所有利益相关者同意
- [ ] 安排实施窗口期（建议选择业务低峰期）
- [ ] 准备应急联系人清单
- [ ] 制定沟通计划

### ✅ 文档准备
- [ ] 阅读 `DATABASE_IMPROVEMENT_PLAN.md`
- [ ] 阅读 `DATABASE_ERD.md`
- [ ] 准备数据迁移脚本
- [ ] 准备数据验证脚本

---

## 📅 第一阶段：基础表改造（预计1-2周）

### 1.1 添加软删除字段

#### Company表
```sql
-- 脚本：migrations/001_add_soft_delete_to_company.sql
ALTER TABLE company 
ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE NOT NULL COMMENT '软删除标记',
ADD COLUMN deleted_at DATETIME NULL COMMENT '删除时间',
ADD COLUMN deleted_by INT NULL COMMENT '删除人ID',
ADD INDEX idx_is_deleted (is_deleted);
```
- [ ] 编写SQL脚本
- [ ] 在测试环境执行
- [ ] 验证字段添加成功
- [ ] 更新SQLModel模型（db/models.py）
- [ ] 更新CRUD函数（db/crud.py）
- [ ] 测试查询功能
- [ ] 在生产环境执行

#### Contractor表
```sql
-- 脚本：migrations/002_add_soft_delete_to_contractor.sql
ALTER TABLE contractor 
ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE NOT NULL COMMENT '软删除标记',
ADD COLUMN deleted_at DATETIME NULL COMMENT '删除时间',
ADD COLUMN deleted_by INT NULL COMMENT '删除人ID',
ADD INDEX idx_is_deleted (is_deleted);
```
- [ ] 编写SQL脚本
- [ ] 在测试环境执行
- [ ] 验证字段添加成功
- [ ] 更新SQLModel模型
- [ ] 更新CRUD函数
- [ ] 测试查询功能
- [ ] 在生产环境执行

#### Department表
```sql
-- 脚本：migrations/003_add_soft_delete_to_department.sql
ALTER TABLE department 
ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE NOT NULL COMMENT '软删除标记',
ADD COLUMN deleted_at DATETIME NULL COMMENT '删除时间',
ADD COLUMN deleted_by INT NULL COMMENT '删除人ID',
ADD INDEX idx_is_deleted (is_deleted);
```
- [ ] 编写SQL脚本
- [ ] 在测试环境执行
- [ ] 验证字段添加成功
- [ ] 更新SQLModel模型
- [ ] 更新CRUD函数
- [ ] 测试查询功能
- [ ] 在生产环境执行

#### Area表
```sql
-- 脚本：migrations/004_add_soft_delete_to_area.sql
ALTER TABLE area 
ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE NOT NULL COMMENT '软删除标记',
ADD COLUMN deleted_at DATETIME NULL COMMENT '删除时间',
ADD COLUMN deleted_by INT NULL COMMENT '删除人ID',
ADD INDEX idx_is_deleted (is_deleted);
```
- [ ] 编写SQL脚本
- [ ] 在测试环境执行
- [ ] 验证字段添加成功
- [ ] 更新SQLModel模型
- [ ] 更新CRUD函数
- [ ] 测试查询功能
- [ ] 在生产环境执行

#### ContractorProject表
```sql
-- 脚本：migrations/005_add_soft_delete_to_contractor_project.sql
ALTER TABLE contractor_project 
ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE NOT NULL COMMENT '软删除标记',
ADD COLUMN deleted_at DATETIME NULL COMMENT '删除时间',
ADD COLUMN deleted_by INT NULL COMMENT '删除人ID',
ADD INDEX idx_is_deleted (is_deleted);
```
- [ ] 编写SQL脚本
- [ ] 在测试环境执行
- [ ] 验证字段添加成功
- [ ] 更新SQLModel模型
- [ ] 更新CRUD函数
- [ ] 测试查询功能
- [ ] 在生产环境执行

### 1.2 创建用户操作日志表

```sql
-- 脚本：migrations/006_create_user_change_logs.sql
CREATE TABLE user_change_logs (
    log_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '被操作的用户ID',
    operation_type ENUM('create', 'update', 'delete', 'lock', 'unlock', 'reset_password', 'status_change') NOT NULL,
    operator_id INT NOT NULL COMMENT '操作人ID',
    operator_name VARCHAR(100) NOT NULL,
    operator_type VARCHAR(20) NOT NULL,
    field_name VARCHAR(100) NULL,
    old_value TEXT NULL,
    new_value TEXT NULL,
    change_reason VARCHAR(500) NULL,
    operation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(50) NULL,
    user_agent VARCHAR(500) NULL,
    
    INDEX idx_user_id (user_id),
    INDEX idx_operator_id (operator_id),
    INDEX idx_operation_type (operation_type),
    INDEX idx_operation_time (operation_time),
    
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (operator_id) REFERENCES users(user_id)
) COMMENT='用户变更日志表';
```
- [ ] 编写SQL脚本
- [ ] 在测试环境执行
- [ ] 验证表创建成功
- [ ] 创建SQLModel模型
- [ ] 创建日志记录函数
- [ ] 测试日志记录功能
- [ ] 在生产环境执行

### 1.3 创建角色相关表

#### 角色表
```sql
-- 脚本：migrations/007_create_roles_table.sql
CREATE TABLE roles (
    role_id INT PRIMARY KEY AUTO_INCREMENT,
    role_code VARCHAR(50) UNIQUE NOT NULL,
    role_name VARCHAR(100) NOT NULL,
    role_type ENUM('system', 'enterprise', 'contractor') NOT NULL,
    company_id INT NULL,
    parent_role_id INT NULL,
    permission_level INT NOT NULL,
    description VARCHAR(500) NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_system BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT NULL,
    deleted_at DATETIME NULL,
    deleted_by INT NULL,
    
    INDEX idx_role_code (role_code),
    INDEX idx_role_type (role_type),
    INDEX idx_company_id (company_id),
    INDEX idx_is_deleted (is_deleted),
    
    FOREIGN KEY (company_id) REFERENCES company(company_id),
    FOREIGN KEY (parent_role_id) REFERENCES roles(role_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id),
    FOREIGN KEY (updated_by) REFERENCES users(user_id),
    FOREIGN KEY (deleted_by) REFERENCES users(user_id)
) COMMENT='角色表';
```
- [ ] 编写SQL脚本
- [ ] 在测试环境执行
- [ ] 验证表创建成功
- [ ] 创建SQLModel模型
- [ ] 插入系统预置角色
- [ ] 在生产环境执行

#### 角色权限表
```sql
-- 脚本：migrations/008_create_role_permissions_table.sql
CREATE TABLE role_permissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    role_id INT NOT NULL,
    permission_code VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NULL,
    
    UNIQUE KEY uk_role_permission (role_id, permission_code),
    INDEX idx_role_id (role_id),
    INDEX idx_resource_type (resource_type),
    
    FOREIGN KEY (role_id) REFERENCES roles(role_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id)
) COMMENT='角色权限表';
```
- [ ] 编写SQL脚本
- [ ] 在测试环境执行
- [ ] 验证表创建成功
- [ ] 创建SQLModel模型
- [ ] 插入系统预置权限
- [ ] 在生产环境执行

---

## 📅 第二阶段：用户系统重构（预计2-3周）

### 2.1 重构用户表

#### 备份现有用户表
```sql
-- 脚本：migrations/009_backup_users_table.sql
CREATE TABLE users_backup AS SELECT * FROM users;
```
- [ ] 备份users表
- [ ] 验证备份数据完整性

#### 修改用户表结构
```sql
-- 脚本：migrations/010_alter_users_table.sql
ALTER TABLE users
ADD COLUMN status ENUM('active', 'inactive', 'locked', 'deleted') DEFAULT 'active' NOT NULL AFTER user_type,
ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE NOT NULL AFTER status,
ADD COLUMN created_by INT NULL AFTER created_at,
ADD COLUMN updated_by INT NULL AFTER updated_at,
ADD COLUMN deleted_at DATETIME NULL AFTER updated_by,
ADD COLUMN deleted_by INT NULL AFTER deleted_at,
ADD COLUMN last_login_at DATETIME NULL AFTER deleted_by,
ADD COLUMN login_attempts INT DEFAULT 0 AFTER last_login_at,
ADD COLUMN locked_until DATETIME NULL AFTER login_attempts,
ADD INDEX idx_status (status),
ADD INDEX idx_is_deleted (is_deleted);
```
- [ ] 编写SQL脚本
- [ ] 在测试环境执行
- [ ] 验证字段添加成功
- [ ] 更新SQLModel模型
- [ ] 在生产环境执行

#### 初始化用户状态
```sql
-- 脚本：migrations/011_init_user_status.sql
UPDATE users SET status = 'active' WHERE status IS NULL;
UPDATE users SET is_deleted = FALSE WHERE is_deleted IS NULL;
```
- [ ] 编写SQL脚本
- [ ] 在测试环境执行
- [ ] 验证数据更新成功
- [ ] 在生产环境执行

### 2.2 修改EnterpriseUser表

```sql
-- 脚本：migrations/012_alter_enterprise_user_table.sql
ALTER TABLE enterprise_user
ADD COLUMN role_id INT NULL AFTER position,
ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE NOT NULL AFTER status,
ADD COLUMN created_by INT NULL AFTER created_at,
ADD COLUMN updated_by INT NULL AFTER updated_at,
ADD COLUMN deleted_at DATETIME NULL AFTER updated_by,
ADD COLUMN deleted_by INT NULL AFTER deleted_at,
ADD INDEX idx_role_id (role_id),
ADD INDEX idx_is_deleted (is_deleted);

-- 添加外键约束
ALTER TABLE enterprise_user
ADD CONSTRAINT fk_enterprise_user_role 
FOREIGN KEY (role_id) REFERENCES roles(role_id);
```
- [ ] 编写SQL脚本
- [ ] 在测试环境执行
- [ ] 验证字段添加成功
- [ ] 更新SQLModel模型
- [ ] 在生产环境执行

#### 迁移角色数据
```sql
-- 脚本：migrations/013_migrate_enterprise_user_roles.sql
-- 将role_type映射到role_id
UPDATE enterprise_user eu
JOIN roles r ON r.role_code = CONCAT('enterprise_', eu.role_type)
SET eu.role_id = r.role_id
WHERE eu.role_id IS NULL;
```
- [ ] 编写SQL脚本
- [ ] 在测试环境执行
- [ ] 验证数据迁移成功
- [ ] 在生产环境执行

### 2.3 修改ContractorUser表

```sql
-- 脚本：migrations/014_alter_contractor_user_table.sql
ALTER TABLE contractor_user
ADD COLUMN role_id INT NULL AFTER work_type,
ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE NOT NULL AFTER status,
ADD COLUMN created_by INT NULL AFTER created_at,
ADD COLUMN updated_by INT NULL AFTER updated_at,
ADD COLUMN deleted_at DATETIME NULL AFTER updated_by,
ADD COLUMN deleted_by INT NULL AFTER deleted_at,
ADD INDEX idx_role_id (role_id),
ADD INDEX idx_is_deleted (is_deleted);

-- 添加外键约束
ALTER TABLE contractor_user
ADD CONSTRAINT fk_contractor_user_role 
FOREIGN KEY (role_id) REFERENCES roles(role_id);
```
- [ ] 编写SQL脚本
- [ ] 在测试环境执行
- [ ] 验证字段添加成功
- [ ] 更新SQLModel模型
- [ ] 在生产环境执行

#### 迁移角色数据
```sql
-- 脚本：migrations/015_migrate_contractor_user_roles.sql
UPDATE contractor_user cu
JOIN roles r ON r.role_code = CONCAT('contractor_', cu.role_type)
SET cu.role_id = r.role_id
WHERE cu.role_id IS NULL;
```
- [ ] 编写SQL脚本
- [ ] 在测试环境执行
- [ ] 验证数据迁移成功
- [ ] 在生产环境执行

### 2.4 实现用户变更日志功能

- [ ] 创建日志记录装饰器
- [ ] 在用户创建函数中添加日志
- [ ] 在用户更新函数中添加日志
- [ ] 在用户删除函数中添加日志
- [ ] 在用户状态变更函数中添加日志
- [ ] 测试日志记录功能
- [ ] 创建日志查询API

### 2.5 更新用户管理API

- [ ] 更新 `/user-management/users/` 接口
- [ ] 更新 `/user-management/users/{user_id}/` 接口
- [ ] 添加用户状态变更接口
- [ ] 添加用户锁定/解锁接口
- [ ] 添加用户变更日志查询接口
- [ ] 更新API文档
- [ ] 测试所有用户管理接口

---

## 📅 第三阶段：工单流程系统（预计3-4周）

### 3.1 创建工单流程定义表

```sql
-- 脚本：migrations/016_create_workflow_definitions.sql
CREATE TABLE workflow_definitions (
    workflow_id INT PRIMARY KEY AUTO_INCREMENT,
    workflow_code VARCHAR(50) UNIQUE NOT NULL,
    workflow_name VARCHAR(100) NOT NULL,
    workflow_type VARCHAR(50) NOT NULL,
    company_id INT NULL,
    description VARCHAR(500) NULL,
    version INT DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL,
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
- [ ] 编写SQL脚本
- [ ] 在测试环境执行
- [ ] 验证表创建成功
- [ ] 创建SQLModel模型
- [ ] 在生产环境执行

### 3.2 创建工单流程步骤表

```sql
-- 脚本：migrations/017_create_workflow_steps.sql
CREATE TABLE workflow_steps (
    step_id INT PRIMARY KEY AUTO_INCREMENT,
    workflow_id INT NOT NULL,
    step_code VARCHAR(50) NOT NULL,
    step_name VARCHAR(100) NOT NULL,
    step_order INT NOT NULL,
    step_type ENUM('start', 'approval', 'notify', 'end') NOT NULL,
    require_approval BOOLEAN DEFAULT FALSE,
    approver_role_id INT NULL,
    approval_level INT NULL,
    can_reject BOOLEAN DEFAULT TRUE,
    reject_to_step_id INT NULL,
    can_cancel BOOLEAN DEFAULT TRUE,
    timeout_hours INT NULL,
    description VARCHAR(500) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT NULL,
    
    UNIQUE KEY uk_workflow_step (workflow_id, step_code),
    INDEX idx_workflow_id (workflow_id),
    INDEX idx_step_order (step_order),
    INDEX idx_approver_role_id (approver_role_id),
    
    FOREIGN KEY (workflow_id) REFERENCES workflow_definitions(workflow_id),
    FOREIGN KEY (approver_role_id) REFERENCES roles(role_id),
    FOREIGN KEY (reject_to_step_id) REFERENCES workflow_steps(step_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id),
    FOREIGN KEY (updated_by) REFERENCES users(user_id)
) COMMENT='工单流程步骤表';
```
- [ ] 编写SQL脚本
- [ ] 在测试环境执行
- [ ] 验证表创建成功
- [ ] 创建SQLModel模型
- [ ] 在生产环境执行

### 3.3 创建默认工单流程

```sql
-- 脚本：migrations/018_create_default_workflow.sql
-- 创建默认工单流程
INSERT INTO workflow_definitions (workflow_code, workflow_name, workflow_type, is_active)
VALUES ('default_ticket_workflow', '默认工单审批流程', 'ticket_approval', TRUE);

-- 获取workflow_id（假设为1）
SET @workflow_id = LAST_INSERT_ID();

-- 创建流程步骤
INSERT INTO workflow_steps (workflow_id, step_code, step_name, step_order, step_type, require_approval, can_reject) VALUES
(@workflow_id, 'start', '开始', 1, 'start', FALSE, FALSE),
(@workflow_id, 'submit', '提交申请', 2, 'approval', FALSE, TRUE),
(@workflow_id, 'dept_approval', '部门审批', 3, 'approval', TRUE, TRUE),
(@workflow_id, 'safety_approval', '安全审批', 4, 'approval', TRUE, TRUE),
(@workflow_id, 'final_approval', '最终审批', 5, 'approval', TRUE, TRUE),
(@workflow_id, 'complete', '完成', 6, 'end', FALSE, FALSE);

-- 设置退回步骤
UPDATE workflow_steps SET reject_to_step_id = (
    SELECT step_id FROM workflow_steps WHERE workflow_id = @workflow_id AND step_code = 'submit'
) WHERE workflow_id = @workflow_id AND step_code IN ('dept_approval', 'safety_approval', 'final_approval');
```
- [ ] 编写SQL脚本
- [ ] 在测试环境执行
- [ ] 验证流程创建成功
- [ ] 在生产环境执行

### 3.4 重构工单表

#### 备份现有工单表
```sql
-- 脚本：migrations/019_backup_ticket_table.sql
CREATE TABLE ticket_backup AS SELECT * FROM ticket;
```
- [ ] 备份ticket表
- [ ] 验证备份数据完整性

#### 修改工单表结构
```sql
-- 脚本：migrations/020_alter_ticket_table.sql
ALTER TABLE ticket
ADD COLUMN ticket_no VARCHAR(50) UNIQUE NULL AFTER ticket_id,
ADD COLUMN workflow_id INT NULL AFTER ticket_no,
ADD COLUMN current_step_id INT NULL AFTER workflow_id,
ADD COLUMN previous_step_id INT NULL AFTER current_step_id,
ADD COLUMN status ENUM('draft', 'in_progress', 'completed', 'cancelled', 'rejected') DEFAULT 'draft' NOT NULL AFTER previous_step_id,
ADD COLUMN company_id INT NULL AFTER applicant,
ADD COLUMN actual_st DATETIME NULL AFTER pre_et,
ADD COLUMN actual_et DATETIME NULL AFTER actual_st,
ADD COLUMN custodian_id INT NULL AFTER worker,
ADD COLUMN completion_notes VARCHAR(1000) NULL AFTER signature,
ADD COLUMN completion_photos VARCHAR(1000) NULL AFTER completion_notes,
ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE NOT NULL AFTER completion_photos,
ADD COLUMN created_by INT NULL AFTER created_at,
ADD COLUMN updated_by INT NULL AFTER updated_at,
ADD COLUMN deleted_at DATETIME NULL AFTER updated_by,
ADD COLUMN deleted_by INT NULL AFTER deleted_at,
ADD COLUMN cancelled_at DATETIME NULL AFTER deleted_by,
ADD COLUMN cancelled_by INT NULL AFTER cancelled_at,
ADD COLUMN cancelled_reason VARCHAR(500) NULL AFTER cancelled_by;

-- 添加索引
ALTER TABLE ticket
ADD INDEX idx_ticket_no (ticket_no),
ADD INDEX idx_workflow_id (workflow_id),
ADD INDEX idx_current_step_id (current_step_id),
ADD INDEX idx_status (status),
ADD INDEX idx_company_id (company_id),
ADD INDEX idx_is_deleted (is_deleted);

-- 重命名字段
ALTER TABLE ticket
CHANGE COLUMN custodians custodian_id_old INT;
```
- [ ] 编写SQL脚本
- [ ] 在测试环境执行
- [ ] 验证字段添加成功
- [ ] 更新SQLModel模型
- [ ] 在生产环境执行

#### 生成工单编号
```sql
-- 脚本：migrations/021_generate_ticket_numbers.sql
UPDATE ticket 
SET ticket_no = CONCAT('TK', DATE_FORMAT(created_at, '%Y%m%d'), LPAD(ticket_id, 6, '0'))
WHERE ticket_no IS NULL;
```
- [ ] 编写SQL脚本
- [ ] 在测试环境执行
- [ ] 验证工单编号生成成功
- [ ] 在生产环境执行

#### 设置默认流程和状态
```sql
-- 脚本：migrations/022_set_default_workflow.sql
UPDATE ticket 
SET workflow_id = (SELECT workflow_id FROM workflow_definitions WHERE workflow_code = 'default_ticket_workflow'),
    status = 'in_progress'
WHERE workflow_id IS NULL;
```
- [ ] 编写SQL脚本
- [ ] 在测试环境执行
- [ ] 验证数据更新成功
- [ ] 在生产环境执行

### 3.5 创建工单流转日志表

```sql
-- 脚本：migrations/023_create_ticket_flow_logs.sql
CREATE TABLE ticket_flow_logs (
    log_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    ticket_id INT NOT NULL,
    ticket_no VARCHAR(50) NOT NULL,
    from_step_id INT NULL,
    from_step_name VARCHAR(100) NULL,
    to_step_id INT NOT NULL,
    to_step_name VARCHAR(100) NOT NULL,
    action ENUM('submit', 'approve', 'reject', 'cancel', 'restart', 'complete') NOT NULL,
    operator_id INT NOT NULL,
    operator_name VARCHAR(100) NOT NULL,
    operator_role VARCHAR(100) NOT NULL,
    approval_result ENUM('pending', 'approved', 'rejected') NULL,
    approval_comments VARCHAR(1000) NULL,
    operation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    duration_minutes INT NULL,
    ip_address VARCHAR(50) NULL,
    attachments VARCHAR(1000) NULL,
    
    INDEX idx_ticket_id (ticket_id),
    INDEX idx_ticket_no (ticket_no),
    INDEX idx_operator_id (operator_id),
    INDEX idx_operation_time (operation_time),
    INDEX idx_action (action),
    
    FOREIGN KEY (ticket_id) REFERENCES ticket(ticket_id),
    FOREIGN KEY (from_step_id) REFERENCES workflow_steps(step_id),
    FOREIGN KEY (to_step_id) REFERENCES workflow_steps(step_id),
    FOREIGN KEY (operator_id) REFERENCES users(user_id)
) COMMENT='工单流转日志表';
```
- [ ] 编写SQL脚本
- [ ] 在测试环境执行
- [ ] 验证表创建成功
- [ ] 创建SQLModel模型
- [ ] 在生产环境执行

### 3.6 创建工单实例步骤表

```sql
-- 脚本：migrations/024_create_ticket_step_instances.sql
CREATE TABLE ticket_step_instances (
    instance_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    ticket_id INT NOT NULL,
    step_id INT NOT NULL,
    step_name VARCHAR(100) NOT NULL,
    status ENUM('pending', 'in_progress', 'completed', 'rejected', 'skipped') DEFAULT 'pending',
    assignee_id INT NULL,
    assignee_name VARCHAR(100) NULL,
    arrived_at DATETIME NULL,
    started_at DATETIME NULL,
    completed_at DATETIME NULL,
    deadline DATETIME NULL,
    result VARCHAR(50) NULL,
    comments VARCHAR(1000) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_ticket_id (ticket_id),
    INDEX idx_step_id (step_id),
    INDEX idx_status (status),
    INDEX idx_assignee_id (assignee_id),
    
    FOREIGN KEY (ticket_id) REFERENCES ticket(ticket_id),
    FOREIGN KEY (step_id) REFERENCES workflow_steps(step_id),
    FOREIGN KEY (assignee_id) REFERENCES users(user_id)
) COMMENT='工单实例步骤表';
```
- [ ] 编写SQL脚本
- [ ] 在测试环境执行
- [ ] 验证表创建成功
- [ ] 创建SQLModel模型
- [ ] 在生产环境执行

### 3.7 实现工单流程逻辑

- [ ] 创建工单流程引擎类
- [ ] 实现工单创建逻辑
- [ ] 实现工单提交逻辑
- [ ] 实现工单审批逻辑
- [ ] 实现工单退回逻辑
- [ ] 实现工单作废逻辑
- [ ] 实现工单完成逻辑
- [ ] 实现流转日志记录
- [ ] 测试工单流程

### 3.8 更新工单管理API

- [ ] 更新 `/tickets/` 接口（列表）
- [ ] 更新 `/tickets/{ticket_id}/` 接口（详情）
- [ ] 添加 `/tickets/{ticket_id}/flow/` 接口（流转）
- [ ] 添加 `/tickets/{ticket_id}/logs/` 接口（日志）
- [ ] 添加 `/tickets/{ticket_id}/approve/` 接口（审批）
- [ ] 添加 `/tickets/{ticket_id}/reject/` 接口（退回）
- [ ] 添加 `/tickets/{ticket_id}/cancel/` 接口（作废）
- [ ] 更新API文档
- [ ] 测试所有工单接口

---

## 📅 第四阶段：权限系统完善（预计1-2周）

### 4.1 实现角色管理功能

- [ ] 创建角色管理CRUD函数
- [ ] 创建角色列表API
- [ ] 创建角色详情API
- [ ] 创建角色创建API
- [ ] 创建角色更新API
- [ ] 创建角色删除API
- [ ] 测试角色管理功能

### 4.2 实现权限管理功能

- [ ] 创建权限管理CRUD函数
- [ ] 创建权限列表API
- [ ] 创建角色权限分配API
- [ ] 创建权限检查装饰器
- [ ] 更新现有接口的权限检查
- [ ] 测试权限控制功能

### 4.3 实现企业级权限定制

- [ ] 创建企业自定义角色功能
- [ ] 创建企业角色权限配置功能
- [ ] 测试企业级权限隔离
- [ ] 更新API文档

---

## 🧪 测试阶段

### 单元测试
- [ ] 用户管理功能测试
- [ ] 角色管理功能测试
- [ ] 权限控制功能测试
- [ ] 工单流程功能测试
- [ ] 日志记录功能测试

### 集成测试
- [ ] 用户登录流程测试
- [ ] 工单完整流程测试
- [ ] 权限控制集成测试
- [ ] 数据隔离测试

### 性能测试
- [ ] 数据库查询性能测试
- [ ] 并发用户测试
- [ ] 工单流转性能测试
- [ ] 日志记录性能测试

### 数据一致性测试
- [ ] 用户数据一致性验证
- [ ] 工单数据一致性验证
- [ ] 角色权限数据一致性验证
- [ ] 软删除数据验证

---

## 📊 上线阶段

### 上线前检查
- [ ] 完整备份生产数据库
- [ ] 准备回滚脚本
- [ ] 通知所有用户系统维护
- [ ] 确认应急联系人在线

### 上线执行
- [ ] 停止应用服务
- [ ] 执行数据库迁移脚本
- [ ] 验证数据迁移成功
- [ ] 部署新版本代码
- [ ] 启动应用服务
- [ ] 验证系统功能正常

### 上线后监控
- [ ] 监控系统错误日志
- [ ] 监控数据库性能
- [ ] 监控用户反馈
- [ ] 记录问题和解决方案

---

## 🔧 维护阶段

### 定期维护任务
- [ ] 每周检查日志表大小
- [ ] 每月执行数据归档
- [ ] 每季度优化数据库索引
- [ ] 每半年评审权限配置

### 监控指标
- [ ] 用户登录成功率
- [ ] 工单流转平均时长
- [ ] 数据库查询响应时间
- [ ] 系统错误率

---

## 📝 文档更新

### 技术文档
- [ ] 更新数据库设计文档
- [ ] 更新API接口文档
- [ ] 更新部署文档
- [ ] 更新运维手册

### 用户文档
- [ ] 更新用户操作手册
- [ ] 更新管理员手册
- [ ] 制作培训材料
- [ ] 录制操作视频

---

## ⚠️ 风险控制

### 回滚方案
- [ ] 准备数据库回滚脚本
- [ ] 准备代码回滚方案
- [ ] 测试回滚流程
- [ ] 文档化回滚步骤

### 应急预案
- [ ] 准备常见问题解决方案
- [ ] 准备应急联系清单
- [ ] 准备数据修复脚本
- [ ] 准备临时解决方案

---

## ✅ 完成标准

### 功能完成标准
- [ ] 所有计划功能已实现
- [ ] 所有测试用例通过
- [ ] 性能指标达标
- [ ] 文档完整更新

### 质量完成标准
- [ ] 代码审查通过
- [ ] 安全审计通过
- [ ] 用户验收通过
- [ ] 运维团队培训完成

---

**文档版本**：v1.0  
**创建日期**：2025-01-04  
**最后更新**：2025-01-04  
**配套文档**：
- DATABASE_IMPROVEMENT_PLAN.md
- DATABASE_ERD.md

