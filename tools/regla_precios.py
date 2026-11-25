#!/usr/bin/env python3
"""Regla de precios TOPP por rol de prenda (Patricio, 25/11/2026 07:34: "aplicá esa regla a toda la tienda").

  costo real  = (USD pagado × 1,07 + peso_kg × USD 26,5 + USD 0,85) × cotización Ualá   (el flete se suma, no se multiplica)
  precio      = costo + ganancia objetivo del rol, redondeado al X.900 más cercano
  techo       = precio máximo de la categoría: si el precio lo pasa, queda en el techo
  mínimo      = si en el techo deja menos de USD 5, el producto sale de la landing

Roles (ganancia objetivo en USD, así no se la come la inflación):
  gancho  USD 8   remeras, shorts, bodies sueltos
  volumen USD 10  pijamas, vestidos, pantalones, mallas, buzos, polares, camperas, ropa interior
  ticket  USD 15  sets, packs de bodies, enteritos, jardineros y todo lo que tiene personaje (licencia)

Excepciones (precios que decidió Patricio; se mantienen salvo que la regla dé menos): Remera Frutillas Rosa 3U482410 $19.900 (21/11,
precio de la competencia), Set UPF H&M 1139368013 $86.900 (23/11), sets Mickey/Minnie H&M 1314910013 y 1347744002 $68.900 (24/11).

Uso: python3 tools/regla_precios.py [--solo-bajar] [--seco]
  --solo-bajar: con el pedido abierto no sube ningún precio publicado (lo que subiría se informa y queda igual),
                salvo que con el precio publicado pierda plata: ahí sube al precio de la regla.
"""
import csv, json, os, re, sys
T = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, T)
import precio as P
from gap_bf18_reglas import LICENCIA

GANANCIA = {'gancho': 8, 'volumen': 10, 'ticket': 15}
ROL = {'Remeras': 'gancho', 'Shorts': 'gancho', 'Bodies': 'gancho',
       'Pijamas': 'volumen', 'Vestidos': 'volumen', 'Pantalones': 'volumen', 'Mallas': 'volumen', 'Trajes de baño': 'volumen',
       'Buzos': 'volumen', 'Pijamas de Polar': 'volumen', 'Camperas': 'volumen', 'Ropa interior': 'volumen',
       'Sets 2 Piezas': 'ticket', 'Packs de Bodies': 'ticket', 'Enteritos': 'ticket', 'Jardineros': 'ticket'}
TECHO = {'Remeras': 29900, 'Shorts': 27900, 'Bodies': 29900, 'Pijamas': 39900, 'Vestidos': 44900, 'Pantalones': 34900,
         'Mallas': 39900, 'Trajes de baño': 39900, 'Buzos': 39900, 'Pijamas de Polar': 35900, 'Camperas': 49900,
         'Ropa interior': 44900, 'Sets 2 Piezas': 44900, 'Enteritos': 49900, 'Jardineros': 49900}
PESO = {'Remeras': 70, 'Shorts': 50, 'Bodies': 60, 'Pijamas': 215, 'Vestidos': 120, 'Pantalones': 100, 'Mallas': 100,
        'Trajes de baño': 100, 'Buzos': 200, 'Pijamas de Polar': 280, 'Camperas': 400, 'Enteritos': 120, 'Jardineros': 250,
        'Sets 2 Piezas': 150}
FIJOS = {'3U482410': 19900, '1139368013': 86900, '1314910013': 68900, '1347744002': 68900}   # decisiones de Patricio (21/11, 23/11, 24/11)
MIN_USD = 5
# 25/11 07:59, Patricio: "los packs déjalos como estaban, al igual que los pijamitas: son las cosas que se vendieron".
# Estas categorías no las toca la regla: quedan al precio publicado (ni bajan ni salen por la regla; sí salen si se agotan).
EXCLUIR = {'Packs de Bodies', 'Pijamas', 'Pijamas de Polar'}


def n_pack(nombre, defecto):
    m = re.search(r'Pack (\d+)', nombre)
    return int(m.group(1)) if m else defecto


def regla(cat, nombre, usd, cot=None):
    """Devuelve (precio, costo, rol) o (None, costo, rol) si no llega al mínimo dentro del techo."""
    cot = cot or P.COT
    if cat == 'Packs de Bodies':
        n = n_pack(nombre, 5); peso = 60 * n; techo = 49900 if n <= 3 else (59900 if n <= 5 else 69900)
    elif cat == 'Ropa interior':
        peso = 30 * n_pack(nombre, 3); techo = TECHO[cat]
    elif re.match(r'Pack \d+', nombre) and cat in PESO:
        # 25/11 16:17: packs de remeras, shorts o calzas (H&M). Peso por prenda × N; techo = techo de la categoría + 50% por
        # cada prenda extra (pack de 3 remeras: $59.900); rol ticket. Antes se los trataba como una sola prenda y salían todos.
        n = n_pack(nombre, 2); peso = PESO[cat] * n
        techo = int(round(TECHO.get(cat, 44900) * (1 + 0.5 * (n - 1)) / 1000)) * 1000 - 100
        cost = (usd * 1.07 + peso / 1000 * 26.5 + 0.85) * (cot or P.COT)
        p = min(int(round((cost + GANANCIA['ticket'] * (cot or P.COT) + 100) / 1000)) * 1000 - 100, techo)
        return (p if p - cost >= MIN_USD * (cot or P.COT) else None), cost, 'ticket'
    elif cat == 'Sets 2 Piezas' and re.search(r'3 Piezas', nombre, re.I):
        peso = 200; techo = 69900
    else:
        peso = PESO.get(cat, 120); techo = TECHO.get(cat, 44900)
    rol = 'ticket' if LICENCIA.search(nombre) else ROL.get(cat, 'volumen')
    costo = (usd * 1.07 + peso / 1000 * 26.5 + 0.85) * cot
    p = int(round((costo + GANANCIA[rol] * cot + 100) / 1000)) * 1000 - 100
    p = min(p, techo)
    if p - costo < MIN_USD * cot:
        return None, costo, rol
    return p, costo, rol


def main():
    solo_bajar = '--solo-bajar' in sys.argv; seco = '--seco' in sys.argv
    html = open(os.path.join(os.path.dirname(T), 'index.html'), encoding='utf-8').read()
    pub = {}
    for a in re.findall(r'<article[^>]*>', html):
        d = dict(re.findall(r'data-([a-z]+)="([^"]*)"', a))
        if 'code' in d and 'precio' in d: pub[d['code']] = int(d['precio'])
    inf = {'baja': [], 'sube': [], 'sube_congelado': [], 'sale': [], 'igual': 0}
    for f in ('carters_verano.tsv', 'hm_verano.tsv', 'gap_verano.tsv'):
        p = os.path.join(T, f); campos = open(p, encoding='utf-8').readline().rstrip('\n').split('\t')
        rows = list(csv.DictReader(open(p, encoding='utf-8'), delimiter='\t')); quedan = []
        for r in rows:
            c = r['code']; marca = r.get('marca') or ('gapfactory' if f.startswith('gap') else 'hm')
            if r['cat'] in EXCLUIR and pub.get(c):
                r['fijo'] = str(pub[c]); quedan.append(r); inf['igual'] += 1; continue
            nuevo, costo, rol = regla(r['cat'], r['nombre'], float(r['usd']))
            if c in FIJOS and (nuevo is None or nuevo > FIJOS[c]): nuevo = FIJOS[c]
            actual = pub.get(c)
            fila = (marca, c, r['cat'], r['nombre'], r['usd'], actual, nuevo, round((nuevo or 0) - costo), rol)
            if nuevo is None:
                inf['sale'].append(fila); continue
            if actual and nuevo > actual and solo_bajar and actual - costo > 0:
                inf['sube_congelado'].append(fila); r['fijo'] = str(actual); quedan.append(r); continue
            if actual and nuevo < actual: inf['baja'].append(fila)
            elif actual and nuevo > actual: inf['sube'].append(fila)
            else: inf['igual'] += 1
            r['fijo'] = str(nuevo); quedan.append(r)
        if not seco:
            w = csv.DictWriter(open(p, 'w', encoding='utf-8', newline=''), fieldnames=campos, delimiter='\t', lineterminator='\n',
                               extrasaction='ignore', restval='')
            w.writeheader(); w.writerows(quedan)
    json.dump(inf, open('/tmp/regla_informe.json', 'w'), ensure_ascii=False)
    print({k: (len(v) if isinstance(v, list) else v) for k, v in inf.items()})


if __name__ == '__main__':
    main()
