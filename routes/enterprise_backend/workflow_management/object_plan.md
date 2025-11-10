# 企业作业流程管理模块 - 对象设计方案

## 1. 模块结构

```
workflow_management/
├── __init__.py          # 路由注册
├── plan.py              # 计划管理接口
├── participant.py       # 参与人员管理接口
├── README.md
├── object_plan.md       # 本文件
└── interface_list.md
```

## 2. 核心对象模型

### 2.1 计划管理

#### PlanListItem
```python
class PlanListItem(BaseModel):
    plan_id: int
    plan_name: str
    project_name: str
    contractor_name: str
    plan_date: date
    status: str  # draft, pending, approved, rejected, executing, completed
    participant_count: int
    registered_count: int
```

#### PlanDetail
```python
class PlanDetail(BaseModel):
    plan_id: int
    plan_name: str
    plan_content: str
    project_id: int
    project_name: str
    contractor_id: int
    contractor_name: str
    plan_date: date
    status: str
    participant_count: int
    registered_count: int
    created_at: datetime
    updated_at: datetime
```

### 2.2 参与人员管理

#### PlanParticipant
```python
class PlanParticipant(BaseModel):
    user_id: int
    name: str
    phone: str
    id_number: str
    work_type: str
    is_registered: bool
    register_time: Optional[datetime]
```

## 3. 业务逻辑设计

### 3.1 计划审批流程
1. 承包商创建计划
2. 企业现场人员初审
3. 企业管理员终审
4. 审批通过后可执行

### 3.2 人员签到流程
1. 验证参与人员
2. 扫码或手动签到
3. 记录签到时间
4. 更新签到状态

## 4. 权限控制

| 操作 | 企业管理员 | 现场人员 | 普通员工 |
|------|-----------|---------|---------|
| 查看计划列表 | ✓ | ✓ | 相关 |
| 查看计划详情 | ✓ | ✓ | 相关 |
| 审批计划 | ✓ | ✗ | ✗ |
| 查看参与人员 | ✓ | ✓ | ✗ |
| 管理签到 | ✓ | ✓ | ✗ |

