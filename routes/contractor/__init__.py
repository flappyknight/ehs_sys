"""
供应商后台管理路由模块
Contractor management routes module
"""
from fastapi import APIRouter
from .contractor import router as contractor_info_router
from .project import router as project_router
from .plan import router as plan_router

# 创建供应商管理主路由
router = APIRouter()

# 注册供应商管理子路由
router.include_router(contractor_info_router, tags=["供应商信息管理"])
router.include_router(project_router, prefix="/projects", tags=["供应商项目管理"])
router.include_router(plan_router, prefix="/plans", tags=["计划管理"])

__all__ = ["router"]

