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
