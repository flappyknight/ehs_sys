"""
人员管理路由
Staff management routes
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from api.model import (
    EnterpriseUser,
    EnterpriseUserListItem,
    EnterpriseUserUpdate,
    User,
    UserType
)
from db import crud
from routes.dependencies import get_current_user, authenticate_enterprise_level

router = APIRouter()


@router.get("/departments/{dept_id}/members/")
async def get_department_members(
    dept_id: int,
    user: User = Depends(get_current_user)
) -> List[EnterpriseUserListItem]:
    """获取指定部门的成员列表"""
    from main import app
    
    try:
        # 权限检查：企业用户只能查看自己企业的部门成员
        if user.user_type == UserType.enterprise:
            # 检查部门是否属于当前用户的企业
            departments = await crud.get_departments_by_enterprise(
                app.state.engine, user.enterprise_user.enterprise_id
            )
            dept_ids = [dept.dept_id for dept in departments]
            if dept_id not in dept_ids:
                raise HTTPException(status_code=403, detail="无权访问该部门")
        
        members = await crud.get_department_members(app.state.engine, dept_id)
        return members
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取部门成员失败: {str(e)}")


@router.get("/enterprise/{enterprise_id}/members/")
async def get_enterprise_members(
    enterprise_id: int,
    dept_id: int = Query(default=None, description="部门ID，可选筛选条件"),
    user: User = Depends(get_current_user)
) -> List[EnterpriseUserListItem]:
    """获取企业成员列表，可按部门筛选"""
    from main import app
    
    try:
        # 权限检查
        if user.user_type == UserType.enterprise:
            if user.enterprise_user.enterprise_id != enterprise_id:
                raise HTTPException(status_code=403, detail="无权访问其他企业的成员")
        elif user.user_type != UserType.admin:
            raise HTTPException(status_code=403, detail="权限不足")
        
        members = await crud.get_enterprise_members(app.state.engine, enterprise_id, dept_id)
        return members
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取企业成员失败: {str(e)}")


@router.get("/users/{user_id}/")
async def get_enterprise_user_detail(
    user_id: int,
    user: User = Depends(get_current_user)
) -> EnterpriseUser:
    """获取企业用户详情"""
    from main import app
    
    try:
        user_detail = await crud.get_enterprise_user_detail(app.state.engine, user_id)
        if not user_detail:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 权限检查：企业用户只能查看自己企业的用户
        if user.user_type == UserType.enterprise:
            if user_detail.company_id != user.enterprise_user.enterprise_id:
                raise HTTPException(status_code=403, detail="无权访问该用户信息")
        elif user.user_type != UserType.admin:
            raise HTTPException(status_code=403, detail="权限不足")
        
        return EnterpriseUser(
            user_id=user_detail.user_id,
            enterprise_id=user_detail.company_id,
            department_id=user_detail.dept_id,
            name=user_detail.name,
            phone=user_detail.phone,
            email=user_detail.email,
            position=user_detail.position,
            role_type=user_detail.role_type,
            approval_level=user_detail.approval_level,
            status=user_detail.status
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取用户详情失败: {str(e)}")


@router.put("/users/{user_id}/", dependencies=[Depends(authenticate_enterprise_level)])
async def update_enterprise_user(
    user_id: int,
    user_data: EnterpriseUserUpdate,
    user: User = Depends(get_current_user)
):
    """更新企业用户信息"""
    from main import app
    
    try:
        # 权限检查：企业用户只能更新自己企业的用户
        user_detail = await crud.get_enterprise_user_detail(app.state.engine, user_id)
        if not user_detail:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        if user.user_type == UserType.enterprise:
            if user_detail.company_id != user.enterprise_user.enterprise_id:
                raise HTTPException(status_code=403, detail="无权修改该用户信息")
            
            # 企业用户只有管理员角色才能修改其他用户
            if user.enterprise_user.role_type != "manager" and user_detail.user_id != user.user_id:
                raise HTTPException(
                    status_code=403, 
                    detail="权限不足，只有管理员可以修改其他用户信息"
                )
        
        updated_user = await crud.update_enterprise_user(app.state.engine, user_id, user_data)
        if not updated_user:
            raise HTTPException(status_code=404, detail="更新失败")
        
        return {"message": "用户信息更新成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"更新用户信息失败: {str(e)}")

