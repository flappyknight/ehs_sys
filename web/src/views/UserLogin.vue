<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="login-title">EHS 系统登录</h1>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="userType">身份选择</label>
          <select
            id="userType"
            v-model="form.userType"
            class="form-select"
            :disabled="authStore.loading"
          >
            <option value="enterprise">企业</option>
            <option value="contractor">承包商</option>
            <option value="admin">系统管理</option>
          </select>
        </div>

        <div class="form-group">
          <label for="username">用户名</label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            placeholder="请输入用户名"
            required
            :disabled="authStore.loading"
          />
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            required
            :disabled="authStore.loading"
          />
        </div>

        <div v-if="authStore.error" class="error-message">
          {{ authStore.error }}
        </div>

        <button
          type="submit"
          class="login-button"
          :disabled="authStore.loading"
        >
          {{ authStore.loading ? '登录中...' : '登录' }}
        </button>

        <div class="action-links">
          <button
            type="button"
            class="link-button"
            @click="goToRegister"
            :disabled="authStore.loading"
          >
            注册账号
          </button>
          <span class="separator">|</span>
          <button
            type="button"
            class="link-button"
            @click="goToForgotPassword"
            :disabled="authStore.loading"
          >
            忘记密码
          </button>
        </div>

        <div class="settlement-section">
          <p class="settlement-text">企业或承包商入驻</p>
          <button
            type="button"
            class="settlement-link"
            @click="goToSettlement"
            :disabled="authStore.loading"
          >
            立即申请 →
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { LoginForm } from '@/types/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive<LoginForm>({
  username: '',
  password: '',
  userType: 'enterprise'
})

const handleLogin = async () => {
  // 使用 auth store 的 login 方法，而不是直接调用 apiService
  const success = await authStore.login(form)

  if (success) {
    // 登录成功，跳转到仪表板
    router.push('/dashboard')
  }
  // 错误信息已经在 auth store 中设置，模板会自动显示
}

const goToRegister = () => {
  router.push('/register')
}

const goToForgotPassword = () => {
  router.push('/forgot-password')
}

const goToSettlement = () => {
  router.push('/settlement')
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 400px;
}

.login-title {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
  font-size: 24px;
  font-weight: 600;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 500;
  color: #555;
}

.form-group input,
.form-select {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-select:focus {
  outline: none;
  border-color: #007bff;
}

.form-group input:disabled,
.form-select:disabled {
  background-color: #f8f9fa;
  cursor: not-allowed;
}

.form-select {
  cursor: pointer;
  background-color: white;
}

.error-message {
  color: #dc3545;
  font-size: 14px;
  text-align: center;
  padding: 10px;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
}

.login-button {
  padding: 12px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
}

.login-button:hover:not(:disabled) {
  background-color: #0056b3;
}

.login-button:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.action-links {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  padding-top: 16px;
}

.link-button {
  background: none;
  border: none;
  color: #007bff;
  font-size: 14px;
  cursor: pointer;
  transition: color 0.3s;
  padding: 4px 8px;
}

.link-button:hover:not(:disabled) {
  color: #0056b3;
  text-decoration: underline;
}

.link-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.separator {
  color: #ddd;
  font-size: 14px;
}

.settlement-section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #eee;
  text-align: center;
}

.settlement-text {
  color: #666;
  font-size: 14px;
  margin-bottom: 12px;
}

.settlement-link {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 10px 24px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.settlement-link:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.settlement-link:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
