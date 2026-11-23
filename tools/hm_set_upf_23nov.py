#!/usr/bin/env python3
"""23/11 (pedido de Patricio): Set UPF 50 de 3 piezas (remera manga larga + short de baño + gorra con cubrenuca) H&M 1139368013,
USD 27,99 (liquidación, antes 39,99), 4 talles con stock. Peso estimado 150 g (sin fuente). Mismo precio que hm_sale_23nov.py
(×1,9, flete por peso). Agrega a hm_verano.tsv, revision/esperado.json y la tarjeta en index.html."""
import csv, json, os, sys, html
T = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, T)
import precio as P
code, cat, gen, nom, g, u = '1139368013', 'Mallas', 'Unisex', 'Set UPF 50 Remera + Short de Baño + Gorra Animales Marinos Turquesa', 150, 27.99
tal = ['2-6M', '6-12M', '1-2Y', '2-4Y']; tls = ['2-6M', '6-12M', '1-2 años', '2-4 años']
img = 'https://image.hm.com/assets/hm/fb/e0/fbe0ba4859707a14532ba1dc78b439a57054f6ed.jpg'
pr = P.precio(u, P.COT, g / 1000 * 26.5 + 0.85)
p = os.path.join(T, 'hm_verano.tsv'); base = list(csv.DictReader(open(p, encoding='utf-8'), delimiter='\t'))
if code not in {r['code'] for r in base}:
    base.append(dict(code=code, cat=cat, gen=gen, nombre=nom, usd=f'{u:g}', talles='|'.join(tls), img=img, fijo=str(pr), marca='hm', grupo='h',
                     edad='Bebés|Niños', pdp=f'/en_us/productpage.{code}.html'))
    w = csv.DictWriter(open(p, 'w', encoding='utf-8', newline=''), fieldnames=list(base[0].keys()), delimiter='\t', lineterminator='\n', extrasaction='ignore')
    w.writeheader(); w.writerows(base)
E = json.load(open(os.path.join(T, 'revision', 'esperado.json'))); E['hm'][code] = {'s': tal, 'u': u}
json.dump(E, open(os.path.join(T, 'revision', 'esperado.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
IDX = os.path.join(T, '..', 'index.html'); s = open(IDX, encoding='utf-8').read()
if f'data-code="{code}"' not in s:
    n = html.escape(nom); url = f'https://www2.hm.com/en_us/productpage.{code}.html'; f = '$' + f'{pr:,}'.replace(',', '.')
    bt = lambda xs: ''.join(f'<button class="tl" data-t="{x}">{x}</button>' for x in xs)
    c = (f'<article class="card" data-grupo="h" data-marca="hm" data-cat="Trajes de baño" data-edad="Bebés|Niños" data-gen="{gen}" data-talles="{"|".join(tls)}" data-code="{code}" data-nom="{n}" data-precio="{pr}">\n'
         f'<a class="ph" href="{url}" target="_blank" rel="noopener"><img loading="lazy" src="{img}?imwidth=600" alt="{n}" onerror="this.style.opacity=0"></a>\n'
         f'<div class="bd">\n<span class="tag">H&M · Trajes de baño · Bebés y Niños</span>\n'
         f'<h3><a class="nm" href="{url}" target="_blank" rel="noopener">{n}</a></h3>\n<div class="pr"><b>{f}</b></div>\n'
         f'<p class="lb">Talles bebés</p>\n<div class="tls">{bt(tls[:2])}</div>\n<p class="lb">Talles (edad)</p>\n<div class="tls">{bt(tls[2:])}</div>\n'
         f'<button class="add" disabled>Elegí un talle</button>\n</div></article>\n')
    k = s.index('<article class="card" data-grupo="h"'); s = s[:k] + c + s[k:]   # primera del grupo H&M
    open(IDX, 'w', encoding='utf-8').write(s)
print(nom, '| USD', u, '|', pr, '|', tls)
