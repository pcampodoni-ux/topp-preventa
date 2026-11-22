"""Relevamiento del stock de wowcyk.com (Tienda Nube) con talles por producto.

Recorre el listado /productos/page/N/ y cada página de producto, lee el JSON de
variantes (data-variants) y guarda tools/wowcyk_stock.json:
[{url, nombre, img, precio, sku, desc, variantes:[{opciones:[...], stock, disponible, precio}]}]
Lo corre el workflow "Relevar WOWCYK" (los servidores de Claude no llegan a wowcyk.com).
"""
import html
import json
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE = 'https://www.wowcyk.com'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36'


def get(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Language': 'es-AR'})
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read().decode('utf-8', 'replace')
        except Exception as e:  # noqa: BLE001
            print('reintento', url, e, file=sys.stderr)
            time.sleep(2 + i * 3)
    return ''


def urls_listado():
    urls, page = [], 1
    while True:
        h = get(f'{BASE}/productos/page/{page}/' if page > 1 else f'{BASE}/productos/')
        found = re.findall(r'"@id":\s*"(https://www\.wowcyk\.com/productos/[^"]+)"', h)
        nuevos = [u for u in found if u not in urls]
        if not nuevos:
            break
        urls += nuevos
        print('pagina', page, len(nuevos), file=sys.stderr)
        page += 1
        if page > 60:
            break
    return urls


def producto(url):
    h = get(url)
    if not h:
        return {'url': url, 'error': 'sin respuesta'}
    out = {'url': url}
    for m in re.finditer(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', h, re.S):
        try:
            j = json.loads(m.group(1))
        except Exception:  # noqa: BLE001
            continue
        if isinstance(j, dict) and j.get('@type') == 'Product':
            out.update(nombre=j.get('name'), img=j.get('image'), sku=j.get('sku'), desc=j.get('description'),
                       precio=(j.get('offers') or {}).get('price'))
            break
    m = re.search(r'data-variants="([^"]*)"', h)
    variantes = []
    if m:
        try:
            for v in json.loads(html.unescape(m.group(1))):
                ops = [v.get(k) for k in ('option0', 'option1', 'option2') if v.get(k)]
                variantes.append({'opciones': ops, 'stock': v.get('stock'), 'disponible': v.get('available'),
                                  'precio': v.get('price_number'), 'sku': v.get('sku')})
        except Exception as e:  # noqa: BLE001
            out['error'] = f'variantes: {e}'
    nombres = re.findall(r'<label class="form-label[^"]*" for="variation_\d+">\s*([^<]+?)\s*</label>', h)
    out['opciones_nombres'] = nombres[:3]
    out['variantes'] = variantes
    return out


def main():
    urls = urls_listado()
    print('productos en listado', len(urls), file=sys.stderr)
    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(producto, urls))
    json.dump(res, open('tools/wowcyk_stock.json', 'w'), ensure_ascii=False, indent=0)
    con = sum(1 for r in res if r.get('variantes'))
    print('listo', len(res), 'con variantes', con, file=sys.stderr)


if __name__ == '__main__':
    main()
