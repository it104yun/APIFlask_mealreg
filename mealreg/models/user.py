# mealreg/models/user.py

from datetime import datetime
# 匯入密碼散列工具
from werkzeug.security import generate_password_hash, check_password_hash
# 匯入 db 實例，用於繼承 db.Model
from ..extensions import db 

class User(db.Model):
    # ========================
    # 欄位定義 (Schema Definition)
    # ========================
    __tablename__ = 'user' # 資料庫表格名稱

    id = db.Column(db.Integer, primary_key=True)
    
    # 用戶名: 必須唯一 (unique=True) 且不能為空 (nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    
    # 電子郵件 (可選，但建議保留)
    email = db.Column(db.String(120), unique=True, nullable=True)
    
    # 密碼散列值: 用來儲存 hash 過的密碼，保護用戶資訊
    password_hash = db.Column(db.String(128))
    
    # 權限欄位: True=總務人員 (Admin), False=普通員工 (Employee)
    is_admin = db.Column(db.Boolean, default=False) 
    
    # 帳號創建時間
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 新增：與 Order 的一對多關聯 (在 order.py 中已經設置了 backref，這裡可以省略顯式定義，但保留清晰)
    # orders = db.relationship('Order', backref='user', lazy='dynamic')


    # ========================
    # 密碼散列方法 (Security Methods)
    # ========================

    # 方法 1: 設定密碼時，自動進行散列
    def set_password(self, password):
        """將純文字密碼轉換為安全的 Hash 值並存入 password_hash 欄位"""
        # 使用安全的 generate_password_hash 函式
        self.password_hash = generate_password_hash(password)

    # 方法 2: 驗證密碼時，比對純文字密碼和 Hash 值
    def check_password(self, password):
        """驗證輸入的密碼是否與儲存的 Hash 值匹配"""
        # 使用 check_password_hash 函式進行安全比對
        return check_password_hash(self.password_hash, password)

    # ========================
    # 其他輔助方法
    # ========================
    
    # 方便在除錯時看到更友好的物件資訊
    def __repr__(self):
        return f'<User id={self.id}, username={self.username}, isAdmin={self.is_admin}>'