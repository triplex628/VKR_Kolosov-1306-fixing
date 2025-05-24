// server/static/scripts/main.js

// -------- Переводы --------
const TRANSLATIONS = {
  ru: {
    login: 'Вход',
    username: 'Имя пользователя',
    password: 'Пароль',
    submitLogin: 'Войти',
    noAccount: 'Нет аккаунта?',
    register: 'Регистрация',
    regTitle: 'Регистрация',
    confirm: 'Повторите пароль',
    submitReg: 'Зарегистрироваться',
    haveAccount: 'Уже есть аккаунт?',
    dashTitle: 'Личный кабинет',
    welcome: 'Добро пожаловать, ',
    lastWorkouts: 'Последние тренировки',
    workoutPlan: 'Текущий план',
    startTraining: 'Начать тренировку',
    exercise: 'Упражнение',
    accuracy: 'Точность',
    date: 'Дата',
    skip: 'Пропустить',
    summaryTitle: 'Результаты тренировки',
    back: 'Назад на главную',
    notFound: 'Страница не найдена',
    goHome: 'Вернуться на главную',
  },
  en: {
    login: 'Login',
    username: 'Username',
    password: 'Password',
    submitLogin: 'Login',
    noAccount: "Don't have an account?",
    register: 'Register',
    regTitle: 'Register',
    confirm: 'Confirm Password',
    submitReg: 'Sign Up',
    haveAccount: 'Already have an account?',
    dashTitle: 'Dashboard',
    welcome: 'Welcome, ',
    lastWorkouts: 'Recent Workouts',
    workoutPlan: 'Current Plan',
    startTraining: 'Start Training',
    exercise: 'Exercise',
    accuracy: 'Accuracy',
    date: 'Date',
    skip: 'Skip',
    summaryTitle: 'Training Summary',
    back: 'Back to Dashboard',
    notFound: 'Page not found',
    goHome: 'Go to Dashboard',
  }
};

let currentLang = 'ru';

function applyTranslations() {
  const t = TRANSLATIONS[currentLang];
  const page = document.body.dataset.page;

  if (page === 'login') {
    document.getElementById('title').textContent = t.login;
    document.getElementById('lbl-user').textContent = t.username;
    document.getElementById('lbl-pass').textContent = t.password;
    document.getElementById('btn-login').textContent = t.submitLogin;
    document.getElementById('link-help').textContent = `${t.noAccount} `;
    document.getElementById('link-reg').textContent = t.register;
  }

  if (page === 'register') {
    document.getElementById('title').textContent = t.regTitle;
    document.getElementById('lbl-user').textContent = t.username;
    document.getElementById('lbl-pass').textContent = t.password;
    document.getElementById('lbl-confirm').textContent = t.confirm;
    document.getElementById('btn-reg').textContent = t.submitReg;
    document.getElementById('link-help').textContent = `${t.haveAccount} `;
    document.getElementById('link-login').textContent = t.login;
  }

  if (page === 'dashboard') {
    document.getElementById('dash-title').textContent = t.dashTitle;
    document.getElementById('welcome').textContent = t.welcome + 
      (localStorage.getItem('username') || '');
    document.getElementById('hdr-recent').textContent = t.lastWorkouts;
    document.getElementById('hdr-plan').textContent = t.workoutPlan;
    document.getElementById('btn-start').textContent = t.startTraining;
  }

  if (page === 'training') {
    document.getElementById('training-title').textContent = t.exercise;
    document.getElementById('btn-skip').textContent = t.skip;
  }

  if (page === 'summary') {
    document.getElementById('summary-title').textContent = t.summaryTitle;
    document.getElementById('btn-back').textContent = t.back;
  }

  if (page === 'notfound') {
    document.getElementById('nf-msg').textContent = t.notFound;
    document.getElementById('btn-home').textContent = t.goHome;
  }
}

function switchLang(lang) {
  currentLang = lang;
  document.querySelectorAll('.lang-switch button').forEach(b => {
    b.classList.toggle('active', b.id === `lang-${lang}`);
  });
  applyTranslations();
}

// Проверка авторизации
function checkAuth() {
  if (!localStorage.getItem('token')) {
    window.location.href = 'login.html';
  }
}

// Загрузка и отображение последних сессий на дашборде
async function loadDashboard() {
  const sessions = await apiFetch('/sessions/');
  const tbody = document.getElementById('recent-body');
  sessions.forEach(s => {
    const tr = document.createElement('tr');
    const date = new Date(s.started_at).toLocaleString();
    const avg = (s.scores.reduce((sum, sc) => sum + sc.score, 0) / s.scores.length).toFixed(2);
    tr.innerHTML = `
      <td>${date}</td>
      <td>${avg}</td>
      <td>${s.total_time}</td>
    `;
    tbody.appendChild(tr);
  });
}

// Загрузка и отображение списка поз на странице тренировки
async function loadTraining() {
  const poses = await apiFetch('/poses/');
  const list = document.getElementById('pose-list');
  poses.forEach(p => {
    const btn = document.createElement('button');
    btn.textContent = p.name;
    btn.onclick = () => {
      // сохраняем выбор позы и просим оценку
      const score = parseFloat(prompt(`Оцените позу "${p.name}" от 0 до 10`, '8'));
      if (!isNaN(score)) {
        sessionScores.push({ pose_id: p.id, score });
      }
    };
    list.appendChild(btn);
  });
}

// Фиксим начало сессии и собираем оценки
let sessionScores = [];
let sessionStart = null;

// Завершить сессию и отправить на бэк
async function finishSession() {
  const started_at = new Date(sessionStart).toISOString();
  const total_time = Math.floor((Date.now() - sessionStart) / 1000);
  await apiFetch('/sessions/', {
    method: 'POST',
    body: { started_at, total_time, scores: sessionScores }
  });
  window.location.href = 'summary.html';
}

// Загрузка статистики на странице summary
async function loadSummary() {
  const stats = await apiFetch('/stats/?period=day');
  // Здесь можно рисовать график или просто показать табличку
  const tbody = document.getElementById('stats-body');
  stats.forEach(pt => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${new Date(pt.period_start).toLocaleDateString()}</td>
      <td>${pt.avg_score.toFixed(2)}</td>
      <td>${pt.total_time}</td>
      <td>${pt.session_count}</td>
    `;
    tbody.appendChild(tr);
  });
}

// Logout
function logout() {
  localStorage.clear();
  window.location.href = 'login.html';
}

// Инициализация на всех страницах
document.addEventListener('DOMContentLoaded', () => {
  // переключение языка
  document.getElementById('lang-ru').onclick = () => switchLang('ru');
  document.getElementById('lang-en').onclick = () => switchLang('en');
  applyTranslations();

  const page = document.body.dataset.page;
  if (page === 'login') {
    // логика логина в login.js
  }
  if (page === 'register') {
    // логика регистрации (можете добавить аналогично login.js)
  }
  if (page === 'dashboard') {
    checkAuth();
    loadDashboard().catch(err => console.error(err));
    document.getElementById('btn-logout').onclick = logout;
  }
  if (page === 'training') {
    checkAuth();
    sessionStart = Date.now();
    loadTraining().catch(err => console.error(err));
    document.getElementById('btn-finish').onclick = finishSession;
    document.getElementById('btn-logout').onclick = logout;
  }
  if (page === 'summary') {
    checkAuth();
    loadSummary().catch(err => console.error(err));
    document.getElementById('btn-back').onclick = () => window.location.href = 'dashboard.html';
    document.getElementById('btn-logout').onclick = logout;
  }
  if (page === 'notfound') {
    document.getElementById('btn-home').onclick = () => window.location.href = 'dashboard.html';
  }
});
