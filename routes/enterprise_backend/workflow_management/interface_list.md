# 企业作业流程管理模块 - 接口列表

## 计划管理接口

### 1. 获取作业计划列表
- **接口路径**: `GET /enterprise-backend/workflow-management/plans`
- **功能描述**: 获取企业的作业计划列表
- **权限要求**: 企业管理员、现场人员
- **请求参数**: project_id, contractor_id, status, start_date, end_date, page, page_size
- **响应数据**: 分页的计划列表

### 2. 获取计划详情
- **接口路径**: `GET /enterprise-backend/workflow-management/plans/{plan_id}`
- **功能描述**: 获取计划详细信息
- **权限要求**: 企业管理员、现场人员
- **响应数据**: 完整的计划信息

### 3. 审批计划
- **接口路径**: `POST /enterprise-backend/workflow-management/plans/{plan_id}/approve`
- **功能描述**: 审批作业计划
- **权限要求**: 企业管理员
- **请求参数**: `{"status": "approved", "comment": "同意执行"}`
- **响应数据**: `{"message": "审批成功"}`

---

## 参与人员管理接口

### 4. 获取计划参与人员
- **接口路径**: `GET /enterprise-backend/workflow-management/plans/{plan_id}/participants`
- **功能描述**: 获取计划的参与人员列表
- **权限要求**: 企业管理员、现场人员
- **响应数据**: 参与人员列表（包含签到状态）

### 5. 人员签到
- **接口路径**: `POST /enterprise-backend/workflow-management/plans/{plan_id}/register`
- **功能描述**: 参与人员签到
- **权限要求**: 企业管理员、现场人员
- **请求参数**: `{"user_id": 1}`
- **响应数据**: `{"message": "签到成功"}`

### 6. 获取签到统计
- **接口路径**: `GET /enterprise-backend/workflow-management/plans/{plan_id}/register-stats`
- **功能描述**: 获取计划的签到统计
- **权限要求**: 企业管理员、现场人员
- **响应数据**: `{"total": 10, "registered": 8, "rate": 0.8}`

