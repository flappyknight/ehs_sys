# 工单管理模块说明 (Ticket Management Module)

## 概述

工单管理模块提供了完整的作业票（工单）管理功能，包括创建、查询、更新和删除工单。工单用于记录和管理企业内的各类作业活动，包括动火作业、高空作业、受限空间作业等。

## 数据模型

### TicketCreate（创建工单）
```python
{
    "apply_date": "2025-11-03",           # 申请日期
    "applicant": 1,                        # 申请人ID（企业用户）
    "area_id": 1,                          # 作业区域ID
    "working_content": "设备维修作业",      # 作业内容
    "pre_st": "2025-11-03T08:00:00",      # 预计开始时间
    "pre_et": "2025-11-03T17:00:00",      # 预计结束时间
    "tools": 0,                            # 主要工具（二进制编码）
    "worker": 1,                           # 作业人员ID（承包商用户）
    "custodians": 2,                       # 监护人ID（企业用户）
    "danger": 0,                           # 危险识别（二进制编码）
    "protection": 0,                       # 防护措施（二进制编码）
    "hot_work": -1,                        # 动火等级：-1未动火 0特级 1一级 2二级
    "work_height_level": 0,                # 作业高度等级：0-4级
    "confined_space_id": null,             # 受限空间ID（可选）
    "temp_power_id": null,                 # 临时用电ID（可选）
    "cross_work_group_id": null,           # 交叉作业组ID（可选）
    "signature": null                      # 签字（可选）
}
```

### TicketUpdate（更新工单）
所有字段都是可选的，只需提供需要更新的字段。

### TicketListItem（工单列表项）
```python
{
    "ticket_id": 1,
    "apply_date": "2025-11-03",
    "applicant_name": "张三",
    "area_name": "生产车间A",
    "working_content": "设备维修作业",
    "pre_st": "2025-11-03T08:00:00",
    "pre_et": "2025-11-03T17:00:00",
    "worker_name": "李四",
    "custodian_name": "王五",
    "hot_work": -1,
    "work_height_level": 0,
    "created_at": "2025-11-03T07:00:00"
}
```

### TicketDetail（工单详情）
包含所有工单信息，包括关联的人员姓名、区域名称等。

## API 接口

### 1. 创建工单
```
POST /api/tickets/
```

**权限要求**: 企业管理员及以上

**请求体**: TicketCreate

**响应**:
```json
{
    "message": "工单创建成功",
    "ticket_id": 1
}
```

**示例**:
```bash
curl -X POST "http://localhost:8000/api/tickets/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "apply_date": "2025-11-03",
    "applicant": 1,
    "area_id": 1,
    "working_content": "设备维修作业",
    "pre_st": "2025-11-03T08:00:00",
    "pre_et": "2025-11-03T17:00:00",
    "tools": 0,
    "worker": 1,
    "custodians": 2,
    "danger": 0,
    "protection": 0,
    "hot_work": -1,
    "work_height_level": 0
  }'
```

### 2. 获取工单列表
```
GET /api/tickets/
```

**权限要求**: 登录用户

**查询参数**:
- `area_id` (可选): 按厂区筛选
- `hot_work` (可选): 按动火等级筛选
- `start_date` (可选): 开始日期
- `end_date` (可选): 结束日期

**响应**: TicketListItem[]

**数据隔离**: 企业用户只能看到自己企业的工单

**示例**:
```bash
# 获取所有工单
curl -X GET "http://localhost:8000/api/tickets/" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 按厂区筛选
curl -X GET "http://localhost:8000/api/tickets/?area_id=1" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 按动火等级筛选
curl -X GET "http://localhost:8000/api/tickets/?hot_work=1" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 按日期范围筛选
curl -X GET "http://localhost:8000/api/tickets/?start_date=2025-11-01&end_date=2025-11-30" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. 获取工单详情
```
GET /api/tickets/{ticket_id}/
```

**权限要求**: 登录用户

**路径参数**:
- `ticket_id`: 工单ID

**响应**: TicketDetail

**数据隔离**: 企业用户只能查看自己企业的工单

**示例**:
```bash
curl -X GET "http://localhost:8000/api/tickets/1/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. 更新工单
```
PUT /api/tickets/{ticket_id}/
```

**权限要求**: 企业管理员及以上

**路径参数**:
- `ticket_id`: 工单ID

**请求体**: TicketUpdate（只需提供要更新的字段）

**响应**:
```json
{
    "message": "工单更新成功"
}
```

**数据隔离**: 企业用户只能修改自己企业的工单

**示例**:
```bash
curl -X PUT "http://localhost:8000/api/tickets/1/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "working_content": "更新后的作业内容",
    "hot_work": 1
  }'
```

### 5. 删除工单
```
DELETE /api/tickets/{ticket_id}/
```

**权限要求**: 企业管理员及以上

**路径参数**:
- `ticket_id`: 工单ID

**响应**:
```json
{
    "message": "工单删除成功"
}
```

**数据隔离**: 企业用户只能删除自己企业的工单

**示例**:
```bash
curl -X DELETE "http://localhost:8000/api/tickets/1/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 字段说明

### 动火等级 (hot_work)
- `-1`: 未动火
- `0`: 特级动火（最高风险）
- `1`: 一级动火
- `2`: 二级动火（最低风险）

### 作业高度等级 (work_height_level)
- `0`: 无高空作业
- `1`: 2-5米
- `2`: 5-15米
- `3`: 15-30米
- `4`: 30米以上（最高风险）

### 工具编码 (tools)
使用二进制位编码，每一位代表一种工具：
- 位0: 电焊机
- 位1: 切割机
- 位2: 手持电动工具
- 位3: 梯子
- 位4: 脚手架
- ...（可根据实际需求扩展）

### 危险识别 (danger)
使用二进制位编码，每一位代表一种危险：
- 位0: 火灾爆炸
- 位1: 高空坠落
- 位2: 触电
- 位3: 中毒窒息
- 位4: 机械伤害
- ...（可根据实际需求扩展）

### 防护措施 (protection)
使用二进制位编码，每一位代表一种防护措施：
- 位0: 安全帽
- 位1: 安全带
- 位2: 防护眼镜
- 位3: 防护手套
- 位4: 防护服
- ...（可根据实际需求扩展）

## 权限控制

### 创建工单
- 需要企业管理员权限
- 申请人必须是企业用户
- 监护人必须是企业用户
- 作业人员必须是承包商用户

### 查看工单
- 所有登录用户都可以查看
- 企业用户只能看到自己企业的工单
- 管理员可以看到所有工单

### 更新工单
- 需要企业管理员权限
- 企业用户只能修改自己企业的工单

### 删除工单
- 需要企业管理员权限
- 企业用户只能删除自己企业的工单

## 数据隔离

工单管理模块实现了严格的数据隔离：

1. **企业级隔离**: 企业用户只能访问自己企业的工单
2. **区域关联**: 通过 area_id 关联到企业，确保数据隔离
3. **权限检查**: 所有操作都会进行权限验证

## 使用场景

### 场景1: 创建动火作业工单
```python
{
    "apply_date": "2025-11-03",
    "applicant": 1,
    "area_id": 1,
    "working_content": "管道焊接作业",
    "pre_st": "2025-11-03T08:00:00",
    "pre_et": "2025-11-03T17:00:00",
    "tools": 3,  # 电焊机(1) + 切割机(2) = 3
    "worker": 1,
    "custodians": 2,
    "danger": 1,  # 火灾爆炸风险
    "protection": 31,  # 安全帽+安全带+防护眼镜+防护手套+防护服
    "hot_work": 1,  # 一级动火
    "work_height_level": 0
}
```

### 场景2: 创建高空作业工单
```python
{
    "apply_date": "2025-11-03",
    "applicant": 1,
    "area_id": 1,
    "working_content": "外墙清洁作业",
    "pre_st": "2025-11-03T08:00:00",
    "pre_et": "2025-11-03T17:00:00",
    "tools": 24,  # 梯子(8) + 脚手架(16) = 24
    "worker": 1,
    "custodians": 2,
    "danger": 2,  # 高空坠落风险
    "protection": 3,  # 安全帽(1) + 安全带(2) = 3
    "hot_work": -1,  # 未动火
    "work_height_level": 2  # 5-15米
}
```

### 场景3: 查询本月所有动火作业
```bash
curl -X GET "http://localhost:8000/api/tickets/?hot_work=1&start_date=2025-11-01&end_date=2025-11-30" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 注意事项

1. **时间格式**: 所有时间字段使用 ISO 8601 格式（如：`2025-11-03T08:00:00`）
2. **用户类型**: 申请人和监护人必须是企业用户，作业人员必须是承包商用户
3. **区域验证**: area_id 必须存在且属于当前企业
4. **数据完整性**: 创建工单时必须提供所有必填字段
5. **权限验证**: 所有操作都会进行严格的权限验证

## 错误处理

常见错误及解决方案：

| 错误码 | 错误信息 | 解决方案 |
|--------|----------|----------|
| 400 | 创建工单失败 | 检查请求数据格式和必填字段 |
| 401 | 权限不足 | 确保有企业管理员权限 |
| 403 | 无权访问该工单 | 只能访问自己企业的工单 |
| 404 | 工单不存在 | 检查工单ID是否正确 |

## 扩展功能建议

未来可以考虑添加的功能：

1. **工单审批流程**: 添加多级审批功能
2. **工单状态管理**: 待审批、进行中、已完成等状态
3. **工单统计**: 按类型、区域、时间统计工单数据
4. **工单模板**: 预设常用工单模板
5. **工单附件**: 支持上传相关文件和图片
6. **工单通知**: 工单状态变更时发送通知
7. **工单历史**: 记录工单的所有变更历史

---

**创建时间**: 2025-11-03  
**版本**: v1.0  
**维护者**: Development Team

