# 企业权限管理模块 - 对象设计方案

## 1. 模块结构

```
permission_management/
├── __init__.py          # 路由注册
├── role.py              # 角色管理接口
├── permission.py        # 权限管理接口
├── README.md
├── object_plan.md       # 本文件
└── interface_list.md
```

## 2. 核心对象模型

### 2.1 角色管理

#### RoleCreate
```python
class RoleCreate(BaseModel):
    role_name: str
    role_type: str  # custom, system
    description: Optional[str]
    permissions: List[str]  # 权限代码列表
```

#### RoleListItem
```python
class RoleListItem(BaseModel):
    role_id: int
    role_name: str
    role_type: str
    user_count: int  # 使用该角色的用户数
    created_at: datetime
```

### 2.2 权限管理

#### Permission
```python
class Permission(BaseModel):
    permission_id: int
    permission_name: str
    permission_code: str
    module: str
    description: Optional[str]
```

## 3. 预定义角色

- **manager**: 企业管理员，拥有所有权限
- **site_staff**: 现场人员，可以管理工单和计划
- **staff**: 普通员工，只能查看相关信息

## 4. 权限代码设计

```
user:view      - 查看用户
user:create    - 创建用户
user:edit      - 编辑用户
user:delete    - 删除用户
ticket:view    - 查看工单
ticket:create  - 创建工单
ticket:approve - 审批工单
plan:view      - 查看计划
plan:approve   - 审批计划
...
```

## 5. 权限验证流程

1. 从 Token 获取用户信息
2. 获取用户角色
3. 获取角色权限列表
4. 验证是否有操作权限
5. 执行业务逻辑

