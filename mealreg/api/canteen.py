# mealreg/api/canteen.py
# 餐廳 (Canteen) 管理 API

from apiflask import APIBlueprint, Schema, abort
from apiflask.fields import Integer, String, Boolean
from apiflask.validators import Length
from flask import jsonify

from ..extensions import db
from ..models.canteen import Canteen
from .decorators import admin_required

# 創建藍圖，前綴為 /admin
canteen_bp = APIBlueprint('canteen', __name__, url_prefix='/admin/canteens', tag='總務管理-餐廳')

# --- Schema 定義 ---

# 輸入 Schema：新增/修改餐廳
class CanteenIn(Schema):
    name = String(
        required=True, 
        validate=Length(min=2, max=100), 
        metadata={'description': '餐廳名稱'}
    )
    description = String(
        validate=Length(max=255), 
        metadata={'description': '餐廳描述'}, 
        required=False
    )
    is_active = Boolean(
        metadata={'description': '是否開放訂購 (True/False)'}, 
        required=False, 
        load_default=True # 預設為開放
    )

# 輸出 Schema：餐廳列表/詳情
class CanteenOut(Schema):
    id = Integer(metadata={'description': '餐廳 ID'})
    name = String()
    description = String()
    is_active = Boolean()
    created_at = String(metadata={'description': '創建時間'})


# --- CRUD 路由定義 ---

# 1. POST: 新增餐廳
@canteen_bp.post('/')
@admin_required() # ❗ 總務人員權限檢查
@canteen_bp.input(CanteenIn)
@canteen_bp.output(CanteenOut, status_code=201)
def create_canteen(json_data):
    # 檢查餐廳名稱是否已存在
    if Canteen.query.filter_by(name=json_data['name']).first():
        abort(409, message=f"餐廳名稱 '{json_data['name']}' 已存在。")

    # 創建 Canteen 實例
    canteen = Canteen(**json_data)
    
    db.session.add(canteen)
    db.session.commit()
    
    return canteen

# 2. GET: 獲取所有餐廳列表
@canteen_bp.get('/')
@canteen_bp.output(CanteenOut(many=True))
@admin_required() # ❗ 總務人員權限檢查
def get_canteens():
    # 這裡我們讓總務人員看到所有餐廳，包含不活躍的
    canteens = db.session.execute(db.select(Canteen).order_by(Canteen.id)).scalars().all()
    return canteens

# 3. GET: 獲取單個餐廳詳情
@canteen_bp.get('/<int:canteen_id>')
@admin_required() # ❗ 總務人員權限檢查
@canteen_bp.output(CanteenOut)
def get_canteen(canteen_id):
    # 使用 db.get_or_404 找不到時自動拋出 404
    canteen = db.get_or_404(Canteen, canteen_id)
    return canteen

# 4. PUT/PATCH: 更新餐廳 (我們用 PUT 實作完整的替換)
@canteen_bp.put('/<int:canteen_id>')
@admin_required() # ❗ 總務人員權限檢查
@canteen_bp.input(CanteenIn(partial=True)) # partial=True 允許部分更新
@canteen_bp.output(CanteenOut)
def update_canteen(canteen_id, data):
    canteen = db.get_or_404(Canteen, canteen_id)

    # 更新欄位
    for key, value in data.items():
        setattr(canteen, key, value)
    
    db.session.commit()
    return canteen

# 5. DELETE: 刪除餐廳
@canteen_bp.delete('/<int:canteen_id>')
@admin_required() # ❗ 總務人員權限檢查
# @canteen_bp.output(status_code=204) # 錯誤的寫法，會導致 500 錯誤
@canteen_bp.output(status_code=204, schema=None)  # ✅ 正確的寫法 (204 No Content 代表成功刪除)
# status_code=204: 告訴客戶端操作成功，但沒有內容 (No Content)。
# schema=None: 告訴 @output 裝飾器：不需要序列化 (serialize) 任何數據，因為響應體 (response body) 將是空的。這樣就滿足了裝飾器對 schema 參數的要求，從而解決了 TypeError。


def delete_canteen(canteen_id):
    canteen = db.get_or_404(Canteen, canteen_id)
    
    db.session.delete(canteen)
    db.session.commit()
    return '' # 204 響應不需要內容