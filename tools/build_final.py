# -*- coding: utf-8 -*-
"""Site Multiprint (pages à la racine du projet).
Sources : cahier des charges ARMD (avril 2026), catalogue produits Multiprint, brief et script du film
institutionnel, moodboard du shooting, banque d'images du shooting (lots Usine et Collaborateurs),
rapport RSE 2023 et site actuel. Usage : python tools/build_final.py"""
import html, json, pathlib, re
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT
P = ''
FRAG = ROOT / 'tools' / 'fragments'
frag = lambda n: (FRAG / n).read_text(encoding='utf-8')
e = lambda s: html.escape(s, quote=True)

# ---------------------------------------------------------------- images
def dims(path):
    with Image.open(ROOT / path) as im: return im.size

def pic(src, alt='', sizes='100vw', cls='', lazy=True, pos='', prio=False):
    """src : 'slug' (shoot, 3 tailles) ou 'hd:produits/x' (une taille) ou chemin img/..."""
    if src.startswith('hd:'):
        path = f'img/hd/{src[3:]}.webp'; w, h = dims(path); srcset = ''
        main = P + path
    elif src.startswith('img/'):
        path = src; w, h = dims(path); srcset = ''; main = P + path
    else:
        w, h = dims(f'img/shoot/{src}-1200.webp')
        sets = [f'{P}img/shoot/{src}-{x}.webp {x}w' for x in (640, 1200, 2400) if (ROOT / f'img/shoot/{src}-{x}.webp').exists()]
        srcset = f' srcset="{", ".join(sets)}" sizes="{sizes}"'; main = f'{P}img/shoot/{src}-1200.webp'
    a = [f'src="{main}"{srcset}', f'width="{w}" height="{h}"', f'alt="{e(alt)}"']
    if cls: a.insert(0, f'class="{cls}"')
    if prio: a.append('fetchpriority="high"')
    elif lazy: a.append('loading="lazy"')
    a.append('decoding="async"')
    if pos: a.append(f'style="object-position:{pos}"')
    return '<img ' + ' '.join(a) + '>'

note = lambda txt, kind='': f'<span class="note{" note--" + kind if kind else ""}">{e(txt)}</span>'

# ---------------------------------------------------------------- contenus
GAMMES = [
    dict(slug='etiquettes', nom='Étiquettes & manchons', court='Étiquettes', card='controle-etiquettes', hero='planches-etiquettes',
         lead="Étiquettes de colle, étiquettes adhésives, stanioles et sleeves, imprimés en quadrichromie ou en ton direct pour habiller bouteilles, pots et emballages."),
    dict(slug='capsules', nom='Capsules & bouchons', court='Capsules', card='capsules-convoyeur', hero='ligne-capsules',
         lead="Bouchons couronnes imprimés et emboutis sur la première ligne de fabrication du Cameroun et d'Afrique centrale, et bouchons plastiques personnalisés."),
    dict(slug='emballages-souples', nom='Emballages souples', court='Souples', card='bobine-film', hero='ligne-heliogravure',
         lead="Films extrudés sur notre site et imprimés en héliogravure 8 couleurs ou en flexographie : rouleaux, sachets, doypacks, sacs et films rétractables."),
    dict(slug='emballages-rigides', nom='Emballages rigides', court='Rigides', card='feuille-carton', hero='atelier-offset',
         lead="Boîtes et étuis en carton imprimés en offset, découpés à la forme et façonnés, ainsi que des produits jetables pour la restauration."),
]
G = {g['slug']: g for g in GAMMES}
SECTEURS = [('agro', 'Agroalimentaire & boissons'), ('cosmetique', 'Cosmétique'), ('pharma', 'Pharmaceutique')]
MATIERES = [('papier', 'Papier'), ('plastique', 'Film plastique'), ('aluminium', 'Aluminium'), ('metal', 'Métal'), ('carton', 'Carton')]
SL = dict(SECTEURS); ML = dict(MATIERES)

PRODUITS = [
    dict(id='etiquettes-colle', nom='Étiquettes de colle', g='etiquettes', img='hd:produits/industrie', vis='ia',
         imp="Quadrichromie ou ton direct sur papier résistant à l'eau et à l'humidité, blanc ou métallisé.",
         fin="Découpe au massicot et à la lombardi, à la forme de l'étiquette.", liv='En pièces.',
         mat=['papier'], sec=['agro'], usage="Bouteilles de bière, de jus et d'huile."),
    dict(id='etiquettes-adhesives', nom='Étiquettes adhésives', g='etiquettes', img='controle-etiquettes',
         imp='Quadrichromie ou ton direct sur vinyle adhésif, papier adhésif ou BOPP autocollant (blanc, transparent ou pearl).',
         fin="Échenillage, mi-chair à la forme de l'étiquette.", liv='En pièces ou en bobines.',
         mat=['papier', 'plastique'], sec=['agro', 'cosmetique', 'pharma'], usage='Fruits, bidons de lubrifiant, produits de grande consommation.'),
    dict(id='stanioles', nom='Stanioles', g='etiquettes', img='planches-etiquettes', vis='indicatif',
         imp='Quadrichromie ou ton direct sur film aluminium.', fin='Découpe au massicot et à la lombardi.', liv='En pièces.',
         mat=['aluminium'], sec=['agro'], usage='Habillage du col des bouteilles de bière.'),
    dict(id='sleeves', nom='Sleeves (manchons)', g='etiquettes', img='rouleau-imprime', vis='indicatif',
         imp='Quadrichromie ou ton direct sur film PVC.', fin='Découpe à la refendeuse, pose à la sleeveuse.', liv='En bobines.',
         mat=['plastique'], sec=['agro', 'cosmetique'], usage='Pots de pâte à tartiner, boîtes de boisson chocolatée.'),
    dict(id='bouchons-couronnes', nom='Bouchons couronnes', g='capsules', img='capsules-plateau',
         imp='Quadrichromie ou ton direct sur fer-blanc électrolytique (ETP) ou acier sans étain (TFS).',
         fin="Emboutissage, pose du joint d'étanchéité et inspection.", liv='En pièces.',
         mat=['metal'], sec=['agro'], usage='Bières, sodas et jus en bouteille de verre.',
         n=('Terminologie TFS / ETP corrigée par rapport au catalogue, à valider', 'adapte')),
    dict(id='bouchons-plastiques', nom='Bouchons plastiques', g='capsules', img='hd:produits/etiquettes', vis='ia',
         imp='Impression personnalisée en quadrichromie ou en ton direct.', fin='À préciser.', liv='À préciser.',
         mat=['plastique'], sec=['agro'], usage="Bouteilles de boissons gazeuses et d'eau.",
         n=("Spécifications à fournir : le catalogue reprend ici le texte des étiquettes adhésives", 'fournir')),
    dict(id='rouleaux-imprimes', nom='Rouleaux imprimés (film, papier)', g='emballages-souples', img='hd:produits/sachets', vis='ia',
         imp='Quadrichromie ou ton direct sur film PE, BOPP (pearl, transparent, blanc), papier métallisé ou CPP.',
         fin='Découpe à la refendeuse, au massicot et à la lombardi.', liv='En pièces ou en bobines.',
         mat=['plastique', 'papier'], sec=['agro', 'cosmetique'], usage="Fardeaux d'eau, étiquettes enveloppantes, conditionnement automatique."),
    dict(id='sachets', nom='Sachets plastiques', g='emballages-souples', img='bobine-film', vis='indicatif',
         imp='Quadrichromie ou ton direct sur film PE, PET, CPP ou BOPP.',
         fin='Refente, complexage, pose de zip ; soufflet latéral, soudure 3 côtés ou soudure centrale.', liv='En bobines et en pièces.',
         mat=['plastique'], sec=['agro', 'cosmetique', 'pharma'], usage='Pâtes, bouillons, lait en poudre, produits secs.'),
    dict(id='doypacks', nom='Sachets doypack (stand-up)', g='emballages-souples', img='pupitre-heliogravure', vis='indicatif',
         imp='Quadrichromie ou ton direct sur BOPP, PE ou CPP.',
         fin='Refente, complexage, mise en forme sur machine à doypack ; fermeture zip, bouchon ou scellage.', liv='En pièces.',
         mat=['plastique'], sec=['agro', 'cosmetique'], usage='Produits alimentaires, liquides et cosmétiques.'),
    dict(id='sacs', nom='Sacs plastiques', g='emballages-souples', img='sacs-imprimes',
         imp='Quadrichromie ou ton direct sur film PE.', fin='Refente, façonnage en sachet.', liv='En pièces.',
         mat=['plastique'], sec=['agro', 'pharma'], usage='Boulangeries, pharmacies, épiceries, sacs génériques.'),
    dict(id='films-retractables', nom='Films rétractables', g='emballages-souples', img='stock-films',
         imp='Film extrudé multicouche, de 40 µm à plus de 95 µm selon vos spécifications techniques.',
         fin='Refente à la laize.', liv='En bobines, au kilogramme souhaité.',
         mat=['plastique'], sec=['agro'], usage='Fardelage et protection des produits palettisés.', n=('Usage adapté', 'adapte')),
    dict(id='boites', nom='Boîtes et étuis imprimés', g='emballages-rigides', img='hd:produits/alimentaire', vis='ia',
         imp='Quadrichromie ou ton direct en offset sur carton dos gris, dos bois ou dos blanc, de 250 à 350 g.',
         fin='Massicot, plieuse-colleuse, découpe à la forme.', liv='En pièces.',
         mat=['carton'], sec=['agro', 'cosmetique', 'pharma'], usage='Boîtes de sucre et de café, barquettes, coiffes, étuis.'),
    dict(id='jetables', nom='Produits jetables', g='emballages-rigides', img='cartons-imprimes', vis='indicatif',
         imp='Quadrichromie ou ton direct sur carton alimentaire et polypropylène.',
         fin='Massicot, machine à plats, machine à gobelets.', liv='En pièces.',
         mat=['carton', 'plastique'], sec=['agro'], usage='Plats, barquettes, gobelets, couverts et nappes.',
         n=('Gamme du catalogue 2016 : à confirmer', 'fournir')),
]

NEWS = [
    dict(id='iso-45001', date='21 août 2025', iso='2025-08-21', cat='certification', catl='Certification', img='img/photos/certification-iso-1200.webp',
         t='Certification ISO 45001:2018', d="Bureau Veritas a certifié notre système de management de la santé et de la sécurité au travail, pour l'ensemble de la fabrication des emballages.",
         link=('https://www.multiprint.cm/assets/docs/certificat_iso45001.pdf', 'Voir le certificat')),
    dict(id='rse-2023', date='Exercice 2023', iso='2024', cat='entreprise', catl='RSE', img='img/docs/rapport_rse.webp',
         t='Rapport RSE 2023', d="Chiffre d'affaires en hausse de 8 %, satisfaction client en hausse de 6 % et contribution aux Objectifs de Développement Durable des Nations unies.",
         link=('https://www.multiprint.cm/assets/docs/rapport_rse_mtp.pdf', 'Lire le rapport')),
    dict(id='40-ans', date='2023', iso='2023', cat='entreprise', catl='Événement', img='anniversaire-40-ans',
         t='Multiprint fête ses 40 ans', d='De Graphis Industrie en 1983 aux emballages industriels d\'aujourd\'hui : quarante ans célébrés avec nos équipes et nos partenaires.',
         n=('Date et texte à confirmer', 'provisoire')),
    dict(id='presse-offset', date='2022', iso='2022', cat='investissement', catl='Investissement', img='atelier-offset',
         t="Une nouvelle presse offset à l'atelier", d="Mise en service d'une nouvelle machine d'impression offset pour les étuis et les boîtes en carton.",
         n=('D\'après le dossier « Nouvelle machine offset 2022 » : à confirmer', 'provisoire')),
    dict(id='minmidt', date='25 juin 2021', iso='2021-06-25', cat='institutionnel', catl='Institutionnel', img='img/photos/visite-ministere-1200.webp',
         t="Visite du Ministère de l'Industrie", d="Une équipe du MINMIDT a visité nos installations pour évaluer notre capacité à répondre au besoin croissant d'emballage au Cameroun et dans la sous-région."),
]

PAGES_NAV = [('solutions.html', 'Nos solutions'), ('a-propos.html', 'À propos'), ('rse.html', 'RSE & Impact'),
             ('actualites.html', 'Actualités'), ('carrieres.html', 'Carrières'), ('contact.html', 'Contact')]

# ---------------------------------------------------------------- squelette commun
ICON = {
    'search': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
    'menu': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M3 7h18M3 12h18M3 17h18"/></svg>',
}
TOPBAR = frag('topbar.html')
INTRO = frag('intro.html').replace('src="img/', f'src="{P}img/')
LEGEND = frag('legende-notes.html')
SOCIAL = frag('reseaux-sociaux.html')


def search_index():
    idx = [dict(t=l, d='Page', c='Page', u=h) for h, l in [('index.html', 'Accueil')] + PAGES_NAV]
    idx += [dict(t=g['nom'], d=g['lead'][:90] + '…', c='Gamme', u=f'{g["slug"]}.html') for g in GAMMES]
    idx += [dict(t=p['nom'], d=p['usage'], c=G[p['g']]['court'], u=f'{p["g"]}.html#{p["id"]}', k=p['imp'] + ' ' + p['fin']) for p in PRODUITS]
    idx += [dict(t=n['t'], d=n['date'], c='Actualité', u=f'actualites.html#{n["id"]}') for n in NEWS]
    idx += [dict(t='Demander un devis', d='Formulaire en 3 étapes', c='Contact', u='contact.html#devis', k='prix tarif commande'),
            dict(t='Nos certifications', d='ISO 9001, ISO 45001, Nestlé, HACCP', c='À propos', u='a-propos.html#certifications', k='qualité norme'),
            dict(t='Candidature spontanée', d='Envoyer votre CV', c='Carrières', u='carrieres.html#candidature', k='emploi recrutement job'),
            dict(t='Rapport RSE 2023', d='Engagements et chiffres', c='RSE', u='rse.html', k='environnement recyclage')]
    return json.dumps(idx, ensure_ascii=False)


def header(cur):
    nav = ''.join(f'<li><a href="{h}"{" aria-current=" + chr(34) + "page" + chr(34) if h == cur else ""}>{l}</a></li>' for h, l in PAGES_NAV)
    mnav = ''.join(f'<a href="{h}"{" aria-current=" + chr(34) + "page" + chr(34) if h == cur else ""}>{l}</a>' for h, l in PAGES_NAV)
    return f'''{TOPBAR.replace('src="img/', f'src="{P}img/')}
<header class="header">
  <div class="wrap">
    <a class="header__logo" href="index.html" aria-label="Multiprint Labels &amp; Packaging, accueil"><img src="{P}img/logos/logo-black.png" width="800" height="408" alt=""></a>
    <nav class="nav" aria-label="Navigation principale"><ul>{nav}</ul></nav>
    <div class="hdr-tools">
      <button class="icon-btn" type="button" data-search-open aria-label="Rechercher sur le site (raccourci : /)" aria-haspopup="dialog" aria-controls="search">{ICON['search']}</button>
      <div class="lang" role="group" aria-label="Langue du site"><span aria-current="true">FR</span><span class="lang__off" title="Version anglaise en cours de traduction">EN<span class="visually-hidden"> (bientôt disponible)</span></span></div>
      <a class="btn header__cta" href="contact.html#devis">Demander un devis</a>
      <button class="menu-btn" type="button" aria-haspopup="dialog" aria-controls="menu" data-menu-open>{ICON['menu']}Menu</button>
    </div>
  </div>
</header>

<dialog class="menu on-dark" id="menu" aria-label="Menu">
  <div class="menu__inner">
    <div class="menu__head">
      <img src="{P}img/logos/logo-white.png" width="800" height="408" alt="Multiprint Labels &amp; Packaging">
      <button class="menu__close" type="button" data-menu-close>Fermer</button>
    </div>
    <nav aria-label="Navigation principale (mobile)"><a href="index.html">Accueil</a>{mnav}</nav>
    <a class="btn" href="contact.html#devis">Demander un devis</a>
    <p class="menu__contact">Route Nationale N°3, avant l'échangeur de Bekoko, Douala<br>
      <a href="tel:+237677550447">(+237) 677 55 04 47</a> · <a href="tel:+237691100459">691 10 04 59</a><br>
      <a href="mailto:commerciaux@multiprint.cm">commerciaux@multiprint.cm</a></p>
  </div>
</dialog>

<dialog class="search" id="search" aria-label="Rechercher sur le site">
  <div class="search__bar">{ICON['search']}<label class="visually-hidden" for="search-q">Rechercher un produit ou une page</label>
    <input id="search-q" type="search" placeholder="Rechercher un produit, une page…" autocomplete="off" aria-describedby="search-count">
    <button class="search__close" type="button" data-search-close>Fermer</button></div>
  <p class="visually-hidden" id="search-count" aria-live="polite"></p>
  <div class="search__list" id="search-list"></div>
</dialog>'''


def footer():
    sols = ''.join(f'<li><a href="{g["slug"]}.html">{g["nom"]}</a></li>' for g in GAMMES)
    return f'''<footer class="footer on-dark">
  <div class="wrap">
    <div class="newsletter">
      <div><h2>Restez informé</h2><p>Nouveautés produits, certifications et actualités de Multiprint, une fois par trimestre. {note("Mailchimp ou équivalent, double opt-in", "provisoire")}</p></div>
      <form data-newsletter novalidate><label class="visually-hidden" for="nl-email">Votre adresse email</label>
        <input id="nl-email" type="email" placeholder="Votre adresse email" autocomplete="email"><button class="btn btn--white" type="submit">S'inscrire</button></form>
      <p class="nl-msg" role="status"></p>
    </div>
    <div class="footer__grid">
      <div class="footer__brand">
        <img src="{P}img/logos/logo-white.png" width="800" height="408" alt="Multiprint Labels &amp; Packaging" loading="lazy">
        <p>Étiquettes, capsules, emballages souples et rigides pour l'industrie agroalimentaire, cosmétique et pharmaceutique, depuis Douala.</p>
        {SOCIAL}
      </div>
      <nav aria-label="Nos solutions"><h2>Nos solutions</h2><ul>{sols}<li><a href="solutions.html">Tout le catalogue</a></li></ul></nav>
      <nav aria-label="Multiprint"><h2>Multiprint</h2><ul><li><a href="a-propos.html">À propos</a></li><li><a href="rse.html">RSE &amp; Impact</a></li><li><a href="actualites.html">Actualités</a></li><li><a href="carrieres.html">Carrières</a></li></ul></nav>
      <div><h2>Contact</h2>
        <address>Route Nationale N°3, avant l'échangeur de Bekoko<br>BP 5238 Douala, Cameroun<br>
          <a href="tel:+237677550447">(+237) 677 55 04 47</a><br><a href="tel:+237691100459">(+237) 691 10 04 59</a><br>
          <a href="mailto:commerciaux@multiprint.cm">commerciaux@multiprint.cm</a></address>
        <p style="margin-top:8px">{note("Numéros à afficher : à confirmer", "fournir")}</p>
      </div>
    </div>
    <div class="footer__bottom">
      <span>© 2026 Multiprint Labels &amp; Packaging</span>
      <span><a href="mentions-legales.html">Mentions légales</a> · <a href="mentions-legales.html#donnees">Données personnelles</a> · {note("Version anglaise /en/ à intégrer", "provisoire")}</span>
    </div>
  </div>
</footer>'''


MBAR = ('<nav class="mbar" aria-label="Actions rapides" data-mbar>'
        '<a class="mbar__call" href="tel:+237677550447"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg>Appeler</a>'
        '<a class="btn mbar__quote" href="contact.html#devis">Demander un devis</a></nav>')


def page(name, title, desc, body, cur='', home=False):
    css = ['motion-tokens.css?v=6'] + (['intro.css?v=6'] if home else []) + ['styles.css?v=8', 'b.css?v=6', 'gamme.css?v=2', 'c.css?v=3', 'final.css?v=12']
    links = '\n'.join(f'<link rel="stylesheet" href="{P}css/{c}">' for c in css)
    pre = f'<script>try{{if((/[?&]intro{chr(92)}b/.test(location.search)||!sessionStorage.getItem(\'mp-intro\'))&&!matchMedia(\'(prefers-reduced-motion: reduce)\').matches)document.documentElement.classList.add(\'intro-on\')}}catch(e){{}}</script>' if home else ''
    switch = ''
    doc = f'''<!doctype html>
<html lang="fr" class="show-notes">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="noindex">
<link rel="icon" type="image/png" href="{P}img/logos/favicon-64.png">
<link rel="apple-touch-icon" href="{P}img/logos/apple-touch-180.png">
<meta name="theme-color" content="#111214">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@100..125,400..800&amp;family=IBM+Plex+Mono:wght@400;500;600&amp;display=swap">
{links}
<script>document.documentElement.classList.add('js')</script>
{pre}
<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@type": "Organization", "name": "Multiprint Labels & Packaging", "url": "https://www.multiprint.cm/", "logo": "https://www.multiprint.cm/logo.png", "address": {"@type": "PostalAddress", "streetAddress": "Route Nationale N°3, avant l'échangeur de Bekoko", "postOfficeBoxNumber": "5238", "addressLocality": "Douala", "addressCountry": "CM"}, "telephone": "+237677550447", "email": "commerciaux@multiprint.cm", "foundingDate": "1983", "sameAs": ["https://www.linkedin.com/company/multiprint-cmr/", "https://www.facebook.com/multiprintcmr/"]}, ensure_ascii=False)}</script>
</head>
<body class="c-page f-page">
{INTRO if home else ''}<a class="skip" href="#main">Aller au contenu</a>
{LEGEND}
{header(cur)}
<main id="main" tabindex="-1">
{body}
</main>
{'' if name == 'contact.html' else MBAR}
{footer()}
<button class="notes-toggle" type="button" aria-pressed="true" data-notes-toggle>Notes maquette : affichées</button>
{switch}
<script>window.MP_INDEX={search_index()};</script>
<script src="{P}js/main.js?v=10" defer></script>
<script src="{P}js/final.js?v=4" defer></script>
{f'<script src="{P}js/intro.js?v=6" defer></script>' if home else ''}
</body>
</html>
'''
    (OUT / name).write_text(doc, encoding='utf-8')


def ghead(img, crumbs, h1, lead, actions='', facts='', pos='', full=False):
    cr = ' / '.join(f'<a href="{h}">{l}</a>' if h else l for h, l in crumbs)
    return f'''  <section class="ghead{' ghead--full' if full else ''} on-dark" aria-labelledby="page-title">
    {pic(img, '', '100vw', 'ghead__img', lazy=False, prio=True, pos=pos)}
    <div class="wrap"><div class="ghead__inner">
      <nav aria-label="Fil d'Ariane"><p class="breadcrumb">{cr}</p></nav>
      <h1 id="page-title">{h1}</h1>
      <p class="lead">{lead}</p>
      {f'<div class="hero__actions">{actions}</div>' if actions else ''}
      {f'<ul class="ghead__facts">{facts}</ul>' if facts else ''}
    </div></div>
  </section>
'''


def head2(h2, p='', id_=''):
    return f'<div class="head"><h2 class="h2 reveal"{f" id={chr(34)}{id_}{chr(34)}" if id_ else ""}>{h2}</h2>{f"<p class={chr(34)}reveal{chr(34)}>{p}</p>" if p else ""}</div>'


def vis_note(p):
    return {'ia': note('Agrandi par IA : packshot HD à fournir', 'visuel'), 'indicatif': note('Visuel indicatif : photo du produit à fournir', 'visuel')}.get(p.get('vis'), '')


def gamme_cards(head=True):
    cards = ''
    for g in GAMMES:
        prods = [p for p in PRODUITS if p['g'] == g['slug']]
        cards += f'''<li class="pcard reveal">
            <a class="pcard__media" href="{g['slug']}.html" tabindex="-1" aria-hidden="true"><span class="pcard__img">{pic(g['card'], '', '(max-width: 560px) 112px, (max-width: 1080px) 45vw, 300px')}</span><span class="pcard__count">{len(prods)} produits</span></a>
            <h3><a class="pcard__title" href="{g['slug']}.html">{g['nom']}</a></h3>
            <ul aria-label="Produits">{''.join(f'<li>{p["nom"].split(" (")[0]}</li>' for p in prods)}</ul>
            <span class="pcard__more"><a class="link-arrow" href="{g['slug']}.html">Voir la gamme</a></span>
          </li>'''
    return cards


PROOF = '''  <section class="cproof" aria-labelledby="proof-title">
    <div class="wrap">
      <h2 class="visually-hidden" id="proof-title">Multiprint en chiffres</h2>
      <ul>
        <li class="reveal"><strong><span data-count="40">40</span><sup>+</sup></strong><span>ans d'expertise</span><small>Fondée en 1983 sous le nom de Graphis Industrie</small></li>
        <li class="reveal"><strong><span data-count="224">224</span></strong><span>collaborateurs</span><small>Dont 99&#8239;% de nationalité camerounaise</small></li>
        <li class="reveal"><strong><span data-count="13">13</span></strong><span>familles de produits</span><small>Étiquettes, capsules, emballages souples et rigides</small></li>
        <li class="reveal"><strong>2012</strong><span>Première ligne de bouchons couronnes</span><small>Au Cameroun et en Afrique centrale</small></li>
      </ul>
      <p class="cproof__src"><span class="note">Sources : rapport RSE 2023 et catalogue produits</span> <span class="note note--fournir">Chiffres clés à compléter par Multiprint (CA, clients)</span></p>
    </div>
  </section>
'''

# Ligne de production : schéma de la B, panneaux avec les photos du shooting
SF = frag('savoir-faire.html')
MACHINE = SF[SF.index('<div class="machine'):SF.index('<div class="pstack">')]
PROCS = [
    ('extrusion', 'Extrusion', 'tour-extrusion', "Extrudeuse 3 couches installée en 2019. Les films PE sont recyclés en granulés sur site pour produire de nouveaux films.", ['3 couches', 'Recyclage PE'], note('Source : RSE 2023')),
    ('helio', 'Héliogravure', 'ligne-heliogravure', "Rotative d'héliogravure 8 couleurs, installée en 2019, pour les films et les emballages souples.", ['8 couleurs', 'Rotative'], note('Source : RSE 2023')),
    ('flexo', 'Flexogravure', 'ligne-impression', 'Impression à partir de clichés souples encrés aux encres UV : étiquettes autocollantes en BOPP, papier pour emballages cosmétiques.', ['Encres UV', 'BOPP'], note('Photo à confirmer : machine flexo ?', 'visuel')),
    ('offset', 'Impression offset', 'atelier-offset', "Impression offset sur papier, carton et métal, et tampographie sur métal et plastique.", ['Papier', 'Carton', 'Métal'], note('Catalogue : « impression sur métal »', 'adapte')),
    ('faconnage', 'Façonnage &amp; encartonnage', 'atelier-faconnage', "Coupe et découpe du papier et du carton, refente des bobines, emboutissage et pose des joints d'étanchéité sur les bouchons couronnes.", ['Découpe', 'Refente', 'Emboutissage'], ''),
]
panels = ''
for i, (pid, t, img, txt, specs, n) in enumerate(PROCS):
    panels += f'''<div class="ppanel" role="tabpanel" id="panel-{pid}" aria-labelledby="tab-{pid}"{'' if i == 0 else ' hidden'}>
          <div class="bpanel"><figure>{pic(img, '', '(max-width: 900px) 100vw, 60vw', lazy=False)}</figure>
            <div class="bpanel__text"><h3>{t}</h3><p>{txt} {n}</p><div class="ppanel__specs">{''.join(f'<span class="spec">{s}</span>' for s in specs)}</div></div></div>
        </div>
        '''
SAVOIR = f'''  <section class="section" id="savoir-faire" aria-labelledby="sf-title" style="background:#fff;border-top:1px solid var(--line)">
    <div class="wrap">
      <div class="head"><h2 class="h2 reveal" id="sf-title">Un site de production intégré</h2>
        <p class="reveal">De l'extrusion du film au façonnage, chaque étape est réalisée dans notre usine de Douala, certifiée ISO 45001.</p></div>
      <div data-tabs>
        {MACHINE}<div class="pstack">
        {panels}</div>
      </div>
    </div>
  </section>
'''

QUALITE = f'''  <section class="section bquality on-dark" id="qualite" aria-labelledby="qualite-title" style="color:#fff">
    {pic('controle-qualite', '', '100vw', 'bquality__bg', pos='50% 35%')}
    <div class="wrap">
      <div class="head"><h2 class="h2 reveal" id="qualite-title">Aux standards des plus grands groupes</h2>
        <p class="reveal" style="color:rgba(255,255,255,.82)">Chaque emballage est contrôlé avant livraison et accompagné d'un certificat d'analyse. Notre service QHSE veille à la conformité de chaque production. {note('Catalogue + site actuel', 'adapte')}</p></div>
      <ul class="seals">
        <li class="seal seal--red reveal"><span class="seal__ring" aria-hidden="true"><b>ISO 9001</b><small>2015</small></span><h3>Management de la qualité</h3><p>Certifié par Bureau Veritas, renouvelé en 2023.</p></li>
        <li class="seal reveal"><span class="seal__ring" aria-hidden="true"><b>ISO 45001</b><small>2018</small></span><h3>Santé et sécurité au travail</h3><p>Certifié par Bureau Veritas jusqu'en août 2028.</p><a class="link-arrow" href="https://www.multiprint.cm/assets/docs/certificat_iso45001.pdf">Certificat (PDF)</a></li>
        <li class="seal reveal"><span class="seal__ring" aria-hidden="true"><b>Nestlé</b><small>Fournisseur</small></span><h3>Fournisseur qualifié Nestlé</h3><p>Audit fournisseur réalisé avec succès en 2023.</p></li>
        <li class="seal reveal"><span class="seal__ring" aria-hidden="true"><b>HACCP</b><small>Alimentaire</small></span><h3>Sécurité des aliments</h3><p>FSSC 22000 en cours de certification. {note('Statut à mettre à jour', 'fournir')}</p></li>
      </ul>
      <div class="bproofs">
        <div class="reveal"><strong>100&#8239;%</strong><p>De nos déchets métalliques et papier recyclés.</p></div>
        <div class="reveal"><strong>1 / 1</strong><p>Chaque livraison accompagnée de son certificat d'analyse.</p></div>
        <div class="reveal"><strong>99&#8239;%</strong><p>De nos collaborateurs sont de nationalité camerounaise.</p></div>
      </div>
      <p style="margin-top:24px"><a class="link-arrow" href="a-propos.html#certifications" style="color:#fff">Toutes nos certifications</a></p>
    </div>
  </section>
'''

REFS = frag('references.html')
REFS = re.sub(r'src="img/clients/', f'src="{P}img/hd/clients/', REFS)
REFS = REFS.replace('<span class="note note--visuel">Logos Brasco, LTE, Mocaf en basse définition : vectoriels à fournir</span>', note('Logos agrandis par IA : versions vectorielles à demander, avec accord des clients', 'visuel'))
REFS = REFS.replace('Ils nous font confiance', 'Les industries de référence nous font confiance')
TESTI = f'''<div class="testi reveal"><span class="testi__mark" aria-hidden="true">“</span><div><b>Témoignage client</b><p>Emplacement prévu pour une citation, le nom, l'entreprise et le logo d'un client, avec son accord. {note('À fournir par Multiprint (cahier des charges §5.3)', 'fournir')}</p></div></div>'''
REFS = REFS.replace('    </div>\n  </section>', f'      {TESTI}\n    </div>\n  </section>', 1)

CTA = f'''  <section class="cta on-dark" id="contact" aria-labelledby="cta-title">
    <div class="wrap">
      <div class="cta__text"><h2 class="h2" id="cta-title" style="font-size:clamp(2.4rem,1.4rem + 4vw,4.5rem)">Parlons de votre projet</h2>
        <p class="lead">Décrivez votre besoin : notre équipe commerciale vous guide dans le choix des meilleures options d'emballage pour votre produit. {note('Catalogue produits, reformulé', 'adapte')}</p></div>
      <div class="cta__actions">
        <a class="btn btn--white" href="contact.html#devis">Demander un devis</a>
        <a class="btn btn--outline-white" href="tel:+237677550447">(+237) 677 55 04 47</a>
        <a class="btn btn--outline-white" href="mailto:commerciaux@multiprint.cm">commerciaux@multiprint.cm</a>
      </div>
    </div>
  </section>
'''

DG_QUOTE = "L'Afrique peut fabriquer ce qu'elle consomme. Et pas seulement fabriquer : fabriquer aux meilleurs standards du monde."
DG_NOTE = note('Piste du script du film institutionnel (ARMD) : à valider par le DG', 'provisoire')


def ncard(n, h3=True):
    media = pic(n['img'], '', '(max-width: 640px) 100vw, (max-width: 1000px) 50vw, 400px') if not n['img'].startswith('img/') else pic(n['img'], '')
    link = f'<a class="link-arrow" href="{n["link"][0]}">{n["link"][1]}</a>' if n.get('link') else ''
    return f'''<li class="ncard reveal" id="{n['id']}" data-cat="{n['cat']}"><div class="ncard__media img-reveal">{media}</div>
        <p class="ncard__meta"><span>{n['catl']}</span><time datetime="{n['iso']}">{n['date']}</time></p>
        <h3>{n['t']}</h3><p>{e(n['d'])} {note(*n['n']) if n.get('n') else ''}</p>{link}</li>'''


# ================================================================= COMPOSITIONS PHOTO
def band(img, title, id_, lead='', label='', quote=False, pos='50% 50%', mid=False, left=False, actions='', extra=''):
    cls = 'band on-dark' + (' band--mid' if mid else '') + (' band--left' if left else '')
    return f'''  <section class="{cls}" aria-labelledby="{id_}">
    <div class="band__media">{pic(img, '', '100vw', 'band__img', pos=pos)}</div>
    <div class="wrap band__inner"><div class="band__text reveal">
      {f'<p class="band__label">{label}</p>' if label else ''}
      <h2 class="band__title{' band__quote' if quote else ''}{' band__title--long' if len(title) > 70 else ''}" id="{id_}">{title}</h2>
      {f'<p class="lead">{lead}</p>' if lead else ''}{extra}
      {f'<div class="band__actions">{actions}</div>' if actions else ''}
    </div></div>
  </section>
'''


def split(img, inner, id_, side='left', tone='', pos='50% 50%', alt='', sid=''):
    cls = f'split split--{side}' + (f' split--{tone} on-dark' if tone else '')
    return f'''  <section class="{cls}"{f' id="{sid}"' if sid else ''} aria-labelledby="{id_}">
    <figure class="split__media img-reveal">{pic(img, alt, '(max-width: 900px) 100vw, 50vw', pos=pos)}</figure>
    <div class="split__body"><div class="split__inner">
      {inner}
    </div></div>
  </section>
'''


def ncard_feat(n):
    media = pic(n['img'], '', '(max-width: 900px) 100vw, 58vw') if not n['img'].startswith('img/') else pic(n['img'], '')
    link = f'<a class="link-arrow" href="{n["link"][0]}">{n["link"][1]}</a>' if n.get('link') else ''
    return f'''<li class="ncard ncard--feat" id="{n['id']}" data-cat="{n['cat']}"><div class="ncard__media img-reveal">{media}</div>
        <div class="ncard__body"><p class="ncard__meta"><span>À la une · {n['catl']}</span><time datetime="{n['iso']}">{n['date']}</time></p>
        <h3>{n['t']}</h3><p>{e(n['d'])} {note(*n['n']) if n.get('n') else ''}</p>{link}</div></li>'''


# ================================================================= ACCUEIL
HERO = f'''  <section class="bhero on-dark" aria-labelledby="hero-title">
    {pic('hall-heliogravure', "Hall d'héliogravure de l'usine Multiprint à Douala", '100vw', 'bhero__img', lazy=False, prio=True, pos='60% 50%')}
    <div class="wrap bhero__grid"><div class="bhero__text">
      <h1 id="hero-title" class="bhero__title"><span class="bhero__line">Experts en</span><span class="bhero__label">emballages</span><span class="bhero__line">industriels</span></h1>
      <p class="lead">Étiquettes, capsules, emballages souples et rigides pour l'industrie agroalimentaire, cosmétique et pharmaceutique, fabriqués à Douala aux standards internationaux. {note('Cahier des charges ARMD', 'adapte')} {note('Film institutionnel à intégrer en fond de hero', 'fournir')}</p>
      <div class="hero__actions"><a class="btn" href="contact.html#devis">Demander un devis</a><a class="btn btn--outline-white" href="solutions.html">Nos solutions</a></div>
      <ul class="facts bhero__facts" aria-label="Certifications et repères">
        <li class="fact"><button class="fact__btn" type="button" aria-describedby="tip-1983">Depuis 1983</button><span class="fact__tip" role="tooltip" id="tip-1983"><strong>Plus de 40 ans d'expertise</strong>Fondée en 1983 sous le nom de Graphis Industrie.</span></li>
        <li class="fact"><button class="fact__btn" type="button" aria-describedby="tip-9001">ISO 9001</button><span class="fact__tip" role="tooltip" id="tip-9001"><strong>Management de la qualité</strong>Certifié par Bureau Veritas.</span></li>
        <li class="fact"><button class="fact__btn" type="button" aria-describedby="tip-45001">ISO 45001</button><span class="fact__tip" role="tooltip" id="tip-45001"><strong>Santé et sécurité au travail</strong>Certifié par Bureau Veritas jusqu'en août 2028.</span></li>
        <li class="fact"><button class="fact__btn" type="button" aria-describedby="tip-nestle">Fournisseur Nestlé</button><span class="fact__tip" role="tooltip" id="tip-nestle"><strong>Fournisseur qualifié</strong>Audit fournisseur Nestlé réussi en 2023.</span></li>
      </ul>
    </div></div>
  </section>
'''
SOLS = f'''  <section class="cprod fsol" data-v="a" id="solutions" aria-labelledby="sol-title">
    <div class="wrap"><div class="cprod__panel">
      <div class="cprod__head"><h2 class="h2" id="sol-title">Nos solutions</h2>
        <p>Quatre gammes, treize familles de produits, imprimés en offset, héliogravure, flexographie ou tampographie, et personnalisés selon les contraintes de votre industrie. {note('Catalogue produits', 'adapte')}</p></div>
      <ul class="pgrid">{gamme_cards()}</ul>
      <div class="sectors"><p>Par secteur&#8239;:</p>{''.join(f'<a class="chip" href="solutions.html?secteur={k}#catalogue">{l}</a>' for k, l in SECTEURS)}<a class="chip" href="solutions.html#catalogue">Tout le catalogue</a></div>
    </div></div>
  </section>
'''
DG = split('dg-portrait', f'''<h2 class="band__label reveal" id="dg-title" style="color:rgba(255,255,255,.75)">Le mot du Directeur Général</h2>
      <blockquote class="reveal"><p>{DG_QUOTE}</p><footer><b>Ibrahima Ousmanou</b><span>Directeur Général, Multiprint Labels &amp; Packaging</span></footer></blockquote>
      <p class="reveal">{DG_NOTE}</p>
      <p class="reveal"><a class="link-arrow" href="a-propos.html" style="color:#fff">Notre histoire et notre vision</a></p>''',
            'dg-title', side='right', tone='ink', pos='50% 22%', alt='Ibrahima Ousmanou, Directeur Général de Multiprint')
NEWS_HOME = f'''  <section class="section section--mist" aria-labelledby="actu-title">
    <div class="wrap">
      <div class="head"><h2 class="h2 reveal" id="actu-title">Actualités</h2><p class="reveal"><a class="link-arrow" href="actualites.html">Toutes les actualités</a></p></div>
      <ul class="ncards">{''.join(ncard(n) for n in NEWS[:3])}</ul>
    </div>
  </section>
'''
CAREER = f'''  <section class="fcareer" aria-labelledby="car-title">
    {pic('equipe-allee', '', '100vw', pos='60% 50%')}
    <div class="wrap"><div class="fcareer__text">
      <h2 class="h2 reveal" id="car-title">Fabriquer ici, avec les talents d'ici</h2>
      <p class="lead reveal">224 collaborateurs, dont 99&#8239;% de nationalité camerounaise, formés sur nos lignes et accompagnés dans leur progression. {note('RSE 2023 + brief ARMD', 'adapte')}</p>
      <p class="reveal"><a class="btn btn--white" href="carrieres.html">Rejoindre Multiprint</a></p>
    </div></div>
  </section>
'''
page('index.html', 'Multiprint Labels &amp; Packaging : étiquettes et emballages industriels à Douala',
     "Étiquettes, capsules, emballages souples et rigides pour l'agroalimentaire, la cosmétique et la pharmacie. Fabricant certifié ISO 9001 et ISO 45001 à Douala, fournisseur qualifié Nestlé.",
     HERO + SOLS + PROOF + SAVOIR + QUALITE + DG + REFS + NEWS_HOME + CAREER + CTA, home=True)

# ================================================================= NOS SOLUTIONS (hub + catalogue)
def cat_card(p):
    g = G[p['g']]
    tags = ''.join(f'<span>{ML[m]}</span>' for m in p['mat'])
    return f'''<li class="pcard" data-gamme="{p['g']}" data-secteur="{' '.join(p['sec'])}" data-matiere="{' '.join(p['mat'])}" data-k="{e(p['imp'] + ' ' + p['fin'] + ' ' + p['liv'])}">
          <a class="pcard__media" href="{p['g']}.html#{p['id']}" tabindex="-1" aria-hidden="true">{pic(p['img'], '', '(max-width: 640px) 100vw, 280px')}</a>
          <h3><a href="{p['g']}.html#{p['id']}" style="text-decoration:none">{p['nom']}</a></h3>
          <p>{e(p['usage'])}</p>
          <span class="pcard__tags"><span>{g['court']}</span>{tags}</span>
          <a class="link-arrow" href="{p['g']}.html#{p['id']}">Voir la fiche</a>
        </li>'''

checks = lambda name, items: ''.join(f'<label><input type="checkbox" name="{name}" value="{k}"> {l}</label>' for k, l in items)
body = ghead('ligne-impression', [('index.html', 'Accueil'), ('', 'Nos solutions')], 'Nos solutions',
             "Quatre gammes et treize familles de produits pour habiller, protéger et valoriser vos produits, du premier prototype à la livraison en bobines ou en pièces.",
             '<a class="btn" href="contact.html#devis">Demander un devis</a><a class="btn btn--outline-white" href="#catalogue">Parcourir le catalogue</a>',
             '<li>Offset</li><li>Héliogravure</li><li>Flexographie</li><li>Tampographie</li><li>Extrusion</li>')
body += f'''  <section class="cprod fsol" data-v="a" aria-labelledby="g-title" style="margin-top:0;background:var(--mist);padding-top:var(--s8)">
    <div class="wrap"><div class="cprod__panel"><div class="cprod__head"><h2 class="h2" id="g-title">Quatre gammes</h2><p>Choisissez une gamme pour voir chaque produit, ses matières, ses finitions et ses modes de livraison.</p></div>
      <ul class="pgrid">{gamme_cards()}</ul></div></div>
  </section>
  <section class="section" id="catalogue" aria-labelledby="cat-title">
    <div class="wrap">
      {head2('Le catalogue', 'Filtrez par gamme, secteur ou matière, ou cherchez un mot-clé. ' + note('Secteurs indicatifs, à valider avec Multiprint', 'provisoire'), 'cat-title')}
      <div class="catalog" data-catalog>
        <div class="filters" role="search" aria-label="Filtrer le catalogue">
          <div class="field"><label for="cat-q">Mot-clé</label><input id="cat-q" type="search" placeholder="BOPP, bière, zip…"></div>
          <fieldset><legend>Gamme</legend>{checks('gamme', [(g['slug'], g['nom']) for g in GAMMES])}</fieldset>
          <fieldset><legend>Secteur</legend>{checks('secteur', SECTEURS)}</fieldset>
          <fieldset><legend>Matière</legend>{checks('matiere', MATIERES)}</fieldset>
          <button class="btn btn--ghost" type="button" id="cat-reset">Réinitialiser</button>
        </div>
        <div>
          <div class="cat-bar"><p id="cat-count" aria-live="polite">13 produits</p>
            <div class="view-switch" role="group" aria-label="Affichage"><button type="button" data-view="grid" aria-pressed="true">Grille</button><button type="button" data-view="list" aria-pressed="false">Liste</button></div></div>
          <ul class="pgrid pgrid--cat">{''.join(cat_card(p) for p in PRODUITS)}</ul>
          <p class="cat-empty" id="cat-empty" hidden>Aucun produit ne correspond. <button class="link-arrow" type="button" onclick="document.getElementById('cat-reset').click()" style="border:0;background:none;cursor:pointer;font:inherit">Réinitialiser les filtres</button></p>
        </div>
      </div>
    </div>
  </section>
'''
PERKS = f'''  <section class="section section--mist section--tight" aria-labelledby="perks-title">
    <div class="wrap">
      {head2("Personnalisé selon vos contraintes", "Des emballages génériques ou entièrement sur mesure, accompagnés d'un étiquetage adhésif pour la personnalisation et des systèmes de fermeture adaptés. " + note('Catalogue produits', 'adapte'), 'perks-title')}
      <ul class="perks">
        <li class="reveal"><b>Finitions</b><p>Gaufrage, dorure à chaud, effets métalliques, personnalisation pour vos promotions.</p></li>
        <li class="reveal"><b>Formes</b><p>Découpe matricielle sur mesure, ou forme régulière.</p></li>
        <li class="reveal"><b>Matières</b><p>Papier blanc ou métallisé, carton, films PE, LDPE, HDPE, PET, BOPP, aluminium, métal.</p></li>
        <li class="reveal"><b>Livraison</b><p>À l'unité, en pièces ou en bobines, avec un certificat d'analyse.</p></li>
      </ul>
    </div>
  </section>
'''
page('solutions.html', 'Nos solutions : étiquettes, capsules, emballages souples et rigides · Multiprint',
     "Catalogue Multiprint : étiquettes de colle et adhésives, stanioles, sleeves, bouchons couronnes, rouleaux imprimés, sachets, doypacks, sacs, films rétractables, boîtes imprimées.",
     body + PERKS + CTA, cur='solutions.html')

# ================================================================= PAGES GAMMES
# Bandeau « fabrication » propre à chaque gamme (faits : catalogue produits, site actuel, RSE 2023)
GBAND = {
    'etiquettes': ('atelier-offset', 'Imprimées sur nos presses offset et flexographiques',
                   "Quadrichromie ou ton direct, sur papier blanc ou métallisé, vinyle, BOPP ou film aluminium, puis découpe à la forme au massicot, à la lombardi ou par échenillage.", '55% 50%'),
    'capsules': ('capsules-convoyeur', "La première ligne de bouchons couronnes d'Afrique centrale",
                 "Depuis 2012, nos capsules sont imprimées sur métal, embouties, garnies de leur joint d'étanchéité et inspectées sur notre site de Douala.", '50% 55%'),
    'emballages-souples': ('stock-films-large', 'Du granulé à la bobine imprimée',
                           "Films extrudés en 3 couches sur notre site, imprimés en héliogravure 8 couleurs ou en flexographie, puis refendus, complexés et façonnés.", '50% 55%'),
    'emballages-rigides': ('atelier-faconnage-large', 'Imprimés en offset, façonnés sur place',
                           "Carton de 250 à 350 g imprimé en offset, découpé à la forme, plié et collé dans notre atelier de façonnage.", '50% 50%'),
}


def fiche(p, g, alt):
    tags = ''.join(f'<span class="chip">{SL[s]}</span>' for s in p['sec'])
    return f'''<article class="fiche{' fiche--alt' if alt else ''}" id="{p['id']}" aria-labelledby="{p['id']}-t">
        <figure class="fiche__media img-reveal">{pic(p['img'], p['nom'], '(max-width: 900px) 100vw, 45vw')}{vis_note(p)}</figure>
        <div class="fiche__body">
          <p class="fiche__gamme">{g['nom']}</p>
          <h2 id="{p['id']}-t">{p['nom']}</h2>
          <p class="fiche__lead">{e(p['usage'])}</p>
          <dl class="specs"><dt>Impression</dt><dd>{e(p['imp'])}</dd><dt>Finition</dt><dd>{e(p['fin'])}</dd><dt>Livraison</dt><dd>{e(p['liv'])}</dd><dt>Matières</dt><dd>{', '.join(ML[m] for m in p['mat'])}</dd></dl>
          <p style="margin-top:8px">{note('Source : catalogue produits Multiprint, à mettre à jour')}{' ' + note(*p['n']) if p.get('n') else ''}</p>
          <div class="fiche__tags" aria-label="Secteurs d'application">{tags}</div>
          <div class="fiche__actions"><a class="btn" href="contact.html?gamme={g['slug']}&amp;produit={p['id']}#devis">Demander un devis pour ce produit</a></div>
        </div>
      </article>
      '''


for g in GAMMES:
    prods = [p for p in PRODUITS if p['g'] == g['slug']]
    gnav = ''.join(f'<li><a href="{x["slug"]}.html"{" aria-current=" + chr(34) + "page" + chr(34) if x is g else ""}>{x["nom"]}</a></li>' for x in GAMMES)
    spy = ''.join(f'<li><a href="#{p["id"]}">{p["nom"].split(" (")[0]}</a></li>' for p in prods)
    cut = 2 if len(prods) > 3 else len(prods)
    first = ''.join(fiche(p, g, i % 2) for i, p in enumerate(prods[:cut]))
    rest = ''.join(fiche(p, g, (i + cut) % 2) for i, p in enumerate(prods[cut:]))
    img, t, txt, pos = GBAND[g['slug']]
    related = ''.join(f'<a href="{x["slug"]}.html">{pic(x["card"], "", "(max-width: 900px) 100vw, 33vw")}<span>{x["nom"]}</span></a>' for x in GAMMES if x is not g)
    body = ghead(g['hero'], [('index.html', 'Accueil'), ('solutions.html', 'Nos solutions'), ('', g['nom'])], g['nom'], e(g['lead']),
                 f'<a class="btn" href="contact.html?gamme={g["slug"]}#devis">Demander un devis</a><a class="btn btn--outline-white" href="#{prods[0]["id"]}">Voir les produits</a>',
                 ''.join(f'<li>{p["nom"].split(" (")[0]}</li>' for p in prods))
    body += f'''  <nav class="gnav" aria-label="Nos gammes"><div class="wrap"><ul>{gnav}</ul></div></nav>
  <nav class="fnav" aria-label="Produits de la gamme {e(g['nom'])}" data-spy><div class="wrap fnav__in">
    <ul>{spy}</ul><a class="btn fnav__cta" href="contact.html?gamme={g['slug']}#devis">Devis</a></div></nav>
  <section class="section section--fiches" aria-label="Fiches produits"><div class="wrap">
      {first}
  </div></section>
{band(img, t, 'gband-title', lead=txt, label='Fabriqué à Douala', left=True, pos=pos, mid=True)}'''
    if rest:
        body += f'''  <section class="section section--fiches" aria-label="Fiches produits (suite)"><div class="wrap">
      {rest}
  </div></section>
'''
    body += f'''{PERKS}  <section class="section" aria-labelledby="rel-title"><div class="wrap">{head2('Gammes complémentaires', '', 'rel-title')}<div class="related">{related}</div></div></section>
'''
    page(f'{g["slug"]}.html', f'{g["nom"]} · Multiprint Labels &amp; Packaging', g['lead'], body + CTA, cur='solutions.html')

# ================================================================= À PROPOS
TIMELINE = [('1983', "Création de Graphis Industrie, première entreprise de photocomposition et de photogravure au Cameroun."),
            ('1989', "Département sérigraphie industrielle : premières affiches routières et PLV imprimées au Cameroun."),
            ('2002', 'Première imprimante numérique grand format au Cameroun.'),
            ('2008', "Lancement de l'imprimerie industrielle spécialisée dans l'emballage alimentaire."),
            ('2012', "Première ligne de fabrication de bouchons couronnes au Cameroun et en Afrique centrale."),
            ('2019', "Extrudeuse 3 couches, emboutissage de capsules et rotative d'héliogravure 8 couleurs."),
            ('2020', 'Certification ISO 9001 version 2015.'), ('2022', "Ouverture d'une filiale au Congo."),
            ('2023', 'Quarante ans de Multiprint ; audit fournisseur Nestlé réussi.'), ('2025', 'Certification ISO 45001:2018 par Bureau Veritas.')]
track = ''.join(f'<li><time datetime="{y}">{y}</time><p>{e(t)}</p></li>' for y, t in TIMELINE)
CERTS = f'''  <section class="section" id="certifications" aria-labelledby="cert-title"><div class="wrap">
    {head2('Nos certifications', 'Des standards internationaux, vérifiés par des organismes indépendants et par nos clients.', 'cert-title')}
    <ul class="certs">
      <li class="cert cert--red reveal"><span class="cert__badge">ISO<br>9001</span><h3>ISO 9001:2015</h3><p>Management de la qualité. Certifié par Bureau Veritas, renouvelé en 2023.</p>{note('Certificat PDF à fournir', 'fournir')}</li>
      <li class="cert reveal"><span class="cert__badge">ISO<br>45001</span><h3>ISO 45001:2018</h3><p>Santé et sécurité au travail, pour l'ensemble de la fabrication des emballages. Valide jusqu'en août 2028.</p><a class="link-arrow" href="https://www.multiprint.cm/assets/docs/certificat_iso45001.pdf">Certificat (PDF)</a></li>
      <li class="cert reveal"><span class="cert__badge">Nestlé</span><h3>Fournisseur qualifié Nestlé</h3><p>Processus, normes et hygiène validés lors de l'audit fournisseur de 2023.</p></li>
      <li class="cert reveal"><span class="cert__badge">HACCP</span><h3>HACCP</h3><p>Analyse des dangers et maîtrise des points critiques pour les emballages au contact des aliments.</p></li>
      <li class="cert cert--pending reveal"><span class="cert__badge">FSSC<br>22000</span><h3>FSSC 22000 · en cours</h3><p>Sécurité des denrées alimentaires, certification engagée.</p>{note('Statut à mettre à jour', 'fournir')}</li>
      <li class="cert cert--pending reveal"><span class="cert__badge">Sedex</span><h3>Sedex · à confirmer</h3><p>Éthique de la chaîne d'approvisionnement.</p>{note('Adhésion à confirmer', 'fournir')}</li>
    </ul></div></section>
'''
body = ghead('equipe-direction', [('index.html', 'Accueil'), ('', 'À propos')], 'À propos',
             "Leader de l'emballage et de l'étiquetage au Cameroun, Multiprint Labels &amp; Packaging conçoit et fabrique depuis Douala les emballages des industries agroalimentaires, cosmétiques et pharmaceutiques d'Afrique centrale. " + note('Cahier des charges ARMD', 'adapte'),
             '<a class="btn" href="contact.html#devis">Demander un devis</a><a class="btn btn--outline-white" href="#histoire">Notre histoire</a>',
             '<li>Société anonyme de droit camerounais</li><li>Douala, Cameroun</li><li>Depuis 1983</li>', pos='50% 35%', full=True)
body += split('dg-bureau', f'''<h2 class="h2 reveal" id="dg2-title">Le mot du Directeur Général</h2>
      <blockquote class="reveal"><p>{DG_QUOTE}</p><footer><b>Ibrahima Ousmanou</b><span>Directeur Général</span></footer></blockquote>
      <p class="reveal">Quand l'entreprise a commencé, étiquettes, emballages et capsules étaient importés. Multiprint est née d'une conviction : fabriquer ici, pour valoriser les producteurs camerounais et régionaux, avec un emballage de qualité mondiale.</p>
      <p class="reveal">{DG_NOTE}</p>''', 'dg2-title', pos='58% 40%', alt='Ibrahima Ousmanou, Directeur Général, à son bureau')
body += band('ligne-impression', "Être le partenaire de référence dans la fourniture des solutions d'emballages en Afrique centrale à l'horizon 2030.",
             'vision-title', label='Notre vision', quote=True, pos='60% 50%', left=True)
body += f'''  <section class="section section--slate on-dark" id="histoire" aria-labelledby="hist-title"><div class="wrap">
      <div class="two-col">
        <h2 class="h2 reveal" id="hist-title">Une mission au service d'une vie meilleure</h2>
        <div class="lead-block">
          <p class="lead reveal">Contribuer à l'essor des produits industriels de qualité. Nous sommes convaincus que l'industrialisation entraîne la baisse des coûts des produits de grande consommation, et augmente ainsi le pouvoir d'achat et le niveau de vie de nos populations.</p>
          <ul class="values reveal" aria-label="Nos valeurs"><li class="chip">Intégrité</li><li class="chip">Engagement</li><li class="chip">Esprit d'équipe</li></ul>
        </div>
      </div>
      <div class="timeline btimeline reveal" data-track style="margin-top:var(--s8)">
        <div class="timeline__bar"><h3 class="pill-title">Plus de 40 ans d'histoire</h3>
          <div class="timeline__nav"><button type="button" data-prev aria-label="Repères précédents">←</button><button type="button" data-next aria-label="Repères suivants">→</button></div></div>
        <ol class="track" tabindex="0" aria-label="Repères historiques, défilement horizontal">{track}</ol>
      </div>
  </div></section>
{PROOF}{CERTS}  <section aria-labelledby="site-title">
    <div class="wrap mosaic-head">{head2('Notre site de Douala', "Une usine intégrée, de l'extrusion du film au façonnage, à Bekoko, sur la Route Nationale N°3.", 'site-title')}</div>
    <div class="mosaic">
      <figure class="m-1 img-reveal">{pic('ligne-heliogravure', "Ligne d'héliogravure", '(max-width: 760px) 100vw, 67vw')}<figcaption>Héliogravure</figcaption></figure>
      <figure class="m-2 img-reveal">{pic('tour-extrusion', "Tour d'extrusion de film", '(max-width: 760px) 50vw, 33vw')}<figcaption>Extrusion</figcaption></figure>
      <figure class="m-3 img-reveal">{pic('ligne-capsules', 'Ligne de fabrication de capsules', '(max-width: 760px) 50vw, 25vw')}<figcaption>Capsules</figcaption></figure>
      <figure class="m-4 img-reveal">{pic('atelier-faconnage-large', 'Atelier de façonnage', '(max-width: 760px) 50vw, 42vw')}<figcaption>Façonnage</figcaption></figure>
      <figure class="m-5 img-reveal">{pic('chariot-logistique', 'Logistique', '(max-width: 760px) 50vw, 33vw', pos='50% 60%')}<figcaption>Logistique</figcaption></figure>
    </div>
    <div class="wrap mosaic-foot"><div class="countries reveal"><span class="chip">Cameroun</span><span class="chip">Tchad</span><span class="chip">RCA</span><span class="chip">RD Congo</span><span class="chip">Guinée équatoriale</span> {note("RSE 2023 · zone CEMAC et Afrique de l'Ouest visées (cahier des charges)", 'adapte')}</div></div>
  </section>
'''
page('a-propos.html', 'À propos : histoire, vision et certifications · Multiprint', "Multiprint Labels & Packaging : plus de 40 ans d'histoire depuis Graphis Industrie en 1983, la vision du Directeur Général, nos valeurs et nos certifications ISO 9001, ISO 45001 et Nestlé.",
     body + CTA, cur='a-propos.html')

# ================================================================= RSE & IMPACT
STEPS = [
    ('cartons-imprimes', '100&#8239;%', 'Déchets métalliques et papier recyclés', "Chutes de carton, de papier et de métal sont triées et entièrement valorisées.", note('Source : RSE 2023')),
    ('tour-extrusion', 'PE', 'Le film recyclé en granulés', "Les chutes de film polyéthylène sont recyclées en granulés sur site, puis réintroduites dans l'extrudeuse pour produire de nouveaux films.", note('Source : RSE 2023')),
    ('equipe-production', '224', 'Emplois directs à Douala', "Dont 99&#8239;% de collaborateurs de nationalité camerounaise, formés sur nos lignes, en production comme en contrôle qualité.", note('Source : RSE 2023')),
    ('controle-qualite', '45001', 'Santé et sécurité certifiées', "Notre système de management de la santé et de la sécurité au travail est certifié ISO 45001:2018 par Bureau Veritas, pour toute la fabrication.", '<a class="link-arrow" href="https://www.multiprint.cm/assets/docs/certificat_iso45001.pdf">Voir le certificat</a>'),
    ('stock-films-large', 'ODD', 'Une contribution mesurée', "Notre rapport RSE suit chaque année notre contribution aux Objectifs de Développement Durable des Nations unies. Une centrale solaire photovoltaïque alimente le site.", note('Centrale solaire : presse 2026, à valider', 'presse')),
]
figs = ''.join(f'<figure{" class=" + chr(34) + "is-active" + chr(34) if i == 0 else ""}>{pic(img, "", "(max-width: 900px) 100vw, 58vw", lazy=i > 0)}</figure>' for i, (img, *_) in enumerate(STEPS))
steps = ''.join(f'''<li class="scrolly__step"><div class="scrolly__mob">{pic(img, '', '100vw')}</div><strong>{num}</strong><h3>{t}</h3><p>{txt}</p><p>{extra}</p></li>''' for img, num, t, txt, extra in STEPS)
body = ghead('granules', [('index.html', 'Accueil'), ('', 'RSE &amp; Impact')], 'RSE &amp; Impact',
             "Fabriquer localement, recycler sur site, former les talents d'ici : notre responsabilité se mesure chaque année dans notre rapport RSE.",
             '<a class="btn" href="https://www.multiprint.cm/assets/docs/rapport_rse_mtp.pdf">Télécharger le rapport RSE 2023 (PDF)</a><a class="btn btn--outline-white" href="#engagements">Nos engagements</a>', pos='50% 62%', full=True)
body += f'''  <section class="section" id="engagements" aria-labelledby="eng-title" data-scrolly><div class="wrap">
      {head2('Nos engagements, en chiffres', 'Cinq engagements suivis dans notre rapport RSE annuel.', 'eng-title')}
      <div class="scrolly__grid">
        <div class="scrolly__media" aria-hidden="true">{figs}<span class="scrolly__count">1 / {len(STEPS)}</span></div>
        <ol class="scrolly__steps">{steps}</ol>
      </div>
  </div></section>
'''
body += band('equipe-groupe', 'Fabriquer ici pour valoriser ici', 'imp-title', left=True, pos='50% 40%',
             lead="Nous produisons au Cameroun des emballages qui étaient importés, aux standards internationaux, et nous accompagnons les producteurs camerounais et régionaux du premier prototype jusqu'au produit fini sur les étagères : traçabilité, hygiène, qualité d'impression.",
             extra=f'<p style="margin-top:12px">{note("Messages clés du brief ARMD", "adapte")}</p>')
body += f'''  <section class="section section--mist section--tight" aria-labelledby="dl-title"><div class="wrap two-col" style="align-items:center">
      <div class="lead-block"><h2 class="h2 reveal" id="dl-title">Rapport RSE 2023</h2><p class="reveal">Chiffre d'affaires en hausse de 8&#8239;%, satisfaction client en hausse de 6&#8239;%, engagements environnementaux et sociaux.</p>
        <p class="reveal"><a class="btn" href="https://www.multiprint.cm/assets/docs/rapport_rse_mtp.pdf">Télécharger le rapport (PDF)</a> {note('Version navigable en ligne à prévoir', 'provisoire')}</p></div>
      <figure class="img-reveal" style="box-shadow:0 30px 60px -30px rgba(17,18,20,.45)">{pic('img/docs/rapport_rse.webp', 'Couverture du rapport RSE 2023 de Multiprint')}</figure>
  </div></section>
'''
page('rse.html', 'RSE & Impact : recyclage, emploi local, import-substitution · Multiprint', "Les engagements RSE de Multiprint : 100 % des déchets métalliques et papier recyclés, recyclage du PE, 224 emplois à Douala, certification ISO 45001, rapport RSE 2023.",
     body + CTA, cur='rse.html')

# ================================================================= ACTUALITÉS
cats = [('all', 'Toutes')] + sorted({(n['cat'], n['catl'] if n['cat'] != 'entreprise' else 'Entreprise') for n in NEWS}, key=lambda x: x[1])
body = ghead('anniversaire-40-ans', [('index.html', 'Accueil'), ('', 'Actualités')], 'Actualités',
             "Communiqués, événements, certifications et investissements de Multiprint. " + note('Rubrique gérée via le CMS (cahier des charges §2.3-5)', 'provisoire'), pos='50% 35%')
body += f'''  <section class="section" aria-labelledby="news-title"><div class="wrap">
      <h2 class="visually-hidden" id="news-title">Tous les articles</h2>
      <div class="nfilter" role="group" aria-label="Filtrer par catégorie">{''.join(f'<button type="button" data-cat="{k}" aria-pressed="{str(k == "all").lower()}">{l}</button>' for k, l in cats)}</div>
      <p class="visually-hidden" id="news-count" aria-live="polite"></p>
      <ul class="ncards ncards--two">{ncard_feat(NEWS[0])}{''.join(ncard(n) for n in NEWS[1:])}</ul>
  </div></section>
'''
body += band('poignee-de-main', 'Suivez Multiprint sur LinkedIn', 'li-title', mid=True, left=True, pos='50% 35%',
             lead="Actualités, certifications, recrutements et coulisses de l'usine de Douala.",
             actions='<a class="btn btn--white" href="https://www.linkedin.com/company/multiprint-cmr/">Suivre sur LinkedIn</a><a class="btn btn--outline-white" href="https://www.facebook.com/multiprintcmr/">Facebook</a>',
             extra=f'<p style="margin-top:12px">{note("Nouveaux comptes créés : liens à confirmer (cahier des charges §8.3)", "fournir")}</p>')
page('actualites.html', 'Actualités · Multiprint Labels &amp; Packaging', "Actualités de Multiprint : certification ISO 45001, rapport RSE 2023, 40 ans de l'entreprise, nouvelle presse offset, visite du Ministère de l'Industrie.",
     body + CTA, cur='actualites.html')

# ================================================================= CARRIÈRES
def field(id_, label, kind='text', req=False, extra='', hint='', ac=''):
    r = ' required aria-required="true"' if req else ''
    star = ' <span aria-hidden="true">*</span>' if req else ''
    hint_html = f'<small id="{id_}-hint">{hint}</small>' if hint else ''
    desc = f' aria-describedby="{id_}-err{" " + id_ + "-hint" if hint else ""}"'
    if kind == 'textarea': ctl = f'<textarea id="{id_}" name="{id_}" rows="4"{r}{desc}></textarea>'
    elif kind.startswith('select:'):
        opts = ''.join(f'<option value="{v}">{l}</option>' for v, l in [('', 'Choisir…')] + [tuple(o.split('=')) for o in kind[7:].split('|')])
        ctl = f'<select id="{id_}" name="{id_}"{r}{desc}>{opts}</select>'
    else: ctl = f'<input id="{id_}" name="{id_}" type="{kind}"{r}{desc}{f" autocomplete={chr(34)}{ac}{chr(34)}" if ac else ""}{extra}>'
    return f'<div class="field"><label for="{id_}">{label}{star}</label>{hint_html}{ctl}<p class="err" id="{id_}-err"></p></div>'

PORTRAITS = ['portrait-allee-1', 'portrait-jardin-3', 'portrait-allee-4', 'portrait-jardin-1', 'portrait-allee-2', 'portrait-laboratoire',
             'portrait-jardin-4', 'portrait-allee-3', 'portrait-jardin-2', 'portrait-allee-5', 'portrait-jardin-5']
film = ''.join(f'<li><figure class="img-reveal">{pic(s, "Collaborateur de Multiprint", "(max-width: 640px) 72vw, 340px", pos="50% 30%")}</figure></li>' for s in PORTRAITS)
body = ghead('equipe-allee', [('index.html', 'Accueil'), ('', 'Carrières')], 'Carrières',
             "Opérateurs, techniciens, qualiticiens, commerciaux : rejoignez une équipe de 224 personnes qui fabrique au Cameroun des emballages aux standards internationaux.",
             '<a class="btn" href="#candidature">Candidature spontanée</a><a class="btn btn--outline-white" href="#offres">Offres d\'emploi</a>', pos='55% 45%', full=True)
body += split('portrait-operatrice', f'''<h2 class="h2 reveal" id="cult-title">Une équipe formée sur nos lignes</h2>
      <p class="lead reveal">Certains collaborateurs sont là depuis le début. D'autres arrivent, et nous les formons, en production comme en contrôle qualité. {note('Adapté du script du film (ARMD)', 'adapte')}</p>
      <ul class="values reveal" aria-label="Nos valeurs"><li class="chip">Intégrité</li><li class="chip">Engagement</li><li class="chip">Esprit d'équipe</li></ul>
      <div class="stats-inline reveal"><div><strong>224</strong><span>collaborateurs</span></div><div><strong>99<sup>&#8239;%</sup></strong><span>de nationalité camerounaise</span></div><div><strong>40<sup>+</sup></strong><span>ans d'expertise</span></div></div>''',
                'cult-title', side='right', tone='ink', pos='50% 25%', alt='Opératrice de production Multiprint')
body += f'''  <section class="film" data-film aria-labelledby="film-title">
    <div class="wrap film__head"><div><h2 class="h2 reveal" id="film-title">Ceux qui fabriquent</h2><p class="reveal">Production, maintenance, qualité, logistique : les femmes et les hommes de l'usine de Douala. {note('Diffusion : selon le tableau de participation photos', 'fournir')}</p></div>
      <div class="film__nav"><button type="button" data-film-prev aria-label="Portraits précédents">←</button><button type="button" data-film-next aria-label="Portraits suivants">→</button></div></div>
    <ul class="film__track" tabindex="0" aria-label="Portraits de collaborateurs, défilement horizontal">{film}</ul>
  </section>
'''
body += band('atelier-equipe-large', "Investir dans les gens, c'est investir dans la qualité.", 'quote-title', quote=True, pos='60% 45%', left=True,
             extra=f'<p style="margin-top:12px">{note("Piste du script du film (ARMD) : à valider", "provisoire")}</p>')
body += f'''  <section class="section section--mist" id="offres" aria-labelledby="jobs-title"><div class="wrap">
      {head2("Offres d'emploi", '', 'jobs-title')}
      <div class="jobs-empty reveal"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 13h18"/></svg>
        <div><b>Aucune offre publiée pour le moment.</b><p>Envoyez-nous une candidature spontanée : nous la conservons et vous recontactons dès qu'un poste correspond à votre profil. {note('Offres et filtres (poste, lieu) à alimenter via le CMS', 'fournir')}</p></div></div>
  </div></section>
  <section class="section" id="candidature" aria-labelledby="cand-title"><div class="wrap two-col">
      <div class="lead-block"><h2 class="h2" id="cand-title">Candidature spontanée</h2><p class="lead">Votre CV est transmis au service des ressources humaines.</p><p>Les champs marqués * sont obligatoires.</p></div>
      <div>
        <form class="fform" data-simple="cand-done" novalidate>
          {field('c-nom', 'Nom et prénom', req=True, ac='name', extra=' data-missing="Indiquez votre nom et prénom."')}
          <div class="fields">{field('c-email', 'Email', 'email', req=True, ac='email', extra=' data-missing="Indiquez votre adresse email."')}{field('c-tel', 'Téléphone', 'tel', ac='tel')}</div>
          {field('c-poste', 'Domaine souhaité', 'select:production=Production|qualite=Qualité et QHSE|maintenance=Maintenance|commercial=Commercial et marketing|admin=Administration et finance|autre=Autre', req=True)}
          {field('c-cv', 'CV (PDF, 5 Mo maximum)', 'file', req=True, extra=' accept=".pdf,.doc,.docx" data-missing="Joignez votre CV."')}
          {field('c-msg', 'Message', 'textarea')}
          <p class="hint">Vos données servent uniquement au traitement de votre candidature.</p>
          <button class="btn" type="submit">Envoyer ma candidature</button>
        </form>
        <div class="done" id="cand-done" tabindex="-1" role="status" hidden><h3>Candidature envoyée</h3><p>Merci. Le service des ressources humaines a bien reçu votre candidature. {note('Notification RH par email à brancher', 'provisoire')}</p></div>
      </div>
  </div></section>
'''
page('carrieres.html', 'Carrières : rejoindre Multiprint à Douala', "Rejoindre Multiprint Labels & Packaging : culture d'entreprise, valeurs, offres d'emploi et candidature spontanée en ligne.", body + CTA, cur='carrieres.html')

# ================================================================= CONTACT (devis par étapes + contact général)
prod_opts = ''.join(f'<optgroup label="{g["nom"]}">' + ''.join(f'<option value="{p["id"]}">{p["nom"]}</option>' for p in PRODUITS if p['g'] == g['slug']) + '</optgroup>' for g in GAMMES)
gchoice = ''.join(f'<label><input type="radio" name="gamme" value="{g["slug"]}"> {g["nom"]}</label>' for g in GAMMES) + '<label><input type="radio" name="gamme" value="conseil"> Je ne sais pas encore</label>'
MAP = 'https://www.google.com/maps?q=Multiprint+Labels+%26+Packaging+Bekoko+Douala&output=embed'
body = ghead('entrepot', [('index.html', 'Accueil'), ('', 'Contact')], 'Contact',
             "Une demande de devis, une question technique, un rendez-vous à l'usine : notre équipe commerciale vous répond.",
             '<a class="btn" href="#devis">Demander un devis</a><a class="btn btn--outline-white" href="tel:+237677550447">(+237) 677 55 04 47</a>', pos='50% 50%')
body += f'''  <section class="section" aria-label="Formulaires de contact"><div class="wrap contact-grid">
    <div data-tabs2>
      <div class="tabs-2" role="tablist" aria-label="Type de demande">
        <button role="tab" id="t-devis" aria-controls="devis" aria-selected="true">Demande de devis</button>
        <button role="tab" id="t-contact" aria-controls="message" aria-selected="false" tabindex="-1">Contact général</button>
      </div>
      <div role="tabpanel" id="devis" aria-labelledby="t-devis">
        <ol class="steps" aria-label="Étapes de la demande"><li aria-current="step">Votre besoin</li><li>Volume et délai</li><li>Vos coordonnées</li></ol>
        <form class="fform" id="quote-form" novalidate>
          <fieldset class="step"><h3 class="h3">Votre besoin</h3>
            <div class="field" id="gamme-group" data-required-group data-missing="Choisissez une gamme, ou « Je ne sais pas encore »."><span style="font-weight:600">Gamme <span aria-hidden="true">*</span></span><div class="choice" role="radiogroup" aria-describedby="gamme-group-err">{gchoice}</div><p class="err" id="gamme-group-err"></p></div>
            <div class="fields">
              <div class="field"><label for="produit">Produit</label><select id="produit" name="produit"><option value="">Choisir…</option>{prod_opts}<option value="autre">Autre produit</option></select></div>
              {field('secteur', 'Secteur', 'select:agro=Agroalimentaire et boissons|cosmetique=Cosmétique|pharma=Pharmaceutique|autre=Autre')}
            </div>
            <div class="step-actions"><span></span><button class="btn" type="button" data-next-step>Continuer</button></div>
          </fieldset>
          <fieldset class="step" hidden><h3 class="h3">Volume et délai</h3>
            <div class="fields">{field('quantite', 'Quantité estimée', 'number', req=True, extra=' min="1" inputmode="numeric" data-missing="Indiquez une quantité estimée."')}{field('unite', 'Unité', 'select:pieces=Pièces|bobines=Bobines|kg=Kilogrammes')}</div>
            {field('delai', 'Délai souhaité', 'select:urgent=Moins de 2 semaines|mois=Dans le mois|trimestre=Dans le trimestre|projet=Projet à l\'étude')}
            {field('fichiers', 'Fichiers (maquette, cahier des charges)', 'file', extra=' multiple accept=".pdf,.ai,.eps,.png,.jpg"', hint='PDF, AI, EPS, PNG ou JPG')}<p class="hint" id="fichiers-info" aria-live="polite"></p>
            {field('besoin', 'Précisions', 'textarea', hint='Format, matière, nombre de couleurs, finitions…')}
            <label style="display:flex;gap:8px;align-items:center"><input type="checkbox" name="echantillon"> Je souhaite recevoir un échantillon</label>
            <div class="step-actions"><button class="btn btn--ghost" type="button" data-prev-step>Retour</button><button class="btn" type="button" data-next-step>Continuer</button></div>
          </fieldset>
          <fieldset class="step" hidden><h3 class="h3">Vos coordonnées</h3>
            <div class="fields">{field('societe', 'Société', req=True, ac='organization', extra=' data-missing="Indiquez le nom de votre société."')}{field('nom', 'Nom et prénom', req=True, ac='name', extra=' data-missing="Indiquez votre nom."')}</div>
            <div class="fields">{field('email', 'Email professionnel', 'email', req=True, ac='email', extra=' data-missing="Indiquez votre adresse email."')}{field('tel', 'Téléphone', 'tel', ac='tel')}</div>
            {field('pays', 'Pays', 'select:CM=Cameroun|TD=Tchad|CF=République centrafricaine|CD=RD Congo|CG=Congo|GA=Gabon|GQ=Guinée équatoriale|autre=Autre')}
            <label style="display:flex;gap:8px;align-items:center"><input type="checkbox" name="whatsapp"> Me recontacter aussi par WhatsApp</label>
            <h4 style="margin-top:8px">Récapitulatif</h4><dl class="recap" id="recap"></dl>
            <p class="hint">Vos données servent uniquement au traitement de votre demande. {note('Protection anti-spam reCAPTCHA v3 et envoi CRM à brancher', 'provisoire')}</p>
            <div class="step-actions"><button class="btn btn--ghost" type="button" data-prev-step>Retour</button><button class="btn" type="submit">Envoyer ma demande</button></div>
          </fieldset>
        </form>
        <div class="done" id="quote-done" tabindex="-1" role="status" hidden><h3>Demande envoyée</h3>
          <p>Merci <b data-company></b>. Un accusé de réception est envoyé à <b data-email></b>, et notre service commercial revient vers vous rapidement. {note('Délai de réponse à fournir', 'fournir')}</p>
          <p><a class="link-arrow" href="solutions.html">Revenir au catalogue</a></p></div>
      </div>
      <div role="tabpanel" id="message" aria-labelledby="t-contact" hidden>
        <form class="fform" data-simple="msg-done" novalidate>
          <div class="fields">{field('m-nom', 'Nom et prénom', req=True, ac='name', extra=' data-missing="Indiquez votre nom."')}{field('m-soc', 'Société', ac='organization')}</div>
          <div class="fields">{field('m-email', 'Email', 'email', req=True, ac='email', extra=' data-missing="Indiquez votre adresse email."')}{field('m-tel', 'Téléphone', 'tel', ac='tel')}</div>
          {field('m-objet', 'Objet', 'select:info=Information générale|partenariat=Partenariat|presse=Presse et médias|fournisseur=Fournisseur|autre=Autre')}
          {field('m-msg', 'Message', 'textarea', req=True, extra=' data-missing="Écrivez votre message."')}
          <p class="hint">Vos données servent uniquement au traitement de votre demande.</p>
          <button class="btn" type="submit">Envoyer</button>
        </form>
        <div class="done" id="msg-done" tabindex="-1" role="status" hidden><h3>Message envoyé</h3><p>Merci, nous vous répondons rapidement.</p></div>
      </div>
    </div>
    <aside class="coords" aria-label="Coordonnées">
      <div><h3>Usine et siège</h3><address>Multiprint Labels &amp; Packaging<br>Route Nationale N°3, avant l'échangeur de Bekoko<br>BP 5238 Douala, Cameroun</address></div>
      <div><h3>Service commercial</h3><p><a href="tel:+237677550447">(+237) 677 55 04 47</a><br><a href="tel:+237691100459">(+237) 691 10 04 59</a><br><a href="mailto:commerciaux@multiprint.cm">commerciaux@multiprint.cm</a></p></div>
      <div class="map" data-map="{MAP}">{pic('chariot-logistique', '', '(max-width: 1000px) 100vw, 40vw', pos='50% 60%')}
        <div class="map__load"><p>La carte est fournie par Google Maps, qui peut déposer des cookies.</p><button class="btn" type="button">Afficher la carte</button>
          <a class="link-arrow" href="https://www.google.com/maps/search/?api=1&amp;query=Multiprint+Bekoko+Douala">Ouvrir l'itinéraire</a></div></div>
      <p>{note('Position exacte du site à valider sur la carte', 'fournir')}</p>
    </aside>
  </div></section>
'''
page('contact.html', 'Contact et demande de devis · Multiprint Labels &amp; Packaging', "Demandez un devis en trois étapes ou contactez Multiprint : usine Route Nationale N°3, Bekoko, Douala. (+237) 677 55 04 47, commerciaux@multiprint.cm.",
     body, cur='contact.html')

# ================================================================= MENTIONS LÉGALES
body = f'''  <nav class="crumbs" aria-label="Fil d'Ariane"><div class="wrap"><ol><li><a href="index.html">Accueil</a></li><li>Mentions légales</li></ol></div></nav>
  <section class="section"><div class="wrap legal">
    <h1 class="h2">Mentions légales</h1>
    <p>{note('Contenu à valider par le service juridique de Multiprint', 'fournir')}</p>
    <h2>Éditeur</h2><p>Multiprint Labels &amp; Packaging, société anonyme de droit camerounais. Siège : Route Nationale N°3, avant l'échangeur de Bekoko, BP 5238 Douala, Cameroun. Directeur de la publication : Ibrahima Ousmanou, Directeur Général. {note('RCCM et NIU à fournir', 'fournir')}</p>
    <h2>Hébergement</h2><p>{note('Hébergeur à définir avec le service informatique (cahier des charges §3.2)', 'fournir')}</p>
    <h2>Propriété intellectuelle</h2><p>Les textes, photographies, logos et marques présents sur ce site sont la propriété de Multiprint Labels &amp; Packaging ou de leurs titulaires. Les logos clients sont reproduits avec leur accord.</p>
    <h2 id="donnees">Données personnelles</h2><p>Les informations saisies dans les formulaires de devis, de contact et de candidature servent uniquement au traitement de votre demande par le service concerné. Vous pouvez demander leur consultation, leur rectification ou leur suppression à <a href="mailto:commerciaux@multiprint.cm">commerciaux@multiprint.cm</a>. Les outils de mesure d'audience ne sont activés qu'avec votre accord.</p>
  </div></section>
'''
page('mentions-legales.html', 'Mentions légales · Multiprint', 'Mentions légales et données personnelles du site Multiprint Labels & Packaging.', body)

print('pages :', sorted(x.name for x in OUT.glob('*.html')))
