#!/usr/bin/env python3
"""Revisión de precios y stock del pedido abierto (17/11/2026, extendido hasta el jueves 19/11 y reabierto hasta el viernes 20/11 22 hs).

Solo toca lo que ya está publicado: nunca agrega productos.
  - Talles: saca los que se agotaron. Si quedan menos de 2 (o de 1 si tenía uno solo), saca el producto.
  - Precio que SUBE (incluye el fin del FRIDAY30 de Carter's o de la promo de GAP):
      sin precio fijo → se recalcula con la fórmula de siempre;
      con precio fijo → se mantiene si el costo subió hasta 10 % (o sigue dentro de la regla: remeras Carter's ≤ USD 4,99,
      pijamas ≤ USD 8); si subió más, el producto sale y queda en el informe para que Patricio decida.
  - Precio que BAJA: no se toca (el precio publicado se mantiene durante el pedido).
Entradas: --carters / --hm = JSON devueltos por carters_rev.js / hm_rev.js (solo los productos que cambiaron),
          tools/gapfactory.tsv recién relevado (workflow "Relevar GAP Factory" + gf_traducir.py) y --gap-promo si|no.
Uso: python3 tools/revision/revisar.py --carters /tmp/rev_carters.json --hm /tmp/rev_hm.json --gap-promo si [--seco]
"""
import argparse, csv, json, os, re, subprocess, sys, collections
R = os.path.dirname(os.path.abspath(__file__)); T = os.path.join(R, '..'); IDX = os.path.join(T, '..', 'index.html')
sys.path.insert(0, T); import precio as P
ap = argparse.ArgumentParser(); ap.add_argument('--carters'); ap.add_argument('--hm'); ap.add_argument('--gap-promo', default='si'); ap.add_argument('--seco', action='store_true')
a = ap.parse_args()

def leer(f): return list(csv.DictReader(open(os.path.join(T, f), encoding='utf-8'), delimiter='\t'))
def escribir(f, rows, campos):
    w = csv.DictWriter(open(os.path.join(T, f), 'w', encoding='utf-8', newline=''), fieldnames=campos, delimiter='\t', lineterminator='\n', extrasaction='ignore')
    w.writeheader(); w.writerows(rows)
E = json.load(open(os.path.join(R, 'esperado.json')))
RC = json.load(open(a.carters)) if a.carters else {}
RH = json.load(open(a.hm)) if a.hm else {}

NORM = {'OS': 'Único', 'NS': 'Único', 'ONE SIZE': 'Único', 'NO SIZE': 'Único', '6/6X': '6-6X', '6X': '6-6X', 'PREEMIE (UP TO 6LBS)': 'PRE', 'PREEMIE': 'PRE'}
ALFA = {'XS': '4-5', 'S': '6-7', 'M': '8', 'L': '10-12', 'XL': '14'}
def n_car(s):
    u = re.sub(r'^(\d+)R$', r'\1', s.upper().strip()); return {NORM.get(u, u), ALFA.get(u, u)}
def n_hm(s):
    s = s.strip()
    if s.upper() == 'ONESIZE': return {'Único'}
    s = s.replace('Y+', 'Y'); return {s[:-1] + ' años' if s.endswith('Y') else s}
def mapear(viejos, crudos, norm):
    out = set()
    for s in crudos: out |= norm(s)
    return out

inf = collections.defaultdict(list)   # informe
def revisar_fila(r, marca, nuevo_usd, talles_ok, esp_ok):
    """Devuelve la fila actualizada o None si sale. nuevo_usd = costo USD hoy; talles_ok = set de talles (formato landing) en stock."""
    nom = f"{r['nombre']} ({marca})"; tal = r['talles'].split('|')
    if esp_ok and talles_ok is not None:
        quedan = [t for t in tal if t in talles_ok]
        if len(quedan) < min(2, len(tal)): inf['sale (sin talles)'].append(nom); return None
        if len(quedan) < len(tal): inf['talles agotados'].append(f"{nom}: sin {', '.join(t for t in tal if t not in quedan)}")
        r['talles'] = '|'.join(quedan)
    viejo = float(r['usd'])
    if nuevo_usd is None or nuevo_usd <= viejo + 0.005: return r
    if r.get('fijo') and marca != 'gapfactory':
        regla = (marca in ('carters', 'oshkosh') and r['cat'] == 'Remeras' and r['fijo'] == '19900' and nuevo_usd <= 4.99) or \
                (r['cat'] in ('Pijamas', 'Pijamas de Polar') and nuevo_usd <= 8)
        if nuevo_usd <= viejo * 1.10 or regla: inf['costo subió, precio fijo se mantiene'].append(f"{nom}: USD {viejo:g} → {nuevo_usd:g}"); r['usd'] = f'{nuevo_usd:g}'; return r
        inf['sale (subió el costo, precio fijo)'].append(f"{nom}: USD {viejo:g} → {nuevo_usd:g}, publicado ${int(r['fijo']):,}".replace(',', '.')); return None
    r['usd'] = f'{nuevo_usd:g}'; r['_subio'] = f'USD {viejo:g} → {nuevo_usd:g}'; return r

# --- Carter's / OshKosh
cv = leer('carters_verano.tsv'); campos_c = list(cv[0].keys()); out = []
for r in cv:
    c = r['code']; d = RC.get(c); marca = r.get('marca') or 'carters'
    if not d: out.append(r); continue
    if d.get('gone'): inf['sale (agotado o fuera del sitio)'].append(f"{r['nombre']} ({marca})"); E['carters'].pop(c, None); continue
    e = E['carters'].get(c, {}); esp_ok = set(r['talles'].split('|')) <= mapear(None, e.get('s', []), n_car)
    usd = round(d['p'] * (0.7 if d.get('x') else 1), 2)
    if e.get('x') and not d.get('x'): inf['terminó el FRIDAY30'].append(f"{r['nombre']} ({marca})")
    nr = revisar_fila(r, marca, usd, mapear(None, d['s'], n_car), esp_ok)
    if nr: out.append(nr); E['carters'][c] = {'s': d['s'], 'p': d['p'], 'x': bool(d.get('x'))}
    else: E['carters'].pop(c, None)
cv2 = out

# --- H&M
hv = leer('hm_verano.tsv'); campos_h = list(hv[0].keys()); out = []
for r in hv:
    c = r['code']; d = RH.get(c)
    if not d: out.append(r); continue
    if d.get('gone'): inf['sale (agotado o fuera del sitio)'].append(f"{r['nombre']} (hm)"); E['hm'].pop(c, None); continue
    e = E['hm'].get(c, {}); esp_ok = set(r['talles'].split('|')) <= mapear(None, e.get('s', []), n_hm)
    nr = revisar_fila(r, 'hm', d['u'], mapear(None, d['s'], n_hm), esp_ok)
    if nr: out.append(nr); E['hm'][c] = {'s': d['s'], 'u': d['u']}
    else: E['hm'].pop(c, None)
hv2 = out

# --- GAP Factory (gapfactory_all.tsv recién relevado; los trajes de baño relevados aparte quedan como están)
gv = leer('gap_verano.tsv'); campos_g = open(os.path.join(T, 'gap_verano.tsv'), encoding='utf-8').readline().rstrip('\n').split('\t'); out = []
if a.gap_promo != 'si':
    inf['GAP: ya no figura el 10% extra al pagar (Black Friday Early) en gapfactory.com → salen todos los productos de GAP'].append(f'{len(gv)} productos'); gv2 = []
else:
    from gap_bf18_reglas import LICENCIA, precio_gap as _pg
    hoy = {r['code']: r for r in leer('gapfactory.tsv')}   # salida fresca de gf_traducir.py
    sys.path.insert(0, T)
    def precio_gap(usd):
        P.MARGEN = 1.9; p = P.precio(usd, 1560); p = 29900 if 30300 <= p <= 35000 else p
        for lo, hi, v in [(0, 10, 39900), (10, 12, 42900), (12, 13, 44900)]:
            if lo <= usd < hi: p = min(p, v)
        return p
    for r in gv:
        h = hoy.get(r['code'])
        if not h:
            if r['cat'] == 'Mallas': out.append(r); continue   # relevados aparte (página de búsqueda), no figuran en el workflow
            inf['sale (agotado o fuera del sitio)'].append(f"{r['nombre']} (gapfactory)"); continue
        # 18/11: GAP Black Friday Early (precio de la web) + 10% extra al pagar; licencias sin el 10% (ver tools/gap_bf18.py)
        usd = round(float(h['usd']) * (1.0 if LICENCIA.search(r['nombre']) else 0.9), 2)
        nr = revisar_fila(r, 'gapfactory', usd, set(h['talles'].split('|')), True)
        if nr:
            if nr.get('_subio'):
                f = precio_gap(float(nr['usd'])); f = 29900 if 29000 <= f < 29900 else f
                if f > 39900: inf['sale (GAP quedó arriba de $39.900)'].append(f"{nr['nombre']}: USD {nr['usd']}"); continue
                nr['fijo'] = str(f); nr['usd_lista'] = h['usd']
            out.append(nr)
    gv2 = out

def precios(f):
    s = open(f, encoding='utf-8').read()
    return {m.group(1): (m.group(2), int(m.group(3))) for m in re.finditer(r'data-code="([^"]+)" data-nom="([^"]*)" data-precio="(\d+)"', s)}
antes = precios(IDX)
cierre = re.search(r'CIERRE=new Date\("([^"]+)"\)', open(IDX, encoding='utf-8').read()).group(1)
if not a.seco:
    escribir('carters_verano.tsv', cv2, campos_c); escribir('hm_verano.tsv', hv2, campos_h); escribir('gap_verano.tsv', gv2, campos_g)
    json.dump(E, open(os.path.join(R, 'esperado.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    subprocess.run([sys.executable, os.path.join(T, 'armar_pedido.py'), '--cierre', cierre, '--tsv', 'carters_verano.tsv:carters,hm_verano.tsv:hm,gap_verano.tsv:gapfactory'], check=True, cwd=os.path.join(T, '..'))
    s = open(IDX, encoding='utf-8').read()
    if 'var ABIERTO = true;' not in s: s = re.sub(r'var ABIERTO = (true|false);', 'var ABIERTO = true;', s, count=1); open(IDX, 'w', encoding='utf-8').write(s)
    despues = precios(IDX)
    for c, (n, p) in despues.items():
        if c in antes and p != antes[c][1]: inf['precio actualizado'].append(f"{n}: ${antes[c][1]:,} → ${p:,}".replace(',', '.'))
    print(f'Productos publicados: {len(antes)} → {len(despues)} (cierre {cierre})')
for k, v in inf.items():
    print(f'\n## {k}: {len(v)}')
    for x in v[:60]: print('  -', x)
    if len(v) > 60: print(f'  … y {len(v) - 60} más')
