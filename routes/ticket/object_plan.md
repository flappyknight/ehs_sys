# 工单模块 - 对象设计方案

## 1. 模块概述

工单模块是系统的核心模块之一，负责作业工单的全生命周期管理。

## 2. 模块结构

```
ticket/
├── __init__.py          # 路由注册
├── ticket.py            # 工单管理接口
├── README.md            # 模块说明
├── CHANGELOG.md         # 变更日志
├── object_plan.md       # 本文件
└── interface_list.md    # 接口文档
```

## 3. 核心对象模型

### 3.1 工单创建

#### TicketCreate
```python
class TicketCreate(BaseModel):
    apply_date: date
    applicant: int  # 申请人ID（企业用户）
    area_id: int  # 厂区ID
    working_content: str  # 作业内容
    pre_st: datetime  # 预计开始时间
    pre_et: datetime  # 预计结束时间
    tools: Optional[str]  # 使用工具
    worker: int  # 作业人员ID（承包商用户）
    custodians: int  # 监护人ID（企业用户）
    danger: Optional[str]  # 危险因素
    protection: Optional[str]  # 防护措施
    hot_work: int  # 动火等级 0-3
    work_height_level: int  # 高处作业等级
    confined_space_id: Optional[int]  # 受限空间ID
    temp_power_id: Optional[int]  # 临时用电ID
    cross_work_group_id: Optional[int]  # 交叉作业组ID
    signature: Optional[str]  # 签名
```

### 3.2 工单列表

#### TicketListItem
```python
class TicketListItem(BaseModel):
    ticket_id: int
    apply_date: date
    applicant_name: str
    area_name: str
    working_content: str
    pre_st: str
    pre_et: str
    worker_name: str
    custodian_name: str
    hot_work: int
    work_height_level: int
    status: str  # pending, approved, rejected, executing, completed
    created_at: str
```

### 3.3 工单详情

#### TicketDetail
```python
class TicketDetail(BaseModel):
    ticket_id: int
    apply_date: date
    applicant: int
    applicant_name: str
    area_id: int
    area_name: str
    working_content: str
    pre_st: str
    pre_et: str
    tools: Optional[str]
    worker: int
    worker_name: str
    custodians: int
    custodian_name: str
    danger: Optional[str]
    protection: Optional[str]
    hot_work: int
    work_height_level: int
    confined_space_id: Optional[int]
    temp_power_id: Optional[int]
    cross_work_group_id: Optional[int]
    signature: Optional[str]
    status: str
    created_at: str
    updated_at: str
```

## 4. 业务逻辑设计

### 4.1 工单创建流程
1. 验证申请人权限（企业现场人员或管理员）
2. 验证厂区归属（必须属于申请人企业）
3. 验证作业人员（必须是承包商用户）
4. 验证监护人（必须是企业用户）
5. 创建工单记录
6. 初始化工单状态为 pending

### 4.2 工单查看流程
1. 根据用户类型过滤工单：
   - 企业用户：只能看到自己企业的工单
   - 承包商用户：只能看到分配给自己员工的工单
   - 管理员：可以看到所有工单
2. 支持多种筛选条件
3. 分页返回结果

### 4.3 工单更新流程
1. 验证权限（企业管理员或创建人）
2. 验证工单归属
3. 更新工单信息
4. 记录更新日志

### 4.4 工单删除流程
1. 验证企业管理员权限
2. 验证工单归属
3. 检查工单状态（执行中的不能删除）
4. 执行删除

## 5. 权限控制

### 5.1 权限矩阵

| 操作 | 系统管理员 | 企业管理员 | 现场人员 | 承包商管理员 | 作业人员 |
|------|-----------|-----------|---------|-------------|---------|
| 创建工单 | ✓ | ✓ | ✓ | ✗ | ✗ |
| 查看工单列表 | ✓ | ✓ | ✓ | ✓ | 分配的 |
| 查看工单详情 | ✓ | ✓ | ✓ | ✓ | 分配的 |
| 编辑工单 | ✓ | ✓ | 创建人 | ✗ | ✗ |
| 删除工单 | ✓ | ✓ | ✗ | ✗ | ✗ |

### 5.2 数据权限
- 企业用户只能访问自己企业的工单
- 承包商用户只能访问分配给自己员工的工单
- 通过 area_id 关联实现企业数据隔离

## 6. 数据验证

### 6.1 必填字段验证
- 申请日期、申请人、厂区、作业内容、预计时间、作业人员、监护人

### 6.2 业务规则验证
- 预计开始时间不能晚于结束时间
- 作业人员和监护人不能是同一人
- 厂区必须属于申请人企业
- 作业人员必须是承包商用户
- 监护人必须是企业用户

### 6.3 状态验证
- 只有 pending 状态的工单可以编辑
- 只有 pending 状态的工单可以删除
- 状态流转：pending → approved → executing → completed

## 7. 数据库设计

### 7.1 涉及的表
- `ticket` - 工单表
- `area` - 厂区表
- `enterprise_user` - 企业用户表
- `contractor_user` - 承包商用户表

### 7.2 关键字段
- `ticket_id`: 主键，自增
- `area_id`: 外键，关联厂区
- `applicant`: 外键，关联企业用户
- `worker`: 外键，关联承包商用户
- `custodians`: 外键，关联企业用户
- `status`: 工单状态
- `created_at`, `updated_at`: 时间戳

## 8. 性能优化

### 8.1 索引优化
- area_id 索引（按厂区查询）
- applicant 索引（按申请人查询）
- worker 索引（按作业人员查询）
- apply_date 索引（按日期查询）
- status 索引（按状态查询）

### 8.2 查询优化
- 使用 JOIN 减少查询次数
- 分页查询避免大数据集
- 缓存常用数据（用户名、厂区名）

## 9. 扩展功能

### 9.1 工单审批
- 多级审批流程
- 审批记录跟踪
- 审批通知

### 9.2 工单执行跟踪
- 执行状态更新
- 执行照片上传
- 执行进度跟踪

### 9.3 工单统计分析
- 按时间统计
- 按厂区统计
- 按作业类型统计
- 完成率分析

