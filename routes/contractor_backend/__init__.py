"""
承包商管理后台路由模块
Contractor backend management routes module
"""
from fastapi import APIRouter

# 创建承包商管理后台主路由
router = APIRouter()

# 导入子模块路由
from .bind import router as bind_router
from .settlement import router as settlement_router
from .permission_apply import router as permission_apply_router
# from .staff_management import router as staff_mgmt_router
# from .ticket_view import router as ticket_view_router
# from .cooperation_request import router as cooperation_router

# 注册子模块路由
router.include_router(bind_router, prefix="/bind", tags=["承包商绑定"])
router.include_router(settlement_router, tags=["承包商入驻"])
router.include_router(permission_apply_router, prefix="/permission-apply", tags=["供应商用户权限申请"])
# router.include_router(staff_mgmt_router, prefix="/staff-management", tags=["承包商人员管理"])
# router.include_router(ticket_view_router, prefix="/ticket-view", tags=["工单浏览"])
# router.include_router(cooperation_router, prefix="/cooperation-request", tags=["合作申请管理"])

__all__ = ["router"]

