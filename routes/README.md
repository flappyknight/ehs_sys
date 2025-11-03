# 路由结构说明 (Router Structure Documentation)

## 概述 (Overview)

本项目采用模块化的路由结构设计，将所有API接口按照功能模块进行分类管理，提高代码的可维护性和可扩展性。

## 目录结构 (Directory Structure)

```
routes/
├── __init__.py                 # 主路由入口，注册所有子路由
├── dependencies.py             # 共享依赖项（认证、权限验证等）
├── auth.py                     # 认证相关路由（登录、登出、获取用户信息）
├── README.md                   # 本文档
├── enterprise/                 # 企业后台管理模块
│   ├── __init__.py            # 企业模块路由入口
│   ├── enterprise.py          # 企业信息管理
│   ├── department.py          # 部门管理
│   ├── area.py                # 厂区管理
│   ├── staff.py               # 人员管理
│   └── project.py             # 项目管理
├── contractor/                 # 供应商后台管理模块
│   ├── __init__.py            # 供应商模块路由入口
│   ├── contractor.py          # 供应商信息管理
│   ├── project.py             # 供应商项目管理
│   └── plan.py                # 计划管理
├── ticket/                     # 工单后台管理模块
│   ├── __init__.py            # 工单模块路由入口
│   └── ticket.py              # 工单管理（增删改查）
└── user/                       # 用户后台管理模块
    ├── __init__.py            # 用户模块路由入口
    ├── user.py                # 用户管理（增删改查）
    └── role.py                # 角色管理
```

## 路由层级 (Route Hierarchy)

### 1. 认证路由 (Authentication Routes)
**基础路径**: `/`

| 端点 | 方法 | 说明 |
|------|------|------|
| `/token` | POST | 用户登录获取访问令牌 |
| `/users/me/` | GET | 获取当前登录用户信息 |
| `/logout` | POST | 用户登出 |
| `/test/` | GET | 测试接口 |

### 2. 企业后台管理 (Enterprise Management)
**基础路径**: `/enterprise`

#### 2.1 企业信息管理
| 端点 | 方法 | 说明 |
|------|------|------|
| `/enterprise/add/` | POST | 添加企业 |
| `/enterprise/add_user/` | POST | 添加企业用户 |
| `/enterprise/list/` | GET | 获取企业列表 |

#### 2.2 部门管理
**基础路径**: `/enterprise/departments`

| 端点 | 方法 | 说明 |
|------|------|------|
| `/enterprise/departments/add/` | POST | 添加部门 |
| `/enterprise/departments/` | GET | 获取部门列表 |
| `/enterprise/departments/with-members/` | GET | 获取部门列表及成员数量 |

#### 2.3 厂区管理
**基础路径**: `/enterprise/areas`

| 端点 | 方法 | 说明 |
|------|------|------|
| `/enterprise/areas/` | POST | 创建厂区 |
| `/enterprise/areas/` | GET | 获取厂区列表 |
| `/enterprise/areas/{area_id}/` | GET | 获取厂区详情 |
| `/enterprise/areas/{area_id}/` | PUT | 更新厂区信息 |
| `/enterprise/areas/{area_id}/` | DELETE | 删除厂区 |
| `/enterprise/areas/by-department/{dept_id}/` | GET | 获取指定部门的厂区 |

#### 2.4 人员管理
**基础路径**: `/enterprise/staff`

| 端点 | 方法 | 说明 |
|------|------|------|
| `/enterprise/staff/departments/{dept_id}/members/` | GET | 获取指定部门的成员列表 |
| `/enterprise/staff/enterprise/{enterprise_id}/members/` | GET | 获取企业成员列表 |
| `/enterprise/staff/users/{user_id}/` | GET | 获取企业用户详情 |
| `/enterprise/staff/users/{user_id}/` | PUT | 更新企业用户信息 |

#### 2.5 项目管理
**基础路径**: `/enterprise/projects`

| 端点 | 方法 | 说明 |
|------|------|------|
| `/enterprise/projects/` | GET | 获取项目列表 |
| `/enterprise/projects/{project_id}/` | GET | 获取项目详情 |

### 3. 供应商后台管理 (Contractor Management)
**基础路径**: `/contractor`

#### 3.1 供应商信息管理
| 端点 | 方法 | 说明 |
|------|------|------|
| `/contractor/add/` | POST | 添加供应商 |
| `/contractor/add_user/` | POST | 添加供应商用户 |
| `/contractor/list/` | GET | 获取承包商列表 |
| `/contractor/create-project/` | POST | 与承包商创建合作项目 |

#### 3.2 供应商项目管理
**基础路径**: `/contractor/projects`

| 端点 | 方法 | 说明 |
|------|------|------|
| `/contractor/projects/add/` | POST | 添加项目 |

#### 3.3 计划管理
**基础路径**: `/contractor/plans`

| 端点 | 方法 | 说明 |
|------|------|------|
| `/contractor/plans/add/` | POST | 添加计划 |
| `/contractor/plans/{plan_id}/participants/` | GET | 获取计划的参与人员列表 |

### 4. 工单后台管理 (Ticket Management)
**基础路径**: `/tickets`

| 端点 | 方法 | 说明 |
|------|------|------|
| `/tickets/` | POST | 创建工单 |
| `/tickets/` | GET | 获取工单列表（支持筛选） |
| `/tickets/{ticket_id}/` | GET | 获取工单详情 |
| `/tickets/{ticket_id}/` | PUT | 更新工单 |
| `/tickets/{ticket_id}/` | DELETE | 删除工单 |

### 5. 用户后台管理 (User Management)
**基础路径**: `/users`

#### 5.1 用户管理
| 端点 | 方法 | 说明 |
|------|------|------|
| `/users/` | POST | 创建用户 |
| `/users/` | GET | 获取用户列表（支持筛选） |
| `/users/{user_id}/` | GET | 获取用户详情 |
| `/users/{user_id}/` | PUT | 更新用户信息 |
| `/users/{user_id}/` | DELETE | 删除用户（软删除） |
| `/users/{user_id}/change-password/` | POST | 修改密码（用户自己） |
| `/users/{user_id}/reset-password/` | POST | 重置密码（管理员） |

#### 5.2 角色管理
**基础路径**: `/users/roles`

| 端点 | 方法 | 说明 |
|------|------|------|
| `/users/roles/` | GET | 获取角色列表 |
| `/users/roles/{role_type}/` | GET | 获取角色详情 |
| `/users/roles/{role_type}/permissions/` | GET | 获取角色权限 |
| `/users/roles/{user_id}/role/` | PUT | 更新用户角色 |
| `/users/roles/enterprise/available/` | GET | 获取企业可用角色 |
| `/users/roles/contractor/available/` | GET | 获取承包商可用角色 |

## 依赖项说明 (Dependencies)

### 共享依赖 (Shared Dependencies)

在 `dependencies.py` 中定义了以下共享依赖：

1. **`get_current_user`**: 获取当前登录用户
2. **`authenticate_enterprise_level`**: 验证企业级别权限（企业管理员及以上）
3. **`authenticate_contractor_level`**: 验证承包商级别权限（承包商审批员及以上）
4. **`get_user_enterprise_id`**: 获取用户的企业ID

### 使用示例

```python
from routes.dependencies import get_current_user, authenticate_enterprise_level

@router.get("/example/")
async def example_endpoint(user: User = Depends(get_current_user)):
    # 需要登录的接口
    pass

@router.post("/example/", dependencies=[Depends(authenticate_enterprise_level)])
async def example_endpoint():
    # 需要企业管理员权限的接口
    pass
```

## 如何集成到 main.py

在 `main.py` 中集成路由的方式：

```python
from routes import main_router
from routes.auth import router as auth_router

# 注册认证路由（不带前缀）
app.include_router(auth_router)

# 注册主路由（包含企业和供应商管理）
app.include_router(main_router, prefix="/api")
```

## 设计原则 (Design Principles)

1. **模块化**: 按功能模块划分路由，每个模块独立管理
2. **层级化**: 采用清晰的路由层级结构，便于理解和维护
3. **可扩展**: 新增功能模块时，只需添加新的路由文件即可
4. **权限分离**: 将认证和权限验证逻辑抽离到 `dependencies.py`
5. **职责单一**: 每个路由文件只负责一个具体的功能模块

## 注意事项 (Notes)

1. 所有路由文件中使用 `from main import app` 来获取应用实例，这是延迟导入以避免循环依赖
2. 权限验证使用 `Depends()` 依赖注入方式
3. 企业用户和供应商用户的权限级别不同，需要使用相应的权限验证依赖
4. 所有接口都应该有适当的错误处理和权限检查

## 未来扩展 (Future Extensions)

如需添加新的功能模块，可以按照以下步骤：

1. 在 `routes/` 目录下创建新的模块目录
2. 在模块目录中创建 `__init__.py` 和具体的路由文件
3. 在 `routes/__init__.py` 中注册新模块的路由
4. 如有新的共享依赖，添加到 `dependencies.py`

例如，添加一个新的"报表管理"模块：

```
routes/
└── report/
    ├── __init__.py
    ├── daily_report.py
    └── monthly_report.py
```

然后在 `routes/__init__.py` 中注册：

```python
from .report import router as report_router
main_router.include_router(report_router, prefix="/report", tags=["报表管理"])
```

