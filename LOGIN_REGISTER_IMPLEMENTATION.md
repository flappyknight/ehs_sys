# 登录注册功能实现说明

## 概述
本文档描述了为 EHS 系统添加的登录页面改进和用户注册功能。

## 功能特性

### 1. 登录页面改进
- ✅ 添加了身份选择下拉框，支持三种用户类型：
  - 企业（默认选项）
  - 承包商
  - 系统管理
- ✅ 添加了"立即注册"按钮，引导用户进行注册
- ✅ 改进了页面UI，使用现代化的设计风格

### 2. 用户注册功能
- ✅ 创建了独立的注册页面
- ✅ 支持企业和承包商用户自助注册（系统管理员需联系管理员创建）
- ✅ 根据选择的用户类型动态显示不同的表单字段
- ✅ 实现了完整的表单验证
- ✅ 注册成功后自动跳转到登录页面

## 修改的文件

### 前端文件

#### 1. `/web/src/views/UserLogin.vue`
**修改内容：**
- 添加了身份选择下拉框
- 添加了注册按钮和相关样式
- 更新了表单数据结构，包含 `userType` 字段

**主要变更：**
```vue
<div class="form-group">
  <label for="userType">身份选择</label>
  <select id="userType" v-model="form.userType" class="form-select">
    <option value="enterprise">企业</option>
    <option value="contractor">承包商</option>
    <option value="admin">系统管理</option>
  </select>
</div>

<div class="register-section">
  <span class="register-text">还没有账号？</span>
  <button type="button" class="register-button" @click="goToRegister">
    立即注册
  </button>
</div>
```

#### 2. `/web/src/views/UserRegister.vue` (新建)
**功能：**
- 完整的用户注册表单
- 支持企业和承包商两种用户类型注册
- 动态表单字段（根据用户类型显示不同字段）
- 表单验证（密码确认、手机号格式等）
- 注册成功提示和自动跳转

**表单字段：**
- 通用字段：用户名、密码、确认密码、姓名、手机号、邮箱（选填）
- 企业用户特有：企业名称、职位（选填）
- 承包商用户特有：承包商公司名称

#### 3. `/web/src/types/auth.ts`
**修改内容：**
- 更新 `LoginForm` 接口，添加 `userType` 字段
- 新增 `RegisterForm` 接口

```typescript
export interface LoginForm {
  username: string
  password: string
  userType?: 'enterprise' | 'contractor' | 'admin'
}

export interface RegisterForm {
  username: string
  password: string
  confirmPassword: string
  userType: 'enterprise' | 'contractor'
  name: string
  phone: string
  email?: string
  companyName?: string
  position?: string
  contractorCompanyName?: string
}
```

#### 4. `/web/src/router/index.ts`
**修改内容：**
- 添加注册页面路由
- 设置为游客可访问（requiresGuest）

```typescript
{
  path: '/register',
  name: 'Register',
  component: Register,
  meta: { requiresGuest: true }
}
```

#### 5. `/web/src/services/api.ts`
**修改内容：**
- 添加 `register` 方法，调用后端注册接口

```typescript
async register(registerData: any): Promise<{ message: string; user_id: number }> {
  return this.request<{ message: string; user_id: number }>('/register', {
    method: 'POST',
    body: JSON.stringify(registerData),
  })
}
```

### 后端文件

#### 6. `/api/model.py`
**修改内容：**
- 添加 `RegisterRequest` 模型类

```python
class RegisterRequest(BaseModel):
    username: str
    password: str
    userType: str
    name: str
    phone: str
    email: Optional[str] = None
    companyName: Optional[str] = None
    position: Optional[str] = None
    contractorCompanyName: Optional[str] = None
```

#### 7. `/routes/auth.py`
**修改内容：**
- 添加 `/register` 端点
- 实现完整的用户注册逻辑

**注册流程：**
1. 检查用户名是否已存在
2. 验证用户类型（只允许 enterprise 和 contractor）
3. 创建用户账号（加密密码）
4. 根据用户类型创建对应的企业用户或承包商用户
5. 如果企业/承包商不存在，自动创建
6. 返回注册成功信息

#### 8. `/routes/dependencies.py`
**修改内容：**
- 添加 `get_engine` 依赖函数，用于获取数据库引擎

```python
async def get_engine():
    """获取数据库引擎"""
    from main import app
    return app.state.engine
```

## 数据库操作

### 企业用户注册
1. 创建 `User` 记录（user_type='enterprise'）
2. 检查/创建 `Company` 记录（type='enterprise'）
3. 创建 `EnterpriseUser` 记录
   - 默认角色：manager
   - 默认审批级别：1
   - 状态：激活

### 承包商用户注册
1. 创建 `User` 记录（user_type='contractor'）
2. 检查/创建 `Contractor` 记录
3. 创建 `ContractorUser` 记录
   - 默认角色：manager
   - 状态：激活

## 安全特性

1. **密码加密**：使用 `get_password_hash` 函数加密存储密码
2. **用户名唯一性检查**：注册前检查用户名是否已存在
3. **输入验证**：
   - 密码长度至少6位
   - 手机号格式验证（中国手机号）
   - 必填字段验证
4. **错误处理**：完善的异常捕获和错误提示

## 用户体验优化

1. **动态表单**：根据选择的用户类型显示相应的表单字段
2. **实时验证**：前端表单验证，提供即时反馈
3. **加载状态**：按钮禁用和加载提示
4. **成功提示**：注册成功后显示提示信息并自动跳转
5. **友好的错误提示**：清晰的中文错误信息

## 使用说明

### 用户注册流程
1. 访问登录页面，点击"立即注册"按钮
2. 选择用户类型（企业或承包商）
3. 填写必填信息：
   - 用户名（唯一）
   - 密码（至少6位）
   - 确认密码
   - 姓名
   - 手机号
   - 企业名称或承包商公司名称
4. 可选填写：邮箱、职位
5. 点击"注册"按钮
6. 注册成功后，3秒后自动跳转到登录页面

### 用户登录流程
1. 访问登录页面
2. 选择身份类型（企业/承包商/系统管理）
3. 输入用户名和密码
4. 点击"登录"按钮
5. 登录成功后跳转到仪表板

## 注意事项

1. **系统管理员账号**：不支持自助注册，需要通过后台管理员创建
2. **企业/承包商自动创建**：如果注册时填写的企业或承包商不存在，系统会自动创建
3. **默认权限**：新注册用户默认为管理员角色（manager）
4. **待完善字段**：承包商的某些字段（如营业执照、身份证号等）在注册时为空，需要后续完善

## 测试建议

1. 测试企业用户注册流程
2. 测试承包商用户注册流程
3. 测试用户名重复的情况
4. 测试密码不一致的情况
5. 测试手机号格式验证
6. 测试注册成功后的登录
7. 测试不同身份类型的登录

## 后续优化建议

1. 添加邮箱验证功能
2. 添加手机号验证码功能
3. 完善承包商注册时的必填字段（营业执照等）
4. 添加图形验证码防止恶意注册
5. 添加密码强度提示
6. 支持找回密码功能

