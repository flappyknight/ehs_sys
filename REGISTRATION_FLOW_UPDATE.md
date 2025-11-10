# 注册流程优化说明

## 📋 更新内容

### 问题
1. 从登录页面点击注册后，用户仍可以在注册页面修改身份类型，不符合逻辑
2. 只有一个"立即注册"按钮，无法区分企业和承包商入驻

### 解决方案
1. ✅ 登录页面添加两个独立的入驻按钮：**企业入驻** 和 **承包商入驻**
2. ✅ 点击对应按钮后，注册页面的身份类型固定，不可修改
3. ✅ 页面标题根据入驻类型动态显示
4. ✅ 使用徽章样式显示固定的身份类型

## 🎨 界面改进

### 登录页面
```
┌─────────────────────────────────────────┐
│        EHS 系统登录                      │
│                                         │
│  [身份选择: 企业 ▼]                     │
│  [用户名输入框]                         │
│  [密码输入框]                           │
│  [登录按钮]                             │
│                                         │
│  ─────────────────────────────────────  │
│                                         │
│  还没有账号？                           │
│  ┌──────────────┐  ┌──────────────┐   │
│  │  企业入驻    │  │ 承包商入驻   │   │
│  └──────────────┘  └──────────────┘   │
│  (蓝色边框)        (绿色边框)         │
└─────────────────────────────────────────┘
```

### 企业入驻页面
```
┌─────────────────────────────────────────┐
│     EHS 系统 - 企业入驻                  │
│                                         │
│  入驻类型                               │
│  ┌───────────────────────────────────┐ │
│  │  [企业入驻] (蓝色徽章，不可修改)   │ │
│  └───────────────────────────────────┘ │
│                                         │
│  [用户名]                               │
│  [密码]                                 │
│  [确认密码]                             │
│  [姓名]                                 │
│  [手机号]                               │
│  [邮箱]                                 │
│  [企业名称] *                           │
│  [职位]                                 │
│                                         │
│  [注册按钮]                             │
└─────────────────────────────────────────┘
```

### 承包商入驻页面
```
┌─────────────────────────────────────────┐
│     EHS 系统 - 承包商入驻                │
│                                         │
│  入驻类型                               │
│  ┌───────────────────────────────────┐ │
│  │ [承包商入驻] (绿色徽章，不可修改)  │ │
│  └───────────────────────────────────┘ │
│                                         │
│  [用户名]                               │
│  [密码]                                 │
│  [确认密码]                             │
│  [姓名]                                 │
│  [手机号]                               │
│  [邮箱]                                 │
│  [承包商公司名称] *                     │
│                                         │
│  [注册按钮]                             │
└─────────────────────────────────────────┘
```

## 🔧 技术实现

### 1. 登录页面改进

**文件**: `/web/src/views/UserLogin.vue`

#### 改动点：
1. **移除单个注册按钮**，改为两个入驻按钮
2. **添加两个导航函数**：
   - `goToEnterpriseRegister()` - 跳转到企业入驻
   - `goToContractorRegister()` - 跳转到承包商入驻

#### 代码示例：
```vue
<div class="register-buttons">
  <button
    type="button"
    class="register-button enterprise"
    @click="goToEnterpriseRegister"
  >
    企业入驻
  </button>
  <button
    type="button"
    class="register-button contractor"
    @click="goToContractorRegister"
  >
    承包商入驻
  </button>
</div>
```

```typescript
const goToEnterpriseRegister = () => {
  router.push('/register?type=enterprise')
}

const goToContractorRegister = () => {
  router.push('/register?type=contractor')
}
```

### 2. 注册页面改进

**文件**: `/web/src/views/UserRegister.vue`

#### 改动点：
1. **从URL参数获取用户类型**
2. **根据URL参数决定是否显示身份选择下拉框**
3. **固定身份时显示徽章样式**
4. **动态页面标题**

#### 核心逻辑：
```typescript
// 从URL参数获取用户类型
const route = useRoute()

// 判断是否可以修改身份类型
const isUserTypeFixed = computed(() => {
  return route.query.type !== undefined
})

// 动态页面标题
const pageTitle = computed(() => {
  if (form.userType === 'enterprise') {
    return 'EHS 系统 - 企业入驻'
  } else if (form.userType === 'contractor') {
    return 'EHS 系统 - 承包商入驻'
  } else {
    return 'EHS 系统注册'
  }
})

// 初始化时设置用户类型
onMounted(() => {
  const typeParam = route.query.type as string
  if (typeParam === 'enterprise' || typeParam === 'contractor') {
    form.userType = typeParam
  }
})
```

#### 模板逻辑：
```vue
<!-- 如果URL没有type参数，显示下拉框 -->
<div class="form-group" v-if="!isUserTypeFixed">
  <label for="userType">身份选择 *</label>
  <select v-model="form.userType" ...>
    <option value="enterprise">企业</option>
    <option value="contractor">承包商</option>
  </select>
</div>

<!-- 如果URL有type参数，显示固定徽章 -->
<div class="form-group" v-else>
  <label for="userTypeDisplay">入驻类型</label>
  <div class="user-type-display">
    <span class="type-badge" :class="form.userType">
      {{ form.userType === 'enterprise' ? '企业入驻' : '承包商入驻' }}
    </span>
  </div>
</div>
```

## 🎨 样式设计

### 登录页面按钮样式
```css
.register-buttons {
  display: flex;
  gap: 12px;
  width: 100%;
}

.register-button {
  flex: 1;
  padding: 10px 16px;
  /* ... */
}

.register-button.enterprise {
  color: #007bff;
  border-color: #007bff;
}

.register-button.contractor {
  color: #28a745;
  border-color: #28a745;
}
```

### 注册页面徽章样式
```css
.user-type-display {
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.type-badge {
  display: inline-block;
  padding: 6px 16px;
  border-radius: 20px;
  font-weight: 500;
  color: white;
}

.type-badge.enterprise {
  background-color: #007bff;
}

.type-badge.contractor {
  background-color: #28a745;
}
```

## 📊 用户流程

### 企业入驻流程
```
1. 用户访问登录页面
   ↓
2. 点击"企业入驻"按钮
   ↓
3. 跳转到 /register?type=enterprise
   ↓
4. 页面显示"EHS 系统 - 企业入驻"
   ↓
5. 身份类型固定为"企业入驻"（蓝色徽章）
   ↓
6. 填写企业相关信息
   ↓
7. 提交注册
```

### 承包商入驻流程
```
1. 用户访问登录页面
   ↓
2. 点击"承包商入驻"按钮
   ↓
3. 跳转到 /register?type=contractor
   ↓
4. 页面显示"EHS 系统 - 承包商入驻"
   ↓
5. 身份类型固定为"承包商入驻"（绿色徽章）
   ↓
6. 填写承包商相关信息
   ↓
7. 提交注册
```

## 🔄 URL参数说明

### 企业入驻
- URL: `/register?type=enterprise`
- 页面标题: "EHS 系统 - 企业入驻"
- 身份类型: 固定为"企业"，不可修改
- 显示字段: 企业名称、职位

### 承包商入驻
- URL: `/register?type=contractor`
- 页面标题: "EHS 系统 - 承包商入驻"
- 身份类型: 固定为"承包商"，不可修改
- 显示字段: 承包商公司名称

### 直接访问注册页面（兼容）
- URL: `/register`（无参数）
- 页面标题: "EHS 系统注册"
- 身份类型: 可以通过下拉框选择
- 显示字段: 根据选择动态显示

## ✅ 优势

1. **用户体验更好**：
   - 明确的入驻入口
   - 避免用户困惑
   - 流程更加清晰

2. **逻辑更合理**：
   - 从企业入驻进入，身份就固定为企业
   - 从承包商入驻进入，身份就固定为承包商
   - 避免用户误操作

3. **视觉区分明显**：
   - 企业使用蓝色
   - 承包商使用绿色
   - 徽章样式醒目

4. **向后兼容**：
   - 直接访问 `/register` 仍然可以选择身份类型
   - 不影响现有功能

## 🧪 测试场景

### 场景1：企业入驻
1. 访问登录页面
2. 点击"企业入驻"按钮
3. 验证页面标题为"EHS 系统 - 企业入驻"
4. 验证显示蓝色"企业入驻"徽章
5. 验证只显示企业相关字段
6. 验证无法修改身份类型

### 场景2：承包商入驻
1. 访问登录页面
2. 点击"承包商入驻"按钮
3. 验证页面标题为"EHS 系统 - 承包商入驻"
4. 验证显示绿色"承包商入驻"徽章
5. 验证只显示承包商相关字段
6. 验证无法修改身份类型

### 场景3：直接访问注册页面
1. 直接访问 `/register`
2. 验证页面标题为"EHS 系统注册"
3. 验证显示身份选择下拉框
4. 验证可以选择不同身份类型

## 📝 注意事项

1. **URL参数验证**：系统会验证type参数，只接受 `enterprise` 和 `contractor`
2. **默认值**：如果URL参数无效，默认显示为企业类型
3. **页面刷新**：刷新页面后，身份类型保持不变（通过URL参数）
4. **返回登录**：点击"立即登录"按钮返回登录页面

## 🎯 后续建议

1. 可以考虑添加面包屑导航
2. 可以添加进度指示器
3. 可以添加表单自动保存功能
4. 可以添加返回上一步功能

---

**更新日期**: 2025-11-10
**状态**: ✅ 已完成并测试通过

