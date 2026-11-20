#!/usr/bin/env python3
"""18/11 (Patricio): GAP Factory vuelve con "Black Friday Early" (40–70% off ya en el precio de la web) + 10% extra al pagar
(no aplica a licencias / ediciones especiales; termina el 22/11). Solo lo que queda hasta $39.900 con margen ×1,7:
remeras, shorts, bodies, pantalones/calzas, buzos, trajes de baño y enteritos; al menos 2 talles; sin packs de 3 bodies ni temáticos de fiestas.
Lee tools/gapfactory.tsv (workflow "Relevar GAP Factory" + gf_traducir.py) y escribe tools/gap_verano.tsv."""
import csv, os, re, sys, collections
T = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, T); import precio as P
def precio_gap(usd):
    P.MARGEN = 1.7; p = P.precio(usd, P.COT); p = 29900 if 30300 <= p <= 35000 else p
    for lo, hi, v in [(0, 10, 39900), (10, 12, 42900), (12, 13, 44900)]:
        if lo <= usd < hi: p = min(p, v)
    return p
CATS = {'Remeras', 'Shorts', 'Bodies', 'Pantalones', 'Buzos', 'Mallas', 'Enteritos'}
FIESTAS = re.compile(r'navid|christmas|halloween|hanukkah|acci[oó]n de gracias|thanksgiving|reno|santa', re.I)
LICENCIA = re.compile(r'disney|mickey|minnie|marvel|spider|frozen|barbie|pok[eé]mon|bluey|star wars|paw patrol|sesame|sonic|hello kitty|peppa|minecraft|harry potter|mario|looney|snoopy|peanuts|batman|superman|cocomelon', re.I)
rows = []
for r in csv.DictReader(open(os.path.join(T, 'gapfactory.tsv'), encoding='utf-8'), delimiter='\t'):
    if r['cat'] not in CATS or FIESTAS.search(r['nombre']) or re.search(r'pack (de )?3', r['nombre'], re.I): continue
    if len(r['talles'].split('|')) < 2: continue
    lista = float(r['usd']); costo = round(lista * (1.0 if LICENCIA.search(r['nombre']) else 0.9), 2)
    fijo = precio_gap(costo)
    if 29000 <= fijo < 29900: fijo = 29900
    if fijo > 39900: continue
    rows.append(dict(code=r['code'], cat=r['cat'], gen=r['gen'], nombre=r['nombre'], usd=f'{costo:.2f}', talles=r['talles'], img=r['img'], usd_lista=r['usd'], fijo=str(fijo)))
seen = collections.Counter()
for r in sorted(rows, key=lambda r: float(r['usd'])):
    b = re.sub(r' \(modelo \d+\)$', '', r['nombre']); seen[b] += 1
    r['nombre'] = b if seen[b] == 1 else f'{b} (modelo {seen[b]})'
w = csv.DictWriter(open(os.path.join(T, 'gap_verano.tsv'), 'w', encoding='utf-8', newline=''), fieldnames=['code', 'cat', 'gen', 'nombre', 'usd', 'talles', 'img', 'usd_lista', 'fijo'], delimiter='\t', lineterminator='\n')
w.writeheader(); w.writerows(rows)
print('GAP 18/11:', len(rows), dict(collections.Counter(r['cat'] for r in rows)), dict(collections.Counter(r['fijo'] for r in rows).most_common(6)))
