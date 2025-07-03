from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from app.core.security import create_access_token, verify_password, get_password_hash
import json

router = APIRouter(prefix="/auth", tags=["認證"])
templates = Jinja2Templates(directory="templates")

# 簡單的內存用戶存儲（僅用於演示）
DEMO_USERS = {
    "admin": {
        "username": "admin",
        "email": "admin@example.com",
        "hashed_password": get_password_hash("admin123"),
        "full_name": "系統管理員",
        "is_active": True,
        "roles": ["admin"]
    },
    "user1": {
        "username": "user1",
        "email": "user1@example.com",
        "hashed_password": get_password_hash("user123"),
        "full_name": "測試用戶1",
        "is_active": True,
        "roles": ["user"]
    },
    "demo": {
        "username": "demo",
        "email": "demo@example.com",
        "hashed_password": get_password_hash("demo123"),
        "full_name": "演示用戶",
        "is_active": True,
        "roles": ["user"]
    }
}


class UserCreate(BaseModel):
    """用戶創建模式"""
    username: str
    email: str
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """用戶登入模式"""
    username: str
    password: str


class Token(BaseModel):
    """Token 響應模式"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class User(BaseModel):
    """用戶響應模式"""
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    roles: list


@router.get("/login", response_class=HTMLResponse, summary="登入頁面")
async def login_page(request: Request):
    """登入頁面"""
    return templates.TemplateResponse(
        "login.html", 
        {"request": request, "title": "用戶登入"}
    )


@router.get("/register", response_class=HTMLResponse, summary="註冊頁面")
async def register_page(request: Request):
    """註冊頁面"""
    return templates.TemplateResponse(
        "register.html", 
        {"request": request, "title": "用戶註冊"}
    )


@router.post("/login", response_model=Token, summary="用戶登入")
async def login(user_login: UserLogin):
    """
    用戶登入
    
    - **username**: 用戶名
    - **password**: 密碼
    
    演示帳戶：
    - admin / admin123 (管理員)
    - user1 / user123 (普通用戶)
    - demo / demo123 (演示用戶)
    """
    # 檢查用戶是否存在
    user = DEMO_USERS.get(user_login.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用戶名或密碼錯誤",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 驗證密碼
    if not verify_password(user_login.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用戶名或密碼錯誤",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 檢查用戶是否啟用
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用戶已被停用"
        )
    
    # 創建 access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user["username"], "user_id": user["username"]},
        expires_delta=access_token_expires
    )
    
    # 返回用戶信息（不包含密碼）
    user_info = {
        "username": user["username"],
        "email": user["email"],
        "full_name": user["full_name"],
        "is_active": user["is_active"],
        "roles": user["roles"]
    }
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 30 * 60,  # 30 分鐘
        "user": user_info
    }


@router.post("/register", response_model=User, summary="用戶註冊")
async def register(user_create: UserCreate):
    """
    用戶註冊（演示版本）
    
    - **username**: 用戶名（唯一）
    - **email**: 郵箱地址（唯一）
    - **password**: 密碼（至少6個字符）
    - **full_name**: 全名（可選）
    """
    # 檢查用戶名是否已存在
    if user_create.username in DEMO_USERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用戶名已存在"
        )
    
    # 檢查郵箱是否已存在
    for existing_user in DEMO_USERS.values():
        if existing_user["email"] == user_create.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="郵箱已存在"
            )
    
    # 密碼長度檢查
    if len(user_create.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密碼長度至少6個字符"
        )
    
    # 創建新用戶
    new_user = {
        "username": user_create.username,
        "email": user_create.email,
        "hashed_password": get_password_hash(user_create.password),
        "full_name": user_create.full_name,
        "is_active": True,
        "roles": ["user"]
    }
    
    # 添加到內存存儲
    DEMO_USERS[user_create.username] = new_user
    
    # 返回用戶信息（不包含密碼）
    return User(
        username=new_user["username"],
        email=new_user["email"],
        full_name=new_user["full_name"],
        is_active=new_user["is_active"],
        roles=new_user["roles"]
    )


@router.get("/users", summary="獲取所有用戶（演示）")
async def get_all_users():
    """獲取所有註冊用戶（僅用於演示）"""
    users = []
    for user_data in DEMO_USERS.values():
        users.append({
            "username": user_data["username"],
            "email": user_data["email"],
            "full_name": user_data["full_name"],
            "is_active": user_data["is_active"],
            "roles": user_data["roles"]
        })
    return {"users": users, "total": len(users)}


@router.get("/demo-accounts", summary="演示帳戶信息")
async def get_demo_accounts():
    """獲取可用的演示帳戶信息"""
    demo_accounts = [
        {
            "username": "admin",
            "password": "admin123",
            "role": "管理員",
            "description": "系統管理員帳戶，擁有所有權限"
        },
        {
            "username": "user1", 
            "password": "user123",
            "role": "普通用戶",
            "description": "普通用戶帳戶，基本功能權限"
        },
        {
            "username": "demo",
            "password": "demo123", 
            "role": "演示用戶",
            "description": "演示用戶帳戶，用於功能展示"
        }
    ]
    
    return {
        "message": "可用的演示帳戶",
        "accounts": demo_accounts,
        "note": "這些是預設的演示帳戶，您也可以註冊新帳戶"
    }
