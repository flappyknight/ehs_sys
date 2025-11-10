# 工单流程模块 - 接口列表

## 流程定义接口

### 1. 创建流程定义
- **接口路径**: `POST /workflow/definitions`
- **功能描述**: 创建流程定义
- **权限要求**: 系统管理员、企业管理员
- **请求参数**: 流程名称、类型、节点配置
- **响应数据**: `{"message": "流程定义创建成功", "workflow_id": 1}`

### 2. 获取流程定义列表
- **接口路径**: `GET /workflow/definitions`
- **功能描述**: 获取流程定义列表
- **权限要求**: 需要认证
- **响应数据**: 流程定义列表

### 3. 获取流程定义详情
- **接口路径**: `GET /workflow/definitions/{workflow_id}`
- **功能描述**: 获取流程定义详情
- **权限要求**: 需要认证
- **响应数据**: 完整的流程定义信息

---

## 流程实例接口

### 4. 启动流程实例
- **接口路径**: `POST /workflow/instances`
- **功能描述**: 启动流程实例
- **权限要求**: 需要认证
- **请求参数**: `{"workflow_id": 1, "business_id": 1, "business_type": "ticket"}`
- **响应数据**: `{"message": "流程已启动", "instance_id": 1}`

### 5. 获取流程实例列表
- **接口路径**: `GET /workflow/instances`
- **功能描述**: 获取流程实例列表
- **权限要求**: 需要认证
- **请求参数**: business_type, status, page, page_size
- **响应数据**: 分页的流程实例列表

### 6. 获取流程实例详情
- **接口路径**: `GET /workflow/instances/{instance_id}`
- **功能描述**: 获取流程实例详情
- **权限要求**: 需要认证
- **响应数据**: 完整的流程实例信息和审批记录

---

## 审批处理接口

### 7. 审批流程
- **接口路径**: `POST /workflow/instances/{instance_id}/approve`
- **功能描述**: 审批流程
- **权限要求**: 审批人
- **请求参数**: `{"status": "approved", "comment": "同意"}`
- **响应数据**: `{"message": "审批成功"}`

### 8. 获取待审批列表
- **接口路径**: `GET /workflow/approvals/pending`
- **功能描述**: 获取当前用户的待审批列表
- **权限要求**: 需要认证
- **响应数据**: 待审批流程列表

### 9. 获取审批历史
- **接口路径**: `GET /workflow/approvals/history`
- **功能描述**: 获取审批历史记录
- **权限要求**: 需要认证
- **请求参数**: start_date, end_date, page, page_size
- **响应数据**: 分页的审批历史记录

---

## 通用说明

### 认证方式
所有接口都需要在请求头中携带 Token:
```
Authorization: Bearer <access_token>
```

### 流程类型
- `ticket_approval`: 工单审批流程
- `plan_approval`: 计划审批流程

### 节点类型
- `start`: 开始节点
- `approval`: 审批节点
- `end`: 结束节点

### 流程状态
- `pending`: 待审批
- `approved`: 已通过
- `rejected`: 已拒绝
- `cancelled`: 已取消

