#!/usr/bin/env python3
"""24/11 19:49 (pedido abierto hasta el 25/11 22 hs). Patricio: "bajemos el precio de las remeras, que dejen de ganancia entre $12.000 y
$15.000, sobre todo las más económicas de GAP". Remeras de GAP Factory y H&M que hoy dejan más de $15.000: se bajan al mayor precio
terminado en .900 que deja entre $12.000 y $15.000. Costo puesto = USD pagado × 1,07 + 70 g × USD 26,5/kg + USD 0,85, × cotización.
Las que ya dejan $15.000 o menos no se tocan (nunca se sube un precio)."""
import csv, os, re, sys
T = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, T)
import precio as P
R = os.path.dirname(T)
html = open(os.path.join(R, 'index.html'), encoding='utf-8').read()
pub = {}
for a in re.findall(r'<article[^>]*>', html):
    d = dict(re.findall(r'data-([a-z]+)="([^"]*)"', a))
    if d.get('cat') == 'Remeras' and d.get('marca') in ('hm', 'gapfactory'): pub[d['code']] = int(d['precio'])
cambios = []
for f in ('gap_verano.tsv', 'hm_verano.tsv'):
    p = os.path.join(T, f); campos = open(p, encoding='utf-8').readline().rstrip('\n').split('\t')
    rows = list(csv.DictReader(open(p, encoding='utf-8'), delimiter='\t'))
    for r in rows:
        if r['code'] not in pub: continue
        precio = pub[r['code']]; costo = (float(r['usd']) * 1.07 + 0.07 * 26.5 + 0.85) * P.COT
        if precio - costo <= 15000: continue
        nuevo = (int((costo + 15000 + 100) // 1000)) * 1000 - 100      # mayor X.900 con ganancia <= 15.000
        if nuevo - costo > 15000: nuevo -= 1000
        if nuevo - costo < 12000 or nuevo >= precio: continue
        r['fijo'] = str(nuevo); cambios.append((f[:3], r['code'], r['nombre'], r['usd'], precio, nuevo, round(nuevo - costo)))
    w = csv.DictWriter(open(p, 'w', encoding='utf-8', newline=''), fieldnames=campos, delimiter='\t', lineterminator='\n', extrasaction='ignore', restval='')
    w.writeheader(); w.writerows(rows)
for c in cambios: print('\t'.join(map(str, c)))
print(len(cambios), 'remeras bajadas')
