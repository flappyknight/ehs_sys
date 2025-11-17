"""
供应商用户权限申请处理
Contractor user permission application handler
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
from db.models import ContractorInfo as ContractorDB, User as UserDB
from db.connection import get_session

router = APIRouter()

# 文件上传目录
UPLOAD_DIR = "uploads/contractor_licenses"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/contractors")
async def get_available_contractors(
    engine: AsyncEngine = Depends(get_engine),
    current_user: User = Depends(get_current_user)
):
    """
    获取可绑定的供应商列表（business_status为续存的供应商）
    只有供应商用户且user_status不为1时可以调用
    管理员用户（role_level=3）不允许绑定
    """
    if current_user.user_type != "contractor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有供应商用户可以查看供应商列表"
        )
    
    try:
        async with get_session(engine) as session:
            # 检查用户是否是管理员或已有供应商关联
            user_query = select(UserDB).where(UserDB.user_id == current_user.user_id)
            user_result = await session.exec(user_query)
            user_db = user_result.first()
            
            if hasattr(user_db, '__getitem__') and not isinstance(user_db, UserDB):
                user_db = user_db[0] if len(user_db) > 0 else None
            
            if user_db:
                # 如果用户状态为待审核（user_status=2），不允许获取供应商列表
                if user_db.user_status == 2:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="您的申请正在审核中，请等待审核结果，不允许绑定供应商"
                    )
                
                if user_db.role_level == 3:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="供应商管理员不允许绑定其他供应商"
                    )
                
                if user_db.contractor_staff_id is not None:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="您已关联供应商，不允许绑定其他供应商"
                    )
            
            # 查询business_status为续存且未删除的供应商
            query = select(ContractorDB).where(
                and_(
                    ContractorDB.business_status == "续存",
                    ContractorDB.is_deleted == False
                )
            ).order_by(ContractorDB.company_name)
            
            result = await session.exec(query)
            contractors = result.all()
            
            items = []
            for contractor in contractors:
                # 处理 Row 对象
                if hasattr(contractor, '__getitem__') and not isinstance(contractor, ContractorDB):
                    contractor = contractor[0] if len(contractor) > 0 else None
                    if contractor is None:
                        continue
                
                items.append({
                    "contractor_id": contractor.contractor_id,
                    "company_name": contractor.company_name,
                    "company_type": contractor.company_type,
                    "license_number": contractor.license_number,
                    "legal_person": contractor.legal_person,
                    "business_status": contractor.business_status
                })
            
            return {"items": items}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取供应商列表失败: {str(e)}"
        )


@router.post("/submit")
async def submit_permission_apply(
    apply_data: dict,
    engine: AsyncEngine = Depends(get_engine),
    current_user: User = Depends(get_current_user)
):
    """
    提交供应商用户权限申请
    
    支持两种方式：
    1. 申请供应商入驻：apply_type="settlement"
    2. 绑定已有供应商：apply_type="bind", contractor_id必填, role_type必填（管理员/员工）
    """
    if current_user.user_type != "contractor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有供应商用户可以提交权限申请"
        )
    
    apply_type = apply_data.get("apply_type")
    
    print("\n" + "🟡" * 30)
    print("【供应商用户权限申请提交】")
    print(f"用户ID: {current_user.user_id}")
    print(f"用户名: {current_user.username}")
    print(f"申请类型: {apply_type}")
    print(f"申请时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"申请数据: {apply_data}")
    print("🟡" * 30 + "\n")
    
    try:
        async with engine.begin() as conn:
            # 检查用户是否已有供应商关联和当前状态
            check_user_query = text("SELECT role_level, contractor_staff_id, user_status FROM users WHERE user_id = :user_id")
            user_result = await conn.execute(check_user_query, {"user_id": current_user.user_id})
            user_row = user_result.fetchone()
            
            if user_row:
                role_level = user_row[0]
                contractor_staff_id = user_row[1]
                user_status = user_row[2]
                
                # 如果用户状态为待审核（user_status=2），不允许再次提交申请
                if user_status == 2:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="您的申请正在审核中，请等待审核结果，不允许重复提交"
                    )
                
                # 如果是管理员（role_level=3）或已有供应商关联，不允许绑定
                if role_level == 3:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="供应商管理员不允许绑定其他供应商"
                    )
                
                if contractor_staff_id is not None:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="您已关联供应商，不允许绑定其他供应商"
                    )
            
            if apply_type == "settlement":
                # 申请供应商入驻，跳转到供应商入驻申请页面
                # 这里只更新状态为待审核，实际的供应商信息需要在入驻页面填写
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
                    "message": "请前往供应商入驻申请页面填写详细信息",
                    "user_id": current_user.user_id,
                    "redirect_to": "/settlement/contractor"
                }
                
            elif apply_type == "bind":
                # 绑定已有供应商
                contractor_id = apply_data.get("contractor_id")
                role_type = apply_data.get("role_type")  # "管理员" 或 "员工"
                
                if not contractor_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="绑定供应商时，contractor_id必填"
                    )
                
                if not role_type or role_type not in ["管理员", "员工"]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="role_type必填，且必须是'管理员'或'员工'"
                    )
                
                # 验证供应商是否存在且状态为续存
                check_contractor_query = text("""
                    SELECT contractor_id FROM contractor_info 
                    WHERE contractor_id = :contractor_id 
                    AND business_status = '续存' 
                    AND is_deleted = false
                """)
                result = await conn.execute(check_contractor_query, {"contractor_id": contractor_id})
                contractor = result.fetchone()
                
                if not contractor:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="供应商不存在或状态不符合要求"
                    )
                
                # 更新用户信息
                role_level = 3 if role_type == "管理员" else 4
                update_query = text("""
                    UPDATE users 
                    SET contractor_staff_id = :contractor_id,
                        role_type = :role_type,
                        role_level = :role_level,
                        user_status = 2,
                        updated_at = :updated_at
                    WHERE user_id = :user_id
                """)
                
                await conn.execute(update_query, {
                    "user_id": current_user.user_id,
                    "contractor_id": contractor_id,
                    "role_type": role_type,
                    "role_level": role_level,
                    "updated_at": datetime.now()
                })
                
                print(f"✅ 供应商绑定申请已提交: user_id={current_user.user_id}, contractor_id={contractor_id}, role_type={role_type}")
                
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
    if current_user.user_type != "contractor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有供应商用户可以查看此信息"
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
            
            # 如果用户是供应商管理员（role_level=3），获取供应商信息
            contractor_info = None
            if user_db.role_level == 3 and user_db.contractor_staff_id:
                contractor_query = select(ContractorDB).where(
                    ContractorDB.contractor_id == user_db.contractor_staff_id
                )
                contractor_result = await session.exec(contractor_query)
                contractor_db = contractor_result.first()
                
                if contractor_db:
                    # 处理 Row 对象
                    if hasattr(contractor_db, '__getitem__') and not isinstance(contractor_db, ContractorDB):
                        contractor_db = contractor_db[0] if len(contractor_db) > 0 else None
                    
                    if contractor_db:
                        contractor_info = {
                            "contractor_id": contractor_db.contractor_id,
                            "company_name": contractor_db.company_name,
                            "license_number": contractor_db.license_number,
                            "company_type": contractor_db.company_type,
                            "company_address": contractor_db.company_address,
                            "legal_person": contractor_db.legal_person,
                            "establish_date": str(contractor_db.establish_date) if contractor_db.establish_date else None,
                            "registered_capital": float(contractor_db.registered_capital) if contractor_db.registered_capital else None,
                            "applicant_name": contractor_db.applicant_name,
                            "business_status": contractor_db.business_status,
                            "license_file": contractor_db.license_file
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
                "contractor_staff_id": user_db.contractor_staff_id,
                "contractor_info": contractor_info
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户信息失败: {str(e)}"
        )


@router.put("/contractor/update")
async def update_contractor(
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
    更新供应商信息（仅限供应商管理员，且供应商状态为审核不通过）
    """
    if current_user.user_type != "contractor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有供应商用户可以更新供应商信息"
        )
    
    try:
        async with engine.begin() as conn:
            # 检查用户是否是管理员
            check_user_query = text("""
                SELECT role_level, contractor_staff_id FROM users 
                WHERE user_id = :user_id
            """)
            user_result = await conn.execute(check_user_query, {"user_id": current_user.user_id})
            user_row = user_result.fetchone()
            
            if not user_row or user_row[0] != 3:  # role_level = 3 表示供应商管理员
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="只有供应商管理员可以更新供应商信息"
                )
            
            contractor_id = user_row[1]
            if not contractor_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用户未关联供应商"
                )
            
            # 检查供应商状态
            check_contractor_query = text("""
                SELECT business_status FROM contractor_info 
                WHERE contractor_id = :contractor_id AND is_deleted = false
            """)
            contractor_result = await conn.execute(check_contractor_query, {"contractor_id": contractor_id})
            contractor_row = contractor_result.fetchone()
            
            if not contractor_row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="供应商不存在"
                )
            
            if contractor_row[0] != "审核不通过":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="只有审核不通过的供应商可以修改"
                )
            
            # 处理文件上传
            license_file_path = None
            if licenseFile:
                file_ext = os.path.splitext(licenseFile.filename)[1]
                file_name = f"{contractor_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_ext}"
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
            
            # 更新供应商信息
            if license_file_path:
                update_query = text("""
                    UPDATE contractor_info 
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
                    WHERE contractor_id = :contractor_id
                """)
                
                await conn.execute(update_query, {
                    "contractor_id": contractor_id,
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
                    UPDATE contractor_info 
                    SET company_name = :company_name,
                        license_number = :license_number,
                        company_address = :company_address,
                        legal_person = :legal_person,
                        establish_date = :establish_date,
                        registered_capital = :registered_capital,
                        applicant_name = :applicant_name,
                        business_status = '待审核',
                        updated_at = :updated_at
                    WHERE contractor_id = :contractor_id
                """)
                
                await conn.execute(update_query, {
                    "contractor_id": contractor_id,
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
                "message": "供应商信息已更新，等待重新审核",
                "contractor_id": contractor_id
            }
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 更新供应商信息失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新供应商信息失败: {str(e)}"
        )
