# main.py
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
from api.model_trans import convert_user_db_to_response, convert_projects_to_list_response, convert_project_to_detail_response

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


from fastapi.security import OAuth2PasswordBearer

# 在文件顶部添加OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/token")
async def login_for_access_token(
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
    return Token(access_token=access_token, token_type="bearer")

# 修改token获取函数
def get_token_from_header(token: str = Depends(oauth2_scheme)):
    return token

@app.get("/users/me/")
async def read_users_me(token: str = Depends(get_token_from_header)) -> User:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Not authenticated")
    username = payload.get("sub")
    user_type = payload.get("user_type")
    user_db = await crud.get_user(app.state.engine, username, user_type)
    
    if not user_db:
        raise HTTPException(status_code=401, detail="User not found")
    
    user = convert_user_db_to_response(user_db)
    
    # 确保返回完整的用户信息
    if user.user_type == UserType.contractor:
        user.contractor_user = user.contractor_user
    elif user.user_type == UserType.enterprise:
        user.enterprise_user = user.enterprise_user
    return user

@app.post("/logout")
async def logout():
    # 由于我们使用localStorage管理token，后端不需要做任何操作
    return {"message": "Logged out"}

# 删除以下重复的代码块（第127-155行）：
# def get_token_from_cookie(access_token: str | None = Cookie(default=None)):
#     if access_token is None:
#         raise HTTPException(status_code=401, detail="Not authenticated")
#     return access_token

# @app.get("/users/me/")
# async def read_users_me(token: str = Depends(get_token_from_cookie)) ->User:
#     try:
#         payload = jwt.decode(token.replace("Bearer ", ""), settings.secret_key, algorithms=[settings.algorithm])
#     except InvalidTokenError:
#         raise HTTPException(status_code=401, detail="Not authenticated")
#     username = payload.get("sub")
#     user_type = payload.get("user_type")
#     user_db = await crud.get_user(app.state.engine, username, user_type)
#     
#     if not user_db:
#         raise HTTPException(status_code=404, detail="User not found")
#     
#     user = convert_user_db_to_response(user_db)
#     
#     # 确保返回完整的用户信息
#     if user.user_type == UserType.contractor:
#         user.contractor_user = user.contractor_user
#     elif user.user_type == UserType.enterprise:
#         user.enterprise_user = user.enterprise_user
#     # admin 用户不需要额外处理
#     return user


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

# 添加一个辅助函数来获取用户的企业ID
def get_user_enterprise_id(user: User) -> int:
    """获取用户的企业ID"""
    if user.user_type == UserType.enterprise and user.enterprise_user:
        return user.enterprise_user.enterprise_id
    return 0

# 企业相关 API 端点
@app.get("/enterprises/")
async def get_enterprises(user: User = Depends(read_users_me)) -> List[EnterpriseListItem]:
    """获取企业列表"""
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

# 部门相关 API 端点
@app.get("/departments/")
async def get_departments(
    enterprise_id: int = Query(default=None, description="企业ID，不传则获取当前用户企业的部门"),
    user: User = Depends(read_users_me)
) -> List[DepartmentListItem]:
    """获取部门列表"""
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

# Area 相关 API 端点
@app.post("/areas/", dependencies=[Depends(authenticate_enterprise_level)])
async def create_area(area: Area):
    """创建厂区"""
    try:
        area_db = await crud.create_area(app.state.engine, area)
        return {"message": "厂区创建成功", "area_id": area_db.area_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"创建厂区失败: {str(e)}")

@app.get("/areas/")
async def get_areas(
    enterprise_id: int = Query(default=None, description="企业ID，不传则获取所有厂区"),
    user: User = Depends(read_users_me)
) -> List[AreaListItem]:
    """获取厂区列表"""
    try:
        # 如果是企业用户，只能查看自己企业的厂区
        if user.user_type == UserType.enterprise and user.enterprise_user:
            enterprise_id = user.enterprise_user.enterprise_id
        
        areas = await crud.get_area_list_with_details(app.state.engine, enterprise_id)
        return areas
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取厂区列表失败: {str(e)}")

@app.get("/areas/{area_id}/")
async def get_area_detail(area_id: int, user: User = Depends(read_users_me)) -> Area:
    """获取厂区详情"""
    try:
        # 自动从用户身份获取企业ID
        enterprise_id = get_user_enterprise_id(user)
        
        area = await crud.get_area_by_id(app.state.engine, area_id)
        if not area:
            raise HTTPException(status_code=404, detail="厂区不存在")
        
        # 确保只能访问自己企业的厂区
        if area.enterprise_id != enterprise_id:
            raise HTTPException(status_code=403, detail="无权限访问该厂区")
        
        return Area(
            area_id=area.area_id,
            area_name=area.area_name,
            dept_id=area.dept_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取厂区详情失败: {str(e)}")

@app.put("/areas/{area_id}/", dependencies=[Depends(authenticate_enterprise_level)])
async def update_area(area_id: int, area_data: Area, user: User = Depends(read_users_me)):
    """更新厂区信息"""
    try:
        # 自动从用户身份获取企业ID
        enterprise_id = get_user_enterprise_id(user)
        
        # 检查厂区是否存在且属于当前企业
        existing_area = await crud.get_area_by_id(app.state.engine, area_id)
        if not existing_area:
            raise HTTPException(status_code=404, detail="厂区不存在")
        
        if existing_area.enterprise_id != enterprise_id:
            raise HTTPException(status_code=403, detail="无权限修改该厂区")
        
        # 创建更新数据，确保企业ID不变
        update_data = Area(
            area_name=area_data.area_name,
            enterprise_id=enterprise_id,  # 确保企业ID不变
            dept_id=area_data.dept_id
        )
        
        updated_area = await crud.update_area(app.state.engine, area_id, update_data)
        if not updated_area:
            raise HTTPException(status_code=404, detail="更新失败")
        
        return {"message": "厂区更新成功", "area_id": updated_area.area_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"更新厂区失败: {str(e)}")

@app.delete("/areas/{area_id}/", dependencies=[Depends(authenticate_enterprise_level)])
async def delete_area(area_id: int, user: User = Depends(read_users_me)):
    """删除厂区"""
    try:
        # 自动从用户身份获取企业ID
        enterprise_id = get_user_enterprise_id(user)
        
        # 检查厂区是否存在且属于当前企业
        existing_area = await crud.get_area_by_id(app.state.engine, area_id)
        if not existing_area:
            raise HTTPException(status_code=404, detail="厂区不存在")
        
        if existing_area.enterprise_id != enterprise_id:
            raise HTTPException(status_code=403, detail="无权限删除该厂区")
        
        success = await crud.delete_area(app.state.engine, area_id)
        if not success:
            raise HTTPException(status_code=404, detail="删除失败")
        
        return {"message": "厂区删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"删除厂区失败: {str(e)}")

@app.get("/departments/{dept_id}/areas/")
async def get_department_areas(dept_id: int, user: User = Depends(read_users_me)) -> List[Area]:
    """获取指定部门的厂区（仅限当前企业）"""
    try:
        # 自动从用户身份获取企业ID
        enterprise_id = get_user_enterprise_id(user)
        
        # 首先验证部门是否属于当前企业
        # 这里需要添加一个检查部门归属的函数
        # 为了简化，我们直接获取部门的厂区，然后过滤
        
        areas = await crud.get_areas_by_department(app.state.engine, dept_id)
        
        # 过滤出属于当前企业的厂区
        filtered_areas = [
            area for area in areas 
            if area.enterprise_id == enterprise_id
        ]
        
        return [
            Area(
                area_id=area.area_id,
                area_name=area.area_name,
                dept_id=area.dept_id
            ) for area in filtered_areas
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取部门厂区失败: {str(e)}")

# ===== 人员管理相关接口 =====

@app.get("/staff/departments/")
async def get_departments_with_members(
    user: User = Depends(read_users_me)
) -> List[DepartmentWithMemberCount]:
    """获取部门列表及成员数量"""
    try:
        if user.user_type == UserType.admin:
            # 管理员可以看到所有部门
            departments = await crud.get_departments_with_member_count(app.state.engine)
        elif user.user_type == UserType.enterprise:
            # 企业用户只能看到自己企业的部门
            enterprise_id = user.enterprise_user.enterprise_id  # 修复：使用company_id而不是enterprise_id
            departments = await crud.get_departments_with_member_count(app.state.engine, enterprise_id)
        else:
            raise HTTPException(status_code=403, detail="权限不足")
        
        return departments
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取部门列表失败: {str(e)}")

@app.get("/staff/departments/{dept_id}/members/")
async def get_department_members(
    dept_id: int,
    user: User = Depends(read_users_me)
) -> List[EnterpriseUserListItem]:
    """获取指定部门的成员列表"""
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

@app.get("/staff/enterprise/{enterprise_id}/members/")
async def get_enterprise_members(
    enterprise_id: int,
    dept_id: int = Query(default=None, description="部门ID，可选筛选条件"),
    user: User = Depends(read_users_me)
) -> List[EnterpriseUserListItem]:
    """获取企业成员列表，可按部门筛选"""
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

@app.get("/staff/users/{user_id}/")
async def get_enterprise_user_detail(
    user_id: int,
    user: User = Depends(read_users_me)
) -> EnterpriseUser:
    """获取企业用户详情"""
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

@app.put("/staff/users/{user_id}/", dependencies=[Depends(authenticate_enterprise_level)])
async def update_enterprise_user(
    user_id: int,
    user_data: EnterpriseUserUpdate,
    user: User = Depends(read_users_me)
):
    """更新企业用户信息"""
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
                raise HTTPException(status_code=403, detail="权限不足，只有管理员可以修改其他用户信息")
        
        updated_user = await crud.update_enterprise_user(app.state.engine, user_id, user_data)
        if not updated_user:
            raise HTTPException(status_code=404, detail="更新失败")
        
        return {"message": "用户信息更新成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"更新用户信息失败: {str(e)}")