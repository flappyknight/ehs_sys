export interface LoginForm {
  username: string
  password: string
}

export interface Token {
  access_token: string
  token_type: string
}

export interface User {
  id: number
  username: string
  user_type: 'admin' | 'enterprise' | 'contractor'
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
