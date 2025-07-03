# FastAPI AI Customer Service Platform

基於 FastAPI 和 AI 技術的智能客服平台，展示現代 Python 後端開發技能。

## 專案概述

這是一個為 **Seasalt.ai Python Backend Engineer** 職位設計的展示專案，完整實現了企業級 AI 客服系統的核心功能。

### 主要特色

- 🤖 **AI 智能對話** - 整合 Ollama qwen3:14b 模型
- 🎫 **工單管理系統** - 完整的工單生命週期管理
- 🔍 **知識庫搜索** - 基於 Elasticsearch 的全文搜索
- 🔐 **JWT 認證授權** - 多角色權限控制
- 📱 **響應式前端** - Bootstrap 5 + WebSocket 實時通信
- 🐳 **容器化部署** - Docker + Docker Compose
- 📊 **API 文檔** - 自動生成的 OpenAPI 文檔

## 技術架構

### 後端技術棧
- **FastAPI** - 高性能異步 Web 框架
- **SQLAlchemy** - 異步 ORM
- **PostgreSQL** - 主資料庫
- **Redis** - 緩存和會話存儲
- **Elasticsearch** - 全文搜索引擎
- **Ollama** - AI 模型服務
- **JWT** - 認證和授權

### 前端技術
- **HTML5/CSS3/JavaScript** - 現代前端技術
- **Bootstrap 5** - 響應式 UI 框架
- **WebSocket** - 實時通信

### 部署技術
- **Docker** - 容器化
- **Docker Compose** - 多服務編排
- **GitHub Actions** - CI/CD 自動化

## 快速開始

### 環境要求

- Python 3.11+
- Docker & Docker Compose
- Git

### 1. 克隆專案

```bash
git clone <repository-url>
cd fastapi-ai-customer-service
```

### 2. 環境配置

```bash
# 複製環境配置文件
cp .env.example .env

# 編輯配置文件（設置資料庫密碼、JWT 密鑰等）
nano .env
```

### 3. 使用 Docker 啟動

```bash
# 啟動所有服務
docker-compose up -d

# 查看服務狀態
docker-compose ps

# 查看日誌
docker-compose logs -f app
```

### 4. 初始化資料庫

```bash
# 進入應用容器
docker-compose exec app bash

# 運行初始化腳本
python scripts/init_db.py
```

### 5. 訪問應用

- **主應用**: http://localhost:8000
- **API 文檔**: http://localhost:8000/docs
- **ReDoc 文檔**: http://localhost:8000/redoc

## 本地開發

### 1. 創建虛擬環境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

### 2. 安裝依賴

```bash
pip install -r requirements.txt
```

### 3. 設置環境變數

```bash
export DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/ai_customer_service"
export REDIS_URL="redis://localhost:6379/0"
export SECRET_KEY="your-secret-key-here"
export OLLAMA_BASE_URL="http://61.66.218.112:30300"
```

### 4. 啟動開發服務器

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API 文檔

### 認證 API

| 方法 | 端點 | 描述 |
|------|------|------|
| POST | `/api/auth/register` | 用戶註冊 |
| POST | `/api/auth/login` | 用戶登入 |
| POST | `/api/auth/refresh` | 刷新 Token |

### 對話 API

| 方法 | 端點 | 描述 |
|------|------|------|
| POST | `/api/chat/message` | 發送消息 |
| GET | `/api/chat/history/{session_id}` | 獲取對話歷史 |
| WebSocket | `/ws/chat/{session_id}` | 實時對話 |

### 工單 API

| 方法 | 端點 | 描述 |
|------|------|------|
| POST | `/api/tickets` | 創建工單 |
| GET | `/api/tickets` | 獲取工單列表 |
| GET | `/api/tickets/{ticket_id}` | 獲取工單詳情 |
| PUT | `/api/tickets/{ticket_id}` | 更新工單 |

## 測試帳戶

初始化後可使用以下測試帳戶：

| 角色 | 用戶名 | 密碼 | 權限 |
|------|--------|------|------|
| 管理員 | admin | admin123 | 全部權限 |
| 客服人員 | staff1 | staff123 | 工單和對話管理 |
| 普通用戶 | user1 | user123 | 基本功能 |
| 普通用戶 | user2 | user123 | 基本功能 |

## 專案結構

```
fastapi-ai-customer-service/
├── app/                    # 應用程式碼
│   ├── core/              # 核心配置
│   ├── models/            # 資料庫模型
│   ├── schemas/           # Pydantic 模式
│   ├── services/          # 業務邏輯
│   ├── routers/           # API 路由
│   └── main.py           # 主應用
├── static/                # 靜態文件
├── templates/             # HTML 模板
├── scripts/               # 工具腳本
├── tests/                 # 測試文件
├── docker-compose.yml     # Docker 編排
├── Dockerfile            # Docker 鏡像
├── requirements.txt      # Python 依賴
└── README.md            # 專案說明
```

## 核心功能展示

### 1. AI 智能對話
- 整合 Ollama qwen3:14b 模型
- 上下文感知對話
- 意圖識別和分類
- 實時 WebSocket 通信

### 2. 用戶認證系統
- JWT Token 認證
- 多角色權限控制
- 密碼加密存儲
- 會話管理

### 3. 工單管理
- 工單創建和分配
- 狀態追蹤
- 優先級管理
- 搜索和篩選

### 4. 知識庫系統
- FAQ 管理
- 全文搜索
- 分類和標籤
- 智能推薦

## 性能特色

- **異步處理** - 基於 asyncio 的高併發處理
- **資料庫優化** - 連接池和查詢優化
- **緩存策略** - Redis 緩存熱點數據
- **API 限流** - 防止濫用和攻擊

## 安全特性

- **JWT 認證** - 無狀態認證機制
- **密碼加密** - bcrypt 哈希加密
- **CORS 配置** - 跨域請求控制
- **SQL 注入防護** - ORM 參數化查詢

## 部署說明

### 生產環境部署

1. **環境準備**
   ```bash
   # 設置生產環境變數
   export DEBUG=False
   export SECRET_KEY="production-secret-key"
   ```

2. **資料庫遷移**
   ```bash
   # 運行資料庫遷移
   alembic upgrade head
   ```

3. **啟動服務**
   ```bash
   # 使用 Gunicorn 啟動
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

### CI/CD 流程

專案包含 GitHub Actions 工作流：
- 自動化測試
- 代碼品質檢查
- Docker 鏡像構建
- 自動部署

## 開發規範

### 代碼風格
- 遵循 PEP 8 規範
- 使用 Black 格式化
- 類型提示覆蓋
- 完整的文檔字符串

### 測試覆蓋
- 單元測試
- 整合測試
- API 端點測試
- 目標覆蓋率 > 80%

## 聯繫信息

這個專案是為 **Seasalt.ai Python Backend Engineer** 職位創建的技術展示專案。

**技能展示重點：**
- FastAPI 框架熟練度
- 異步程式設計能力
- 資料庫設計和優化
- AI 模型整合經驗
- 前端技術理解
- 容器化部署能力
- API 設計最佳實踐

---

**注意：** 這是一個展示專案，包含的測試數據和配置僅用於演示目的。在生產環境中請修改所有默認密碼和密鑰。


## License

本專案採用 MIT License 授權 - 詳見 [LICENSE](LICENSE) 文件。

### 第三方組件

本專案使用了以下開源組件，詳細的授權信息請參見 [NOTICE](NOTICE) 文件：

- **Bootstrap 5.3.0** - MIT License
- **Font Awesome 6.0.0** - Font Awesome Free License
- **FastAPI** - MIT License
- **Uvicorn** - BSD License
- **其他 Python 依賴** - 各自的開源授權

### 致謝

感謝所有開源社群的貢獻者，讓這個專案得以實現。
