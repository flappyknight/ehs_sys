# 路由模块索引 (Routes Module Index)

## 📂 文件清单

### 核心文件 (Core Files)

| 文件 | 大小 | 说明 | 接口数 |
|------|------|------|--------|
| `__init__.py` | 482B | 主路由注册中心 | - |
| `dependencies.py` | 4.0KB | 共享依赖（认证、权限） | - |
| `auth.py` | 1.7KB | 认证路由 | 4 |

### 企业管理模块 (Enterprise Module)

| 文件 | 说明 | 接口数 |
|------|------|--------|
| `enterprise/__init__.py` | 企业路由注册 | - |
| `enterprise/enterprise.py` | 企业信息管理 | 3 |
| `enterprise/department.py` | 部门管理 | 3 |
| `enterprise/area.py` | 厂区管理 | 6 |
| `enterprise/staff.py` | 人员管理 | 4 |
| `enterprise/project.py` | 项目管理 | 2 |

### 供应商管理模块 (Contractor Module)

| 文件 | 说明 | 接口数 |
|------|------|--------|
| `contractor/__init__.py` | 供应商路由注册 | - |
| `contractor/contractor.py` | 供应商信息管理 | 4 |
| `contractor/project.py` | 供应商项目管理 | 1 |
| `contractor/plan.py` | 计划管理 | 2 |

### 工单管理模块 (Ticket Module)

| 文件 | 说明 | 接口数 |
|------|------|--------|
| `ticket/__init__.py` | 工单路由注册 | - |
| `ticket/ticket.py` | 工单管理（增删改查） | 5 |

### 用户管理模块 (User Module)

| 文件 | 说明 | 接口数 |
|------|------|--------|
| `user/__init__.py` | 用户路由注册 | - |
| `user/user.py` | 用户管理（增删改查） | 7 |
| `user/role.py` | 角色管理 | 6 |

### 文档文件 (Documentation)

| 文件 | 大小 | 说明 |
|------|------|------|
| `README.md` | 6.8KB | 详细的路由结构说明 |
| `STRUCTURE.md` | 7.1KB | 可视化结构图和统计 |
| `INTEGRATION_GUIDE.md` | 7.9KB | 集成指南（前后端） |
| `SUMMARY.md` | 7.2KB | 项目重构总结 |
| `QUICK_START.md` | 6.5KB | 5分钟快速开始 |
| `INDEX.md` | 本文件 | 文件索引和导航 |

## 📊 统计数据

- **总文件数**: 23个文件
  - Python 文件: 17个
  - 文档文件: 6个（含本文件）
- **总代码行数**: ~2,200行
- **总接口数**: 47个
- **模块数**: 4个主模块（企业、供应商、工单、用户）
- **子模块数**: 11个功能子模块

## 🗺️ 文档导航

### 👉 新手入门
1. **先看**: `QUICK_START.md` - 5分钟快速集成
2. **再看**: `INTEGRATION_GUIDE.md` - 详细集成方案

### 👉 深入了解
1. **结构**: `STRUCTURE.md` - 完整的路由结构图
2. **说明**: `README.md` - 详细的功能说明
3. **总结**: `SUMMARY.md` - 项目重构总结

### 👉 日常使用
- 查找接口: 使用 `STRUCTURE.md` 的路由树
- 添加功能: 参考 `README.md` 的设计原则
- 问题排查: 查看 `QUICK_START.md` 的常见问题

## 🎯 快速查找

### 我想...

#### 集成路由到 main.py
→ 查看 `QUICK_START.md` 步骤 2-3

#### 了解路由结构
→ 查看 `STRUCTURE.md` 的路由树

#### 添加新接口
→ 查看 `README.md` 的"维护指南"

#### 修改权限验证
→ 编辑 `dependencies.py`

#### 添加新模块
→ 查看 `README.md` 的"未来扩展"

#### 前端集成
→ 查看 `INTEGRATION_GUIDE.md` 的"前端调整建议"

#### 测试接口
→ 查看 `QUICK_START.md` 的"测试新路由"

## 📋 接口速查

### 认证 (Authentication)
```
POST   /token              # 登录
GET    /users/me/          # 获取用户信息
POST   /logout             # 登出
GET    /test/              # 测试
```

### 企业管理 (Enterprise)
```
# 企业信息
POST   /api/enterprise/add/
GET    /api/enterprise/list/
POST   /api/enterprise/add_user/

# 部门管理
POST   /api/enterprise/departments/add/
GET    /api/enterprise/departments/
GET    /api/enterprise/departments/with-members/

# 厂区管理
POST   /api/enterprise/areas/
GET    /api/enterprise/areas/
GET    /api/enterprise/areas/{area_id}/
PUT    /api/enterprise/areas/{area_id}/
DELETE /api/enterprise/areas/{area_id}/
GET    /api/enterprise/areas/by-department/{dept_id}/

# 人员管理
GET    /api/enterprise/staff/departments/{dept_id}/members/
GET    /api/enterprise/staff/enterprise/{enterprise_id}/members/
GET    /api/enterprise/staff/users/{user_id}/
PUT    /api/enterprise/staff/users/{user_id}/

# 项目管理
GET    /api/enterprise/projects/
GET    /api/enterprise/projects/{project_id}/
```

### 供应商管理 (Contractor)
```
# 供应商信息
POST   /api/contractor/add/
POST   /api/contractor/add_user/
GET    /api/contractor/list/
POST   /api/contractor/create-project/

# 项目管理
POST   /api/contractor/projects/add/

# 计划管理
POST   /api/contractor/plans/add/
GET    /api/contractor/plans/{plan_id}/participants/
```

### 工单管理 (Ticket)
```
POST   /api/tickets/                    # 创建工单
GET    /api/tickets/                    # 获取工单列表（支持筛选）
GET    /api/tickets/{ticket_id}/        # 获取工单详情
PUT    /api/tickets/{ticket_id}/        # 更新工单
DELETE /api/tickets/{ticket_id}/        # 删除工单
```

### 用户管理 (User)
```
# 用户管理
POST   /api/users/                              # 创建用户
GET    /api/users/                              # 获取用户列表（支持筛选）
GET    /api/users/{user_id}/                    # 获取用户详情
PUT    /api/users/{user_id}/                    # 更新用户信息
DELETE /api/users/{user_id}/                    # 删除用户（软删除）
POST   /api/users/{user_id}/change-password/   # 修改密码
POST   /api/users/{user_id}/reset-password/    # 重置密码（管理员）

# 角色管理
GET    /api/users/roles/                        # 获取角色列表
GET    /api/users/roles/{role_type}/            # 获取角色详情
GET    /api/users/roles/{role_type}/permissions/ # 获取角色权限
PUT    /api/users/roles/{user_id}/role/         # 更新用户角色
GET    /api/users/roles/enterprise/available/   # 获取企业可用角色
GET    /api/users/roles/contractor/available/   # 获取承包商可用角色
```

## 🔧 维护信息

### 版本历史
- **v1.0** (2025-11-03): 初始版本，完整路由结构

### 贡献者
- 架构设计: AI Assistant
- 代码实现: AI Assistant
- 文档编写: AI Assistant

### 许可证
根据项目主许可证

## 🚀 下一步

### 立即行动
1. [ ] 阅读 `QUICK_START.md`
2. [ ] 在 main.py 中集成路由
3. [ ] 测试所有接口
4. [ ] 更新前端 API 调用

### 后续优化
1. [ ] 添加单元测试
2. [ ] 实现接口缓存
3. [ ] 添加请求日志
4. [ ] 性能监控

## 📞 获取帮助

### 遇到问题？
1. 先查看 `QUICK_START.md` 的"常见问题"
2. 查看 FastAPI 自动文档 `/docs`
3. 检查应用日志
4. 查看相关源代码

### 需要扩展？
1. 参考 `README.md` 的"未来扩展"章节
2. 查看现有模块的实现方式
3. 遵循相同的代码风格和结构

---

**最后更新**: 2025-11-03  
**文档版本**: v1.0  
**状态**: ✅ 完成

**提示**: 建议将本文件加入书签，作为路由模块的快速参考！

