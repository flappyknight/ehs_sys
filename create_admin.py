#!/usr/bin/env python3
"""创建 admin 用户的脚本"""

import asyncio
from db.connection import create_engine
from db import crud
from core import password as pwd
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
        existing_user = await crud.get_user(engine, settings.admin_username, "admin")
        
        if existing_user:
            print(f"   ⚠️  admin 用户已存在！")
            print(f"   用户名: {existing_user.username}")
            print(f"   用户类型: {existing_user.user_type}")
            
            # 验证密码
            is_valid = pwd.verify_password(settings.admin_password, existing_user.password_hash)
            if is_valid:
                print(f"\n✅ 密码验证成功！")
                print(f"\n可以使用以下凭据登录:")
                print(f"   用户名: {settings.admin_username}")
                print(f"   密码: {settings.admin_password}")
            else:
                print(f"\n❌ 密码不匹配，正在重置密码...")
                # 重置密码
                from sqlmodel import update
                from db.models import User
                
                new_password_hash = pwd.get_password_hash(settings.admin_password)
                async with engine.begin() as conn:
                    stmt = (
                        update(User)
                        .where(User.user_id == existing_user.user_id)
                        .values(password_hash=new_password_hash)
                    )
                    await conn.execute(stmt)
                
                print(f"✅ 密码已重置！")
                print(f"\n可以使用以下凭据登录:")
                print(f"   用户名: {settings.admin_username}")
                print(f"   密码: {settings.admin_password}")
        else:
            print(f"   ℹ️  admin 用户不存在，正在创建...")
            
            # 创建 admin 用户
            user = await crud.create_user(
                engine,
                username=settings.admin_username,
                password_hash=pwd.get_password_hash(settings.admin_password),
                user_type="admin"
            )
            
            print(f"\n✅ admin 用户创建成功！")
            print(f"   用户ID: {user.user_id}")
            print(f"   用户名: {user.username}")
            print(f"   用户类型: {user.user_type}")
            print(f"\n可以使用以下凭据登录:")
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

