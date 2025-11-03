"""
工单管理路由模块
Ticket management routes module
"""
from fastapi import APIRouter
from .ticket import router as ticket_router

# 创建工单管理主路由
router = APIRouter()

# 注册工单管理路由
router.include_router(ticket_router, tags=["工单管理"])

__all__ = ["router"]

