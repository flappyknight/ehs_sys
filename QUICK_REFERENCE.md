# 数据库改进方案 - 快速参考卡

## 📚 文档导航

| 文档 | 用途 | 适合人群 |
|------|------|----------|
| **DATABASE_IMPROVEMENT_SUMMARY.md** | 执行摘要，快速了解改进点 | 决策者、项目经理 |
| **DATABASE_IMPROVEMENT_PLAN.md** | 详细改进方案，包含完整SQL | 开发人员、DBA |
| **DATABASE_ERD.md** | 数据库ER图和关系说明 | 架构师、开发人员 |
| **BEFORE_AFTER_COMPARISON.md** | 改进前后对比 | 所有人 |
| **IMPLEMENTATION_CHECKLIST.md** | 实施检查清单 | 项目经理、实施人员 |
| **QUICK_REFERENCE.md** | 快速参考（本文档） | 所有人 |

---

## 🎯 核心改进点速查

### 1. 统一用户管理
```
所有用户 → users表
├── admin（管理员）
├── enterprise（企业用户）→ enterprise_user表（扩展信息）
└── contractor（承包商用户）→ contractor_user表（扩展信息）
```

### 2. 软删除机制
```sql
-- 所有核心表添加
is_deleted BOOLEAN DEFAULT FALSE
deleted_at DATETIME
deleted_by INT
```

### 3. 用户变更日志
```
user_change_logs表
记录：创建、更新、删除、锁定、解锁、密码重置等
```

### 4. 角色权限系统
```
roles表（角色定义）
  ↓
role_permissions表（权限配置）
  ↓
enterprise_user.role_id / contractor_user.role_id
```

### 5. 工单流程化
```
workflow_definitions（流程定义）
  ↓
workflow_steps（流程步骤）
  ↓
ticket（工单实例）
  ├── ticket_flow_logs（流转日志）
  └── ticket_step_instances（步骤实例）
```

---

## 📊 新增表速查

| 表名 | 用途 | 重要性 |
|------|------|--------|
| `user_change_logs` | 用户变更日志 | ⭐⭐⭐⭐⭐ |
| `roles` | 角色定义 | ⭐⭐⭐⭐⭐ |
| `role_permissions` | 角色权限 | ⭐⭐⭐⭐⭐ |
| `workflow_definitions` | 工单流程定义 | ⭐⭐⭐⭐⭐ |
| `workflow_steps` | 流程步骤 | ⭐⭐⭐⭐⭐ |
| `ticket_flow_logs` | 工单流转日志 | ⭐⭐⭐⭐⭐ |
| `ticket_step_instances` | 工单步骤实例 | ⭐⭐⭐⭐ |

---

## 🔧 常用SQL速查

### 软删除用户
```sql
UPDATE users 
SET is_deleted = TRUE,
    deleted_at = NOW(),
    deleted_by = ?,
    status = 'deleted'
WHERE user_id = ?;
```

### 恢复用户
```sql
UPDATE users 
SET is_deleted = FALSE,
    deleted_at = NULL,
    deleted_by = NULL,
    status = 'active'
WHERE user_id = ?;
```

### 查询未删除用户
```sql
SELECT * FROM users 
WHERE is_deleted = FALSE;
```

### 查询用户变更历史
```sql
SELECT * FROM user_change_logs 
WHERE user_id = ? 
ORDER BY operation_time DESC;
```

### 查询用户权限
```sql
SELECT rp.permission_code, rp.resource_type, rp.action
FROM users u
JOIN enterprise_user eu ON u.enterprise_user_id = eu.user_id
JOIN roles r ON eu.role_id = r.role_id
JOIN role_permissions rp ON r.role_id = rp.role_id
WHERE u.user_id = ?;
```

### 查询工单流转历史
```sql
SELECT * FROM ticket_flow_logs 
WHERE ticket_id = ? 
ORDER BY operation_time ASC;
```

### 查询待审批工单
```sql
SELECT t.*, ws.step_name
FROM ticket t
JOIN workflow_steps ws ON t.current_step_id = ws.step_id
WHERE ws.require_approval = TRUE
  AND t.status = 'in_progress'
  AND t.is_deleted = FALSE;
```

---

## 🎨 状态枚举速查

### 用户状态（users.status）
```python
'active'    # 启用
'inactive'  # 停用
'locked'    # 锁定
'deleted'   # 已删除
```

### 工单状态（ticket.status）
```python
'draft'        # 草稿
'in_progress'  # 进行中
'completed'    # 已完成
'cancelled'    # 已作废
'rejected'     # 已拒绝
```

### 步骤类型（workflow_steps.step_type）
```python
'start'     # 开始
'approval'  # 审批
'notify'    # 通知
'end'       # 结束
```

### 步骤状态（ticket_step_instances.status）
```python
'pending'      # 待处理
'in_progress'  # 处理中
'completed'    # 已完成
'rejected'     # 已拒绝
'skipped'      # 已跳过
```

### 操作类型（user_change_logs.operation_type）
```python
'create'          # 创建
'update'          # 更新
'delete'          # 删除
'lock'            # 锁定
'unlock'          # 解锁
'reset_password'  # 重置密码
'status_change'   # 状态变更
```

### 流转动作（ticket_flow_logs.action）
```python
'submit'    # 提交
'approve'   # 批准
'reject'    # 退回
'cancel'    # 作废
'restart'   # 重新开始
'complete'  # 完成
```

---

## 🔑 系统预置角色速查

### 管理员角色
```
admin - 系统管理员（permission_level: 0）
```

### 企业角色
```
enterprise_manager   - 企业管理员（permission_level: 1）
enterprise_approver  - 企业审批员（permission_level: 2）
enterprise_staff     - 企业普通员工（permission_level: 3）
```

### 承包商角色
```
contractor_manager   - 承包商管理员（permission_level: 1）
contractor_approver  - 承包商审批员（permission_level: 2）
contractor_worker    - 承包商普通员工（permission_level: 3）
```

---

## 📝 权限编码规范

### 格式
```
{resource}.{action}
```

### 示例
```python
# 工单权限
'ticket.create'   # 创建工单
'ticket.read'     # 查看工单
'ticket.update'   # 更新工单
'ticket.delete'   # 删除工单
'ticket.approve'  # 审批工单
'ticket.reject'   # 退回工单

# 用户权限
'user.create'     # 创建用户
'user.read'       # 查看用户
'user.update'     # 更新用户
'user.delete'     # 删除用户
'user.manage'     # 管理用户

# 角色权限
'role.create'     # 创建角色
'role.read'       # 查看角色
'role.update'     # 更新角色
'role.delete'     # 删除角色
'role.assign'     # 分配角色
```

---

## 🎫 工单编号规则

### 格式
```
TK + YYYYMMDD + 6位序号
```

### 示例
```
TK20250104000001  # 2025年1月4日第1个工单
TK20250104000002  # 2025年1月4日第2个工单
TK20250105000001  # 2025年1月5日第1个工单
```

### 生成逻辑
```python
def generate_ticket_no(apply_date: date) -> str:
    date_str = apply_date.strftime('%Y%m%d')
    prefix = f'TK{date_str}'
    
    # 获取当天最大序号
    max_seq = get_max_seq_for_date(date_str)
    seq = (max_seq or 0) + 1
    
    return f'{prefix}{seq:06d}'
```

---

## 🔄 工单流程示例

### 标准审批流程
```
1. 开始 (start)
   ↓
2. 提交申请 (approval, 不需要审批)
   ↓
3. 部门审批 (approval, 需要审批, 可退回)
   ↓
4. 安全审批 (approval, 需要审批, 可退回)
   ↓
5. 最终审批 (approval, 需要审批, 可退回)
   ↓
6. 完成 (end)
```

### 流转操作
```python
# 提交工单
flow_ticket(ticket_id, action='submit', operator_id)

# 审批通过
flow_ticket(ticket_id, action='approve', operator_id, comments='同意')

# 审批退回
flow_ticket(ticket_id, action='reject', operator_id, comments='需要补充材料')

# 作废工单
flow_ticket(ticket_id, action='cancel', operator_id, comments='不再需要')
```

---

## 📈 索引建议速查

### 用户相关
```sql
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_type_status ON users(user_type, status, is_deleted);
CREATE INDEX idx_users_is_deleted ON users(is_deleted);
CREATE INDEX idx_enterprise_user_company ON enterprise_user(company_id);
CREATE INDEX idx_enterprise_user_role ON enterprise_user(role_id);
CREATE INDEX idx_contractor_user_contractor ON contractor_user(contractor_id);
CREATE INDEX idx_contractor_user_role ON contractor_user(role_id);
```

### 工单相关
```sql
CREATE INDEX idx_ticket_no ON ticket(ticket_no);
CREATE INDEX idx_ticket_workflow ON ticket(workflow_id);
CREATE INDEX idx_ticket_current_step ON ticket(current_step_id);
CREATE INDEX idx_ticket_status ON ticket(status);
CREATE INDEX idx_ticket_company_status ON ticket(company_id, status, is_deleted);
CREATE INDEX idx_ticket_applicant_date ON ticket(applicant_id, apply_date);
```

### 日志相关
```sql
CREATE INDEX idx_user_change_logs_user ON user_change_logs(user_id);
CREATE INDEX idx_user_change_logs_operator ON user_change_logs(operator_id);
CREATE INDEX idx_user_change_logs_time ON user_change_logs(operation_time);
CREATE INDEX idx_ticket_flow_logs_ticket ON ticket_flow_logs(ticket_id);
CREATE INDEX idx_ticket_flow_logs_time ON ticket_flow_logs(operation_time);
```

### 角色权限相关
```sql
CREATE INDEX idx_roles_code ON roles(role_code);
CREATE INDEX idx_roles_company ON roles(company_id, is_deleted);
CREATE INDEX idx_role_permissions_role ON role_permissions(role_id);
```

---

## 🛠️ Python代码示例

### 软删除用户
```python
async def delete_user(engine, user_id: int, operator_id: int):
    async with get_session(engine) as session:
        user = await session.get(User, user_id)
        user.is_deleted = True
        user.deleted_at = datetime.now()
        user.deleted_by = operator_id
        user.status = 'deleted'
        await session.commit()
        
        # 记录日志
        await log_user_change(
            session, user_id, 'delete', operator_id
        )
```

### 检查权限
```python
async def check_permission(user: User, permission_code: str) -> bool:
    if user.user_type == 'admin':
        return True
    
    if user.user_type == 'enterprise':
        role_id = user.enterprise_user.role_id
    elif user.user_type == 'contractor':
        role_id = user.contractor_user.role_id
    else:
        return False
    
    statement = select(RolePermission).where(
        RolePermission.role_id == role_id,
        RolePermission.permission_code == permission_code
    )
    result = await session.exec(statement)
    return result.first() is not None
```

### 工单流转
```python
async def flow_ticket(
    engine, 
    ticket_id: int, 
    action: str,
    operator_id: int,
    comments: str = None
):
    async with get_session(engine) as session:
        ticket = await session.get(Ticket, ticket_id)
        current_step = await session.get(WorkflowStep, ticket.current_step_id)
        
        # 确定下一步
        if action == 'approve':
            next_step = await get_next_step(session, current_step)
        elif action == 'reject':
            next_step = await session.get(WorkflowStep, current_step.reject_to_step_id)
        elif action == 'cancel':
            ticket.status = 'cancelled'
            ticket.cancelled_at = datetime.now()
            ticket.cancelled_by = operator_id
            ticket.cancelled_reason = comments
        
        # 更新工单
        if action != 'cancel':
            ticket.previous_step_id = ticket.current_step_id
            ticket.current_step_id = next_step.step_id
        
        # 记录日志
        await log_ticket_flow(
            session, ticket_id, current_step, next_step,
            action, operator_id, comments
        )
        
        await session.commit()
```

---

## 📋 实施步骤速查

### 第一阶段（1-2周）：基础表改造
- [ ] 添加软删除字段到现有表
- [ ] 创建用户操作日志表
- [ ] 创建角色相关表

### 第二阶段（2-3周）：用户系统重构
- [ ] 重构用户表
- [ ] 迁移现有用户数据
- [ ] 实现用户变更日志功能
- [ ] 更新用户管理API

### 第三阶段（3-4周）：工单流程系统
- [ ] 创建工单流程相关表
- [ ] 重构工单表
- [ ] 实现工单流转逻辑
- [ ] 迁移现有工单数据
- [ ] 更新工单管理API

### 第四阶段（1-2周）：权限系统完善
- [ ] 实现角色管理
- [ ] 实现权限控制
- [ ] 实现企业级权限定制

---

## ⚠️ 注意事项

### 数据备份
```bash
# 备份数据库
mysqldump -u root -p ehs_sys > backup_$(date +%Y%m%d_%H%M%S).sql

# 恢复数据库
mysql -u root -p ehs_sys < backup_20250104_100000.sql
```

### 测试验证
- ✅ 在测试环境充分测试
- ✅ 验证数据迁移完整性
- ✅ 验证功能正常运行
- ✅ 验证性能指标

### 回滚准备
- ✅ 保留旧表备份
- ✅ 准备回滚脚本
- ✅ 测试回滚流程

---

## 🔗 相关资源

### 文档
- DATABASE_IMPROVEMENT_PLAN.md - 详细改进方案
- DATABASE_ERD.md - 数据库ER图
- IMPLEMENTATION_CHECKLIST.md - 实施检查清单
- DATABASE_IMPROVEMENT_SUMMARY.md - 执行摘要
- BEFORE_AFTER_COMPARISON.md - 改进前后对比

### 工具
- Alembic - 数据库迁移工具
- SQLModel - Python ORM
- FastAPI - Web框架

### 命令
```bash
# 激活虚拟环境
conda activate ehs_env

# 运行数据库迁移
alembic upgrade head

# 启动服务
./start-server.sh
```

---

## 📞 支持

如有问题，请参考：
1. 详细文档（DATABASE_IMPROVEMENT_PLAN.md）
2. 实施清单（IMPLEMENTATION_CHECKLIST.md）
3. 对比文档（BEFORE_AFTER_COMPARISON.md）

---

**文档版本**：v1.0  
**创建日期**：2025-01-04  
**最后更新**：2025-01-04

