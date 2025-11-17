"""
企业用户权限申请处理
Enterprise user permission application handler
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text, select, and_
from sqlmodel import select as sql_select
import os
import shutil

from api.model import User
from routes.dependencies import get_current_user, get_engine
from db.models import EnterpriseInfo as EnterpriseDB, User as UserDB
from db.connection import get_session

router = APIRouter()

# 文件上传目录
UPLOAD_DIR = "uploads/enterprise_licenses"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/enterprises")
async def get_available_enterprises(
    engine: AsyncEngine = Depends(get_engine),
    current_user: User = Depends(get_current_user)
):
    """
    获取可绑定的企业列表（business_status为续存的企业）
    只有企业用户且user_status不为1时可以调用
    管理员用户（role_level=1）不允许绑定
    """
    if current_user.user_type != "enterprise":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有企业用户可以查看企业列表"
        )
    
    try:
        async with get_session(engine) as session:
            # 检查用户是否是管理员或已有企业关联
            user_query = select(UserDB).where(UserDB.user_id == current_user.user_id)
            user_result = await session.exec(user_query)
            user_db = user_result.first()
            
            if hasattr(user_db, '__getitem__') and not isinstance(user_db, UserDB):
                user_db = user_db[0] if len(user_db) > 0 else None
            
            if user_db:
                # 如果用户状态为待审核（user_status=2），不允许获取企业列表
                if user_db.user_status == 2:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="您的申请正在审核中，请等待审核结果，不允许绑定企业"
                    )
                
                if user_db.role_level == 1:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="企业管理员不允许绑定其他企业"
                    )
                
                if user_db.enterprise_staff_id is not None:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="您已关联企业，不允许绑定其他企业"
                    )
            
            # 查询business_status为续存且未删除的企业
            query = select(EnterpriseDB).where(
                and_(
                    EnterpriseDB.business_status == "续存",
                    EnterpriseDB.is_deleted == False
                )
            ).order_by(EnterpriseDB.company_name)
            
            result = await session.exec(query)
            enterprises = result.all()
            
            items = []
            for enterprise in enterprises:
                # 处理 Row 对象
                if hasattr(enterprise, '__getitem__') and not isinstance(enterprise, EnterpriseDB):
                    enterprise = enterprise[0] if len(enterprise) > 0 else None
                    if enterprise is None:
                        continue
                
                items.append({
                    "enterprise_id": enterprise.enterprise_id,
                    "company_name": enterprise.company_name,
                    "company_type": enterprise.company_type,
                    "license_number": enterprise.license_number,
                    "legal_person": enterprise.legal_person,
                    "business_status": enterprise.business_status
                })
            
            return {"items": items}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取企业列表失败: {str(e)}"
        )


@router.post("/submit")
async def submit_permission_apply(
    apply_data: dict,
    engine: AsyncEngine = Depends(get_engine),
    current_user: User = Depends(get_current_user)
):
    """
    提交企业用户权限申请
    
    支持两种方式：
    1. 申请企业入驻：apply_type="settlement"
    2. 绑定已有企业：apply_type="bind", enterprise_id必填, role_type必填（管理员/员工）
    """
    if current_user.user_type != "enterprise":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有企业用户可以提交权限申请"
        )
    
    apply_type = apply_data.get("apply_type")
    
    print("\n" + "🟢" * 30)
    print("【企业用户权限申请提交】")
    print(f"用户ID: {current_user.user_id}")
    print(f"用户名: {current_user.username}")
    print(f"申请类型: {apply_type}")
    print(f"申请时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"申请数据: {apply_data}")
    print("🟢" * 30 + "\n")
    
    try:
        async with engine.begin() as conn:
            # 检查用户是否已有企业关联和当前状态
            check_user_query = text("SELECT role_level, enterprise_staff_id, user_status FROM users WHERE user_id = :user_id")
            user_result = await conn.execute(check_user_query, {"user_id": current_user.user_id})
            user_row = user_result.fetchone()
            
            if user_row:
                role_level = user_row[0]
                enterprise_staff_id = user_row[1]
                user_status = user_row[2]
                
                # 如果用户状态为待审核（user_status=2），不允许再次提交申请
                if user_status == 2:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="您的申请正在审核中，请等待审核结果，不允许重复提交"
                    )
                
                # 如果是管理员（role_level=1）或已有企业关联，不允许绑定
                if role_level == 1:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="企业管理员不允许绑定其他企业"
                    )
                
                if enterprise_staff_id is not None:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="您已关联企业，不允许绑定其他企业"
                    )
            
            if apply_type == "settlement":
                # 申请企业入驻，跳转到企业入驻申请页面
                # 这里只更新状态为待审核，实际的企业信息需要在入驻页面填写
                update_query = text("""
                    UPDATE users 
                    SET user_status = 2,
                        updated_at = :updated_at
                    WHERE user_id = :user_id
                """)
                
                await conn.execute(update_query, {
                    "user_id": current_user.user_id,
                    "updated_at": datetime.now()
                })
                
                return {
                    "message": "请前往企业入驻申请页面填写详细信息",
                    "user_id": current_user.user_id,
                    "redirect_to": "/settlement/enterprise"
                }
                
            elif apply_type == "bind":
                # 绑定已有企业
                enterprise_id = apply_data.get("enterprise_id")
                role_type = apply_data.get("role_type")  # "管理员" 或 "员工"
                
                if not enterprise_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="绑定企业时，enterprise_id必填"
                    )
                
                if not role_type or role_type not in ["管理员", "员工"]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="role_type必填，且必须是'管理员'或'员工'"
                    )
                
                # 验证企业是否存在且状态为续存
                check_enterprise_query = text("""
                    SELECT enterprise_id FROM enterprise_info 
                    WHERE enterprise_id = :enterprise_id 
                    AND business_status = '续存' 
                    AND is_deleted = false
                """)
                result = await conn.execute(check_enterprise_query, {"enterprise_id": enterprise_id})
                enterprise = result.fetchone()
                
                if not enterprise:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="企业不存在或状态不符合要求"
                    )
                
                # 更新用户信息
                role_level = 1 if role_type == "管理员" else 2
                update_query = text("""
                    UPDATE users 
                    SET enterprise_staff_id = :enterprise_id,
                        role_type = :role_type,
                        role_level = :role_level,
                        user_status = 2,
                        updated_at = :updated_at
                    WHERE user_id = :user_id
                """)
                
                await conn.execute(update_query, {
                    "user_id": current_user.user_id,
                    "enterprise_id": enterprise_id,
                    "role_type": role_type,
                    "role_level": role_level,
                    "updated_at": datetime.now()
                })
                
                print(f"✅ 企业绑定申请已提交: user_id={current_user.user_id}, enterprise_id={enterprise_id}, role_type={role_type}")
                
                return {
                    "message": "绑定申请已提交，等待审核",
                    "user_id": current_user.user_id
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="apply_type必须是'settlement'或'bind'"
                )
                
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 提交权限申请失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交权限申请失败: {str(e)}"
        )


@router.get("/info")
async def get_user_info(
    engine: AsyncEngine = Depends(get_engine),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的详细信息
    """
    if current_user.user_type != "enterprise":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有企业用户可以查看此信息"
        )
    
    try:
        async with get_session(engine) as session:
            query = select(UserDB).where(UserDB.user_id == current_user.user_id)
            result = await session.exec(query)
            user_db = result.first()
            
            if not user_db:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="用户不存在"
                )
            
            # 处理 Row 对象
            if hasattr(user_db, '__getitem__') and not isinstance(user_db, UserDB):
                user_db = user_db[0] if len(user_db) > 0 else None
                if user_db is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="用户不存在"
                    )
            
            # 获取状态文本
            status_text = {
                0: "未通过审核",
                1: "通过审核",
                2: "待审核",
                3: "审核不通过"
            }.get(user_db.user_status, "未知状态")
            
            # 如果用户是企业管理员（role_level=1），获取企业信息
            enterprise_info = None
            if user_db.role_level == 1 and user_db.enterprise_staff_id:
                enterprise_query = select(EnterpriseDB).where(
                    EnterpriseDB.enterprise_id == user_db.enterprise_staff_id
                )
                enterprise_result = await session.exec(enterprise_query)
                enterprise_db = enterprise_result.first()
                
                if enterprise_db:
                    # 处理 Row 对象
                    if hasattr(enterprise_db, '__getitem__') and not isinstance(enterprise_db, EnterpriseDB):
                        enterprise_db = enterprise_db[0] if len(enterprise_db) > 0 else None
                    
                    if enterprise_db:
                        enterprise_info = {
                            "enterprise_id": enterprise_db.enterprise_id,
                            "company_name": enterprise_db.company_name,
                            "license_number": enterprise_db.license_number,
                            "company_type": enterprise_db.company_type,
                            "company_address": enterprise_db.company_address,
                            "legal_person": enterprise_db.legal_person,
                            "establish_date": str(enterprise_db.establish_date) if enterprise_db.establish_date else None,
                            "registered_capital": float(enterprise_db.registered_capital) if enterprise_db.registered_capital else None,
                            "applicant_name": enterprise_db.applicant_name,
                            "business_status": enterprise_db.business_status,
                            "license_file": enterprise_db.license_file
                        }
            
            return {
                "user_id": user_db.user_id,
                "username": user_db.username,
                "name": user_db.name_str or user_db.relay_name or user_db.username,
                "phone": user_db.phone,
                "email": user_db.email,
                "user_type": user_db.user_type,
                "user_status": user_db.user_status,
                "status_text": status_text,
                "role_type": user_db.role_type,
                "role_level": user_db.role_level,
                "enterprise_staff_id": user_db.enterprise_staff_id,
                "enterprise_info": enterprise_info
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户信息失败: {str(e)}"
        )


@router.put("/enterprise/update")
async def update_enterprise(
    companyName: str = Form(...),
    licenseFile: Optional[UploadFile] = File(None),
    licenseNumber: str = Form(...),
    companyAddress: str = Form(...),
    legalPerson: Optional[str] = Form(None),
    establishDate: Optional[str] = Form(None),
    registeredCapital: Optional[str] = Form(None),
    applicantName: Optional[str] = Form(None),
    engine: AsyncEngine = Depends(get_engine),
    current_user: User = Depends(get_current_user)
):
    """
    更新企业信息（仅限企业管理员，且企业状态为审核不通过）
    """
    if current_user.user_type != "enterprise":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有企业用户可以更新企业信息"
        )
    
    try:
        async with engine.begin() as conn:
            # 检查用户是否是管理员
            check_user_query = text("""
                SELECT role_level, enterprise_staff_id FROM users 
                WHERE user_id = :user_id
            """)
            user_result = await conn.execute(check_user_query, {"user_id": current_user.user_id})
            user_row = user_result.fetchone()
            
            if not user_row or user_row[0] != 1:  # role_level = 1 表示企业管理员
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="只有企业管理员可以更新企业信息"
                )
            
            enterprise_id = user_row[1]
            if not enterprise_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用户未关联企业"
                )
            
            # 检查企业状态
            check_enterprise_query = text("""
                SELECT business_status FROM enterprise_info 
                WHERE enterprise_id = :enterprise_id AND is_deleted = false
            """)
            enterprise_result = await conn.execute(check_enterprise_query, {"enterprise_id": enterprise_id})
            enterprise_row = enterprise_result.fetchone()
            
            if not enterprise_row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="企业不存在"
                )
            
            if enterprise_row[0] != "审核不通过":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="只有审核不通过的企业可以修改"
                )
            
            # 处理文件上传
            license_file_path = None
            if licenseFile:
                file_ext = os.path.splitext(licenseFile.filename)[1]
                file_name = f"{enterprise_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_ext}"
                file_path = os.path.join(UPLOAD_DIR, file_name)
                
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(licenseFile.file, buffer)
                
                license_file_path = file_path
            
            # 处理日期和数值
            establish_date_value = None
            if establishDate:
                try:
                    establish_date_value = datetime.strptime(establishDate, "%Y-%m-%d").date()
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="成立日期格式错误，应为YYYY-MM-DD"
                    )
            
            registered_capital_value = None
            if registeredCapital:
                try:
                    registered_capital_value = float(registeredCapital)
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="注册资本格式错误"
                    )
            
            # 更新企业信息
            if license_file_path:
                update_query = text("""
                    UPDATE enterprise_info 
                    SET company_name = :company_name,
                        license_number = :license_number,
                        license_file = :license_file,
                        company_address = :company_address,
                        legal_person = :legal_person,
                        establish_date = :establish_date,
                        registered_capital = :registered_capital,
                        applicant_name = :applicant_name,
                        business_status = '待审核',
                        updated_at = :updated_at
                    WHERE enterprise_id = :enterprise_id
                """)
                
                await conn.execute(update_query, {
                    "enterprise_id": enterprise_id,
                    "company_name": companyName,
                    "license_number": licenseNumber.strip(),
                    "license_file": license_file_path,
                    "company_address": companyAddress.strip(),
                    "legal_person": legalPerson,
                    "establish_date": establish_date_value,
                    "registered_capital": registered_capital_value,
                    "applicant_name": applicantName,
                    "updated_at": datetime.now()
                })
            else:
                update_query = text("""
                    UPDATE enterprise_info 
                    SET company_name = :company_name,
                        license_number = :license_number,
                        company_address = :company_address,
                        legal_person = :legal_person,
                        establish_date = :establish_date,
                        registered_capital = :registered_capital,
                        applicant_name = :applicant_name,
                        business_status = '待审核',
                        updated_at = :updated_at
                    WHERE enterprise_id = :enterprise_id
                """)
                
                await conn.execute(update_query, {
                    "enterprise_id": enterprise_id,
                    "company_name": companyName,
                    "license_number": licenseNumber.strip(),
                    "company_address": companyAddress.strip(),
                    "legal_person": legalPerson,
                    "establish_date": establish_date_value,
                    "registered_capital": registered_capital_value,
                    "applicant_name": applicantName,
                    "updated_at": datetime.now()
                })
            
            # 更新用户状态为待审核
            update_user_query = text("""
                UPDATE users 
                SET user_status = 2,
                    updated_at = :updated_at
                WHERE user_id = :user_id
            """)
            
            await conn.execute(update_user_query, {
                "user_id": current_user.user_id,
                "updated_at": datetime.now()
            })
            
            return {
                "message": "企业信息已更新，等待重新审核",
                "enterprise_id": enterprise_id
            }
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 更新企业信息失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新企业信息失败: {str(e)}"
        )
