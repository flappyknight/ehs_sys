# 承包商管理后台模块 (Contractor Backend Module)

## 模块概述

承包商管理后台模块是为承包商用户提供的管理平台，包括人员管理、工单浏览和合作申请管理等功能。

## 子模块结构

```
contractor_backend/
├── staff_management/        # 承包商人员管理
├── ticket_view/             # 工单浏览
└── cooperation_request/     # 合作申请管理
```

## 主要功能

### 1. 承包商人员管理 (staff_management)
- 承包商员工的增删改查
- 员工资质管理
- 员工培训记录

### 2. 工单浏览 (ticket_view)
- 查看相关工单
- 工单执行情况上报
- 工单完成确认

### 3. 合作申请管理 (cooperation_request)
- 查看合作邀请
- 接受/拒绝合作
- 合作项目查看

## 权限要求

- 基础权限：承包商用户 (UserType.contractor)
- 管理权限：承包商管理员 (role_type = "approver")
- 部分接口对作业人员开放 (role_type = "worker")

## 技术栈

- FastAPI
- SQLModel
- JWT 认证
- 数据权限隔离

## 相关文档

- [接口列表](./interface_list.md) - 详细的 API 接口文档
- [对象设计方案](./object_plan.md) - 模块设计方案和数据模型

## 子模块文档

- [承包商人员管理](./staff_management/README.md)
- [工单浏览](./ticket_view/README.md)
- [合作申请管理](./cooperation_request/README.md)

