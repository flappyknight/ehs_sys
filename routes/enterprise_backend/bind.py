"""
企业绑定信息处理
Enterprise binding handler
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text

from api.model import User
from routes.dependencies import get_current_user, get_engine

router = APIRouter()


@router.post("/submit")
async def submit_enterprise_bind(
    bind_data: dict,
    engine: AsyncEngine = Depends(get_engine),
    current_user: User = Depends(get_current_user)
):
    """
    提交企业绑定信息
    
    只有enterprise用户且audit_status=1时可以提交
    """
    if current_user.user_type != "enterprise":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有企业用户可以提交绑定信息"
        )
    
    # 检查用户状态
    if current_user.audit_status != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前状态不允许提交绑定信息"
        )
    
    print("\n" + "🟢" * 30)
    print("【企业绑定信息提交】")
    print(f"用户ID: {current_user.user_id}")
    print(f"用户名: {current_user.username}")
    print(f"提交时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"绑定数据: {bind_data}")
    print("🟢" * 30 + "\n")
    
    # TODO: 这里应该创建或更新企业信息表（enterprise_info）
    # 目前先更新用户状态为待审核
    
    async with engine.begin() as conn:
        # 更新audit_status为3（待审核）
        update_query = text("""
            UPDATE users 
            SET audit_status = 3,
                updated_at = :updated_at
            WHERE user_id = :user_id
        """)
        
        await conn.execute(update_query, {
            "user_id": current_user.user_id,
            "updated_at": datetime.now()
        })
        
        print(f"✅ 企业绑定信息已提交: user_id={current_user.user_id}")
    
    return {
        "message": "企业绑定信息已提交，等待审核",
        "user_id": current_user.user_id
    }

