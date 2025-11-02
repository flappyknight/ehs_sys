<template>
  <div class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>编辑成员信息</h2>
        <button @click="closeModal" class="close-btn">&times;</button>
      </div>

      <form @submit.prevent="handleSubmit" class="modal-body">
        <div class="form-group">
          <label for="name">姓名 *</label>
          <input
            id="name"
            v-model="memberForm.name"
            type="text"
            required
            placeholder="请输入姓名"
          />
        </div>

        <div class="form-group">
          <label for="phone">手机号 *</label>
          <input
            id="phone"
            v-model="memberForm.phone"
            type="tel"
            required
            placeholder="请输入手机号"
          />
        </div>

        <div class="form-group">
          <label for="email">邮箱 *</label>
          <input
            id="email"
            v-model="memberForm.email"
            type="email"
            required
            placeholder="请输入邮箱"
          />
        </div>

        <div class="form-group">
          <label for="position">职位</label>
          <input
            id="position"
            v-model="memberForm.position"
            type="text"
            placeholder="请输入职位"
          />
        </div>

        <div class="form-group">
          <label for="dept_id">所属部门</label>
          <select
            id="dept_id"
            v-model="memberForm.dept_id"
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

        <div class="form-group">
          <label for="role_type">角色类型</label>
          <select
            id="role_type"
            v-model="memberForm.role_type"
          >
            <option value="normal">普通员工</option>
            <option value="approver">审批员</option>
            <option value="manager">管理员</option>
          </select>
        </div>

        <div class="form-group">
          <label class="checkbox-label">
            <input
              type="checkbox"
              v-model="memberForm.status"
            />
            启用账户
          </label>
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <div class="modal-footer">
          <button type="button" @click="closeModal" class="cancel-btn">
            取消
          </button>
          <button type="submit" :disabled="loading" class="submit-btn">
            {{ loading ? '保存中...' : '保存' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiService, type EnterpriseUserListItem, type EnterpriseUserUpdate, type DepartmentListItem } from '@/services/api'

const props = defineProps<{
  member: EnterpriseUserListItem | null
}>()

const emit = defineEmits<{
  close: []
  success: []
}>()

const loading = ref(false)
const error = ref('')
const departments = ref<DepartmentListItem[]>([])

const memberForm = ref<EnterpriseUserUpdate>({
  name: '',
  phone: '',
  email: '',
  position: '',
  dept_id: null,
  role_type: 'normal',
  status: true
})

// 获取部门列表
const fetchDepartments = async () => {
  try {
    departments.value = await apiService.getDepartments()
  } catch (err) {
    console.error('获取部门列表失败:', err)
  }
}

// 初始化表单数据
const initializeForm = () => {
  if (props.member) {
    memberForm.value = {
      name: props.member.name,
      phone: props.member.phone,
      email: props.member.email,
      position: props.member.position,
      dept_id: props.member.dept_id,
      role_type: props.member.role_type,
      status: props.member.status
    }
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!props.member) return

  loading.value = true
  error.value = ''

  try {
    await apiService.updateEnterpriseUser(props.member.user_id, memberForm.value)
    emit('success')
    closeModal()
  } catch (err) {
    error.value = '更新成员信息失败: ' + (err as Error).message
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
  color: #999;
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
  color: #333;
  font-weight: 500;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #007bff;
}

.checkbox-label {
  display: flex !important;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
  margin: 0;
}

.error-message {
  background-color: #fee;
  color: #c33;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 20px;
  font-size: 14px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #eee;
}

.cancel-btn,
.submit-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s ease;
}

.cancel-btn {
  background-color: #6c757d;
  color: white;
}

.cancel-btn:hover {
  background-color: #545b62;
}

.submit-btn {
  background-color: #007bff;
  color: white;
}

.submit-btn:hover:not(:disabled) {
  background-color: #0056b3;
}

.submit-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>
