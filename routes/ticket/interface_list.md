# 工单模块 - 接口列表

## 工单管理接口

### 1. 创建工单
- **接口路径**: `POST /tickets`
- **功能描述**: 创建作业工单
- **权限要求**: 企业管理员、现场人员
- **请求参数**:
  ```json
  {
    "apply_date": "2024-01-15",
    "applicant": 1,
    "area_id": 1,
    "working_content": "设备维护作业",
    "pre_st": "2024-01-15T08:00:00",
    "pre_et": "2024-01-15T17:00:00",
    "tools": "扳手、螺丝刀",
    "worker": 10,
    "custodians": 2,
    "danger": "高处作业、用电",
    "protection": "安全带、绝缘手套",
    "hot_work": 0,
    "work_height_level": 2,
    "confined_space_id": null,
    "temp_power_id": null,
    "cross_work_group_id": null,
    "signature": "data:image/png;base64,..."
  }
  ```
- **响应数据**:
  ```json
  {
    "message": "工单创建成功",
    "ticket_id": 1
  }
  ```
- **错误响应**:
  - 400: 参数验证失败
  - 403: 权限不足或数据归属错误

### 2. 获取工单列表
- **接口路径**: `GET /tickets`
- **功能描述**: 获取工单列表（根据用户权限自动过滤）
- **权限要求**: 需要认证
- **请求参数**:
  - `area_id` (可选): 按厂区筛选
  - `hot_work` (可选): 按动火等级筛选 (0-3)
  - `start_date` (可选): 开始日期
  - `end_date` (可选): 结束日期
  - `status` (可选): 按状态筛选
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
        "ticket_id": 1,
        "apply_date": "2024-01-15",
        "applicant_name": "张三",
        "area_name": "生产厂区A",
        "working_content": "设备维护作业",
        "pre_st": "2024-01-15T08:00:00",
        "pre_et": "2024-01-15T17:00:00",
        "worker_name": "李四",
        "custodian_name": "王五",
        "hot_work": 0,
        "work_height_level": 2,
        "status": "pending",
        "created_at": "2024-01-14T10:00:00"
      }
    ]
  }
  ```

### 3. 获取工单详情
- **接口路径**: `GET /tickets/{ticket_id}`
- **功能描述**: 获取工单详细信息
- **权限要求**: 需要认证
- **请求参数**: 路径参数 `ticket_id`
- **响应数据**:
  ```json
  {
    "ticket_id": 1,
    "apply_date": "2024-01-15",
    "applicant": 1,
    "applicant_name": "张三",
    "area_id": 1,
    "area_name": "生产厂区A",
    "working_content": "设备维护作业",
    "pre_st": "2024-01-15T08:00:00",
    "pre_et": "2024-01-15T17:00:00",
    "tools": "扳手、螺丝刀",
    "worker": 10,
    "worker_name": "李四",
    "custodians": 2,
    "custodian_name": "王五",
    "danger": "高处作业、用电",
    "protection": "安全带、绝缘手套",
    "hot_work": 0,
    "work_height_level": 2,
    "confined_space_id": null,
    "temp_power_id": null,
    "cross_work_group_id": null,
    "signature": "data:image/png;base64,...",
    "status": "pending",
    "created_at": "2024-01-14T10:00:00",
    "updated_at": "2024-01-14T10:00:00"
  }
  ```
- **错误响应**:
  - 403: 无权访问该工单
  - 404: 工单不存在

### 4. 更新工单
- **接口路径**: `PUT /tickets/{ticket_id}`
- **功能描述**: 更新工单信息
- **权限要求**: 企业管理员、创建人
- **请求参数**:
  ```json
  {
    "working_content": "设备维护作业（更新）",
    "pre_st": "2024-01-15T09:00:00",
    "pre_et": "2024-01-15T18:00:00",
    "tools": "扳手、螺丝刀、电钻"
  }
  ```
- **响应数据**:
  ```json
  {
    "message": "工单更新成功"
  }
  ```
- **错误响应**:
  - 400: 工单状态不允许编辑
  - 403: 权限不足
  - 404: 工单不存在

### 5. 删除工单
- **接口路径**: `DELETE /tickets/{ticket_id}`
- **功能描述**: 删除工单
- **权限要求**: 企业管理员
- **请求参数**: 路径参数 `ticket_id`
- **响应数据**:
  ```json
  {
    "message": "工单删除成功"
  }
  ```
- **错误响应**:
  - 400: 工单状态不允许删除
  - 403: 权限不足
  - 404: 工单不存在

---

## 通用说明

### 认证方式
所有接口都需要在请求头中携带 Token:
```
Authorization: Bearer <access_token>
```

### 数据隔离规则
- **企业用户**: 只能访问自己企业厂区的工单
- **承包商用户**: 只能访问分配给自己员工的工单
- **系统管理员**: 可以访问所有工单

### 工单状态说明
- `pending`: 待审批
- `approved`: 已审批
- `rejected`: 已拒绝
- `executing`: 执行中
- `completed`: 已完成
- `cancelled`: 已取消

### 动火等级说明
- `0`: 无动火作业
- `1`: 一级动火（一般动火）
- `2`: 二级动火（较高风险）
- `3`: 三级动火（高风险特殊动火）

### 高处作业等级说明
- `0`: 无高处作业
- `1`: 2-5米
- `2`: 5-15米
- `3`: 15-30米
- `4`: 30米以上

### 分页参数
- `page`: 页码，从 1 开始
- `page_size`: 每页数量，默认 20，最大 100

### 错误响应格式
```json
{
  "detail": "错误描述信息"
}
```

### 常见错误码
- 400: 请求参数错误或业务规则验证失败
- 401: 未认证或认证失败
- 403: 权限不足或跨企业/承包商访问
- 404: 资源不存在
- 500: 服务器内部错误

