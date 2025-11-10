# 合作申请管理模块 - 对象设计方案

## 1. 核心对象模型

### CooperationRequest
```python
class CooperationRequest(BaseModel):
    request_id: int
    enterprise_id: int
    enterprise_name: str
    project_name: str
    project_content: str
    start_date: date
    end_date: Optional[date]
    status: str  # pending, accepted, rejected
    created_at: datetime
```

### CooperationResponse
```python
class CooperationResponse(BaseModel):
    request_id: int
    status: str  # accepted, rejected
    comment: Optional[str]
    contact_person: str
    contact_phone: str
```

## 2. 业务逻辑

### 查看合作邀请流程
1. 验证承包商用户权限
2. 查询发送给本承包商的邀请
3. 返回邀请列表

### 处理合作邀请流程
1. 验证承包商管理员权限
2. 检查邀请状态
3. 更新邀请状态
4. 如果接受，创建项目关联
5. 发送通知给企业

## 3. 权限控制

| 操作 | 承包商管理员 | 作业人员 |
|------|-------------|---------|
| 查看邀请列表 | ✓ | ✓ |
| 查看邀请详情 | ✓ | ✓ |
| 接受邀请 | ✓ | ✗ |
| 拒绝邀请 | ✓ | ✗ |

