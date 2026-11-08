#!/usr/bin/env python3
"""Curaduría del pedido: solo categorías principales y, dentro de cada categoría y edad, los N más baratos (prioriza liquidación).
Uso: python3 tools/curar.py entrada.tsv salida.tsv N [raw.json]"""
import csv, sys, json, collections, re
ent, sal, N = sys.argv[1], sys.argv[2], int(sys.argv[3])
cl, en = set(), {}
if len(sys.argv) > 4:
    raw = json.load(open(sys.argv[4])); cl = {r['code'] for r in raw if r.get('cl')}; en = {r['code']: r['name'] for r in raw}
ROPA = {'Packs de Bodies', 'Sets 2 Piezas', 'Enteritos', 'Pijamas', 'Pijamas de Polar', 'Vestidos', 'Remeras', 'Buzos', 'Pantalones', 'Shorts'}
SKIP = {'Hora de Comer', 'Hora del Baño', 'Mochilas y Bolsos', 'Juguetes'}
BABY = {'PRE', 'NB', '3M', '6M', '9M', '12M', '18M', '24M'}
def edad(t):
    t = t.split('|')
    if any(x in BABY for x in t): return 'b'
    if any(x.endswith('T') for x in t): return 'n'
    return 'g'
rows = list(csv.DictReader(open(ent, encoding='utf-8'), delimiter='\t')); hdr = list(rows[0].keys())
grp = collections.defaultdict(list)
for r in rows:
    if r['cat'] in ROPA: grp[(r['cat'], edad(r['talles']))].append(r)
    elif r['cat'] in SKIP: grp[(r['cat'], 'u')].append(r)
out = []
for k, xs in grp.items():
    xs.sort(key=lambda r: (float(r['usd']), r['code'] not in cl))
    xs = [r for r in xs if not re.search(r'Sorbete', r['nombre'])]   # 7/11: sin vasos con sorbete
    xs = [r for r in xs if not (r['nombre'].startswith('Pack 2') and float(r['usd']) > 13)]   # 8/11: packs de 2 que saldrían más caros que un pack de 5
    out += xs[: (max(4, N // 3) if k[1] == 'u' else (999 if k[0] == 'Packs de Bodies' else (N * 2 if k[0] in ('Bodies', 'Remeras', 'Sets 2 Piezas') else N)))]
# 7/11: todas las remeras de manga corta (y musculosas), sin tope
ya = {r['code'] for r in out}
def manga_corta(r):
    n = en.get(r['code'], '') + ' ' + r['nombre']
    return not re.search(r'Long[- ]Sleeve|Turtleneck|Manga Larga|Polera', n, re.I)
out += [r for r in rows if r['cat'] == 'Remeras' and r['code'] not in ya and manga_corta(r)]
seen = collections.Counter()
for r in sorted(out, key=lambda r: float(r['usd'])):
    b = re.sub(r' \(modelo \d+\)$', '', r['nombre']); seen[b] += 1
    r['nombre'] = b if seen[b] == 1 else f'{b} (modelo {seen[b]})'
w = csv.DictWriter(open(sal, 'w', encoding='utf-8', newline=''), fieldnames=hdr, delimiter='\t', lineterminator='\n'); w.writeheader(); w.writerows(out)
c = collections.Counter(r['cat'] for r in out)
print(len(out), 'productos; liquidación:', sum(r['code'] in cl for r in out), dict(c))
