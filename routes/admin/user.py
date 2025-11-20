"""
系统用户管理路由
System user management routes
"""
from typing import List, Optional
from datetime import datetime
import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select, and_, or_

from api.model import User, UserType
from core import password as pwd
from routes.dependencies import get_current_user, get_engine
from db.connection import get_session

router = APIRouter()


def verify_admin(user: User = Depends(get_current_user)):
    """
    验证系统管理员权限
    
    系统管理员需要满足：
    - role_level = 0
    - user_status = 1 (通过审核)
    """
    if user.role_level != 0:
        raise HTTPException(status_code=403, detail="需要系统管理员权限")
    if user.user_status != 1:
        raise HTTPException(status_code=403, detail="系统管理员账号未通过审核")
    return user


@router.post("/", dependencies=[Depends(verify_admin)])
async def create_admin_user(
    username: str = Query(description="用户名"),
    password: str = Query(description="密码"),
    email: Optional[str] = Query(default=None, description="邮箱")
):
    """
    创建系统管理员账户
    
    只有系统管理员可以创建新的管理员账户
    """
    from main import app
    from db import crud
    
    try:
        # 检查用户名是否已存在
        existing_user = await crud.get_user(app.state.engine, username)
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已存在")
        
        # 创建管理员账户
        from db.models import User as UserDB
        from sqlmodel import select
        
        async with app.state.engine.begin() as conn:
            new_user = UserDB(
                user_type=UserType.admin,
                username=username,
                password_hash=pwd.get_password_hash(password),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # 如果有 email 字段，设置它
            if hasattr(new_user, 'email') and email:
                new_user.email = email
            
            conn.add(new_user)
            await conn.commit()
            await conn.refresh(new_user)
            
            return {
                "message": "管理员账户创建成功",
                "user_id": new_user.user_id,
                "username": username
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"创建管理员账户失败: {str(e)}")


@router.get("/")
async def get_admin_users(
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
    user: User = Depends(verify_admin)
) -> dict:
    """
    获取系统管理员列表
    
    查看所有系统管理员账户
    """
    from main import app
    from db.models import User as UserDB
    from sqlmodel import select
    
    try:
        async with app.state.engine.begin() as conn:
            # 查询管理员用户
            query = select(UserDB).where(UserDB.user_type == UserType.admin)
            
            # 计算总数
            count_result = await conn.execute(query)
            total = len(count_result.all())
            
            # 分页查询
            query = query.offset((page - 1) * page_size).limit(page_size)
            result = await conn.execute(query)
            users = result.scalars().all()
            
            items = [
                {
                    "user_id": u.user_id,
                    "username": u.username,
                    "email": getattr(u, 'email', None),
                    "created_at": u.created_at.isoformat() if hasattr(u, 'created_at') else None,
                    "updated_at": u.updated_at.isoformat() if hasattr(u, 'updated_at') else None
                } for u in users
            ]
            
            return {
                "total": total,
                "page": page,
                "page_size": page_size,
                "items": items
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取管理员列表失败: {str(e)}")


@router.delete("/{user_id}/", dependencies=[Depends(verify_admin)])
async def delete_admin_user(user_id: int, current_user: User = Depends(verify_admin)):
    """
    删除系统管理员账户
    
    注意：不能删除自己的账户
    """
    from main import app
    from db.models import User as UserDB
    from sqlmodel import select
    
    try:
        # 不能删除自己
        if current_user.user_id == user_id:
            raise HTTPException(status_code=400, detail="不能删除自己的账户")
        
        async with app.state.engine.begin() as conn:
            # 查询用户
            query = select(UserDB).where(UserDB.user_id == user_id)
            result = await conn.execute(query)
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(status_code=404, detail="用户不存在")
            
            if user.user_type != UserType.admin:
                raise HTTPException(status_code=400, detail="该用户不是系统管理员")
            
            # 删除用户
            await conn.delete(user)
            await conn.commit()
            
            return {"message": "管理员账户删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"删除管理员账户失败: {str(e)}")


@router.post("/{user_id}/reset-password/", dependencies=[Depends(verify_admin)])
async def reset_admin_password(
    user_id: int,
    new_password: str = Query(description="新密码")
):
    """
    重置管理员密码
    
    系统管理员可以重置其他管理员的密码
    """
    from main import app
    from db.models import User as UserDB
    from sqlmodel import select
    
    try:
        async with app.state.engine.begin() as conn:
            # 查询用户
            query = select(UserDB).where(UserDB.user_id == user_id)
            result = await conn.execute(query)
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(status_code=404, detail="用户不存在")
            
            if user.user_type != UserType.admin:
                raise HTTPException(status_code=400, detail="该用户不是系统管理员")
            
            # 更新密码
            user.password_hash = pwd.get_password_hash(new_password)
            if hasattr(user, 'updated_at'):
                user.updated_at = datetime.now()
            
            await conn.commit()
            
            return {"message": "密码重置成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"重置密码失败: {str(e)}")


def verify_approval_access(user: User = Depends(get_current_user)):
    """
    验证审批权限
    
    允许访问的用户：
    - role_level=0 且 user_status=1 (系统管理员)
    - role_level=1 (企业管理员)
    """
    # 系统管理员：role_level=0 且 user_status=1
    if user.role_level == 0:
        # 检查 user_status，如果是 None 或不是 1，给出明确错误
        if user.user_status is None:
            raise HTTPException(
                status_code=403, 
                detail="系统管理员账号状态未设置（user_status 为 None），请联系管理员设置账号状态为 1（通过审核）"
            )
        elif user.user_status == 1:
            return user  # 系统管理员（已通过审核）
        else:
            raise HTTPException(
                status_code=403, 
                detail=f"系统管理员账号未通过审核（当前状态: {user.user_status}，需要状态: 1）。请确保系统管理员的 user_status 字段设置为 1"
            )
    
    # 企业管理员：role_level=1
    if user.role_level == 1:
        if not user.enterprise_staff_id:
            raise HTTPException(status_code=403, detail="企业管理员未绑定企业")
        return user  # 企业管理员
    
    raise HTTPException(
        status_code=403, 
        detail=f"无权访问此资源（role_level: {user.role_level}, user_status: {user.user_status}）"
    )


@router.get("/pending/")
async def get_pending_staff(
    user_type: Optional[str] = Query(default=None, description="用户类型筛选: enterprise, contractor, admin"),
    keyword: Optional[str] = Query(default=None, description="搜索关键词（用户名、姓名）"),
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
    user: User = Depends(verify_approval_access),
    engine = Depends(get_engine)
) -> dict:
    """
    获取待审批人员列表
    
    根据用户权限级别过滤：
    - 系统管理员(role_level=0): 可以查看所有待审批的人员（user_status=2）
    - 企业管理员(role_level=1): 只能查看自己企业的待审批人员
    """
    try:
        from db.models import User as UserDB
        from sqlalchemy import func
        
        async with get_session(engine) as session:
            # 构建查询条件
            conditions = [UserDB.user_status == 2]  # 待审核状态
            
            # 根据权限过滤
            if user.role_level == 1:
                # 企业管理员：只能查看自己企业的员工
                if user.enterprise_staff_id:
                    conditions.append(
                        and_(
                            UserDB.user_type == "enterprise",
                            UserDB.enterprise_staff_id == user.enterprise_staff_id
                        )
                    )
                else:
                    # 如果没有绑定企业，返回空列表
                    return {
                        "items": [],
                        "total": 0,
                        "page": page,
                        "page_size": page_size,
                        "total_pages": 0
                    }
            
            if user_type:
                conditions.append(UserDB.user_type == user_type)
            
            if keyword:
                # 搜索用户名或姓名
                keyword_conditions = [UserDB.username.contains(keyword)]
                # 添加 name_str 和 relay_name 的搜索条件（如果字段存在）
                try:
                    keyword_conditions.append(UserDB.name_str.contains(keyword))
                except:
                    pass
                try:
                    keyword_conditions.append(UserDB.relay_name.contains(keyword))
                except:
                    pass
                conditions.append(or_(*keyword_conditions))
            
            # 计算总数
            count_query = select(func.count(UserDB.user_id)).where(and_(*conditions))
            count_result = await session.exec(count_query)
            total = count_result.one()
            
            # 分页查询
            query = select(UserDB).where(and_(*conditions))
            query = query.order_by(UserDB.created_at.desc())
            query = query.offset((page - 1) * page_size).limit(page_size)
            result = await session.exec(query)
            users = result.all()
            
            # 转换为响应格式
            items = []
            for user_obj in users:
                # 处理 Row 对象
                if hasattr(user_obj, '__getitem__') and not isinstance(user_obj, UserDB):
                    user_obj = user_obj[0] if len(user_obj) > 0 else None
                    if user_obj is None:
                        continue
                
                # 获取关联的企业或供应商名称
                company_name = None
                if user_obj.user_type == "enterprise" and user_obj.enterprise_staff_id:
                    from db.models import EnterpriseInfo as EnterpriseDB
                    enterprise_query = select(EnterpriseDB).where(EnterpriseDB.enterprise_id == user_obj.enterprise_staff_id)
                    enterprise_result = await session.exec(enterprise_query)
                    enterprise = enterprise_result.first()
                    if enterprise:
                        if hasattr(enterprise, '__getitem__') and not isinstance(enterprise, EnterpriseDB):
                            enterprise = enterprise[0] if len(enterprise) > 0 else None
                        if enterprise:
                            company_name = enterprise.company_name
                
                elif user_obj.user_type == "contractor" and user_obj.contractor_staff_id:
                    from db.models import ContractorInfo as ContractorDB
                    contractor_query = select(ContractorDB).where(ContractorDB.contractor_id == user_obj.contractor_staff_id)
                    contractor_result = await session.exec(contractor_query)
                    contractor = contractor_result.first()
                    if contractor:
                        if hasattr(contractor, '__getitem__') and not isinstance(contractor, ContractorDB):
                            contractor = contractor[0] if len(contractor) > 0 else None
                        if contractor:
                            company_name = contractor.company_name
                
                items.append({
                    "user_id": user_obj.user_id,
                    "username": user_obj.username,
                    "name": user_obj.name_str or user_obj.relay_name or user_obj.username,
                    "user_type": user_obj.user_type,
                    "phone": user_obj.phone,
                    "email": user_obj.email,
                    "role_type": user_obj.role_type,
                    "role_level": user_obj.role_level,
                    "user_status": user_obj.user_status,
                    "enterprise_staff_id": user_obj.enterprise_staff_id,
                    "contractor_staff_id": user_obj.contractor_staff_id,
                    "company_name": company_name,
                    "created_at": user_obj.created_at.isoformat() if user_obj.created_at else None,
                    "updated_at": user_obj.updated_at.isoformat() if user_obj.updated_at else None,
                })
            
            return {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取待审批人员列表失败: {str(e)}")


@router.post("/{user_id}/approve/", dependencies=[Depends(verify_approval_access)])
async def approve_staff(
    user_id: int,
    approved: bool = Query(description="true=批准, false=拒绝"),
    comment: Optional[str] = Query(default=None, description="审批意见"),
    current_user: User = Depends(verify_approval_access),
    engine = Depends(get_engine)
):
    """
    审批人员
    
    根据用户权限级别审批：
    - 系统管理员(role_level=0): 可以审批所有人员
    - 企业管理员(role_level=1): 只能审批自己企业的员工
    
    审核通过：user_status 从 2（待审核）改为 1（通过审核）
    审核拒绝：user_status 从 2（待审核）改为 3（审核不通过）
    """
    try:
        from db.models import User as UserDB
        
        async with get_session(engine) as session:
            # 查询用户
            query = select(UserDB).where(UserDB.user_id == user_id)
            result = await session.exec(query)
            user_obj = result.first()
            
            if not user_obj:
                raise HTTPException(status_code=404, detail="用户不存在")
            
            # 处理 Row 对象
            if hasattr(user_obj, '__getitem__') and not isinstance(user_obj, UserDB):
                user_obj = user_obj[0] if len(user_obj) > 0 else None
                if user_obj is None:
                    raise HTTPException(status_code=404, detail="用户不存在")
            
            # 权限检查：企业管理员只能审批自己企业的员工
            if current_user.role_level == 1:
                if user_obj.user_type != "enterprise" or user_obj.enterprise_staff_id != current_user.enterprise_staff_id:
                    raise HTTPException(status_code=403, detail="无权审批此用户")
            
            # 检查当前状态
            if user_obj.user_status != 2:
                raise HTTPException(
                    status_code=400, 
                    detail=f"用户当前状态为'{user_obj.user_status}'，无法进行审批操作"
                )
            
            # 更新状态
            if approved:
                user_obj.user_status = 1  # 通过审核
                status_text = "批准"
            else:
                user_obj.user_status = 3  # 审核不通过
                status_text = "拒绝"
            
            user_obj.updated_at = datetime.now()
            
            session.add(user_obj)
            await session.commit()
            await session.refresh(user_obj)
            
            return {
                "message": f"人员审批已{status_text}",
                "user_id": user_obj.user_id,
                "user_status": user_obj.user_status,
                "comment": comment
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"审批人员失败: {str(e)}")


@router.get("/all/")
async def get_all_users(
    user_type: Optional[str] = Query(default=None, description="用户类型筛选: enterprise, contractor, admin"),
    user_status: Optional[int] = Query(default=None, description="审核状态筛选: 0未通过审核, 1通过审核, 2待审核, 3审核不通过"),
    role_level: Optional[int] = Query(default=None, description="角色等级: -1用户还未选择角色, 0系统管理员, 1企业管理员, 2企业员工, 3承包商管理员, 4承包商员工"),
    username: Optional[str] = Query(default=None, description="用户名模糊搜索"),
    user_id: Optional[int] = Query(default=None, description="用户ID精确搜索"),
    enterprise_staff_id: Optional[int] = Query(default=None, description="企业ID筛选"),
    contractor_staff_id: Optional[int] = Query(default=None, description="供应商ID筛选"),
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(verify_approval_access),
    engine = Depends(get_engine)
) -> dict:
    """
    获取所有用户列表
    
    根据用户权限级别过滤：
    - 系统管理员(role_level=0): 可以查看所有用户
    - 企业管理员(role_level=1): 只能查看自己企业的所有员工
    
    支持多种过滤条件：
    - user_type: 用户类型
    - user_status: 审核状态
    - role_level: 角色等级
    - username: 用户名模糊搜索
    - user_id: 用户ID精确搜索
    - enterprise_staff_id: 企业ID筛选
    - contractor_staff_id: 供应商ID筛选
    """
    try:
        from db.models import User as UserDB, EnterpriseInfo as EnterpriseDB, ContractorInfo as ContractorDB
        from sqlalchemy import func
        
        async with get_session(engine) as session:
            # 构建查询条件
            conditions = []
            
            # 根据权限过滤：系统管理员可以查看所有用户，企业管理员只能查看自己企业的员工
            if current_user.role_level == 0 and current_user.user_status == 1:
                # 系统管理员：可以查看所有用户，不需要添加过滤条件
                pass
            elif current_user.role_level == 1:
                # 企业管理员：只能查看自己企业的员工
                if current_user.enterprise_staff_id:
                    # 查询 enterprise_staff_id 与当前用户 enterprise_staff_id 相同的所有用户
                    conditions.append(UserDB.enterprise_staff_id == current_user.enterprise_staff_id)
                else:
                    # 如果没有绑定企业，返回空列表
                    return {
                        "items": [],
                        "total": 0,
                        "page": page,
                        "page_size": page_size,
                        "total_pages": 0
                    }
            else:
                # 其他角色无权访问
                raise HTTPException(status_code=403, detail="无权访问此资源")
            
            if user_type:
                conditions.append(UserDB.user_type == user_type)
            
            if user_status is not None:
                conditions.append(UserDB.user_status == user_status)
            
            if role_level is not None:
                conditions.append(UserDB.role_level == role_level)
            
            if username:
                conditions.append(UserDB.username.contains(username))
            
            if user_id:
                conditions.append(UserDB.user_id == user_id)
            
            # 系统管理员可以使用这些筛选条件，企业管理员已经通过上面的条件过滤了
            if current_user.role_level == 0 and current_user.user_status == 1:
                if enterprise_staff_id:
                    conditions.append(UserDB.enterprise_staff_id == enterprise_staff_id)
                
                if contractor_staff_id:
                    conditions.append(UserDB.contractor_staff_id == contractor_staff_id)
            
            # 计算总数
            if conditions:
                count_query = select(func.count(UserDB.user_id)).where(and_(*conditions))
            else:
                count_query = select(func.count(UserDB.user_id))
            count_result = await session.exec(count_query)
            total = count_result.one()
            
            # 分页查询
            if conditions:
                query = select(UserDB).where(and_(*conditions))
            else:
                query = select(UserDB)
            query = query.order_by(UserDB.created_at.desc())
            query = query.offset((page - 1) * page_size).limit(page_size)
            result = await session.exec(query)
            users = result.all()
            
            # 转换为响应格式
            items = []
            for user_obj in users:
                # 处理 Row 对象
                if hasattr(user_obj, '__getitem__') and not isinstance(user_obj, UserDB):
                    user_obj = user_obj[0] if len(user_obj) > 0 else None
                    if user_obj is None:
                        continue
                
                # 获取关联的企业信息
                enterprise_name = None
                enterprise_license_number = None
                if user_obj.enterprise_staff_id:
                    enterprise_query = select(EnterpriseDB).where(EnterpriseDB.enterprise_id == user_obj.enterprise_staff_id)
                    enterprise_result = await session.exec(enterprise_query)
                    enterprise = enterprise_result.first()
                    if enterprise:
                        if hasattr(enterprise, '__getitem__') and not isinstance(enterprise, EnterpriseDB):
                            enterprise = enterprise[0] if len(enterprise) > 0 else None
                        if enterprise:
                            enterprise_name = enterprise.company_name
                            enterprise_license_number = enterprise.license_number
                
                # 获取关联的供应商信息
                contractor_name = None
                contractor_license_number = None
                if user_obj.contractor_staff_id:
                    contractor_query = select(ContractorDB).where(ContractorDB.contractor_id == user_obj.contractor_staff_id)
                    contractor_result = await session.exec(contractor_query)
                    contractor = contractor_result.first()
                    if contractor:
                        if hasattr(contractor, '__getitem__') and not isinstance(contractor, ContractorDB):
                            contractor = contractor[0] if len(contractor) > 0 else None
                        if contractor:
                            contractor_name = contractor.company_name
                            contractor_license_number = contractor.license_number
                
                items.append({
                    "user_id": user_obj.user_id,
                    "username": user_obj.username,
                    "name": user_obj.name_str or user_obj.relay_name or user_obj.username,
                    "user_type": user_obj.user_type,
                    "phone": user_obj.phone,
                    "email": user_obj.email,
                    "role_type": user_obj.role_type,
                    "role_level": user_obj.role_level,
                    "user_status": user_obj.user_status,
                    "enterprise_staff_id": user_obj.enterprise_staff_id,
                    "contractor_staff_id": user_obj.contractor_staff_id,
                    "enterprise_name": enterprise_name,
                    "enterprise_license_number": enterprise_license_number,
                    "contractor_name": contractor_name,
                    "contractor_license_number": contractor_license_number,
                    "created_at": user_obj.created_at.isoformat() if user_obj.created_at else None,
                    "updated_at": user_obj.updated_at.isoformat() if user_obj.updated_at else None,
                })
            
            return {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取用户列表失败: {str(e)}")


@router.put("/{user_id}/status/", dependencies=[Depends(verify_approval_access)])
async def update_user_status(
    user_id: int,
    user_status: Optional[int] = Query(default=None, description="用户状态: 0未通过审核, 1通过审核, 2待审核, 3审核不通过"),
    role_level: Optional[int] = Query(default=None, description="角色等级: 1企业管理员, 2企业员工"),
    comment: Optional[str] = Query(default=None, description="审批意见"),
    current_user: User = Depends(verify_approval_access),
    engine = Depends(get_engine)
):
    """
    更新用户状态
    
    根据用户权限级别：
    - 系统管理员(role_level=0): 可以更新所有用户的状态
    - 企业管理员(role_level=1): 只能更新自己企业员工的状态
    
    允许直接修改用户的user_status字段
    
    审核逻辑：
    1. 如果选择"通过审核"（user_status=1），同时将audit_status设置为2（审核通过）
       - 如果是企业管理员（role_level=1），需要检查所属企业在enterprise_info表中的business_status必须为"续存"
       - 如果是承包商管理员（role_level=3），需要检查所属供应商在contractor_info表中的business_status必须为"续存"
       - 如果企业或供应商状态不是"续存"，则不允许操作
    2. 如果从"审核通过"（user_status=1）变更为"待审核"（user_status=2）或"审核不通过"（user_status=3），需要检查：
       - 如果是系统管理员（user_type='admin'）：
         * 必须确保系统中至少还有3个系统管理员处于user_status=1（通过审核）状态
         * 如果不足3个，则不允许操作
       - 如果是企业管理员（role_level=1）：
         * 需要确保相同enterprise_staff_id下至少还有一个企业管理员是user_status=1（通过审核）
         * 如果没有其他通过审核的管理员，则不允许操作
       - 如果是承包商管理员（role_level=3）：
         * 需要确保相同contractor_staff_id下至少还有一个承包商管理员是user_status=1（通过审核）
         * 如果没有其他通过审核的管理员，则不允许操作
    3. 如果从其他状态变更为"审核不通过"（user_status=3），也需要进行上述检查
    """
    try:
        from db.models import User as UserDB
        
        # 验证状态值
        if user_status not in [0, 1, 2, 3]:
            raise HTTPException(status_code=400, detail="user_status必须是0、1、2或3")
        
        async with get_session(engine) as session:
            # 查询用户
            query = select(UserDB).where(UserDB.user_id == user_id)
            result = await session.exec(query)
            user_obj = result.first()
            
            if not user_obj:
                raise HTTPException(status_code=404, detail="用户不存在")
            
            # 处理 Row 对象
            if hasattr(user_obj, '__getitem__') and not isinstance(user_obj, UserDB):
                user_obj = user_obj[0] if len(user_obj) > 0 else None
                if user_obj is None:
                    raise HTTPException(status_code=404, detail="用户不存在")
            
            # 权限检查：企业管理员只能更新自己企业的员工
            if current_user.role_level == 1:
                if user_obj.user_type != "enterprise" or user_obj.enterprise_staff_id != current_user.enterprise_staff_id:
                    raise HTTPException(status_code=403, detail="无权更新此用户状态")
            
            # 处理role_level变更（仅企业管理员）
            if current_user.role_level == 1 and role_level is not None and role_level != user_obj.role_level:
                if role_level not in [1, 2]:
                    raise HTTPException(status_code=400, detail="企业管理员只能设置角色等级为1（企业管理员）或2（企业员工）")
                
                # 从1变成2时，需要验证当前企业审核通过的管理员不能少于3个
                if user_obj.role_level == 1 and role_level == 2:
                    admin_query = select(UserDB).where(
                        and_(
                            UserDB.enterprise_staff_id == current_user.enterprise_staff_id,
                            UserDB.role_level == 1,
                            UserDB.user_status == 1,
                            UserDB.user_id != user_id
                        )
                    )
                    admin_result = await session.exec(admin_query)
                    other_admins = admin_result.all()
                    
                    if not other_admins or len(other_admins) < 3:
                        raise HTTPException(
                            status_code=400,
                            detail="不允许操作：当前企业必须至少保留3个处于'通过审核'状态的企业管理员"
                        )
                
                user_obj.role_level = role_level
            
            # 验证user_status
            if user_status is not None:
                if user_status not in [0, 1, 2, 3]:
                    raise HTTPException(status_code=400, detail="user_status必须是0、1、2或3")
            
            # 检查管理员状态变更逻辑（仅在user_status有变更时）
            if user_status is not None:
                # 需要检查的情况：
                # 1. 从"审核通过"（user_status=1）变更为"待审核"（user_status=2）或"审核不通过"（user_status=3）
                # 2. 从其他状态变更为"审核不通过"（user_status=3）
                current_status = user_obj.user_status
                is_changing_from_approved = current_status == 1 and user_status in [2, 3]
                is_changing_to_rejected = user_status == 3
                
                if is_changing_from_approved or is_changing_to_rejected:
                    # 检查是否是系统管理员
                    is_system_admin = user_obj.user_type == "admin"
                    
                    if is_system_admin:
                        # 查找其他通过审核的系统管理员（user_type='admin' 且 user_status=1）
                        system_admin_query = select(UserDB).where(
                            and_(
                                UserDB.user_type == "admin",
                                UserDB.user_id != user_id,
                                UserDB.user_status == 1  # 通过审核
                            )
                        )
                        system_admin_result = await session.exec(system_admin_query)
                        other_approved_system_admins = system_admin_result.all()
                        
                        # 必须至少还有3个通过审核的系统管理员
                        if not other_approved_system_admins or len(other_approved_system_admins) < 3:
                            raise HTTPException(
                                status_code=400,
                                detail="不允许操作：系统必须至少保留3个处于'通过审核'状态的系统管理员。当前系统中通过审核的系统管理员数量不足3个。"
                            )
                    
                    # 检查是否是管理员：企业管理员（role_level=1）或承包商管理员（role_level=3）
                    is_enterprise_admin = user_obj.role_level == 1
                    is_contractor_admin = user_obj.role_level == 3
                    
                    if is_enterprise_admin or is_contractor_admin:
                        # 构建查询条件：查找相同enterprise_staff_id或contractor_staff_id下的其他管理员
                        admin_conditions = []
                        
                        if is_enterprise_admin and user_obj.enterprise_staff_id:
                            # 查找相同enterprise_staff_id下的其他企业管理员（role_level=1）
                            admin_conditions.append(
                                and_(
                                    UserDB.enterprise_staff_id == user_obj.enterprise_staff_id,
                                    UserDB.role_level == 1,
                                    UserDB.user_id != user_id,
                                    UserDB.user_status == 1  # 通过审核
                                )
                            )
                        
                        if is_contractor_admin and user_obj.contractor_staff_id:
                            # 查找相同contractor_staff_id下的其他承包商管理员（role_level=3）
                            admin_conditions.append(
                                and_(
                                    UserDB.contractor_staff_id == user_obj.contractor_staff_id,
                                    UserDB.role_level == 3,
                                    UserDB.user_id != user_id,
                                    UserDB.user_status == 1  # 通过审核
                                )
                            )
                        
                        # 如果找到了符合条件的查询条件，执行查询
                        if admin_conditions:
                            admin_query = select(UserDB).where(or_(*admin_conditions))
                            admin_result = await session.exec(admin_query)
                            other_approved_admins = admin_result.all()
                            
                            # 如果没有其他通过审核的管理员，不允许操作
                            if not other_approved_admins or len(other_approved_admins) == 0:
                                entity_type = "企业" if is_enterprise_admin else "供应商"
                                raise HTTPException(
                                    status_code=400,
                                    detail=f"不允许操作：该{entity_type}必须至少有一个管理员处于'通过审核'状态。当前{entity_type}下没有其他通过审核的管理员。"
                                )
            
            # 如果选择"通过审核"（user_status=1），需要检查企业或承包商的business_status
            if user_status is not None and user_status == 1:
                # 检查是否是管理员：企业管理员（role_level=1）或承包商管理员（role_level=3）
                is_enterprise_admin = user_obj.role_level == 1
                is_contractor_admin = user_obj.role_level == 3
                
                if is_enterprise_admin and user_obj.enterprise_staff_id:
                    # 检查企业信息表中的business_status
                    from db.models import EnterpriseInfo as EnterpriseDB
                    enterprise_query = select(EnterpriseDB).where(
                        EnterpriseDB.enterprise_id == user_obj.enterprise_staff_id
                    )
                    enterprise_result = await session.exec(enterprise_query)
                    enterprise = enterprise_result.first()
                    
                    if enterprise:
                        # 处理 Row 对象
                        if hasattr(enterprise, '__getitem__') and not isinstance(enterprise, EnterpriseDB):
                            enterprise = enterprise[0] if len(enterprise) > 0 else None
                        
                        if enterprise and enterprise.business_status != "续存":
                            raise HTTPException(
                                status_code=400,
                                detail=f"不允许操作：该企业当前状态为'{enterprise.business_status}'，只有状态为'续存'的企业管理员才能被审核通过。"
                            )
                
                if is_contractor_admin and user_obj.contractor_staff_id:
                    # 检查承包商信息表中的business_status
                    from db.models import ContractorInfo as ContractorDB
                    contractor_query = select(ContractorDB).where(
                        ContractorDB.contractor_id == user_obj.contractor_staff_id
                    )
                    contractor_result = await session.exec(contractor_query)
                    contractor = contractor_result.first()
                    
                    if contractor:
                        # 处理 Row 对象
                        if hasattr(contractor, '__getitem__') and not isinstance(contractor, ContractorDB):
                            contractor = contractor[0] if len(contractor) > 0 else None
                        
                        if contractor and contractor.business_status != "续存":
                            raise HTTPException(
                                status_code=400,
                                detail=f"不允许操作：该供应商当前状态为'{contractor.business_status}'，只有状态为'续存'的供应商管理员才能被审核通过。"
                            )
            
            # 更新状态
            if user_status is not None:
                user_obj.user_status = user_status
                
                # 如果选择"通过审核"（user_status=1），同时更新audit_status为2（审核通过）
                if user_status == 1:
                    user_obj.audit_status = 2
            
            user_obj.updated_at = datetime.now()
            
            session.add(user_obj)
            await session.commit()
            await session.refresh(user_obj)
            
            status_map = {0: "未通过审核", 1: "通过审核", 2: "待审核", 3: "审核不通过"}
            status_text = status_map.get(user_status, "未知状态")
            
            return {
                "message": f"用户状态已更新为：{status_text}",
                "user_id": user_obj.user_id,
                "user_status": user_obj.user_status,
                "audit_status": getattr(user_obj, 'audit_status', None),
                "comment": comment
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"更新用户状态失败: {str(e)}")

