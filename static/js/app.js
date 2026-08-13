async function api(url, options = {}) {
  try {
    const response = await fetch(url, {headers: {'Content-Type':'application/json', ...(options.headers || {})}, ...options});
    const data = await response.json().catch(() => ({success:false,message:'Invalid server response.'}));
    if (!response.ok) { showToast(data.message || 'Request failed.', 'error'); return data; }
    if (data.message && data.success !== false) showToast(data.message, 'success');
    return data;
  } catch (err) { showToast('Unable to connect to the server.', 'error'); return {success:false,message:'Network error.'}; }
}
function showToast(message, type='success') {
  const container = document.getElementById('toast-container'); if (!container) return;
  const toast = document.createElement('div'); toast.className = `toast ${type}`; toast.textContent = message; container.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}
async function logout() { const result = await api('/api/logout', {method:'POST'}); if (result.success) location.href='/login'; }
function escapeHtml(value) { const div=document.createElement('div'); div.textContent=value ?? ''; return div.innerHTML; }
function formatDate(value) { return new Date(`${value}T00:00:00`).toLocaleDateString(undefined,{day:'2-digit',month:'short',year:'numeric'}); }
