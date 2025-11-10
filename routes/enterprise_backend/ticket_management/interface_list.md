# 企业工单管理模块 - 接口列表

## 工单管理接口

### 1. 创建工单
- **接口路径**: `POST /enterprise-backend/ticket-management/tickets`
- **功能描述**: 创建作业工单
- **权限要求**: 企业管理员、现场人员
- **请求参数**: 参考 TicketCreate 对象
- **响应数据**: `{"message": "工单创建成功", "ticket_id": 1}`

### 2. 获取工单列表
- **接口路径**: `GET /enterprise-backend/ticket-management/tickets`
- **功能描述**: 获取工单列表
- **权限要求**: 所有企业用户
- **请求参数**: area_id, hot_work, start_date, end_date, status, page, page_size
- **响应数据**: 分页的工单列表

### 3. 获取工单详情
- **接口路径**: `GET /enterprise-backend/ticket-management/tickets/{ticket_id}`
- **功能描述**: 获取工单详细信息
- **权限要求**: 所有企业用户
- **响应数据**: 完整的工单信息

### 4. 更新工单
- **接口路径**: `PUT /enterprise-backend/ticket-management/tickets/{ticket_id}`
- **功能描述**: 更新工单信息
- **权限要求**: 企业管理员、创建人
- **响应数据**: `{"message": "工单更新成功"}`

### 5. 删除工单
- **接口路径**: `DELETE /enterprise-backend/ticket-management/tickets/{ticket_id}`
- **功能描述**: 删除工单
- **权限要求**: 企业管理员
- **响应数据**: `{"message": "工单删除成功"}`

---

## 工单审批接口

### 6. 提交工单审批
- **接口路径**: `POST /enterprise-backend/ticket-management/tickets/{ticket_id}/submit`
- **功能描述**: 提交工单进入审批流程
- **权限要求**: 创建人
- **响应数据**: `{"message": "工单已提交审批"}`

### 7. 审批工单
- **接口路径**: `POST /enterprise-backend/ticket-management/tickets/{ticket_id}/approve`
- **功能描述**: 审批工单
- **权限要求**: 审批人
- **请求参数**: `{"status": "approved", "comment": "同意"}`
- **响应数据**: `{"message": "审批成功"}`

### 8. 获取审批记录
- **接口路径**: `GET /enterprise-backend/ticket-management/tickets/{ticket_id}/approvals`
- **功能描述**: 获取工单的审批记录
- **权限要求**: 所有企业用户
- **响应数据**: 审批记录列表

