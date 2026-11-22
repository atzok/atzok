import * as THREE from 'three';
import {
  brickTextures, plankTexture, pavingTexture, ledGradient, softSprite,
  neonText, bottleShelf, fridgeTexture,
} from './textures.js';

export const PALETTE = {
  red: new THREE.Color('#ff1f3d'),
  amber: new THREE.Color('#ff8a1e'),
  cobalt: new THREE.Color('#3d4bff'),
  bone: new THREE.Color('#f2ece2'),
  brass: new THREE.Color('#c8a24a'),
};

const WALL_H = 3.4;

// ---------- helpers ----------
function std(color, opts = {}) {
  return new THREE.MeshStandardMaterial({ color, roughness: 0.8, metalness: 0, ...opts });
}

function box(w, h, d, mat, x, y, z, parent) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);
  m.position.set(x, y, z);
  m.castShadow = true; m.receiveShadow = true;
  parent.add(m);
  return m;
}

// Placa corrugada translúcida com LED atrás (o balcão-assinatura do MEOW).
function corrugated(width, height, color, intensity = 2.0) {
  const waves = Math.round(width * 9);
  const geo = new THREE.PlaneGeometry(width, height, waves * 6, 1);
  const pos = geo.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i);
    pos.setZ(i, Math.sin((x / width) * waves * Math.PI * 2) * 0.025);
  }
  geo.computeVertexNormals();
  const mat = new THREE.MeshStandardMaterial({
    color: color.clone().multiplyScalar(0.6),
    emissive: color,
    emissiveIntensity: intensity,
    emissiveMap: ledGradient(),
    roughness: 0.35,
    metalness: 0,
  });
  return new THREE.Mesh(geo, mat);
}

// Neon em tubo, a partir de pontos (curva suave).
function neonTube(points, color, radius = 0.05, intensity = 2.6) {
  const curve = new THREE.CatmullRomCurve3(points, false, 'catmullrom', 0.5);
  const geo = new THREE.TubeGeometry(curve, points.length * 24, radius, 10, false);
  const mat = new THREE.MeshStandardMaterial({
    color: '#330008', emissive: color, emissiveIntensity: intensity, roughness: 0.4,
  });
  const m = new THREE.Mesh(geo, mat);
  return m;
}

// Neon em segmentos retos (letreiro anguloso do MEOW).
function neonPolyline(strokes, color, scale, radius = 0.035, intensity = 2.4) {
  const g = new THREE.Group();
  const mat = new THREE.MeshStandardMaterial({ color: '#330008', emissive: color, emissiveIntensity: intensity });
  for (const stroke of strokes) {
    for (let i = 0; i < stroke.length - 1; i++) {
      const a = new THREE.Vector3(stroke[i][0] * scale, stroke[i][1] * scale, 0);
      const b = new THREE.Vector3(stroke[i + 1][0] * scale, stroke[i + 1][1] * scale, 0);
      const len = a.distanceTo(b);
      const cyl = new THREE.Mesh(new THREE.CylinderGeometry(radius, radius, len, 8), mat);
      cyl.position.copy(a).add(b).multiplyScalar(0.5);
      cyl.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), b.clone().sub(a).normalize());
      g.add(cyl);
      const j = new THREE.Mesh(new THREE.SphereGeometry(radius, 8, 6), mat);
      j.position.copy(b); g.add(j);
    }
  }
  return g;
}

// Letras pontiagudas, no espírito do letreiro da casa.
const MEOW_STROKES = [
  // M
  [[0, 0], [0.05, 1.05], [0.22, 0.5], [0.3, 0.72], [0.42, 0.38], [0.55, 0.78], [0.62, 0.55], [0.75, 1.1], [0.78, 0]],
  // E
  [[1.72, 1.05], [1.0, 1.0], [1.12, 0.62], [1.02, 0.52], [1.55, 0.55], [1.38, 0.48]],
  [[1.02, 0.52], [1.08, 0.2], [0.98, -0.02], [1.75, 0.02]],
  // O
  [[2.35, 1.08], [2.75, 0.8], [2.62, 0.62], [2.8, 0.3], [2.4, -0.04], [2.12, 0.18], [2.0, 0.55], [2.15, 0.62], [2.05, 0.9], [2.35, 1.08]],
  // W
  [[3.05, 1.06], [3.22, 0.0], [3.42, 0.58], [3.5, 0.45], [3.66, 0.0], [3.9, 1.1], [3.78, 0.85]],
];

export function meowSign(color = PALETTE.red, scale = 0.6) {
  const g = neonPolyline(MEOW_STROKES, color, scale);
  g.position.x = -3.9 * scale / 2;
  const wrap = new THREE.Group();
  wrap.add(g);
  return wrap;
}

function framedPortrait(url, w, h) {
  const g = new THREE.Group();
  const tex = new THREE.TextureLoader().load(url);
  tex.colorSpace = THREE.SRGBColorSpace;
  const frameMat = std(PALETTE.brass, { metalness: 0.85, roughness: 0.35 });
  const t = 0.09;
  box(w + t * 2, t, 0.08, frameMat, 0, h / 2 + t / 2, 0, g);
  box(w + t * 2, t, 0.08, frameMat, 0, -h / 2 - t / 2, 0, g);
  box(t, h, 0.08, frameMat, -w / 2 - t / 2, 0, 0, g);
  box(t, h, 0.08, frameMat, w / 2 + t / 2, 0, 0, g);
  const pic = new THREE.Mesh(
    new THREE.PlaneGeometry(w, h),
    new THREE.MeshStandardMaterial({ map: tex, roughness: 0.6, emissive: '#ffffff', emissiveMap: tex, emissiveIntensity: 0.25 }),
  );
  pic.position.z = 0.01;
  g.add(pic);
  // arandela de quadro
  const lamp = new THREE.Mesh(new THREE.SphereGeometry(0.06, 12, 8), new THREE.MeshStandardMaterial({ emissive: '#ffb066', emissiveIntensity: 8 }));
  lamp.position.set(0, h / 2 + 0.3, 0.25);
  g.add(lamp);
  const spot = new THREE.SpotLight('#ffa860', 6, 3.5, 0.7, 0.6, 1.5);
  spot.position.set(0, h / 2 + 0.3, 0.35);
  spot.target.position.set(0, -0.2, 0);
  g.add(spot, spot.target);
  return g;
}

// ---------- personagens ----------
const skinTones = ['#f1c9a5', '#d9a27a', '#a86f4c', '#7a4a32', '#5a3624'];

export function makePerson({ shirt = '#222', skin = skinTones[1], hair = '#1a0f0a', scale = 1, hairStyle = 'short' } = {}) {
  const g = new THREE.Group();
  const body = new THREE.Mesh(new THREE.CapsuleGeometry(0.24, 0.5, 6, 14), std(shirt, { roughness: 0.75 }));
  body.position.y = 0.6; body.castShadow = true;
  const legs = new THREE.Mesh(new THREE.CapsuleGeometry(0.2, 0.3, 4, 10), std('#14100f'));
  legs.position.y = 0.28; legs.castShadow = true;
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.22, 24, 18), std(skin, { roughness: 0.6 }));
  head.position.y = 1.2; head.scale.setScalar(1.25); head.castShadow = true;
  g.add(legs, body, head);
  const arms = [];
  for (const s of [-1, 1]) {
    const pivot = new THREE.Group(); pivot.position.set(0.27 * s, 0.86, 0);
    const arm = new THREE.Mesh(new THREE.CapsuleGeometry(0.075, 0.36, 4, 8), std(shirt, { roughness: 0.75 }));
    arm.position.y = -0.22; arm.castShadow = true; pivot.add(arm);
    const hand = new THREE.Mesh(new THREE.SphereGeometry(0.075, 10, 8), std(skin, { roughness: 0.6 }));
    hand.position.y = -0.46; pivot.add(hand);
    pivot.rotation.z = 0.12 * s;
    g.add(pivot); arms.push(pivot);
  }
  for (const s of [-1, 1]) {
    const shoe = new THREE.Mesh(new THREE.CapsuleGeometry(0.08, 0.12, 4, 8), std('#f2ece2', { roughness: 0.5 }));
    shoe.rotation.x = Math.PI / 2; shoe.position.set(0.1 * s, 0.07, 0.06); g.add(shoe);
  }
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.035, 8, 6), std(skin, { roughness: 0.6 }));
  nose.position.set(0, 1.17, 0.275); g.add(nose);
  g.userData.arms = arms;
  const hairMat = std(hair, { roughness: 0.9 });
  if (hairStyle === 'short') {
    const h = new THREE.Mesh(new THREE.SphereGeometry(0.285, 24, 12, 0, Math.PI * 2, 0, Math.PI * 0.45), hairMat);
    h.position.y = 1.23; g.add(h);
  } else if (hairStyle === 'long') {
    const h = new THREE.Mesh(new THREE.SphereGeometry(0.295, 24, 12, 0, Math.PI * 2, 0, Math.PI * 0.62), hairMat);
    h.position.y = 1.2; g.add(h);
    const back = new THREE.Mesh(new THREE.CapsuleGeometry(0.22, 0.32, 4, 10), hairMat);
    back.position.set(0, 0.98, -0.12); g.add(back);
  } else if (hairStyle === 'cap') {
    const c = new THREE.Mesh(new THREE.SphereGeometry(0.29, 20, 10, 0, Math.PI * 2, 0, Math.PI * 0.42), std('#0c0c0c'));
    c.position.y = 1.25; g.add(c);
    const brim = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.14, 0.02, 16, 1, false, -Math.PI / 2, Math.PI), std('#0c0c0c'));
    brim.position.set(0, 1.32, 0.2); g.add(brim);
  }
  // olhos
  const eyeMat = std('#0a0505', { roughness: 0.2 });
  for (const s of [-1, 1]) {
    const e = new THREE.Mesh(new THREE.SphereGeometry(0.028, 8, 6), eyeMat);
    e.position.set(0.09 * s, 1.24, 0.26); g.add(e);
  }
  g.scale.setScalar(scale);
  g.userData.body = body;
  g.userData.head = head;
  return g;
}

export function makeCat() {
  const g = new THREE.Group();
  const white = std('#f4efe6', { roughness: 0.55 });
  const black = std('#0d0c10', { roughness: 0.5 });
  const body = new THREE.Mesh(new THREE.CapsuleGeometry(0.22, 0.42, 6, 14), black);
  body.position.y = 0.55; body.castShadow = true;
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.3, 32, 24), white);
  head.scale.set(1.08, 0.95, 1); head.position.y = 1.12; head.castShadow = true;
  g.add(body, head);
  for (const s of [-1, 1]) {
    const ear = new THREE.Mesh(new THREE.ConeGeometry(0.1, 0.24, 4), white);
    ear.position.set(0.17 * s, 1.4, 0); ear.rotation.z = -0.35 * s; ear.castShadow = true;
    const inner = new THREE.Mesh(new THREE.ConeGeometry(0.055, 0.15, 4), std('#f29aa3'));
    inner.position.set(0.165 * s, 1.385, 0.04); inner.rotation.z = -0.35 * s;
    g.add(ear, inner);
    // óculos escuros
    const lens = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.11, 0.05), std('#050506', { roughness: 0.05, metalness: 0.6 }));
    lens.position.set(0.12 * s, 1.15, 0.27); lens.rotation.y = 0.25 * s;
    g.add(lens);
  }
  const bridge = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.025, 0.03), black);
  bridge.position.set(0, 1.17, 0.3); g.add(bridge);
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.03, 8, 6), std('#e98a90'));
  nose.position.set(0, 1.05, 0.3); g.add(nose);
  // coleira de spikes
  const collar = new THREE.Mesh(new THREE.TorusGeometry(0.2, 0.035, 8, 24), std('#151515', { roughness: 0.3 }));
  collar.rotation.x = Math.PI / 2; collar.position.y = 0.86; g.add(collar);
  for (let i = 0; i < 9; i++) {
    const a = (i / 9) * Math.PI * 2;
    const spike = new THREE.Mesh(new THREE.ConeGeometry(0.02, 0.06, 6), std('#d8d8d8', { metalness: 1, roughness: 0.2 }));
    spike.position.set(Math.cos(a) * 0.23, 0.86, Math.sin(a) * 0.23);
    spike.rotation.z = -Math.PI / 2; spike.rotation.y = -a;
    g.add(spike);
  }
  const tail = neonFreeTube([[0, 0.35, -0.2], [0, 0.4, -0.45], [0.05, 0.75, -0.55], [0.12, 0.95, -0.45]], 0.045, white);
  g.add(tail);
  g.userData.body = body;
  g.userData.head = head;
  return g;
}

function neonFreeTube(pts, r, mat) {
  const curve = new THREE.CatmullRomCurve3(pts.map(p => new THREE.Vector3(...p)));
  const m = new THREE.Mesh(new THREE.TubeGeometry(curve, 20, r, 8, false), mat);
  m.castShadow = true;
  return m;
}

// Cone de lanterna visível (feixe na fumaça).
function beamMaterial(color) {
  return new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
    uniforms: { uColor: { value: new THREE.Color(color) }, uAlpha: { value: 0.22 } },
    vertexShader: `varying vec2 vP;
      void main(){ vP = position.xy; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
    fragmentShader: `uniform vec3 uColor; uniform float uAlpha; varying vec2 vP;
      void main(){ float d = length(vP)/4.5; float a = atan(vP.x, vP.y);
      float edge = smoothstep(0.6, 0.45, abs(a)); float fall = (1.0 - d) * (1.0 - d);
      float ring = smoothstep(0.02, 0.0, abs(d - 0.98)) * 0.6;
      gl_FragColor = vec4(uColor, uAlpha * (fall * edge + ring * edge)); }`,
  });
}

export function makeGuard() {
  const g = makePerson({ shirt: '#09090b', skin: skinTones[3], hair: '#050505', scale: 1.22, hairStyle: 'short' });
  // óculos escuros e sobrancelha franzida
  const shades = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.09, 0.06), std('#030303', { roughness: 0.05, metalness: 0.7 }));
  shades.position.set(0, 1.25, 0.25); g.add(shades);
  // fone no ouvido
  const ear = new THREE.Mesh(new THREE.TorusGeometry(0.06, 0.01, 6, 12, Math.PI), std('#dddddd'));
  ear.position.set(0.22, 1.18, 0); ear.rotation.y = Math.PI / 2; g.add(ear);
  // lanterna
  const torch = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.04, 0.25, 10), std('#222', { metalness: 0.8, roughness: 0.3 }));
  torch.rotation.x = Math.PI / 2; torch.position.set(0.28, 0.75, 0.25); g.add(torch);
  const beamLen = 4.5;
  const fan = new THREE.Mesh(new THREE.CircleGeometry(beamLen, 40, Math.PI / 2 - 0.6, 1.2), beamMaterial('#ffe7a8'));
  fan.rotation.x = -Math.PI / 2; fan.position.y = 0.03;
  g.add(fan);
  const spot = new THREE.SpotLight('#fff1c2', 14, 7, 0.55, 0.6, 1.3);
  spot.position.set(0.28, 0.9, 0.3);
  spot.target.position.set(0.28, 0, 3.5);
  g.add(spot, spot.target);
  const cone = fan;
  g.userData.cone = cone;
  return g;
}

// ---------- mundo ----------
export function buildWorld(scene) {
  const colliders = [];
  const animated = [];
  const brick = brickTextures(6, 2);
  const brickMat = std('#ffffff', { map: brick.map, bumpMap: brick.bump, bumpScale: 2.2, roughness: 0.95 });
  const darkMat = std('#0b0607', { roughness: 0.9 });

  // piso
  const planks = plankTexture();
  planks.repeat.set(4, 3);
  const floor = new THREE.Mesh(
    new THREE.PlaneGeometry(30, 22),
    new THREE.MeshStandardMaterial({ map: planks, roughness: 0.42, metalness: 0.05 }),
  );
  floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true;
  scene.add(floor);
  // piso de pedra do corredor de entrada
  const pave = pavingTexture(); pave.repeat.set(2, 6);
  const corridor = new THREE.Mesh(new THREE.PlaneGeometry(3.2, 12), std('#ffffff', { map: pave, roughness: 0.7 }));
  corridor.rotation.x = -Math.PI / 2; corridor.position.set(-12.4, 0.01, 3.5); corridor.receiveShadow = true;
  scene.add(corridor);

  // paredes (corte de casa de bonecas: sem parede da frente)
  function wall(w, x, z, rotY = 0, h = WALL_H) {
    const geo = new THREE.BoxGeometry(w, h, 0.3);
    const m = new THREE.Mesh(geo, brickMat);
    m.position.set(x, h / 2, z); m.rotation.y = rotY;
    m.castShadow = true; m.receiveShadow = true;
    scene.add(m);
    // topo de corte escuro
    const cap = new THREE.Mesh(new THREE.BoxGeometry(w, 0.06, 0.32), darkMat);
    cap.position.set(x, h + 0.03, z); cap.rotation.y = rotY; scene.add(cap);
    colliders.push(new THREE.Box3().setFromObject(m));
    return m;
  }
  wall(30, 0, -11); // fundo
  wall(22, -15, 0, Math.PI / 2); // esquerda
  wall(22, 15, 0, Math.PI / 2); // direita
  wall(5, 12.5, -2.5); // divisória lounge
  wall(8, 9.8, 2, Math.PI / 2, 2.2); // mureta lounge
  wall(9, -10.8, -1.2, Math.PI / 2, WALL_H); // divisória corredor

  // pilares
  for (const [x, z] of [[-4, -4], [6.5, -4], [-4, 5], [6.5, 5]]) {
    box(0.5, WALL_H, 0.5, brickMat, x, WALL_H / 2, z, scene);
    colliders.push(new THREE.Box3().setFromCenterAndSize(new THREE.Vector3(x, 1, z), new THREE.Vector3(0.6, 2, 0.6)));
  }

  // ===== corredor de entrada: paredes corrugadas âmbar =====
  for (const side of [-1, 1]) {
    const panel = corrugated(11, 2.2, PALETTE.amber, 0.7);
    panel.position.set(-12.4 + side * 1.55, 1.6, 3.5);
    panel.rotation.y = side * -Math.PI / 2;
    scene.add(panel);
  }
  const amb = new THREE.PointLight('#ff8a2e', 14, 9, 1.6);
  amb.position.set(-12.4, 2.2, 4); scene.add(amb);
  const amb2 = new THREE.PointLight('#ff8a2e', 12, 9, 1.6);
  amb2.position.set(-12.4, 2.2, -1); scene.add(amb2);
  // bancos de ferro
  for (const z of [1, 4.2]) {
    const bench = new THREE.Group();
    box(0.4, 0.06, 1.3, std('#2a170c'), 0, 0.45, 0, bench);
    box(0.05, 0.45, 0.05, std('#0a0a0a', { metalness: 0.7 }), 0, 0.22, -0.55, bench);
    box(0.05, 0.45, 0.05, std('#0a0a0a', { metalness: 0.7 }), 0, 0.22, 0.55, bench);
    bench.position.set(-13.4, 0, z); scene.add(bench);
  }

  // ===== caixa + chapelaria =====
  const cashier = new THREE.Group();
  box(2.6, 1.1, 0.7, std('#1a0c0b'), 0, 0.55, 0, cashier);
  box(2.6, 0.06, 0.8, std('#2a1410', { roughness: 0.3 }), 0, 1.13, 0, cashier);
  const plate = new THREE.Mesh(new THREE.PlaneGeometry(1.6, 0.25), new THREE.MeshBasicMaterial({ map: neonText('CHAPELARIA', { color: '#dfe8ff', font: '800 92px "Unbounded"' }), transparent: true }));
  plate.position.set(0, 2.1, -0.3); cashier.add(plate);
  cashier.position.set(-12.4, 0, -6.5); scene.add(cashier);
  colliders.push(new THREE.Box3().setFromCenterAndSize(new THREE.Vector3(-12.4, 0.5, -6.5), new THREE.Vector3(2.6, 1, 0.8)));
  const cashLight = new THREE.PointLight('#ffb070', 6, 5, 1.5); cashLight.position.set(-12.4, 2.4, -5.5); scene.add(cashLight);

  // ===== bar azul / energia =====
  const blueBar = new THREE.Group();
  // fundo
  const shelf = new THREE.Mesh(new THREE.PlaneGeometry(3, 1.6), new THREE.MeshStandardMaterial({ map: bottleShelf(), emissive: '#ffffff', emissiveMap: bottleShelf(), emissiveIntensity: 1.4 }));
  shelf.position.set(0, 1.9, -0.95); blueBar.add(shelf);
  const fridgeTex = fridgeTexture();
  for (const x of [-2.4, 2.4]) {
    box(1, 2.1, 0.7, std('#0b0b10', { roughness: 0.4 }), x, 1.05, -0.6, blueBar);
    const door = new THREE.Mesh(new THREE.PlaneGeometry(0.8, 1.7), new THREE.MeshStandardMaterial({ map: fridgeTex, emissive: '#ffffff', emissiveMap: fridgeTex, emissiveIntensity: 1.6 }));
    door.position.set(x, 1.0, -0.24); blueBar.add(door);
  }
  const front = corrugated(6.4, 1.05, PALETTE.amber, 1.86);
  front.position.set(0, 0.55, 0.9); blueBar.add(front);
  box(6.6, 0.08, 0.9, std('#141528', { roughness: 0.15, metalness: 0.2 }), 0, 1.12, 0.5, blueBar);
  box(6.4, 1.05, 0.2, darkMat, 0, 0.55, 0.75, blueBar);
  const sign = new THREE.Mesh(new THREE.PlaneGeometry(4.4, 0.55), new THREE.MeshBasicMaterial({
    map: neonText('ENERGIA PARA A PRÓXIMA VIDA', { color: '#ff3a52', font: '700 54px "Unbounded"', w: 1600, h: 200 }), transparent: true, toneMapped: false,
  }));
  sign.position.set(0, 3.05, -0.9); blueBar.add(sign);
  blueBar.position.set(-6.5, 0, -9.8); scene.add(blueBar);
  colliders.push(new THREE.Box3().setFromCenterAndSize(new THREE.Vector3(-6.5, 0.5, -9.2), new THREE.Vector3(6.8, 1, 2.2)));
  const blueWash = new THREE.PointLight('#3d4bff', 30, 9, 1.4); blueWash.position.set(-6.5, 3, -9); scene.add(blueWash);
  const amberBar = new THREE.PointLight('#ff8a1e', 10, 5, 1.5); amberBar.position.set(-6.5, 0.6, -8); scene.add(amberBar);
  // bartender
  const bt1 = makePerson({ shirt: '#1d1d24', skin: skinTones[2], hairStyle: 'cap' });
  bt1.position.set(-5.4, 0, -10.2); scene.add(bt1);
  animated.push({ obj: bt1, type: 'idle', phase: 1.3 });

  // ===== bar vermelho da pista =====
  const redBar = new THREE.Group();
  const rf = corrugated(5.2, 1.1, PALETTE.red, 2.11);
  rf.position.set(0, 0.57, 0.42); redBar.add(rf);
  box(5.2, 1.1, 0.5, darkMat, 0, 0.55, 0.12, redBar);
  box(5.4, 0.08, 1.0, std('#0b0a0c', { roughness: 0.15 }), 0, 1.14, 0.0, redBar);
  // copos e garrafas
  for (let i = 0; i < 9; i++) {
    const glass = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.035, 0.12, 10), new THREE.MeshPhysicalMaterial({ color: '#ffd0d0', transmission: 0.6, roughness: 0.05, thickness: 0.1, transparent: true, opacity: 0.6 }));
    glass.position.set(-2.2 + i * 0.5 + Math.random() * 0.1, 1.24, -0.1 + Math.random() * 0.2);
    redBar.add(glass);
  }
  redBar.rotation.y = Math.PI / 2;
  redBar.position.set(-7.6, 0, 1.6); scene.add(redBar);
  colliders.push(new THREE.Box3().setFromCenterAndSize(new THREE.Vector3(-7.6, 0.5, 1.6), new THREE.Vector3(1.2, 1, 5.4)));
  const redGlow = new THREE.PointLight('#ff1f3d', 16, 6, 1.4); redGlow.position.set(-6.6, 0.5, 1.6); scene.add(redGlow);
  const bt2 = makePerson({ shirt: '#0c0c0e', skin: skinTones[0], hair: '#8a2b1a', hairStyle: 'long' });
  bt2.position.set(-8.4, 0, 0.6); bt2.rotation.y = Math.PI / 2; scene.add(bt2);
  animated.push({ obj: bt2, type: 'idle', phase: 2.1 });
  // letreiro MEOW sobre o bar vermelho
  const meow = meowSign(PALETTE.red, 0.62);
  meow.position.set(-10.5, 2.3, 1.6); meow.rotation.y = Math.PI / 2;
  scene.add(meow);
  const meowLight = new THREE.PointLight('#ff1f3d', 10, 5, 1.5); meowLight.position.set(-10, 2.4, 1.6); scene.add(meowLight);

  // ===== cabine do DJ =====
  const dj = new THREE.Group();
  box(3.6, 1.1, 1.2, std('#08080a', { roughness: 0.5 }), 0, 0.55, 0, dj);
  const djFront = corrugated(3.6, 0.25, PALETTE.red, 2.79);
  djFront.position.set(0, 0.95, 0.61); dj.add(djFront);
  for (const x of [-1.1, 1.1]) {
    const plat = new THREE.Mesh(new THREE.CylinderGeometry(0.32, 0.32, 0.04, 32), std('#1a1a1e', { metalness: 0.6, roughness: 0.3 }));
    plat.position.set(x, 1.13, 0); dj.add(plat);
    const rec = new THREE.Mesh(new THREE.CylinderGeometry(0.28, 0.28, 0.01, 32), std('#050505', { roughness: 0.2 }));
    rec.position.set(x, 1.16, 0); dj.add(rec);
    const lab = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 0.012, 16), new THREE.MeshStandardMaterial({ emissive: '#ff1f3d', emissiveIntensity: 3 }));
    lab.position.set(x, 1.17, 0); dj.add(lab);
    animated.push({ obj: rec, type: 'spin' }, { obj: lab, type: 'spin' });
  }
  const mixer = box(0.8, 0.06, 0.6, std('#202024', { metalness: 0.5 }), 0, 1.14, 0, dj);
  for (let i = 0; i < 6; i++) {
    const led = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.02, 0.15), new THREE.MeshStandardMaterial({ emissive: i < 4 ? '#3dff9a' : '#ff3d3d', emissiveIntensity: 4 }));
    led.position.set(-0.25 + i * 0.1, 1.18, 0); dj.add(led);
  }
  dj.position.set(1.2, 0, -8.6); scene.add(dj);
  colliders.push(new THREE.Box3().setFromCenterAndSize(new THREE.Vector3(1.2, 0.5, -8.6), new THREE.Vector3(3.8, 1, 1.4)));
  const djPerson = makePerson({ shirt: '#e8e4dc', skin: skinTones[3], hairStyle: 'cap' });
  djPerson.position.set(1.2, 0, -9.5); scene.add(djPerson);
  // fone
  const phones = new THREE.Mesh(new THREE.TorusGeometry(0.24, 0.03, 8, 20, Math.PI), std('#0a0a0a'));
  phones.position.y = 1.22; djPerson.add(phones);
  animated.push({ obj: djPerson, type: 'dj' });
  // caixas de som
  for (const x of [-2.2, 4.6]) {
    box(0.9, 1.6, 0.8, std('#0d0d0f', { roughness: 0.6 }), x, 2.2, -10.4, scene);
    const cone = new THREE.Mesh(new THREE.CircleGeometry(0.3, 24), std('#1d1d22', { roughness: 0.4 }));
    cone.position.set(x, 2.3, -9.99); scene.add(cone);
  }

  // ===== tubos neon vermelhos (instalação do teto da pista) =====
  const tubeRoutes = [
    [[-9, 3.2, -3], [-6, 2.4, -6], [-3, 3.0, -2], [0, 2.2, -5.5], [2.5, 2.9, -1.5], [5, 2.3, -6], [8, 3.1, -3], [11, 2.6, -7]],
    [[-5, 2.7, 2.5], [-2, 2.0, -1], [1, 2.8, 2], [3, 1.95, -2.5], [6, 2.7, 1.5], [7.5, 2.1, -1]],
    [[-3, 3.3, -9], [-1, 2.3, -7], [1.5, 2.7, -4], [0.5, 2.1, -1], [-2.5, 2.6, 0.5], [-1, 2.2, 3.5], [2, 2.9, 4.5]],
    [[3, 3.3, -9.5], [4.5, 2.5, -7.5], [3.2, 2.0, -4.5], [6, 2.6, -3], [4, 2.2, 0], [5.5, 2.5, 3.5]],
  ];
  for (const r of tubeRoutes) {
    const t = neonTube(r.map(p => new THREE.Vector3(p[0], p[1] + 0.9, p[2])), PALETTE.red, 0.07, 2.4);
    scene.add(t);
  }
  for (const [x, z] of [[-3, -4], [3, -4], [0, 1], [5, 0], [-3, 2]]) {
    const l = new THREE.PointLight('#ff1f3d', 12, 7, 1.5);
    l.position.set(x, 2.2, z); scene.add(l);
  }

  // luz principal da pista (com sombra)
  const key = new THREE.SpotLight('#ff4a5e', 120, 22, 0.75, 0.8, 1.2);
  key.position.set(1, 11, 3); key.target.position.set(1, 0, -2);
  key.castShadow = true; key.shadow.mapSize.set(2048, 2048); key.shadow.bias = -0.0005; key.shadow.radius = 4;
  scene.add(key, key.target);

  // ===== lounge: sofá, quadros, painel de luz vermelho =====
  const sofa = new THREE.Group();
  const leather = std('#0e0a0a', { roughness: 0.35, metalness: 0.1 });
  box(3.4, 0.45, 1.0, leather, 0, 0.32, 0, sofa);
  box(3.4, 0.75, 0.25, leather, 0, 0.75, -0.4, sofa);
  for (const s of [-1, 1]) {
    const arm = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.22, 1.0, 20), leather);
    arm.rotation.x = Math.PI / 2; arm.position.set(1.7 * s, 0.65, 0); arm.castShadow = true; sofa.add(arm);
  }
  for (let i = 0; i < 12; i++) {
    const btn = new THREE.Mesh(new THREE.SphereGeometry(0.02, 6, 4), std('#c8a24a', { metalness: 1, roughness: 0.3 }));
    btn.position.set(-1.5 + i * 0.27, 0.95, -0.27); sofa.add(btn);
  }
  sofa.position.set(12.5, 0, -9.9); scene.add(sofa);
  colliders.push(new THREE.Box3().setFromCenterAndSize(new THREE.Vector3(12.5, 0.5, -9.8), new THREE.Vector3(3.8, 1, 1.2)));

  const frames = [
    ['/art/cat-chains.jpg', 1.2, 1.8, [9.0, 1.9, -10.82], 0],
    ['/art/cat-shades.jpg', 1.4, 1.6, [14.82, 1.9, -7.5], -Math.PI / 2],
    ['/art/cat-smile.jpg', 1.0, 1.9, [14.82, 1.9, -4.5], -Math.PI / 2],
    ['/art/cat-shades.jpg', 1.2, 1.4, [-3.2, 1.9, -10.82], 0],
    ['/art/cat-chains.jpg', 1.0, 1.5, [14.82, 1.9, 4.5], -Math.PI / 2],
    ['/art/cat-smile.jpg', 0.9, 1.6, [14.82, 1.9, 7.5], -Math.PI / 2],
  ];
  for (const [url, w, h, p, ry] of frames) {
    const f = framedPortrait(url, w, h);
    f.position.set(...p); f.rotation.y = ry; scene.add(f);
  }
  // painel de luz vermelha flutuante (o "céu" vermelho do lounge)
  const panel = new THREE.Mesh(new THREE.BoxGeometry(5, 0.08, 4), new THREE.MeshStandardMaterial({ color: '#300', emissive: PALETTE.red, emissiveIntensity: 2.4 }));
  panel.position.set(12.2, 3.6, -6.5); scene.add(panel);
  const panelFrame = new THREE.Mesh(new THREE.BoxGeometry(5.4, 0.12, 4.4), darkMat);
  panelFrame.position.set(12.2, 3.68, -6.5); scene.add(panelFrame);
  const panelLight = new THREE.PointLight('#ff1f3d', 26, 8, 1.4);
  panelLight.position.set(12.2, 3.0, -6.5); scene.add(panelLight);
  // mesas altas
  for (const [x, z] of [[11, -3], [13.2, -2]]) {
    const t = new THREE.Group();
    box(0.6, 0.04, 0.6, std('#3a2a1a', { roughness: 0.5 }), 0, 1.05, 0, t);
    const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 1.05, 8), std('#c8c8c8', { metalness: 1, roughness: 0.3 }));
    leg.position.y = 0.52; t.add(leg);
    t.position.set(x, 0, z); scene.add(t);
  }

  // corredor de quadros (lado direito, embaixo)
  const hallLight = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.06, 7), new THREE.MeshStandardMaterial({ emissive: PALETTE.red, emissiveIntensity: 3 }));
  hallLight.position.set(12.5, 3.5, 6); scene.add(hallLight);
  const hl = new THREE.PointLight('#ff1f3d', 16, 8, 1.4); hl.position.set(12.5, 2.8, 6); scene.add(hl);
  // arandela vermelha de parede
  const sconce = new THREE.Mesh(new THREE.SphereGeometry(0.14, 16, 12), new THREE.MeshStandardMaterial({ emissive: '#ff5a3a', emissiveIntensity: 6 }));
  sconce.position.set(10.1, 2.3, 6); scene.add(sconce);

  // ===== sinuca e mesas altas (lado de baixo da casa) =====
  const pool = new THREE.Group();
  box(2.6, 0.12, 1.5, std('#1e5a3a', { roughness: 0.95 }), 0, 0.86, 0, pool);
  const rail = std('#2a140c', { roughness: 0.4 });
  box(2.8, 0.16, 0.12, rail, 0, 0.9, 0.81, pool); box(2.8, 0.16, 0.12, rail, 0, 0.9, -0.81, pool);
  box(0.12, 0.16, 1.5, rail, 1.4, 0.9, 0, pool); box(0.12, 0.16, 1.5, rail, -1.4, 0.9, 0, pool);
  box(2.2, 0.75, 1.0, std('#160a06'), 0, 0.42, 0, pool);
  const ballCols = ['#f2ece2', '#e8c24a', '#2b46c9', '#d8423a', '#6b2a7a', '#ff8a1e', '#1e7a3a', '#0a0a0a'];
  ballCols.forEach((c, i) => {
    const b = new THREE.Mesh(new THREE.SphereGeometry(0.045, 14, 10), std(c, { roughness: 0.15 }));
    b.position.set(-0.6 + (i % 4) * 0.12 + (i > 3 ? 0.06 : 0), 0.97, -0.1 + (i > 3 ? 0.1 : 0)); b.castShadow = true; pool.add(b);
  });
  const cue = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.02, 1.4, 8), std('#c8a26a'));
  cue.rotation.z = Math.PI / 2; cue.rotation.y = 0.3; cue.position.set(0.5, 1.0, 0.3); pool.add(cue);
  pool.position.set(2.4, 0, 7.4); scene.add(pool);
  colliders.push(new THREE.Box3().setFromCenterAndSize(new THREE.Vector3(2.4, 0.5, 7.4), new THREE.Vector3(2.9, 1, 1.7)));
  const poolLamp = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.1, 0.3), new THREE.MeshStandardMaterial({ color: '#111', emissive: '#ffd0a0', emissiveIntensity: 1.2 }));
  poolLamp.position.set(2.4, 2.3, 7.4); scene.add(poolLamp);
  const poolLight = new THREE.SpotLight('#ffd8b0', 22, 5, 0.8, 0.5, 1.3);
  poolLight.position.set(2.4, 2.25, 7.4); poolLight.target.position.set(2.4, 0, 7.4); poolLight.castShadow = true;
  scene.add(poolLight, poolLight.target);
  for (const [x, z] of [[-2.5, 8], [7.5, 7.8], [-6, 7.5]]) {
    const t = new THREE.Group();
    const top = new THREE.Mesh(new THREE.CylinderGeometry(0.38, 0.38, 0.04, 24), std('#2a1a12', { roughness: 0.4 }));
    top.position.y = 1.05; top.castShadow = true; t.add(top);
    const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 1.05, 8), std('#cfcfcf', { metalness: 1, roughness: 0.3 }));
    leg.position.y = 0.52; t.add(leg);
    const can = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, 0.12, 12), std('#3a52d8', { metalness: 0.8, roughness: 0.3 }));
    can.position.set(0.1, 1.13, 0.05); t.add(can);
    t.position.set(x, 0, z); scene.add(t);
  }
  const southWash = new THREE.PointLight('#ff3a4a', 10, 9, 1.3); southWash.position.set(-3, 2.5, 7.5); scene.add(southWash);
  const southWash2 = new THREE.PointLight('#ff6a3a', 8, 8, 1.3); southWash2.position.set(8, 2.5, 7); scene.add(southWash2);
  // pessoas conversando nas mesas
  const chat = [[-2.9, 8.4, 2.4, '#d8d4cc', 'long'], [-2.1, 7.7, -0.8, '#2a4aa8', 'short'], [7.9, 8.2, 3.4, '#b83a2a', 'cap'], [1.2, 8.6, 2.6, '#e0b84a', 'short']];
  for (const [x, z, ry, shirt, hs] of chat) {
    const p = makePerson({ shirt, skin: skinTones[Math.floor(Math.abs(x * 7)) % 5], hairStyle: hs });
    p.position.set(x, 0, z); p.rotation.y = ry; scene.add(p);
    animated.push({ obj: p, type: 'idle', phase: x });
  }

  // ===== multidão =====
  const shirts = ['#6b2a7a', '#1a6a5a', '#d8d4cc', '#2a2a2e', '#b83a2a', '#2a4aa8', '#0e0e10', '#e0b84a', '#3a1a2a', '#7a7f86'];
  const hairs = ['#1a0f0a', '#3a1d10', '#0a0a0a', '#7a4a22', '#c9a35a'];
  const styles = ['short', 'long', 'short', 'cap', 'long'];
  const crowd = [];
  let seed = 4;
  const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  for (let i = 0; i < 26; i++) {
    const p = makePerson({
      shirt: shirts[i % shirts.length], skin: skinTones[Math.floor(rnd() * skinTones.length)],
      hair: hairs[Math.floor(rnd() * hairs.length)], hairStyle: styles[Math.floor(rnd() * styles.length)],
      scale: 0.92 + rnd() * 0.15,
    });
    const a = rnd() * Math.PI * 2, r = 1 + rnd() * 3.6;
    p.position.set(1.2 + Math.cos(a) * r * 1.3, 0, -3.2 + Math.sin(a) * r * 0.9);
    p.rotation.y = Math.atan2(1.2 - p.position.x, -8 - p.position.z) + (rnd() - 0.5);
    scene.add(p);
    crowd.push(p);
    animated.push({ obj: p, type: 'dance', phase: rnd() * 10, speed: 0.8 + rnd() * 0.5 });
  }
  // gerente
  const manager = makePerson({ shirt: '#4a1a5a', skin: skinTones[0], hair: '#c8a040', hairStyle: 'long' });
  const clip = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.3, 0.02), std('#e8dcc0'));
  clip.position.set(0.25, 0.75, 0.2); clip.rotation.x = -0.5; manager.add(clip);
  manager.position.set(9, 0, 3.5); manager.rotation.y = -2.4; scene.add(manager);
  animated.push({ obj: manager, type: 'idle', phase: 0.4 });

  // ===== fumaça (haze) =====
  const hazeCount = 260;
  const hazeGeo = new THREE.BufferGeometry();
  const hp = new Float32Array(hazeCount * 3);
  for (let i = 0; i < hazeCount; i++) {
    hp[i * 3] = (rnd() - 0.5) * 28; hp[i * 3 + 1] = 0.3 + rnd() * 3; hp[i * 3 + 2] = (rnd() - 0.5) * 20;
  }
  hazeGeo.setAttribute('position', new THREE.BufferAttribute(hp, 3));
  const haze = new THREE.Points(hazeGeo, new THREE.PointsMaterial({
    size: 6, map: softSprite(), color: '#ff4a5a', transparent: true, opacity: 0.022,
    depthWrite: false, blending: THREE.AdditiveBlending, sizeAttenuation: true,
  }));
  scene.add(haze);
  animated.push({ obj: haze, type: 'haze' });

  // luz ambiente baixa
  scene.add(new THREE.HemisphereLight('#7a3040', '#1a0a14', 1.3));
  // luz de recorte que desenha os volumes vistos de cima
  const rim = new THREE.DirectionalLight('#ffb0a0', 0.6); rim.position.set(-6, 14, 10); scene.add(rim);
  // lavagens de parede para o tijolo aparecer
  for (const [x, z, c] of [[-8, -10.4, '#ff6a3a'], [6, -10.4, '#ff3a4a'], [14.4, 2, '#ff4a3a'], [-14.4, -6, '#ff8a3a'], [10, -10.4, '#ff5a3a']]) {
    const l = new THREE.PointLight(c, 9, 6, 1.4); l.position.set(x, 0.4, z); scene.add(l);
  }

  // itens coletáveis
  const items = [];
  function item(kind, x, z, color) {
    const g = new THREE.Group();
    const geo = kind === 'pulseira' ? new THREE.TorusGeometry(0.16, 0.04, 10, 28) : new THREE.CylinderGeometry(0.08, 0.08, 0.28, 16);
    const m = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: '#111', emissive: color, emissiveIntensity: 5 }));
    g.add(m);
    const l = new THREE.PointLight(color, 3, 2.5, 1.5); g.add(l);
    g.position.set(x, 0.6, z);
    scene.add(g);
    items.push({ kind, obj: g });
    animated.push({ obj: g, type: 'float', phase: x });
  }
  item('pulseira', -1.8, 3.6, '#3dffb0');
  item('lata', 8.4, -6.5, '#ffd23d');

  return { colliders, animated, items, crowd };
}

export function updateAnimated(list, t, dt) {
  for (const a of list) {
    const o = a.obj;
    if (a.type === 'dance') {
      const s = t * 2.1 * a.speed + a.phase;
      o.position.y = Math.abs(Math.sin(s)) * 0.12;
      o.userData.body.rotation.z = Math.sin(s) * 0.12;
      o.userData.head.position.x = Math.sin(s) * 0.03;
      o.rotation.y += Math.sin(s * 0.25) * 0.004;
      const arms = o.userData.arms;
      if (arms) {
        const up = a.phase % 3 < 1 ? 2.6 : 0.9; // uns levantam os braços, outros só balançam
        arms[0].rotation.z = -0.2 - Math.abs(Math.sin(s)) * up * 0.5;
        arms[1].rotation.z = 0.2 + Math.abs(Math.cos(s)) * up * 0.5;
        arms[0].rotation.x = arms[1].rotation.x = -Math.abs(Math.sin(s * 0.5)) * up * 0.4;
      }
    } else if (a.type === 'dj') {
      o.userData.head.position.y = 1.2 + Math.abs(Math.sin(t * 4.2)) * 0.05;
      o.userData.body.rotation.z = Math.sin(t * 2.1) * 0.06;
    } else if (a.type === 'idle') {
      o.userData.body.scale.y = 1 + Math.sin(t * 1.4 + a.phase) * 0.015;
    } else if (a.type === 'spin') {
      o.rotation.y += dt * 3.5;
    } else if (a.type === 'float') {
      o.position.y = 0.6 + Math.sin(t * 2 + a.phase) * 0.1;
      o.rotation.y += dt * 1.5;
    } else if (a.type === 'haze') {
      o.rotation.y = Math.sin(t * 0.05) * 0.1;
    }
  }
}
