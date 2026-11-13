#!/usr/bin/env python3
"""Pedido "verano hasta USD 17" (13/11/2026): Carter's/OshKosh, H&M y GAP Factory.

Criterio de Patricio: todo lo de verano, en oferta, hasta USD 17, lo más atractivo por precio.
Toma los TSV completos de cada marca y deja, por marca, categoría y edad, los N más baratos.
  - Categorías de verano: remeras, shorts, vestidos, sets, enteritos, packs de bodies y mallas
    (sin bodies sueltos, sin manga larga, sin abrigo ni prendas de fiestas de invierno).
  - H&M: como mucho 3 colores por modelo (los de más talles disponibles) para no repetir.
Uso: python3 tools/verano.py [N_carters] [N_gap] [N_hm]
Salida: tools/carters_verano.tsv, tools/gap_verano.tsv, tools/hm_verano.tsv
"""
import csv, os, re, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
NC, NG, NH = (int(x) for x in (sys.argv[1:4] + ['15', '10', '15'][len(sys.argv[1:4]):]))
MAX = 17
VERANO = {'Remeras', 'Shorts', 'Vestidos', 'Sets 2 Piezas', 'Enteritos', 'Packs de Bodies', 'Mallas'}
FUERA = re.compile(r'Manga Larga|Polar|Frisad|Abrigo|Campera|Buzo|Navidad|Navideñ|Halloween|Acción de Gracias|Papá Noel|Reno\b|Janucá|Hanukkah|Pijama|Corderoy|Térmic|Escoc|Frisa|Candy ?cane|Candycane|Plaid|Tart[aá]n|Gingerbread|Jengibre|Navide|Holiday|Santa|Snow|Nieve', re.I)
BABY = {'PRE', 'NB', '3M', '6M', '9M', '12M', '18M', '24M'}

def edad(r):
    if r.get('edad'): return r['edad'].split('|')[0]
    t = r['talles'].split('|')
    if any(x in BABY or x.endswith('M') for x in t): return 'Bebés'
    if any(x.endswith('T') for x in t): return 'Niños'
    return 'Grandes'

def leer(f):
    p = os.path.join(HERE, f)
    return list(csv.DictReader(open(p, encoding='utf-8'), delimiter='\t')) if os.path.exists(p) else []

def curar(rows, n, nombre_salida, por_modelo=None):
    ok = [r for r in rows if r['cat'] in VERANO and float(r['usd']) <= MAX and not FUERA.search(r['nombre'])]
    if por_modelo:   # H&M: hasta 3 colores por modelo, los de más talles
        g = collections.defaultdict(list)
        for r in ok: g[r['code'][:7]].append(r)
        ok = [x for xs in g.values() for x in sorted(xs, key=lambda r: (-len(r['talles'].split('|')), float(r['usd'])))[:por_modelo]]
    grupos = collections.defaultdict(list)
    for r in ok: grupos[(r.get('marca', ''), r['cat'], edad(r))].append(r)
    out = []
    for k, xs in grupos.items():
        xs.sort(key=lambda r: (float(r['usd']), -len(r['talles'].split('|'))))
        out += xs[: (999 if k[1] == 'Packs de Bodies' else n)]
    if not out: print(nombre_salida, 'sin productos'); return
    seen = collections.Counter()   # renumera los "(modelo N)" para que arranquen de 2 dentro de lo elegido
    for r in sorted(out, key=lambda r: float(r['usd'])):
        b = re.sub(r' \(modelo \d+\)$', '', r['nombre']); seen[b] += 1
        r['nombre'] = b if seen[b] == 1 else f'{b} (modelo {seen[b]})'
    cols = list(rows[0].keys())
    w = csv.DictWriter(open(os.path.join(HERE, nombre_salida), 'w', encoding='utf-8', newline=''), fieldnames=cols, delimiter='\t', lineterminator='\n')
    w.writeheader(); w.writerows(out)
    print(nombre_salida, len(out), dict(collections.Counter(r['cat'] for r in out)))

curar(leer('carters_full_all.tsv'), NC, 'carters_verano.tsv')
curar(leer('gapfactory_all.tsv'), NG, 'gap_verano.tsv')
curar(leer('hm.tsv'), NH, 'hm_verano.tsv', por_modelo=3)
