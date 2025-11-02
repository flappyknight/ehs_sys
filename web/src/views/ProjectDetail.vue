<template>
  <div class="project-detail-container">
    <div class="header">
      <button @click="goBack" class="back-btn">← 返回</button>
      <h2>项目详情</h2>
    </div>

    <div v-if="loading" class="loading">
      加载中...
    </div>

    <div v-if="error" class="error">
      {{ error }}
    </div>

    <div v-if="project && !loading" class="project-info">
      <div class="info-card">
        <h3>基本信息</h3>
        <div class="info-grid">
          <div class="info-item">
            <label>项目名称:</label>
            <span>{{ project.project_name }}</span>
          </div>
          <div class="info-item">
            <label>承包商:</label>
            <span>{{ project.contractor_name }}</span>
          </div>
          <div class="info-item">
            <label>项目负责人:</label>
            <span>{{ project.project_leader }}</span>
          </div>
          <div class="info-item">
            <label>负责人电话:</label>
            <span>{{ project.leader_phone }}</span>
          </div>
        </div>
      </div>

      <div class="plans-section">
        <h3>进场计划表</h3>
        <div v-if="project.plans.length === 0" class="no-plans">
          暂无进场计划
        </div>
        <div v-else class="plans-list">
          <div
            v-for="plan in project.plans"
            :key="plan.plan_id"
            class="plan-item"
          >
            <div
              class="plan-header"
              @click="togglePlan(plan.plan_id)"
            >
              <div class="plan-info">
                <span class="plan-date">{{ formatDate(plan.plan_date) }}</span>
                <span class="participant-count">参与人数: {{ plan.participant_count }}</span>
                <span class="status" :class="{ completed: plan.is_completed }">
                  {{ plan.is_completed ? '已完成' : '进行中' }}
                </span>
              </div>
              <div class="expand-icon" :class="{ expanded: expandedPlans.has(plan.plan_id) }">
                ▼
              </div>
            </div>

            <div
              v-if="expandedPlans.has(plan.plan_id)"
              class="plan-participants"
            >
              <div class="participants-header">
                <span>姓名</span>
                <span>电话</span>
                <span>身份证号</span>
                <span>登记状态</span>
              </div>
              <div
                v-for="participant in plan.participants"
                :key="participant.user_id"
                class="participant-row"
              >
                <span>{{ participant.name }}</span>
                <span>{{ participant.phone }}</span>
                <span>{{ participant.id_number }}</span>
                <span class="registration-status" :class="{ registered: participant.is_registered }">
                  {{ participant.is_registered ? '已登记' : '未登记' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { apiService, type ProjectDetail } from '@/services/api'

const router = useRouter()
const route = useRoute()
const project = ref<ProjectDetail | null>(null)
const loading = ref(false)
const error = ref('')
const expandedPlans = ref(new Set<number>())

const fetchProjectDetail = async () => {
  const projectId = route.params.id
  if (!projectId) {
    error.value = '项目ID不存在'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const data = await apiService.getProjectDetail(Number(projectId))
    project.value = data
  } catch (err) {
    error.value = '获取项目详情失败: ' + (err as Error).message
    console.error('Error fetching project detail:', err)
  } finally {
    loading.value = false
  }
}

const togglePlan = (planId: number) => {
  if (expandedPlans.value.has(planId)) {
    expandedPlans.value.delete(planId)
  } else {
    expandedPlans.value.add(planId)
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  fetchProjectDetail()
})
</script>

<style scoped>
.project-detail-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  gap: 16px;
}

.back-btn {
  background-color: #6c757d;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.back-btn:hover {
  background-color: #5a6268;
}

.header h2 {
  color: #333;
  font-size: 24px;
  margin: 0;
}

.info-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
}

.info-card h3 {
  margin: 0 0 16px 0;
  color: #333;
  font-size: 18px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item label {
  font-weight: 600;
  color: #666;
  font-size: 14px;
}

.info-item span {
  color: #333;
  font-size: 16px;
}

.plans-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.plans-section h3 {
  margin: 0 0 16px 0;
  color: #333;
  font-size: 18px;
}

.no-plans {
  text-align: center;
  color: #666;
  padding: 40px;
}

.plan-item {
  border: 1px solid #eee;
  border-radius: 6px;
  margin-bottom: 12px;
  overflow: hidden;
}

.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background-color: #f8f9fa;
  cursor: pointer;
  transition: background-color 0.2s;
}

.plan-header:hover {
  background-color: #e9ecef;
}

.plan-info {
  display: flex;
  gap: 20px;
  align-items: center;
}

.plan-date {
  font-weight: 600;
  color: #333;
}

.participant-count {
  color: #666;
  font-size: 14px;
}

.status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  background-color: #ffc107;
  color: #212529;
}

.status.completed {
  background-color: #28a745;
  color: white;
}

.expand-icon {
  transition: transform 0.2s;
  color: #666;
}

.expand-icon.expanded {
  transform: rotate(180deg);
}

.plan-participants {
  border-top: 1px solid #eee;
}

.participants-header {
  display: grid;
  grid-template-columns: 1fr 1fr 2fr 1fr;
  gap: 16px;
  padding: 12px 16px;
  background-color: #f5f5f5;
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.participant-row {
  display: grid;
  grid-template-columns: 1fr 1fr 2fr 1fr;
  gap: 16px;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
}

.participant-row:last-child {
  border-bottom: none;
}

.registration-status {
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 12px;
  background-color: #dc3545;
  color: white;
  text-align: center;
}

.registration-status.registered {
  background-color: #28a745;
}

.loading {
  text-align: center;
  padding: 40px;
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
</style>
