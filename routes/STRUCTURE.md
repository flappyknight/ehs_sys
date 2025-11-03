# 路由结构图 (Router Structure Diagram)

## 完整路由树 (Complete Route Tree)

```
FastAPI Application
│
├── 认证路由 (Authentication) - 无前缀
│   ├── POST   /token                          # 用户登录
│   ├── GET    /users/me/                      # 获取当前用户信息
│   ├── POST   /logout                         # 用户登出
│   └── GET    /test/                          # 测试接口
│
├── /enterprise (企业后台管理)
│   │
│   ├── 企业信息管理
│   │   ├── POST   /enterprise/add/            # 添加企业
│   │   ├── POST   /enterprise/add_user/       # 添加企业用户
│   │   └── GET    /enterprise/list/           # 获取企业列表
│   │
│   ├── /departments (部门管理)
│   │   ├── POST   /enterprise/departments/add/              # 添加部门
│   │   ├── GET    /enterprise/departments/                  # 获取部门列表
│   │   └── GET    /enterprise/departments/with-members/     # 获取部门及成员数量
│   │
│   ├── /areas (厂区管理)
│   │   ├── POST   /enterprise/areas/                        # 创建厂区
│   │   ├── GET    /enterprise/areas/                        # 获取厂区列表
│   │   ├── GET    /enterprise/areas/{area_id}/              # 获取厂区详情
│   │   ├── PUT    /enterprise/areas/{area_id}/              # 更新厂区信息
│   │   ├── DELETE /enterprise/areas/{area_id}/              # 删除厂区
│   │   └── GET    /enterprise/areas/by-department/{dept_id}/ # 获取部门厂区
│   │
│   ├── /staff (人员管理)
│   │   ├── GET    /enterprise/staff/departments/{dept_id}/members/        # 获取部门成员
│   │   ├── GET    /enterprise/staff/enterprise/{enterprise_id}/members/   # 获取企业成员
│   │   ├── GET    /enterprise/staff/users/{user_id}/                      # 获取用户详情
│   │   └── PUT    /enterprise/staff/users/{user_id}/                      # 更新用户信息
│   │
│   └── /projects (项目管理)
│       ├── GET    /enterprise/projects/                     # 获取项目列表
│       └── GET    /enterprise/projects/{project_id}/        # 获取项目详情
│
├── /contractor (供应商后台管理)
│   │
│   ├── 供应商信息管理
│   │   ├── POST   /contractor/add/                          # 添加供应商
│   │   ├── POST   /contractor/add_user/                     # 添加供应商用户
│   │   ├── GET    /contractor/list/                         # 获取承包商列表
│   │   └── POST   /contractor/create-project/               # 创建合作项目
│   │
│   ├── /projects (供应商项目管理)
│   │   └── POST   /contractor/projects/add/                 # 添加项目
│   │
│   └── /plans (计划管理)
│       ├── POST   /contractor/plans/add/                    # 添加计划
│       └── GET    /contractor/plans/{plan_id}/participants/ # 获取计划参与人员
│
└── /tickets (工单后台管理)
    ├── POST   /tickets/                                     # 创建工单
    ├── GET    /tickets/                                     # 获取工单列表
    ├── GET    /tickets/{ticket_id}/                         # 获取工单详情
    ├── PUT    /tickets/{ticket_id}/                         # 更新工单
    └── DELETE /tickets/{ticket_id}/                         # 删除工单
```

## 模块文件映射 (Module File Mapping)

```
routes/
│
├── __init__.py                    → 主路由注册中心
├── dependencies.py                → 共享依赖（认证、权限）
├── auth.py                        → 认证路由
├── README.md                      → 详细文档
├── STRUCTURE.md                   → 本结构图
│
├── enterprise/                    → 企业管理模块
│   ├── __init__.py               → 企业路由注册
│   ├── enterprise.py             → 企业信息管理 (3 endpoints)
│   ├── department.py             → 部门管理 (3 endpoints)
│   ├── area.py                   → 厂区管理 (6 endpoints)
│   ├── staff.py                  → 人员管理 (4 endpoints)
│   └── project.py                → 项目管理 (2 endpoints)
│
├── contractor/                    → 供应商管理模块
│   ├── __init__.py               → 供应商路由注册
│   ├── contractor.py             → 供应商信息管理 (4 endpoints)
│   ├── project.py                → 供应商项目管理 (1 endpoint)
│   └── plan.py                   → 计划管理 (2 endpoints)
│
└── ticket/                        → 工单管理模块
    ├── __init__.py               → 工单路由注册
    └── ticket.py                 → 工单管理 (5 endpoints)
```

## 权限层级 (Permission Hierarchy)

```
权限级别从高到低:

1. Admin (管理员)
   └── 可以访问所有接口

2. Enterprise Manager (企业管理员)
   ├── 可以管理企业信息
   ├── 可以管理部门
   ├── 可以管理厂区
   ├── 可以管理人员
   └── 可以管理项目

3. Enterprise Site Staff (企业现场人员)
   ├── 可以查看项目
   └── 有限的操作权限

4. Contractor Approver (供应商审批员)
   ├── 可以管理供应商用户
   ├── 可以管理计划
   └── 可以查看项目

5. Contractor Normal (供应商普通用户)
   └── 基本查看权限
```

## 依赖关系图 (Dependency Graph)

```
main.py
  │
  ├── routes/__init__.py (main_router)
  │     │
  │     ├── enterprise/__init__.py (enterprise_router)
  │     │     │
  │     │     ├── enterprise.py
  │     │     ├── department.py
  │     │     ├── area.py
  │     │     ├── staff.py
  │     │     └── project.py
  │     │
  │     └── contractor/__init__.py (contractor_router)
  │           │
  │           ├── contractor.py
  │           ├── project.py
  │           └── plan.py
  │
  ├── auth.py (auth_router)
  │
  └── dependencies.py
        │
        ├── get_current_user
        ├── authenticate_enterprise_level
        ├── authenticate_contractor_level
        └── get_user_enterprise_id
```

## 数据流示意 (Data Flow)

```
客户端请求 (Client Request)
    ↓
FastAPI 应用 (FastAPI App)
    ↓
路由匹配 (Route Matching)
    ↓
依赖注入 (Dependency Injection)
    ├── OAuth2 Token 验证
    ├── 用户身份验证
    └── 权限级别检查
    ↓
路由处理函数 (Route Handler)
    ↓
数据库操作 (Database Operations via CRUD)
    ↓
响应返回 (Response)
```

## 接口统计 (Endpoint Statistics)

| 模块 | 子模块 | 接口数量 |
|------|--------|----------|
| 认证 | - | 4 |
| 企业管理 | 企业信息 | 3 |
| 企业管理 | 部门管理 | 3 |
| 企业管理 | 厂区管理 | 6 |
| 企业管理 | 人员管理 | 4 |
| 企业管理 | 项目管理 | 2 |
| 供应商管理 | 供应商信息 | 4 |
| 供应商管理 | 项目管理 | 1 |
| 供应商管理 | 计划管理 | 2 |
| 工单管理 | 工单管理 | 5 |
| **总计** | - | **34** |

## 标签分类 (Tag Classification)

FastAPI 自动文档中的标签分类：

- 🔐 **认证** (Authentication)
- 🏢 **企业后台管理** (Enterprise Management)
  - 企业信息管理
  - 部门管理
  - 厂区管理
  - 人员管理
  - 项目管理
- 🏗️ **供应商后台管理** (Contractor Management)
  - 供应商信息管理
  - 供应商项目管理
  - 计划管理
- 📋 **工单后台管理** (Ticket Management)
  - 工单管理

