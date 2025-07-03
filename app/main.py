from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
from contextlib import asynccontextmanager

from app.core.config import settings
from app.services.ai_service import AIService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用生命週期管理"""
    # 啟動時執行
    print("正在啟動應用...")

    # 檢查 AI 服務
    ai_service = AIService()
    if await ai_service.check_service_health():
        print("AI 服務連接正常")
    else:
        print("警告: AI 服務連接失敗")

    yield

    # 關閉時執行
    print("應用已關閉")


# 創建 FastAPI 應用
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="基於 FastAPI 的 AI 客服平台",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 靜態文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 模板
templates = Jinja2Templates(directory="templates")

# 註冊路由
from app.routers.chat import router as chat_router
from app.routers.auth_simple import router as auth_router
from app.routers.tickets import router as tickets_router
from app.routers.knowledge import router as knowledge_router
app.include_router(chat_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(tickets_router, prefix="/api")
app.include_router(knowledge_router, prefix="/api")

# 根路由
@app.get("/", response_class=HTMLResponse, summary="首頁")
async def root(request: Request):
    """應用首頁"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": settings.PROJECT_NAME}
    )


# 聊天頁面
@app.get("/chat", response_class=HTMLResponse, summary="聊天頁面")
async def chat_page(request: Request):
    """AI 聊天頁面"""
    return templates.TemplateResponse(
        "chat.html",
        {"request": request, "title": "AI 智能客服"}
    )


# 登入頁面快捷方式
@app.get("/login", response_class=HTMLResponse, summary="登入頁面")
async def login_shortcut(request: Request):
    """登入頁面快捷方式"""
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "title": "用戶登入"}
    )


# 註冊頁面快捷方式
@app.get("/register", response_class=HTMLResponse, summary="註冊頁面")
async def register_shortcut(request: Request):
    """註冊頁面快捷方式"""
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "title": "用戶註冊"}
    )


# 工單頁面快捷方式
@app.get("/tickets", response_class=HTMLResponse, summary="工單管理頁面")
async def tickets_shortcut(request: Request):
    """工單管理頁面快捷方式"""
    return templates.TemplateResponse(
        "tickets.html",
        {"request": request, "title": "工單管理"}
    )


# 知識庫頁面快捷方式
@app.get("/knowledge", response_class=HTMLResponse, summary="知識庫頁面")
async def knowledge_shortcut(request: Request):
    """知識庫頁面快捷方式"""
    return templates.TemplateResponse(
        "knowledge.html",
        {"request": request, "title": "知識庫"}
    )


# 健康檢查
@app.get("/health", summary="健康檢查")
async def health_check():
    """健康檢查端點"""
    ai_service = AIService()
    ai_status = await ai_service.check_service_health()
    
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "ai_service": "online" if ai_status else "offline"
    }


# API 信息
@app.get("/api/info", summary="API 信息")
async def api_info():
    """獲取 API 基本信息"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": "FastAPI AI Customer Service Platform",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
