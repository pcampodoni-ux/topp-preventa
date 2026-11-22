#!/usr/bin/env python3
"""22/11 (Patricio: "veamos todo GAP, H&M y agreguemos lo que podamos"): liquidación de H&M de hoy (baby, 2-8 y 9-14; ~780 productos
en sale) leída desde el navegador (listados + página de cada producto). Lo que no estaba publicado, precio de liquidación hasta USD 12,99
y al menos 2 talles en stock. Sin Halloween (fantasmas, calabazas, esqueletos, murciélagos), sin fundas de celular, sin gorro de merino
(ya se había descartado por caro) y sin la remera lisa blanca de USD 12,99 de recién nacido.
Precio como hm_invierno_20nov.py: fórmula ×1,9 con flete por peso real (USD 26,5/kg + 0,85 por prenda), piso de $29.900 y tramos por USD.
Agrega a tools/hm_verano.tsv y a tools/revision/esperado.json (para que la revisión siga stock y precio)."""
import csv, json, os, re, sys
T = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, T)
import precio as P

# code, categoría, género, nombre, peso_g, USD (liquidación), talles con stock, imagen
D = [
 ('1147423017', 'Sets 2 Piezas', 'Unisex', 'Set 2 Piezas Morley Ositos Verde Agua', 120, 10.49, '1½-2Y|2-3Y|3-4Y', 'ea/a5/eaa5f74cbcc6af50e2207729c23fc0870140dc96.jpg'),
 ('1220090004', 'Shorts', 'Nene', 'Pack 4 Shorts de Jersey Verde y Azul', 160, 11.49, '1-2M|1½-2Y', '2b/f3/2bf33921a92de87296bfe96e38f89af7e2036933.jpg'),
 ('1232182001', 'Vestidos', 'Nena', 'Pollera Plisada Negra', 120, 9.99, '7-8Y|9-10Y', 'c9/91/c991ca59d7c77995855c9117409e395bfccbc796.jpg'),
 ('1262117006', 'Shorts', 'Nena', 'Pack 2 Calzas Cortas Morley Verde Agua Estampadas', 70, 11.99, '0-1M|1-2M', '72/4a/724a961077fc5bc5155deecad60b48a1c4360e20.jpg'),
 ('1270903001', 'Jardineros', 'Nene', 'Jardinero Short de Jean Azul', 200, 11.99, '4-6M|6-9M', '6e/9a/6e9a5e71cec40497fec176da5fa450ee4951c75d.jpg'),
 ('1270903002', 'Jardineros', 'Nene', 'Jardinero Short Beige', 200, 11.49, '4-6M|6-9M', '84/08/8408338a5d96554659d59e06581c4c597841aa6c.jpg'),
 ('1289975001', 'Jardineros', 'Nene', 'Jardinero Short de Jean Bordado Autos', 200, 12.49, '4-6M|6-9M', '3e/3a/3e3a1ec3fed1802770dd89fed34464acf0f000e2.jpg'),
 ('1273967001', 'Vestidos', 'Nena', 'Pollera Crinkle Crudo', 100, 11.49, '1½-2Y|2-3Y', '35/e6/35e66451f58733b76e8231e77f4ba135240d5d25.jpg'),
 ('1275329001', 'Shorts', 'Nene', 'Bermuda de Lino Crudo', 120, 11.99, '2-3Y|3-4Y|4-5Y|5-6Y|6-7Y|7-8Y|8-9Y|9-10Y', '50/4e/504e0ee49982912076f90cf494046f4c9cf0ceb4.jpg'),
 ('1290769002', 'Shorts', 'Nene', 'Short Cargo Verde', 100, 11.99, '1½-2Y|2-3Y', '25/25/252547ce9966df4d74ed19e8a455e6e4e4900584.jpg'),
 ('1283503001', 'Enteritos', 'Unisex', 'Enterito de Seersucker Beige', 120, 11.49, '1-2M|2-4M|4-6M|6-9M', 'bb/ba/bbba62d447c770e10702813621616f28fe41b21f.jpg'),
 ('1312974002', 'Enteritos', 'Nena', 'Enterito de Algodón Verde Flores', 120, 12.99, '0-1M|1-2M', 'b1/86/b1864944b50338b3986184ac708922bd40bf23b4.jpg'),
 ('1323632004', 'Enteritos', 'Nena', 'Enterito de Algodón Frambuesa', 120, 12.99, '0-1M|1-2M', '1b/54/1b5440a88ae9a7ae76de8c63d88bb6e51bf9032b.jpg'),
 ('1333699001', 'Enteritos', 'Nena', 'Enterito con Volados Blanco Flores', 100, 11.99, '1-2M|2-4M', '00/79/0079135e1ce6fad9a9197963155289d7ddb2f08e.jpg'),
 ('1323832002', 'Sets 2 Piezas', 'Unisex', 'Set 2 Piezas Waffle Beige', 150, 12.49, '0-1M|1-2M', '8d/3d/8d3d730d2ebff87db7098b4fa64cd7e8c4f82189.jpg'),
 ('1330555002', 'Vestidos', 'Nena', 'Vestido con Volados Blanco Flores', 120, 12.49, '1½-2Y|2-3Y', 'ae/4c/ae4c2d300ea509501e2e8a47158656a4f2030525.jpg'),
 ('1289756010', 'Remeras', 'Nene', 'Camisa Cuello Mao Autos Cruda', 150, 9.99, '8-9Y|9-10Y', '17/90/1790559f3a672cf17ee08d45516b5f1c7afa1df3.jpg'),
 ('1291103001', 'Remeras', 'Nena', 'Blusa de Jean Bordada Flores', 150, 12.49, '4-6M|6-9M|9-12M|12-18M|1½-2Y|2-3Y|3-4Y', '36/0e/360e9541911e947022934bf4962ee3ba3970b070.jpg'),
 ('1315195001', 'Remeras', 'Nena', 'Blusa Manga Globo Blanca Flores', 100, 11.49, '1½-2Y|2-3Y|3-4Y|4-5Y|5-6Y|6-7Y', '1c/90/1c902c8a5edc53fc60b87309dc60e0a9902af5f1.jpg'),
 ('1348032002', 'Remeras', 'Nena', 'Blusa de Algodón Blanca Flores', 80, 11.49, '4-6M|6-9M', '9c/13/9c13c39051f35837f8efc796df87beb1c87c1d89.jpg'),
 ('1351204002', 'Remeras', 'Nena', 'Blusa Smock Rosa Claro Flores', 100, 12.49, '1½-2Y|9-10Y', '37/2a/372a7c897d7e13364373a26152cd1b9baf4a3f78.jpg'),
 ('1319652001', 'Remeras', 'Nena', 'Remera Manga Larga con Tul Rosa Claro', 100, 9.99, '1½-2Y|2-4Y', '16/e9/16e90beae55e50f0a16ea37034c10c486d1e6b0f.jpg'),
 ('1346177001', 'Remeras', 'Nena', 'Remera Frisada Carpincho Cruda', 150, 7.49, '1½-2Y|2-4Y', '7e/ac/7eac4e04a35e322ac1d10c069a6f98d904704b6f.jpg'),
 ('1353711001', 'Remeras', 'Nena', 'Remera Estampada Negra (La Flor)', 70, 4.99, '1½-2Y|4-6Y', 'dd/9b/dd9b498d22381954bfe11f3c7dccf9038cbe6c86.jpg'),
 ('1354454004', 'Remeras', 'Nene', 'Remera Manga Larga Lilo & Stitch Negra', 100, 5.99, '1½-2Y|2-4Y|4-6Y|6-8Y|8-10Y', '70/17/70178c25eeabbeb956ef2c73fa2be6428241e9b9.jpg'),
 ('1354454005', 'Remeras', 'Nene', 'Remera Manga Larga Minecraft Verde', 100, 4.99, '4-6Y|6-8Y|8-10Y', '06/df/06df38688f55c98a9e495f9bd134ece30f9a7dfa.jpg'),
 ('1354454006', 'Remeras', 'Nene', 'Remera Manga Larga Spider-Man Marrón', 100, 6.49, '1½-2Y|2-4Y|8-10Y', 'c3/64/c3640f424d4660bf35097d65ac57391045d519a2.jpg'),
 ('1315153006', 'Pantalones', 'Nene', 'Pantalón de Lino Verde Oscuro', 150, 9.99, '1½-2Y|2-3Y', 'b0/20/b02064721932a0b5d6f59b79b1908d2dd21b5043.jpg'),
 ('1331783001', 'Pantalones', 'Nena', 'Pantalón Bordado Inglés Blanco', 200, 12.99, '10-11Y|11-12Y|12-13Y|13-14Y', '8b/5b/8b5beedcc343a16e287e66cb0aac6adb316fe46f.jpg'),
 ('1333488001', 'Pantalones', 'Nena', 'Pantalón Efecto Crochet Blanco', 200, 9.99, '11-12Y|12-13Y|14Y+', 'a9/fa/a9fa482d0c5ff265422e8614ced0d6567118b69e.jpg'),
 ('1331753003', 'Mallas', 'Nena', 'Malla PAW Patrol Violeta', 100, 11.49, '1½-2Y|2-4Y|4-6Y|6-8Y|8-10Y', 'a7/ac/a7aceb65bafce42eb015b8661a2f2d48e31c1a9f.jpg'),
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
print('H&M liquidación 22/11:', len(extra))
for r in extra: print(f"  {r['cat']:<13} | {r['nombre']:<48} | USD {r['usd']:<5} | ${int(r['fijo']):,}".replace(',', '.'), '|', r['talles'])
