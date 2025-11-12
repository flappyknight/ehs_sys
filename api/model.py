from datetime import date
from typing import List, Optional
from pydantic import BaseModel
from enum import Enum, IntEnum


class Token(BaseModel):
    access_token: str
    token_type: str
    redirect_to: Optional[str] = None  # 前端重定向路径
    message: Optional[str] = None  # 提示信息


class UserType(str, Enum):
    contractor = "contractor"
    enterprise = "enterprise"
    admin = "admin"


class RegisterRequest(BaseModel):
    username: str
    password: str
    userType: str  # 'enterprise', 'contractor', or 'admin'
    phone: str
    email: str
    temp_token: str  # 前端生成的临时token


class PermissionLevel(IntEnum):
    manager = 3
    approver = 2
    site_staff = 1

    @classmethod
    def map(cls, key: str):
        return getattr(cls, key)


class ApprovalLevel(IntEnum):
    level_1 = 1
    level_2 = 2
    level_3 = 3


class User(BaseModel):
    user_id: Optional[int] = None
    user_type: UserType
    username: str
    password_hash: Optional[str] = None
    enterprise_staff_id: Optional[int] = None
    contractor_staff_id: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    user_level: Optional[int] = None
    audit_status: Optional[int] = None
    temp_token: Optional[str] = None
    sys_only_id: Optional[int] = None
    enterprise_user: Optional["EnterpriseUser"] = None
    contractor_user: Optional["ContractorUser"] = None


class EnterpriseUser(BaseModel):
    user_id: Optional[int] = None
    enterprise_id: int
    department_id: Optional[int] = None
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    position: Optional[str] = None
    role_type: str = "normal"
    role_id: Optional[int] = None
    approval_level: ApprovalLevel | int = ApprovalLevel.level_1
    status: int = 1
    sys_only_id: Optional[int] = None


class EnterpriseInfo(BaseModel):
    """企业信息模型"""
    enterprise_id: Optional[int] = None
    license_file: str
    company_name: str
    company_type: Optional[str] = None
    legal_person: Optional[str] = None
    establish_date: Optional[str] = None
    registered_capital: Optional[float] = None
    applicant_name: Optional[str] = None
    business_status: str = "续存"
    is_deleted: bool = False
    parent_enterprise_id: Optional[int] = None
    subsidiary_ids: List[int] = []
    allowed_contractor_ids: List[int] = []
    modification_log: List[dict] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class EnterpriseInfoCreate(BaseModel):
    """创建企业信息请求模型"""
    license_file: str
    company_name: str
    company_type: Optional[str] = None
    legal_person: Optional[str] = None
    establish_date: Optional[str] = None
    registered_capital: Optional[float] = None
    applicant_name: Optional[str] = None
    parent_enterprise_id: Optional[int] = None


class EnterpriseInfoUpdate(BaseModel):
    """更新企业信息请求模型"""
    license_file: Optional[str] = None
    company_name: Optional[str] = None
    company_type: Optional[str] = None
    legal_person: Optional[str] = None
    establish_date: Optional[str] = None
    registered_capital: Optional[float] = None
    applicant_name: Optional[str] = None
    business_status: Optional[str] = None
    parent_enterprise_id: Optional[int] = None


class ContractorInfo(BaseModel):
    """承包商信息模型"""
    contractor_id: Optional[int] = None
    license_file: str
    company_name: str
    company_type: Optional[str] = None
    legal_person: Optional[str] = None
    establish_date: Optional[str] = None
    registered_capital: Optional[float] = None
    applicant_name: Optional[str] = None
    business_status: str = "续存"
    is_deleted: bool = False
    active_enterprise_ids: List[int] = []
    inactive_enterprise_ids: List[int] = []
    cooperation_detail_log: List[dict] = []
    modification_log: List[dict] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ContractorInfoCreate(BaseModel):
    """创建承包商信息请求模型"""
    license_file: str
    company_name: str
    company_type: Optional[str] = None
    legal_person: Optional[str] = None
    establish_date: Optional[str] = None
    registered_capital: Optional[float] = None
    applicant_name: Optional[str] = None


class ContractorInfoUpdate(BaseModel):
    """更新承包商信息请求模型"""
    license_file: Optional[str] = None
    company_name: Optional[str] = None
    company_type: Optional[str] = None
    legal_person: Optional[str] = None
    establish_date: Optional[str] = None
    registered_capital: Optional[float] = None
    applicant_name: Optional[str] = None
    business_status: Optional[str] = None




class Project(BaseModel):
    project_id: Optional[int] = None
    contractor_id: int
    enterprise_id: int
    project_name: str
    project_leader: str
    leader_phone: str


class ContractorUser(BaseModel):
    user_id: Optional[int] = None
    contractor_id: int
    name: str
    phone: str
    id_number: str
    work_type: str
    personal_photo: str
    role_type: str
    status: int
    sys_only_id: Optional[int] = None


class ContractorListItem(BaseModel):
    contractor_id: int
    company_name: str
    company_type: str
    legal_person: str
    establish_date: str
    project_count: int


class ContractorProjectRequest(BaseModel):
    contractor_id: Optional[int] = None
    company_name: Optional[str] = None
    license_file: Optional[str] = None
    company_type: Optional[str] = None
    legal_person: Optional[str] = None
    establish_date: Optional[str] = None
    registered_capital: Optional[float] = None
    applicant_name: Optional[str] = None
    project_name: str
    leader_name: str
    leader_phone: str


class ContractorProjectResponse(BaseModel):
    contractor_id: int
    project_id: int
    message: str


# ===== 人员管理相关模型 =====

class EnterpriseUserListItem(BaseModel):
    """企业用户列表项"""
    user_id: int
    name: str
    phone: str
    email: str
    position: Optional[str] = None
    role_type: str
    company_name: str
    dept_id: Optional[int] = None
    status: int


class EnterpriseUserUpdate(BaseModel):
    """企业用户更新模型"""
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    position: Optional[str] = None
    dept_id: Optional[int] = None
    role_type: Optional[str] = None
    status: Optional[int] = None


# ===== 工单管理相关模型 =====

class TicketCreate(BaseModel):
    """创建工单请求模型"""
    apply_date: date
    applicant: int
    area_id: Optional[int] = None
    working_content: str
    pre_st: str
    pre_et: str
    tools: int = 0
    worker: int
    custodians: int
    danger: int = 0
    protection: int = 0
    hot_work: int = -1
    work_height_level: int = 0
    confined_space_id: Optional[int] = None
    temp_power_id: Optional[int] = None
    cross_work_group_id: Optional[str] = None
    signature: Optional[str] = None


class TicketUpdate(BaseModel):
    """更新工单请求模型"""
    apply_date: Optional[date] = None
    area_id: Optional[int] = None
    working_content: Optional[str] = None
    pre_st: Optional[str] = None
    pre_et: Optional[str] = None
    tools: Optional[int] = None
    worker: Optional[int] = None
    custodians: Optional[int] = None
    danger: Optional[int] = None
    protection: Optional[int] = None
    hot_work: Optional[int] = None
    work_height_level: Optional[int] = None
    confined_space_id: Optional[int] = None
    temp_power_id: Optional[int] = None
    cross_work_group_id: Optional[str] = None
    signature: Optional[str] = None


class TicketListItem(BaseModel):
    """工单列表项"""
    ticket_id: int
    apply_date: date
    applicant_name: str
    area_name: Optional[str] = None
    working_content: str
    pre_st: str
    pre_et: str
    worker_name: str
    custodian_name: str
    hot_work: int
    work_height_level: int
    created_at: str


class TicketDetail(BaseModel):
    """工单详情"""
    ticket_id: int
    apply_date: date
    applicant: int
    applicant_name: str
    area_id: Optional[int] = None
    area_name: Optional[str] = None
    working_content: str
    pre_st: str
    pre_et: str
    tools: int
    worker: int
    worker_name: str
    custodians: int
    custodian_name: str
    danger: int
    protection: int
    hot_work: int
    work_height_level: int
    confined_space_id: Optional[int] = None
    temp_power_id: Optional[int] = None
    cross_work_group_id: Optional[str] = None
    signature: Optional[str] = None
    created_at: str
    updated_at: str


# ===== 用户管理相关模型 =====

class UserCreate(BaseModel):
    """创建用户请求模型"""
    username: str
    password: str
    user_type: UserType
    enterprise_id: Optional[int] = None
    contractor_id: Optional[int] = None
    name: str
    phone: str
    email: Optional[str] = None
    position: Optional[str] = None
    role_type: str = "normal"
    department_id: Optional[int] = None
    id_number: Optional[str] = None
    work_type: Optional[str] = None
    personal_photo: Optional[str] = None


class UserUpdate(BaseModel):
    """更新用户请求模型"""
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    position: Optional[str] = None
    role_type: Optional[str] = None
    department_id: Optional[int] = None
    status: Optional[int] = None
    password: Optional[str] = None


class UserListItem(BaseModel):
    """用户列表项"""
    user_id: int
    username: str
    user_type: UserType
    name: str
    phone: str
    email: Optional[str] = None
    role_type: str
    status: int
    company_name: Optional[str] = None
    department_name: Optional[str] = None
    created_at: str


class UserDetail(BaseModel):
    """用户详情"""
    user_id: int
    username: str
    user_type: UserType
    name: str
    phone: str
    email: Optional[str] = None
    position: Optional[str] = None
    role_type: str
    status: int
    company_id: Optional[int] = None
    company_name: Optional[str] = None
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    contractor_id: Optional[int] = None
    id_number: Optional[str] = None
    work_type: Optional[str] = None
    approval_level: Optional[int] = None
    created_at: str
    updated_at: str


class PasswordChange(BaseModel):
    """修改密码请求模型"""
    old_password: str
    new_password: str


class PasswordReset(BaseModel):
    """重置密码请求模型（管理员操作）"""
    new_password: str


# ===== 角色管理相关模型 =====

class RoleInfo(BaseModel):
    """角色信息"""
    role_type: str
    role_name: str
    description: str
    permission_level: int
    user_type: UserType


class RoleListItem(BaseModel):
    """角色列表项"""
    role_type: str
    role_name: str
    description: str
    permission_level: int
    user_count: int


class RolePermission(BaseModel):
    """角色权限"""
    role_type: str
    permissions: List[str]


class UserRoleUpdate(BaseModel):
    """更新用户角色"""
    role_type: str
