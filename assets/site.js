// Receipts for YNAB site: theme toggle, FAQ accordion, hero video, license expander.
// The initial theme is applied by the inline script in each page's <head>, before paint.
(function () {
  var KEY = 'receipts-ynab-theme';
  var root = document.documentElement;

  // Theme toggle: flip and remember.
  document.querySelectorAll('.theme-toggle').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var next = root.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem(KEY, next); } catch (e) {}
    });
  });

  // Follow the system setting until the visitor picks one.
  if (window.matchMedia) {
    var mq = window.matchMedia('(prefers-color-scheme: light)');
    var onChange = function (e) {
      var stored = null;
      try { stored = localStorage.getItem(KEY); } catch (err) {}
      if (!stored) root.setAttribute('data-theme', e.matches ? 'light' : 'dark');
    };
    if (mq.addEventListener) mq.addEventListener('change', onChange);
  }

  // FAQ accordion: one item open at a time.
  var faqButtons = document.querySelectorAll('.faq-q');
  faqButtons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var wasOpen = btn.getAttribute('aria-expanded') === 'true';
      faqButtons.forEach(function (other) {
        other.setAttribute('aria-expanded', 'false');
        other.querySelector('.faq-sign').textContent = '+';
        document.getElementById(other.getAttribute('aria-controls')).hidden = true;
      });
      if (!wasOpen) {
        btn.setAttribute('aria-expanded', 'true');
        btn.querySelector('.faq-sign').textContent = '−';
        document.getElementById(btn.getAttribute('aria-controls')).hidden = false;
      }
    });
  });

  // Hero video: the still overlay plays the recording once from the start.
  var video = document.querySelector('.phone video');
  var still = document.querySelector('.phone-still');
  if (video && still) {
    video.muted = true; // browsers only allow scripted playback of muted video
    still.addEventListener('click', function () {
      still.hidden = true;
      video.currentTime = 0;
      var p = video.play();
      if (p && p.catch) p.catch(function () { still.hidden = false; });
    });
    video.addEventListener('ended', function () { still.hidden = false; });
  }

  // License expander.
  document.querySelectorAll('.expand-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var text = document.querySelector('.license-text');
      if (!text) return;
      var collapsed = text.classList.toggle('license-text-collapsed');
      btn.textContent = collapsed ? 'Show Full License' : 'Hide Full License';
    });
  });
})();
