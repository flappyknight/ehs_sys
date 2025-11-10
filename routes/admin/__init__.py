"""
系统账户后台管理路由模块
Admin backend management routes module
"""
from fastapi import APIRouter

# 创建管理员主路由
router = APIRouter()

# 注册管理员子路由
# from .auth import router as auth_router
# from .user_management import router as user_mgmt_router
# from .enterprise import router as enterprise_router
# from .contractor import router as contractor_router

# router.include_router(auth_router, tags=["系统认证"])
# router.include_router(user_mgmt_router, prefix="/users", tags=["系统用户管理"])
# router.include_router(enterprise_router, prefix="/enterprises", tags=["企业管理"])
# router.include_router(contractor_router, prefix="/contractors", tags=["承包商管理"])

__all__ = ["router"]

