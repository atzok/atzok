import * as THREE from 'three';

function canvas(w, h) {
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  return [c, c.getContext('2d')];
}

function rand(seed) {
  let s = seed;
  return () => (s = (s * 16807) % 2147483647) / 2147483647;
}

// Tijolo aparente pintado de escuro, como as paredes do MEOW.
export function brickTextures(repeatX = 4, repeatY = 2) {
  const [c, g] = canvas(512, 512);
  const [b, gb] = canvas(512, 512);
  const r = rand(7);
  g.fillStyle = '#1c0b0a'; g.fillRect(0, 0, 512, 512);
  gb.fillStyle = '#000'; gb.fillRect(0, 0, 512, 512);
  const bw = 64, bh = 26;
  for (let y = 0; y < 512; y += bh) {
    const off = (y / bh) % 2 ? bw / 2 : 0;
    for (let x = -bw; x < 512 + bw; x += bw) {
      const v = 0.75 + r() * 0.5;
      const red = Math.floor(92 * v), gr = Math.floor(38 * v), bl = Math.floor(30 * v);
      g.fillStyle = `rgb(${red},${gr},${bl})`;
      g.fillRect(x + off + 2, y + 2, bw - 4, bh - 4);
      // manchas de reboco
      if (r() > 0.7) {
        g.fillStyle = `rgba(200,170,150,${0.08 + r() * 0.12})`;
        g.fillRect(x + off + r() * 30, y + r() * 10, 10 + r() * 30, 4 + r() * 10);
      }
      const gv = Math.floor(150 + r() * 80);
      gb.fillStyle = `rgb(${gv},${gv},${gv})`;
      gb.fillRect(x + off + 2, y + 2, bw - 4, bh - 4);
    }
  }
  const map = new THREE.CanvasTexture(c);
  map.colorSpace = THREE.SRGBColorSpace;
  const bump = new THREE.CanvasTexture(b);
  for (const t of [map, bump]) {
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    t.repeat.set(repeatX, repeatY);
    t.anisotropy = 8;
  }
  return { map, bump };
}

// Piso de madeira escura da pista.
export function plankTexture() {
  const [c, g] = canvas(1024, 1024);
  const r = rand(3);
  const ph = 64;
  for (let y = 0; y < 1024; y += ph) {
    let x = -r() * 300;
    while (x < 1024) {
      const len = 260 + r() * 300;
      const v = 0.7 + r() * 0.45;
      g.fillStyle = `rgb(${Math.floor(46 * v)},${Math.floor(24 * v)},${Math.floor(20 * v)})`;
      g.fillRect(x, y, len, ph);
      for (let i = 0; i < 14; i++) {
        g.strokeStyle = `rgba(0,0,0,${0.08 + r() * 0.1})`;
        g.beginPath();
        const yy = y + r() * ph;
        g.moveTo(x, yy);
        g.bezierCurveTo(x + len * 0.3, yy + r() * 6 - 3, x + len * 0.6, yy + r() * 6 - 3, x + len, yy);
        g.stroke();
      }
      g.fillStyle = 'rgba(0,0,0,.6)';
      g.fillRect(x, y, 2, ph);
      x += len;
    }
    g.fillStyle = 'rgba(0,0,0,.7)';
    g.fillRect(0, y, 1024, 2);
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.anisotropy = 8;
  return t;
}

// Ladrilho de pedra do corredor de entrada.
export function pavingTexture() {
  const [c, g] = canvas(512, 512);
  const r = rand(11);
  g.fillStyle = '#120706'; g.fillRect(0, 0, 512, 512);
  for (let y = 0; y < 512; y += 32) {
    for (let x = 0; x < 512; x += 64) {
      const off = (y / 32) % 2 ? 32 : 0;
      const v = 0.7 + r() * 0.5;
      g.fillStyle = `rgb(${Math.floor(70 * v)},${Math.floor(40 * v)},${Math.floor(34 * v)})`;
      g.fillRect(x + off + 2, y + 2, 60, 28);
    }
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  return t;
}

// Gradiente para emissivo das placas corrugadas (mais forte embaixo, como a fita de LED).
export function ledGradient() {
  const [c, g] = canvas(4, 256);
  const grd = g.createLinearGradient(0, 0, 0, 256);
  grd.addColorStop(0, '#5a5a5a');
  grd.addColorStop(0.5, '#bdbdbd');
  grd.addColorStop(1, '#ffffff');
  g.fillStyle = grd; g.fillRect(0, 0, 4, 256);
  const t = new THREE.CanvasTexture(c);
  return t;
}

// Sprite macio para a fumaça.
export function softSprite() {
  const [c, g] = canvas(128, 128);
  const grd = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  grd.addColorStop(0, 'rgba(255,255,255,1)');
  grd.addColorStop(0.4, 'rgba(255,255,255,.35)');
  grd.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = grd; g.fillRect(0, 0, 128, 128);
  const t = new THREE.CanvasTexture(c);
  return t;
}

// Letreiro neon em texto (para placas pequenas).
export function neonText(text, { color = '#ff2745', font = '700 64px "Unbounded"', w = 1024, h = 160 } = {}) {
  const [c, g] = canvas(w, h);
  g.font = font;
  g.textAlign = 'center';
  g.textBaseline = 'middle';
  g.shadowColor = color;
  g.shadowBlur = 18;
  g.fillStyle = color;
  g.fillText(text, w / 2, h / 2);
  g.shadowBlur = 0;
  g.fillStyle = '#fff3f0';
  g.globalAlpha = 0.85;
  g.fillText(text, w / 2, h / 2);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

// Prateleira de garrafas retroiluminada.
export function bottleShelf() {
  const [c, g] = canvas(512, 256);
  const r = rand(5);
  g.fillStyle = '#1a0a02'; g.fillRect(0, 0, 512, 256);
  for (let row = 0; row < 3; row++) {
    const base = 80 + row * 84;
    g.fillStyle = '#ff9a2e';
    g.globalAlpha = 0.25;
    g.fillRect(0, base - 70, 512, 70);
    g.globalAlpha = 1;
    let x = 6;
    while (x < 500) {
      const bw = 14 + r() * 10, bh = 34 + r() * 30;
      const hue = r();
      g.fillStyle = hue > 0.6 ? '#ffb347' : hue > 0.3 ? '#e07a1f' : '#fff0c8';
      g.globalAlpha = 0.65 + r() * 0.35;
      g.fillRect(x, base - bh, bw, bh);
      g.fillRect(x + bw * 0.35, base - bh - 12, bw * 0.3, 12);
      g.globalAlpha = 1;
      x += bw + 4 + r() * 4;
    }
    g.fillStyle = '#0a0402';
    g.fillRect(0, base, 512, 6);
  }
  // grade metálica
  g.strokeStyle = 'rgba(0,0,0,.55)';
  g.lineWidth = 1;
  for (let x = 0; x < 512; x += 12) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, 256); g.stroke(); }
  for (let y = 0; y < 256; y += 12) { g.beginPath(); g.moveTo(0, y); g.lineTo(512, y); g.stroke(); }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

// Geladeira de latinhas.
export function fridgeTexture() {
  const [c, g] = canvas(128, 256);
  const r = rand(9);
  g.fillStyle = '#f4f1ff'; g.fillRect(0, 0, 128, 256);
  const cols = ['#2b46c9', '#c9c9d6', '#d8423a', '#8a6ad6', '#e8c24a', '#9fd66a'];
  for (let row = 0; row < 7; row++) {
    const col = cols[Math.floor(r() * cols.length)];
    for (let x = 6; x < 120; x += 14) {
      g.fillStyle = col; g.fillRect(x, 12 + row * 34, 10, 24);
      g.fillStyle = 'rgba(255,255,255,.6)'; g.fillRect(x + 2, 14 + row * 34, 2, 20);
    }
    g.fillStyle = '#b8b8c8'; g.fillRect(0, 38 + row * 34, 128, 2);
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}
