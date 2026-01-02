(function () {
  const STORAGE_KEY = 'lingoo-theme';
  const root = document.documentElement;

  const saved = localStorage.getItem(STORAGE_KEY);
  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  const initialTheme = saved || (prefersDark ? 'dark' : 'light');
  root.setAttribute('data-theme', initialTheme);

  function applyTheme(next) {
    root.setAttribute('data-theme', next);
    localStorage.setItem(STORAGE_KEY, next);
    const toggle = document.getElementById('themeToggle');
    if (toggle) {
      toggle.textContent = next === 'dark' ? '☀️ Mode clair' : '🌙 Mode sombre';
      toggle.setAttribute('aria-pressed', next === 'dark');
    }
  }

  function toggleTheme() {
    const current = root.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
    applyTheme(current === 'dark' ? 'light' : 'dark');
  }

  window.addEventListener('DOMContentLoaded', () => {
    applyTheme(root.getAttribute('data-theme') || initialTheme);
    const toggle = document.getElementById('themeToggle');
    if (toggle) {
      toggle.addEventListener('click', toggleTheme);
    }
  });
})();
