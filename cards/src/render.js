// uso: node render.js  (gera ../card-01.png … ../card-10.png e checa vazamentos)
const {chromium}=require('playwright');const path=require('path');
(async()=>{
  const dir=__dirname,out=path.join(dir,'..');
  const b=await chromium.launch();const p=await b.newPage({viewport:{width:1200,height:1400},deviceScaleFactor:1});
  await p.goto('file://'+dir+'/cards.html');await p.waitForFunction(()=>window.__built);
  const qa=await p.evaluate(()=>[...document.querySelectorAll('.card')].map(c=>{const issues=[];const m=c.querySelector('.main');
    if(m.scrollHeight>m.clientHeight+1)issues.push('conteúdo-estoura-altura:'+(m.scrollHeight-m.clientHeight)+'px');
    const mb=m.getBoundingClientRect();
    c.querySelectorAll('.main *').forEach(e=>{const r=e.getBoundingClientRect();if(r.width&&(e.scrollWidth>e.clientWidth+2||r.right>mb.right+2||r.left<mb.left-14))issues.push('vaza-x:'+e.textContent.trim().slice(0,18));});
    // espaço mínimo entre blocos do .main
    const kids=[...m.children];for(let i=1;i<kids.length;i++){const g=kids[i].getBoundingClientRect().top-kids[i-1].getBoundingClientRect().bottom;if(g<40)issues.push('blocos-colados:'+Math.round(g)+'px');}
    return c.id+': '+([...new Set(issues)].join(' | ')||'ok');}));
  console.log(qa.join('\n'));
  for(let i=1;i<=10;i++){await p.locator('#c'+i).screenshot({path:`${out}/card-${String(i).padStart(2,'0')}.png`});}
  await b.close();
})();
