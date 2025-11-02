<template>
  <div class="contractor-views">
    <div class="header">
      <h2>承包商管理</h2>
    </div>

    <div class="table-container">
      <table class="contractor-table">
        <thead>
          <tr>
            <th class="name-header">承包商名称</th>
            <th class="legal-person-header">承包商法人</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="contractor in contractors" :key="contractor.contractor_id" class="contractor-row">
            <td class="name-cell">
              <div class="company-name">{{ contractor.company_name }}</div>
              <div class="company-type">{{ contractor.company_type }}</div>
            </td>
            <td class="legal-person-cell">
              <div class="legal-person">{{ contractor.legal_person }}</div>
              <div class="project-count">合作项目: {{ contractor.project_count }}个</div>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="loading" class="loading">
        加载中...
      </div>

      <div v-if="!loading && contractors.length === 0 && !error" class="empty-state">
        暂无承包商数据
      </div>

      <div v-if="error" class="error-state">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiService, type ContractorListItem } from '@/services/api'

const contractors = ref<ContractorListItem[]>([])
const loading = ref(false)
const error = ref('')

// 获取承包商列表
const fetchContractors = async () => {
  loading.value = true
  error.value = ''

  try {
    contractors.value = await apiService.getContractors()
  } catch (err) {
    if (err instanceof Error) {
      error.value = err.message || '获取承包商列表失败'
    } else {
      error.value = '获取承包商列表失败'
    }
    console.error('获取承包商列表失败:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchContractors()
})
</script>

<style scoped>
.contractor-views {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  margin-bottom: 24px;
}

.header h2 {
  color: #333;
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.contractor-table {
  width: 100%;
  border-collapse: collapse;
}

.contractor-table thead {
  background-color: #f5f5f5;
}

.contractor-table th {
  padding: 16px 20px;
  text-align: left;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #e0e0e0;
}

.name-header {
  width: 60%;
  text-align: left;
}

.legal-person-header {
  width: 40%;
  text-align: right;
}

.contractor-row {
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s ease;
}

.contractor-row:hover {
  background-color: #f9f9f9;
}

.contractor-row:last-child {
  border-bottom: none;
}

.name-cell {
  padding: 20px;
  text-align: left;
}

.legal-person-cell {
  padding: 20px;
  text-align: right;
}

.company-name {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
  line-height: 1.4;
}

.company-type {
  font-size: 14px;
  color: #666;
}

.legal-person {
  font-size: 16px;
  color: #555;
  margin-bottom: 4px;
}

.project-count {
  font-size: 12px;
  color: #888;
}

.loading {
  padding: 40px;
  text-align: center;
  color: #666;
  font-size: 16px;
}

.empty-state {
  padding: 40px;
  text-align: center;
  color: #999;
  font-size: 16px;
}

.error-state {
  padding: 40px;
  text-align: center;
  color: #e74c3c;
  font-size: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .contractor-views {
    padding: 16px;
  }

  .contractor-table th,
  .name-cell,
  .legal-person-cell {
    padding: 16px 12px;
  }

  .company-name {
    font-size: 16px;
  }

  .legal-person {
    font-size: 14px;
  }
}
</style>
