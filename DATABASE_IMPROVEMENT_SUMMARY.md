# 数据库改进方案 - 执行摘要

## 📌 核心改进点

### 1. **统一用户管理** ✅
**问题**：当前企业用户和承包商用户分散在不同表，管理复杂  
**解决方案**：
- 所有用户统一在 `users` 表管理
- 通过 `user_type` 字段区分用户类型（admin/enterprise/contractor）
- `enterprise_user` 和 `contractor_user` 表仅存储扩展信息

**优势**：
- 统一的用户认证和授权
- 简化用户管理逻辑
- 便于跨类型用户查询

---

### 2. **软删除机制** ✅
**问题**：当前系统直接物理删除数据，无法恢复  
**解决方案**：
- 所有核心表添加 `is_deleted` 字段
- 删除操作只标记，不物理删除
- 记录删除时间（`deleted_at`）和删除人（`deleted_by`）

**影响范围**：
- `users`
- `enterprise_user`
- `contractor_user`
- `company`
- `contractor`
- `department`
- `area`
- `contractor_project`
- `ticket`

**代码示例**：
```python
# 删除用户（软删除）
async def delete_user(engine, user_id: int, operator_id: int):
    async with get_session(engine) as session:
        user = await session.get(User, user_id)
        user.is_deleted = True
        user.deleted_at = datetime.now()
        user.deleted_by = operator_id
        user.status = 'deleted'
        await session.commit()
```

---

### 3. **用户变更日志** ✅
**问题**：无法追踪用户信息的变更历史  
**解决方案**：
- 新增 `user_change_logs` 表
- 记录所有用户变更操作
- 包含操作人、操作时间、变更内容等

**记录内容**：
- 用户创建
- 用户更新（记录字段级变更）
- 用户删除
- 用户锁定/解锁
- 密码重置
- 状态变更

**查询示例**：
```python
# 查询用户变更历史
async def get_user_change_logs(engine, user_id: int):
    statement = select(UserChangeLog).where(
        UserChangeLog.user_id == user_id
    ).order_by(UserChangeLog.operation_time.desc())
    
    async with get_session(engine) as session:
        result = await session.exec(statement)
        return result.all()
```

---

### 4. **角色权限系统** ✅
**问题**：当前角色权限固化在代码中，无法灵活配置  
**解决方案**：
- 新增 `roles` 表：定义角色
- 新增 `role_permissions` 表：定义角色权限
- 支持系统级和企业级角色
- 支持企业自定义角色和权限

**角色层级**：
```
系统角色（is_system=TRUE）
├── admin（系统管理员）
├── enterprise_manager（企业管理员）
├── enterprise_approver（企业审批员）
├── enterprise_staff（企业员工）
├── contractor_manager（承包商管理员）
├── contractor_approver（承包商审批员）
└── contractor_worker（承包商工人）

企业自定义角色（company_id != NULL）
├── 企业A的自定义角色1
├── 企业A的自定义角色2
└── ...
```

**权限示例**：
```python
# 检查用户权限
async def check_permission(user: User, permission_code: str) -> bool:
    # 获取用户角色
    if user.user_type == 'enterprise':
        role_id = user.enterprise_user.role_id
    elif user.user_type == 'contractor':
        role_id = user.contractor_user.role_id
    else:
        return True  # admin has all permissions
    
    # 检查权限
    statement = select(RolePermission).where(
        RolePermission.role_id == role_id,
        RolePermission.permission_code == permission_code
    )
    result = await session.exec(statement)
    return result.first() is not None
```

---

### 5. **工单流程化** ✅
**问题**：当前工单状态固化，无法支持灵活的审批流程  
**解决方案**：
- 新增 `workflow_definitions` 表：定义流程模板
- 新增 `workflow_steps` 表：定义流程步骤
- 新增 `ticket_flow_logs` 表：记录流转历史
- 新增 `ticket_step_instances` 表：记录步骤实例
- 工单表添加流程相关字段

**工单状态机**：
```
draft（草稿）
  ↓ submit
in_progress（进行中）
  ↓ approve/reject/cancel
completed（已完成）/ cancelled（已作废）/ rejected（已拒绝）
```

**流程示例**：
```
开始 → 提交申请 → 部门审批 → 安全审批 → 最终审批 → 完成
        ↓           ↓           ↓           ↓
      作废        退回        退回        退回
```

**流转逻辑**：
```python
# 工单流转
async def flow_ticket(
    engine, 
    ticket_id: int, 
    action: str,  # submit/approve/reject/cancel
    operator_id: int,
    comments: str = None
):
    async with get_session(engine) as session:
        ticket = await session.get(Ticket, ticket_id)
        
        # 获取当前步骤
        current_step = await session.get(WorkflowStep, ticket.current_step_id)
        
        # 根据action确定下一步
        if action == 'approve':
            next_step = await get_next_step(session, current_step)
        elif action == 'reject':
            next_step = await session.get(WorkflowStep, current_step.reject_to_step_id)
        elif action == 'cancel':
            ticket.status = 'cancelled'
            ticket.cancelled_at = datetime.now()
            ticket.cancelled_by = operator_id
            ticket.cancelled_reason = comments
            await log_ticket_flow(...)
            await session.commit()
            return
        
        # 更新工单状态
        ticket.previous_step_id = ticket.current_step_id
        ticket.current_step_id = next_step.step_id
        
        # 记录流转日志
        await log_ticket_flow(
            session, ticket_id, 
            from_step=current_step, 
            to_step=next_step,
            action=action,
            operator_id=operator_id,
            comments=comments
        )
        
        await session.commit()
```

---

### 6. **工单唯一编号** ✅
**问题**：当前工单没有唯一编号，不便于追踪  
**解决方案**：
- 添加 `ticket_no` 字段（唯一索引）
- 格式：`TK + YYYYMMDD + 6位序号`
- 示例：`TK20250104000001`

**生成逻辑**：
```python
async def generate_ticket_no(engine, apply_date: date) -> str:
    date_str = apply_date.strftime('%Y%m%d')
    prefix = f'TK{date_str}'
    
    # 获取当天最大序号
    statement = select(func.max(Ticket.ticket_no)).where(
        Ticket.ticket_no.like(f'{prefix}%')
    )
    async with get_session(engine) as session:
        result = await session.exec(statement)
        max_no = result.first()
        
        if max_no:
            seq = int(max_no[-6:]) + 1
        else:
            seq = 1
        
        return f'{prefix}{seq:06d}'
```

---

### 7. **用户状态管理** ✅
**问题**：当前只有简单的 `status` 布尔字段，无法表达复杂状态  
**解决方案**：
- 改为枚举类型：`active`/`inactive`/`locked`/`deleted`
- 添加锁定相关字段：`login_attempts`、`locked_until`
- 添加最后登录时间：`last_login_at`

**状态说明**：
- `active`：正常启用
- `inactive`：已停用（可恢复）
- `locked`：已锁定（登录失败次数过多）
- `deleted`：已删除（软删除）

**登录控制**：
```python
async def authenticate_user(username: str, password: str):
    user = await get_user(engine, username)
    
    # 检查用户状态
    if user.status == 'deleted':
        raise HTTPException(401, "用户不存在")
    if user.status == 'inactive':
        raise HTTPException(401, "用户已停用")
    if user.status == 'locked':
        if user.locked_until and user.locked_until > datetime.now():
            raise HTTPException(401, f"用户已锁定，请在{user.locked_until}后重试")
        else:
            # 解锁
            user.status = 'active'
            user.login_attempts = 0
    
    # 验证密码
    if not verify_password(password, user.password_hash):
        user.login_attempts += 1
        if user.login_attempts >= 5:
            user.status = 'locked'
            user.locked_until = datetime.now() + timedelta(hours=1)
        await session.commit()
        raise HTTPException(401, "密码错误")
    
    # 登录成功
    user.login_attempts = 0
    user.last_login_at = datetime.now()
    await session.commit()
    return user
```

---

## 📊 表结构对比

### 改进前
```
users (8 fields)
├── user_id
├── username
├── password_hash
├── user_type
├── enterprise_staff_id
├── contractor_staff_id
├── created_at
└── updated_at
```

### 改进后
```
users (15 fields)
├── user_id
├── username
├── password_hash
├── user_type
├── status ⭐ 新增
├── is_deleted ⭐ 新增
├── enterprise_user_id
├── contractor_user_id
├── created_at
├── created_by ⭐ 新增
├── updated_at
├── updated_by ⭐ 新增
├── deleted_at ⭐ 新增
├── deleted_by ⭐ 新增
├── last_login_at ⭐ 新增
├── login_attempts ⭐ 新增
└── locked_until ⭐ 新增
```

---

## 🆕 新增表

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

## 🔄 数据迁移要点

### 1. 用户数据迁移
```sql
-- 更新用户状态
UPDATE users SET status = 'active' WHERE status IS NULL;

-- 初始化软删除标记
UPDATE users SET is_deleted = FALSE WHERE is_deleted IS NULL;
```

### 2. 角色数据迁移
```sql
-- 企业用户角色迁移
UPDATE enterprise_user eu
JOIN roles r ON r.role_code = CONCAT('enterprise_', eu.role_type)
SET eu.role_id = r.role_id;

-- 承包商用户角色迁移
UPDATE contractor_user cu
JOIN roles r ON r.role_code = CONCAT('contractor_', cu.role_type)
SET cu.role_id = r.role_id;
```

### 3. 工单数据迁移
```sql
-- 生成工单编号
UPDATE ticket 
SET ticket_no = CONCAT('TK', DATE_FORMAT(created_at, '%Y%m%d'), LPAD(ticket_id, 6, '0'));

-- 设置默认流程
UPDATE ticket 
SET workflow_id = (SELECT workflow_id FROM workflow_definitions WHERE workflow_code = 'default_ticket_workflow'),
    status = 'in_progress';
```

---

## ⚡ 性能优化建议

### 1. 索引优化
```sql
-- 高频查询索引
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_type_status ON users(user_type, status, is_deleted);
CREATE INDEX idx_ticket_company_status ON ticket(company_id, status, is_deleted);
CREATE INDEX idx_ticket_no ON ticket(ticket_no);

-- 外键索引
CREATE INDEX idx_enterprise_user_company ON enterprise_user(company_id);
CREATE INDEX idx_enterprise_user_role ON enterprise_user(role_id);
```

### 2. 分区策略
```sql
-- 日志表按月分区
ALTER TABLE user_change_logs PARTITION BY RANGE (TO_DAYS(operation_time));
ALTER TABLE ticket_flow_logs PARTITION BY RANGE (TO_DAYS(operation_time));

-- 工单表按年分区
ALTER TABLE ticket PARTITION BY RANGE (YEAR(apply_date));
```

### 3. 归档策略
- 用户变更日志：保留12个月
- 工单流转日志：保留24个月
- 已完成工单：保留36个月
- 已删除数据：保留6个月

---

## 🎯 实施建议

### 实施顺序
1. **第一阶段（1-2周）**：基础表改造
   - 添加软删除字段
   - 创建日志表
   - 创建角色表

2. **第二阶段（2-3周）**：用户系统重构
   - 重构用户表
   - 迁移用户数据
   - 实现日志功能

3. **第三阶段（3-4周）**：工单流程系统
   - 创建流程表
   - 重构工单表
   - 实现流程逻辑

4. **第四阶段（1-2周）**：权限系统完善
   - 实现角色管理
   - 实现权限控制

### 风险控制
- ✅ 每次迁移前完整备份
- ✅ 先在测试环境验证
- ✅ 保留旧表结构（备份表）
- ✅ 准备回滚方案
- ✅ 添加数据一致性监控

---

## 📝 API 变更影响

### 需要修改的接口
1. **用户管理**
   - `GET /user-management/users/` - 适配新字段
   - `GET /user-management/users/{user_id}/` - 返回完整信息
   - `PUT /user-management/users/{user_id}/` - 记录变更日志
   - `DELETE /user-management/users/{user_id}/` - 软删除

2. **角色管理**（新增）
   - `GET /user-management/roles/` - 角色列表
   - `POST /user-management/roles/` - 创建角色
   - `PUT /user-management/roles/{role_id}/` - 更新角色
   - `GET /user-management/roles/{role_id}/permissions/` - 角色权限

3. **工单管理**
   - `GET /tickets/` - 返回工单状态和流程信息
   - `GET /tickets/{ticket_id}/` - 返回流程步骤
   - `POST /tickets/{ticket_id}/flow/` - 工单流转（新增）
   - `GET /tickets/{ticket_id}/logs/` - 流转日志（新增）

### 兼容性处理
- 保持现有API路径不变
- 响应数据向后兼容
- 新增字段设置默认值
- 提供API版本控制

---

## ✅ 验收标准

### 功能验收
- [ ] 所有用户类型统一管理
- [ ] 软删除功能正常工作
- [ ] 用户变更日志完整记录
- [ ] 角色权限系统正常运行
- [ ] 工单流程流转正常
- [ ] 工单流转日志完整

### 性能验收
- [ ] 用户登录响应时间 < 500ms
- [ ] 工单列表查询 < 1s
- [ ] 工单流转操作 < 2s
- [ ] 数据库CPU使用率 < 70%

### 数据验收
- [ ] 用户数据迁移完整
- [ ] 角色数据迁移正确
- [ ] 工单数据迁移完整
- [ ] 无数据丢失

---

## 📚 相关文档

1. **DATABASE_IMPROVEMENT_PLAN.md** - 详细改进方案
2. **DATABASE_ERD.md** - 数据库ER图
3. **IMPLEMENTATION_CHECKLIST.md** - 实施检查清单

---

## 🤝 支持与反馈

如有任何问题或建议，请：
1. 仔细阅读完整的改进方案文档
2. 在测试环境充分验证
3. 记录遇到的问题和解决方案
4. 及时更新文档

---

**文档版本**：v1.0  
**创建日期**：2025-01-04  
**最后更新**：2025-01-04  
**作者**：AI Assistant

---

## 🎉 总结

本改进方案通过引入**统一用户管理**、**软删除机制**、**操作审计**、**工单流程化**和**细粒度权限控制**，全面提升了系统的可维护性、可追溯性和灵活性。

核心优势：
- ✅ 数据不丢失（软删除）
- ✅ 操作可追溯（审计日志）
- ✅ 流程可配置（工单流程）
- ✅ 权限可定制（角色权限）
- ✅ 管理更简单（统一用户）

建议按照实施检查清单逐步推进，确保每个阶段都经过充分测试和验证。

