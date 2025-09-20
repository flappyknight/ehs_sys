from config import settings
from db import crud, connection
from core import password


async def init_admin_user(app):
    engine = app.state.engine
    try:
       count = await crud.get_user_count(engine)
       if not count:
           try:
               await crud.create_user(engine, username=settings.admin_username,
                                password_hash=password.get_password_hash(settings.admin_password),
                                user_type="admin")
               print("admin user created")
           except Exception as e:
               print(f"Failed to create admin user error: {e}")
       else:
           print("admin user already exists")
    except Exception as e:
        print(f"Failed to get user count! init_admin Failed! error: {e}")
    pass
