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
        handleRedirection(user.role);
        return true;
    }
    return false;
}

function handleRedirection(role) {
    const roleMap = {
        'ADMIN': 'manager',
        'SELLER': 'seller',
        'CASHIER': 'cashier',
        'STOREKEEPER': 'storekeeper',
        'WORKER': 'worker'
    };
    window.location.href = `/dashboard/${roleMap[role] || 'worker'}`;
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
    if (list) {
        list.innerHTML = products.map(p => `
            <tr>
                <td><strong>${p.name}</strong></td>
                <td><code class="small">${p.sku}</code></td>
                <td>${p.total_stock}</td>
                <td>-</td>
                <td><span class="badge ${p.total_stock > 10 ? 'bg-success' : 'bg-warning'}">${p.total_stock > 10 ? 'موجود' : 'کمبود'}</span></td>
                <td><button class="btn btn-sm btn-light border"><i class="bi bi-eye"></i></button></td>
            </tr>
        `).join('');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
        const user = JSON.parse(userStr);
        const sidebar = document.getElementById('sidebar');
        if (sidebar) {
            sidebar.classList.remove('d-none');
            document.getElementById('user-fullname').textContent = user.full_name;
            document.getElementById('user-role').textContent = user.role;

            const nav = document.getElementById('nav-links');
            let links = `
                <li class="nav-item"><a class="nav-link ${window.location.pathname.includes('manager') ? 'active' : ''}" href="/dashboard/manager"><i class="bi bi-speedometer2 me-2"></i> داشبورد</a></li>
                <li class="nav-item"><a class="nav-link ${window.location.pathname.includes('seller') ? 'active' : ''}" href="/dashboard/seller"><i class="bi bi-cart me-2"></i> فروش</a></li>
                <li class="nav-item"><a class="nav-link ${window.location.pathname.includes('cashier') ? 'active' : ''}" href="/dashboard/cashier"><i class="bi bi-calculator me-2"></i> صندوق</a></li>
                <li class="nav-item"><a class="nav-link ${window.location.pathname.includes('storekeeper') ? 'active' : ''}" href="/dashboard/storekeeper"><i class="bi bi-houses me-2"></i> انبارداری</a></li>
                <li class="nav-item"><a class="nav-link ${window.location.pathname.includes('worker') ? 'active' : ''}" href="/dashboard/worker"><i class="bi bi-box-seam me-2"></i> عملیات</a></li>
            `;
            nav.innerHTML = links;
            if (window.location.pathname.includes('manager')) loadProducts();
        }
    } else if (window.location.pathname !== '/') {
        window.location.href = '/';
    }
});
