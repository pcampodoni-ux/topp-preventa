#!/usr/bin/env python3
"""Arma el catálogo de un pedido nuevo en index.html a partir de:
  tools/carters_bf.tsv   (Carter's: code cat gen nombre usd talles img fijo)  → margen 1,9
  tools/gapfactory.tsv   (GAP Factory: code cat gen nombre usd talles img)    → margen 1,7
Reemplaza TODOS los productos, filtros de categoría/edad/talles y la fecha de cierre.
Uso: python3 tools/armar_pedido.py --cierre 2026-11-05T23:30:00-03:00 --titulo "Black Friday"
"""
import argparse, csv, html, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import precio as P

ap = argparse.ArgumentParser()
ap.add_argument('--cierre', required=True); ap.add_argument('--titulo', default='Black Friday'); ap.add_argument('--cot', type=float, default=1560)
a = ap.parse_args()
HERE = os.path.dirname(os.path.abspath(__file__)); IDX = os.path.join(HERE, '..', 'index.html')
IMG_C = 'https://dw.cartersstorefront.com/dw/image/v2/AAMK_PRD/on/demandware.static/-/Sites-carters_master_catalog/default/'
CATS = ["Packs de Bodies", "Bodies", "Sets 2 Piezas", "Enteritos", "Pijamas", "Pijamas de Polar", "Vestidos", "Remeras", "Buzos", "Camperas",
        "Pantalones", "Shorts", "Mallas", "Medias", "Ropa interior", "Accesorios"]
ACC = {'Medias', 'Accesorios', 'Ropa interior'}
BIG = ['4', '4-5', '5', '6', '6-6X', '6-7', '7', '8', '10', '12', '14', '14-16', '16']
BABY = ['PRE', 'NB', '3M', '6M', '9M', '12M', '18M', '24M']; TOD = ['2T', '3T', '4T', '5T']

TRAMOS = [(9, 10, 39900), (10, 12, 42900), (12, 13, 44900)]  # USD 9–9,99 → $39.900; 10–11,99 → $42.900; 12–12,99 → $44.900

def fmt(n): return '$' + f"{n:,}".replace(',', '.')
def precio(usd, cat, margen, fijo=None):
    if fijo: return int(fijo)
    P.MARGEN = margen
    p = P.precio(usd, a.cot, 3.5 if cat in ACC else None)
    p = 29900 if 30300 <= p <= 35000 else p
    for lo, hi, v in TRAMOS:          # precios por tramo de USD (5/11/2026); nunca suben un precio
        if lo <= usd < hi: p = min(p, v)
    return p

TT = '<button class="ttl" type="button" data-tt>¿Qué talle?</button>'
def card(r, marca):
    p = precio(float(r['usd']), r['cat'], 1.9 if marca == 'carters' else 1.7, r.get('fijo'))
    t = r['talles'].split('|')
    kind = lambda x: 'u' if x == 'Único' else ('g' if x in BIG else ('n' if x.endswith('T') else 'b'))
    G = [('b', 'Talles bebés', 'Bebés'), ('n', 'Talles niños', 'Niños'), ('g', 'Talles (años)', 'Grandes'), ('u', 'Talle', None)]
    groups = [(lb, [x for x in t if kind(x) == k], ed) for k, lb, ed in G if any(kind(x) == k for x in t)]
    eds = [ed for _, _, ed in groups if ed] or ['Bebés', 'Niños']
    ED_TXT = {'Bebés': 'Bebés', 'Niños': 'Niños', 'Grandes': 'Niños grandes'}
    nom = html.escape(r['nombre'], quote=True)
    if marca == 'carters':
        url = f'https://www.carters.com/p/x/V_{r["code"]}'; img = f'{IMG_C}{r["img"]}?sw=600'; tag = "Carter's"
    else:
        url = f'https://www.gapfactory.com/browse/product.do?pid={r["code"]}'; img = f'https://content.gapinc.com/b/00{r["img"]}?width=600'; tag = 'GAP Factory'
    def grp(xs): return ''.join(f'<button class="tl" data-t="{x}">{x}</button>' for x in xs)
    lbl = groups[0][0] + (TT if groups[0][2] else '')
    btns = grp(groups[0][1]) + ''.join(f'</div>\n<p class="lb">{lb}</p>\n<div class="tls">{grp(xs)}' for lb, xs, _ in groups[1:])
    art = (f'<article class="card" data-marca="{marca}" data-cat="{r["cat"]}" data-edad="{"|".join(eds)}" data-gen="{r["gen"]}" '
           f'data-talles="{r["talles"]}" data-code="{r["code"]}" data-nom="{nom}" data-precio="{p}">\n'
           f'<a class="ph" href="{url}" target="_blank" rel="noopener"><img loading="lazy" src="{img}" alt="{nom}" onerror="this.style.opacity=0"></a>\n'
           f'<div class="bd">\n<span class="tag">{tag} · {r["cat"]} · {" y ".join(ED_TXT[e] for e in eds)}</span>\n'
           f'<h3><a class="nm" href="{url}" target="_blank" rel="noopener">{nom}</a></h3>\n<div class="pr"><b>{fmt(p)}</b></div>\n'
           f'<p class="lb">{lbl}</p>\n<div class="tls">{btns}</div>\n<button class="add" disabled>Elegí un talle</button>\n</div></article>')
    return (CATS.index(r['cat']), p, 0 if marca == 'carters' else 1, art), set(t), set(eds)

items, talles, edades = [], set(), set()
for f, marca in (('carters_bf.tsv', 'carters'), ('carters_cl.tsv', 'carters'), ('gapfactory.tsv', 'gapfactory')):
    path = os.path.join(HERE, f)
    if not os.path.exists(path): continue
    for r in csv.DictReader(open(path, encoding='utf-8'), delimiter='\t'):
        it, t, e = card(r, marca); items.append(it); talles |= t; edades |= e
items.sort(key=lambda x: (x[0], x[1], x[2]))

s = open(IDX, encoding='utf-8').read()
g0 = s.index('<div class="grid" id="grid">') + len('<div class="grid" id="grid">'); g1 = s.index('</div><div class="empty" id="empty">')
s = s[:g0] + '\n' + '\n'.join(x[3] for x in items) + '\n' + s[g1:]

present = {CATS[x[0]] for x in items}
chip = lambda f, v, t=None: f'<button class="chip" data-f="{f}" data-v="{v}">{t or v}</button>'
s = re.sub(r'<div class="frow wrap"><em>Categoría</em>.*?</div>', '<div class="frow wrap"><em>Categoría</em>' + ''.join(chip('cat', c) for c in CATS if c in present) + '</div>', s, count=1)
marcas = [m for m, t in (('carters', "Carter's"), ('gapfactory', 'GAP Factory')) if any(f'data-marca="{m}"' in x[3] for x in items)]
s = re.sub(r'<div class="frow" id="fmarca">.*?</div>', '<div class="frow" id="fmarca"><em>Marca</em>' + ''.join(chip('marca', m, {'carters': "Carter's", 'gapfactory': 'GAP Factory'}[m]) for m in marcas) + '</div>', s, count=1)
ED = [('Bebés', 'Bebés (0 a 24 meses)'), ('Niños', 'Niños (2 a 5 años)'), ('Grandes', 'Niños grandes (4 a 16 años)')]
s = re.sub(r'<div class="frow"><em>Edad</em>.*?</div>', '<div class="frow"><em>Edad</em>' + ''.join(chip('edad', v, t) for v, t in ED if v in edades) + '</div>', s, count=1)
def fila(lbl, lista, extra=''):
    xs = [x for x in lista if x in talles]
    return f'<div class="frow"{extra}><em>{lbl}</em>' + ''.join(chip('talle', x) for x in xs) + '</div>' if xs else ''
s = re.sub(r'<div class="frow"><em>Talles bebés</em>.*?</div>', fila('Talles bebés', BABY), s, count=1)
s = re.sub(r'<div class="frow"><em>Talles niños</em>.*?</div>', fila('Talles niños', TOD), s, count=1)
s = re.sub(r'<div class="frow" id="ftg"><em>Talles grandes</em>.*?</div>', fila('Talles grandes', BIG, ' id="ftg"'), s, count=1)

s = re.sub(r'CIERRE=new Date\("[^"]+"\)', f'CIERRE=new Date("{a.cierre}")', s)
s = re.sub(r'<title>TOPP by WOWCYK — Pedido [^<]*</title>', f'<title>TOPP by WOWCYK — Pedido Noviembre 2026 — {a.titulo}</title>', s)
s = re.sub(r'<meta name="description" content="Pedido [^"]*">', f'<meta name="description" content="Pedido Noviembre 2026 — {a.titulo}. Reservá con seña.">', s)
open(IDX, 'w', encoding='utf-8').write(s)
n_c = sum(1 for x in items if x[2] == 0)
print(f'{len(items)} productos: {n_c} Carter\'s, {len(items) - n_c} GAP Factory; categorías: {sorted(present, key=CATS.index)}')
