"""
承包商管理后台路由模块
Contractor backend management routes module
"""
from fastapi import APIRouter

# 创建承包商管理后台主路由
router = APIRouter()

# 导入子模块路由
# from .staff_management import router as staff_mgmt_router
# from .ticket_view import router as ticket_view_router
# from .cooperation_request import router as cooperation_router

# 注册子模块路由
# router.include_router(staff_mgmt_router, prefix="/staff-management", tags=["承包商人员管理"])
# router.include_router(ticket_view_router, prefix="/ticket-view", tags=["工单浏览"])
# router.include_router(cooperation_router, prefix="/cooperation-request", tags=["合作申请管理"])

__all__ = ["router"]

