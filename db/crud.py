from datetime import datetime
from typing import List
from sqlalchemy import select, func
# selectinload 已不再使用，因为enterprise_user和contractor_user表已删除

from db.models import *
from db.connection import get_session
from api import model as api


async def get_user(engine, username, user_type: str=None) -> User|None:
    # 不再加载已删除的enterprise_user和contractor_user关系
    statement = select(User).where(User.username == username)
    async with get_session(engine) as session:
        try:
            result = await session.exec(statement)
            # 对于 SQLModel，使用 first() 获取第一个结果
            row = result.first()
            if row is None:
                return None
            
            # 处理 Row 对象：如果返回的是 Row，提取第一个元素（User对象）
            if hasattr(row, '__getitem__') and not isinstance(row, User):
                # 这是一个 Row 对象，提取 User 对象
                user = row[0] if len(row) > 0 else None
            else:
                # 直接是 User 对象
                user = row
            
            if user is None:
                return None
            
            # 确保返回的是 User 对象
            if isinstance(user, User):
                return user
            else:
                print(f"⚠️ 警告: get_user 返回的不是 User 对象，类型: {type(user)}")
                return None
        except Exception as e:
            print(f"no such user! Error: {e}")
            import traceback
            traceback.print_exc()
            return None

async def get_user_count(engine) -> int:
    """获取User表中的记录数量"""
    statement = select(func.count()).select_from(User)  # 创建查询语句
    async with get_session(engine) as session:
        result = await session.exec(statement)  # 执行查询
        count = result.scalar_one()  # 获取数量
    return count


async def create_enterprise_user(engine, enterprise_user: api.EnterpriseUser, user: api.User|None=None):
    """
    创建企业用户（不再使用enterprise_user表，直接写入users表）
    """
    async with get_session(engine) as session:
        if user is not None:
            # 如果提供了user信息，创建users表记录，包含企业用户信息
            user_db = User(
                username=user.username,
                password_hash=user.password_hash,
                user_type=user.user_type,
                phone=enterprise_user.phone,
                email=enterprise_user.email,
                name_str=enterprise_user.name,
                role_type=enterprise_user.role_type,
                role_level=enterprise_user.approval_level,  # approval_level映射到role_level
                user_status=enterprise_user.status,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(user_db)
            await session.flush()
            await session.refresh(user_db)
            await session.commit()
            return user_db
        else:
            # 如果没有提供user信息，只返回企业用户信息（不创建账号）
            # 这种情况下，返回一个包含企业用户信息的字典或对象
            # 注意：由于不再使用EnterpriseUser表，这里需要返回一个兼容的对象
            from api.model import EnterpriseUser as EnterpriseUserModel
            return EnterpriseUserModel(
                enterprise_id=enterprise_user.enterprise_id,
                name=enterprise_user.name,
                phone=enterprise_user.phone,
                email=enterprise_user.email,
                position=enterprise_user.position,
                role_type=enterprise_user.role_type,
                approval_level=enterprise_user.approval_level,
                status=enterprise_user.status
            )

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