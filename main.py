# main.py
"""
FastAPI 应用主文件

注意：大部分路由已迁移到 routes/ 模块中，本文件保留的是一些遗留路由和辅助函数。
新的路由结构请参考 routes/ROUTES_STRUCTURE.md

路由模块结构：
- routes/admin/ - 系统账户后台管理
- routes/enterprise_backend/ - 企业管理后台
- routes/contractor_backend/ - 承包商管理后台
- routes/ticket/ - 工单管理
- routes/workflow/ - 工单流程管理
- routes/auth.py - 认证相关
"""
from datetime import timedelta, datetime, timezone
from typing import AsyncIterator, Union, Annotated

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
import jwt
from jwt.exceptions import InvalidTokenError

from db.connection import create_engine
from db import crud
from core.init_admin import init_admin_user
from core import password as pwd
from config import settings
from api.model import *
from api.model_trans import convert_user_db_to_response

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # Startup
    # 创建数据库连接engine
    engine = create_engine()
    app.state.engine = engine
    await init_admin_user(app)
    yield

    # Shutdown
    await engine.dispose()
    print("数据库连接已关闭")

app = FastAPI(lifespan=lifespan)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://192.168.1.185:3000",
        "http://www.youngj.icu:8100",
        "http://www.youngj.icu"
    ],  # 明确指定允许的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
from routes import main_router
app.include_router(main_router)

# 导入共享依赖项（认证相关函数已迁移到 routes/dependencies.py）
from routes.dependencies import (
    get_current_user,
    authenticate_enterprise_level,
    authenticate_contractor_level,
    get_user_enterprise_id
)


@app.post("/contractor/add/", dependencies=[Depends(authenticate_enterprise_level)])
async def add_contractor(contractor: Contractor):
    contractor_db = await crud.create_contractor(app.state.engine, contractor)
    return contractor_db


@app.post("/contractor/add_project", dependencies=[Depends(authenticate_enterprise_level)])
async def add_project(project: Project):
    project_db = await crud.create_project(app.state.engine, project)
    return project_db


@app.get("/contractors/")
async def get_contractors(user: User = Depends(get_current_user)) -> List[ContractorListItem]:
    """获取与当前企业有合作的承包商列表（保证数据隔离）"""
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

@app.post("/contractors/create-project/")
async def create_contractor_project(
    request: ContractorProjectRequest, 
    user: User = Depends(authenticate_enterprise_level)
) -> ContractorProjectResponse:
    """与承包商创建合作项目（支持新承包商和已有承包商）"""
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
