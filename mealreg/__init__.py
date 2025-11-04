from apiflask import APIFlask
from flask import Flask, render_template
from .config import Config
from .extensions import db, jwt

# **這是應用程式工廠函式**：標準的 Flask/APIFlask 實例建立方式
def create_app(config_class=Config):
    # 建立 APIFlask 實例
    app = APIFlask(__name__, title=config_class.TITLE)

    # 載入配置
    app.config.from_object(config_class)
    # 初始化擴展套件
    db.init_app(app)
    jwt.init_app(app)

    # ===============================================
    # ❗ 關鍵修正：註冊 auth 藍圖
    # ===============================================
    from .api.auth import auth_bp 
    app.register_blueprint(auth_bp) # 由於 auth_bp 已經設定 url_prefix='/auth'，這裡無需再設定


    # ===============================================
    # ❗ 首次展示：定義一個根目錄路由 (Route)
    # ===============================================

    # 處理根目錄 "/" 的 GET 請求
    @app.get('/')
    def index():
        # 回傳一個 JSON 格式的字典
        initial_dict =  {
            "message": "Hello World! APIFlask_mealreg 服務已啟動。",
            "status": "Running",
            "version": "v1.0.0"
        }
        # return initial_dict

        # 也可以使用 HTML 模板來渲染頁面
        # 也可以使用 HTML 模板來渲染頁面
        # initial_pharse = ["Hi, I am Sophia.", "This is a utility initial app.py that I made.","You can change the code for user needs."]        
        initial_pharse = ["Hi, I am Sophia.", "APIFlask_mealreg 服務已啟動","歡迎使用午餐訂購平台！"]        
        return render_template('index.html', initial_parameter=initial_pharse)
    
    # APIFlask 會自動為我們生成文檔，通常在 /docs 或 /redoc
    @app.get('/hello')
    def hello():
        return {"data": "This is another test endpoint."}

    return app