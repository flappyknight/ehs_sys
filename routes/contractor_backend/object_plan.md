# 承包商管理后台模块 - 对象设计方案

## 1. 模块架构

```
contractor_backend/
├── __init__.py                      # 路由注册
├── README.md                        # 模块说明
├── object_plan.md                   # 本文件
├── interface_list.md                # 接口文档
├── staff_management/                # 承包商人员管理
│   ├── __init__.py
│   ├── staff.py                     # 人员管理接口
│   ├── README.md
│   ├── object_plan.md
│   └── interface_list.md
├── ticket_view/                     # 工单浏览
│   ├── __init__.py
│   ├── ticket.py                    # 工单查看接口
│   ├── README.md
│   ├── object_plan.md
│   └── interface_list.md
└── cooperation_request/             # 合作申请管理
    ├── __init__.py
    ├── request.py                   # 合作申请接口
    ├── README.md
    ├── object_plan.md
    └── interface_list.md
```

## 2. 核心设计原则

### 2.1 数据隔离
- 承包商用户只能访问自己公司的数据
- 通过 `contractor_id` 进行数据过滤
- 只能查看相关项目的工单

### 2.2 权限分级
```
承包商管理员 (approver)
  └─ 可以管理所有承包商数据
作业人员 (worker)
  └─ 可以查看和执行工单
```

### 2.3 模块化设计
- 每个子模块独立管理
- 清晰的接口边界
- 便于维护和扩展

## 3. 数据模型设计

### 3.1 承包商用户相关

#### ContractorUser
```python
class ContractorUser(BaseModel):
    user_id: int
    contractor_id: int
    name: str
    phone: str
    id_number: str
    work_type: str
    personal_photo: Optional[str]
    role_type: str  # approver, worker
    status: bool
```

### 3.2 工单查看相关

#### ContractorTicketListItem
```python
class ContractorTicketListItem(BaseModel):
    ticket_id: int
    apply_date: date
    enterprise_name: str
    area_name: str
    working_content: str
    pre_st: str
    pre_et: str
    worker_name: str
    status: str
```

### 3.3 合作申请相关

#### CooperationRequest
```python
class CooperationRequest(BaseModel):
    request_id: int
    enterprise_id: int
    enterprise_name: str
    project_name: str
    project_content: str
    start_date: date
    status: str  # pending, accepted, rejected
    created_at: datetime
```

## 4. 权限验证流程

### 4.1 认证流程
1. 从 Token 中解析用户信息
2. 验证用户类型为 contractor
3. 获取用户的 contractor_id
4. 验证用户状态是否有效

### 4.2 授权流程
1. 检查用户角色类型
2. 验证是否有操作权限
3. 检查数据归属（contractor_id）
4. 执行业务逻辑

## 5. 数据库设计

### 5.1 涉及的表
- `contractor_user` - 承包商用户表
- `contractor` - 承包商表
- `project` - 项目表
- `ticket` - 工单表
- `plan` - 计划表

### 5.2 关键关系
- 承包商用户 → 承包商 (多对一)
- 项目 → 承包商 (多对一)
- 项目 → 企业 (多对一)
- 工单 → 项目 (通过作业人员关联)
- 计划 → 项目 (多对一)

## 6. 安全设计

### 6.1 数据隔离
- 所有查询自动添加 contractor_id 过滤
- 跨承包商访问直接拒绝
- 只能查看相关项目的工单

### 6.2 操作审计
- 记录所有管理操作
- 包含操作人、时间、内容
- 支持审计日志查询

## 7. 性能优化

### 7.1 查询优化
- 使用索引优化常用查询
- 分页查询大数据集
- 缓存常用数据

## 8. 错误处理

### 8.1 错误码设计
- 400: 请求参数错误
- 401: 未认证
- 403: 权限不足或跨承包商访问
- 404: 资源不存在
- 500: 服务器内部错误

