// server/static/scripts/login.js

// Обработчик формы логина
document.getElementById('login-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const email = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value;

  if (!email || !password) {
    alert('Введите email и пароль');
    return;
  }

  // FastAPI ожидает form-data для /token
  const form = new URLSearchParams();
  form.append('username', email);
  form.append('password', password);

  try {
    // isJson: false, чтобы не ставить Content-Type: application/json
    const data = await apiFetch('/token', {
      method: 'POST',
      body: form,
      isJson: false,
    });

    // Сохраняем токен и имя для приветствия
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('username', email);

    alert('Вход выполнен успешно!');
    window.location.href = 'dashboard.html';

  } catch (err) {
    alert(err.message);
    console.error('Ошибка входа:', err);
  }
});
