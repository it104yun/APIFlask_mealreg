# app.py

from dotenv import load_dotenv

load_dotenv() 

from mealreg import create_app
from mealreg.extensions import db

# ❗ 確保在 db.create_all() 之前匯入 User 模型
from mealreg.models.user import User

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

    # admin_user = User(username='emp05', email='emp05@tingx.com', is_admin=False)
    # admin_user.set_password('123456') # 實際應使用更複雜的密碼   
    # db.session.add(admin_user)
    # db.session.commit()

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


if __name__ == '__main__':
    app.run(debug=True)