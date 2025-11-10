# 企业权限管理模块 - 接口列表

## 角色管理接口

### 1. 创建角色
- **接口路径**: `POST /enterprise-backend/permission-management/roles`
- **功能描述**: 创建自定义角色
- **权限要求**: 企业管理员
- **请求参数**: 参考 RoleCreate 对象
- **响应数据**: `{"message": "角色创建成功", "role_id": 1}`

### 2. 获取角色列表
- **接口路径**: `GET /enterprise-backend/permission-management/roles`
- **功能描述**: 获取企业的角色列表
- **权限要求**: 企业管理员
- **响应数据**: 角色列表

### 3. 更新角色
- **接口路径**: `PUT /enterprise-backend/permission-management/roles/{role_id}`
- **功能描述**: 更新角色信息和权限
- **权限要求**: 企业管理员
- **响应数据**: `{"message": "角色更新成功"}`

### 4. 删除角色
- **接口路径**: `DELETE /enterprise-backend/permission-management/roles/{role_id}`
- **功能描述**: 删除自定义角色
- **权限要求**: 企业管理员
- **响应数据**: `{"message": "角色删除成功"}`

---

## 权限管理接口

### 5. 获取权限列表
- **接口路径**: `GET /enterprise-backend/permission-management/permissions`
- **功能描述**: 获取所有可用权限
- **权限要求**: 企业管理员
- **响应数据**: 权限列表（按模块分组）

### 6. 分配用户角色
- **接口路径**: `POST /enterprise-backend/permission-management/users/{user_id}/roles`
- **功能描述**: 为用户分配角色
- **权限要求**: 企业管理员
- **请求参数**: `{"role_type": "site_staff"}`
- **响应数据**: `{"message": "角色分配成功"}`

