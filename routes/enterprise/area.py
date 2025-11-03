"""
厂区管理路由
Area management routes
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from api.model import Area, AreaListItem, User, UserType
from db import crud
from routes.dependencies import (
    get_current_user, 
    authenticate_enterprise_level,
    get_user_enterprise_id
)

router = APIRouter()


@router.post("/", dependencies=[Depends(authenticate_enterprise_level)])
async def create_area(area: Area):
    """创建厂区"""
    from main import app
    
    try:
        area_db = await crud.create_area(app.state.engine, area)
        return {"message": "厂区创建成功", "area_id": area_db.area_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"创建厂区失败: {str(e)}")


@router.get("/")
async def get_areas(
    enterprise_id: int = Query(default=None, description="企业ID，不传则获取所有厂区"),
    user: User = Depends(get_current_user)
) -> List[AreaListItem]:
    """获取厂区列表"""
    from main import app
    
    try:
        # 如果是企业用户，只能查看自己企业的厂区
        if user.user_type == UserType.enterprise and user.enterprise_user:
            enterprise_id = user.enterprise_user.enterprise_id
        
        areas = await crud.get_area_list_with_details(app.state.engine, enterprise_id)
        return areas
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取厂区列表失败: {str(e)}")


@router.get("/{area_id}/")
async def get_area_detail(area_id: int, user: User = Depends(get_current_user)) -> Area:
    """获取厂区详情"""
    from main import app
    
    try:
        # 自动从用户身份获取企业ID
        enterprise_id = get_user_enterprise_id(user)
        
        area = await crud.get_area_by_id(app.state.engine, area_id)
        if not area:
            raise HTTPException(status_code=404, detail="厂区不存在")
        
        # 确保只能访问自己企业的厂区
        if area.enterprise_id != enterprise_id:
            raise HTTPException(status_code=403, detail="无权限访问该厂区")
        
        return Area(
            area_id=area.area_id,
            area_name=area.area_name,
            dept_id=area.dept_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取厂区详情失败: {str(e)}")


@router.put("/{area_id}/", dependencies=[Depends(authenticate_enterprise_level)])
async def update_area(area_id: int, area_data: Area, user: User = Depends(get_current_user)):
    """更新厂区信息"""
    from main import app
    
    try:
        # 自动从用户身份获取企业ID
        enterprise_id = get_user_enterprise_id(user)
        
        # 检查厂区是否存在且属于当前企业
        existing_area = await crud.get_area_by_id(app.state.engine, area_id)
        if not existing_area:
            raise HTTPException(status_code=404, detail="厂区不存在")
        
        if existing_area.enterprise_id != enterprise_id:
            raise HTTPException(status_code=403, detail="无权限修改该厂区")
        
        # 创建更新数据，确保企业ID不变
        update_data = Area(
            area_name=area_data.area_name,
            enterprise_id=enterprise_id,  # 确保企业ID不变
            dept_id=area_data.dept_id
        )
        
        updated_area = await crud.update_area(app.state.engine, area_id, update_data)
        if not updated_area:
            raise HTTPException(status_code=404, detail="更新失败")
        
        return {"message": "厂区更新成功", "area_id": updated_area.area_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"更新厂区失败: {str(e)}")


@router.delete("/{area_id}/", dependencies=[Depends(authenticate_enterprise_level)])
async def delete_area(area_id: int, user: User = Depends(get_current_user)):
    """删除厂区"""
    from main import app
    
    try:
        # 自动从用户身份获取企业ID
        enterprise_id = get_user_enterprise_id(user)
        
        # 检查厂区是否存在且属于当前企业
        existing_area = await crud.get_area_by_id(app.state.engine, area_id)
        if not existing_area:
            raise HTTPException(status_code=404, detail="厂区不存在")
        
        if existing_area.enterprise_id != enterprise_id:
            raise HTTPException(status_code=403, detail="无权限删除该厂区")
        
        success = await crud.delete_area(app.state.engine, area_id)
        if not success:
            raise HTTPException(status_code=404, detail="删除失败")
        
        return {"message": "厂区删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"删除厂区失败: {str(e)}")


@router.get("/by-department/{dept_id}/")
async def get_department_areas(dept_id: int, user: User = Depends(get_current_user)) -> List[Area]:
    """获取指定部门的厂区（仅限当前企业）"""
    from main import app
    
    try:
        # 自动从用户身份获取企业ID
        enterprise_id = get_user_enterprise_id(user)
        
        areas = await crud.get_areas_by_department(app.state.engine, dept_id)
        
        # 过滤出属于当前企业的厂区
        filtered_areas = [
            area for area in areas 
            if area.enterprise_id == enterprise_id
        ]
        
        return [
            Area(
                area_id=area.area_id,
                area_name=area.area_name,
                dept_id=area.dept_id
            ) for area in filtered_areas
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取部门厂区失败: {str(e)}")

