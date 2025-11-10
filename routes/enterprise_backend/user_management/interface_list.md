# 企业用户管理模块 - 接口列表

## 员工管理接口

### 1. 添加企业员工
- **接口路径**: `POST /enterprise-backend/user-management/users`
- **功能描述**: 添加新的企业员工
- **权限要求**: 企业管理员
- **请求参数**:
  ```json
  {
    "name": "张三",
    "phone": "13800138000",
    "email": "zhangsan@example.com",
    "position": "工程师",
    "department_id": 1,
    "role_type": "staff",
    "create_account": true
  }
  ```
- **响应数据**:
  ```json
  {
    "message": "员工添加成功",
    "user_id": 1
  }
  ```

### 2. 获取员工列表
- **接口路径**: `GET /enterprise-backend/user-management/users`
- **功能描述**: 获取企业员工列表
- **权限要求**: 企业管理员、现场人员
- **请求参数**:
  - `department_id` (可选): 按部门筛选
  - `role_type` (可选): 按角色筛选
  - `status` (可选): 按状态筛选
  - `keyword` (可选): 搜索关键词（姓名、手机号）
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
        "user_id": 1,
        "name": "张三",
        "phone": "13800138000",
        "email": "zhangsan@example.com",
        "position": "工程师",
        "department_name": "技术部",
        "role_type": "staff",
        "status": true
      }
    ]
  }
  ```

### 3. 获取员工详情
- **接口路径**: `GET /enterprise-backend/user-management/users/{user_id}`
- **功能描述**: 获取指定员工的详细信息
- **权限要求**: 企业管理员、现场人员、本人
- **请求参数**: 路径参数 `user_id`
- **响应数据**:
  ```json
  {
    "user_id": 1,
    "name": "张三",
    "phone": "13800138000",
    "email": "zhangsan@example.com",
    "position": "工程师",
    "department_id": 1,
    "department_name": "技术部",
    "role_type": "staff",
    "approval_level": 1,
    "status": true,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
  ```

### 4. 更新员工信息
- **接口路径**: `PUT /enterprise-backend/user-management/users/{user_id}`
- **功能描述**: 更新员工信息
- **权限要求**: 企业管理员、本人（部分字段）
- **请求参数**:
  ```json
  {
    "name": "张三",
    "phone": "13800138000",
    "email": "zhangsan@example.com",
    "position": "高级工程师",
    "department_id": 2,
    "role_type": "site_staff"
  }
  ```
- **响应数据**:
  ```json
  {
    "message": "员工信息更新成功"
  }
  ```

### 5. 禁用/启用员工
- **接口路径**: `PUT /enterprise-backend/user-management/users/{user_id}/status`
- **功能描述**: 禁用或启用员工账户
- **权限要求**: 企业管理员
- **请求参数**:
  ```json
  {
    "status": false
  }
  ```
- **响应数据**:
  ```json
  {
    "message": "员工状态更新成功"
  }
  ```

---

## 部门管理接口

### 6. 创建部门
- **接口路径**: `POST /enterprise-backend/user-management/departments`
- **功能描述**: 创建新部门
- **权限要求**: 企业管理员
- **请求参数**:
  ```json
  {
    "name": "技术部",
    "parent_id": null
  }
  ```
- **响应数据**:
  ```json
  {
    "message": "部门创建成功",
    "dept_id": 1
  }
  ```

### 7. 获取部门列表
- **接口路径**: `GET /enterprise-backend/user-management/departments`
- **功能描述**: 获取企业部门列表（树形结构）
- **权限要求**: 所有企业用户
- **请求参数**: 无
- **响应数据**:
  ```json
  [
    {
      "dept_id": 1,
      "name": "技术部",
      "parent_id": null,
      "member_count": 20,
      "children": [
        {
          "dept_id": 2,
          "name": "研发组",
          "parent_id": 1,
          "member_count": 10,
          "children": []
        }
      ]
    }
  ]
  ```

### 8. 获取部门详情
- **接口路径**: `GET /enterprise-backend/user-management/departments/{dept_id}`
- **功能描述**: 获取部门详细信息
- **权限要求**: 所有企业用户
- **请求参数**: 路径参数 `dept_id`
- **响应数据**:
  ```json
  {
    "dept_id": 1,
    "name": "技术部",
    "parent_id": null,
    "member_count": 20,
    "area_count": 3,
    "created_at": "2024-01-01T00:00:00"
  }
  ```

### 9. 更新部门信息
- **接口路径**: `PUT /enterprise-backend/user-management/departments/{dept_id}`
- **功能描述**: 更新部门信息
- **权限要求**: 企业管理员
- **请求参数**:
  ```json
  {
    "name": "技术研发部",
    "parent_id": null
  }
  ```
- **响应数据**:
  ```json
  {
    "message": "部门信息更新成功"
  }
  ```

### 10. 删除部门
- **接口路径**: `DELETE /enterprise-backend/user-management/departments/{dept_id}`
- **功能描述**: 删除部门
- **权限要求**: 企业管理员
- **请求参数**: 路径参数 `dept_id`
- **响应数据**:
  ```json
  {
    "message": "部门删除成功"
  }
  ```
- **错误响应**:
  - 400: 部门下有员工或子部门，无法删除

### 11. 获取部门成员
- **接口路径**: `GET /enterprise-backend/user-management/departments/{dept_id}/members`
- **功能描述**: 获取指定部门的成员列表
- **权限要求**: 所有企业用户
- **请求参数**: 路径参数 `dept_id`
- **响应数据**:
  ```json
  [
    {
      "user_id": 1,
      "name": "张三",
      "phone": "13800138000",
      "position": "工程师",
      "role_type": "staff",
      "status": true
    }
  ]
  ```

---

## 厂区管理接口

### 12. 创建厂区
- **接口路径**: `POST /enterprise-backend/user-management/areas`
- **功能描述**: 创建新厂区
- **权限要求**: 企业管理员
- **请求参数**:
  ```json
  {
    "area_name": "生产厂区A",
    "dept_id": 1
  }
  ```
- **响应数据**:
  ```json
  {
    "message": "厂区创建成功",
    "area_id": 1
  }
  ```

### 13. 获取厂区列表
- **接口路径**: `GET /enterprise-backend/user-management/areas`
- **功能描述**: 获取企业厂区列表
- **权限要求**: 所有企业用户
- **请求参数**:
  - `dept_id` (可选): 按部门筛选
- **响应数据**:
  ```json
  [
    {
      "area_id": 1,
      "area_name": "生产厂区A",
      "dept_name": "生产部",
      "enterprise_name": "XX企业"
    }
  ]
  ```

### 14. 获取厂区详情
- **接口路径**: `GET /enterprise-backend/user-management/areas/{area_id}`
- **功能描述**: 获取厂区详细信息
- **权限要求**: 所有企业用户
- **请求参数**: 路径参数 `area_id`
- **响应数据**:
  ```json
  {
    "area_id": 1,
    "area_name": "生产厂区A",
    "dept_id": 1,
    "dept_name": "生产部",
    "enterprise_id": 1,
    "enterprise_name": "XX企业",
    "created_at": "2024-01-01T00:00:00"
  }
  ```

### 15. 更新厂区信息
- **接口路径**: `PUT /enterprise-backend/user-management/areas/{area_id}`
- **功能描述**: 更新厂区信息
- **权限要求**: 企业管理员
- **请求参数**:
  ```json
  {
    "area_name": "生产厂区A（扩建）",
    "dept_id": 1
  }
  ```
- **响应数据**:
  ```json
  {
    "message": "厂区信息更新成功"
  }
  ```

### 16. 删除厂区
- **接口路径**: `DELETE /enterprise-backend/user-management/areas/{area_id}`
- **功能描述**: 删除厂区
- **权限要求**: 企业管理员
- **请求参数**: 路径参数 `area_id`
- **响应数据**:
  ```json
  {
    "message": "厂区删除成功"
  }
  ```
- **错误响应**:
  - 400: 厂区下有关联工单，无法删除

---

## 通用说明

### 认证方式
所有接口都需要在请求头中携带 Token:
```
Authorization: Bearer <access_token>
```

### 数据隔离
- 所有接口自动过滤当前用户的企业数据
- 跨企业访问返回 403 错误

### 分页参数
- `page`: 页码，从 1 开始
- `page_size`: 每页数量，默认 20，最大 100

### 错误响应格式
```json
{
  "detail": "错误描述信息"
}
```

