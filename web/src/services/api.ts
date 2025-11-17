import type { LoginForm, Token, User } from '@/types/auth'

const API_BASE = 'http://localhost:8100'
// const API_BASE = 'http://www.youngj.icu:8100'

// Token管理类
class TokenManager {
  private static readonly TOKEN_KEY = 'access_token'

  static setToken(token: string): void {
    localStorage.setItem(this.TOKEN_KEY, token)
  }

  static getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY)
  }

  static removeToken(): void {
    localStorage.removeItem(this.TOKEN_KEY)
  }

  static isTokenValid(): boolean {
    const token = this.getToken()
    if (!token) return false

    try {
      // 简单的token过期检查
      const payload = JSON.parse(atob(token.split('.')[1]))
      const currentTime = Date.now() / 1000
      return payload.exp > currentTime
    } catch {
      return false
    }
  }
}

// 添加项目相关的类型定义
export interface ProjectListItem {
  project_id: number
  project_name: string
  contractor_name: string
  project_leader: string
  leader_phone: string
  planned_entry_count: number
}

// 添加承包商相关的类型定义
export interface ContractorListItem {
  contractor_id: number
  company_name: string
  company_type: string
  legal_person: string
  establish_date: string
  project_count: number
}

// 承包商信息（用于审批页面）
export interface ContractorInfo {
  contractor_id: number
  license_file: string
  license_number?: string | null
  company_name: string
  company_type?: string | null
  company_address?: string | null
  legal_person?: string | null
  establish_date?: string | null
  registered_capital?: number | null
  applicant_name?: string | null
  business_status: string
  created_at?: string | null
  updated_at?: string | null
  admins?: AdminInfo[]
}

// 承包商列表响应
export interface ContractorListResponse {
  items: ContractorInfo[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// 添加厂区相关的类型定义
export interface AreaListItem {
  area_id: number
  area_name: string
  enterprise_name: string
  dept_name?: string | null
}

export interface Area {
  area_id?: number | null
  enterprise_id: number
  area_name: string
  dept_id?: number | null
}

// 添加企业相关的类型定义
export interface EnterpriseListItem {
  company_id: number
  name: string
  type: string
}

// 管理员信息
export interface AdminInfo {
  user_id: number
  username: string
  name: string
  phone?: string | null
  email?: string | null
  user_status?: number | null
}

// 企业信息（用于审批页面）
export interface EnterpriseInfo {
  enterprise_id: number
  license_file: string
  license_number?: string | null
  company_name: string
  company_type?: string | null
  company_address?: string | null
  legal_person?: string | null
  establish_date?: string | null
  registered_capital?: number | null
  applicant_name?: string | null
  business_status: string
  parent_enterprise_id?: number | null
  created_at?: string | null
  updated_at?: string | null
  admins?: AdminInfo[]
}

// 企业列表响应
export interface EnterpriseListResponse {
  items: EnterpriseInfo[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// 待审批人员信息
export interface PendingStaffInfo {
  user_id: number
  username: string
  name: string
  user_type: string
  phone?: string | null
  email?: string | null
  role_type?: string | null
  role_level?: number | null
  user_status: number
  enterprise_staff_id?: number | null
  contractor_staff_id?: number | null
  company_name?: string | null
  created_at?: string | null
  updated_at?: string | null
}

// 待审批人员列表响应
export interface PendingStaffListResponse {
  items: PendingStaffInfo[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// 用户信息（完整版，包含企业和供应商信息）
export interface UserInfo {
  user_id: number
  username: string
  name: string
  user_type: string
  phone?: string | null
  email?: string | null
  role_type?: string | null
  role_level?: number | null
  user_status: number
  enterprise_staff_id?: number | null
  contractor_staff_id?: number | null
  enterprise_name?: string | null
  enterprise_license_number?: string | null
  contractor_name?: string | null
  contractor_license_number?: string | null
  created_at?: string | null
  updated_at?: string | null
}

// 用户列表响应
export interface UserListResponse {
  items: UserInfo[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// 审批企业请求
export interface ApproveEnterpriseRequest {
  approved: boolean
  comment?: string | null
}

// 添加部门相关的类型定义
export interface DepartmentListItem {
  dept_id: number
  company_id: number
  name: string
  parent_id?: number | null
}

// 创建承包商项目的请求类型
export interface ContractorProjectRequest {
  // 承包商信息（新承包商时必填，已有承包商时只需contractor_id）
  contractor_id?: number | null  // 已有承包商的ID
  company_name?: string
  license_file?: string
  company_type?: string
  legal_person?: string
  establish_date?: string
  registered_capital?: number | null
  applicant_name?: string

  // 项目信息（必填）
  project_name: string
  leader_name: string
  leader_phone: string
}

// 创建承包商项目的响应类型
export interface ContractorProjectResponse {
  contractor_id: number
  project_id: number
  message: string
}

export interface PlanParticipant {
  user_id: number
  name: string
  phone: string
  id_number: string
  is_registered: boolean
}

export interface PlanDetail {
  plan_id: number
  project_name: string
  plan_date: string // 日期字符串格式
  participant_count: number
  is_completed: boolean
  participants: PlanParticipant[]
}

export interface ProjectDetail {
  project_id: number
  project_name: string
  contractor_name: string
  project_leader: string
  leader_phone: string
  plans: PlanDetail[]
}

// 添加人员管理相关的类型定义
export interface DepartmentWithMemberCount {
  dept_id: number
  name: string
  company_id: number
  company_name: string
  member_count: number
  parent_id?: number | null
}

export interface EnterpriseUserListItem {
  user_id: number
  name: string
  phone: string
  email: string
  position?: string | null
  role_type: string
  company_name: string
  dept_id?: number | null
  status: boolean
}

export interface EnterpriseUserUpdate {
  name?: string | null
  phone?: string | null
  email?: string | null
  position?: string | null
  dept_id?: number | null
  role_type?: string | null
  status?: boolean | null
}

export class ApiService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE}${endpoint}`

    // 获取token并添加到请求头
    const token = TokenManager.getToken()

    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    }

    const response = await fetch(url, config)

    // 处理401错误，自动清除token
    if (response.status === 401) {
      TokenManager.removeToken()
      // 不自动跳转，让路由守卫或组件自己处理
      throw new Error('未授权访问，请重新登录')
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Network error' }))
      throw new Error(error.detail || `HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  // 登录
  async login(credentials: LoginForm): Promise<Token> {
    const formData = new FormData()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)

    const result = await this.request<Token>('/token', {
      method: 'POST',
      headers: {}, // 不设置Content-Type，让浏览器自动设置FormData的边界
      body: formData,
    })

    // 登录成功后保存token
    TokenManager.setToken(result.access_token)
    return result
  }

  // 注册
  async register(registerData: any): Promise<{ message: string; user_id: number }> {
    return this.request<{ message: string; user_id: number }>('/register', {
      method: 'POST',
      body: JSON.stringify(registerData),
    })
  }

  // 管理员权限申请提交
  async submitAdminPermissionApply(applyData: any): Promise<{ message: string; user_id: number }> {
    return this.request<{ message: string; user_id: number }>('/admin/permission-apply/submit', {
      method: 'POST',
      body: JSON.stringify(applyData),
    })
  }

  // 企业绑定信息提交
  async submitEnterpriseBind(bindData: any): Promise<{ message: string; user_id: number }> {
    return this.request<{ message: string; user_id: number }>('/enterprise-backend/bind/submit', {
      method: 'POST',
      body: JSON.stringify(bindData),
    })
  }

  // 承包商绑定信息提交
  async submitContractorBind(bindData: any): Promise<{ message: string; user_id: number }> {
    return this.request<{ message: string; user_id: number }>('/contractor-backend/bind/submit', {
      method: 'POST',
      body: JSON.stringify(bindData),
    })
  }

  // 登出
  async logout(): Promise<void> {
    TokenManager.removeToken()
  }

  // 获取当前用户信息
  async getCurrentUser(): Promise<User> {
    return this.request<User>('/users/me/')
  }

  // 获取项目列表
  async getProjects(): Promise<ProjectListItem[]> {
    return this.request<ProjectListItem[]>('/projects/')
  }

  // 获取项目详情
  async getProjectDetail(projectId: number): Promise<ProjectDetail> {
    return this.request<ProjectDetail>(`/projects/${projectId}/`)
  }

  // 获取承包商列表
  async getContractors(): Promise<ContractorListItem[]> {
    return this.request<ContractorListItem[]>('/contractors/')
  }

  // 创建承包商项目
  async createContractorProject(request: ContractorProjectRequest): Promise<ContractorProjectResponse> {
    return this.request<ContractorProjectResponse>('/contractors/create-project/', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  // 获取计划参与人员列表
  async getPlanParticipants(planId: number): Promise<PlanParticipant[]> {
    return this.request<PlanParticipant[]>(`/plans/${planId}/participants/`)
  }

  // ===== 企业相关接口 =====

  // 获取企业列表（仅管理员）
  async getEnterprises(): Promise<EnterpriseListItem[]> {
    return this.request<EnterpriseListItem[]>('/enterprises/')
  }

  // 获取企业列表（管理员审批用，支持筛选）
  async getEnterprisesForApproval(params?: {
    business_status?: string
    company_type?: string
    keyword?: string
    page?: number
    page_size?: number
  }): Promise<EnterpriseListResponse> {
    const queryParams = new URLSearchParams()
    if (params?.business_status) queryParams.append('business_status', params.business_status)
    if (params?.company_type) queryParams.append('company_type', params.company_type)
    if (params?.keyword) queryParams.append('keyword', params.keyword)
    if (params?.page) queryParams.append('page', params.page.toString())
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString())
    
    const queryString = queryParams.toString()
    const url = `/admin/enterprises${queryString ? '?' + queryString : ''}`
    return this.request<EnterpriseListResponse>(url)
  }

  // 获取企业详情（管理员）
  async getEnterpriseDetail(enterpriseId: number): Promise<EnterpriseInfo> {
    return this.request<EnterpriseInfo>(`/admin/enterprises/${enterpriseId}/`)
  }

  // 审批企业（管理员）
  async approveEnterprise(
    enterpriseId: number,
    approved: boolean,
    comment?: string,
    adminApprovals?: Record<number, boolean>
  ): Promise<{ message: string; enterprise_id: number; business_status: string; comment?: string }> {
    const queryParams = new URLSearchParams()
    queryParams.append('approved', approved.toString())
    if (comment) queryParams.append('comment', comment)
    if (adminApprovals) {
      queryParams.append('admin_approvals', JSON.stringify(adminApprovals))
    }
    
    return this.request(`/admin/enterprises/${enterpriseId}/approve/?${queryParams.toString()}`, {
      method: 'POST',
    })
  }

  // ===== 承包商相关接口（管理员审批用） =====

  // 获取承包商列表（管理员审批用，支持筛选）
  async getContractorsForApproval(params?: {
    business_status?: string
    company_type?: string
    keyword?: string
    page?: number
    page_size?: number
  }): Promise<ContractorListResponse> {
    const queryParams = new URLSearchParams()
    if (params?.business_status) queryParams.append('business_status', params.business_status)
    if (params?.company_type) queryParams.append('company_type', params.company_type)
    if (params?.keyword) queryParams.append('keyword', params.keyword)
    if (params?.page) queryParams.append('page', params.page.toString())
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString())
    
    const queryString = queryParams.toString()
    const url = `/admin/contractors${queryString ? '?' + queryString : ''}`
    return this.request<ContractorListResponse>(url)
  }

  // 获取承包商详情（管理员）
  async getContractorDetail(contractorId: number): Promise<ContractorInfo> {
    return this.request<ContractorInfo>(`/admin/contractors/${contractorId}/`)
  }

  // 审批承包商（管理员）
  async approveContractor(
    contractorId: number,
    approved: boolean,
    comment?: string,
    adminApprovals?: Record<number, boolean>
  ): Promise<{ message: string; contractor_id: number; business_status: string; comment?: string }> {
    const queryParams = new URLSearchParams()
    queryParams.append('approved', approved.toString())
    if (comment) queryParams.append('comment', comment)
    if (adminApprovals) {
      queryParams.append('admin_approvals', JSON.stringify(adminApprovals))
    }
    
    return this.request(`/admin/contractors/${contractorId}/approve/?${queryParams.toString()}`, {
      method: 'POST',
    })
  }

  // ===== 人员审批相关接口（管理员用） =====

  // 获取待审批人员列表（管理员）
  async getPendingStaff(params?: {
    user_type?: string
    keyword?: string
    page?: number
    page_size?: number
  }): Promise<PendingStaffListResponse> {
    const queryParams = new URLSearchParams()
    if (params?.user_type) queryParams.append('user_type', params.user_type)
    if (params?.keyword) queryParams.append('keyword', params.keyword)
    if (params?.page) queryParams.append('page', params.page.toString())
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString())
    
    const queryString = queryParams.toString()
    const url = `/admin/users/pending${queryString ? '?' + queryString : ''}`
    return this.request<PendingStaffListResponse>(url)
  }

  // 审批人员（管理员）
  async approveStaff(
    userId: number,
    approved: boolean,
    comment?: string
  ): Promise<{ message: string; user_id: number; user_status: number; comment?: string }> {
    const queryParams = new URLSearchParams()
    queryParams.append('approved', approved.toString())
    if (comment) queryParams.append('comment', comment)
    
    return this.request(`/admin/users/${userId}/approve/?${queryParams.toString()}`, {
      method: 'POST',
    })
  }

  // 获取所有用户列表（管理员，支持多种过滤条件）
  async getAllUsers(params?: {
    user_type?: string
    user_status?: number
    role_level?: number
    username?: string
    user_id?: number
    enterprise_staff_id?: number
    contractor_staff_id?: number
    page?: number
    page_size?: number
  }): Promise<UserListResponse> {
    const queryParams = new URLSearchParams()
    if (params?.user_type) queryParams.append('user_type', params.user_type)
    if (params?.user_status !== undefined) queryParams.append('user_status', params.user_status.toString())
    if (params?.role_level !== undefined) queryParams.append('role_level', params.role_level.toString())
    if (params?.username) queryParams.append('username', params.username)
    if (params?.user_id) queryParams.append('user_id', params.user_id.toString())
    if (params?.enterprise_staff_id) queryParams.append('enterprise_staff_id', params.enterprise_staff_id.toString())
    if (params?.contractor_staff_id) queryParams.append('contractor_staff_id', params.contractor_staff_id.toString())
    if (params?.page) queryParams.append('page', params.page.toString())
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString())
    
    const queryString = queryParams.toString()
    const url = `/admin/users/all${queryString ? '?' + queryString : ''}`
    return this.request<UserListResponse>(url)
  }

  // 更新用户状态（管理员）
  async updateUserStatus(
    userId: number,
    userStatus: number,
    comment?: string
  ): Promise<{ message: string; user_id: number; user_status: number; comment?: string }> {
    const queryParams = new URLSearchParams()
    queryParams.append('user_status', userStatus.toString())
    if (comment) queryParams.append('comment', comment)
    
    return this.request(`/admin/users/${userId}/status/?${queryParams.toString()}`, {
      method: 'PUT',
    })
  }

  // ===== 部门相关接口 =====

  // 获取部门列表
  async getDepartments(enterpriseId?: number): Promise<DepartmentListItem[]> {
    const params = enterpriseId ? `?enterprise_id=${enterpriseId}` : ''
    return this.request<DepartmentListItem[]>(`/departments/${params}`)
  }

  // ===== 厂区相关接口 =====

  // 获取厂区列表
  async getAreas(enterpriseId?: number): Promise<AreaListItem[]> {
    const params = enterpriseId ? `?enterprise_id=${enterpriseId}` : ''
    return this.request<AreaListItem[]>(`/areas/${params}`)
  }

  // 获取厂区详情
  async getAreaDetail(areaId: number): Promise<Area> {
    return this.request<Area>(`/areas/${areaId}/`)
  }

  // 创建厂区
  async createArea(area: Area): Promise<{ message: string; area_id: number }> {
    return this.request<{ message: string; area_id: number }>('/areas/', {
      method: 'POST',
      body: JSON.stringify(area),
    })
  }

  // 更新厂区
  async updateArea(areaId: number, area: Area): Promise<{ message: string; area_id: number }> {
    return this.request<{ message: string; area_id: number }>(`/areas/${areaId}/`, {
      method: 'PUT',
      body: JSON.stringify(area),
    })
  }

  // 删除厂区
  async deleteArea(areaId: number): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/areas/${areaId}/`, {
      method: 'DELETE',
    })
  }

  // 获取企业的所有厂区
  async getEnterpriseAreas(enterpriseId: number): Promise<Area[]> {
    return this.request<Area[]>(`/enterprises/${enterpriseId}/areas/`)
  }

  // 获取部门的所有厂区
  async getDepartmentAreas(deptId: number): Promise<Area[]> {
    return this.request<Area[]>(`/departments/${deptId}/areas/`)
  }


  // ===== 人员管理相关接口 =====

  // 获取部门列表及成员数量
  async getDepartmentsWithMembers(): Promise<DepartmentWithMemberCount[]> {
    return this.request<DepartmentWithMemberCount[]>('/staff/departments/')
  }

  // 获取指定部门的成员列表
  async getDepartmentMembers(deptId: number): Promise<EnterpriseUserListItem[]> {
    return this.request<EnterpriseUserListItem[]>(`/staff/departments/${deptId}/members/`)
  }

  // 获取企业成员列表
  async getEnterpriseMembers(enterpriseId: number, deptId?: number): Promise<EnterpriseUserListItem[]> {
    const params = deptId ? `?dept_id=${deptId}` : ''
    return this.request<EnterpriseUserListItem[]>(`/staff/enterprise/${enterpriseId}/members/${params}`)
  }

  // 获取企业用户详情
  async getEnterpriseUserDetail(userId: number): Promise<EnterpriseUserListItem> {
    return this.request<EnterpriseUserListItem>(`/staff/users/${userId}/`)
  }

  // 更新企业用户信息
  async updateEnterpriseUser(userId: number, userData: EnterpriseUserUpdate): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/staff/users/${userId}/`, {
      method: 'PUT',
      body: JSON.stringify(userData),
    })
  }
}

// 导出TokenManager供其他地方使用
export { TokenManager }
export const apiService = new ApiService()
