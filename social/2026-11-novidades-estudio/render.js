const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1200,height:1400}});
const dir=process.argv[2];
await p.goto('file://'+dir+'/cards.html');await p.waitForLoadState('networkidle');await p.evaluate(()=>document.fonts.ready);
for(let i=1;i<=9;i++){await p.locator('#c'+i).screenshot({path:`${dir}/atzok-0${i}.png`});}
// overflow check
const o=await p.evaluate(()=>[...document.querySelectorAll('.card')].map(c=>{return c.id+':'+(c.scrollHeight>c.clientHeight?'OVERFLOW':'ok')+':'+[...c.children].filter(e=>e.getBoundingClientRect().bottom>c.getBoundingClientRect().bottom-60).map(e=>e.className).join(',')}));
console.log(o.join(' '));await b.close();})();
