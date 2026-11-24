#!/usr/bin/env python3
"""24/11: sets de GAP Factory hasta $69.000 (pedido de Patricio: "sets y conjuntos atractivos"). Los 3 tienen el 50% extra de la liquidación
(marcados en gap_flags_23nov.json): costo = web × 0,5, ×1,7 con tramos. Se dejó afuera 1172702051 (sin marca del 50%: saldría $64.990
al lado de sus otros colores a $39.900)."""
import csv, os, sys
T = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, T)
from gap_bf18_reglas import precio_gap
NOM = {'1173185001': 'GAP · Malla 2 Piezas Estampada Floral', '1174721001': 'GAP · Set Malla Remera UV y Short Azul Estrellas',
       '1174911001': 'GAP · Set 2 Piezas Osito Brannan Azul'}
f = os.path.join(T, 'gap_verano.tsv'); campos = open(f, encoding='utf-8').readline().rstrip('\n').split('\t')
base = list(csv.DictReader(open(f, encoding='utf-8'), delimiter='\t')); pub = {r['code'] for r in base}
extra = []
for r in csv.DictReader(open(os.path.join(T, 'gapfactory.tsv'), encoding='utf-8'), delimiter='\t'):
    if r['code'] in NOM and r['code'] not in pub:
        costo = round(float(r['usd']) * 0.5, 2)
        cat = 'Mallas' if 'Malla' in NOM[r['code']] else 'Sets 2 Piezas'
        extra.append(dict(r, cat=cat, nombre=NOM[r['code']], usd=f'{costo:.2f}', usd_lista=r['usd'], fijo=str(precio_gap(costo)), desc='50'))
w = csv.DictWriter(open(f, 'w', encoding='utf-8', newline=''), fieldnames=campos, delimiter='\t', lineterminator='\n', extrasaction='ignore', restval='')
w.writeheader(); w.writerows(base + extra)
for r in extra: print(r['code'], r['cat'], r['nombre'], r['usd'], r['fijo'], r['talles'])
