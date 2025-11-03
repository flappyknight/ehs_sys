"""
计划管理路由
Plan management routes
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from api.model import Plan, PlanParticipant, User
from db import crud
from routes.dependencies import get_current_user, authenticate_contractor_level

router = APIRouter()


@router.post("/add/", dependencies=[Depends(authenticate_contractor_level)])
async def add_plan(plan: Plan):
    """添加计划"""
    from main import app
    plan_db = await crud.create_plan(app.state.engine, plan)
    return plan_db


@router.get("/{plan_id}/participants/")
async def get_plan_participants(
    plan_id: int, 
    user: User = Depends(get_current_user)
) -> List[PlanParticipant]:
    """获取计划的参与人员列表"""
    from main import app
    
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

