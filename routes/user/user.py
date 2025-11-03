"""
用户管理路由
User management routes
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select, and_, or_

from api.model import (
    UserCreate,
    UserUpdate,
    UserListItem,
    UserDetail,
    PasswordChange,
    PasswordReset,
    User,
    UserType,
    EnterpriseUser as EnterpriseUserAPI,
    ContractorUser as ContractorUserAPI,
    EnterpriseUserUpdate,
    EnterpriseUserListItem,
    DepartmentWithMemberCount
)
from db.models import User as UserDB, EnterpriseUser, ContractorUser, Company, Department, Contractor
from core import password as pwd
from routes.dependencies import get_current_user, authenticate_enterprise_level, authenticate_contractor_level

router = APIRouter()


@router.post("/", dependencies=[Depends(authenticate_enterprise_level)])
async def create_user(user_data: UserCreate):
    """创建用户（统一接口）"""
    from main import app
    from db import crud
    
    try:
        # 验证用户类型和必填字段
        if user_data.user_type == UserType.enterprise:
            if not user_data.enterprise_id:
                raise HTTPException(status_code=400, detail="企业用户必须指定企业ID")
        elif user_data.user_type == UserType.contractor:
            if not user_data.contractor_id or not user_data.id_number or not user_data.work_type:
                raise HTTPException(status_code=400, detail="承包商用户必须指定承包商ID、身份证号和工种")
        
        # 检查用户名是否已存在
        existing_user = await crud.get_user(app.state.engine, user_data.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已存在")
        
        # 创建用户账号
        password_hash = pwd.get_password_hash(user_data.password)
        
        if user_data.user_type == UserType.enterprise:
            # 创建企业用户
            from api.model import EnterpriseUser as EnterpriseUserAPI
            enterprise_user = EnterpriseUserAPI(
                enterprise_id=user_data.enterprise_id,
                department_id=user_data.department_id,
                name=user_data.name,
                phone=user_data.phone,
                email=user_data.email,
                position=user_data.position,
                role_type=user_data.role_type,
                status=True
            )
            user_account = User(
                user_type=user_data.user_type,
                username=user_data.username,
                password_hash=password_hash
            )
            result = await crud.create_enterprise_user(app.state.engine, enterprise_user, user_account)
            
        elif user_data.user_type == UserType.contractor:
            # 创建承包商用户
            from api.model import ContractorUser as ContractorUserAPI
            contractor_user = ContractorUserAPI(
                contractor_id=user_data.contractor_id,
                name=user_data.name,
                phone=user_data.phone,
                id_number=user_data.id_number,
                work_type=user_data.work_type,
                personal_photo=user_data.personal_photo or "",
                role_type=user_data.role_type,
                status=True
            )
            user_account = User(
                user_type=user_data.user_type,
                username=user_data.username,
                password_hash=password_hash
            )
            result = await crud.create_contractor_user(app.state.engine, contractor_user, user_account)
        
        else:
            raise HTTPException(status_code=400, detail="不支持的用户类型")
        
        return {
            "message": "用户创建成功",
            "user_id": result.user_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"创建用户失败: {str(e)}")


@router.get("/")
async def get_users(
    user_type: UserType = Query(default=None, description="按用户类型筛选"),
    status: bool = Query(default=None, description="按状态筛选"),
    keyword: str = Query(default=None, description="搜索关键词（姓名、手机号）"),
    user: User = Depends(get_current_user)
) -> List[UserListItem]:
    """获取用户列表"""
    from main import app
    
    try:
        async with app.state.engine.begin() as conn:
            users = []
            
            # 根据用户类型筛选
            if user_type == UserType.enterprise or user_type is None:
                # 查询企业用户
                query = select(
                    EnterpriseUser,
                    UserDB,
                    Company.name.label("company_name"),
                    Department.name.label("dept_name")
                ).join(
                    UserDB, EnterpriseUser.user_id == UserDB.enterprise_staff_id
                ).join(
                    Company, EnterpriseUser.company_id == Company.company_id
                ).outerjoin(
                    Department, EnterpriseUser.dept_id == Department.dept_id
                )
                
                # 企业用户只能看到自己企业的用户
                if user.user_type == UserType.enterprise:
                    query = query.where(EnterpriseUser.company_id == user.enterprise_user.enterprise_id)
                
                # 添加筛选条件
                if status is not None:
                    query = query.where(EnterpriseUser.status == status)
                
                if keyword:
                    query = query.where(
                        or_(
                            EnterpriseUser.name.contains(keyword),
                            EnterpriseUser.phone.contains(keyword)
                        )
                    )
                
                result = await conn.execute(query)
                rows = result.all()
                
                for row in rows:
                    eu, u, company_name, dept_name = row
                    users.append(UserListItem(
                        user_id=eu.user_id,
                        username=u.username,
                        user_type=UserType.enterprise,
                        name=eu.name,
                        phone=eu.phone,
                        email=eu.email,
                        role_type=eu.role_type,
                        status=eu.status,
                        company_name=company_name,
                        department_name=dept_name,
                        created_at=u.created_at.isoformat()
                    ))
            
            if user_type == UserType.contractor or user_type is None:
                # 查询承包商用户（只有管理员可以查看）
                if user.user_type == UserType.admin:
                    query = select(
                        ContractorUser,
                        UserDB,
                        Contractor.company_name
                    ).join(
                        UserDB, ContractorUser.user_id == UserDB.contractor_staff_id
                    ).join(
                        Contractor, ContractorUser.contractor_id == Contractor.contractor_id
                    )
                    
                    if status is not None:
                        query = query.where(ContractorUser.status == status)
                    
                    if keyword:
                        query = query.where(
                            or_(
                                ContractorUser.name.contains(keyword),
                                ContractorUser.phone.contains(keyword)
                            )
                        )
                    
                    result = await conn.execute(query)
                    rows = result.all()
                    
                    for row in rows:
                        cu, u, company_name = row
                        users.append(UserListItem(
                            user_id=cu.user_id,
                            username=u.username,
                            user_type=UserType.contractor,
                            name=cu.name,
                            phone=cu.phone,
                            email=None,
                            role_type=cu.role_type,
                            status=cu.status,
                            company_name=company_name,
                            department_name=None,
                            created_at=u.created_at.isoformat()
                        ))
            
            return users
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取用户列表失败: {str(e)}")


@router.get("/{user_id}/")
async def get_user_detail(
    user_id: int,
    current_user: User = Depends(get_current_user)
) -> UserDetail:
    """获取用户详情"""
    from main import app
    
    try:
        async with app.state.engine.begin() as conn:
            # 先尝试查询企业用户
            eu_query = select(
                EnterpriseUser,
                UserDB,
                Company.name.label("company_name"),
                Department.name.label("dept_name")
            ).join(
                UserDB, EnterpriseUser.user_id == UserDB.enterprise_staff_id
            ).join(
                Company, EnterpriseUser.company_id == Company.company_id
            ).outerjoin(
                Department, EnterpriseUser.dept_id == Department.dept_id
            ).where(EnterpriseUser.user_id == user_id)
            
            result = await conn.execute(eu_query)
            row = result.first()
            
            if row:
                eu, u, company_name, dept_name = row
                
                # 权限检查
                if current_user.user_type == UserType.enterprise:
                    if eu.company_id != current_user.enterprise_user.enterprise_id:
                        raise HTTPException(status_code=403, detail="无权访问该用户信息")
                
                return UserDetail(
                    user_id=eu.user_id,
                    username=u.username,
                    user_type=UserType.enterprise,
                    name=eu.name,
                    phone=eu.phone,
                    email=eu.email,
                    position=eu.position,
                    role_type=eu.role_type,
                    status=eu.status,
                    company_id=eu.company_id,
                    company_name=company_name,
                    department_id=eu.dept_id,
                    department_name=dept_name,
                    contractor_id=None,
                    id_number=None,
                    work_type=None,
                    approval_level=eu.approval_level,
                    created_at=u.created_at.isoformat(),
                    updated_at=u.updated_at.isoformat()
                )
            
            # 查询承包商用户
            cu_query = select(
                ContractorUser,
                UserDB,
                Contractor.company_name
            ).join(
                UserDB, ContractorUser.user_id == UserDB.contractor_staff_id
            ).join(
                Contractor, ContractorUser.contractor_id == Contractor.contractor_id
            ).where(ContractorUser.user_id == user_id)
            
            result = await conn.execute(cu_query)
            row = result.first()
            
            if row:
                cu, u, company_name = row
                
                # 只有管理员可以查看承包商用户详情
                if current_user.user_type != UserType.admin:
                    raise HTTPException(status_code=403, detail="无权访问该用户信息")
                
                return UserDetail(
                    user_id=cu.user_id,
                    username=u.username,
                    user_type=UserType.contractor,
                    name=cu.name,
                    phone=cu.phone,
                    email=None,
                    position=None,
                    role_type=cu.role_type,
                    status=cu.status,
                    company_id=None,
                    company_name=company_name,
                    department_id=None,
                    department_name=None,
                    contractor_id=cu.contractor_id,
                    id_number=cu.id_number,
                    work_type=cu.work_type,
                    approval_level=None,
                    created_at=u.created_at.isoformat(),
                    updated_at=u.updated_at.isoformat()
                )
            
            raise HTTPException(status_code=404, detail="用户不存在")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取用户详情失败: {str(e)}")


@router.put("/{user_id}/", dependencies=[Depends(authenticate_enterprise_level)])
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """更新用户信息"""
    from main import app
    from db import crud
    
    try:
        # 使用现有的更新函数
        result = await crud.update_enterprise_user(app.state.engine, user_id, user_data)
        
        if not result:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 如果需要修改密码
        if user_data.password:
            user_account = await crud.get_user(app.state.engine, result.phone)
            if user_account:
                async with app.state.engine.begin() as conn:
                    query = select(UserDB).where(UserDB.user_id == user_account.user_id)
                    result_user = await conn.execute(query)
                    db_user = result_user.scalar_one_or_none()
                    if db_user:
                        db_user.password_hash = pwd.get_password_hash(user_data.password)
                        await conn.commit()
        
        return {"message": "用户信息更新成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"更新用户信息失败: {str(e)}")


@router.delete("/{user_id}/", dependencies=[Depends(authenticate_enterprise_level)])
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """删除用户（软删除，设置status为False）"""
    from main import app
    
    try:
        async with app.state.engine.begin() as conn:
            # 尝试查询企业用户
            eu_query = select(EnterpriseUser).where(EnterpriseUser.user_id == user_id)
            result = await conn.execute(eu_query)
            eu = result.scalar_one_or_none()
            
            if eu:
                # 权限检查
                if current_user.user_type == UserType.enterprise:
                    if eu.company_id != current_user.enterprise_user.enterprise_id:
                        raise HTTPException(status_code=403, detail="无权删除该用户")
                
                eu.status = False
                await conn.commit()
                return {"message": "用户已禁用"}
            
            # 尝试查询承包商用户
            cu_query = select(ContractorUser).where(ContractorUser.user_id == user_id)
            result = await conn.execute(cu_query)
            cu = result.scalar_one_or_none()
            
            if cu:
                if current_user.user_type != UserType.admin:
                    raise HTTPException(status_code=403, detail="无权删除该用户")
                
                cu.status = False
                await conn.commit()
                return {"message": "用户已禁用"}
            
            raise HTTPException(status_code=404, detail="用户不存在")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"删除用户失败: {str(e)}")


@router.post("/{user_id}/change-password/")
async def change_password(
    user_id: int,
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user)
):
    """修改密码（用户自己修改）"""
    from main import app
    
    # 只能修改自己的密码
    if current_user.user_id != user_id and current_user.user_type != UserType.admin:
        raise HTTPException(status_code=403, detail="只能修改自己的密码")
    
    try:
        async with app.state.engine.begin() as conn:
            # 获取用户账号
            query = select(UserDB).where(
                or_(
                    UserDB.enterprise_staff_id == user_id,
                    UserDB.contractor_staff_id == user_id
                )
            )
            result = await conn.execute(query)
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(status_code=404, detail="用户不存在")
            
            # 验证旧密码
            if not pwd.verify_password(password_data.old_password, user.password_hash):
                raise HTTPException(status_code=400, detail="原密码错误")
            
            # 更新密码
            user.password_hash = pwd.get_password_hash(password_data.new_password)
            user.updated_at = pwd.datetime.now()
            await conn.commit()
            
            return {"message": "密码修改成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"修改密码失败: {str(e)}")


@router.post("/{user_id}/reset-password/", dependencies=[Depends(authenticate_enterprise_level)])
async def reset_password(
    user_id: int,
    password_data: PasswordReset,
    current_user: User = Depends(get_current_user)
):
    """重置密码（管理员操作）"""
    from main import app
    
    try:
        async with app.state.engine.begin() as conn:
            # 获取用户账号
            query = select(UserDB).where(
                or_(
                    UserDB.enterprise_staff_id == user_id,
                    UserDB.contractor_staff_id == user_id
                )
            )
            result = await conn.execute(query)
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(status_code=404, detail="用户不存在")
            
            # 更新密码
            user.password_hash = pwd.get_password_hash(password_data.new_password)
            user.updated_at = pwd.datetime.now()
            await conn.commit()
            
            return {"message": "密码重置成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"重置密码失败: {str(e)}")


# ===== 企业用户管理接口 =====

@router.post("/enterprise/", dependencies=[Depends(authenticate_enterprise_level)])
async def add_enterprise_user(enterprise_user: EnterpriseUserAPI, create_account: bool = Query(default=True)):
    """添加企业用户"""
    from main import app
    from db import crud
    
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
        raise HTTPException(status_code=500, detail=f"Failed to create this enterprise user: {str(e)}")
    return enterprise_user_db


@router.get("/staff/departments/")
async def get_departments_with_members(
    user: User = Depends(get_current_user)
) -> List[DepartmentWithMemberCount]:
    """获取部门列表及成员数量"""
    from main import app
    from db import crud
    
    try:
        if user.user_type == UserType.admin:
            # 管理员可以看到所有部门
            departments = await crud.get_departments_with_member_count(app.state.engine)
        elif user.user_type == UserType.enterprise:
            # 企业用户只能看到自己企业的部门
            enterprise_id = user.enterprise_user.enterprise_id
            departments = await crud.get_departments_with_member_count(app.state.engine, enterprise_id)
        else:
            raise HTTPException(status_code=403, detail="权限不足")
        
        return departments
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取部门列表失败: {str(e)}")


@router.get("/staff/departments/{dept_id}/members/")
async def get_department_members(
    dept_id: int,
    user: User = Depends(get_current_user)
) -> List[EnterpriseUserListItem]:
    """获取指定部门的成员列表"""
    from main import app
    from db import crud
    
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


@router.get("/staff/enterprise/{enterprise_id}/members/")
async def get_enterprise_members(
    enterprise_id: int,
    dept_id: int = Query(default=None, description="部门ID，可选筛选条件"),
    user: User = Depends(get_current_user)
) -> List[EnterpriseUserListItem]:
    """获取企业成员列表，可按部门筛选"""
    from main import app
    from db import crud
    
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


@router.get("/staff/users/{user_id}/")
async def get_enterprise_user_detail(
    user_id: int,
    user: User = Depends(get_current_user)
) -> EnterpriseUserAPI:
    """获取企业用户详情"""
    from main import app
    from db import crud
    
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
        
        return EnterpriseUserAPI(
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


@router.put("/staff/users/{user_id}/", dependencies=[Depends(authenticate_enterprise_level)])
async def update_enterprise_user(
    user_id: int,
    user_data: EnterpriseUserUpdate,
    user: User = Depends(get_current_user)
):
    """更新企业用户信息"""
    from main import app
    from db import crud
    
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


# ===== 承包商用户管理接口 =====

@router.post("/contractor/", dependencies=[Depends(authenticate_contractor_level)])
async def add_contractor_user(contractor_user: ContractorUserAPI, create_account: bool = Query(default=True)):
    """添加承包商用户"""
    from main import app
    from db import crud
    
    try:
        if create_account:
            user = User(
                user_type=UserType.contractor,
                username=contractor_user.phone,
                password_hash=pwd.get_password_hash(contractor_user.phone[-6:])
            )
            contractor_user_db = await crud.create_contractor_user(app.state.engine, contractor_user, user)
        else:
            contractor_user_db = await crud.create_contractor_user(app.state.engine, contractor_user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create this contractor user: {str(e)}")
    return contractor_user_db

