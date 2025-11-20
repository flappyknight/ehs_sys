"""
共享依赖项
Shared dependencies for routes
"""
from typing import Union, List, Optional
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
    try:
        user = await crud.get_user(engine, username)
        if not user:
            print(f"❌ 用户 {username} 不存在")
            return False
        # 检查password_hash属性是否存在
        if not hasattr(user, 'password_hash') or user.password_hash is None:
            print(f"❌ 用户 {username} 没有password_hash字段")
            return False
        print(f"🔍 验证密码: 输入密码长度={len(password)}, 哈希长度={len(user.password_hash) if user.password_hash else 0}")
        print(f"🔍 密码哈希前20字符: {user.password_hash[:20] if user.password_hash else 'None'}...")
        verify_result = pwd.verify_password(password, user.password_hash)
        print(f"🔍 密码验证结果: {verify_result}")
        if not verify_result:
            print(f"❌ 密码验证失败")
            return False
        print(f"✅ 密码验证成功")
        return user
    except AttributeError as e:
        print(f"❌ 访问用户属性时出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ 验证用户身份时出错: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


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


def verify_system_admin(user: User = Depends(get_current_user)):
    """
    验证系统管理员权限
    
    系统管理员需要满足：
    - role_level = 0
    - user_status = 1 (通过审核)
    """
    if user.role_level != 0:
        raise HTTPException(status_code=403, detail="需要系统管理员权限")
    if user.user_status != 1:
        raise HTTPException(status_code=403, detail="系统管理员账号未通过审核")
    return user


async def get_user_accessible_enterprise_ids(user: User, engine) -> Optional[List[int]]:
    """
    获取用户可访问的企业ID列表
    
    根据用户的 role_level 返回可访问的企业ID：
    - role_level=0 且 user_status=1 (系统管理员): 返回 None，表示可以访问所有企业
    - role_level=1 (企业管理员): 返回 [enterprise_staff_id]
    - role_level=3 (承包商管理员): 返回 contractor_staff_id 对应的承包商在 contractor_info 表中的 active_enterprise_ids
    - 其他: 返回空列表
    """
    if user.role_level == 0 and user.user_status == 1:
        return None  # None 表示可以访问所有
    
    if user.role_level == 1:
        # 企业管理员：只能访问自己的企业
        if user.enterprise_staff_id:
            return [user.enterprise_staff_id]
        return []
    
    if user.role_level == 3:
        # 承包商管理员：只能访问与自己承包商有合作关系的企业
        if not user.contractor_staff_id:
            return []
        
        from db.models import ContractorInfo as ContractorDB
        from sqlmodel import select
        from db.connection import get_session
        
        async with get_session(engine) as session:
            query = select(ContractorDB).where(
                ContractorDB.contractor_id == user.contractor_staff_id
            )
            result = await session.exec(query)
            contractor = result.first()
            
            if contractor:
                # 处理 Row 对象
                if hasattr(contractor, '__getitem__') and not isinstance(contractor, ContractorDB):
                    contractor = contractor[0] if len(contractor) > 0 else None
                
                if contractor and hasattr(contractor, 'active_enterprise_ids'):
                    active_ids = contractor.active_enterprise_ids
                    if isinstance(active_ids, list):
                        return active_ids
                    return []
        return []
    
    return []


async def get_user_accessible_contractor_ids(user: User, engine) -> Optional[List[int]]:
    """
    获取用户可访问的承包商ID列表
    
    根据用户的 role_level 返回可访问的承包商ID：
    - role_level=0 且 user_status=1 (系统管理员): 返回 None，表示可以访问所有承包商
    - role_level=1 (企业管理员): 返回企业 allowed_contractor_ids 字段中的承包商ID列表
    - role_level=3 (承包商管理员): 返回 [contractor_staff_id]
    - 其他: 返回空列表
    """
    if user.role_level == 0 and user.user_status == 1:
        return None  # None 表示可以访问所有
    
    if user.role_level == 1:
        # 企业管理员：只能访问企业 allowed_contractor_ids 中的承包商
        if not user.enterprise_staff_id:
            return []
        
        from db.models import EnterpriseInfo as EnterpriseDB
        from sqlmodel import select
        from db.connection import get_session
        
        async with get_session(engine) as session:
            query = select(EnterpriseDB).where(
                EnterpriseDB.enterprise_id == user.enterprise_staff_id
            )
            result = await session.exec(query)
            enterprise = result.first()
            
            if enterprise:
                # 处理 Row 对象
                if hasattr(enterprise, '__getitem__') and not isinstance(enterprise, EnterpriseDB):
                    enterprise = enterprise[0] if len(enterprise) > 0 else None
                
                if enterprise and hasattr(enterprise, 'allowed_contractor_ids'):
                    allowed_ids = enterprise.allowed_contractor_ids
                    if isinstance(allowed_ids, list):
                        return allowed_ids
                    return []
        return []
    
    if user.role_level == 3:
        # 承包商管理员：只能访问自己的承包商
        if user.contractor_staff_id:
            return [user.contractor_staff_id]
        return []
    
    return []

