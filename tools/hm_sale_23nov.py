#!/usr/bin/env python3
"""23/11: liquidación de H&M de hoy (Black Friday, hasta 50% off). De ~750 productos en sale, solo 1 nuevo con 2+ talles
que no es de Halloween. Mismo criterio y precio que hm_sale_22nov.py; agrega a tools/hm_verano.tsv y a tools/revision/esperado.json."""
import csv, json, os, re, sys
T = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, T)
import precio as P

# code, categoría, género, nombre, peso_g, USD (liquidación), talles con stock, imagen
D = [
 ('1336102001', 'Remeras', 'Nene', 'Pack 2 Remeras Henley de Algodón Beige y Azul Marino', 160, 9.99, '1-2M|2-3Y', '96/46/9646e7bfd90a982f50a1c547f6560cc4dffd7a15.jpg'),
]
TRAMOS = [(0, 10, 39900), (10, 12, 42900), (12, 13, 44900)]
def precio(usd, cat, g):
    fl = 3.5 if cat == 'Accesorios' else g / 1000 * 26.5 + 0.85
    p = P.precio(usd, P.COT, fl)
    p = 29900 if 30300 <= p <= 35000 else p
    for lo, hi, v in TRAMOS:
        if lo <= usd < hi: p = min(p, v)
    return p
def talle(s): s = s.replace('Y+', 'Y'); return s[:-1] + ' años' if s.endswith('Y') else s
def edad_t(t):
    if t.endswith('M'): return 'Bebés'
    a = float(re.match(r'([\d½]+)', t).group(1).replace('½', '.5')); return 'Bebés' if a < 2 else ('Niños' if a < 6 else 'Grandes')
p = os.path.join(T, 'hm_verano.tsv'); base = list(csv.DictReader(open(p, encoding='utf-8'), delimiter='\t'))
campos = list(base[0].keys()); ya = {r['code'] for r in base}
E = json.load(open(os.path.join(T, 'revision', 'esperado.json')))
extra = []
for code, cat, gen, nom, g, u, tal, img in D:
    if code in ya: continue
    tls = [talle(x) for x in tal.split('|')]
    extra.append(dict(code=code, cat=cat, gen=gen, nombre=nom, usd=f'{u:g}', talles='|'.join(tls), img='https://image.hm.com/assets/hm/' + img,
                      fijo=str(precio(u, cat, g)), marca='hm', grupo='h', pdp=f'/en_us/productpage.{code}.html',
                      edad='|'.join(sorted({edad_t(x) for x in tls}, key=['Bebés', 'Niños', 'Grandes'].index))))
    E['hm'][code] = {'s': tal.split('|'), 'u': u}
w = csv.DictWriter(open(p, 'w', encoding='utf-8', newline=''), fieldnames=campos, delimiter='\t', lineterminator='\n', extrasaction='ignore')
w.writeheader(); w.writerows(base + extra)
json.dump(E, open(os.path.join(T, 'revision', 'esperado.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
print('H&M liquidación 23/11:', len(extra))
for r in extra: print(f"  {r['cat']:<13} | {r['nombre']:<48} | USD {r['usd']:<5} | ${int(r['fijo']):,}".replace(',', '.'), '|', r['talles'])
