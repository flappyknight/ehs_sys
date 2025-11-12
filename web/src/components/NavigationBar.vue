<template>
  <nav class="navigation">
    <div class="nav-container">
      <div class="nav-brand">
        <h2>EHS 管理系统</h2>
      </div>

      <div class="nav-menu">
        <router-link
          v-for="item in visibleNavItems"
          :key="item.key"
          :to="item.path || '#'"
          class="nav-item"
          exact-active-class="active"
        >
          {{ item.label }}
        </router-link>
      </div>

      <div class="nav-user">
        <span class="user-info">
          {{ authStore.user?.username }}
          <span class="user-role">({{ getUserRoleText() }})</span>
        </span>
        <button @click="handleLogout" class="logout-btn">
          退出登录
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { NavItem, UserRole } from '@/types/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// 所有可能的导航项
const allNavItems: NavItem[] = [
  { key: 'overview', label: '总览', path: '/dashboard' },
  { key: 'enterprise', label: '企业管理', path: '/enterprise' },
  { key: 'contractor', label: '供应商管理', path: '/contractor' },
  { key: 'approval', label: '审批', path: '/approval' }
]

// 检查下拉菜单是否应该高亮
const isDropdownActive = (item: NavItem): boolean => {
  if (!item.children) return false

  return item.children.some(child =>
    child.path && route.path === child.path
  )
}

// 获取当前用户角色
const getCurrentUserRole = (): UserRole => {
  const user = authStore.user
  console.log(user)
  if (!user) return 'enterprise_site_staff'

  if (user.user_type === 'admin') {
    return 'admin'
  } else if (user.user_type === 'enterprise' && user.enterprise_user) {
    return `enterprise_${user.enterprise_user.role_type}` as UserRole
  } else if (user.user_type === 'contractor' && user.contractor_user) {
    return `contractor_${user.contractor_user.role_type}` as UserRole
  }

  return 'enterprise_site_staff'
}

// 根据用户角色获取可见的导航项
const getVisibleNavKeys = (role: UserRole): string[] => {
  // 所有用户都可以看到所有导航项
  return ['overview', 'enterprise', 'contractor', 'approval']
}

// 计算可见的导航项
const visibleNavItems = computed(() => {
  return allNavItems
})

// 获取用户角色显示文本
const getUserRoleText = (): string => {
  const role = getCurrentUserRole()
  const roleTexts: Record<UserRole, string> = {
    admin: '系统管理员',
    enterprise_manager: '企业管理员',
    enterprise_approver: '企业审批员',
    enterprise_site_staff: '企业现场人员',
    contractor_manager: '承包商管理员',
    contractor_approver: '承包商审批员',
    contractor_site_staff: '承包商现场人员'
  }
  return roleTexts[role] || '用户'
}

// 处理登出
const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.navigation {
  background: #fff;
  border-bottom: 1px solid #e5e5e5;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.nav-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  height: 60px;
}

.nav-brand h2 {
  margin: 0;
  color: #333;
  font-size: 20px;
  font-weight: 600;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 0;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  color: #666;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
  border: none;
  background: none;
  cursor: pointer;
  height: 60px;
}

.nav-item:hover {
  color: #007bff;
  background-color: #f8f9fa;
}

/* 使用自定义的 active 类而不是 router-link-active */
.nav-item.active {
  color: #007bff;
  background-color: #e3f2fd;
}

.nav-dropdown {
  position: relative;
}

.dropdown-toggle {
  display: flex;
  align-items: center;
  gap: 5px;
}

.dropdown-arrow {
  font-size: 10px;
  transition: transform 0.3s;
}

.nav-dropdown:hover .dropdown-arrow {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  background: white;
  border: 1px solid #e5e5e5;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  min-width: 150px;
  opacity: 0;
  visibility: hidden;
  transform: translateY(-10px);
  transition: all 0.3s;
  z-index: 1000;
}

.nav-dropdown:hover .dropdown-menu {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.dropdown-item {
  display: block;
  padding: 12px 16px;
  color: #666;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.3s;
}

.dropdown-item:hover {
  color: #007bff;
  background-color: #f8f9fa;
}

.dropdown-item.active {
  color: #007bff;
  background-color: #e3f2fd;
}

.dropdown-item:first-child {
  border-radius: 4px 4px 0 0;
}

.dropdown-item:last-child {
  border-radius: 0 0 4px 4px;
}

.nav-user {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-info {
  font-size: 14px;
  color: #666;
}

.user-role {
  color: #999;
  font-size: 12px;
}

.logout-btn {
  padding: 8px 16px;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.logout-btn:hover {
  background-color: #c82333;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .nav-container {
    padding: 0 15px;
  }

  .nav-menu {
    gap: 0;
  }

  .nav-item {
    padding: 15px 10px;
    font-size: 13px;
  }

  .user-info {
    display: none;
  }
}
</style>
