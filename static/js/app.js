// 全局應用 JavaScript

// API 基礎 URL
const API_BASE_URL = '/api';

// 全局狀態
let currentUser = null;
let authToken = null;

// 初始化應用
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// 初始化應用
function initializeApp() {
    // 檢查本地存儲的認證信息
    checkAuthStatus();
    
    // 設置全局事件監聽器
    setupEventListeners();
    
    // 初始化工具提示
    initializeTooltips();
}

// 檢查認證狀態
function checkAuthStatus() {
    const token = localStorage.getItem('access_token');
    const user = localStorage.getItem('current_user');
    
    if (token && user) {
        authToken = token;
        currentUser = JSON.parse(user);
        updateUIForAuthenticatedUser();
    } else {
        updateUIForGuestUser();
    }
}

// 更新已認證用戶的 UI
function updateUIForAuthenticatedUser() {
    document.getElementById('userMenu').style.display = 'block';
    document.getElementById('loginBtn').style.display = 'none';
    document.getElementById('registerBtn').style.display = 'none';
    document.getElementById('username').textContent = currentUser.username;
}

// 更新訪客用戶的 UI
function updateUIForGuestUser() {
    document.getElementById('userMenu').style.display = 'none';
    document.getElementById('loginBtn').style.display = 'block';
    document.getElementById('registerBtn').style.display = 'block';
}

// 設置事件監聽器
function setupEventListeners() {
    // 表單提交事件
    document.addEventListener('submit', handleFormSubmit);
    
    // 點擊事件
    document.addEventListener('click', handleClick);
}

// 處理表單提交
function handleFormSubmit(event) {
    const form = event.target;
    
    if (form.classList.contains('auth-form')) {
        event.preventDefault();
        handleAuthForm(form);
    }
}

// 處理點擊事件
function handleClick(event) {
    const target = event.target;
    
    // 處理登出按鈕
    if (target.onclick && target.onclick.toString().includes('logout')) {
        event.preventDefault();
        logout();
    }
}

// 處理認證表單
async function handleAuthForm(form) {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    try {
        showLoading(form);
        
        let response;
        if (form.id === 'loginForm') {
            response = await login(data);
        } else if (form.id === 'registerForm') {
            response = await register(data);
        }
        
        if (response.success) {
            showSuccess(response.message || '操作成功');
            if (response.redirect) {
                setTimeout(() => {
                    window.location.href = response.redirect;
                }, 1500);
            }
        } else {
            showError(response.message || '操作失敗');
        }
    } catch (error) {
        showError('網絡錯誤，請稍後重試');
        console.error('表單提交錯誤:', error);
    } finally {
        hideLoading(form);
    }
}

// 登入
async function login(data) {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // 保存認證信息
            localStorage.setItem('access_token', result.access_token);
            
            // 獲取用戶信息
            const userInfo = await getCurrentUser(result.access_token);
            if (userInfo) {
                localStorage.setItem('current_user', JSON.stringify(userInfo));
                authToken = result.access_token;
                currentUser = userInfo;
                updateUIForAuthenticatedUser();
            }
            
            return {
                success: true,
                message: '登入成功',
                redirect: '/'
            };
        } else {
            return {
                success: false,
                message: result.detail || '登入失敗'
            };
        }
    } catch (error) {
        console.error('登入錯誤:', error);
        return {
            success: false,
            message: '網絡錯誤'
        };
    }
}

// 註冊
async function register(data) {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            return {
                success: true,
                message: '註冊成功，請登入',
                redirect: '/login'
            };
        } else {
            return {
                success: false,
                message: result.detail || '註冊失敗'
            };
        }
    } catch (error) {
        console.error('註冊錯誤:', error);
        return {
            success: false,
            message: '網絡錯誤'
        };
    }
}

// 獲取當前用戶信息
async function getCurrentUser(token) {
    try {
        const response = await fetch(`${API_BASE_URL}/users/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            return await response.json();
        }
        return null;
    } catch (error) {
        console.error('獲取用戶信息錯誤:', error);
        return null;
    }
}

// 登出
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('current_user');
    authToken = null;
    currentUser = null;
    updateUIForGuestUser();
    showSuccess('已成功登出');
    setTimeout(() => {
        window.location.href = '/';
    }, 1500);
}

// 顯示載入狀態
function showLoading(element) {
    const submitBtn = element.querySelector('button[type="submit"]');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="loading"></span> 處理中...';
    }
}

// 隱藏載入狀態
function hideLoading(element) {
    const submitBtn = element.querySelector('button[type="submit"]');
    if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = submitBtn.dataset.originalText || '提交';
    }
}

// 顯示成功消息
function showSuccess(message) {
    showToast(message, 'success');
}

// 顯示錯誤消息
function showError(message) {
    showToast(message, 'error');
}

// 顯示提示消息
function showToast(message, type = 'info') {
    // 創建 toast 元素
    const toast = document.createElement('div');
    toast.className = `alert alert-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    // 自動移除
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 5000);
}

// 初始化工具提示
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// API 請求輔助函數
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (authToken) {
        defaultOptions.headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    const finalOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };
    
    try {
        const response = await fetch(url, finalOptions);
        
        if (response.status === 401) {
            // Token 過期，清除認證信息
            logout();
            return null;
        }
        
        return response;
    } catch (error) {
        console.error('API 請求錯誤:', error);
        throw error;
    }
}

// 格式化日期
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('zh-TW');
}

// 格式化相對時間
function formatRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 1) return '剛剛';
    if (minutes < 60) return `${minutes} 分鐘前`;
    if (hours < 24) return `${hours} 小時前`;
    if (days < 7) return `${days} 天前`;
    
    return formatDate(dateString);
}
