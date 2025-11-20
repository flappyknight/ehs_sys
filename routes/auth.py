"""
认证路由
Authentication routes
"""
from typing import Annotated
from datetime import datetime
import random
import re

from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncEngine
from typing import Optional
from pydantic import BaseModel

from api.model import Token, User, RegisterRequest
from config import settings
from .dependencies import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_engine
)
from db.models import User as UserDB
from db.connection import get_session
from core import password as pwd

router = APIRouter()

# 验证码存储（临时使用内存字典，预留Redis接口）
# TODO: 替换为Redis存储
verification_codes: dict[str, dict] = {}  # {username: {"code": str, "expires_at": datetime}}


class ForgotPasswordRequest(BaseModel):
    """忘记密码请求"""
    username: str  # 用户名
    contact: str  # 手机号或邮箱


class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    username: str
    new_password: str
    confirm_password: str
    verification_code: str


def generate_verification_code() -> str:
    """生成6位随机验证码"""
    return str(random.randint(100000, 999999))


def save_verification_code(username: str, code: str, expires_minutes: int = 10):
    """保存验证码（临时使用内存，预留Redis接口）"""
    from datetime import timedelta
    expires_at = datetime.now() + timedelta(minutes=expires_minutes)
    verification_codes[username] = {
        "code": code,
        "expires_at": expires_at
    }
    print(f"📝 验证码已保存到内存: username={username}, code={code}, expires_at={expires_at}")
    # TODO: 替换为Redis存储
    # await redis_client.setex(f"verification_code:{username}", expires_minutes * 60, code)


def get_verification_code(username: str) -> Optional[str]:
    """获取验证码（临时使用内存，预留Redis接口）"""
    if username not in verification_codes:
        return None
    
    code_info = verification_codes[username]
    if datetime.now() > code_info["expires_at"]:
        # 验证码已过期，删除
        del verification_codes[username]
        return None
    
    return code_info["code"]
    # TODO: 替换为Redis存储
    # return await redis_client.get(f"verification_code:{username}")


def delete_verification_code(username: str):
    """删除验证码（临时使用内存，预留Redis接口）"""
    if username in verification_codes:
        del verification_codes[username]
    # TODO: 替换为Redis存储
    # await redis_client.delete(f"verification_code:{username}")


def send_verification_code_sms(phone: str, code: str):
    """发送短信验证码（模拟，预留接口）"""
    print("=" * 60)
    print("【模拟发送短信验证码】")
    print(f"手机号: {phone}")
    print(f"验证码: {code}")
    print(f"发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    # TODO: 实现真实的短信发送功能
    # await sms_service.send(phone, f"您的验证码是: {code}")


def send_verification_code_email(email: str, code: str):
    """发送邮件验证码（模拟，预留接口）"""
    print("=" * 60)
    print("【模拟发送邮件验证码】")
    print(f"邮箱: {email}")
    print(f"验证码: {code}")
    print(f"发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    # TODO: 实现真实的邮件发送功能
    # await email_service.send(email, "密码重置验证码", f"您的验证码是: {code}")


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


@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    engine: AsyncEngine = Depends(get_engine)
):
    """发送密码重置验证码"""
    from main import app
    from db import crud
    
    try:
        print("=" * 60)
        print("【密码找回请求】")
        print(f"用户名: {request.username}")
        print(f"联系方式: {request.contact}")
        print(f"请求时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 先根据用户名查找用户
        user = await crud.get_user(engine, request.username)
        
        if not user:
            print(f"❌ 密码找回失败: 用户不存在")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户名不存在"
            )
        
        # 检查用户是否被删除
        if user.is_deleted:
            print(f"❌ 密码找回失败: 用户已被删除")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 验证输入的手机号或邮箱是否与数据库中的匹配
        is_email = '@' in request.contact
        if is_email:
            # 验证邮箱
            if not user.email or user.email != request.contact:
                print(f"❌ 密码找回失败: 邮箱不匹配 - 输入: {request.contact}, 数据库: {user.email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱或手机不正确"
                )
        else:
            # 验证手机号
            if not user.phone or user.phone != request.contact:
                print(f"❌ 密码找回失败: 手机号不匹配 - 输入: {request.contact}, 数据库: {user.phone}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱或手机不正确"
                )
        
        # 生成验证码
        code = generate_verification_code()
        
        # 保存验证码（10分钟有效期）
        save_verification_code(user.username, code, expires_minutes=10)
        
        # 发送验证码
        if is_email:
            send_verification_code_email(request.contact, code)
        else:
            send_verification_code_sms(request.contact, code)
        
        print(f"✅ 验证码已发送: username={user.username}")
        
        return {
            "message": "验证码已发送",
            "username": user.username  # 返回用户名，前端需要用于重置密码
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 密码找回过程发生错误: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"发送验证码失败: {str(e)}"
        )


@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    engine: AsyncEngine = Depends(get_engine)
):
    """重置密码"""
    from main import app
    
    try:
        print("=" * 60)
        print("【密码重置请求】")
        print(f"用户名: {request.username}")
        print(f"新密码: {'*' * len(request.new_password)}")
        print(f"确认密码: {'*' * len(request.confirm_password)}")
        print(f"验证码: {request.verification_code}")
        print(f"请求时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 验证新密码和确认密码是否一致
        if request.new_password != request.confirm_password:
            print(f"❌ 密码重置失败: 新密码和确认密码不一致")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="新密码和确认密码不一致，请重新输入"
            )
        
        # 验证验证码
        stored_code = get_verification_code(request.username)
        if not stored_code:
            print(f"❌ 密码重置失败: 验证码不存在或已过期")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="验证码不存在或已过期，请重新获取"
            )
        
        if stored_code != request.verification_code:
            print(f"❌ 密码重置失败: 验证码错误")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="验证码错误，请重新输入"
            )
        
        # 查找用户
        async with get_session(engine) as session:
            statement = select(UserDB).where(
                UserDB.username == request.username,
                UserDB.is_deleted == False
            )
            result = await session.exec(statement)
            user = result.first()
            
            if not user:
                print(f"❌ 密码重置失败: 用户不存在")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="用户不存在"
                )
            
            # 处理 Row 对象
            if hasattr(user, '__getitem__') and not isinstance(user, UserDB):
                user = user[0] if len(user) > 0 else None
            
            if not user or not isinstance(user, UserDB):
                print(f"❌ 密码重置失败: 用户数据异常")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="用户数据异常"
                )
            
            # 更新密码
            user.password_hash = pwd.get_password_hash(request.new_password)
            user.updated_at = datetime.now()
            
            await session.commit()
            
            # 删除验证码
            delete_verification_code(request.username)
            
            print(f"✅ 密码重置成功: username={request.username}")
            
            return {
                "message": "密码重置成功"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 密码重置过程发生错误: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"密码重置失败: {str(e)}"
        )


@router.get("/test/")
async def test(user: User = Depends(get_current_user)):
    """测试接口"""
    return {"hello": "world"}
