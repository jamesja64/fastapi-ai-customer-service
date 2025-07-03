from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    """用戶基礎模式"""
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """用戶創建模式"""
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('密碼長度至少 8 個字符')
        return v


class UserUpdate(BaseModel):
    """用戶更新模式"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None


class UserInDB(UserBase):
    """資料庫中的用戶模式"""
    id: int
    hashed_password: str
    is_verified: bool
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class User(UserBase):
    """用戶響應模式"""
    id: int
    is_verified: bool
    avatar_url: Optional[str] = None
    created_at: datetime
    roles: List['Role'] = []
    
    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    """角色基礎模式"""
    name: str
    description: Optional[str] = None
    permissions: Optional[str] = None


class RoleCreate(RoleBase):
    """角色創建模式"""
    pass


class Role(RoleBase):
    """角色響應模式"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token 響應模式"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token 數據模式"""
    username: Optional[str] = None
    user_id: Optional[int] = None


class LoginRequest(BaseModel):
    """登入請求模式"""
    username: str
    password: str


# 解決前向引用
User.model_rebuild()
