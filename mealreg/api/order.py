# mealreg/api/order.py
# 這個 API 將允許任何已登入的員工選擇當天可用的便當，並將訂購記錄寫入 order_record 資料庫表格。

from datetime import date, time, datetime
from apiflask import APIBlueprint, Schema, abort
from apiflask.fields import Integer, String, Float, Boolean, DateTime
from apiflask.validators import Range
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..api.decorators import admin_required

from apiflask.fields import Integer, String, Float, Boolean, DateTime, List, Nested
# 雖然 list 是 Python 的內建型別，但在定義 Marshmallow/APIFlask Schema 欄位時，必須使用從 apiflask.fields 匯入的 List (大寫 L)。

from ..extensions import db
from ..models.user import User
from ..models.meal import Meal
from ..models.order import Order
from ..models.canteen import Canteen  # 用於檢查餐廳是否活躍
from ..models.setting import Setting  # 用於截止時間設定
from sqlalchemy import func, select   # ❗ 匯入 func 函式 (用於 GROUP BY 和 SUM)

# 1. 員工訂單藍圖 (前綴 /orders),前綴為 /orders
order_bp = APIBlueprint('order', __name__, url_prefix='/orders', tag='員工-訂單')


# --- Schema 定義 ---

# 1. 輸入 Schema：訂購請求 (POST /orders)
class OrderIn(Schema):
    meal_id = Integer(
        required=True, 
        validate=Range(min=1), 
        metadata={'description': '欲訂購的便當 ID'}
    )

# 2. 輸出 Schema：單筆訂單詳情
class OrderOut(Schema):
    id = Integer(metadata={'description': '訂單 ID'})
    user_id = Integer(metadata={'description': '訂購人 ID'})
    
    # 訂單快照資訊
    meal_name = String(metadata={'description': '訂購時的便當名稱快照'})
    price = Float(metadata={'description': '訂購時的價格快照 (元)'})
    
    is_paid = Boolean(metadata={'description': '是否已繳款'})
    order_date = String(metadata={'description': '訂購日期 (YYYY-MM-DD)'})
    created_at = DateTime(metadata={'description': '訂單創建時間'})

#   核心功能：總務人員的訂單統計與結算 API。
#   這個功能允許總務人員：
#                   (1).查看某一天或今天的訂單總結（哪些便當被訂了多少份）。
#                   (2).將員工的訂單標記為已繳款。
# 3. 輸出 Schema：每日訂單統計總結
class OrderSummaryOut(Schema):
    order_date = String(metadata={'description': '統計的日期'})
    total_orders = Integer(metadata={'description': '當天總訂單數'})
    total_amount = Float(metadata={'description': '當天總金額 (元)'})
    
    # 按便當分類的明細列表
    meals_summary = List(
        # 內層 Schema：單個便當的統計
        Nested(Schema.from_dict({
            'meal_name': String(metadata={'description': '便當名稱快照'}),
            'count': Integer(metadata={'description': '訂購數量'}),
            'total_price': Float(metadata={'description': '該便當總金額 (元)'})
        })),
        metadata={'description': '按便當分類的訂單明細'}
    )



# --- 路由定義 ---
def order_to_out(order):
    """將 Order 模型物件轉換為適合輸出的字典格式，並將價格快照轉為元"""
    return {
        'id': order.id,
        'user_id': order.user_id,
        'meal_name': order.meal_name_snapshot,
        'price': order.price_snapshot / 100.0,
        'is_paid': order.is_paid,
        'order_date': order.order_date.isoformat(),
        'created_at': order.created_at
    }

@order_bp.post('/')
@jwt_required() # ❗ 需要登入才能訂購
@order_bp.input(OrderIn)
@order_bp.output(OrderOut, status_code=201)
def place_order(json_data):
    """員工下訂單：選擇當日便當"""
    user_id = get_jwt_identity()
    meal_id = json_data['meal_id']
    today = date.today()

    # 1. 檢查用戶今天是否已經訂購
    existing_order = Order.query.filter_by(user_id=user_id, order_date=today).first()
    if existing_order:
        abort(409, description=f"您今天 ({today.isoformat()}) 已經訂購過了。")

    # 2. 檢查便當是否存在且活躍
    meal = db.get_or_404(Meal, meal_id, description="找不到指定的便當或該便當已下架。")
    if not meal.is_active:
        abort(400, description="該便當目前已暫停販售。")
        
    # 3. 檢查便當所屬餐廳是否活躍
    # 這裡需要找到便當的餐廳 ID，並檢查餐廳的活躍狀態
    canteen = db.get_or_404(Canteen, meal.canteen_id, description="找不到所屬餐廳。")
    if not canteen.is_active:
        abort(400, description=f"所屬餐廳 '{canteen.name}' 目前暫停訂購。")

    # 4. 創建新的訂單，並記錄價格快照
    new_order = Order(
        user_id=user_id,
        meal_id=meal_id,
        meal_name_snapshot=meal.name, # 紀錄名稱快照
        price_snapshot=meal.price,    # 紀錄價格快照 (分)
        order_date=today,
        is_paid=False
    )
    
    db.session.add(new_order)
    db.session.commit()
    
    return order_to_out(new_order)

# 實作員工查詢自己的訂單
@order_bp.get('/mine')
@jwt_required()
@order_bp.output(OrderOut(many=True))
def get_my_orders():
    """查詢當前用戶的所有歷史訂單"""
    user_id = get_jwt_identity()
    
    # 查詢該用戶所有訂單，並按日期倒序排列
    orders = db.session.execute(
        db.select(Order).filter_by(user_id=user_id).order_by(Order.order_date.desc())
    ).scalars().all()
    
    return [order_to_out(order) for order in orders]


@order_bp.get('/summary')
@admin_required() # ❗ 總務權限
@order_bp.input(Schema.from_dict({'date': String(metadata={'description': '查詢日期 (YYYY-MM-DD)', 'example': '2025-11-04'}, load_default=date.today().isoformat())}), location='query')
@order_bp.output(OrderSummaryOut)
def get_order_summary(query_data):
    """總務人員獲取每日訂單統計總結"""
    
    # 嘗試將查詢參數的日期字串轉換為 date 物件
    try:
        query_date = date.fromisoformat(query_data['date'])
    except ValueError:
        abort(400, description="日期格式無效，請使用 YYYY-MM-DD 格式。")

    # 1. 執行 GROUP BY 查詢，按便當名稱分組
    # 這裡我們使用 SQLAlchemy Core 的 select 語句配合 func 進行聚合
    meal_summary_stmt = select(
        Order.meal_name_snapshot,
        func.count(Order.id).label('count'),
        func.sum(Order.price_snapshot).label('total_price_cents')
    ).filter_by(order_date=query_date).group_by(Order.meal_name_snapshot)

    meal_summary_results = db.session.execute(meal_summary_stmt).all()

    # 2. 處理和彙總數據
    total_orders = 0
    total_amount_cents = 0
    meals_summary = []

    for name, count, total_price_cents in meal_summary_results:
        total_orders += count
        total_amount_cents += total_price_cents
        
        meals_summary.append({
            'meal_name': name,
            'count': count,
            'total_price': total_price_cents / 100.0 # 轉為元
        })

    # 3. 輸出最終結果
    return {
        'order_date': query_date.isoformat(),
        'total_orders': total_orders,
        'total_amount': total_amount_cents / 100.0, # 轉為元
        'meals_summary': meals_summary
    }


@order_bp.put('/<int:order_id>/paid')
@admin_required() # ❗ 總務權限
@order_bp.output(OrderOut)
def mark_order_paid(order_id):
    """總務人員標記單筆訂單為已繳款"""
    
    order = db.get_or_404(Order, order_id, description="找不到該訂單。")
    
    if order.is_paid:
        # 如果已經繳款，則無需重複操作
        return order_to_out(order)

    # 標記為已繳款
    order.is_paid = True
    db.session.commit()
    
    return order_to_out(order)

@order_bp.delete('/del/<int:order_id>')
@jwt_required()
@order_bp.output(Schema(),status_code=204)
def delete_order(order_id):
    """
    刪除訂單 (總務可刪除所有，員工只能刪除自己的)
    規則：必須在訂單日 設定的截止時間 (例如 12:00 PM) 前刪除。
    """
    user_id = get_jwt_identity()
    current_user = db.get_or_404(User, user_id)
    order = db.get_or_404(Order, order_id, description="找不到該訂單。")
    
    # --- 1. 動態讀取截止時間設定 ---
    cutoff_setting = Setting.query.filter_by(key='ORDER_CUTOFF_TIME').first()
    
    if not cutoff_setting:
        # 如果設定不存在，使用硬編碼預設值作為備用 (例如 12:00)
        cutoff_time = time(12, 0, 0) 
        time_str = "12:00"
    else:
        # 嘗試解析儲存在資料庫中的時間字串 (例如 '12:00')
        try:
            hour, minute = map(int, cutoff_setting.value.split(':'))
            cutoff_time = time(hour, minute, 0)
            time_str = cutoff_setting.value
        except ValueError:
            # 解析失敗，使用硬編碼預設值
            cutoff_time = time(12, 0, 0)
            time_str = "12:00 (設定解析錯誤)"

    # --- 2. 時間檢查：確認是否已過當日截止時間 ---
    
    # 結合訂單日期和設定的截止時間
    cutoff_datetime = datetime.combine(order.order_date, cutoff_time)
    now = datetime.now() 
    
    # 如果當前時間超過截止時間，則禁止刪除
    if now > cutoff_datetime:
        abort(403, message=f"已超過訂單日 {time_str} 刪除截止時間，無法刪除。")
        
    # --- 3. 權限檢查 (邏輯不變) ---
    if not current_user.is_admin and order.user_id != user_id:
        abort(403, message="您沒有權限刪除此訂單。您只能刪除自己的訂單。")
        
    # --- 4. 執行刪除 (邏輯不變) ---
    db.session.delete(order)
    db.session.commit()
    
    return ''