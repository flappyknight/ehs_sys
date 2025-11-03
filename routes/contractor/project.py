"""
供应商项目管理路由
Contractor project management routes
"""
from fastapi import APIRouter, Depends

from api.model import Project
from db import crud
from routes.dependencies import authenticate_enterprise_level

router = APIRouter()


@router.post("/add/", dependencies=[Depends(authenticate_enterprise_level)])
async def add_project(project: Project):
    """添加项目"""
    from main import app
    project_db = await crud.create_project(app.state.engine, project)
    return project_db

