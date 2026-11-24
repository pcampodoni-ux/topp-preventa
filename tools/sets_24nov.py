#!/usr/bin/env python3
"""24/11 (Patricio reabre el pedido hasta el miércoles 25/11 22 hs): "sumá algunos productos, hasta $69.000, siempre que sean sets y conjuntos atractivos".
Carter's: categorías de sets (baby girl/boy/neutral, toddler girl/boy, girls/boys) ordenadas por precio, leídas desde el navegador de Patricio.
Criterio: hasta USD 14,50, al menos 2 talles, sin fiestas (Navidad, Acción de Gracias) ni abrigo (polar, teddy, tejidos, capucha).
Precio: fórmula con tramos; los de USD 14–14,50 a $66.490 (mismo precio fijo que los sets de 3 piezas del 23/11, ~$30.000 de ganancia)."""
import csv, json, os, sys
T = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, T)
IMG = 'https://www.carters.com/on/demandware.static/-/Sites-carters_master_catalog/default/productimages/'
G = {'G': 'Nena', 'B': 'Nene', 'N': 'Unisex'}
# code, género, nombre, USD, talles en stock
D = [
 ('1W373210', 'G', 'Set Body Manga Larga y Pantalón de Tul Lila', 9, 'NB,3M,6M,9M,12M,18M,24M'),
 ('1W095810', 'G', 'Set Body Manga Larga con Moñito y Pantalón Rosa', 10, 'NB,3M,6M,9M,12M,18M,24M'),
 ('1W373410', 'G', 'Set Body Manga Larga y Pantalón Negro y Crudo', 10, 'NB,6M'),
 ('1W241010', 'G', 'Set Body "Daddy\'s Little Princess" y Pantalón de Tul Rosa', 9, 'NB,3M,6M,9M,12M,18M,24M'),
 ('1W095610', 'G', 'Set Body "Little Sweethearts Club" y Pantalón Rosa y Gris', 9, 'NB,3M,6M,9M,12M,18M,24M'),
 ('1W096410', 'G', 'Set Body Manga Larga y Pantalón Rojo', 9, 'NB,3M,6M,9M,12M,18M,24M'),
 ('1W224410', 'G', 'Set 3 Piezas Zorrito Lila', 14.4, 'NB,3M,6M,9M,12M,18M,24M'),
 ('1W096310', 'G', 'Set Body y Pantalón Copos de Nieve Azul', 10, 'NB,3M'),
 ('1V909810', 'G', 'Set Remera Manga Larga y Pantalón Corazones Marrón y Negro', 14.5, '12M,18M,24M'),
 ('1W123710', 'G', 'Set 3 Piezas Leopardo Marrón, Crudo y Negro', 14.5, 'NB,3M,6M,9M,12M,18M,24M'),
 ('1W284810', 'G', 'Set 3 Piezas Corazones y Flores Verde y Crudo', 14.5, 'NB,3M,6M,9M,12M,18M,24M'),
 ('1W096910', 'B', 'Set Body "Little Man On a Mission" Espacio y Pantalón Azul Marino', 10, 'NB,3M,6M,9M,24M'),
 ('1W372510', 'B', 'Set Body Autitos y Pantalón Marrón y Crudo', 9, 'NB,3M,6M,9M,12M,18M,24M'),
 ('1W097610', 'B', 'Set Body Bosque y Pantalón Verde y Crudo', 9, 'NB,3M,6M,9M,12M,18M,24M'),
 ('1W626210', 'B', 'Set Body "Mama\'s Little Love" y Pantalón Rojo y Azul', 10, 'NB,3M,6M,9M,12M,18M,24M'),
 ('1W281910', 'B', 'Set 3 Piezas Perritos Verde y Gris', 12.8, 'NB,3M,6M,9M,12M'),
 ('1W097710', 'B', 'Set Body Osito y Pantalón Azul y Gris', 9, 'NB,3M,6M,9M,12M,18M,24M'),
 ('1V883110', 'B', 'Set Buzo y Pantalón de Algodón Fútbol Americano Azul Marino', 10.8, 'NB,3M,6M,9M,12M,18M,24M'),
 ('1W123410', 'B', 'Set 3 Piezas Leche y Galletitas Azul y Crudo', 11.6, 'NB,3M,6M,9M,12M,18M,24M'),
 ('1W123210', 'B', 'Set 3 Piezas Trencito Azul y Crudo', 14.5, 'NB,3M,6M,9M,12M,18M,24M'),
 ('1W661210', 'B', 'Set Remera Manga Larga Rayada y Pantalón Marrón, Blanco y Azul', 12.8, '12M,18M,24M'),
 ('1W769610', 'N', 'Set Body Harry Potter "Snuggle This Muggle" y Pantalón Azul', 14, 'NB,3M,6M,9M,12M,18M,24M'),
 ('1V418810', 'N', 'Set 3 Piezas Ovejita de Toalla Crudo', 12.8, 'NB,3M,6M,9M,12M'),
 ('1V418710', 'N', 'Set 3 Piezas Leoncito de Toalla Amarillo', 12.8, 'NB,3M,6M,9M,12M'),
 ('1V416410', 'N', 'Set Jardinero Osito Marrón', 14.5, 'NB,3M,6M,9M,12M'),
 ('1V392710', 'N', 'Set 3 Piezas Ballenas Crudo', 14.5, 'PRE,3M,6M,9M'),
 ('1V410510', 'N', 'Set Jardinero Dinosaurios Verde y Crudo', 11.6, 'NB,3M,6M,9M,12M'),
 ('2V911210', 'G', 'Set Remera Manga Larga y Pantalón Corazones Marrón', 14.5, '2T,3T,4T,5T'),
 ('2V911110', 'G', 'Set Remera Manga Larga y Pantalón Floral Verde', 14.5, '2T,3T,4T,5T'),
 ('2V911310', 'G', 'Set Remera Manga Larga y Pantalón Gatitos Rosa', 14.5, '2T,3T,4T,5T'),
 ('2W629710', 'B', 'Set Remera "Roll With It" Autos de Carrera y Pantalón Azul', 14.4, '2T,3T,4T,5T'),
 ('2W661210', 'B', 'Set Remera Manga Larga Rayada y Pantalón Marrón, Blanco y Azul', 14.4, '2T,3T,4T,5T'),
]
f = os.path.join(T, 'carters_verano.tsv'); campos = open(f, encoding='utf-8').readline().rstrip('\n').split('\t')
base = list(csv.DictReader(open(f, encoding='utf-8'), delimiter='\t')); ya = {r['code'] for r in base}
E = json.load(open(os.path.join(T, 'revision', 'esperado.json')))
extra = []
for c, g, n, u, s in D:
    if c in ya: continue
    tal = s.split(',')
    extra.append(dict(code=c, cat='Sets 2 Piezas', gen=G[g], nombre=n, usd=f'{u:g}', talles='|'.join(tal), img=IMG + c + '.jpg',
                      fijo='66490' if u >= 14 else '', marca='carters'))
    E['carters'][c] = {'s': tal, 'p': u, 'x': False}
w = csv.DictWriter(open(f, 'w', encoding='utf-8', newline=''), fieldnames=campos, delimiter='\t', lineterminator='\n', extrasaction='ignore', restval='')
w.writeheader(); w.writerows(base + extra)
json.dump(E, open(os.path.join(T, 'revision', 'esperado.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
print("Carter's sets 24/11:", len(extra))
