#!/usr/bin/env python3
"""Convierte tools/gf_raw.json (relevamiento de GAP Factory) en tools/gapfactory.tsv con nombres en castellano."""
import json, re, collections, os
HERE = os.path.dirname(os.path.abspath(__file__))
raw = json.load(open(os.path.join(HERE, 'gf_raw.json')))

SZ = {'UP TO 7 LB': 'NB', 'UP TO 7LB': 'NB', 'PREEMIE': 'NB', '0-3 M': '3M', '3-6 M': '6M', '6-12 M': '12M', '12-18 M': '18M', '18-24 M': '24M',
      '2 YRS': '2T', '3 YRS': '3T', '4 YRS': '4T', '5 YRS': '5T',
      'XS (4/5)': '4-5', 'S (6/7)': '6-7', 'M (8)': '8', 'L (10)': '10', 'L (10/11)': '10', 'XL (12)': '12', 'XXL (14/16)': '14-16',
      '4': '4-5', '5': '4-5', '6': '6-7', '7': '6-7', '8': '8', '10': '10', '12': '12', '14': '14-16', '16': '14-16',
      'ONE SIZE': 'Único', 'ONE-SIZE': 'Único', 'OS': 'Único'}
ORDER = ['NB', '3M', '6M', '12M', '18M', '24M', '2T', '3T', '4T', '5T', '4-5', '6-7', '8', '10', '12', '14-16', 'Único']

# (patrón en el nombre en inglés, categoría, nombre base en castellano) — gana el primero que coincide
TIPOS = [
    (r'PJ|Pajama|Sleep|Footed', 'Pijamas', 'Pijama'),
    (r'Bodysuit.*\((\d)-Pack\)|(\d)-Pack.*Bodysuit', 'Packs de Bodies', 'Pack {n} Bodies'),
    (r'Bodysuit', 'Bodies', 'Body'),
    (r'Outfit Set|Two-Piece|2-Piece|Set\b', 'Sets 2 Piezas', 'Set 2 Piezas'),
    (r'One-Piece|Coverall|Shortall|Romper|Overall', 'Enteritos', 'Enterito'),
    (r'Dress|Skirtall|Jumper|Jumpsuit', 'Vestidos', 'Vestido'),
    (r'Skort', 'Shorts', 'Pollera-Short'),
    (r'Skirt', 'Vestidos', 'Pollera'),
    (r'Swim|Rash Guard|Trunks', 'Mallas', 'Malla'),
    (r'Puffer|Jacket|Coat|Vest|Parka|Anorak|Shacket', 'Camperas', 'Campera'),
    (r'Zip Hoodie', 'Buzos', 'Campera Buzo con Cierre'),
    (r'Hoodie', 'Buzos', 'Buzo Canguro'),
    (r'Sweatshirt|Pullover|Quarter-Zip|Half-Zip', 'Buzos', 'Buzo'),
    (r'Sweater|Cardigan', 'Buzos', 'Sweater'),
    (r'Sweatpants|Joggers?', 'Pantalones', 'Pantalón Jogging'),
    (r'Leggings', 'Pantalones', 'Calza'),
    (r'Bike Shorts', 'Shorts', 'Calza Corta'),
    (r'Shorts', 'Shorts', 'Short'),
    (r'Jeans', 'Pantalones', 'Jean'),
    (r'Pants|Trousers|Chinos', 'Pantalones', 'Pantalón'),
    (r'Socks', 'Medias', 'Medias'),
    (r'Beanie|Hat|Cap\b|Mittens|Gloves|Scarf|Headband|Bow|Bag|Backpack|Sunglasses|Slippers|Shoes|Sneakers|Clogs|Boots|Tights|Hair', 'Accesorios', 'Accesorio'),
    (r'Polo', 'Remeras', 'Chomba'),
    (r'Tank|Cami', 'Remeras', 'Musculosa'),
    (r'Shirt|Tee|T-Shirt|Top|Henley|Turtleneck|Mockneck', 'Remeras', 'Remera'),
]
ACC = {
    r'Beanie': 'Gorro', r'Hat|Cap\b': 'Gorro', r'Mittens': 'Mitones', r'Gloves': 'Guantes', r'Scarf': 'Bufanda', r'Headband': 'Vincha',
    r'Bow': 'Moños', r'Backpack': 'Mochila', r'Bag': 'Bolso', r'Sunglasses': 'Anteojos de Sol', r'Slippers': 'Pantuflas', r'Clogs': 'Zuecos',
    r'Boots': 'Botas', r'Sneakers|Shoes': 'Zapatillas', r'Tights': 'Medias Can-Can', r'Hair': 'Accesorios para el Pelo'}
EXTRA = [  # detalles que vale la pena mostrar
    (r'Long[- ]Sleeve', 'Manga Larga'), (r'Short[- ]Sleeve', 'Manga Corta'), (r'Logo', 'Logo'), (r'Brannan', 'Osito Brannan'),
    (r'Fleece|Sherpa', 'Polar'), (r'Puffer', 'Inflable'), (r'Denim', 'de Jean'), (r'Corduroy', 'de Corderoy'), (r'Velour', 'de Plush'),
    (r'Waffle', 'Waffle'), (r'Rib(bed)?\b', 'Morley'), (r'Pointelle', 'Calado'), (r'Stripe', 'Rayado'), (r'Graphic', 'Estampado'),
    (r'Print\b', 'Estampado'), (r'Floral', 'Floral'), (r'Tulle', 'de Tul'), (r'Flannel', 'Escocés'), (r'Linen', 'de Lino'),
    (r'Cable-Knit', 'Tejido Trenzado'), (r'Holiday|Christmas|X-Mas|Santa|Reindeer|Elf', 'Navideño'), (r'Halloween', 'Halloween'),
    (r'Organic Cotton', 'Algodón Orgánico'), (r'Polo', ''), (r'Henley', 'con Botones'), (r'Turtleneck|Mockneck', 'Cuello Alto'),
    (r'Varsity', 'Varsity'), (r'Brooklyn', 'Brooklyn'), (r'\bNY\b|NYC', 'NY')]
COLOR = [  # palabras en el color (inglés) → castellano; se arma en orden de aparición
    ('navy', 'Azul Marino'), ('black', 'Negro'), ('white', 'Blanco'), ('off white', 'Crudo'), ('ivory', 'Crudo'), ('cream', 'Crudo'),
    ('grey', 'Gris'), ('gray', 'Gris'), ('heather', ''), ('marl', 'Melange'), ('charcoal', 'Gris Topo'), ('pink', 'Rosa'), ('rose', 'Rosa'),
    ('red', 'Rojo'), ('burgundy', 'Bordó'), ('maroon', 'Bordó'), ('blue', 'Azul'), ('denim', 'Jean'), ('wash', ''), ('green', 'Verde'),
    ('olive', 'Verde Oliva'), ('sage', 'Verde Salvia'), ('yellow', 'Amarillo'), ('orange', 'Naranja'), ('purple', 'Violeta'),
    ('lilac', 'Lila'), ('lavender', 'Lavanda'), ('violet', 'Violeta'), ('brown', 'Marrón'), ('beige', 'Beige'), ('tan', 'Beige'),
    ('khaki', 'Caqui'), ('camel', 'Camel'), ('oatmeal', 'Beige'), ('stripe', 'Rayado'), ('floral', 'Floral'), ('plaid', 'Escocés'),
    ('camo', 'Camuflado'), ('leopard', 'Leopardo'), ('dino', 'Dinosaurios'), ('bear', 'Ositos'), ('heart', 'Corazones'),
    ('star', 'Estrellas'), ('dot', 'Lunares'), ('cherry', 'Cerezas'), ('strawberr', 'Frutillas'), ('unicorn', 'Unicornios'),
    ('butterfl', 'Mariposas'), ('shark', 'Tiburones'), ('truck', 'Camiones'), ('car', 'Autos'), ('rainbow', 'Arcoíris'),
    ('gingham', 'Cuadrillé'), ('multi', 'Multicolor'), ('gold', 'Dorado'), ('silver', 'Plateado'), ('teal', 'Verde Azulado'),
    ('aqua', 'Turquesa'), ('turquoise', 'Turquesa'), ('mint', 'Verde Agua'), ('coral', 'Coral'), ('peach', 'Durazno')]

def color_es(c):
    cl = c.lower(); out = []
    for en, es in COLOR:
        if en in cl and es and es not in out:
            if en == 'red' and ('bored' in cl or 'tiered' in cl): continue
            if en == 'car' and ('carrot' in cl or 'cardinal' in cl or 'caramel' in cl): continue
            out.append(es)
    if 'Crudo' in out and 'Blanco' in out: out.remove('Blanco')
    if 'Azul Marino' in out and 'Azul' in out: out.remove('Azul')
    return ' '.join(out[:3]) or c.strip().title()

rows, sk = [], collections.Counter()
seen = collections.Counter()
for a in raw:
    if a.get('err') or not a.get('sizes'): sk['sin datos'] += 1; continue
    nm = a['name'].replace('&#124', '').replace('&#153', '').replace('™', '').strip()
    cat = base = None
    for pat, c, b in TIPOS:
        m = re.search(pat, nm, re.I)
        if m:
            cat, base = c, b
            if '{n}' in b:
                n = next((g for g in m.groups() if g), '3'); base = b.format(n=n)
            break
    if not cat: sk['sin tipo'] += 1; continue
    if cat == 'Accesorios':
        base = next((v for k, v in ACC.items() if re.search(k, nm, re.I)), 'Accesorio')
    st = []
    for sid, ok in a['sizes']:
        t = SZ.get(sid.upper().strip())
        if ok and t and t not in st: st.append(t)
    st = sorted(st, key=ORDER.index)
    minimo = 1 if cat in ('Accesorios', 'Medias') else 2
    if len(st) < minimo: sk['talles'] += 1; continue
    usd = max(a['price'], a.get('pmax') or 0)
    if usd > 20: sk['> USD 20'] += 1; continue
    ext = []
    for pat, es in EXTRA:
        if es and re.search(pat, nm, re.I) and es not in ext and es not in base: ext.append(es)
    if cat in ('Remeras', 'Bodies', 'Packs de Bodies', 'Sets 2 Piezas'):
        ext = [e for e in ext if not (e == 'Manga Corta' and cat == 'Remeras')]
    col = color_es(a['color'])
    name = ' '.join(['GAP ·', base] + ext[:3] + [col])
    name = re.sub(r'\s+', ' ', name).strip()
    seen[name] += 1
    if seen[name] > 1: name += f' (modelo {seen[name]})'
    gen = 'Nena' if a['k'] in ('g', 'tg', 'bg') else 'Nene'
    img = a['img']
    if img.startswith('00'): img = img[2:]
    rows.append('\t'.join([a['pid'], cat, gen, name, f"{usd:.2f}", '|'.join(st), img]))
open(os.path.join(HERE, 'gapfactory.tsv'), 'w', encoding='utf-8').write('code\tcat\tgen\tnombre\tusd\ttalles\timg\n' + '\n'.join(rows) + '\n')
print(len(rows), 'productos;', dict(sk))
print(collections.Counter(r.split('\t')[1] for r in rows))
