"""
部门管理路由
Department management routes
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from api.model import (
    Department, 
    DepartmentListItem, 
    User, 
    UserType,
    DepartmentWithMemberCount
)
from db import crud
from routes.dependencies import get_current_user, authenticate_enterprise_level

router = APIRouter()


@router.post("/", dependencies=[Depends(authenticate_enterprise_level)])
async def add_department(department: Department):
    """添加部门"""
    from main import app
    department_db = await crud.create_department(app.state.engine, department)
    return department_db


@router.get("/")
async def get_departments(
    enterprise_id: int = Query(default=None, description="企业ID，不传则获取当前用户企业的部门"),
    user: User = Depends(get_current_user)
) -> List[DepartmentListItem]:
    """获取部门列表"""
    from main import app
    
    try:
        # 如果没有指定企业ID，使用当前用户的企业ID
        if enterprise_id is None:
            if user.user_type == UserType.enterprise and user.enterprise_user:
                enterprise_id = user.enterprise_user.enterprise_id
            elif user.user_type == UserType.admin:
                # 管理员如果不指定企业ID，返回所有部门
                departments = await crud.get_all_departments(app.state.engine)
                return [
                    DepartmentListItem(
                        dept_id=dept.dept_id,
                        company_id=dept.company_id,
                        name=dept.name,
                        parent_id=dept.parent_id
                    ) for dept in departments
                ]
            else:
                raise HTTPException(status_code=400, detail="无法确定企业ID")
        
        # 权限检查：企业用户只能查看自己企业的部门
        if user.user_type == UserType.enterprise and user.enterprise_user:
            if enterprise_id != user.enterprise_user.enterprise_id:
                raise HTTPException(status_code=403, detail="无权限访问该企业的部门")
        
        departments = await crud.get_departments_by_enterprise(app.state.engine, enterprise_id)
        return [
            DepartmentListItem(
                dept_id=dept.dept_id,
                company_id=dept.company_id,
                name=dept.name,
                parent_id=dept.parent_id
            ) for dept in departments
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取部门列表失败: {str(e)}")


@router.get("/with-members/")
async def get_departments_with_members(
    user: User = Depends(get_current_user)
) -> List[DepartmentWithMemberCount]:
    """获取部门列表及成员数量"""
    from main import app
    
    try:
        if user.user_type == UserType.admin:
            # 管理员可以看到所有部门
            departments = await crud.get_departments_with_member_count(app.state.engine)
        elif user.user_type == UserType.enterprise:
            # 企业用户只能看到自己企业的部门
            enterprise_id = user.enterprise_user.enterprise_id
            departments = await crud.get_departments_with_member_count(
                app.state.engine, enterprise_id
            )
        else:
            raise HTTPException(status_code=403, detail="权限不足")
        
        return departments
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取部门列表失败: {str(e)}")

