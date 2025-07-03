from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional
from app.models.user import User, Role
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class UserService:
    """用戶服務類"""
    
    @staticmethod
    async def create_user(db: AsyncSession, user_create: UserCreate) -> User:
        """創建新用戶"""
        # 檢查用戶名是否已存在
        existing_user = await UserService.get_user_by_username(
            db, user_create.username
        )
        if existing_user:
            raise ValueError("用戶名已存在")
        
        # 檢查郵箱是否已存在
        existing_email = await UserService.get_user_by_email(
            db, user_create.email
        )
        if existing_email:
            raise ValueError("郵箱已存在")
        
        # 創建用戶
        hashed_password = get_password_hash(user_create.password)
        db_user = User(
            username=user_create.username,
            email=user_create.email,
            hashed_password=hashed_password,
            full_name=user_create.full_name,
            phone=user_create.phone,
            is_active=user_create.is_active
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """根據 ID 獲取用戶"""
        result = await db.execute(
            select(User)
            .options(selectinload(User.roles))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_username(
        db: AsyncSession, username: str
    ) -> Optional[User]:
        """根據用戶名獲取用戶"""
        result = await db.execute(
            select(User)
            .options(selectinload(User.roles))
            .where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """根據郵箱獲取用戶"""
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def authenticate_user(
        db: AsyncSession, username: str, password: str
    ) -> Optional[User]:
        """驗證用戶登入"""
        user = await UserService.get_user_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    async def update_user(
        db: AsyncSession, user_id: int, user_update: UserUpdate
    ) -> Optional[User]:
        """更新用戶信息"""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def deactivate_user(db: AsyncSession, user_id: int) -> bool:
        """停用用戶"""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            return False
        
        user.is_active = False
        await db.commit()
        return True
    
    @staticmethod
    async def assign_role_to_user(
        db: AsyncSession, user_id: int, role_name: str
    ) -> bool:
        """為用戶分配角色"""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            return False
        
        result = await db.execute(select(Role).where(Role.name == role_name))
        role = result.scalar_one_or_none()
        if not role:
            return False
        
        if role not in user.roles:
            user.roles.append(role)
            await db.commit()
        
        return True
