"""
工单管理路由
Ticket management routes
"""
from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select, and_

from api.model import (
    TicketCreate,
    TicketUpdate,
    TicketListItem,
    TicketDetail,
    User,
    UserType
)
from db.models import Ticket, EnterpriseUser, ContractorUser
from routes.dependencies import get_current_user, authenticate_enterprise_level

router = APIRouter()


@router.post("/", dependencies=[Depends(authenticate_enterprise_level)])
async def create_ticket(ticket_data: TicketCreate, user: User = Depends(get_current_user)):
    """创建工单"""
    from main import app
    
    try:
        # 转换时间字符串为 datetime 对象
        pre_st = datetime.fromisoformat(ticket_data.pre_st.replace('Z', '+00:00'))
        pre_et = datetime.fromisoformat(ticket_data.pre_et.replace('Z', '+00:00'))
        
        # 创建工单
        ticket = Ticket(
            apply_date=ticket_data.apply_date,
            applicant=ticket_data.applicant,
            area_id=ticket_data.area_id,
            working_content=ticket_data.working_content,
            pre_st=pre_st,
            pre_et=pre_et,
            tools=ticket_data.tools,
            worker=ticket_data.worker,
            custodians=ticket_data.custodians,
            danger=ticket_data.danger,
            protection=ticket_data.protection,
            hot_work=ticket_data.hot_work,
            work_height_level=ticket_data.work_height_level,
            confined_space_id=ticket_data.confined_space_id,
            temp_power_id=ticket_data.temp_power_id,
            cross_work_group_id=ticket_data.cross_work_group_id,
            signature=ticket_data.signature
        )
        
        async with app.state.engine.begin() as conn:
            conn.add(ticket)
            await conn.commit()
            await conn.refresh(ticket)
        
        return {
            "message": "工单创建成功",
            "ticket_id": ticket.ticket_id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"创建工单失败: {str(e)}")


@router.get("/")
async def get_tickets(
    area_id: int = Query(default=None, description="按厂区筛选"),
    hot_work: int = Query(default=None, description="按动火等级筛选"),
    start_date: str = Query(default=None, description="开始日期"),
    end_date: str = Query(default=None, description="结束日期"),
    user: User = Depends(get_current_user)
) -> List[TicketListItem]:
    """获取工单列表"""
    from main import app
    
    try:
        async with app.state.engine.begin() as conn:
            # 构建基础查询
            query = select(
                Ticket,
                EnterpriseUser.name.label("applicant_name"),
                Area.area_name,
                ContractorUser.name.label("worker_name")
            ).join(
                EnterpriseUser, Ticket.applicant == EnterpriseUser.user_id
            ).join(
                Area, Ticket.area_id == Area.area_id
            ).join(
                ContractorUser, Ticket.worker == ContractorUser.user_id
            )
            
            # 添加筛选条件
            filters = []
            
            # 企业用户只能看到自己企业的工单
            if user.user_type == UserType.enterprise:
                filters.append(Area.enterprise_id == user.enterprise_user.enterprise_id)
            
            if area_id:
                filters.append(Ticket.area_id == area_id)
            
            if hot_work is not None:
                filters.append(Ticket.hot_work == hot_work)
            
            if start_date:
                filters.append(Ticket.apply_date >= start_date)
            
            if end_date:
                filters.append(Ticket.apply_date <= end_date)
            
            if filters:
                query = query.where(and_(*filters))
            
            # 执行查询
            result = await conn.execute(query)
            rows = result.all()
            
            # 获取监护人信息
            tickets = []
            for row in rows:
                ticket = row[0]
                applicant_name = row[1]
                area_name = row[2]
                worker_name = row[3]
                
                # 获取监护人姓名
                custodian_query = select(EnterpriseUser.name).where(
                    EnterpriseUser.user_id == ticket.custodians
                )
                custodian_result = await conn.execute(custodian_query)
                custodian_name = custodian_result.scalar_one_or_none() or "未知"
                
                ticket_item = TicketListItem(
                    ticket_id=ticket.ticket_id,
                    apply_date=ticket.apply_date,
                    applicant_name=applicant_name,
                    area_name=area_name,
                    working_content=ticket.working_content,
                    pre_st=ticket.pre_st.isoformat(),
                    pre_et=ticket.pre_et.isoformat(),
                    worker_name=worker_name,
                    custodian_name=custodian_name,
                    hot_work=ticket.hot_work,
                    work_height_level=ticket.work_height_level,
                    created_at=ticket.created_at.isoformat()
                )
                tickets.append(ticket_item)
            
            return tickets
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取工单列表失败: {str(e)}")


@router.get("/{ticket_id}/")
async def get_ticket_detail(
    ticket_id: int,
    user: User = Depends(get_current_user)
) -> TicketDetail:
    """获取工单详情"""
    from main import app
    
    try:
        async with app.state.engine.begin() as conn:
            # 查询工单及相关信息
            query = select(
                Ticket,
                EnterpriseUser.name.label("applicant_name"),
                Area.area_name,
                ContractorUser.name.label("worker_name")
            ).join(
                EnterpriseUser, Ticket.applicant == EnterpriseUser.user_id
            ).join(
                Area, Ticket.area_id == Area.area_id
            ).join(
                ContractorUser, Ticket.worker == ContractorUser.user_id
            ).where(
                Ticket.ticket_id == ticket_id
            )
            
            result = await conn.execute(query)
            row = result.first()
            
            if not row:
                raise HTTPException(status_code=404, detail="工单不存在")
            
            ticket = row[0]
            applicant_name = row[1]
            area_name = row[2]
            worker_name = row[3]
            
            # 权限检查：企业用户只能查看自己企业的工单
            if user.user_type == UserType.enterprise:
                area_query = select(Area).where(Area.area_id == ticket.area_id)
                area_result = await conn.execute(area_query)
                area = area_result.scalar_one_or_none()
                if area and area.enterprise_id != user.enterprise_user.enterprise_id:
                    raise HTTPException(status_code=403, detail="无权访问该工单")
            
            # 获取监护人姓名
            custodian_query = select(EnterpriseUser.name).where(
                EnterpriseUser.user_id == ticket.custodians
            )
            custodian_result = await conn.execute(custodian_query)
            custodian_name = custodian_result.scalar_one_or_none() or "未知"
            
            return TicketDetail(
                ticket_id=ticket.ticket_id,
                apply_date=ticket.apply_date,
                applicant=ticket.applicant,
                applicant_name=applicant_name,
                area_id=ticket.area_id,
                area_name=area_name,
                working_content=ticket.working_content,
                pre_st=ticket.pre_st.isoformat(),
                pre_et=ticket.pre_et.isoformat(),
                tools=ticket.tools,
                worker=ticket.worker,
                worker_name=worker_name,
                custodians=ticket.custodians,
                custodian_name=custodian_name,
                danger=ticket.danger,
                protection=ticket.protection,
                hot_work=ticket.hot_work,
                work_height_level=ticket.work_height_level,
                confined_space_id=ticket.confined_space_id,
                temp_power_id=ticket.temp_power_id,
                cross_work_group_id=ticket.cross_work_group_id,
                signature=ticket.signature,
                created_at=ticket.created_at.isoformat(),
                updated_at=ticket.updated_at.isoformat()
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取工单详情失败: {str(e)}")


@router.put("/{ticket_id}/", dependencies=[Depends(authenticate_enterprise_level)])
async def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    user: User = Depends(get_current_user)
):
    """更新工单"""
    from main import app
    
    try:
        async with app.state.engine.begin() as conn:
            # 查询工单
            query = select(Ticket).where(Ticket.ticket_id == ticket_id)
            result = await conn.execute(query)
            ticket = result.scalar_one_or_none()
            
            if not ticket:
                raise HTTPException(status_code=404, detail="工单不存在")
            
            # 权限检查：企业用户只能修改自己企业的工单
            if user.user_type == UserType.enterprise:
                area_query = select(Area).where(Area.area_id == ticket.area_id)
                area_result = await conn.execute(area_query)
                area = area_result.scalar_one_or_none()
                if area and area.enterprise_id != user.enterprise_user.enterprise_id:
                    raise HTTPException(status_code=403, detail="无权修改该工单")
            
            # 更新字段
            update_data = ticket_data.model_dump(exclude_unset=True)
            
            # 处理时间字段
            if 'pre_st' in update_data and update_data['pre_st']:
                update_data['pre_st'] = datetime.fromisoformat(
                    update_data['pre_st'].replace('Z', '+00:00')
                )
            if 'pre_et' in update_data and update_data['pre_et']:
                update_data['pre_et'] = datetime.fromisoformat(
                    update_data['pre_et'].replace('Z', '+00:00')
                )
            
            for key, value in update_data.items():
                setattr(ticket, key, value)
            
            ticket.updated_at = datetime.now()
            
            await conn.commit()
            
            return {"message": "工单更新成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"更新工单失败: {str(e)}")


@router.delete("/{ticket_id}/", dependencies=[Depends(authenticate_enterprise_level)])
async def delete_ticket(
    ticket_id: int,
    user: User = Depends(get_current_user)
):
    """删除工单"""
    from main import app
    
    try:
        async with app.state.engine.begin() as conn:
            # 查询工单
            query = select(Ticket).where(Ticket.ticket_id == ticket_id)
            result = await conn.execute(query)
            ticket = result.scalar_one_or_none()
            
            if not ticket:
                raise HTTPException(status_code=404, detail="工单不存在")
            
            # 权限检查：企业用户只能删除自己企业的工单
            if user.user_type == UserType.enterprise:
                area_query = select(Area).where(Area.area_id == ticket.area_id)
                area_result = await conn.execute(area_query)
                area = area_result.scalar_one_or_none()
                if area and area.enterprise_id != user.enterprise_user.enterprise_id:
                    raise HTTPException(status_code=403, detail="无权删除该工单")
            
            # 删除工单
            await conn.delete(ticket)
            await conn.commit()
            
            return {"message": "工单删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"删除工单失败: {str(e)}")

