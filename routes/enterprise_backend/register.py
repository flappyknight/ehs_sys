"""
企业用户注册处理
Enterprise user registration handler
"""
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text

from api.model import RegisterRequest
from core import password as pwd


async def handle_enterprise_registration(register_data: RegisterRequest, engine: AsyncEngine):
    """
    处理企业用户注册
    
    Args:
        register_data: 注册数据
        engine: 数据库引擎
    
    Returns:
        dict: 注册结果
    """
    print("\n" + "🟢" * 30)
    print("【企业用户注册处理】")
    print(f"处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"路由位置: routes/enterprise_backend/register.py")
    print("-" * 60)
    
    # 生成密码哈希
    password_hash = pwd.get_password_hash(register_data.password)
    
    # 打印即将写入数据库的数据
    print("【准备写入数据库的数据】")
    print(f"用户表 (users):")
    print(f"  - username: {register_data.username}")
    print(f"  - password_hash: {password_hash[:20]}...")
    print(f"  - user_type: 'enterprise'")
    print(f"  - phone: {register_data.phone}")
    print(f"  - email: {register_data.email}")
    print(f"  - user_level: -1 (待审核状态)")
    print(f"  - audit_status: 1 (审核未提交)")
    print(f"  - temp_token: {register_data.temp_token}")
    print(f"  - sys_only_id: <将自动设置为user_id>")
    print(f"  - created_at: {datetime.now()}")
    print(f"  - updated_at: {datetime.now()}")
    
    print("\n【注意】")
    print("  ℹ️  企业用户注册后需要等待审核")
    print("  ℹ️  审核通过后需要绑定企业信息")
    
    print("🟢" * 30 + "\n")
    
    # 实际的数据库写入逻辑
    async with engine.begin() as conn:
        # 检查用户名是否已存在（只检查is_deleted=false的记录）
        username_check_query = text("""
            SELECT user_id FROM users 
            WHERE username = :username AND is_deleted = false
        """)
        result = await conn.execute(username_check_query, {"username": register_data.username})
        existing_user = result.fetchone()
        
        if existing_user:
            print(f"❌ 注册失败: 用户名 '{register_data.username}' 已存在")
            raise ValueError(f"用户名 '{register_data.username}' 已存在")
        
        # 检查手机号是否已存在（只检查is_deleted=false的记录）
        if register_data.phone:
            phone_check_query = text("""
                SELECT user_id FROM users 
                WHERE phone = :phone AND is_deleted = false
            """)
            result = await conn.execute(phone_check_query, {"phone": register_data.phone})
            existing_phone = result.fetchone()
            
            if existing_phone:
                print(f"❌ 注册失败: 手机号 '{register_data.phone}' 已被使用")
                raise ValueError(f"手机号 '{register_data.phone}' 已被使用")
        
        # 检查邮箱是否已存在（只检查is_deleted=false的记录）
        if register_data.email:
            email_check_query = text("""
                SELECT user_id FROM users 
                WHERE email = :email AND is_deleted = false
            """)
            result = await conn.execute(email_check_query, {"email": register_data.email})
            existing_email = result.fetchone()
            
            if existing_email:
                print(f"❌ 注册失败: 邮箱 '{register_data.email}' 已被使用")
                raise ValueError(f"邮箱 '{register_data.email}' 已被使用")
        
        # 插入新用户
        insert_query = text("""
            INSERT INTO users (
                username, password_hash, user_type, phone, email,
                user_level, audit_status, temp_token, created_at, updated_at
            ) VALUES (
                :username, :password_hash, :user_type, :phone, :email,
                :user_level, :audit_status, :temp_token, :created_at, :updated_at
            ) RETURNING user_id
        """)
        
        result = await conn.execute(insert_query, {
            "username": register_data.username,
            "password_hash": password_hash,
            "user_type": "enterprise",
            "phone": register_data.phone,
            "email": register_data.email,
            "user_level": -1,
            "audit_status": 1,
            "temp_token": register_data.temp_token,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })
        
        user_id = result.fetchone()[0]
        
        # 更新 sys_only_id 为 user_id
        update_query = text("UPDATE users SET sys_only_id = :user_id WHERE user_id = :user_id")
        await conn.execute(update_query, {"user_id": user_id})
        
        print(f"✅ 企业用户注册成功: user_id={user_id}, username={register_data.username}")
    
    # 返回结果
    return {
        "user_id": user_id,
        "username": register_data.username,
        "user_type": "enterprise",
        "message": "企业用户注册成功，等待审核"
    }

