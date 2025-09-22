from db import models as db_models
from api.model import User, UserType, EnterpriseUser, ContractorUser


def convert_user_db_to_response(user_db: db_models.User) -> User:
    # 处理企业用户
    enterprise_user = None
    if user_db.user_type == "enterprise" and user_db.enterprise_user:
        enterprise_user = convert_enterprise_user_to_response(user_db.enterprise_user)

    # 处理承包商用户
    contractor_user = None
    if user_db.user_type == "contractor" and user_db.contractor_user:
        contractor_user = convert_contractor_user_to_response(user_db.contractor_user)

    return User(
        user_id=user_db.user_id,
        user_type=UserType(user_db.user_type),
        username=user_db.username,
        enterprise_staff_id=user_db.enterprise_staff_id if user_db.enterprise_staff_id is not None else None,
        contractor_staff_id=user_db.contractor_staff_id if user_db.contractor_staff_id is not None else None,
        enterprise_user=enterprise_user,
        contractor_user=contractor_user
    )

def convert_enterprise_user_to_response(user_db: db_models.EnterpriseUser) -> EnterpriseUser:
    return EnterpriseUser(
        user_id=user_db.user_id,
        enterprise_id=user_db.company_id,  # 数据库中是company_id，API中是enterprise_id
        department_id=user_db.dept_id,     # 数据库中是dept_id，API中是department_id
        name=user_db.name,
        phone=user_db.phone,
        email=user_db.email,
        position=user_db.position,
        role_type=user_db.role_type,
        approval_level=user_db.approval_level,
        status=user_db.status
    )


def convert_contractor_user_to_response(user_db: db_models.ContractorUser) -> ContractorUser:
    return ContractorUser(
        user_id=user_db.user_id,
        contractor_id=user_db.contractor_id,
        name=user_db.name,
        phone=user_db.phone,
        id_number=user_db.id_number,
        work_type=user_db.work_type,
        personal_photo=user_db.personal_photo,
        role_type=user_db.role_type,
        status=user_db.status
    )