// Completa los talles de tools/gf_raw.json usando un Chromium real (Playwright) desde gapfactory.com.
const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const raw = JSON.parse(fs.readFileSync('tools/gf_raw.json', 'utf8'));
  const b = await chromium.launch();
  const ctx = await b.newContext({ userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36', locale: 'en-US' });
  const p = await ctx.newPage();
  await p.goto('https://www.gapfactory.com/browse/category.do?cid=1042786', { waitUntil: 'domcontentloaded', timeout: 60000 }).catch(e => console.error('home', String(e)));
  await p.waitForTimeout(4000);
  const pids = raw.map(a => a.pid);
  const res = await p.evaluate(async (pids) => {
    const out = {}; const q = [...pids];
    async function w() { while (q.length) { const pid = q.shift();
      try { const t = await fetch('/browse/product.do?pid=' + pid).then(r => r.text());
        const d = new DOMParser().parseFromString(t, 'text/html');
        const sizes = [...d.querySelectorAll('input[name="buybox-sizeDimension1"]')].map(i => [i.id.replace('pdp_buybox_dimension_', ''), /outofstock/.test(i.getAttribute('data-testid') || '') ? 0 : 1]);
        let pmax = null, desc = '';
        try { const j = [...d.querySelectorAll('script[type="application/ld+json"]')].map(s => JSON.parse(s.textContent)).find(j => j.offers);
          const ins = j.offers.filter(o => /InStock/.test(o.availability)).map(o => +o.price); if (ins.length) pmax = Math.max(...ins); desc = (j.description || '').slice(0, 300); } catch (e) {}
        out[pid] = { sizes, pmax, desc, len: t.length };
      } catch (e) { out[pid] = { err: String(e) }; } } }
    await Promise.all([w(), w(), w(), w(), w(), w()]); return out;
  }, pids);
  let ok = 0;
  for (const a of raw) { const r = res[a.pid] || {}; Object.assign(a, r); if (r.sizes && r.sizes.length) ok++; }
  console.error('con talles', ok, 'de', raw.length, 'ejemplo', JSON.stringify(res[pids[0]]).slice(0, 300));
  fs.writeFileSync('tools/gf_raw.json', JSON.stringify(raw));
  await b.close();
})();
