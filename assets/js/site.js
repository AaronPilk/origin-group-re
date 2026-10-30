/* Origin Group — site.js (no dependencies besides optional Lenis) */
(() => {
  const d = document, root = d.documentElement, body = d.body;
  const RM = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const FINE = matchMedia('(hover: hover) and (pointer: fine)').matches;
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const escHTML = s => s.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  let vw = innerWidth, vh = innerHeight;

  /* ---------------- smooth scroll ---------------- */
  let lenis = null;
  if (!RM && window.Lenis) {
    lenis = new window.Lenis({ lerp: 0.085, smoothWheel: true, wheelMultiplier: 0.95 });
    const raf = t => { lenis.raf(t); requestAnimationFrame(raf); };
    requestAnimationFrame(raf);
  }
  const scrollTo = (target) => lenis ? lenis.scrollTo(target, { offset: -80, duration: 1.4 }) : target.scrollIntoView({ behavior: RM ? 'auto' : 'smooth' });
  d.querySelectorAll('a[href^="#"]').forEach(a => a.addEventListener('click', e => {
    const id = a.getAttribute('href').slice(1); const t = id && d.getElementById(id);
    if (t) { e.preventDefault(); scrollTo(t); history.replaceState(null, '', '#' + id); }
  }));

  /* ---------------- split headings into masked words ---------------- */
  d.querySelectorAll('[data-split]').forEach(el => {
    const text = el.textContent.trim().replace(/\s+/g, ' ');
    el.innerHTML = `<span class="sr-only">${escHTML(text)}</span>` + text.split(' ').map((w, i) => {
      const cls = w === '&' ? ' class="amp"' : '';
      return `<span class="w" aria-hidden="true"><span style="--i:${i}"${cls}>${escHTML(w)}</span></span>`;
    }).join(' ');
  });
  d.querySelectorAll('[data-hero] [data-split]').forEach(el => el.style.setProperty('--base', '250ms'));

  /* statement words that light up with scroll */
  const wordBlocks = [...d.querySelectorAll('[data-words]')].map(el => {
    const text = el.textContent.trim().replace(/\s+/g, ' ');
    el.innerHTML = `<span class="sr-only">${escHTML(text)}</span>` + text.split(' ').map(w => `<span class="sw" aria-hidden="true">${escHTML(w)}</span>`).join(' ');
    return { el, words: [...el.querySelectorAll('.sw')], last: -1 };
  });

  /* ---------------- reveal on enter ---------------- */
  const io = new IntersectionObserver(entries => entries.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
  }), { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
  d.querySelectorAll('[data-reveal],[data-split],[data-img]').forEach(el => io.observe(el));

  /* ---------------- hero load ---------------- */
  const markLoaded = () => requestAnimationFrame(() => root.classList.add('is-loaded'));
  const video = d.querySelector('.hero__video');
  if (video) {
    const portrait = matchMedia('(max-aspect-ratio: 4/5)').matches;
    if (portrait && video.dataset.posterPortrait) video.poster = video.dataset.posterPortrait;
    // poster paints first (LCP); the film starts once the page has loaded
    const start = () => { if (RM) return; video.preload = 'auto'; video.load(); video.addEventListener('canplay', () => video.classList.add('is-playing'), { once: true }); const p = video.play(); if (p && p.catch) p.catch(() => {}); };
    if (d.readyState === 'complete') setTimeout(start, 150); else addEventListener('load', () => setTimeout(start, 150), { once: true });
    d.addEventListener('visibilitychange', () => { if (d.hidden) video.pause(); else if (!RM) video.play().catch(() => {}); });
  }
  if (d.readyState === 'complete') markLoaded(); else addEventListener('load', markLoaded);
  setTimeout(markLoaded, 1200);

  /* ---------------- page curtain ---------------- */
  if (root.classList.contains('arriving')) {
    try { sessionStorage.removeItem('og-nav'); } catch (e) {}
    requestAnimationFrame(() => requestAnimationFrame(() => root.classList.add('is-ready')));
    setTimeout(() => root.classList.remove('arriving', 'is-ready'), 1100);
  }
  if (!RM) d.addEventListener('click', e => {
    const a = e.target.closest('a');
    if (!a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    if (a.target === '_blank' || a.hasAttribute('download') || a.hasAttribute('data-lightbox')) return;
    const url = new URL(a.href, location.href);
    if (url.origin !== location.origin || /\.(txt|xml|pdf|jpg|webp|png|mp4)$/i.test(url.pathname)) return;
    if (url.pathname === location.pathname && url.hash) return;
    e.preventDefault();
    try { sessionStorage.setItem('og-nav', '1'); } catch (err) {}
    root.classList.add('is-leaving');
    setTimeout(() => { location.href = url.href; }, 560);
  });
  addEventListener('pageshow', e => { if (e.persisted) root.classList.remove('is-leaving', 'arriving', 'is-ready'); });

  /* ---------------- nav ---------------- */
  const nav = d.querySelector('[data-nav]');
  const toggle = d.querySelector('[data-menu-toggle]');
  const menu = d.getElementById('menu');
  const setMenu = open => {
    root.classList.toggle('menu-open', open);
    toggle.setAttribute('aria-expanded', open); toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    menu.setAttribute('aria-hidden', !open);
    if (lenis) open ? lenis.stop() : lenis.start();
  };
  toggle && toggle.addEventListener('click', () => setMenu(!root.classList.contains('menu-open')));
  d.addEventListener('keydown', e => { if (e.key === 'Escape' && root.classList.contains('menu-open')) setMenu(false); });

  /* ---------------- parallax registry ---------------- */
  const par = [...d.querySelectorAll('[data-parallax]')].map(el => ({ el, speed: parseFloat(el.dataset.parallax) || 0, top: 0, h: 0 }));
  const parInner = [...d.querySelectorAll('[data-parallax-inner]')].map(el => ({ el, speed: parseFloat(el.dataset.parallaxInner) || 0, box: el.closest('figure') || el.parentElement }));
  const heroMedia = d.querySelector('[data-hero-media]');
  const heroContent = d.querySelector('[data-hero-content]');
  const measure = () => {
    vw = innerWidth; vh = innerHeight;
    par.forEach(p => { p.el.style.transform = ''; const r = p.el.getBoundingClientRect(); p.top = r.top + scrollY; p.h = r.height; });
    setupH();
  };

  /* ---------------- pinned horizontal transactions ---------------- */
  const hs = d.querySelector('[data-hscroll]');
  const htrack = hs && hs.querySelector('[data-htrack]');
  const hprog = hs && hs.querySelector('[data-hprogress]');
  let hState = null;
  function setupH() {
    if (!hs) return;
    const pin = !RM && vw > 900 && vh > 560;
    hs.classList.toggle('is-pinned', pin);
    hs.style.height = ''; htrack.style.transform = '';
    if (!pin) { hState = null; return; }
    const dist = Math.max(0, htrack.scrollWidth - vw);
    hs.style.height = (vh + dist) + 'px';
    const r = hs.getBoundingClientRect();
    hState = { top: r.top + scrollY, dist, cur: 0 };
  }
  if (hs && !RM) {
    const vp = hs.querySelector('.tx__viewport');
    vp.addEventListener('scroll', () => { if (!hState && hprog) hprog.style.transform = `scaleX(${vp.scrollLeft / Math.max(1, vp.scrollWidth - vp.clientWidth)})`; }, { passive: true });
  }

  /* ---------------- capabilities sticky list ---------------- */
  const caps = [...d.querySelectorAll('[data-cap]')];
  const capImgs = [...d.querySelectorAll('[data-cap-img]')];
  if (caps.length) {
    const cio = new IntersectionObserver(es => es.forEach(e => {
      if (!e.isIntersecting) return;
      const i = e.target.dataset.cap;
      caps.forEach(c => c.classList.toggle('is-active', c.dataset.cap === i));
      capImgs.forEach(c => c.classList.toggle('is-active', c.dataset.capImg === i));
    }), { rootMargin: '-42% 0px -42% 0px' });
    caps.forEach(c => cio.observe(c));
  }

  /* ---------------- marquees (scroll-velocity reactive) ---------------- */
  const mqs = [...d.querySelectorAll('[data-marquee]')].map(el => ({ el, dir: parseFloat(el.dataset.marquee) || 1, x: 0, half: 0, vis: false }));
  const mio = new IntersectionObserver(es => es.forEach(e => { const m = mqs.find(q => q.el === e.target); if (m) m.vis = e.isIntersecting; }));
  mqs.forEach(m => { mio.observe(m.el); });
  const measureMq = () => mqs.forEach(m => { m.half = m.el.scrollWidth / 2; });

  /* ---------------- main frame loop ---------------- */
  let lastY = scrollY, vel = 0, navHidden = false;
  if (!RM && wordBlocks.length) {
    const arm = () => { root.classList.add('words-armed'); removeEventListener('scroll', arm); };
    if (scrollY > 0) arm(); else addEventListener('scroll', arm, { passive: true });
  }
  function frame() {
    const y = scrollY;
    const dy = y - lastY; lastY = y;
    vel = lerp(vel, dy, 0.12);

    // nav state
    if (nav) {
      nav.classList.toggle('is-scrolled', y > 40);
      if (!root.classList.contains('menu-open')) {
        if (dy > 2 && y > 500 && !navHidden) { nav.classList.add('is-hidden'); navHidden = true; }
        else if ((dy < -2 || y < 200) && navHidden) { nav.classList.remove('is-hidden'); navHidden = false; }
      }
    }

    if (!RM) {
      // hero
      if (heroMedia && y < vh * 1.2) {
        const p = y / vh;
        heroMedia.style.transform = `translate3d(0,${y * 0.32}px,0)`;
        if (heroContent) { heroContent.style.transform = `translate3d(0,${y * 0.12}px,0)`; heroContent.style.opacity = clamp(1 - p * 1.3, 0, 1); }
      }
      // parallax
      for (const p of par) {
        const center = p.top + p.h / 2 - y - vh / 2;
        if (Math.abs(center) > vh * 1.6) continue;
        p.el.style.transform = `translate3d(0,${(-center * p.speed).toFixed(1)}px,0)`;
      }
      for (const p of parInner) {
        const r = p.box.getBoundingClientRect();
        if (r.bottom < -100 || r.top > vh + 100) continue;
        const prog = (r.top + r.height / 2 - vh / 2) / vh;
        p.el.style.transform = `translate3d(0,${(prog * p.speed * -100 - 7).toFixed(2)}%,0)`;
      }
      // horizontal pin
      if (hState) {
        const prog = clamp((y - hState.top) / Math.max(1, hState.dist), 0, 1);
        hState.cur = lerp(hState.cur, prog, 0.14);
        htrack.style.transform = `translate3d(${(-hState.cur * hState.dist).toFixed(1)}px,0,0)`;
        if (hprog) hprog.style.transform = `scaleX(${hState.cur.toFixed(4)})`;
      }
      // marquees
      const boost = Math.min(Math.abs(vel) * 0.35, 14);
      for (const m of mqs) {
        if (!m.vis || !m.half) continue;
        m.x -= (0.45 + boost) * m.dir;
        if (m.x <= -m.half) m.x += m.half; if (m.x > 0) m.x -= m.half;
        m.el.style.transform = `translate3d(${m.x.toFixed(2)}px,0,0)`;
      }
    }

    // word-by-word statements
    for (const b of wordBlocks) {
      const r = b.el.getBoundingClientRect();
      if (r.bottom < 0 || r.top > vh) continue;
      const prog = RM ? 1 : clamp((vh * 0.88 - r.top) / (vh * 0.55 + r.height * 0.5), 0, 1);
      const n = Math.round(prog * b.words.length);
      if (n !== b.last) { b.words.forEach((w, i) => w.classList.toggle('on', i < n)); b.last = n; }
    }
    requestAnimationFrame(frame);
  }

  /* ---------------- custom cursor ---------------- */
  if (FINE && !RM) {
    const c = d.createElement('div'); c.className = 'cursor'; c.setAttribute('aria-hidden', 'true'); c.innerHTML = '<span></span>';
    body.appendChild(c);
    const label = c.firstChild;
    let mx = -100, my = -100, cx = -100, cy = -100;
    addEventListener('pointermove', e => { mx = e.clientX; my = e.clientY; c.classList.add('is-visible'); }, { passive: true });
    d.addEventListener('pointerleave', () => c.classList.remove('is-visible'));
    const loop = () => { cx = lerp(cx, mx, 0.2); cy = lerp(cy, my, 0.2); c.style.transform = `translate3d(${cx}px,${cy}px,0)`; requestAnimationFrame(loop); };
    loop();
    d.addEventListener('pointerover', e => {
      const t = e.target.closest('[data-cursor]');
      if (t) { label.textContent = t.dataset.cursor; c.classList.add('is-label'); c.classList.remove('is-link'); return; }
      c.classList.remove('is-label');
      c.classList.toggle('is-link', !!e.target.closest('a,button,summary,input,textarea'));
    });
    // magnetic buttons
    d.querySelectorAll('[data-magnetic]').forEach(b => {
      b.addEventListener('pointermove', e => {
        const r = b.getBoundingClientRect();
        b.style.transform = `translate3d(${(e.clientX - r.left - r.width / 2) * 0.18}px,${(e.clientY - r.top - r.height / 2) * 0.28}px,0)`;
      });
      b.addEventListener('pointerleave', () => { b.style.transition = 'transform .5s cubic-bezier(.23,1,.32,1),background-color .35s,color .35s,border-color .35s'; b.style.transform = ''; setTimeout(() => b.style.transition = '', 500); });
    });
  }

  /* ---------------- lightbox ---------------- */
  const lbLinks = [...d.querySelectorAll('[data-lightbox]')];
  if (lbLinks.length) {
    const lb = d.createElement('div'); lb.className = 'lb'; lb.setAttribute('role', 'dialog'); lb.setAttribute('aria-modal', 'true'); lb.setAttribute('aria-label', 'Photo viewer');
    lb.innerHTML = `<img class="lb__img" alt=""><button class="lb__btn lb__close" type="button" aria-label="Close">${svg('x')}</button>
      <button class="lb__btn lb__prev" type="button" aria-label="Previous photo">${svg('l')}</button><button class="lb__btn lb__next" type="button" aria-label="Next photo">${svg('r')}</button><p class="lb__count"></p>`;
    body.appendChild(lb);
    const im = lb.querySelector('.lb__img'), cnt = lb.querySelector('.lb__count');
    let idx = 0, lastFocus = null;
    const show = i => {
      idx = (i + lbLinks.length) % lbLinks.length;
      const a = lbLinks[idx], src = a.getAttribute('href'), alt = (a.querySelector('img') || {}).alt || '';
      im.classList.add('is-swapping');
      const pre = new Image(); pre.onload = () => { im.src = src; im.alt = alt; im.classList.remove('is-swapping'); }; pre.src = src;
      cnt.textContent = `${String(idx + 1).padStart(2, '0')} / ${String(lbLinks.length).padStart(2, '0')}`;
    };
    const open = i => { lastFocus = d.activeElement; show(i); lb.classList.add('is-open'); if (lenis) lenis.stop(); lb.querySelector('.lb__close').focus(); };
    const close = () => { lb.classList.remove('is-open'); if (lenis) lenis.start(); lastFocus && lastFocus.focus(); };
    lbLinks.forEach((a, i) => a.addEventListener('click', e => { e.preventDefault(); open(i); }));
    lb.querySelector('.lb__close').onclick = close;
    lb.querySelector('.lb__prev').onclick = () => show(idx - 1);
    lb.querySelector('.lb__next').onclick = () => show(idx + 1);
    lb.addEventListener('click', e => { if (e.target === lb) close(); });
    d.addEventListener('keydown', e => {
      if (!lb.classList.contains('is-open')) return;
      if (e.key === 'Escape') close(); else if (e.key === 'ArrowLeft') show(idx - 1); else if (e.key === 'ArrowRight') show(idx + 1);
      else if (e.key === 'Tab') { const f = [...lb.querySelectorAll('button')]; const i = f.indexOf(d.activeElement); e.preventDefault(); f[(i + (e.shiftKey ? -1 : 1) + f.length) % f.length].focus(); }
    });
    let sx = null;
    lb.addEventListener('pointerdown', e => { sx = e.clientX; });
    lb.addEventListener('pointerup', e => { if (sx === null) return; const dx = e.clientX - sx; if (Math.abs(dx) > 50) show(idx + (dx < 0 ? 1 : -1)); sx = null; });
  }
  function svg(k) {
    const p = { x: 'M5 5l14 14M19 5L5 19', l: 'M15 5l-7 7 7 7', r: 'M9 5l7 7-7 7' }[k];
    return `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="${p}"/></svg>`;
  }

  /* ---------------- forms ---------------- */
  d.querySelectorAll('[data-form]').forEach(f => {
    f.addEventListener('submit', async e => {
      e.preventDefault();
      const ok = f.querySelector('.form__ok'), err = f.querySelector('.form__err'), btn = f.querySelector('[type=submit]');
      ok.hidden = true; err.hidden = true;
      let valid = true;
      f.querySelectorAll('[required]').forEach(i => {
        const bad = !i.value.trim() || (i.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(i.value));
        i.setAttribute('aria-invalid', bad); if (bad && valid) { i.focus(); valid = false; }
      });
      if (!valid) { err.textContent = 'Please complete the required fields.'; err.hidden = false; return; }
      const data = Object.fromEntries(new FormData(f).entries());
      if (data._honey) return;
      const kind = f.dataset.kind;
      const payload = kind === 'newsletter'
        ? { _subject: 'Select Insights signup — origingroupre.com', email: data.email, _template: 'table', _captcha: 'false' }
        : { _subject: `Website inquiry: ${data.subject}`, name: `${data.first_name} ${data.last_name}`, email: data.email, subject: data.subject, message: data.message, _replyto: data.email, _template: 'table', _captcha: 'false' };
      const label = btn.textContent; btn.disabled = true; btn.textContent = 'Sending…';
      try {
        const r = await fetch(window.OG_FORM, { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(payload) });
        if (!r.ok) throw new Error(r.status);
        f.reset(); ok.hidden = false;
      } catch (x) {
        const mail = `mailto:${window.OG_EMAIL}?subject=${encodeURIComponent(payload._subject)}&body=${encodeURIComponent(kind === 'newsletter' ? 'Please add me to Select Insights: ' + data.email : data.message + '\n\n' + payload.name + ' · ' + data.email)}`;
        err.innerHTML = `Something went wrong sending that. <a href="${mail}">Email us directly</a>.`; err.hidden = false;
      } finally { btn.disabled = false; btn.textContent = label; }
    });
  });

  /* ---------------- boot ---------------- */
  const remeasure = () => { measure(); measureMq(); };
  addEventListener('resize', (() => { let t; return () => { clearTimeout(t); t = setTimeout(remeasure, 150); }; })());
  addEventListener('load', remeasure);
  if (d.fonts && d.fonts.ready) d.fonts.ready.then(remeasure);
  remeasure();
  requestAnimationFrame(frame);
})();
