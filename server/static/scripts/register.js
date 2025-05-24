// server/static/scripts/register.js
document
  .getElementById('register-form')
  .addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const confirm = document.getElementById('confirm').value;
    if (password !== confirm) {
      return alert('Пароли не совпадают');
    }

    try {
      // POST /users/ { email, password }
      await apiFetch('/users/', {
        method: 'POST',
        body: { email, password },
      });
      alert('Успешная регистрация, теперь можно войти.');
      window.location.href = 'login.html';
    } catch (err) {
      alert(err.message);
      console.error('Ошибка регистрации:', err);
    }
  });
