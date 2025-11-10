# 工单浏览模块 - 接口列表

## 工单查看接口

### 1. 获取工单列表
- **接口路径**: `GET /contractor-backend/ticket-view/tickets`
- **功能描述**: 获取相关工单列表
- **权限要求**: 所有承包商用户
- **请求参数**: status, start_date, end_date, assigned_to_me, page, page_size
- **响应数据**: 分页的工单列表

### 2. 获取工单详情
- **接口路径**: `GET /contractor-backend/ticket-view/tickets/{ticket_id}`
- **功能描述**: 获取工单详细信息
- **权限要求**: 所有承包商用户（相关工单）
- **响应数据**: 完整的工单信息

---

## 工单执行接口

### 3. 上报执行情况
- **接口路径**: `POST /contractor-backend/ticket-view/tickets/{ticket_id}/report`
- **功能描述**: 上报工单执行情况
- **权限要求**: 分配的作业人员
- **请求参数**:
  ```json
  {
    "execution_status": "in_progress",
    "progress": 50,
    "photos": ["url1", "url2"],
    "comment": "已完成50%"
  }
  ```
- **响应数据**: `{"message": "上报成功"}`

### 4. 完成工单
- **接口路径**: `POST /contractor-backend/ticket-view/tickets/{ticket_id}/complete`
- **功能描述**: 标记工单为已完成
- **权限要求**: 分配的作业人员
- **请求参数**:
  ```json
  {
    "completion_photos": ["url1", "url2"],
    "completion_comment": "作业已完成"
  }
  ```
- **响应数据**: `{"message": "工单已完成"}`

---

## 工单统计接口

### 5. 获取工单统计
- **接口路径**: `GET /contractor-backend/ticket-view/statistics`
- **功能描述**: 获取工单统计数据
- **权限要求**: 承包商管理员
- **请求参数**: start_date, end_date
- **响应数据**:
  ```json
  {
    "total": 100,
    "completed": 80,
    "in_progress": 15,
    "pending": 5,
    "completion_rate": 0.8
  }
  ```

