# mealreg/models/setting.py

from ..extensions import db

class Setting(db.Model):
    __tablename__ = 'setting'

    # 設定鍵 (Key)
    key = db.Column(db.String(64), primary_key=True)
    
    # 設定值 (Value)
    value = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Setting key={self.key}, value={self.value}>'