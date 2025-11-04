# mealreg/api/public.py
# 由於這個 API 的目的是展示給員工，我們需要一個專門的輸出結構來組織數據：按餐廳分組並列出其活躍的菜單。

from apiflask import APIBlueprint, Schema
from apiflask.fields import Integer, String, Boolean, Float, List, Nested
from ..extensions import db
from ..models.canteen import Canteen
from ..models.meal import Meal

# 創建藍圖，前綴為 /public
public_bp = APIBlueprint('public', __name__, url_prefix='/public', tag='公開查詢-員工')

# --- Schema 定義 ---

# 1. 巢狀結構：單個活躍便當的輸出 Schema
class ActiveMealOut(Schema):
    id = Integer(metadata={'description': '便當 ID'})
    name = String(metadata={'description': '便當名稱'})
    price = Float(metadata={'description': '價格 (元)'})
    # is_active=True 不需再輸出，因為只列出活躍的

# 2. 主輸出結構：活躍餐廳與其菜單列表
class CanteenMenuOut(Schema):
    id = Integer(metadata={'description': '餐廳 ID'})
    name = String(metadata={'description': '餐廳名稱'})
    description = String(metadata={'description': '餐廳描述'})
    is_active = Boolean(metadata={'description': '是否開放訂購'})
    
    # 巢狀列表：包含該餐廳所有活躍的菜單
    meals = List(
        Nested(ActiveMealOut), 
        metadata={'description': '該餐廳目前所有可訂購的便當列表'}
    )


# --- 路由定義 ---實作菜單查詢路由

# GET: 獲取所有活躍的餐廳和菜單
@public_bp.get('/menu')
@public_bp.output(CanteenMenuOut(many=True))
def get_active_menu():
    """獲取所有目前可訂購的餐廳及其菜單"""
    
    # 1. 查詢所有活躍的餐廳 (Canteen)
    active_canteens = db.session.execute(
        db.select(Canteen).filter_by(is_active=True).order_by(Canteen.id)
    ).scalars().all()
    
    result = []
    
    for canteen in active_canteens:
        # 2. 查詢該餐廳所有活躍的便當 (Meal)
        active_meals = db.session.execute(
            db.select(Meal).filter_by(canteen_id=canteen.id, is_active=True)
            .order_by(Meal.id)
        ).scalars().all()
        
        # 3. 組合數據
        meals_list = []
        for meal in active_meals:
            meals_list.append({
                'id': meal.id,
                'name': meal.name,
                'price': meal.price / 100.0, # 將 "分" 轉 "元"
            })
            
        result.append({
            'id': canteen.id,
            'name': canteen.name,
            'description': canteen.description,
            'is_active': canteen.is_active,
            'meals': meals_list
        })
        
    return result