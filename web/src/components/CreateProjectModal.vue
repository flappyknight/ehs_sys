<template>
  <div v-if="visible" class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>新建项目</h3>
        <button @click="closeModal" class="close-btn">&times;</button>
      </div>

      <form @submit.prevent="submitProject" class="project-form">
        <!-- 项目信息 -->
        <div class="form-section">
          <h4>项目信息</h4>
          <div class="form-group">
            <label for="projectName">项目名称 *</label>
            <input
              id="projectName"
              v-model="projectForm.project_name"
              type="text"
              required
              placeholder="请输入项目名称"
            />
          </div>
          <div class="form-group">
            <label for="leaderName">项目负责人 *</label>
            <input
              id="leaderName"
              v-model="projectForm.leader_name"
              type="text"
              required
              placeholder="请输入负责人姓名"
            />
          </div>
          <div class="form-group">
            <label for="leaderPhone">负责人电话 *</label>
            <input
              id="leaderPhone"
              v-model="projectForm.leader_phone"
              type="tel"
              required
              placeholder="请输入负责人电话"
            />
          </div>
        </div>

        <!-- 承包商信息 -->
        <div class="form-section">
          <h4>承包商信息</h4>
          <div class="form-group" v-if="hasContractors">
            <label>承包商类型 *</label>
            <div class="radio-group">
              <label class="radio-label">
                <input
                  type="radio"
                  v-model="contractorType"
                  value="existing"
                />
                选择已有承包商
              </label>
              <label class="radio-label">
                <input
                  type="radio"
                  v-model="contractorType"
                  value="new"
                />
                新建承包商
              </label>
            </div>
          </div>

          <!-- 选择已有承包商 -->
          <div v-if="contractorType === 'existing' && hasContractors" class="form-group">
            <label for="existingContractor">选择承包商 *</label>
            <div class="contractor-search-container">
              <input
                id="existingContractor"
                v-model="contractorSearchText"
                type="text"
                placeholder="搜索承包商名称或法人代表"
                @focus="showContractorDropdown = true"
                @input="showContractorDropdown = true"
                required
              />
              <button
                v-if="projectForm.contractor_id"
                type="button"
                class="clear-btn"
                @click="clearContractorSelection"
              >
                ×
              </button>
              <div
                v-if="showContractorDropdown && filteredContractors.length > 0"
                class="contractor-dropdown"
              >
                <div
                  v-for="contractor in filteredContractors"
                  :key="contractor.contractor_id"
                  class="contractor-option"
                  @click="selectContractor(contractor)"
                >
                  <div class="contractor-name">{{ contractor.company_name }}</div>
                  <div class="contractor-legal">法人：{{ contractor.legal_person }}</div>
                </div>
              </div>
              <div
                v-if="showContractorDropdown && filteredContractors.length === 0 && contractorSearchText"
                class="contractor-dropdown"
              >
                <div class="no-results">未找到匹配的承包商</div>
              </div>
            </div>
          </div>

          <!-- 新建承包商 -->
          <div v-if="contractorType === 'new'" class="new-contractor-form">
            <div class="form-group">
              <label for="companyName">公司名称 *</label>
              <input
                id="companyName"
                v-model="projectForm.company_name"
                type="text"
                :required="contractorType === 'new'"
                placeholder="请输入公司名称"
              />
            </div>
            <div class="form-group">
              <label for="companyType">公司类型 *</label>
              <select
                id="companyType"
                v-model="projectForm.company_type"
                :required="contractorType === 'new'"
              >
                <option value="">请选择公司类型</option>
                <option value="有限责任公司">有限责任公司</option>
                <option value="股份有限公司">股份有限公司</option>
                <option value="个人独资企业">个人独资企业</option>
                <option value="合伙企业">合伙企业</option>
                <option value="其他">其他</option>
              </select>
            </div>
            <div class="form-group">
              <label for="legalPerson">法人代表 *</label>
              <input
                id="legalPerson"
                v-model="projectForm.legal_person"
                type="text"
                :required="contractorType === 'new'"
                placeholder="请输入法人代表姓名"
              />
            </div>
            <div class="form-group">
              <label for="establishDate">成立日期 *</label>
              <input
                id="establishDate"
                v-model="projectForm.establish_date"
                type="date"
                :required="contractorType === 'new'"
              />
            </div>
            <div class="form-group">
              <label for="registeredCapital">注册资本 (万元) *</label>
              <input
                id="registeredCapital"
                v-model="projectForm.registered_capital"
                type="number"
                step="0.01"
                :required="contractorType === 'new'"
                placeholder="请输入注册资本"
              />
            </div>
            <div class="form-group">
              <label for="applicantName">申请人姓名 *</label>
              <input
                id="applicantName"
                v-model="projectForm.applicant_name"
                type="text"
                :required="contractorType === 'new'"
                placeholder="请输入申请人姓名"
              />
            </div>
            <div class="form-group">
              <label for="licenseFile">营业执照 *</label>
              <input
                id="licenseFile"
                v-model="projectForm.license_file"
                type="text"
                :required="contractorType === 'new'"
                placeholder="请输入营业执照文件路径或编号"
              />
            </div>
          </div>
        </div>

        <div class="form-actions">
          <button type="button" @click="closeModal" class="cancel-btn">取消</button>
          <button type="submit" :disabled="submitting" class="submit-btn">
            {{ submitting ? '创建中...' : '确认创建' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue'
import { apiService, type ContractorListItem, type ContractorProjectRequest } from '@/services/api'

interface Props {
  visible: boolean
}

interface Emits {
  (e: 'close'): void
  (e: 'success'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const contractors = ref<ContractorListItem[]>([])
const submitting = ref(false)
const contractorType = ref<'existing' | 'new'>('existing')
const contractorSearchText = ref('')
const showContractorDropdown = ref(false)

// 项目表单数据
const projectForm = ref({
  // 项目信息
  project_name: '',
  leader_name: '',
  leader_phone: '',

  // 承包商信息 - 已有承包商
  contractor_id: null as number | null,

  // 承包商信息 - 新承包商
  company_name: '',
  company_type: '',
  legal_person: '',
  establish_date: '',
  registered_capital: null as number | null,
  applicant_name: '',
  license_file: ''
})

// 计算属性：是否有可选择的承包商
const hasContractors = computed(() => contractors.value.length > 0)

// 计算属性：过滤后的承包商列表
const filteredContractors = computed(() => {
  if (!contractorSearchText.value) {
    return contractors.value
  }
  return contractors.value.filter(contractor =>
    contractor.company_name.toLowerCase().includes(contractorSearchText.value.toLowerCase()) ||
    contractor.legal_person.toLowerCase().includes(contractorSearchText.value.toLowerCase())
  )
})

// // 计算属性：选中的承包商信息
// const selectedContractor = computed(() => {
//   if (!projectForm.value.contractor_id) return null
//   return contractors.value.find(c => c.contractor_id === projectForm.value.contractor_id)
// })

// 获取承包商列表
const fetchContractors = async () => {
  try {
    contractors.value = await apiService.getContractors()
    // 如果没有承包商，自动切换到新建模式
    if (contractors.value.length === 0) {
      contractorType.value = 'new'
    }
  } catch (err) {
    console.error('获取承包商列表失败:', err)
    contractorType.value = 'new'
  }
}

// 选择承包商
const selectContractor = (contractor: ContractorListItem) => {
  projectForm.value.contractor_id = contractor.contractor_id
  contractorSearchText.value = `${contractor.company_name} (${contractor.legal_person})`
  showContractorDropdown.value = false
}

// 清除承包商选择
const clearContractorSelection = () => {
  projectForm.value.contractor_id = null
  contractorSearchText.value = ''
}

// 关闭弹窗
const closeModal = () => {
  emit('close')
  resetForm()
}

// 重置表单
const resetForm = () => {
  projectForm.value = {
    project_name: '',
    leader_name: '',
    leader_phone: '',
    contractor_id: null,
    company_name: '',
    company_type: '',
    legal_person: '',
    establish_date: '',
    registered_capital: null,
    applicant_name: '',
    license_file: ''
  }
  contractorType.value = hasContractors.value ? 'existing' : 'new'
  contractorSearchText.value = ''
  showContractorDropdown.value = false
}

// 提交项目
const submitProject = async () => {
  submitting.value = true

  try {
    const requestData: ContractorProjectRequest = {
      // 项目信息
      project_name: projectForm.value.project_name,
      leader_name: projectForm.value.leader_name,
      leader_phone: projectForm.value.leader_phone,

      // 承包商信息
      ...(contractorType.value === 'existing'
        ? { contractor_id: projectForm.value.contractor_id }
        : {
            company_name: projectForm.value.company_name,
            company_type: projectForm.value.company_type,
            legal_person: projectForm.value.legal_person,
            establish_date: projectForm.value.establish_date,
            registered_capital: projectForm.value.registered_capital,
            applicant_name: projectForm.value.applicant_name,
            license_file: projectForm.value.license_file
          }
      )
    }

    await apiService.createContractorProject(requestData)

    emit('success')
    closeModal()

    alert('项目创建成功！')
  } catch (err) {
    if (err instanceof Error) {
      alert(`创建失败: ${err.message}`)
    } else {
      alert('创建失败，请重试')
    }
    console.error('创建项目失败:', err)
  } finally {
    submitting.value = false
  }
}

// 监听弹窗显示状态，加载承包商列表
watch(() => props.visible, (newVisible) => {
  if (newVisible) {
    fetchContractors()
  }
})

onMounted(() => {
  if (props.visible) {
    fetchContractors()
  }
})
</script>

<style scoped>
/* 弹窗样式 */
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
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
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
  color: #666;
}

.project-form {
  padding: 24px;
}

.form-section {
  margin-bottom: 32px;
}

.form-section h4 {
  margin: 0 0 16px 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 8px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  color: #333;
  font-weight: 500;
  font-size: 14px;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.radio-group {
  display: flex;
  gap: 20px;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-weight: normal;
}

.radio-label input[type="radio"] {
  width: auto;
  margin: 0;
}

.new-contractor-form {
  background-color: #f8f9fa;
  padding: 16px;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.cancel-btn {
  background-color: #6c757d;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.cancel-btn:hover {
  background-color: #5a6268;
}

.submit-btn {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.submit-btn:hover:not(:disabled) {
  background-color: #0056b3;
}

.submit-btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .modal-content {
    width: 95%;
    margin: 20px;
  }

  .radio-group {
    flex-direction: column;
    gap: 10px;
  }

  .form-actions {
    flex-direction: column;
  }
}

.contractor-search-container {
  position: relative;
}

.contractor-search-container input {
  width: 100%;
  padding-right: 30px;
}

.clear-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #999;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.clear-btn:hover {
  color: #666;
}

.contractor-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #ddd;
  border-top: none;
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.contractor-option {
  padding: 12px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
}

.contractor-option:hover {
  background-color: #f5f5f5;
}

.contractor-option:last-child {
  border-bottom: none;
}

.contractor-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.contractor-legal {
  font-size: 12px;
  color: #666;
}

.no-results {
  padding: 12px;
  color: #999;
  text-align: center;
}
</style>
