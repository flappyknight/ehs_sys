"""
供应商信息管理路由
Contractor information management routes
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from api.model import (
    Contractor,
    ContractorUser,
    ContractorListItem,
    ContractorProjectRequest,
    ContractorProjectResponse,
    User,
    UserType
)
from core import password as pwd
from db import crud
from routes.dependencies import (
    get_current_user,
    authenticate_enterprise_level,
    authenticate_contractor_level
)

router = APIRouter()


@router.post("/add/", dependencies=[Depends(authenticate_enterprise_level)])
async def add_contractor(contractor: Contractor):
    """添加供应商"""
    from main import app
    contractor_db = await crud.create_contractor(app.state.engine, contractor)
    return contractor_db


@router.post("/add_user/", dependencies=[Depends(authenticate_contractor_level)])
async def add_contractor_user(contractor_user: ContractorUser, create_account: bool = Query(default=True)):
    """添加供应商用户"""
    from main import app
    
    try:
        if create_account:
            user = User(
                user_type=UserType.contractor,
                username=contractor_user.phone,
                password_hash=pwd.get_password_hash(contractor_user.phone[-6:])
            )
            contractor_user_db = await crud.create_contractor_user(
                app.state.engine, contractor_user, user
            )
        else:
            contractor_user_db = await crud.create_contractor_user(
                app.state.engine, contractor_user
            )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail="Failed to create this contractor user: " + str(e)
        )
    return contractor_user_db


@router.get("/list/")
async def get_contractors(user: User = Depends(get_current_user)) -> List[ContractorListItem]:
    """获取与当前企业有合作的承包商列表（保证数据隔离）"""
    from main import app
    
    if user.user_type != UserType.enterprise:
        raise HTTPException(status_code=403, detail="只有企业用户可以查看承包商列表")
    
    enterprise_id = user.enterprise_user.enterprise_id
    contractors = await crud.get_contractors_for_enterprise(app.state.engine, enterprise_id)
    
    result = []
    for contractor in contractors:
        project_count = await crud.get_contractor_project_count(
            app.state.engine, contractor.contractor_id, enterprise_id
        )
        contractor_item = ContractorListItem(
            contractor_id=contractor.contractor_id,
            company_name=contractor.company_name,
            company_type=contractor.company_type,
            legal_person=contractor.legal_person,
            establish_date=str(contractor.establish_date),
            project_count=project_count
        )
        result.append(contractor_item)
    
    return result


@router.post("/create-project/")
async def create_contractor_project(
    request: ContractorProjectRequest, 
    user: User = Depends(authenticate_enterprise_level)
) -> ContractorProjectResponse:
    """与承包商创建合作项目（支持新承包商和已有承包商）"""
    from main import app
    
    enterprise_id = user.enterprise_user.enterprise_id
    
    try:
        contractor, project = await crud.create_contractor_with_project(
            app.state.engine, request, enterprise_id
        )
        
        if request.contractor_id:
            message = f"成功与承包商 {contractor.company_name} 创建新项目 {project.project_name}"
        else:
            message = f"成功创建新承包商 {contractor.company_name} 并建立合作项目 {project.project_name}"
        
        return ContractorProjectResponse(
            contractor_id=contractor.contractor_id,
            project_id=project.project_id,
            message=message
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")

