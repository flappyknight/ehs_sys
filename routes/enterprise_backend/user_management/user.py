"""
企业员工管理路由
Enterprise staff management routes
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from api.model import (
    EnterpriseUser,
    EnterpriseUserListItem,
    User,
    UserType
)
from core import password as pwd
from db import crud
from routes.dependencies import get_current_user, authenticate_enterprise_level, get_engine

router = APIRouter()


@router.post("/", dependencies=[Depends(authenticate_enterprise_level)])
async def add_enterprise_user(enterprise_user: EnterpriseUser, create_account: bool = Query(default=True)):
    """添加企业用户"""
    from main import app
    
    try:
        if create_account:
            user = User(
                user_type=UserType.enterprise,
                username=enterprise_user.phone,
                password_hash=pwd.get_password_hash(enterprise_user.phone[-6:])
            )
            enterprise_user_db = await crud.create_enterprise_user(
                app.state.engine, enterprise_user, user
            )
        else:
            enterprise_user_db = await crud.create_enterprise_user(
                app.state.engine, enterprise_user
            )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to create this enterprise user: {str(e)}"
        )
    return enterprise_user_db


@router.get("/")
async def get_enterprise_users(
    department_id: int = Query(default=None, description="部门ID筛选"),
    user: User = Depends(get_current_user),
    engine = Depends(get_engine)
) -> List[EnterpriseUserListItem]:
    """获取企业用户列表"""
    from db.models import User as UserDB, EnterpriseInfo as EnterpriseDB
    from sqlmodel import select, and_
    from db.connection import get_session
    
    try:
        async with get_session(engine) as session:
            conditions = []
            
            # 根据用户权限过滤
            role_level = user.role_level if user.role_level is not None else -1
            user_status = user.user_status if user.user_status is not None else 0
            
            if role_level == 0 and user_status == 1:
                # 系统管理员：可以看到所有企业用户
                conditions.append(UserDB.user_type == "enterprise")
            elif role_level == 1:
                # 企业管理员：只能看到自己企业的用户
                if user.enterprise_staff_id:
                    conditions.append(UserDB.enterprise_staff_id == user.enterprise_staff_id)
                    conditions.append(UserDB.user_type == "enterprise")
                else:
                    return []
            elif role_level == 3:
                # 承包商管理员：只能看到自己承包商的所有人员
                if user.contractor_staff_id:
                    # 查询 contractor_staff_id 与当前用户 contractor_staff_id 相同的所有用户
                    conditions.append(UserDB.contractor_staff_id == user.contractor_staff_id)
                else:
                    return []
            else:
                raise HTTPException(status_code=403, detail="权限不足")
            
            # 执行查询
            if conditions:
                query = select(UserDB).where(and_(*conditions))
            else:
                query = select(UserDB)
            result = await session.exec(query)
            users_list = result.all()
            
            # 转换为响应格式
            members = []
            for user_obj in users_list:
                # 处理 Row 对象
                if hasattr(user_obj, '__getitem__') and not isinstance(user_obj, UserDB):
                    user_obj = user_obj[0] if len(user_obj) > 0 else None
                    if user_obj is None:
                        continue
                
                # 获取企业信息
                company_name = None
                enterprise_license_number = None
                if user_obj.enterprise_staff_id:
                    enterprise_query = select(EnterpriseDB).where(EnterpriseDB.enterprise_id == user_obj.enterprise_staff_id)
                    enterprise_result = await session.exec(enterprise_query)
                    enterprise = enterprise_result.first()
                    if enterprise:
                        if hasattr(enterprise, '__getitem__') and not isinstance(enterprise, EnterpriseDB):
                            enterprise = enterprise[0] if len(enterprise) > 0 else None
                        if enterprise:
                            company_name = enterprise.company_name
                            enterprise_license_number = enterprise.license_number
                
                # 获取承包商信息
                from db.models import ContractorInfo as ContractorDB
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
                
                # 返回完整信息
                members.append(EnterpriseUserListItem(
                    user_id=user_obj.user_id,
                    username=user_obj.username,
                    name=user_obj.name_str or user_obj.relay_name or user_obj.username,
                    phone=user_obj.phone or "",
                    email=user_obj.email or "",
                    position=None,
                    role_type=user_obj.role_type or "normal",
                    role_level=user_obj.role_level,
                    user_type=user_obj.user_type,
                    user_status=user_obj.user_status if user_obj.user_status is not None else 1,
                    company_name=company_name or "",
                    enterprise_name=company_name or "",
                    enterprise_license_number=enterprise_license_number or "",
                    contractor_name=contractor_name or "",
                    contractor_license_number=contractor_license_number or "",
                    enterprise_staff_id=user_obj.enterprise_staff_id,
                    contractor_staff_id=user_obj.contractor_staff_id,
                    dept_id=None,
                    status=user_obj.user_status if user_obj.user_status is not None else 1
                ))
            
            return members
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取用户列表失败: {str(e)}")


@router.put("/{user_id}/status/")
async def update_enterprise_user_status(
    user_id: int,
    user_status: Optional[int] = Query(default=None, description="用户状态: 0未通过审核, 1通过审核, 2待审核, 3审核不通过"),
    role_level: Optional[int] = Query(default=None, description="角色等级: 1企业管理员, 2企业员工, 3承包商管理员, 4承包商员工"),
    current_user: User = Depends(get_current_user),
    engine = Depends(get_engine)
):
    """
    更新企业用户状态和角色等级
    
    根据当前用户权限：
    - 企业管理员(role_level=1): 只能更新自己企业的员工，可以修改role_level（1和2之间）和user_status
    - 承包商管理员(role_level=3): 只能更新自己承包商的员工，可以修改role_level（3和4之间）和user_status
    
    验证逻辑：
    1. 企业管理员：从role_level=1变更为2时，需要验证当前企业审核通过的管理员不能少于3个
    2. 承包商管理员：从role_level=3变更为4时，需要验证当前承包商审核通过的管理员不能少于3个
    3. 承包商管理员：修改承包商管理员（role_level=3）的user_status从1变更为其他状态时，需要验证当前承包商审核通过的管理员不能少于3个
    """
    from db.models import User as UserDB
    from sqlmodel import select, and_
    from db.connection import get_session
    from datetime import datetime
    
    try:
        async with get_session(engine) as session:
            # 查询要更新的用户
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
            
            # 权限检查
            current_role_level = current_user.role_level if current_user.role_level is not None else -1
            
            if current_role_level == 1:
                # 企业管理员：只能更新自己企业的员工
                if user_obj.enterprise_staff_id != current_user.enterprise_staff_id:
                    raise HTTPException(status_code=403, detail="无权更新此用户")
                
                # 验证role_level变更
                if role_level is not None and role_level != user_obj.role_level:
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
            
            elif current_role_level == 3:
                # 承包商管理员：只能更新自己承包商的员工
                if user_obj.contractor_staff_id != current_user.contractor_staff_id:
                    raise HTTPException(status_code=403, detail="无权更新此用户")
                
                # 验证role_level变更
                if role_level is not None and role_level != user_obj.role_level:
                    if role_level not in [3, 4]:
                        raise HTTPException(status_code=400, detail="承包商管理员只能设置角色等级为3（承包商管理员）或4（承包商员工）")
                    
                    # 从3变成4时，需要验证当前承包商审核通过的管理员不能少于3个
                    if user_obj.role_level == 3 and role_level == 4:
                        admin_query = select(UserDB).where(
                            and_(
                                UserDB.contractor_staff_id == current_user.contractor_staff_id,
                                UserDB.role_level == 3,
                                UserDB.user_status == 1,
                                UserDB.user_id != user_id
                            )
                        )
                        admin_result = await session.exec(admin_query)
                        other_admins = admin_result.all()
                        
                        if not other_admins or len(other_admins) < 3:
                            raise HTTPException(
                                status_code=400,
                                detail="不允许操作：当前承包商必须至少保留3个处于'通过审核'状态的承包商管理员"
                            )
                    
                    user_obj.role_level = role_level
                
                # 验证user_status变更（针对承包商管理员和承包商员工）
                if user_status is not None and user_status != user_obj.user_status:
                    # 如果被修改的是承包商管理员（role_level=3），从通过审核（1）变更为其他状态时
                    if user_obj.role_level == 3 and user_obj.user_status == 1 and user_status != 1:
                        admin_query = select(UserDB).where(
                            and_(
                                UserDB.contractor_staff_id == current_user.contractor_staff_id,
                                UserDB.role_level == 3,
                                UserDB.user_status == 1,
                                UserDB.user_id != user_id
                            )
                        )
                        admin_result = await session.exec(admin_query)
                        other_admins = admin_result.all()
                        
                        if not other_admins or len(other_admins) < 3:
                            raise HTTPException(
                                status_code=400,
                                detail="不允许操作：当前承包商必须至少保留3个处于'通过审核'状态的承包商管理员"
                            )
                    
                    # 承包商员工（role_level=4）可以正常修改user_status
                    user_obj.user_status = user_status
            else:
                raise HTTPException(status_code=403, detail="权限不足")
            
            user_obj.updated_at = datetime.now()
            session.add(user_obj)
            await session.commit()
            await session.refresh(user_obj)
            
            return {
                "message": "用户信息已更新",
                "user_id": user_obj.user_id,
                "user_status": user_obj.user_status,
                "role_level": user_obj.role_level
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"更新用户信息失败: {str(e)}")

