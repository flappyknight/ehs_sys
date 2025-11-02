<template>
  <div class="staff-management">
    <div class="page-header">
      <h1>人员管理</h1>
      <p>管理企业部门和成员信息</p>
    </div>

    <div v-if="loading" class="loading">
      加载中...
    </div>

    <div v-else-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-else class="departments-grid">
      <div
        v-for="department in departments"
        :key="department.dept_id"
        class="department-card"
        @click="goToDepartmentMembers(department.dept_id, department.name)"
      >
        <div class="department-header">
          <h3>{{ department.name }}</h3>
          <span class="member-count">{{ department.member_count }} 人</span>
        </div>
        <div class="department-info">
          <p class="company-name">{{ department.company_name }}</p>
          <div class="department-actions">
            <button class="view-btn">查看成员</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!loading && departments.length === 0" class="empty-state">
      <p>暂无部门数据</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { apiService, type DepartmentWithMemberCount } from '@/services/api'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const departments = ref<DepartmentWithMemberCount[]>([])

// 获取部门列表
const fetchDepartments = async () => {
  loading.value = true
  error.value = ''

  try {
    departments.value = await apiService.getDepartmentsWithMembers()
  } catch (err) {
    error.value = '获取部门列表失败: ' + (err as Error).message
  } finally {
    loading.value = false
  }
}

// 跳转到部门成员页面
const goToDepartmentMembers = (deptId: number, deptName: string) => {
  router.push({
    name: 'DepartmentMembers',
    params: { deptId: deptId.toString() },
    query: { deptName }
  })
}

// 组件挂载时获取数据
onMounted(() => {
  fetchDepartments()
})
</script>

<style scoped>
.staff-management {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 28px;
}

.page-header p {
  margin: 0;
  color: #666;
  font-size: 16px;
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

.departments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.department-card {
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.department-card:hover {
  border-color: #007bff;
  box-shadow: 0 2px 8px rgba(0, 123, 255, 0.1);
  transform: translateY(-2px);
}

.department-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.department-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.member-count {
  background-color: #007bff;
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: bold;
}

.department-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.company-name {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.department-actions {
  display: flex;
  justify-content: flex-end;
}

.view-btn {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s ease;
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
