from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid

router = APIRouter(prefix="/tickets", tags=["工單管理"])
templates = Jinja2Templates(directory="templates")


class TicketStatus(str, Enum):
    """工單狀態枚舉"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(str, Enum):
    """工單優先級枚舉"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketCreate(BaseModel):
    """創建工單模型"""
    title: str
    description: str
    category: Optional[str] = "general"
    priority: TicketPriority = TicketPriority.MEDIUM
    user_name: Optional[str] = "匿名用戶"
    user_email: Optional[str] = None


class TicketUpdate(BaseModel):
    """更新工單模型"""
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    assigned_to: Optional[str] = None
    resolution: Optional[str] = None


class Ticket(BaseModel):
    """工單響應模型"""
    id: str
    ticket_number: str
    title: str
    description: str
    status: TicketStatus
    priority: TicketPriority
    category: str
    user_name: str
    user_email: Optional[str]
    assigned_to: Optional[str]
    resolution: Optional[str]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None


# 簡單的內存工單存儲（僅用於演示）
DEMO_TICKETS = {
    "1": {
        "id": "1",
        "ticket_number": "TK-2024-001",
        "title": "無法登入系統",
        "description": "我嘗試登入系統但一直顯示密碼錯誤，請協助處理。",
        "status": TicketStatus.RESOLVED,
        "priority": TicketPriority.HIGH,
        "category": "技術問題",
        "user_name": "張三",
        "user_email": "zhang@example.com",
        "assigned_to": "客服小王",
        "resolution": "已重設用戶密碼，問題已解決。",
        "created_at": datetime(2024, 1, 15, 10, 30),
        "updated_at": datetime(2024, 1, 15, 14, 20),
        "resolved_at": datetime(2024, 1, 15, 14, 20)
    },
    "2": {
        "id": "2", 
        "ticket_number": "TK-2024-002",
        "title": "功能建議：增加搜索功能",
        "description": "希望能在知識庫中增加更強大的搜索功能，支援模糊搜索。",
        "status": TicketStatus.IN_PROGRESS,
        "priority": TicketPriority.MEDIUM,
        "category": "功能建議",
        "user_name": "李四",
        "user_email": "li@example.com",
        "assigned_to": "產品經理",
        "resolution": None,
        "created_at": datetime(2024, 1, 16, 9, 15),
        "updated_at": datetime(2024, 1, 16, 11, 30),
        "resolved_at": None
    },
    "3": {
        "id": "3",
        "ticket_number": "TK-2024-003", 
        "title": "系統回應速度慢",
        "description": "最近使用系統時發現回應速度明顯變慢，特別是 AI 對話功能。",
        "status": TicketStatus.PENDING,
        "priority": TicketPriority.HIGH,
        "category": "性能問題",
        "user_name": "王五",
        "user_email": "wang@example.com",
        "assigned_to": None,
        "resolution": None,
        "created_at": datetime(2024, 1, 17, 14, 45),
        "updated_at": datetime(2024, 1, 17, 14, 45),
        "resolved_at": None
    }
}


@router.get("/", response_class=HTMLResponse, summary="工單管理頁面")
async def tickets_page(request: Request):
    """工單管理頁面"""
    return templates.TemplateResponse(
        "tickets.html",
        {"request": request, "title": "工單管理"}
    )


@router.get("/api", summary="獲取所有工單")
async def get_tickets(
    status: Optional[TicketStatus] = None,
    priority: Optional[TicketPriority] = None,
    category: Optional[str] = None
):
    """
    獲取工單列表
    
    - **status**: 篩選狀態（可選）
    - **priority**: 篩選優先級（可選）
    - **category**: 篩選類別（可選）
    """
    tickets = list(DEMO_TICKETS.values())
    
    # 應用篩選條件
    if status:
        tickets = [t for t in tickets if t["status"] == status]
    if priority:
        tickets = [t for t in tickets if t["priority"] == priority]
    if category:
        tickets = [t for t in tickets if t["category"] == category]
    
    # 按創建時間排序（最新的在前）
    tickets.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {
        "tickets": tickets,
        "total": len(tickets),
        "filters": {
            "status": status,
            "priority": priority,
            "category": category
        }
    }


@router.get("/api/stats", summary="工單統計")
async def get_ticket_stats():
    """獲取工單統計信息"""
    tickets = list(DEMO_TICKETS.values())

    # 按狀態統計
    status_stats = {}
    for status in TicketStatus:
        status_stats[status.value] = len([t for t in tickets if t["status"] == status])

    # 按優先級統計
    priority_stats = {}
    for priority in TicketPriority:
        priority_stats[priority.value] = len([t for t in tickets if t["priority"] == priority])

    # 按類別統計
    categories = list(set(t["category"] for t in tickets))
    category_stats = {}
    for category in categories:
        category_stats[category] = len([t for t in tickets if t["category"] == category])

    return {
        "total_tickets": len(tickets),
        "status_distribution": status_stats,
        "priority_distribution": priority_stats,
        "category_distribution": category_stats,
        "avg_resolution_time": "2.5 小時",  # 模擬數據
        "open_tickets": status_stats.get("pending", 0) + status_stats.get("in_progress", 0)
    }


@router.get("/api/{ticket_id}", summary="獲取工單詳情")
async def get_ticket(ticket_id: str):
    """獲取特定工單的詳細信息"""
    if ticket_id not in DEMO_TICKETS:
        raise HTTPException(status_code=404, detail="工單不存在")

    return DEMO_TICKETS[ticket_id]


@router.post("/api", summary="創建新工單")
async def create_ticket(ticket_create: TicketCreate):
    """
    創建新工單
    
    - **title**: 工單標題
    - **description**: 問題描述
    - **category**: 問題類別
    - **priority**: 優先級
    - **user_name**: 用戶姓名
    - **user_email**: 用戶郵箱
    """
    # 生成新的工單 ID 和編號
    ticket_id = str(len(DEMO_TICKETS) + 1)
    ticket_number = f"TK-2024-{len(DEMO_TICKETS) + 1:03d}"
    
    # 創建新工單
    new_ticket = {
        "id": ticket_id,
        "ticket_number": ticket_number,
        "title": ticket_create.title,
        "description": ticket_create.description,
        "status": TicketStatus.PENDING,
        "priority": ticket_create.priority,
        "category": ticket_create.category,
        "user_name": ticket_create.user_name,
        "user_email": ticket_create.user_email,
        "assigned_to": None,
        "resolution": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "resolved_at": None
    }
    
    # 添加到存儲
    DEMO_TICKETS[ticket_id] = new_ticket
    
    return new_ticket


@router.put("/api/{ticket_id}", summary="更新工單")
async def update_ticket(ticket_id: str, ticket_update: TicketUpdate):
    """
    更新工單信息
    
    - **status**: 更新狀態
    - **priority**: 更新優先級
    - **assigned_to**: 分配給誰
    - **resolution**: 解決方案
    """
    if ticket_id not in DEMO_TICKETS:
        raise HTTPException(status_code=404, detail="工單不存在")
    
    ticket = DEMO_TICKETS[ticket_id]
    
    # 更新字段
    if ticket_update.status is not None:
        ticket["status"] = ticket_update.status
        if ticket_update.status == TicketStatus.RESOLVED:
            ticket["resolved_at"] = datetime.now()
    
    if ticket_update.priority is not None:
        ticket["priority"] = ticket_update.priority
    
    if ticket_update.assigned_to is not None:
        ticket["assigned_to"] = ticket_update.assigned_to
    
    if ticket_update.resolution is not None:
        ticket["resolution"] = ticket_update.resolution
    
    ticket["updated_at"] = datetime.now()
    
    return ticket


@router.delete("/api/{ticket_id}", summary="刪除工單")
async def delete_ticket(ticket_id: str):
    """刪除工單（僅用於演示）"""
    if ticket_id not in DEMO_TICKETS:
        raise HTTPException(status_code=404, detail="工單不存在")
    
    deleted_ticket = DEMO_TICKETS.pop(ticket_id)
    return {"message": "工單已刪除", "deleted_ticket": deleted_ticket}



