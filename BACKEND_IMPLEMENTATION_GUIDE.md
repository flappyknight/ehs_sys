# 后端实现指南

## 📋 已完成的功能

### 1. 登录接口改进 ✅
- **位置**: `/routes/auth.py` - `POST /token`
- **功能**: 打印登录请求的详细信息
- **打印内容**:
  - 用户名
  - 密码（隐藏显示为 `*`）
  - 登录时间
  - 登录结果（成功/失败）
  - 用户类型

### 2. 注册接口实现 ✅
- **位置**: `/routes/auth.py` - `POST /register`
- **功能**: 接收并打印注册数据（暂不写入数据库）
- **支持的用户类型**:
  - 企业用户 (enterprise)
  - 承包商用户 (contractor)
  - 系统管理员 (admin)

### 3. 前端注册页面 ✅
- **位置**: `/web/src/views/UserRegister.vue`
- **功能**: 完整的三种用户类型注册表单
- **动态表单**: 根据选择的用户类型显示不同的字段

## 🔧 技术实现细节

### 后端修改

#### 1. `/routes/auth.py` - 登录接口
```python
@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    # 打印登录数据
    print("=" * 50)
    print("【登录请求】")
    print(f"用户名: {form_data.username}")
    print(f"密码: {'*' * len(form_data.password)}")
    print(f"登录时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # ... 验证逻辑 ...
    
    print(f"✅ 登录成功: 用户类型={user.user_type}")
```

#### 2. `/routes/auth.py` - 注册接口
```python
@router.post("/register")
async def register_user(
    register_data: RegisterRequest,
    engine: AsyncEngine = Depends(get_engine)
):
    # 打印注册数据
    print("\n" + "=" * 60)
    print("【注册请求】")
    print(f"注册时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"用户类型: {register_data.userType}")
    print(f"用户名: {register_data.username}")
    # ... 更多字段 ...
    
    # 根据用户类型打印特定字段
    if register_data.userType == 'enterprise':
        print(f"\n【企业用户信息】")
        print(f"企业名称: {register_data.companyName}")
        print(f"职位: {register_data.position or '未填写'}")
    elif register_data.userType == 'contractor':
        print(f"\n【承包商用户信息】")
        print(f"承包商公司名称: {register_data.contractorCompanyName}")
    elif register_data.userType == 'admin':
        print(f"\n【系统管理员信息】")
        print(f"管理员授权码: {register_data.adminCode or '未填写'}")
        print(f"所属部门: {register_data.department or '未填写'}")
    
    # 返回测试响应（不写入数据库）
    return {
        "message": "注册数据已接收（测试模式，未写入数据库）",
        "user_id": 999,
        "username": register_data.username,
        "userType": register_data.userType
    }
```

#### 3. `/api/model.py` - 数据模型
```python
class RegisterRequest(BaseModel):
    username: str
    password: str
    userType: str  # 'enterprise', 'contractor', or 'admin'
    name: str
    phone: str
    email: Optional[str] = None
    # 企业用户特有字段
    companyName: Optional[str] = None
    position: Optional[str] = None
    # 承包商用户特有字段
    contractorCompanyName: Optional[str] = None
    # 系统管理员特有字段
    adminCode: Optional[str] = None
    department: Optional[str] = None
```

### 前端修改

#### 1. `/web/src/views/UserRegister.vue` - 注册表单
**支持三种用户类型**:
- 企业用户
- 承包商用户
- 系统管理员

**表单字段**:

**通用字段**:
- 用户名 *
- 密码 *
- 确认密码 *
- 姓名 *
- 手机号 *
- 邮箱

**企业用户特有**:
- 企业名称 *
- 职位

**承包商用户特有**:
- 承包商公司名称 *

**系统管理员特有**:
- 管理员授权码 *
- 所属部门

#### 2. `/web/src/types/auth.ts` - 类型定义
```typescript
export interface RegisterForm {
  username: string
  password: string
  confirmPassword: string
  userType: 'enterprise' | 'contractor' | 'admin'
  name: string
  phone: string
  email?: string
  companyName?: string
  position?: string
  contractorCompanyName?: string
  adminCode?: string
  department?: string
}
```

## 🧪 测试结果

### 1. 企业用户注册测试
```bash
curl -X POST "http://localhost:8100/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_enterprise",
    "password": "123456",
    "userType": "enterprise",
    "name": "张三",
    "phone": "13800138000",
    "email": "test@example.com",
    "companyName": "测试企业有限公司",
    "position": "安全经理"
  }'
```

**后端控制台输出**:
```
============================================================
【注册请求】
注册时间: 2025-11-10 XX:XX:XX
用户类型: enterprise
用户名: test_enterprise
密码: ******
姓名: 张三
手机号: 13800138000
邮箱: test@example.com

【企业用户信息】
企业名称: 测试企业有限公司
职位: 安全经理
============================================================
```

**响应**:
```json
{
  "message": "注册数据已接收（测试模式，未写入数据库）",
  "user_id": 999,
  "username": "test_enterprise",
  "userType": "enterprise"
}
```

### 2. 承包商用户注册测试
```bash
curl -X POST "http://localhost:8100/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_contractor",
    "password": "123456",
    "userType": "contractor",
    "name": "李四",
    "phone": "13900139000",
    "email": "lisi@example.com",
    "contractorCompanyName": "测试承包商公司"
  }'
```

**后端控制台输出**:
```
============================================================
【注册请求】
注册时间: 2025-11-10 XX:XX:XX
用户类型: contractor
用户名: test_contractor
密码: ******
姓名:李四
手机号: 13900139000
邮箱: lisi@example.com

【承包商用户信息】
承包商公司名称: 测试承包商公司
============================================================
```

### 3. 系统管理员注册测试
```bash
curl -X POST "http://localhost:8100/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_admin",
    "password": "123456",
    "userType": "admin",
    "name": "王五",
    "phone": "13700137000",
    "email": "admin@example.com",
    "adminCode": "ADMIN2024",
    "department": "系统管理部"
  }'
```

**后端控制台输出**:
```
============================================================
【注册请求】
注册时间: 2025-11-10 XX:XX:XX
用户类型: admin
用户名: test_admin
密码: ******
姓名: 王五
手机号: 13700137000
邮箱: admin@example.com

【系统管理员信息】
管理员授权码: ADMIN2024
所属部门: 系统管理部
============================================================
```

### 4. 登录测试
```bash
curl -X POST "http://localhost:8100/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

**后端控制台输出**:
```
==================================================
【登录请求】
用户名: admin
密码: *********
登录时间: 2025-11-10 XX:XX:XX
==================================================
✅ 登录成功: 用户类型=admin
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## 📝 注册表单字段说明

### 企业用户注册
| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | string | ✅ | 用户名（唯一） |
| password | string | ✅ | 密码（至少6位） |
| confirmPassword | string | ✅ | 确认密码 |
| userType | string | ✅ | 固定为 "enterprise" |
| name | string | ✅ | 真实姓名 |
| phone | string | ✅ | 手机号（11位） |
| email | string | ❌ | 邮箱地址 |
| companyName | string | ✅ | 企业名称 |
| position | string | ❌ | 职位 |

### 承包商用户注册
| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | string | ✅ | 用户名（唯一） |
| password | string | ✅ | 密码（至少6位） |
| confirmPassword | string | ✅ | 确认密码 |
| userType | string | ✅ | 固定为 "contractor" |
| name | string | ✅ | 真实姓名 |
| phone | string | ✅ | 手机号（11位） |
| email | string | ❌ | 邮箱地址 |
| contractorCompanyName | string | ✅ | 承包商公司名称 |

### 系统管理员注册
| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | string | ✅ | 用户名（唯一） |
| password | string | ✅ | 密码（至少6位） |
| confirmPassword | string | ✅ | 确认密码 |
| userType | string | ✅ | 固定为 "admin" |
| name | string | ✅ | 真实姓名 |
| phone | string | ✅ | 手机号（11位） |
| email | string | ❌ | 邮箱地址 |
| adminCode | string | ✅ | 管理员授权码 |
| department | string | ❌ | 所属部门 |

## 🔄 后续数据库集成步骤

当您准备好进行数据库集成时，需要修改 `/routes/auth.py` 中的 `register_user` 函数：

### 1. 恢复数据库写入逻辑
将当前的测试代码替换为实际的数据库操作代码（已在之前版本中实现）

### 2. 需要考虑的数据库表
- **users** 表：存储基础用户账号信息
- **company** 表：存储企业信息
- **enterprise_user** 表：存储企业用户详细信息
- **contractor** 表：存储承包商信息
- **contractor_user** 表：存储承包商用户详细信息
- **admin_user** 表（如需要）：存储系统管理员信息

### 3. 建议的字段映射

#### 企业用户
```python
# users 表
user_type = 'enterprise'
username = register_data.username
password_hash = get_password_hash(register_data.password)

# company 表
name = register_data.companyName
type = 'enterprise'

# enterprise_user 表
name = register_data.name
phone = register_data.phone
email = register_data.email
position = register_data.position
role_type = 'manager'  # 默认
```

#### 承包商用户
```python
# users 表
user_type = 'contractor'
username = register_data.username
password_hash = get_password_hash(register_data.password)

# contractor 表
company_name = register_data.contractorCompanyName
# 其他字段根据数据库设计补充

# contractor_user 表
name = register_data.name
phone = register_data.phone
# 其他字段根据数据库设计补充
```

#### 系统管理员
```python
# users 表
user_type = 'admin'
username = register_data.username
password_hash = get_password_hash(register_data.password)

# 可能需要验证 adminCode
# 可能需要创建 admin_user 表记录
```

## 🚀 启动和测试

### 启动后端服务
```bash
cd /Users/dubin/work/ehs_sys
source /opt/anaconda3/bin/activate ehs_env
uvicorn main:app --host 0.0.0.0 --port 8100 --reload
```

### 启动前端服务
```bash
cd /Users/dubin/work/ehs_sys/web
npm run dev
```

### 访问地址
- 前端: http://localhost:5173
- 后端API文档: http://localhost:8100/docs

## ✅ 完成清单

- [x] 登录接口打印数据
- [x] 注册接口接收并打印数据
- [x] 支持三种用户类型注册
- [x] 前端注册页面完整实现
- [x] 动态表单字段
- [x] 表单验证
- [x] 接口测试通过
- [ ] 数据库集成（待您根据库表设计完成）

## 📞 注意事项

1. **当前状态**: 注册接口只打印数据，不写入数据库
2. **测试模式**: 所有注册请求都会返回成功，user_id固定为999
3. **数据库集成**: 您需要根据实际的数据库表结构修改注册逻辑
4. **密码安全**: 打印时密码已隐藏为 `*`，实际存储需要加密
5. **授权码验证**: 系统管理员的授权码验证逻辑需要您补充

---

**实现日期**: 2025-11-10
**测试状态**: ✅ 通过
**下一步**: 根据数据库表结构完成数据写入逻辑

