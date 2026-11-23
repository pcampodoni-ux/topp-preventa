#!/usr/bin/env python3
"""23/11 (Patricio reabre el pedido hasta las 22 hs): GAP Factory hoy tiene "Black Friday 50–70% Off Everything + Extra 10% Off"
(al pagar, sin código; excluye licencias y ediciones especiales) y la liquidación sigue con "Extra 50% off" al pagar.
Flags de la API leídos hoy desde el navegador → tools/gap_flags_23nov.json (c50 = 50% extra, ex = excluidos de promociones).
Suma lo que no estaba publicado con las reglas de siempre: costo = web × 0,5 (50% extra) / × 0,9 (10%) / × 1 (excluidos y licencias),
×1,7 con tramos, hasta $39.900, al menos 2 talles, sin fiestas, sin packs de bodies ni accesorios."""
import csv, json, os, re, sys, collections
T = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, T)
from gap_bf18_reglas import precio_gap, LICENCIA
F = json.load(open(os.path.join(T, 'gap_flags_23nov.json'))); C50 = set(F['c50']); EX = set(F['ex'])
FIESTAS = re.compile(r'navid|christmas|holiday|candy cane|halloween|hanukkah|acci[oó]n de gracias|thanksgiving|reno|santa', re.I)
LIMPIAR = [(r'Stamp Print Flowers', 'Estampado Flores'), (r'Light Wash', 'Claro'), (r'Medium Wash', 'Azul Medio'), (r'Dark Wash', 'Oscuro'),
           (r'Moonstone', 'Gris Claro'), (r'Rain Forest', 'Verde Selva'), (r'\bVerde Verde\b', 'Verde')]
f = os.path.join(T, 'gap_verano.tsv'); campos = open(f, encoding='utf-8').readline().rstrip('\n').split('\t')
base = list(csv.DictReader(open(f, encoding='utf-8'), delimiter='\t')); pub = {r['code'] for r in base}
noms = collections.Counter(re.sub(r' \(modelo \d+\)$', '', r['nombre']) for r in base)
extra = []
for r in csv.DictReader(open(os.path.join(T, 'gapfactory.tsv'), encoding='utf-8'), delimiter='\t'):
    c = r['code']
    if c in pub or len(r['talles'].split('|')) < 2 or FIESTAS.search(r['nombre']) or r['cat'] in ('Accesorios', 'Medias', 'Packs de Bodies'): continue
    u = float(r['usd'])
    if c in C50: costo, d = round(u * 0.5, 2), '50'
    elif c in EX or LICENCIA.search(r['nombre']): costo, d = u, ''
    else: costo, d = round(u * 0.9, 2), ''
    p = precio_gap(costo); p = 29900 if 29000 <= p < 29900 else p
    if p > 39900: continue
    extra.append(dict(r, usd=f'{costo:.2f}', usd_lista=r['usd'], fijo=str(p), desc=d))
for r in extra:
    n = r['nombre']
    for a, b in LIMPIAR: n = re.sub(a, b, n)
    b = re.sub(r' \(modelo \d+\)$', '', n); noms[b] += 1
    r['nombre'] = b if noms[b] == 1 else f'{b} (modelo {noms[b]})'
w = csv.DictWriter(open(f, 'w', encoding='utf-8', newline=''), fieldnames=campos, delimiter='\t', lineterminator='\n', extrasaction='ignore', restval='')
w.writeheader(); w.writerows(base + extra)
print('GAP 23/11:', len(extra), dict(collections.Counter(r['cat'] for r in extra)))
for r in extra: print(' ', r['cat'], '|', r['nombre'], '|', r['usd'], '|', r['fijo'], '|', r['talles'])
