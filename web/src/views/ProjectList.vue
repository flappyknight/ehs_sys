<template>
  <div class="project-list-container">
    <div class="header">
      <h2>项目管理</h2>
      <button
        v-if="canCreateProject"
        @click="showCreateModal = true"
        class="create-btn"
      >
        新建项目
      </button>
    </div>

    <div class="project-table">
      <table>
        <thead>
          <tr>
            <th>项目名称</th>
            <th>承包商</th>
            <th>项目负责人</th>
            <th>负责人电话</th>
            <th>已计划进场数/次</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="project in projects"
            :key="project.project_id"
            @click="viewProjectDetail(project.project_id)"
            class="project-row"
          >
            <td>{{ project.project_name }}</td>
            <td>{{ project.contractor_name }}</td>
            <td>{{ project.project_leader }}</td>
            <td>{{ project.leader_phone }}</td>
            <td>{{ project.planned_entry_count }}</td>
            <td>
              <button @click.stop="viewProjectDetail(project.project_id)" class="detail-btn">
                查看详情
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="loading" class="loading">
      加载中...
    </div>

    <div v-if="error" class="error">
      {{ error }}
    </div>

    <!-- 新建项目弹窗组件 -->
    <CreateProjectModal
      v-if="canCreateProject"
      :visible="showCreateModal"
      @close="showCreateModal = false"
      @success="handleCreateSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { apiService, type ProjectListItem } from '@/services/api'
import type { User } from '@/types/auth'
import CreateProjectModal from '@/components/CreateProjectModal.vue'

const router = useRouter()
const projects = ref<ProjectListItem[]>([])
const loading = ref(false)
const error = ref('')
const showCreateModal = ref(false)
const currentUser = ref<User | null>(null)

// 计算属性：检查用户是否有创建项目的权限
const canCreateProject = computed(() => {
  if (!currentUser.value) return false

  // admin用户可以创建项目
  if (currentUser.value.user_type === 'admin') {
    return true
  }

  // enterprise用户且role_type为manager才能创建项目
  if (currentUser.value.user_type === 'enterprise' && currentUser.value.enterprise_user) {
    return currentUser.value.enterprise_user.role_type === 'manager'
  }

  // 其他情况不能创建项目
  return false
})

// 获取当前用户信息
const fetchCurrentUser = async () => {
  try {
    currentUser.value = await apiService.getCurrentUser()
  } catch (err) {
    console.error('获取用户信息失败:', err)
    // 如果获取用户信息失败，可能需要重新登录
    if ((err as Error).message.includes('401') || (err as Error).message.includes('Not authenticated')) {
      // router.push('/login')
    }
  }
}

const fetchProjects = async () => {
  loading.value = true
  error.value = ''

  try {
    const data = await apiService.getProjects()
    projects.value = data
  } catch (err) {
    error.value = '获取项目列表失败: ' + (err as Error).message
    console.error('Error fetching projects:', err)

    // 如果是认证错误，可以跳转到登录页面
    if ((err as Error).message.includes('401') || (err as Error).message.includes('Not authenticated')) {
      // router.push('/login')
    }
  } finally {
    loading.value = false
  }
}

const viewProjectDetail = (projectId: number) => {
  router.push(`/projects/${projectId}`)
}

const handleCreateSuccess = () => {
  // 创建成功后刷新项目列表
  fetchProjects()
}

onMounted(async () => {
  // 先获取用户信息，再获取项目列表
  await fetchCurrentUser()
  await fetchProjects()
})
</script>

<style scoped>
.project-list-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h2 {
  color: #333;
  font-size: 24px;
  margin: 0;
}

.create-btn {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s ease;
}

.create-btn:hover {
  background-color: #0056b3;
}

.project-table {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background-color: #f5f5f5;
}

th, td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  font-weight: 600;
  color: #333;
}

.project-row {
  cursor: pointer;
  transition: background-color 0.2s;
}

.project-row:hover {
  background-color: #f9f9f9;
}

.detail-btn {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.detail-btn:hover {
  background-color: #0056b3;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #666;
}

.error {
  text-align: center;
  padding: 20px;
  color: #d32f2f;
  background-color: #ffebee;
  border-radius: 4px;
  margin-top: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
}
</style>
