// Uso: node render.js <pasta>   → renderiza cada .slide/.story de <pasta>/*.html em PNG na própria pasta
const {chromium}=require('playwright'); const fs=require('fs'), path=require('path');
(async()=>{
  const dir=path.resolve(process.argv[2]); const b=await chromium.launch();
  for(const f of fs.readdirSync(dir).filter(x=>x.endsWith('.html'))){
    const p=await b.newPage({viewport:{width:1200,height:2000},deviceScaleFactor:1});
    await p.goto('file://'+path.join(dir,f)); await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(800);
    const ids=await p.$$eval('.slide,.story',els=>els.map(e=>e.id));
    for(const id of ids){await p.locator('#'+id).screenshot({path:path.join(dir,id+'.png')});}
    console.log(f,ids.length); await p.close();
  }
  await b.close();
})();
