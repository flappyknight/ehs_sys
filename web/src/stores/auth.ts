import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiService } from '@/services/api'
import type { User, LoginForm } from '@/types/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!user.value)

  // 检查认证状态
  const checkAuth = async () => {
    try {
      loading.value = true
      error.value = null
      const userData = await apiService.getCurrentUser()
      user.value = userData
      return true
    } catch (err) {
      console.error('Authentication check failed:', err)
      user.value = null
      return false
    } finally {
      loading.value = false
    }
  }

  // 登录
  const login = async (credentials: LoginForm) => {
    try {
      loading.value = true
      error.value = null

      const tokenResponse = await apiService.login(credentials)
      // 登录成功后获取用户信息
      await checkAuth()

      // 返回token响应，包含redirect_to和message信息
      return tokenResponse
    } catch (err) {
      error.value = err instanceof Error ? err.message : '登录失败'
      return null
    } finally {
      loading.value = false
    }
  }

  // 登出
  const logout = async () => {
    try {
      await apiService.logout()
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      user.value = null
    }
  }

  // 清除错误
  const clearError = () => {
    error.value = null
  }

  return {
    user,
    loading,
    error,
    isAuthenticated,
    checkAuth,
    login,
    logout,
    clearError
  }
})
