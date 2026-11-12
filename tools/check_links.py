# -*- coding: utf-8 -*-
"""Vérifie tous les liens internes de la maquette : page cible existante et ancre (#id) existante.
Usage : python tools/check_links.py"""
import html.parser, pathlib, sys, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
pages = sorted(p for p in ROOT.glob('*.html') if not p.name.startswith('_'))


class Collect(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.links = set(), []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.add(a['id'])
        if tag == 'a' and 'href' in a:
            self.links.append((a['href'], self.getpos()[0]))


parsed = {}
for p in pages:
    c = Collect()
    c.feed(p.read_text(encoding='utf-8'))
    parsed[p.name] = c

errors, count = [], 0
for name, c in parsed.items():
    for href, line in c.links:
        u = urllib.parse.urlparse(href)
        if u.scheme in ('http', 'https', 'mailto', 'tel') or href.startswith('//'):
            continue
        count += 1
        target = u.path or name
        if target not in parsed:
            if not (ROOT / target).exists():
                errors.append(f'{name}:{line}  {href}  -> fichier introuvable')
            continue
        if u.fragment and u.fragment not in parsed[target].ids:
            errors.append(f'{name}:{line}  {href}  -> ancre #{u.fragment} absente de {target}')
        if href == '#':
            errors.append(f'{name}:{line}  lien vide « # »')

print(f'{len(pages)} pages, {count} liens internes vérifiés, {len(errors)} problème(s)')
for e in errors:
    print('  ' + e)
sys.exit(1 if errors else 0)
