# 企业管理后台模块 - 对象设计方案

## 1. 模块架构

```
enterprise_backend/
├── __init__.py                      # 路由注册
├── README.md                        # 模块说明
├── object_plan.md                   # 本文件
├── interface_list.md                # 接口文档
├── user_management/                 # 企业用户管理
│   ├── __init__.py
│   ├── user.py                      # 用户管理接口
│   ├── department.py                # 部门管理接口
│   ├── area.py                      # 厂区管理接口
│   ├── README.md
│   ├── object_plan.md
│   └── interface_list.md
├── contractor_management/           # 企业承包商管理
│   ├── __init__.py
│   ├── contractor.py                # 承包商管理接口
│   ├── project.py                   # 项目管理接口
│   ├── README.md
│   ├── object_plan.md
│   └── interface_list.md
├── ticket_management/               # 企业工单管理
│   ├── __init__.py
│   ├── ticket.py                    # 工单管理接口
│   ├── approval.py                  # 工单审批接口
│   ├── README.md
│   ├── object_plan.md
│   └── interface_list.md
├── workflow_management/             # 企业作业流程管理
│   ├── __init__.py
│   ├── plan.py                      # 计划管理接口
│   ├── participant.py               # 参与人员管理接口
│   ├── README.md
│   ├── object_plan.md
│   └── interface_list.md
└── permission_management/           # 企业权限管理
    ├── __init__.py
    ├── role.py                      # 角色管理接口
    ├── permission.py                # 权限管理接口
    ├── README.md
    ├── object_plan.md
    └── interface_list.md
```

## 2. 核心设计原则

### 2.1 数据隔离
- 企业用户只能访问自己企业的数据
- 通过 `enterprise_id` 进行数据过滤
- 所有查询都自动添加企业过滤条件

### 2.2 权限分级
```
企业管理员 (manager)
  └─ 可以管理所有企业数据
现场人员 (site_staff)
  └─ 可以查看和操作工单、计划
普通员工 (staff)
  └─ 只能查看自己相关的数据
```

### 2.3 模块化设计
- 每个子模块独立管理
- 清晰的接口边界
- 便于维护和扩展

## 3. 数据模型设计

### 3.1 企业用户相关

#### EnterpriseUser
```python
class EnterpriseUser(BaseModel):
    user_id: int
    enterprise_id: int
    department_id: Optional[int]
    name: str
    phone: str
    email: Optional[str]
    position: Optional[str]
    role_type: str  # manager, site_staff, staff
    approval_level: Optional[int]
    status: bool
```

#### Department
```python
class Department(BaseModel):
    dept_id: int
    company_id: int
    name: str
    parent_id: Optional[int]
```

#### Area
```python
class Area(BaseModel):
    area_id: int
    area_name: str
    enterprise_id: int
    dept_id: Optional[int]
```

### 3.2 承包商管理相关

#### ContractorListItem
```python
class ContractorListItem(BaseModel):
    contractor_id: int
    company_name: str
    company_type: str
    legal_person: str
    establish_date: str
    project_count: int
```

#### ContractorProject
```python
class ContractorProject(BaseModel):
    project_id: int
    project_name: str
    contractor_id: int
    enterprise_id: int
    start_date: date
    end_date: Optional[date]
    status: str
```

### 3.3 工单管理相关

#### Ticket
```python
class Ticket(BaseModel):
    ticket_id: int
    apply_date: date
    applicant: int
    area_id: int
    working_content: str
    pre_st: datetime
    pre_et: datetime
    tools: Optional[str]
    worker: int
    custodians: int
    danger: Optional[str]
    protection: Optional[str]
    hot_work: int
    work_height_level: int
    status: str  # pending, approved, rejected, completed
```

### 3.4 作业流程相关

#### Plan
```python
class Plan(BaseModel):
    plan_id: int
    project_id: int
    plan_name: str
    plan_date: date
    plan_content: str
    status: str  # draft, pending, approved, rejected
```

#### PlanParticipant
```python
class PlanParticipant(BaseModel):
    user_id: int
    name: str
    phone: str
    id_number: str
    is_registered: bool
```

### 3.5 权限管理相关

#### Role
```python
class Role(BaseModel):
    role_id: int
    role_name: str
    role_type: str
    permissions: List[str]
    enterprise_id: int
```

#### Permission
```python
class Permission(BaseModel):
    permission_id: int
    permission_name: str
    permission_code: str
    module: str
```

## 4. 权限验证流程

### 4.1 认证流程
1. 从 Token 中解析用户信息
2. 验证用户类型为 enterprise
3. 获取用户的 enterprise_id
4. 验证用户状态是否有效

### 4.2 授权流程
1. 检查用户角色类型
2. 验证是否有操作权限
3. 检查数据归属（enterprise_id）
4. 执行业务逻辑

### 4.3 权限级别映射
```python
PermissionLevel = {
    "manager": 3,      # 企业管理员
    "site_staff": 2,   # 现场人员
    "staff": 1         # 普通员工
}
```

## 5. 数据库设计

### 5.1 涉及的表
- `enterprise_user` - 企业用户表
- `department` - 部门表
- `area` - 厂区表
- `company` - 企业表
- `contractor` - 承包商表
- `project` - 项目表
- `ticket` - 工单表
- `plan` - 计划表
- `role` - 角色表
- `permission` - 权限表

### 5.2 关键关系
- 企业用户 → 企业 (多对一)
- 企业用户 → 部门 (多对一)
- 厂区 → 企业 (多对一)
- 厂区 → 部门 (多对一)
- 项目 → 企业 (多对一)
- 项目 → 承包商 (多对一)
- 工单 → 厂区 (多对一)
- 计划 → 项目 (多对一)

## 6. 安全设计

### 6.1 数据隔离
- 所有查询自动添加 enterprise_id 过滤
- 跨企业访问直接拒绝
- 敏感数据加密存储

### 6.2 操作审计
- 记录所有管理操作
- 包含操作人、时间、内容
- 支持审计日志查询

### 6.3 权限控制
- 基于角色的访问控制 (RBAC)
- 细粒度权限管理
- 动态权限验证

## 7. 性能优化

### 7.1 查询优化
- 使用索引优化常用查询
- 分页查询大数据集
- 缓存常用数据

### 7.2 并发控制
- 使用数据库事务
- 乐观锁处理并发更新
- 防止重复提交

## 8. 错误处理

### 8.1 错误码设计
- 400: 请求参数错误
- 401: 未认证
- 403: 权限不足或跨企业访问
- 404: 资源不存在
- 409: 数据冲突
- 500: 服务器内部错误

### 8.2 错误响应格式
```python
{
    "detail": "错误描述信息"
}
```

## 9. 扩展性设计

### 9.1 模块化
- 每个子模块独立
- 清晰的接口定义
- 便于单元测试

### 9.2 可配置性
- 权限可动态配置
- 审批流程可定制
- 支持多租户扩展

## 10. 监控与日志

### 10.1 操作日志
- 记录所有管理操作
- 包含操作人、时间、内容
- 支持日志查询和审计

### 10.2 监控指标
- API 调用频率
- 响应时间
- 错误率统计
- 用户活跃度

