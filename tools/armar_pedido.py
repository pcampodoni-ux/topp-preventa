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
ap.add_argument('--cierre', required=True); ap.add_argument('--titulo', default='Black Friday'); ap.add_argument('--cot', type=float, default=1560); ap.add_argument('--tsv', default='zapatillas.tsv:carters,hm.tsv:hm')
a = ap.parse_args()
HERE = os.path.dirname(os.path.abspath(__file__)); IDX = os.path.join(HERE, '..', 'index.html')
IMG_C = 'https://dw.cartersstorefront.com/dw/image/v2/AAMK_PRD/on/demandware.static/-/Sites-carters_master_catalog/default/'
CATS = ["Zapatillas", "Sandalias", "Jardineros", "Packs de Bodies", "Bodies", "Sets 2 Piezas", "Enteritos", "Pijamas", "Pijamas de Polar", "Vestidos", "Remeras", "Buzos", "Camperas",
        "Pantalones", "Shorts", "Mallas", "Medias", "Ropa interior", "Accesorios", "Hora del Baño", "Hora de Comer", "Juguetes", "Mochilas y Bolsos"]
ACC = {'Medias', 'Accesorios', 'Ropa interior', 'Hora del Baño', 'Hora de Comer'}
BIG = ['4', '4-5', '5', '6', '6-6X', '6-7', '7', '8', '10', '10-12', '12', '14', '14-16', '16']
MARCAS = {'carters': "Carter's", 'oshkosh': "OshKosh B'gosh", 'skiphop': 'Skip Hop', 'gapfactory': 'GAP Factory', 'hm': 'H&M'}
ORDEN_GRUPOS = 'zcohgs'   # pestañas: Zapatillas, Carter's, OshKosh, H&M, GAP, Skip Hop
BABY = ['PRE', 'NB', '3M', '6M', '9M', '12M', '18M', '24M']; TOD = ['2T', '3T', '4T', '5T']

TRAMOS = [(0, 10, 39900), (10, 12, 42900), (12, 13, 44900)]  # tope $39.900 hasta USD 9,99; 10–11,99 → $42.900; 12–12,99 → $44.900

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
    marca = r.get('marca') or marca
    p = precio(float(r['usd']), r['cat'], 1.7 if marca == 'gapfactory' else 1.9, r.get('fijo'))
    t = r['talles'].split('|')
    kind = lambda x: 'z' if x.startswith('US ') else ('y' if x.endswith(' años') else ('u' if x == 'Único' else ('g' if x in BIG else ('n' if x.endswith('T') else 'b'))))
    G = [('b', 'Talles bebés', 'Bebés'), ('n', 'Talles niños', 'Niños'), ('g', 'Talles (años)', 'Grandes'), ('y', 'Talles (edad)', None), ('z', 'Talle de calzado (EE.UU.)', None), ('u', 'Talle', None)]
    if marca == 'hm': G = [(k, l, None) for k, l, _ in G]   # sin tabla de talles para H&M
    groups = [(lb, [x for x in t if kind(x) == k], ed) for k, lb, ed in G if any(kind(x) == k for x in t)]
    eds = r['edad'].split('|') if r.get('edad') else ([ed for _, _, ed in groups if ed] or ['Bebés', 'Niños'])
    ED_TXT = {'Bebés': 'Bebés', 'Niños': 'Niños', 'Grandes': 'Niños grandes'}
    nom = html.escape(r['nombre'], quote=True)
    if marca == 'hm':
        url = 'https://www2.hm.com' + r['pdp']; img = r['img'] + ('&' if '?' in r['img'] else '?') + 'imwidth=600'
    elif marca != 'gapfactory':
        url = f'https://www.carters.com/p/x/V_{r["code"]}'
        im = r['img'].split('on/demandware.static/')[-1] if r['img'].startswith('http') else None
        img = (f'https://dw.cartersstorefront.com/dw/image/v2/AAMK_PRD/on/demandware.static/{im}?sw=600' if im else f'{IMG_C}{r["img"]}?sw=600')
    else:
        url = f'https://www.gapfactory.com/browse/product.do?pid={r["code"]}'; img = f'https://content.gapinc.com/b/00{r["img"]}?width=600'
    tag = MARCAS[marca]; grupo = r.get('grupo') or {'carters': 'c', 'oshkosh': 'o', 'skiphop': 's', 'gapfactory': 'g', 'hm': 'h'}[marca]
    def grp(xs): return ''.join(f'<button class="tl" data-t="{x}">{x}</button>' for x in xs)
    lbl = groups[0][0] + (TT if (groups[0][2] or grupo == 'z') else '')
    btns = grp(groups[0][1]) + ''.join(f'</div>\n<p class="lb">{lb}</p>\n<div class="tls">{grp(xs)}' for lb, xs, _ in groups[1:])
    art = (f'<article class="card" data-grupo="{grupo}" data-marca="{marca}" data-cat="{r["cat"]}" data-edad="{"|".join(eds)}" data-gen="{r["gen"]}" '
           f'data-talles="{r["talles"]}" data-code="{r["code"]}" data-nom="{nom}" data-precio="{p}">\n'
           f'<a class="ph" href="{url}" target="_blank" rel="noopener"><img loading="lazy" src="{img}" alt="{nom}" onerror="this.style.opacity=0"></a>\n'
           f'<div class="bd">\n<span class="tag">{tag} · {r["cat"]} · {" y ".join(ED_TXT[e] for e in eds)}</span>\n'
           f'<h3><a class="nm" href="{url}" target="_blank" rel="noopener">{nom}</a></h3>\n<div class="pr"><b>{fmt(p)}</b></div>\n'
           f'<p class="lb">{lbl}</p>\n<div class="tls">{btns}</div>\n<button class="add" disabled>Elegí un talle</button>\n</div></article>')
    nm = r['nombre']
    if grupo == 'z': pri = 0 if float(r['usd']) == 12 else 1   # 12/11: primero la promo de zapatillas a USD 12
    elif r['cat'] in ('Pijamas', 'Pijamas de Polar'): pri = -1   # 14/11: primero los pijamas, del más barato al más caro
    elif r['cat'] == 'Jardineros': pri = 1 if 'Corderoy' in nm else 0   # 9/11: primero jardineros (jean/chambray antes que corderoy)
    elif r['cat'] != 'Packs de Bodies': pri = 3
    elif nm.startswith('Pack 5') and not re.search(r'Manga Larga|Musculosa', nm): pri = 0   # 8/11: primero packs de 5 manga corta
    elif nm.startswith('Pack 4') and 'Manga Larga' in nm: pri = 1                          # después packs de 4 manga larga
    else: pri = 2
    return (ORDEN_GRUPOS.index(grupo), pri, p, CATS.index(r['cat']), art), set(t), set(eds)

items, talles, edades = [], set(), set()
for f, marca in (x.split(':') for x in a.tsv.split(',')):
    path = os.path.join(HERE, f)
    if not os.path.exists(path): continue
    for r in csv.DictReader(open(path, encoding='utf-8'), delimiter='\t'):
        it, t, e = card(r, marca); items.append(it); talles |= t; edades |= e
items.sort(key=lambda x: (x[0], x[1], x[2], x[3]))

s = open(IDX, encoding='utf-8').read()
g0 = s.index('<div class="grid" id="grid">') + len('<div class="grid" id="grid">'); g1 = s.index('</div><div class="empty" id="empty">')
s = s[:g0] + '\n' + '\n'.join(x[4] for x in items) + '\n' + s[g1:]

present = {CATS[x[3]] for x in items}
chip = lambda f, v, t=None: f'<button class="chip" data-f="{f}" data-v="{v}">{t or v}</button>'
s = re.sub(r'<div class="frow wrap"><em>Categoría</em>.*?</div>', '<div class="frow wrap"><em>Categoría</em>' + ''.join(chip('cat', c) for c in CATS if c in present) + '</div>', s, count=1)
marcas = [m for m in ('carters', 'oshkosh', 'skiphop') if any(f'data-marca="{m}"' in x[4] for x in items)]
s = re.sub(r'<div class="frow" id="fmarca">.*?</div>', '<div class="frow" id="fmarca"><em>Marca</em>' + ''.join(chip('marca', m, MARCAS[m]) for m in marcas) + '</div>', s, count=1)
nc = sum(1 for x in items if x[0] == 0); ng = len(items) - nc
pf = lambda n: f'{n:,}'.replace(',', '.') + ' productos'
s = re.sub(r'(data-g="c">[^<]*<small>)[^<]*(</small>)', lambda m: m.group(1) + pf(nc) + m.group(2), s, count=1)
s = re.sub(r'(data-g="g">[^<]*<small>)[^<]*(</small>)', lambda m: m.group(1) + pf(ng) + m.group(2), s, count=1)
ED = [('Bebés', 'Bebés (0 a 24 meses)'), ('Niños', 'Niños (2 a 5 años)'), ('Grandes', 'Niños grandes (4 a 16 años)')]
s = re.sub(r'<div class="frow"><em>Edad</em>.*?</div>', '<div class="frow"><em>Edad</em>' + ''.join(chip('edad', v, t) for v, t in ED if v in edades) + '</div>', s, count=1)
def fila(lbl, lista, extra=''):
    xs = [x for x in lista if x in talles]
    return f'<div class="frow"{extra}><em>{lbl}</em>' + ''.join(chip('talle', x) for x in xs) + '</div>' if xs else ''
s = re.sub(r'<div class="frow"(?: id="ftg")?><em>Talles (?:bebés|niños|grandes)</em>.*?</div>', '', s)
gi = s.index('<div class="frow"><em>Género</em>'); gi = s.index('</div>', gi) + len('</div>')
s = s[:gi] + fila('Talles bebés', BABY) + fila('Talles niños', TOD) + fila('Talles grandes', BIG, ' id="ftg"') + s[gi:]
# pestañas: una por grupo presente, en ORDEN_GRUPOS; la primera queda activa
NOMBRE_TAB = {'z': "Carter's Zapatillas", 'h': 'H&amp;M', 'c': "Carter's", 'o': 'OshKosh', 's': 'Skip Hop', 'g': 'GAP Factory'}
grupos = [g for g in ORDEN_GRUPOS if any(f'data-grupo="{g}"' in x[4] for x in items)]
tabs = ''.join(f'<button type="button" class="gt{" on" if i == 0 else ""}" data-g="{g}">{NOMBRE_TAB[g]}</button>' for i, g in enumerate(grupos))
s = re.sub(r'<div class="gtabs" id="gtabs"[^>]*>.*?</div>', f'<div class="gtabs" id="gtabs" style="grid-template-columns:repeat({len(grupos)},1fr)">{tabs}</div>', s, count=1, flags=re.S)
s = re.sub(r"(var F=\{[^}]*grupo:')[a-z](')", lambda m: m.group(1) + grupos[0] + m.group(2), s, count=1)

s = re.sub(r'CIERRE=new Date\("[^"]+"\)', f'CIERRE=new Date("{a.cierre}")', s)
s = re.sub(r'<title>[^<]*</title>', '<title>TOPP by WOWCYK</title>', s, count=1)   # 9/11: el título no lleva nada más (vista previa de WhatsApp)
s = re.sub(r'<meta name="description" content="[^"]*">\n?', '', s, count=1)
open(IDX, 'w', encoding='utf-8').write(s)
import collections
print(len(items), 'productos;', dict(collections.Counter(re.search(r'data-marca="(\w+)"', x[4]).group(1) for x in items)), sorted(present, key=CATS.index))
