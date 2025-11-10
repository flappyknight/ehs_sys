# 系统账户后台模块 - 接口列表

## 认证接口

### 1. 用户登录
- **接口路径**: `POST /admin/token`
- **功能描述**: 用户登录获取访问令牌
- **权限要求**: 无（公开接口）
- **请求参数**:
  ```json
  {
    "username": "admin",
    "password": "password123"
  }
  ```
- **响应数据**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
  ```
- **错误响应**:
  - 401: 用户名或密码错误

### 2. 获取当前用户信息
- **接口路径**: `GET /admin/users/me`
- **功能描述**: 获取当前登录用户的详细信息
- **权限要求**: 需要认证
- **请求参数**: 无
- **响应数据**:
  ```json
  {
    "user_id": 1,
    "username": "admin",
    "user_type": "admin",
    "email": "admin@example.com",
    "created_at": "2024-01-01T00:00:00"
  }
  ```

### 3. 用户登出
- **接口路径**: `POST /admin/logout`
- **功能描述**: 用户登出（清除客户端 Token）
- **权限要求**: 需要认证
- **请求参数**: 无
- **响应数据**:
  ```json
  {
    "message": "Logged out"
  }
  ```

---

## 系统用户管理接口

### 4. 创建管理员账户
- **接口路径**: `POST /admin/users`
- **功能描述**: 创建新的系统管理员账户
- **权限要求**: 系统管理员
- **请求参数**:
  ```json
  {
    "username": "new_admin",
    "password": "secure_password",
    "email": "admin@example.com"
  }
  ```
- **响应数据**:
  ```json
  {
    "message": "管理员账户创建成功",
    "user_id": 2
  }
  ```
- **错误响应**:
  - 400: 用户名已存在
  - 403: 权限不足

### 5. 获取所有用户列表
- **接口路径**: `GET /admin/users`
- **功能描述**: 获取系统中所有用户的列表（包括企业用户、承包商用户）
- **权限要求**: 系统管理员
- **请求参数**:
  - `user_type` (可选): 按用户类型筛选 (admin/enterprise/contractor)
  - `status` (可选): 按状态筛选 (true/false)
  - `keyword` (可选): 搜索关键词
  - `page` (可选): 页码，默认 1
  - `page_size` (可选): 每页数量，默认 20
- **响应数据**:
  ```json
  {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "user_id": 1,
        "username": "user001",
        "user_type": "enterprise",
        "name": "张三",
        "phone": "13800138000",
        "company_name": "XX企业",
        "status": true,
        "created_at": "2024-01-01T00:00:00"
      }
    ]
  }
  ```

### 6. 获取用户详情
- **接口路径**: `GET /admin/users/{user_id}`
- **功能描述**: 获取指定用户的详细信息
- **权限要求**: 系统管理员
- **请求参数**: 路径参数 `user_id`
- **响应数据**:
  ```json
  {
    "user_id": 1,
    "username": "user001",
    "user_type": "enterprise",
    "name": "张三",
    "phone": "13800138000",
    "email": "zhangsan@example.com",
    "company_id": 1,
    "company_name": "XX企业",
    "department_id": 1,
    "department_name": "技术部",
    "role_type": "manager",
    "status": true,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
  ```

### 7. 重置用户密码
- **接口路径**: `POST /admin/users/{user_id}/reset-password`
- **功能描述**: 管理员重置用户密码
- **权限要求**: 系统管理员
- **请求参数**:
  ```json
  {
    "new_password": "new_secure_password"
  }
  ```
- **响应数据**:
  ```json
  {
    "message": "密码重置成功"
  }
  ```

### 8. 禁用/启用用户
- **接口路径**: `PUT /admin/users/{user_id}/status`
- **功能描述**: 禁用或启用用户账户
- **权限要求**: 系统管理员
- **请求参数**:
  ```json
  {
    "status": false
  }
  ```
- **响应数据**:
  ```json
  {
    "message": "用户状态更新成功"
  }
  ```

---

## 企业管理接口

### 9. 创建企业
- **接口路径**: `POST /admin/enterprises`
- **功能描述**: 创建新企业
- **权限要求**: 系统管理员
- **请求参数**:
  ```json
  {
    "name": "XX科技有限公司",
    "type": "科技公司",
    "address": "北京市朝阳区XX路XX号",
    "contact_person": "李四",
    "contact_phone": "13900139000"
  }
  ```
- **响应数据**:
  ```json
  {
    "message": "企业创建成功",
    "company_id": 1
  }
  ```

### 10. 获取企业列表
- **接口路径**: `GET /admin/enterprises`
- **功能描述**: 获取所有企业列表
- **权限要求**: 系统管理员
- **请求参数**:
  - `keyword` (可选): 搜索关键词
  - `status` (可选): 按状态筛选
  - `page` (可选): 页码
  - `page_size` (可选): 每页数量
- **响应数据**:
  ```json
  {
    "total": 50,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "company_id": 1,
        "name": "XX科技有限公司",
        "type": "科技公司",
        "contact_person": "李四",
        "contact_phone": "13900139000",
        "status": true,
        "created_at": "2024-01-01T00:00:00"
      }
    ]
  }
  ```

### 11. 获取企业详情
- **接口路径**: `GET /admin/enterprises/{company_id}`
- **功能描述**: 获取指定企业的详细信息
- **权限要求**: 系统管理员
- **请求参数**: 路径参数 `company_id`
- **响应数据**:
  ```json
  {
    "company_id": 1,
    "name": "XX科技有限公司",
    "type": "科技公司",
    "address": "北京市朝阳区XX路XX号",
    "contact_person": "李四",
    "contact_phone": "13900139000",
    "status": true,
    "department_count": 5,
    "staff_count": 50,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
  ```

### 12. 更新企业信息
- **接口路径**: `PUT /admin/enterprises/{company_id}`
- **功能描述**: 更新企业信息
- **权限要求**: 系统管理员
- **请求参数**:
  ```json
  {
    "name": "XX科技有限公司",
    "type": "科技公司",
    "address": "北京市朝阳区XX路XX号",
    "contact_person": "李四",
    "contact_phone": "13900139000"
  }
  ```
- **响应数据**:
  ```json
  {
    "message": "企业信息更新成功"
  }
  ```

### 13. 删除企业
- **接口路径**: `DELETE /admin/enterprises/{company_id}`
- **功能描述**: 删除企业（软删除）
- **权限要求**: 系统管理员
- **请求参数**: 路径参数 `company_id`
- **响应数据**:
  ```json
  {
    "message": "企业删除成功"
  }
  ```

---

## 承包商管理接口

### 14. 创建承包商
- **接口路径**: `POST /admin/contractors`
- **功能描述**: 创建新承包商
- **权限要求**: 系统管理员
- **请求参数**:
  ```json
  {
    "company_name": "XX建筑工程有限公司",
    "company_type": "建筑施工",
    "legal_person": "王五",
    "establish_date": "2020-01-01",
    "business_license": "91110000XXXXXXXXXX"
  }
  ```
- **响应数据**:
  ```json
  {
    "message": "承包商创建成功",
    "contractor_id": 1
  }
  ```

### 15. 获取承包商列表
- **接口路径**: `GET /admin/contractors`
- **功能描述**: 获取所有承包商列表
- **权限要求**: 系统管理员
- **请求参数**:
  - `keyword` (可选): 搜索关键词
  - `company_type` (可选): 按公司类型筛选
  - `status` (可选): 按状态筛选
  - `page` (可选): 页码
  - `page_size` (可选): 每页数量
- **响应数据**:
  ```json
  {
    "total": 30,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "contractor_id": 1,
        "company_name": "XX建筑工程有限公司",
        "company_type": "建筑施工",
        "legal_person": "王五",
        "establish_date": "2020-01-01",
        "status": true,
        "project_count": 5,
        "created_at": "2024-01-01T00:00:00"
      }
    ]
  }
  ```

### 16. 获取承包商详情
- **接口路径**: `GET /admin/contractors/{contractor_id}`
- **功能描述**: 获取指定承包商的详细信息
- **权限要求**: 系统管理员
- **请求参数**: 路径参数 `contractor_id`
- **响应数据**:
  ```json
  {
    "contractor_id": 1,
    "company_name": "XX建筑工程有限公司",
    "company_type": "建筑施工",
    "legal_person": "王五",
    "establish_date": "2020-01-01",
    "business_license": "91110000XXXXXXXXXX",
    "status": true,
    "staff_count": 20,
    "project_count": 5,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
  ```

### 17. 更新承包商信息
- **接口路径**: `PUT /admin/contractors/{contractor_id}`
- **功能描述**: 更新承包商信息
- **权限要求**: 系统管理员
- **请求参数**:
  ```json
  {
    "company_name": "XX建筑工程有限公司",
    "company_type": "建筑施工",
    "legal_person": "王五",
    "establish_date": "2020-01-01",
    "business_license": "91110000XXXXXXXXXX"
  }
  ```
- **响应数据**:
  ```json
  {
    "message": "承包商信息更新成功"
  }
  ```

### 18. 删除承包商
- **接口路径**: `DELETE /admin/contractors/{contractor_id}`
- **功能描述**: 删除承包商（软删除）
- **权限要求**: 系统管理员
- **请求参数**: 路径参数 `contractor_id`
- **响应数据**:
  ```json
  {
    "message": "承包商删除成功"
  }
  ```

---

## 测试接口

### 19. 测试接口
- **接口路径**: `GET /admin/test`
- **功能描述**: 测试接口连通性
- **权限要求**: 需要认证
- **请求参数**: 无
- **响应数据**:
  ```json
  {
    "hello": "world",
    "user": "admin",
    "timestamp": "2024-01-01T00:00:00"
  }
  ```

---

## 通用说明

### 认证方式
所有需要认证的接口都需要在请求头中携带 Token:
```
Authorization: Bearer <access_token>
```

### 分页参数
支持分页的接口统一使用以下参数:
- `page`: 页码，从 1 开始
- `page_size`: 每页数量，默认 20，最大 100

### 错误响应格式
```json
{
  "detail": "错误描述信息"
}
```

### 常见错误码
- 400: 请求参数错误
- 401: 未认证或认证失败
- 403: 权限不足
- 404: 资源不存在
- 500: 服务器内部错误

