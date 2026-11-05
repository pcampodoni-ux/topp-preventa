// Releva GAP Factory (Clearance bebé, toddler y niños) hasta USD MAX con talles en stock.
// Uso: node tools/relevar_gap.mjs > tools/gf_raw.json
const MAX = +(process.env.MAX || 20);
const CATS = { tg: [1042786, 165], tb: [1042787, 166], bg: [1091767, 165], bb: [1091779, 166], g: [1042785, 48], b: [1042766, 16] };
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36';
const H = { 'User-Agent': UA, 'Accept-Language': 'en-US,en;q=0.9' };
const sleep = ms => new Promise(r => setTimeout(r, ms));
async function get(url, json) {
  for (let i = 0; i < 3; i++) {
    try { const r = await fetch(url, { headers: H }); if (r.ok) return json ? r.json() : r.text(); console.error('HTTP', r.status, url); }
    catch (e) { console.error('ERR', String(e), url); }
    await sleep(1500 * (i + 1));
  }
  return null;
}
const all = {};
for (const [k, [cid, dep]] of Object.entries(CATS)) {
  let p = 0, tot = 1;
  while (p < tot) {
    const j = await get(`https://api.gapfactory.com/commerce/search/products/v2/cc?brand=gapfs&market=us&cid=${cid}&locale=en_US&pageSize=200&pageNumber=${p}&ignoreInventory=false&department=${dep}`, true);
    if (!j) break;
    tot = +j.pagination.pageNumberTotal;
    const sub = {}; (j.categories || []).forEach(c => c.ccList.forEach(x => sub[x.ccId] = c.subCategoryName));
    for (const s of j.products) for (const c of s.styleColors) {
      if (all[c.ccId]) continue;
      const ims = c.images || [];
      const im = ims.find(i => i.type === 'P01_PRST') || ims.find(i => i.type === 'P01') || {};
      all[c.ccId] = { k, pid: c.ccId, name: c.styleName || s.styleName, type: s.webProductType || '', sub: sub[c.ccId] || '', color: c.ccShortDescription || c.ccName || '',
        price: +c.effectivePrice, reg: +c.regularPrice, inv: c.inventoryStatus, img: (im.path || '').replace(/^\/?webcontent\//, '') };
    }
    p++;
  }
}
const cand = Object.values(all).filter(a => a.inv === 'In Stock' && a.price <= MAX);
console.error('candidatos', cand.length, 'de', Object.keys(all).length);
let done = 0;
async function pdp(a) {
  const t = await get('https://www.gapfactory.com/browse/product.do?pid=' + a.pid);
  if (!t) { a.err = 1; return; }
  a.sizes = [...t.matchAll(/<input[^>]*name="buybox-sizeDimension1"[^>]*>/g)].map(m => {
    const id = (m[0].match(/id="pdp_buybox_dimension_([^"]+)"/) || [])[1];
    const tid = (m[0].match(/data-testid="([^"]+)"/) || [])[1] || '';
    return [id, /outofstock/.test(tid) ? 0 : 1];
  });
  try {
    for (const s of t.matchAll(/<script type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/g)) {
      const j = JSON.parse(s[1]);
      if (j.offers) {
        const ins = j.offers.filter(o => /InStock/.test(o.availability)).map(o => +o.price);
        if (ins.length) a.pmax = Math.max(...ins);
        a.desc = (j.description || '').slice(0, 400);
      }
    }
  } catch (e) {}
}
const q = process.env.SKIP_PDP ? [] : [...cand];
await Promise.all(Array.from({ length: 6 }, async () => { while (q.length) { await pdp(q.shift()); if (++done % 100 === 0) console.error('pdp', done); await sleep(150); } }));
console.log(JSON.stringify(cand));
