#!/usr/bin/env python3
"""直接使用 bcrypt 创建 admin 用户"""

import asyncio
import bcrypt
from datetime import datetime
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from db.connection import create_engine
from db.models import User
from config import settings

async def create_admin():
    """创建 admin 用户"""
    engine = create_engine()
    
    try:
        print("=" * 50)
        print("创建 admin 用户")
        print("=" * 50)
        
        # 检查用户是否已存在
        print(f"\n🔍 检查 admin 用户是否存在...")
        async with AsyncSession(engine) as session:
            stmt = select(User).where(User.username == settings.admin_username)
            result = await session.execute(stmt)
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"   ⚠️  admin 用户已存在！")
                print(f"   用户名: {existing_user.username}")
                print(f"   用户类型: {existing_user.user_type}")
                
                # 重置密码
                print(f"\n🔄 重置密码...")
                password_bytes = settings.admin_password.encode('utf-8')
                hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
                
                existing_user.password_hash = hashed.decode('utf-8')
                session.add(existing_user)
                await session.commit()
                
                print(f"✅ 密码已重置！")
            else:
                print(f"   ℹ️  admin 用户不存在，正在创建...")
                
                # 创建密码哈希
                password_bytes = settings.admin_password.encode('utf-8')
                hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
                
                # 创建用户
                new_user = User(
                    username=settings.admin_username,
                    password_hash=hashed.decode('utf-8'),
                    user_type="admin",
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                session.add(new_user)
                await session.commit()
                await session.refresh(new_user)
                
                print(f"\n✅ admin 用户创建成功！")
                print(f"   用户ID: {new_user.user_id}")
                print(f"   用户名: {new_user.username}")
                print(f"   用户类型: {new_user.user_type}")
        
        print(f"\n✨ 可以使用以下凭据登录:")
        print(f"   用户名: {settings.admin_username}")
        print(f"   密码: {settings.admin_password}")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()
        print("\n" + "=" * 50)

if __name__ == "__main__":
    asyncio.run(create_admin())

