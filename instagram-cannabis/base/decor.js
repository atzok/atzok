const NS="http://www.w3.org/2000/svg";
// starburst
document.querySelectorAll(".burst").forEach(s=>{
  const n=+s.dataset.points, r2=+s.dataset.inner; s.setAttribute("viewBox","-100 -100 200 200");
  let p=[]; for(let i=0;i<n*2;i++){const a=Math.PI*i/n, r=i%2?100*r2:100; p.push((Math.cos(a)*r).toFixed(2)+","+(Math.sin(a)*r).toFixed(2));}
  const pg=document.createElementNS(NS,"polygon"); pg.setAttribute("points",p.join(" ")); s.appendChild(pg);
});
// torn paper edges
let seed=7; const rnd=()=>{seed=(seed*16807)%2147483647;return seed/2147483647};
document.querySelectorAll(".torn").forEach(el=>{
  const pts=[], step=2.2, j=1.1;
  for(let x=0;x<=100;x+=step)pts.push(`${x}% ${rnd()*j*1.6}%`);
  for(let y=0;y<=100;y+=step*1.6)pts.push(`${100-rnd()*j}% ${y}%`);
  for(let x=100;x>=0;x-=step)pts.push(`${x}% ${100-rnd()*j*1.6}%`);
  for(let y=100;y>=0;y-=step*1.6)pts.push(`${rnd()*j}% ${y}%`);
  el.style.clipPath=`polygon(${pts.join(",")})`;
});
// leaf path builder
function leaf(g,fill,leaflets=7){
  const L=[[-88,.42],[-58,.72],[-28,.92],[0,1],[28,.92],[58,.72],[88,.42]].slice((7-leaflets)/2,7-(7-leaflets)/2);
  L.forEach(([ang,s])=>{const p=document.createElementNS(NS,"path");
    p.setAttribute("d","M0,0 C 14,-28 13,-72 0,-110 C -13,-72 -14,-28 0,0 Z");
    p.setAttribute("transform",`rotate(${ang}) scale(${s})`); p.setAttribute("fill",fill); g.appendChild(p);});
  const st=document.createElementNS(NS,"path"); st.setAttribute("d","M-2,0 L2,0 L1,40 L-1,40 Z"); st.setAttribute("fill",fill); g.appendChild(st);
}
// halftone leaf
document.querySelectorAll(".leaf").forEach(s=>{
  s.setAttribute("viewBox","-120 -120 240 180");
  s.innerHTML=`<defs><pattern id="ht" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(30)"><circle cx="2.5" cy="2.5" r="1.9" fill="${s.dataset.fill}"/></pattern></defs>`;
  const g=document.createElementNS(NS,"g"); leaf(g,"url(#ht)"); s.appendChild(g);
  const g2=document.createElementNS(NS,"g"); g2.setAttribute("transform","translate(4,4)"); g2.setAttribute("opacity",".0"); s.appendChild(g2);
});
// leaf rows (pattern from reference)
document.querySelectorAll(".leafrow").forEach(el=>{
  const c=el.dataset.color, svg=document.createElementNS(NS,"svg");
  svg.setAttribute("viewBox","0 0 1080 120"); svg.setAttribute("width","1080"); svg.setAttribute("height","120");
  for(let i=0;i<16;i++){const g=document.createElementNS(NS,"g");
    const x=20+i*70, y=i%2?95:55; g.setAttribute("transform",`translate(${x},${y}) scale(.3)`); leaf(g,c,5); svg.appendChild(g);}
  el.appendChild(svg);
});
// checker stripes
document.querySelectorAll(".checker").forEach(el=>{
  const a=el.dataset.a,b=el.dataset.b;
  el.style.background=`repeating-linear-gradient(90deg,${a} 0 90px,${b} 90px 180px)`;
  el.style.maskImage="none";
  el.innerHTML=`<div style="position:absolute;inset:50% 0 0 0;background:repeating-linear-gradient(90deg,${b} 0 90px,${a} 90px 180px)"></div>`;
});
