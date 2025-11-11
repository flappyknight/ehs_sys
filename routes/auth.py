"""
认证路由
Authentication routes
"""
from typing import Annotated
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncEngine

from api.model import Token, User, RegisterRequest
from config import settings
from core.password import get_password_hash
from db.models import User as DBUser, EnterpriseUser, Contractor, ContractorUser
from .dependencies import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_engine
)

router = APIRouter()


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """用户登录获取访问令牌"""
    from main import app  # 延迟导入避免循环依赖
    
    # 打印登录数据
    print("=" * 50)
    print("【登录请求】")
    print(f"用户名: {form_data.username}")
    print(f"密码: {'*' * len(form_data.password)}")  # 密码不明文打印
    print(f"登录时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    user = await authenticate_user(app.state.engine, form_data.username, form_data.password)
    if not user:
        print(f"❌ 登录失败: 用户名或密码错误")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"✅ 登录成功: 用户类型={user.user_type}")
    
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


@router.post("/register")
async def register_user(
    register_data: RegisterRequest,
    engine: AsyncEngine = Depends(get_engine)
):
    """用户注册（暂时只打印数据，不写入数据库）"""
    
    # 打印注册数据
    print("\n" + "=" * 60)
    print("【注册请求】")
    print(f"注册时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"用户类型: {register_data.userType}")
    print(f"用户名: {register_data.username}")
    print(f"密码: {'*' * len(register_data.password)}")  # 密码不明文打印
    print(f"姓名: {register_data.name}")
    print(f"手机号: {register_data.phone}")
    print(f"邮箱: {register_data.email or '未填写'}")
    
    if register_data.userType == 'enterprise':
        print(f"\n【企业用户信息】")
        print(f"企业名称: {register_data.companyName}")
        print(f"职位: {register_data.position or '未填写'}")
    elif register_data.userType == 'contractor':
        print(f"\n【承包商用户信息】")
        print(f"承包商公司名称: {register_data.contractorCompanyName}")
    elif register_data.userType == 'admin':
        print(f"\n【系统管理员信息】")
        print(f"管理员授权码: {register_data.adminCode or '未填写'}")
        print(f"所属部门: {register_data.department or '未填写'}")
    
    print("=" * 60 + "\n")
    
    # 验证用户类型
    if register_data.userType not in ['enterprise', 'contractor', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的用户类型"
        )
    
    # 暂时返回成功（不实际写入数据库）
    return {
        "message": "注册数据已接收（测试模式，未写入数据库）",
        "user_id": 999,  # 模拟的用户ID
        "username": register_data.username,
        "userType": register_data.userType
    }


@router.post("/logout")
async def logout():
    """用户登出"""
    # 由于我们使用localStorage管理token，后端不需要做任何操作
    return {"message": "Logged out"}


@router.get("/test/")
async def test(user: User = Depends(get_current_user)):
    """测试接口"""
    return {"hello": "world"}

