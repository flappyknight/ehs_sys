# 路由集成指南 (Router Integration Guide)

## 如何在 main.py 中集成新路由结构

### 方案一：完全替换（推荐用于新项目）

如果你想完全使用新的路由结构，可以按照以下步骤操作：

#### 1. 在 main.py 中导入路由

```python
# 在 main.py 顶部添加导入
from routes import main_router
from routes.auth import router as auth_router
```

#### 2. 注册路由

```python
# 在创建 FastAPI app 和添加 CORS 中间件之后
# 注册认证路由（不带前缀，保持原有路径）
app.include_router(auth_router)

# 注册主路由（企业和供应商管理）
app.include_router(main_router, prefix="/api")
```

#### 3. 完整示例

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import main_router
from routes.auth import router as auth_router

# ... lifespan 和其他配置 ...

app = FastAPI(lifespan=lifespan)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://192.168.1.185:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router)
app.include_router(main_router, prefix="/api")
```

### 方案二：渐进式迁移（推荐用于现有项目）

如果你想逐步迁移，保留原有接口的同时使用新路由：

#### 1. 保留 main.py 中的所有现有路由

不要删除 main.py 中的任何代码。

#### 2. 添加新路由作为备用

```python
# 在 main.py 末尾添加
from routes import main_router
from routes.auth import router as auth_router

# 新版本的路由使用 /v2 前缀
app.include_router(auth_router, prefix="/v2")
app.include_router(main_router, prefix="/v2/api")
```

#### 3. 测试新路由

- 原有接口: `POST /token`
- 新版接口: `POST /v2/token`

#### 4. 逐步切换前端调用

在确认新路由工作正常后，逐步将前端的 API 调用切换到新路由。

#### 5. 最终清理

当所有接口都切换完成后，删除 main.py 中的旧路由代码，并移除 `/v2` 前缀。

## 路径对比表

### 认证接口

| 功能 | 原路径 | 新路径（方案一） | 新路径（方案二） |
|------|--------|-----------------|-----------------|
| 登录 | `POST /token` | `POST /token` | `POST /v2/token` |
| 获取用户信息 | `GET /users/me/` | `GET /users/me/` | `GET /v2/users/me/` |
| 登出 | `POST /logout` | `POST /logout` | `POST /v2/logout` |

### 企业管理接口

| 功能 | 原路径 | 新路径（方案一） | 新路径（方案二） |
|------|--------|-----------------|-----------------|
| 添加企业 | `POST /enterprise/add/` | `POST /api/enterprise/add/` | `POST /v2/api/enterprise/add/` |
| 获取企业列表 | `GET /enterprises/` | `GET /api/enterprise/list/` | `GET /v2/api/enterprise/list/` |
| 获取部门列表 | `GET /departments/` | `GET /api/enterprise/departments/` | `GET /v2/api/enterprise/departments/` |
| 创建厂区 | `POST /areas/` | `POST /api/enterprise/areas/` | `POST /v2/api/enterprise/areas/` |
| 获取项目列表 | `GET /projects/` | `GET /api/enterprise/projects/` | `GET /v2/api/enterprise/projects/` |

### 供应商管理接口

| 功能 | 原路径 | 新路径（方案一） | 新路径（方案二） |
|------|--------|-----------------|-----------------|
| 添加供应商 | `POST /contractor/add/` | `POST /api/contractor/add/` | `POST /v2/api/contractor/add/` |
| 获取承包商列表 | `GET /contractors/` | `GET /api/contractor/list/` | `GET /v2/api/contractor/list/` |
| 添加计划 | `POST /contractor/add_plan/` | `POST /api/contractor/plans/add/` | `POST /v2/api/contractor/plans/add/` |

## 前端调整建议

### 1. 创建 API 配置文件

```typescript
// src/config/api.ts
const API_VERSION = 'v2'; // 或者留空 ''
const API_PREFIX = API_VERSION ? `/${API_VERSION}` : '';

export const API_ENDPOINTS = {
  // 认证
  LOGIN: `${API_PREFIX}/token`,
  LOGOUT: `${API_PREFIX}/logout`,
  USER_INFO: `${API_PREFIX}/users/me/`,
  
  // 企业管理
  ENTERPRISE: {
    ADD: `${API_PREFIX}/api/enterprise/add/`,
    LIST: `${API_PREFIX}/api/enterprise/list/`,
    ADD_USER: `${API_PREFIX}/api/enterprise/add_user/`,
  },
  
  // 部门管理
  DEPARTMENT: {
    ADD: `${API_PREFIX}/api/enterprise/departments/add/`,
    LIST: `${API_PREFIX}/api/enterprise/departments/`,
  },
  
  // 厂区管理
  AREA: {
    CREATE: `${API_PREFIX}/api/enterprise/areas/`,
    LIST: `${API_PREFIX}/api/enterprise/areas/`,
    DETAIL: (id: number) => `${API_PREFIX}/api/enterprise/areas/${id}/`,
  },
  
  // 项目管理
  PROJECT: {
    LIST: `${API_PREFIX}/api/enterprise/projects/`,
    DETAIL: (id: number) => `${API_PREFIX}/api/enterprise/projects/${id}/`,
  },
  
  // 供应商管理
  CONTRACTOR: {
    ADD: `${API_PREFIX}/api/contractor/add/`,
    LIST: `${API_PREFIX}/api/contractor/list/`,
    CREATE_PROJECT: `${API_PREFIX}/api/contractor/create-project/`,
  },
  
  // 计划管理
  PLAN: {
    ADD: `${API_PREFIX}/api/contractor/plans/add/`,
    PARTICIPANTS: (id: number) => `${API_PREFIX}/api/contractor/plans/${id}/participants/`,
  },
};
```

### 2. 使用示例

```typescript
import { API_ENDPOINTS } from '@/config/api';
import axios from 'axios';

// 登录
const login = async (username: string, password: string) => {
  const response = await axios.post(API_ENDPOINTS.LOGIN, {
    username,
    password,
  });
  return response.data;
};

// 获取项目列表
const getProjects = async () => {
  const response = await axios.get(API_ENDPOINTS.PROJECT.LIST);
  return response.data;
};

// 获取项目详情
const getProjectDetail = async (projectId: number) => {
  const response = await axios.get(API_ENDPOINTS.PROJECT.DETAIL(projectId));
  return response.data;
};
```

## 注意事项

1. **延迟导入**: 路由文件中使用 `from main import app` 是为了避免循环依赖，这是正常的。

2. **数据库引擎**: 所有路由都通过 `app.state.engine` 访问数据库连接，确保 main.py 中正确初始化了 engine。

3. **权限依赖**: 新路由使用了统一的权限验证依赖，确保权限逻辑一致。

4. **错误处理**: 所有路由都包含了适当的错误处理和 HTTP 异常。

5. **API 文档**: 使用新路由后，FastAPI 的自动文档 (`/docs`) 会按照标签分组显示，更加清晰。

## 测试建议

### 1. 使用 FastAPI 自动文档测试

访问 `http://localhost:8000/docs` 查看所有接口，可以直接在浏览器中测试。

### 2. 使用 curl 测试

```bash
# 登录
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# 获取用户信息（需要 token）
curl -X GET "http://localhost:8000/users/me/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# 获取项目列表
curl -X GET "http://localhost:8000/api/enterprise/projects/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 3. 使用 Postman 或 Insomnia

导入 OpenAPI 规范（从 `/docs` 页面导出）到 Postman 或 Insomnia 进行测试。

## 回滚方案

如果新路由出现问题，可以快速回滚：

### 方案一回滚

```python
# 注释掉新路由
# app.include_router(auth_router)
# app.include_router(main_router, prefix="/api")

# 原有的路由代码保持不变
```

### 方案二回滚

```python
# 直接删除或注释掉 v2 路由
# app.include_router(auth_router, prefix="/v2")
# app.include_router(main_router, prefix="/v2/api")
```

## 性能优化建议

1. **异步操作**: 所有路由处理函数都是异步的，充分利用 FastAPI 的异步特性。

2. **数据库连接池**: 确保在 `db/connection.py` 中正确配置了连接池。

3. **缓存**: 对于频繁访问的数据（如企业列表、部门列表），可以考虑添加缓存。

4. **分页**: 对于返回大量数据的接口，建议添加分页功能。

## 下一步

1. ✅ 路由结构已创建
2. ⏭️ 在 main.py 中集成路由
3. ⏭️ 测试所有接口
4. ⏭️ 更新前端 API 调用
5. ⏭️ 清理旧代码（可选）

