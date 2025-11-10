"""
共享依赖项
Shared dependencies for routes
"""
from typing import Union
from datetime import timedelta, datetime, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError

from api.model import User, UserType, PermissionLevel
from config import settings
from db import crud
from core import password as pwd


# OAuth2 密码认证
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def authenticate_user(engine, username: str, password: str):
    """验证用户身份"""
    user = await crud.get_user(engine, username)
    if not user:
        return False
    if not pwd.verify_password(password, user.password_hash):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def get_token_from_header(token: str = Depends(oauth2_scheme)):
    """从请求头获取token"""
    return token


async def get_current_user(token: str = Depends(get_token_from_header)) -> User:
    """获取当前登录用户"""
    from main import app  # 延迟导入避免循环依赖
    from api.model_trans import convert_user_db_to_response
    
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    username = payload.get("sub")
    user_type = payload.get("user_type")
    user_db = await crud.get_user(app.state.engine, username, user_type)
    
    if not user_db:
        raise HTTPException(status_code=401, detail="User not found")
    
    user = convert_user_db_to_response(user_db)
    
    # 确保返回完整的用户信息
    if user.user_type == UserType.contractor:
        user.contractor_user = user.contractor_user
    elif user.user_type == UserType.enterprise:
        user.enterprise_user = user.enterprise_user
    
    return user


async def authenticate_enterprise_level(user: User = Depends(get_current_user)):
    """验证企业级别权限（企业管理员及以上）"""
    if user.user_type != UserType.admin and user.user_type != UserType.enterprise:
        raise HTTPException(
            status_code=401, 
            detail="Access to this api is not permitted! higher access level needed!"
        )
    if user.user_type == UserType.enterprise and PermissionLevel.map(user.enterprise_user.role_type) < PermissionLevel.manager:
        raise HTTPException(
            status_code=401, 
            detail="Access to this api is not permitted! higher access level needed!"
        )
    return user


async def authenticate_contractor_level(user: User = Depends(get_current_user)):
    """验证承包商级别权限（承包商审批员及以上）"""
    if user.user_type != UserType.admin:
        if user.user_type == UserType.contractor and PermissionLevel.map(user.contractor_user.role_type) < PermissionLevel.approver:
            raise HTTPException(
                status_code=401, 
                detail="Access to this api is not permitted! higher access level needed!"
            )
        if user.user_type == UserType.enterprise and PermissionLevel.map(user.enterprise_user.role_type) < PermissionLevel.site_staff:
            raise HTTPException(
                status_code=401, 
                detail="Access to this api is not permitted! higher access level needed!"
            )
    return user


def get_user_enterprise_id(user: User) -> int:
    """获取用户的企业ID"""
    if user.user_type == UserType.enterprise and user.enterprise_user:
        return user.enterprise_user.enterprise_id
    return 0


async def get_engine():
    """获取数据库引擎"""
    from main import app  # 延迟导入避免循环依赖
    return app.state.engine

