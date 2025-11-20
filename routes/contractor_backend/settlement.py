"""
承包商入驻申请路由
Contractor settlement application routes
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text

from api.model import User
from routes.dependencies import get_engine
from core import password as pwd

router = APIRouter()


# 承包商入驻申请
@router.post("/settlement/contractor")
async def submit_contractor_settlement(
    # 承包商基本信息（对应contractor_info表）
    companyName: str = Form(...),
    licenseFile: UploadFile = File(...),
    licenseNumber: str = Form(...),  # 营业执照号码，必填
    companyType: Optional[str] = Form(None),
    serviceScope: Optional[str] = Form(None),
    legalPerson: Optional[str] = Form(None),
    establishDate: Optional[str] = Form(None),
    registeredCapital: Optional[str] = Form(None),
    companyAddress: str = Form(...),  # 公司地址，必填
    businessLicense: Optional[str] = Form(None),
    applicantName: Optional[str] = Form(None),
    remarks: Optional[str] = Form(None),
    # 管理员信息
    adminUsername: str = Form(...),
    adminPassword: str = Form(...),
    adminPhone: str = Form(...),
    adminEmail: str = Form(...),
    tempToken: str = Form(...),
    engine: AsyncEngine = Depends(get_engine)
):
    """
    提交承包商入驻申请
    
    创建承包商信息和管理员用户账号
    """
    print("\n" + "=" * 60)
    print("【承包商入驻申请】")
    print(f"申请时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"承包商公司名称: {companyName}")
    print(f"营业执照号码: {licenseNumber}")
    print(f"公司地址: {companyAddress}")
    print(f"管理员用户名: {adminUsername}")
    print("=" * 60 + "\n")
    
    # 验证营业执照号码必填
    if not licenseNumber or not licenseNumber.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="营业执照号码为必填项，不能为空"
        )
    
    # 验证公司地址必填
    if not companyAddress or not companyAddress.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="公司地址为必填项，不能为空"
        )
    
    # 验证管理员用户名格式
    import re
    username_regex = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]{5,}$')
    if not username_regex.match(adminUsername):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="管理员用户名只能包含英文字母、数字和下划线，至少6个字符，不能以数字开头"
        )
    
    async with engine.begin() as conn:
        try:
            # ========== 1. 唯一性检查 ==========
            # 检查承包商公司名称是否已存在（排除已注销的承包商）
            check_company_name_query = text("""
                SELECT contractor_id FROM contractor_info 
                WHERE company_name = :company_name 
                AND is_deleted = false 
                AND business_status != '已注销'
            """)
            result = await conn.execute(check_company_name_query, {
                "company_name": companyName
            })
            existing = result.fetchone()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="该供应商名称已被使用，不允许重复注册"
                )
            
            # 检查营业执照编号是否已存在（排除已注销的承包商）
            check_license_number_query = text("""
                SELECT contractor_id FROM contractor_info 
                WHERE license_number = :license_number 
                AND is_deleted = false 
                AND business_status != '已注销'
            """)
            result = await conn.execute(check_license_number_query, {
                "license_number": licenseNumber.strip()
            })
            existing = result.fetchone()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="该营业执照编号已被使用，不允许重复注册"
                )
            
            # 检查users表中的username, phone, email（排除已删除的用户）
            # 检查用户名
            check_username_query = text("""
                SELECT user_id FROM users 
                WHERE username = :username AND is_deleted = false
            """)
            result = await conn.execute(check_username_query, {
                "username": adminUsername
            })
            existing = result.fetchone()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="该管理员用户名已被使用，不允许重复注册"
                )
            
            # 检查手机号
            if adminPhone:
                check_phone_query = text("""
                    SELECT user_id FROM users 
                    WHERE phone = :phone AND is_deleted = false
                """)
                result = await conn.execute(check_phone_query, {
                    "phone": adminPhone
                })
                existing = result.fetchone()
                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="该管理员手机号已被使用，不允许重复注册"
                    )
            
            # 检查邮箱
            if adminEmail:
                check_email_query = text("""
                    SELECT user_id FROM users 
                    WHERE email = :email AND is_deleted = false
                """)
                result = await conn.execute(check_email_query, {
                    "email": adminEmail
                })
                existing = result.fetchone()
                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="该管理员邮箱已被使用，不允许重复注册"
                    )
            
            
            # ========== 2. 处理文件上传 ==========
            # 这里可以保存文件到服务器，暂时只保存路径
            # 实际项目中应该保存文件并返回文件路径
            license_file_path = f"uploads/contractor/{datetime.now().strftime('%Y%m%d')}/{licenseFile.filename}"
            
            # ========== 3. 创建contractor_info表记录 ==========
            # 处理日期格式
            establish_date_value = None
            if establishDate:
                try:
                    establish_date_value = datetime.strptime(establishDate, "%Y-%m-%d").date()
                except ValueError:
                    pass  # 如果日期格式错误，设为None
            
            # 处理注册资本
            registered_capital_value = None
            if registeredCapital:
                try:
                    # 前端传入的是万元，需要转换为元
                    registered_capital_value = float(registeredCapital) * 10000
                except ValueError:
                    pass  # 如果转换失败，设为None
            
            insert_contractor_info_query = text("""
                INSERT INTO contractor_info (
                    license_file, license_number, company_name, company_type, company_address, legal_person,
                    establish_date, registered_capital, applicant_name,
                    business_status,
                    created_at, updated_at
                ) VALUES (
                    :license_file, :license_number, :company_name, :company_type, :company_address, :legal_person,
                    :establish_date, :registered_capital, :applicant_name,
                    :business_status,
                    :created_at, :updated_at
                ) RETURNING contractor_id
            """)
            
            result = await conn.execute(insert_contractor_info_query, {
                "license_file": license_file_path,
                "license_number": licenseNumber.strip(),
                "company_name": companyName,
                "company_type": companyType,
                "company_address": companyAddress.strip(),
                "legal_person": legalPerson,
                "establish_date": establish_date_value,
                "registered_capital": registered_capital_value,
                "applicant_name": applicantName,
                "business_status": "待审核",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })
            
            contractor_id = result.fetchone()[0]
            
            # ========== 4. 创建users表记录（包含承包商用户信息） ==========
            password_hash = pwd.get_password_hash(adminPassword)
            
            insert_user_query = text("""
                INSERT INTO users (
                    username, password_hash, user_type, phone, email,
                    user_level, audit_status, temp_token,
                    name_str, role_type, role_level, user_status,
                    contractor_staff_id,
                    created_at, updated_at
                ) VALUES (
                    :username, :password_hash, :user_type, :phone, :email,
                    :user_level, :audit_status, :temp_token,
                    :name_str, :role_type, :role_level, :user_status,
                    :contractor_staff_id,
                    :created_at, :updated_at
                ) RETURNING user_id
            """)
            
            result = await conn.execute(insert_user_query, {
                "username": adminUsername,
                "password_hash": password_hash,
                "user_type": "contractor",
                "phone": adminPhone,
                "email": adminEmail,
                "user_level": -1,  # 待审核状态
                "audit_status": 3,  # 待审核状态
                "temp_token": tempToken,
                "name_str": adminUsername,  # 姓名
                "role_type": "admin",  # 管理员角色
                "role_level": 3,  # 承包商管理员（根据create_tables.sql注释：3 承包商管理员）
                "user_status": 2,  # 待审核（根据create_tables.sql注释：2 待审核）
                "contractor_staff_id": contractor_id,  # 直接赋值为contractor_info表的contractor_id
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })
            
            user_id = result.fetchone()[0]
            
            # ========== 5. 更新sys_only_id ==========
            # 更新users表的sys_only_id为user_id
            update_user_sys_id_query = text("UPDATE users SET sys_only_id = :user_id WHERE user_id = :user_id")
            await conn.execute(update_user_sys_id_query, {"user_id": user_id})
            
            print(f"✅ 承包商入驻申请提交成功")
            print(f"   承包商ID: {contractor_id}")
            print(f"   用户ID: {user_id}")
            print(f"   用户名: {adminUsername}")
            print(f"   公司名称: {companyName}")
            print(f"   审核状态: 待审核 (audit_status=3, business_status=待审核)")
            
            return {
                "message": "申请提交成功，等待审核",
                "contractor_id": contractor_id,
                "user_id": user_id,
                "application_status": "pending"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ 承包商入驻申请失败: {str(e)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"提交申请失败: {str(e)}"
            )

