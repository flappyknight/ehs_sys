# 路由模块结构说明 (Routes Structure)

## 模块概述

本文档描述了整个项目的路由结构和组织方式。

## 总体架构

```
routes/
├── __init__.py                      # 主路由注册
├── auth.py                          # 认证路由
├── dependencies.py                  # 共享依赖项
├── admin/                           # 系统账户后台模块
│   ├── __init__.py
│   ├── README.md
│   ├── object_plan.md
│   └── interface_list.md
├── enterprise_backend/              # 企业管理后台模块
│   ├── __init__.py
│   ├── README.md
│   ├── object_plan.md
│   ├── interface_list.md
│   ├── user_management/             # 企业用户管理
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── department.py
│   │   ├── area.py
│   │   ├── README.md
│   │   ├── object_plan.md
│   │   └── interface_list.md
│   ├── contractor_management/       # 企业承包商管理
│   │   ├── __init__.py
│   │   ├── contractor.py
│   │   ├── project.py
│   │   ├── README.md
│   │   ├── object_plan.md
│   │   └── interface_list.md
│   ├── ticket_management/           # 企业工单管理
│   │   ├── __init__.py
│   │   ├── ticket.py
│   │   ├── approval.py
│   │   ├── README.md
│   │   ├── object_plan.md
│   │   └── interface_list.md
│   ├── workflow_management/         # 企业作业流程管理
│   │   ├── __init__.py
│   │   ├── plan.py
│   │   ├── participant.py
│   │   ├── README.md
│   │   ├── object_plan.md
│   │   └── interface_list.md
│   └── permission_management/       # 企业权限管理
│       ├── __init__.py
│       ├── role.py
│       ├── permission.py
│       ├── README.md
│       ├── object_plan.md
│       └── interface_list.md
├── contractor_backend/              # 承包商管理后台模块
│   ├── __init__.py
│   ├── README.md
│   ├── object_plan.md
│   ├── interface_list.md
│   ├── staff_management/            # 承包商人员管理
│   │   ├── __init__.py
│   │   ├── staff.py
│   │   ├── README.md
│   │   ├── object_plan.md
│   │   └── interface_list.md
│   ├── ticket_view/                 # 工单浏览
│   │   ├── __init__.py
│   │   ├── ticket.py
│   │   ├── README.md
│   │   ├── object_plan.md
│   │   └── interface_list.md
│   └── cooperation_request/         # 合作申请管理
│       ├── __init__.py
│       ├── request.py
│       ├── README.md
│       ├── object_plan.md
│       └── interface_list.md
├── ticket/                          # 工单模块
│   ├── __init__.py
│   ├── ticket.py
│   ├── README.md
│   ├── CHANGELOG.md
│   ├── object_plan.md
│   └── interface_list.md
└── workflow/                        # 工单流程模块
    ├── __init__.py
    ├── workflow.py
    ├── approval.py
    ├── README.md
    ├── object_plan.md
    └── interface_list.md
```

## 模块说明

### 1. 系统账户后台 (admin/)
**路由前缀**: `/admin`

**功能**: 系统管理员的核心管理功能
- 用户认证和管理
- 企业管理
- 承包商管理
- 系统配置

**权限**: 系统管理员 (UserType.admin)

**文档**: [admin/README.md](./admin/README.md)

---

### 2. 企业管理后台 (enterprise_backend/)
**路由前缀**: `/enterprise-backend`

**功能**: 企业用户的管理平台

#### 2.1 企业用户管理 (user_management/)
**路由前缀**: `/enterprise-backend/user-management`
- 员工管理
- 部门管理
- 厂区管理

#### 2.2 企业承包商管理 (contractor_management/)
**路由前缀**: `/enterprise-backend/contractor-management`
- 承包商列表查看
- 合作项目管理

#### 2.3 企业工单管理 (ticket_management/)
**路由前缀**: `/enterprise-backend/ticket-management`
- 工单创建和管理
- 工单审批

#### 2.4 企业作业流程管理 (workflow_management/)
**路由前缀**: `/enterprise-backend/workflow-management`
- 作业计划查看和审批
- 参与人员管理

#### 2.5 企业权限管理 (permission_management/)
**路由前缀**: `/enterprise-backend/permission-management`
- 角色管理
- 权限分配

**权限**: 企业用户 (UserType.enterprise)

**文档**: [enterprise_backend/README.md](./enterprise_backend/README.md)

---

### 3. 承包商管理后台 (contractor_backend/)
**路由前缀**: `/contractor-backend`

**功能**: 承包商用户的管理平台

#### 3.1 承包商人员管理 (staff_management/)
**路由前缀**: `/contractor-backend/staff-management`
- 员工管理
- 资质管理

#### 3.2 工单浏览 (ticket_view/)
**路由前缀**: `/contractor-backend/ticket-view`
- 工单查看
- 工单执行上报

#### 3.3 合作申请管理 (cooperation_request/)
**路由前缀**: `/contractor-backend/cooperation-request`
- 合作邀请处理
- 合作项目查看

**权限**: 承包商用户 (UserType.contractor)

**文档**: [contractor_backend/README.md](./contractor_backend/README.md)

---

### 4. 工单模块 (ticket/)
**路由前缀**: `/tickets`

**功能**: 作业工单的全生命周期管理
- 工单创建
- 工单查看
- 工单更新
- 工单删除

**权限**: 根据用户类型自动过滤数据

**文档**: [ticket/README.md](./ticket/README.md)

---

### 5. 工单流程模块 (workflow/)
**路由前缀**: `/workflow`

**功能**: 工单流程的审批和管理
- 流程定义
- 流程实例
- 审批处理

**权限**: 根据用户类型和审批角色

**文档**: [workflow/README.md](./workflow/README.md)

---

### 6. 认证模块 (auth.py)
**路由前缀**: 无（直接挂载到根路径）

**功能**: 用户认证相关
- 用户登录 (`POST /token`)
- 获取当前用户 (`GET /users/me`)
- 用户登出 (`POST /logout`)
- 测试接口 (`GET /test`)

**权限**: 部分接口公开，部分需要认证

---

## 路由注册流程

1. 各子模块在自己的 `__init__.py` 中创建 `router`
2. 主路由文件 `routes/__init__.py` 导入各子模块的 `router`
3. 使用 `include_router` 注册到 `main_router`
4. `main.py` 导入并使用 `main_router`

## 数据隔离策略

### 企业用户
- 通过 `enterprise_id` 过滤数据
- 只能访问自己企业的数据
- 在 `dependencies.py` 中自动添加过滤条件

### 承包商用户
- 通过 `contractor_id` 过滤数据
- 只能访问自己承包商的数据
- 只能查看分配给自己员工的工单

### 系统管理员
- 可以访问所有数据
- 无数据隔离限制

## 权限验证

### 认证依赖项
- `get_current_user`: 获取当前登录用户
- `authenticate_enterprise_level`: 验证企业管理员权限
- `authenticate_contractor_level`: 验证承包商管理员权限

### 使用方式
```python
from routes.dependencies import get_current_user, authenticate_enterprise_level

@router.get("/")
async def get_data(user: User = Depends(get_current_user)):
    # 需要认证，但不限制用户类型
    pass

@router.post("/")
async def create_data(user: User = Depends(authenticate_enterprise_level)):
    # 需要企业管理员权限
    pass
```

## 文档规范

每个模块和子模块都包含以下文档：

### README.md
- 模块概述
- 主要功能
- 权限要求
- 相关文档链接

### object_plan.md
- 模块结构
- 核心对象模型
- 业务逻辑设计
- 权限控制
- 数据验证
- 性能优化

### interface_list.md
- 详细的 API 接口文档
- 请求参数
- 响应数据
- 错误响应
- 使用示例

## 开发指南

### 添加新接口
1. 在对应模块的 Python 文件中添加路由函数
2. 更新 `interface_list.md` 文档
3. 如果涉及新的数据模型，更新 `object_plan.md`

### 添加新模块
1. 创建模块目录
2. 创建 `__init__.py` 并定义 `router`
3. 创建三个文档文件：`README.md`, `object_plan.md`, `interface_list.md`
4. 在 `routes/__init__.py` 中注册新模块

### 测试接口
使用 FastAPI 自动生成的文档：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 注意事项

1. **数据隔离**: 所有查询都必须考虑数据隔离，避免跨企业/承包商访问
2. **权限验证**: 敏感操作必须添加权限验证
3. **错误处理**: 使用统一的错误响应格式
4. **文档更新**: 接口变更时及时更新文档
5. **代码规范**: 遵循 Python PEP 8 规范

