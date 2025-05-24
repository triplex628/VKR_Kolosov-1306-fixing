// server/static/scripts/api.js
const API_BASE = 'http://localhost:8000';

async function apiFetch(path, { method = 'GET', body = null, isJson = true } = {}) {
  const headers = {};
  if (isJson) headers['Content-Type'] = 'application/json';
  const token = localStorage.getItem('token');
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body && isJson ? JSON.stringify(body) : body,
  });

  if (!res.ok) {
    let err;
    try { err = (await res.json()).detail || (await res.text()); }
    catch { err = res.statusText; }
    throw new Error(err);
  }
  return res.status === 204 ? null : res.json();
}
