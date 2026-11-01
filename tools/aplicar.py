#!/usr/bin/env python3
"""Aplica el resultado de revisar-talles.js sobre index.html.

Uso: python3 tools/aplicar.py resultado.json [--cot 1560 --margen 1.9 --flete 6.94 --flete-acc 3.5 --min-ganancia 8000]

- Saca de cada producto los talles que Carter's ya no tiene en stock.
- Saca los productos que se quedaron sin ningún talle.
- No cambia precios. Informa los productos cuyo precio en Carter's subió tanto
  que la ganancia estimada queda por debajo de --min-ganancia.
"""
import argparse, json, re, html as H

ap = argparse.ArgumentParser()
ap.add_argument('resultado'); ap.add_argument('--index', default='index.html')
ap.add_argument('--cot', type=float, default=1560); ap.add_argument('--flete', type=float, default=6.94)
ap.add_argument('--flete-acc', type=float, default=3.5); ap.add_argument('--min-ganancia', type=float, default=8000)
a = ap.parse_args()
ACC = {'Medias', 'Mantas', 'Mitones', 'Ropa interior', 'Hora del baño', 'Hora de comer'}

res = {r['code']: r for r in json.load(open(a.resultado)) if 'code' in r}
s = open(a.index, encoding='utf-8').read()
quitados, recortados, errores, ganancia_baja = [], [], [], []

def tocar(m):
    art = m.group(0)
    code = re.search(r'data-code="([^"]+)"', art).group(1)
    r = res.get(code)
    if not r: return art
    nom = H.unescape(re.search(r'data-nom="([^"]*)"', art).group(1))
    if r.get('err') or r.get('noLD'):
        errores.append(f'{nom} [{code}]'); return art
    if r['usd']:
        fl = a.flete_acc if r['cat'] in ACC else a.flete
        costo = (r['usd'] * 1.07 + fl) * a.cot
        if r['precio'] - costo < a.min_ganancia:
            ganancia_baja.append(f"{nom} [{code}]: precio ${r['precio']:,} – costo ${costo:,.0f} = ${r['precio']-costo:,.0f} (USD {r['usd']})".replace(',', '.'))
    if not r['still']:
        quitados.append(f'{nom} [{code}]'); return ''
    if not r['gone']: return art
    recortados.append(f"{nom} [{code}]: sin {', '.join(r['gone'])}")
    art = re.sub(r'data-talles="[^"]*"', 'data-talles="' + '|'.join(r['still']) + '"', art)
    for t in r['gone']:
        art = art.replace(f'<button class="tl" data-t="{t}">{t}</button>', '')
    art = re.sub(r'<p class="lb">(?:(?!</p>).)*</p>\n<div class="tls"></div>\n?', '', art)
    return art

s2 = re.sub(r'<article class="card"[\s\S]*?</article>\n?', tocar, s)
open(a.index, 'w', encoding='utf-8').write(s2)
print(json.dumps({'productos_quitados': quitados, 'talles_quitados': recortados,
                  'sin_datos': errores, 'ganancia_baja': ganancia_baja}, ensure_ascii=False, indent=1))
