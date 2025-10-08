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
    enterprise_id: int
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


