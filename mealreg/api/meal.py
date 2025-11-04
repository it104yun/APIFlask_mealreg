# mealreg/api/meal.py
# 便當 (Meal) 管理 API

from apiflask import APIBlueprint, Schema, abort
from apiflask.fields import Integer, String, Boolean, Float
from apiflask.validators import Length, Range

from ..extensions import db
from ..models.canteen import Canteen
from ..models.meal import Meal
from .decorators import admin_required

# 創建藍圖，前綴為 /admin
meal_bp = APIBlueprint('meal', __name__, url_prefix='/admin/meals', tag='總務管理-菜單')

# --- Schema 定義 ---

# 輸入 Schema：新增/修改便當
class MealIn(Schema):
    name = String(
        required=True, 
        validate=Length(min=2, max=100), 
        metadata={'description': '便當名稱'}
    )
    # 價格以 "元" 為單位傳入 (APIFlask 會自動轉換為後端內部使用的 "分" 儲存)
    price = Float(
        required=True, 
        validate=Range(min=0.01), 
        metadata={'description': '便當價格 (元)'}
    )
    canteen_id = Integer(
        required=True, 
        metadata={'description': '所屬餐廳 ID'}
    )
    is_active = Boolean(
        metadata={'description': '是否活躍販售 (True/False)'}, 
        required=False, 
        load_default=True
    )

# 輸出 Schema：便當列表/詳情
class MealOut(Schema):
    id = Integer()
    name = String()
    # 輸出時將價格從 "分" 轉回 "元"
    price = Float(metadata={'description': '便當價格 (元)'}) 
    canteen_id = Integer()
    canteen_name = String(metadata={'description': '餐廳名稱'})
    is_active = Boolean()
    created_at = String(metadata={'description': '創建時間'})


# --- CRUD 路由定義 ---

# 協助將 Meal 物件轉為輸出格式
def meal_to_out(meal):
    """將 Meal 模型物件轉換為適合輸出的字典格式，並將價格轉為元"""
    return {
        'id': meal.id,
        'name': meal.name,
        # 將資料庫的 price (分) 轉換為 price (元)
        'price': meal.price / 100.0, 
        'canteen_id': meal.canteen_id,
        'canteen_name': meal.canteen.name if meal.canteen else None,
        'is_active': meal.is_active,
        'created_at': meal.created_at.isoformat() if meal.created_at else None
    }

# 1. POST: 新增便當
@meal_bp.post('/')
@admin_required() 
@meal_bp.input(MealIn)
@meal_bp.output(MealOut, status_code=201)
def create_meal(json_data):
    # for key in json_data:
    #     print(f"-> Received meal data: {key} = {json_data[key]}")

    # 檢查所屬餐廳 ID 是否存在
    # db.get_or_404(Canteen, json_data['canteen_id'], message="所屬餐廳不存在")
    db.get_or_404(Canteen, json_data['canteen_id'], description="所屬餐廳不存在")
    # 將輸入的價格 (元) 轉換為整數 (分) 儲存
    json_data['price'] = int(json_data['price'] * 100)
    
    # 創建 Meal 實例    
    meal = Meal(**json_data)
    db.session.add(meal)
    db.session.commit()
    
    return meal_to_out(meal)

# 2. GET: 獲取所有便當列表 (或依餐廳過濾)
@meal_bp.get('/')
@admin_required() 
@meal_bp.output(MealOut(many=True))
def get_meals():
    # 總務人員查看所有便當
    meals = db.session.execute(db.select(Meal).order_by(Meal.canteen_id, Meal.id)).scalars().all()
    return [meal_to_out(meal) for meal in meals]

# 3. PUT/PATCH: 更新便當
@meal_bp.put('/<int:meal_id>')
@admin_required()
@meal_bp.input(MealIn(partial=True))
@meal_bp.output(MealOut)
def update_meal(meal_id, data):
    meal = db.get_or_404(Meal, meal_id)

    # 檢查 canteen_id 是否存在 (如果傳入)
    if 'canteen_id' in data:
        db.get_or_404(Canteen, data['canteen_id'], message="所屬餐廳不存在")

    # 轉換價格 (如果傳入)
    if 'price' in data:
        data['price'] = int(data['price'] * 100)
        
    for key, value in data.items():
        setattr(meal, key, value)
    
    db.session.commit()
    return meal_to_out(meal)

# 4. DELETE: 刪除便當
@meal_bp.delete('/<int:meal_id>')
@admin_required()
# @meal_bp.output(status_code=204)  # 錯誤的寫法，會導致 500 錯誤
@meal_bp.output(status_code=204, schema=None)  # ✅ 正確的寫法 (204 No Content 代表成功刪除)
# status_code=204: 告訴客戶端操作成功，但沒有內容 (No Content)。
# schema=None: 告訴 @output 裝飾器：不需要序列化 (serialize) 任何數據，因為響應體 (response body) 將是空的。這樣就滿足了裝飾器對 schema 參數的要求，從而解決了 TypeError。


def delete_meal(meal_id):
    meal = db.get_or_404(Meal, meal_id)
    
    db.session.delete(meal)
    db.session.commit()
    return ''