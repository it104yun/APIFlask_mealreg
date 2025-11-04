# **🚀 APIFlask 午餐訂購平台 \- 開發步驟流程說明書**

## **一、專案基礎架構與環境設置**

| 步驟 | 說明 | 關鍵技術點 |
| :---- | :---- | :---- |
| **1\. 專案初始化** | 創建 Python 虛擬環境 (venv) 並安裝核心依賴：APIFlask, Flask-SQLAlchemy, Flask-JWT-Extended, python-dotenv。 | pip install apiflask flask-sqlalchemy flask-jwt-extended python-dotenv |
| **2\. 專案結構定義** | 建立模組化目錄結構 (mealreg/, mealreg/models/, mealreg/api/)。 | 模組化 (\_\_init\_\_.py) |
| **3\. 核心配置** | 設置 mealreg/config.py，定義資料庫連線 (SQLALCHEMY\_DATABASE\_URI) 和 JWT 配置 (JWT\_SECRET\_KEY)。 | Config 類別, .env |
| **4\. 擴展套件初始化** | 在 mealreg/extensions.py 中初始化 SQLAlchemy (db) 和 JWTManager (jwt)。 | db \= SQLAlchemy(), jwt \= JWTManager() |
| **5\. 應用程式工廠** | 在 mealreg/\_\_init\_\_.py 中實現 create\_app() 函式，用於註冊配置和擴展套件。 | 應用工廠模式 (Application Factory) |

## **二、使用者與安全認證模組**

| 步驟 | 說明 | 關鍵技術點 |
| :---- | :---- | :---- |
| **6\. User 模型定義** | 創建 mealreg/models/user.py，定義 User 模型，包含 username, password\_hash, is\_admin。使用 werkzeug.security 處理密碼雜湊。 | db.Model, generate\_password\_hash, check\_password\_hash |
| **7\. 啟動腳本優化** | 修改 app.py，在啟動時自動創建資料庫 (db.create\_all()) 和預設 Admin 帳號。 | with app.app\_context():, 初始化數據 |
| **8\. JWT 認證 API** | 創建 mealreg/api/auth.py，實現 /auth/login 路由，驗證身份並返回 Access Token。 | jwt\_required, create\_access\_token, get\_jwt\_identity |
| **9\. Admin 權限裝飾器** | 創建 mealreg/api/decorators.py，定義 @admin\_required() 裝飾器，檢查當前用戶是否為 Admin。 | functools.wraps, abort(403), User.is\_admin |

## **三、數據模型與管理功能實作**

| 步驟 | 說明 | 關鍵技術點 |
| :---- | :---- | :---- |
| **10\. Canteen 模型** | 創建 mealreg/models/canteen.py，定義餐廳模型，包含 name 和 is\_active。 | db.relationship (一對多) |
| **11\. Meal 模型** | 創建 mealreg/models/meal.py，定義便當模型，包含 name, **price (以分儲存)**, 和 canteen\_id 外鍵。 | 價格整數化避免浮點數誤差 |
| **12\. 總務管理 API (CRUD)** | 創建 mealreg/api/canteen.py 和 mealreg/api/meal.py，實現對餐廳和便當的增、查、改、刪 API。所有路由皆使用 @admin\_required() 保護。 | APIBaseBlueprint, @bp.input(), @bp.output() |
| **13\. 公開查詢 API** | 創建 mealreg/api/public.py，實現 /public/menu，僅返回所有**活躍**的餐廳及便當。 | filter\_by(is\_active=True), 巢狀 Schema |

## **四、訂單與業務邏輯實作**

| 步驟 | 說明 | 關鍵技術點 |
| :---- | :---- | :---- |
| **14\. Order 模型** | 創建 mealreg/models/order.py，定義訂單模型，包含 user\_id, meal\_id, **價格快照**, 和 order\_date。 | UniqueConstraint('user\_id', 'order\_date') |
| **15\. 員工訂購 API** | 創建 mealreg/api/order.py，實現 POST /orders 邏輯：檢查**當日是否重複訂購**，並記錄**價格快照**。 | 業務邏輯檢查 (409 Conflict), date.today() |
| **16\. 系統設定模型** | 創建 mealreg/models/setting.py，用於儲存可配置的截止時間。並在 app.py 初始化預設值。 | 提高系統靈活性 |
| **17\. 訂單刪除 API (複雜邏輯)** | 實現 DELETE /orders/del/{id}：動態讀取 **ORDER\_CUTOFF\_TIME**，並同時執行**時間檢查**和**所有權檢查**。 | datetime.combine(), time(), 多重權限判斷 |
| **18\. 總務訂單統計** | 在 mealreg/api/order.py 中，實現 GET /orders/summary，使用 SQLAlchemy 的 func.count() 和 func.sum() 進行聚合查詢。 | sqlalchemy.func, GROUP BY |
| **19\. 訂單結算 API** | 實現 PUT /orders/{id}/paid，標記訂單 is\_paid \= True。 | db.get\_or\_404, 狀態碼 200 |

## **五、最終優化與文件生成**

| 步驟 | 說明 | 關鍵技術點 |
| :---- | :---- | :---- |
| **20\. 藍圖註冊** | 在 mealreg/\_\_init\_\_.py 中匯入並註冊所有藍圖 (auth\_bp, canteen\_bp, meal\_bp, public\_bp, order\_bp)。 | 確保所有路由可訪問 |
| **21\. 錯誤修復與測試** | 修復開發中遇到的 TypeError, NameError, 404 等問題，並執行全面的測試。 | 確保代碼健壯性 |
| **22\. API 文件生成** | 驗證 APIFlask 自動生成的 **Swagger UI** (/docs)，確認所有輸入/輸出 Schema、描述和狀態碼正確顯示。 | APIFlask 自動文件生成 |

