"""
认证路由
Authentication routes
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from api.model import Token, User
from config import settings
from .dependencies import (
    authenticate_user,
    create_access_token,
    get_current_user
)

router = APIRouter()


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """用户登录获取访问令牌"""
    from main import app  # 延迟导入避免循环依赖
    
    user = await authenticate_user(app.state.engine, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = settings.access_token_expire_minutes
    access_token = create_access_token(
        data={"sub": user.username, "user_type": user.user_type}, 
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/users/me/")
async def read_users_me(user: User = Depends(get_current_user)) -> User:
    """获取当前登录用户信息"""
    return user


@router.post("/logout")
async def logout():
    """用户登出"""
    # 由于我们使用localStorage管理token，后端不需要做任何操作
    return {"message": "Logged out"}


@router.get("/test/")
async def test(user: User = Depends(get_current_user)):
    """测试接口"""
    return {"hello": "world"}

