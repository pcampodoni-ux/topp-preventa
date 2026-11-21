#!/usr/bin/env python3
"""21/11 (Patricio: "si están lindos los pijamas hagamos excepción"): pijamas GAP Factory de "Deals of the Week" (60% off PJs),
excepción al tope de $39.900 de GAP: entran a $42.900–44.900 (fórmula ×1,7 con tramos). Elegidos mirando las fotos:
solo pijamas completos (sin pantalones de pijama sueltos), sin licencias (Mickey, Minnie, Toy Story, Snoopy, Peanuts, Disney),
sin navideños (Cascanueces, Holiday Trellis) y sin el que brilla en la oscuridad; tope $44.900 (los de USD 14,97–18,99 quedaban en $58.990–69.690)."""
import csv, os, re, sys
T = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, T)
from gap_bf18_reglas import precio_gap
ELEGIDOS = '''436171001 529311001 529528001 803673001 817156001 828983001 1172741001 1172753001 1175063001 1175067001 1175072001 1175074001
1175077001 1178647001 1178648001 1178727001 1178739001 1178740001 1178741001 1178747001 1178755001 1178758001 1178760001 1178761001
1182671001 1182678001 1182686001 1182689001 1184047001 1184051001 1184059001 1184061001 1184070001 1185539001 1185547001 1185554001'''.split()
fn = os.path.join(T, 'gap_verano.tsv'); rows = list(csv.DictReader(open(fn, encoding='utf-8'), delimiter='\t'))
campos = open(fn, encoding='utf-8').readline().rstrip('\n').split('\t'); ya = {r['code'] for r in rows}
base = lambda n: re.sub(r' \(modelo \d+\)$', '', n)
usados = {}
for r in rows: usados[base(r['nombre'])] = usados.get(base(r['nombre']), 0) + 1
gf = {r['code']: r for r in csv.DictReader(open(os.path.join(T, 'gapfactory.tsv'), encoding='utf-8'), delimiter='\t')}
nuevos = []
for c in ELEGIDOS:
    if c in ya or c not in gf: continue
    r = gf[c]; costo = round(float(r['usd']) * 0.9, 2); f = precio_gap(costo); f = 29900 if 29000 <= f < 29900 else f
    if f > 44900: continue
    b = base(r['nombre']); usados[b] = usados.get(b, 0) + 1
    nom = b if usados[b] == 1 else f'{b} (modelo {usados[b]})'
    nuevos.append(dict(code=c, cat='Pijamas', gen=r['gen'], nombre=nom, usd=f'{costo:.2f}', talles=r['talles'], img=r['img'], usd_lista=r['usd'], fijo=str(f)))
w = csv.DictWriter(open(fn, 'w', encoding='utf-8', newline=''), fieldnames=campos, delimiter='\t', lineterminator='\n', extrasaction='ignore')
w.writeheader(); w.writerows(rows + nuevos)
print('Pijamas GAP sumados:', len(nuevos))
for r in nuevos: print(f"  ${int(r['fijo']):,} | USD {r['usd_lista']} | {r['nombre']} | {r['talles']}".replace(',', '.'))
