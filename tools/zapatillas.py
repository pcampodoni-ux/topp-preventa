#!/usr/bin/env python3
"""Zapatillas Carter's/OshKosh (12/11/2026) → tools/zapatillas.tsv

Reglas de precio (pedido de Patricio, 12/11/2026):
  - Promo del día "USD 12 Shoes": bebé $53.900; niños (toddler y kids) $59.900.
  - El resto: fórmula de siempre (×1,9 con tramos), pero la ganancia nunca baja de $16.000 por par.
Entrada: tools/zapatillas_raw.json (quickview de carters.com, relevado desde el navegador de Patricio).
"""
import json, os, re, math, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import precio as P

COT, FLETE, GAN_MIN, MAX_USD = 1560, 6.94, 16000, 20
TRAMOS = [(0, 10, 39900), (10, 12, 42900), (12, 13, 44900)]
COLOR = [('navy', 'Azul Marino'), ('black', 'Negro'), ('white', 'Blanco'), ('ivory', 'Crudo'), ('cream', 'Crudo'), ('grey', 'Gris'), ('gray', 'Gris'),
         ('pink', 'Rosa'), ('red', 'Rojo'), ('burgundy', 'Bordó'), ('blue', 'Azul'), ('green', 'Verde'), ('olive', 'Verde Oliva'), ('yellow', 'Amarillo'),
         ('orange', 'Naranja'), ('purple', 'Lila'), ('brown', 'Marrón'), ('beige', 'Beige'), ('tan', 'Beige'), ('gold', 'Dorado'), ('silver', 'Plateado'),
         ('aqua', 'Turquesa'), ('multi', 'Multicolor')]
FUERA = r'Slipper|Boot|Bootie|Snow|Tee\b|Sock'          # invierno / no es calzado
TIPO = [(r'Cleat', 'Botines de Fútbol', 'Zapatillas'), (r'Sandal', 'Sandalias', 'Sandalias'), (r'Clog', 'Zuecos', 'Sandalias'),
        (r'Mary Jane|Ballet|Flats?\b', 'Guillerminas', 'Zapatillas'), (r'Loafer', 'Mocasines', 'Zapatillas'), (r'Boat', 'Náuticos', 'Zapatillas'),
        (r'Moccasin|Mocassin', 'Mocasines', 'Zapatillas'), (r'Dress Shoe', 'Zapatos de Vestir', 'Zapatillas'),
        (r'High[- ]Top', 'Zapatillas Altas', 'Zapatillas'), (r'Athletic|Sport', 'Zapatillas Deportivas', 'Zapatillas'),
        (r'Slip-On', 'Panchas', 'Zapatillas'), (r'Sneaker|Trainer|Canvas', 'Zapatillas', 'Zapatillas'), (r'Shoe', 'Zapatos', 'Zapatillas')]
EXTRA = [(r'Every Step|First Walker', 'Primeros Pasos'), (r'Light[- ]?Up', 'con Luces'), (r'Jelly', 'de Goma'), (r'Metallic|Shimmer|Iridescent', 'Brillantes'),
         (r'Leopard|Cheetah', 'Animal Print'), (r'Heart', 'Corazones'), (r'Floral|Flower', 'Flores'), (r'Striped', 'Rayadas'), (r'Bow', 'con Moño'),
         (r'Dinosaur|Monster', 'Dinosaurio'), (r'Shark', 'Tiburón'), (r'Unicorn', 'Unicornio'), (r'Rainbow', 'Arcoíris'), (r'Color ?[Bb]lock', 'Combinadas'),
         (r'Varsity', 'Varsity'), (r'Corduroy', 'Corderoy'), (r'Woven|Braided|Crochet', 'Tejidas'), (r'Platform', 'Plataforma')]
EDAD = {'Baby': 'Bebés', 'Toddler': 'Niños', 'Kid': 'Grandes'}

def color_es(c):
    out = []
    for part in re.split(r'[/,&]| and ', c.lower()):
        for en, es in COLOR:
            if en in part and es not in out: out.append(es); break
    return ' y '.join(out[:2])

def x900(n): return int(math.ceil(n / 1000.0)) * 1000 - 100

def precio(usd, seg):
    costo = (usd * 1.07 + FLETE) * COT
    if usd == 12: return 53900 if seg == 'Baby' else 59900, costo
    p = P.precio(usd, COT)
    p = 29900 if 30300 <= p <= 35000 else p
    for lo, hi, v in TRAMOS:
        if lo <= usd < hi: p = min(p, v)
    return max(p, x900(costo + GAN_MIN)), costo

raw = json.load(open(os.path.join(HERE, 'zapatillas_raw.json')))
rows, sk, seen = [], collections.Counter(), collections.Counter()
for r in raw:
    nm = (r.get('name') or '').strip()
    if not nm or re.search(FUERA, nm, re.I): sk['fuera (invierno/no calzado)'] += 1; continue
    usd = r.get('sx')
    if usd is None or usd > MAX_USD: sk['> USD 20'] += 1; continue
    t = next(((b, c) for pat, b, c in TIPO if re.search(pat, nm, re.I)), None)
    if not t: sk['sin tipo'] += 1; continue
    tal = [z[0] for z in r['z'] if z[1]]
    if len(tal) < 2: sk['menos de 2 talles'] += 1; continue
    base, cat = t
    ext = [es for pat, es in EXTRA if re.search(pat, nm, re.I)]
    if base.split()[0] in ('Zapatos', 'Mocasines', 'Náuticos', 'Zuecos', 'Botines'):
        ext = [{'Rayadas': 'Rayados', 'Combinadas': 'Combinados', 'Tejidas': 'Tejidos'}.get(e, e) for e in ext]
    col = color_es(nm.split(' - ', 1)[1]) if ' - ' in nm else ''
    nombre = ' '.join([base] + ext[:2] + ([col] if col else []))
    seen[nombre] += 1
    if seen[nombre] > 1: nombre += f' (modelo {seen[nombre]})'
    g, bo = re.search(r'\bGirls?\b', nm), re.search(r'\bBoys?\b', nm)
    gen = 'Nena' if g and not bo else ('Nene' if bo and not g else 'Unisex')
    seg = r.get('seg') or 'Toddler'
    p, costo = precio(usd, seg)
    marca = 'oshkosh' if r.get('brand') == 'oshkosh' else 'carters'
    rows.append(dict(code=r['code'], cat=cat, gen=gen, nombre=nombre, usd=f'{usd:g}', talles='|'.join('US ' + x for x in tal),
                     img=r['img'], fijo=str(p), marca=marca, grupo='z', edad=EDAD.get(seg, 'Niños'), ganancia=str(round(p - costo))))
cols = ['code', 'cat', 'gen', 'nombre', 'usd', 'talles', 'img', 'fijo', 'marca', 'grupo', 'edad', 'ganancia']
with open(os.path.join(HERE, 'zapatillas.tsv'), 'w', encoding='utf-8') as f:
    f.write('\t'.join(cols) + '\n')
    for d in rows: f.write('\t'.join(d[c] for c in cols) + '\n')
print(len(rows), 'zapatillas;', dict(sk))
print('promo USD 12:', sum(1 for d in rows if d['usd'] == '12'), '| ganancia mínima:', min(int(d['ganancia']) for d in rows))
