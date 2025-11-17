from datetime import datetime, date
from typing import Optional, Any

from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy.dialects.postgresql import JSONB


class User(SQLModel, table=True):
    """用户表 - 存储所有用户的登录凭证和基本信息"""
    __tablename__ = 'users'
    user_id: int = Field(default=None, primary_key=True)
    username: str = Field(max_length=50, unique=True, default=None, nullable=False)
    password_hash: str = Field(max_length=255, default=None, nullable=False)
    user_type: str = Field(max_length=20, default=0, nullable=False)  # enterprise, contractor, admin
    enterprise_staff_id: Optional[int] = Field(default=None, nullable=True)  # 保留字段，但不再有外键约束
    contractor_staff_id: Optional[int] = Field(default=None, nullable=True)  # 保留字段，但不再有外键约束
    phone: Optional[str] = Field(max_length=20, default=None, nullable=True)
    email: Optional[str] = Field(max_length=100, default=None, nullable=True)
    user_level: Optional[int] = Field(default=None, nullable=True)
    audit_status: Optional[int] = Field(default=None, nullable=True)
    temp_token: Optional[str] = Field(max_length=500, default=None, nullable=True)
    relay_name: Optional[str] = Field(max_length=100, default=None, nullable=True)
    sys_only_id: Optional[int] = Field(default=None, unique=True, nullable=True)
    # 新增字段
    name_str: Optional[str] = Field(max_length=100, default=None, nullable=True)  # 姓名
    role_type: Optional[str] = Field(max_length=100, default=None, nullable=True)  # 角色类型
    role_level: Optional[int] = Field(default=None, nullable=True)  # 角色等级
    user_status: Optional[int] = Field(default=None, nullable=True)  # 用户状态
    work_type: Optional[str] = Field(max_length=100, default='', nullable=False)  # 工种
    is_deleted: bool = Field(default=False, nullable=False)  # 假删除标记

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class EnterpriseInfo(SQLModel, table=True):
    """企业信息表 - 存储企业基本信息、组织关系及合作承包商信息"""
    __tablename__ = 'enterprise_info'
    enterprise_id: int = Field(default=None, primary_key=True)
    license_file: str = Field(max_length=255, default=None, nullable=False)
    license_number: Optional[str] = Field(max_length=100, default=None, nullable=True)
    company_name: str = Field(max_length=255, default=None, nullable=False)
    company_type: Optional[str] = Field(max_length=100, default=None, nullable=True)
    company_address: Optional[str] = Field(max_length=255, default=None, nullable=True)
    legal_person: Optional[str] = Field(max_length=100, default=None, nullable=True)
    establish_date: Optional[date] = Field(default=None, nullable=True)
    registered_capital: Optional[float] = Field(default=None, nullable=True)
    applicant_name: Optional[str] = Field(max_length=100, default=None, nullable=True)
    business_status: str = Field(max_length=50, default='续存', nullable=False)
    is_deleted: bool = Field(default=False, nullable=False)
    parent_enterprise_id: Optional[int] = Field(default=None, nullable=True)
    subsidiary_ids: Any = Field(default_factory=list, sa_column=Column(JSONB))
    allowed_contractor_ids: Any = Field(default_factory=list, sa_column=Column(JSONB))
    modification_log: Any = Field(default_factory=list, sa_column=Column(JSONB))
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ContractorInfo(SQLModel, table=True):
    """承包商信息表 - 存储承包商基本信息、合作状态及合作企业详情"""
    __tablename__ = 'contractor_info'
    contractor_id: int = Field(default=None, primary_key=True)
    license_file: str = Field(max_length=255, default=None, nullable=False)
    license_number: Optional[str] = Field(max_length=100, default=None, nullable=True)
    company_name: str = Field(max_length=255, default=None, nullable=False)
    company_type: Optional[str] = Field(max_length=100, default=None, nullable=True)
    company_address: Optional[str] = Field(max_length=255, default=None, nullable=True)
    legal_person: Optional[str] = Field(max_length=100, default=None, nullable=True)
    establish_date: Optional[date] = Field(default=None, nullable=True)
    registered_capital: Optional[float] = Field(default=None, nullable=True)
    applicant_name: Optional[str] = Field(max_length=100, default=None, nullable=True)
    business_status: str = Field(max_length=50, default='续存', nullable=False)
    is_deleted: bool = Field(default=False, nullable=False)
    active_enterprise_ids: Any = Field(default_factory=list, sa_column=Column(JSONB))
    inactive_enterprise_ids: Any = Field(default_factory=list, sa_column=Column(JSONB))
    cooperation_detail_log: Any = Field(default_factory=list, sa_column=Column(JSONB))
    modification_log: Any = Field(default_factory=list, sa_column=Column(JSONB))

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)




class ContractorProject(SQLModel, table=True):
    """承包商项目表"""
    __tablename__ = 'contractor_project'
    project_id: int = Field(default=None, primary_key=True)
    contractor_id: int = Field(default=None, nullable=False)
    enterprise_id: int = Field(default=None, nullable=False)
    project_name: str = Field(max_length=255, default=None, nullable=False)
    leader_name_str: str = Field(max_length=100, default=None, nullable=False)
    leader_phone: str = Field(max_length=20, default=None, nullable=False)

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# 注意：ContractorUser和EnterpriseUser表已删除，模型定义保留用于兼容性
# 但不再使用table=True，避免SQLAlchemy尝试创建表
class ContractorUser(SQLModel):
    """承包商用户表（已删除，仅保留用于兼容性）"""
    __tablename__ = 'contractor_user'
    user_id: Optional[int] = None
    contractor_id: Optional[int] = None
    name_str: Optional[str] = None
    phone: Optional[str] = None
    id_number: Optional[str] = None
    work_type: Optional[str] = None
    role_type: Optional[str] = None
    personal_photo: Optional[str] = None
    status: Optional[int] = None
    relay_name: Optional[str] = None
    sys_only_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class EnterpriseUser(SQLModel):
    """企业用户表（已删除，仅保留用于兼容性）"""
    __tablename__ = 'enterprise_user'
    user_id: Optional[int] = None
    company_id: Optional[int] = None
    dept_id: Optional[int] = None
    name_str: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    position: Optional[str] = None
    role_type: Optional[str] = None
    role_id: Optional[int] = None
    approval_level: Optional[int] = None
    status: Optional[int] = None
    relay_name: Optional[str] = None
    sys_only_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Ticket(SQLModel, table=True):
    """作业票表"""
    __tablename__ = 'ticket'
    ticket_id: int = Field(default=None, primary_key=True)
    apply_date: date = Field(default=None, nullable=False)
    applicant: int = Field(default=None, foreign_key="users.user_id", nullable=False)
    area_id: Optional[int] = Field(default=None, nullable=True)
    working_content: str = Field(max_length=1024, default=None, nullable=False)
    pre_st: datetime = Field(default=None, nullable=False)
    pre_et: datetime = Field(default=None, nullable=False)
    tools: int = Field(default=0, nullable=False)
    worker: int = Field(default=None, foreign_key="users.user_id", nullable=False)
    custodians: int = Field(default=None, foreign_key="users.user_id", nullable=False)
    danger: int = Field(default=0, nullable=False)
    protection: int = Field(default=0, nullable=False)
    
    # 特殊作业字段
    hot_work: int = Field(default=-1, nullable=False)
    work_height_level: int = Field(default=0, nullable=False)
    confined_space_id: Optional[int] = Field(default=None, nullable=True)
    temp_power_id: Optional[int] = Field(default=None, nullable=True)
    cross_work_group_id: Optional[str] = Field(max_length=50, default=None, nullable=True)
    
    signature: Optional[str] = Field(max_length=255, default=None, nullable=True)
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
