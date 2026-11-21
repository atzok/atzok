// uso: node render.js  (gera ../card-01.png … ../card-10.png e checa vazamentos)
const {chromium}=require('playwright');const path=require('path');
(async()=>{
  const dir=__dirname,out=path.join(dir,'..');
  const b=await chromium.launch();const p=await b.newPage({viewport:{width:1200,height:1400},deviceScaleFactor:1});
  await p.goto('file://'+dir+'/cards.html');await p.waitForLoadState('networkidle');await p.evaluate(()=>document.fonts.ready);await p.waitForFunction(()=>window.__built);
  const fonts=await p.evaluate(()=>[...document.fonts].map(f=>f.family+':'+f.status).join(' '));console.log('fonts',fonts);
  // QA: texto fora da área segura (88px) e escorrido sobre texto
  const qa=await p.evaluate(()=>[...document.querySelectorAll('.card')].map(c=>{const cb=c.getBoundingClientRect(),M=80,issues=[];
    c.querySelectorAll('.t,.foot,.kick,.stamp').forEach(e=>{const r=e.getBoundingClientRect();
      if(r.left-cb.left<M-1||cb.right-r.right<M-1||r.top-cb.top<M-1||cb.bottom-r.bottom<M-1)issues.push('fora-da-area:'+(e.className)+':'+e.textContent.trim().slice(0,20));
      if(e.scrollWidth>e.clientWidth+2)issues.push('vaza-x:'+e.textContent.trim().slice(0,20));});
    const texts=[...c.querySelectorAll('.t,.stamp,.foot')].filter(t=>!t.querySelector('[data-drip]')&&!t.hasAttribute('data-drip'));
    c.querySelectorAll('svg.drips path').forEach(d=>{const r=d.getBoundingClientRect();texts.forEach(t=>{
      const rg=document.createRange();rg.selectNodeContents(t);[...rg.getClientRects()].forEach(q=>{
        if(q.width>2&&r.left<q.right&&r.right>q.left&&r.top+14<q.bottom&&r.bottom>q.top)issues.push('drip-sobre-texto:'+t.textContent.trim().slice(0,15));});});});
    return c.id+': '+([...new Set(issues)].join(' | ')||'ok');}));
  console.log(qa.join('\n'));
  for(let i=1;i<=10;i++){await p.locator('#c'+i).screenshot({path:`${out}/card-${String(i).padStart(2,'0')}.png`});}
  await b.close();
})();
