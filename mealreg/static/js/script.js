// mealreg/static/js/script.js

// API 基礎 URL - 由於前端和 Flask 服務器在同一域下，我們可以直接使用相對路徑
const API_BASE_URL = ''; 

// 全域狀態管理
let userState = {
    token: localStorage.getItem('userToken') || null,
    isAdmin: false,
    isAuthenticated: false,
    currentUserId: null
};

// --- 輔助函式區域：API 呼叫 ---

async function callAPI(endpoint, method = 'GET', data = null, authRequired = true) {
    const headers = {
        'Content-Type': 'application/json',
    };

    if (authRequired && userState.token) {
        headers['Authorization'] = `Bearer ${userState.token}`;
    }

    const config = {
        method: method,
        headers: headers,
        // 只有 POST/PUT/DELETE 需要 body
        body: data ? JSON.stringify(data) : null,
    };

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
        
        // 處理登出或 Token 失效
        if (response.status === 401 || response.status === 422) {
            handleLogout();
            return { success: false, status: response.status, message: '認證失敗或過期，請重新登入。' };
        }
        
        // 204 No Content
        if (response.status === 204) {
            return { success: true, status: 204, data: null };
        }
        
        // 嘗試解析 JSON
        const result = await response.json();

        if (response.ok) {
            return { success: true, status: response.status, data: result };
        } else {
            // 處理 API 返回的錯誤 (400, 403, 409, 500)
            return { success: false, status: response.status, message: result.message || `API 請求失敗: ${response.status}` };
        }
    } catch (error) {
        console.error('網路或伺服器連接錯誤:', error);
        return { success: false, status: 0, message: '無法連接伺服器，請檢查後端是否運行。' };
    }
}

// --- 輔助函式區域：UI 控制 ---

// 導航到指定頁面區塊
function navigateTo(pageId) {
    document.querySelectorAll('.page-section').forEach(section => {
        section.style.display = 'none';
    });
    const targetSection = document.getElementById(pageId);
    if (targetSection) {
        targetSection.style.display = 'block';
    } else {
        console.error(`找不到頁面區塊: ${pageId}`);
    }
}

// 根據用戶狀態渲染導航欄
async function renderNavbar() {
    const navLinksContainer = document.getElementById('nav-links');
    navLinksContainer.innerHTML = '';
    
    // 公共連結：總是顯示
    const homeLink = `<li class="nav-item"><a class="nav-link" href="#" onclick="initApp(); return false;">首頁</a></li>`;
    navLinksContainer.innerHTML += homeLink;

    if (userState.isAuthenticated) {
        // 員工/登入用戶連結
        const orderLink = `<li class="nav-item"><a class="nav-link" href="#" onclick="showEmployeeOrderPage(); return false;">我要訂餐</a></li>`;
        const historyLink = `<li class="nav-item"><a class="nav-link" href="#" onclick="showEmployeeHistoryPage(); return false;">我的訂單</a></li>`;
        
        navLinksContainer.innerHTML += orderLink;
        navLinksContainer.innerHTML += historyLink;

        if (userState.isAdmin) {
            // 總務專屬連結
            const adminLink = `<li class="nav-item"><a class="nav-link" href="#" onclick="showAdminDashboard(); return false;">總務管理</a></li>`;
            navLinksContainer.innerHTML += adminLink;
        }

        // 登出連結
        const logoutLink = `<li class="nav-item"><a class="btn btn-danger btn-sm" href="#" onclick="handleLogout(); return false;">登出</a></li>`;
        navLinksContainer.innerHTML += logoutLink;

    } else {
        // 未登入連結
        const loginLink = `<li class="nav-item"><a class="nav-link" href="#" onclick="navigateTo('login-page'); return false;">登入</a></li>`;
        navLinksContainer.innerHTML += loginLink;
    }
}

// ----------------------
// 核心應用程式流程
// ----------------------

// 登出處理
function handleLogout() {
    userState.token = null;
    userState.isAdmin = false;
    userState.isAuthenticated = false;
    userState.currentUserId = null;
    localStorage.removeItem('userToken');
    renderNavbar();
    navigateTo('login-page');
}

// 初始化應用程式：檢查 Token 並跳轉到對應頁面
async function initApp() {
    if (userState.token) {
        // 檢查 Token 是否有效並獲取權限
        const result = await callAPI('/auth/protected', 'GET', null, true);
        
        if (result.success) {
            userState.isAuthenticated = true;
            userState.isAdmin = result.data.is_admin;
            userState.currentUserId = result.data.sub;

            // 根據權限導航
            if (userState.isAdmin) {
                showAdminDashboard();
            } else {
                showEmployeeOrderPage();
            }
        } else {
            // Token 無效，強制登出
            handleLogout();
        }
    } else {
        // 未登入，顯示登入頁
        navigateTo('login-page');
    }
    renderNavbar();
}

// ----------------------
// 頁面顯示函式 (我們將在後續步驟中填充內容)
// ----------------------

function showEmployeeOrderPage() {
    // TODO: 載入菜單數據
    navigateTo('employee-order-page');
}

function showEmployeeHistoryPage() {
    // TODO: 載入歷史訂單數據
    navigateTo('employee-history-page');
}

function showAdminDashboard() {
    // TODO: 載入管理數據
    navigateTo('admin-dashboard-page');
}

// ----------------------
// 事件監聽器：登入表單
// ----------------------

document.addEventListener('DOMContentLoaded', () => {
    // 綁定登入表單提交事件
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    // ❗ 新增：餐廳 Modal 表單提交
    document.getElementById('canteen-form').addEventListener('submit', handleCanteenSubmit);
    
    // ❗ 新增：便當 Modal 表單提交
    document.getElementById('meal-form').addEventListener('submit', handleMealSubmit);
    
    // ❗ 新增：綁定總務儀表板上的新增按鈕 (因為它們沒有 ID)
    // 透過 data-bs-target 屬性來找到對應的按鈕
    document.querySelector('[data-bs-target="#canteenModal"]').onclick = showAddCanteenModal;
    document.querySelector('[data-bs-target="#mealModal"]').onclick = showAddMealModal;
});

async function handleLogin(event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const alertElement = document.getElementById('login-alert');
    
    alertElement.classList.add('d-none');
    
    const result = await callAPI('/auth/login', 'POST', { username, password }, false);

    if (result.success) {
        // 儲存 Token
        userState.token = result.data.access_token;
        localStorage.setItem('userToken', result.data.access_token);
        
        // 重新初始化應用程式，進入主介面
        initApp();
    } else {
        // 顯示錯誤訊息
        alertElement.textContent = result.message || '登入失敗，請檢查用戶名和密碼。';
        alertElement.classList.remove('d-none');
    }
}

// **********************************************
// 接下來的步驟將圍繞填充這三個 show...Page 函式展開。
// **********************************************

// mealreg/static/js/script.js (在現有函式下方新增或修改)

// P2: 顯示員工訂餐頁面
async function showEmployeeOrderPage() {
    navigateTo('employee-order-page');
    
    const menuListElement = document.getElementById('menu-list');
    const alertElement = document.getElementById('order-status-alert');
    menuListElement.innerHTML = '<div class="spinner-border text-primary" role="status"></div> 載入菜單中...';
    alertElement.classList.add('d-none'); // 隱藏所有提示

    // 1. 呼叫 API 獲取菜單
    const result = await callAPI('/public/menu', 'GET', null, false); // /public/menu 無需 Token

    if (result.success) {
        menuListElement.innerHTML = '';
        if (result.data.length === 0) {
            menuListElement.innerHTML = '<p class="alert alert-info">今天沒有可訂購的菜單項目。</p>';
            return;
        }

        // 2. 渲染菜單列表
        result.data.forEach(canteen => {
            // 餐廳標題
            const canteenHeader = `
                <div class="col-12 mt-4 mb-3">
                    <h3>${canteen.name} <small class="text-muted fs-6">(${canteen.description || '無描述'})</small></h3>
                </div>
            `;
            menuListElement.innerHTML += canteenHeader;
            
            // 渲染便當卡片
            canteen.meals.forEach(meal => {
                const mealCard = `
                    <div class="col-md-4 col-sm-6 mb-4">
                        <div class="card h-100 shadow-sm">
                            <div class="card-body">
                                <h5 class="card-title">${meal.name}</h5>
                                <p class="card-text text-success fs-4">NT$ ${meal.price.toFixed(2)}</p>
                                <button 
                                    class="btn btn-primary order-btn" 
                                    data-meal-id="${meal.id}"
                                    data-meal-name="${meal.name}"
                                    onclick="handleCreateOrder(${meal.id}, '${meal.name}')"
                                >
                                    我要訂購
                                </button>
                            </div>
                        </div>
                    </div>
                `;
                menuListElement.innerHTML += mealCard;
            });
        });

    } else {
        menuListElement.innerHTML = `<p class="alert alert-danger">載入菜單失敗: ${result.message}</p>`;
    }
}


// 訂單創建邏輯
async function handleCreateOrder(mealId, mealName) {
    // 禁用按鈕防止重複點擊
    document.querySelectorAll('.order-btn').forEach(btn => btn.disabled = true);
    
    const alertElement = document.getElementById('order-status-alert');
    alertElement.classList.remove('d-none', 'alert-success', 'alert-danger');
    alertElement.classList.add('alert-warning');
    alertElement.textContent = `正在提交 ${mealName} 的訂單...`;
    
    // 呼叫 API 創建訂單
    const result = await callAPI('/orders', 'POST', { meal_id: mealId }, true);

    if (result.success) {
        alertElement.classList.replace('alert-warning', 'alert-success');
        alertElement.textContent = `${mealName} 訂單創建成功！您今天已訂購。`;
        
        // 訂購成功後，自動刷新並切換到訂單歷史頁面
        showEmployeeHistoryPage();
    } else {
        alertElement.classList.replace('alert-warning', 'alert-danger');
        
        if (result.status === 409) {
            alertElement.textContent = `訂購失敗：${result.message} (今天已訂過，不可重複訂購)`;
        } else {
            alertElement.textContent = `訂購失敗: ${result.message}`;
        }
        
        // 恢復按鈕
        document.querySelectorAll('.order-btn').forEach(btn => btn.disabled = false);
    }
}

// mealreg/static/js/script.js (在現有函式下方新增或修改)

// P3: 顯示員工訂單歷史頁面
async function showEmployeeHistoryPage() {
    navigateTo('employee-history-page');
    
    const tableBody = document.getElementById('history-table-body');
    tableBody.innerHTML = '<tr><td colspan="5"><div class="spinner-border spinner-border-sm text-primary" role="status"></div> 載入中...</td></tr>';
    
    const today = new Date().toISOString().slice(0, 10); // YYYY-MM-DD
    
    // 1. 呼叫 API 獲取訂單歷史
    const result = await callAPI('/orders/mine', 'GET', null, true);

    if (result.success && result.data.length > 0) {
        tableBody.innerHTML = '';
        
        // 2. 渲染訂單列表
        result.data.forEach(order => {
            const isToday = order.order_date === today;
            
            // 價格格式化
            const price = (order.price / 100).toFixed(2); 
            
            // 訂單狀態標籤
            const statusLabel = order.is_paid 
                ? '<span class="badge bg-success">已結帳</span>' 
                : '<span class="badge bg-warning text-dark">未結帳</span>';
            
            // 刪除按鈕 (僅限當日訂單)
            let actionButton = '';
            if (isToday && !order.is_paid) {
                actionButton = `
                    <button 
                        class="btn btn-sm btn-danger delete-order-btn" 
                        onclick="handleDeleteOrder(${order.id})"
                    >
                        刪除
                    </button>
                `;
            } else if (isToday && order.is_paid) {
                actionButton = `<span class="text-muted">已結帳，無法刪除</span>`;
            } else {
                actionButton = `<span class="text-muted">歷史訂單</span>`;
            }

            const row = `
                <tr id="order-row-${order.id}" class="${isToday ? 'table-primary' : ''}">
                    <td>${order.order_date}</td>
                    <td>${order.meal_name}</td>
                    <td>${price}</td>
                    <td>${statusLabel}</td>
                    <td>${actionButton}</td>
                </tr>
            `;
            tableBody.innerHTML += row;
        });
    } else if (result.success && result.data.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="5" class="text-center">您目前沒有訂單記錄。</td></tr>';
    } else {
        tableBody.innerHTML = `<tr><td colspan="5" class="text-danger">載入訂單失敗: ${result.message}</td></tr>`;
    }
}


// 訂單刪除邏輯
async function handleDeleteOrder(orderId) {
    if (!confirm('您確定要刪除這筆訂單嗎？請注意截止時間限制。')) {
        return;
    }
    
    // 禁用所有刪除按鈕
    document.querySelectorAll('.delete-order-btn').forEach(btn => btn.disabled = true);
    
    // 呼叫 API 刪除訂單
    const result = await callAPI(`/orders/del/${orderId}`, 'DELETE', null, true);

    // 重新啟用按鈕
    document.querySelectorAll('.delete-order-btn').forEach(btn => btn.disabled = false);

    if (result.success) {
        // 刪除成功，直接從 DOM 中移除該行
        const row = document.getElementById(`order-row-${orderId}`);
        if (row) {
            row.remove();
        }
        alert('訂單刪除成功！');
    } else {
        // 刪除失敗
        alert(`刪除失敗 (${result.status}): ${result.message}`);
    }
    
    // 重新載入歷史列表以確保狀態最新
    showEmployeeHistoryPage();
}

// mealreg/static/js/script.js (在現有函式下方新增或修改)

// P4: 顯示總務儀表板
async function showAdminDashboard() {
    if (!userState.isAdmin) {
        alert('權限不足，無法進入管理介面！');
        handleLogout();
        return;
    }
    navigateTo('admin-dashboard-page');
    
    // 預設顯示訂單統計 Tab
    // 我們需要同時載入統計數據和管理數據，以備切換
    await loadOrderSummary();
    await loadAdminManagementLists();
}

// ----------------------------------------------------
// Step 7.1: 訂單統計與結算 (P5)
// ----------------------------------------------------

async function loadOrderSummary() {
    const summaryDataElement = document.getElementById('summary-data');
    const mealsSummaryBody = document.getElementById('meals-summary-body');
    
    summaryDataElement.innerHTML = '<div class="spinner-border spinner-border-sm text-primary" role="status"></div> 載入中...';
    mealsSummaryBody.innerHTML = '';

    // 呼叫訂單統計 API (不需 date 參數，預設為今天)
    const result = await callAPI('/orders/summary', 'GET', null, true);

    if (result.success) {
        const data = result.data;
        
        // 渲染總計數據
        summaryDataElement.innerHTML = `
            <div class="col-md-6">
                <p class="alert alert-info">總訂單筆數: <strong>${data.total_orders} 筆</strong></p>
            </div>
            <div class="col-md-6">
                <p class="alert alert-success">總金額 (未結算): <strong>NT$ ${data.total_amount.toFixed(2)}</strong></p>
            </div>
        `;

        // 渲染按便當分類的統計表格
        if (data.meal_summary && data.meal_summary.length > 0) {
            data.meal_summary.forEach(summary => {
                const totalAmount = (summary.total_price / 100).toFixed(2);
                
                // 結算按鈕
                const actionBtn = `
                    <button 
                        class="btn btn-sm btn-primary settle-btn"
                        onclick="handleSettleOrder('${summary.meal_name}', ${summary.total_order_ids.join(',')})"
                    >
                        批量結算 (${summary.order_count} 筆)
                    </button>
                `;

                mealsSummaryBody.innerHTML += `
                    <tr>
                        <td>${summary.meal_name}</td>
                        <td>${summary.order_count} 份</td>
                        <td>NT$ ${totalAmount}</td>
                        <td>${actionBtn}</td>
                    </tr>
                `;
            });
        } else {
            mealsSummaryBody.innerHTML = '<tr><td colspan="4" class="text-center">今日尚無訂單。</td></tr>';
        }
    } else {
        summaryDataElement.innerHTML = `<p class="alert alert-danger">載入統計數據失敗: ${result.message}</p>`;
    }
}


// 批量結算處理邏輯 (只結算未結帳的訂單)
async function handleSettleOrder(mealName, orderIds) {
    if (!confirm(`您確定要結算所有未付清的 [${mealName}] 訂單嗎？這將標記為已付款。`)) {
        return;
    }

    // 禁用所有結算按鈕
    document.querySelectorAll('.settle-btn').forEach(btn => btn.disabled = true);
    
    const ids = Array.isArray(orderIds) ? orderIds : String(orderIds).split(',').map(id => parseInt(id));

    let successCount = 0;
    let failureCount = 0;

    // 由於後端 API 是單筆結算，這裡使用 Promise.all 併發處理
    const settlementPromises = ids.map(id => 
        callAPI(`/orders/${id}/paid`, 'PUT', null, true)
            .then(res => {
                if (res.success) {
                    successCount++;
                } else {
                    failureCount++;
                }
            })
    );
    
    await Promise.all(settlementPromises);
    
    // 重新啟用按鈕
    document.querySelectorAll('.settle-btn').forEach(btn => btn.disabled = false);

    if (failureCount === 0) {
        alert(`結算完成！成功標記 ${successCount} 筆訂單為已付款。`);
    } else {
        alert(`結算完成，但有 ${failureCount} 筆訂單失敗。請刷新頁面檢查。`);
    }
    
    // 刷新統計數據
    await loadOrderSummary(); 
    
    // 由於結算後員工的歷史訂單狀態也改變，我們刷新員工歷史介面 (如果正在顯示)
    if (document.getElementById('employee-history-page').style.display === 'block') {
         showEmployeeHistoryPage();
    }
}

// ----------------------------------------------------
// Step 7.2: 菜單/餐廳管理 (P6) (將在下一部分實現)
// ----------------------------------------------------
async function loadAdminManagementLists() {
    // TODO: 載入餐廳列表和便當列表的 CRUD 介面
    // 由於內容較多，我們將在下一部分逐步實現
    
    // 這裡只是預留位
    const canteenList = document.getElementById('canteen-list');
    canteenList.innerHTML = '<p class="text-muted">載入餐廳列表...</p>';
    
    const mealListAdmin = document.getElementById('meal-list-admin');
    mealListAdmin.innerHTML = '<p class="text-muted">載入便當列表...</p>';

    // (實際的載入函數：loadCanteensForAdmin(), loadMealsForAdmin())
}

// mealreg/static/js/script.js (在現有函式下方新增或修改)

// ----------------------------------------------------
// Step 7.2: 菜單/餐廳管理 (P6)
// ----------------------------------------------------

async function loadAdminManagementLists() {
    // 載入餐廳列表
    await loadCanteensForAdmin();
    // 載入便當列表
    await loadMealsForAdmin();
}

// 載入並渲染餐廳列表
async function loadCanteensForAdmin() {
    const canteenListElement = document.getElementById('canteen-list');
    canteenListElement.innerHTML = '<div class="spinner-border spinner-border-sm text-primary" role="status"></div> 載入中...';
    
    // 呼叫 API 獲取所有餐廳 (包括不活躍的)
    const result = await callAPI('/admin/canteens', 'GET', null, true);

    if (result.success) {
        canteenListElement.innerHTML = '';
        if (result.data.length === 0) {
            canteenListElement.innerHTML = '<p class="alert alert-info">尚未創建任何餐廳。</p>';
            return;
        }

        let html = '<ul class="list-group">';
        result.data.forEach(canteen => {
            const statusBadge = canteen.is_active 
                ? '<span class="badge bg-success">活躍</span>' 
                : '<span class="badge bg-secondary">下架</span>';
            
            html += `
                <li class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <strong>${canteen.name}</strong> (${canteen.description || '無描述'}) ${statusBadge}
                    </div>
                    <div>
                        <button class="btn btn-sm btn-warning me-2" onclick="showEditCanteenModal(${canteen.id}, '${canteen.name}', '${canteen.description}', ${canteen.is_active})">編輯</button>
                        <button class="btn btn-sm btn-danger" onclick="handleDeleteCanteen(${canteen.id}, '${canteen.name}')">刪除</button>
                    </div>
                </li>
            `;
        });
        html += '</ul>';
        canteenListElement.innerHTML = html;

    } else {
        canteenListElement.innerHTML = `<p class="alert alert-danger">載入餐廳列表失敗: ${result.message}</p>`;
    }
}


// 載入並渲染便當列表
async function loadMealsForAdmin() {
    const mealListElement = document.getElementById('meal-list-admin');
    mealListElement.innerHTML = '<div class="spinner-border spinner-border-sm text-primary" role="status"></div> 載入中...';
    
    // 呼叫 API 獲取所有便當
    const result = await callAPI('/admin/meals', 'GET', null, true);

    if (result.success) {
        mealListElement.innerHTML = '';
        if (result.data.length === 0) {
            mealListElement.innerHTML = '<p class="alert alert-info">尚未創建任何便當。</p>';
            return;
        }

        let html = '<ul class="list-group">';
        result.data.forEach(meal => {
            const statusBadge = meal.is_active 
                ? '<span class="badge bg-success">供應中</span>' 
                : '<span class="badge bg-secondary">停售</span>';
            const price = (meal.price / 100).toFixed(2);
            
            html += `
                <li class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <strong>${meal.name}</strong> - NT$ ${price} 
                        (${meal.canteen_name}) ${statusBadge}
                    </div>
                    <div>
                        <button class="btn btn-sm btn-warning me-2" onclick="showEditMealModal(${meal.id}, '${meal.name}', ${meal.price}, ${meal.canteen_id}, ${meal.is_active})">編輯</button>
                        <button class="btn btn-sm btn-danger" onclick="handleDeleteMeal(${meal.id}, '${meal.name}')">刪除</button>
                    </div>
                </li>
            `;
        });
        html += '</ul>';
        mealListElement.innerHTML = html;
        
    } else {
        mealListElement.innerHTML = `<p class="alert alert-danger">載入便當列表失敗: ${result.message}</p>`;
    }
}

// mealreg/static/js/script.js (在現有函式下方新增)

// ----------------------------------------------------
// CRUD 處理函式 (新增、修改、刪除)
// ----------------------------------------------------

// 通用處理函數 (這裡我們只定義刪除邏輯)
async function handleDelete(endpoint, itemName, reloadFunction) {
    if (!confirm(`確定要刪除 [${itemName}] 嗎？此操作不可逆！`)) {
        return;
    }
    
    const result = await callAPI(endpoint, 'DELETE', null, true);

    if (result.success) {
        alert(`${itemName} 刪除成功！`);
        reloadFunction(); // 刷新列表
        showEmployeeOrderPage(); // 順便刷新員工菜單
    } else {
        alert(`刪除 ${itemName} 失敗: ${result.message}`);
    }
}

// 刪除餐廳
function handleDeleteCanteen(canteenId, canteenName) {
    handleDelete(`/admin/canteens/${canteenId}`, canteenName, loadCanteensForAdmin);
}

// 刪除便當
function handleDeleteMeal(mealId, mealName) {
    handleDelete(`/admin/meals/${mealId}`, mealName, loadMealsForAdmin);
}


// TODO: 這裡還缺少新增和編輯的 Modal 邏輯
// 由於 Modal HTML 結構較複雜，我們將在 Step 7.3 中定義並完成其 JS 邏輯。

// mealreg/static/js/script.js (新增)

let currentCanteenModal = null; // 用於儲存 Bootstrap Modal 實例

// 顯示新增餐廳 Modal
function showAddCanteenModal() {
    // 重置表單和 ID
    document.getElementById('canteen-id').value = '';
    document.getElementById('canteen-name').value = '';
    document.getElementById('canteen-description').value = '';
    document.getElementById('canteen-is-active').checked = true;
    document.getElementById('canteenModalLabel').textContent = '新增餐廳';
    document.getElementById('canteen-alert').classList.add('d-none');
    
    // 顯示 Modal
    currentCanteenModal = new bootstrap.Modal(document.getElementById('canteenModal'));
    currentCanteenModal.show();
}

// 顯示編輯餐廳 Modal
function showEditCanteenModal(id, name, description, isActive) {
    // 填充表單
    document.getElementById('canteen-id').value = id;
    document.getElementById('canteen-name').value = name;
    document.getElementById('canteen-description').value = description;
    document.getElementById('canteen-is-active').checked = isActive;
    document.getElementById('canteenModalLabel').textContent = '編輯餐廳';
    document.getElementById('canteen-alert').classList.add('d-none');
    
    // 顯示 Modal
    currentCanteenModal = new bootstrap.Modal(document.getElementById('canteenModal'));
    currentCanteenModal.show();
}


// mealreg/static/js/script.js (新增)

let currentMealModal = null; // 用於儲存 Bootstrap Modal 實例

// 載入餐廳下拉選單
async function populateCanteenDropdown(selectedCanteenId = null) {
    const dropdown = document.getElementById('meal-canteen');
    dropdown.innerHTML = '<option value="">載入中...</option>';
    
    const result = await callAPI('/admin/canteens', 'GET', null, true);
    
    dropdown.innerHTML = '';
    if (result.success && result.data.length > 0) {
        result.data.forEach(canteen => {
            const selected = (canteen.id == selectedCanteenId) ? 'selected' : '';
            dropdown.innerHTML += `<option value="${canteen.id}" ${selected}>${canteen.name}</option>`;
        });
    } else {
        dropdown.innerHTML = '<option value="">請先新增餐廳</option>';
    }
}

// 顯示新增便當 Modal
function showAddMealModal() {
    document.getElementById('meal-id').value = '';
    document.getElementById('meal-name').value = '';
    document.getElementById('meal-price').value = '';
    document.getElementById('meal-is-active').checked = true;
    document.getElementById('mealModalLabel').textContent = '新增便當';
    document.getElementById('meal-alert').classList.add('d-none');
    
    populateCanteenDropdown(); // 載入餐廳清單
    
    currentMealModal = new bootstrap.Modal(document.getElementById('mealModal'));
    currentMealModal.show();
}

// 顯示編輯便當 Modal
function showEditMealModal(id, name, price, canteenId, isActive) {
    document.getElementById('meal-id').value = id;
    document.getElementById('meal-name').value = name;
    // 後端價格是分，前端顯示為元
    document.getElementById('meal-price').value = (price / 100).toFixed(2); 
    document.getElementById('meal-is-active').checked = isActive;
    document.getElementById('mealModalLabel').textContent = '編輯便當';
    document.getElementById('meal-alert').classList.add('d-none');
    
    populateCanteenDropdown(canteenId); // 載入餐廳清單並選中當前項
    
    currentMealModal = new bootstrap.Modal(document.getElementById('mealModal'));
    currentMealModal.show();
}

// mealreg/static/js/script.js (新增)

async function handleMealSubmit(event) {
    event.preventDefault();
    
    const id = document.getElementById('meal-id').value;
    const name = document.getElementById('meal-name').value;
    const price = parseFloat(document.getElementById('meal-price').value);
    const canteenId = parseInt(document.getElementById('meal-canteen').value);
    const isActive = document.getElementById('meal-is-active').checked;
    const alertElement = document.getElementById('meal-alert');
    const submitBtn = document.getElementById('meal-submit-btn');
    
    if (isNaN(price) || price <= 0) {
        alertElement.textContent = '請輸入有效的價格。';
        alertElement.classList.remove('d-none');
        return;
    }

    alertElement.classList.add('d-none');
    submitBtn.disabled = true;
    
    // 價格轉為分 (整數)
    const priceInCents = Math.round(price * 100); 

    const data = {
        name: name,
        price: priceInCents,
        canteen_id: canteenId,
        is_active: isActive
    };

    let result;
    if (id) {
        // 編輯 (PUT)
        result = await callAPI(`/admin/meals/${id}`, 'PUT', data, true);
    } else {
        // 新增 (POST)
        result = await callAPI('/admin/meals', 'POST', data, true);
    }

    submitBtn.disabled = false;

    if (result.success) {
        alert(`${id ? '編輯' : '新增'}便當成功！`);
        currentMealModal.hide(); // 關閉 Modal
        await loadAdminManagementLists(); // 刷新管理列表
        showEmployeeOrderPage(); // 刷新員工菜單 (因為可能有變動)
    } else {
        alertElement.textContent = result.message;
        alertElement.classList.remove('d-none');
    }
}

