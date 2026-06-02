const API_BASE = '/inventory';
const AUTH_BASE = '/auth';

async function login(username, password) {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    const response = await fetch(`${AUTH_BASE}/login`, { method: 'POST', body: formData });
    if (response.ok) {
        const data = await response.json();
        localStorage.setItem('access_token', data.access_token);
        const user = await fetchUserProfile();
        if (user.role === 'MANAGER') window.location.href = '/dashboard/manager';
        else if (user.role === 'SELLER') window.location.href = '/dashboard/seller';
        else if (user.role === 'WORKER') window.location.href = '/dashboard/worker';
        return true;
    }
    return false;
}

async function fetchUserProfile() {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_BASE}/me`, { headers: { 'Authorization': `Bearer ${token}` } });
    const user = await response.json();
    localStorage.setItem('user', JSON.stringify(user));
    return user;
}

function logout() { localStorage.clear(); window.location.href = '/'; }

async function loadProducts() {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_BASE}/products`, { headers: { 'Authorization': `Bearer ${token}` } });
    const products = await response.json();
    const list = document.getElementById('product-list');
    if (list) list.innerHTML = products.map(p => `<tr><td>${p.sku}</td><td>${p.name}</td><td>${p.price}</td><td>${p.current_stock}</td></tr>`).join('');
}

async function loadProductsForSale() {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_BASE}/products`, { headers: { 'Authorization': `Bearer ${token}` } });
    const products = await response.json();
    const list = document.getElementById('product-sale-list');
    if (list) list.innerHTML = products.map(p => `<tr><td>${p.name}</td><td>${p.price}</td><td>${p.current_stock}</td><td><button class="btn btn-sm btn-primary" onclick="processStock('${p.sku}', 'SALE')">فروش</button></td></tr>`).join('');
}

async function loadProductsForAdjustment() {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_BASE}/products`, { headers: { 'Authorization': `Bearer ${token}` } });
    const products = await response.json();
    const list = document.getElementById('product-adjustment-list');
    if (list) list.innerHTML = products.map(p => `<tr><td>${p.name}</td><td>${p.sku}</td><td>${p.current_stock}</td><td><input type="number" id="qty-${p.sku}" class="form-control" style="width:80px"></td><td><button class="btn btn-sm btn-warning" onclick="processStock('${p.sku}', 'ADJUSTMENT')">ثبت</button></td></tr>`).join('');
}

async function processStock(sku, type) {
    const token = localStorage.getItem('access_token');
    let qty = type === 'SALE' ? -1 : parseInt(document.getElementById(`qty-${sku}`).value);
    await fetch(`${API_BASE}/products/${sku}/stock`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ quantity_change: qty, transaction_type: type })
    });
    location.reload();
}

document.addEventListener('DOMContentLoaded', () => {
    const user = JSON.parse(localStorage.getItem('user'));
    if (user && document.getElementById('user-info')) document.getElementById('user-info').textContent = `${user.full_name} (${user.role})`;
});
