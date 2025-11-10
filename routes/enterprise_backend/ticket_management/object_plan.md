# 企业工单管理模块 - 对象设计方案

## 1. 模块结构

```
ticket_management/
├── __init__.py          # 路由注册
├── ticket.py            # 工单管理接口
├── approval.py          # 工单审批接口
├── README.md
├── object_plan.md       # 本文件
└── interface_list.md
```

## 2. 核心对象模型

### 2.1 工单管理

#### TicketCreate
```python
class TicketCreate(BaseModel):
    apply_date: date
    applicant: int  # 申请人ID
    area_id: int
    working_content: str
    pre_st: datetime  # 预计开始时间
    pre_et: datetime  # 预计结束时间
    tools: Optional[str]
    worker: int  # 作业人员ID
    custodians: int  # 监护人ID
    danger: Optional[str]
    protection: Optional[str]
    hot_work: int  # 动火等级 0-3
    work_height_level: int  # 高处作业等级
    confined_space_id: Optional[int]
    temp_power_id: Optional[int]
    cross_work_group_id: Optional[int]
    signature: Optional[str]
```

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
    status: str
    created_at: str
```

### 2.2 工单审批

#### ApprovalRecord
```python
class ApprovalRecord(BaseModel):
    approval_id: int
    ticket_id: int
    approver_id: int
    approver_name: str
    approval_level: int
    status: str  # pending, approved, rejected
    comment: Optional[str]
    approval_time: Optional[datetime]
```

## 3. 业务逻辑设计

### 3.1 工单创建流程
1. 验证现场人员权限
2. 验证厂区归属
3. 验证作业人员和监护人
4. 创建工单记录
5. 初始化审批流程

### 3.2 工单审批流程
1. 验证审批人权限
2. 检查审批顺序
3. 更新审批记录
4. 如果全部通过，更新工单状态
5. 发送通知

## 4. 权限控制

| 操作 | 企业管理员 | 现场人员 | 普通员工 |
|------|-----------|---------|---------|
| 创建工单 | ✓ | ✓ | ✗ |
| 查看工单列表 | ✓ | ✓ | 相关 |
| 编辑工单 | ✓ | 创建人 | ✗ |
| 删除工单 | ✓ | ✗ | ✗ |
| 审批工单 | ✓ | ✗ | ✗ |

