"""
用户管理路由模块
User management routes module
"""
from fastapi import APIRouter
from .user import router as user_router
from .role import router as role_router

# 创建用户管理主路由
router = APIRouter()

# 注册用户管理子路由
router.include_router(user_router, tags=["用户管理"])
router.include_router(role_router, prefix="/roles", tags=["角色管理"])

__all__ = ["router"]

