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

/* Scrollspy: light up the header nav item for the section in view (homepage). */
(function () {
  var links = Array.prototype.slice.call(document.querySelectorAll('.topbar nav a, .mobile-nav a'));
  if (!links.length) return;
  var tracked = [];
  function bind(el, pick) {
    if (!el) return;
    var matched = links.filter(pick);
    if (matched.length) tracked.push({ el: el, links: matched });
  }
  ['guides', 'start', 'life', 'explore', 'resources'].forEach(function (id) {
    bind(document.getElementById(id), function (a) { return a.hash === '#' + id; });
  });
  if (!tracked.length) return;
  function setCurrent(entry) {
    tracked.forEach(function (t) {
      t.links.forEach(function (a) { a.classList.toggle('nav-current', t === entry); });
    });
  }
  tracked.forEach(function (t) {
    t.links.forEach(function (a) {
      a.addEventListener('click', function () { setCurrent(t); });
    });
  });
  if (!('IntersectionObserver' in window)) return;
  var visible = new Set();
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      var t = tracked.filter(function (x) { return x.el === en.target; })[0];
      if (!t) return;
      if (en.isIntersecting) visible.add(t); else visible.delete(t);
    });
    var current = tracked.filter(function (t) { return visible.has(t); })[0] || null;
    setCurrent(current);
  }, { rootMargin: '-40% 0px -55% 0px' });
  tracked.forEach(function (t) { observer.observe(t.el); });
})();

/* Share button: native share sheet where available, otherwise copy the link. */
(function () {
  var btn = document.querySelector('.share-btn');
  if (!btn) return;
  function tip(msg) {
    var t = document.createElement('div');
    t.className = 'share-tip';
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(function () { t.classList.add('show'); }, 10);
    setTimeout(function () {
      t.classList.remove('show');
      setTimeout(function () { t.remove(); }, 300);
    }, 1800);
  }
  function copyUrl(url) {
    function done() { tip('链接已复制'); }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(done, function () { tip('复制失败，请长按地址栏复制'); });
      return;
    }
    var ta = document.createElement('textarea');
    ta.value = url;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); done(); } catch (e) { tip('复制失败，请长按地址栏复制'); }
    ta.remove();
  }
  btn.addEventListener('click', function () {
    if (navigator.share) {
      navigator.share({ title: document.title, url: location.href }).catch(function () {});
    } else {
      copyUrl(location.href);
    }
  });
})();
