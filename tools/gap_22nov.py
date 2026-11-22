#!/usr/bin/env python3
"""22/11 (Patricio: "veamos todo GAP y H&M y agreguemos lo que podamos"; el pedido cierra hoy 22 hs).
GAP Factory hoy: "Extra 50% Off Clearance" aplicado al pagar (además del Black Friday Early 40–70% y del GFCARD 10%, que vence hoy).
La API de GAP marca cada producto con "Extra 50% off. Applied at checkout" o "Excluded from promotions"
(leído hoy desde el navegador → tools/gap_flags_22nov.json: c50 = con 50% extra, ex = excluidos).
- Suma lo de liquidación con 50% extra que no estaba publicado: costo = precio de la web × 0,5 (se asume que el 10% NO se suma al 50%),
  ×1,7 con tramos, hasta $39.900, al menos 2 talles, sin temáticos de fiestas, sin packs de bodies ni accesorios. Columna desc=50 para que
  revision/revisar.py calcule el costo con el 50%.
- Vuelven los trajes de baño de GAP que salieron por error en la reapertura del 21/11 (el tope de $39.900 los dejó afuera) y siguen con
  2+ talles: al precio con que estaban publicados el 20/11.
Lee tools/gapfactory.tsv (relevamiento de hoy, GAP_MAX=60) y agrega a tools/gap_verano.tsv."""
import csv, json, os, re, sys, collections
T = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, T)
from gap_bf18_reglas import precio_gap
F = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(T, 'gap_flags_22nov.json'))); C50 = set(F['c50'])
FIESTAS = re.compile(r'navid|christmas|halloween|hanukkah|acci[oó]n de gracias|thanksgiving|reno|santa', re.I)
MALLAS_20NOV = {'1172536001': '42900', '1172543001': '47900', '1172543011': '47900', '1172330001': '52900', '1172334001': '52900', '1175031001': '57590'}
LIMPIAR = [(r'Stamp Print Flowers', 'Estampado Flores'), (r'Light Wash', 'Claro'), (r'Medium Wash', 'Azul Medio'), (r'Moonstone', 'Gris Claro'),
           (r'Rain Forest', 'Verde Selva'), (r'\bVerde Verde\b', 'Verde')]
f = os.path.join(T, 'gap_verano.tsv'); campos = open(f, encoding='utf-8').readline().rstrip('\n').split('\t')
if 'desc' not in campos: campos.append('desc')
base = list(csv.DictReader(open(f, encoding='utf-8'), delimiter='\t')); pub = {r['code'] for r in base}
noms = collections.Counter(re.sub(r' \(modelo \d+\)$', '', r['nombre']) for r in base)
for r in base:
    if r['code'] in ('1172722001', '1172722011'): r['nombre'] = r['nombre'].replace('GAP · Malla ', 'GAP · Gorro de Sol para el Agua ')
import subprocess
VIEJO = {}   # filas de los trajes de baño tal como estaban publicados el 20/11 (nombre, categoría, foto)
_t = subprocess.run(['git', 'show', 'fd69f31:tools/gap_verano.tsv'], capture_output=True, text=True, cwd=T).stdout.splitlines()
for _l in _t[1:]:
    _d = dict(zip(_t[0].split('\t'), _l.split('\t')))
    if _d['code'] in MALLAS_20NOV: VIEJO[_d['code']] = _d
extra = []
for r in csv.DictReader(open(os.path.join(T, 'gapfactory.tsv'), encoding='utf-8'), delimiter='\t'):
    c = r['code']
    if c in pub or len(r['talles'].split('|')) < 2: continue
    if c in MALLAS_20NOV:
        u = float(r['usd']); costo = u if c in F['ex'] else round(u * (0.5 if c in C50 else 0.9), 2)
        v = VIEJO.get(c, r)
        extra.append(dict(r, cat=v['cat'], nombre=v['nombre'], gen=v['gen'], usd=f'{costo:.2f}', usd_lista=r['usd'], fijo=MALLAS_20NOV[c], desc='50' if c in C50 else '')); continue
    if c not in C50 or FIESTAS.search(r['nombre']) or r['cat'] in ('Accesorios', 'Medias', 'Packs de Bodies'): continue
    costo = round(float(r['usd']) * 0.5, 2); p = precio_gap(costo); p = 29900 if 29000 <= p < 29900 else p
    if p > 39900: continue
    extra.append(dict(r, usd=f'{costo:.2f}', usd_lista=r['usd'], fijo=str(p), desc='50'))
for r in extra:
    n = r['nombre']
    for a, b in LIMPIAR: n = re.sub(a, b, n)
    b = re.sub(r' \(modelo \d+\)$', '', n); noms[b] += 1
    r['nombre'] = b if noms[b] == 1 else f'{b} (modelo {noms[b]})'
w = csv.DictWriter(open(f, 'w', encoding='utf-8', newline=''), fieldnames=campos, delimiter='\t', lineterminator='\n', extrasaction='ignore', restval='')
w.writeheader(); w.writerows(base + extra)
print('GAP 22/11:', len(extra), dict(collections.Counter(r['cat'] for r in extra)))
for r in extra: print(' ', r['cat'], '|', r['nombre'], '|', r['usd'], '|', r['fijo'], '|', r['talles'])
