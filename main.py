# main.py
from datetime import timedelta, datetime, timezone
from typing import AsyncIterator, Union, Annotated


from fastapi import FastAPI, Depends, HTTPException, status, Cookie, Response, Query
from fastapi.security import OAuth2PasswordRequestForm

from contextlib import asynccontextmanager
import jwt
from jwt.exceptions import InvalidTokenError

from db.connection import create_engine
from db import crud
from core.init_admin import init_admin_user
from core import password as pwd
from config import settings
from api.model import *



@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # Startup
    # 创建数据库连接engine
    engine = create_engine()
    app.state.engine = engine
    await init_admin_user(app)
    yield

    # Shutdown
    await engine.dispose()
    print("数据库连接已关闭")


app = FastAPI(lifespan=lifespan)

async def authenticate_user(username: str, password: str):
    user = await crud.get_user(app.state.engine, username)
    if not user:
        return False
    if not pwd.verify_password(password, user.password_hash):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


@app.post("/token")
async def login_for_access_token(response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        access_token_expires = settings.access_token_expire_minutes
        access_token = create_access_token(
            data={"sub": user.username, "user_type": user.user_type}, expires_delta=access_token_expires
        )
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=access_token_expires,  # 可选：设置过期时间
        )
    return Token(access_token=access_token, token_type="bearer")


def get_token_from_cookie(access_token: str | None = Cookie(default=None)):
    if access_token is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return access_token

@app.get("/users/me/")
async def read_users_me(token: str = Depends(get_token_from_cookie)):
    try:
        payload = jwt.decode(token.replace("Bearer ", ""), settings.secret_key, algorithms=[settings.algorithm])
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Not authenticated")
    username = payload.get("sub")
    user_type = payload.get("user_type")
    user = await crud.get_user(app.state.engine, username, user_type)
    if user.user_type == UserType.contractor:
        return user.contractor_user
    elif user.user_type == UserType.enterprise:
        return user.enterprise_user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def authenticate_enterprise_level(user: User=Depends(read_users_me)):
    if user.user_type != UserType.admin and user.user_type != UserType.enterprise:  # 无权访问该接口
        raise HTTPException(status_code=401, detail="Access to this api is not permitted! higher access level needed!")
    if user.user_type == UserType.enterprise and PermissionLevel.map(user.enterprise_user.role_type) < PermissionLevel.manager:
        raise HTTPException(status_code=401, detail="Access to this api is not permitted! higher access level needed!")
    return user

async def authenticate_contractor_level(user: User=Depends(read_users_me)):
    if user.user_type != UserType.admin:
        if user.user_type == UserType.contractor and PermissionLevel.map(user.contractor_user.role_type) < PermissionLevel.approver:
            raise HTTPException(status_code=401, detail="Access to this api is not permitted! higher access level needed!")
        if user.user_type == UserType.enterprise and PermissionLevel.map(user.enterprise_user.role_type) < PermissionLevel.site_staff:
            raise HTTPException(status_code=401, detail="Access to this api is not permitted! higher access level needed!")
    return user


@app.post("/enterprise/add/", dependencies=[Depends(authenticate_enterprise_level)])
async def add_enterprise(enterprise: Enterprise):
    enterprise_db =  await crud.create_enterprise(app.state.engine, enterprise)
    return enterprise_db


@app.post("/enterprise/add_user/", dependencies=[Depends(authenticate_enterprise_level)])
async def add_enterprise_user(enterprise_user: EnterpriseUser, create_account: bool=Query(default=True)):
    try:
        if create_account:
            user = User(
                user_type=UserType.enterprise,
                username=enterprise_user.phone,
                password_hash=pwd.get_password_hash(enterprise_user.phone[-6:])
            )
            enterprise_user_db = await crud.create_enterprise_user(app.state.engine, enterprise_user, user)
        else:
            enterprise_user_db = await crud.create_enterprise_user(app.state.engine, enterprise_user)
    except Exception as e:
        return HTTPException(status_code=500, detail="Failed to create this enterprise user: " + str(e))
    return enterprise_user_db

@app.post("/enterprise/add_department/", dependencies=[Depends(authenticate_enterprise_level)])
async def add_department(department: Department):
    department_db = await crud.create_department(app.state.engine, department)
    return department_db


@app.post("/contractor/add/", dependencies=[Depends(authenticate_enterprise_level)])
async def add_contractor(contractor: Contractor):
    contractor_db = await crud.create_contractor(app.state.engine, contractor)
    return contractor_db


@app.post("/contractor/add_user/", dependencies=[Depends(authenticate_contractor_level)])
async def add_contractor_user(contractor_user: ContractorUser):
    contractor_user_db = await crud.create_contractor_user(app.state.engine, contractor_user)
    return contractor_user_db
