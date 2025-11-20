"""
承包商合作申请处理
Contractor cooperation request handler
"""
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import select, and_
from sqlmodel import select as sql_select
from pydantic import BaseModel

from api.model import User
from routes.dependencies import get_current_user, get_engine
from db.models import EnterpriseInfo as EnterpriseDB, ContractorInfo as ContractorDB, User as UserDB
from db.connection import get_session, SessionCreatError

router = APIRouter()


class EnterpriseListItem(BaseModel):
    """企业列表项"""
    enterprise_id: int
    company_name: str
    license_number: Optional[str]
    legal_person: Optional[str]


class CooperationRequestSubmit(BaseModel):
    """合作申请提交"""
    enterprise_id: int
    start_time: str  # 格式: YYYY-MM-DD
    end_time: str    # 格式: YYYY-MM-DD


@router.get("/enterprises")
async def get_available_enterprises(
    company_name: Optional[str] = Query(default=None, description="企业名称过滤（模糊匹配）"),
    license_number: Optional[str] = Query(default=None, description="营业执照编号过滤（模糊匹配）"),
    engine: AsyncEngine = Depends(get_engine),
    current_user: User = Depends(get_current_user)
) -> List[EnterpriseListItem]:
    """
    获取可申请的企业列表
    
    只返回business_status为"续存"的企业
    支持通过企业名称和营业执照编号进行过滤
    只有承包商管理员(role_level=3, user_status=1)可以调用
    """
    # 验证用户身份：必须是承包商管理员
    if current_user.role_level != 3 or current_user.user_status != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有承包商管理员可以查看可申请的企业列表"
        )
    
    if not current_user.contractor_staff_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前用户未绑定承包商"
        )
    
    try:
        async with get_session(engine) as session:
            # 构建查询条件
            conditions = [
                EnterpriseDB.business_status == "续存",
                EnterpriseDB.is_deleted == False
            ]
            
            # 添加过滤条件
            if company_name:
                conditions.append(EnterpriseDB.company_name.contains(company_name))
            if license_number:
                conditions.append(EnterpriseDB.license_number.contains(license_number))
            
            # 查询business_status为"续存"且未删除的企业
            query = select(EnterpriseDB).where(and_(*conditions))
            result = await session.exec(query)
            enterprises = result.all()
            
            # 转换为响应格式
            items = []
            for enterprise in enterprises:
                # 处理 Row 对象
                if hasattr(enterprise, '__getitem__') and not isinstance(enterprise, EnterpriseDB):
                    enterprise = enterprise[0] if len(enterprise) > 0 else None
                
                if enterprise:
                    items.append(EnterpriseListItem(
                        enterprise_id=enterprise.enterprise_id,
                        company_name=enterprise.company_name,
                        license_number=enterprise.license_number,
                        legal_person=enterprise.legal_person
                    ))
            
            return items
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取企业列表失败: {str(e)}"
        )


@router.post("/submit")
async def submit_cooperation_request(
    request: CooperationRequestSubmit,
    engine: AsyncEngine = Depends(get_engine),
    current_user: User = Depends(get_current_user)
):
    """
    提交合作申请
    
    校验逻辑：
    1. 检查当前企业是否已经与当前承包商处于合作状态（allowed_contractor_ids包含contractor_staff_id）
    2. 检查是否已经提交过申请（candidate_contractor_ids包含contractor_staff_id）
    3. 如果都不包含，则允许提交
    
    提交后操作：
    1. 将contractor_staff_id追加到enterprise_info的candidate_contractor_ids
    2. 将合作信息存到enterprise_info的contractor_detail_info（key为contractor_staff_id）
    3. 将企业id追加到contractor_info的pending_allowed_ids（如果已存在则拒绝）
    4. 将企业信息存到contractor_info的active_enterprise_detail（key为企业id）
    """
    # 验证用户身份：必须是承包商管理员
    if current_user.role_level != 3 or current_user.user_status != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有承包商管理员可以提交合作申请"
        )
    
    if not current_user.contractor_staff_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前用户未绑定承包商"
        )
    
    contractor_staff_id = current_user.contractor_staff_id
    
    try:
        async with get_session(engine) as session:
            # 1. 查询企业信息
            enterprise_query = select(EnterpriseDB).where(
                and_(
                    EnterpriseDB.enterprise_id == request.enterprise_id,
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
            
            # 2. 检查是否已经处于合作状态
            allowed_contractor_ids = enterprise.allowed_contractor_ids or []
            if contractor_staff_id in allowed_contractor_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="当前承包商已与该企业处于合作状态，无法重复申请"
                )
            
            # 3. 检查是否已经提交过申请
            candidate_contractor_ids = enterprise.candidate_contractor_ids or []
            if contractor_staff_id in candidate_contractor_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="当前承包商已提交过申请，正在等待审核中，无法重复提交"
                )
            
            # 4. 查询承包商信息
            contractor_query = select(ContractorDB).where(
                and_(
                    ContractorDB.contractor_id == contractor_staff_id,
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
            
            # 5. 检查contractor_info的pending_allowed_ids是否已包含该企业id
            pending_allowed_ids = contractor.pending_allowed_ids or []
            if request.enterprise_id in pending_allowed_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="已向该企业提交过申请，无法重复提交"
                )
            
            # 6. 更新enterprise_info表
            # 追加contractor_staff_id到candidate_contractor_ids
            if contractor_staff_id not in candidate_contractor_ids:
                candidate_contractor_ids.append(contractor_staff_id)
                enterprise.candidate_contractor_ids = candidate_contractor_ids
            
            # 更新contractor_detail_info
            contractor_detail_info = enterprise.contractor_detail_info or {}
            contractor_detail_info[str(contractor_staff_id)] = {
                "start_time": request.start_time,
                "end_time": request.end_time,
                "company_name": contractor.company_name,
                "license_number": contractor.license_number
            }
            enterprise.contractor_detail_info = contractor_detail_info
            
            # 保存企业信息
            session.add(enterprise)
            await session.flush()
            
            # 7. 更新contractor_info表
            # 追加企业id到pending_allowed_ids
            if request.enterprise_id not in pending_allowed_ids:
                pending_allowed_ids.append(request.enterprise_id)
                contractor.pending_allowed_ids = pending_allowed_ids
            
            # 更新active_enterprise_detail
            active_enterprise_detail = contractor.active_enterprise_detail or {}
            active_enterprise_detail[str(request.enterprise_id)] = {
                "start_time": request.start_time,
                "end_time": request.end_time,
                "company_name": enterprise.company_name,
                "license_number": enterprise.license_number
            }
            contractor.active_enterprise_detail = active_enterprise_detail
            
            # 保存承包商信息
            session.add(contractor)
            await session.flush()
            
            # 在提交前获取需要返回的数据，避免在会话关闭后访问属性
            enterprise_name = enterprise.company_name
            contractor_name = contractor.company_name
            
            # 提交事务
            await session.commit()
            
            return {
                "message": "合作申请提交成功",
                "enterprise_id": request.enterprise_id,
                "enterprise_name": enterprise_name,
                "contractor_id": contractor_staff_id,
                "contractor_name": contractor_name
            }
    except HTTPException:
        raise
    except SessionCreatError as e:
        # SessionCreatError 已经被包装，直接抛出原始错误信息
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交合作申请失败: {e.message if hasattr(e, 'message') else str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交合作申请失败: {str(e)}"
        )

