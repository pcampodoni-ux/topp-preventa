// Releva una sección de carters.com (por defecto /c/clearance) con Chromium real: códigos, nombre, foto, talles en stock y precio.
// Uso: SECCION=/c/clearance MAX=20 node tools/relevar_carters.js  → tools/carters_raw.json
const { chromium } = require('playwright'); const fs = require('fs');
const SECCION = process.env.SECCION || '/c/clearance', MAX = +(process.env.MAX || 20);
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36', locale: 'en-US', viewport: { width: 1366, height: 900 } });
  const p = await ctx.newPage();
  await p.goto('https://www.carters.com' + SECCION, { waitUntil: 'domcontentloaded', timeout: 90000 });
  await p.waitForTimeout(6000);
  const total = await p.evaluate(() => +((document.body.innerText.match(/([\d,]+)\s+items/i) || [])[1] || '0').replace(/,/g, ''));
  console.error('items en la sección', total);
  let prev = 0;
  for (let k = 0; k < 80; k++) {
    const n = await p.evaluate(() => new Set([...document.querySelectorAll('a[href*="/p/"]')].map(a => (a.href.match(/V_([A-Z0-9]+)/) || [])[1]).filter(Boolean)).size);
    if (k % 5 === 0) console.error('cargados', n);
    if (n >= total - 2) break;
    const clicked = await p.evaluate(() => { const bt = [...document.querySelectorAll('button,a')].find(x => /^(load more|load all)/i.test((x.innerText || '').trim())); if (bt) { bt.scrollIntoView(); bt.click(); return true; } window.scrollTo(0, document.body.scrollHeight); return false; });
    await p.waitForTimeout(clicked ? 3500 : 2000);
    if (n === prev && !clicked && k > 3) break; prev = n;
  }
  const codes = await p.evaluate(() => [...new Set([...document.querySelectorAll('a[href*="/p/"]')].map(a => (a.href.match(/V_([A-Z0-9]+)/) || [])[1]).filter(Boolean))]);
  console.error('códigos', codes.length);
  const res = await p.evaluate(async (codes) => {
    const out = []; const q = [...codes];
    async function w() { while (q.length) { const c = q.shift();
      try { const t = await fetch('/p/x/V_' + c).then(r => r.text());
        const d = new DOMParser().parseFromString(t, 'text/html'); let prod = null;
        for (const s of d.querySelectorAll('script[type="application/ld+json"]')) { try { const j = JSON.parse(s.textContent); for (const o of (Array.isArray(j) ? j : [j])) if (o.hasVariant || (o['@type'] === 'Product' && !prod)) prod = o; } catch (e) {} }
        const vs = prod && prod.hasVariant ? prod.hasVariant.map(z => ({ s: z.size || 'OS', p: +(z.offers && z.offers.price || 0), st: /InStock/.test(z.offers && z.offers.availability || '') }))
          : (prod && prod.offers ? [{ s: 'OS', p: +(prod.offers.price || 0), st: /InStock/.test(prod.offers.availability || '') }] : []);
        let img = prod && (Array.isArray(prod.image) ? prod.image[0] : prod.image) || ''; if (typeof img === 'object') img = img.url || img.contentUrl || '';
        out.push({ code: c, name: prod && prod.name, img: String(img).replace(/^.*\/default\//, '').replace(/\?.*$/, ''), vs, isNew: /"c_isNew"\s*:\s*true/.test(t), crumbs: (t.match(/"c_merchClass"\s*:\s*"([^"]+)"/) || [])[1] || '' });
      } catch (e) { out.push({ code: c, err: String(e) }); } } }
    await Promise.all([w(), w(), w(), w(), w(), w()]); return out;
  }, codes);
  const ok = res.filter(r => r.vs && r.vs.length).length;
  console.error('con datos', ok, 'de', res.length, 'ejemplo', JSON.stringify(res[0]).slice(0, 300));
  fs.writeFileSync('tools/carters_raw.json', JSON.stringify(res));
  await b.close();
})();
