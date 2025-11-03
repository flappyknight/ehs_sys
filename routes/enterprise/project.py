"""
项目管理路由
Project management routes
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from api.model import (
    ProjectListItem,
    ProjectDetail,
    User
)
from api.model_trans import convert_projects_to_list_response, convert_project_to_detail_response
from db import crud
from routes.dependencies import get_current_user

router = APIRouter()


@router.get("/")
async def get_projects(user: User = Depends(get_current_user)) -> List[ProjectListItem]:
    """获取项目列表，根据用户权限过滤"""
    from main import app
    
    projects = await crud.get_projects_for_user(app.state.engine, user)
    return await convert_projects_to_list_response(app.state.engine, projects)


@router.get("/{project_id}/")
async def get_project_detail(
    project_id: int, 
    user: User = Depends(get_current_user)
) -> ProjectDetail:
    """获取项目详情，包含计划列表"""
    from main import app
    
    project = await crud.get_project_detail(app.state.engine, project_id, user)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在或无权限访问")
    return await convert_project_to_detail_response(app.state.engine, project)

