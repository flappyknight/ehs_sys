"""
承包商合作申请路由
Contractor cooperation request routes
"""
from fastapi import APIRouter

router = APIRouter()

from .cooperation_request import router as cooperation_request_router

router.include_router(cooperation_request_router, tags=["承包商合作申请"])

__all__ = ["router"]

