#!/usr/bin/env python3
"""17/11: mejoras de la landing (se aplica una sola vez sobre index.html; armar_pedido.py las conserva).
- Botones: grupo de WhatsApp (WA_GRUPO) y tienda con stock wowcyk.com.
- Buscador fijo arriba: busca en TODAS las marcas por prenda, dibujo, color, talle o código (con sinónimos y sin tildes).
- Tira de categorías con foto y cantidad, de un toque.
- Código corto en cada producto (Cód. XXXX, estable) para historias y posteos; se busca escribiéndolo.
- Links: ?q=texto abre la búsqueda (ej. topp.wowcyk.com/?q=pijama 2T); ?p=CÓDIGO sigue andando.
Uso: python3 tools/landing_buscador.py [link del grupo de WhatsApp]"""
import os, re, sys
IDX = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'index.html')
s = open(IDX, encoding='utf-8').read()
grupo = sys.argv[1] if len(sys.argv) > 1 else ''
if 'id="sbar"' in s:
    if grupo: s = re.sub(r'var WA_GRUPO="[^"]*";', f'var WA_GRUPO="{grupo}";', s); open(IDX, 'w', encoding='utf-8').write(s); print('link del grupo actualizado')
    else: print('ya aplicado')
    sys.exit()

CSS = """
/* 17/11: botones, buscador, tira de categorías y código corto */
.links{background:#fff;padding:14px 0 4px}
.links .wrap{display:grid;grid-template-columns:1fr 1fr;gap:10px;max-width:760px}
.lk{display:flex;flex-direction:column;justify-content:center;text-decoration:none;border-radius:12px;padding:11px 14px;font-weight:700;font-size:14.5px;line-height:1.2;color:#fff}
.lk small{font-weight:400;font-size:11.5px;opacity:.92;margin-top:3px}
.lk.wa{background:#25a35a}.lk.st{background:#fff;color:var(--v);border:2px solid var(--v)}
.lk[hidden]{display:none}.links .wrap.uno{grid-template-columns:1fr}
@media(max-width:420px){.lk{font-size:13.5px;padding:10px 11px}}
.sbar{position:sticky;top:0;z-index:46;background:rgba(242,248,248,.97);padding:10px 0;border-bottom:1px solid var(--gr)}
.sbox{display:flex;align-items:center;background:#fff;border:2px solid var(--v);border-radius:99px;padding:0 6px 0 14px}
.sbox input{flex:1;min-width:0;border:0;outline:0;background:none;font:inherit;font-size:16px;padding:11px 6px;color:var(--tx)}
.sbox .x{border:0;background:var(--gr);color:var(--tx);border-radius:99px;width:30px;height:30px;font-size:15px;cursor:pointer;display:none}
.sbox.on .x{display:block}
.sbox input::-webkit-search-cancel-button{-webkit-appearance:none;display:none}
.sinfo{font-size:12.5px;color:var(--v);padding:6px 4px 0;display:none}.sinfo.on{display:block}
.fmini{top:var(--sbh,0px)}.fbar{top:var(--sbh,0px)}
.cstrip{display:flex;gap:12px;overflow-x:auto;padding:12px 0 6px;scrollbar-width:none}.cstrip::-webkit-scrollbar{display:none}
.cs{flex:0 0 auto;width:76px;border:0;background:none;font:inherit;cursor:pointer;text-align:center;color:var(--tx);padding:0}
.cs i{display:block;width:68px;height:68px;margin:0 auto 5px;border-radius:50%;background:#fff center/contain no-repeat;border:2px solid var(--v2)}
.cs span{display:block;font-size:11.5px;line-height:1.15}.cs em{display:block;font-style:normal;font-size:10.5px;color:#9aa4a6}
.cs.on i{border-color:var(--v);box-shadow:0 0 0 3px var(--v2)}.cs.on span{color:var(--v);font-weight:700}
body.buscando .cstrip,body.buscando .gtabs{opacity:.35}
.sc{font-size:11px;letter-spacing:1px;color:#9aa4a6}.sc b{color:var(--tx)}
.emq a{color:var(--v);font-weight:700}
.fmini{display:none!important}.fbar{display:none}
#fov .fbar{display:block;position:static;border:0;background:none;padding:6px 0 0}#fov .fbar .wrap{padding:0}#fov .frow{flex-wrap:wrap}
.srow{display:flex;gap:8px;align-items:center}.srow .sbox{flex:1;min-width:0}
.fbtn{flex:0 0 auto;position:relative;border:2px solid var(--v);background:#fff;color:var(--v);border-radius:99px;padding:10px 14px;font:inherit;font-weight:700;font-size:14px;cursor:pointer}
.fbtn b{position:absolute;top:-6px;right:-4px;background:#c0392b;color:#fff;border-radius:99px;font-size:11px;min-width:19px;height:19px;line-height:19px;display:none}.fbtn b.on{display:block}
@media(max-width:420px){.fbtn{padding:10px 11px;font-size:13px}}
@media(max-width:560px){.grid{grid-template-columns:1fr 1fr;gap:10px;padding-top:12px}.bd{padding:9px;gap:6px}.card h3{font-size:13px;min-height:32px}
 .pr b{font-size:17px}.tag{font-size:8.5px;letter-spacing:.8px}.tl{padding:4px 5px;min-width:32px;font-size:11.5px}.add{font-size:12.5px;padding:9px 4px}
 .shr{font-size:11.5px;letter-spacing:0}.lb{font-size:8.5px}}
.factv{display:none;align-items:center;gap:8px;font-size:12.5px;padding:4px 0 0;color:var(--tx)}.factv.on{display:flex}
.factv span{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.factv button{border:0;background:none;color:var(--v);font:inherit;font-weight:700;cursor:pointer;text-decoration:underline}
"""
s = s.replace('</style>', CSS + '</style>', 1)

LINKS = ('<section class="links"><div class="wrap">'
         '<a class="lk wa" id="lkgrupo" href="#" target="_blank" rel="noopener" hidden>💬 Unite al grupo de WhatsApp<small>Enterate primero de cada pedido</small></a>'
         '<a class="lk st" href="https://www.wowcyk.com" target="_blank" rel="noopener">🛍️ Tienda con stock<small>wowcyk.com · productos listos para entregar</small></a>'
         '</div></section>\n\n')
s = s.replace('<section class="steps">', LINKS + '<section class="steps">', 1)

SBAR = ('<div class="sbar" id="sbar"><div class="wrap"><div class="srow"><div class="sbox" id="sbox">🔎<input id="q" type="search" enterkeyhint="search" autocomplete="off" '
        'placeholder="Buscá: remera, pijama 2T, malla…" aria-label="Buscar productos"><button type="button" class="x" id="qx" aria-label="Borrar búsqueda">✕</button></div>'
        '<button type="button" class="fbtn" id="fbtn">⚙ <span>Filtrar</span><b id="fbn"></b></button></div>'
        '<div class="sinfo" id="sinfo"></div></div></div>\n')
s = s.replace('<div class="wrap"><div class="gtabs" id="gtabs"', SBAR + '<div class="wrap"><div class="gtabs" id="gtabs"', 1)
s = s.replace('<div class="fmini" id="fmini">', '<div class="wrap"><div class="cstrip" id="cstrip"></div><div class="factv" id="factv"><span id="factt"></span><button type="button" id="factc">Limpiar filtros</button></div></div>\n<div class="fmini" id="fmini">', 1)

# render(): con búsqueda se ignora la pestaña de marca
old = "var ok=(c.dataset.grupo===F.grupo)&&"
assert old in s
s = s.replace(old, "var ok=(QS.length?qMatch(c):c.dataset.grupo===F.grupo)&&", 1)
old = "  document.getElementById('empty').style.display=n?'none':'block';\n}"
assert old in s
s = s.replace(old, "  document.getElementById('empty').style.display=n?'none':'block';\n  if(window.afterRender)afterRender(n);\n}", 1)
# al tocar una pestaña de marca se borra la búsqueda
old = "    F.grupo=b.dataset.g;\n"
assert old in s
s = s.replace(old, "    F.grupo=b.dataset.g;\n    if(window.qClear)qClear(true);\n", 1)
# variables que render() usa antes de que cargue el buscador
s = s.replace("var F={cat:null,", "var QS=[];function qMatch(){return true;}\nvar F={cat:null,", 1)

JS = r"""
<script>
/* ---------- 17/11: GRUPO DE WHATSAPP, BUSCADOR, CATEGORÍAS CON FOTO Y CÓDIGO CORTO ---------- */
var WA_GRUPO="";
(function(){
  var lg=document.getElementById('lkgrupo');
  if(WA_GRUPO){lg.href=WA_GRUPO;lg.hidden=false;}else{lg.parentNode.classList.add('uno');}
  var N=function(t){return (t||'').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/&quot;|["']/g,' ');};
  /* código corto estable (4 caracteres) a partir del código del producto */
  var AB='23456789ABCDEFGHJKMNPQRSTUVWXYZ';
  function corto(code){var h=2166136261;for(var i=0;i<code.length;i++){h^=code.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}
    var o='';for(var k=0;k<4;k++){o+=AB[h%31];h=Math.floor(h/31);}return o;}
  var MN={carters:"carter's carters",oshkosh:'oshkosh',hm:'h&m hym hm',gapfactory:'gap',skiphop:'skip hop'};
  var GN={Nena:'nena nina nenas ninas chica',Nene:'nene nino nenes ninos varon',Unisex:'unisex nena nene'};
  var EN={'Bebés':'bebe bebes baby','Niños':'nino ninos toddler','Grandes':'grandes'};
  var CARDS=[].slice.call(document.querySelectorAll('.card'));
  var USADOS={};
  CARDS.slice().sort(function(a,b){return a.dataset.code<b.dataset.code?-1:1;}).forEach(function(c){
    var k=c.dataset.code,sc=corto(k);while(USADOS[sc]){k+='*';sc=corto(k);}USADOS[sc]=1;c.dataset.sc=sc;});
  CARDS.forEach(function(c){
    var sc=c.dataset.sc;
    var sh=c.querySelector('.shr'),sp=document.createElement('span');sp.className='sc';sp.innerHTML='Cód. <b>'+sc+'</b>';
    var bd=c.querySelector('.bd');if(sh)bd.insertBefore(sp,sh);else bd.appendChild(sp);
    c._h=' '+N([c.dataset.nom,c.dataset.cat,MN[c.dataset.marca]||c.dataset.marca,GN[c.dataset.gen]||'',
      (c.dataset.edad||'').split('|').map(function(e){return EN[e]||e;}).join(' ')].join(' '))+' ';
    c._t=(c.dataset.talles||'').split('|').map(N);
  });
  /* sinónimos: lo que escribe la clienta → lo que dice el producto */
  var SIN={camiseta:'remera',remerita:'remera',tee:'remera',top:'remera',musculosa:'musculosa',piyama:'pijama',pyjama:'pijama',pijamita:'pijama',
    malla:'malla|short de bano|bikini|enteriza',mallas:'malla|short de bano|bikini|enteriza',spiderman:'hombre arana|spider',minnie:'minnie',mickey:'mickey',disney:'disney',bluey:'bluey',traje:'trajes de bano',pileta:'trajes de bano',bikini:'bikini|dos piezas|malla',
    mameluco:'enterito',jardinero:'enterito|jardinero',osito:'osito|enterito',bermuda:'short',bermudas:'short',jogging:'jogging|pantalon',joggin:'jogging',buzo:'buzo',
    legging:'calza',leggings:'calza',leggin:'calza',calzas:'calza',sombrero:'gorr',gorrito:'gorr',gorra:'gorr',gorro:'gorr',dino:'dinosaur',dinos:'dinosaur',
    bombacha:'bombacha',calzoncillo:'boxer|slip|calzoncillo',boxer:'boxer',bebe:'bebe',baby:'bebe',nina:'nena',nino:'nene',varon:'nene',pollera:'pollera',falda:'pollera',
    conjunto:'set|conjunto',set:'set|conjunto',vestidito:'vestido',jean:'jean',navidad:'navide',navideno:'navide',celeste:'celeste|azul claro',bordo:'bordo'};
  function stem(t){if(/^bod/.test(t))return 'bod';if(t.length>5&&/es$/.test(t)&&!/(ces|les)$/.test(t))return t.slice(0,-2);if(t.length>4&&/s$/.test(t))return t.slice(0,-1);return t;}
  var esTalle=function(t){return /^(\d+(m|t|y)?|nb|pre|xs|s|m|l|xl|\d+-\d+[a-z]?)$/.test(t);};
  window.qMatch=function(c){
    for(var i=0;i<QS.length;i++){var q=QS[i],ok=false;
      if(q.length===4&&c.dataset.sc.toLowerCase()===q)ok=true;
      else if(q.length>=6&&N(c.dataset.code).indexOf(q)>-1)ok=true;
      else if(esTalle(q)){ok=c._t.some(function(t){return t===q||t.indexOf(q)===0&&!/\d/.test(t.charAt(q.length));});
        if(!ok&&!/^\d/.test(q))ok=c._h.indexOf(' '+q+' ')>-1;}
      else{var alts=(SIN[q]||stem(q)).split('|');ok=alts.some(function(a){return c._h.indexOf(a)>-1;});}
      if(!ok)return false;}
    return true;
  };
  var inp=document.getElementById('q'),box=document.getElementById('sbox'),info=document.getElementById('sinfo'),tmr;
  function aplicar(){var v=inp.value;QS=N(v).split(/[\s,]+/).filter(Boolean);
    if(QS.length&&F.cat){var cc=document.querySelector('.chip.on[data-f="cat"]');if(cc){cc.classList.remove('on');F.cat=null;}}
    box.classList.toggle('on',!!v);document.body.classList.toggle('buscando',QS.length>0);render();}
  inp.addEventListener('input',function(){clearTimeout(tmr);tmr=setTimeout(aplicar,180);});
  inp.addEventListener('keydown',function(e){if(e.key==='Enter'){inp.blur();aplicar();var g=document.getElementById('grid');window.scrollTo({top:g.getBoundingClientRect().top+window.pageYOffset-80,behavior:'smooth'});}});
  window.qClear=function(silencio){inp.value='';QS=[];box.classList.remove('on');document.body.classList.remove('buscando');if(!silencio)render();};
  document.getElementById('qx').onclick=function(){qClear();inp.focus();};
  var emp=document.getElementById('empty'),empTxt=emp.innerHTML;
  window.afterRender=function(n){
    if(QS.length){info.classList.add('on');
      info.innerHTML=n?('<b>'+n+'</b> '+(n===1?'producto':'productos')+' para “'+inp.value.trim().replace(/</g,'')+'” en todas las marcas'):'';
      emp.innerHTML=n?'':'<span class="emq">No encontramos “'+inp.value.trim().replace(/</g,'')+'”. Probá con otra palabra (remera, pijama, 2T) o '+
        '<a href="https://wa.me/'+WA+'?text='+encodeURIComponent('Hola! Busco: '+inp.value.trim())+'" target="_blank" rel="noopener">preguntanos por WhatsApp</a>.</span>';
    }else{info.classList.remove('on');emp.innerHTML=empTxt;}
    pintarCats();
  };
  /* tira de categorías con foto */
  var cs=document.getElementById('cstrip');
  function pintarCats(){
    var orden=[],m={};
    CARDS.forEach(function(c){if(c.dataset.grupo!==F.grupo)return;var k=c.dataset.cat;
      if(!m[k]){m[k]={n:0,img:(c.querySelector('img')||{}).src};orden.push(k);}m[k].n++;});
    cs.innerHTML=orden.map(function(k){return '<button type="button" class="cs'+(F.cat===k?' on':'')+'" data-k="'+k+'"><i style="background-image:url(\''+m[k].img+'\')"></i><span>'+k+'</span><em>'+m[k].n+'</em></button>';}).join('');
    cs.querySelectorAll('.cs').forEach(function(b){b.onclick=function(){
      if(QS.length)qClear(true);
      var ch=document.querySelector('.chip[data-f="cat"][data-v="'+b.dataset.k+'"]');if(ch)ch.click();
      var g=document.getElementById('grid');window.scrollTo({top:g.getBoundingClientRect().top+window.pageYOffset-140,behavior:'smooth'});};});
  }
  /* compartir: el texto lleva el código corto */
  CARDS.forEach(function(c){var b=c.querySelector('.shr');if(!b)return;var old=b.onclick;
    b.onclick=function(e){e.preventDefault();e.stopPropagation();var u=location.origin+location.pathname+'?p='+c.dataset.code,
      t=c.dataset.nom+' — '+money(+c.dataset.precio)+' · Cód. '+c.dataset.sc;
      if(navigator.share){navigator.share({title:'TOPP by WOWCYK',text:t,url:u}).catch(function(){});}
      else if(navigator.clipboard){navigator.clipboard.writeText(t+' '+u).then(function(){toast('Link copiado');},function(){toast(u);});}else toast(u);};});
  /* panel de filtros (talle, edad, género, orden) que se abre desde el botón ⚙ */
  var fb=document.querySelector('.fbar'),fov=document.createElement('div');fov.className='ov';fov.id='fov';
  fov.innerHTML='<div class="modal"><h2>Filtros</h2><p class="sub">Elegí talle, edad o género. Se aplican a la marca elegida.</p><div id="fbody"></div>'+
    '<button type="button" class="wa" id="fver">Ver productos</button><button type="button" class="cls" id="flimp">Limpiar filtros</button></div>';
  document.body.appendChild(fov);document.getElementById('fbody').appendChild(fb);
  var catRow=fb.querySelector('.frow.wrap');if(catRow)catRow.style.display='none';
  document.getElementById('fbtn').onclick=function(){fov.classList.add('on');};
  document.getElementById('fver').onclick=function(){fov.classList.remove('on');var g=document.getElementById('grid');window.scrollTo({top:g.getBoundingClientRect().top+window.pageYOffset-140,behavior:'smooth'});};
  fov.onclick=function(e){if(e.target===fov)fov.classList.remove('on');};
  function limpiar(){[].slice.call(document.querySelectorAll('.chip.on[data-f]')).forEach(function(c){c.click();});}
  document.getElementById('flimp').onclick=limpiar;document.getElementById('factc').onclick=limpiar;
  function actFiltros(n){var on=[].slice.call(document.querySelectorAll('.chip.on[data-f]')).filter(function(c){return c.dataset.f!=='cat';}).map(function(c){return c.textContent.trim();});
    var bn=document.getElementById('fbn');bn.textContent=on.length;bn.classList.toggle('on',on.length>0);
    var fa=document.getElementById('factv'),cat=F.cat?[F.cat]:[];var all=cat.concat(on);
    fa.classList.toggle('on',all.length>0);document.getElementById('factt').textContent='Mostrando: '+all.join(' · ');
    document.getElementById('fver').textContent='Ver '+n+(n===1?' producto':' productos');}
  /* al cambiar de marca, si los filtros dejan la pestaña vacía, se limpian */
  document.querySelectorAll('.gt').forEach(function(b){b.addEventListener('click',function(){setTimeout(function(){
    var n=[].slice.call(document.querySelectorAll('.card')).filter(function(c){return c.style.display!=='none';}).length;if(!n)limpiar();},0);});});
  var ar=window.afterRender;window.afterRender=function(n){ar(n);actFiltros(n);};
  /* alto del buscador para que la barra de filtros quede debajo */
  function sbh(){document.documentElement.style.setProperty('--sbh',document.getElementById('sbar').offsetHeight+'px');}
  sbh();window.addEventListener('resize',sbh);
  /* ?q=texto abre la búsqueda */
  var q=(location.search.match(/[?&]q=([^&]+)/)||[])[1];
  if(q){inp.value=decodeURIComponent(q.replace(/\+/g,' '));aplicar();}
  else render();
})();
</script>
"""
s = s.replace('</body>', JS + '</body>', 1)
s = s.replace("b.textContent='🔗 Compartir este producto'", "b.textContent='🔗 Compartir'", 1)
open(IDX, 'w', encoding='utf-8').write(s)
print('ok')
