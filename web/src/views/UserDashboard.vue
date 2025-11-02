<template>
  <div class="dashboard">
    <!-- 移除这行：<NavigationBar /> -->

    <main class="dashboard-content">
      <div class="welcome-card">
        <h2>欢迎使用 EHS 管理系统</h2>
        <p>您已成功登录系统</p>

        <div v-if="authStore.user" class="user-details">
          <h3>用户信息</h3>
          <div class="info-grid">
            <div class="info-item">
              <label>用户名:</label>
              <span>{{ authStore.user.username }}</span>
            </div>
            <div class="info-item">
              <label>用户类型:</label>
              <span>{{ getUserTypeText(authStore.user.user_type) }}</span>
            </div>
            <div v-if="authStore.user.enterprise_user" class="info-item">
              <label>姓名:</label>
              <span>{{ authStore.user.enterprise_user.name }}</span>
            </div>
            <div v-if="authStore.user.contractor_user" class="info-item">
              <label>姓名:</label>
              <span>{{ authStore.user.contractor_user.name }}</span>
            </div>
            <div v-if="authStore.user.enterprise_user" class="info-item">
              <label>角色:</label>
              <span>{{ getRoleText(authStore.user.enterprise_user.role_type) }}</span>
            </div>
            <div v-if="authStore.user.contractor_user" class="info-item">
              <label>角色:</label>
              <span>{{ getRoleText(authStore.user.contractor_user.role_type) }}</span>
            </div>
          </div>
        </div>

        <div class="quick-actions">
          <h3>快速操作</h3>
          <div class="action-grid">
            <div class="action-card" @click="navigateTo('/overview')">
              <div class="action-icon">📊</div>
              <div class="action-title">系统总览</div>
              <div class="action-desc">查看系统整体状态</div>
            </div>

            <div v-if="canAccess('operation')" class="action-card" @click="navigateTo('/operation')">
              <div class="action-icon">🔧</div>
              <div class="action-title">作业管理</div>
              <div class="action-desc">管理作业任务</div>
            </div>

            <div v-if="canAccess('approval')" class="action-card" @click="navigateTo('/approval')">
              <div class="action-icon">✅</div>
              <div class="action-title">审批中心</div>
              <div class="action-desc">处理待审批事项</div>
            </div>

            <div v-if="canAccess('personnel')" class="action-card" @click="navigateTo('/personnel')">
              <div class="action-icon">👥</div>
              <div class="action-title">人员管理</div>
              <div class="action-desc">管理人员信息</div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
// 移除这行：import NavigationBar from '@/components/NavigationBar.vue'
import type { UserRole } from '@/types/auth'

const router = useRouter()
const authStore = useAuthStore()

const getUserTypeText = (userType: string) => {
  const typeMap = {
    admin: '管理员',
    enterprise: '企业用户',
    contractor: '承包商用户'
  }
  return typeMap[userType as keyof typeof typeMap] || userType
}

const getRoleText = (roleType: string) => {
  const roleMap = {
    manager: '管理员',
    approver: '审批员',
    site_staff: '现场人员'
  }
  return roleMap[roleType as keyof typeof roleMap] || roleType
}

// 获取当前用户角色
const getCurrentUserRole = (): UserRole => {
  const user = authStore.user
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

// 检查用户是否有权限访问某个功能
const canAccess = (feature: string): boolean => {
  const userRole = getCurrentUserRole()

  const permissions: Record<UserRole, string[]> = {
    admin: ['overview', 'company', 'project', 'site', 'personnel', 'operation', 'approval', 'contractor'],
    enterprise_manager: ['overview', 'project', 'site', 'personnel', 'operation', 'approval', 'contractor'],
    enterprise_approver: ['overview', 'project', 'site', 'personnel', 'operation', 'approval', 'contractor'],
    enterprise_site_staff: ['overview', 'project', 'operation', 'approval'],
    contractor_manager: ['overview', 'project', 'personnel', 'operation', 'approval', 'plan_application', 'entry_registration'],
    contractor_approver: ['overview', 'operation', 'contractor', 'entry_registration'],
    contractor_site_staff: ['overview', 'operation', 'contractor', 'entry_registration']
  }

  return permissions[userRole]?.includes(feature) || false
}

// 导航到指定页面
const navigateTo = (path: string) => {
  router.push(path)
}
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.dashboard-content {
  padding: 30px;
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-card {
  background: white;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.welcome-card h2 {
  margin-top: 0;
  color: #333;
  font-size: 28px;
  margin-bottom: 10px;
}

.welcome-card > p {
  color: #666;
  font-size: 16px;
  margin-bottom: 30px;
}

.user-details {
  margin-bottom: 40px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.user-details h3 {
  margin-bottom: 20px;
  color: #555;
  font-size: 18px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
  margin-bottom: 30px;
}

.info-item {
  display: flex;
  gap: 10px;
  padding: 10px 0;
}

.info-item label {
  font-weight: 500;
  color: #666;
  min-width: 80px;
}

.info-item span {
  color: #333;
}

.quick-actions h3 {
  margin-bottom: 20px;
  color: #555;
  font-size: 18px;
  border-top: 1px solid #eee;
  padding-top: 20px;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.action-card {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.action-card:hover {
  background: #e9ecef;
  border-color: #007bff;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.action-icon {
  font-size: 32px;
  margin-bottom: 10px;
}

.action-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 5px;
}

.action-desc {
  font-size: 14px;
  color: #666;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard-content {
    padding: 20px 15px;
  }

  .welcome-card {
    padding: 20px;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .action-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 15px;
  }

  .action-card {
    padding: 15px;
  }
}
</style>
