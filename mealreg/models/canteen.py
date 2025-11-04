# mealreg/models/canteen.py

from datetime import datetime
from ..extensions import db

class Canteen(db.Model):
    __tablename__ = 'canteen'

    id = db.Column(db.Integer, primary_key=True)
    
    # 餐廳名稱
    name = db.Column(db.String(100), unique=True, nullable=False)
    
    # 餐廳描述或備註
    description = db.Column(db.String(255), nullable=True)
    
    # 是否活躍 (總務人員可暫停某餐廳的訂購)
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 建立與 Meal 模型的一對多關聯 (backref='canteen' 讓 Meal 實例可以透過 .canteen 訪問對應的 Canteen 實例)
    meals = db.relationship('Meal', backref='canteen', lazy='dynamic', cascade='all, delete-orphan')

    # 新增：與 Order 的一對多關聯 (在 order.py 中已經設置了 backref，這裡可以省略顯式定義)
    # orders = db.relationship('Order', backref='meal', lazy='dynamic')

    def __repr__(self):
        return f'<Canteen id={self.id}, name={self.name}>'