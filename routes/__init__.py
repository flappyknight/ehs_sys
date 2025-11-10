"""
路由模块初始化
Routes module initialization

本模块包含以下子模块：
1. admin - 系统账户后台管理
2. enterprise_backend - 企业管理后台
3. contractor_backend - 承包商管理后台
4. ticket - 工单管理
5. workflow - 工单流程管理
6. auth - 认证相关（登录、登出等）
"""
from fastapi import APIRouter

# 导入各模块路由
from .admin import router as admin_router
from .enterprise_backend import router as enterprise_backend_router
from .contractor_backend import router as contractor_backend_router
from .ticket import router as ticket_router
from .workflow import router as workflow_router
from .auth import router as auth_router

# 创建主路由
main_router = APIRouter()

# 注册子路由
# 认证路由（无前缀，直接挂载到根路径）
main_router.include_router(auth_router, tags=["认证管理"])

# 系统账户后台管理
main_router.include_router(admin_router, prefix="/admin", tags=["系统账户后台"])

# 企业管理后台
main_router.include_router(enterprise_backend_router, prefix="/enterprise-backend", tags=["企业管理后台"])

# 承包商管理后台
main_router.include_router(contractor_backend_router, prefix="/contractor-backend", tags=["承包商管理后台"])

# 工单管理
main_router.include_router(ticket_router, prefix="/tickets", tags=["工单管理"])

# 工单流程管理
main_router.include_router(workflow_router, prefix="/workflow", tags=["工单流程管理"])

__all__ = ["main_router"]
