# 新业务逻辑实现指南

## 📋 业务逻辑说明

### 核心概念区分

1. **企业/承包商入驻** = 注册公司（Company/Contractor）
   - 独立的申请流程
   - 需要填写公司信息、证照信息
   - 需要管理员审核

2. **用户注册** = 注册个人用户账号（User）
   - 注册企业用户或承包商用户
   - 需要关联到已存在的公司
   - 填写个人信息

## 🎯 新的页面结构

### 1. 登录页面 (`/login`)
```
EHS 系统登录
├── 身份选择（企业/承包商/系统管理）
├── 用户名
├── 密码
├── [登录按钮]
├── 注册账号 | 忘记密码
└── 企业或承包商入驻
    └── [立即申请 →]
```

### 2. 入驻选择页面 (`/settlement`)
```
EHS 系统入驻申请
├── [企业入驻] 卡片
│   └── 适用于生产制造企业、工厂等
└── [承包商入驻] 卡片
    └── 适用于施工单位、服务商等
```

### 3. 企业入驻申请页面 (`/settlement/enterprise`)
```
企业入驻申请
├── 基本信息
│   ├── 企业名称 *
│   ├── 法定代表人 *
│   ├── 联系电话 *
│   ├── 企业地址 *
│   ├── 行业类型 *
│   └── 员工人数 *
├── 证照信息
│   ├── 营业执照号 *
│   └── 营业执照扫描件
├── 联系人信息
│   ├── 联系人姓名 *
│   ├── 联系人职位
│   └── 联系人邮箱 *
└── 备注说明
```

### 4. 承包商入驻申请页面 (`/settlement/contractor`)
```
承包商入驻申请
├── 基本信息
│   ├── 承包商公司名称 *
│   ├── 公司类型 *
│   ├── 服务范围 *
│   ├── 法定代表人 *
│   ├── 成立日期 *
│   ├── 注册资本
│   └── 公司地址 *
├── 证照信息
│   ├── 营业执照号 *
│   ├── 营业执照扫描件 *
│   └── 资质证书扫描件
├── 联系人信息
│   ├── 联系人姓名 *
│   ├── 联系电话 *
│   ├── 联系人职位
│   └── 联系人邮箱 *
└── 备注说明
```

### 5. 用户注册页面 (`/register`)
```
用户注册
├── 用户类型 *（企业用户/承包商用户/系统管理员）
├── 用户名 *
├── 密码 *
├── 确认密码 *
├── 姓名 *
├── 手机号 *
├── 邮箱
└── 根据用户类型显示不同字段
    ├── 企业用户：企业名称、职位
    ├── 承包商用户：承包商公司名称
    └── 系统管理员：授权码、所属部门
```

### 6. 忘记密码页面 (`/forgot-password`)
```
找回密码
├── 手机号/邮箱 *
└── [发送重置链接]
```

## 🔄 完整的用户流程

### 流程1：企业入驻 + 用户注册
```
1. 访问登录页面
   ↓
2. 点击"立即申请"进入入驻选择页面
   ↓
3. 选择"企业入驻"
   ↓
4. 填写企业信息提交申请
   ↓
5. 等待管理员审核（3个工作日）
   ↓
6. 审核通过后，企业被创建
   ↓
7. 点击"注册账号"
   ↓
8. 选择"企业用户"类型
   ↓
9. 填写个人信息和企业名称
   ↓
10. 注册成功，可以登录
```

### 流程2：承包商入驻 + 用户注册
```
1. 访问登录页面
   ↓
2. 点击"立即申请"进入入驻选择页面
   ↓
3. 选择"承包商入驻"
   ↓
4. 填写承包商信息提交申请
   ↓
5. 等待管理员审核（3个工作日）
   ↓
6. 审核通过后，承包商被创建
   ↓
7. 点击"注册账号"
   ↓
8. 选择"承包商用户"类型
   ↓
9. 填写个人信息和承包商公司名称
   ↓
10. 注册成功，可以登录
```

### 流程3：已有公司的用户注册
```
1. 访问登录页面
   ↓
2. 点击"注册账号"
   ↓
3. 选择用户类型
   ↓
4. 填写个人信息
   ↓
5. 填写所属公司名称（必须是已审核通过的公司）
   ↓
6. 注册成功，可以登录
```

## 📁 新增的文件

### 前端文件
1. `/web/src/views/SettlementChoice.vue` - 入驻选择页面
2. `/web/src/views/EnterpriseSettlement.vue` - 企业入驻申请页面
3. `/web/src/views/ContractorSettlement.vue` - 承包商入驻申请页面
4. `/web/src/views/ForgotPassword.vue` - 忘记密码页面

### 修改的文件
1. `/web/src/views/UserLogin.vue` - 登录页面
2. `/web/src/views/UserRegister.vue` - 用户注册页面
3. `/web/src/router/index.ts` - 路由配置

## 🎨 页面设计特点

### 入驻选择页面
- **渐变背景**：紫色渐变，吸引眼球
- **卡片式设计**：两个大卡片，清晰区分
- **悬停效果**：卡片悬停时上移并变色
- **图标展示**：使用SVG图标增强视觉效果

### 入驻申请页面
- **分区设计**：基本信息、证照信息、联系人信息
- **左侧边框**：每个区域标题有彩色左边框
- **响应式布局**：表单字段自适应排列
- **文件上传**：支持营业执照和资质证书上传

### 登录页面
- **简洁链接**：注册和忘记密码使用文字链接
- **醒目入驻按钮**：渐变色按钮，突出入驻入口
- **清晰分隔**：使用分隔线区分不同功能区

## 🔧 技术实现

### 路由配置
```typescript
{
  path: '/settlement',
  name: 'SettlementChoice',
  component: SettlementChoice,
  meta: { requiresGuest: true }
},
{
  path: '/settlement/enterprise',
  name: 'EnterpriseSettlement',
  component: EnterpriseSettlement,
  meta: { requiresGuest: true }
},
{
  path: '/settlement/contractor',
  name: 'ContractorSettlement',
  component: ContractorSettlement,
  meta: { requiresGuest: true }
},
{
  path: '/forgot-password',
  name: 'ForgotPassword',
  component: ForgotPassword,
  meta: { requiresGuest: true }
}
```

### 企业入驻表单数据结构
```typescript
{
  companyName: string          // 企业名称
  legalPerson: string          // 法定代表人
  contactPhone: string         // 联系电话
  address: string              // 企业地址
  industryType: string         // 行业类型
  employeeCount: string        // 员工人数
  businessLicense: string      // 营业执照号
  licenseFile: File | null     // 营业执照扫描件
  contactName: string          // 联系人姓名
  contactPosition: string      // 联系人职位
  contactEmail: string         // 联系人邮箱
  remarks: string              // 备注说明
}
```

### 承包商入驻表单数据结构
```typescript
{
  companyName: string              // 承包商公司名称
  companyType: string              // 公司类型
  serviceScope: string             // 服务范围
  legalPerson: string              // 法定代表人
  establishDate: string            // 成立日期
  registeredCapital: number | null // 注册资本
  address: string                  // 公司地址
  businessLicense: string          // 营业执照号
  licenseFile: File | null         // 营业执照扫描件
  qualificationFile: File | null   // 资质证书扫描件
  contactName: string              // 联系人姓名
  contactPhone: string             // 联系电话
  contactPosition: string          // 联系人职位
  contactEmail: string             // 联系人邮箱
  remarks: string                  // 备注说明
}
```

## 🎯 后端API需求

### 1. 企业入驻申请接口
```
POST /api/settlement/enterprise
Content-Type: multipart/form-data

请求参数：
- companyName: 企业名称
- legalPerson: 法定代表人
- contactPhone: 联系电话
- address: 企业地址
- industryType: 行业类型
- employeeCount: 员工人数
- businessLicense: 营业执照号
- licenseFile: 营业执照扫描件（文件）
- contactName: 联系人姓名
- contactPosition: 联系人职位
- contactEmail: 联系人邮箱
- remarks: 备注说明

响应：
{
  "message": "申请提交成功",
  "application_id": 123
}
```

### 2. 承包商入驻申请接口
```
POST /api/settlement/contractor
Content-Type: multipart/form-data

请求参数：
- companyName: 承包商公司名称
- companyType: 公司类型
- serviceScope: 服务范围
- legalPerson: 法定代表人
- establishDate: 成立日期
- registeredCapital: 注册资本
- address: 公司地址
- businessLicense: 营业执照号
- licenseFile: 营业执照扫描件（文件）
- qualificationFile: 资质证书扫描件（文件，可选）
- contactName: 联系人姓名
- contactPhone: 联系电话
- contactPosition: 联系人职位
- contactEmail: 联系人邮箱
- remarks: 备注说明

响应：
{
  "message": "申请提交成功",
  "application_id": 124
}
```

### 3. 忘记密码接口
```
POST /api/forgot-password

请求参数：
{
  "contact": "手机号或邮箱"
}

响应：
{
  "message": "重置链接已发送"
}
```

## 📊 数据库设计建议

### 入驻申请表 (settlement_applications)
```sql
CREATE TABLE settlement_applications (
  application_id SERIAL PRIMARY KEY,
  application_type VARCHAR(20) NOT NULL, -- 'enterprise' or 'contractor'
  company_name VARCHAR(255) NOT NULL,
  legal_person VARCHAR(100) NOT NULL,
  contact_phone VARCHAR(20) NOT NULL,
  contact_email VARCHAR(100) NOT NULL,
  contact_name VARCHAR(100) NOT NULL,
  contact_position VARCHAR(100),
  address TEXT NOT NULL,
  business_license VARCHAR(100) NOT NULL,
  license_file_path VARCHAR(255),
  
  -- 企业特有字段
  industry_type VARCHAR(50),
  employee_count VARCHAR(20),
  
  -- 承包商特有字段
  company_type VARCHAR(50),
  service_scope VARCHAR(255),
  establish_date DATE,
  registered_capital DECIMAL(15,2),
  qualification_file_path VARCHAR(255),
  
  remarks TEXT,
  status VARCHAR(20) DEFAULT 'pending', -- pending, approved, rejected
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  reviewed_by INT,
  reviewed_at TIMESTAMP,
  review_comments TEXT
);
```

## ✅ 功能清单

### 已完成
- [x] 入驻选择页面
- [x] 企业入驻申请页面
- [x] 承包商入驻申请页面
- [x] 忘记密码页面
- [x] 修改登录页面
- [x] 修改用户注册页面
- [x] 路由配置
- [x] 前端表单验证
- [x] 响应式设计
- [x] 无linting错误

### 待实现（后端）
- [ ] 企业入驻申请API
- [ ] 承包商入驻申请API
- [ ] 文件上传处理
- [ ] 入驻申请审核管理
- [ ] 忘记密码API
- [ ] 邮件/短信通知
- [ ] 用户注册时验证公司是否存在

## 🧪 测试场景

### 场景1：企业入驻申请
1. 访问 `/login`
2. 点击"立即申请 →"
3. 选择"企业入驻"
4. 填写所有必填字段
5. 上传营业执照
6. 提交申请
7. 验证成功提示
8. 验证3秒后跳转到登录页

### 场景2：承包商入驻申请
1. 访问 `/login`
2. 点击"立即申请 →"
3. 选择"承包商入驻"
4. 填写所有必填字段
5. 上传营业执照和资质证书
6. 提交申请
7. 验证成功提示
8. 验证3秒后跳转到登录页

### 场景3：用户注册
1. 访问 `/login`
2. 点击"注册账号"
3. 选择用户类型
4. 填写个人信息
5. 填写公司信息
6. 提交注册
7. 验证成功提示

### 场景4：忘记密码
1. 访问 `/login`
2. 点击"忘记密码"
3. 输入手机号或邮箱
4. 点击发送
5. 验证成功提示
6. 验证3秒后跳转到登录页

## 💡 后续优化建议

1. **入驻申请管理后台**
   - 管理员查看所有申请
   - 审核通过/拒绝
   - 查看申请详情

2. **邮件/短信通知**
   - 申请提交成功通知
   - 审核结果通知
   - 密码重置链接

3. **文件管理**
   - 文件大小限制
   - 文件格式验证
   - 文件预览功能

4. **进度追踪**
   - 申请状态查询
   - 审核进度显示

5. **表单优化**
   - 自动保存草稿
   - 表单分步填写
   - 智能表单验证

---

**更新日期**: 2025-11-10
**状态**: ✅ 前端已完成，后端待实现

