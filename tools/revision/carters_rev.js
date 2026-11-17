// Revisión de stock y precio de Carter's/OshKosh (se pega en una pestaña de www.carters.com con javascript_tool).
// Lee el stock/precio de referencia de topp.wowcyk.com y deja en window.__REV solo los productos que cambiaron.
(async () => {
  const E = (await (await fetch('https://topp.wowcyk.com/tools/revision/esperado.json?t=' + Date.now(), { cache: 'no-store' })).json()).carters;
  window.__REV = {}; window.__revErr = []; window.__revDone = 0; const q = Object.keys(E); window.__revTotal = q.length;
  async function one(c) {
    const r0 = await fetch('/p/x/V_' + c); if (r0.status === 404) return { gone: 1 }; if (!r0.ok) throw new Error('st' + r0.status);
    const t = await r0.text(); const d = new DOMParser().parseFromString(t, 'text/html'); let prod = null;
    for (const s of d.querySelectorAll('script[type="application/ld+json"]')) { try { const j = JSON.parse(s.textContent); for (const o of (Array.isArray(j) ? j : [j])) if (o.hasVariant || (o['@type'] === 'Product' && !prod)) prod = o; } catch (e) {} }
    if (!prod) { if (/c_websiteBrand/.test(t)) return { gone: 1 }; throw new Error('sin datos'); }
    const vs = prod.hasVariant ? prod.hasVariant.map(z => ({ s: z.size || 'OS', p: +(z.offers && z.offers.price || 0), st: /InStock/.test(z.offers && z.offers.availability || '') }))
      : (prod.offers ? [{ s: 'OS', p: +(prod.offers.price || 0), st: /InStock/.test(prod.offers.availability || '') }] : []);
    const st = vs.filter(v => v.st); if (!st.length) return { gone: 1 };
    return { s: st.map(v => v.s), p: Math.max(...st.map(v => v.p)), x: /c_promoCallouts":\[[^\]]*FRIDAY30/.test(t) };
  }
  async function w() { while (q.length) { const c = q.shift(); let ok = false;
    for (let k = 0; k < 3 && !ok; k++) { try { const r = await one(c); const e = E[c];
      if (r.gone || r.p !== e.p || r.x !== e.x || r.s.join('|') !== e.s.join('|')) window.__REV[c] = r; ok = true; } catch (e) { await new Promise(z => setTimeout(z, 3000)); } }
    if (!ok) window.__revErr.push(c); window.__revDone++; } }
  for (let i = 0; i < 6; i++) w();
  return q.length;
})()
