{
const WA='5493794235712', MIN=25;
const $=id=>document.getElementById(id);
const fmt=n=>'$'+Math.round(n).toLocaleString('es-AR');
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const cards=[...document.querySelectorAll('.card')];
const F={grupo:'',q:'',cat:new Set(),edad:new Set(),gen:new Set(),talle:new Set(),s:''};
const store={get(k){try{return JSON.parse(localStorage.getItem(k))}catch(e){return null}},set(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}};
let cart=store.get('wowmay_cart')||[];   /* [{code,id,nom,t,precio,q,max}] */
const norm=s=>s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'');
cards.forEach((c,i)=>{c._o=i;c._s=norm(c.dataset.nom+' '+c.dataset.cat+' '+c.dataset.talles.replace(/\|/g,' '))});

function toast(m){const t=$('toast');t.textContent=m;t.classList.add('on');clearTimeout(t._h);t._h=setTimeout(()=>t.classList.remove('on'),1800)}

/* ---------- filtros ---------- */
function aplicar(){
  const q=norm(F.q.trim()).split(/\s+/).filter(Boolean);let n=0;
  cards.forEach(c=>{const d=c.dataset,ts=d.talles.toUpperCase().split('|');
    const ok=(!F.grupo||d.grupo===F.grupo)&&(!F.cat.size||F.cat.has(d.cat))&&(!F.edad.size||F.edad.has(d.edad))&&(!F.gen.size||F.gen.has(d.gen))
      &&(!F.talle.size||ts.some(t=>F.talle.has(t)))&&q.every(w=>c._s.includes(w));
    c.style.display=ok?'':'none';if(ok)n++});
  const g=$('grid');const arr=[...cards];
  if(F.s)arr.sort((a,b)=>F.s==='asc'?a.dataset.precio-b.dataset.precio:b.dataset.precio-a.dataset.precio);else arr.sort((a,b)=>a._o-b._o);
  arr.forEach(c=>g.appendChild(c));
  $('empty').style.display=n?'none':'block';
  const act=[...F.cat,...F.edad,...F.gen,...[...F.talle].map(t=>'Talle '+t)];
  $('fbn').textContent=act.length;$('fbn').classList.toggle('on',act.length>0);
  $('factv').classList.toggle('on',act.length>0);$('factt').textContent=act.join(' · ');
  $('sinfo').classList.toggle('on',!!F.q.trim());$('sinfo').textContent=F.q.trim()?n+' resultado'+(n===1?'':'s')+' para "'+F.q.trim()+'"':'';
  document.body.classList.toggle('buscando',!!F.q.trim());
}
function limpiar(){F.cat.clear();F.edad.clear();F.gen.clear();F.talle.clear();F.s='';
  document.querySelectorAll('#fov .chip').forEach(c=>c.classList.toggle('on',c.dataset.s===''));aplicar()}
$('gtabs').addEventListener('click',e=>{const b=e.target.closest('.gt');if(!b)return;F.grupo=b.dataset.g;
  document.querySelectorAll('.gt').forEach(x=>x.classList.toggle('on',x===b));aplicar()});
$('q').addEventListener('input',e=>{F.q=e.target.value;$('sbox').classList.toggle('on',!!F.q);aplicar()});
$('qx').addEventListener('click',()=>{$('q').value='';F.q='';$('sbox').classList.remove('on');aplicar();$('q').focus()});
$('fov').addEventListener('click',e=>{const c=e.target.closest('.chip');
  if(c){if(c.dataset.s!==undefined){F.s=c.dataset.s;c.parentNode.querySelectorAll('.chip').forEach(x=>x.classList.toggle('on',x===c))}
    else{const set=F[c.dataset.f],v=c.dataset.v;set.has(v)?set.delete(v):set.add(v);c.classList.toggle('on',set.has(v))}aplicar();return}
  if(e.target.id==='fov')$('fov').classList.remove('on')});
$('fbtn').addEventListener('click',()=>$('fov').classList.add('on'));
$('fok').addEventListener('click',()=>{$('fov').classList.remove('on');$('grid').scrollIntoView({behavior:'smooth'})});
$('fclr').addEventListener('click',limpiar);$('factc').addEventListener('click',limpiar);
$('emclr').addEventListener('click',e=>{e.preventDefault();limpiar();$('q').value='';F.q='';aplicar()});

/* ---------- tabla de talles ---------- */
document.addEventListener('click',e=>{if(e.target.closest('[data-tt]'))$('ttov').classList.add('on')});
$('ttcls').addEventListener('click',()=>$('ttov').classList.remove('on'));
$('ttov').addEventListener('click',e=>{if(e.target.id==='ttov')$('ttov').classList.remove('on');
  const b=e.target.closest('[data-ttb]');if(b){document.querySelectorAll('[data-ttb]').forEach(x=>x.classList.toggle('on',x===b));
  document.querySelectorAll('.ttc').forEach(x=>x.classList.toggle('on',x.dataset.ttc===b.dataset.ttb))}});

/* ---------- tarjetas ---------- */
const enCarro=(code,t)=>cart.find(l=>l.code===code&&l.t===t);
function pintarAdd(c){const tl=c.querySelector('.tl.on'),a=c.querySelector('.add');
  if(!tl){a.disabled=true;a.textContent='Elegí un talle';a.classList.remove('done');return}
  const l=enCarro(c.dataset.code+'#'+c.dataset.id,tl.dataset.t),max=+tl.dataset.n,q=l?l.q:0;
  a.disabled=q>=max;a.classList.toggle('done',q>0);
  a.textContent=q>=max?`Agregaste ${q} (no hay más)`:q?`Agregar otro (llevás ${q})`:'Agregar al pedido'}
$('grid').addEventListener('click',e=>{
  const tl=e.target.closest('.tl');if(tl){const c=tl.closest('.card');c.querySelectorAll('.tl').forEach(x=>x.classList.toggle('on',x===tl));pintarAdd(c);return}
  const a=e.target.closest('.add');if(!a||a.disabled)return;
  const c=a.closest('.card'),t=c.querySelector('.tl.on');if(!t)return;
  const code=c.dataset.code+'#'+c.dataset.id;let l=enCarro(code,t.dataset.t);
  if(l){if(l.q<l.max)l.q++}else cart.push(l={code,id:c.dataset.id,nom:c.dataset.nom,t:t.dataset.t,precio:+c.dataset.precio,q:1,max:+t.dataset.n});
  guardar();pintarAdd(c);toast(`Agregado: ${c.dataset.nom} · ${t.dataset.t}`)});

/* ---------- pedido ---------- */
const unid=()=>cart.reduce((a,l)=>a+l.q,0), total=()=>cart.reduce((a,l)=>a+l.q*l.precio,0);
function guardar(){cart=cart.filter(l=>l.q>0);store.set('wowmay_cart',cart);resumen()}
function resumen(){
  const u=unid(),t=total(),f=Math.max(0,MIN-u);
  $('cartbar').classList.toggle('on',u>0);
  $('cn').textContent=`${u} unidad${u===1?'':'es'} · `+(f?`faltan ${f} para el mínimo`:'mínimo alcanzado');$('ct').textContent=fmt(t);
  $('mnum').innerHTML=`${u} <small>/ 25 unidades</small>`;$('mtrack').firstElementChild.style.width=Math.min(100,u/MIN*100)+'%';
  $('mtrack').classList.toggle('full',u>=MIN);
  $('mmsg').textContent=f?`Te faltan ${f} unidad${f===1?'':'es'} para llegar al mínimo.`:'Llegaste al mínimo: ya podés enviar tu pedido.';
  $('mu').textContent=`${u} unidad${u===1?'':'es'}`;$('mt').textContent=fmt(t);
  $('minw').className='minw'+(f?'':' ok');$('minw').textContent=f?`Te faltan ${f} unidad${f===1?'':'es'} para el mínimo de 25 (podés mezclar modelos y talles).`:'Pedido listo: completá tus datos y envialo.';
  $('items').innerHTML=cart.map((l,i)=>`<div class="li"><div class="ln">${esc(l.nom)}<em>Talle ${esc(l.t)} · ${fmt(l.precio)} c/u · ${fmt(l.q*l.precio)}</em><button data-del="${i}">Quitar</button></div>
   <div class="qty"><button data-m="${i}" aria-label="Una menos">−</button><span>${l.q}</span><button data-p="${i}" aria-label="Una más" ${l.q>=l.max?'disabled':''}>+</button></div></div>`).join('')||'<p class="sub">Todavía no agregaste productos.</p>';
}
$('items').addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;const d=b.dataset;
  if(d.del!==undefined)cart[+d.del].q=0;else if(d.m!==undefined)cart[+d.m].q--;else if(d.p!==undefined&&cart[+d.p].q<cart[+d.p].max)cart[+d.p].q++;
  guardar();cards.forEach(c=>{if(c.querySelector('.tl.on'))pintarAdd(c)})});
$('open').addEventListener('click',()=>{resumen();$('ov').classList.add('on')});
$('cls').addEventListener('click',()=>$('ov').classList.remove('on'));
$('ov').addEventListener('click',e=>{if(e.target.id==='ov')$('ov').classList.remove('on')});
document.addEventListener('keydown',e=>{if(e.key==='Escape')document.querySelectorAll('.ov.on').forEach(o=>o.classList.remove('on'))});
const campos=['loc','cli','tel','res','cuit','obs'];
const fd=store.get('wowmay_form')||{};campos.forEach(k=>{if(fd[k])$(k).value=fd[k]});
campos.forEach(k=>$(k).addEventListener('input',()=>{const o={};campos.forEach(x=>o[x]=$(x).value);store.set('wowmay_form',o)}));
$('wa').addEventListener('click',()=>{
  const v=k=>$(k).value.trim(),u=unid();
  const err={locerr:!v('loc'),clerr:!v('cli'),telerr:v('tel').replace(/\D/g,'').length<10,reserr:!v('res')};
  Object.entries(err).forEach(([k,b])=>$(k).classList.toggle('on',b));
  if(u<MIN){toast(`Necesitás al menos ${MIN} unidades (llevás ${u})`);$('minw').scrollIntoView({behavior:'smooth',block:'center'});return}
  if(Object.values(err).some(Boolean)){toast('Completá los datos marcados');return}
  let m=`*Pedido mayorista WOWCYK*\n\n*Local:* ${v('loc')}\n*Nombre:* ${v('cli')}\n*WhatsApp:* ${v('tel')}\n*Ciudad:* ${v('res')}\n`+(v('cuit')?`*CUIT:* ${v('cuit')}\n`:'')+'\n';
  m+=cart.map(l=>`• ${l.q} × ${l.nom} (${l.code.split('#')[0]}) — Talle ${l.t} — ${fmt(l.precio)} c/u = ${fmt(l.q*l.precio)}`).join('\n');
  m+=`\n\n*Total: ${u} unidades — ${fmt(total())}*\nPago con transferencia.`;
  if(v('obs'))m+=`\n\n*Comentarios:* ${v('obs')}`;
  window.open('https://wa.me/'+WA+'?text='+encodeURIComponent(m),'_blank');
});
resumen();aplicar();
}
