"""
企业信息管理路由
Enterprise information management routes
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from api.model import Enterprise, EnterpriseListItem, User, UserType, EnterpriseUser
from core import password as pwd
from db import crud
from routes.dependencies import get_current_user, authenticate_enterprise_level

router = APIRouter()


@router.post("/add/", dependencies=[Depends(authenticate_enterprise_level)])
async def add_enterprise(enterprise: Enterprise):
    """添加企业"""
    from main import app
    enterprise_db = await crud.create_enterprise(app.state.engine, enterprise)
    return enterprise_db


@router.post("/add_user/", dependencies=[Depends(authenticate_enterprise_level)])
async def add_enterprise_user(enterprise_user: EnterpriseUser, create_account: bool = True):
    """添加企业用户"""
    from main import app
    from fastapi import Query
    
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
            detail="Failed to create this enterprise user: " + str(e)
        )
    return enterprise_user_db


@router.get("/list/")
async def get_enterprises(user: User = Depends(get_current_user)) -> List[EnterpriseListItem]:
    """获取企业列表"""
    from main import app
    
    try:
        # 只有管理员可以查看所有企业
        if user.user_type != UserType.admin:
            raise HTTPException(status_code=403, detail="只有管理员可以查看企业列表")
        
        enterprises = await crud.get_enterprises(app.state.engine)
        return [
            EnterpriseListItem(
                company_id=enterprise.company_id,
                name=enterprise.name,
                type=enterprise.type
            ) for enterprise in enterprises
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取企业列表失败: {str(e)}")

