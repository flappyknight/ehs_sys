# 快速开始指南 (Quick Start Guide)

## 🚀 5分钟快速集成

### 步骤 1: 检查文件结构

确保你的 `routes/` 目录包含以下文件：

```
routes/
├── __init__.py              ✅ 主路由注册
├── dependencies.py          ✅ 共享依赖
├── auth.py                  ✅ 认证路由
├── enterprise/              ✅ 企业管理模块
│   ├── __init__.py
│   ├── enterprise.py
│   ├── department.py
│   ├── area.py
│   ├── staff.py
│   └── project.py
└── contractor/              ✅ 供应商管理模块
    ├── __init__.py
    ├── contractor.py
    ├── project.py
    └── plan.py
```

### 步骤 2: 在 main.py 中添加导入

在 `main.py` 文件顶部（在其他导入之后）添加：

```python
# 导入新的路由模块
from routes import main_router
from routes.auth import router as auth_router
```

### 步骤 3: 注册路由

在 `main.py` 中，在创建 FastAPI app 和 CORS 中间件之后，添加：

```python
# 注册认证路由（保持原有路径）
app.include_router(auth_router)

# 注册主路由（企业和供应商管理）
app.include_router(main_router, prefix="/api")
```

### 步骤 4: 测试

启动应用：

```bash
# 如果使用 uvicorn
uvicorn main:app --reload

# 如果使用其他方式，按照你的启动方式
```

访问自动文档：
```
http://localhost:8000/docs
```

你应该能看到按照标签分组的所有接口！

## 📝 完整示例

下面是一个完整的 `main.py` 集成示例：

```python
from datetime import timedelta, datetime, timezone
from typing import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.connection import create_engine
from core.init_admin import init_admin_user

# 导入新的路由模块
from routes import main_router
from routes.auth import router as auth_router

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # Startup
    engine = create_engine()
    app.state.engine = engine
    await init_admin_user(app)
    yield
    # Shutdown
    await engine.dispose()
    print("数据库连接已关闭")

app = FastAPI(lifespan=lifespan)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://192.168.1.185:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router)
app.include_router(main_router, prefix="/api")

# 可选：保留原有的路由作为备份（渐进式迁移）
# ... 原有的路由代码 ...
```

## 🧪 测试新路由

### 1. 测试登录接口

```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=your_password"
```

### 2. 测试获取用户信息

```bash
curl -X GET "http://localhost:8000/users/me/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 3. 测试企业接口

```bash
# 获取企业列表（需要管理员权限）
curl -X GET "http://localhost:8000/api/enterprise/list/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# 获取部门列表
curl -X GET "http://localhost:8000/api/enterprise/departments/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# 获取项目列表
curl -X GET "http://localhost:8000/api/enterprise/projects/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 4. 测试供应商接口

```bash
# 获取承包商列表
curl -X GET "http://localhost:8000/api/contractor/list/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🔍 验证清单

完成集成后，请检查以下项目：

- [ ] 应用能正常启动，无导入错误
- [ ] 访问 `/docs` 能看到所有接口
- [ ] 接口按标签正确分组
- [ ] 登录接口正常工作
- [ ] 能获取当前用户信息
- [ ] 企业管理接口可以访问
- [ ] 供应商管理接口可以访问
- [ ] 权限验证正常工作

## 🎯 路径对照表

### 认证接口（无变化）

| 功能 | 路径 |
|------|------|
| 登录 | `POST /token` |
| 获取用户信息 | `GET /users/me/` |
| 登出 | `POST /logout` |
| 测试 | `GET /test/` |

### 企业管理接口（添加 /api/enterprise 前缀）

| 原路径 | 新路径 |
|--------|--------|
| `POST /enterprise/add/` | `POST /api/enterprise/add/` |
| `GET /enterprises/` | `GET /api/enterprise/list/` |
| `GET /departments/` | `GET /api/enterprise/departments/` |
| `POST /areas/` | `POST /api/enterprise/areas/` |
| `GET /projects/` | `GET /api/enterprise/projects/` |

### 供应商管理接口（添加 /api/contractor 前缀）

| 原路径 | 新路径 |
|--------|--------|
| `POST /contractor/add/` | `POST /api/contractor/add/` |
| `GET /contractors/` | `GET /api/contractor/list/` |
| `POST /contractor/add_plan/` | `POST /api/contractor/plans/add/` |

## ⚠️ 常见问题

### Q1: 导入错误 "cannot import name 'main_router'"

**解决方案**: 确保 `routes/__init__.py` 文件存在且内容正确。

### Q2: 循环依赖错误

**解决方案**: 这是正常的，路由文件中使用 `from main import app` 是延迟导入，不会导致问题。

### Q3: 接口返回 404

**解决方案**: 
- 检查路由是否正确注册
- 检查 URL 路径是否正确（注意 `/api` 前缀）
- 查看 `/docs` 确认接口路径

### Q4: 权限验证失败

**解决方案**:
- 确保 token 正确传递
- 检查用户角色和权限级别
- 查看 `dependencies.py` 中的权限验证逻辑

### Q5: 数据库连接错误

**解决方案**:
- 确保 `app.state.engine` 在 lifespan 中正确初始化
- 检查数据库连接配置

## 📚 更多文档

- **详细说明**: 查看 `README.md`
- **结构图**: 查看 `STRUCTURE.md`
- **集成指南**: 查看 `INTEGRATION_GUIDE.md`
- **项目总结**: 查看 `SUMMARY.md`

## 💡 提示

1. **渐进式迁移**: 如果不确定，可以先使用 `/v2` 前缀测试新路由
2. **保留备份**: 在删除 main.py 中的旧代码前，先确保新路由完全正常
3. **查看文档**: FastAPI 的自动文档 (`/docs`) 是你的好朋友
4. **日志调试**: 如有问题，查看应用日志获取详细错误信息

## 🎉 完成！

如果所有测试都通过，恭喜你已经成功集成了新的路由结构！

现在你的项目拥有：
- ✅ 清晰的代码结构
- ✅ 易于维护的模块化设计
- ✅ 完善的权限控制
- ✅ 良好的扩展性

---

**需要帮助？** 查看其他文档或联系开发团队。

