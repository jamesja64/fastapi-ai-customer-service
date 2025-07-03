import httpx
import json
from typing import Dict, List, Optional
from app.core.config import settings


class AIService:
    """AI 服務類，負責與 Ollama 模型交互"""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT
    
    async def generate_response(
        self, 
        message: str, 
        context: Optional[List[Dict]] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """生成 AI 回應"""
        try:
            # 構建消息歷史
            messages = []
            
            # 添加系統提示
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            else:
                messages.append({
                    "role": "system",
                    "content": self._get_default_system_prompt()
                })
            
            # 添加上下文歷史
            if context:
                messages.extend(context)
            
            # 添加當前用戶消息
            messages.append({
                "role": "user",
                "content": message
            })
            
            # 調用 Ollama API
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("message", {}).get("content", "抱歉，我無法回答這個問題。")
                else:
                    return "抱歉，AI 服務暫時不可用。"
                    
        except Exception as e:
            print(f"AI 服務錯誤: {e}")
            return "抱歉，處理您的請求時出現錯誤。"
    
    async def analyze_intent(self, message: str) -> Dict[str, str]:
        """分析用戶意圖"""
        system_prompt = """
        你是一個客服意圖分析助手。請分析用戶消息的意圖，並返回以下格式的 JSON：
        {
            "intent": "意圖類型",
            "category": "問題類別",
            "confidence": "置信度(0-1)",
            "keywords": ["關鍵詞1", "關鍵詞2"]
        }
        
        意圖類型包括：
        - question: 一般問題
        - complaint: 投訴
        - request: 請求幫助
        - technical: 技術問題
        - billing: 計費問題
        - other: 其他
        """
        
        try:
            response = await self.generate_response(
                message, 
                system_prompt=system_prompt
            )
            
            # 嘗試解析 JSON 回應
            try:
                intent_data = json.loads(response)
                return intent_data
            except json.JSONDecodeError:
                return {
                    "intent": "other",
                    "category": "未知",
                    "confidence": "0.5",
                    "keywords": []
                }
                
        except Exception as e:
            print(f"意圖分析錯誤: {e}")
            return {
                "intent": "other",
                "category": "未知",
                "confidence": "0.0",
                "keywords": []
            }
    
    async def generate_summary(self, conversation: List[Dict]) -> str:
        """生成對話摘要"""
        system_prompt = """
        請為以下對話生成一個簡潔的摘要，包括：
        1. 用戶的主要問題
        2. 提供的解決方案
        3. 對話結果
        
        摘要應該在 100 字以內。
        """
        
        # 構建對話文本
        conversation_text = ""
        for msg in conversation:
            role = "用戶" if msg.get("role") == "user" else "客服"
            conversation_text += f"{role}: {msg.get('content', '')}\n"
        
        try:
            summary = await self.generate_response(
                f"請為以下對話生成摘要：\n\n{conversation_text}",
                system_prompt=system_prompt
            )
            return summary
        except Exception as e:
            print(f"摘要生成錯誤: {e}")
            return "對話摘要生成失敗"
    
    def _get_default_system_prompt(self) -> str:
        """獲取默認系統提示"""
        return """
        你是一個專業的客服助手，名字叫小助手。你的任務是：
        
        1. 友善、專業地回答用戶問題
        2. 提供準確、有用的信息
        3. 如果不確定答案，誠實地說明並建議聯繫人工客服
        4. 保持回答簡潔明了
        5. 使用繁體中文回答
        
        請始終保持禮貌和專業的態度。
        """
    
    async def check_service_health(self) -> bool:
        """檢查 AI 服務健康狀態"""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False
