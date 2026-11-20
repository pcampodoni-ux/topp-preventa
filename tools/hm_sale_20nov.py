#!/usr/bin/env python3
"""20/11 (Patricio: "¿hay productos para agregar en H&M?"): liquidación de H&M de hoy (baby, 2-8 y 9-14),
solo ropa de verano hasta USD 10 que no estaba publicada y con al menos 2 talles en stock (los gorros pueden tener 1).
tools/hm_sale_20nov.json = [code, título, categoría, color, w, red, talles con stock, img] (leído desde el navegador).
Precio como la liquidación del 16-17/11: < USD 5 $19.900; < USD 8 $29.900; hasta USD 10 $32.900.
Packs de bodies: sin precio fijo (fórmula con tramos, como los demás packs de H&M).
Agrega a tools/hm_verano.tsv y a tools/revision/esperado.json (para que la revisión siga su stock y precio)."""
import csv, json, os, re, collections
T = os.path.dirname(os.path.abspath(__file__))
COL = [('dusty green', 'Verde Agua'), ('light beige', 'Beige'), ('beige', 'Beige'), ('light pink', 'Rosa Claro'), ('pink', 'Rosa'), ('white', 'Blanco'),
       ('dark gray', 'Gris Oscuro'), ('light blue', 'Celeste'), ('blue', 'Azul')]
MOT = [('cherries', 'Cerezas'), ('striped', 'Rayas'), ('strawberr', 'Frutillas'), ('floral', 'Flores'), ('gingham', 'Cuadrillé'), ('lilo & stitch', 'Lilo & Stitch')]
TIPOS = [(r'2-pack.*sun hats', 'Mallas', 'Pack 2 Gorros de Sol de Muselina'), (r'sun hat', 'Mallas', 'Gorro de Sol UPF 50'),
         (r'3-pack.*bodysuits', 'Packs de Bodies', 'Pack 3 Bodies Morley'), (r'2-pack henley bodysuits', 'Packs de Bodies', 'Pack 2 Bodies Henley'),
         (r'2-piece ribbed', 'Sets 2 Piezas', 'Set 2 Piezas Morley'), (r'romper', 'Enteritos', 'Enterito de Lino'),
         (r'short-sleeved cotton shirt', 'Remeras', 'Camisa Manga Corta de Algodón'), (r'pointelle', 'Remeras', 'Remera Calada'),
         (r't-shirt', 'Remeras', 'Remera Estampada de Algodón'), (r'smocked dress', 'Vestidos', 'Vestido Smock')]
FEM = {'Remera', 'Camisa'}
def talle(s): s = s.replace('Y+', 'Y'); return s[:-1] + ' años' if s.endswith('Y') else s
def edad_t(t):
    if t.endswith('M'): return 'Bebés'
    a = float(re.match(r'([\d½]+)', t).group(1).replace('½', '.5')); return 'Bebés' if a < 2 else ('Niños' if a < 6 else 'Grandes')
def leer(f): return list(csv.DictReader(open(os.path.join(T, f), encoding='utf-8'), delimiter='\t'))
p = os.path.join(T, 'hm_verano.tsv'); base = leer('hm_verano.tsv'); campos = list(base[0].keys()); ya = {r['code'] for r in base}
E = json.load(open(os.path.join(T, 'revision', 'esperado.json')))
extra = []
for code, t, cat, sw, w, red, tal, img in json.load(open(os.path.join(T, 'hm_sale_20nov.json'))):
    if code in ya: continue
    u = min(x for x in (w, red) if x); tl = t.lower()
    categ, tipo = next((c_, n_) for pat, c_, n_ in TIPOS if re.search(pat, tl))
    if categ != 'Mallas' and len(tal) < 2: continue
    c = sw.lower(); col = next((es for en, es in COL if en in c), ''); mot = next((es for en, es in MOT if en in c), '')
    if tipo.split()[0] in FEM and col: col = {'Blanco': 'Blanca'}.get(col, col)
    tls = [talle(x) for x in tal]
    fijo = '' if categ == 'Packs de Bodies' else ('19900' if u < 5 else ('29900' if u < 8 else '32900'))
    gen = 'Nena' if ('girl' in cat or categ == 'Vestidos' or 'pink' in c) else ('Nene' if 'boy' in cat else 'Unisex')
    if categ in ('Packs de Bodies', 'Mallas', 'Enteritos'): gen = 'Unisex' if 'pink' not in c else 'Nena'
    extra.append(dict(code=code, cat=categ, gen=gen, nombre=' '.join(x for x in (tipo, mot, col) if x), usd=f'{u:g}', talles='|'.join(tls),
                      img='https://image.hm.com/assets/hm/' + img, fijo=fijo, marca='hm', grupo='h',
                      edad='|'.join(sorted({edad_t(x) for x in tls}, key=['Bebés', 'Niños', 'Grandes'].index)), pdp=f'/en_us/productpage.{code}.html'))
    E['hm'][code] = {'s': tal, 'u': u}
seen = collections.Counter(re.sub(r' \(modelo \d+\)$', '', r['nombre']) for r in base)
for r in extra:
    seen[r['nombre']] += 1
    if seen[r['nombre']] > 1: r['nombre'] += f" (modelo {seen[r['nombre']]})"
w_ = csv.DictWriter(open(p, 'w', encoding='utf-8', newline=''), fieldnames=campos, delimiter='\t', lineterminator='\n', extrasaction='ignore')
w_.writeheader(); w_.writerows(base + extra)
json.dump(E, open(os.path.join(T, 'revision', 'esperado.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
print('H&M liquidación 20/11:', len(extra))
for r in extra: print(' ', r['cat'], '|', r['nombre'], '|', r['usd'], '|', r['talles'], '|', r['fijo'] or 'fórmula')
