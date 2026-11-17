// Revisión de stock y precio de H&M (se pega en una pestaña de www2.hm.com abierta en una página de producto, con javascript_tool).
// Si H&M muestra el desafío anti-bot, la página de producto abierta en la pestaña lo resuelve; los bloqueados quedan en window.__revBlk.
(async () => {
  const E = (await (await fetch('https://topp.wowcyk.com/tools/revision/esperado.json?t=' + Date.now(), { cache: 'no-store' })).json()).hm;
  window.__REV = {}; window.__revBlk = []; window.__revDone = 0; const by = {};
  for (const c of Object.keys(E)) (by[c.slice(0, 7)] = by[c.slice(0, 7)] || []).push(c);
  const q = Object.entries(by); window.__revTotal = q.length; const sl = ms => new Promise(r => setTimeout(r, ms));
  async function base(b, codes) {
    const r = await fetch('/en_us/productpage.' + codes[0] + '.html');
    if (r.status === 404) { for (const c of codes) window.__REV[c] = { gone: 1 }; return true; }
    const t = await r.text(); const m = t.match(/<script id="__NEXT_DATA__"[^>]*>([\s\S]*?)<\/script>/); if (!m) return false;
    const pp = JSON.parse(m[1]).props.pageProps.productPageProps; const p = pp && pp.aemData && pp.aemData.productArticleDetails;
    if (!p) { for (const c of codes) window.__REV[c] = { gone: 1 }; return true; }
    const av = new Set((pp.ssrAvailability && pp.ssrAvailability.availability) || []);
    for (const c of codes) { const v = p.variations && p.variations[c]; if (!v) { window.__REV[c] = { gone: 1 }; continue; }
      const s = (v.sizes || []).filter(z => av.has(z.sizeCode)).map(z => z.name); const u = Math.min(...[+v.whitePriceValue, +v.redPriceValue].filter(x => x > 0));
      if (!s.length) { window.__REV[c] = { gone: 1 }; continue; }
      const e = E[c]; if (u !== e.u || s.join('|') !== e.s.join('|')) window.__REV[c] = { s, u }; }
    return true;
  }
  async function w() { while (q.length) { const [b, codes] = q.shift(); let ok = false; try { ok = await base(b, codes); } catch (e) {} if (!ok) window.__revBlk.push(...codes); window.__revDone++; await sl(700); } }
  w(); w();
  return q.length;
})()
