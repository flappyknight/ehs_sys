# 路由模块文档索引 (Routes Documentation Index)

## 快速导航

### 📚 总览文档
- [模块说明](./README.md) - 快速了解路由模块
- [路由结构说明](./ROUTES_STRUCTURE.md) - 完整的路由结构和开发指南
- [重构总结](./RESTRUCTURE_SUMMARY.md) - 本次重构的详细说明和统计
- [清理总结](./CLEANUP_SUMMARY.md) - 路由清理和迁移说明

---

## 🔐 认证模块
- **文件**: `auth.py`
- **前缀**: 无（直接挂载到根路径）
- **功能**: 用户登录、登出、Token管理

---

## 🛠️ 系统账户后台 (Admin)
- **前缀**: `/admin`
- **文档目录**: [admin/](./admin/)
  - [README.md](./admin/README.md) - 模块说明
  - [object_plan.md](./admin/object_plan.md) - 设计方案
  - [interface_list.md](./admin/interface_list.md) - 接口文档

**主要功能**:
- 系统用户管理
- 企业管理
- 承包商管理

---

## 🏢 企业管理后台 (Enterprise Backend)
- **前缀**: `/enterprise-backend`
- **文档目录**: [enterprise_backend/](./enterprise_backend/)
  - [README.md](./enterprise_backend/README.md) - 模块说明
  - [object_plan.md](./enterprise_backend/object_plan.md) - 设计方案
  - [interface_list.md](./enterprise_backend/interface_list.md) - 接口汇总

### 子模块

#### 1. 企业用户管理 (User Management)
- **前缀**: `/enterprise-backend/user-management`
- **文档**: [user_management/](./enterprise_backend/user_management/)
  - [README.md](./enterprise_backend/user_management/README.md)
  - [object_plan.md](./enterprise_backend/user_management/object_plan.md)
  - [interface_list.md](./enterprise_backend/user_management/interface_list.md)
- **功能**: 员工管理、部门管理、厂区管理

#### 2. 企业承包商管理 (Contractor Management)
- **前缀**: `/enterprise-backend/contractor-management`
- **文档**: [contractor_management/](./enterprise_backend/contractor_management/)
  - [README.md](./enterprise_backend/contractor_management/README.md)
  - [object_plan.md](./enterprise_backend/contractor_management/object_plan.md)
  - [interface_list.md](./enterprise_backend/contractor_management/interface_list.md)
- **功能**: 承包商列表、合作项目管理

#### 3. 企业工单管理 (Ticket Management)
- **前缀**: `/enterprise-backend/ticket-management`
- **文档**: [ticket_management/](./enterprise_backend/ticket_management/)
  - [README.md](./enterprise_backend/ticket_management/README.md)
  - [object_plan.md](./enterprise_backend/ticket_management/object_plan.md)
  - [interface_list.md](./enterprise_backend/ticket_management/interface_list.md)
- **功能**: 工单创建、审批、跟踪

#### 4. 企业作业流程管理 (Workflow Management)
- **前缀**: `/enterprise-backend/workflow-management`
- **文档**: [workflow_management/](./enterprise_backend/workflow_management/)
  - [README.md](./enterprise_backend/workflow_management/README.md)
  - [object_plan.md](./enterprise_backend/workflow_management/object_plan.md)
  - [interface_list.md](./enterprise_backend/workflow_management/interface_list.md)
- **功能**: 计划审批、人员管理、签到管理

#### 5. 企业权限管理 (Permission Management)
- **前缀**: `/enterprise-backend/permission-management`
- **文档**: [permission_management/](./enterprise_backend/permission_management/)
  - [README.md](./enterprise_backend/permission_management/README.md)
  - [object_plan.md](./enterprise_backend/permission_management/object_plan.md)
  - [interface_list.md](./enterprise_backend/permission_management/interface_list.md)
- **功能**: 角色管理、权限分配

---

## 🏗️ 承包商管理后台 (Contractor Backend)
- **前缀**: `/contractor-backend`
- **文档目录**: [contractor_backend/](./contractor_backend/)
  - [README.md](./contractor_backend/README.md) - 模块说明
  - [object_plan.md](./contractor_backend/object_plan.md) - 设计方案
  - [interface_list.md](./contractor_backend/interface_list.md) - 接口汇总

### 子模块

#### 1. 承包商人员管理 (Staff Management)
- **前缀**: `/contractor-backend/staff-management`
- **文档**: [staff_management/](./contractor_backend/staff_management/)
  - [README.md](./contractor_backend/staff_management/README.md)
  - [object_plan.md](./contractor_backend/staff_management/object_plan.md)
  - [interface_list.md](./contractor_backend/staff_management/interface_list.md)
- **功能**: 员工管理、资质管理

#### 2. 工单浏览 (Ticket View)
- **前缀**: `/contractor-backend/ticket-view`
- **文档**: [ticket_view/](./contractor_backend/ticket_view/)
  - [README.md](./contractor_backend/ticket_view/README.md)
  - [object_plan.md](./contractor_backend/ticket_view/object_plan.md)
  - [interface_list.md](./contractor_backend/ticket_view/interface_list.md)
- **功能**: 工单查看、执行上报

#### 3. 合作申请管理 (Cooperation Request)
- **前缀**: `/contractor-backend/cooperation-request`
- **文档**: [cooperation_request/](./contractor_backend/cooperation_request/)
  - [README.md](./contractor_backend/cooperation_request/README.md)
  - [object_plan.md](./contractor_backend/cooperation_request/object_plan.md)
  - [interface_list.md](./contractor_backend/cooperation_request/interface_list.md)
- **功能**: 合作邀请处理、项目查看

---

## 📋 工单模块 (Ticket)
- **前缀**: `/tickets`
- **文档目录**: [ticket/](./ticket/)
  - [README.md](./ticket/README.md) - 模块说明
  - [CHANGELOG.md](./ticket/CHANGELOG.md) - 变更日志
  - [object_plan.md](./ticket/object_plan.md) - 设计方案
  - [interface_list.md](./ticket/interface_list.md) - 接口文档

**主要功能**:
- 工单创建
- 工单查看（根据权限自动过滤）
- 工单更新
- 工单删除

---

## 🔄 工单流程模块 (Workflow)
- **前缀**: `/workflow`
- **文档目录**: [workflow/](./workflow/)
  - [README.md](./workflow/README.md) - 模块说明
  - [object_plan.md](./workflow/object_plan.md) - 设计方案
  - [interface_list.md](./workflow/interface_list.md) - 接口文档

**主要功能**:
- 流程定义
- 流程实例管理
- 审批处理

---

## 📖 文档说明

### 文档类型

#### README.md
- **内容**: 模块概述、主要功能、权限要求
- **适合**: 快速了解模块功能

#### object_plan.md
- **内容**: 详细的设计方案、数据模型、业务逻辑
- **适合**: 开发人员深入了解模块设计

#### interface_list.md
- **内容**: 完整的 API 接口文档
- **适合**: 前端开发、接口测试、API 集成

---

## 🔍 快速查找

### 按功能查找

| 功能 | 模块 | 文档链接 |
|------|------|---------|
| 用户登录 | auth | [auth.py](./auth.py) |
| 员工管理 | enterprise_backend/user_management | [文档](./enterprise_backend/user_management/) |
| 承包商管理 | enterprise_backend/contractor_management | [文档](./enterprise_backend/contractor_management/) |
| 工单管理 | ticket | [文档](./ticket/) |
| 工单审批 | workflow | [文档](./workflow/) |
| 人员签到 | enterprise_backend/workflow_management | [文档](./enterprise_backend/workflow_management/) |
| 资质管理 | contractor_backend/staff_management | [文档](./contractor_backend/staff_management/) |

### 按用户类型查找

| 用户类型 | 可用模块 |
|---------|---------|
| 系统管理员 | admin, 所有模块 |
| 企业管理员 | enterprise_backend (全部子模块) |
| 企业现场人员 | enterprise_backend (部分功能) |
| 承包商管理员 | contractor_backend (全部子模块) |
| 承包商作业人员 | contractor_backend (部分功能) |

---

## 🚀 开发指南

### 查看接口文档
1. 找到对应的模块目录
2. 打开 `interface_list.md`
3. 查看接口路径、参数和响应

### 了解设计方案
1. 找到对应的模块目录
2. 打开 `object_plan.md`
3. 查看数据模型和业务逻辑

### 快速上手
1. 阅读 [ROUTES_STRUCTURE.md](./ROUTES_STRUCTURE.md)
2. 查看 [RESTRUCTURE_SUMMARY.md](./RESTRUCTURE_SUMMARY.md)
3. 根据需要查看具体模块文档

---

## 📝 更新日志

- **2024-11-10**: 完成路由重构，创建完整文档体系
- **版本**: v1.0

---

## 📞 联系方式

如有问题或建议，请联系项目负责人。
