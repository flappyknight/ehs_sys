export interface LoginForm {
  username: string
  password: string
  userType?: 'enterprise' | 'contractor' | 'admin'
}

export interface RegisterForm {
  username: string
  password: string
  confirmPassword: string
  userType: 'enterprise' | 'contractor' | 'admin'
  phone: string
  email: string
  temp_token?: string  // 前端生成的临时token
}

export interface Token {
  access_token: string
  token_type: string
  redirect_to?: string
  message?: string
}

export interface User {
  user_id: number
  username: string
  user_type: 'admin' | 'enterprise' | 'contractor'
  user_level?: number
  audit_status?: number
  role_level?: number  // -1 用户还未选择角色, 0 系统管理员, 1 企业管理员, 2 企业员工, 3 承包商管理员, 4 承包商员工
  user_status?: number  // 用户状态：0未通过审核，1通过审核，2待审核，3审核不通过
  enterprise_staff_id?: number
  contractor_staff_id?: number
  is_deleted?: boolean  // 假删除标记
  enterprise_user?: EnterpriseUser
  contractor_user?: ContractorUser
}

export interface EnterpriseUser {
  id: number
  name: string
  phone: string
  role_type: 'manager' | 'approver' | 'site_staff'
  enterprise_id: number
  department_id?: number
}

export interface ContractorUser {
  id: number
  name: string
  phone: string
  role_type: 'manager' | 'approver' | 'site_staff'
  contractor_id: number
}

// 导航菜单项类型
export interface NavItem {
  key: string
  label: string
  path?: string
  children?: NavItem[]
}

// 用户权限类型
export type UserRole =
  | 'admin'
  | 'enterprise_manager'
  | 'enterprise_approver'
  | 'enterprise_site_staff'
  | 'contractor_manager'
  | 'contractor_approver'
  | 'contractor_site_staff'
