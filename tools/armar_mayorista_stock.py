"""Arma mayorista-stock.html: lista mayorista del stock de wowcyk.com con el formato de index.html.

Entradas:
  tools/wowcyk_stock.json             (workflow "Relevar WOWCYK": talles y stock por producto)
  tools/wowcyk_mayorista_precios.json (precio mayorista por URL: reposición Carter's ÷ 0,80, cot. 1.630;
                                       packs de 4 y 5 bodies a $49.900, decisión de Patricio 22/11/2026)
  tools/wowcyk_listado.json           (nombre, foto, descripción del listado de la tienda)
Reglas: mínimo 25 unidades surtidas, solo transferencia, sin seña.
"""
import html
import json
import re

R = 'tools/'
stock = {x['url']: x for x in json.load(open(R + 'wowcyk_stock.json'))}
precios = json.load(open(R + 'wowcyk_mayorista_precios.json'))
listado = {x['url']: x for x in json.load(open(R + 'wowcyk_listado.json'))}
ajustes = json.load(open(R + 'wowcyk_mayorista_ajustes.json'))

TALLE_RX = re.compile(r'^(PRE|NB|OSZ|ÚNICO|UNICO|U|XXS|XS|S|M|L|XL|XXL|\d+\s*[MT]|\d+(-\d+X?)?|\d+X|N°\s*\d+|\d+\s*-\s*\d+\s*[MT]?|\d+/\d+)$', re.I)
ORD_T = ['PRE', 'NB', '0-3M', '3M', '3-6M', '6M', '6-9M', '9M', '12M', '18M', '24M', '2T', '3T', '4T', '5T', '6T', '7T', '8T',
         '4', '4-5', '5', '6', '6-6X', '6-7', '7', '8', '10', '10-12', '12', '14', '14-16', '16']
CATS = ['Packs de bodies', 'Sets 2 piezas', 'Sets 3 piezas', 'Sets 4 piezas', 'Enteritos / rompers', 'Bodies individuales',
        'Ositos / pijamas enteros', 'Pijamas', 'Remeras, camisas y chombas', 'Shorts y bermudas', 'Vestidos y polleras',
        'Jardineros', 'Pantalones y jeans', 'Baño (mallas y UV)', 'Packs (otros)', 'Mochilas', 'Baño y accesorios Skip Hop',
        'Baberos y accesorios', 'Medias y ropa interior', 'Accesorios', 'Calzado', 'Abrigo', 'Otros']
GRUPOS = [('c', "Carter's"), ('o', 'OshKosh'), ('s', 'Skip Hop'), ('x', 'Otras marcas')]


def e(s):
    return html.escape(str(s or ''), quote=True)


def fmt(n):
    return '$' + f'{int(n):,}'.replace(',', '.')


def talle_de(ops):
    t = [o for o in ops if TALLE_RX.match(str(o).strip())]
    return (t[-1] if t else ops[-1]).strip() if ops else 'Único'


def orden_t(t):
    u = t.upper().replace(' ', '')
    return (ORD_T.index(u), u) if u in ORD_T else (99, u)


CARTERS_SKU = re.compile(r'^L?(\d[A-Z]\d{6}|\d{3}[A-Z]\d{3}|\d{6}1[01])$')
SKIPHOP_SKU = re.compile(r'^9[A-Z]\d{6}$')


def grupo(nom, desc, skus=()):
    """Carter's / OshKosh / Skip Hop por nombre, descripción o código (los códigos tipo 1T006810 son de Carter's/OshKosh;
    9R168110 = Skip Hop). Little Planet es una línea de Carter's."""
    n, s = nom.lower(), (nom + ' ' + (desc or '')).lower()
    skus = [str(x).strip().upper() for x in skus if x]
    if n.startswith('oshkosh') or ('oshkosh' in s and not n.startswith('carter')):
        return 'o'
    if n.startswith('carter') or 'little planet' in s:
        return 'c'
    if 'skip hop' in s or 'spark style' in s or any(SKIPHOP_SKU.match(x) for x in skus):
        return 's'
    if "carter" in s or any(CARTERS_SKU.match(x) for x in skus):
        return 'c'
    return 'x'


def genero(s):
    s = s.lower()
    if re.search(r'nena|niña|beba\b', s):
        return 'Nena'
    if re.search(r'nene|niño|varon|varón', s):
        return 'Nene'
    return 'Unisex'


def edad(desc, talles):
    if re.search(r'beb[eé]', desc.lower()) or any(re.match(r'^(PRE|NB|\d+M)$', t, re.I) for t in talles):
        return 'Bebés'
    return 'Niños'


def desc_talles(desc):
    m = re.search(r'Talles?\s+([0-9A-Za-z\-/]+)(?:\s*a\s*([0-9A-Za-z\-/]+))?', desc or '')
    return m.group(1) if m and not m.group(2) else None


prods = []
for url, p in precios.items():
    if url in ajustes['excluir']:
        continue
    li = listado.get(url, {})
    st = stock.get(url, {})
    nom = (li.get('name') or st.get('nombre') or '').strip().strip('"').replace('""', '"')
    desc = li.get('desc') or ''
    vs = {}
    colores = set()
    for v in st.get('variantes', []):
        n = v.get('stock')
        n = 10 if n is None and v.get('disponible') else (n or 0)
        if n <= 0:
            continue
        ops = [str(o) for o in v.get('opciones', [])]
        t = talle_de(ops)
        otros = [o for o in ops if o != t]
        colores.add(' '.join(otros))
        vs[(t, ' '.join(otros))] = vs.get((t, ' '.join(otros)), 0) + n
    if not st.get('variantes'):
        if st.get('error') and li:
            t = desc_talles(desc) or 'Consultar'
            vs[(t, '')] = int(li.get('stock') or 1)
        else:
            continue
    if not vs:
        continue
    multi_color = len(colores) > 1
    tl = []
    for (t, c), n in sorted(vs.items(), key=lambda kv: (kv[0][1], orden_t(kv[0][0]))):
        tv = 'Único' if t.upper() == 'OSZ' else t
        tl.append({'t': (c + ' ' + tv).strip() if multi_color else tv, 'n': n, 'f': t})
    # tope: nunca más caro que el precio con transferencia (20% off) del talle más barato con stock en la tienda,
    # salvo los packs de 4 y 5 bodies a $49.900 (decisión de Patricio)
    precio = p['may']
    vp = [v['precio'] for v in st.get('variantes', []) if v.get('precio') and ((v.get('stock') or 0) > 0 or v.get('stock') is None)]
    if vp and precio != 49900:
        precio = min(precio, int(min(vp) * 0.8) // 100 * 100)
    # 22/11 (Patricio): lo que queda igual o más caro que la tienda con transferencia baja $5.000,
    # solo si sigue dejando al menos 10% sobre el costo de reposición
    if vp:
        tr = min(vp) * 0.8
        baja = int(tr - 5000) // 100 * 100
        if precio > tr - 1000 and baja >= p['costo'] * 1.10:
            precio = baja
    precio = ajustes['fijos'].get(url, precio)
    g = grupo(nom, desc, [li.get('sku')] + [v.get('sku') for v in st.get('variantes', [])])
    img = re.sub(r'-\d+-0\.webp$', '-480-0.webp', li.get('img') or st.get('img') or '')
    prods.append(dict(url=url, nom=nom, cat=p['cat'], precio=precio, img=img, sku=li.get('sku') or st.get('sku') or '',
                      g=g, gen=genero(nom + ' ' + desc), edad=edad(desc + ' ' + nom, [x['f'] for x in tl]), tl=tl))

prods.sort(key=lambda x: (CATS.index(x['cat']) if x['cat'] in CATS else 99, x['nom']))
for i, p in enumerate(prods):
    p['id'] = i


def card(p):
    marca = dict(GRUPOS)[p['g']]
    tot = sum(x['n'] for x in p['tl'])
    btns = ''.join(f'<button class="tl" data-t="{e(x["t"])}" data-n="{x["n"]}">{e(x["t"])}{"<sup>" + str(x["n"]) + "</sup>" if x["n"] > 1 else ""}</button>' for x in p['tl'])
    return (f'<article class="card" data-id="{p["id"]}" data-grupo="{p["g"]}" data-cat="{e(p["cat"])}" data-edad="{p["edad"]}" '
            f'data-gen="{p["gen"]}" data-talles="{e("|".join(x["f"] for x in p["tl"]))}" data-code="{e(p["sku"])}" '
            f'data-nom="{e(p["nom"])}" data-precio="{p["precio"]}">\n'
            f'<a class="ph" href="{e(p["url"])}" target="_blank" rel="noopener"><img loading="lazy" src="{e(p["img"])}" alt="{e(p["nom"])}" onerror="this.style.opacity=0"></a>\n'
            f'<div class="bd">\n<span class="tag">{e(marca)} · {e(p["cat"])} · {p["edad"]}</span>\n'
            f'<h3><a class="nm" href="{e(p["url"])}" target="_blank" rel="noopener">{e(p["nom"])}</a></h3>\n'
            f'<div class="pr"><b>{fmt(p["precio"])}</b><span class="cu">c/u</span></div>\n'
            f'<p class="lb">Talles · {tot} disponible{"s" if tot > 1 else ""}<button class="ttl" type="button" data-tt>¿Qué talle?</button></p>\n'
            f'<div class="tls">{btns}</div>\n<button class="add" disabled>Elegí un talle</button>\n</div></article>')


idx = open('index.html').read()
css = idx[idx.find('<style'):idx.find('</style>') + 8]
tt = idx[idx.find('<div class="ov" id="ttov">'):idx.find('<div class="toast" id="toast">')]
css_extra = """<style>
.pr .cu{font-size:12px;color:#9aa4a6}
.tl sup{font-size:9px;margin-left:2px;opacity:.75}
.tl.on sup{opacity:1}
.add.done{background:#4a7a5c}
.meta{background:#fff;padding:16px 0}
.mbar{max-width:640px;margin:0 auto;text-align:center}
.mbar .num{font-size:28px;font-weight:700;color:var(--v)}
.mbar .num small{font-size:14px;font-weight:300;color:var(--tx)}
.mtrack{height:12px;border-radius:99px;background:var(--gr);overflow:hidden;margin:8px 0 6px}
.mtrack i{display:block;height:100%;width:0;background:var(--v);border-radius:99px;transition:width .3s}
.mtrack.full i{background:#4a7a5c}
.mbar p{font-size:13px;font-weight:300}
.qty{display:flex;align-items:center;gap:6px;flex:0 0 auto}
.qty button{width:30px;height:30px;border:1px solid var(--v2);background:#fff;color:var(--v);border-radius:8px;font:inherit;font-weight:700;font-size:16px;cursor:pointer;padding:0}
.qty button:disabled{opacity:.35;cursor:default}
.qty span{min-width:22px;text-align:center;font-weight:700}
.li .ln{flex:1;min-width:0}
.minw{background:#fdecea;color:#c0392b;border-radius:10px;padding:10px 12px;font-size:13.5px;font-weight:600;margin-top:10px}
.minw.ok{background:#e8f3ec;color:#4a7a5c}
textarea.f{width:100%;border:1px solid var(--v2);border-radius:9px;padding:11px;font:inherit;font-size:15px;background:#fff;color:var(--tx);min-height:64px}
.fbar .frow{flex-wrap:wrap;overflow:visible;row-gap:6px}
#fov .modal{max-width:640px}
</style>"""

chips = lambda f, vals: ''.join(f'<button class="chip" data-f="{f}" data-v="{e(v)}">{e(l)}</button>' for v, l in vals)
cats_pres = [c for c in CATS if any(p['cat'] == c for p in prods)]
grupos_pres = [(k, v) for k, v in GRUPOS if any(p['g'] == k for p in prods)]
tbebe = ['PRE', 'NB', '3M', '6M', '9M', '12M', '18M', '24M']
tnino = ['2T', '3T', '4T', '5T']
tgr = ['4', '4-5', '5', '6', '6-6X', '6-7', '7', '8', '10', '10-12', '12', '14', '14-16', '16']
todos_t = {x['f'].upper() for p in prods for x in p['tl']}
fb = (f'<div class="fbar"><div class="wrap">'
      f'<div class="frow"><em>Ordenar</em><button class="chip on" data-s="">Sugerido</button><button class="chip" data-s="desc">Mayor precio</button><button class="chip" data-s="asc">Menor precio</button></div>'
      f'<div class="frow"><em>Categoría</em>{chips("cat", [(c, c) for c in cats_pres])}</div>'
      f'<div class="frow"><em>Edad</em>{chips("edad", [("Bebés", "Bebés (0 a 24 meses)"), ("Niños", "Niños (2 años en adelante)")])}</div>'
      f'<div class="frow"><em>Género</em>{chips("gen", [("Nena", "Nena"), ("Nene", "Nene"), ("Unisex", "Unisex")])}</div>'
      f'<div class="frow"><em>Talles bebés</em>{chips("talle", [(t, t) for t in tbebe if t in todos_t])}</div>'
      f'<div class="frow"><em>Talles niños</em>{chips("talle", [(t, t) for t in tnino if t in todos_t])}</div>'
      f'<div class="frow"><em>Talles grandes</em>{chips("talle", [(t, t) for t in tgr if t in todos_t])}</div>'
      f'</div></div>')

tabs = ''.join(f'<button type="button" class="gt{" on" if not k else ""}" data-g="{k}">{e(v)}<small>{n} productos</small></button>'
               for k, v, n in [('', 'Todo', len(prods))] + [(k, v, sum(1 for p in prods if p['g'] == k)) for k, v in grupos_pres])
unidades = sum(x['n'] for p in prods for x in p['tl'])

page = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>WOWCYK Mayorista</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Josefin+Sans:wght@300;400;600;700&display=swap" rel="stylesheet">
{css}
{css_extra}
</head>
<body>

<header><div class="logo">WOWCYK<small>VENTA MAYORISTA</small></div></header>

<section class="hero">
  <div class="wrap">
    <div class="badge">● LISTA MAYORISTA</div>
    <h1 style="margin-top:14px">Stock propio con entrega inmediata</h1>
    <p>{len(prods):,} productos y {unidades:,} unidades de ropa de bebés y niños. Compra mínima 25 unidades surtidas. Precios solo con transferencia.</p>
  </div>
</section>

<section class="links"><div class="wrap"><div class="tpp"><h2>🏬 Esta es nuestra lista <b>MAYORISTA</b> para locales</h2><p>Mezclá modelos y talles como quieras hasta llegar a <b>25 unidades</b>. Los precios son por unidad y valen <b>solo pagando con transferencia</b>. Todo lo que ves está en stock y sale apenas confirmás.</p></div><div class="lks uno"><a class="lk lkw" href="https://wa.me/5493794235712" target="_blank" rel="noopener"><i>💬</i><span>Consultas por WhatsApp<small>3794235712 · te respondemos stock, envío y facturación</small></span></a></div></div></section>

<section class="steps"><div class="wrap"><ol>
  <li><b>1</b>Elegí productos y talles</li>
  <li><b>2</b>Sumá 25 unidades o más (podés mezclar)</li>
  <li><b>3</b>Enviá el pedido por WhatsApp</li>
  <li><b>4</b>Transferís y te lo despachamos</li>
</ol></div></section>

<section class="meta"><div class="wrap"><div class="mbar"><div class="num" id="mnum">0 <small>/ 25 unidades</small></div><div class="mtrack" id="mtrack"><i></i></div><p id="mmsg">Te faltan 25 unidades para llegar al mínimo.</p></div></div></section>

<div class="sbar" id="sbar"><div class="wrap"><div class="srow"><div class="sbox" id="sbox">🔎<input id="q" type="search" enterkeyhint="search" autocomplete="off" placeholder="Buscá: pack bodies, set 3T, malla…" aria-label="Buscar productos"><button type="button" class="x" id="qx" aria-label="Borrar búsqueda">✕</button></div><button type="button" class="fbtn" id="fbtn">⚙ <span>Filtrar</span><b id="fbn"></b></button></div><div class="sinfo" id="sinfo"></div></div></div>
<div class="wrap"><div class="gtabs" id="gtabs" style="grid-template-columns:repeat({len(grupos_pres) + 1},1fr)">{tabs}</div></div>
<div class="wrap"><div class="factv" id="factv"><span id="factt"></span><button type="button" id="factc">Limpiar filtros</button></div></div>

<div class="wrap"><div class="grid" id="grid">
{chr(10).join(card(p) for p in prods)}
</div><div class="empty" id="empty">No hay productos con esos filtros. <a href="#" id="emclr">Limpiar filtros</a></div></div>

<div class="cartbar" id="cartbar">
  <div class="i"><span id="cn">0 unidades · faltan 25 para el mínimo</span><b id="ct">$0</b></div>
  <button id="open">Ver mi pedido</button>
</div>

<div class="ov" id="ov"><div class="modal">
  <h2>Tu pedido mayorista</h2>
  <p class="sub">Mínimo 25 unidades surtidas. Precios por unidad, solo con transferencia.</p>
  <div id="items"></div>
  <div class="tot"><span id="mu">0 unidades</span><span id="mt">$0</span></div>
  <div class="minw" id="minw"></div>

  <label class="f" for="loc">Nombre del local <b>*</b></label>
  <input class="f" id="loc" type="text" placeholder="Nombre del local o comercio" autocomplete="organization">
  <div class="err" id="locerr">Poné el nombre del local.</div>

  <label class="f" for="cli">Nombre y apellido <b>*</b></label>
  <input class="f" id="cli" type="text" placeholder="Nombre y apellido" autocomplete="name">
  <div class="err" id="clerr">Poné tu nombre y apellido.</div>

  <label class="f" for="tel">Número de WhatsApp <b>*</b></label>
  <input class="f" id="tel" type="tel" inputmode="numeric" placeholder="Ej: 3795123456 (sin 0 ni 15)" autocomplete="tel">
  <div class="err" id="telerr">Poné tu número de WhatsApp con característica, sin 0 ni 15.</div>

  <label class="f" for="res">Ciudad y provincia <b>*</b></label>
  <input class="f" id="res" type="text" placeholder="Ej: Resistencia, Chaco" autocomplete="address-level2">
  <div class="err" id="reserr">Poné tu ciudad y provincia.</div>

  <label class="f" for="cuit">CUIT <span class="opt">(opcional, si necesitás factura)</span></label>
  <input class="f" id="cuit" type="text" inputmode="numeric" placeholder="Ej: 20-12345678-9">

  <label class="f" for="obs">Comentarios <span class="opt">(envío, retiro, otra consulta)</span></label>
  <textarea class="f" id="obs" rows="2"></textarea>

  <div class="pay">
    <b>Pago solo por transferencia</b><br>
    Al recibir tu pedido te confirmamos el stock, el costo de envío y te pasamos los datos para transferir.
  </div>

  <button class="wa" id="wa">Enviar pedido por WhatsApp</button>
  <button class="cls" id="cls">Seguir mirando</button>
</div></div>

<div class="ov" id="fov"><div class="modal">
  <h2>Filtrar</h2>
  {fb}
  <button class="wa" id="fok" style="background:var(--v)">Ver productos</button>
  <button class="cls" id="fclr">Limpiar filtros</button>
</div></div>

{tt}<div class="toast" id="toast"></div>

<footer>
  <b>WOWCYK · Venta mayorista</b><br>
  Lista de precios del 22/11/2026. Precios por unidad, válidos solo con transferencia; pueden cambiar sin aviso.<br>
  Consultas: <a href="https://wa.me/5493794235712">3794235712</a>
</footer>

<script>
{open('tools/mayorista_stock.js').read()}
</script>
</body>
</html>
"""
open('mayorista-stock.html', 'w').write(page)
print('productos', len(prods), 'unidades', unidades, 'bytes', len(page))
