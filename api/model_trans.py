from db import models as db_models
from api.model import User, UserType, EnterpriseUser, ContractorUser, ProjectListItem, ProjectDetail, PlanDetail, PlanParticipant, ContractorListItem
from db import crud
from typing import List


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

# 在文件末尾添加新的转换函数

async def convert_projects_to_list_response(engine, projects: List[db_models.ContractorProject]) -> List[ProjectListItem]:
    """将数据库项目列表转换为API响应格式"""
    result = []
    for project in projects:
        # 获取承包商信息
        contractor = await crud.get_contractor_by_id(engine, project.contractor_id)
        contractor_name = contractor.company_name if contractor else "未知承包商"
        
        # 计算已计划进场数/次
        planned_entry_count = len(project.plans) if project.plans else 0
        
        project_item = ProjectListItem(
            project_id=project.project_id,
            project_name=project.project_name,
            contractor_name=contractor_name,
            project_leader=project.leader_name,
            leader_phone=project.leader_phone,
            planned_entry_count=planned_entry_count
        )
        result.append(project_item)
    
    return result

async def convert_project_to_detail_response(engine, project: db_models.ContractorProject) -> ProjectDetail:
    """将数据库项目转换为详情API响应格式"""
    # 获取承包商信息
    contractor = await crud.get_contractor_by_id(engine, project.contractor_id)
    contractor_name = contractor.company_name if contractor else "未知承包商"
    
    # 转换计划列表
    plans = []
    for plan in project.plans:
        participants = await crud.get_plan_participants(engine, plan.plan_id)
        participant_list = []
        
        for participant in participants:
            is_registered = await crud.check_user_registration(engine, participant.user_id, plan.plan_id)
            participant_item = PlanParticipant(
                user_id=participant.user_id,
                name=participant.name,
                phone=participant.phone,
                id_number=participant.id_number,
                is_registered=is_registered
            )
            participant_list.append(participant_item)
        
        plan_detail = PlanDetail(
            plan_id=plan.plan_id,
            project_name=project.project_name,
            plan_date=plan.plan_date,
            participant_count=len(participant_list),
            is_completed=False,  # 这里可以根据业务逻辑判断是否完成
            participants=participant_list
        )
        plans.append(plan_detail)
    
    project_detail = ProjectDetail(
        project_id=project.project_id,
        project_name=project.project_name,
        contractor_name=contractor_name,
        project_leader=project.leader_name,
        leader_phone=project.leader_phone,
        plans=plans
    )
    
    return project_detail

async def convert_contractors_to_list_response(engine, contractors: List[db_models.Contractor], enterprise_id: int) -> List[ContractorListItem]:
    """将承包商数据库对象转换为API响应格式"""
    result = []
    for contractor in contractors:
        project_count = await crud.get_contractor_project_count(engine, contractor.contractor_id, enterprise_id)
        contractor_item = ContractorListItem(
            contractor_id=contractor.contractor_id,
            company_name=contractor.company_name,
            company_type=contractor.company_type,
            legal_person=contractor.legal_person,
            establish_date=str(contractor.establish_date),
            project_count=project_count
        )
        result.append(contractor_item)
    return result