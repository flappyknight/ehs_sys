"""
系统账户后台管理路由模块
Admin backend management routes module
"""
from fastapi import APIRouter

# 创建管理员主路由
router = APIRouter()

# 导入子路由
from .enterprise import router as enterprise_router
from .contractor import router as contractor_router
from .user import router as user_router
from .permission_apply import router as permission_apply_router

# 注册子路由
router.include_router(enterprise_router, prefix="/enterprises", tags=["企业管理"])
router.include_router(contractor_router, prefix="/contractors", tags=["承包商管理"])
router.include_router(user_router, prefix="/users", tags=["系统用户管理"])
router.include_router(permission_apply_router, prefix="/permission-apply", tags=["权限申请"])

__all__ = ["router"]
