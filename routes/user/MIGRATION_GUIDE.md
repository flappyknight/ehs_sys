# 用户管理接口迁移指南

## 📋 迁移概述

用户管理相关的接口已从 `main.py` 迁移到 `routes/user` 模块，以实现更好的代码组织和模块化。

## 🔄 接口路径变化

### ⚠️ 重要提示
所有迁移的接口路径前缀从原来的根路径改为 `/user-management`

### 企业用户管理接口

| 原路径 | 新路径 | 方法 | 说明 |
|--------|--------|------|------|
| `/enterprise/add_user/` | `/user-management/enterprise/` | POST | 添加企业用户 |
| `/staff/departments/` | `/user-management/staff/departments/` | GET | 获取部门列表及成员数量 |
| `/staff/departments/{dept_id}/members/` | `/user-management/staff/departments/{dept_id}/members/` | GET | 获取指定部门的成员列表 |
| `/staff/enterprise/{enterprise_id}/members/` | `/user-management/staff/enterprise/{enterprise_id}/members/` | GET | 获取企业成员列表 |
| `/staff/users/{user_id}/` | `/user-management/staff/users/{user_id}/` | GET | 获取企业用户详情 |
| `/staff/users/{user_id}/` | `/user-management/staff/users/{user_id}/` | PUT | 更新企业用户信息 |

### 承包商用户管理接口

| 原路径 | 新路径 | 方法 | 说明 |
|--------|--------|------|------|
| `/contractor/add_user/` | `/user-management/contractor/` | POST | 添加承包商用户 |

### 保持不变的接口

以下认证相关接口保持在 `main.py` 中，路径**不变**：

| 路径 | 方法 | 说明 |
|------|------|------|
| `/token` | POST | 用户登录获取 token |
| `/users/me/` | GET | 获取当前登录用户信息 |
| `/logout` | POST | 用户登出 |

## 🔧 前端代码需要修改的地方

如果前端代码中有调用以下接口，需要更新路径：

### 示例：添加企业用户

**旧代码：**
```typescript
await api.post('/enterprise/add_user/', userData)
```

**新代码：**
```typescript
await api.post('/user-management/enterprise/', userData)
```

### 示例：获取部门成员

**旧代码：**
```typescript
await api.get(`/staff/departments/${deptId}/members/`)
```

**新代码：**
```typescript
await api.get(`/user-management/staff/departments/${deptId}/members/`)
```

## ✅ 验证步骤

1. **启动服务器**
   ```bash
   conda activate ehs_env
   cd /Users/dubin/work/ehs_sys
   python -m uvicorn main:app --reload --port 8100 --host 0.0.0.0
   ```

2. **测试登录接口**
   ```bash
   curl -X POST "http://localhost:8100/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=admin123"
   ```

3. **测试用户信息接口**
   ```bash
   curl -X GET "http://localhost:8100/users/me/" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

4. **查看所有接口文档**
   访问：http://localhost:8100/docs

## 📝 注意事项

1. **路径前缀变化**：所有用户管理接口现在使用 `/user-management` 前缀
2. **认证接口不变**：`/users/me/` 等认证接口保持原路径
3. **权限验证不变**：所有接口的权限验证逻辑保持不变
4. **数据隔离不变**：企业数据隔离逻辑保持不变

## 🎯 迁移优势

1. **更好的代码组织**：用户管理功能集中在 `routes/user` 模块
2. **模块化设计**：便于维护和扩展
3. **清晰的路由结构**：通过 `/user-management` 前缀明确标识用户管理接口
4. **避免路径冲突**：使用独立前缀避免与认证接口冲突

## 🐛 问题排查

### 问题：前端调用接口返回 404

**原因**：前端代码还在使用旧的路径

**解决**：更新前端代码中的接口路径，添加 `/user-management` 前缀

### 问题：/users/me/ 返回 422 错误

**原因**：路由冲突，`/users` 前缀被 user_router 占用

**解决**：已将 user_router 改为 `/user-management` 前缀，避免冲突

## 📞 联系方式

如有问题，请联系开发团队。

---

**最后更新时间**：2025-11-03
**版本**：v1.0

