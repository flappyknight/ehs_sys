from sqlalchemy import select, func

from db.models import *
from db.connection import get_session
from api import model as api


async def get_user(engine, username) -> User:
    statement = select(User).where(User.username == username)
    async with get_session(engine) as session:
        result = await session.exec(statement)
        user = result.first()[0]
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

async def create_enterprise_user(engine, enterprise_user: api.EnterpriseUser):
    enterprise_user_db = EnterpriseUser(
        company_id = enterprise_user.enterprise_id,
        dept_id = enterprise_user.department_id,
        name = enterprise_user.name,
        phone = enterprise_user.phone,
        email = enterprise_user.email,
        position = enterprise_user.position,
        role_type = enterprise_user.rotype,
        approval_level = enterprise_user.approval_level,
        status = enterprise_user.status
    )
    async with get_session(engine) as session:
        session.add(enterprise_user_db)
        await session.commit()
        await session.refresh(enterprise_user_db)
    return enterprise_user_db


async def create_user(engine, username: str, password_hash: str, user_type: str,
                             enterprise_staff_id: int = None, contractor_staff_id: int = None) -> User:
    """简化版的用户创建函数"""
    user = User(
        username=username,
        password_hash=password_hash,
        user_type=user_type,
        enterprise_staff_id=enterprise_staff_id,
        contractor_staff_id=contractor_staff_id,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    async with get_session(engine) as session:
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


async def create_department(engine, department: api.Department):
    """创建部门"""
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
    """创建承包商"""
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
        await session.commit()
        await session.refresh(contractor_db)
    return contractor_db


async def create_contractor_user(engine, contractor_user: api.ContractorUser):
    """创建承包商用户"""
    contractor_user_db = ContractorUser(
        contractor_id=contractor_user.contractor_id,
        name=contractor_user.name,
        phone=contractor_user.phone,
        id_number=contractor_user.id_number,
        work_type=contractor_user.work_type,
        personal_photo=contractor_user.personal_photo,
        status=contractor_user.status
    )
    async with get_session(engine) as session:
        session.add(contractor_user_db)
        await session.commit()
        await session.refresh(contractor_user_db)
    return contractor_user_db

# 使用示例
async def main():
    from sqlalchemy.ext.asyncio import create_async_engine
    from config import settings
    try:
        user_count = await get_user_count(create_async_engine(settings.database_url))
        print(f"User表中的记录数量: {user_count}")
    except Exception as e:
        print(f"查询失败: {e}")




if __name__ == "__main__":
    import asyncio
    asyncio.run(main())