#!/usr/bin/env python3
"""H&M (12/11/2026) → tools/hm.tsv

Criterio de Patricio (audio del 12/11): ropa de verano que más se vende, sin cargar toda la web:
vestidos y soleritas, conjuntos (sets) de nena y varón, remeras hasta USD 10 y packs de remeras hasta USD 20;
bebé, toddler y niños. Precio USD = precio sin socio (rojo o blanco); fórmula de siempre ×1,9 con tramos.
Entrada: tools/hm_raw.json (listados + disponibilidad de www2.hm.com, relevado desde el navegador de Patricio).
"""
import json, os, re, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))

COLOR = [('dark gray', 'Gris Oscuro'), ('light gray', 'Gris Claro'), ('gray', 'Gris'), ('navy', 'Azul Marino'), ('dark blue', 'Azul Oscuro'),
         ('light blue', 'Celeste'), ('blue', 'Azul'), ('black', 'Negro'), ('white', 'Blanco'), ('cream', 'Crudo'), ('natural', 'Crudo'), ('beige', 'Beige'),
         ('light pink', 'Rosa Claro'), ('dusty pink', 'Rosa Viejo'), ('pink', 'Rosa'), ('red', 'Rojo'), ('green', 'Verde'), ('khaki', 'Caqui'),
         ('yellow', 'Amarillo'), ('orange', 'Naranja'), ('purple', 'Lila'), ('lilac', 'Lila'), ('brown', 'Marrón'), ('turquoise', 'Turquesa'),
         ('mint', 'Verde Agua'), ('coral', 'Coral'), ('burgundy', 'Bordó')]
MOTIVO = [('floral', 'Flores'), ('flower', 'Flores'), ('heart', 'Corazones'), ('striped', 'Rayas'), ('stripe', 'Rayas'), ('dino', 'Dinosaurios'),
          ('butterfl', 'Mariposas'), ('strawberr', 'Frutillas'), ('cherr', 'Cerezas'), ('spot', 'Lunares'), ('dot', 'Lunares'), ('star', 'Estrellas'),
          ('animal', 'Animales'), ('car', 'Autos'), ('lemon', 'Limones'), ('ladybug', 'Vaquitas')]
ADJ = [(r'Ruffle', 'con Volados'), (r'Muslin', 'de Muselina'), (r'Linen', 'de Lino'), (r'Ribbed', 'Morley'), (r'Plumeti', 'Plumeti'),
       (r'Smock', 'Smock'), (r'Embroider', 'Bordado'), (r'Broderie|Eyelet', 'Bordado Inglés'), (r'Sleeveless', 'Sin Mangas'), (r'Jersey', 'de Jersey'),
       (r'Printed|Patterned', 'Estampado'), (r'Collar', 'con Cuello'), (r'Ladybug', 'Vaquitas'), (r'Tiered', 'con Volados'), (r'Denim', 'de Jean'),
       (r'Bow-Tie', 'con Moñito'), (r'Shorts', 'con Short')]
FEM = {'Remera', 'Musculosa', 'Camisa'}

def color_es(c):
    c = c.lower(); col = next((es for en, es in COLOR if en in c), ''); mot = next((es for en, es in MOTIVO if en in c), '')
    return ' '.join(x for x in (mot, col) if x)

def base_de(t, tipo):
    m = re.search(r'(\d)-[Pp]ack', t)
    if tipo == 'Vestidos': return 'Vestido'
    if tipo == 'Sets 2 Piezas':
        n = re.search(r'(\d)-[Pp]iece', t); return f'Set {n.group(1) if n else 2} Piezas'
    if re.search(r'Tank', t): b = 'Musculosas' if m else 'Musculosa'
    elif re.search(r'Shirt\b', t) and not re.search(r'T-[Ss]hirt', t): b = 'Camisas' if m else 'Camisa'
    else: b = 'Remeras' if m else 'Remera'
    return f'Pack {m.group(1)} {b}' if m else b

def talle(s):
    s = s.strip()
    if re.fullmatch(r'[\d½-]+M', s): return s                       # bebés: 4-6M, 12-18M
    m = re.fullmatch(r'([\d½]+(?:-[\d½]+)?)Y', s)
    return f'{m.group(1)} años' if m else None

def edad(t):
    if t.endswith('M'): return 'Bebés'
    a = re.match(r'([\d½]+)', t).group(1).replace('½', '.5'); a = float(a)
    return 'Bebés' if a < 2 else ('Niños' if a < 6 else 'Grandes')

raw = json.load(open(os.path.join(HERE, 'hm_raw.json')))
rows, sk, seen = [], collections.Counter(), collections.Counter()
for x in raw:
    if x.get('err') or not x.get('sizes'): sk['sin datos'] += 1; continue
    usd = x.get('r') or x.get('w')
    tal = [talle(s) for s, ok in x['sizes'] if ok == 1]
    tal = [t for t in tal if t]
    if len(tal) < 2: sk['menos de 2 talles'] += 1; continue
    t = x['t']; tipo = x['tipo']
    b = base_de(t, tipo)
    ext = []
    for pat, es in ADJ:
        if re.search(pat, t, re.I) and es not in ext: ext.append(es)
    noun = b.split()[-1]
    if noun in FEM: ext = [{'Estampado': 'Estampada', 'Bordado': 'Bordada', 'Bordado Inglés': 'Bordado Inglés'}.get(e, e) for e in ext]
    elif noun in ('Remeras', 'Musculosas', 'Camisas'): ext = [{'Estampado': 'Estampadas', 'Bordado': 'Bordadas'}.get(e, e) for e in ext]
    col = color_es(x.get('sw') or '')
    nombre = ' '.join([b] + ext[:2] + ([col] if col else []))
    seen[nombre] += 1
    if seen[nombre] > 1: nombre += f' (modelo {seen[nombre]})'
    cat = x['cat'].lower(); src = x.get('src', '')
    gen = 'Nena' if ('girl' in cat or 'nena' in src) else ('Nene' if ('boy' in cat or 'nene' in src) else 'Unisex')
    if tipo == 'Vestidos': gen = 'Nena'
    eds = sorted({edad(z) for z in tal}, key=['Bebés', 'Niños', 'Grandes'].index)
    rows.append(dict(code=x['code'], cat=tipo, gen=gen, nombre=nombre, usd=f'{usd:g}', talles='|'.join(tal), img=x.get('img') or '',
                     fijo='', marca='hm', grupo='h', edad='|'.join(eds), pdp=x['pdp']))
cols = ['code', 'cat', 'gen', 'nombre', 'usd', 'talles', 'img', 'fijo', 'marca', 'grupo', 'edad', 'pdp']
with open(os.path.join(HERE, 'hm.tsv'), 'w', encoding='utf-8') as f:
    f.write('\t'.join(cols) + '\n')
    for d in rows: f.write('\t'.join(d[c] for c in cols) + '\n')
print(len(rows), 'productos H&M;', dict(sk), dict(collections.Counter(d['cat'] for d in rows)))
