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
            # 企业用户只能看到自己企业的项目
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


# Area CRUD 函数
async def create_area(engine, area: api.Area):
    """创建厂区"""
    area_db = Area(
        enterprise_id=area.enterprise_id,
        area_name=area.area_name,
        dept_id=area.dept_id
    )
    async with get_session(engine) as session:
        session.add(area_db)
        await session.commit()
        await session.refresh(area_db)
    return area_db

async def get_area_by_id(engine, area_id: int) -> Area|None:
    """根据ID获取厂区"""
    statement = select(Area).where(Area.area_id == area_id)
    async with get_session(engine) as session:
        result = await session.exec(statement)
        area = result.scalars().first()  # 修复：使用 scalars().first()
        return area

async def get_areas_by_enterprise(engine, enterprise_id: int) -> List[Area]:
    """获取企业的所有厂区"""
    statement = select(Area).where(Area.enterprise_id == enterprise_id)
    async with get_session(engine) as session:
        result = await session.exec(statement)
        areas = result.scalars().all()  # 修复：使用 scalars().all()
        return areas

async def get_areas_by_department(engine, dept_id: int) -> List[Area]:
    """获取部门的所有厂区"""
    statement = select(Area).where(Area.dept_id == dept_id)
    async with get_session(engine) as session:
        result = await session.exec(statement)
        areas = result.scalars().all()  # 修复：使用 scalars().all()
        return areas

async def update_area(engine, area_id: int, area_data: api.Area):
    """更新厂区信息"""
    async with get_session(engine) as session:
        statement = select(Area).where(Area.area_id == area_id)
        result = await session.exec(statement)
        area = result.scalars().first()  # 修复：使用 scalars().first()
        
        if not area:
            return None
            
        # 更新字段
        if area_data.area_name is not None:
            area.area_name = area_data.area_name
        if area_data.dept_id is not None:
            area.dept_id = area_data.dept_id
        if area_data.enterprise_id is not None:
            area.enterprise_id = area_data.enterprise_id
            
        area.updated_at = datetime.now()
        
        await session.commit()
        await session.refresh(area)
        return area

async def delete_area(engine, area_id: int) -> bool:
    """删除厂区"""
    async with get_session(engine) as session:
        statement = select(Area).where(Area.area_id == area_id)
        result = await session.exec(statement)
        area = result.scalars().first()  # 修复：使用 scalars().first()
        
        if not area:
            return False
            
        await session.delete(area)
        await session.commit()
        return True

async def get_area_list_with_details(engine, enterprise_id: int = None) -> List[api.AreaListItem]:
    """获取厂区列表，包含企业和部门信息"""
    if enterprise_id:
        statement = (
            select(Area, Company, Department)
            .join(Company, Area.enterprise_id == Company.company_id)
            .outerjoin(Department, Area.dept_id == Department.dept_id)
            .where(Area.enterprise_id == enterprise_id)
        )
    else:
        statement = (
            select(Area, Company, Department)
            .join(Company, Area.enterprise_id == Company.company_id)
            .outerjoin(Department, Area.dept_id == Department.dept_id)
        )
    
    async with get_session(engine) as session:
        result = await session.exec(statement)
        area_list = []
        
        for row in result.all():
            area, company, department = row
            area_item = api.AreaListItem(
                area_id=area.area_id,
                area_name=area.area_name,
                enterprise_name=company.name,
                dept_name=department.name if department else None
            )
            area_list.append(area_item)
            
        return area_list

async def get_enterprises(engine) -> List[Company]:
    """获取所有企业列表"""
    statement = select(Company).where(Company.type == "enterprise")
    async with get_session(engine) as session:
        result = await session.exec(statement)
        enterprises = result.scalars().all()  # 修复：使用 scalars().all()
        return enterprises

async def get_departments_by_enterprise(engine, enterprise_id: int) -> List[Department]:
    """获取指定企业的所有部门"""
    statement = select(Department).where(Department.company_id == enterprise_id)
    async with get_session(engine) as session:
        result = await session.exec(statement)
        departments = result.scalars().all()  # 修复：使用 scalars().all()
        return departments

async def get_all_departments(engine) -> List[Department]:
    """获取所有部门列表"""
    statement = select(Department)
    async with get_session(engine) as session:
        result = await session.exec(statement)
        departments = result.scalars().all()  # 修复：使用 scalars().all()
        return departments

async def get_enterprise_user_detail(engine, user_id: int) -> EnterpriseUser|None:
    """获取企业用户详情"""
    statement = select(EnterpriseUser).where(EnterpriseUser.user_id == user_id)
    async with get_session(engine) as session:
        result = await session.exec(statement)
        return result.scalars().first()  # 修复：使用 scalars().first()

async def update_enterprise_user(engine, user_id: int, user_data: api.EnterpriseUserUpdate):
    """更新企业用户信息"""
    async with get_session(engine) as session:
        statement = select(EnterpriseUser).where(EnterpriseUser.user_id == user_id)
        result = await session.exec(statement)
        user = result.scalars().first()  # 修复：使用 scalars().first()
        
        if not user:
            return None
            
        # 更新字段
        if user_data.name is not None:
            user.name = user_data.name
        if user_data.phone is not None:
            user.phone = user_data.phone
        if user_data.email is not None:
            user.email = user_data.email
        if user_data.position is not None:
            user.position = user_data.position
        if user_data.dept_id is not None:
            user.dept_id = user_data.dept_id
        if user_data.role_type is not None:
            user.role_type = user_data.role_type
        if user_data.approval_level is not None:
            user.approval_level = user_data.approval_level
        if user_data.status is not None:
            user.status = user_data.status
            
        user.updated_at = datetime.now()
        
        await session.commit()
        await session.refresh(user)
        return user

async def get_departments_with_member_count(engine, enterprise_id: int = None) -> List[api.DepartmentWithMemberCount]:
    """获取部门列表及其成员数量"""
    if enterprise_id:
        # 企业用户只能看到自己企业的部门
        dept_statement = select(Department).where(Department.company_id == enterprise_id)
    else:
        # 管理员可以看到所有部门
        dept_statement = select(Department)
    
    async with get_session(engine) as session:
        dept_result = await session.exec(dept_statement)
        departments = dept_result.scalars().all()  # 使用scalars()确保返回Department对象
        
        result = []
        for dept in departments:
            # 统计该部门的成员数量
            member_count_statement = select(func.count()).select_from(EnterpriseUser).where(
                EnterpriseUser.dept_id == dept.dept_id
            )
            member_count_result = await session.exec(member_count_statement)
            member_count = member_count_result.scalar_one()
            
            # 获取企业名称
            company_statement = select(Company).where(Company.company_id == dept.company_id)
            company_result = await session.exec(company_statement)
            company = company_result.scalars().first()
            
            result.append(api.DepartmentWithMemberCount(
                dept_id=dept.dept_id,
                name=dept.name,
                company_id=dept.company_id,
                company_name=company.name if company else "",
                member_count=member_count,
                parent_id=dept.parent_id
            ))
        
        return result

async def get_department_members(engine, dept_id: int) -> List[api.EnterpriseUserListItem]:
    """获取部门成员列表"""
    statement = select(EnterpriseUser, Company).join(
        Company, EnterpriseUser.company_id == Company.company_id
    ).where(EnterpriseUser.dept_id == dept_id)
    
    async with get_session(engine) as session:
        result = await session.exec(statement)
        members = result.all()
        
        return [
            api.EnterpriseUserListItem(
                user_id=member[0].user_id,
                name=member[0].name,
                phone=member[0].phone,
                email=member[0].email,
                position=member[0].position,
                role_type=member[0].role_type,
                company_name=member[1].name,
                dept_id=member[0].dept_id,
                status=member[0].status
            )
            for member in members
        ]

async def get_enterprise_members(engine, enterprise_id: int, dept_id: int = None) -> List[api.EnterpriseUserListItem]:
    """获取企业成员列表，可按部门筛选"""
    statement = select(EnterpriseUser, Company).join(
        Company, EnterpriseUser.company_id == Company.company_id
    ).where(EnterpriseUser.company_id == enterprise_id)
    
    if dept_id:
        statement = statement.where(EnterpriseUser.dept_id == dept_id)
    
    async with get_session(engine) as session:
        result = await session.exec(statement)
        members = result.all()
        
        return [
            api.EnterpriseUserListItem(
                user_id=member[0].user_id,
                name=member[0].name,
                phone=member[0].phone,
                email=member[0].email,
                position=member[0].position,
                role_type=member[0].role_type,
                company_name=member[1].name,
                dept_id=member[0].dept_id,
                status=member[0].status
            )
            for member in members
        ]

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())