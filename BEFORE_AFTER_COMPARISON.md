# 数据库改进方案 - 改进前后对比

## 📊 总体对比

| 维度 | 改进前 | 改进后 | 改进效果 |
|------|--------|--------|----------|
| **核心表数量** | 15张 | 22张 (+7张) | ⬆️ 功能更完善 |
| **用户管理** | 分散管理 | 统一管理 | ✅ 简化管理 |
| **删除机制** | 物理删除 | 软删除 | ✅ 数据可恢复 |
| **操作审计** | 无 | 完整日志 | ✅ 可追溯 |
| **角色权限** | 固化在代码 | 数据库配置 | ✅ 灵活可配 |
| **工单流程** | 固定状态 | 流程引擎 | ✅ 可自定义 |
| **工单编号** | 无 | 唯一编号 | ✅ 便于追踪 |

---

## 1️⃣ 用户表（users）对比

### 改进前
```sql
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    user_type VARCHAR(20) NOT NULL,  -- 'admin'/'enterprise'/'contractor'
    enterprise_staff_id INT,
    contractor_staff_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```
**问题**：
- ❌ 无法追踪用户状态变化
- ❌ 删除后数据无法恢复
- ❌ 不知道谁创建/修改/删除了用户
- ❌ 无法实现账号锁定功能

### 改进后
```sql
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    user_type ENUM('admin', 'enterprise', 'contractor') NOT NULL,
    
    -- 🆕 状态管理
    status ENUM('active', 'inactive', 'locked', 'deleted') DEFAULT 'active' NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL,
    
    -- 关联信息
    enterprise_user_id INT,
    contractor_user_id INT,
    
    -- 🆕 审计字段
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT,
    deleted_at DATETIME,
    deleted_by INT,
    
    -- 🆕 安全字段
    last_login_at DATETIME,
    login_attempts INT DEFAULT 0,
    locked_until DATETIME,
    
    INDEX idx_username (username),
    INDEX idx_user_type (user_type),
    INDEX idx_status (status),
    INDEX idx_is_deleted (is_deleted)
);
```
**改进**：
- ✅ 支持多种用户状态
- ✅ 软删除，数据可恢复
- ✅ 完整的审计信息
- ✅ 支持账号锁定
- ✅ 记录登录信息

---

## 2️⃣ 企业用户表（enterprise_user）对比

### 改进前
```sql
CREATE TABLE enterprise_user (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    company_id INT NOT NULL,
    dept_id INT,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    position VARCHAR(100),
    role_type VARCHAR(100) NOT NULL,  -- 🔴 字符串，不灵活
    approval_level INT DEFAULT 4,
    status BOOLEAN DEFAULT TRUE,  -- 🔴 只有true/false
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```
**问题**：
- ❌ `role_type` 是字符串，无法关联权限
- ❌ `status` 只有布尔值，表达能力有限
- ❌ 无软删除，数据无法恢复
- ❌ 无审计信息

### 改进后
```sql
CREATE TABLE enterprise_user (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    company_id INT NOT NULL,
    dept_id INT,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    position VARCHAR(100),
    id_number VARCHAR(50),  -- 🆕 身份证号
    
    -- 🆕 角色关联（替代role_type字符串）
    role_id INT NOT NULL,
    approval_level INT DEFAULT 4,
    
    -- 🆕 状态管理
    status ENUM('active', 'inactive', 'deleted') DEFAULT 'active' NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL,
    
    -- 🆕 审计字段
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT,
    deleted_at DATETIME,
    deleted_by INT,
    
    INDEX idx_company_id (company_id),
    INDEX idx_dept_id (dept_id),
    INDEX idx_role_id (role_id),
    INDEX idx_phone (phone),
    INDEX idx_is_deleted (is_deleted),
    
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);
```
**改进**：
- ✅ `role_id` 关联角色表，灵活可配
- ✅ 状态枚举，表达更清晰
- ✅ 软删除支持
- ✅ 完整审计信息
- ✅ 添加身份证号字段

---

## 3️⃣ 工单表（ticket）对比

### 改进前
```sql
CREATE TABLE ticket (
    ticket_id INT PRIMARY KEY AUTO_INCREMENT,
    apply_date DATE NOT NULL,
    applicant INT NOT NULL,  -- 申请人ID
    area_id INT NOT NULL,
    working_content VARCHAR(1024) NOT NULL,
    pre_st DATETIME NOT NULL,  -- 预计开始时间
    pre_et DATETIME NOT NULL,  -- 预计结束时间
    tools INT DEFAULT 0,
    worker INT NOT NULL,
    custodians INT NOT NULL,
    danger INT DEFAULT 0,
    protection INT DEFAULT 0,
    hot_work INT DEFAULT -1,
    work_height_level INT DEFAULT 0,
    confined_space_id INT,
    temp_power_id INT,
    cross_work_group_id VARCHAR(50),
    signature VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```
**问题**：
- ❌ 无工单唯一编号，不便追踪
- ❌ 无工单状态，无法表达流程
- ❌ 无流程定义，流程固化
- ❌ 无流转记录，无法追溯
- ❌ 无软删除
- ❌ 无审计信息

### 改进后
```sql
CREATE TABLE ticket (
    ticket_id INT PRIMARY KEY AUTO_INCREMENT,
    ticket_no VARCHAR(50) UNIQUE NOT NULL,  -- 🆕 唯一编号（如：TK20250104000001）
    
    -- 🆕 流程信息
    workflow_id INT NOT NULL,  -- 关联流程定义
    current_step_id INT,  -- 当前步骤
    previous_step_id INT,  -- 上一步骤
    
    -- 🆕 工单状态
    status ENUM('draft', 'in_progress', 'completed', 'cancelled', 'rejected') DEFAULT 'draft' NOT NULL,
    
    -- 基本信息
    apply_date DATE NOT NULL,
    applicant_id INT NOT NULL,
    company_id INT NOT NULL,  -- 🆕 所属企业
    area_id INT NOT NULL,
    
    -- 作业信息
    working_content VARCHAR(1024) NOT NULL,
    pre_st DATETIME NOT NULL,
    pre_et DATETIME NOT NULL,
    actual_st DATETIME,  -- 🆕 实际开始时间
    actual_et DATETIME,  -- 🆕 实际结束时间
    
    -- 人员信息
    worker_id INT NOT NULL,
    custodian_id INT NOT NULL,
    
    -- 作业配置
    tools INT DEFAULT 0,
    danger INT DEFAULT 0,
    protection INT DEFAULT 0,
    
    -- 特殊作业
    hot_work INT DEFAULT -1,
    work_height_level INT DEFAULT 0,
    confined_space_id INT,
    temp_power_id INT,
    cross_work_group_id VARCHAR(50),
    
    -- 签字信息
    signature VARCHAR(255),
    
    -- 🆕 完成信息
    completion_notes VARCHAR(1000),
    completion_photos VARCHAR(1000),
    
    -- 🆕 状态管理
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL,
    
    -- 🆕 审计字段
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT,
    deleted_at DATETIME,
    deleted_by INT,
    cancelled_at DATETIME,  -- 🆕 作废时间
    cancelled_by INT,  -- 🆕 作废人
    cancelled_reason VARCHAR(500),  -- 🆕 作废原因
    
    INDEX idx_ticket_no (ticket_no),
    INDEX idx_workflow_id (workflow_id),
    INDEX idx_current_step_id (current_step_id),
    INDEX idx_status (status),
    INDEX idx_applicant_id (applicant_id),
    INDEX idx_company_id (company_id),
    INDEX idx_apply_date (apply_date),
    INDEX idx_is_deleted (is_deleted),
    
    FOREIGN KEY (workflow_id) REFERENCES workflow_definitions(workflow_id),
    FOREIGN KEY (current_step_id) REFERENCES workflow_steps(step_id),
    FOREIGN KEY (previous_step_id) REFERENCES workflow_steps(step_id)
);
```
**改进**：
- ✅ 唯一工单编号
- ✅ 完整的流程支持
- ✅ 明确的工单状态
- ✅ 实际时间记录
- ✅ 完成信息记录
- ✅ 软删除支持
- ✅ 完整审计信息
- ✅ 作废原因记录

---

## 4️⃣ 新增表对比

### 🆕 用户变更日志表（user_change_logs）

**改进前**：❌ 不存在

**改进后**：
```sql
CREATE TABLE user_change_logs (
    log_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    operation_type ENUM('create', 'update', 'delete', 'lock', 'unlock', 'reset_password', 'status_change') NOT NULL,
    operator_id INT NOT NULL,
    operator_name VARCHAR(100) NOT NULL,
    operator_type VARCHAR(20) NOT NULL,
    field_name VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    change_reason VARCHAR(500),
    operation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(50),
    user_agent VARCHAR(500),
    
    INDEX idx_user_id (user_id),
    INDEX idx_operator_id (operator_id),
    INDEX idx_operation_type (operation_type),
    INDEX idx_operation_time (operation_time)
);
```
**价值**：
- ✅ 完整记录用户变更历史
- ✅ 支持审计和合规要求
- ✅ 可追溯所有操作

**使用场景**：
```python
# 查询用户变更历史
logs = await get_user_change_logs(user_id=123)
for log in logs:
    print(f"{log.operation_time}: {log.operator_name} {log.operation_type}")
    print(f"  {log.field_name}: {log.old_value} → {log.new_value}")
```

---

### 🆕 角色表（roles）

**改进前**：❌ 不存在，角色固化在代码中

**改进后**：
```sql
CREATE TABLE roles (
    role_id INT PRIMARY KEY AUTO_INCREMENT,
    role_code VARCHAR(50) UNIQUE NOT NULL,
    role_name VARCHAR(100) NOT NULL,
    role_type ENUM('system', 'enterprise', 'contractor') NOT NULL,
    company_id INT,  -- 企业自定义角色时使用
    parent_role_id INT,  -- 继承权限
    permission_level INT NOT NULL,
    description VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    is_system BOOLEAN DEFAULT FALSE,  -- 系统内置角色不可删除
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT,
    deleted_at DATETIME,
    deleted_by INT,
    
    INDEX idx_role_code (role_code),
    INDEX idx_role_type (role_type),
    INDEX idx_company_id (company_id),
    INDEX idx_is_deleted (is_deleted)
);
```
**价值**：
- ✅ 角色可配置，不再固化在代码
- ✅ 支持企业自定义角色
- ✅ 支持角色继承
- ✅ 灵活的权限管理

**对比**：
| 功能 | 改进前 | 改进后 |
|------|--------|--------|
| 角色定义 | 代码中硬编码 | 数据库配置 |
| 新增角色 | 需要修改代码 | 管理界面操作 |
| 企业自定义 | ❌ 不支持 | ✅ 支持 |
| 权限配置 | ❌ 固定 | ✅ 灵活配置 |

---

### 🆕 角色权限表（role_permissions）

**改进前**：❌ 不存在

**改进后**：
```sql
CREATE TABLE role_permissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    role_id INT NOT NULL,
    permission_code VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT,
    
    UNIQUE KEY uk_role_permission (role_id, permission_code),
    INDEX idx_role_id (role_id),
    INDEX idx_resource_type (resource_type)
);
```
**价值**：
- ✅ 细粒度权限控制
- ✅ 权限可配置
- ✅ 支持资源级权限

**权限示例**：
```sql
-- 企业管理员权限
INSERT INTO role_permissions (role_id, permission_code, resource_type, action) VALUES
(2, 'ticket.create', 'ticket', 'create'),
(2, 'ticket.read', 'ticket', 'read'),
(2, 'ticket.update', 'ticket', 'update'),
(2, 'ticket.delete', 'ticket', 'delete'),
(2, 'ticket.approve', 'ticket', 'approve'),
(2, 'user.create', 'user', 'create'),
(2, 'user.manage', 'user', 'manage');
```

---

### 🆕 工单流程定义表（workflow_definitions）

**改进前**：❌ 不存在，流程固化

**改进后**：
```sql
CREATE TABLE workflow_definitions (
    workflow_id INT PRIMARY KEY AUTO_INCREMENT,
    workflow_code VARCHAR(50) UNIQUE NOT NULL,
    workflow_name VARCHAR(100) NOT NULL,
    workflow_type VARCHAR(50) NOT NULL,
    company_id INT,  -- NULL表示系统通用流程
    description VARCHAR(500),
    version INT DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT,
    deleted_at DATETIME,
    deleted_by INT,
    
    INDEX idx_workflow_code (workflow_code),
    INDEX idx_company_id (company_id),
    INDEX idx_is_active (is_active),
    INDEX idx_is_deleted (is_deleted)
);
```
**价值**：
- ✅ 流程可配置
- ✅ 支持企业自定义流程
- ✅ 支持流程版本管理
- ✅ 灵活的流程定义

---

### 🆕 工单流程步骤表（workflow_steps）

**改进前**：❌ 不存在

**改进后**：
```sql
CREATE TABLE workflow_steps (
    step_id INT PRIMARY KEY AUTO_INCREMENT,
    workflow_id INT NOT NULL,
    step_code VARCHAR(50) NOT NULL,
    step_name VARCHAR(100) NOT NULL,
    step_order INT NOT NULL,
    step_type ENUM('start', 'approval', 'notify', 'end') NOT NULL,
    require_approval BOOLEAN DEFAULT FALSE,
    approver_role_id INT,
    approval_level INT,
    can_reject BOOLEAN DEFAULT TRUE,
    reject_to_step_id INT,
    can_cancel BOOLEAN DEFAULT TRUE,
    timeout_hours INT,
    description VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT,
    
    UNIQUE KEY uk_workflow_step (workflow_id, step_code),
    INDEX idx_workflow_id (workflow_id),
    INDEX idx_step_order (step_order),
    INDEX idx_approver_role_id (approver_role_id)
);
```
**价值**：
- ✅ 定义流程的具体步骤
- ✅ 支持审批配置
- ✅ 支持退回配置
- ✅ 支持超时配置

**流程示例**：
```
步骤1: 开始 (start)
  ↓
步骤2: 提交申请 (approval, 不需要审批)
  ↓
步骤3: 部门审批 (approval, 需要审批, 可退回到步骤2)
  ↓
步骤4: 安全审批 (approval, 需要审批, 可退回到步骤2)
  ↓
步骤5: 最终审批 (approval, 需要审批, 可退回到步骤2)
  ↓
步骤6: 完成 (end)
```

---

### 🆕 工单流转日志表（ticket_flow_logs）

**改进前**：❌ 不存在，无法追踪流转历史

**改进后**：
```sql
CREATE TABLE ticket_flow_logs (
    log_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    ticket_id INT NOT NULL,
    ticket_no VARCHAR(50) NOT NULL,
    from_step_id INT,
    from_step_name VARCHAR(100),
    to_step_id INT NOT NULL,
    to_step_name VARCHAR(100) NOT NULL,
    action ENUM('submit', 'approve', 'reject', 'cancel', 'restart', 'complete') NOT NULL,
    operator_id INT NOT NULL,
    operator_name VARCHAR(100) NOT NULL,
    operator_role VARCHAR(100) NOT NULL,
    approval_result ENUM('pending', 'approved', 'rejected'),
    approval_comments VARCHAR(1000),
    operation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    duration_minutes INT,
    ip_address VARCHAR(50),
    attachments VARCHAR(1000),
    
    INDEX idx_ticket_id (ticket_id),
    INDEX idx_ticket_no (ticket_no),
    INDEX idx_operator_id (operator_id),
    INDEX idx_operation_time (operation_time),
    INDEX idx_action (action)
);
```
**价值**：
- ✅ 完整记录工单流转历史
- ✅ 记录审批意见
- ✅ 记录停留时长
- ✅ 支持审计和追溯

**查询示例**：
```python
# 查询工单流转历史
logs = await get_ticket_flow_logs(ticket_id=123)
for log in logs:
    print(f"{log.operation_time}: {log.operator_name}")
    print(f"  {log.from_step_name} → {log.to_step_name}")
    print(f"  操作: {log.action}, 意见: {log.approval_comments}")
```

---

### 🆕 工单实例步骤表（ticket_step_instances）

**改进前**：❌ 不存在

**改进后**：
```sql
CREATE TABLE ticket_step_instances (
    instance_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    ticket_id INT NOT NULL,
    step_id INT NOT NULL,
    step_name VARCHAR(100) NOT NULL,
    status ENUM('pending', 'in_progress', 'completed', 'rejected', 'skipped') DEFAULT 'pending',
    assignee_id INT,
    assignee_name VARCHAR(100),
    arrived_at DATETIME,
    started_at DATETIME,
    completed_at DATETIME,
    deadline DATETIME,
    result VARCHAR(50),
    comments VARCHAR(1000),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_ticket_id (ticket_id),
    INDEX idx_step_id (step_id),
    INDEX idx_status (status),
    INDEX idx_assignee_id (assignee_id)
);
```
**价值**：
- ✅ 记录工单在各步骤的状态
- ✅ 记录处理人和处理时间
- ✅ 支持超时监控
- ✅ 支持任务分配

---

## 5️⃣ 功能对比

### 用户管理功能

| 功能 | 改进前 | 改进后 |
|------|--------|--------|
| 用户创建 | ✅ | ✅ |
| 用户更新 | ✅ | ✅ + 变更日志 |
| 用户删除 | ❌ 物理删除 | ✅ 软删除 + 日志 |
| 用户恢复 | ❌ 不支持 | ✅ 支持 |
| 账号锁定 | ❌ 不支持 | ✅ 支持 |
| 登录失败锁定 | ❌ 不支持 | ✅ 自动锁定 |
| 变更历史查询 | ❌ 不支持 | ✅ 完整日志 |
| 操作审计 | ❌ 无 | ✅ 完整审计 |

### 角色权限功能

| 功能 | 改进前 | 改进后 |
|------|--------|--------|
| 角色定义 | ❌ 代码硬编码 | ✅ 数据库配置 |
| 新增角色 | ❌ 需改代码 | ✅ 管理界面 |
| 企业自定义角色 | ❌ 不支持 | ✅ 支持 |
| 权限配置 | ❌ 固定 | ✅ 灵活配置 |
| 权限检查 | ✅ 代码判断 | ✅ 数据库查询 |
| 权限继承 | ❌ 不支持 | ✅ 支持 |

### 工单管理功能

| 功能 | 改进前 | 改进后 |
|------|--------|--------|
| 工单创建 | ✅ | ✅ + 唯一编号 |
| 工单编号 | ❌ 无 | ✅ 唯一编号 |
| 工单状态 | ❌ 无 | ✅ 多种状态 |
| 工单流程 | ❌ 固化 | ✅ 可配置 |
| 流程流转 | ❌ 不支持 | ✅ 完整支持 |
| 审批功能 | ❌ 不支持 | ✅ 支持 |
| 退回功能 | ❌ 不支持 | ✅ 支持 |
| 作废功能 | ❌ 不支持 | ✅ 支持 |
| 流转日志 | ❌ 无 | ✅ 完整日志 |
| 步骤追踪 | ❌ 无 | ✅ 实时追踪 |
| 超时监控 | ❌ 不支持 | ✅ 支持 |

---

## 6️⃣ 数据安全对比

### 数据删除

**改进前**：
```python
# 物理删除，数据永久丢失
async def delete_user(user_id: int):
    await session.delete(user)
    await session.commit()
    # ❌ 数据无法恢复
```

**改进后**：
```python
# 软删除，数据可恢复
async def delete_user(user_id: int, operator_id: int):
    user.is_deleted = True
    user.deleted_at = datetime.now()
    user.deleted_by = operator_id
    user.status = 'deleted'
    await session.commit()
    
    # 记录日志
    await log_user_change(
        user_id=user_id,
        operation_type='delete',
        operator_id=operator_id
    )
    # ✅ 数据可恢复，有审计记录
```

### 数据恢复

**改进前**：❌ 不支持

**改进后**：
```python
# 恢复已删除用户
async def restore_user(user_id: int, operator_id: int):
    user.is_deleted = False
    user.deleted_at = None
    user.deleted_by = None
    user.status = 'active'
    await session.commit()
    
    # 记录日志
    await log_user_change(
        user_id=user_id,
        operation_type='restore',
        operator_id=operator_id
    )
    # ✅ 数据恢复，有审计记录
```

---

## 7️⃣ 查询性能对比

### 用户查询

**改进前**：
```python
# 查询所有用户（包括已删除）
users = await session.exec(select(User)).all()
```

**改进后**：
```python
# 只查询未删除用户
users = await session.exec(
    select(User).where(User.is_deleted == False)
).all()

# 添加索引后性能更好
# CREATE INDEX idx_is_deleted ON users(is_deleted);
```

### 工单查询

**改进前**：
```python
# 查询所有工单
tickets = await session.exec(select(Ticket)).all()
# ❌ 无法按状态筛选
# ❌ 无法按流程筛选
```

**改进后**：
```python
# 查询进行中的工单
tickets = await session.exec(
    select(Ticket).where(
        Ticket.status == 'in_progress',
        Ticket.is_deleted == False
    )
).all()

# 查询待审批的工单
tickets = await session.exec(
    select(Ticket)
    .join(WorkflowStep)
    .where(
        Ticket.current_step_id == WorkflowStep.step_id,
        WorkflowStep.require_approval == True,
        Ticket.is_deleted == False
    )
).all()

# ✅ 支持多维度查询
# ✅ 添加索引后性能更好
```

---

## 8️⃣ API响应对比

### 用户详情API

**改进前**：
```json
{
  "user_id": 123,
  "username": "zhangsan",
  "user_type": "enterprise",
  "enterprise_user": {
    "name": "张三",
    "phone": "13800138000",
    "role_type": "manager"
  }
}
```

**改进后**：
```json
{
  "user_id": 123,
  "username": "zhangsan",
  "user_type": "enterprise",
  "status": "active",
  "last_login_at": "2025-01-04 10:30:00",
  "created_at": "2024-01-01 00:00:00",
  "created_by": 1,
  "enterprise_user": {
    "name": "张三",
    "phone": "13800138000",
    "role": {
      "role_id": 2,
      "role_name": "企业管理员",
      "permission_level": 1
    }
  },
  "permissions": [
    "ticket.create",
    "ticket.approve",
    "user.manage"
  ]
}
```

### 工单详情API

**改进前**：
```json
{
  "ticket_id": 456,
  "apply_date": "2025-01-04",
  "applicant": 123,
  "area_id": 1,
  "working_content": "设备维修",
  "pre_st": "2025-01-05 08:00:00",
  "pre_et": "2025-01-05 18:00:00"
}
```

**改进后**：
```json
{
  "ticket_id": 456,
  "ticket_no": "TK20250104000001",
  "status": "in_progress",
  "apply_date": "2025-01-04",
  "applicant": {
    "user_id": 123,
    "name": "张三"
  },
  "area": {
    "area_id": 1,
    "area_name": "A厂区"
  },
  "working_content": "设备维修",
  "pre_st": "2025-01-05 08:00:00",
  "pre_et": "2025-01-05 18:00:00",
  "workflow": {
    "workflow_id": 1,
    "workflow_name": "默认工单审批流程"
  },
  "current_step": {
    "step_id": 3,
    "step_name": "部门审批",
    "assignee": {
      "user_id": 124,
      "name": "李四"
    }
  },
  "flow_logs": [
    {
      "operation_time": "2025-01-04 09:00:00",
      "operator_name": "张三",
      "action": "submit",
      "from_step": "提交申请",
      "to_step": "部门审批"
    }
  ]
}
```

---

## 9️⃣ 总结

### 核心改进

1. **数据安全** ⬆️
   - 软删除机制保护数据
   - 完整的审计日志
   - 数据可恢复

2. **功能灵活性** ⬆️
   - 角色权限可配置
   - 工单流程可定制
   - 企业级定制支持

3. **可追溯性** ⬆️
   - 用户变更日志
   - 工单流转日志
   - 完整的审计信息

4. **管理便捷性** ⬆️
   - 统一用户管理
   - 工单唯一编号
   - 状态清晰明确

5. **系统扩展性** ⬆️
   - 支持企业自定义
   - 支持流程扩展
   - 支持权限扩展

### 实施建议

1. **分阶段实施**：按照实施检查清单逐步推进
2. **充分测试**：每个阶段都要在测试环境验证
3. **数据备份**：每次迁移前完整备份
4. **监控告警**：上线后密切监控系统状态
5. **用户培训**：对管理员和用户进行培训

---

**文档版本**：v1.0  
**创建日期**：2025-01-04  
**配套文档**：
- DATABASE_IMPROVEMENT_PLAN.md（详细方案）
- DATABASE_ERD.md（数据库ER图）
- IMPLEMENTATION_CHECKLIST.md（实施清单）
- DATABASE_IMPROVEMENT_SUMMARY.md（执行摘要）

