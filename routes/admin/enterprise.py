"""
企业管理路由 (系统管理员)
Enterprise management routes for system admin
"""
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select, and_

from api.model import (
    Enterprise,
    EnterpriseListItem,
    User,
    UserType,
    EnterpriseUser
)
from core import password as pwd
from db import crud
from db.models import Company, EnterpriseUser as EnterpriseUserDB
from routes.dependencies import get_current_user

router = APIRouter()


def verify_admin(user: User = Depends(get_current_user)):
    """验证系统管理员权限"""
    if user.user_type != UserType.admin:
        raise HTTPException(status_code=403, detail="需要系统管理员权限")
    return user


@router.post("/", dependencies=[Depends(verify_admin)])
async def create_enterprise(enterprise: Enterprise):
    """
    创建企业
    
    系统管理员创建新企业，企业初始状态为待审批
    """
    from main import app
    
    try:
        enterprise_db = await crud.create_enterprise(app.state.engine, enterprise)
        return {
            "message": "企业创建成功",
            "company_id": enterprise_db.company_id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"创建企业失败: {str(e)}")


@router.get("/")
async def get_enterprises(
    status: Optional[str] = Query(default=None, description="状态筛选: pending(待审批), approved(已批准), rejected(已拒绝)"),
    keyword: Optional[str] = Query(default=None, description="搜索关键词（企业名称）"),
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
    user: User = Depends(verify_admin)
) -> dict:
    """
    获取企业列表
    
    系统管理员可以查看所有企业，支持按状态筛选和搜索
    """
    from main import app
    
    try:
        async with app.state.engine.begin() as conn:
            # 构建查询
            query = select(Company)
            
            # 添加筛选条件
            conditions = []
            if status:
                conditions.append(Company.status == status)
            if keyword:
                conditions.append(Company.name.contains(keyword))
            
            if conditions:
                query = query.where(and_(*conditions))
            
            # 计算总数
            count_result = await conn.execute(
                select(Company).where(and_(*conditions)) if conditions else select(Company)
            )
            total = len(count_result.all())
            
            # 分页查询
            query = query.offset((page - 1) * page_size).limit(page_size)
            result = await conn.execute(query)
            enterprises = result.scalars().all()
            
            # 转换为响应格式
            items = [
                EnterpriseListItem(
                    company_id=ent.company_id,
                    name=ent.name,
                    type=ent.type,
                    status=getattr(ent, 'status', 'approved'),  # 默认为已批准
                    contact_person=getattr(ent, 'contact_person', None),
                    contact_phone=getattr(ent, 'contact_phone', None),
                    created_at=ent.created_at.isoformat() if hasattr(ent, 'created_at') else None
                ) for ent in enterprises
            ]
            
            return {
                "total": total,
                "page": page,
                "page_size": page_size,
                "items": items
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取企业列表失败: {str(e)}")


@router.get("/{company_id}/")
async def get_enterprise_detail(
    company_id: int,
    user: User = Depends(verify_admin)
):
    """
    获取企业详情
    
    查看企业的详细信息，包括部门数、员工数等统计信息
    """
    from main import app
    
    try:
        async with app.state.engine.begin() as conn:
            # 查询企业信息
            query = select(Company).where(Company.company_id == company_id)
            result = await conn.execute(query)
            enterprise = result.scalar_one_or_none()
            
            if not enterprise:
                raise HTTPException(status_code=404, detail="企业不存在")
            
            # 统计部门数量
            from db.models import Department
            dept_query = select(Department).where(Department.company_id == company_id)
            dept_result = await conn.execute(dept_query)
            department_count = len(dept_result.all())
            
            # 统计员工数量
            staff_query = select(EnterpriseUserDB).where(EnterpriseUserDB.company_id == company_id)
            staff_result = await conn.execute(staff_query)
            staff_count = len(staff_result.all())
            
            return {
                "company_id": enterprise.company_id,
                "name": enterprise.name,
                "type": enterprise.type,
                "address": getattr(enterprise, 'address', None),
                "contact_person": getattr(enterprise, 'contact_person', None),
                "contact_phone": getattr(enterprise, 'contact_phone', None),
                "status": getattr(enterprise, 'status', 'approved'),
                "department_count": department_count,
                "staff_count": staff_count,
                "created_at": enterprise.created_at.isoformat() if hasattr(enterprise, 'created_at') else None,
                "updated_at": enterprise.updated_at.isoformat() if hasattr(enterprise, 'updated_at') else None
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取企业详情失败: {str(e)}")


@router.put("/{company_id}/", dependencies=[Depends(verify_admin)])
async def update_enterprise(company_id: int, enterprise_data: Enterprise):
    """
    更新企业信息
    
    系统管理员可以修改企业的基本信息
    """
    from main import app
    
    try:
        async with app.state.engine.begin() as conn:
            # 查询企业
            query = select(Company).where(Company.company_id == company_id)
            result = await conn.execute(query)
            enterprise = result.scalar_one_or_none()
            
            if not enterprise:
                raise HTTPException(status_code=404, detail="企业不存在")
            
            # 更新字段
            update_data = enterprise_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                if hasattr(enterprise, key) and value is not None:
                    setattr(enterprise, key, value)
            
            if hasattr(enterprise, 'updated_at'):
                enterprise.updated_at = datetime.now()
            
            await conn.commit()
            
            return {"message": "企业信息更新成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"更新企业信息失败: {str(e)}")


@router.delete("/{company_id}/", dependencies=[Depends(verify_admin)])
async def delete_enterprise(company_id: int):
    """
    删除企业
    
    软删除企业，将状态设置为 deleted
    注意：删除前需要确保企业下没有活跃的员工和项目
    """
    from main import app
    
    try:
        async with app.state.engine.begin() as conn:
            # 查询企业
            query = select(Company).where(Company.company_id == company_id)
            result = await conn.execute(query)
            enterprise = result.scalar_one_or_none()
            
            if not enterprise:
                raise HTTPException(status_code=404, detail="企业不存在")
            
            # 检查是否有活跃员工
            staff_query = select(EnterpriseUserDB).where(
                and_(
                    EnterpriseUserDB.company_id == company_id,
                    EnterpriseUserDB.status == True
                )
            )
            staff_result = await conn.execute(staff_query)
            active_staff = staff_result.all()
            
            if active_staff:
                raise HTTPException(
                    status_code=400, 
                    detail=f"无法删除企业，还有 {len(active_staff)} 个活跃员工"
                )
            
            # 软删除
            if hasattr(enterprise, 'status'):
                enterprise.status = 'deleted'
            if hasattr(enterprise, 'updated_at'):
                enterprise.updated_at = datetime.now()
            
            await conn.commit()
            
            return {"message": "企业删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"删除企业失败: {str(e)}")


@router.post("/{company_id}/approve/", dependencies=[Depends(verify_admin)])
async def approve_enterprise(
    company_id: int,
    approved: bool = Query(description="true=批准, false=拒绝"),
    comment: Optional[str] = Query(default=None, description="审批意见")
):
    """
    审批企业注册
    
    系统管理员审批企业的注册申请
    """
    from main import app
    
    try:
        async with app.state.engine.begin() as conn:
            # 查询企业
            query = select(Company).where(Company.company_id == company_id)
            result = await conn.execute(query)
            enterprise = result.scalar_one_or_none()
            
            if not enterprise:
                raise HTTPException(status_code=404, detail="企业不存在")
            
            # 更新状态
            if hasattr(enterprise, 'status'):
                enterprise.status = 'approved' if approved else 'rejected'
            if hasattr(enterprise, 'approval_comment'):
                enterprise.approval_comment = comment
            if hasattr(enterprise, 'approval_time'):
                enterprise.approval_time = datetime.now()
            if hasattr(enterprise, 'updated_at'):
                enterprise.updated_at = datetime.now()
            
            await conn.commit()
            
            status_text = "批准" if approved else "拒绝"
            return {
                "message": f"企业注册已{status_text}",
                "status": enterprise.status if hasattr(enterprise, 'status') else None
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"审批企业失败: {str(e)}")


@router.post("/{company_id}/admin/", dependencies=[Depends(verify_admin)])
async def create_enterprise_admin(
    company_id: int,
    admin_data: EnterpriseUser
):
    """
    为企业创建超级管理员
    
    系统管理员为新批准的企业创建第一个管理员账户
    """
    from main import app
    
    try:
        # 验证企业存在
        async with app.state.engine.begin() as conn:
            query = select(Company).where(Company.company_id == company_id)
            result = await conn.execute(query)
            enterprise = result.scalar_one_or_none()
            
            if not enterprise:
                raise HTTPException(status_code=404, detail="企业不存在")
        
        # 设置为管理员角色
        admin_data.enterprise_id = company_id
        admin_data.role_type = "manager"
        admin_data.status = True
        
        # 创建用户账号
        user = User(
            user_type=UserType.enterprise,
            username=admin_data.phone,
            password_hash=pwd.get_password_hash(admin_data.phone[-6:])  # 默认密码为手机号后6位
        )
        
        enterprise_user_db = await crud.create_enterprise_user(
            app.state.engine, admin_data, user
        )
        
        return {
            "message": "企业管理员创建成功",
            "user_id": enterprise_user_db.user_id,
            "username": admin_data.phone,
            "default_password": admin_data.phone[-6:]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"创建企业管理员失败: {str(e)}")


@router.get("/{company_id}/admins/")
async def get_enterprise_admins(
    company_id: int,
    user: User = Depends(verify_admin)
) -> List[dict]:
    """
    获取企业管理员列表
    
    查看指定企业的所有管理员账户
    """
    from main import app
    
    try:
        async with app.state.engine.begin() as conn:
            # 查询企业管理员
            query = select(EnterpriseUserDB).where(
                and_(
                    EnterpriseUserDB.company_id == company_id,
                    EnterpriseUserDB.role_type == "manager"
                )
            )
            result = await conn.execute(query)
            admins = result.scalars().all()
            
            return [
                {
                    "user_id": admin.user_id,
                    "name": admin.name,
                    "phone": admin.phone,
                    "email": admin.email,
                    "position": admin.position,
                    "status": admin.status,
                    "created_at": admin.created_at.isoformat() if hasattr(admin, 'created_at') else None
                } for admin in admins
            ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取企业管理员列表失败: {str(e)}")

