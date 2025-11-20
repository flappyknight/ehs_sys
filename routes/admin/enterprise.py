"""
企业管理路由 (系统管理员)
Enterprise management routes for system admin
"""
from typing import List, Optional
from datetime import datetime
import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from api.model import (
    User,
    UserType,
    EnterpriseInfo,
    EnterpriseInfoCreate,
    EnterpriseInfoUpdate
)
from db.models import EnterpriseInfo as EnterpriseDB
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


def verify_enterprise_or_admin_access(user: User = Depends(get_current_user)):
    """
    验证企业管理员或系统管理员权限
    
    允许访问的用户：
    - role_level=0 且 user_status=1 (系统管理员)
    - role_level=1 (企业管理员)
    - role_level=3 (承包商管理员)
    """
    if user.role_level == 0 and user.user_status == 1:
        return user  # 系统管理员
    
    if user.role_level == 1:
        if not user.enterprise_staff_id:
            raise HTTPException(status_code=403, detail="企业管理员未绑定企业")
        return user  # 企业管理员
    
    if user.role_level == 3:
        if not user.contractor_staff_id:
            raise HTTPException(status_code=403, detail="承包商管理员未绑定承包商")
        return user  # 承包商管理员
    
    raise HTTPException(status_code=403, detail="无权访问此资源")


@router.get("/")
async def get_enterprises(
    business_status: Optional[str] = Query(default=None, description="状态筛选: 待审核, 续存, 审核不通过, 已注销"),
    company_type: Optional[str] = Query(default=None, description="公司类型筛选"),
    keyword: Optional[str] = Query(default=None, description="搜索关键词（公司名称）"),
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
    user: User = Depends(verify_enterprise_or_admin_access),
    engine = Depends(get_engine)
) -> dict:
    """
    获取企业列表
    
    根据用户权限级别过滤：
    - 系统管理员(role_level=0): 可以查看所有企业
    - 企业管理员(role_level=1): 只能查看自己的企业
    - 承包商管理员(role_level=3): 只能查看与自己承包商有合作关系的企业
    """
    try:
        from routes.dependencies import get_user_accessible_enterprise_ids
        
        # 获取用户可访问的企业ID列表
        accessible_enterprise_ids = await get_user_accessible_enterprise_ids(user, engine)
        
        async with get_session(engine) as session:
            # 构建筛选条件
            conditions = [EnterpriseDB.is_deleted == False]
            
            # 根据权限过滤企业ID
            if accessible_enterprise_ids is not None:  # None 表示可以访问所有
                if accessible_enterprise_ids:
                    conditions.append(EnterpriseDB.enterprise_id.in_(accessible_enterprise_ids))
                else:
                    # 如果没有可访问的企业，返回空列表
                    return {
                        "items": [],
                        "total": 0,
                        "page": page,
                        "page_size": page_size,
                        "total_pages": 0
                    }
            
            if business_status:
                conditions.append(EnterpriseDB.business_status == business_status)
            if company_type:
                conditions.append(EnterpriseDB.company_type == company_type)
            if keyword:
                conditions.append(EnterpriseDB.company_name.contains(keyword))
            
            # 计算总数
            from sqlalchemy import func
            count_query = select(func.count(EnterpriseDB.enterprise_id)).where(and_(*conditions))
            count_result = await session.exec(count_query)
            total = count_result.one()
            
            # 分页查询
            query = select(EnterpriseDB).where(and_(*conditions))
            query = query.order_by(EnterpriseDB.created_at.desc())
            query = query.offset((page - 1) * page_size).limit(page_size)
            result = await session.exec(query)
            enterprises = result.all()
            
            # 转换为响应格式
            items = []
            for enterprise in enterprises:
                # 处理 Row 对象
                if hasattr(enterprise, '__getitem__') and not isinstance(enterprise, EnterpriseDB):
                    enterprise = enterprise[0] if len(enterprise) > 0 else None
                    if enterprise is None:
                        continue
                
                # 查询企业管理员（user_type='enterprise' 且 role_level=1 或 0）
                # 兼容旧数据：role_level=0 也视为企业管理员
                from db.models import User as UserDB
                from sqlmodel import or_
                admin_query = select(UserDB).where(
                    and_(
                        UserDB.enterprise_staff_id == enterprise.enterprise_id,
                        UserDB.user_type == "enterprise",
                        or_(UserDB.role_level == 1, UserDB.role_level == 0)
                    )
                )
                admin_result = await session.exec(admin_query)
                admins = admin_result.all()
                
                # 处理管理员数据
                admin_list = []
                for admin in admins:
                    # 处理 Row 对象
                    if hasattr(admin, '__getitem__') and not isinstance(admin, UserDB):
                        admin = admin[0] if len(admin) > 0 else None
                        if admin is None:
                            continue
                    
                    admin_list.append({
                        "user_id": admin.user_id,
                        "username": admin.username,
                        "name": admin.name_str or admin.relay_name or admin.username,
                        "phone": admin.phone,
                        "email": admin.email,
                        "user_status": admin.user_status,
                    })
                
                items.append({
                    "enterprise_id": enterprise.enterprise_id,
                    "license_file": enterprise.license_file,
                    "license_number": enterprise.license_number,
                    "company_name": enterprise.company_name,
                    "company_type": enterprise.company_type,
                    "company_address": enterprise.company_address,
                    "legal_person": enterprise.legal_person,
                    "establish_date": str(enterprise.establish_date) if enterprise.establish_date else None,
                    "registered_capital": float(enterprise.registered_capital) if enterprise.registered_capital else None,
                    "applicant_name": enterprise.applicant_name,
                    "business_status": enterprise.business_status,
                    "parent_enterprise_id": enterprise.parent_enterprise_id,
                    "created_at": enterprise.created_at.isoformat() if enterprise.created_at else None,
                    "updated_at": enterprise.updated_at.isoformat() if enterprise.updated_at else None,
                    "admins": admin_list,  # 添加管理员列表
                })
            
            return {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取企业列表失败: {str(e)}")


@router.get("/{enterprise_id}/")
async def get_enterprise(
    enterprise_id: int,
    user: User = Depends(verify_admin),
    engine = Depends(get_engine)
) -> EnterpriseInfo:
    """
    获取企业详情
    
    系统管理员可以查看单个企业的详细信息
    """
    try:
        async with get_session(engine) as session:
            query = select(EnterpriseDB).where(
                and_(
                    EnterpriseDB.enterprise_id == enterprise_id,
                    EnterpriseDB.is_deleted == False
                )
            )
            result = await session.exec(query)
            enterprise = result.first()
            
            if not enterprise:
                raise HTTPException(status_code=404, detail="企业不存在")
            
            # 处理 Row 对象
            if hasattr(enterprise, '__getitem__') and not isinstance(enterprise, EnterpriseDB):
                enterprise = enterprise[0] if len(enterprise) > 0 else None
                if enterprise is None:
                    raise HTTPException(status_code=404, detail="企业不存在")
            
            return EnterpriseInfo(
                enterprise_id=enterprise.enterprise_id,
                license_file=enterprise.license_file,
                license_number=enterprise.license_number,
                company_name=enterprise.company_name,
                company_type=enterprise.company_type,
                company_address=enterprise.company_address,
                legal_person=enterprise.legal_person,
                establish_date=str(enterprise.establish_date) if enterprise.establish_date else None,
                registered_capital=float(enterprise.registered_capital) if enterprise.registered_capital else None,
                applicant_name=enterprise.applicant_name,
                business_status=enterprise.business_status,
                is_deleted=enterprise.is_deleted,
                parent_enterprise_id=enterprise.parent_enterprise_id,
                subsidiary_ids=enterprise.subsidiary_ids if hasattr(enterprise, 'subsidiary_ids') else [],
                allowed_contractor_ids=enterprise.allowed_contractor_ids if hasattr(enterprise, 'allowed_contractor_ids') else [],
                modification_log=enterprise.modification_log if hasattr(enterprise, 'modification_log') else [],
                created_at=enterprise.created_at.isoformat() if enterprise.created_at else None,
                updated_at=enterprise.updated_at.isoformat() if enterprise.updated_at else None,
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取企业详情失败: {str(e)}")


@router.post("/{enterprise_id}/approve/", dependencies=[Depends(verify_admin)])
async def approve_enterprise(
    enterprise_id: int,
    approved: bool = Query(description="true=批准, false=拒绝"),
    comment: Optional[str] = Query(default=None, description="审批意见"),
    admin_approvals: Optional[str] = Query(default=None, description="管理员审批状态JSON，格式：{\"user_id\": true/false}"),
    user: User = Depends(verify_admin),
    engine = Depends(get_engine)
):
    """
    审批企业注册
    
    系统管理员审批企业的注册申请
    审核通过：business_status 从"待审核"改为"续存"
    审核拒绝：business_status 从"待审核"改为"审核不通过"
    """
    try:
        async with get_session(engine) as session:
            # 查询企业
            query = select(EnterpriseDB).where(
                and_(
                    EnterpriseDB.enterprise_id == enterprise_id,
                    EnterpriseDB.is_deleted == False
                )
            )
            result = await session.exec(query)
            enterprise = result.first()
            
            if not enterprise:
                raise HTTPException(status_code=404, detail="企业不存在")
            
            # 处理 Row 对象
            if hasattr(enterprise, '__getitem__') and not isinstance(enterprise, EnterpriseDB):
                enterprise = enterprise[0] if len(enterprise) > 0 else None
                if enterprise is None:
                    raise HTTPException(status_code=404, detail="企业不存在")
            
            # 检查当前状态
            if enterprise.business_status != "待审核":
                raise HTTPException(
                    status_code=400, 
                    detail=f"企业当前状态为'{enterprise.business_status}'，无法进行审批操作"
                )
            
            # 更新管理员状态
            from db.models import User as UserDB
            from sqlmodel import or_
            # 查询所有企业管理员（兼容旧数据）
            admin_query = select(UserDB).where(
                and_(
                    UserDB.enterprise_staff_id == enterprise.enterprise_id,
                    UserDB.user_type == "enterprise",
                    or_(UserDB.role_level == 1, UserDB.role_level == 0)
                )
            )
            admin_result = await session.exec(admin_query)
            admins = admin_result.all()
            
            # 解析管理员审批状态
            admin_approval_dict = {}
            if admin_approvals:
                try:
                    admin_approval_dict = json.loads(admin_approvals)
                except:
                    pass
            
            # 如果是审核通过，验证至少有一个管理员被选择为"审核通过"
            if approved:
                if not admins or len(admins) == 0:
                    raise HTTPException(
                        status_code=400,
                        detail="审核失败：该企业没有管理员信息，无法审核通过"
                    )
                
                # 检查是否有至少一个管理员被选择为"审核通过"
                has_approved_admin = False
                for admin in admins:
                    # 处理 Row 对象
                    admin_obj = admin
                    if hasattr(admin, '__getitem__') and not isinstance(admin, UserDB):
                        admin_obj = admin[0] if len(admin) > 0 else None
                        if admin_obj is None:
                            continue
                    
                    # 检查管理员是否被选择为通过
                    if str(admin_obj.user_id) in admin_approval_dict:
                        if admin_approval_dict[str(admin_obj.user_id)]:
                            has_approved_admin = True
                            break
                    else:
                        # 默认通过，也算作已选择通过
                        has_approved_admin = True
                        break
                
                if not has_approved_admin:
                    raise HTTPException(
                        status_code=400,
                        detail="审核失败：必须至少选择一个管理员为'审核通过'状态才能通过该企业的审核"
                    )
            
            # 更新企业状态
            if approved:
                enterprise.business_status = "续存"
                status_text = "批准"
            else:
                enterprise.business_status = "审核不通过"
                status_text = "拒绝"
            
            # 更新修改日志
            if hasattr(enterprise, 'modification_log'):
                modification_log = enterprise.modification_log if enterprise.modification_log else []
                modification_log.append({
                    "action": "审批",
                    "operator": user.username,
                    "operator_type": "系统管理员",
                    "old_status": "待审核",
                    "new_status": enterprise.business_status,
                    "comment": comment,
                    "timestamp": datetime.now().isoformat()
                })
                enterprise.modification_log = modification_log
            
            enterprise.updated_at = datetime.now()
            session.add(enterprise)
            
            # 更新每个管理员的状态
            for admin in admins:
                # 处理 Row 对象
                if hasattr(admin, '__getitem__') and not isinstance(admin, UserDB):
                    admin = admin[0] if len(admin) > 0 else None
                    if admin is None:
                        continue
                
                if approved:
                    # 审核通过：根据选择项更新状态
                    # admin_approval_dict中为true的设置为1（通过审核），否则保持原状或设置为0
                    if str(admin.user_id) in admin_approval_dict:
                        if admin_approval_dict[str(admin.user_id)]:
                            admin.user_status = 1  # 通过审核
                        else:
                            admin.user_status = 0  # 未通过审核
                    else:
                        # 默认通过
                        admin.user_status = 1
                else:
                    # 审核拒绝：所有管理员状态改为3（审核不通过）
                    admin.user_status = 3
                
                admin.updated_at = datetime.now()
                session.add(admin)
            
            await session.commit()
            await session.refresh(enterprise)
            
            return {
                "message": f"企业注册已{status_text}",
                "enterprise_id": enterprise.enterprise_id,
                "business_status": enterprise.business_status,
                "comment": comment
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"审批企业失败: {str(e)}")
