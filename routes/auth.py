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
    """用户登录获取访问令牌 - 包含权限验证逻辑"""
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
    
    print(f"✅ 登录成功: 用户类型={user.user_type}, user_level={user.user_level}, audit_status={user.audit_status}")
    
    # 权限验证逻辑
    redirect_to = None
    message = None
    
    if user.user_type == "admin":
        # 管理员：先检查user_level
        if user.user_level == -1:
            # 还没有通过审批，跳转到权限申请页面
            redirect_to = "/admin/permission-apply"
            message = "请先提交权限申请信息"
        else:
            # 已经提交了申请，检查audit_status
            if user.audit_status == 1:
                # 还未提交审核，跳转到权限申请页面
                redirect_to = "/admin/permission-apply"
                message = "请先提交权限申请信息"
            elif user.audit_status == 2:
                # 审核通过，可以进入主页面
                redirect_to = "/dashboard"
            elif user.audit_status == 3:
                # 待审核状态，提示等待审核
                redirect_to = "/login"
                message = "您的权限申请正在审核中，请耐心等待"
            else:
                redirect_to = "/dashboard"
    
    elif user.user_type == "enterprise":
        # 企业用户：检查audit_status
        if user.audit_status == 1:
            # 还没有绑定企业，跳转到绑定企业页面
            redirect_to = "/enterprise/bind"
            message = "请先绑定企业信息"
        elif user.audit_status == 2:
            # 审核通过，可以进入主页面
            redirect_to = "/dashboard"
        elif user.audit_status == 3:
            # 待审核状态，提示等待审核
            redirect_to = "/login"
            message = "您的企业信息正在审核中，请耐心等待"
        else:
            redirect_to = "/dashboard"
    
    elif user.user_type == "contractor":
        # 承包商用户：检查audit_status
        if user.audit_status == 1:
            # 还没有绑定供应商，跳转到绑定供应商页面
            redirect_to = "/contractor/bind"
            message = "请先绑定供应商信息"
        elif user.audit_status == 2:
            # 审核通过，可以进入主页面
            redirect_to = "/dashboard"
        elif user.audit_status == 3:
            # 待审核状态，提示等待审核
            redirect_to = "/login"
            message = "您的供应商信息正在审核中，请耐心等待"
        else:
            redirect_to = "/dashboard"
    
    access_token_expires = settings.access_token_expire_minutes
    access_token = create_access_token(
        data={"sub": user.username, "user_type": user.user_type}, 
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token, 
        token_type="bearer",
        redirect_to=redirect_to,
        message=message
    )


@router.get("/users/me/")
async def read_users_me(user: User = Depends(get_current_user)) -> User:
    """获取当前登录用户信息"""
    return user


@router.post("/register")
async def register_user(
    register_data: RegisterRequest,
    engine: AsyncEngine = Depends(get_engine)
):
    """用户注册 - 根据用户类型分发到不同的处理模块"""
    
    # 打印注册数据
    print("\n" + "=" * 60)
    print("【注册请求 - 路由分发】")
    print(f"注册时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"用户类型: {register_data.userType}")
    print(f"用户名: {register_data.username}")
    print(f"密码: {'*' * len(register_data.password)}")  # 密码不明文打印
    print(f"手机号: {register_data.phone}")
    print(f"邮箱: {register_data.email}")
    print(f"临时Token: {register_data.temp_token}")
    print("=" * 60 + "\n")
    
    # 验证用户类型
    if register_data.userType not in ['enterprise', 'contractor', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的用户类型"
        )
    
    # 根据用户类型分发到不同的处理模块
    try:
        if register_data.userType == 'enterprise':
            # 分发到企业用户注册处理
            from routes.enterprise_backend.register import handle_enterprise_registration
            print("🔀 路由分发: routes/enterprise_backend/register.py")
            result = await handle_enterprise_registration(register_data, engine)
            
        elif register_data.userType == 'contractor':
            # 分发到承包商用户注册处理
            from routes.contractor_backend.register import handle_contractor_registration
            print("🔀 路由分发: routes/contractor_backend/register.py")
            result = await handle_contractor_registration(register_data, engine)
            
        elif register_data.userType == 'admin':
            # 分发到系统管理员注册处理
            from routes.admin.register import handle_admin_registration
            print("🔀 路由分发: routes/admin/register.py")
            result = await handle_admin_registration(register_data, engine)
        
        return result
        
    except ValueError as e:
        # 业务逻辑错误（如用户名已存在）
        print(f"❌ 注册失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # 其他错误
        print(f"❌ 注册失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        )


@router.post("/logout")
async def logout():
    """用户登出"""
    # 由于我们使用localStorage管理token，后端不需要做任何操作
    return {"message": "Logged out"}


@router.get("/test/")
async def test(user: User = Depends(get_current_user)):
    """测试接口"""
    return {"hello": "world"}

