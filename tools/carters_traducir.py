#!/usr/bin/env python3
"""Convierte tools/carters_raw.json (relevamiento de una sección de carters.com) en tools/carters_cl.tsv.
Reglas: USD ≤ MAX (talle en stock más caro), al menos 2 talles en stock (1 en accesorios), sin zapatos.
Precios fijos de Patricio: pack 3 bodies $49.900; packs 4 y 5 bodies $59.900; remeras ≤ USD 4,99 $23.900; pijamas de polar ≤ USD 10 $39.900.
Uso: python3 tools/carters_traducir.py [--max 20] [--excluir tools/carters_bf.tsv]"""
import argparse, json, re, os, collections, csv
ap = argparse.ArgumentParser(); ap.add_argument('--max', type=float, default=20); ap.add_argument('--excluir', default='')
a = ap.parse_args()
HERE = os.path.dirname(os.path.abspath(__file__))
raw = json.load(open(os.path.join(HERE, 'carters_raw.json')))
ya = set()
if a.excluir and os.path.exists(a.excluir):
    ya = {r['code'] for r in csv.DictReader(open(a.excluir, encoding='utf-8'), delimiter='\t')}

ORDER = ['PRE', 'NB', '3M', '6M', '9M', '12M', '18M', '24M', '2T', '3T', '4T', '5T', '4', '5', '6', '6-6X', '7', '8', '10', '12', '14', '16', 'Único']
NORM = {'OS': 'Único', 'ONE SIZE': 'Único', 'NO SIZE': 'Único', '6/6X': '6-6X', '6X': '6-6X'}

TIPOS = [
    (r'Shoe|Sneaker|Sandal|Boot|Slipper|Crib Shoe|Booties', None, None),
    (r'Fleece.*(Pajama|Sleep|Footie)|(Pajama|Sleep|Footie).*Fleece', 'Pijamas de Polar', 'Pijama de Polar'),
    (r'Pajama|PJ|Sleep ?& ?Play|Sleeper|Footie|Nightgown|Sleepsuit|Sleep Bag|Sleep Gown', 'Pijamas', 'Pijama'),
    (r'(\d)-Pack.*Bodysuit', 'Packs de Bodies', 'Pack {n} Bodies'),
    (r'Bodysuit Dress', 'Vestidos', 'Vestido Body'),
    (r'Bodysuit', None, None),   # se decide abajo: set o body suelto
    (r'(\d)-Piece|Set\b', 'Sets 2 Piezas', 'Set {n} Piezas'),
    (r'Jumpsuit|Romper|Overall|Shortall|Coverall|One-Piece', 'Enteritos', 'Enterito'),
    (r'Dress', 'Vestidos', 'Vestido'),
    (r'Skort', 'Shorts', 'Pollera-Short'),
    (r'Skirt', 'Vestidos', 'Pollera'),
    (r'Swim|Rash Guard|Trunks', 'Mallas', 'Malla'),
    (r'Puffer|Jacket|Coat|Vest\b|Parka|Snowsuit|Fleece Zip', 'Camperas', 'Campera'),
    (r'Hoodie', 'Buzos', 'Buzo Canguro'),
    (r'Sweatshirt|Pullover|Fleece', 'Buzos', 'Buzo'),
    (r'Sweater|Cardigan', 'Buzos', 'Sweater'),
    (r'Jogger|Sweatpant', 'Pantalones', 'Pantalón Jogging'),
    (r'Legging', 'Pantalones', 'Calza'),
    (r'Bike Short', 'Shorts', 'Calza Corta'),
    (r'Short', 'Shorts', 'Short'),
    (r'Jean', 'Pantalones', 'Jean'),
    (r'Pant|Trouser|Chino', 'Pantalones', 'Pantalón'),
    (r'Sock', 'Medias', 'Medias'),
    (r'Underwear|Brief|Panties|Boxer', 'Ropa interior', 'Ropa Interior'),
    (r'Hat|Beanie|Cap\b|Mitten|Glove|Scarf|Headband|Bow|Bib|Burp|Blanket|Swaddle|Bag|Backpack|Sunglass|Hair', 'Accesorios', 'Accesorio'),
    (r'Polo', 'Remeras', 'Chomba'),
    (r'Tank|Cami', 'Remeras', 'Musculosa'),
    (r'Tee|T-Shirt|Shirt|Top|Henley|Turtleneck|Blouse|Tunic', 'Remeras', 'Remera'),
]
ACC = {r'Beanie|Hat|Cap\b': 'Gorro', r'Mitten': 'Mitones', r'Glove': 'Guantes', r'Scarf': 'Bufanda', r'Headband': 'Vincha', r'Bow': 'Moños',
       r'Bib': 'Babero', r'Burp': 'Paño', r'Blanket': 'Manta', r'Swaddle': 'Manta para Envolver', r'Backpack': 'Mochila', r'Bag': 'Bolso',
       r'Sunglass': 'Anteojos de Sol', r'Hair': 'Accesorios para el Pelo'}
EXTRA = [(r'Long[- ]Sleeve', 'Manga Larga'), (r'Short[- ]Sleeve', 'Manga Corta'), (r'Sleeveless|Tank', 'Musculosa'), (r'Fleece|Sherpa', 'Polar'),
         (r'Thermal', 'Térmico'), (r'French Terry', 'Frisa Liviana'), (r'Denim', 'de Jean'), (r'Corduroy', 'de Corderoy'), (r'Velour', 'de Plush'),
         (r'Ribbed|Rib\b', 'Morley'), (r'Pointelle', 'Calado'), (r'Tulle', 'de Tul'), (r'Muslin|Gauze', 'de Gasa'), (r'Organic', 'Algodón Orgánico'),
         (r'Striped|Stripe', 'Rayado'), (r'Floral', 'Floral'), (r'Plaid|Flannel', 'Escocés'), (r'Holiday|Christmas|Santa|Reindeer|Elf|Gingerbread', 'Navideño'),
         (r'Halloween|Pumpkin', 'Halloween'), (r'Dinosaur|Dino', 'Dinosaurios'), (r'Heart', 'Corazones'), (r'Bear', 'Osito'), (r'Bunny|Rabbit', 'Conejito'),
         (r'Dog|Puppy', 'Perrito'), (r'Cat\b|Kitty', 'Gatito'), (r'Unicorn', 'Unicornios'), (r'Butterfl', 'Mariposas'), (r'Shark', 'Tiburones'),
         (r'Truck|Construction', 'Camiones'), (r'Car\b|Cars\b', 'Autos'), (r'Rainbow', 'Arcoíris'), (r'Star\b|Stars\b', 'Estrellas'),
         (r'Strawberr', 'Frutillas'), (r'Cherr', 'Cerezas'), (r'Apple', 'Manzanas'), (r'Leopard', 'Leopardo'), (r'Camo', 'Camuflado'),
         (r'Football|Sports|Soccer|Basketball|Baseball', 'Deportes'), (r'Space|Planet|Rocket', 'Espacio'), (r'Woodland|Forest', 'Bosque'),
         (r'Safari|Jungle|Animal|Zoo', 'Animales'), (r'Snow|Winter|Penguin|Arctic', 'Invierno'), (r'Bow\b', 'Moños'), (r'Lace|Eyelet', 'Bordado'),
         (r'Graphic|Print', 'Estampado')]
COLOR = [('navy', 'Azul Marino'), ('black', 'Negro'), ('white', 'Blanco'), ('ivory', 'Crudo'), ('cream', 'Crudo'), ('heather grey', 'Gris'), ('grey', 'Gris'),
         ('gray', 'Gris'), ('charcoal', 'Gris Topo'), ('pink', 'Rosa'), ('rose', 'Rosa'), ('red', 'Rojo'), ('burgundy', 'Bordó'), ('maroon', 'Bordó'),
         ('blue', 'Azul'), ('green', 'Verde'), ('olive', 'Verde Oliva'), ('sage', 'Verde Salvia'), ('yellow', 'Amarillo'), ('orange', 'Naranja'),
         ('purple', 'Lila'), ('lilac', 'Lila'), ('lavender', 'Lavanda'), ('brown', 'Marrón'), ('beige', 'Beige'), ('tan', 'Beige'), ('khaki', 'Caqui'),
         ('multi', 'Multicolor'), ('gold', 'Dorado'), ('silver', 'Plateado'), ('teal', 'Verde Azulado'), ('aqua', 'Turquesa'), ('turquoise', 'Turquesa'),
         ('mint', 'Verde Agua'), ('coral', 'Coral'), ('peach', 'Durazno'), ('mauve', 'Malva'), ('rust', 'Óxido'), ('denim', 'Jean')]
FEM = {'Remera', 'Musculosa', 'Chomba', 'Calza', 'Campera', 'Malla', 'Pollera', 'Pollera-Short', 'Ropa'}
FEMW = [('Estampado', 'Estampada'), ('Rayado', 'Rayada'), ('Calado', 'Calada'), ('Navideño', 'Navideña'), ('Negro', 'Negra'), ('Blanco', 'Blanca'),
        ('Rojo', 'Roja'), ('Amarillo', 'Amarilla'), ('Camuflado', 'Camuflada'), ('Escocés', 'Escocesa'), ('Dorado', 'Dorada'), ('Plateado', 'Plateada'),
        ('Térmico', 'Térmica')]

def color_es(c):
    out = []
    for part in re.split(r'[/,&]| and ', c.lower()):
        for en, es in COLOR:
            if en in part and es not in out: out.append(es); break
    return ' y '.join(out[:2]) if out else c.strip()

rows, sk, seen = [], collections.Counter(), collections.Counter()
for r in raw:
    if r.get('err') or not r.get('vs') or not r.get('name'): sk['sin datos'] += 1; continue
    if r['code'] in ya: sk['ya está (Black Friday)'] += 1; continue
    full = r['name'].strip()
    nm, _, col = full.partition(' - ') if ' - ' in full else (full, '', '')
    cat = base = None
    for pat, c, b in TIPOS:
        m = re.search(pat, nm, re.I)
        if m:
            cat, base = c, b
            if pat.startswith(r'Shoe'): cat = 'ZAPATOS'
            elif pat == r'Bodysuit':
                if re.search(r'Pant|Short|Legging|Skirt|Set|Piece', nm, re.I): cat, base = 'Sets 2 Piezas', 'Set Body y Pantalón' if re.search('Pant|Legging', nm) else 'Set Body y Short'
                else: cat, base = 'Bodies', 'Body'
            elif base and '{n}' in base:
                n = next((g for g in m.groups() if g), '2'); base = base.format(n=n)
                if base == 'Set 2 Piezas' and re.search('Bodysuit', nm): base = 'Set Body y Pantalón'
            break
    if cat == 'ZAPATOS': sk['zapatos'] += 1; continue
    if not cat: sk['sin tipo'] += 1; continue
    if cat == 'Accesorios': base = next((v for k, v in ACC.items() if re.search(k, nm, re.I)), 'Accesorio')
    inst = {}
    for v in r['vs']:
        if not v['st']: continue
        t = NORM.get(v['s'].upper().strip(), v['s'].strip().upper())
        if t in ORDER: inst[t] = max(inst.get(t, 0), v['p'])
    st = sorted(inst, key=ORDER.index)
    minimo = 1 if cat in ('Accesorios', 'Medias', 'Ropa interior') else 2
    if len(st) < minimo: sk['talles'] += 1; continue
    usd = max(inst.values())
    if usd > a.max: sk[f'> USD {a.max:g}'] += 1; continue
    fijo = ''
    if cat == 'Packs de Bodies': fijo = '49900' if base.startswith('Pack 3') else ('59900' if base[5] in '45' else '')
    elif cat == 'Remeras' and usd <= 4.99: fijo = '23900'
    elif cat == 'Pijamas de Polar' and usd <= 10: fijo = '39900'
    if cat == 'Pijamas de Polar' and not fijo: cat = 'Pijamas'
    quote = re.findall(r"'([^']{3,40})'", nm)
    ext = []
    for pat, es in EXTRA:
        if re.search(pat, nm, re.I) and es not in ext and es not in base and not (es == 'Musculosa' and base == 'Musculosa'): ext.append(es)
    if cat in ('Remeras', 'Bodies') and 'Manga Corta' in ext: ext.remove('Manga Corta')
    if quote: ext = [e for e in ext if e not in ('Estampado',)]
    parts = [base] + ([f'"{quote[0]}"'] if quote else []) + ext[:2] + ([color_es(col)] if col else [])
    name = re.sub(r'\s+', ' ', ' '.join(parts)).strip()
    if base.split()[0] in FEM:
        for m_, f_ in FEMW: name = re.sub(r'\b' + m_ + r'\b', f_, name)
    if seen[name]: name = f'{name} (modelo {seen[name] + 1})'
    seen[re.sub(r' \(modelo \d+\)$', '', name)] += 1
    g = re.search(r'\b(Girl|Girls)\b', nm); bo = re.search(r'\b(Boy|Boys)\b', nm)
    gen = 'Nena' if g and not bo else ('Nene' if bo and not g else 'Unisex')
    rows.append('\t'.join([r['code'], cat, gen, name, f'{usd:g}', '|'.join(st), r['img'], fijo]))
open(os.path.join(HERE, 'carters_cl.tsv'), 'w', encoding='utf-8').write('code\tcat\tgen\tnombre\tusd\ttalles\timg\tfijo\n' + '\n'.join(rows) + '\n')
print(len(rows), 'productos;', dict(sk))
print(collections.Counter(x.split('\t')[1] for x in rows))
