"""
企业管理路由 (系统管理员)
Enterprise management routes for system admin

注意：所有路由已被注释，因为相关的 Company 和 Department 表已被删除
"""
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select, and_

from api.model import (
    User,
    UserType,
    EnterpriseUser
)
from core import password as pwd
from db import crud
from db.models import EnterpriseUser as EnterpriseUserDB
from routes.dependencies import get_current_user

router = APIRouter()


def verify_admin(user: User = Depends(get_current_user)):
    """验证系统管理员权限"""
    if user.user_type != UserType.admin:
        raise HTTPException(status_code=403, detail="需要系统管理员权限")
    return user

