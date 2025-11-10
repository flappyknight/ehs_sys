# 工单浏览模块 - 对象设计方案

## 1. 核心对象模型

### ContractorTicketListItem
```python
class ContractorTicketListItem(BaseModel):
    ticket_id: int
    apply_date: date
    enterprise_name: str
    area_name: str
    working_content: str
    pre_st: str
    pre_et: str
    worker_name: str
    status: str
    is_assigned_to_me: bool
```

### TicketExecutionReport
```python
class TicketExecutionReport(BaseModel):
    ticket_id: int
    execution_status: str
    progress: int  # 0-100
    photos: List[str]
    comment: str
    report_time: datetime
```

## 2. 业务逻辑

### 工单查看流程
1. 验证承包商用户权限
2. 查询相关项目的工单
3. 过滤出分配给本承包商员工的工单
4. 返回工单列表

### 工单执行上报流程
1. 验证作业人员权限
2. 检查工单是否分配给自己
3. 上传执行情况
4. 更新工单状态

## 3. 权限控制

| 操作 | 承包商管理员 | 作业人员 |
|------|-------------|---------|
| 查看工单列表 | ✓ | 分配给自己的 |
| 查看工单详情 | ✓ | 分配给自己的 |
| 上报执行情况 | ✓ | 分配给自己的 |
| 完成工单 | ✓ | 分配给自己的 |

