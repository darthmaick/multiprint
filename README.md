# Multiprint Labels & Packaging — maquette du nouveau site

Maquette HTML/CSS/JS statique du futur site de Multiprint Labels & Packaging (Douala, Cameroun),
réalisée par Mad Makers en accompagnement d'ARMD Group, d'après le cahier des charges ARMD (avril 2026),
le catalogue produits et le shooting professionnel. Maquette de travail : contenus à valider par Multiprint.

## Ouvrir le site en local

Prérequis : Python 3.

```bash
git clone https://github.com/darthmaick/multiprint.git
cd multiprint
python tools/serve.py 8765
```

Puis ouvrir http://localhost:8765/

## Pages

`index.html` (accueil), `solutions.html` (catalogue filtrable), `etiquettes.html`, `capsules.html`,
`emballages-souples.html`, `emballages-rigides.html` (gammes et fiches produits), `a-propos.html`, `rse.html`,
`actualites.html`, `carrieres.html`, `contact.html` (devis en 3 étapes), `mentions-legales.html`.

## Organisation

| Dossier | Rôle |
|---|---|
| `css/` | `styles.css` (base), `b.css`, `c.css`, `gamme.css` (composants), `final.css` (pages et compositions), `intro.css`, `motion-tokens.css` (durées et courbes des animations). |
| `js/` | `main.js` (menu, onglets, ligne de production, frise), `final.js` (recherche, catalogue, devis, compositions photo, barre mobile), `intro.js` (animation du logo). |
| `img/` | Images optimisées en WebP : `shoot/` (shooting professionnel), `hd/` (agrandies par IA, à remplacer par des packshots), `photos/`, `clients/`, `logos/`, `docs/`. |
| `tools/` | `build_final.py` génère les 12 pages ; `fragments/` contient les blocs partagés ; `serve.py` (serveur local) ; `check_links.py` (vérification des liens). |
| `A-VALIDER-AVEC-MULTIPRINT.md` | Points à valider ou à fournir par le client. |

## Modifier le site

Les pages sont générées : modifier `tools/build_final.py` (ou `tools/fragments/`), puis lancer

```bash
python tools/build_final.py
python tools/check_links.py
```

Les pastilles colorées (bouton « Notes maquette ») indiquent la source de chaque contenu et ce qui reste à fournir.
