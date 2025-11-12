"""
企业入驻申请路由
Enterprise settlement application routes
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


@router.post("/settlement/enterprise")
async def submit_enterprise_settlement(
    # 企业基本信息
    companyName: str = Form(...),
    legalPerson: str = Form(...),
    contactPhone: str = Form(...),
    address: str = Form(...),
    industryType: str = Form(...),
    employeeCount: str = Form(...),
    businessLicense: str = Form(...),
    licenseFile: Optional[UploadFile] = File(None),
    # 联系人信息
    contactName: str = Form(...),
    contactPosition: Optional[str] = Form(None),
    contactEmail: str = Form(...),
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
    提交企业入驻申请
    
    创建企业信息和管理员用户账号
    """
    print("\n" + "=" * 60)
    print("【企业入驻申请】")
    print(f"申请时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"企业名称: {companyName}")
    print(f"管理员用户名: {adminUsername}")
    print("=" * 60 + "\n")
    
    async with engine.begin() as conn:
        try:
            # ========== 1. 唯一性检查 ==========
            # 检查users表中的username, phone, email
            check_users_query = text("""
                SELECT user_id FROM users 
                WHERE username = :username OR phone = :phone OR email = :email
            """)
            result = await conn.execute(check_users_query, {
                "username": adminUsername,
                "phone": adminPhone,
                "email": adminEmail
            })
            existing = result.fetchone()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用户名、手机号或邮箱已被使用（users表）"
                )
            
            # 检查enterprise_user表中的name_str, phone, email
            check_enterprise_user_query = text("""
                SELECT user_id FROM enterprise_user 
                WHERE name_str = :name_str OR phone = :phone OR email = :email
            """)
            result = await conn.execute(check_enterprise_user_query, {
                "name_str": adminUsername,
                "phone": adminPhone,
                "email": adminEmail
            })
            existing = result.fetchone()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用户名、手机号或邮箱已被使用（enterprise_user表）"
                )
            
            # 检查contractor_user表中的name_str, phone
            check_contractor_user_query = text("""
                SELECT user_id FROM contractor_user 
                WHERE name_str = :name_str OR phone = :phone
            """)
            result = await conn.execute(check_contractor_user_query, {
                "name_str": adminUsername,
                "phone": adminPhone
            })
            existing = result.fetchone()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用户名或手机号已被使用（contractor_user表）"
                )
            
            # ========== 2. 处理文件上传 ==========
            license_file_path = ""
            if licenseFile:
                # 这里可以保存文件到服务器，暂时只保存路径
                # 实际项目中应该保存文件并返回文件路径
                license_file_path = f"uploads/enterprise/{datetime.now().strftime('%Y%m%d')}/{licenseFile.filename}"
            else:
                # 如果没有上传文件，使用默认值或必填
                license_file_path = f"pending_{businessLicense}"
            
            # ========== 3. 创建enterprise_info表记录 ==========
            insert_enterprise_info_query = text("""
                INSERT INTO enterprise_info (
                    license_file, company_name, company_type, legal_person,
                    business_status, applicant_name,
                    created_at, updated_at
                ) VALUES (
                    :license_file, :company_name, :company_type, :legal_person,
                    :business_status, :applicant_name,
                    :created_at, :updated_at
                ) RETURNING enterprise_id
            """)
            
            result = await conn.execute(insert_enterprise_info_query, {
                "license_file": license_file_path,
                "company_name": companyName,
                "company_type": industryType,  # 使用industryType作为company_type
                "legal_person": legalPerson,
                "business_status": "待审核",
                "applicant_name": contactName,  # 使用联系人姓名作为申请人
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })
            
            enterprise_id = result.fetchone()[0]
            
            # ========== 4. 创建enterprise_user表记录 ==========
            insert_enterprise_user_query = text("""
                INSERT INTO enterprise_user (
                    company_id, name_str, phone, email, position,
                    role_type, approval_level, status,
                    created_at, updated_at
                ) VALUES (
                    :company_id, :name_str, :phone, :email, :position,
                    :role_type, :approval_level, :status,
                    :created_at, :updated_at
                ) RETURNING user_id
            """)
            
            result = await conn.execute(insert_enterprise_user_query, {
                "company_id": enterprise_id,
                "name_str": adminUsername,  # 使用管理员用户名作为name_str
                "phone": adminPhone,
                "email": adminEmail,
                "position": contactPosition if contactPosition else "管理员",
                "role_type": "admin",  # 管理员角色
                "approval_level": 4,  # 默认审批级别
                "status": 1,  # 默认状态
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })
            
            enterprise_user_id = result.fetchone()[0]
            
            # ========== 5. 创建users表记录 ==========
            password_hash = pwd.get_password_hash(adminPassword)
            
            insert_user_query = text("""
                INSERT INTO users (
                    username, password_hash, user_type, phone, email,
                    user_level, audit_status, temp_token, enterprise_staff_id,
                    created_at, updated_at
                ) VALUES (
                    :username, :password_hash, :user_type, :phone, :email,
                    :user_level, :audit_status, :temp_token, :enterprise_staff_id,
                    :created_at, :updated_at
                ) RETURNING user_id
            """)
            
            result = await conn.execute(insert_user_query, {
                "username": adminUsername,
                "password_hash": password_hash,
                "user_type": "enterprise",
                "phone": adminPhone,
                "email": adminEmail,
                "user_level": -1,  # 按用户要求设置为-1
                "audit_status": 3,  # 待审核状态
                "temp_token": tempToken,
                "enterprise_staff_id": enterprise_user_id,  # 关联enterprise_user的user_id
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })
            
            user_id = result.fetchone()[0]
            
            # ========== 6. 更新sys_only_id ==========
            # 更新users表的sys_only_id为user_id
            update_user_sys_id_query = text("UPDATE users SET sys_only_id = :user_id WHERE user_id = :user_id")
            await conn.execute(update_user_sys_id_query, {"user_id": user_id})
            
            # 更新enterprise_user表的sys_only_id为enterprise_user_id
            update_enterprise_user_sys_id_query = text("UPDATE enterprise_user SET sys_only_id = :enterprise_user_id WHERE user_id = :enterprise_user_id")
            await conn.execute(update_enterprise_user_sys_id_query, {"enterprise_user_id": enterprise_user_id})
            
            print(f"✅ 企业入驻申请提交成功")
            print(f"   企业ID: {enterprise_id}")
            print(f"   企业用户ID: {enterprise_user_id}")
            print(f"   用户ID: {user_id}")
            print(f"   用户名: {adminUsername}")
            print(f"   企业名称: {companyName}")
            print(f"   审核状态: 待审核 (audit_status=3, business_status=待审核)")
            
            return {
                "message": "申请提交成功，等待审核",
                "enterprise_id": enterprise_id,
                "enterprise_user_id": enterprise_user_id,
                "user_id": user_id,
                "application_status": "pending"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ 企业入驻申请失败: {str(e)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"提交申请失败: {str(e)}"
            )

