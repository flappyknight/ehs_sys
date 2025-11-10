import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Login from '@/views/UserLogin.vue'
import Register from '@/views/UserRegister.vue'
import ForgotPassword from '@/views/ForgotPassword.vue'
import SettlementChoice from '@/views/SettlementChoice.vue'
import EnterpriseSettlement from '@/views/EnterpriseSettlement.vue'
import ContractorSettlement from '@/views/ContractorSettlement.vue'
import Dashboard from '@/views/UserDashboard.vue'
import ProjectList from '@/views/ProjectList.vue'
import ProjectDetail from '@/views/ProjectDetail.vue'
import ContractorViews from '@/views/ContractorViews.vue'
import AreaManagement from '@/views/AreaManagement.vue'
import StaffManagement from '@/views/StaffManagement.vue'
import DepartmentMembers from '@/views/DepartmentMembers.vue'
import MainLayout from '@/layouts/MainLayout.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: Login,
      meta: { requiresGuest: true }
    },
    {
      path: '/register',
      name: 'Register',
      component: Register,
      meta: { requiresGuest: true }
    },
    {
      path: '/forgot-password',
      name: 'ForgotPassword',
      component: ForgotPassword,
      meta: { requiresGuest: true }
    },
    {
      path: '/settlement',
      name: 'SettlementChoice',
      component: SettlementChoice
      // 入驻申请页面允许任何人访问
    },
    {
      path: '/settlement/enterprise',
      name: 'EnterpriseSettlement',
      component: EnterpriseSettlement
      // 入驻申请页面允许任何人访问
    },
    {
      path: '/settlement/contractor',
      name: 'ContractorSettlement',
      component: ContractorSettlement
      // 入驻申请页面允许任何人访问
    },
    {
      path: '/',
      component: MainLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          redirect: '/dashboard'
        },
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: Dashboard
        },
        {
          path: 'projects',
          name: 'ProjectList',
          component: ProjectList
        },
        {
          path: 'projects/:id',
          name: 'ProjectDetail',
          component: ProjectDetail
        },
        {
          path: 'contractor',
          name: 'ContractorViews',
          component: ContractorViews
        },
        {
          path: 'areas',
          name: 'AreaManagement',
          component: AreaManagement
        },
        {
          path: 'staff',
          name: 'StaffManagement',
          component: StaffManagement
        },
        {
          path: 'staff/departments/:deptId/members',
          name: 'DepartmentMembers',
          component: DepartmentMembers
        }
      ]
    }
  ]
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // 只有在需要认证的页面才检查用户状态
  if (to.meta.requiresAuth || to.meta.requiresGuest) {
    // 检查用户认证状态
    if (!authStore.isAuthenticated) {
      await authStore.checkAuth()
    }

    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
      next('/login')
    } else if (to.meta.requiresGuest && authStore.isAuthenticated) {
      next('/dashboard')
    } else {
      next()
    }
  } else {
    // 对于不需要认证的页面，直接放行
    next()
  }
})

export default router
