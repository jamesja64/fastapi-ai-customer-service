from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token
from app.core.config import settings
from app.schemas.user import UserCreate, User, Token, LoginRequest
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["認證"])


@router.post("/register", response_model=User, summary="用戶註冊")
async def register(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    用戶註冊
    
    - **username**: 用戶名（唯一）
    - **email**: 郵箱地址（唯一）
    - **password**: 密碼（至少8個字符）
    - **full_name**: 全名（可選）
    - **phone**: 電話號碼（可選）
    """
    try:
        user = await UserService.create_user(db, user_create)
        
        # 為新用戶分配默認角色
        await UserService.assign_role_to_user(db, user.id, "user")
        
        # 重新獲取用戶以包含角色信息
        user = await UserService.get_user_by_id(db, user.id)
        
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token, summary="用戶登入")
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    用戶登入
    
    - **username**: 用戶名
    - **password**: 密碼
    
    返回 JWT access token
    """
    user = await UserService.authenticate_user(
        db, login_data.username, login_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用戶名或密碼錯誤",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用戶已被停用"
        )
    
    # 創建 access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/login/form", response_model=Token, summary="表單登入")
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    OAuth2 表單登入（兼容 FastAPI 文檔界面）
    """
    user = await UserService.authenticate_user(
        db, form_data.username, form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用戶名或密碼錯誤",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用戶已被停用"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }
