"""
认证路由
Authentication routes
"""
from typing import Annotated
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncEngine
from typing import Optional

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
    user_type: Optional[str] = Form(None),
) -> Token:
    """用户登录获取访问令牌 - 包含权限验证逻辑"""
    from main import app  # 延迟导入避免循环依赖
    
    try:
        # 打印登录数据
        print("=" * 50)
        print("【登录请求】")
        print(f"用户名: {form_data.username}")
        print(f"密码: {'*' * len(form_data.password)}")  # 密码不明文打印
        print(f"选择的用户类型: {user_type}")
        print(f"登录时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        # 先检查用户是否存在
        from db import crud
        user_check = await crud.get_user(app.state.engine, form_data.username)
        if not user_check:
            print(f"❌ 登录失败: 用户不存在")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在，请先注册",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 验证用户名和密码
        user = await authenticate_user(app.state.engine, form_data.username, form_data.password)
        if not user:
            print(f"❌ 登录失败: 用户名或密码错误")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 验证用户类型是否匹配
        if user_type and user_type != user.user_type:
            print(f"❌ 登录失败: 用户类型不匹配 - 选择的类型: {user_type}, 实际类型: {user.user_type}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="用户类型不正确，请选择正确的身份类型",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 检查用户是否被删除
        if user.is_deleted:
            print(f"❌ 登录失败: 用户已被删除")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="用户已被删除",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        print(f"✅ 登录成功: 用户类型={user.user_type}, user_status={user.user_status}")
        
        # 权限验证逻辑 - 根据user_status字段判断
        redirect_to = None
        message = None
        
        # 检查user_status是否为1（审核通过）
        if user.user_status == 1:
            # 审核通过，允许进入系统
            redirect_to = "/dashboard"
        else:
            # user_status不为1，需要跳转到权限申请页面
            if user.user_type == "admin":
                redirect_to = "/admin/permission-apply"
                message = "请先提交权限申请信息"
            elif user.user_type == "enterprise":
                redirect_to = "/enterprise/permission-apply"
                message = "请先完成权限申请"
            elif user.user_type == "contractor":
                redirect_to = "/contractor/permission-apply"
                message = "请先完成权限申请"
            else:
                redirect_to = "/login"
                message = "未知用户类型"
        
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
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 登录过程发生错误: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}"
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
    
    # 验证用户名格式
    import re
    username_regex = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]{5,}$')
    if not username_regex.match(register_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名只能包含英文字母、数字和下划线，至少6个字符，不能以数字开头"
        )
    
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
