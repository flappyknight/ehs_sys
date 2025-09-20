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
    normal = 1
    advanced = 2
    admin =3

    @classmethod
    def map(cls, key:str):
        return getattr(cls, key)


class ApprovalLevel(IntEnum):
    level_1 = 1
    level_2 = 2
    level_3 = 3
    pass


class Enterprise(BaseModel):
    enterprise_id: int =None
    name: str = None
    type: str = "enterprise"

    pass


class EnterpriseUser(BaseModel):
    user_id: int = None
    enterprise_id: int
    department_id: int = None
    name: str
    phone: str = None
    email: str = None
    position: str = None
    role_type: str = "normal"
    approval_level: ApprovalLevel = ApprovalLevel.level_1
    status: bool = True
    pass


class Contractor(BaseModel):
    contractor_id: int =None
    company_name: str
    license_file: str
    company_type: str
    legal_person: str
    establish_date: str
    registered_capital: int
    applicant_name: str

    pass


class Project(BaseModel):
    project_id: int = None
    project_name: str
    project_leader: str
    leader_phone: str
    pass


class Plan(BaseModel):
    plan_id: int = None
    project_id: int
    project_name: str
    plan_date: str

    pass

class PlanWorker(BaseModel):
    plan_user_id: int = None
    plan_id: int
    user_id: int


class ContractorUser(BaseModel):
    user_id: int = None
    contractor_id: int
    name: str
    phone: str
    id_number: str
    work_type: str
    personal_photo: str
    role_type: str
    status: bool


class Department(BaseModel):
    department_id: int = None
    enterprise_id: int
    name: str
    parent_id: int = None
    pass