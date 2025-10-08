from datetime import datetime, date
from typing import List

from sqlmodel import SQLModel, Field, Relationship  #UniqueConstraint,


class User(SQLModel, table=True):
    __tablename__ = 'users'
    user_id: int = Field(default=None, primary_key=True)
    username: str = Field(max_length=50, unique=True, default=None, nullable=False)
    password_hash: str = Field(max_length=255, default=None, nullable=False)
    user_type: str = Field(max_length=20, default=0, nullable=False) # 约束检查 in [enterprise, contractor, admin]
    enterprise_staff_id: int = Field(default=None, foreign_key="enterprise_user.user_id", nullable=True)
    contractor_staff_id: int = Field(default=None, foreign_key="contractor_user.user_id", nullable=True)

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    enterprise_user: "EnterpriseUser" = Relationship(back_populates="user")
    contractor_user: "ContractorUser" = Relationship(back_populates="user")
    pass


class Company(SQLModel, table=True):
    __tablename__ = "company"  # 修正表名从 'user' 改为 'company'

    company_id: int = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, nullable=False)
    type: str = Field(max_length=20, nullable=False)  # 约束检查 in [enterprise, contractor]
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    

class Contractor(SQLModel, table=True):
    __tablename__ = 'contractor'
    contractor_id: int = Field(default=None, primary_key=True)
    license_file :str = Field(max_length=255,default=None, nullable=False)
    company_name: str = Field(max_length=255,default=None, nullable=False)
    company_type: str = Field(max_length=100,default=None, nullable=True)
    legal_person: str = Field(max_length=100,default=None, nullable=True)
    establish_date: date = Field(default=None, nullable=True)  # 修改字段名以匹配数据库
    registered_capital: float = Field(default=None, nullable=True)
    applicant_name: str = Field(max_length=100,default=None, nullable=True)

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    pass

class ContractorProject(SQLModel, table=True):
    __tablename__ = 'contractor_project'
    project_id: int = Field(default=None, primary_key=True)
    contractor_id: int = Field(default=None, foreign_key="contractor.contractor_id", nullable=False)
    enterprise_id: int = Field(default=None, foreign_key="company.company_id", nullable=False)
    project_name: str = Field(max_length=255, default=None, nullable=False)
    leader_name: str = Field(max_length=100, default=None, nullable=False)
    leader_phone: str = Field(max_length=20, default=None, nullable=False)

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    plans : List["EntryPlan"] = Relationship(back_populates="project")
    pass


class ContractorUser(SQLModel, table=True):
    __tablename__ = 'contractor_user'
    user_id: int = Field(default=None, primary_key=True)
    contractor_id: int = Field(default=None, foreign_key="contractor.contractor_id", nullable=False)
    name: str = Field(max_length=100, default=None, nullable=False)
    phone: str = Field(max_length=20, default=None, nullable=False)
    id_number: str = Field(max_length=50, default=None, nullable=False)
    work_type: str = Field(max_length=100, default=None, nullable=False)
    role_type: str = Field(max_length=10, default="normal", nullable=False)
    personal_photo: str = Field(max_length=255, default=None, nullable=False)
    status: bool = Field(default=False, nullable=False)

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    user: User = Relationship(back_populates="contractor_user")
    pass

class Department(SQLModel, table=True):
    __tablename__ = 'department'
    dept_id: int = Field(default=None, primary_key=True)
    company_id: int = Field(default=None, foreign_key="company.company_id", nullable=False)
    name: str = Field(max_length=255, default=None, nullable=False)
    parent_id: int = Field(default=None, nullable=True)

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    pass

class EnterpriseUser(SQLModel, table=True):
    __tablename__ = 'enterprise_user'
    user_id: int = Field(default=None, primary_key=True)
    company_id: int = Field(default=None, foreign_key="company.company_id", nullable=False)
    dept_id: int = Field(default=None, foreign_key="department.dept_id", nullable=True)
    name: str = Field(max_length=100, default=None, nullable=False)
    phone: str = Field(max_length=20, default=None, nullable=False)
    email: str = Field(max_length=100, default=None, nullable=False)
    position: str = Field(max_length=100, default=None, nullable=True)
    role_type: str = Field(max_length=100, default=None, nullable=False)
    approval_level: int = Field(default=4, nullable=False)
    status: bool = Field(default=True, nullable=False)

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    user: User = Relationship(back_populates="enterprise_user")
    pass


class EntryPlan(SQLModel, table=True):
    __tablename__ = 'entry_plan'
    plan_id: int = Field(default=None, primary_key=True)
    project_id: int = Field(default=None, foreign_key="contractor_project.project_id", nullable=False)
    plan_date: date = Field(default=None, nullable=False)
    status: int = Field(default=0, nullable=False)

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    workers: List["EntryPlanUser"] = Relationship(back_populates="plan")
    project: ContractorProject = Relationship(back_populates="plans")
    pass


class EntryPlanUser(SQLModel, table=True):
    __tablename__ = 'entry_plan_user'
    id: int = Field(default=None, primary_key=True)
    project_id: int = Field(default=None, foreign_key="contractor_project.project_id", nullable=False)
    plan_id: int = Field(default=None, foreign_key="entry_plan.plan_id", nullable=False)
    user_id: int = Field(default=None, foreign_key="contractor_user.user_id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.now)

    plan: EntryPlan = Relationship(back_populates="workers")


class EntryRegister(SQLModel, table=True):
    __tablename__ = 'entry_register'
    register_id: int = Field(default=None, primary_key=True)
    plan_user_id: int = Field(default=None, foreign_key="entry_plan_user.id", nullable=False)
    actual_time: datetime = Field(default=None, nullable=False)
    photo_path: str = Field(max_length=255, default=None, nullable=False)

    created_at: datetime = Field(default_factory=datetime.now)

class Area(SQLModel, table=True):
    __tablename__ = 'area'
    area_id: int = Field(default=None, primary_key=True)
    enterprise_id: int = Field(default=None, foreign_key="company.company_id", nullable=False)
    area_name: str = Field(max_length=64, default=None, nullable=False)
    dept_id: int = Field(default=None, foreign_key="department.dept_id", nullable=True)
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# 作业设备表
class WorkEquipment(SQLModel, table=True):
    __tablename__ = 'work_equipment'
    equipment_id: int = Field(default=None, primary_key=True)
    equipment_name: str = Field(max_length=100, default=None, nullable=False)
    equipment_power: str = Field(max_length=50, default=None, nullable=False)  # 设备功率
    work_voltage: str = Field(max_length=50, default=None, nullable=False)  # 工作电压
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

# 受限空间表
class ConfinedSpace(SQLModel, table=True):
    __tablename__ = 'confined_space'
    confined_space_id: int = Field(default=None, primary_key=True)
    ticket_id: int = Field(default=None, foreign_key="ticket.ticket_id", nullable=False)
    space_level: int = Field(default=None, nullable=False)  # 受限空间等级 (1:一级，2：二级)
    space_name: str = Field(max_length=50, default=None, nullable=False)  # 受限空间名称
    original_medium: str = Field(max_length=50, default=None, nullable=False)  # 有限空间原有介质
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

# 临时用电表
class TemporaryPower(SQLModel, table=True):
    __tablename__ = 'temporary_power'
    temp_power_id: int = Field(default=None, primary_key=True)
    ticket_id: int = Field(default=None, foreign_key="ticket.ticket_id", nullable=False)
    equipment_id: int = Field(default=None, foreign_key="work_equipment.equipment_id", nullable=False)
    power_access_point: str = Field(max_length=100, default=None, nullable=False)  # 电源接入点
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

# 交叉作业表
class CrossWork(SQLModel, table=True):
    __tablename__ = 'cross_work'
    id: int = Field(default=None, primary_key=True)
    group_id: str = Field(max_length=50, default=None, nullable=False)  # 交叉作业组ID
    area_id: int = Field(default=None, foreign_key="area.area_id", nullable=False)
    ticket_id: int = Field(default=None, foreign_key="ticket.ticket_id", nullable=False)
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

# 修改后的作业票表
class Ticket(SQLModel, table=True):
    __tablename__ = 'ticket'
    ticket_id: int = Field(default=None, primary_key=True)
    apply_date: date = Field(default=None, nullable=False)
    applicant: int = Field(default=None, foreign_key="enterprise_user.user_id", nullable=False)
    area_id: int = Field(default=None, foreign_key="area.area_id", nullable=False)
    working_content: str = Field(max_length=1024, default=None, nullable=False)
    pre_st: datetime = Field(default=None, nullable=False)  # 预计开始时间
    pre_et: datetime = Field(default=None, nullable=False)  # 预计结束时间
    tools: int = Field(default=0, nullable=False)  # 主要工具（二进制编码）
    worker: int = Field(default=None, foreign_key="contractor_user.user_id", nullable=False)
    custodians: int = Field(default=None, foreign_key="enterprise_user.user_id", nullable=False)  # 监护人
    danger: int = Field(default=0, nullable=False)  # 危险识别（二进制编码）
    protection: int = Field(default=0, nullable=False)  # 防护措施（二进制编码）
    
    # 特殊作业字段
    hot_work: int = Field(default=-1, nullable=False)  # 动火等级：-1:未动火 0:特级动火 1:一级动火 2:二级动火
    work_height_level: int = Field(default=0, nullable=False)  # 作业高度等级：0-4级，数值越大危险程度越高
    confined_space_id: int = Field(default=None, foreign_key="confined_space.confined_space_id", nullable=True)  # 受限空间ID
    temp_power_id: int = Field(default=None, foreign_key="temporary_power.temp_power_id", nullable=True)  # 临时用电ID
    cross_work_group_id: str = Field(max_length=50, default=None, nullable=True)  # 交叉作业组ID
    
    signature: str = Field(max_length=255, default=None, nullable=True)  # 签字
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
