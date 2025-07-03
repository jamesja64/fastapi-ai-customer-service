#!/bin/bash

echo "🚀 FastAPI AI 客服平台本地部署腳本"
echo "=================================="

# 檢查 FastAPI 應用是否運行
if ! curl -s http://localhost:8001/health > /dev/null; then
    echo "❌ FastAPI 應用未運行在 port 8001"
    echo "請先啟動應用："
    echo "cd pycharm_v1/fastapi-ai-customer-service"
    echo "source venv/bin/activate"
    echo "uvicorn app.main:app --reload --host 0.0.0.0 --port 8001"
    exit 1
fi

echo "✅ FastAPI 應用運行正常"

# 獲取本機 IP
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)

echo ""
echo "🌐 您的應用可以通過以下方式訪問："
echo "=================================="
echo "本地訪問: http://localhost:8001"
echo "局域網訪問: http://$LOCAL_IP:8001"
echo ""
echo "📱 主要功能頁面："
echo "- 首頁: http://$LOCAL_IP:8001/"
echo "- AI 聊天: http://$LOCAL_IP:8001/chat"
echo "- 用戶登入: http://$LOCAL_IP:8001/login"
echo "- 工單管理: http://$LOCAL_IP:8001/tickets"
echo "- 知識庫: http://$LOCAL_IP:8001/knowledge"
echo "- API 文檔: http://$LOCAL_IP:8001/docs"
echo ""
echo "🔧 演示帳戶："
echo "- 管理員: admin / admin123"
echo "- 用戶: user1 / user123"
echo "- 演示: demo / demo123"
echo ""
echo "💡 提示："
echo "- 確保防火牆允許 8001 端口"
echo "- 同一局域網的設備可以訪問"
echo "- 如需公網訪問，請使用 ngrok 或雲端部署"
