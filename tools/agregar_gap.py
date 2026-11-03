#!/usr/bin/env python3
"""Suma productos GAP Factory (tools/gapfactory.tsv) al catálogo publicado (index.html) sin tocar los de Carter's.

Uso: python3 tools/agregar_gap.py
- Precio con la misma fórmula (precio.py) y las mismas reglas: $30.300–$35.000 pasan a $29.900.
- Agrega las categorías nuevas (Bodies, Buzos), el filtro por Marca y la equivalencia de talles GAP.
- Es idempotente: si ya hay tarjetas GAP, las reemplaza.
"""
import csv, html, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from precio import precio

COT = 1560
HERE = os.path.dirname(os.path.abspath(__file__))
IDX = os.path.join(HERE, '..', 'index.html')
CATS = ["Packs de Bodies", "Bodies", "Sets 2 Piezas", "Sets 3 Piezas", "Enteritos", "Vestidos",
        "Remeras", "Buzos", "Shorts", "Pijamas", "Pijamas de Polar", "Mallas", "Medias", "Mantas",
        "Mitones", "Ropa interior", "Hora del baño", "Hora de comer"]
CHIP_TXT = {'Hora del baño': 'Skip Hop · Hora del baño', 'Hora de comer': 'Skip Hop · Hora de comer'}

def fmt(n): return '$' + f"{n:,}".replace(',', '.')

def card(r):
    p = precio(float(r['usd']), COT)
    if 30300 <= p <= 35000: p = 29900
    t = r['talles'].split('|')
    eds = [e for e, ok in (('Bebés', any(not x.endswith('T') for x in t)), ('Niños', any(x.endswith('T') for x in t))) if ok]
    nom = html.escape(r['nombre'], quote=True)
    url = f'https://www.gapfactory.com/browse/product.do?pid={r["code"]}'
    img = f'https://content.gapinc.com/b/00{r["img"]}?width=600'
    def grp(xs): return ''.join(f'<button class="tl" data-t="{x}">{x}</button>' for x in xs)
    tb = [x for x in t if not x.endswith('T')]; tn = [x for x in t if x.endswith('T')]
    if tb and tn:
        btns = f'{grp(tb)}</div>\n<p class="lb">Talles niños</p>\n<div class="tls">{grp(tn)}'; lbl = 'Talles bebés'
    else:
        btns = grp(t); lbl = 'Talles niños' if tn else 'Talles bebés'
    return p, (
        f'<article class="card" data-marca="gapfactory" data-cat="{r["cat"]}" data-edad="{"|".join(eds)}" data-gen="{r["gen"]}" '
        f'data-talles="{r["talles"]}" data-code="{r["code"]}" data-nom="{nom}" data-precio="{p}">\n'
        f'<a class="ph" href="{url}" target="_blank" rel="noopener"><img loading="lazy" src="{img}" alt="{nom}" '
        f'onerror="this.style.opacity=0"></a>\n<div class="bd">\n<span class="tag">GAP Factory · {r["cat"]} · {" y ".join(eds)}</span>\n'
        f'<h3><a class="nm" href="{url}" target="_blank" rel="noopener">{nom}</a></h3>\n<div class="pr"><b>{fmt(p)}</b></div>\n'
        f'<p class="lb">{lbl}</p>\n<div class="tls">{btns}</div>\n<button class="add" disabled>Elegí un talle</button>\n</div></article>')

s = open(IDX, encoding='utf-8').read()
g0 = s.index('<div class="grid" id="grid">') + len('<div class="grid" id="grid">')
g1 = s.index('</div><div class="empty" id="empty">')
arts = re.findall(r'<article class="card"[\s\S]*?</article>', s[g0:g1])
arts = [a for a in arts if 'data-marca="gapfactory"' not in a]
# Carter's / Skip Hop: marca explícita y etiqueta
fixed = []
for a in arts:
    sk = re.search(r'data-cat="(Hora del baño|Hora de comer)"', a)
    if 'data-marca=' not in a:
        a = a.replace('<article class="card" ', f'<article class="card" data-marca="{"skiphop" if sk else "carters"}" ', 1)
        if not sk:
            a = a.replace('<span class="tag">', '<span class="tag">Carter\'s · ', 1)
    fixed.append(a)
items = [(CATS.index(re.search(r'data-cat="([^"]+)"', a).group(1)), int(re.search(r'data-precio="(\d+)"', a).group(1)), 0, a) for a in fixed]
gap = list(csv.DictReader(open(os.path.join(HERE, 'gapfactory.tsv'), encoding='utf-8'), delimiter='\t'))
for r in gap:
    p, a = card(r)
    items.append((CATS.index(r['cat']), p, 1, a))
items.sort(key=lambda x: (x[0], x[1], x[2]))
s = s[:g0] + '\n' + '\n'.join(x[3] for x in items) + '\n' + s[g1:]

# Filtro de categorías (solo las que tienen productos) + filtro de marca
present = {re.search(r'data-cat="([^"]+)"', x[3]).group(1) for x in items}
chips = ''.join(f'<button class="chip" data-f="cat" data-v="{c}">{CHIP_TXT.get(c, c)}</button>' for c in CATS if c in present)
s = re.sub(r'<div class="frow wrap"><em>Categoría</em>.*?</div>', f'<div class="frow wrap"><em>Categoría</em>{chips}</div>', s, count=1)
MARCA = ('<div class="frow" id="fmarca"><em>Marca</em><button class="chip" data-f="marca" data-v="carters">Carter\'s</button>'
         '<button class="chip" data-f="marca" data-v="gapfactory">GAP Factory</button><button class="chip" data-f="marca" data-v="skiphop">Skip Hop</button></div>')
s = re.sub(r'<div class="frow" id="fmarca">.*?</div>', '', s)
s = re.sub(r'(<div class="frow wrap"><em>Categoría</em>.*?</div>)', lambda m: m.group(1) + MARCA, s, count=1)
s = s.replace('var F={cat:null,gen:null,talle:null,edad:null};', 'var F={cat:null,gen:null,talle:null,edad:null,marca:null};')
if '(!F.marca||' not in s:
    s = s.replace("var ok=(!F.cat||c.dataset.cat===F.cat)", "var ok=(!F.marca||c.dataset.marca===F.marca)&&(!F.cat||c.dataset.cat===F.cat)")
assert '(!F.marca||' in s

# Tabla de talles: equivalencia GAP
NOTA = ('<br><b>GAP:</b> 0-3 meses = 3M · 3-6 meses = 6M · 6-12 meses = 12M · 12-18 meses = 18M · 18-24 meses = 24M · '
        '2 a 5 años = 2T a 5T. Hasta 3,2 kg = NB.')
if '<b>GAP:</b>' not in s:
    i = s.index('<div class="ttn">'); j = s.index('</div>', i)
    s = s[:j] + NOTA + s[j:]
open(IDX, 'w', encoding='utf-8').write(s)
n_gap = sum(1 for x in items if x[2] == 1)
print(f'{len(items)} productos ({n_gap} GAP)')
