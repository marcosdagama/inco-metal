/* INCO — site behaviour. No dependencies. */
(function () {
  'use strict';
  var html = document.documentElement;
  var LANG = html.lang === 'es' ? 'es' : 'en';
  var I18N = window.INCO_I18N || {};
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };

  /* ---------- language ---------- */
  // Remember an explicit choice made with the switcher.
  document.querySelectorAll('[data-setlang]').forEach(function (a) {
    a.addEventListener('click', function () {
      store.set('inco-lang', a.getAttribute('data-setlang'));
      // keep the current section when switching
      if (location.hash) a.href = a.href.split('#')[0] + location.hash;
    });
  });

  /* ---------- header ---------- */
  var hdr = document.querySelector('.hdr');
  var menuBtn = document.querySelector('.menu-btn');
  function onScroll() { if (hdr) hdr.classList.toggle('solid', window.scrollY > 24 || hdr.classList.contains('open')); }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
  if (menuBtn) {
    menuBtn.addEventListener('click', function () {
      var open = hdr.classList.toggle('open');
      menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
      onScroll();
    });
    document.querySelectorAll('.nav a').forEach(function (a) {
      a.addEventListener('click', function () {
        hdr.classList.remove('open');
        menuBtn.setAttribute('aria-expanded', 'false');
        onScroll();
      });
    });
  }

  // active section in nav
  var navLinks = [].slice.call(document.querySelectorAll('.nav a[href^="#"]'));
  var secs = navLinks.map(function (a) { return document.querySelector(a.getAttribute('href')); }).filter(Boolean);
  if (secs.length && 'IntersectionObserver' in window) {
    var secObs = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) {
          navLinks.forEach(function (a) { a.classList.toggle('on', a.getAttribute('href') === '#' + e.target.id); });
        }
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    secs.forEach(function (s) { secObs.observe(s); });
  }

  /* ---------- reveal ---------- */
  var rv = document.querySelectorAll('.rv, .timeline li');
  if ('IntersectionObserver' in window) {
    var rObs = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('vis'); rObs.unobserve(e.target); } });
    }, { threshold: 0.12 });
    rv.forEach(function (el) { rObs.observe(el); });
  } else {
    rv.forEach(function (el) { el.classList.add('vis'); });
  }

  /* ---------- process line schema ---------- */
  var schema = document.querySelector('.schema');
  if (schema) {
    var stations = [].slice.call(schema.querySelectorAll('.st'));
    var panel = document.querySelector('.schema-panel');
    var pn = panel.querySelector('.pn'), ph = panel.querySelector('h3'), pp = panel.querySelector('p');
    var cur = 0;
    function show(i) {
      cur = (i + stations.length) % stations.length;
      stations.forEach(function (s, j) {
        s.classList.toggle('on', j === cur);
        s.setAttribute('aria-pressed', j === cur ? 'true' : 'false');
      });
      var s = stations[cur];
      pn.textContent = String(cur + 1).padStart(2, '0');
      ph.textContent = s.getAttribute('data-name');
      pp.textContent = s.getAttribute('data-desc');
    }
    stations.forEach(function (s, i) {
      s.addEventListener('click', function () { show(i); });
      s.addEventListener('mouseenter', function () { show(i); });
      s.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); show(i); }
        if (e.key === 'ArrowRight') { e.preventDefault(); show(i + 1); stations[cur].focus(); }
        if (e.key === 'ArrowLeft') { e.preventDefault(); show(i - 1); stations[cur].focus(); }
      });
    });
    var prev = document.querySelector('[data-schema="prev"]'), next = document.querySelector('[data-schema="next"]');
    if (prev) prev.addEventListener('click', function () { show(cur - 1); });
    if (next) next.addEventListener('click', function () { show(cur + 1); });
    show(0);
  }

  /* ---------- project filters ---------- */
  var grid = document.getElementById('pgrid');
  if (grid) {
    var cards = [].slice.call(grid.querySelectorAll('.pc'));
    var state = { process: 'all', metal: 'all' };
    var countEl = document.getElementById('fcount');
    var resetBtn = document.getElementById('freset');
    var empty = document.getElementById('fempty');

    function matches(card, key, val) {
      return val === 'all' || (card.getAttribute('data-' + key) || '').split(' ').indexOf(val) > -1;
    }
    function visibleWith(st) {
      return cards.filter(function (c) { return matches(c, 'process', st.process) && matches(c, 'metal', st.metal); });
    }
    function apply(push) {
      var vis = visibleWith(state);
      cards.forEach(function (c) { c.hidden = vis.indexOf(c) < 0; });
      // counts per chip, given the other dimension
      document.querySelectorAll('.chip').forEach(function (b) {
        var key = b.getAttribute('data-key'), val = b.getAttribute('data-val');
        var probe = { process: state.process, metal: state.metal };
        probe[key] = val;
        var n = visibleWith(probe).length;
        var sup = b.querySelector('sup');
        if (sup) sup.textContent = n;
        b.setAttribute('aria-pressed', state[key] === val ? 'true' : 'false');
        b.disabled = n === 0 && state[key] !== val;
      });
      var tpl = vis.length === 1 ? I18N.showingOne : I18N.showing;
      countEl.textContent = (tpl || '{n}').replace('{n}', vis.length).replace('{t}', cards.length);
      resetBtn.hidden = state.process === 'all' && state.metal === 'all';
      empty.hidden = vis.length > 0;
      if (push) {
        var q = [];
        if (state.process !== 'all') q.push('process=' + state.process);
        if (state.metal !== 'all') q.push('metal=' + state.metal);
        history.replaceState(null, '', location.pathname + (q.length ? '?' + q.join('&') : '') + '#projects');
      }
    }
    document.querySelectorAll('.chip').forEach(function (b) {
      b.addEventListener('click', function () {
        var key = b.getAttribute('data-key'), val = b.getAttribute('data-val');
        state[key] = (state[key] === val && val !== 'all') ? 'all' : val;
        apply(true);
      });
    });
    resetBtn.addEventListener('click', function () { state = { process: 'all', metal: 'all' }; apply(true); });
    // restore from URL (shareable filtered views)
    var params = new URLSearchParams(location.search);
    ['process', 'metal'].forEach(function (k) {
      var v = params.get(k);
      if (v && document.querySelector('.chip[data-key="' + k + '"][data-val="' + v + '"]')) state[k] = v;
    });
    apply(false);
  }

  /* ---------- project modal ---------- */
  var modal = document.getElementById('modal');
  var DATA = window.INCO_PROJECTS || [];
  var lastFocus = null;
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function openModal(id) {
    var p = DATA.filter(function (d) { return d.id === id; })[0];
    if (!p || !modal) return;
    lastFocus = document.activeElement;
    modal.querySelector('.duo img').src = p.img;
    modal.querySelector('.duo img').alt = p.title;
    modal.querySelector('.meta').textContent = p.tag;
    modal.querySelector('h3').textContent = p.title;
    modal.querySelector('.mdesc').textContent = p.desc;
    modal.querySelector('.specs tbody').innerHTML = p.specs.map(function (s) {
      return '<tr><th scope="row">' + esc(s[0]) + '</th><td>' + esc(s[1]) + '</td></tr>';
    }).join('');
    var cta = modal.querySelector('.mcta');
    cta.setAttribute('data-process', p.formProcess || '');
    modal.classList.add('open');
    document.body.style.overflow = 'hidden';
    modal.querySelector('.mclose').focus();
  }
  function closeModal() {
    if (!modal || !modal.classList.contains('open')) return;
    modal.classList.remove('open');
    document.body.style.overflow = '';
    if (lastFocus) lastFocus.focus();
  }
  document.querySelectorAll('.pc').forEach(function (c) {
    c.addEventListener('click', function () { openModal(c.getAttribute('data-id')); });
  });
  if (modal) {
    modal.addEventListener('click', function (e) { if (e.target === modal) closeModal(); });
    modal.querySelector('.mclose').addEventListener('click', closeModal);
    modal.querySelector('.mcta').addEventListener('click', function () {
      var v = this.getAttribute('data-process');
      var sel = document.querySelector('#f-process');
      if (sel && v) sel.value = v;
      closeModal();
    });
    document.addEventListener('keydown', function (e) {
      if (!modal.classList.contains('open')) return;
      if (e.key === 'Escape') closeModal();
      if (e.key === 'Tab') { // keep focus inside the dialog
        var f = [].slice.call(modal.querySelectorAll('button, a[href]'));
        var first = f[0], last = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });
  }

  /* ---------- contact form (Web3Forms, free tier) ---------- */
  var form = document.getElementById('enquiry');
  if (form) {
    var msg = form.querySelector('.fmsg');
    var btn = form.querySelector('button[type="submit"]');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }
      var key = form.getAttribute('data-key');
      if (!key) { // prototype: no access key configured yet
        msg.className = 'fmsg';
        msg.textContent = I18N.formProto;
        return;
      }
      var data = new FormData(form);
      data.append('access_key', key);
      btn.disabled = true;
      msg.className = 'fmsg';
      msg.textContent = I18N.formSending;
      fetch('https://api.web3forms.com/submit', { method: 'POST', body: data, headers: { Accept: 'application/json' } })
        .then(function (r) { return r.json(); })
        .then(function (j) {
          if (j.success) { form.reset(); msg.className = 'fmsg ok'; msg.textContent = I18N.formOk; }
          else { throw new Error(j.message); }
        })
        .catch(function () { msg.className = 'fmsg err'; msg.textContent = I18N.formErr; })
        .then(function () { btn.disabled = false; });
    });
  }
})();
