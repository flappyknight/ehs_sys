from datetime import date
from typing import List, Optional
from pydantic import BaseModel
from enum import Enum, IntEnum

class Token(BaseModel):
    access_token: str
    token_type: str


class UserType(str, Enum):
    contractor = "contractor"
    enterprise = "enterprise"
    admin = "admin"
    pass


class PermissionLevel(IntEnum):
    manager = 3
    approver = 2
    site_staff = 1

    @classmethod
    def map(cls, key:str):
        return getattr(cls, key)


class ApprovalLevel(IntEnum):
    level_1 = 1
    level_2 = 2
    level_3 = 3
    pass

class User(BaseModel):
    user_id: Optional[int] = None
    user_type: UserType
    username: str
    password_hash: Optional[str] = None
    enterprise_staff_id: Optional[int] = None
    contractor_staff_id: Optional[int] = None
    enterprise_user: Optional["EnterpriseUser"] = None
    contractor_user: Optional["ContractorUser"] = None
    pass

class Enterprise(BaseModel):
    enterprise_id: Optional[int] = None
    name: Optional[str] = None
    type: str = "enterprise"
    pass

class EnterpriseUser(BaseModel):
    user_id: Optional[int] = None
    enterprise_id: int
    department_id: Optional[int] = None
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    position: Optional[str] = None
    role_type: str = "normal"
    approval_level: ApprovalLevel|int = ApprovalLevel.level_1
    status: bool = True
    pass

class Contractor(BaseModel):
    contractor_id: Optional[int] = None
    company_name: str
    license_file: str
    company_type: str
    legal_person: str
    establish_date: str
    registered_capital: int
    applicant_name: str
    pass

class Project(BaseModel):
    project_id: Optional[int] = None
    contractor_id: int
    enterprise_id: int
    project_name: str
    project_leader: str
    leader_phone: str
    pass

class Plan(BaseModel):
    plan_id: Optional[int] = None
    project_id: int
    plan_date: date
    workers: List[int]
    pass

class PlanWorker(BaseModel):
    plan_user_id: Optional[int] = None
    plan_id: int
    user_id: int

class ContractorUser(BaseModel):
    user_id: Optional[int] = None
    contractor_id: int
    name: str
    phone: str
    id_number: str
    work_type: str
    personal_photo: str
    role_type: str
    status: bool

class Department(BaseModel):
    department_id: Optional[int] = None
    enterprise_id: int
    name: str
    parent_id: Optional[int] = None
    pass

# 新增企业响应类型
class EnterpriseListItem(BaseModel):
    company_id: int
    name: str
    type: str

# 新增部门响应类型  
class DepartmentListItem(BaseModel):
    dept_id: int
    company_id: int
    name: str
    parent_id: Optional[int] = None


class ProjectListItem(BaseModel):
    project_id: int
    project_name: str
    contractor_name: str
    project_leader: str
    leader_phone: str
    planned_entry_count: int  # 已计划进场数/次

class ProjectDetail(BaseModel):
    project_id: int
    project_name: str
    contractor_name: str
    project_leader: str
    leader_phone: str
    plans: List["PlanDetail"]

class PlanDetail(BaseModel):
    plan_id: int
    project_name: str
    plan_date: date
    participant_count: int  # 计划参与人数
    is_completed: bool  # 是否完成计划
    participants: List["PlanParticipant"] = []

class PlanParticipant(BaseModel):
    user_id: int
    name: str
    phone: str
    id_number: str
    is_registered: bool  # 是否登记


class ContractorListItem(BaseModel):
    contractor_id: int
    company_name: str
    company_type: str
    legal_person: str
    establish_date: str
    project_count: int  # 合作项目数量

class ContractorProjectRequest(BaseModel):
    # 承包商信息（新承包商时必填，已有承包商时只需contractor_id）
    contractor_id: Optional[int] = None  # 已有承包商的ID
    company_name: Optional[str] = None
    license_file: Optional[str] = None
    company_type: Optional[str] = None
    legal_person: Optional[str] = None
    establish_date: Optional[str] = None
    registered_capital: Optional[float] = None
    applicant_name: Optional[str] = None
    
    # 项目信息（必填）
    project_name: str
    leader_name: str
    leader_phone: str

class ContractorProjectResponse(BaseModel):
    contractor_id: int
    project_id: int
    message: str

class Area(BaseModel):
    area_id: Optional[int] = None
    enterprise_id: Optional[int] = None
    area_name: str
    dept_id: Optional[int] = None
    pass

class AreaListItem(BaseModel):
    area_id: int
    area_name: str
    enterprise_name: str
    dept_name: Optional[str] = None
    pass


# ===== 人员管理相关模型 =====

class DepartmentWithMemberCount(BaseModel):
    """部门信息及成员数量"""
    dept_id: int
    name: str
    company_id: int
    company_name: str
    member_count: int
    parent_id: Optional[int] = None  # 修复：使用 Optional[int]

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
    status: bool

class EnterpriseUserUpdate(BaseModel):
    """企业用户更新模型"""
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    position: Optional[str] = None
    dept_id: Optional[int] = None
    role_type: Optional[str] = None
    status: Optional[bool] = None


# ===== 工单管理相关模型 =====

class TicketCreate(BaseModel):
    """创建工单请求模型"""
    apply_date: date
    applicant: int  # 申请人ID
    area_id: int  # 作业区域ID
    working_content: str  # 作业内容
    pre_st: str  # 预计开始时间
    pre_et: str  # 预计结束时间
    tools: int = 0  # 主要工具（二进制编码）
    worker: int  # 作业人员ID
    custodians: int  # 监护人ID
    danger: int = 0  # 危险识别（二进制编码）
    protection: int = 0  # 防护措施（二进制编码）
    hot_work: int = -1  # 动火等级：-1:未动火 0:特级动火 1:一级动火 2:二级动火
    work_height_level: int = 0  # 作业高度等级：0-4级
    confined_space_id: Optional[int] = None  # 受限空间ID
    temp_power_id: Optional[int] = None  # 临时用电ID
    cross_work_group_id: Optional[str] = None  # 交叉作业组ID
    signature: Optional[str] = None  # 签字


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
    applicant_name: str  # 申请人姓名
    area_name: str  # 作业区域名称
    working_content: str  # 作业内容
    pre_st: str  # 预计开始时间
    pre_et: str  # 预计结束时间
    worker_name: str  # 作业人员姓名
    custodian_name: str  # 监护人姓名
    hot_work: int  # 动火等级
    work_height_level: int  # 作业高度等级
    created_at: str  # 创建时间


class TicketDetail(BaseModel):
    """工单详情"""
    ticket_id: int
    apply_date: date
    applicant: int
    applicant_name: str
    area_id: int
    area_name: str
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
    enterprise_id: Optional[int] = None  # 企业用户必填
    contractor_id: Optional[int] = None  # 承包商用户必填
    name: str
    phone: str
    email: Optional[str] = None
    position: Optional[str] = None
    role_type: str = "normal"
    department_id: Optional[int] = None  # 企业用户可选
    id_number: Optional[str] = None  # 承包商用户必填
    work_type: Optional[str] = None  # 承包商用户必填
    personal_photo: Optional[str] = None  # 承包商用户可选


class UserUpdate(BaseModel):
    """更新用户请求模型"""
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    position: Optional[str] = None
    role_type: Optional[str] = None
    department_id: Optional[int] = None
    status: Optional[bool] = None
    password: Optional[str] = None  # 可选修改密码


class UserListItem(BaseModel):
    """用户列表项"""
    user_id: int
    username: str
    user_type: UserType
    name: str
    phone: str
    email: Optional[str] = None
    role_type: str
    status: bool
    company_name: Optional[str] = None  # 所属企业/承包商名称
    department_name: Optional[str] = None  # 部门名称（企业用户）
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
    status: bool
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
    user_count: int  # 使用该角色的用户数量


class RolePermission(BaseModel):
    """角色权限"""
    role_type: str
    permissions: List[str]  # 权限列表


class UserRoleUpdate(BaseModel):
    """更新用户角色"""
    role_type: str


