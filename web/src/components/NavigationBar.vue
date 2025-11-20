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
  { key: 'contractor', label: '承包商管理', path: '/contractor' },
  { key: 'application', label: '申请', path: '/application' },
  { key: 'approval', label: '审批', path: '/approval' },
  { key: 'ticket', label: '工单', path: '/enterprise/tickets' }
]

// 检查下拉菜单是否应该高亮
const isDropdownActive = (item: NavItem): boolean => {
  if (!item.children) return false

  return item.children.some(child =>
    child.path && route.path === child.path
  )
}

// 根据 role_level 获取可见的导航项
const getVisibleNavKeys = (roleLevel: number | undefined, userStatus: number | undefined): string[] => {
  if (roleLevel === undefined || roleLevel === null) {
    return ['overview']
  }

  // role_level: -1 用户还未选择角色（不考虑，进不了页面）
  // role_level: 0 且 user_status=1 系统管理员（最高权限，能看到所有选项）
  if (roleLevel === 0 && userStatus === 1) {
    return ['overview', 'enterprise', 'contractor', 'application', 'approval', 'ticket']
  }

  // role_level: 1 企业管理员
  // 企业管理、承包商管理、审批三个选项
  if (roleLevel === 1) {
    return ['overview', 'enterprise', 'contractor', 'approval']
  }

  // role_level: 2 企业员工
  // 总览、申请、工单三个选项，去掉审批选项
  if (roleLevel === 2) {
    return ['overview', 'application', 'ticket']
  }

  // role_level: 3 承包商管理员
  // 企业管理能展示的只能是当前用户对应的供应商，将承包商管理选项替换为申请选项
  if (roleLevel === 3) {
    return ['overview', 'enterprise', 'application']
  }

  // role_level: 4 承包商员工
  // 只能有申请选项，没有审批、企业管理、承包商管理选项
  if (roleLevel === 4) {
    return ['overview', 'application']
  }

  // 默认只显示总览
  return ['overview']
}

// 计算可见的导航项
const visibleNavItems = computed(() => {
  const user = authStore.user
  const roleLevel = user?.role_level
  const userStatus = user?.user_status
  const visibleKeys = getVisibleNavKeys(roleLevel, userStatus)
  
  return allNavItems.filter(item => visibleKeys.includes(item.key))
})

// 获取用户角色显示文本
const getUserRoleText = (): string => {
  const user = authStore.user
  if (!user) return '用户'

  const roleLevel = user.role_level
  if (roleLevel === undefined || roleLevel === null) {
    return '用户'
  }

  const roleTexts: Record<number, string> = {
    0: '系统管理员',
    1: '企业管理员',
    2: '企业员工',
    3: '承包商管理员',
    4: '承包商员工'
  }

  return roleTexts[roleLevel] || '用户'
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
