# 企业承包商管理模块 - 对象设计方案

## 1. 模块结构

```
contractor_management/
├── __init__.py          # 路由注册
├── contractor.py        # 承包商管理接口
├── project.py           # 项目管理接口
├── README.md
├── object_plan.md       # 本文件
└── interface_list.md
```

## 2. 核心对象模型

### 2.1 承包商管理

#### ContractorListItem
```python
class ContractorListItem(BaseModel):
    contractor_id: int
    company_name: str
    company_type: str
    legal_person: str
    establish_date: str
    project_count: int  # 合作项目数量
    rating: Optional[float]  # 评分
```

#### ContractorDetail
```python
class ContractorDetail(BaseModel):
    contractor_id: int
    company_name: str
    company_type: str
    legal_person: str
    establish_date: date
    business_license: Optional[str]
    contact_person: Optional[str]
    contact_phone: Optional[str]
    project_count: int
    staff_count: int
    rating: Optional[float]
    created_at: datetime
```

### 2.2 项目管理

#### ContractorProjectCreate
```python
class ContractorProjectCreate(BaseModel):
    contractor_id: Optional[int]  # 已有承包商ID
    contractor_info: Optional[ContractorCreate]  # 新承包商信息
    project_name: str
    project_content: str
    start_date: date
    end_date: Optional[date]
```

#### ContractorProjectListItem
```python
class ContractorProjectListItem(BaseModel):
    project_id: int
    project_name: str
    contractor_name: str
    start_date: date
    end_date: Optional[date]
    status: str  # active, completed, cancelled
    plan_count: int  # 计划数量
```

#### ContractorProjectDetail
```python
class ContractorProjectDetail(BaseModel):
    project_id: int
    project_name: str
    project_content: str
    contractor_id: int
    contractor_name: str
    enterprise_id: int
    start_date: date
    end_date: Optional[date]
    status: str
    plan_count: int
    created_at: datetime
    updated_at: datetime
```

## 3. 业务逻辑设计

### 3.1 承包商查看流程

#### 获取承包商列表
1. 验证企业用户权限
2. 查询与当前企业有合作项目的承包商
3. 统计每个承包商的项目数量
4. 返回承包商列表

#### 查看承包商详情
1. 验证权限
2. 检查是否有合作关系
3. 获取承包商详细信息
4. 统计项目和人员数量

### 3.2 项目管理流程

#### 创建合作项目
1. 验证企业管理员权限
2. 如果是新承包商，先创建承包商
3. 创建项目记录
4. 建立企业-承包商关联
5. 返回项目信息

#### 结束项目
1. 验证权限
2. 检查项目状态
3. 更新项目状态为 completed
4. 设置结束日期

## 4. 数据验证

### 4.1 承包商数据验证
- 公司名称不能为空
- 法人代表不能为空
- 成立日期格式验证
- 营业执照号格式验证

### 4.2 项目数据验证
- 项目名称不能为空
- 开始日期不能晚于结束日期
- 承包商必须存在
- 项目名称在企业内唯一

## 5. 权限控制

### 5.1 权限矩阵

| 操作 | 企业管理员 | 现场人员 | 普通员工 |
|------|-----------|---------|---------|
| 查看承包商列表 | ✓ | ✓ | ✗ |
| 查看承包商详情 | ✓ | ✓ | ✗ |
| 创建承包商 | ✓ | ✗ | ✗ |
| 创建项目 | ✓ | ✗ | ✗ |
| 查看项目列表 | ✓ | ✓ | ✗ |
| 编辑项目 | ✓ | ✗ | ✗ |
| 结束项目 | ✓ | ✗ | ✗ |

### 5.2 数据权限
- 只能查看有合作关系的承包商
- 通过项目表关联过滤数据
- 跨企业访问被拒绝

## 6. 扩展功能

### 6.1 承包商评价
- 项目结束后评价
- 评分系统（1-5星）
- 评价内容记录

### 6.2 承包商资质管理
- 资质证书上传
- 资质到期提醒
- 资质审核

### 6.3 合作统计
- 合作项目统计
- 合作金额统计
- 合作时长统计

