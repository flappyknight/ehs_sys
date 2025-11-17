from db import models as db_models
from api.model import User, UserType, EnterpriseUser, ContractorUser, ContractorListItem
from db import crud
from typing import List


def convert_user_db_to_response(user_db: db_models.User) -> User:
    # 处理企业用户（从users表的新字段构建）
    enterprise_user = None
    if user_db.user_type == "enterprise":
        # 从users表的新字段构建EnterpriseUser对象
        # enterprise_staff_id 直接存储了 enterprise_id（根据之前的修改）
        enterprise_id = user_db.enterprise_staff_id if hasattr(user_db, 'enterprise_staff_id') and user_db.enterprise_staff_id is not None else 0
        name = user_db.name_str if hasattr(user_db, 'name_str') and user_db.name_str else (user_db.relay_name if hasattr(user_db, 'relay_name') and user_db.relay_name else user_db.username)
        
        # 只有在有足够数据时才创建 EnterpriseUser 对象
        # 如果 enterprise_id 为 0 或 None，说明用户还没有绑定企业，不创建 enterprise_user
        if enterprise_id and enterprise_id > 0:
            from api.model import ApprovalLevel
            enterprise_user = EnterpriseUser(
                user_id=user_db.user_id,
                enterprise_id=enterprise_id,  # enterprise_staff_id 就是 enterprise_id
                department_id=None,  # 需要从其他地方获取
                name=name or user_db.username,  # 确保 name 不为空
                phone=user_db.phone if hasattr(user_db, 'phone') and user_db.phone else None,
                email=user_db.email if hasattr(user_db, 'email') and user_db.email else None,
                position=None,  # users表中没有position字段
                role_type=user_db.role_type if hasattr(user_db, 'role_type') and user_db.role_type else "normal",
                approval_level=user_db.role_level if hasattr(user_db, 'role_level') and user_db.role_level is not None else ApprovalLevel.level_1,
                status=user_db.user_status if hasattr(user_db, 'user_status') and user_db.user_status is not None else 1
            )

    # 处理承包商用户（从users表的新字段构建）
    contractor_user = None
    if user_db.user_type == "contractor":
        # 从users表的新字段构建ContractorUser对象
        # contractor_staff_id 可能存储了 contractor_id，但需要确认
        contractor_id = user_db.contractor_staff_id if hasattr(user_db, 'contractor_staff_id') and user_db.contractor_staff_id is not None else 0
        name = user_db.name_str if hasattr(user_db, 'name_str') and user_db.name_str else (user_db.relay_name if hasattr(user_db, 'relay_name') and user_db.relay_name else user_db.username)
        
        # 只有在有足够数据时才创建 ContractorUser 对象
        # 如果 contractor_id 为 0 或 None，说明用户还没有绑定承包商，不创建 contractor_user
        if contractor_id and contractor_id > 0:
            contractor_user = ContractorUser(
                user_id=user_db.user_id,
                contractor_id=contractor_id,
                name=name or user_db.username,  # 确保 name 不为空
                phone=user_db.phone if hasattr(user_db, 'phone') and user_db.phone else "",
                id_number="",  # users表中没有id_number字段，使用空字符串
                work_type=user_db.work_type if hasattr(user_db, 'work_type') and user_db.work_type else "",
                personal_photo="",  # users表中没有personal_photo字段，使用空字符串
                role_type=user_db.role_type if hasattr(user_db, 'role_type') and user_db.role_type else "normal",
                status=user_db.user_status if hasattr(user_db, 'user_status') and user_db.user_status is not None else 1
            )

    return User(
        user_id=user_db.user_id,
        user_type=UserType(user_db.user_type),
        username=user_db.username,
        enterprise_staff_id=user_db.enterprise_staff_id if hasattr(user_db, 'enterprise_staff_id') and user_db.enterprise_staff_id is not None else None,
        contractor_staff_id=user_db.contractor_staff_id if hasattr(user_db, 'contractor_staff_id') and user_db.contractor_staff_id is not None else None,
        phone=user_db.phone if hasattr(user_db, 'phone') else None,
        email=user_db.email if hasattr(user_db, 'email') else None,
        user_level=user_db.user_level if hasattr(user_db, 'user_level') else None,
        audit_status=user_db.audit_status if hasattr(user_db, 'audit_status') else None,
        user_status=user_db.user_status if hasattr(user_db, 'user_status') and user_db.user_status is not None else None,
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
