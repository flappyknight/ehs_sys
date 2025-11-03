"""
企业后台管理路由模块
Enterprise management routes module
"""
from fastapi import APIRouter
from .enterprise import router as enterprise_info_router
from .department import router as department_router
from .area import router as area_router
from .staff import router as staff_router
from .project import router as project_router

# 创建企业管理主路由
router = APIRouter()

# 注册企业管理子路由
router.include_router(enterprise_info_router, tags=["企业信息管理"])
router.include_router(department_router, prefix="/departments", tags=["部门管理"])
router.include_router(area_router, prefix="/areas", tags=["厂区管理"])
router.include_router(staff_router, prefix="/staff", tags=["人员管理"])
router.include_router(project_router, prefix="/projects", tags=["项目管理"])

__all__ = ["router"]

