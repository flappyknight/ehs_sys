# 企业用户管理模块 - 对象设计方案

## 1. 模块结构

```
user_management/
├── __init__.py          # 路由注册
├── user.py              # 员工管理接口
├── department.py        # 部门管理接口
├── area.py              # 厂区管理接口
├── README.md
├── object_plan.md       # 本文件
└── interface_list.md
```

## 2. 核心对象模型

### 2.1 员工管理

#### EnterpriseUserCreate
```python
class EnterpriseUserCreate(BaseModel):
    name: str
    phone: str
    email: Optional[str]
    position: Optional[str]
    department_id: Optional[int]
    role_type: str = "staff"  # manager, site_staff, staff
    create_account: bool = True
```

#### EnterpriseUserUpdate
```python
class EnterpriseUserUpdate(BaseModel):
    name: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    position: Optional[str]
    department_id: Optional[int]
    role_type: Optional[str]
    status: Optional[bool]
```

#### EnterpriseUserListItem
```python
class EnterpriseUserListItem(BaseModel):
    user_id: int
    name: str
    phone: str
    email: Optional[str]
    position: Optional[str]
    department_name: Optional[str]
    role_type: str
    status: bool
```

### 2.2 部门管理

#### DepartmentCreate
```python
class DepartmentCreate(BaseModel):
    name: str
    parent_id: Optional[int]
```

#### DepartmentUpdate
```python
class DepartmentUpdate(BaseModel):
    name: Optional[str]
    parent_id: Optional[int]
```

#### DepartmentWithMemberCount
```python
class DepartmentWithMemberCount(BaseModel):
    dept_id: int
    name: str
    parent_id: Optional[int]
    member_count: int
```

### 2.3 厂区管理

#### AreaCreate
```python
class AreaCreate(BaseModel):
    area_name: str
    dept_id: Optional[int]
```

#### AreaUpdate
```python
class AreaUpdate(BaseModel):
    area_name: Optional[str]
    dept_id: Optional[int]
```

#### AreaListItem
```python
class AreaListItem(BaseModel):
    area_id: int
    area_name: str
    dept_name: Optional[str]
    enterprise_name: str
```

## 3. 业务逻辑设计

### 3.1 员工管理流程

#### 添加员工
1. 验证企业管理员权限
2. 检查手机号是否已存在
3. 创建员工记录
4. 如果 create_account=True，创建登录账户
5. 默认密码为手机号后6位

#### 编辑员工
1. 验证权限（管理员或本人）
2. 验证员工归属企业
3. 更新员工信息
4. 记录操作日志

#### 禁用员工
1. 验证管理员权限
2. 设置 status=False（软删除）
3. 禁用关联的登录账户

### 3.2 部门管理流程

#### 创建部门
1. 验证管理员权限
2. 自动设置 company_id 为当前用户企业
3. 验证父部门是否存在
4. 创建部门记录

#### 删除部门
1. 验证管理员权限
2. 检查是否有子部门
3. 检查是否有员工
4. 检查是否有关联厂区
5. 执行删除

### 3.3 厂区管理流程

#### 创建厂区
1. 验证管理员权限
2. 自动设置 enterprise_id
3. 验证部门归属
4. 创建厂区记录

#### 删除厂区
1. 验证管理员权限
2. 检查是否有关联工单
3. 执行删除

## 4. 数据验证

### 4.1 员工数据验证
- 手机号格式验证（11位数字）
- 邮箱格式验证
- 角色类型验证（manager, site_staff, staff）
- 部门归属验证

### 4.2 部门数据验证
- 部门名称不能为空
- 父部门必须存在
- 不能设置自己为父部门
- 避免循环引用

### 4.3 厂区数据验证
- 厂区名称不能为空
- 部门必须属于当前企业
- 厂区名称在企业内唯一

## 5. 权限控制

### 5.1 权限矩阵

| 操作 | 企业管理员 | 现场人员 | 普通员工 |
|------|-----------|---------|---------|
| 添加员工 | ✓ | ✗ | ✗ |
| 查看员工列表 | ✓ | ✓ | ✗ |
| 编辑员工 | ✓ | ✗ | 本人 |
| 禁用员工 | ✓ | ✗ | ✗ |
| 创建部门 | ✓ | ✗ | ✗ |
| 查看部门 | ✓ | ✓ | ✓ |
| 编辑部门 | ✓ | ✗ | ✗ |
| 删除部门 | ✓ | ✗ | ✗ |
| 创建厂区 | ✓ | ✗ | ✗ |
| 查看厂区 | ✓ | ✓ | ✓ |
| 编辑厂区 | ✓ | ✗ | ✗ |
| 删除厂区 | ✓ | ✗ | ✗ |

### 5.2 数据权限
- 所有查询自动添加 enterprise_id 过滤
- 编辑操作验证数据归属
- 跨企业访问返回 403 错误

## 6. 错误处理

### 6.1 常见错误
- 400: 参数验证失败
- 403: 权限不足或跨企业访问
- 404: 员工/部门/厂区不存在
- 409: 手机号已存在、部门名称重复等

### 6.2 错误消息
- 清晰的中文错误描述
- 包含错误原因
- 提供解决建议

## 7. 性能优化

### 7.1 查询优化
- 员工列表支持分页
- 使用索引优化查询
- 缓存部门树结构

### 7.2 批量操作
- 支持批量导入员工
- 批量修改员工状态
- 批量分配部门

## 8. 扩展功能

### 8.1 员工导入
- 支持 Excel 导入
- 数据验证
- 错误报告

### 8.2 组织架构图
- 部门树形结构
- 可视化展示
- 拖拽调整

### 8.3 员工档案
- 完整的员工信息
- 工作履历
- 培训记录

