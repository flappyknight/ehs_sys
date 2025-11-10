# 路由模块 (Routes Module)

## 快速导航

- 📖 [完整文档索引](./INDEX.md) - 查看所有模块的详细文档
- 🏗️ [路由结构说明](./ROUTES_STRUCTURE.md) - 了解路由架构和开发指南
- 📊 [重构总结](./RESTRUCTURE_SUMMARY.md) - 查看重构详情和统计数据

## 模块结构

```
routes/
├── admin/                    # 系统账户后台 (/admin)
├── enterprise_backend/       # 企业管理后台 (/enterprise-backend)
│   ├── user_management/      # 企业用户管理
│   ├── contractor_management/# 企业承包商管理
│   ├── ticket_management/    # 企业工单管理
│   ├── workflow_management/  # 企业作业流程管理
│   └── permission_management/# 企业权限管理
├── contractor_backend/       # 承包商管理后台 (/contractor-backend)
│   ├── staff_management/     # 承包商人员管理
│   ├── ticket_view/          # 工单浏览
│   └── cooperation_request/  # 合作申请管理
├── ticket/                   # 工单模块 (/tickets)
├── workflow/                 # 工单流程模块 (/workflow)
├── auth.py                   # 认证路由
└── dependencies.py           # 共享依赖项
```

## 主要模块

| 模块 | 路由前缀 | 说明 |
|------|---------|------|
| 认证模块 | `/token`, `/users/me`, `/logout` | 用户登录认证 |
| 系统账户后台 | `/admin` | 系统管理员功能 |
| 企业管理后台 | `/enterprise-backend` | 企业用户管理平台 |
| 承包商管理后台 | `/contractor-backend` | 承包商用户管理平台 |
| 工单模块 | `/tickets` | 作业工单管理 |
| 工单流程模块 | `/workflow` | 流程审批管理 |

## 文档规范

每个模块包含三类文档：

- **README.md** - 模块概述和功能说明
- **object_plan.md** - 设计方案和数据模型
- **interface_list.md** - API 接口文档

## 快速开始

### 查看接口文档
```bash
# 查看工单模块接口
cat routes/ticket/interface_list.md

# 查看企业用户管理接口
cat routes/enterprise_backend/user_management/interface_list.md
```

### 测试接口
访问 FastAPI 自动生成的文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 开发指南

1. **添加新接口**: 在对应模块的 Python 文件中添加路由函数
2. **更新文档**: 修改对应的 `interface_list.md` 文件
3. **测试**: 使用 FastAPI 文档进行测试
4. **提交**: 提交代码和文档更新

## 数据隔离

- **企业用户**: 通过 `enterprise_id` 自动过滤数据
- **承包商用户**: 通过 `contractor_id` 自动过滤数据
- **系统管理员**: 可访问所有数据

## 权限验证

使用 `dependencies.py` 中的依赖项：

```python
from routes.dependencies import get_current_user, authenticate_enterprise_level

@router.get("/")
async def get_data(user: User = Depends(get_current_user)):
    # 需要认证
    pass

@router.post("/")
async def create_data(user: User = Depends(authenticate_enterprise_level)):
    # 需要企业管理员权限
    pass
```

## 更多信息

详细文档请查看 [INDEX.md](./INDEX.md)

