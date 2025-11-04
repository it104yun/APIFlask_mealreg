# mealreg/api/auth.py

from apiflask import APIBlueprint, Schema, abort
from apiflask.fields import String, Integer, Boolean
from apiflask.validators import Length, OneOf
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from ..extensions import db # 引入 db
from ..models.user import User # 引入 User 模型

# 建立藍圖實例 (所有路由前綴為 /auth)
auth_bp = APIBlueprint('auth', __name__, url_prefix='/auth')

# ==================================
# A. 輸入結構：登入請求 (Request Body)
# ==================================
class LoginIn(Schema):
    # username = String(required=True, validate=Length(min=3, max=64), description='用戶名稱')
    # password = String(required=True, validate=Length(min=6), description='密碼')
    # ❗ 修正：將 description 放在 metadata 字典中
    username = String(
        required=True, 
        validate=Length(min=3, max=64),
        metadata={'description': '用戶名稱'} 
    )
    password = String(
        required=True, 
        validate=Length(min=6),
        metadata={'description': '密碼'}
    )


# ==================================
# B. 輸出結構：登入成功響應 (Response Body)
# ==================================
class TokenOut(Schema):
    # access_token = String(description='JWT 訪問令牌')
    # token_type = String(description='Token 類型 (Bearer)', default='Bearer')
    # expires_in = Integer(description='Access Token 有效秒數')
    # ❗ 修正：將 description 放在 metadata 字典中
    access_token = String(
        metadata={'description': 'JWT 訪問令牌'}
    )
    token_type = String(
        metadata={'description': 'Token 類型 (Bearer)', 'default': 'Bearer'}
    )
    expires_in = Integer(
        metadata={'description': 'Access Token 有效秒數'}
    )

    # 這裡也可以根據需求加入用戶基本資訊

# ==================================
# C. 登入路由 (Login Endpoint)
# ==================================
@auth_bp.post('/login')
@auth_bp.input(LoginIn) # 應用輸入結構
@auth_bp.output(TokenOut, status_code=200) # 應用輸出結構
def login(json_data):
    for x in json_data:
        print(f"-> Received login data: {x} = {json_data[x]}")

    # 1. 查找用戶
    user = User.query.filter_by(username=json_data['username']).first()
    
    # 2. 驗證用戶名和密碼
    if user is None or not user.check_password(json_data['password']):
        # 使用 APIFlask 的 abort 拋出標準錯誤
        abort(401, message="用戶名或密碼錯誤。") 

    # 3. 登入成功：創建 JWT Access Token
    # identity 參數是儲存在 Token 裡面的用戶標識 (通常是 User ID)
    print("-> User authenticated successfully.", f"User ID: {user.id}, Username: {user.username}")
    # access_token = create_access_token(identity=user.id)
    access_token = create_access_token(identity=str(user.id))  # ❗ 修正：將 User ID 轉為字串---"msg": "Subject must be a string"   
    
    # 4. 回傳 Token
    return {
        'access_token': access_token,
        'token_type': 'Bearer',
        # 這裡的秒數應該從 app.config.JWT_ACCESS_TOKEN_EXPIRES 取得，
        # 為了簡化，我們先硬編碼一個值
        'expires_in': 1800 
    }

# ==================================
# D. 測試路由 (Protected Endpoint)
# ==================================
@auth_bp.get('/protected')
@jwt_required() # ❗ 應用 JWT 驗證保護
def protected():
    # 獲取 Token 中儲存的身份資訊 (User ID)
    current_user_id = get_jwt_identity()
    user = db.get_or_404(User, current_user_id) # 查找用戶
    print(f"-> Protected endpoint accessed by user ID: {current_user_id}")
    print(f"-> User details: {user}")
    
    return {
        'message': f'成功訪問！歡迎用戶 ID: {current_user_id} ({user.username})',
        'is_admin': user.is_admin
    }