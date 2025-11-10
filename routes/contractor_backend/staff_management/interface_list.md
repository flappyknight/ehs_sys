# 承包商人员管理模块 - 接口列表

## 员工管理接口

### 1. 添加承包商员工
- **接口路径**: `POST /contractor-backend/staff-management/staff`
- **功能描述**: 添加新的承包商员工
- **权限要求**: 承包商管理员
- **请求参数**:
  ```json
  {
    "name": "张三",
    "phone": "13800138000",
    "id_number": "110101199001011234",
    "work_type": "电工",
    "personal_photo": "http://example.com/photo.jpg",
    "role_type": "worker",
    "create_account": true
  }
  ```
- **响应数据**: `{"message": "员工添加成功", "user_id": 1}`

### 2. 获取员工列表
- **接口路径**: `GET /contractor-backend/staff-management/staff`
- **功能描述**: 获取承包商员工列表
- **权限要求**: 承包商管理员
- **请求参数**: work_type, status, keyword, page, page_size
- **响应数据**: 分页的员工列表

### 3. 获取员工详情
- **接口路径**: `GET /contractor-backend/staff-management/staff/{user_id}`
- **功能描述**: 获取员工详细信息
- **权限要求**: 承包商管理员、本人
- **响应数据**: 完整的员工信息

### 4. 更新员工信息
- **接口路径**: `PUT /contractor-backend/staff-management/staff/{user_id}`
- **功能描述**: 更新员工信息
- **权限要求**: 承包商管理员、本人（部分字段）
- **响应数据**: `{"message": "员工信息更新成功"}`

### 5. 禁用/启用员工
- **接口路径**: `PUT /contractor-backend/staff-management/staff/{user_id}/status`
- **功能描述**: 禁用或启用员工账户
- **权限要求**: 承包商管理员
- **响应数据**: `{"message": "员工状态更新成功"}`

---

## 资质管理接口

### 6. 上传资质证书
- **接口路径**: `POST /contractor-backend/staff-management/staff/{user_id}/qualifications`
- **功能描述**: 上传员工资质证书
- **权限要求**: 承包商管理员、本人
- **请求参数**: 资质类型、证书编号、有效期、证书图片
- **响应数据**: `{"message": "资质上传成功"}`

### 7. 获取资质列表
- **接口路径**: `GET /contractor-backend/staff-management/staff/{user_id}/qualifications`
- **功能描述**: 获取员工的资质列表
- **权限要求**: 承包商管理员、本人
- **响应数据**: 资质列表

### 8. 删除资质
- **接口路径**: `DELETE /contractor-backend/staff-management/staff/{user_id}/qualifications/{qualification_id}`
- **功能描述**: 删除资质证书
- **权限要求**: 承包商管理员
- **响应数据**: `{"message": "资质删除成功"}`

