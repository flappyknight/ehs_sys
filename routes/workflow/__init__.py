"""
工单流程管理路由模块
Workflow management routes module
"""
from fastapi import APIRouter

# 创建工单流程管理主路由
router = APIRouter()

# TODO: 导入子模块路由
# 当实现具体的工单流程管理功能时，在这里导入并注册子路由
# 例如：
# from .workflow_template import router as template_router
# router.include_router(template_router, prefix="/templates", tags=["流程模板"])

__all__ = ["router"]

