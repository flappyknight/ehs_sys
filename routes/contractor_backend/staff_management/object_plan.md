# 承包商人员管理模块 - 对象设计方案

## 1. 核心对象模型

### ContractorUserCreate
```python
class ContractorUserCreate(BaseModel):
    name: str
    phone: str
    id_number: str
    work_type: str
    personal_photo: Optional[str]
    role_type: str = "worker"
    create_account: bool = True
```

### ContractorUserListItem
```python
class ContractorUserListItem(BaseModel):
    user_id: int
    name: str
    phone: str
    id_number: str
    work_type: str
    role_type: str
    status: bool
    has_qualification: bool
```

## 2. 业务逻辑

### 添加员工流程
1. 验证承包商管理员权限
2. 检查身份证号是否已存在
3. 创建员工记录
4. 如果 create_account=True，创建登录账户
5. 默认密码为手机号后6位

### 资质管理流程
1. 上传资质证书
2. 设置有效期
3. 到期前提醒
4. 资质过期禁止作业

## 3. 权限控制

| 操作 | 承包商管理员 | 作业人员 |
|------|-------------|---------|
| 添加员工 | ✓ | ✗ |
| 查看员工列表 | ✓ | ✗ |
| 编辑员工 | ✓ | 本人 |
| 禁用员工 | ✓ | ✗ |
| 管理资质 | ✓ | 本人 |

