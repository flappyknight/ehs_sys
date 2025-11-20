"""
企业供应商审批路由
Enterprise contractor approval routes
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import select, and_
from pydantic import BaseModel

from api.model import User
from routes.dependencies import get_current_user, get_engine
from db.models import EnterpriseInfo as EnterpriseDB, ContractorInfo as ContractorDB
from db.connection import get_session

router = APIRouter()


class ApproveRequest(BaseModel):
    """审批请求"""
    approved: bool


class ContractorDetailInfo(BaseModel):
    """承包商详细信息"""
    start_time: str
    end_time: str
    company_name: str
    license_number: Optional[str]


class ContractorApprovalItem(BaseModel):
    """承包商审批项"""
    contractor_id: int
    company_name: str
    license_number: Optional[str]
    company_type: Optional[str]
    company_address: Optional[str]
    legal_person: Optional[str]
    establish_date: Optional[str]
    registered_capital: Optional[float]
    business_status: str
    status: str  # "approved" 或 "pending"
    detail_info: Optional[ContractorDetailInfo] = None


def verify_enterprise_admin_or_system_admin(user: User = Depends(get_current_user)):
    """验证企业管理员或系统管理员权限"""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未认证"
        )
    
    # 检查是否被删除
    if hasattr(user, 'is_deleted') and user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账号已被删除"
        )
    
    # 系统管理员：role_level=0, user_status=1, is_deleted=false
    if user.role_level == 0:
        if user.user_status is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="系统管理员账号状态未设置（user_status 为 None），请联系管理员设置账号状态为 1（通过审核）"
            )
        elif user.user_status == 1:
            return user
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"系统管理员账号未通过审核（当前状态: {user.user_status}，需要状态: 1）"
            )
    
    # 企业管理员：role_level=1, user_status=1, is_deleted=false
    if user.role_level == 1:
        if user.user_status is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="企业管理员账号状态未设置（user_status 为 None），请联系管理员设置账号状态为 1（通过审核）"
            )
        elif user.user_status != 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"企业管理员账号未通过审核（当前状态: {user.user_status}，需要状态: 1）"
            )
        if not user.enterprise_staff_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="企业管理员未绑定企业"
            )
        return user
    
    # 其他情况
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"只有企业管理员（role_level=1, user_status=1）或系统管理员（role_level=0, user_status=1）可以访问此功能。当前用户：role_level={user.role_level}, user_status={user.user_status}, is_deleted={getattr(user, 'is_deleted', False)}"
    )


@router.get("/contractors")
async def get_contractors_for_approval(
    engine: AsyncEngine = Depends(get_engine),
    current_user: User = Depends(verify_enterprise_admin_or_system_admin)
) -> List[ContractorApprovalItem]:
    """
    获取企业相关的承包商列表（已审核通过和待审核）
    
    返回当前企业相关的承包商：
    - 已审核通过的承包商（从allowed_contractor_ids获取）
    - 待审核的承包商（从candidate_contractor_ids获取）
    """
    try:
        # 获取企业ID
        if current_user.role_level == 0:
            # 系统管理员，需要从查询参数或其他方式获取企业ID
            # 这里暂时不支持系统管理员查看所有企业的承包商
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="系统管理员需要指定企业ID"
            )
        
        enterprise_id = current_user.enterprise_staff_id
        
        async with get_session(engine) as session:
            # 查询企业信息
            enterprise_query = select(EnterpriseDB).where(
                and_(
                    EnterpriseDB.enterprise_id == enterprise_id,
                    EnterpriseDB.is_deleted == False
                )
            )
            enterprise_result = await session.exec(enterprise_query)
            enterprise = enterprise_result.first()
            
            if not enterprise:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="企业不存在"
                )
            
            # 处理 Row 对象
            if hasattr(enterprise, '__getitem__') and not isinstance(enterprise, EnterpriseDB):
                enterprise = enterprise[0] if len(enterprise) > 0 else None
                if not enterprise:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="企业不存在"
                    )
            
            # 获取已审核通过的承包商ID列表
            allowed_contractor_ids = enterprise.allowed_contractor_ids or []
            # 获取待审核的承包商ID列表
            candidate_contractor_ids = enterprise.candidate_contractor_ids or []
            # 获取承包商详细信息
            contractor_detail_info = enterprise.contractor_detail_info or {}
            
            # 合并所有需要查询的承包商ID
            all_contractor_ids = list(set(allowed_contractor_ids + candidate_contractor_ids))
            
            if not all_contractor_ids:
                return []
            
            # 查询承包商信息
            contractor_query = select(ContractorDB).where(
                and_(
                    ContractorDB.contractor_id.in_(all_contractor_ids),
                    ContractorDB.is_deleted == False
                )
            )
            contractor_result = await session.exec(contractor_query)
            contractors = contractor_result.all()
            
            # 构建响应数据
            items = []
            for contractor in contractors:
                # 处理 Row 对象
                if hasattr(contractor, '__getitem__') and not isinstance(contractor, ContractorDB):
                    contractor = contractor[0] if len(contractor) > 0 else None
                    if not contractor:
                        continue
                
                contractor_id = contractor.contractor_id
                
                # 判断状态
                if contractor_id in allowed_contractor_ids:
                    status = "approved"
                elif contractor_id in candidate_contractor_ids:
                    status = "pending"
                else:
                    continue
                
                # 获取详细信息
                detail_info = None
                detail_dict = contractor_detail_info.get(str(contractor_id))
                if detail_dict:
                    detail_info = ContractorDetailInfo(
                        start_time=detail_dict.get("start_time", ""),
                        end_time=detail_dict.get("end_time", ""),
                        company_name=detail_dict.get("company_name", contractor.company_name),
                        license_number=detail_dict.get("license_number", contractor.license_number)
                    )
                
                items.append(ContractorApprovalItem(
                    contractor_id=contractor_id,
                    company_name=contractor.company_name,
                    license_number=contractor.license_number,
                    company_type=contractor.company_type,
                    company_address=contractor.company_address,
                    legal_person=contractor.legal_person,
                    establish_date=str(contractor.establish_date) if contractor.establish_date else None,
                    registered_capital=float(contractor.registered_capital) if contractor.registered_capital else None,
                    business_status=contractor.business_status,
                    status=status,
                    detail_info=detail_info
                ))
            
            return items
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取承包商列表失败: {str(e)}"
        )


@router.post("/contractors/{contractor_id}/approve")
async def approve_contractor(
    contractor_id: int,
    request: ApproveRequest = Body(...),
    engine: AsyncEngine = Depends(get_engine),
    current_user: User = Depends(verify_enterprise_admin_or_system_admin)
):
    """
    审批承包商合作申请
    
    approved=True: 通过审核
    approved=False: 拒绝申请
    """
    approved = request.approved
    try:
        if current_user.role_level == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="系统管理员需要指定企业ID"
            )
        
        enterprise_id = current_user.enterprise_staff_id
        
        async with get_session(engine) as session:
            # 查询企业信息
            enterprise_query = select(EnterpriseDB).where(
                and_(
                    EnterpriseDB.enterprise_id == enterprise_id,
                    EnterpriseDB.is_deleted == False
                )
            )
            enterprise_result = await session.exec(enterprise_query)
            enterprise = enterprise_result.first()
            
            if not enterprise:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="企业不存在"
                )
            
            # 处理 Row 对象
            if hasattr(enterprise, '__getitem__') and not isinstance(enterprise, EnterpriseDB):
                enterprise = enterprise[0] if len(enterprise) > 0 else None
                if not enterprise:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="企业不存在"
                    )
            
            # 检查承包商是否在待审核列表中
            candidate_contractor_ids = enterprise.candidate_contractor_ids or []
            if contractor_id not in candidate_contractor_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="该承包商不在待审核列表中"
                )
            
            if approved:
                # 通过审核
                # 1. 从candidate_contractor_ids删除（使用新列表确保SQLAlchemy检测到变化）
                candidate_contractor_ids = list(enterprise.candidate_contractor_ids) if enterprise.candidate_contractor_ids else []
                if contractor_id in candidate_contractor_ids:
                    candidate_contractor_ids.remove(contractor_id)
                    enterprise.candidate_contractor_ids = candidate_contractor_ids
                
                # 2. 追加到allowed_contractor_ids（去重）
                allowed_contractor_ids = list(enterprise.allowed_contractor_ids) if enterprise.allowed_contractor_ids else []
                if contractor_id not in allowed_contractor_ids:
                    allowed_contractor_ids.append(contractor_id)
                    enterprise.allowed_contractor_ids = allowed_contractor_ids
                
                # 3. 更新contractor_info表
                contractor_query = select(ContractorDB).where(
                    and_(
                        ContractorDB.contractor_id == contractor_id,
                        ContractorDB.is_deleted == False
                    )
                )
                contractor_result = await session.exec(contractor_query)
                contractor = contractor_result.first()
                
                if not contractor:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="承包商不存在"
                    )
                
                # 处理 Row 对象
                if hasattr(contractor, '__getitem__') and not isinstance(contractor, ContractorDB):
                    contractor = contractor[0] if len(contractor) > 0 else None
                    if not contractor:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail="承包商不存在"
                        )
                
                # 从pending_allowed_ids删除企业ID
                pending_allowed_ids = list(contractor.pending_allowed_ids) if contractor.pending_allowed_ids else []
                if enterprise_id in pending_allowed_ids:
                    pending_allowed_ids.remove(enterprise_id)
                    contractor.pending_allowed_ids = pending_allowed_ids
                
                # 追加到active_enterprise_ids
                active_enterprise_ids = list(contractor.active_enterprise_ids) if contractor.active_enterprise_ids else []
                if enterprise_id not in active_enterprise_ids:
                    active_enterprise_ids.append(enterprise_id)
                    contractor.active_enterprise_ids = active_enterprise_ids
                
                session.add(contractor)
                await session.flush()
            else:
                # 拒绝申请
                # 1. 从candidate_contractor_ids删除（使用新列表确保SQLAlchemy检测到变化）
                candidate_contractor_ids = list(enterprise.candidate_contractor_ids) if enterprise.candidate_contractor_ids else []
                if contractor_id in candidate_contractor_ids:
                    candidate_contractor_ids.remove(contractor_id)
                    enterprise.candidate_contractor_ids = candidate_contractor_ids
                
                # 2. 从contractor_detail_info删除该承包商信息（使用新字典确保SQLAlchemy检测到变化）
                contractor_detail_info = dict(enterprise.contractor_detail_info) if enterprise.contractor_detail_info else {}
                if str(contractor_id) in contractor_detail_info:
                    del contractor_detail_info[str(contractor_id)]
                    enterprise.contractor_detail_info = contractor_detail_info
                
                # 3. 更新contractor_info表
                contractor_query = select(ContractorDB).where(
                    and_(
                        ContractorDB.contractor_id == contractor_id,
                        ContractorDB.is_deleted == False
                    )
                )
                contractor_result = await session.exec(contractor_query)
                contractor = contractor_result.first()
                
                if contractor:
                    # 处理 Row 对象
                    if hasattr(contractor, '__getitem__') and not isinstance(contractor, ContractorDB):
                        contractor = contractor[0] if len(contractor) > 0 else None
                    
                    if contractor:
                        # 从pending_allowed_ids删除企业ID（使用新列表确保SQLAlchemy检测到变化）
                        pending_allowed_ids = list(contractor.pending_allowed_ids) if contractor.pending_allowed_ids else []
                        if enterprise_id in pending_allowed_ids:
                            pending_allowed_ids.remove(enterprise_id)
                            contractor.pending_allowed_ids = pending_allowed_ids
                        
                        # 从active_enterprise_detail删除企业信息（使用新字典确保SQLAlchemy检测到变化）
                        active_enterprise_detail = dict(contractor.active_enterprise_detail) if contractor.active_enterprise_detail else {}
                        if str(enterprise_id) in active_enterprise_detail:
                            del active_enterprise_detail[str(enterprise_id)]
                            contractor.active_enterprise_detail = active_enterprise_detail
                        
                        session.add(contractor)
                        await session.flush()
            
            # 保存企业信息（确保所有变更被保存，两个分支都需要）
            session.add(enterprise)
            await session.flush()
            
            # 提交事务
            await session.commit()
            
            return {
                "message": "审批操作成功" if approved else "拒绝申请成功",
                "contractor_id": contractor_id,
                "approved": approved
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"审批操作失败: {str(e)}"
        )


@router.delete("/contractors/{contractor_id}")
async def remove_contractor(
    contractor_id: int,
    engine: AsyncEngine = Depends(get_engine),
    current_user: User = Depends(verify_enterprise_admin_or_system_admin)
):
    """
    移除已审核通过的承包商
    """
    try:
        if current_user.role_level == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="系统管理员需要指定企业ID"
            )
        
        enterprise_id = current_user.enterprise_staff_id
        
        async with get_session(engine) as session:
            # 查询企业信息
            enterprise_query = select(EnterpriseDB).where(
                and_(
                    EnterpriseDB.enterprise_id == enterprise_id,
                    EnterpriseDB.is_deleted == False
                )
            )
            enterprise_result = await session.exec(enterprise_query)
            enterprise = enterprise_result.first()
            
            if not enterprise:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="企业不存在"
                )
            
            # 处理 Row 对象
            if hasattr(enterprise, '__getitem__') and not isinstance(enterprise, EnterpriseDB):
                enterprise = enterprise[0] if len(enterprise) > 0 else None
                if not enterprise:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="企业不存在"
                    )
            
            # 检查承包商是否在已审核通过列表中或待审核列表中
            allowed_contractor_ids = list(enterprise.allowed_contractor_ids) if enterprise.allowed_contractor_ids else []
            candidate_contractor_ids = list(enterprise.candidate_contractor_ids) if enterprise.candidate_contractor_ids else []
            
            if contractor_id not in allowed_contractor_ids and contractor_id not in candidate_contractor_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="该承包商不在已审核通过列表或待审核列表中"
                )
            
            # 1. 从allowed_contractor_ids删除（如果存在）
            if contractor_id in allowed_contractor_ids:
                allowed_contractor_ids.remove(contractor_id)
                enterprise.allowed_contractor_ids = allowed_contractor_ids
            
            # 2. 从candidate_contractor_ids删除（如果存在）
            if contractor_id in candidate_contractor_ids:
                candidate_contractor_ids.remove(contractor_id)
                enterprise.candidate_contractor_ids = candidate_contractor_ids
            
            # 3. 从contractor_detail_info删除该承包商信息
            contractor_detail_info = dict(enterprise.contractor_detail_info) if enterprise.contractor_detail_info else {}
            if str(contractor_id) in contractor_detail_info:
                del contractor_detail_info[str(contractor_id)]
                enterprise.contractor_detail_info = contractor_detail_info
            
            # 3. 更新contractor_info表
            contractor_query = select(ContractorDB).where(
                and_(
                    ContractorDB.contractor_id == contractor_id,
                    ContractorDB.is_deleted == False
                )
            )
            contractor_result = await session.exec(contractor_query)
            contractor = contractor_result.first()
            
            if contractor:
                # 处理 Row 对象
                if hasattr(contractor, '__getitem__') and not isinstance(contractor, ContractorDB):
                    contractor = contractor[0] if len(contractor) > 0 else None
                
                if contractor:
                    # 从active_enterprise_ids删除企业ID（使用新列表确保SQLAlchemy检测到变化）
                    active_enterprise_ids = list(contractor.active_enterprise_ids) if contractor.active_enterprise_ids else []
                    if enterprise_id in active_enterprise_ids:
                        active_enterprise_ids.remove(enterprise_id)
                        contractor.active_enterprise_ids = active_enterprise_ids
                    
                    # 从active_enterprise_detail删除企业信息（使用新字典确保SQLAlchemy检测到变化）
                    active_enterprise_detail = dict(contractor.active_enterprise_detail) if contractor.active_enterprise_detail else {}
                    if str(enterprise_id) in active_enterprise_detail:
                        del active_enterprise_detail[str(enterprise_id)]
                        contractor.active_enterprise_detail = active_enterprise_detail
                    
                    session.add(contractor)
                    await session.flush()
            
            # 保存企业信息和承包商信息
            session.add(enterprise)
            if contractor:
                session.add(contractor)
            await session.flush()
            await session.commit()
            
            return {
                "message": "移除承包商成功",
                "contractor_id": contractor_id
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"移除承包商失败: {str(e)}"
        )

