"""
企业员工管理路由
Enterprise staff management routes
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from api.model import (
    EnterpriseUser,
    EnterpriseUserListItem,
    User,
    UserType
)
from core import password as pwd
from db import crud
from routes.dependencies import get_current_user, authenticate_enterprise_level

router = APIRouter()


@router.post("/", dependencies=[Depends(authenticate_enterprise_level)])
async def add_enterprise_user(enterprise_user: EnterpriseUser, create_account: bool = Query(default=True)):
    """添加企业用户"""
    from main import app
    
    try:
        if create_account:
            user = User(
                user_type=UserType.enterprise,
                username=enterprise_user.phone,
                password_hash=pwd.get_password_hash(enterprise_user.phone[-6:])
            )
            enterprise_user_db = await crud.create_enterprise_user(
                app.state.engine, enterprise_user, user
            )
        else:
            enterprise_user_db = await crud.create_enterprise_user(
                app.state.engine, enterprise_user
            )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to create this enterprise user: {str(e)}"
        )
    return enterprise_user_db


@router.get("/")
async def get_enterprise_users(
    department_id: int = Query(default=None, description="部门ID筛选"),
    user: User = Depends(get_current_user)
) -> List[EnterpriseUserListItem]:
    """获取企业用户列表"""
    from main import app
    
    try:
        if user.user_type == UserType.admin:
            # 管理员可以看到所有用户
            members = await crud.get_all_enterprise_members(app.state.engine, department_id)
        elif user.user_type == UserType.enterprise:
            # 企业用户只能看到自己企业的用户
            enterprise_id = user.enterprise_user.enterprise_id
            members = await crud.get_enterprise_members(app.state.engine, enterprise_id, department_id)
        else:
            raise HTTPException(status_code=403, detail="权限不足")
        
        return members
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取用户列表失败: {str(e)}")

