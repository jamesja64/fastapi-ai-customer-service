from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from app.services.ai_service import AIService

router = APIRouter(prefix="/chat", tags=["對話"])

# AI 服務實例
ai_service = AIService()


class ChatMessage(BaseModel):
    """聊天消息模型"""
    message: str
    context: Optional[List[Dict]] = None


class ChatResponse(BaseModel):
    """聊天回應模型"""
    response: str
    intent: Optional[Dict] = None


@router.post("/message", response_model=ChatResponse, summary="發送消息給 AI")
async def send_message(chat_message: ChatMessage):
    """
    發送消息給 AI 並獲取回應

    - **message**: 用戶消息
    - **context**: 對話上下文（可選）
    """
    try:
        # 生成 AI 回應
        response = await ai_service.generate_response(
            message=chat_message.message,
            context=chat_message.context
        )

        # 分析用戶意圖
        intent = await ai_service.analyze_intent(chat_message.message)

        return ChatResponse(
            response=response,
            intent=intent
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI 服務錯誤: {str(e)}"
        )


@router.get("/health", summary="檢查 AI 服務健康狀態")
async def check_ai_health():
    """檢查 AI 服務是否正常運行"""
    is_healthy = await ai_service.check_service_health()

    return {
        "ai_service": "online" if is_healthy else "offline",
        "status": "healthy" if is_healthy else "unhealthy"
    }


@router.post("/test", summary="測試 AI 對話")
async def test_chat():
    """測試 AI 對話功能"""
    test_message = "你好，我需要幫助"

    try:
        response = await ai_service.generate_response(test_message)
        return {
            "test_message": test_message,
            "ai_response": response,
            "status": "success"
        }
    except Exception as e:
        return {
            "test_message": test_message,
            "error": str(e),
            "status": "failed"
        }
