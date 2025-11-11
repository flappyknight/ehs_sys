"""
企业用户管理子模块
Enterprise user management sub-module
"""
from fastapi import APIRouter

# 导入子路由
from .user import router as user_router

# 创建用户管理主路由
router = APIRouter()

# 注册子路由
router.include_router(user_router, prefix="/users", tags=["企业员工管理"])


__all__ = ["router"]

