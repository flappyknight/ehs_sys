# 企业管理后台模块 - 接口列表汇总

## 模块概述

企业管理后台模块包含5个子模块，每个子模块都有详细的接口文档。

## 子模块接口文档

### 1. 企业用户管理 (user_management)
- [详细接口文档](./user_management/interface_list.md)
- 主要接口：
  - 员工管理（增删改查）
  - 部门管理（增删改查）
  - 厂区管理（增删改查）

### 2. 企业承包商管理 (contractor_management)
- [详细接口文档](./contractor_management/interface_list.md)
- 主要接口：
  - 承包商列表查看
  - 合作项目创建和管理
  - 项目计划查看

### 3. 企业工单管理 (ticket_management)
- [详细接口文档](./ticket_management/interface_list.md)
- 主要接口：
  - 工单创建和管理
  - 工单审批
  - 工单状态跟踪

### 4. 企业作业流程管理 (workflow_management)
- [详细接口文档](./workflow_management/interface_list.md)
- 主要接口：
  - 作业计划查看和审批
  - 参与人员管理
  - 人员签到管理

### 5. 企业权限管理 (permission_management)
- [详细接口文档](./permission_management/interface_list.md)
- 主要接口：
  - 角色管理
  - 权限分配
  - 审批流程配置

## 接口前缀

所有企业管理后台接口的前缀为：`/enterprise-backend`

例如：
- `/enterprise-backend/user-management/users`
- `/enterprise-backend/contractor-management/contractors`
- `/enterprise-backend/ticket-management/tickets`
- `/enterprise-backend/workflow-management/plans`
- `/enterprise-backend/permission-management/roles`

## 认证方式

所有接口都需要在请求头中携带 Token:
```
Authorization: Bearer <access_token>
```

## 数据隔离

所有接口自动过滤当前用户的企业数据，确保数据安全隔离。

