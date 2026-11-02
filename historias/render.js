const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
(async()=>{const dir=process.argv[2],out=process.argv[3];fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
for(const f of fs.readdirSync(dir).filter(f=>f.endsWith('.html')).sort()){
 await p.goto('file://'+path.resolve(dir,f),{waitUntil:'networkidle',timeout:60000}).catch(()=>{});
 await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(500);
 const bad=await p.evaluate(()=>[...document.images].filter(i=>!i.naturalWidth).length);
 console.log(f,'imgs fallidas:',bad);
 await p.screenshot({path:path.join(out,f.replace('.html','.jpg')),type:'jpeg',quality:90});}
await b.close();})();
