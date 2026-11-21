#!/usr/bin/env python3
"""21/11/2026: cotización $1.625 (dólar de referencia de Ualá, Patricio). Antes $1.588.
Recalcula los precios que salen de la fórmula y que están guardados como 'fijo' (GAP Factory y los 37 de invierno de H&M del 20/11);
los que no tienen fijo los recalcula armar_pedido.py solo. Regla: con el pedido reabierto no baja ningún precio publicado
(si la fórmula da menos, queda el precio anterior)."""
import csv, os, re, sys, subprocess
T = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, T)
import precio as P
from gap_bf18_reglas import precio_gap
VIEJA = 1588
def leer(f): return list(csv.DictReader(open(os.path.join(T, f), encoding='utf-8'), delimiter='\t'))
def escribir(f, rows):
    campos = open(os.path.join(T, f), encoding='utf-8').readline().rstrip('\n').split('\t')
    w = csv.DictWriter(open(os.path.join(T, f), 'w', encoding='utf-8', newline=''), fieldnames=campos, delimiter='\t', lineterminator='\n', extrasaction='ignore')
    w.writeheader(); w.writerows(rows)
def con_cot(cot, fn, *a):
    old = P.COT; P.COT = cot
    try: return fn(*a)
    finally: P.COT = old
def gap(usd): p = precio_gap(usd); return 29900 if 29000 <= p < 29900 else p
IDX = os.path.join(T, '..', 'index.html')
def precios(): return {m.group(1): int(m.group(2)) for m in re.finditer(r'data-code="([^"]+)" data-nom="[^"]*" data-precio="(\d+)"', open(IDX, encoding='utf-8').read())}
antes = precios()
# GAP: solo los fijos que coinciden con la fórmula a la cotización vieja
g = leer('gap_verano.tsv'); n = 0
for r in g:
    if r.get('fijo') and int(r['fijo']) == con_cot(VIEJA, gap, float(r['usd'])):
        nuevo = gap(float(r['usd']))
        if nuevo > int(r['fijo']): r['fijo'] = str(nuevo); n += 1
escribir('gap_verano.tsv', g); print('GAP suben:', n)
# H&M invierno 20/11 (fórmula con flete por peso)
import importlib.util
src = open(os.path.join(T, 'hm_invierno_20nov.py'), encoding='utf-8').read()
D = eval(src[src.index('D = [') + 4: src.index(']\nTRAMOS') + 1])
TR = [(0, 10, 39900), (10, 12, 42900), (12, 13, 44900)]
def hmp(usd, cat, gr):
    fl = 3.5 if cat == 'Accesorios' else gr / 1000 * 26.5 + 0.85
    p = P.precio(usd, P.COT, fl); p = 29900 if 30300 <= p <= 35000 else p
    for lo, hi, v in TR:
        if lo <= usd < hi: p = min(p, v)
    return p
W = {d[0]: d for d in D}; h = leer('hm_verano.tsv'); n = 0
for r in h:
    d = W.get(r['code'])
    if d and r.get('fijo'):
        nuevo = hmp(float(r['usd']), d[1], d[4])
        if nuevo > int(r['fijo']): r['fijo'] = str(nuevo); n += 1
escribir('hm_verano.tsv', h); print('H&M invierno suben:', n)
cierre = re.search(r'CIERRE=new Date\("([^"]+)"\)', open(IDX, encoding='utf-8').read()).group(1)
arm = [sys.executable, os.path.join(T, 'armar_pedido.py'), '--cierre', cierre, '--tsv', 'carters_verano.tsv:carters,hm_verano.tsv:hm,gap_verano.tsv:gapfactory']
subprocess.run(arm, check=True, capture_output=True)
# congelar lo que bajaría (redondeos 090–490 → 990)
despues = precios(); baja = {c: antes[c] for c, p in despues.items() if c in antes and p < antes[c]}
for f in ('carters_verano.tsv', 'hm_verano.tsv', 'gap_verano.tsv'):
    rows = leer(f); ch = False
    for r in rows:
        if r['code'] in baja: r['fijo'] = str(baja[r['code']]); ch = True
    if ch: escribir(f, rows)
if baja: subprocess.run(arm, check=True, capture_output=True)
despues = precios(); sub = [(c, antes[c], p) for c, p in despues.items() if c in antes and p > antes[c]]
print(f'Suben {len(sub)} de {len(despues)} (promedio +${sum(b - a for _, a, b in sub) // max(1, len(sub)):,}); congelados por no bajar: {len(baja)}'.replace(',', '.'))
