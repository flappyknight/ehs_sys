# 承包商管理后台模块 - 接口列表汇总

## 模块概述

承包商管理后台模块包含3个子模块，每个子模块都有详细的接口文档。

## 子模块接口文档

### 1. 承包商人员管理 (staff_management)
- [详细接口文档](./staff_management/interface_list.md)
- 主要接口：
  - 员工管理（增删改查）
  - 资质管理
  - 培训记录管理

### 2. 工单浏览 (ticket_view)
- [详细接口文档](./ticket_view/interface_list.md)
- 主要接口：
  - 工单查看
  - 工单执行上报
  - 工单统计

### 3. 合作申请管理 (cooperation_request)
- [详细接口文档](./cooperation_request/interface_list.md)
- 主要接口：
  - 合作邀请查看和处理
  - 合作项目查看

## 接口前缀

所有承包商管理后台接口的前缀为：`/contractor-backend`

例如：
- `/contractor-backend/staff-management/staff`
- `/contractor-backend/ticket-view/tickets`
- `/contractor-backend/cooperation-request/requests`

## 认证方式

所有接口都需要在请求头中携带 Token:
```
Authorization: Bearer <access_token>
```

## 数据隔离

所有接口自动过滤当前用户的承包商数据，确保数据安全隔离。

