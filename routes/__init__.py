"""
路由模块初始化
Routes module initialization
"""
from fastapi import APIRouter
from .enterprise import router as enterprise_router
from .contractor import router as contractor_router
from .ticket import router as ticket_router
from .user import router as user_router

# 创建主路由
main_router = APIRouter()

# 注册子路由
main_router.include_router(enterprise_router, prefix="/enterprise", tags=["企业后台管理"])
main_router.include_router(contractor_router, prefix="/contractor", tags=["供应商后台管理"])
main_router.include_router(ticket_router, prefix="/tickets", tags=["工单后台管理"])
main_router.include_router(user_router, prefix="/users", tags=["用户后台管理"])

__all__ = ["main_router"]

