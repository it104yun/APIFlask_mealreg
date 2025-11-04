# mealreg/models/order.py

from datetime import date, datetime
from ..extensions import db

class Order(db.Model):
    __tablename__ = 'order_record' # 避免與 SQL 保留字 'order' 衝突

    id = db.Column(db.Integer, primary_key=True)
    
    # ========================
    # 關聯：外鍵 (Foreign Keys)
    # ========================
    
    # 訂購人 (User)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # 訂購的便當 (Meal)
    meal_id = db.Column(db.Integer, db.ForeignKey('meal.id'), nullable=False)
    
    # ========================
    # 訂單細節 (Snapshot of the Meal)
    # ❗ 註：訂單必須儲存價格快照，因為便當價格未來可能改變
    # ========================
    
    # 訂購時的便當名稱快照
    meal_name_snapshot = db.Column(db.String(100), nullable=False)
    
    # 訂購時的價格快照 (以分儲存)
    price_snapshot = db.Column(db.Integer, nullable=False)
    
    # ========================
    # 訂單狀態與時間
    # ========================
    
    # 訂購日期 (用於每日統計) - 僅包含日期 YYYY-MM-DD
    order_date = db.Column(db.Date, default=date.today, nullable=False)
    
    # 是否已繳款 (用於總務結算)
    is_paid = db.Column(db.Boolean, default=False)
    
    # 訂單創建時間 (包含時間)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ========================
    # 關聯關係 (Relationships)
    # ========================
    
    # 與 User 建立關聯 (backref 讓 User 實例可以透過 .orders 訪問所有訂單)
    user = db.relationship('User', backref='orders')
    
    # 與 Meal 建立關聯
    meal = db.relationship('Meal', backref='orders')

    # 設置複合唯一約束：確保同一個用戶在同一天只能訂購一次
    __table_args__ = (
        db.UniqueConstraint('user_id', 'order_date', name='_user_day_uc'),
    )
    
    def get_price_yuan(self):
        """獲取以元為單位的價格快照"""
        return self.price_snapshot / 100.0

    def __repr__(self):
        return f'<Order id={self.id}, user_id={self.user_id}, meal={self.meal_name_snapshot}, date={self.order_date}>'