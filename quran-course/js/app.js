(function () {
  const view = document.getElementById('view');
  const toastEl = document.getElementById('toast');
  const COURSES = window.COURSES;
  const byId = id => COURSES.find(c => c.id === id);
  const shownPct = {};   // last progress value rendered per course (for smooth animation)
  const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  /* ---------- helpers ---------- */
  function illustration(course, size) {
    const base = 'assets/illustrations/' + course.image;
    const sizes = size === 'lg' ? '(min-width: 768px) 260px, 200px' : '(min-width: 768px) 132px, 104px';
    return `<picture class="illus illus-${size}">
      <source type="image/webp" srcset="${base}-320.webp 320w, ${base}-640.webp 640w" sizes="${sizes}">
      <img src="${base}.svg" alt="" width="240" height="240" decoding="async" ${size === 'lg' ? 'fetchpriority="high"' : 'loading="eager"'}>
    </picture>`;
  }

  function progressBar(course, label = true) {
    const p = Store.progress(course);
    const from = shownPct[course.id] ?? 0;
    return `<div class="progress" data-course="${course.id}" data-target="${p.pct}">
      ${label ? `<div class="progress-meta"><span>${p.done} / ${p.total} сабақ</span><span>${p.pct}%</span></div>` : ''}
      <div class="bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${p.pct}" aria-label="${esc(course.title)} прогресі">
        <i style="width:${from}%"></i>
      </div>
    </div>`;
  }

  function animateBars() {
    requestAnimationFrame(() => requestAnimationFrame(() => {
      view.querySelectorAll('.progress').forEach(el => {
        const t = +el.dataset.target;
        el.querySelector('.bar i').style.width = t + '%';
        shownPct[el.dataset.course] = t;
      });
    }));
  }

  const arrow = '<svg class="chev" viewBox="0 0 24 24" aria-hidden="true"><path d="m9 6 6 6-6 6"/></svg>';
  const back = (href, text) => `<a class="back" href="${href}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m15 6-6 6 6 6"/></svg>${text}</a>`;
  const check = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m5 12.5 4.5 4.5L19 7.5"/></svg>';

  function toast(html) {
    toastEl.innerHTML = html;
    toastEl.classList.add('show');
    clearTimeout(toast.t);
    toast.t = setTimeout(() => toastEl.classList.remove('show'), 3200);
  }

  /* ---------- audio (device Arabic voice, if present) ---------- */
  let arVoice = null;
  function pickVoice() {
    if (!('speechSynthesis' in window)) return;
    arVoice = speechSynthesis.getVoices().find(v => /^ar/i.test(v.lang)) || null;
  }
  if ('speechSynthesis' in window) { pickVoice(); speechSynthesis.addEventListener?.('voiceschanged', pickVoice); }
  function speak(text) {
    if (!arVoice) { toast('Бұл құрылғыда араб дауысы жоқ — буынды өзіңіз дауыстап оқыңыз'); return false; }
    speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.voice = arVoice; u.lang = arVoice.lang; u.rate = .7;
    speechSynthesis.speak(u);
    return true;
  }
  const speaker = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9.5h3.5L12 5.5v13l-4.5-4H4Z"/><path d="M15.5 9a4 4 0 0 1 0 6M18 6.5a7.5 7.5 0 0 1 0 11"/></svg>';
  const starsFor = score => score >= 100 ? 3 : score >= 60 ? 2 : 1;
  function starRow(n) {
    return `<span class="stars" aria-label="${n} жұлдыз">${[1, 2, 3].map(i => `<svg viewBox="0 0 24 24" class="${i <= n ? 'on' : ''}" aria-hidden="true"><path d="m12 3 2.7 5.6 6.1.8-4.5 4.2 1.1 6.1L12 16.8l-5.4 2.9 1.1-6.1L3.2 9.4l6.1-.8Z"/></svg>`).join('')}</span>`;
  }

  /* ---------- views ---------- */
  function home() {
    const name = Store.state.name;
    const total = COURSES.reduce((n, c) => n + c.lessons.length, 0);
    const done = Store.totalDone();
    return `
      <section class="hero enter" style="--d:0">
        <p class="eyebrow">Ассаләму аләйкум${name ? ', ' + esc(name) : ''}</p>
        <h1>Құранды бірге<br>үйренейік</h1>
        <div class="overall">
          <div class="overall-ring" style="--p:${total ? Math.round(done / total * 100) : 0}"><span>${done}</span></div>
          <p><b>${done} / ${total}</b> сабақ аяқталды<br><span class="muted">Күніне бір сабақ — үлкен нәтиже</span></p>
        </div>
      </section>
      <h2 class="section-title enter" style="--d:1">Курстар</h2>
      <ul class="course-list">
        ${COURSES.map((c, i) => {
          const p = Store.progress(c);
          return `<li class="enter" style="--d:${i + 2}">
            <a class="course-card" href="#course-${c.id}">
              <div class="course-art">${illustration(c, 'sm')}</div>
              <div class="course-text">
                <h3>${c.title}</h3>
                <p>${c.desc}</p>
                <span class="pill">${p.done}/${p.total} сабақ</span>
              </div>
              ${arrow}
            </a>
          </li>`;
        }).join('')}
      </ul>`;
  }

  function course(id) {
    const c = byId(id);
    if (!c) return notFound();
    const nextIdx = c.lessons.findIndex(l => !Store.isDone(c.id, l.id));
    if (c.layout === 'path') return coursePath(c, nextIdx);
    return `
      ${back('#home', 'Басты бет')}
      <section class="course-header enter" style="--d:0">
        <div class="course-header-art">${illustration(c, 'lg')}</div>
        <div class="course-header-text">
          <h1>${c.title}</h1>
          <p>${c.desc}</p>
          ${progressBar(c)}
        </div>
      </section>
      <h2 class="section-title enter" style="--d:1">Сабақтар</h2>
      <ol class="lesson-list">
        ${c.lessons.map((l, i) => {
          const done = Store.isDone(c.id, l.id);
          return `<li class="enter" style="--d:${Math.min(i + 2, 8)}">
            <a class="lesson-card ${done ? 'done' : ''} ${i === nextIdx ? 'next' : ''}" href="#lesson-${c.id}-${l.id}">
              <span class="num">${done ? check : i + 1}</span>
              <span class="lesson-text">
                <b>${esc(l.title)}</b>
                <small><span class="${c.id === 'alippe' ? 'ar' : ''}">${esc(l.subtitle)}</span> · ${l.duration}</small>
              </span>
              ${i === nextIdx ? '<span class="pill pill-gold">Келесі</span>' : '<span></span>'}
              ${arrow}
            </a>
          </li>`;
        }).join('')}
      </ol>`;
  }

  function header(c) {
    return `<section class="course-header enter" style="--d:0">
        <div class="course-header-art">${illustration(c, 'lg')}</div>
        <div class="course-header-text">
          <h1>${c.title}</h1>
          <p>${c.desc}</p>
          ${progressBar(c)}
        </div>
      </section>`;
  }

  function coursePath(c, nextIdx) {
    const done = Store.state.completed[c.id] || {};
    return `
      ${back('#home', 'Басты бет')}
      ${header(c)}
      <h2 class="section-title enter" style="--d:1">Оқу жолы</h2>
      <ol class="path">
        ${c.lessons.map((l, i) => {
          const rec = done[l.id];
          const locked = !rec && i > (nextIdx === -1 ? c.lessons.length : nextIdx);
          const state = rec ? 'done' : i === nextIdx ? 'next' : locked ? 'locked' : '';
          const inner = `<span class="node">${rec ? check : i + 1}</span>
              <span class="path-text"><b>${esc(l.title)}</b><small class="ar">${esc(l.subtitle)}</small>${rec ? starRow(starsFor(rec.score)) : ''}</span>`;
          return `<li class="path-step enter ${i % 2 ? 'alt' : ''}" style="--d:${i + 2}">
            ${locked
              ? `<div class="path-card locked" aria-disabled="true">${inner}<span class="lock" aria-label="Жабық">${lockIcon}</span></div>`
              : `<a class="path-card ${state}" href="#lesson-${c.id}-${l.id}">${inner}${i === nextIdx ? '<span class="pill pill-gold">Бастау</span>' : ''}</a>`}
          </li>`;
        }).join('')}
      </ol>`;
  }
  const lockIcon = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="10.5" width="14" height="10" rx="2.5"/><path d="M8.5 10.5V8a3.5 3.5 0 0 1 7 0v2.5"/></svg>';

  function videoBlock(l) {
    if (l.video && l.video.youtube) {
      return `<div class="video"><iframe src="https://www.youtube-nocookie.com/embed/${encodeURIComponent(l.video.youtube)}" title="${esc(l.title)}" loading="lazy" allow="accelerometer; encrypted-media; gyroscope; picture-in-picture; fullscreen" allowfullscreen></iframe></div>`;
    }
    if (l.video && l.video.src) {
      return `<div class="video"><video src="${esc(l.video.src)}" controls playsinline preload="metadata"></video></div>`;
    }
    return `<div class="video video-empty"><div>
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13l10.5-6.5Z"/></svg>
        <p>Видеосабақ жақында қосылады</p></div></div>`;
  }

  function lesson(cid, lid) {
    const c = byId(cid);
    const l = c && c.lessons.find(x => x.id === lid);
    if (!l) return notFound();
    const idx = c.lessons.indexOf(l);
    const done = Store.isDone(cid, lid);
    return `
      ${back('#course-' + cid, c.title)}
      <article class="lesson enter" style="--d:0">
        <p class="eyebrow">${idx + 1}-сабақ · ${l.duration}</p>
        <h1>${esc(l.title)}</h1>
        ${videoBlock(l)}
        <div class="lesson-body">${l.body}</div>
        ${l.board ? `<p class="hint">Буынды басыңыз — тыңдап, дауыстап қайталаңыз. Оқылғандары белгіленеді.</p>
          <div class="board">${l.board.map((b, bi) => `<button type="button" class="syl" data-say="${esc(b.ar)}" data-bi="${bi}"><span class="ar">${b.ar}</span><small>${esc(b.tr)}</small></button>`).join('')}</div>
          <p class="board-count" aria-live="polite"><span>0</span> / ${l.board.length} оқылды</p>` : ''}
        ${l.letters ? `<div class="letters">${l.letters.map(([ch, n]) => `<div class="letter"><span class="ar">${ch}</span><small>${n}</small></div>`).join('')}</div>` : ''}
      </article>
      <section class="quiz enter" style="--d:1" data-total="${l.quiz.length}">
        <h2>Жаттығу</h2>
        ${l.quiz.map((q, qi) => `
          <fieldset class="q" data-answer="${q.answer}">
            <legend>${qi + 1}. ${esc(q.q)}</legend>
            ${q.arabic ? `<div class="q-arabic ar">${q.arabic}</div>` : ''}
            ${q.say ? `<button type="button" class="listen" data-say="${esc(q.say)}">${speaker}<span>Тыңдау</span></button>` : ''}
            <div class="options">
              ${q.options.map((o, oi) => `<button type="button" class="opt ${q.arabicOptions ? 'ar' : ''}" data-i="${oi}">${esc(o)}</button>`).join('')}
            </div>
          </fieldset>`).join('')}
        <div class="quiz-foot">
          <p class="score" aria-live="polite"></p>
          <button class="btn-primary" id="completeBtn" ${done ? '' : 'disabled'}>${done ? 'Қайта аяқтау' : 'Сабақты аяқтау'}</button>
        </div>
      </section>`;
  }

  function bindLesson(cid, lid) {
    const c = byId(cid);
    const quiz = view.querySelector('.quiz');
    const btn = document.getElementById('completeBtn');
    const scoreEl = quiz.querySelector('.score');
    const read = new Set();
    view.querySelectorAll('.syl').forEach(b => b.addEventListener('click', () => {
      speak(b.dataset.say);
      b.classList.add('read'); read.add(b.dataset.bi);
      const cnt = view.querySelector('.board-count span'); if (cnt) cnt.textContent = read.size;
    }));
    view.querySelectorAll('.listen').forEach(b => b.addEventListener('click', e => { e.stopPropagation(); speak(b.dataset.say); }));
    let answered = 0, correct = 0;
    const total = +quiz.dataset.total;
    quiz.querySelectorAll('.q').forEach(fs => {
      fs.addEventListener('click', e => {
        const b = e.target.closest('.opt');
        if (!b || fs.classList.contains('answered')) return;
        fs.classList.add('answered');
        const ok = +b.dataset.i === +fs.dataset.answer;
        b.classList.add(ok ? 'right' : 'wrong');
        if (!ok) fs.querySelector(`.opt[data-i="${fs.dataset.answer}"]`).classList.add('right');
        fs.querySelectorAll('.opt').forEach(o => o.setAttribute('aria-disabled', 'true'));
        answered++; if (ok) correct++;
        if (answered === total) {
          const pct = Math.round(correct / total * 100);
          scoreEl.textContent = `Нәтиже: ${correct} / ${total} (${pct}%)`;
          btn.disabled = false;
          btn.dataset.score = pct;
        }
      });
    });
    btn.addEventListener('click', () => {
      const score = btn.dataset.score ? +btn.dataset.score : 0;
      const newly = Store.complete(c, lid, score);
      updateChrome();
      const names = newly.map(id => (ACHIEVEMENTS.find(a => a.id === id) || {}).title).filter(Boolean);
      const stars = c.layout === 'path' ? ' ' + starRow(starsFor(score)) : '';
      toast(names.length ? `<b>Жаңа жетістік!</b> ${names.map(esc).join(', ')}${stars}` : `<b>Жарайсыз!</b> Деңгей аяқталды${stars}`);
      go('#course-' + cid);
    });
  }

  function profile() {
    const s = Store.state;
    const name = s.name || 'Шәкірт';
    const ach = Object.keys(s.achievements).length;
    return `
      <section class="profile-head enter" style="--d:0">
        <div class="avatar" aria-hidden="true">${esc(name.trim().charAt(0).toUpperCase())}</div>
        <div><h1>${esc(name)}</h1><a href="#prefs" class="link">Атыңызды өзгерту</a></div>
      </section>
      <div class="stats enter" style="--d:1">
        <div><b>${Store.totalDone()}</b><span>сабақ</span></div>
        <div><b>${Store.currentStreak()}</b><span>күн қатарынан</span></div>
        <div><b>${ach}</b><span>жетістік</span></div>
      </div>
      <h2 class="section-title enter" style="--d:2">Курс прогресі</h2>
      <div class="panel enter" style="--d:3">
        ${COURSES.map(c => `<a class="prog-row" href="#course-${c.id}">
          <div class="prog-art">${illustration(c, 'sm')}</div>
          <div class="prog-body"><b>${c.title}</b>${progressBar(c)}</div></a>`).join('')}
      </div>
      <h2 class="section-title enter" style="--d:4">Жетістіктер</h2>
      <ul class="badges enter" style="--d:5">
        ${ACHIEVEMENTS.map(a => {
          const got = !!s.achievements[a.id];
          return `<li class="badge ${got ? 'got' : ''}">
            <span class="medal" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M12 2.5 14.6 5h3.9v3.9L21 11.5 18.5 14v3.9h-3.9L12 20.5 9.4 17.9H5.5V14L3 11.5 5.5 8.9V5h3.9Z"/></svg></span>
            <b>${a.title}</b><small>${got ? a.desc : 'Әлі ашылмаған'}</small></li>`;
        }).join('')}
      </ul>`;
  }

  function settings() {
    const st = Store.state.settings;
    return `
      ${back('#home', 'Басты бет')}
      <h1 class="page-title enter" style="--d:0">Баптаулар</h1>
      <form class="panel settings enter" style="--d:1" id="settingsForm">
        <label class="field"><span>Атыңыз</span>
          <input name="name" maxlength="40" autocomplete="given-name" value="${esc(Store.state.name)}" placeholder="Мысалы, Айгерім"></label>
        <div class="field"><span>Мәтін өлшемі</span>
          <div class="seg" role="radiogroup" aria-label="Мәтін өлшемі">
            ${[[0.9, 'Кіші'], [1, 'Қалыпты'], [1.15, 'Үлкен']].map(([v, t]) =>
              `<label><input type="radio" name="fontScale" value="${v}" ${st.fontScale == v ? 'checked' : ''}><span>${t}</span></label>`).join('')}
          </div></div>
        <label class="switch"><span>Анимацияны азайту</span>
          <input type="checkbox" name="reduceMotion" ${st.reduceMotion ? 'checked' : ''}><i></i></label>
        <button class="btn-primary" type="submit">Сақтау</button>
      </form>
      <div class="panel danger enter" style="--d:2">
        <p><b>Прогресті тазалау</b><br><span class="muted">Барлық аяқталған сабақтар мен жетістіктер өшіріледі.</span></p>
        <button class="btn-ghost" id="resetBtn" type="button">Тазалау</button>
      </div>`;
  }

  function bindSettings() {
    const form = document.getElementById('settingsForm');
    form.addEventListener('submit', e => {
      e.preventDefault();
      const fd = new FormData(form);
      Store.state.name = String(fd.get('name') || '').trim();
      Store.state.settings.fontScale = +fd.get('fontScale') || 1;
      Store.state.settings.reduceMotion = !!fd.get('reduceMotion');
      Store.save();
      applySettings();
      toast('<b>Сақталды</b>');
    });
    document.getElementById('resetBtn').addEventListener('click', e => {
      const btn = e.currentTarget;
      if (!btn.dataset.armed) {
        btn.dataset.armed = '1'; btn.textContent = 'Иә, өшіру';
        setTimeout(() => { delete btn.dataset.armed; btn.textContent = 'Тазалау'; }, 4000);
        return;
      }
      {
        Store.reset(); applySettings(); updateChrome();
        Object.keys(shownPct).forEach(k => delete shownPct[k]);
        toast('Прогресс тазаланды'); go('#home');
      }
    });
  }

  function notFound() {
    return `<div class="panel empty"><h1>Бет табылмады</h1><p><a class="link" href="#home">Басты бетке оралу</a></p></div>`;
  }

  /* ---------- router ---------- */
  function go(hash) { if (location.hash === hash) render(); else location.hash = hash; }

  function route() {
    const h = location.hash.replace(/^#/, '');
    const parts = h.split('-');
    switch (parts[0]) {
      case '': case 'home': return { html: home(), nav: 'home' };
      case 'course': return { html: course(parts[1]), nav: 'home' };
      case 'lesson': return { html: lesson(parts[1], parts[2]), nav: 'home', bind: () => bindLesson(parts[1], parts[2]) };
      case 'profile': return { html: profile(), nav: 'profile' };
      case 'prefs': return { html: settings(), nav: 'settings', bind: bindSettings };
      default: return { html: notFound(), nav: '' };
    }
  }

  function render() {
    const r = route();
    const swap = () => {
      view.innerHTML = r.html;
      document.querySelectorAll('[data-nav]').forEach(a => {
        const on = a.dataset.nav === r.nav;
        a.classList.toggle('active', on);
        on ? a.setAttribute('aria-current', 'page') : a.removeAttribute('aria-current');
      });
      r.bind && r.bind();
      animateBars();
      window.scrollTo(0, 0);
      view.focus({ preventScroll: true });
    };
    if (document.startViewTransition && !reducedMotion() && view.childElementCount) {
      document.startViewTransition(swap);
    } else swap();
  }

  function reducedMotion() {
    return Store.state.settings.reduceMotion || matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  function applySettings() {
    const st = Store.state.settings;
    document.documentElement.style.setProperty('--font-scale', st.fontScale);
    document.documentElement.classList.toggle('reduce-motion', !!st.reduceMotion);
  }

  function updateChrome() {
    const n = Store.currentStreak();
    const el = document.getElementById('streak');
    el.innerHTML = n ? `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3c1 3.5 5 5.5 5 10a5 5 0 0 1-10 0c0-2 1-3.5 2-4.5 0 2 1 3 2 3 0-3-1-5.5 1-8.5Z"/></svg><span>${n}</span>` : '';
    el.setAttribute('aria-label', n ? `${n} күн қатарынан` : '');
  }

  applySettings();
  updateChrome();
  window.addEventListener('hashchange', render);
  render();
})();
