<template>
  <div class="department-members">
    <div class="page-header">
      <div class="header-left">
        <button @click="goBack" class="back-btn">← 返回</button>
        <div class="title-section">
          <h1>{{ departmentName || '部门成员' }}</h1>
          <p>管理部门成员信息</p>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading">
      加载中...
    </div>

    <div v-else-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-else>
      <div class="members-table-container">
        <table class="members-table">
          <thead>
            <tr>
              <th>姓名</th>
              <th>手机号</th>
              <th>邮箱</th>
              <th>职位</th>
              <th>角色</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="member in members" :key="member.user_id">
              <td>{{ member.name }}</td>
              <td>{{ member.phone }}</td>
              <td>{{ member.email }}</td>
              <td>{{ member.position || '-' }}</td>
              <td>
                <span class="role-badge" :class="getRoleClass(member.role_type)">
                  {{ getRoleText(member.role_type) }}
                </span>
              </td>
              <td>
                <span class="status-badge" :class="member.status ? 'active' : 'inactive'">
                  {{ member.status ? '正常' : '停用' }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button 
                    @click="editMember(member)" 
                    class="edit-btn"
                    v-if="canEditMember"
                  >
                    编辑
                  </button>
                  <button 
                    @click="viewMember(member)" 
                    class="view-btn"
                  >
                    查看
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="members.length === 0" class="empty-state">
        <p>该部门暂无成员</p>
      </div>
    </div>

    <!-- 编辑成员模态框 -->
    <EditMemberModal
      v-if="showEditModal"
      :member="selectedMember"
      @close="closeEditModal"
      @success="handleEditSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { apiService, type EnterpriseUserListItem } from '@/services/api'
import type { User } from '@/types/auth'
import EditMemberModal from '@/components/EditMemberModal.vue'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const error = ref('')
const members = ref<EnterpriseUserListItem[]>([])
const currentUser = ref<User | null>(null)
const showEditModal = ref(false)
const selectedMember = ref<EnterpriseUserListItem | null>(null)

const departmentId = computed(() => parseInt(route.params.deptId as string))
const departmentName = computed(() => route.query.deptName as string)

// 检查是否可以编辑成员
const canEditMember = computed(() => {
  if (!currentUser.value) return false
  if (currentUser.value.user_type === 'admin') return true
  if (currentUser.value.user_type === 'enterprise' && 
      currentUser.value.enterprise_user?.role_type === 'manager') {
    return true
  }
  return false
})

// 获取当前用户信息
const fetchCurrentUser = async () => {
  try {
    currentUser.value = await apiService.getCurrentUser()
  } catch (err) {
    console.error('获取用户信息失败:', err)
  }
}

// 获取部门成员列表
const fetchMembers = async () => {
  loading.value = true
  error.value = ''
  
  try {
    members.value = await apiService.getDepartmentMembers(departmentId.value)
  } catch (err) {
    error.value = '获取部门成员失败: ' + (err as Error).message
  } finally {
    loading.value = false
  }
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 获取角色样式类
const getRoleClass = (roleType: string) => {
  switch (roleType) {
    case 'manager':
      return 'manager'
    case 'approver':
      return 'approver'
    default:
      return 'normal'
  }
}

// 获取角色文本
const getRoleText = (roleType: string) => {
  switch (roleType) {
    case 'manager':
      return '管理员'
    case 'approver':
      return '审批员'
    default:
      return '普通员工'
  }
}

// 编辑成员
const editMember = (member: EnterpriseUserListItem) => {
  selectedMember.value = member
  showEditModal.value = true
}

// 查看成员详情
const viewMember = (member: EnterpriseUserListItem) => {
  // 这里可以实现查看成员详情的逻辑
  console.log('查看成员:', member)
}

// 关闭编辑模态框
const closeEditModal = () => {
  showEditModal.value = false
  selectedMember.value = null
}

// 编辑成功处理
const handleEditSuccess = () => {
  closeEditModal()
  fetchMembers() // 重新获取成员列表
}

// 组件挂载时获取数据
onMounted(async () => {
  await fetchCurrentUser()
  await fetchMembers()
})
</script>

<style scoped>
.department-members {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.back-btn {
  background: none;
  border: 1px solid #ddd;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  color: #666;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background-color: #f5f5f5;
  border-color: #999;
}

.title-section h1 {
  margin: 0 0 5px 0;
  color: #333;
  font-size: 24px;
}

.title-section p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
}

.error-message {
  background-color: #fee;
  color: #c33;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.members-table-container {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.members-table {
  width: 100%;
  border-collapse: collapse;
}

.members-table th,
.members-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.members-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.members-table tbody tr:hover {
  background-color: #f8f9fa;
}

.role-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.role-badge.manager {
  background-color: #dc3545;
  color: white;
}

.role-badge.approver {
  background-color: #ffc107;
  color: #333;
}

.role-badge.normal {
  background-color: #6c757d;
  color: white;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.status-badge.active {
  background-color: #28a745;
  color: white;
}

.status-badge.inactive {
  background-color: #dc3545;
  color: white;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.edit-btn,
.view-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: background-color 0.2s ease;
}

.edit-btn {
  background-color: #007bff;
  color: white;
}

.edit-btn:hover {
  background-color: #0056b3;
}

.view-btn {
  background-color: #28a745;
  color: white;
}

.view-btn:hover {
  background-color: #218838;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.empty-state p {
  margin: 0;
  font-size: 16px;
}
</style>