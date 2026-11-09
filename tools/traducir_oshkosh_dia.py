#!/usr/bin/env python3
"""Promo "12 días de ofertas" OshKosh (9/11/2026) → tools/oshkosh_dia.tsv
Entrada: TSV code, usd, nombre en inglés, img, talles. Jardineros a $49.900 fijo; el resto por fórmula con flete por peso + tramos."""
import csv, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import precio as P
COT = 1560; P.MARGEN = 1.9
TRAMOS = [(0, 10, 39900), (10, 12, 42900), (12, 13, 44900)]
PESO = {'Jardineros': 250, 'Pantalones': 250, 'Remeras': 100, 'Bodies': 70, 'Buzos': 180}
def precio(usd, cat):
    if cat == 'Jardineros': return 49900
    f = PESO[cat] / 1000 * 26.5 + 0.85
    p = P.precio(usd, COT, f); p = 29900 if 30300 <= p <= 35000 else p
    for lo, hi, v in TRAMOS:
        if lo <= usd < hi: p = min(p, v)
    return p
COL = [('Navy Blue/Green', 'Azul Marino y Verde'), ('White/Red/Black', 'Blanco, Rojo y Negro'), ('Red/Black', 'Rojo y Negro'), ('Red/White', 'Rojo y Blanco'),
       ('Navy Blue', 'Azul Marino'), ('Olive Green', 'Verde Oliva'), ('Dark Pink', 'Rosa Oscuro'), ('Green', 'Verde'), ('Red', 'Rojo'), ('Pink', 'Rosa'),
       ('Blue', 'Azul'), ('White', 'Blanco'), ('Khaki', 'Caqui'), ('Dark Wash', 'Lavado Oscuro'), ('Medium Wash', 'Lavado Medio'), ('Light Wash', 'Lavado Claro')]
def color(c):
    for en, es in COL:
        if c.strip() == en: return es
    return c.strip()
def lavado(n):
    for en, es in (('Sun Faded Light Wash', 'Lavado Claro Gastado'), ('Faded Dark Wash', 'Lavado Oscuro Gastado'), ('Faded Blue Wash', 'Azul Gastado'), ('Faded Wash', 'Gastado'),
                   ('Dark Blue Wash', 'Azul Oscuro'), ('Medium Blue Wash', 'Azul Medio'), ('Light Blue Wash', 'Celeste'), ('Blue Ice Wash', 'Celeste Hielo'),
                   ('Dark Wash', 'Lavado Oscuro'), ('Medium Wash', 'Lavado Medio')):
        if en in n: return es
    return ''
def traducir(en):
    base, col = re.split(r'\s*-\s+', en, maxsplit=1) if re.search(r'\s*-\s+', en) else (en, '')
    col = color(col) if col else ''
    b = re.sub(r'^(Baby Boy|Baby Girl|Baby|Toddler Boy|Toddler Girl|Toddler)\s+', '', base)
    gen = 'Nena' if re.search(r'Girl|Skirtall|Scalloped|Jegging', en) else ('Nene' if 'Boy' in en else 'Unisex')
    if re.search(r'Overalls|Skirtall', b):
        cat = 'Jardineros'
        tipo = 'Vestido Jardinero' if 'Skirtall' in b else 'Jardinero'
        tela = ('de Chambray' if 'Chambray' in b else 'de Jean Tejido' if re.search(r'Knit(-Like)? Denim', b) else 'de Jean Elastizado' if 'Stretch Denim' in b
                else 'de Corderoy' if 'Corduroy' in b else 'de Jean' if 'Denim' in b else '')
        det = []
        for en_, es in (('Nutcracker', 'Cascanueces'), ('Bear', 'Osito'), ('Airplane', 'Avión'), ('Plane', 'Avión'), ('Train', 'con Tren'), ('Alphabet', 'Abecedario'),
                        ('Heart-Print', 'Corazones'), ('Hickory Stripe', 'Rayado Hickory'), ('Buffalo Check', 'a Cuadros'), ('Plaid', 'Escocés'), ('Logo', 'con Logo'), ('Wide-Leg', 'Pierna Ancha')):
            if en_ in b and es not in det: det.append(es)
        nom = ' '.join(x for x in [tipo, tela] + det + [col] if x)
    elif re.search(r'Jeans|Jeggings', b):
        cat = 'Pantalones'
        tipo = ('Jegging Cintura Elástica' if 'Jegging' in b else 'Jean Super Skinny' if 'Super Skinny' in b else 'Jean Skinny' if 'Skinny' in b
                else 'Jean Recto' if 'Straight' in b else 'Jean Clásico')
        nom = f'{tipo} {lavado(b)}'.strip()
    elif 'Hood' in b:
        cat = 'Bodies' if 'Bodysuit' in b else 'Buzos'
        nom = ('Body Térmico Manga Larga con Capucha' if cat == 'Bodies' else 'Buzo Térmico con Capucha') + ' ' + col
    else:
        cat = 'Bodies' if 'Bodysuit' in b else 'Remeras'
        tipo = 'Body' if cat == 'Bodies' else ('Camisa' if 'Shirt' in b and ('Buffalo' in b or 'Button' in b) else 'Remera')
        if 'Button-Down' in b: tipo = 'Body Camisero'
        manga = 'Manga Corta' if 'Short-Sleeve' in b else 'Manga Larga'
        det = []
        if 'Buffalo Check' in b: det.append('a Cuadros')
        if 'Nutcracker' in b: det.append('Navideño Cascanueces' if tipo.startswith('Body') else 'Navideña Cascanueces')
        if 'Scalloped' in b: det.append('Cuello con Ondas')
        if 'Floral' in b: det.append('Floreado' if tipo.startswith('Body') else 'Floreada')
        if tipo in ('Remera', 'Camisa') and ' ' not in col: col = col.replace('Blanco', 'Blanca').replace('Rojo', 'Roja')
        nom = ' '.join([tipo, manga] + det + [col])
    return cat, gen, nom
rows = []
for code, usd, en, img, talles in csv.reader(open(sys.argv[1], encoding='utf-8'), delimiter='\t'):
    if len(talles.split('|')) < 2: continue          # al menos 2 talles en stock
    cat, gen, nom = traducir(en); u = float(usd)
    rows.append(dict(code=code, cat=cat, gen=gen, nombre=nom, usd=usd, talles=talles, img=img, fijo=precio(u, cat), marca='oshkosh'))
w = csv.DictWriter(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'oshkosh_dia.tsv'), 'w', encoding='utf-8', newline=''),
                   fieldnames=['code', 'cat', 'gen', 'nombre', 'usd', 'talles', 'img', 'fijo', 'marca'], delimiter='\t')
w.writeheader(); w.writerows(rows)
print(len(rows), 'productos')
