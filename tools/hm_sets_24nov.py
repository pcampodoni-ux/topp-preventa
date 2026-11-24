#!/usr/bin/env python3
"""24/11 (Patricio reabre el pedido hasta el miércoles 25/11 22 hs: "sumá sets y conjuntos atractivos, hasta $69.000"): sets de la liquidación de H&M
Criterio: hasta $69.000, al menos 2 talles, sin Halloween, Navidad ni disfraces; sin los frisados sin personaje. Precio como hm_sale_23nov.py."""
import csv, json, os, re, sys
T = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, T)
import precio as P

# code, categoría, género, nombre, peso_g, USD (liquidación), talles con stock, imagen
D = [
 ('1073066045', 'Sets 2 Piezas', 'Nena', 'Set Remera y Calza Corta Pitufos Rosa', 120, 8.99, '1½-2Y|3-4Y|4-5Y|5-6Y', '58/9d/589dc24416c1430963dc240211d537d8430e81d0.jpg'),
 ('1238606013', 'Sets 2 Piezas', 'Nena', 'Set Remera y Calza Corta Corazones Beige', 120, 6.99, '5-6Y|6-7Y|7-8Y', '8e/83/8e83ef2b6533f46ca047d505b23c2f45ba2311c7.jpg'),
 ('1314917019', 'Sets 2 Piezas', 'Nene', 'Set Remera y Pantalón Mickey Blanco', 150, 12.49, '4-6M|6-9M|9-12M|12-18M|1½-2Y|2-3Y|3-4Y', 'e2/52/e252b9a12b13233cdaed47cb0d6f3310d1faa797.jpg'),
 ('1314910013', 'Sets 2 Piezas', 'Nene', 'Set Buzo y Jogging Mickey Celeste', 250, 15.99, '4-6M|6-9M|9-12M|12-18M|1½-2Y|2-3Y|3-4Y', 'd4/0b/d40b4a4132feea3b6407e9bc561928490931c217.jpg'),
 ('1315800013', 'Sets 2 Piezas', 'Nena', 'Set Buzo y Jogging Hello Kitty Blanco', 250, 12.99, '4-6M|6-9M|9-12M|12-18M|1½-2Y|2-3Y|3-4Y', '07/dd/07dde62bd13afe7341868fba69956b9cc3267265.jpg'),
 ('1347744002', 'Sets 2 Piezas', 'Nena', 'Conjunto Deportivo Minnie Rosa', 250, 14.99, '4-6M|6-9M|9-12M|12-18M|1½-2Y|2-3Y|3-4Y', '04/1a/041a78d71d1d9a36c369d556cbc0d7c6475cced7.jpg'),
 ('1347892006', 'Sets 2 Piezas', 'Nena', 'Set Buzo y Pantalón Minnie Blanco', 250, 12.99, '4-6M|6-9M|9-12M|12-18M|1½-2Y|2-3Y|3-4Y', '12/12/121250877c121f4ad836b5ea2f90c40f2618994e.jpg'),
 ('1359251004', 'Sets 2 Piezas', 'Nena', 'Set Buzo y Pantalón Moñitos Rojo', 250, 7.99, '4-6M|6-9M|9-12M|12-18M|1½-2Y|2-3Y|3-4Y', '06/62/0662b48f0e2e12d3ae421123bd934567ed56d58e.jpg'),
 ('1339105001', 'Sets 2 Piezas', 'Nena', 'Set Musculosa y Short New York Gris Melange', 120, 8.49, '8-9Y|10-11Y|11-12Y', 'fa/bd/fabdc7c2dce45fef1a50c66ba1bbd04c220b77a2.jpg'),
 ('1339105003', 'Sets 2 Piezas', 'Nena', 'Set Musculosa y Short Rosa Claro', 120, 6.99, '8-9Y|11-12Y|12-13Y|13-14Y|14Y+', '24/20/24201ff85d269ea139c044810c767d0fa35ce724.jpg'),
 ('1345656001', 'Pijamas', 'Nena', 'Pijama 2 Piezas de Algodón Ositos Crudo', 150, 9.99, '1-2M|2-4M|4-6M|6-9M|9-12M|12-18M|1½-2Y|2-3Y|3-4Y', '26/fc/26fc2abdce08bddabd0323a6412e6b7dd361c273.jpg'),
 ('1345656003', 'Pijamas', 'Unisex', 'Pijama 2 Piezas de Algodón Rayado Azul y Blanco', 150, 7.99, '1-2M|2-4M|4-6M|6-9M|9-12M|12-18M|1½-2Y|2-3Y|3-4Y', 'e5/66/e566c723786734865c4cab7faf65762c641f7235.jpg'),
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
for r in extra:   # tope de Patricio: hasta $69.000 → los 2 sets de buzo y jogging Mickey/Minnie (fórmula $75.890 / $69.900) a $68.900
    if r['code'] in ('1314910013', '1347744002'): r['fijo'] = '68900'
w = csv.DictWriter(open(p, 'w', encoding='utf-8', newline=''), fieldnames=campos, delimiter='\t', lineterminator='\n', extrasaction='ignore')
w.writeheader(); w.writerows(base + extra)
json.dump(E, open(os.path.join(T, 'revision', 'esperado.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
print('H&M sets 24/11:', len(extra))
for r in extra: print(f"  {r['cat']:<13} | {r['nombre']:<48} | USD {r['usd']:<5} | ${int(r['fijo']):,}".replace(',', '.'), '|', r['talles'])
