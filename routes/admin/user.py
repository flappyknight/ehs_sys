"""
系统用户管理路由
System user management routes
"""
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from api.model import User, UserType
from core import password as pwd
from routes.dependencies import get_current_user

router = APIRouter()


def verify_admin(user: User = Depends(get_current_user)):
    """验证系统管理员权限"""
    if user.user_type != UserType.admin:
        raise HTTPException(status_code=403, detail="需要系统管理员权限")
    return user


@router.post("/", dependencies=[Depends(verify_admin)])
async def create_admin_user(
    username: str = Query(description="用户名"),
    password: str = Query(description="密码"),
    email: Optional[str] = Query(default=None, description="邮箱")
):
    """
    创建系统管理员账户
    
    只有系统管理员可以创建新的管理员账户
    """
    from main import app
    from db import crud
    
    try:
        # 检查用户名是否已存在
        existing_user = await crud.get_user(app.state.engine, username)
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已存在")
        
        # 创建管理员账户
        from db.models import User as UserDB
        from sqlmodel import select
        
        async with app.state.engine.begin() as conn:
            new_user = UserDB(
                user_type=UserType.admin,
                username=username,
                password_hash=pwd.get_password_hash(password),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # 如果有 email 字段，设置它
            if hasattr(new_user, 'email') and email:
                new_user.email = email
            
            conn.add(new_user)
            await conn.commit()
            await conn.refresh(new_user)
            
            return {
                "message": "管理员账户创建成功",
                "user_id": new_user.user_id,
                "username": username
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"创建管理员账户失败: {str(e)}")


@router.get("/")
async def get_admin_users(
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
    user: User = Depends(verify_admin)
) -> dict:
    """
    获取系统管理员列表
    
    查看所有系统管理员账户
    """
    from main import app
    from db.models import User as UserDB
    from sqlmodel import select
    
    try:
        async with app.state.engine.begin() as conn:
            # 查询管理员用户
            query = select(UserDB).where(UserDB.user_type == UserType.admin)
            
            # 计算总数
            count_result = await conn.execute(query)
            total = len(count_result.all())
            
            # 分页查询
            query = query.offset((page - 1) * page_size).limit(page_size)
            result = await conn.execute(query)
            users = result.scalars().all()
            
            items = [
                {
                    "user_id": u.user_id,
                    "username": u.username,
                    "email": getattr(u, 'email', None),
                    "created_at": u.created_at.isoformat() if hasattr(u, 'created_at') else None,
                    "updated_at": u.updated_at.isoformat() if hasattr(u, 'updated_at') else None
                } for u in users
            ]
            
            return {
                "total": total,
                "page": page,
                "page_size": page_size,
                "items": items
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取管理员列表失败: {str(e)}")


@router.delete("/{user_id}/", dependencies=[Depends(verify_admin)])
async def delete_admin_user(user_id: int, current_user: User = Depends(verify_admin)):
    """
    删除系统管理员账户
    
    注意：不能删除自己的账户
    """
    from main import app
    from db.models import User as UserDB
    from sqlmodel import select
    
    try:
        # 不能删除自己
        if current_user.user_id == user_id:
            raise HTTPException(status_code=400, detail="不能删除自己的账户")
        
        async with app.state.engine.begin() as conn:
            # 查询用户
            query = select(UserDB).where(UserDB.user_id == user_id)
            result = await conn.execute(query)
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(status_code=404, detail="用户不存在")
            
            if user.user_type != UserType.admin:
                raise HTTPException(status_code=400, detail="该用户不是系统管理员")
            
            # 删除用户
            await conn.delete(user)
            await conn.commit()
            
            return {"message": "管理员账户删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"删除管理员账户失败: {str(e)}")


@router.post("/{user_id}/reset-password/", dependencies=[Depends(verify_admin)])
async def reset_admin_password(
    user_id: int,
    new_password: str = Query(description="新密码")
):
    """
    重置管理员密码
    
    系统管理员可以重置其他管理员的密码
    """
    from main import app
    from db.models import User as UserDB
    from sqlmodel import select
    
    try:
        async with app.state.engine.begin() as conn:
            # 查询用户
            query = select(UserDB).where(UserDB.user_id == user_id)
            result = await conn.execute(query)
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(status_code=404, detail="用户不存在")
            
            if user.user_type != UserType.admin:
                raise HTTPException(status_code=400, detail="该用户不是系统管理员")
            
            # 更新密码
            user.password_hash = pwd.get_password_hash(new_password)
            if hasattr(user, 'updated_at'):
                user.updated_at = datetime.now()
            
            await conn.commit()
            
            return {"message": "密码重置成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"重置密码失败: {str(e)}")

