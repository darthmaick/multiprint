/* Multiprint — pilotage de l'intro : sortie vers le logo du header, Échap ou clic pour la fermer, une fois par visite. */
(() => {
  const html = document.documentElement;
  const intro = document.getElementById('intro');
  if (!intro || !html.classList.contains('intro-on')) { intro?.remove(); return; }

  const logo = intro.querySelector('.intro__logo');
  const target = document.querySelector('.header__logo img');
  let done = false;
  const css = getComputedStyle(intro);
  const pace = parseFloat(css.getPropertyValue('--intro-pace')) || 1;
  const flight = parseFloat(css.getPropertyValue('--intro-leave')) || 1100;
  // Pendant l'intro, la page derrière est inerte (Tab ne s'y égare pas)
  const behind = [...document.body.children].filter(el => el !== intro && el.tagName !== 'SCRIPT');
  behind.forEach(el => { el.inert = true; });

  const remember = () => { try { sessionStorage.setItem('mp-intro', 'seen'); } catch { /* stockage indisponible */ } };
  const finish = () => {
    if (done) return;
    done = true;
    remember();
    html.classList.remove('intro-on');
    behind.forEach(el => { el.inert = false; });
    intro.remove();
    document.removeEventListener('keydown', onKey);
  };

  const leave = () => {
    if (done || intro.classList.contains('is-leaving')) return;
    if (!target) { skip(); return; }
    const from = logo.getBoundingClientRect();
    const to = target.getBoundingClientRect();
    // Fige l'état de fin de l'entrée, puis vole jusqu'au logo du header
    logo.style.animation = 'none';
    logo.style.translate = '0 0';
    logo.getBoundingClientRect(); // force l'état de départ avant la transition
    const s = to.width / from.width;
    intro.classList.add('is-leaving');
    requestAnimationFrame(() => {
      logo.style.transform = `translate(${to.left - from.left}px, ${to.top - from.top}px) scale(${s})`;
    });
    logo.addEventListener('transitionend', finish, { once: true });
    setTimeout(finish, flight + 300); // filet si transitionend ne vient pas
  };

  const skip = () => {
    if (done) return;
    intro.classList.add('is-skipped');
    setTimeout(finish, 170); // --duration-quick + marge
  };

  const onKey = e => { if (e.key === 'Escape') skip(); };
  intro.addEventListener('click', skip);
  document.addEventListener('keydown', onKey);

  // Feu vert : on attend que la page soit chargée (au plus 400 ms) puis deux images, pour que les
  // premières images de l'intro ne soient pas ralenties par le chargement des polices et des images.
  const play = () => {
    if (intro.classList.contains('is-playing')) return;
    requestAnimationFrame(() => requestAnimationFrame(() => {
      intro.classList.add('is-playing');
      if (/[?&]intro=hold/.test(location.search)) return; // revue image par image
      // Le vol part pendant la traîne de la révélation du slogan (déjà à 99 %) : pas de temps mort
      setTimeout(leave, 2850 * pace);
    }));
  };
  if (document.readyState === 'complete') play();
  else { addEventListener('load', play, { once: true }); setTimeout(play, 400); }
})();
