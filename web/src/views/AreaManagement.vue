<template>
  <div class="area-management">
    <div class="header">
      <h1>厂区管理</h1>
      <button
        v-if="canCreateArea"
        @click="showCreateModal = true"
        class="create-btn"
      >
        新建厂区
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading">
      加载中...
    </div>

    <!-- 错误信息 -->
    <div v-if="error" class="error">
      {{ error }}
    </div>

    <!-- 厂区表格 -->
    <div v-if="!loading && !error" class="area-table-container">
      <table class="area-table">
        <thead>
          <tr>
            <th>厂区名称</th>
            <th>所属部门</th>
            <th v-if="canEditArea">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="areas.length === 0">
            <td :colspan="canEditArea ? 3 : 2" class="empty-state">
              暂无厂区数据
            </td>
          </tr>
          <tr v-for="area in areas" :key="area.area_id">
            <td>{{ area.area_name }}</td>
            <td>{{ area.dept_name || '无' }}</td>
            <td v-if="canEditArea" class="actions">
              <button
                @click="editArea(area)"
                class="edit-btn"
              >
                编辑
              </button>
              <button
                @click="deleteAreaConfirm(area)"
                class="delete-btn"
              >
                删除
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 创建/编辑厂区模态框 -->
    <CreateAreaModal
      v-if="showCreateModal"
      :area="editingArea"
      @close="closeModal"
      @success="handleCreateSuccess"
    />

    <!-- 删除确认模态框 -->
    <DeleteConfirmModal
      v-if="showDeleteModal"
      :item-name="deletingArea?.area_name || ''"
      item-type="厂区"
      @confirm="handleDelete"
      @cancel="showDeleteModal = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { apiService, type AreaListItem } from '@/services/api'
import type { User } from '@/types/auth'
import CreateAreaModal from '@/components/CreateAreaModal.vue'
import DeleteConfirmModal from '@/components/DeleteConfirmModal.vue'

const areas = ref<AreaListItem[]>([])
const loading = ref(false)
const error = ref('')
const showCreateModal = ref(false)
const showDeleteModal = ref(false)
const editingArea = ref<AreaListItem | null>(null)
const deletingArea = ref<AreaListItem | null>(null)
const currentUser = ref<User | null>(null)

// 权限检查
const canCreateArea = computed(() => {
  if (!currentUser.value) return false

  // admin用户可以创建厂区
  if (currentUser.value.user_type === 'admin') {
    return true
  }

  // enterprise用户且role_type为manager才能创建厂区
  if (currentUser.value.user_type === 'enterprise' && currentUser.value.enterprise_user) {
    return currentUser.value.enterprise_user.role_type === 'manager'
  }

  return false
})

const canEditArea = computed(() => canCreateArea.value)

// 获取当前用户信息
const fetchCurrentUser = async () => {
  try {
    currentUser.value = await apiService.getCurrentUser()
  } catch (err) {
    console.error('获取用户信息失败:', err)
  }
}

// 获取厂区列表
const fetchAreas = async () => {
  loading.value = true
  error.value = ''

  try {
    const data = await apiService.getAreas()
    areas.value = data
  } catch (err) {
    error.value = '获取厂区列表失败: ' + (err as Error).message
    console.error('Error fetching areas:', err)
  } finally {
    loading.value = false
  }
}

// 编辑厂区
const editArea = (area: AreaListItem) => {
  editingArea.value = area
  showCreateModal.value = true
}

// 删除厂区确认
const deleteAreaConfirm = (area: AreaListItem) => {
  deletingArea.value = area
  showDeleteModal.value = true
}

// 执行删除
const handleDelete = async () => {
  if (!deletingArea.value) return

  try {
    await apiService.deleteArea(deletingArea.value.area_id)
    await fetchAreas() // 刷新列表
    showDeleteModal.value = false
    deletingArea.value = null
  } catch (err) {
    error.value = '删除厂区失败: ' + (err as Error).message
    console.error('Error deleting area:', err)
  }
}

// 关闭模态框
const closeModal = () => {
  showCreateModal.value = false
  editingArea.value = null
}

// 创建/更新成功后的处理
const handleCreateSuccess = () => {
  fetchAreas() // 刷新列表
}

onMounted(async () => {
  await fetchCurrentUser()
  await fetchAreas()
})
</script>

<style scoped>
.area-management {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h1 {
  margin: 0;
  color: #333;
}

.create-btn {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.create-btn:hover {
  background-color: #0056b3;
}

.loading, .error {
  text-align: center;
  padding: 20px;
  font-size: 16px;
}

.error {
  color: #dc3545;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
}

.area-table-container {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.area-table {
  width: 100%;
  border-collapse: collapse;
}

.area-table th,
.area-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.area-table th {
  background-color: #f8f9fa;
  font-weight: bold;
  color: #333;
}

.area-table tbody tr:hover {
  background-color: #f8f9fa;
}

.empty-state {
  text-align: center;
  color: #666;
  font-style: italic;
}

.actions {
  display: flex;
  gap: 8px;
}

.edit-btn, .delete-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.edit-btn {
  background-color: #28a745;
  color: white;
}

.edit-btn:hover {
  background-color: #218838;
}

.delete-btn {
  background-color: #dc3545;
  color: white;
}

.delete-btn:hover {
  background-color: #c82333;
}
</style>
