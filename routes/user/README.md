# 用户管理模块说明 (User Management Module)

## 概述

用户管理模块提供了完整的用户和角色管理功能，包括用户的增删改查、密码管理、角色分配和权限控制。支持企业用户和承包商用户两种类型。

## 模块结构

```
routes/user/
├── __init__.py          # 用户管理路由注册
├── user.py              # 用户管理路由（7个接口）
├── role.py              # 角色管理路由（6个接口）
└── README.md            # 本文档
```

## 用户类型

### 1. 企业用户 (Enterprise User)
- 属于某个企业
- 可以分配到部门
- 拥有职位、邮箱等信息
- 支持审批级别设置

### 2. 承包商用户 (Contractor User)
- 属于某个承包商公司
- 需要身份证号和工种信息
- 可以上传个人照片
- 主要用于现场作业

### 3. 管理员用户 (Admin User)
- 系统最高权限
- 可以管理所有企业和承包商
- 不属于任何企业或承包商

## 角色系统

### 企业角色

| 角色类型 | 角色名称 | 权限级别 | 说明 |
|---------|---------|---------|------|
| `manager` | 管理员 | 3 | 拥有所有权限，可以管理企业内所有资源 |
| `site_staff` | 现场人员 | 1 | 现场作业人员，可以查看和操作工单 |
| `normal` | 普通员工 | 1 | 普通员工，只能查看基本信息 |

### 承包商角色

| 角色类型 | 角色名称 | 权限级别 | 说明 |
|---------|---------|---------|------|
| `approver` | 审批员 | 2 | 承包商审批员，可以管理承包商用户和计划 |
| `normal` | 普通员工 | 1 | 承包商普通员工，只能查看基本信息 |

## API 接口

### 用户管理接口

#### 1. 创建用户
```
POST /api/users/
```

**权限要求**: 企业管理员及以上

**请求体**: UserCreate
```json
{
    "username": "zhangsan",
    "password": "password123",
    "user_type": "enterprise",
    "enterprise_id": 1,
    "name": "张三",
    "phone": "13800138000",
    "email": "zhangsan@example.com",
    "position": "工程师",
    "role_type": "normal",
    "department_id": 1
}
```

**企业用户必填字段**:
- `username`, `password`, `user_type`, `enterprise_id`, `name`, `phone`

**承包商用户必填字段**:
- `username`, `password`, `user_type`, `contractor_id`, `name`, `phone`, `id_number`, `work_type`

**响应**:
```json
{
    "message": "用户创建成功",
    "user_id": 1
}
```

#### 2. 获取用户列表
```
GET /api/users/
```

**权限要求**: 登录用户

**查询参数**:
- `user_type` (可选): 按用户类型筛选 (enterprise/contractor)
- `status` (可选): 按状态筛选 (true/false)
- `keyword` (可选): 搜索关键词（姓名、手机号）

**数据隔离**: 企业用户只能看到自己企业的用户

**响应**: UserListItem[]
```json
[
    {
        "user_id": 1,
        "username": "zhangsan",
        "user_type": "enterprise",
        "name": "张三",
        "phone": "13800138000",
        "email": "zhangsan@example.com",
        "role_type": "normal",
        "status": true,
        "company_name": "XX科技有限公司",
        "department_name": "技术部",
        "created_at": "2025-11-03T08:00:00"
    }
]
```

#### 3. 获取用户详情
```
GET /api/users/{user_id}/
```

**权限要求**: 登录用户

**响应**: UserDetail
```json
{
    "user_id": 1,
    "username": "zhangsan",
    "user_type": "enterprise",
    "name": "张三",
    "phone": "13800138000",
    "email": "zhangsan@example.com",
    "position": "工程师",
    "role_type": "normal",
    "status": true,
    "company_id": 1,
    "company_name": "XX科技有限公司",
    "department_id": 1,
    "department_name": "技术部",
    "approval_level": 1,
    "created_at": "2025-11-03T08:00:00",
    "updated_at": "2025-11-03T08:00:00"
}
```

#### 4. 更新用户信息
```
PUT /api/users/{user_id}/
```

**权限要求**: 企业管理员及以上

**请求体**: UserUpdate（只需提供要更新的字段）
```json
{
    "name": "张三三",
    "position": "高级工程师",
    "role_type": "site_staff"
}
```

**响应**:
```json
{
    "message": "用户信息更新成功"
}
```

#### 5. 删除用户（软删除）
```
DELETE /api/users/{user_id}/
```

**权限要求**: 企业管理员及以上

**说明**: 软删除，将用户状态设置为 false，不会真正删除数据

**响应**:
```json
{
    "message": "用户已禁用"
}
```

#### 6. 修改密码（用户自己）
```
POST /api/users/{user_id}/change-password/
```

**权限要求**: 用户本人或管理员

**请求体**: PasswordChange
```json
{
    "old_password": "oldpassword123",
    "new_password": "newpassword123"
}
```

**响应**:
```json
{
    "message": "密码修改成功"
}
```

#### 7. 重置密码（管理员操作）
```
POST /api/users/{user_id}/reset-password/
```

**权限要求**: 企业管理员及以上

**请求体**: PasswordReset
```json
{
    "new_password": "newpassword123"
}
```

**响应**:
```json
{
    "message": "密码重置成功"
}
```

### 角色管理接口

#### 1. 获取角色列表
```
GET /api/users/roles/
```

**权限要求**: 登录用户

**查询参数**:
- `user_type` (可选): 按用户类型筛选

**响应**: RoleListItem[]
```json
[
    {
        "role_type": "manager",
        "role_name": "管理员",
        "description": "拥有所有权限，可以管理企业内所有资源",
        "permission_level": 3,
        "user_count": 5
    }
]
```

#### 2. 获取角色详情
```
GET /api/users/roles/{role_type}/
```

**权限要求**: 登录用户

**响应**: RoleInfo
```json
{
    "role_type": "manager",
    "role_name": "管理员",
    "description": "拥有所有权限，可以管理企业内所有资源",
    "permission_level": 3,
    "user_type": "enterprise"
}
```

#### 3. 获取角色权限
```
GET /api/users/roles/{role_type}/permissions/
```

**权限要求**: 登录用户

**响应**: RolePermission
```json
{
    "role_type": "manager",
    "permissions": [
        "user.create",
        "user.read",
        "user.update",
        "user.delete",
        "department.create",
        "department.read",
        "department.update",
        "department.delete",
        "area.create",
        "area.read",
        "area.update",
        "area.delete",
        "ticket.create",
        "ticket.read",
        "ticket.update",
        "ticket.delete",
        "project.read",
        "project.update",
        "contractor.read"
    ]
}
```

#### 4. 更新用户角色
```
PUT /api/users/roles/{user_id}/role/
```

**权限要求**: 企业管理员及以上

**请求体**: UserRoleUpdate
```json
{
    "role_type": "manager"
}
```

**响应**:
```json
{
    "message": "用户角色更新成功"
}
```

#### 5. 获取企业可用角色
```
GET /api/users/roles/enterprise/available/
```

**权限要求**: 登录用户

**响应**: RoleInfo[]

#### 6. 获取承包商可用角色
```
GET /api/users/roles/contractor/available/
```

**权限要求**: 管理员

**响应**: RoleInfo[]

## 权限说明

### 权限级别
- **Level 3 (Manager)**: 管理员，拥有所有权限
- **Level 2 (Approver)**: 审批员，可以审批和管理
- **Level 1 (Site Staff/Normal)**: 现场人员/普通员工，基本权限

### 权限矩阵

| 操作 | 管理员 | 审批员 | 现场人员 | 普通员工 |
|------|--------|--------|---------|---------|
| 创建用户 | ✅ | ✅ | ❌ | ❌ |
| 查看用户 | ✅ | ✅ | ✅ | ✅ |
| 更新用户 | ✅ | ✅ | ❌ | ❌ |
| 删除用户 | ✅ | ✅ | ❌ | ❌ |
| 创建工单 | ✅ | ❌ | ✅ | ❌ |
| 审批工单 | ✅ | ✅ | ❌ | ❌ |
| 管理部门 | ✅ | ❌ | ❌ | ❌ |
| 管理厂区 | ✅ | ❌ | ❌ | ❌ |

## 数据隔离

### 企业级隔离
- 企业用户只能看到和管理自己企业的用户
- 通过 `company_id` 进行数据隔离
- 管理员可以跨企业查看和管理

### 承包商隔离
- 承包商用户信息只有管理员可以查看
- 企业用户无法直接管理承包商用户

## 使用场景

### 场景1: 创建企业用户
```bash
curl -X POST "http://localhost:8000/api/users/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "zhangsan",
    "password": "password123",
    "user_type": "enterprise",
    "enterprise_id": 1,
    "name": "张三",
    "phone": "13800138000",
    "email": "zhangsan@example.com",
    "position": "工程师",
    "role_type": "normal",
    "department_id": 1
  }'
```

### 场景2: 创建承包商用户
```bash
curl -X POST "http://localhost:8000/api/users/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "lisi",
    "password": "password123",
    "user_type": "contractor",
    "contractor_id": 1,
    "name": "李四",
    "phone": "13900139000",
    "id_number": "110101199001011234",
    "work_type": "电工",
    "role_type": "normal"
  }'
```

### 场景3: 查询企业用户列表
```bash
curl -X GET "http://localhost:8000/api/users/?user_type=enterprise&status=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 场景4: 搜索用户
```bash
curl -X GET "http://localhost:8000/api/users/?keyword=张三" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 场景5: 更新用户角色
```bash
curl -X PUT "http://localhost:8000/api/users/roles/1/role/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role_type": "manager"
  }'
```

### 场景6: 修改密码
```bash
curl -X POST "http://localhost:8000/api/users/1/change-password/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "oldpassword123",
    "new_password": "newpassword123"
  }'
```

## 注意事项

1. **用户名唯一性**: 用户名在整个系统中必须唯一
2. **密码安全**: 密码使用bcrypt加密存储
3. **软删除**: 删除用户只是将状态设置为false，不会真正删除数据
4. **角色固定**: 角色是预定义的，不支持动态创建角色
5. **权限检查**: 所有操作都会进行严格的权限验证

## 错误处理

| 错误码 | 错误信息 | 解决方案 |
|--------|----------|----------|
| 400 | 用户名已存在 | 使用不同的用户名 |
| 400 | 企业用户必须指定企业ID | 提供 enterprise_id |
| 400 | 承包商用户必须指定承包商ID | 提供 contractor_id |
| 400 | 无效的角色类型 | 使用预定义的角色类型 |
| 401 | 权限不足 | 确保有足够的权限 |
| 403 | 无权访问该用户信息 | 只能访问自己企业的用户 |
| 404 | 用户不存在 | 检查用户ID是否正确 |

## 扩展功能建议

1. **用户导入导出**: 批量导入和导出用户
2. **用户组管理**: 支持用户组功能
3. **自定义角色**: 支持动态创建和配置角色
4. **权限细粒度控制**: 更细粒度的权限控制
5. **用户活动日志**: 记录用户的所有操作
6. **密码策略**: 密码强度要求、定期修改等
7. **多因素认证**: 支持短信验证码、邮箱验证等
8. **用户标签**: 为用户添加自定义标签

---

**创建时间**: 2025-11-03  
**版本**: v1.0  
**维护者**: Development Team

