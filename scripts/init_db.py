#!/usr/bin/env python3
"""
資料庫初始化腳本
創建初始角色和管理員用戶
"""

import asyncio
import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal, init_db
from app.models.user import User, Role
from app.core.security import get_password_hash
from sqlalchemy import select


async def create_initial_roles():
    """創建初始角色"""
    async with AsyncSessionLocal() as db:
        # 檢查角色是否已存在
        result = await db.execute(select(Role))
        existing_roles = result.scalars().all()
        
        if existing_roles:
            print("角色已存在，跳過創建")
            return
        
        # 創建角色
        roles = [
            Role(
                name="admin",
                description="系統管理員",
                permissions='{"all": true}'
            ),
            Role(
                name="staff",
                description="客服人員",
                permissions='{"tickets": ["read", "write"], "chat": ["read", "write"]}'
            ),
            Role(
                name="user",
                description="普通用戶",
                permissions='{"tickets": ["read", "create"], "chat": ["read", "write"]}'
            )
        ]
        
        for role in roles:
            db.add(role)
        
        await db.commit()
        print("初始角色創建完成")


async def create_admin_user():
    """創建管理員用戶"""
    async with AsyncSessionLocal() as db:
        # 檢查管理員是否已存在
        result = await db.execute(
            select(User).where(User.username == "admin")
        )
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            print("管理員用戶已存在，跳過創建")
            return
        
        # 獲取管理員角色
        result = await db.execute(
            select(Role).where(Role.name == "admin")
        )
        admin_role = result.scalar_one_or_none()
        
        if not admin_role:
            print("錯誤：管理員角色不存在")
            return
        
        # 創建管理員用戶
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            full_name="系統管理員",
            is_active=True,
            is_verified=True
        )
        
        admin_user.roles.append(admin_role)
        db.add(admin_user)
        await db.commit()
        
        print("管理員用戶創建完成")
        print("用戶名: admin")
        print("密碼: admin123")
        print("請在生產環境中修改默認密碼！")


async def create_demo_users():
    """創建演示用戶"""
    async with AsyncSessionLocal() as db:
        # 獲取角色
        result = await db.execute(select(Role))
        roles = {role.name: role for role in result.scalars().all()}
        
        # 演示用戶數據
        demo_users = [
            {
                "username": "staff1",
                "email": "staff1@example.com",
                "password": "staff123",
                "full_name": "客服人員1",
                "role": "staff"
            },
            {
                "username": "user1",
                "email": "user1@example.com",
                "password": "user123",
                "full_name": "測試用戶1",
                "role": "user"
            },
            {
                "username": "user2",
                "email": "user2@example.com",
                "password": "user123",
                "full_name": "測試用戶2",
                "role": "user"
            }
        ]
        
        for user_data in demo_users:
            # 檢查用戶是否已存在
            result = await db.execute(
                select(User).where(User.username == user_data["username"])
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                continue
            
            # 創建用戶
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                full_name=user_data["full_name"],
                is_active=True,
                is_verified=True
            )
            
            # 分配角色
            if user_data["role"] in roles:
                user.roles.append(roles[user_data["role"]])
            
            db.add(user)
        
        await db.commit()
        print("演示用戶創建完成")


async def create_sample_faqs():
    """創建示例 FAQ"""
    from app.models.knowledge import FAQ
    
    async with AsyncSessionLocal() as db:
        # 檢查是否已有 FAQ
        result = await db.execute(select(FAQ))
        existing_faqs = result.scalars().all()
        
        if existing_faqs:
            print("FAQ 已存在，跳過創建")
            return
        
        # 示例 FAQ 數據
        sample_faqs = [
            {
                "question": "如何重設密碼？",
                "answer": "您可以在登入頁面點擊「忘記密碼」連結，輸入您的郵箱地址，系統會發送重設密碼的連結到您的郵箱。",
                "category": "帳戶管理",
                "tags": '["密碼", "重設", "帳戶"]'
            },
            {
                "question": "如何聯繫客服？",
                "answer": "您可以通過以下方式聯繫我們：1. 使用網站上的智能客服聊天功能 2. 發送郵件到 support@example.com 3. 撥打客服電話 0800-123-456",
                "category": "客服支援",
                "tags": '["客服", "聯繫", "支援"]'
            },
            {
                "question": "系統支援哪些瀏覽器？",
                "answer": "我們的系統支援以下瀏覽器的最新版本：Chrome、Firefox、Safari、Edge。建議使用 Chrome 以獲得最佳體驗。",
                "category": "技術支援",
                "tags": '["瀏覽器", "兼容性", "技術"]'
            },
            {
                "question": "如何創建工單？",
                "answer": "登入後，點擊「工單管理」→「創建工單」，填寫問題描述和相關信息，選擇優先級後提交即可。",
                "category": "工單管理",
                "tags": '["工單", "創建", "問題"]'
            },
            {
                "question": "AI 客服的工作時間是？",
                "answer": "我們的 AI 智能客服 24 小時全天候為您服務。如需人工客服協助，服務時間為週一至週五 9:00-18:00。",
                "category": "服務時間",
                "tags": '["AI", "客服", "時間"]'
            }
        ]
        
        for faq_data in sample_faqs:
            faq = FAQ(**faq_data)
            db.add(faq)
        
        await db.commit()
        print("示例 FAQ 創建完成")


async def main():
    """主函數"""
    print("開始初始化資料庫...")
    
    try:
        # 初始化資料庫表
        await init_db()
        print("資料庫表創建完成")
        
        # 創建初始角色
        await create_initial_roles()
        
        # 創建管理員用戶
        await create_admin_user()
        
        # 創建演示用戶
        await create_demo_users()
        
        # 創建示例 FAQ
        await create_sample_faqs()
        
        print("\n資料庫初始化完成！")
        print("\n可用的測試帳戶：")
        print("管理員 - 用戶名: admin, 密碼: admin123")
        print("客服人員 - 用戶名: staff1, 密碼: staff123")
        print("普通用戶 - 用戶名: user1, 密碼: user123")
        print("普通用戶 - 用戶名: user2, 密碼: user123")
        
    except Exception as e:
        print(f"初始化失敗: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
