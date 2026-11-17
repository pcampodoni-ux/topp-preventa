#!/usr/bin/env python3
"""Crea tools/revision/esperado.json: el stock y precio de referencia de cada producto publicado (17/11, relevamiento del día).
Lo usan preparar.py (para que el navegador devuelva solo lo que cambió) y revisar.py (que lo actualiza después de cada revisión)."""
import csv, json, os, sys
T = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
def leer(f): return list(csv.DictReader(open(os.path.join(T, f), encoding='utf-8'), delimiter='\t'))
raw = {x['code']: x for x in json.load(open(os.path.join(T, 'carters_full_raw.json')))}
hr = json.load(open(sys.argv[1]))['hr']   # hm_17nov.json bajado del navegador
E = {'carters': {}, 'hm': {}}
for r in leer('carters_verano.tsv'):
    x = raw.get(r['code'])
    if not x: continue
    st = [v for v in x['vs'] if v['st']]
    E['carters'][r['code']] = {'s': [v['s'] for v in st], 'p': max(v.get('p0', v['p']) for v in st), 'x': bool(x.get('x30'))}
for r in leer('hm_verano.tsv'):
    x = hr.get(r['code'])
    if not x or x.get('gone'): continue
    E['hm'][r['code']] = {'s': [s for s, ok in x['sizes'] if ok], 'u': min(p for p in (x['w'], x['red']) if p)}
json.dump(E, open(os.path.join(T, 'revision', 'esperado.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
print({k: len(v) for k, v in E.items()})
