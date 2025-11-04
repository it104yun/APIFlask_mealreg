# mealreg/models/meal.py

from datetime import datetime
from ..extensions import db

class Meal(db.Model):
    __tablename__ = 'meal'

    id = db.Column(db.Integer, primary_key=True)
    
    # 便當名稱
    name = db.Column(db.String(100), nullable=False)
    
    # 價格 (使用 Integer 儲存，單位為「分」，避免浮點數計算誤差)
    # 例如：100 元 = 10000 分
    price = db.Column(db.Integer, nullable=False)
    
    # 是否活躍 (總務人員可暫時停用某個便當)
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ========================
    # 關聯：與 Canteen 建立多對一關係 (外鍵)
    # ========================
    # 儲存此便當所屬 Canteen 的 ID
    canteen_id = db.Column(db.Integer, db.ForeignKey('canteen.id'), nullable=False)

    def get_price_yuan(self):
        """獲取以元為單位的價格"""
        return self.price / 100.0

    def __repr__(self):
        return f'<Meal id={self.id}, name={self.name}, price={self.get_price_yuan()}元>'