"""
企业管理后台路由模块
Enterprise backend management routes module
"""
from fastapi import APIRouter

# 创建企业管理后台主路由
router = APIRouter()

# 导入子模块路由
from .user_management import router as user_mgmt_router
from .bind import router as bind_router
from .settlement import router as settlement_router
from .permission_apply import router as permission_apply_router
# from .contractor_management import router as contractor_mgmt_router
# from .ticket_management import router as ticket_mgmt_router
# from .workflow_management import router as workflow_mgmt_router
# from .permission_management import router as permission_mgmt_router

# 注册子模块路由
router.include_router(user_mgmt_router, prefix="/user-management", tags=["企业用户管理"])
router.include_router(bind_router, prefix="/bind", tags=["企业绑定"])
router.include_router(settlement_router, tags=["企业入驻申请"])
router.include_router(permission_apply_router, prefix="/permission-apply", tags=["企业用户权限申请"])
# router.include_router(contractor_mgmt_router, prefix="/contractor-management", tags=["企业承包商管理"])
# router.include_router(ticket_mgmt_router, prefix="/ticket-management", tags=["企业工单管理"])
# router.include_router(workflow_mgmt_router, prefix="/workflow-management", tags=["企业作业流程管理"])
# router.include_router(permission_mgmt_router, prefix="/permission-management", tags=["企业权限管理"])

__all__ = ["router"]

