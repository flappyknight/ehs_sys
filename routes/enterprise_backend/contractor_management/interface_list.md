# 企业承包商管理模块 - 接口列表

## 承包商管理接口

### 1. 获取合作承包商列表
- **接口路径**: `GET /enterprise-backend/contractor-management/contractors`
- **功能描述**: 获取与当前企业有合作关系的承包商列表
- **权限要求**: 企业管理员、现场人员
- **请求参数**:
  - `company_type` (可选): 按公司类型筛选
  - `keyword` (可选): 搜索关键词
  - `page` (可选): 页码
  - `page_size` (可选): 每页数量
- **响应数据**:
  ```json
  {
    "total": 20,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "contractor_id": 1,
        "company_name": "XX建筑工程有限公司",
        "company_type": "建筑施工",
        "legal_person": "王五",
        "establish_date": "2020-01-01",
        "project_count": 3,
        "rating": 4.5
      }
    ]
  }
  ```

### 2. 获取承包商详情
- **接口路径**: `GET /enterprise-backend/contractor-management/contractors/{contractor_id}`
- **功能描述**: 获取承包商详细信息
- **权限要求**: 企业管理员、现场人员
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
    "contact_person": "赵六",
    "contact_phone": "13900139000",
    "project_count": 3,
    "staff_count": 20,
    "rating": 4.5,
    "created_at": "2024-01-01T00:00:00"
  }
  ```
- **错误响应**:
  - 403: 无合作关系，无权查看
  - 404: 承包商不存在

---

## 项目管理接口

### 3. 创建合作项目
- **接口路径**: `POST /enterprise-backend/contractor-management/projects`
- **功能描述**: 与承包商创建合作项目（支持新建承包商或选择已有承包商）
- **权限要求**: 企业管理员
- **请求参数（已有承包商）**:
  ```json
  {
    "contractor_id": 1,
    "project_name": "厂区A设备维护项目",
    "project_content": "负责厂区A的设备日常维护和检修",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }
  ```
- **请求参数（新建承包商）**:
  ```json
  {
    "contractor_info": {
      "company_name": "XX建筑工程有限公司",
      "company_type": "建筑施工",
      "legal_person": "王五",
      "establish_date": "2020-01-01",
      "business_license": "91110000XXXXXXXXXX"
    },
    "project_name": "厂区A设备维护项目",
    "project_content": "负责厂区A的设备日常维护和检修",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }
  ```
- **响应数据**:
  ```json
  {
    "message": "项目创建成功",
    "project_id": 1,
    "contractor_id": 1
  }
  ```

### 4. 获取项目列表
- **接口路径**: `GET /enterprise-backend/contractor-management/projects`
- **功能描述**: 获取企业的承包商项目列表
- **权限要求**: 企业管理员、现场人员
- **请求参数**:
  - `contractor_id` (可选): 按承包商筛选
  - `status` (可选): 按状态筛选 (active, completed, cancelled)
  - `keyword` (可选): 搜索关键词
  - `page` (可选): 页码
  - `page_size` (可选): 每页数量
- **响应数据**:
  ```json
  {
    "total": 10,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "project_id": 1,
        "project_name": "厂区A设备维护项目",
        "contractor_name": "XX建筑工程有限公司",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "status": "active",
        "plan_count": 5
      }
    ]
  }
  ```

### 5. 获取项目详情
- **接口路径**: `GET /enterprise-backend/contractor-management/projects/{project_id}`
- **功能描述**: 获取项目详细信息
- **权限要求**: 企业管理员、现场人员
- **请求参数**: 路径参数 `project_id`
- **响应数据**:
  ```json
  {
    "project_id": 1,
    "project_name": "厂区A设备维护项目",
    "project_content": "负责厂区A的设备日常维护和检修",
    "contractor_id": 1,
    "contractor_name": "XX建筑工程有限公司",
    "enterprise_id": 1,
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "status": "active",
    "plan_count": 5,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
  ```

### 6. 更新项目信息
- **接口路径**: `PUT /enterprise-backend/contractor-management/projects/{project_id}`
- **功能描述**: 更新项目信息
- **权限要求**: 企业管理员
- **请求参数**:
  ```json
  {
    "project_name": "厂区A设备维护项目（扩展）",
    "project_content": "负责厂区A和厂区B的设备日常维护和检修",
    "end_date": "2025-12-31"
  }
  ```
- **响应数据**:
  ```json
  {
    "message": "项目信息更新成功"
  }
  ```

### 7. 结束项目
- **接口路径**: `PUT /enterprise-backend/contractor-management/projects/{project_id}/complete`
- **功能描述**: 结束项目
- **权限要求**: 企业管理员
- **请求参数**:
  ```json
  {
    "end_date": "2024-06-30",
    "rating": 4.5,
    "comment": "合作愉快，工作质量高"
  }
  ```
- **响应数据**:
  ```json
  {
    "message": "项目已结束"
  }
  ```

### 8. 获取项目的作业计划列表
- **接口路径**: `GET /enterprise-backend/contractor-management/projects/{project_id}/plans`
- **功能描述**: 获取项目下的所有作业计划
- **权限要求**: 企业管理员、现场人员
- **请求参数**: 路径参数 `project_id`
- **响应数据**:
  ```json
  [
    {
      "plan_id": 1,
      "plan_name": "设备例行检查",
      "plan_date": "2024-01-15",
      "status": "approved",
      "participant_count": 5
    }
  ]
  ```

---

## 通用说明

### 认证方式
所有接口都需要在请求头中携带 Token:
```
Authorization: Bearer <access_token>
```

### 数据隔离
- 只能查看和管理与当前企业有合作关系的承包商
- 通过项目表关联实现数据隔离

### 错误响应格式
```json
{
  "detail": "错误描述信息"
}
```

