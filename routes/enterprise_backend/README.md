# 企业管理后台模块 (Enterprise Backend Module)

## 模块概述

企业管理后台模块是为企业用户提供的管理平台，包括用户管理、承包商管理、工单管理、作业流程管理和权限管理等核心功能。

## 子模块结构

```
enterprise_backend/
├── user_management/         # 企业用户管理
├── contractor_management/   # 企业承包商管理
├── ticket_management/       # 企业工单管理
├── workflow_management/     # 企业作业流程管理
└── permission_management/   # 企业权限管理
```

## 主要功能

### 1. 企业用户管理 (user_management)
- 企业员工的增删改查
- 部门管理
- 厂区管理
- 员工角色分配

### 2. 企业承包商管理 (contractor_management)
- 查看合作承包商列表
- 创建与承包商的合作项目
- 管理承包商项目
- 承包商评价

### 3. 企业工单管理 (ticket_management)
- 创建作业工单
- 查看工单列表
- 审批工单
- 工单状态跟踪

### 4. 企业作业流程管理 (workflow_management)
- 查看作业计划
- 审批作业计划
- 查看计划参与人员
- 人员签到管理

### 5. 企业权限管理 (permission_management)
- 角色定义
- 权限分配
- 审批流程配置
- 权限审计

## 权限要求

- 基础权限：企业用户 (UserType.enterprise)
- 管理权限：企业管理员 (role_type = "manager")
- 部分接口对现场人员开放 (role_type = "site_staff")

## 技术栈

- FastAPI
- SQLModel
- JWT 认证
- 数据权限隔离

## 相关文档

- [接口列表](./interface_list.md) - 详细的 API 接口文档
- [对象设计方案](./object_plan.md) - 模块设计方案和数据模型

## 子模块文档

- [企业用户管理](./user_management/README.md)
- [企业承包商管理](./contractor_management/README.md)
- [企业工单管理](./ticket_management/README.md)
- [企业作业流程管理](./workflow_management/README.md)
- [企业权限管理](./permission_management/README.md)

