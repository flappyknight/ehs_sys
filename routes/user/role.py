"""
角色管理路由
Role management routes
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, func

from api.model import (
    RoleInfo,
    RoleListItem,
    RolePermission,
    UserRoleUpdate,
    User,
    UserType,
    PermissionLevel
)
from db.models import EnterpriseUser, ContractorUser
from routes.dependencies import get_current_user, authenticate_enterprise_level

router = APIRouter()

# 角色定义
ENTERPRISE_ROLES = {
    "manager": {
        "role_name": "管理员",
        "description": "拥有所有权限，可以管理企业内所有资源",
        "permission_level": PermissionLevel.manager,
        "permissions": [
            "user.create", "user.read", "user.update", "user.delete",
            "department.create", "department.read", "department.update", "department.delete",
            "area.create", "area.read", "area.update", "area.delete",
            "ticket.create", "ticket.read", "ticket.update", "ticket.delete",
            "project.read", "project.update",
            "contractor.read"
        ]
    },
    "site_staff": {
        "role_name": "现场人员",
        "description": "现场作业人员，可以查看和操作工单",
        "permission_level": PermissionLevel.site_staff,
        "permissions": [
            "ticket.read", "ticket.create", "ticket.update",
            "project.read",
            "area.read"
        ]
    },
    "normal": {
        "role_name": "普通员工",
        "description": "普通员工，只能查看基本信息",
        "permission_level": PermissionLevel.site_staff,
        "permissions": [
            "ticket.read",
            "project.read",
            "area.read"
        ]
    }
}

CONTRACTOR_ROLES = {
    "approver": {
        "role_name": "审批员",
        "description": "承包商审批员，可以管理承包商用户和计划",
        "permission_level": PermissionLevel.approver,
        "permissions": [
            "user.create", "user.read", "user.update",
            "plan.create", "plan.read", "plan.update",
            "project.read"
        ]
    },
    "normal": {
        "role_name": "普通员工",
        "description": "承包商普通员工，只能查看基本信息",
        "permission_level": PermissionLevel.site_staff,
        "permissions": [
            "plan.read",
            "project.read"
        ]
    }
}


@router.get("/")
async def get_roles(
    user_type: UserType = None,
    user: User = Depends(get_current_user)
) -> List[RoleListItem]:
    """获取角色列表"""
    from main import app
    
    try:
        roles = []
        
        # 根据用户类型筛选角色
        if user_type == UserType.enterprise or user_type is None:
            async with app.state.engine.begin() as conn:
                for role_type, role_info in ENTERPRISE_ROLES.items():
                    # 统计使用该角色的用户数量
                    query = select(func.count(EnterpriseUser.user_id)).where(
                        EnterpriseUser.role_type == role_type
                    )
                    result = await conn.execute(query)
                    user_count = result.scalar() or 0
                    
                    roles.append(RoleListItem(
                        role_type=role_type,
                        role_name=role_info["role_name"],
                        description=role_info["description"],
                        permission_level=role_info["permission_level"],
                        user_count=user_count
                    ))
        
        if user_type == UserType.contractor or user_type is None:
            # 只有管理员可以查看承包商角色
            if user.user_type == UserType.admin:
                async with app.state.engine.begin() as conn:
                    for role_type, role_info in CONTRACTOR_ROLES.items():
                        # 统计使用该角色的用户数量
                        query = select(func.count(ContractorUser.user_id)).where(
                            ContractorUser.role_type == role_type
                        )
                        result = await conn.execute(query)
                        user_count = result.scalar() or 0
                        
                        roles.append(RoleListItem(
                            role_type=role_type,
                            role_name=role_info["role_name"],
                            description=role_info["description"],
                            permission_level=role_info["permission_level"],
                            user_count=user_count
                        ))
        
        return roles
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取角色列表失败: {str(e)}")


@router.get("/{role_type}/")
async def get_role_detail(
    role_type: str,
    user: User = Depends(get_current_user)
) -> RoleInfo:
    """获取角色详情"""
    try:
        # 查找角色
        role_info = None
        user_type = None
        
        if role_type in ENTERPRISE_ROLES:
            role_info = ENTERPRISE_ROLES[role_type]
            user_type = UserType.enterprise
        elif role_type in CONTRACTOR_ROLES:
            if user.user_type != UserType.admin:
                raise HTTPException(status_code=403, detail="无权访问承包商角色信息")
            role_info = CONTRACTOR_ROLES[role_type]
            user_type = UserType.contractor
        
        if not role_info:
            raise HTTPException(status_code=404, detail="角色不存在")
        
        return RoleInfo(
            role_type=role_type,
            role_name=role_info["role_name"],
            description=role_info["description"],
            permission_level=role_info["permission_level"],
            user_type=user_type
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取角色详情失败: {str(e)}")


@router.get("/{role_type}/permissions/")
async def get_role_permissions(
    role_type: str,
    user: User = Depends(get_current_user)
) -> RolePermission:
    """获取角色权限列表"""
    try:
        # 查找角色
        permissions = None
        
        if role_type in ENTERPRISE_ROLES:
            permissions = ENTERPRISE_ROLES[role_type]["permissions"]
        elif role_type in CONTRACTOR_ROLES:
            if user.user_type != UserType.admin:
                raise HTTPException(status_code=403, detail="无权访问承包商角色权限")
            permissions = CONTRACTOR_ROLES[role_type]["permissions"]
        
        if permissions is None:
            raise HTTPException(status_code=404, detail="角色不存在")
        
        return RolePermission(
            role_type=role_type,
            permissions=permissions
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取角色权限失败: {str(e)}")


@router.put("/{user_id}/role/", dependencies=[Depends(authenticate_enterprise_level)])
async def update_user_role(
    user_id: int,
    role_data: UserRoleUpdate,
    current_user: User = Depends(get_current_user)
):
    """更新用户角色"""
    from main import app
    
    try:
        async with app.state.engine.begin() as conn:
            # 尝试查询企业用户
            eu_query = select(EnterpriseUser).where(EnterpriseUser.user_id == user_id)
            result = await conn.execute(eu_query)
            eu = result.scalar_one_or_none()
            
            if eu:
                # 验证角色是否存在
                if role_data.role_type not in ENTERPRISE_ROLES:
                    raise HTTPException(status_code=400, detail="无效的角色类型")
                
                # 权限检查
                if current_user.user_type == UserType.enterprise:
                    if eu.company_id != current_user.enterprise_user.enterprise_id:
                        raise HTTPException(status_code=403, detail="无权修改该用户角色")
                
                eu.role_type = role_data.role_type
                await conn.commit()
                return {"message": "用户角色更新成功"}
            
            # 尝试查询承包商用户
            cu_query = select(ContractorUser).where(ContractorUser.user_id == user_id)
            result = await conn.execute(cu_query)
            cu = result.scalar_one_or_none()
            
            if cu:
                # 验证角色是否存在
                if role_data.role_type not in CONTRACTOR_ROLES:
                    raise HTTPException(status_code=400, detail="无效的角色类型")
                
                # 只有管理员可以修改承包商用户角色
                if current_user.user_type != UserType.admin:
                    raise HTTPException(status_code=403, detail="无权修改该用户角色")
                
                cu.role_type = role_data.role_type
                await conn.commit()
                return {"message": "用户角色更新成功"}
            
            raise HTTPException(status_code=404, detail="用户不存在")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"更新用户角色失败: {str(e)}")


@router.get("/enterprise/available/")
async def get_enterprise_available_roles(
    user: User = Depends(get_current_user)
) -> List[RoleInfo]:
    """获取企业可用角色列表"""
    try:
        roles = []
        for role_type, role_info in ENTERPRISE_ROLES.items():
            roles.append(RoleInfo(
                role_type=role_type,
                role_name=role_info["role_name"],
                description=role_info["description"],
                permission_level=role_info["permission_level"],
                user_type=UserType.enterprise
            ))
        return roles
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取可用角色失败: {str(e)}")


@router.get("/contractor/available/")
async def get_contractor_available_roles(
    user: User = Depends(get_current_user)
) -> List[RoleInfo]:
    """获取承包商可用角色列表"""
    try:
        if user.user_type != UserType.admin:
            raise HTTPException(status_code=403, detail="无权访问承包商角色")
        
        roles = []
        for role_type, role_info in CONTRACTOR_ROLES.items():
            roles.append(RoleInfo(
                role_type=role_type,
                role_name=role_info["role_name"],
                description=role_info["description"],
                permission_level=role_info["permission_level"],
                user_type=UserType.contractor
            ))
        return roles
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取可用角色失败: {str(e)}")

