"""
承包商管理路由 (系统管理员)
Contractor management routes for system admin
"""
from typing import List, Optional
from datetime import datetime
import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from api.model import (
    ContractorListItem,
    User,
    UserType,
    ContractorUser,
    ContractorInfo
)
from core import password as pwd
from db import crud
from db.models import ContractorInfo as ContractorDB, ContractorUser as ContractorUserDB
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


def verify_contractor_or_admin_access(user: User = Depends(get_current_user)):
    """
    验证企业管理员或系统管理员权限（用于承包商管理）
    
    允许访问的用户：
    - role_level=0 且 user_status=1 (系统管理员)
    - role_level=1 (企业管理员)
    """
    if user.role_level == 0 and user.user_status == 1:
        return user  # 系统管理员
    
    if user.role_level == 1:
        if not user.enterprise_staff_id:
            raise HTTPException(status_code=403, detail="企业管理员未绑定企业")
        return user  # 企业管理员
    
    raise HTTPException(status_code=403, detail="无权访问此资源")


@router.post("/", dependencies=[Depends(verify_admin)])
async def create_contractor(contractor: ContractorInfo):
    """
    创建承包商
    
    系统管理员创建新承包商，承包商初始状态为待审批
    """
    from main import app
    
    try:
        contractor_db = await crud.create_contractor_info(app.state.engine, contractor)
        return {
            "message": "承包商创建成功",
            "contractor_id": contractor_db.contractor_id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"创建承包商失败: {str(e)}")


@router.get("/")
async def get_contractors(
    business_status: Optional[str] = Query(default=None, description="状态筛选: 待审核, 续存, 审核不通过, 已注销"),
    company_type: Optional[str] = Query(default=None, description="公司类型筛选"),
    keyword: Optional[str] = Query(default=None, description="搜索关键词（公司名称）"),
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
    user: User = Depends(verify_contractor_or_admin_access),
    engine = Depends(get_engine)
) -> dict:
    """
    获取承包商列表
    
    根据用户权限级别过滤：
    - 系统管理员(role_level=0): 可以查看所有承包商
    - 企业管理员(role_level=1): 只能查看企业 allowed_contractor_ids 中的承包商
    """
    try:
        from routes.dependencies import get_user_accessible_contractor_ids
        
        # 获取用户可访问的承包商ID列表
        accessible_contractor_ids = await get_user_accessible_contractor_ids(user, engine)
        
        async with get_session(engine) as session:
            # 构建筛选条件
            conditions = [ContractorDB.is_deleted == False]
            
            # 根据权限过滤承包商ID
            if accessible_contractor_ids is not None:  # None 表示可以访问所有
                if accessible_contractor_ids:
                    conditions.append(ContractorDB.contractor_id.in_(accessible_contractor_ids))
                else:
                    # 如果没有可访问的承包商，返回空列表
                    return {
                        "items": [],
                        "total": 0,
                        "page": page,
                        "page_size": page_size,
                        "total_pages": 0
                    }
            
            if business_status:
                conditions.append(ContractorDB.business_status == business_status)
            if company_type:
                conditions.append(ContractorDB.company_type == company_type)
            if keyword:
                conditions.append(ContractorDB.company_name.contains(keyword))
            
            # 计算总数
            from sqlalchemy import func
            count_query = select(func.count(ContractorDB.contractor_id)).where(and_(*conditions))
            count_result = await session.exec(count_query)
            total = count_result.one()
            
            # 分页查询
            query = select(ContractorDB).where(and_(*conditions))
            query = query.order_by(ContractorDB.created_at.desc())
            query = query.offset((page - 1) * page_size).limit(page_size)
            result = await session.exec(query)
            contractors = result.all()
            
            # 转换为响应格式
            items = []
            for contractor in contractors:
                # 处理 Row 对象
                if hasattr(contractor, '__getitem__') and not isinstance(contractor, ContractorDB):
                    contractor = contractor[0] if len(contractor) > 0 else None
                    if contractor is None:
                        continue
                
                # 查询供应商管理员（user_type='contractor' 且 role_level=3 或 0）
                # 兼容旧数据：role_level=0 也视为供应商管理员
                from db.models import User as UserDB
                from sqlmodel import or_
                admin_query = select(UserDB).where(
                    and_(
                        UserDB.contractor_staff_id == contractor.contractor_id,
                        UserDB.user_type == "contractor",
                        or_(UserDB.role_level == 3, UserDB.role_level == 0)
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
                    "contractor_id": contractor.contractor_id,
                    "license_file": contractor.license_file,
                    "license_number": contractor.license_number,
                    "company_name": contractor.company_name,
                    "company_type": contractor.company_type,
                    "company_address": contractor.company_address,
                    "legal_person": contractor.legal_person,
                    "establish_date": str(contractor.establish_date) if contractor.establish_date else None,
                    "registered_capital": float(contractor.registered_capital) if contractor.registered_capital else None,
                    "applicant_name": contractor.applicant_name,
                    "business_status": contractor.business_status,
                    "created_at": contractor.created_at.isoformat() if contractor.created_at else None,
                    "updated_at": contractor.updated_at.isoformat() if contractor.updated_at else None,
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
        raise HTTPException(status_code=400, detail=f"获取承包商列表失败: {str(e)}")


@router.get("/{contractor_id}/")
async def get_contractor_detail(
    contractor_id: int,
    user: User = Depends(verify_admin),
    engine = Depends(get_engine)
) -> ContractorInfo:
    """
    获取承包商详情
    
    系统管理员可以查看单个承包商的详细信息
    """
    try:
        async with get_session(engine) as session:
            query = select(ContractorDB).where(
                and_(
                    ContractorDB.contractor_id == contractor_id,
                    ContractorDB.is_deleted == False
                )
            )
            result = await session.exec(query)
            contractor = result.first()
            
            if not contractor:
                raise HTTPException(status_code=404, detail="承包商不存在")
            
            # 处理 Row 对象
            if hasattr(contractor, '__getitem__') and not isinstance(contractor, ContractorDB):
                contractor = contractor[0] if len(contractor) > 0 else None
                if contractor is None:
                    raise HTTPException(status_code=404, detail="承包商不存在")
            
            return ContractorInfo(
                contractor_id=contractor.contractor_id,
                license_file=contractor.license_file,
                license_number=contractor.license_number,
                company_name=contractor.company_name,
                company_type=contractor.company_type,
                company_address=contractor.company_address,
                legal_person=contractor.legal_person,
                establish_date=str(contractor.establish_date) if contractor.establish_date else None,
                registered_capital=float(contractor.registered_capital) if contractor.registered_capital else None,
                applicant_name=contractor.applicant_name,
                business_status=contractor.business_status,
                is_deleted=contractor.is_deleted,
                active_enterprise_ids=contractor.active_enterprise_ids if hasattr(contractor, 'active_enterprise_ids') else [],
                inactive_enterprise_ids=contractor.inactive_enterprise_ids if hasattr(contractor, 'inactive_enterprise_ids') else [],
                cooperation_detail_log=contractor.cooperation_detail_log if hasattr(contractor, 'cooperation_detail_log') else [],
                modification_log=contractor.modification_log if hasattr(contractor, 'modification_log') else [],
                created_at=contractor.created_at.isoformat() if contractor.created_at else None,
                updated_at=contractor.updated_at.isoformat() if contractor.updated_at else None,
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取承包商详情失败: {str(e)}")


@router.put("/{contractor_id}/", dependencies=[Depends(verify_admin)])
async def update_contractor(contractor_id: int, contractor_data: ContractorInfo):
    """
    更新承包商信息
    
    系统管理员可以修改承包商的基本信息
    """
    from main import app
    
    try:
        async with app.state.engine.begin() as conn:
            # 查询承包商
            query = select(ContractorDB).where(ContractorDB.contractor_id == contractor_id)
            result = await conn.execute(query)
            contractor = result.scalar_one_or_none()
            
            if not contractor:
                raise HTTPException(status_code=404, detail="承包商不存在")
            
            # 更新字段
            update_data = contractor_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                if hasattr(contractor, key) and value is not None:
                    setattr(contractor, key, value)
            
            if hasattr(contractor, 'updated_at'):
                contractor.updated_at = datetime.now()
            
            await conn.commit()
            
            return {"message": "承包商信息更新成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"更新承包商信息失败: {str(e)}")


@router.delete("/{contractor_id}/", dependencies=[Depends(verify_admin)])
async def delete_contractor(contractor_id: int):
    """
    删除承包商
    
    软删除承包商，将状态设置为 deleted
    注意：删除前需要确保承包商下没有活跃的员工和项目
    """
    from main import app
    
    try:
        async with app.state.engine.begin() as conn:
            # 查询承包商
            query = select(ContractorDB).where(ContractorDB.contractor_id == contractor_id)
            result = await conn.execute(query)
            contractor = result.scalar_one_or_none()
            
            if not contractor:
                raise HTTPException(status_code=404, detail="承包商不存在")
            
            # 检查是否有活跃员工
            staff_query = select(ContractorUserDB).where(
                and_(
                    ContractorUserDB.contractor_id == contractor_id,
                    ContractorUserDB.status == True
                )
            )
            staff_result = await conn.execute(staff_query)
            active_staff = staff_result.all()
            
            if active_staff:
                raise HTTPException(
                    status_code=400, 
                    detail=f"无法删除承包商，还有 {len(active_staff)} 个活跃员工"
                )
            
            # 检查是否有进行中的项目
            from db.models import Project
            project_query = select(Project).where(
                and_(
                    Project.contractor_id == contractor_id,
                    Project.status == 'active'
                )
            )
            project_result = await conn.execute(project_query)
            active_projects = project_result.all()
            
            if active_projects:
                raise HTTPException(
                    status_code=400, 
                    detail=f"无法删除承包商，还有 {len(active_projects)} 个进行中的项目"
                )
            
            # 软删除
            if hasattr(contractor, 'status'):
                contractor.status = 'deleted'
            if hasattr(contractor, 'updated_at'):
                contractor.updated_at = datetime.now()
            
            await conn.commit()
            
            return {"message": "承包商删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"删除承包商失败: {str(e)}")


@router.post("/{contractor_id}/approve/", dependencies=[Depends(verify_admin)])
async def approve_contractor(
    contractor_id: int,
    approved: bool = Query(description="true=批准, false=拒绝"),
    comment: Optional[str] = Query(default=None, description="审批意见"),
    admin_approvals: Optional[str] = Query(default=None, description="管理员审批状态JSON，格式：{\"user_id\": true/false}"),
    user: User = Depends(verify_admin),
    engine = Depends(get_engine)
):
    """
    审批承包商注册
    
    系统管理员审批承包商的注册申请
    审核通过：business_status 从"待审核"改为"续存"
    审核拒绝：business_status 从"待审核"改为"审核不通过"
    """
    try:
        async with get_session(engine) as session:
            # 查询承包商
            query = select(ContractorDB).where(
                and_(
                    ContractorDB.contractor_id == contractor_id,
                    ContractorDB.is_deleted == False
                )
            )
            result = await session.exec(query)
            contractor = result.first()
            
            if not contractor:
                raise HTTPException(status_code=404, detail="承包商不存在")
            
            # 处理 Row 对象
            if hasattr(contractor, '__getitem__') and not isinstance(contractor, ContractorDB):
                contractor = contractor[0] if len(contractor) > 0 else None
                if contractor is None:
                    raise HTTPException(status_code=404, detail="承包商不存在")
            
            # 检查当前状态
            if contractor.business_status != "待审核":
                raise HTTPException(
                    status_code=400, 
                    detail=f"承包商当前状态为'{contractor.business_status}'，无法进行审批操作"
                )
            
            # 更新管理员状态
            from db.models import User as UserDB
            from sqlmodel import or_
            # 查询所有供应商管理员（兼容旧数据）
            admin_query = select(UserDB).where(
                and_(
                    UserDB.contractor_staff_id == contractor.contractor_id,
                    UserDB.user_type == "contractor",
                    or_(UserDB.role_level == 3, UserDB.role_level == 0)
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
                        detail="审核失败：该供应商没有管理员信息，无法审核通过"
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
                        detail="审核失败：必须至少选择一个管理员为'审核通过'状态才能通过该供应商的审核"
                    )
            
            # 更新供应商状态
            if approved:
                contractor.business_status = "续存"
                status_text = "批准"
            else:
                contractor.business_status = "审核不通过"
                status_text = "拒绝"
            
            # 更新修改日志
            if hasattr(contractor, 'modification_log'):
                modification_log = contractor.modification_log if contractor.modification_log else []
                modification_log.append({
                    "action": "审批",
                    "operator": user.username,
                    "operator_type": "系统管理员",
                    "old_status": "待审核",
                    "new_status": contractor.business_status,
                    "comment": comment,
                    "timestamp": datetime.now().isoformat()
                })
                contractor.modification_log = modification_log
            
            contractor.updated_at = datetime.now()
            session.add(contractor)
            
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
            await session.refresh(contractor)
            
            return {
                "message": f"承包商注册已{status_text}",
                "contractor_id": contractor.contractor_id,
                "business_status": contractor.business_status,
                "comment": comment
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"审批承包商失败: {str(e)}")


@router.post("/{contractor_id}/admin/", dependencies=[Depends(verify_admin)])
async def create_contractor_admin(
    contractor_id: int,
    admin_data: ContractorUser
):
    """
    为承包商创建超级管理员
    
    系统管理员为新批准的承包商创建第一个管理员账户
    """
    from main import app
    
    try:
        # 验证承包商存在
        async with app.state.engine.begin() as conn:
            query = select(ContractorDB).where(ContractorDB.contractor_id == contractor_id)
            result = await conn.execute(query)
            contractor = result.scalar_one_or_none()
            
            if not contractor:
                raise HTTPException(status_code=404, detail="承包商不存在")
        
        # 设置为管理员角色
        admin_data.contractor_id = contractor_id
        admin_data.role_type = "approver"  # 承包商管理员
        admin_data.status = True
        
        # 创建用户账号
        user = User(
            user_type=UserType.contractor,
            username=admin_data.phone,
            password_hash=pwd.get_password_hash(admin_data.phone[-6:])  # 默认密码为手机号后6位
        )
        
        contractor_user_db = await crud.create_contractor_user(
            app.state.engine, admin_data, user
        )
        
        return {
            "message": "承包商管理员创建成功",
            "user_id": contractor_user_db.user_id,
            "username": admin_data.phone,
            "default_password": admin_data.phone[-6:]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"创建承包商管理员失败: {str(e)}")


@router.get("/{contractor_id}/admins/")
async def get_contractor_admins(
    contractor_id: int,
    user: User = Depends(verify_admin)
) -> List[dict]:
    """
    获取承包商管理员列表
    
    查看指定承包商的所有管理员账户
    """
    from main import app
    
    try:
        async with app.state.engine.begin() as conn:
            # 查询承包商管理员
            query = select(ContractorUserDB).where(
                and_(
                    ContractorUserDB.contractor_id == contractor_id,
                    ContractorUserDB.role_type == "approver"
                )
            )
            result = await conn.execute(query)
            admins = result.scalars().all()
            
            return [
                {
                    "user_id": admin.user_id,
                    "name": admin.name,
                    "phone": admin.phone,
                    "id_number": admin.id_number,
                    "work_type": admin.work_type,
                    "status": admin.status,
                    "created_at": admin.created_at.isoformat() if hasattr(admin, 'created_at') else None
                } for admin in admins
            ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取承包商管理员列表失败: {str(e)}")

