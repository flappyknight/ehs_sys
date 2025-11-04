# 数据库ER图（实体关系图）

## 核心表关系图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              用户与角色体系                                    │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌──────────────────┐
                    │   Company        │
                    │  (企业/承包商)    │
                    ├──────────────────┤
                    │ company_id (PK)  │
                    │ name             │
                    │ type             │
                    │ is_deleted       │
                    └────────┬─────────┘
                             │
                ┌────────────┼────────────┐
                │            │            │
                ▼            ▼            ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │ Department   │  │   Roles      │  │  Contractor  │
    ├──────────────┤  ├──────────────┤  ├──────────────┤
    │ dept_id (PK) │  │ role_id (PK) │  │contractor_id │
    │ company_id   │  │ role_code    │  │company_name  │
    │ name         │  │ role_name    │  │license_file  │
    │ parent_id    │  │ role_type    │  │is_deleted    │
    │ is_deleted   │  │ company_id   │  └──────┬───────┘
    └──────┬───────┘  │ permission_  │         │
           │          │   level      │         │
           │          │ is_deleted   │         │
           │          └──────┬───────┘         │
           │                 │                 │
           │                 │                 │
           │          ┌──────┴───────┐         │
           │          │              │         │
           ▼          ▼              ▼         ▼
    ┌──────────────────────┐  ┌──────────────────────┐
    │  EnterpriseUser      │  │  ContractorUser      │
    ├──────────────────────┤  ├──────────────────────┤
    │ user_id (PK)         │  │ user_id (PK)         │
    │ company_id (FK)      │  │ contractor_id (FK)   │
    │ dept_id (FK)         │  │ role_id (FK)         │
    │ role_id (FK)         │  │ name                 │
    │ name                 │  │ phone                │
    │ phone                │  │ id_number            │
    │ email                │  │ work_type            │
    │ position             │  │ status               │
    │ approval_level       │  │ is_deleted           │
    │ status               │  └──────────┬───────────┘
    │ is_deleted           │             │
    └──────────┬───────────┘             │
               │                         │
               └────────┬────────────────┘
                        │
                        ▼
              ┌──────────────────┐
              │      Users       │
              │  (统一用户表)     │
              ├──────────────────┤
              │ user_id (PK)     │
              │ username         │
              │ password_hash    │
              │ user_type        │
              │ status           │
              │ enterprise_      │
              │   user_id (FK)   │
              │ contractor_      │
              │   user_id (FK)   │
              │ is_deleted       │
              │ last_login_at    │
              │ created_by       │
              │ updated_by       │
              │ deleted_by       │
              └──────────┬───────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ UserChangeLogs       │
              │  (用户变更日志)       │
              ├──────────────────────┤
              │ log_id (PK)          │
              │ user_id (FK)         │
              │ operation_type       │
              │ operator_id (FK)     │
              │ field_name           │
              │ old_value            │
              │ new_value            │
              │ change_reason        │
              │ operation_time       │
              └──────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                            工单流程体系                                        │
└─────────────────────────────────────────────────────────────────────────────┘

              ┌──────────────────────────┐
              │ WorkflowDefinitions      │
              │   (流程定义)              │
              ├──────────────────────────┤
              │ workflow_id (PK)         │
              │ workflow_code            │
              │ workflow_name            │
              │ workflow_type            │
              │ company_id (FK)          │
              │ version                  │
              │ is_active                │
              │ is_deleted               │
              └────────────┬─────────────┘
                           │
                           │ 1:N
                           ▼
              ┌──────────────────────────┐
              │ WorkflowSteps            │
              │   (流程步骤)              │
              ├──────────────────────────┤
              │ step_id (PK)             │
              │ workflow_id (FK)         │
              │ step_code                │
              │ step_name                │
              │ step_order               │
              │ step_type                │
              │ require_approval         │
              │ approver_role_id (FK)    │
              │ approval_level           │
              │ can_reject               │
              │ reject_to_step_id (FK)   │
              │ can_cancel               │
              │ timeout_hours            │
              └────────────┬─────────────┘
                           │
                           │ N:1
                           ▼
              ┌──────────────────────────┐
              │      Ticket              │
              │      (工单)               │
              ├──────────────────────────┤
              │ ticket_id (PK)           │
              │ ticket_no (UNIQUE)       │
              │ workflow_id (FK)         │
              │ current_step_id (FK)     │
              │ previous_step_id (FK)    │
              │ status                   │
              │ apply_date               │
              │ applicant_id (FK)        │
              │ company_id (FK)          │
              │ area_id (FK)             │
              │ working_content          │
              │ pre_st / pre_et          │
              │ actual_st / actual_et    │
              │ worker_id (FK)           │
              │ custodian_id (FK)        │
              │ tools / danger /         │
              │   protection             │
              │ hot_work                 │
              │ work_height_level        │
              │ is_deleted               │
              │ cancelled_at             │
              │ cancelled_by             │
              └────┬──────────────┬──────┘
                   │              │
                   │ 1:N          │ 1:N
                   ▼              ▼
    ┌──────────────────────┐  ┌──────────────────────┐
    │ TicketStepInstances  │  │  TicketFlowLogs      │
    │  (工单步骤实例)       │  │  (工单流转日志)       │
    ├──────────────────────┤  ├──────────────────────┤
    │ instance_id (PK)     │  │ log_id (PK)          │
    │ ticket_id (FK)       │  │ ticket_id (FK)       │
    │ step_id (FK)         │  │ ticket_no            │
    │ step_name            │  │ from_step_id (FK)    │
    │ status               │  │ from_step_name       │
    │ assignee_id (FK)     │  │ to_step_id (FK)      │
    │ assignee_name        │  │ to_step_name         │
    │ arrived_at           │  │ action               │
    │ started_at           │  │ operator_id (FK)     │
    │ completed_at         │  │ operator_name        │
    │ deadline             │  │ operator_role        │
    │ result               │  │ approval_result      │
    │ comments             │  │ approval_comments    │
    └──────────────────────┘  │ operation_time       │
                              │ duration_minutes     │
                              └──────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                            角色权限体系                                        │
└─────────────────────────────────────────────────────────────────────────────┘

              ┌──────────────────────┐
              │      Roles           │
              ├──────────────────────┤
              │ role_id (PK)         │
              │ role_code            │
              │ role_name            │
              │ role_type            │
              │ company_id (FK)      │
              │ permission_level     │
              │ is_system            │
              └──────────┬───────────┘
                         │
                         │ 1:N
                         ▼
              ┌──────────────────────┐
              │  RolePermissions     │
              ├──────────────────────┤
              │ id (PK)              │
              │ role_id (FK)         │
              │ permission_code      │
              │ resource_type        │
              │ action               │
              └──────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                          作业区域与特殊作业                                    │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │   Company    │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐         ┌──────────────────┐
    │  Department  │────────▶│      Area        │
    └──────────────┘         │   (厂区/区域)     │
                             ├──────────────────┤
                             │ area_id (PK)     │
                             │ enterprise_id    │
                             │ area_name        │
                             │ dept_id (FK)     │
                             │ is_deleted       │
                             └────────┬─────────┘
                                      │
                                      ▼
                             ┌──────────────────┐
                             │    Ticket        │
                             │ area_id (FK)     │
                             └────────┬─────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 ▼
         ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
         │ConfinedSpace │  │TemporaryPower│  │  CrossWork   │
         │ (受限空间)    │  │  (临时用电)   │  │ (交叉作业)    │
         ├──────────────┤  ├──────────────┤  ├──────────────┤
         │confined_     │  │temp_power_   │  │ id (PK)      │
         │  space_id    │  │  id (PK)     │  │ group_id     │
         │ticket_id (FK)│  │ticket_id (FK)│  │ area_id (FK) │
         │space_level   │  │equipment_id  │  │ticket_id (FK)│
         │space_name    │  │power_access_ │  └──────────────┘
         │original_     │  │  point       │
         │  medium      │  └──────────────┘
         └──────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                          承包商项目与进场管理                                  │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐         ┌──────────────────┐
    │  Contractor  │────────▶│ContractorProject │
    └──────────────┘         │   (合作项目)      │
                             ├──────────────────┤
           ┌─────────────────│ project_id (PK)  │
           │                 │ contractor_id    │
           │                 │ enterprise_id    │
           │                 │ project_name     │
           │                 │ leader_name      │
           │                 │ leader_phone     │
           │                 │ is_deleted       │
           │                 └────────┬─────────┘
           │                          │
           │                          │ 1:N
           │                          ▼
           │                 ┌──────────────────┐
           │                 │   EntryPlan      │
           │                 │  (进场计划)       │
           │                 ├──────────────────┤
           │                 │ plan_id (PK)     │
           │                 │ project_id (FK)  │
           │                 │ plan_date        │
           │                 │ status           │
           │                 └────────┬─────────┘
           │                          │
           │                          │ 1:N
           │                          ▼
           │                 ┌──────────────────┐
           │                 │ EntryPlanUser    │
           │                 │ (计划人员关联)    │
           │                 ├──────────────────┤
           │                 │ id (PK)          │
           │                 │ project_id (FK)  │
           │                 │ plan_id (FK)     │
           └────────────────▶│ user_id (FK)     │
                             └────────┬─────────┘
                                      │
                                      │ 1:1
                                      ▼
                             ┌──────────────────┐
                             │ EntryRegister    │
                             │  (进场登记)       │
                             ├──────────────────┤
                             │ register_id (PK) │
                             │ plan_user_id(FK) │
                             │ actual_time      │
                             │ photo_path       │
                             └──────────────────┘
```

## 关键关系说明

### 1. 用户体系
- **Users** 是核心用户表，通过 `user_type` 区分用户类型
- **EnterpriseUser** 和 **ContractorUser** 存储具体用户信息
- **Roles** 定义角色，可以是系统级或企业级
- **UserChangeLogs** 记录所有用户变更

### 2. 工单流程
- **WorkflowDefinitions** 定义流程模板
- **WorkflowSteps** 定义流程的各个步骤
- **Ticket** 是工单实例，关联流程定义
- **TicketStepInstances** 记录工单在各步骤的状态
- **TicketFlowLogs** 记录工单流转历史

### 3. 权限体系
- **Roles** 定义角色
- **RolePermissions** 定义角色的具体权限
- 支持企业级权限定制（通过 company_id）

### 4. 数据隔离
- 所有业务数据都关联 `company_id`
- 通过用户的企业归属实现数据隔离
- 查询时自动过滤非本企业数据

### 5. 软删除
- 所有核心表都有 `is_deleted` 字段
- 删除操作只标记，不物理删除
- 保留 `deleted_at` 和 `deleted_by` 审计信息

## 索引策略

### 高频查询索引
```sql
-- 用户查询
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_type_status ON users(user_type, status, is_deleted);

-- 工单查询
CREATE INDEX idx_ticket_company_status ON ticket(company_id, status, is_deleted);
CREATE INDEX idx_ticket_applicant_date ON ticket(applicant_id, apply_date);
CREATE INDEX idx_ticket_no ON ticket(ticket_no);

-- 流程查询
CREATE INDEX idx_ticket_flow_ticket ON ticket_flow_logs(ticket_id, operation_time);
CREATE INDEX idx_ticket_step_instance ON ticket_step_instances(ticket_id, status);

-- 角色权限查询
CREATE INDEX idx_role_permissions_role ON role_permissions(role_id);
CREATE INDEX idx_roles_company ON roles(company_id, is_deleted);
```

### 外键索引
```sql
-- 所有外键都应该有索引以提高JOIN性能
CREATE INDEX idx_enterprise_user_company ON enterprise_user(company_id);
CREATE INDEX idx_enterprise_user_dept ON enterprise_user(dept_id);
CREATE INDEX idx_enterprise_user_role ON enterprise_user(role_id);
-- ... 其他外键索引
```

## 分区策略

### 日志表分区（按月）
```sql
-- 用户变更日志表按月分区
ALTER TABLE user_change_logs PARTITION BY RANGE (TO_DAYS(operation_time)) (
    PARTITION p202501 VALUES LESS THAN (TO_DAYS('2025-02-01')),
    PARTITION p202502 VALUES LESS THAN (TO_DAYS('2025-03-01')),
    -- ... 继续添加
);

-- 工单流转日志表按月分区
ALTER TABLE ticket_flow_logs PARTITION BY RANGE (TO_DAYS(operation_time)) (
    PARTITION p202501 VALUES LESS THAN (TO_DAYS('2025-02-01')),
    PARTITION p202502 VALUES LESS THAN (TO_DAYS('2025-03-01')),
    -- ... 继续添加
);
```

### 工单表分区（按年）
```sql
-- 工单表按年分区
ALTER TABLE ticket PARTITION BY RANGE (YEAR(apply_date)) (
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p2025 VALUES LESS THAN (2026),
    PARTITION p2026 VALUES LESS THAN (2027),
    -- ... 继续添加
);
```

## 数据归档策略

### 归档规则
1. **用户变更日志**：保留最近12个月，超过12个月的归档到历史表
2. **工单流转日志**：保留最近24个月，超过24个月的归档
3. **已完成工单**：保留最近36个月，超过36个月的归档
4. **已删除数据**：保留最近6个月，超过6个月的可物理删除

### 归档表示例
```sql
-- 创建归档表（结构与原表相同）
CREATE TABLE user_change_logs_archive LIKE user_change_logs;
CREATE TABLE ticket_flow_logs_archive LIKE ticket_flow_logs;
CREATE TABLE ticket_archive LIKE ticket;

-- 定期归档任务（示例）
INSERT INTO user_change_logs_archive 
SELECT * FROM user_change_logs 
WHERE operation_time < DATE_SUB(NOW(), INTERVAL 12 MONTH);

DELETE FROM user_change_logs 
WHERE operation_time < DATE_SUB(NOW(), INTERVAL 12 MONTH);
```

---

**文档版本**：v1.0  
**创建日期**：2025-01-04  
**配套文档**：DATABASE_IMPROVEMENT_PLAN.md

