#!/usr/bin/env python3
"""检查和重置 admin 用户的脚本"""

import asyncio
from db.connection import create_engine
from db import crud
from core import password as pwd
from config import settings

async def check_admin():
    """检查 admin 用户"""
    engine = create_engine()
    
    try:
        print("=" * 50)
        print("检查 admin 用户配置")
        print("=" * 50)
        
        # 显示配置的用户名和密码
        print(f"\n📋 .env 文件中配置的 admin 信息:")
        print(f"   用户名: {settings.admin_username}")
        print(f"   密码: {settings.admin_password}")
        
        # 检查数据库中的用户
        print(f"\n🔍 检查数据库中的 admin 用户...")
        user = await crud.get_user(engine, settings.admin_username, "admin")
        
        if user:
            print(f"   ✅ admin 用户存在")
            print(f"   用户ID: {user.user_id}")
            print(f"   用户名: {user.username}")
            print(f"   用户类型: {user.user_type}")
            
            # 验证密码
            print(f"\n🔐 验证密码...")
            is_valid = pwd.verify_password(settings.admin_password, user.password_hash)
            if is_valid:
                print(f"   ✅ 密码正确！")
                print(f"\n✨ 可以使用以下凭据登录:")
                print(f"   用户名: {settings.admin_username}")
                print(f"   密码: {settings.admin_password}")
            else:
                print(f"   ❌ 密码不匹配！")
                print(f"\n🔧 需要重置密码吗? (y/n)")
                choice = input().strip().lower()
                if choice == 'y':
                    await reset_password(engine, user)
        else:
            print(f"   ❌ admin 用户不存在")
            print(f"\n🔧 需要创建 admin 用户吗? (y/n)")
            choice = input().strip().lower()
            if choice == 'y':
                await create_admin(engine)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
    finally:
        await engine.dispose()
        print("\n" + "=" * 50)

async def reset_password(engine, user):
    """重置 admin 密码"""
    try:
        new_password_hash = pwd.get_password_hash(settings.admin_password)
        
        # 更新密码
        from sqlmodel import select, update
        from db.models import User
        
        async with engine.begin() as conn:
            stmt = (
                update(User)
                .where(User.user_id == user.user_id)
                .values(password_hash=new_password_hash)
            )
            await conn.execute(stmt)
        
        print(f"\n✅ 密码已重置为: {settings.admin_password}")
        
    except Exception as e:
        print(f"\n❌ 重置密码失败: {e}")

async def create_admin(engine):
    """创建 admin 用户"""
    try:
        await crud.create_user(
            engine,
            username=settings.admin_username,
            password_hash=pwd.get_password_hash(settings.admin_password),
            user_type="admin"
        )
        print(f"\n✅ admin 用户创建成功！")
        print(f"   用户名: {settings.admin_username}")
        print(f"   密码: {settings.admin_password}")
        
    except Exception as e:
        print(f"\n❌ 创建 admin 用户失败: {e}")

if __name__ == "__main__":
    asyncio.run(check_admin())

