# app.py

from dotenv import load_dotenv

load_dotenv() 

from mealreg import create_app
from mealreg.extensions import db

# ❗ 確保在 db.create_all() 之前匯入所有 \models 模型
from mealreg.models.user import User
from mealreg.models.canteen import Canteen 
from mealreg.models.meal import Meal  
from mealreg.models.order import Order    
from mealreg.models.setting import Setting 

# 建立應用程式實例
app = create_app()

# ===============================================
# 執行資料庫創建與預設管理員帳號 (初始化動作)
# ===============================================

# 確保在應用程式上下文中執行資料庫操作
with app.app_context():
    print("-> 嘗試創建資料庫表格...")
    # 只有在表格不存在時才會創建
    db.create_all() 
    print("-> 資料庫表格創建完成。")

    # 創建一個預設的總務管理員帳號 (假設 ID=1)
    if not User.query.filter_by(username='admin').first():
        admin_user = User(username='admin', email='admin@example.com', is_admin=True)
        # admin_user = User(username='sophialiyun', email='sophialiyun@gmail.com', is_admin=True)
        # 設定密碼並自動散列
        admin_user.set_password('123456') # 實際應使用更複雜的密碼
        
        db.session.add(admin_user)
        db.session.commit()
        print("-> 已創建預設總務帳號: username=%s, email=%s" % (admin_user.username, ''+admin_user.email))
    else:
        print("-> 預設總務帳號已存在，跳過創建。")

    # 創建一個普通員工帳號用於測試 (非管理員)
    new_user='emp10' 
    # employee, emp06~emp10 password="password"
    # emp01~emp05 password="123456"
    if not User.query.filter_by(username=new_user).first():
        employee_user = User(username=new_user, email=new_user+'@example.com.tw', is_admin=False)
        employee_user.set_password('password') 
        db.session.add(employee_user)
        db.session.commit()
        print("-> 已創建預設員工帳號:", new_user)
    else:
        print(new_user+"-> 預設員工帳號已存在，跳過創建。")    

    # [新功能] 初始化預設(訂單)截止時間設定
    CUTOFF_KEY = 'ORDER_CUTOFF_TIME'
    DEFAULT_TIME = '11:00'
    
    if not Setting.query.filter_by(key=CUTOFF_KEY).first():
        cutoff_setting = Setting(key=CUTOFF_KEY, value=DEFAULT_TIME)
        db.session.add(cutoff_setting)
        db.session.commit()
        print(f"-> 初始化訂單截止時間設定: {CUTOFF_KEY} = {DEFAULT_TIME}")
    else:
        print("-> 訂單截止時間設定已存在，跳過初始化。")


if __name__ == '__main__':
    app.run(debug=True)