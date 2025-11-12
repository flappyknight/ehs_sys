"""
管理员权限申请处理
Admin permission application handler
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text

from api.model import User
from routes.dependencies import get_current_user, get_engine

router = APIRouter()


@router.post("/submit")
async def submit_permission_apply(
    apply_data: dict,
    engine: AsyncEngine = Depends(get_engine),
    current_user: User = Depends(get_current_user)
):
    """
    提交管理员权限申请
    
    只有admin用户且user_level=-1或audit_status=1时可以提交
    """
    if current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以提交权限申请"
        )
    
    # 检查用户状态
    if current_user.user_level != -1 and current_user.audit_status != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前状态不允许提交权限申请"
        )
    
    print("\n" + "🔵" * 30)
    print("【管理员权限申请提交】")
    print(f"用户ID: {current_user.user_id}")
    print(f"用户名: {current_user.username}")
    print(f"申请时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"申请数据: {apply_data}")
    print("🔵" * 30 + "\n")
    
    # 更新用户状态
    async with engine.begin() as conn:
        # 更新user_level为0（表示已提交申请），audit_status为3（待审核）
        update_query = text("""
            UPDATE users 
            SET user_level = 0, 
                audit_status = 3,
                updated_at = :updated_at
            WHERE user_id = :user_id
        """)
        
        await conn.execute(update_query, {
            "user_id": current_user.user_id,
            "updated_at": datetime.now()
        })
        
        print(f"✅ 权限申请已提交: user_id={current_user.user_id}")
    
    return {
        "message": "权限申请已提交，等待审核",
        "user_id": current_user.user_id
    }

