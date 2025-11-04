# mealreg/api/decorators.py
# 建立 Admin 權限驗證裝飾器
# 我們需要一個自定義的裝飾器 (@admin_required()) 來檢查當前 JWT token 攜帶的用戶 ID 是否為 is_admin=True。

from functools import wraps
from flask_jwt_extended import get_jwt_identity, jwt_required
from apiflask import abort
from ..extensions import db
from ..models.user import User

def admin_required():
    """
    自定義裝飾器：要求用戶必須登入 (JWT) 且具有管理員權限 (is_admin=True)。
    """
    def wrapper(fn):
        @wraps(fn)
        @jwt_required() # 確保用戶已登入
        def decorator(*args, **kwargs):
            # 1. 獲取當前用戶 ID
            current_user_id = get_jwt_identity()
            
            # 2. 根據 ID 查找用戶
            # user = db.get_or_404(User, current_user_id, message="用戶不存在") # 原始程式碼 (錯誤):
            # 修改後 (正確): 有些版本的 SQLAlchemy 不支援 message 參數
            user = db.get_or_404(User, current_user_id, description="用戶不存在")
            
            # 3. 檢查是否為管理員
            if not user.is_admin:
                # 拋出 403 Forbidden 錯誤
                abort(403, message="權限不足，此操作需要總務人員權限。")
            
            # 如果通過檢查，則執行原函數
            return fn(*args, **kwargs)
        return decorator
    return wrapper