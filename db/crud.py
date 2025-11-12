from datetime import datetime
from typing import List
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


async def create_enterprise_user(engine, enterprise_user: api.EnterpriseUser, user: api.User|None=None):
    enterprise_user_db = EnterpriseUser(
        enterprise_id = enterprise_user.enterprise_id,
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

# 使用示例
async def main():
    from sqlalchemy.ext.asyncio import create_async_engine
    from config import settings
    try:
        user_count = await get_user_count(create_async_engine(settings.database_url))
        print(f"User表中的记录数量: {user_count}")
    except Exception as e:
        print(f"查询失败: {e}")



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

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())