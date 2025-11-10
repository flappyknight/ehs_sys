# 系统账户后台模块 - 对象设计方案

## 1. 模块架构

```
admin/
├── __init__.py          # 路由注册
├── auth.py              # 认证相关接口
├── user_management.py   # 系统用户管理
├── enterprise.py        # 企业管理
├── contractor.py        # 承包商管理
├── README.md           # 模块说明
├── object_plan.md      # 本文件
└── interface_list.md   # 接口文档
```

## 2. 核心对象模型

### 2.1 认证相关

#### Token
```python
class Token(BaseModel):
    access_token: str
    token_type: str
```

#### LoginRequest
```python
class LoginRequest(BaseModel):
    username: str
    password: str
```

### 2.2 用户管理

#### AdminUser
```python
class AdminUser(BaseModel):
    user_id: int
    username: str
    email: Optional[str]
    created_at: datetime
    updated_at: datetime
```

#### AdminUserCreate
```python
class AdminUserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str]
```

### 2.3 企业管理

#### Enterprise
```python
class Enterprise(BaseModel):
    company_id: int
    name: str
    type: str
    address: Optional[str]
    contact_person: Optional[str]
    contact_phone: Optional[str]
    status: bool
```

#### EnterpriseCreate
```python
class EnterpriseCreate(BaseModel):
    name: str
    type: str
    address: Optional[str]
    contact_person: Optional[str]
    contact_phone: Optional[str]
```

### 2.4 承包商管理

#### Contractor
```python
class Contractor(BaseModel):
    contractor_id: int
    company_name: str
    company_type: str
    legal_person: str
    establish_date: date
    business_license: Optional[str]
    status: bool
```

#### ContractorCreate
```python
class ContractorCreate(BaseModel):
    company_name: str
    company_type: str
    legal_person: str
    establish_date: date
    business_license: Optional[str]
```

## 3. 权限设计

### 3.1 权限级别
- **系统管理员 (admin)**: 最高权限，可访问所有接口
- **企业管理员 (enterprise_manager)**: 部分企业管理接口

### 3.2 权限验证流程
1. 从 Token 中解析用户信息
2. 验证用户类型是否为 admin
3. 检查用户状态是否有效
4. 执行业务逻辑

## 4. 数据库设计

### 4.1 涉及的表
- `user` - 用户账户表
- `company` - 企业表
- `contractor` - 承包商表

### 4.2 关键字段
- 所有表都包含 `created_at` 和 `updated_at` 时间戳
- 使用 `status` 字段实现软删除
- 使用自增主键 ID

## 5. 安全设计

### 5.1 密码安全
- 使用 bcrypt 加密存储密码
- 密码强度验证
- 密码重置机制

### 5.2 Token 安全
- JWT Token 有效期设置
- Token 刷新机制
- Token 黑名单（可选）

### 5.3 API 安全
- 所有接口需要认证
- 敏感操作需要二次验证
- 操作日志记录

## 6. 错误处理

### 6.1 错误码设计
- 400: 请求参数错误
- 401: 未认证或认证失败
- 403: 权限不足
- 404: 资源不存在
- 500: 服务器内部错误

### 6.2 错误响应格式
```python
{
    "detail": "错误描述信息"
}
```

## 7. 性能优化

### 7.1 数据库优化
- 使用索引优化查询
- 分页查询大数据集
- 使用连接池管理数据库连接

### 7.2 缓存策略
- Token 验证结果缓存
- 用户信息缓存
- 企业/承包商列表缓存

## 8. 扩展性设计

### 8.1 模块化
- 每个功能独立成文件
- 清晰的接口定义
- 便于单元测试

### 8.2 可配置性
- 配置文件管理敏感信息
- 环境变量支持
- 灵活的权限配置

## 9. 日志与监控

### 9.1 操作日志
- 记录所有管理操作
- 包含操作人、时间、内容
- 支持日志查询和审计

### 9.2 监控指标
- API 调用频率
- 响应时间
- 错误率统计

