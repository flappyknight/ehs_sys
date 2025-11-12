"""
承包商管理路由 (系统管理员)
Contractor management routes for system admin
"""
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select, and_

from api.model import (
    ContractorListItem,
    User,
    UserType,
    ContractorUser,
    ContractorInfo
)
from core import password as pwd
from db import crud
from db.models import ContractorInfo as ContractorDB, ContractorUser as ContractorUserDB
from routes.dependencies import get_current_user

router = APIRouter()


def verify_admin(user: User = Depends(get_current_user)):
    """验证系统管理员权限"""
    if user.user_type != UserType.admin:
        raise HTTPException(status_code=403, detail="需要系统管理员权限")
    return user


@router.post("/", dependencies=[Depends(verify_admin)])
async def create_contractor(contractor: ContractorInfo):
    """
    创建承包商
    
    系统管理员创建新承包商，承包商初始状态为待审批
    """
    from main import app
    
    try:
        contractor_db = await crud.create_contractor_info(app.state.engine, contractor)
        return {
            "message": "承包商创建成功",
            "contractor_id": contractor_db.contractor_id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"创建承包商失败: {str(e)}")


@router.get("/")
async def get_contractors(
    status: Optional[str] = Query(default=None, description="状态筛选: pending(待审批), approved(已批准), rejected(已拒绝)"),
    company_type: Optional[str] = Query(default=None, description="公司类型筛选"),
    keyword: Optional[str] = Query(default=None, description="搜索关键词（公司名称）"),
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
    user: User = Depends(verify_admin)
) -> dict:
    """
    获取承包商列表
    
    系统管理员可以查看所有承包商，支持按状态、类型筛选和搜索
    """
    from main import app
    
    try:
        async with app.state.engine.begin() as conn:
            # 构建查询
            query = select(ContractorDB)
            
            # 添加筛选条件
            conditions = []
            if status:
                conditions.append(ContractorDB.status == status)
            if company_type:
                conditions.append(ContractorDB.company_type == company_type)
            if keyword:
                conditions.append(ContractorDB.company_name.contains(keyword))
            
            if conditions:
                query = query.where(and_(*conditions))
            
            # 计算总数
            count_result = await conn.execute(query)
            total = len(count_result.all())
            
            # 分页查询
            query = query.offset((page - 1) * page_size).limit(page_size)
            result = await conn.execute(query)
            contractors = result.scalars().all()
            
            # 转换为响应格式
            items = []
            for contractor in contractors:
                # 统计项目数量
                from db.models import Project
                project_query = select(Project).where(Project.contractor_id == contractor.contractor_id)
                project_result = await conn.execute(project_query)
                project_count = len(project_result.all())
                
                items.append(
                    ContractorListItem(
                        contractor_id=contractor.contractor_id,
                        company_name=contractor.company_name,
                        company_type=contractor.company_type,
                        legal_person=contractor.legal_person,
                        establish_date=str(contractor.establish_date),
                        status=getattr(contractor, 'status', 'approved'),
                        project_count=project_count,
                        created_at=contractor.created_at.isoformat() if hasattr(contractor, 'created_at') else None
                    )
                )
            
            return {
                "total": total,
                "page": page,
                "page_size": page_size,
                "items": items
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取承包商列表失败: {str(e)}")


@router.get("/{contractor_id}/")
async def get_contractor_detail(
    contractor_id: int,
    user: User = Depends(verify_admin)
):
    """
    获取承包商详情
    
    查看承包商的详细信息，包括项目数、员工数等统计信息
    """
    from main import app
    
    try:
        async with app.state.engine.begin() as conn:
            # 查询承包商信息
            query = select(ContractorDB).where(ContractorDB.contractor_id == contractor_id)
            result = await conn.execute(query)
            contractor = result.scalar_one_or_none()
            
            if not contractor:
                raise HTTPException(status_code=404, detail="承包商不存在")
            
            # 统计项目数量
            from db.models import Project
            project_query = select(Project).where(Project.contractor_id == contractor_id)
            project_result = await conn.execute(project_query)
            project_count = len(project_result.all())
            
            # 统计员工数量
            staff_query = select(ContractorUserDB).where(ContractorUserDB.contractor_id == contractor_id)
            staff_result = await conn.execute(staff_query)
            staff_count = len(staff_result.all())
            
            return {
                "contractor_id": contractor.contractor_id,
                "company_name": contractor.company_name,
                "company_type": contractor.company_type,
                "legal_person": contractor.legal_person,
                "establish_date": str(contractor.establish_date),
                "business_license": getattr(contractor, 'business_license', None),
                "contact_person": getattr(contractor, 'contact_person', None),
                "contact_phone": getattr(contractor, 'contact_phone', None),
                "status": getattr(contractor, 'status', 'approved'),
                "project_count": project_count,
                "staff_count": staff_count,
                "created_at": contractor.created_at.isoformat() if hasattr(contractor, 'created_at') else None,
                "updated_at": contractor.updated_at.isoformat() if hasattr(contractor, 'updated_at') else None
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取承包商详情失败: {str(e)}")


@router.put("/{contractor_id}/", dependencies=[Depends(verify_admin)])
async def update_contractor(contractor_id: int, contractor_data: ContractorInfo):
    """
    更新承包商信息
    
    系统管理员可以修改承包商的基本信息
    """
    from main import app
    
    try:
        async with app.state.engine.begin() as conn:
            # 查询承包商
            query = select(ContractorDB).where(ContractorDB.contractor_id == contractor_id)
            result = await conn.execute(query)
            contractor = result.scalar_one_or_none()
            
            if not contractor:
                raise HTTPException(status_code=404, detail="承包商不存在")
            
            # 更新字段
            update_data = contractor_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                if hasattr(contractor, key) and value is not None:
                    setattr(contractor, key, value)
            
            if hasattr(contractor, 'updated_at'):
                contractor.updated_at = datetime.now()
            
            await conn.commit()
            
            return {"message": "承包商信息更新成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"更新承包商信息失败: {str(e)}")


@router.delete("/{contractor_id}/", dependencies=[Depends(verify_admin)])
async def delete_contractor(contractor_id: int):
    """
    删除承包商
    
    软删除承包商，将状态设置为 deleted
    注意：删除前需要确保承包商下没有活跃的员工和项目
    """
    from main import app
    
    try:
        async with app.state.engine.begin() as conn:
            # 查询承包商
            query = select(ContractorDB).where(ContractorDB.contractor_id == contractor_id)
            result = await conn.execute(query)
            contractor = result.scalar_one_or_none()
            
            if not contractor:
                raise HTTPException(status_code=404, detail="承包商不存在")
            
            # 检查是否有活跃员工
            staff_query = select(ContractorUserDB).where(
                and_(
                    ContractorUserDB.contractor_id == contractor_id,
                    ContractorUserDB.status == True
                )
            )
            staff_result = await conn.execute(staff_query)
            active_staff = staff_result.all()
            
            if active_staff:
                raise HTTPException(
                    status_code=400, 
                    detail=f"无法删除承包商，还有 {len(active_staff)} 个活跃员工"
                )
            
            # 检查是否有进行中的项目
            from db.models import Project
            project_query = select(Project).where(
                and_(
                    Project.contractor_id == contractor_id,
                    Project.status == 'active'
                )
            )
            project_result = await conn.execute(project_query)
            active_projects = project_result.all()
            
            if active_projects:
                raise HTTPException(
                    status_code=400, 
                    detail=f"无法删除承包商，还有 {len(active_projects)} 个进行中的项目"
                )
            
            # 软删除
            if hasattr(contractor, 'status'):
                contractor.status = 'deleted'
            if hasattr(contractor, 'updated_at'):
                contractor.updated_at = datetime.now()
            
            await conn.commit()
            
            return {"message": "承包商删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"删除承包商失败: {str(e)}")


@router.post("/{contractor_id}/approve/", dependencies=[Depends(verify_admin)])
async def approve_contractor(
    contractor_id: int,
    approved: bool = Query(description="true=批准, false=拒绝"),
    comment: Optional[str] = Query(default=None, description="审批意见")
):
    """
    审批承包商注册
    
    系统管理员审批承包商的注册申请
    """
    from main import app
    
    try:
        async with app.state.engine.begin() as conn:
            # 查询承包商
            query = select(ContractorDB).where(ContractorDB.contractor_id == contractor_id)
            result = await conn.execute(query)
            contractor = result.scalar_one_or_none()
            
            if not contractor:
                raise HTTPException(status_code=404, detail="承包商不存在")
            
            # 更新状态
            if hasattr(contractor, 'status'):
                contractor.status = 'approved' if approved else 'rejected'
            if hasattr(contractor, 'approval_comment'):
                contractor.approval_comment = comment
            if hasattr(contractor, 'approval_time'):
                contractor.approval_time = datetime.now()
            if hasattr(contractor, 'updated_at'):
                contractor.updated_at = datetime.now()
            
            await conn.commit()
            
            status_text = "批准" if approved else "拒绝"
            return {
                "message": f"承包商注册已{status_text}",
                "status": contractor.status if hasattr(contractor, 'status') else None
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"审批承包商失败: {str(e)}")


@router.post("/{contractor_id}/admin/", dependencies=[Depends(verify_admin)])
async def create_contractor_admin(
    contractor_id: int,
    admin_data: ContractorUser
):
    """
    为承包商创建超级管理员
    
    系统管理员为新批准的承包商创建第一个管理员账户
    """
    from main import app
    
    try:
        # 验证承包商存在
        async with app.state.engine.begin() as conn:
            query = select(ContractorDB).where(ContractorDB.contractor_id == contractor_id)
            result = await conn.execute(query)
            contractor = result.scalar_one_or_none()
            
            if not contractor:
                raise HTTPException(status_code=404, detail="承包商不存在")
        
        # 设置为管理员角色
        admin_data.contractor_id = contractor_id
        admin_data.role_type = "approver"  # 承包商管理员
        admin_data.status = True
        
        # 创建用户账号
        user = User(
            user_type=UserType.contractor,
            username=admin_data.phone,
            password_hash=pwd.get_password_hash(admin_data.phone[-6:])  # 默认密码为手机号后6位
        )
        
        contractor_user_db = await crud.create_contractor_user(
            app.state.engine, admin_data, user
        )
        
        return {
            "message": "承包商管理员创建成功",
            "user_id": contractor_user_db.user_id,
            "username": admin_data.phone,
            "default_password": admin_data.phone[-6:]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"创建承包商管理员失败: {str(e)}")


@router.get("/{contractor_id}/admins/")
async def get_contractor_admins(
    contractor_id: int,
    user: User = Depends(verify_admin)
) -> List[dict]:
    """
    获取承包商管理员列表
    
    查看指定承包商的所有管理员账户
    """
    from main import app
    
    try:
        async with app.state.engine.begin() as conn:
            # 查询承包商管理员
            query = select(ContractorUserDB).where(
                and_(
                    ContractorUserDB.contractor_id == contractor_id,
                    ContractorUserDB.role_type == "approver"
                )
            )
            result = await conn.execute(query)
            admins = result.scalars().all()
            
            return [
                {
                    "user_id": admin.user_id,
                    "name": admin.name,
                    "phone": admin.phone,
                    "id_number": admin.id_number,
                    "work_type": admin.work_type,
                    "status": admin.status,
                    "created_at": admin.created_at.isoformat() if hasattr(admin, 'created_at') else None
                } for admin in admins
            ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取承包商管理员列表失败: {str(e)}")

