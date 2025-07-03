from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

router = APIRouter(prefix="/knowledge", tags=["知識庫"])
templates = Jinja2Templates(directory="templates")


class FAQCreate(BaseModel):
    """創建 FAQ 模型"""
    question: str
    answer: str
    category: Optional[str] = "一般問題"
    tags: Optional[List[str]] = []


class FAQUpdate(BaseModel):
    """更新 FAQ 模型"""
    question: Optional[str] = None
    answer: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None


class FAQ(BaseModel):
    """FAQ 響應模型"""
    id: str
    question: str
    answer: str
    category: str
    tags: List[str]
    is_active: bool
    view_count: int
    helpful_count: int
    created_at: datetime
    updated_at: datetime


class KnowledgeCreate(BaseModel):
    """創建知識庫文檔模型"""
    title: str
    content: str
    summary: Optional[str] = None
    category: Optional[str] = "一般文檔"
    tags: Optional[List[str]] = []


class Knowledge(BaseModel):
    """知識庫文檔響應模型"""
    id: str
    title: str
    content: str
    summary: Optional[str]
    category: str
    tags: List[str]
    is_published: bool
    view_count: int
    created_at: datetime
    updated_at: datetime


# 簡單的內存 FAQ 存儲（僅用於演示）
DEMO_FAQS = {
    "1": {
        "id": "1",
        "question": "如何重設密碼？",
        "answer": "您可以在登入頁面點擊「忘記密碼」連結，輸入您的郵箱地址，系統會發送重設密碼的連結到您的郵箱。請檢查您的郵箱（包括垃圾郵件資料夾）並按照指示操作。",
        "category": "帳戶管理",
        "tags": ["密碼", "重設", "帳戶", "登入"],
        "is_active": True,
        "view_count": 156,
        "helpful_count": 142,
        "created_at": datetime(2024, 1, 10, 9, 0),
        "updated_at": datetime(2024, 1, 15, 14, 30)
    },
    "2": {
        "id": "2",
        "question": "如何聯繫客服？",
        "answer": "您可以通過以下方式聯繫我們：\n1. 使用網站上的 AI 智能客服聊天功能（24小時服務）\n2. 發送郵件到 support@example.com\n3. 撥打客服電話 0800-123-456（週一至週五 9:00-18:00）\n4. 創建客服工單，我們會盡快回覆",
        "category": "客服支援",
        "tags": ["客服", "聯繫", "支援", "電話", "郵件"],
        "is_active": True,
        "view_count": 203,
        "helpful_count": 189,
        "created_at": datetime(2024, 1, 8, 10, 15),
        "updated_at": datetime(2024, 1, 12, 16, 45)
    },
    "3": {
        "id": "3",
        "question": "系統支援哪些瀏覽器？",
        "answer": "我們的系統支援以下瀏覽器的最新版本：\n• Google Chrome（推薦）\n• Mozilla Firefox\n• Safari\n• Microsoft Edge\n\n建議使用 Chrome 以獲得最佳體驗。如果您使用的是較舊版本的瀏覽器，可能會遇到兼容性問題。",
        "category": "技術支援",
        "tags": ["瀏覽器", "兼容性", "技術", "Chrome", "Firefox"],
        "is_active": True,
        "view_count": 89,
        "helpful_count": 76,
        "created_at": datetime(2024, 1, 12, 14, 20),
        "updated_at": datetime(2024, 1, 18, 11, 10)
    },
    "4": {
        "id": "4",
        "question": "如何創建工單？",
        "answer": "創建工單很簡單：\n1. 登入您的帳戶\n2. 點擊「工單管理」選單\n3. 點擊「創建工單」按鈕\n4. 填寫問題描述和相關信息\n5. 選擇適當的優先級\n6. 提交工單\n\n您會收到工單編號，可以隨時查看處理進度。",
        "category": "工單管理",
        "tags": ["工單", "創建", "問題", "客服"],
        "is_active": True,
        "view_count": 134,
        "helpful_count": 118,
        "created_at": datetime(2024, 1, 14, 16, 30),
        "updated_at": datetime(2024, 1, 20, 9, 15)
    },
    "5": {
        "id": "5",
        "question": "AI 客服的工作時間是？",
        "answer": "我們的 AI 智能客服 24 小時全天候為您服務，無休息時間。AI 客服可以：\n• 回答常見問題\n• 協助基本操作指導\n• 創建客服工單\n• 提供產品信息\n\n如需人工客服協助，服務時間為週一至週五 9:00-18:00。",
        "category": "服務時間",
        "tags": ["AI", "客服", "時間", "24小時", "人工"],
        "is_active": True,
        "view_count": 178,
        "helpful_count": 165,
        "created_at": datetime(2024, 1, 9, 11, 45),
        "updated_at": datetime(2024, 1, 16, 13, 20)
    }
}

# 簡單的內存知識庫存儲
DEMO_KNOWLEDGE = {
    "1": {
        "id": "1",
        "title": "FastAPI AI 客服平台使用指南",
        "content": "本指南將幫助您快速上手使用 FastAPI AI 客服平台...",
        "summary": "完整的平台使用指南，包含所有功能介紹",
        "category": "使用指南",
        "tags": ["指南", "教學", "FastAPI", "AI"],
        "is_published": True,
        "view_count": 245,
        "created_at": datetime(2024, 1, 5, 10, 0),
        "updated_at": datetime(2024, 1, 20, 15, 30)
    },
    "2": {
        "id": "2",
        "title": "AI 對話功能詳解",
        "content": "AI 對話功能基於先進的 Ollama qwen3:14b 模型...",
        "summary": "詳細介紹 AI 對話功能的使用方法和技巧",
        "category": "AI 功能",
        "tags": ["AI", "對話", "Ollama", "qwen"],
        "is_published": True,
        "view_count": 189,
        "created_at": datetime(2024, 1, 8, 14, 15),
        "updated_at": datetime(2024, 1, 18, 10, 45)
    }
}


@router.get("/", response_class=HTMLResponse, summary="知識庫頁面")
async def knowledge_page(request: Request):
    """知識庫管理頁面"""
    return templates.TemplateResponse(
        "knowledge.html",
        {"request": request, "title": "知識庫"}
    )


@router.get("/api/faq", summary="獲取 FAQ 列表")
async def get_faqs(
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(default=10, le=100)
):
    """
    獲取 FAQ 列表
    
    - **category**: 篩選類別（可選）
    - **search**: 搜索關鍵詞（可選）
    - **limit**: 返回數量限制
    """
    faqs = list(DEMO_FAQS.values())
    
    # 只返回啟用的 FAQ
    faqs = [faq for faq in faqs if faq["is_active"]]
    
    # 應用類別篩選
    if category:
        faqs = [faq for faq in faqs if faq["category"] == category]
    
    # 應用搜索篩選
    if search:
        search_lower = search.lower()
        faqs = [
            faq for faq in faqs 
            if search_lower in faq["question"].lower() 
            or search_lower in faq["answer"].lower()
            or any(search_lower in tag.lower() for tag in faq["tags"])
        ]
    
    # 按瀏覽次數排序
    faqs.sort(key=lambda x: x["view_count"], reverse=True)
    
    # 限制返回數量
    faqs = faqs[:limit]
    
    return {
        "faqs": faqs,
        "total": len(faqs),
        "filters": {
            "category": category,
            "search": search,
            "limit": limit
        }
    }


@router.get("/api/faq/{faq_id}", summary="獲取 FAQ 詳情")
async def get_faq(faq_id: str):
    """獲取特定 FAQ 的詳細信息"""
    if faq_id not in DEMO_FAQS:
        raise HTTPException(status_code=404, detail="FAQ 不存在")
    
    faq = DEMO_FAQS[faq_id].copy()
    
    # 增加瀏覽次數
    DEMO_FAQS[faq_id]["view_count"] += 1
    faq["view_count"] = DEMO_FAQS[faq_id]["view_count"]
    
    return faq


@router.post("/api/faq", summary="創建 FAQ")
async def create_faq(faq_create: FAQCreate):
    """
    創建新的 FAQ
    
    - **question**: 問題
    - **answer**: 答案
    - **category**: 類別
    - **tags**: 標籤列表
    """
    faq_id = str(len(DEMO_FAQS) + 1)
    
    new_faq = {
        "id": faq_id,
        "question": faq_create.question,
        "answer": faq_create.answer,
        "category": faq_create.category,
        "tags": faq_create.tags,
        "is_active": True,
        "view_count": 0,
        "helpful_count": 0,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    DEMO_FAQS[faq_id] = new_faq
    return new_faq


@router.put("/api/faq/{faq_id}", summary="更新 FAQ")
async def update_faq(faq_id: str, faq_update: FAQUpdate):
    """更新 FAQ 信息"""
    if faq_id not in DEMO_FAQS:
        raise HTTPException(status_code=404, detail="FAQ 不存在")
    
    faq = DEMO_FAQS[faq_id]
    
    # 更新字段
    if faq_update.question is not None:
        faq["question"] = faq_update.question
    if faq_update.answer is not None:
        faq["answer"] = faq_update.answer
    if faq_update.category is not None:
        faq["category"] = faq_update.category
    if faq_update.tags is not None:
        faq["tags"] = faq_update.tags
    if faq_update.is_active is not None:
        faq["is_active"] = faq_update.is_active
    
    faq["updated_at"] = datetime.now()
    
    return faq


@router.post("/api/faq/{faq_id}/helpful", summary="標記 FAQ 有用")
async def mark_faq_helpful(faq_id: str):
    """標記 FAQ 為有用"""
    if faq_id not in DEMO_FAQS:
        raise HTTPException(status_code=404, detail="FAQ 不存在")
    
    DEMO_FAQS[faq_id]["helpful_count"] += 1
    
    return {
        "message": "感謝您的反饋",
        "helpful_count": DEMO_FAQS[faq_id]["helpful_count"]
    }


@router.get("/api/knowledge", summary="獲取知識庫文檔")
async def get_knowledge_docs(
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(default=10, le=100)
):
    """獲取知識庫文檔列表"""
    docs = list(DEMO_KNOWLEDGE.values())

    # 只返回已發布的文檔
    docs = [doc for doc in docs if doc["is_published"]]

    # 應用篩選
    if category:
        docs = [doc for doc in docs if doc["category"] == category]

    if search:
        search_lower = search.lower()
        docs = [
            doc for doc in docs
            if search_lower in doc["title"].lower()
            or search_lower in doc["content"].lower()
            or (doc["summary"] and search_lower in doc["summary"].lower())
        ]

    # 按瀏覽次數排序
    docs.sort(key=lambda x: x["view_count"], reverse=True)
    docs = docs[:limit]

    return {
        "documents": docs,
        "total": len(docs),
        "filters": {
            "category": category,
            "search": search,
            "limit": limit
        }
    }


@router.get("/api/knowledge/{doc_id}", summary="獲取知識庫文檔詳情")
async def get_knowledge_doc(doc_id: str):
    """獲取特定知識庫文檔的詳細信息"""
    if doc_id not in DEMO_KNOWLEDGE:
        raise HTTPException(status_code=404, detail="文檔不存在")

    doc = DEMO_KNOWLEDGE[doc_id].copy()

    # 增加瀏覽次數
    DEMO_KNOWLEDGE[doc_id]["view_count"] += 1
    doc["view_count"] = DEMO_KNOWLEDGE[doc_id]["view_count"]

    return doc


@router.post("/api/knowledge", summary="創建知識庫文檔")
async def create_knowledge_doc(doc_create: KnowledgeCreate):
    """
    創建新的知識庫文檔

    - **title**: 文檔標題
    - **content**: 文檔內容
    - **summary**: 文檔摘要（可選）
    - **category**: 文檔類別
    - **tags**: 標籤列表
    """
    doc_id = str(len(DEMO_KNOWLEDGE) + 1)

    new_doc = {
        "id": doc_id,
        "title": doc_create.title,
        "content": doc_create.content,
        "summary": doc_create.summary,
        "category": doc_create.category,
        "tags": doc_create.tags,
        "is_published": True,  # 預設為已發布
        "view_count": 0,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

    DEMO_KNOWLEDGE[doc_id] = new_doc
    return new_doc


class KnowledgeUpdate(BaseModel):
    """更新知識庫文檔模型"""
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_published: Optional[bool] = None


@router.put("/api/knowledge/{doc_id}", summary="更新知識庫文檔")
async def update_knowledge_doc(doc_id: str, doc_update: KnowledgeUpdate):
    """更新知識庫文檔信息"""
    if doc_id not in DEMO_KNOWLEDGE:
        raise HTTPException(status_code=404, detail="文檔不存在")

    doc = DEMO_KNOWLEDGE[doc_id]

    # 更新字段
    if doc_update.title is not None:
        doc["title"] = doc_update.title
    if doc_update.content is not None:
        doc["content"] = doc_update.content
    if doc_update.summary is not None:
        doc["summary"] = doc_update.summary
    if doc_update.category is not None:
        doc["category"] = doc_update.category
    if doc_update.tags is not None:
        doc["tags"] = doc_update.tags
    if doc_update.is_published is not None:
        doc["is_published"] = doc_update.is_published

    doc["updated_at"] = datetime.now()

    return doc


@router.delete("/api/knowledge/{doc_id}", summary="刪除知識庫文檔")
async def delete_knowledge_doc(doc_id: str):
    """刪除知識庫文檔（僅用於演示）"""
    if doc_id not in DEMO_KNOWLEDGE:
        raise HTTPException(status_code=404, detail="文檔不存在")

    deleted_doc = DEMO_KNOWLEDGE.pop(doc_id)
    return {"message": "文檔已刪除", "deleted_document": deleted_doc}


@router.get("/api/search", summary="全文搜索")
async def search_knowledge(
    q: str = Query(..., description="搜索關鍵詞"),
    limit: int = Query(default=10, le=50)
):
    """
    在 FAQ 和知識庫中進行全文搜索
    
    - **q**: 搜索關鍵詞
    - **limit**: 返回結果數量限制
    """
    results = []
    search_lower = q.lower()
    
    # 搜索 FAQ
    for faq in DEMO_FAQS.values():
        if not faq["is_active"]:
            continue
            
        score = 0
        if search_lower in faq["question"].lower():
            score += 3
        if search_lower in faq["answer"].lower():
            score += 2
        if any(search_lower in tag.lower() for tag in faq["tags"]):
            score += 1
            
        if score > 0:
            results.append({
                "type": "faq",
                "id": faq["id"],
                "title": faq["question"],
                "content": faq["answer"][:200] + "..." if len(faq["answer"]) > 200 else faq["answer"],
                "category": faq["category"],
                "score": score,
                "url": f"/knowledge/faq/{faq['id']}"
            })
    
    # 搜索知識庫文檔
    for doc in DEMO_KNOWLEDGE.values():
        if not doc["is_published"]:
            continue
            
        score = 0
        if search_lower in doc["title"].lower():
            score += 3
        if search_lower in doc["content"].lower():
            score += 2
        if doc["summary"] and search_lower in doc["summary"].lower():
            score += 1
            
        if score > 0:
            results.append({
                "type": "document",
                "id": doc["id"],
                "title": doc["title"],
                "content": doc["summary"] or doc["content"][:200] + "...",
                "category": doc["category"],
                "score": score,
                "url": f"/knowledge/doc/{doc['id']}"
            })
    
    # 按分數排序
    results.sort(key=lambda x: x["score"], reverse=True)
    results = results[:limit]
    
    return {
        "query": q,
        "results": results,
        "total": len(results)
    }


@router.get("/api/categories", summary="獲取所有類別")
async def get_categories():
    """獲取所有 FAQ 和知識庫的類別"""
    faq_categories = list(set(faq["category"] for faq in DEMO_FAQS.values()))
    doc_categories = list(set(doc["category"] for doc in DEMO_KNOWLEDGE.values()))
    
    all_categories = list(set(faq_categories + doc_categories))
    
    return {
        "faq_categories": faq_categories,
        "document_categories": doc_categories,
        "all_categories": sorted(all_categories)
    }


@router.get("/api/stats", summary="知識庫統計")
async def get_knowledge_stats():
    """獲取知識庫統計信息"""
    total_faqs = len([faq for faq in DEMO_FAQS.values() if faq["is_active"]])
    total_docs = len([doc for doc in DEMO_KNOWLEDGE.values() if doc["is_published"]])
    total_views = sum(faq["view_count"] for faq in DEMO_FAQS.values())
    total_helpful = sum(faq["helpful_count"] for faq in DEMO_FAQS.values())
    
    return {
        "total_faqs": total_faqs,
        "total_documents": total_docs,
        "total_views": total_views,
        "total_helpful_votes": total_helpful,
        "categories": len(set(faq["category"] for faq in DEMO_FAQS.values())),
        "avg_helpful_rate": round(total_helpful / total_views * 100, 1) if total_views > 0 else 0
    }
