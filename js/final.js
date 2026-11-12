/* Multiprint — version finale : recherche, catalogue filtrable, devis par étapes, actualités, carte, newsletter.
   Complète main.js (menu, apparitions, onglets, ligne de production, frise). */
(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const norm = s => (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');

  /* ---------- Recherche (index statique du site, window.MP_INDEX) ---------- */
  const dlg = $('#search');
  if (dlg && window.MP_INDEX) {
    const input = $('#search-q', dlg), list = $('#search-list', dlg);
    const render = q => {
      const n = norm(q).trim();
      const hits = window.MP_INDEX.filter(it => !n || norm(it.t + ' ' + it.d + ' ' + (it.k || '')).includes(n)).slice(0, 12);
      list.replaceChildren(...(hits.length ? hits.map(it => {
        const a = document.createElement('a'); a.href = it.u;
        a.innerHTML = `<b></b><small></small><em></em>`;
        a.querySelector('b').textContent = it.t; a.querySelector('small').textContent = it.d; a.querySelector('em').textContent = it.c;
        return a;
      }) : [Object.assign(document.createElement('p'), { className: 'search__empty', textContent: 'Aucun résultat. Essayez « étiquettes », « capsules » ou « devis ».' })]));
      $('#search-count', dlg).textContent = hits.length ? `${hits.length} résultat${hits.length > 1 ? 's' : ''}` : 'Aucun résultat';
    };
    let opener = $('[data-search-open]');
    $$('[data-search-open]').forEach(b => b.addEventListener('click', () => { opener = b; dlg.showModal(); input.value = ''; render(''); input.focus(); }));
    // Le navigateur rend le focus à l'élément actif d'avant l'ouverture (souvent body avec le raccourci /) : on le replace après lui
    dlg.addEventListener('close', () => setTimeout(() => { if (opener && opener.offsetParent !== null) opener.focus(); }, 0));
    $('[data-search-close]', dlg).addEventListener('click', () => dlg.close());
    dlg.addEventListener('click', e => { if (e.target === dlg) dlg.close(); });
    input.addEventListener('input', () => render(input.value));
    input.addEventListener('keydown', e => { if (e.key === 'ArrowDown') { e.preventDefault(); list.querySelector('a')?.focus(); } });
    list.addEventListener('keydown', e => {
      const links = $$('a', list), i = links.indexOf(document.activeElement);
      if (e.key === 'ArrowDown' && i < links.length - 1) { e.preventDefault(); links[i + 1].focus(); }
      if (e.key === 'ArrowUp') { e.preventDefault(); (i > 0 ? links[i - 1] : input).focus(); }
    });
    addEventListener('keydown', e => { if (e.key === '/' && !/input|textarea|select/i.test(document.activeElement.tagName) && !dlg.open) { e.preventDefault(); $('[data-search-open]').click(); } });
  }

  /* ---------- Catalogue : filtres gamme / secteur / matière, mot-clé, grille ou liste ---------- */
  const cat = $('[data-catalog]');
  if (cat) {
    const grid = $('.pgrid', cat), cards = $$('.pcard', grid), count = $('#cat-count'), empty = $('#cat-empty');
    const q = $('#cat-q');
    const params = new URLSearchParams(location.search);
    ['gamme', 'secteur', 'matiere'].forEach(k => { const v = params.get(k); if (v) $$(`input[name="${k}"][value="${v}"]`, cat).forEach(i => { i.checked = true; }); });
    const apply = () => {
      const sel = k => $$(`input[name="${k}"]:checked`, cat).map(i => i.value);
      const g = sel('gamme'), s = sel('secteur'), m = sel('matiere'), n = norm(q.value).trim();
      let shown = 0;
      cards.forEach(c => {
        const has = (k, vals) => !vals.length || vals.some(v => (c.dataset[k] || '').split(' ').includes(v));
        const ok = has('gamme', g) && has('secteur', s) && has('matiere', m) && (!n || norm(c.textContent + ' ' + (c.dataset.k || '')).includes(n));
        c.hidden = !ok; if (ok) shown++;
      });
      count.textContent = `${shown} produit${shown > 1 ? 's' : ''} sur ${cards.length}`;
      empty.hidden = shown > 0;
    };
    $$('input', cat).forEach(i => i.addEventListener(i.type === 'search' ? 'input' : 'change', apply));
    $('#cat-reset')?.addEventListener('click', () => { $$('input[type="checkbox"]', cat).forEach(i => { i.checked = false; }); q.value = ''; apply(); q.focus(); });
    $$('.view-switch button', cat).forEach(b => b.addEventListener('click', () => {
      $$('.view-switch button', cat).forEach(x => x.setAttribute('aria-pressed', String(x === b)));
      grid.classList.toggle('pgrid--list', b.dataset.view === 'list');
    }));
    apply();
  }

  /* ---------- Actualités : filtre par catégorie ---------- */
  const nf = $('.nfilter');
  if (nf) {
    const cards = $$('.ncards .ncard');
    $$('button', nf).forEach(b => b.addEventListener('click', () => {
      $$('button', nf).forEach(x => x.setAttribute('aria-pressed', String(x === b)));
      cards.forEach(c => { c.hidden = b.dataset.cat !== 'all' && c.dataset.cat !== b.dataset.cat; });
      $('#news-count').textContent = `${cards.filter(c => !c.hidden).length} article(s)`;
    }));
  }

  /* ---------- Validation commune ---------- */
  const msgFor = f => {
    const v = f.validity;
    if (v.valid) return '';
    if (v.valueMissing) return f.dataset.missing || 'Ce champ est obligatoire.';
    if (v.typeMismatch) return 'Saisissez une adresse email valide, par exemple nom@entreprise.com.';
    return f.validationMessage;
  };
  const check = f => {
    const m = msgFor(f), el = document.getElementById(`${f.id}-err`);
    if (el) el.textContent = m;
    f.setAttribute('aria-invalid', m ? 'true' : 'false');
    return m;
  };
  const checkAll = scope => {
    const bad = $$('[required]', scope).filter(f => check(f));
    // Groupes de boutons radio requis
    $$('[data-required-group]', scope).forEach(g => {
      const ok = $$('input', g).some(i => i.checked), el = document.getElementById(`${g.id}-err`);
      if (el) el.textContent = ok ? '' : g.dataset.missing;
      if (!ok) bad.push($('input', g));
    });
    if (bad.length) bad[0].focus();
    return !bad.length;
  };

  /* ---------- Devis par étapes (cahier des charges §2.3-1) ---------- */
  const qf = $('#quote-form');
  if (qf) {
    const steps = $$('.step', qf), marks = $$('.steps li');
    let cur = 0;
    const params = new URLSearchParams(location.search);
    const pre = params.get('gamme'); if (pre) { const r = $(`input[name="gamme"][value="${pre}"]`, qf); if (r) r.checked = true; }
    const prod = params.get('produit'); if (prod && qf.elements.produit) qf.elements.produit.value = prod;
    const show = i => {
      steps.forEach((s, k) => { s.hidden = k !== i; });
      marks.forEach((m, k) => { m.classList.toggle('is-done', k < i); k === i ? m.setAttribute('aria-current', 'step') : m.removeAttribute('aria-current'); });
      cur = i;
      const h = $('h3', steps[i]); h.setAttribute('tabindex', '-1'); h.focus({ preventScroll: true });
      const top = qf.getBoundingClientRect().top + scrollY - 140; if (scrollY > top) scrollTo({ top, behavior: reduce ? 'auto' : 'smooth' });
      if (i === steps.length - 1) recap();
    };
    const recap = () => {
      {
        const v = n => { const el = qf.elements[n]; if (!el) return '—'; if (el.tagName === 'SELECT') return el.value ? el.selectedOptions[0].textContent.trim() : '—'; if (el instanceof RadioNodeList) return ($$(`input[name="${n}"]:checked`, qf)[0]?.parentElement.textContent || '—').trim(); return el.value.trim() || '—'; };
        $('#recap').innerHTML = '';
        [['Gamme', v('gamme')], ['Produit', v('produit')], ['Quantité', [v('quantite'), v('unite')].join(' ')], ['Délai', v('delai')], ['Société', v('societe')], ['Contact', `${v('nom')} · ${v('email')}`]].forEach(([k, val]) => {
          const dt = document.createElement('dt'), dd = document.createElement('dd'); dt.textContent = k; dd.textContent = val; $('#recap').append(dt, dd);
        });
      }
    };
    qf.addEventListener('input', () => { if (cur === steps.length - 1) recap(); });
    qf.addEventListener('change', () => { if (cur === steps.length - 1) recap(); });
    $$('[data-next-step]', qf).forEach(b => b.addEventListener('click', () => { if (checkAll(steps[cur])) show(cur + 1); }));
    $$('[data-prev-step]', qf).forEach(b => b.addEventListener('click', () => show(cur - 1)));
    $$('[required]', qf).forEach(f => f.addEventListener('blur', () => { if (f.value || f.getAttribute('aria-invalid') === 'true') check(f); }));
    const files = qf.elements.fichiers, info = $('#fichiers-info');
    files?.addEventListener('change', () => { const l = [...files.files]; info.textContent = l.length ? `${l.length} fichier(s) : ${l.map(f => f.name).join(', ')}` : ''; });
    qf.addEventListener('submit', e => {
      e.preventDefault();
      if (!checkAll(qf)) return;
      const done = $('#quote-done');
      $('[data-company]', done).textContent = qf.elements.societe.value.trim();
      $('[data-email]', done).textContent = qf.elements.email.value.trim();
      qf.hidden = true; $('.steps').hidden = true; done.hidden = false; done.focus();
    });
  }

  /* ---------- Formulaires simples (contact, candidature) ---------- */
  $$('form[data-simple]').forEach(f => {
    $$('[required]', f).forEach(x => x.addEventListener('blur', () => { if (x.value || x.getAttribute('aria-invalid') === 'true') check(x); }));
    f.addEventListener('submit', e => {
      e.preventDefault();
      if (!checkAll(f)) return;
      const ok = document.getElementById(f.dataset.simple); f.hidden = true; ok.hidden = false; ok.focus();
    });
  });

  /* ---------- Onglets contact / devis ---------- */
  $$('[data-tabs2]').forEach(root => {
    const tabs = $$('[role="tab"]', root);
    const sel = (t, focus) => {
      tabs.forEach(x => { const on = x === t; x.setAttribute('aria-selected', on); x.tabIndex = on ? 0 : -1; document.getElementById(x.getAttribute('aria-controls')).hidden = !on; });
      if (focus) t.focus();
      history.replaceState(null, '', '#' + t.getAttribute('aria-controls'));
    };
    tabs.forEach((t, i) => {
      t.addEventListener('click', () => sel(t));
      t.addEventListener('keydown', e => { if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { e.preventDefault(); sel(tabs[(i + (e.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length], true); } });
    });
    const fromHash = tabs.find(t => '#' + t.getAttribute('aria-controls') === location.hash);
    if (fromHash || location.search.includes('gamme=') || location.search.includes('produit=')) sel(fromHash || tabs.find(t => t.getAttribute('aria-controls') === 'devis'));
  });

  /* ---------- Carte : chargée seulement à la demande (pas de service tiers avant clic) ---------- */
  $$('[data-map]').forEach(m => {
    $('button', m)?.addEventListener('click', () => {
      const f = document.createElement('iframe');
      f.src = m.dataset.map; f.title = 'Carte : site Multiprint à Bekoko, Douala'; f.loading = 'lazy'; f.referrerPolicy = 'no-referrer-when-downgrade';
      m.replaceChildren(f);
    });
  });

  /* ---------- Newsletter (maquette : pas d'envoi) ---------- */
  $$('[data-newsletter]').forEach(f => f.addEventListener('submit', e => {
    e.preventDefault();
    const i = $('input[type="email"]', f), msg = $('.nl-msg', f.closest('.newsletter'));
    if (!i.value || !i.validity.valid) { msg.textContent = 'Saisissez une adresse email valide.'; i.focus(); return; }
    msg.textContent = `Merci. Un email de confirmation sera envoyé à ${i.value} (double opt-in).`; f.reset();
  }));
})();

/* Compositions photo : apparition en rideau, défilement à photo fixe, galerie de portraits */
(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Rideau : l'image se dévoile quand elle entre dans l'écran (une seule fois)
  const reveals = document.querySelectorAll('.img-reveal');
  if (reveals.length && 'IntersectionObserver' in window && !reduce) {
    const io = new IntersectionObserver(entries => entries.forEach(en => {
      if (en.isIntersecting) { en.target.classList.add('is-shown'); io.unobserve(en.target); }
    }), { threshold: .2, rootMargin: '0px 0px -8% 0px' });
    reveals.forEach(el => io.observe(el));
  } else reveals.forEach(el => el.classList.add('is-shown'));

  // Défilement à photo fixe : l'étape au centre de l'écran choisit la photo affichée
  document.querySelectorAll('[data-scrolly]').forEach(root => {
    const steps = [...root.querySelectorAll('.scrolly__step')];
    const figs = [...root.querySelectorAll('.scrolly__media figure')];
    const count = root.querySelector('.scrolly__count');
    const set = i => {
      steps.forEach((s, k) => s.classList.toggle('is-active', k === i));
      figs.forEach((f, k) => f.classList.toggle('is-active', k === i));
      if (count) count.textContent = `${i + 1} / ${steps.length}`;
    };
    set(0);
    if (!('IntersectionObserver' in window)) return;
    const io = new IntersectionObserver(entries => entries.forEach(en => {
      if (en.isIntersecting) set(steps.indexOf(en.target));
    }), { rootMargin: '-45% 0px -45% 0px' });
    steps.forEach(s => io.observe(s));
  });

  // Galerie de portraits : boutons précédent / suivant (alternative au glissement, WCAG 2.5.7)
  document.querySelectorAll('[data-film]').forEach(root => {
    const track = root.querySelector('.film__track');
    const prev = root.querySelector('[data-film-prev]'), next = root.querySelector('[data-film-next]');
    const step = () => (track.querySelector('li')?.getBoundingClientRect().width || 300) + 16;
    const update = () => {
      prev.disabled = track.scrollLeft <= 2;
      next.disabled = track.scrollLeft + track.clientWidth >= track.scrollWidth - 2;
    };
    prev.addEventListener('click', () => track.scrollBy({ left: -step() * 2 }));
    next.addEventListener('click', () => track.scrollBy({ left: step() * 2 }));
    track.addEventListener('scroll', update, { passive: true });
    addEventListener('resize', update);
    update();
  });
})();

/* Parcours : suivi des produits dans la barre de gamme, barre d'action mobile */
(() => {
  // Barre produits : le produit lu est marqué, et sa pastille reste visible dans la barre
  document.querySelectorAll('[data-spy]').forEach(nav => {
    const links = [...nav.querySelectorAll('a[href^="#"]')];
    const list = nav.querySelector('ul');
    const targets = links.map(a => document.getElementById(a.getAttribute('href').slice(1))).filter(Boolean);
    if (!targets.length || !('IntersectionObserver' in window)) return;
    const mark = id => links.forEach(a => {
      const on = a.getAttribute('href') === '#' + id;
      on ? a.setAttribute('aria-current', 'true') : a.removeAttribute('aria-current');
      if (on && list.scrollWidth > list.clientWidth) {
        const l = list.getBoundingClientRect(), r = a.getBoundingClientRect();
        if (r.left < l.left || r.right > l.right) list.scrollBy({ left: r.left - l.left - 16, behavior: 'smooth' });
      }
    });
    const io = new IntersectionObserver(entries => entries.forEach(en => { if (en.isIntersecting) mark(en.target.id); }),
      { rootMargin: '-35% 0px -60% 0px' });
    targets.forEach(t => io.observe(t));
  });

  // Barre d'action mobile : apparaît après le premier écran, s'efface quand le bloc contact ou le pied de page est visible
  const bar = document.querySelector('[data-mbar]');
  if (bar) {
    const html = document.documentElement;
    let past = false, footerSeen = false;
    const apply = () => { const on = past && !footerSeen; bar.classList.toggle('is-on', on); html.classList.toggle('mbar-on', on); };
    addEventListener('scroll', () => { const p = scrollY > innerHeight * .6; if (p !== past) { past = p; apply(); } }, { passive: true });
    const ends = document.querySelectorAll('.cta, .footer');
    if ('IntersectionObserver' in window && ends.length) {
      const seen = new Set();
      const io = new IntersectionObserver(entries => {
        entries.forEach(en => en.isIntersecting ? seen.add(en.target) : seen.delete(en.target));
        footerSeen = seen.size > 0; apply();
      });
      ends.forEach(el => io.observe(el));
    }
  }
})();
