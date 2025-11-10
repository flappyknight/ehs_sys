# 合作申请管理模块 - 接口列表

## 合作邀请接口

### 1. 获取合作邀请列表
- **接口路径**: `GET /contractor-backend/cooperation-request/requests`
- **功能描述**: 获取合作邀请列表
- **权限要求**: 所有承包商用户
- **请求参数**: status, page, page_size
- **响应数据**: 分页的邀请列表

### 2. 获取邀请详情
- **接口路径**: `GET /contractor-backend/cooperation-request/requests/{request_id}`
- **功能描述**: 获取邀请详细信息
- **权限要求**: 所有承包商用户
- **响应数据**: 完整的邀请信息

### 3. 接受合作邀请
- **接口路径**: `POST /contractor-backend/cooperation-request/requests/{request_id}/accept`
- **功能描述**: 接受合作邀请
- **权限要求**: 承包商管理员
- **请求参数**:
  ```json
  {
    "comment": "同意合作",
    "contact_person": "张三",
    "contact_phone": "13800138000"
  }
  ```
- **响应数据**: `{"message": "已接受合作邀请", "project_id": 1}`

### 4. 拒绝合作邀请
- **接口路径**: `POST /contractor-backend/cooperation-request/requests/{request_id}/reject`
- **功能描述**: 拒绝合作邀请
- **权限要求**: 承包商管理员
- **请求参数**:
  ```json
  {
    "comment": "暂时无法合作"
  }
  ```
- **响应数据**: `{"message": "已拒绝合作邀请"}`

---

## 合作项目接口

### 5. 获取合作项目列表
- **接口路径**: `GET /contractor-backend/cooperation-request/projects`
- **功能描述**: 获取当前合作项目列表
- **权限要求**: 所有承包商用户
- **请求参数**: enterprise_id, status, page, page_size
- **响应数据**: 分页的项目列表

### 6. 获取项目详情
- **接口路径**: `GET /contractor-backend/cooperation-request/projects/{project_id}`
- **功能描述**: 获取项目详细信息
- **权限要求**: 所有承包商用户
- **响应数据**: 完整的项目信息

