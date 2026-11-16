#!/usr/bin/env python3
"""Pedido "verano hasta USD 17" (13/11/2026): Carter's/OshKosh, H&M y GAP Factory.

Criterio de Patricio: todo lo de verano, en oferta, hasta USD 17, lo más atractivo por precio.
Toma los TSV completos de cada marca y deja, por marca, categoría y edad, los N más baratos.
  - Categorías de verano: remeras, shorts, vestidos, sets, enteritos, packs de bodies y mallas
    (sin bodies sueltos, sin manga larga, sin abrigo ni prendas de fiestas de invierno).
  - H&M: como mucho 3 colores por modelo (los de más talles disponibles) para no repetir.
Uso: python3 tools/verano.py [N_carters] [N_gap] [N_hm]
Salida: tools/carters_verano.tsv, tools/gap_verano.tsv, tools/hm_verano.tsv
"""
import csv, os, re, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
NC, NG, NH = (int(x) for x in (sys.argv[1:4] + ['15', '10', '15'][len(sys.argv[1:4]):]))
MAX = 17
VERANO = {'Remeras', 'Shorts', 'Vestidos', 'Sets 2 Piezas', 'Enteritos', 'Packs de Bodies', 'Mallas'}
FUERA = re.compile(r'Manga Larga|Polar|Frisad|Abrigo|Campera|Buzo|Navidad|Navideñ|Halloween|Acción de Gracias|Papá Noel|Reno\b|Janucá|Hanukkah|Pijama|Corderoy|Térmic|Escoc|Frisa|Candy ?cane|Candycane|Plaid|Tart[aá]n|Gingerbread|Jengibre|Navide|Holiday|Santa|Snow|Nieve', re.I)
BABY = {'PRE', 'NB', '3M', '6M', '9M', '12M', '18M', '24M'}

def edad(r):
    if r.get('edad'): return r['edad'].split('|')[0]
    t = r['talles'].split('|')
    if any(x in BABY or x.endswith('M') for x in t): return 'Bebés'
    if any(x.endswith('T') for x in t): return 'Niños'
    return 'Grandes'

def leer(f):
    p = os.path.join(HERE, f)
    return list(csv.DictReader(open(p, encoding='utf-8'), delimiter='\t')) if os.path.exists(p) else []

import json
EN = {}
try: EN = {r['code']: r['name'] for r in json.load(open(os.path.join(HERE, 'carters_full_raw.json')))}
except Exception: pass
FUERA_EN = re.compile(r'Long[- ]Sleeve|Sweater|Fleece|Sherpa|Thanksgiving|Christmas|Halloween|Hanukkah|Santa|Holiday|Thermal|Velour|Corduroy|Footed', re.I)

def curar(rows, n, nombre_salida, por_modelo=None):
    ok = [r for r in rows if r['cat'] in VERANO and float(r['usd']) <= MAX and not FUERA.search(r['nombre']) and not FUERA_EN.search(EN.get(r['code'], ''))]
    ok = [r for r in ok if not (r['cat'] == 'Packs de Bodies' and not r.get('fijo') and r.get('marca') != 'hm')]   # 16/11: sin packs de 2 (no tienen precio fijo)
    if por_modelo:   # H&M: hasta 3 colores por modelo, los de más talles
        g = collections.defaultdict(list)
        for r in ok: g[r['code'][:7]].append(r)
        ok = [x for xs in g.values() for x in sorted(xs, key=lambda r: (-len(r['talles'].split('|')), float(r['usd'])))[:por_modelo]]
    grupos = collections.defaultdict(list)
    for r in ok: grupos[(r.get('marca', ''), r['cat'], edad(r))].append(r)
    out = []
    for k, xs in grupos.items():
        xs.sort(key=lambda r: (float(r['usd']), -len(r['talles'].split('|'))))
        out += xs[: (999 if k[1] in ('Packs de Bodies', 'Mallas') else n)]   # 16/11: todas las mallas
    if not out: print(nombre_salida, 'sin productos'); return
    seen = collections.Counter()   # renumera los "(modelo N)" para que arranquen de 2 dentro de lo elegido
    for r in sorted(out, key=lambda r: float(r['usd'])):
        b = re.sub(r' \(modelo \d+\)$', '', r['nombre']); seen[b] += 1
        r['nombre'] = b if seen[b] == 1 else f'{b} (modelo {seen[b]})'
    cols = list(rows[0].keys())
    w = csv.DictWriter(open(os.path.join(HERE, nombre_salida), 'w', encoding='utf-8', newline=''), fieldnames=cols, delimiter='\t', lineterminator='\n')
    w.writeheader(); w.writerows(out)
    print(nombre_salida, len(out), dict(collections.Counter(r['cat'] for r in out)))

curar(leer('carters_full_all.tsv'), NC, 'carters_verano.tsv')

# Pijamas (14/11, pedido de Patricio): todos los de verano (manga corta) + una selección de invierno,
# los más baratos por edad (sin Halloween/Navidad/Acción de Gracias/Janucá).
PIJ_VER = re.compile(r'Short[- ]Sleeve|Shorts?\b|Tank|Sleeveless', re.I)
PIJ_NO = re.compile(r'Footed|Fleece|Long[- ]Sleeve|Christmas|Halloween|Holiday|Thanksgiving|Hanukkah|Santa', re.I)
FIESTA = re.compile(r'Christmas|Halloween|Holiday|Thanksgiving|Hanukkah|Santa|Navide|Navidad|Halloween|Gracias|Janucá|Papá Noel|Reno\b|Gingerbread|Jengibre|Candy ?cane', re.I)
def pijamas(n_inv=10):
    rows = [r for r in leer('carters_full_all.tsv') if r['cat'] in ('Pijamas', 'Pijamas de Polar') and float(r['usd']) <= MAX]
    ver = [r for r in rows if float(r['usd']) < 13 and PIJ_VER.search(EN.get(r['code'], '')) and not PIJ_NO.search(EN.get(r['code'], ''))]
    inv = [r for r in rows if r not in ver and not FIESTA.search(EN.get(r['code'], '') + ' ' + r['nombre'])]
    g = collections.defaultdict(list)
    for r in inv: g[edad(r)].append(r)
    sel = list(ver)
    for xs in g.values():
        xs.sort(key=lambda r: (float(r['usd']), -len(r['talles'].split('|')))); sel += xs[:n_inv]
    # Precios 14/11 (Patricio, frente a la competencia; flete por peso): bebé hasta 9M $29.900,
    # bebé 12–24M $32.900, toddler 2T–5T de USD 6 a 9,99 $38.900. Niños 4–14 y USD 10+ quedan por fórmula/tramo.
    PRE9 = {'PRE', 'NB', '3M', '6M', '9M'}
    for r in sel:
        t = set(r['talles'].split('|')); u = float(r['usd'])
        if t <= PRE9: r['fijo'] = '29900'
        elif edad(r) == 'Bebés': r['fijo'] = '32900'
        elif edad(r) == 'Niños' and 6 <= u < 10: r['fijo'] = '38900'
    seen = collections.Counter()
    for r in sorted(sel, key=lambda r: float(r['usd'])):
        b = re.sub(r' \(modelo \d+\)$', '', r['nombre']); seen[b] += 1
        r['nombre'] = b if seen[b] == 1 else f'{b} (modelo {seen[b]})'
    p = os.path.join(HERE, 'carters_verano.tsv'); base = leer('carters_verano.tsv')
    w = csv.DictWriter(open(p, 'w', encoding='utf-8', newline=''), fieldnames=list(base[0].keys()), delimiter='\t', lineterminator='\n')
    w.writeheader(); w.writerows(base + sel)
    print('pijamas', len(sel), 'verano', len(ver), 'invierno', len(sel) - len(ver))
# pijamas()   # 14/11 21:20: Patricio los saca del pedido extendido (van a cambiar de precio)
# GAP Factory (13/11): la liquidación tiene un extra 60% que se aplica en el checkout ("Cyber Sale Sneak Peek").
# El costo real es el precio de lista × 0,4 y el precio de venta se calcula sobre ese costo con ×1,9 (decisión de Patricio).
sys.path.insert(0, HERE); import precio as P
def precio_gap(usd):
    P.MARGEN = 1.9; p = P.precio(usd, 1560); p = 29900 if 30300 <= p <= 35000 else p
    for lo, hi, v in [(0, 10, 39900), (10, 12, 42900), (12, 13, 44900)]:
        if lo <= usd < hi: p = min(p, v)
    return p
gap = leer('gapfactory_all.tsv')
for r in gap:
    r['usd_lista'] = r['usd']; r['usd'] = f"{float(r['usd']) * 0.4:.2f}"; r['fijo'] = str(precio_gap(float(r['usd'])))
curar(gap, NG, 'gap_verano.tsv')
curar(leer(os.environ.get('HM_TSV', 'hm.tsv')), NH, 'hm_verano.tsv', por_modelo=3)

# 14/11 (Patricio): todos los vestidos de H&M de menos de USD 8 (verificados hoy) a $29.900.
def vestidos_hm():
    p = os.path.join(HERE, 'hm_verano.tsv'); base = leer('hm_verano.tsv'); ya = {r['code'] for r in base}
    extra = [r for r in leer(os.environ.get('HM_TSV', 'hm.tsv')) if r['cat'] == 'Vestidos' and float(r['usd']) < 8 and r['code'] not in ya]
    rows = base + extra
    for r in rows:
        if r['cat'] == 'Vestidos' and float(r['usd']) < 8: r['fijo'] = '29900'
    seen = collections.Counter()
    for r in sorted(rows, key=lambda r: float(r['usd'])):
        b = re.sub(r' \(modelo \d+\)$', '', r['nombre']); seen[b] += 1
        r['nombre'] = b if seen[b] == 1 else f'{b} (modelo {seen[b]})'
    w = csv.DictWriter(open(p, 'w', encoding='utf-8', newline=''), fieldnames=list(base[0].keys()), delimiter='\t', lineterminator='\n')
    w.writeheader(); w.writerows(rows)
    print('vestidos H&M a $29.900:', sum(1 for r in rows if r.get('fijo') == '29900'), '(nuevos', len(extra), ')')
vestidos_hm()

# H&M vestidos (14/11, Patricio): menos de USD 8 → $29.900; de USD 8 a 8,99 → $35.900.
def hm_vestidos():
    p = os.path.join(HERE, 'hm_verano.tsv'); rows = leer('hm_verano.tsv')
    if not rows: return
    for r in rows:
        if r['cat'] != 'Vestidos': continue
        u = float(r['usd'])
        if u < 8: r['fijo'] = '29900'
        elif u < 9: r['fijo'] = '35900'
    w = csv.DictWriter(open(p, 'w', encoding='utf-8', newline=''), fieldnames=list(rows[0].keys()), delimiter='\t', lineterminator='\n')
    w.writeheader(); w.writerows(rows)
# H&M link del 14/11 (Patricio: "subí todo lo que está en este link", búsqueda "Cotton T-Shirt with Printed baby kids"):
# todo lo de verano (sin manga larga) de hasta USD 17 a precio normal (sin socio), con stock verificado ese día, sin tope por grupo.
def hm_link():
    try: link = set(json.load(open(os.path.join(HERE, 'hm_link_14nov.json'))))
    except Exception: return
    p = os.path.join(HERE, 'hm_verano.tsv'); rows = leer('hm_verano.tsv'); ya = {r['code'] for r in rows}
    extra = [r for r in leer('hm.tsv') if r['code'] in link and r['code'] not in ya and float(r['usd']) <= MAX and not FUERA.search(r['nombre'])]
    w = csv.DictWriter(open(p, 'w', encoding='utf-8', newline=''), fieldnames=list(rows[0].keys()), delimiter='\t', lineterminator='\n')
    w.writeheader(); w.writerows(rows + extra)
    print('H&M link 14/11: se suman', len(extra), dict(collections.Counter(r['cat'] for r in extra)))
hm_link()
hm_vestidos()

# H&M "2-Piece Cotton Set" de USD 9,99 (modelo 1314916, 14/11, Patricio) → $37.900.
def hm_sets():
    p = os.path.join(HERE, 'hm_verano.tsv'); rows = leer('hm_verano.tsv')
    for r in rows:
        if r['code'].startswith('1314916') and abs(float(r['usd']) - 9.99) < 0.01: r['fijo'] = '37900'
    w = csv.DictWriter(open(p, 'w', encoding='utf-8', newline=''), fieldnames=list(rows[0].keys()), delimiter='\t', lineterminator='\n')
    w.writeheader(); w.writerows(rows)
hm_sets()

# H&M precios 14/11 noche (Patricio): remeras sueltas USD 6,99–7,99 $29.900; 9,99 $32.900; 12,99 $37.900; 14,99 $44.900;
# sets de USD 14,99 $49.900; packs de remeras de USD 14,99 $54.900.
def hm_precios():
    p = os.path.join(HERE, 'hm_verano.tsv'); rows = leer('hm_verano.tsv')
    for r in rows:
        u = round(float(r['usd']), 2); pack = r['nombre'].startswith('Pack')
        if r['cat'] == 'Remeras' and not pack:
            v = '29900' if u < 8 else '32900' if u < 10 else '37900' if u < 13 else '44900' if u < 15 else None   # rangos: los USD intermedios siguen al escalón
            if v: r['fijo'] = v
        elif r['cat'] == 'Remeras' and pack and u == 14.99: r['fijo'] = '54900'
        elif r['cat'] == 'Sets 2 Piezas' and u == 14.99: r['fijo'] = '49900'
    w = csv.DictWriter(open(p, 'w', encoding='utf-8', newline=''), fieldnames=list(rows[0].keys()), delimiter='\t', lineterminator='\n')
    w.writeheader(); w.writerows(rows)
hm_precios()

# Pantalones (14/11 noche, Patricio: "los más baratos"): Carter's/OshKosh y GAP Factory hasta USD 10 de costo,
# sin polar ni frisa, los 15 más baratos por marca y edad.
SIN_ABRIGO_EN = re.compile(r'Fleece|Sherpa|French Terry|Thermal|Velour|Corduroy|Sweatpant|Plush|Quilted|Lined|Christmas|Halloween|Holiday|Santa', re.I)
def pantalones(n=15, tope=10):
    def elegir(rows):
        ok = [r for r in rows if r['cat'] == 'Pantalones' and float(r['usd']) <= tope and not FUERA.search(r['nombre'])
              and not SIN_ABRIGO_EN.search(EN.get(r['code'], ''))]
        g = collections.defaultdict(list)
        for r in ok: g[(r.get('marca', ''), edad(r))].append(r)
        out = []
        for xs in g.values():
            xs.sort(key=lambda r: (float(r['usd']), -len(r['talles'].split('|')))); out += xs[:n]
        return out
    def sumar(salida, extra):
        base = leer(salida); ya = {r['code'] for r in base}; extra = [r for r in extra if r['code'] not in ya]
        seen = collections.Counter()
        for r in sorted(extra, key=lambda r: float(r['usd'])):
            b = re.sub(r' \(modelo \d+\)$', '', r['nombre']); seen[b] += 1
            r['nombre'] = b if seen[b] == 1 else f'{b} (modelo {seen[b]})'
        cols = list(base[0].keys())
        w = csv.DictWriter(open(os.path.join(HERE, salida), 'w', encoding='utf-8', newline=''), fieldnames=cols, delimiter='\t', lineterminator='\n', extrasaction='ignore')
        w.writeheader(); w.writerows(base + extra)
        print('pantalones', salida, len(extra))
    sumar('carters_verano.tsv', elegir(leer('carters_full_all.tsv')))
    g = leer('gapfactory_all.tsv')
    for r in g:
        r['usd_lista'] = r['usd']; r['usd'] = f"{float(r['usd']) * 0.4:.2f}"; r['fijo'] = str(precio_gap(float(r['usd'])))
    sumar('gap_verano.tsv', elegir(g))
pantalones()

# Oferta del día Carter's 15/11 ("Today's Deal: $4 graphic tees & bodysuits"): todo lo de verano a USD 4, sin tope por grupo.
# Remeras a $24.900 (sin bodies sueltos: Patricio, 15/11) (mismo precio fijo que las remeras de hasta USD 4,99).
def oferta_dia(usd=4.0):
    p = os.path.join(HERE, 'carters_verano.tsv'); base = leer('carters_verano.tsv'); ya = {r['code'] for r in base}
    extra = [r for r in leer('carters_full_all.tsv') if r['code'] not in ya and abs(float(r['usd']) - usd) < 0.001
             and r['cat'] == 'Remeras' and not FUERA.search(r['nombre']) and not FUERA_EN.search(EN.get(r['code'], ''))]
    for r in base + extra:
        if r['cat'] in ('Remeras', 'Bodies') and abs(float(r['usd']) - usd) < 0.001: r['fijo'] = '19900'   # 15/11 12:10: Patricio las baja a $19.900
        if r['cat'] == 'Remeras' and float(r['usd']) <= 4.99: r['fijo'] = '19900'   # 15/11 12:10: todas las remeras Carter's/OshKosh de hasta USD 4,99 a $19.900
    seen = collections.Counter()
    for r in sorted(base + extra, key=lambda r: float(r['usd'])):
        b = re.sub(r' \(modelo \d+\)$', '', r['nombre']); seen[b] += 1
        r['nombre'] = b if seen[b] == 1 else f'{b} (modelo {seen[b]})'
    w = csv.DictWriter(open(p, 'w', encoding='utf-8', newline=''), fieldnames=list(base[0].keys()), delimiter='\t', lineterminator='\n', extrasaction='ignore')
    w.writeheader(); w.writerows(base + extra)
    print('oferta del día USD 4: se suman', len(extra), dict(collections.Counter(r['cat'] for r in extra)))
oferta_dia()

# Ropa interior (15/11, Patricio: precios "más agresivos"). H&M: packs de 5 de USD 9,99 $34.900, 12,99 $39.900, 14,99 $44.900
# (precio normal, stock verificado 15/11 en tools/hm_uw_15nov.json). Carter's: USD 9,99 $39.900, 13 $44.900, 14,99–16 $49.900.
COL_UW = [('dark green', 'Verde Oscuro'), ('navy', 'Azul Marino'), ('dark blue', 'Azul Oscuro'), ('pale blue', 'Celeste'), ('light blue', 'Celeste'),
          ('turquoise', 'Turquesa'), ('blue', 'Azul'), ('dusty pink', 'Rosa Viejo'), ('light pink', 'Rosa Claro'), ('pink', 'Rosa'), ('lilac', 'Lila'),
          ('red', 'Rojo'), ('black', 'Negro'), ('white', 'Blanco'), ('gray', 'Gris'), ('green', 'Verde'), ('cream', 'Crudo')]
MOT_UW = [('heart', 'Corazones'), ('polka', 'Lunares'), ('unicorn', 'Unicornios'), ('dinosaur', 'Dinosaurios'), ('space', 'Espacio')]
def ropa_interior():
    def talle_hm(s):
        s = s.replace('Y+', 'Y'); return s[:-1] + ' años' if s.endswith('Y') else s
    def edad_t(t):
        a = float(re.match(r'([\d½]+)', t).group(1).replace('½', '.5')); return 'Bebés' if a < 2 else ('Niños' if a < 6 else 'Grandes')
    # H&M
    p = os.path.join(HERE, 'hm_verano.tsv'); base = leer('hm_verano.tsv'); ya = {r['code'] for r in base}; extra = []
    for code, t, cat, sw, usd, tal, img in json.load(open(os.path.join(HERE, 'hm_uw_15nov.json'))):
        if code in ya: continue
        nena = 'girl' in cat; boxer = 'boxer' in cat
        tipo = 'Bóxers' if boxer else ('Bombachas' if nena else 'Slips')
        c = sw.lower(); col = next((es for en, es in COL_UW if en in c), ''); mot = next((es for en, es in MOT_UW if en in c), '')
        tl = [talle_hm(x) for x in tal.split('|')]
        extra.append(dict(code=code, cat='Ropa interior', gen='Nena' if nena else 'Nene', nombre=' '.join(x for x in (f'Pack 5 {tipo}', mot, col) if x),
                          usd=f'{usd:g}', talles='|'.join(tl), img='https://image.hm.com/assets/hm/' + img + '?imwidth=600',
                          fijo='34900' if usd < 10.5 else ('39900' if usd < 13.5 else '44900'), marca='hm', grupo='h',
                          edad='|'.join(sorted({edad_t(x) for x in tl}, key=['Bebés', 'Niños', 'Grandes'].index)), pdp=f'/en_us/productpage.{code}.html'))
    seen = collections.Counter()
    for r in extra:
        seen[r['nombre']] += 1
        if seen[r['nombre']] > 1: r['nombre'] += f" (modelo {seen[r['nombre']]})"
    w = csv.DictWriter(open(p, 'w', encoding='utf-8', newline=''), fieldnames=list(base[0].keys()), delimiter='\t', lineterminator='\n', extrasaction='ignore')
    w.writeheader(); w.writerows(base + extra)
    # Carter's
    p = os.path.join(HERE, 'carters_verano.tsv'); base = leer('carters_verano.tsv'); ya = {r['code'] for r in base}; cx = []
    for r in leer('carters_full_all.tsv'):
        if r['cat'] != 'Ropa interior' or r['code'] in ya or float(r['usd']) > 16: continue
        en = EN.get(r['code'], ''); n = re.search(r'(\d+)-Pack', en); n = n.group(1) if n else ''
        tipo = 'Bóxers' if re.search(r'Boxer', en, re.I) else ('Bombachas' if r['gen'] == 'Nena' or re.search(r'Hipster|Bikini|Boyshort|Girl', en) else 'Slips')
        resto = re.sub(r'^Ropa Interior ?', '', re.sub(r' \(modelo \d+\)$', '', r['nombre']))
        r['nombre'] = ' '.join(x for x in ((f'Pack {n} {tipo}' if n else tipo), resto) if x)
        if tipo == 'Bombachas': r['nombre'] = r['nombre'].replace('Estampada', 'Estampadas')
        else:
            for a, b in (('Estampada', 'Estampados'), ('Roja', 'Rojo'), ('Negra', 'Negro'), ('Blanca', 'Blanco'), ('Amarilla', 'Amarillo')):
                r['nombre'] = re.sub(r'\b' + a + r'\b', b, r['nombre'])
        u = float(r['usd']); r['fijo'] = '39900' if u < 10 else ('44900' if u < 14 else '49900')
        cx.append(r)
    seen = collections.Counter()
    for r in cx:
        seen[r['nombre']] += 1
        if seen[r['nombre']] > 1: r['nombre'] += f" (modelo {seen[r['nombre']]})"
    w = csv.DictWriter(open(p, 'w', encoding='utf-8', newline=''), fieldnames=list(base[0].keys()), delimiter='\t', lineterminator='\n', extrasaction='ignore')
    w.writeheader(); w.writerows(base + cx)
    print('ropa interior: H&M', len(extra), "Carter's", len(cx))
ropa_interior()


# 16/11 (Patricio): todo el swimwear. GAP Factory: trajes de baño de la búsqueda "swim" (no están en liquidación; el precio de la
# página ya trae el 60% del Cyber Sale). tools/gap_swim_16nov.json = [pid, nombre, color, usd, talles, img]. Precio fijo por escalón.
GS_COL = [('neon pink', 'Rosa Flúor'), ('pink', 'Rosa'), ('neon yellow', 'Amarillo Flúor'), ('orange', 'Naranja'), ('admiral blue', 'Azul'), ('blue', 'Azul'),
          ('hot red', 'Rojo'), ('red', 'Rojo'), ('floral', 'Floral'), ('fish', 'Peces')]
GS_MOT = [('sharks', 'Tiburones'), ('cars', 'Autos'), ('strawberr', 'Frutillas'), ('gingham', 'Vichy'), ('mickey', ''), ('minnie', '')]
def gap_swim():
    try: data = json.load(open(os.path.join(HERE, 'gap_swim_16nov.json')))
    except Exception: return
    SZ = {'6-12 M': '12M', '12-18 M': '18M', '18-24 M': '24M', '2 YRS': '2T', '3 YRS': '3T', '4 YRS': '4T', '5 YRS': '5T',
          'XS (4/5)': '4-5', 'S (6/7)': '6-7', 'M (8)': '8', 'L (10)': '10', 'XL (12)': '12', 'XXL (14/16)': '14-16'}
    p = os.path.join(HERE, 'gap_verano.tsv'); swp = {d[0] for d in data}; base = [r for r in leer('gap_verano.tsv') if r['code'] not in swp]; ya = set(); extra = []   # 16/11: las mallas de la búsqueda reemplazan a las del relevamiento de liquidación
    for pid, nm, col, usd, tal, img in data:
        tl = [SZ[x] for x in tal.split('|') if x in SZ]
        if len(tl) < 2: continue
        if 'Final sale' in nm or usd > 20: usd = round(usd * 0.4, 2)   # liquidación: 60% extra en el checkout
        if re.search(r'Two-Piece Rash Guard', nm): tipo, gen = 'Malla 2 Piezas con Remera UV', 'Nena'
        elif re.search(r'One-Piece Rash Guard', nm): tipo, gen = 'Malla Enteriza Manga Larga UV', 'Nena'
        elif re.search(r'Rash Guard', nm): tipo, gen = 'Remera UV de Agua', 'Nene' if re.search(r'cars|mickey|red', col, re.I) else 'Unisex'
        elif re.search(r'Trunks', nm): tipo, gen = 'Short de Baño', 'Nene'
        elif re.search(r'Two-Piece', nm): tipo, gen = 'Malla 2 Piezas', 'Nena'
        else: tipo, gen = 'Malla', 'Unisex'
        c = col.lower(); color = next((es for en, es in GS_COL if en in c), ''); mot = next((es for en, es in GS_MOT if en in c), '')
        nombre = ' '.join(x for x in ('GAP ·', tipo, mot, color) if x)
        fijo = '42900' if usd < 12.5 else ('47900' if usd < 14.5 else '52900')
        extra.append(dict(code=pid, cat='Mallas', gen=gen, nombre=nombre, usd=f'{usd:.2f}', talles='|'.join(tl), img=img, usd_lista=f'{usd:.2f}', fijo=fijo))
    seen = collections.Counter()
    for r in extra:
        seen[r['nombre']] += 1
        if seen[r['nombre']] > 1: r['nombre'] += f" (modelo {seen[r['nombre']]})"
    w = csv.DictWriter(open(p, 'w', encoding='utf-8', newline=''), fieldnames=list(base[0].keys()), delimiter='\t', lineterminator='\n', extrasaction='ignore')
    w.writeheader(); w.writerows(base + extra)
    print('GAP swim:', len(extra))
gap_swim()

# 16/11: Skip Hop en liquidación "a muy buen precio": al menos 50% off y hasta USD 17.
SK_NOM = {'9W583010': 'Juguete Didáctico Bandana', '9U956210': 'Botella con Sorbete CoComelon', '9U956610': 'Colectivo Musical de Peluche CoComelon',
          '9U956110': 'Vaso para Snacks CoComelon', '9T450410': 'Mochila Blippi', '9T484810': 'Vaso para Snacks Blippi', '9T484910': 'Vaso para Snacks Blippi y Meekah',
          '9T459610': 'Botella Térmica con Sorbete Blippi', '9T459710': 'Botella Térmica con Sorbete Blippi y Meekah', '9T450310': 'Mini Mochila Meekah'}
def skiphop_cl(desc=0.5):
    raw = {x['code']: x for x in json.load(open(os.path.join(HERE, 'carters_full_raw.json')))}
    p = os.path.join(HERE, 'carters_verano.tsv'); base = leer('carters_verano.tsv'); ya = {r['code'] for r in base}; extra = []
    for r in leer('carters_full_all.tsv'):
        if r.get('marca') != 'skiphop' or r['code'] in ya: continue
        x = raw.get(r['code'], {}); lst = x.get('list') or 0; u = float(r['usd'])
        if u > MAX or not lst or u > lst * (1 - desc): continue
        r['nombre'] = SK_NOM.get(r['code'], r['nombre']); extra.append(r)
    w = csv.DictWriter(open(p, 'w', encoding='utf-8', newline=''), fieldnames=list(base[0].keys()), delimiter='\t', lineterminator='\n', extrasaction='ignore')
    w.writeheader(); w.writerows(base + extra)
    print('Skip Hop liquidación:', len(extra), dict(collections.Counter(r['cat'] for r in extra)))
# skiphop_cl()   # 16/11 9:00: Patricio lo saca (no hay nada a buen precio en Skip Hop)


# 16/11: precio de mallas en todas las marcas (con la fórmula, las de USD 13–16 quedaban en $60.000–71.000).
# Hasta USD 12,99 siguen la fórmula con tramos (≤ $44.900); USD 13–14,99 → $47.900; USD 15 o más → $52.900.
def mallas_precio():
    for f in ('carters_verano.tsv', 'gap_verano.tsv'):
        p = os.path.join(HERE, f); rows = leer(f)
        for r in rows:
            if r['cat'] != 'Mallas': continue
            u = float(r['usd'])
            if 13 <= u < 15: r['fijo'] = '47900'
            elif u >= 15: r['fijo'] = '52900'
        w = csv.DictWriter(open(p, 'w', encoding='utf-8', newline=''), fieldnames=list(rows[0].keys()), delimiter='\t', lineterminator='\n', extrasaction='ignore')
        w.writeheader(); w.writerows(rows)
mallas_precio()

# 16/11: trajes de baño H&M (categoría Swimwear de kids y baby), precio normal hasta USD 17, stock del 16/11.
# tools/hm_swim_16nov.json = [code, título, categoría, color, w, red, talles con stock, img]
def hm_swim():
    try: data = json.load(open(os.path.join(HERE, 'hm_swim_16nov.json')))
    except Exception: return
    def talle_hm(s):
        s = s.replace('Y+', 'Y'); return s[:-1] + ' años' if s.endswith('Y') else s.replace('M', 'M')
    def edad_t(t):
        if t.endswith('M'): return 'Bebés'
        a = float(re.match(r'([\d½]+)', t).group(1).replace('½', '.5')); return 'Bebés' if a < 2 else ('Niños' if a < 6 else 'Grandes')
    p = os.path.join(HERE, 'hm_verano.tsv'); base = leer('hm_verano.tsv'); ya = {r['code'] for r in base}; extra = []
    for code, t, cat, sw, w, red, tal, img in data:
        if code in ya or len(tal) < 2: continue
        u = min(x for x in (w, red) if x)
        if u > MAX: continue
        tl = t.lower(); nena = 'girl' in cat
        if 'bikini' in tl: tipo = 'Bikini'
        elif 'shorts' in tl or 'trunks' in tl: tipo = 'Short de Baño'
        elif 'rash' in tl or 'upf' in tl and 'top' in tl: tipo = 'Remera UV de Agua'
        elif 'set' in tl: tipo = 'Set de Baño UPF 50' if 'upf' in tl else 'Set de Baño'
        elif 'swimsuit' in tl or 'swimwear' in tl: tipo = 'Malla Enteriza'
        else: tipo = 'Malla'
        c = sw.lower(); col = next((es for en, es in COL_UW if en in c), ''); mot = next((es for en, es in MOT_UW + [('shark', 'Tiburones'), ('fish', 'Peces'), ('floral', 'Floral'), ('stripe', 'Rayas'), ('fruit', 'Frutas')] if en in c), '')
        tls = [talle_hm(x) for x in tal]
        fijo = '' if u < 13 else ('47900' if u < 15 else '52900')
        extra.append(dict(code=code, cat='Mallas', gen='Nena' if nena else ('Nene' if 'boy' in cat else 'Unisex'), nombre=' '.join(x for x in (tipo, mot, col) if x),
                          usd=f'{u:g}', talles='|'.join(tls), img=img, fijo=fijo, marca='hm', grupo='h',
                          edad='|'.join(sorted({edad_t(x) for x in tls}, key=['Bebés', 'Niños', 'Grandes'].index)), pdp=f'/en_us/productpage.{code}.html'))
    seen = collections.Counter()
    for r in extra:
        seen[r['nombre']] += 1
        if seen[r['nombre']] > 1: r['nombre'] += f" (modelo {seen[r['nombre']]})"
    w_ = csv.DictWriter(open(p, 'w', encoding='utf-8', newline=''), fieldnames=list(base[0].keys()), delimiter='\t', lineterminator='\n', extrasaction='ignore')
    w_.writeheader(); w_.writerows(base + extra)
    print('H&M swim:', len(extra))
hm_swim()

# 16/11: los "Baby Swim Bucket Hat" de GAP salían como "Malla": son gorros para el agua (quedan en la categoría Mallas).
def gap_gorros():
    try: gr = {x['pid']: x for x in json.load(open(os.path.join(HERE, 'gf_raw.json')))}
    except Exception: return
    p = os.path.join(HERE, 'gap_verano.tsv'); rows = leer('gap_verano.tsv')
    for r in rows:
        x = gr.get(r['code'])
        if x and re.search(r'Bucket Hat|Sun Hat|Swim Hat', x.get('name', ''), re.I):
            r['nombre'] = re.sub(r'GAP · Malla', 'GAP · Gorro de Sol para el Agua', r['nombre']); r['cat'] = 'Mallas'
    w = csv.DictWriter(open(p, 'w', encoding='utf-8', newline=''), fieldnames=list(rows[0].keys()), delimiter='\t', lineterminator='\n', extrasaction='ignore')
    w.writeheader(); w.writerows(rows)
gap_gorros()

# 16/11 (Patricio pregunta por los gorros de H&M): gorras y gorros de sol de H&M (categorías Hats de kids y baby), hasta USD 17.
# Precio fijo: hasta USD 10 $32.900; hasta USD 13 $37.900; hasta USD 15 $42.900. Con 1 talle alcanza (son de talle amplio).
def hm_gorros():
    try: data = json.load(open(os.path.join(HERE, 'hm_gorros_16nov.json')))
    except Exception: return
    def talle(s): return s[:-1] + ' años' if s.endswith('Y') else s
    def edad_t(t):
        if t.endswith('M'): return 'Bebés'
        a = float(re.match(r'([\d½]+)', t).group(1).replace('½', '.5')); return 'Bebés' if a < 2 else ('Niños' if a < 6 else 'Grandes')
    p = os.path.join(HERE, 'hm_verano.tsv'); base = leer('hm_verano.tsv'); ya = {r['code'] for r in base}; extra = []
    for code, t, cat, sw, w, red, tal, img in data:
        if code in ya or not tal: continue
        u = min(x for x in (w, red) if x)
        tl = t.lower()
        if 'straw' in tl: tipo = 'Sombrero de Paja'
        elif 'bucket' in tl: tipo = 'Piluso'
        elif '2-pack' in tl and 'sun hat' in tl: tipo = 'Pack 2 Gorros de Sol'
        elif 'sun cap' in tl: tipo = 'Gorra con Cubrenuca UPF 50'
        elif 'wide-brim' in tl: tipo = 'Sombrero de Sol Ala Ancha'
        elif 'sun hat' in tl: tipo = 'Gorro de Sol'
        elif 'trucker' in tl: tipo = 'Gorra Trucker'
        elif 'water-repellent' in tl: tipo = 'Gorra Deportiva Impermeable'
        else: tipo = 'Gorra'
        if 'linen' in tl and tipo in ('Gorro de Sol', 'Piluso'): tipo += ' de Lino'
        c = sw.lower(); col = next((es for en, es in COL_UW + [('beige', 'Beige'), ('brown', 'Marrón'), ('khaki', 'Verde Militar'), ('taupe', 'Topo'), ('purple', 'Lila'), ('dusty green', 'Verde')] if en in c), '')
        mot = next((es for en, es in MOT_UW + [('floral', 'Floral'), ('cherr', 'Cerezas'), ('lemon', 'Limones'), ('cars', 'Autos'), ('dinosaur', 'Dinosaurios')] if en in c), '')
        tls = [talle(x) for x in tal]
        if tipo.startswith('Gorra') and col: col = {'Blanco': 'Blanca', 'Rojo': 'Roja', 'Negro': 'Negra', 'Amarillo': 'Amarillo'}.get(col, col)
        fijo = '32900' if u < 10.5 else ('37900' if u < 13.5 else '42900')
        gen = 'Nena' if 'girl' in cat else ('Nene' if 'boys' in cat else 'Unisex')
        extra.append(dict(code=code, cat='Accesorios', gen=gen, nombre=' '.join(x for x in (tipo, mot, col) if x), usd=f'{u:g}', talles='|'.join(tls), img='https://image.hm.com/assets/hm/' + img,
                          fijo=fijo, marca='hm', grupo='h', edad='|'.join(sorted({edad_t(x) for x in tls}, key=['Bebés', 'Niños', 'Grandes'].index)), pdp=f'/en_us/productpage.{code}.html'))
    seen = collections.Counter()
    for r in extra:
        seen[r['nombre']] += 1
        if seen[r['nombre']] > 1: r['nombre'] += f" (modelo {seen[r['nombre']]})"
    w_ = csv.DictWriter(open(p, 'w', encoding='utf-8', newline=''), fieldnames=list(base[0].keys()), delimiter='\t', lineterminator='\n', extrasaction='ignore')
    w_.writeheader(); w_.writerows(base + extra)
    print('H&M gorros:', len(extra))
hm_gorros()

# 16/11: liquidación (Sale) de H&M: trajes de baño y gorros de sol que estaban en oferta (USD 1,99–7,49) y no aparecían en las
# secciones normales. tools/hm_sale_16nov.json = [code, título, categoría, color, w, red, talles con stock, img].
# Precio: < USD 5 $19.900; < USD 8 $29.900; < USD 10 $32.900; desde USD 10 como el resto de los trajes de baño.
def hm_sale():
    try: data = json.load(open(os.path.join(HERE, 'hm_sale_16nov.json')))
    except Exception: return
    def talle(s): return 'Único' if s.upper() == 'ONESIZE' else (s[:-1] + ' años' if s.endswith('Y') else s)
    def edad_t(t):
        if t.endswith('M'): return 'Bebés'
        if not re.match(r'[\d½]', t): return 'Grandes'
        a = float(re.match(r'([\d½]+)', t).group(1).replace('½', '.5')); return 'Bebés' if a < 2 else ('Niños' if a < 6 else 'Grandes')
    p = os.path.join(HERE, 'hm_verano.tsv'); base = leer('hm_verano.tsv'); ya = {r['code'] for r in base}; extra = []
    for code, t, cat, sw, w, red, tal, img in data:
        if code in ya or not tal: continue
        u = min(x for x in (w, red) if x)
        if u > MAX: continue
        tl = t.lower(); gorro = bool(re.search(r'\bhat\b|\bcap\b|hats\b', tl)); acc = 'poncho' in tl or 'sarong' in tl
        if not (gorro or acc) and len(tal) < 2: continue
        if acc:
            tipo = 'Toallón Poncho de Muselina' if 'poncho' in tl else 'Pareo'; categ = 'Mallas'
        elif gorro:
            if 'sun cap' in tl: tipo = 'Gorra con Cubrenuca UPF 50'
            elif 'bucket' in tl: tipo = 'Piluso'
            elif '2-pack' in tl: tipo = 'Pack 2 Gorros de Sol'
            elif 'sun hat' in tl: tipo = 'Gorro de Sol'
            else: tipo = 'Gorra'
            categ = 'Accesorios'
        else:
            if 'bikini' in tl: tipo = 'Bikini'
            elif 'shirt' in tl or 'rash' in tl: tipo = 'Remera UV de Agua'
            elif 'trunks' in tl or 'shorts' in tl: tipo = 'Short de Baño'
            elif 'briefs' in tl: tipo = 'Pack 2 Bombachas de Baño' if '2-pack' in tl else 'Bombacha de Baño'
            elif 'set' in tl: tipo = 'Set de Baño UPF 50' if 'upf' in tl else 'Set de Baño'
            else: tipo = 'Malla Enteriza'
            if 'upf' in tl and 'UPF' not in tipo: tipo += ' UPF 50'
            categ = 'Mallas'
        c = sw.lower(); col = next((es for en, es in COL_UW + [('beige', 'Beige'), ('brown', 'Marrón'), ('khaki', 'Verde Militar'), ('purple', 'Lila'), ('yellow', 'Amarillo'), ('orange', 'Naranja')] if en in c), '')
        mot = next((es for en, es in MOT_UW + [('floral', 'Floral'), ('stripe', 'Rayas'), ('fish', 'Peces'), ('shark', 'Tiburones'), ('dinosaur', 'Dinosaurios'), ('fruit', 'Frutas'), ('cherr', 'Cerezas')] if en in c), '')
        if tipo.startswith('Gorra') and col: col = {'Blanco': 'Blanca', 'Rojo': 'Roja', 'Negro': 'Negra'}.get(col, col)
        tls = [talle(x) for x in tal]
        fijo = '19900' if u < 5 else ('29900' if u < 8 else ('32900' if u < 10 else ('' if u < 13 else ('47900' if u < 15 else '52900'))))
        gen = 'Nena' if 'girl' in cat else ('Nene' if 'boy' in cat else 'Unisex')
        extra.append(dict(code=code, cat=categ, gen=gen, nombre=' '.join(x for x in (tipo, mot, col) if x), usd=f'{u:g}', talles='|'.join(tls), img=img,
                          fijo=fijo, marca='hm', grupo='h', edad='|'.join(sorted({edad_t(x) for x in tls}, key=['Bebés', 'Niños', 'Grandes'].index)), pdp=f'/en_us/productpage.{code}.html'))
    seen = collections.Counter(r['nombre'] for r in base)
    for r in extra:
        seen[r['nombre']] += 1
        if seen[r['nombre']] > 1: r['nombre'] += f" (modelo {seen[r['nombre']]})"
    w_ = csv.DictWriter(open(p, 'w', encoding='utf-8', newline=''), fieldnames=list(base[0].keys()), delimiter='\t', lineterminator='\n', extrasaction='ignore')
    w_.writeheader(); w_.writerows(base + extra)
    print('H&M liquidación (trajes de baño y gorros):', len(extra), dict(collections.Counter(r['cat'] for r in extra)))
hm_sale()
