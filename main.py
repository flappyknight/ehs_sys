# main.py
from datetime import timedelta, datetime, timezone
from typing import AsyncIterator, Union, Annotated

from fastapi import FastAPI, Depends, HTTPException, status, Cookie, Response, Query
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
from api.model_trans import convert_user_db_to_response, convert_projects_to_list_response, convert_project_to_detail_response, convert_contractors_to_list_response

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
    allow_origins=["*"],  # 开发环境允许所有来源，生产环境应指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def authenticate_user(username: str, password: str):
    user = await crud.get_user(app.state.engine, username)
    if not user:
        return False
    if not pwd.verify_password(password, user.password_hash):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


@app.post("/token")
async def login_for_access_token(response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        access_token_expires = settings.access_token_expire_minutes
        access_token = create_access_token(
            data={"sub": user.username, "user_type": user.user_type}, expires_delta=access_token_expires
        )
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=False,
            max_age=int(access_token_expires.total_seconds()),  # 转换为秒数
            samesite="none",  # 允许跨站请求
            secure=True,  # 开发环境设为 False，生产环境应设为 True
            path="/",
        )
    return Token(access_token=access_token, token_type="bearer")

@app.post("/logout")
async def logout(response: Response):
    # 删除 access_token Cookie
    response.delete_cookie(
        key="access_token",
        path="/",
    )
    return {"message": "Logged out"}


def get_token_from_cookie(access_token: str | None = Cookie(default=None)):
    if access_token is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return access_token

@app.get("/users/me/")
async def read_users_me(token: str = Depends(get_token_from_cookie)) ->User:
    try:
        payload = jwt.decode(token.replace("Bearer ", ""), settings.secret_key, algorithms=[settings.algorithm])
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Not authenticated")
    username = payload.get("sub")
    user_type = payload.get("user_type")
    user_db = await crud.get_user(app.state.engine, username, user_type)
    
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = convert_user_db_to_response(user_db)
    
    # 确保返回完整的用户信息
    if user.user_type == UserType.contractor:
        user.contractor_user = user.contractor_user
    elif user.user_type == UserType.enterprise:
        user.enterprise_user = user.enterprise_user
    # admin 用户不需要额外处理
    return user


async def authenticate_enterprise_level(user: User=Depends(read_users_me)):
    if user.user_type != UserType.admin and user.user_type != UserType.enterprise:  # 无权访问该接口
        raise HTTPException(status_code=401, detail="Access to this api is not permitted! higher access level needed!")
    if user.user_type == UserType.enterprise and PermissionLevel.map(user.enterprise_user.role_type) < PermissionLevel.manager:
        raise HTTPException(status_code=401, detail="Access to this api is not permitted! higher access level needed!")
    return user

async def authenticate_contractor_level(user: User=Depends(read_users_me)):
    if user.user_type != UserType.admin:
        if user.user_type == UserType.contractor and PermissionLevel.map(user.contractor_user.role_type) < PermissionLevel.approver:
            raise HTTPException(status_code=401, detail="Access to this api is not permitted! higher access level needed!")
        if user.user_type == UserType.enterprise and PermissionLevel.map(user.enterprise_user.role_type) < PermissionLevel.site_staff:
            raise HTTPException(status_code=401, detail="Access to this api is not permitted! higher access level needed!")
    return user


@app.post("/enterprise/add/", dependencies=[Depends(authenticate_enterprise_level)])
async def add_enterprise(enterprise: Enterprise):
    enterprise_db =  await crud.create_enterprise(app.state.engine, enterprise)
    return enterprise_db


@app.post("/enterprise/add_user/", dependencies=[Depends(authenticate_enterprise_level)])
async def add_enterprise_user(enterprise_user: EnterpriseUser, create_account: bool=Query(default=True)):
    try:
        if create_account:
            user = User(
                user_type=UserType.enterprise,
                username=enterprise_user.phone,
                password_hash=pwd.get_password_hash(enterprise_user.phone[-6:])
            )
            enterprise_user_db = await crud.create_enterprise_user(app.state.engine, enterprise_user, user)
        else:
            enterprise_user_db = await crud.create_enterprise_user(app.state.engine, enterprise_user)
    except Exception as e:
        return HTTPException(status_code=500, detail="Failed to create this enterprise user: " + str(e))
    return enterprise_user_db

@app.post("/enterprise/add_department/", dependencies=[Depends(authenticate_enterprise_level)])
async def add_department(department: Department):
    department_db = await crud.create_department(app.state.engine, department)
    return department_db


@app.post("/contractor/add/", dependencies=[Depends(authenticate_enterprise_level)])
async def add_contractor(contractor: Contractor):
    contractor_db = await crud.create_contractor(app.state.engine, contractor)
    return contractor_db


@app.post("/contractor/add_user/", dependencies=[Depends(authenticate_contractor_level)])
async def add_contractor_user(contractor_user: ContractorUser, create_account: bool=Query(default=True)):
    try:
        if create_account:
            user = User(
                user_type=UserType.enterprise,
                username=contractor_user.phone,
                password_hash=pwd.get_password_hash(contractor_user.phone[-6:])
            )
            contractor_user_db = await crud.create_contractor_user(app.state.engine, contractor_user, user)
        else:
            contractor_user_db = await crud.create_contractor_user(app.state.engine, contractor_user)
    except Exception as e:
        return HTTPException(status_code=500, detail="Failed to create this enterprise user: " + str(e))
    return contractor_user_db

@app.post("/contractor/add_project", dependencies=[Depends(authenticate_enterprise_level)])
async def add_project(project: Project):
    project_db = await crud.create_project(app.state.engine, project)
    return project_db

@app.post("/contractor/add_plan/", dependencies=[Depends(authenticate_contractor_level)])
async def add_plan(plan: Plan):
    plan_db = await crud.create_plan(app.state.engine, plan)
    return plan_db

@app.get("/projects/")
async def get_projects(user: User = Depends(read_users_me)) -> List[ProjectListItem]:
    """获取项目列表，根据用户权限过滤"""
    projects = await crud.get_projects_for_user(app.state.engine, user)
    return await convert_projects_to_list_response(app.state.engine, projects)


@app.get("/test/", dependencies=[Depends(read_users_me)])
async def test() :
    return {"hello": "world"}

@app.get("/projects/{project_id}/", dependencies=[Depends(read_users_me)])
async def get_project_detail(project_id: int, user: User = Depends(read_users_me)) -> ProjectDetail:
    """获取项目详情，包含计划列表"""
    project = await crud.get_project_detail(app.state.engine, project_id, user)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在或无权限访问")
    return await convert_project_to_detail_response(app.state.engine, project)

@app.get("/plans/{plan_id}/participants/", dependencies=[Depends(read_users_me)])
async def get_plan_participants(plan_id: int, user: User = Depends(read_users_me)) -> List[PlanParticipant]:
    """获取计划的参与人员列表"""
    # 这里可以添加权限检查，确保用户有权限查看该计划
    participants = await crud.get_plan_participants(app.state.engine, plan_id)
    result = []
    for participant in participants:
        is_registered = await crud.check_user_registration(app.state.engine, participant.user_id, plan_id)
        participant_item = PlanParticipant(
            user_id=participant.user_id,
            name=participant.name,
            phone=participant.phone,
            id_number=participant.id_number,
            is_registered=is_registered
        )
        result.append(participant_item)
    return result

@app.get("/contractors/")
async def get_contractors(user: User = Depends(read_users_me)) -> List[ContractorListItem]:
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