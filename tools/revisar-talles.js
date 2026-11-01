// Revisión de talles TOPP — se pega en el navegador estando en una página de www.carters.com.
// Lee el catálogo publicado (topp.wowcyk.com), revisa cada producto en carters.com
// y deja el resultado en window.__chk (y en localStorage 'topp_chk') cuando window.__cd === true.
(async () => {
  const r = await fetch('https://topp.wowcyk.com/?nc=' + Date.now(), { cache: 'no-store' });
  const d = new DOMParser().parseFromString(await r.text(), 'text/html');
  const cards = [...d.querySelectorAll('.card')].map(c => ({
    code: c.dataset.code, cat: c.dataset.cat, talles: c.dataset.talles.split('|'),
    precio: +c.dataset.precio, nom: c.dataset.nom }));
  const ACC = ['Medias', 'Mantas', 'Mitones', 'Ropa interior'];
  const norm = s => s.toLowerCase().replace(/[^0-9a-z]/g, '').replace(/^(os|osz|unico)$/, 'os');
  const nAcc = s => norm(s.normalize('NFD').replace(/[̀-ͯ]/g, '')).replace(/[mt]/g, '');
  window.__chk = []; window.__cd = false; window.__ci = 0; window.__total = cards.length;
  for (const c of cards) {
    window.__ci++;
    try {
      const t = await (await fetch('/p/x/V_' + c.code, { cache: 'no-store' })).text();
      const doc = new DOMParser().parseFromString(t, 'text/html');
      let prod = null;
      for (const s of doc.querySelectorAll('script[type="application/ld+json"]')) {
        try { const j = JSON.parse(s.textContent);
          for (const o of (Array.isArray(j) ? j : [j])) if (o.hasVariant || (o['@type'] === 'Product' && !prod)) prod = o;
        } catch (e) {}
      }
      const vs = prod && prod.hasVariant
        ? prod.hasVariant.map(z => ({ s: z.size || 'OS', p: +(z.offers && z.offers.price || 0), st: /InStock/.test(z.offers && z.offers.availability || '') }))
        : (prod && prod.offers ? [{ s: 'OS', p: +prod.offers.price, st: /InStock/.test(prod.offers.availability || '') }] : []);
      const f = ACC.includes(c.cat) ? nAcc : (x => x);
      const inst = {}; vs.filter(z => z.st).forEach(z => inst[f(z.s)] = z.p);
      const still = c.talles.filter(t => f(t) in inst);
      const gone = c.talles.filter(t => !(f(t) in inst));
      const usd = Math.max(0, ...still.map(t => inst[f(t)]));
      window.__chk.push({ code: c.code, cat: c.cat, nom: c.nom, precio: c.precio, still, gone, usd, noLD: !prod });
    } catch (e) { window.__chk.push({ code: c.code, err: String(e) }); }
    await new Promise(res => setTimeout(res, 150));
  }
  localStorage.setItem('topp_chk', JSON.stringify(window.__chk));
  window.__cd = true;
})();
