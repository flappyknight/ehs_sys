from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload  # 添加这个导入

from db.models import *
from db.connection import get_session
from api import model as api


async def get_user(engine, username, user_type: str=None) -> User|None:
    if user_type == api.UserType.contractor:
        statement = select(User).where(User.username == username).options(selectinload(User.contractor_user))
    elif user_type == api.UserType.enterprise:
        statement = select(User).where(User.username == username).options(selectinload(User.enterprise_user))
    else:
        statement = select(User).where(User.username == username)
    async with get_session(engine) as session:
        result = await session.exec(statement)
        try :
            user = result.first()[0]
        except Exception:
            print("no such user!")
            return None
        return user

async def get_user_count(engine) -> int:
    """获取User表中的记录数量"""
    statement = select(func.count()).select_from(User)  # 创建查询语句
    async with get_session(engine) as session:
        result = await session.exec(statement)  # 执行查询
        count = result.scalar_one()  # 获取数量
    return count


async def create_enterprise(engine, enterprise: api.Enterprise):
    enterprise_db = Company(
        name=enterprise.name,
        type=enterprise.type,
    )
    async with get_session(engine) as session:
        session.add(enterprise_db)
        await session.commit()
        await session.refresh(enterprise_db)
    return enterprise_db

async def create_enterprise_user(engine, enterprise_user: api.EnterpriseUser, user: api.User|None=None):
    enterprise_user_db = EnterpriseUser(
        company_id = enterprise_user.enterprise_id,
        dept_id = enterprise_user.department_id,
        name = enterprise_user.name,
        phone = enterprise_user.phone,
        email = enterprise_user.email,
        position = enterprise_user.position,
        role_type = enterprise_user.role_type,
        approval_level = enterprise_user.approval_level,
        status = enterprise_user.status
    )
    async with get_session(engine) as session:
        session.add(enterprise_user_db)
        if user is not None:
            await session.flush()
            await session.refresh(enterprise_user_db)
            await create_user(engine, user.username, user.password_hash, user_type=user.user_type,
                              enterprise_staff_id=enterprise_user_db.user_id, session=session)

        await session.commit()
        await session.refresh(enterprise_user_db)

    return enterprise_user_db

async def create_user(engine, username: str, password_hash: str, user_type: str,
                             enterprise_staff_id: int = None, contractor_staff_id: int = None, session=None) -> User:
    user = User(
        username=username,
        password_hash=password_hash,
        user_type=user_type,
        enterprise_staff_id=enterprise_staff_id,
        contractor_staff_id=contractor_staff_id,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    if session is not None:
        session.add(user)
        await session.flush()
        await session.refresh(user)
        return user
    async with get_session(engine) as session:
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


async def create_department(engine, department: api.Department):
    department_db = Department(
        company_id=department.enterprise_id,
        name=department.name,
        parent_id=department.parent_id
    )
    async with get_session(engine) as session:
        session.add(department_db)
        await session.commit()
        await session.refresh(department_db)
    return department_db


async def create_contractor(engine, contractor: api.Contractor):
    contractor_db = Contractor(
        license_file=contractor.license_file,
        company_name=contractor.company_name,
        company_type=contractor.company_type,
        legal_person=contractor.legal_person,
        established_date=datetime.strptime(contractor.establish_date, "%Y-%m-%d").date() if contractor.establish_date else None,
        registered_capital=contractor.registered_capital,
        applicant_name=contractor.applicant_name
    )
    async with get_session(engine) as session:
        session.add(contractor_db)
        await session.flush()
        await session.refresh(contractor_db)

    return contractor_db


async def create_contractor_user(engine, contractor_user: api.ContractorUser, user: User|None=None):
    """创建承包商用户"""
    contractor_user_db = ContractorUser(
        contractor_id=contractor_user.contractor_id,
        name=contractor_user.name,
        phone=contractor_user.phone,
        id_number=contractor_user.id_number,
        work_type=contractor_user.work_type,
        personal_photo=contractor_user.personal_photo,
        role_type=contractor_user.role_type,
        status=contractor_user.status
    )
    async with get_session(engine) as session:
        session.add(contractor_user_db)
        if user is not None:
            await session.flush()
            await session.refresh(contractor_user_db)
            await create_user(engine, user.username, user.password_hash, user_type=user.user_type,
                              enterprise_staff_id=contractor_user_db.user_id, session=session)
        await session.commit()
        await session.refresh(contractor_user_db)
    return contractor_user_db

async def create_project(engine, project: api.Project):
    project_db = ContractorProject(
        contractor_id=project.contractor_id,  # 注意数据库字段名是constractor_id
        enterprise_id=project.enterprise_id,
        project_name=project.project_name,
        leader_name=project.project_leader,
        leader_phone=project.leader_phone
    )
    
    async with get_session(engine) as session:
        session.add(project_db)
        await session.commit()
        await session.refresh(project_db)
    return project_db

async def create_plan(engine, plan: api.Plan):
    plan_db = EntryPlan(
        project_id=plan.project_id,
        plan_date=plan.plan_date
    )

    async with get_session(engine) as session:
        session.add(plan_db)
        await session.flush()
        await session.refresh(plan_db)
        plan_workers = [EntryPlanUser(project_id=plan_db.project_id, plan_id=plan_db.plan_id,
                                      plan_date=plan_db.plan_id, user_id=cu_id)
                        for cu_id in plan.workers]
        session.add_all(plan_workers)
        await session.commit()
    return plan_db


# 使用示例
async def main():
    from sqlalchemy.ext.asyncio import create_async_engine
    from config import settings
    try:
        user_count = await get_user_count(create_async_engine(settings.database_url))
        print(f"User表中的记录数量: {user_count}")
    except Exception as e:
        print(f"查询失败: {e}")


async def get_projects_for_user(engine, user: api.User) -> List[ContractorProject]:
    """根据用户类型和权限获取项目列表"""
    async with get_session(engine) as session:
        if user.user_type == "admin":
            # 管理员可以看到所有项目
            statement = select(ContractorProject).options(selectinload(ContractorProject.plans))
        elif user.user_type == "enterprise" and user.enterprise_user:
            # 企业用户只能看到自己公司的项目
            statement = select(ContractorProject).where(
                ContractorProject.enterprise_id == user.enterprise_user.enterprise_id
            ).options(selectinload(ContractorProject.plans))
        elif user.user_type == "contractor" and user.contractor_user:
            # 承包商用户只能看到自己承包商的项目
            statement = select(ContractorProject).where(
                ContractorProject.contractor_id == user.contractor_user.contractor_id
            ).options(selectinload(ContractorProject.plans))
        else:
            return []
        
        result = await session.exec(statement)
        projects = result.scalars().all()  # 使用 scalars() 确保返回模型对象
        return projects

async def get_project_detail(engine, project_id: int, user: api.User) -> ContractorProject|None:
    """获取项目详情，包含计划列表"""
    async with get_session(engine) as session:
        # 首先检查用户是否有权限访问该项目
        if user.user_type == "admin":
            statement = select(ContractorProject).where(ContractorProject.project_id == project_id)
        elif user.user_type == "enterprise" and user.enterprise_user:
            statement = select(ContractorProject).where(
                ContractorProject.project_id == project_id,
                ContractorProject.enterprise_id == user.enterprise_user.enterprise_id
            )
        elif user.user_type == "contractor" and user.contractor_user:
            statement = select(ContractorProject).where(
                ContractorProject.project_id == project_id,
                ContractorProject.contractor_id == user.contractor_user.contractor_id
            )
        else:
            return None
        
        statement = statement.options(selectinload(ContractorProject.plans))
        result = await session.exec(statement)
        project = result.scalars().first()  # 使用 scalars().first() 而不是 first()
        return project

async def get_plan_participants(engine, plan_id: int) -> List[ContractorUser]:
    """获取计划的参与人员列表"""
    async with get_session(engine) as session:
        statement = select(ContractorUser).join(
            EntryPlanUser, ContractorUser.user_id == EntryPlanUser.user_id
        ).where(EntryPlanUser.plan_id == plan_id)
        
        result = await session.exec(statement)
        participants = result.scalars().all()  # 使用 scalars().all() 而不是 all()
        return participants

async def get_contractor_by_id(engine, contractor_id: int) -> Contractor|None:
    """根据承包商ID获取承包商信息"""
    async with get_session(engine) as session:
        statement = select(Contractor).where(Contractor.contractor_id == contractor_id)
        result = await session.exec(statement)
        contractor = result.scalars().first()  # 使用 scalars() 确保返回模型对象
        return contractor

async def check_user_registration(engine, user_id: int, plan_id: int) -> bool:
    """检查用户是否已经登记"""
    async with get_session(engine) as session:
        # 查找该用户在该计划中的EntryPlanUser记录
        plan_user_statement = select(EntryPlanUser).where(
            EntryPlanUser.user_id == user_id,
            EntryPlanUser.plan_id == plan_id
        )
        plan_user_result = await session.exec(plan_user_statement)
        plan_user = plan_user_result.scalars().first()  # 使用 scalars().first()
        
        if not plan_user:
            return False
        
        # 检查是否有对应的登记记录
        register_statement = select(EntryRegister).where(
            EntryRegister.plan_user_id == plan_user.id
        )
        register_result = await session.exec(register_statement)
        register = register_result.scalars().first()  # 使用 scalars().first()
        
        return register is not None


async def get_contractors_for_enterprise(engine, enterprise_id: int) -> List[Contractor]:
    """获取与指定企业有合作的承包商列表（保证数据隔离）"""
    statement = select(Contractor).join(
        ContractorProject, Contractor.contractor_id == ContractorProject.contractor_id
    ).where(
        ContractorProject.enterprise_id == enterprise_id
    ).distinct()
    
    async with get_session(engine) as session:
        result = await session.exec(statement)
        contractors = result.scalars().all()
        return list(contractors)

async def get_contractor_project_count(engine, contractor_id: int, enterprise_id: int) -> int:
    """获取承包商与指定企业的合作项目数量"""
    statement = select(func.count()).select_from(ContractorProject).where(
        ContractorProject.contractor_id == contractor_id,
        ContractorProject.enterprise_id == enterprise_id
    )
    
    async with get_session(engine) as session:
        result = await session.exec(statement)
        count = result.scalar_one()
        return count

async def create_contractor_with_project(engine, request: api.ContractorProjectRequest, enterprise_id: int) -> tuple[Contractor, ContractorProject]:
    """创建承包商和项目（支持新承包商和已有承包商两种情况）"""
    async with get_session(engine) as session:
        contractor = None
        
        if request.contractor_id:
            # 情况2：与已有承包商创建新项目
            contractor_statement = select(Contractor).where(Contractor.contractor_id == request.contractor_id)
            contractor_result = await session.exec(contractor_statement)
            contractor = contractor_result.scalars().first()
            
            if contractor is None:
                raise ValueError(f"承包商ID {request.contractor_id} 不存在")
                
            # 验证该承包商是否与当前企业有过合作（数据隔离检查）
            existing_project_statement = select(ContractorProject).where(
                ContractorProject.contractor_id == request.contractor_id,
                ContractorProject.enterprise_id == enterprise_id
            )
            existing_project_result = await session.exec(existing_project_statement)
            existing_project = existing_project_result.scalars().first()
            
            if not existing_project:
                raise ValueError("该承包商与当前企业无合作历史，无法创建新项目")
        else:
            # 情况1：创建新承包商和项目
            if not all([request.company_name, request.license_file, request.company_type, 
                       request.legal_person, request.establish_date, request.registered_capital, 
                       request.applicant_name]):
                raise ValueError("创建新承包商时，所有承包商信息字段都是必填的")
            
            contractor = Contractor(
                company_name=request.company_name,
                license_file=request.license_file,
                company_type=request.company_type,
                legal_person=request.legal_person,
                establish_date=request.establish_date,
                registered_capital=request.registered_capital,
                applicant_name=request.applicant_name
            )
            session.add(contractor)
            await session.flush()  # 获取contractor_id
            await session.refresh(contractor)
        
        # 创建项目
        project = ContractorProject(
            contractor_id=contractor.contractor_id,
            enterprise_id=enterprise_id,
            project_name=request.project_name,
            leader_name=request.leader_name,
            leader_phone=request.leader_phone
        )
        session.add(project)
        await session.commit()
        await session.refresh(contractor)
        await session.refresh(project)
        
        return contractor, project


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())