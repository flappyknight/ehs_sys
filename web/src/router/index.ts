import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Login from '@/views/UserLogin.vue'
import Register from '@/views/UserRegister.vue'
import ForgotPassword from '@/views/ForgotPassword.vue'
import ResetPassword from '@/views/ResetPassword.vue'
import SettlementChoice from '@/views/SettlementChoice.vue'
import EnterpriseSettlement from '@/views/EnterpriseSettlement.vue'
import ContractorSettlement from '@/views/ContractorSettlement.vue'
import AdminPermissionApply from '@/views/AdminPermissionApply.vue'
import EnterprisePermissionApply from '@/views/EnterprisePermissionApply.vue'
import ContractorPermissionApply from '@/views/ContractorPermissionApply.vue'
import EnterpriseEdit from '@/views/EnterpriseEdit.vue'
import ContractorEdit from '@/views/ContractorEdit.vue'
import EnterpriseBind from '@/views/EnterpriseBind.vue'
import ContractorBind from '@/views/ContractorBind.vue'
import Dashboard from '@/views/UserDashboard.vue'
import ProjectList from '@/views/ProjectList.vue'
import ProjectDetail from '@/views/ProjectDetail.vue'
import ContractorViews from '@/views/ContractorViews.vue'
import AreaManagement from '@/views/AreaManagement.vue'
import StaffManagement from '@/views/StaffManagement.vue'
import DepartmentMembers from '@/views/DepartmentMembers.vue'
import MainLayout from '@/layouts/MainLayout.vue'
// 企业管理相关页面
import EnterpriseManagement from '@/views/EnterpriseManagement.vue'
import EnterpriseDetail from '@/views/EnterpriseDetail.vue'
import EnterpriseStaff from '@/views/EnterpriseStaff.vue'
import EnterpriseTickets from '@/views/EnterpriseTickets.vue'
import EnterpriseRoles from '@/views/EnterpriseRoles.vue'
import EnterpriseApproval from '@/views/EnterpriseApproval.vue'
// 供应商管理相关页面
import ContractorManagement from '@/views/ContractorManagement.vue'
import ContractorDetail from '@/views/ContractorDetail.vue'
import ContractorStaff from '@/views/ContractorStaff.vue'
import ContractorApproval from '@/views/ContractorApproval.vue'
import ContractorCooperation from '@/views/ContractorCooperation.vue'
// 审批相关页面
import ApprovalManagement from '@/views/ApprovalManagement.vue'
import ApprovalEnterprise from '@/views/ApprovalEnterprise.vue'
import ApprovalContractor from '@/views/ApprovalContractor.vue'
import ApprovalStaff from '@/views/ApprovalStaff.vue'
import ApplicationManagement from '@/views/ApplicationManagement.vue'

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
      path: '/reset-password',
      name: 'ResetPassword',
      component: ResetPassword,
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
      path: '/admin/permission-apply',
      name: 'AdminPermissionApply',
      component: AdminPermissionApply,
      meta: { requiresAuth: true }
    },
    {
      path: '/enterprise/permission-apply',
      name: 'EnterprisePermissionApply',
      component: EnterprisePermissionApply,
      meta: { requiresAuth: true }
    },
    {
      path: '/enterprise/edit',
      name: 'EnterpriseEdit',
      component: EnterpriseEdit,
      meta: { requiresAuth: true }
    },
    {
      path: '/contractor/permission-apply',
      name: 'ContractorPermissionApply',
      component: ContractorPermissionApply,
      meta: { requiresAuth: true }
    },
    {
      path: '/contractor/edit',
      name: 'ContractorEdit',
      component: ContractorEdit,
      meta: { requiresAuth: true }
    },
    {
      path: '/enterprise/bind',
      name: 'EnterpriseBind',
      component: EnterpriseBind,
      meta: { requiresAuth: true }
    },
    {
      path: '/contractor/bind',
      name: 'ContractorBind',
      component: ContractorBind,
      meta: { requiresAuth: true }
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
        // 企业管理
        {
          path: 'enterprise',
          name: 'EnterpriseManagement',
          component: EnterpriseManagement
        },
        {
          path: 'enterprise/detail',
          name: 'EnterpriseDetail',
          component: EnterpriseDetail
        },
        {
          path: 'enterprise/staff',
          name: 'EnterpriseStaff',
          component: EnterpriseStaff
        },
        {
          path: 'enterprise/tickets',
          name: 'EnterpriseTickets',
          component: EnterpriseTickets
        },
        {
          path: 'enterprise/roles',
          name: 'EnterpriseRoles',
          component: EnterpriseRoles
        },
        {
          path: 'enterprise/approval',
          name: 'EnterpriseApproval',
          component: EnterpriseApproval
        },
        // 供应商管理
        {
          path: 'contractor',
          name: 'ContractorManagement',
          component: ContractorManagement
        },
        {
          path: 'contractor/detail',
          name: 'ContractorDetail',
          component: ContractorDetail
        },
        {
          path: 'contractor/staff',
          name: 'ContractorStaff',
          component: ContractorStaff
        },
        {
          path: 'contractor/approval',
          name: 'ContractorApproval',
          component: ContractorApproval
        },
        {
          path: 'contractor/cooperation',
          name: 'ContractorCooperation',
          component: ContractorCooperation
        },
        // 审批
        {
          path: 'approval',
          name: 'ApprovalManagement',
          component: ApprovalManagement
        },
        {
          path: 'approval/enterprise',
          name: 'ApprovalEnterprise',
          component: ApprovalEnterprise
        },
        {
          path: 'approval/contractor',
          name: 'ApprovalContractor',
          component: ApprovalContractor
        },
        {
          path: 'approval/staff',
          name: 'ApprovalStaff',
          component: ApprovalStaff
        },
        // 申请
        {
          path: 'application',
          name: 'ApplicationManagement',
          component: ApplicationManagement
        },
        // 保留旧路由（兼容性）
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
          path: 'contractor-old',
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

// 权限检查函数：根据用户状态返回应该重定向的路径
// 返回null表示允许访问，返回路径字符串表示需要重定向
function checkUserPermission(user: any): string | null {
  if (!user) return '/login'

  const userType = user.user_type
  const userStatus = user.user_status ?? 0

  // 检查user_status是否为1（审核通过）
  if (userStatus === 1) {
    // 审核通过，允许访问
    return null
  } else {
    // user_status不为1，需要跳转到权限申请页面
    if (userType === 'admin') {
      return '/admin/permission-apply'
    } else if (userType === 'enterprise') {
      return '/enterprise/permission-apply'
    } else if (userType === 'contractor') {
      return '/contractor/permission-apply'
    }
  }

  // 默认不允许访问（未知状态）
  return '/login'
}

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // 对于需要认证的页面
  if (to.meta.requiresAuth) {
    // 检查用户认证状态
    if (!authStore.isAuthenticated) {
      await authStore.checkAuth()
    }

    if (!authStore.isAuthenticated) {
      next('/login')
      return
    }

    // 检查用户权限状态
    const redirectPath = checkUserPermission(authStore.user)
    
    // 如果当前页面是信息填报页面，允许访问（即使状态不符合）
    const isInfoPage = [
      '/admin/permission-apply',
      '/enterprise/permission-apply',
      '/enterprise/edit',
      '/contractor/permission-apply',
      '/contractor/edit',
      '/enterprise/bind',
      '/contractor/bind'
    ].includes(to.path)

    if (redirectPath && !isInfoPage) {
      // 用户状态不符合要求，且不是信息填报页面，重定向
      next(redirectPath)
      return
    }

    // 如果当前页面是信息填报页面，但用户状态已经通过审核，重定向到主页面
    if (isInfoPage && redirectPath === null) {
      next('/dashboard')
      return
    }

    // 允许访问
    next()
  } 
  // 对于访客页面（登录、注册等）
  else if (to.meta.requiresGuest) {
    // 只有在已经有用户信息的情况下才检查
    if (authStore.isAuthenticated) {
      // 检查用户权限，如果已通过审核，跳转到主页面
      const redirectPath = checkUserPermission(authStore.user)
      if (redirectPath === null) {
        next('/dashboard')
      } else {
        // 如果用户状态不符合要求，跳转到相应的页面
        next(redirectPath)
      }
    } else {
      // 如果没有用户信息，直接放行，不调用checkAuth
      next()
    }
  } 
  // 对于不需要认证的页面，直接放行
  else {
    next()
  }
})

export default router
