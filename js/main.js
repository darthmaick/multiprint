/* Multiprint — maquette : menu mobile, notes de maquette, apparitions, formulaire de devis. */
(() => {
  const html = document.documentElement;
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch { /* stockage indisponible */ } },
  };

  // Menu mobile : <dialog> natif (Échap, focus et retour de focus gérés par le navigateur)
  const menu = document.getElementById('menu');
  const opener = document.querySelector('[data-menu-open]');
  if (menu && opener) {
    opener.addEventListener('click', () => { menu.showModal(); opener.setAttribute('aria-expanded', 'true'); });
    menu.querySelector('[data-menu-close]').addEventListener('click', () => menu.close());
    menu.addEventListener('close', () => { opener.setAttribute('aria-expanded', 'false'); opener.focus(); });
    menu.querySelectorAll('nav a').forEach(a => a.addEventListener('click', () => menu.close()));
    matchMedia('(min-width: 1081px)').addEventListener('change', e => { if (e.matches && menu.open) menu.close(); });
  }

  // Notes de maquette (affichées par défaut, choix mémorisé)
  const toggle = document.querySelector('[data-notes-toggle]');
  const applyNotes = on => {
    html.classList.toggle('show-notes', on);
    if (toggle) {
      toggle.setAttribute('aria-pressed', String(on));
      toggle.textContent = on ? 'Notes maquette : affichées' : 'Notes maquette : masquées';
    }
  };
  applyNotes(store.get('mp-notes') !== 'off');
  toggle?.addEventListener('click', () => {
    const on = !html.classList.contains('show-notes');
    applyNotes(on);
    store.set('mp-notes', on ? 'on' : 'off');
  });

  // Apparitions au scroll (CSS les ignore si « réduire les animations » est actif)
  const reveals = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && matchMedia('(prefers-reduced-motion: no-preference)').matches) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    // Décalage --duration-stagger (40 ms), 4 éléments max : 120 ms au total
    reveals.forEach((el, i) => { el.style.transitionDelay = `${(i % 4) * 40}ms`; io.observe(el); });
  } else {
    reveals.forEach(el => el.classList.add('is-in'));
  }

  // Chiffres clés : défilement jusqu'à la valeur à l'apparition (ease smooth-out, 1 s), rien sous « réduire les animations »
  const counters = document.querySelectorAll('[data-count]');
  if (counters.length && 'IntersectionObserver' in window && matchMedia('(prefers-reduced-motion: no-preference)').matches) {
    const out = t => 1 - Math.pow(1 - t, 4);
    const run = el => {
      const to = +el.dataset.count, t0 = performance.now(), dur = 1000;
      const step = now => { const k = Math.min(1, (now - t0) / dur); el.textContent = Math.round(to * out(k)); if (k < 1) requestAnimationFrame(step); };
      el.textContent = '0'; requestAnimationFrame(step);
    };
    const cio = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { cio.unobserve(e.target); run(e.target); } }), { rootMargin: '0px 0px -10% 0px' });
    counters.forEach(el => cio.observe(el));
  }

  // Info-bulles des repères du hero : survol et focus, Échap pour fermer (WCAG 1.4.13)
  document.querySelectorAll('.fact').forEach(fact => {
    const btn = fact.querySelector('.fact__btn');
    const open = () => {
      document.querySelectorAll('.fact.is-open').forEach(f => f !== fact && f.classList.remove('is-open'));
      fact.classList.add('is-open');
      const tip = fact.querySelector('.fact__tip');
      tip.style.setProperty('--shift', '0px');
      const over = tip.getBoundingClientRect().right - (document.documentElement.clientWidth - 16);
      if (over > 0) tip.style.setProperty('--shift', `${-over}px`);
    };
    const close = () => fact.classList.remove('is-open');
    fact.addEventListener('mouseenter', open);
    fact.addEventListener('mouseleave', () => { if (document.activeElement !== btn) close(); });
    btn.addEventListener('focus', open);
    btn.addEventListener('blur', close);
    btn.addEventListener('click', () => (fact.classList.contains('is-open') ? close() : open()));
  });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') document.querySelectorAll('.fact.is-open').forEach(f => f.classList.remove('is-open'));
  });

  // Onglets des procédés (motif ARIA « tabs », activation automatique)
  document.querySelectorAll('[data-tabs]').forEach(root => {
    const tabs = [...root.querySelectorAll('[role="tab"]')];
    // Images des panneaux décodées à l'avance : l'échange ne montre jamais une image en cours de chargement
    const panelOf = t => document.getElementById(t.getAttribute('aria-controls'));
    const ready = t => {
      const img = panelOf(t).querySelector('img');
      if (!img || (img.complete && img.naturalWidth)) return Promise.resolve();
      return Promise.race([img.decode().catch(() => {}), new Promise(r => setTimeout(r, 300))]);
    };
    if ('IntersectionObserver' in window) {
      const io = new IntersectionObserver(es => { if (es.some(e => e.isIntersecting)) { io.disconnect(); tabs.forEach(t => ready(t)); } }, { rootMargin: '600px 0px' });
      io.observe(root);
    }
    let pending = 0;
    const select = (tab, focus) => {
      tabs.forEach(t => {
        const on = t === tab;
        t.setAttribute('aria-selected', String(on));
        t.tabIndex = on ? 0 : -1;
      });
      const ticket = ++pending;
      ready(tab).then(() => {
        if (ticket !== pending) return; // un autre onglet a été choisi entre-temps
        tabs.forEach(t => { panelOf(t).hidden = t !== tab; });
      });
      if (focus) tab.focus();
      root.dispatchEvent(new CustomEvent('tabchange', { detail: { index: tabs.indexOf(tab) } }));
    };
    tabs.forEach((tab, i) => {
      tab.addEventListener('click', () => select(tab));
      tab.addEventListener('keydown', e => {
        const keys = { ArrowDown: 1, ArrowRight: 1, ArrowUp: -1, ArrowLeft: -1 };
        if (e.key in keys) { e.preventDefault(); select(tabs[(i + keys[e.key] + tabs.length) % tabs.length], true); }
        if (e.key === 'Home') { e.preventDefault(); select(tabs[0], true); }
        if (e.key === 'End') { e.preventDefault(); select(tabs[tabs.length - 1], true); }
      });
    });
  });

  // Version B : ligne de production. La bande avance, les rouleaux tournent,
  // l'impression se révèle jusqu'au procédé choisi.
  document.querySelectorAll('[data-machine]').forEach(machine => {
    const root = machine.closest('[data-tabs]');
    const film = machine.querySelector('.m-film');
    const reveal = machine.querySelector('.m-reveal');
    const prints = [...machine.querySelectorAll('.m-print')];
    const rolls = [...machine.querySelectorAll('.m-roll')];
    const tabs = [...machine.querySelectorAll('[role="tab"]')];
    const nameEl = machine.querySelector('[data-readout-name]');
    if (!film || !root) return;
    const total = film.getTotalLength();
    const stops = machine.dataset.stops.split(',').map(Number);
    const baseOffsets = prints.map(p => parseFloat(getComputedStyle(p).strokeDashoffset) || 0);
    const R = 26;
    const reduce = matchMedia('(prefers-reduced-motion: reduce)');
    let pos = 0, travel = 0, raf = 0, current = Math.max(0, tabs.findIndex(t => t.getAttribute('aria-selected') === 'true'));

    reveal.style.strokeDasharray = `${total} ${total}`;
    const render = () => {
      reveal.style.strokeDashoffset = `${total - pos}`;
      prints.forEach((p, k) => { p.style.strokeDashoffset = `${baseOffsets[k] - travel}`; });
      rolls.forEach(g => {
        const rot = g.querySelector('.m-rot');
        const deg = (travel / R) * (180 / Math.PI) * Number(g.dataset.dir);
        rot.setAttribute('transform', `rotate(${deg.toFixed(2)} ${rot.dataset.cx} ${rot.dataset.cy})`);
      });
    };
    const mark = i => {
      rolls.forEach((g, k) => g.classList.toggle('is-on', k === i));
      if (nameEl) nameEl.textContent = tabs[i].textContent.trim();
    };
    // --ease-smooth-out : cubic-bezier(0.22, 1, 0.36, 1), résolu numériquement (même courbe que le CSS)
    const bez = (x1, y1, x2, y2) => {
      const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx;
      const cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
      const X = t => ((ax * t + bx) * t + cx) * t, Y = t => ((ay * t + by) * t + cy) * t;
      const dX = t => (3 * ax * t + 2 * bx) * t + cx;
      return x => { let t = x; for (let n = 0; n < 6; n++) { const d = dX(t); if (Math.abs(d) < 1e-6) break; t -= (X(t) - x) / d; } return Y(Math.min(1, Math.max(0, t))); };
    };
    const ease = bez(.22, 1, .36, 1);
    const goTo = i => {
      cancelAnimationFrame(raf);
      mark(i);
      const target = stops[i];
      if (reduce.matches) { pos = target; render(); return; }
      const from = pos, run = Math.abs(target - from) + 220, t0 = performance.now(), start = travel;
      const dur = 500; // --duration-very-slow : moment d'emphase
      const step = now => {
        const k = Math.min(1, (now - t0) / dur), e = ease(k);
        pos = from + (target - from) * e;
        travel = start + run * e;
        render();
        if (k < 1) raf = requestAnimationFrame(step);
      };
      raf = requestAnimationFrame(step);
    };

    render(); mark(current);
    root.addEventListener('tabchange', e => { current = e.detail.index; goTo(current); });
    rolls.forEach((g, k) => {
      g.addEventListener('click', () => tabs[k].click());
      g.addEventListener('mouseenter', () => g.classList.add('is-hover'));
      g.addEventListener('mouseleave', () => g.classList.remove('is-hover'));
    });
    tabs.forEach((t, k) => {
      t.addEventListener('mouseenter', () => rolls[k].classList.add('is-hover'));
      t.addEventListener('mouseleave', () => rolls[k].classList.remove('is-hover'));
    });
    // Mise en route à la première apparition (une seule fois, moins de 2 s)
    if ('IntersectionObserver' in window) {
      const io = new IntersectionObserver(entries => {
        if (entries.some(en => en.isIntersecting)) { io.disconnect(); goTo(current); }
      }, { threshold: .5 });
      io.observe(machine);
    } else { goTo(current); }
  });

  // Changement de procédé : l'onglet actif reste visible dans la ligne qui défile (mobile),
  // et le bloc se recale s'il dépasse de l'écran, pour ne pas avoir à remonter.
  document.querySelectorAll('[data-tabs]').forEach(root => {
    root.addEventListener('tabchange', e => {
      const smooth = matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth';
      const tab = root.querySelectorAll('[role="tab"]')[e.detail.index];
      const list = tab && tab.parentElement;
      if (list && list.scrollWidth > list.clientWidth + 1) {
        const l = list.getBoundingClientRect(), t = tab.getBoundingClientRect();
        list.scrollTo({ left: list.scrollLeft + t.left - l.left - (l.width - t.width) / 2, behavior: smooth });
      }
      const header = document.querySelector('.header');
      const top = header ? header.getBoundingClientRect().bottom : 0;
      const r = root.getBoundingClientRect();
      if (r.top < top || r.bottom > innerHeight) {
        root.scrollIntoView({ block: r.height <= innerHeight - top ? 'nearest' : 'start', behavior: smooth });
      }
    });
  });

  // Frise horizontale : boutons précédent / suivant (alternative au glissement, WCAG 2.5.7)
  document.querySelectorAll('[data-track]').forEach(root => {
    const track = root.querySelector('.track');
    const prev = root.querySelector('[data-prev]');
    const next = root.querySelector('[data-next]');
    const step = () => track.querySelector('li').getBoundingClientRect().width + 24;
    const update = () => {
      prev.disabled = track.scrollLeft <= 2;
      next.disabled = track.scrollLeft + track.clientWidth >= track.scrollWidth - 2;
    };
    prev.addEventListener('click', () => track.scrollBy({ left: -step() }));
    next.addEventListener('click', () => track.scrollBy({ left: step() }));
    track.addEventListener('scroll', update, { passive: true });
    addEventListener('resize', update);
    update();
  });

  // Formulaire de devis
  const form = document.getElementById('devis-form');
  if (!form) return;

  const params = new URLSearchParams(location.search);
  const preset = (name, value) => {
    const field = form.elements[name];
    if (field && value && [...field.options].some(o => o.value === value)) field.value = value;
  };
  preset('produit', params.get('produit'));
  preset('application', params.get('application'));

  const summary = document.getElementById('error-summary');
  const summaryList = summary.querySelector('ul');
  const messages = {
    valueMissing: field => field.dataset.missing || 'Ce champ est obligatoire.',
    typeMismatch: () => 'Saisissez une adresse email valide, par exemple nom@entreprise.com.',
  };
  const errorEl = field => document.getElementById(`${field.id}-error`);
  const check = field => {
    const v = field.validity;
    const msg = v.valid ? '' : (v.valueMissing ? messages.valueMissing(field) : v.typeMismatch ? messages.typeMismatch(field) : field.validationMessage);
    const el = errorEl(field);
    if (el) el.textContent = msg;
    field.setAttribute('aria-invalid', msg ? 'true' : 'false');
    return msg;
  };

  form.querySelectorAll('[required]').forEach(field => {
    field.addEventListener('blur', () => { if (field.getAttribute('aria-invalid') === 'true' || field.value) check(field); });
    field.addEventListener('change', () => { if (field.getAttribute('aria-invalid') === 'true') check(field); });
  });

  const files = form.elements.fichiers;
  const filesInfo = document.getElementById('fichiers-info');
  files?.addEventListener('change', () => {
    const list = [...files.files];
    const total = list.reduce((s, f) => s + f.size, 0);
    filesInfo.textContent = list.length
      ? `${list.length} fichier${list.length > 1 ? 's' : ''} sélectionné${list.length > 1 ? 's' : ''} (${(total / 1048576).toFixed(1)} Mo) : ${list.map(f => f.name).join(', ')}`
      : '';
  });

  form.addEventListener('submit', e => {
    e.preventDefault();
    const errors = [];
    form.querySelectorAll('[required]').forEach(field => {
      const msg = check(field);
      if (msg) errors.push({ field, msg });
    });
    summaryList.replaceChildren(...errors.map(({ field, msg }) => {
      const li = document.createElement('li');
      const a = document.createElement('a');
      a.href = `#${field.id}`;
      a.textContent = `${field.dataset.label || document.querySelector(`label[for="${field.id}"]`)?.textContent.replace('*', '').trim()} : ${msg}`;
      a.addEventListener('click', ev => { ev.preventDefault(); field.focus(); });
      li.append(a);
      return li;
    }));
    if (errors.length) {
      summary.hidden = false;
      summary.querySelector('h2').textContent = errors.length > 1 ? `${errors.length} champs sont à corriger` : 'Un champ est à corriger';
      summary.focus();
      return;
    }
    summary.hidden = true;
    const success = document.getElementById('devis-success');
    success.querySelector('[data-company]').textContent = form.elements.societe.value.trim();
    form.hidden = true;
    success.hidden = false;
    success.focus();
    scrollTo({ top: success.getBoundingClientRect().top + scrollY - 120, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
  });
})();
