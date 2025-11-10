# 工单流程模块 - 对象设计方案

## 1. 模块结构

```
workflow/
├── __init__.py          # 路由注册
├── workflow.py          # 流程管理接口
├── approval.py          # 审批管理接口
├── README.md
├── object_plan.md       # 本文件
└── interface_list.md
```

## 2. 核心对象模型

### 2.1 流程定义

#### WorkflowDefinition
```python
class WorkflowDefinition(BaseModel):
    workflow_id: int
    workflow_name: str
    workflow_type: str  # ticket_approval, plan_approval
    enterprise_id: Optional[int]  # 企业ID，null表示系统级
    nodes: List[WorkflowNode]
    status: str  # active, inactive
```

#### WorkflowNode
```python
class WorkflowNode(BaseModel):
    node_id: int
    node_name: str
    node_type: str  # start, approval, end
    approver_role: Optional[str]
    approver_level: Optional[int]
    next_nodes: List[int]
```

### 2.2 流程实例

#### WorkflowInstance
```python
class WorkflowInstance(BaseModel):
    instance_id: int
    workflow_id: int
    business_id: int  # 关联的业务ID（工单ID、计划ID等）
    business_type: str  # ticket, plan
    current_node_id: int
    status: str  # pending, approved, rejected, cancelled
    created_at: datetime
    updated_at: datetime
```

### 2.3 审批记录

#### ApprovalRecord
```python
class ApprovalRecord(BaseModel):
    record_id: int
    instance_id: int
    node_id: int
    approver_id: int
    approver_name: str
    status: str  # pending, approved, rejected
    comment: Optional[str]
    approval_time: Optional[datetime]
```

## 3. 业务逻辑设计

### 3.1 流程定义流程
1. 创建流程定义
2. 添加流程节点
3. 配置节点关系
4. 激活流程

### 3.2 流程执行流程
1. 创建流程实例
2. 初始化到开始节点
3. 流转到第一个审批节点
4. 等待审批
5. 根据审批结果流转
6. 到达结束节点

### 3.3 审批处理流程
1. 验证审批人权限
2. 检查当前节点
3. 记录审批结果
4. 流转到下一节点
5. 发送通知

## 4. 流程状态机

```
pending (待审批)
  ├─ approved → 下一节点
  ├─ rejected → 结束
  └─ cancelled → 结束

approved (已通过)
  └─ 流程结束

rejected (已拒绝)
  └─ 流程结束

cancelled (已取消)
  └─ 流程结束
```

## 5. 权限控制

| 操作 | 系统管理员 | 企业管理员 | 审批人 | 普通用户 |
|------|-----------|-----------|--------|---------|
| 创建流程定义 | ✓ | ✓ | ✗ | ✗ |
| 查看流程定义 | ✓ | ✓ | ✓ | ✗ |
| 启动流程实例 | ✓ | ✓ | ✓ | ✗ |
| 审批流程 | ✓ | ✓ | ✓ | ✗ |
| 查看流程记录 | ✓ | ✓ | ✓ | 相关 |

## 6. 扩展功能

### 6.1 条件流转
- 根据条件选择下一节点
- 支持并行审批
- 支持会签

### 6.2 超时处理
- 审批超时提醒
- 自动流转
- 升级处理

### 6.3 流程监控
- 流程执行状态
- 审批效率统计
- 瓶颈分析

