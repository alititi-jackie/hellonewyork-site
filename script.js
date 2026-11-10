document.getElementById('year').textContent = new Date().getFullYear();

(function () {
  var hero = document.querySelector('.hero-full');
  if (!hero) return;
  var slides = hero.querySelectorAll('.hero-photo');
  var dots = hero.querySelectorAll('.hero-dot');
  if (slides.length < 2) return;
  var i = 0, timer = null, DELAY = 5000;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function show(n) {
    slides[i].classList.remove('is-active');
    if (dots[i]) dots[i].classList.remove('is-active');
    i = (n + slides.length) % slides.length;
    slides[i].classList.add('is-active');
    if (dots[i]) dots[i].classList.add('is-active');
  }
  function next() {
    for (var k = 1; k < slides.length; k++) {
      var n = (i + k) % slides.length;
      if (slides[n].complete && slides[n].naturalWidth > 0) { show(n); return; }
    }
  }
  function start() { if (!reduce && !timer) timer = setInterval(next, DELAY); }
  function stop() { if (timer) { clearInterval(timer); timer = null; } }
  function restart() { stop(); start(); }
  hero.addEventListener('click', function (e) {
    if (e.target.closest('a, button')) return;
    next(); restart();
  });
  dots.forEach(function (d, n) {
    d.addEventListener('click', function () { show(n); restart(); });
  });
  hero.addEventListener('mouseenter', stop);
  hero.addEventListener('mouseleave', start);
  document.addEventListener('visibilitychange', function () {
    if (document.hidden) stop(); else start();
  });
  window.addEventListener('load', function () {
    slides.forEach(function (s) { var im = new Image(); im.src = s.getAttribute('src'); });
  });
  start();
})();
