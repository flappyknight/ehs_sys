<template>
  <div class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>{{ isEditing ? '编辑厂区' : '新建厂区' }}</h2>
        <button @click="closeModal" class="close-btn">&times;</button>
      </div>

      <form @submit.prevent="handleSubmit" class="modal-body">
        <div class="form-group">
          <label for="area_name">厂区名称 *</label>
          <input
            id="area_name"
            v-model="areaForm.area_name"
            type="text"
            required
            placeholder="请输入厂区名称"
          />
        </div>

        <div class="form-group">
          <label for="dept_id">所属部门</label>
          <select
            id="dept_id"
            v-model="areaForm.dept_id"
          >
            <option :value="null">无</option>
            <option
              v-for="department in departments"
              :key="department.dept_id"
              :value="department.dept_id"
            >
              {{ department.name }}
            </option>
          </select>
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <div class="modal-footer">
          <button type="button" @click="closeModal" class="cancel-btn">
            取消
          </button>
          <button type="submit" :disabled="loading" class="submit-btn">
            {{ loading ? '提交中...' : (isEditing ? '更新' : '创建') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { apiService, type AreaListItem, type Area, type DepartmentListItem } from '@/services/api'
import type { User } from '@/types/auth'

const props = defineProps<{
  area?: AreaListItem | null
}>()

const emit = defineEmits<{
  close: []
  success: []
}>()

const loading = ref(false)
const error = ref('')
const currentUser = ref<User | null>(null)
const departments = ref<DepartmentListItem[]>([])

const areaForm = ref<Area>({
  area_id: null,
  enterprise_id: 0,
  area_name: '',
  dept_id: null
})

const isEditing = computed(() => !!props.area)

// 获取当前用户信息
const fetchCurrentUser = async () => {
  try {
    currentUser.value = await apiService.getCurrentUser()

    // 设置企业ID
    if (currentUser.value.user_type === 'enterprise' && currentUser.value.enterprise_user) {
      areaForm.value.enterprise_id = currentUser.value.enterprise_user.enterprise_id
    }
  } catch (err) {
    console.error('获取用户信息失败:', err)
  }
}

// 获取部门列表
const fetchDepartments = async () => {
  try {
    const data = await apiService.getDepartments()
    departments.value = data
  } catch (err) {
    console.error('获取部门列表失败:', err)
  }
}

// 初始化表单数据
const initializeForm = () => {
  if (props.area) {
    // 编辑模式：获取厂区详情
    fetchAreaDetail()
  } else {
    // 新建模式：重置表单
    resetForm()
  }
}

// 获取厂区详情
const fetchAreaDetail = async () => {
  if (!props.area) return

  try {
    const areaDetail = await apiService.getAreaDetail(props.area.area_id)
    areaForm.value = { ...areaDetail }
  } catch (err) {
    error.value = '获取厂区详情失败: ' + (err as Error).message
  }
}

// 重置表单
const resetForm = () => {
  areaForm.value = {
    area_id: null,
    enterprise_id: currentUser.value?.user_type === 'enterprise' && currentUser.value.enterprise_user
      ? currentUser.value.enterprise_user.enterprise_id
      : 0,
    area_name: '',
    dept_id: null
  }
  error.value = ''
}

// 提交表单
const handleSubmit = async () => {
  loading.value = true
  error.value = ''

  try {
    // 直接使用表单数据，不需要额外的类型转换
    const submitData = { ...areaForm.value }

    if (isEditing.value && submitData.area_id) {
      // 更新厂区
      await apiService.updateArea(submitData.area_id, submitData)
    } else {
      // 创建厂区
      await apiService.createArea(submitData)
    }

    emit('success')
    closeModal()
  } catch (err) {
    error.value = (isEditing.value ? '更新' : '创建') + '厂区失败: ' + (err as Error).message
  } finally {
    loading.value = false
  }
}

// 关闭模态框
const closeModal = () => {
  emit('close')
}

// 组件挂载时初始化
onMounted(async () => {
  await fetchCurrentUser()
  await fetchDepartments()
  initializeForm()
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h2 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #333;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #007bff;
}

.error-message {
  color: #dc3545;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 20px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.cancel-btn,
.submit-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.cancel-btn {
  background-color: #6c757d;
  color: white;
}

.cancel-btn:hover {
  background-color: #5a6268;
}

.submit-btn {
  background-color: #007bff;
  color: white;
}

.submit-btn:hover:not(:disabled) {
  background-color: #0056b3;
}

.submit-btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}
</style>
