#!/usr/bin/env python3
"""20/11 (Patricio: "agregame más productos de H&M, los de invierno que estén en muy buen precio, liquidaciones"):
liquidación de invierno de H&M (baby, 2-8 y 9-14) leída hoy desde el navegador (listados de sale + página de cada producto).
Criterio: abrigo/invierno (buzos, sweaters, camperas, calzas, joggers, pantalones, pijamas, manga larga, gorro),
precio de liquidación hasta USD 12,99 (lo de USD 13–15 quedaba en $63.000–78.000 y se sacó; también el gorro de merino a $36.990), al menos 2 talles en stock, sin Halloween, sin jeans/jeggings ni calzado.
Precio: fórmula ×1,9 con flete por peso real (USD 26,5/kg + 0,85 por prenda; accesorios USD 3,50), luego piso de
$29.900 (30.300–35.000) y tramos por USD (como armar_pedido). Los precios de la liquidación de verano (< USD 5 $19.900,
< USD 8 $29.900) no sirven acá: un set de buzo + calza de ~300 g a USD 9,99 cuesta ~$31.000 puesto en Corrientes.
Agrega a tools/hm_verano.tsv y a tools/revision/esperado.json (para que la revisión siga stock y precio)."""
import csv, json, os, re, sys
T = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, T)
import precio as P

# code, categoría, género, nombre, peso_g, USD (liquidación), talles con stock, imagen
D = [
 ('1362341008', 'Sets 2 Piezas', 'Nena', 'Set Buzo y Calza Lilo & Stitch Rosa', 300, 9.99, '1½-2Y|2-3Y|3-4Y|4-5Y|5-6Y|6-7Y|7-8Y|8-9Y|9-10Y', '1c/6c/1c6c9716648b560849112ab479a821d2053775ba.jpg'),
 ('1308059002', 'Sets 2 Piezas', 'Nene', 'Set Buzo y Jogger Frisado Negro', 330, 11.99, '4-6M|6-9M|9-12M|12-18M', '36/96/3696c2bb25334bd9b6712153af9fe25b6c2d7abf.jpg'),
 ('1341325034', 'Buzos', 'Nena', 'Buzo Frisado Osito Rosa', 200, 5.99, '1½-2Y|2-4Y|4-6Y|8-10Y', 'c5/19/c5199c1e3fbcba90f98eac62599ff03d001701e9.jpg'),
 ('1366825004', 'Buzos', 'Nena', 'Buzo Oversize Lilo & Stitch Beige', 220, 6.99, '2-4Y|4-6Y|6-8Y|8-10Y', '46/dd/46dd7696c13b9f3bcbb2ce1d4d7ed229d71be515.jpg'),
 ('1268555002', 'Buzos', 'Nena', 'Buzo Estampado Durazno', 180, 6.99, '1½-2Y|2-3Y', 'ca/17/ca1774d73b7a4a6868d003a48fb1cc44b804fb34.jpg'),
 ('1296500002', 'Buzos', 'Nene', 'Buzo Frisado Dinosaurio Blanco', 200, 9.49, '2-3Y|3-4Y', 'cc/01/cc0143b56e649c25a9b1c2fc09a83251df34ff95.jpg'),
 ('1243063066', 'Buzos', 'Nena', 'Buzo Carpincho Rosa Claro', 200, 9.99, '1½-2Y|2-4Y', '18/96/1896ab81090692c28b7d5cb7ae6b97a9e686bdbf.jpg'),
 ('1267711042', 'Buzos', 'Nena', 'Buzo Lilo & Stitch Beige', 200, 9.99, '1½-2Y|2-4Y', '53/65/5365fe60cd551d19b3ace7fba25c2eaa21e8970a.jpg'),
 ('1353712001', 'Buzos', 'Nena', 'Buzo Frisado Estampado Negro', 200, 9.99, '1½-2Y|2-4Y', '2d/09/2d09684544c10f478e28ece73ded1cc5cd5b1ced.jpg'),
 ('1345886002', 'Buzos', 'Nena', 'Sweater Osito Beige', 220, 12.49, '1½-2Y|2-4Y', '16/af/16aff509972d4051cdc068096de153623626b5f7.jpg'),
 ('1273982001', 'Camperas', 'Nene', 'Chaleco de Gabardina Beige', 120, 3.99, '4-6M|6-9M|9-12M|12-18M|1½-2Y|2-3Y|3-4Y', '49/4f/494f8d0f252081a87dc15a7457237149e635e519.jpg'),
 ('1257523001', 'Camperas', 'Nene', 'Chaleco Jacquard Negro', 120, 6.99, '4-6M|9-12M|12-18M|1½-2Y|2-3Y|3-4Y', '7c/fb/7cfbbf69b15c17229d547823bf4514b0903fc0c5.jpg'),
 ('1281685001', 'Camperas', 'Nena', 'Campera Jacquard Flores Azul', 300, 11.99, '3-4Y|4-5Y|8-9Y|9-10Y', '28/79/28793a1fa7b0d99322e7a7a0b005db24f4b3615e.jpg'),
 ('1325889002', 'Camperas', 'Nena', 'Campera Polar Teddy Corazones Blanca', 280, 12.49, '1½-2Y|2-4Y', '5f/16/5f167bfba6f61a1c731e8dcf9a6e317193c507ef.jpg'),
 ('1314148002', 'Camperas', 'Nena', 'Campera de Gabardina con Volados Lila', 280, 12.49, '1½-2Y|2-3Y', 'a5/33/a5337b21e74374c1b73dfc00be73d3ccdfc7c938.jpg'),
 ('1286039009', 'Camperas', 'Nene', 'Campera Frisada con Capucha Celeste', 320, 12.49, '8-10Y|10-12Y', 'd8/1b/d81be727081859074433aea17cecbfc3267c3006.jpg'),
 ('1299492008', 'Camperas', 'Nena', 'Campera Frisada con Capucha Rosa Claro', 350, 12.49, '12-14Y|14Y+', 'ba/11/ba11f9be0d0327eac5dcd7d9df142e5b2c9b1a2c.jpg'),
 ('1245043002', 'Pantalones', 'Nena', 'Calza con Alforzas Negra', 80, 3.99, '4-6M|6-9M|9-12M|12-18M|1½-2Y|2-3Y', 'c7/65/c7650b1adc806817d76f07af840ae5eea25238c2.jpg'),
 ('1292894001', 'Pantalones', 'Unisex', 'Pantalón de Gabardina Lilo & Stitch Beige', 150, 5.99, '4-6M|6-9M|9-12M|12-18M|1½-2Y', '50/7c/507c8548a7efe41bcfc739f75fd9b31aa2ac5d5f.jpg'),
 ('1313585003', 'Pantalones', 'Unisex', 'Calza de Algodón Pima Marrón', 60, 6.49, '0-1M|6-9M', '22/08/2208296ae9f133018748be47e182ef8d75f74245.jpg'),
 ('1343386003', 'Pantalones', 'Nena', 'Calza Oxford Flores Lila', 100, 6.49, '1½-2Y|2-3Y', 'fb/e9/fbe9069a7fd130f89e0c3035aa6305f928a9984f.jpg'),
 ('1313585001', 'Pantalones', 'Unisex', 'Calza de Algodón Pima Celeste', 60, 7.99, '0-1M|1-2M|2-4M', 'a1/3b/a13ba028cc0a1828ba2d6cc04d58b1a7f84479a9.jpg'),
 ('1231781004', 'Pantalones', 'Unisex', 'Calza Morley Beige', 60, 7.99, '0-1M|1-2M', '04/0d/040dd51ffea9a2967c774059d91c09bd0a65ba5e.jpg'),
 ('1245253016', 'Pantalones', 'Nena', 'Calza Oxford Negra con Brillos', 120, 9.99, '1½-2Y|2-3Y', '47/5d/475d315e30c5184b7a165deadff5164854bb945b.jpg'),
 ('1353069005', 'Pantalones', 'Nena', 'Calza Deportiva Lila', 120, 9.99, '4-5Y|5-6Y', 'b1/d6/b1d637cd088da34ecb349e253387f67bf0c6c1d1.jpg'),
 ('1211290025', 'Pantalones', 'Nene', 'Jogger Cargo Frisado Gris', 200, 9.99, '1½-2Y|2-3Y', '88/40/88406a78c379fc5e481b1d26195b0164063b9b25.jpg'),
 ('1308028012', 'Pantalones', 'Nene', 'Jogger Bordado Gris Oscuro', 200, 9.99, '1½-2Y|2-3Y', '0f/3f/0f3f2bf30940da8579959f73b46e442e975be6bf.jpg'),
 ('1332470002', 'Pantalones', 'Unisex', 'Jogger Frisado Negro', 200, 9.99, '1½-2Y|2-3Y', 'b9/36/b93669ebb7cd9fb5ca6c53366e72748607b7469f.jpg'),
 ('0916397030', 'Pantalones', 'Nena', 'Pack 3 Calzas de Algodón Rosa y Blanco', 300, 9.99, '6-7Y|8-9Y', '2c/35/2c359144e0dcdbb0fbc8f655c49390c5ddd3c594.jpg'),
 ('1260989001', 'Pantalones', 'Unisex', 'Pack 2 Calzas de Algodón Pima Negro y Marrón', 120, 10.99, '0-1M|1-2M', '00/01/00014264cdcfd6e1d6ed7d4f41919cd999d30b2d.jpg'),
 ('1313707002', 'Pantalones', 'Nena', 'Pantalón Oxford Negro Rayado', 150, 11.99, '1½-2Y|2-3Y|3-4Y|4-5Y', 'f3/73/f373c030eb3d16376a9bc53d0f28e14736e4ba4c.jpg'),
 ('1291272013', 'Pantalones', 'Nena', 'Pack 2 Calzas Oxford Lila y Gris', 220, 12.49, '1½-2Y|2-3Y', 'a6/be/a6be244fe77e36d24b47fb3b58bf417078c32c8d.jpg'),
 ('1145359010', 'Remeras', 'Nene', 'Pack 2 Remeras Manga Larga Vehículos Celeste', 120, 6.49, '1-2M|2-4M', 'c5/a4/c5a448516b4566442ba30bd9c20330eb0ceddc5c.jpg'),
 ('1244756001', 'Remeras', 'Nena', 'Pack 2 Remeras Manga Larga Morley Gris Oscuro', 180, 9.99, '2-4Y|4-6Y', '97/33/973308bd74970dcae9925b28d83f14936b5a1150.jpg'),
 ('1092245046', 'Pijamas', 'Nene', 'Pack 2 Pijamas Superman Celeste', 250, 12.49, '0-1M|1-2M', '88/b4/88b41e67a7ebe39a390fa2239cb6e9661e365a49.jpg'),
 ('1333816001', 'Pijamas', 'Unisex', 'Pack 2 Pijamas Enteritos Mickey Gris', 250, 12.49, '0-1M|1-2M', '4e/bd/4ebde79e6b936b99f6187955b71da3cfc3efb71e.jpg'),
 ('1280451001', 'Pijamas', 'Nena', 'Pijama de Algodón Lilo & Stitch', 300, 12.49, '13Y|14Y', '4c/7b/4c7bbab79ad8314bbdd0c7c083e8103efb12f5d6.jpg'),
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
print('H&M invierno 20/11:', len(extra))
for r in extra: print(f"  {r['cat']:<13} | {r['nombre']:<48} | USD {r['usd']:<5} | ${int(r['fijo']):,}".replace(',', '.'), '|', r['talles'])
