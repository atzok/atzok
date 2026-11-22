import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import '@fontsource/unbounded/500.css';
import '@fontsource/unbounded/800.css';
import '@fontsource/bricolage-grotesque/400.css';
import '@fontsource/bricolage-grotesque/600.css';
import './style.css';
import { buildWorld, updateAnimated, makeCat, makeGuard } from './world.js';

const app = document.getElementById('app');
const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.toneMapping = THREE.NeutralToneMapping;
renderer.toneMappingExposure = 1.1;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
app.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color('#050203');
scene.fog = new THREE.FogExp2('#14050b', 0.011);

const camera = new THREE.PerspectiveCamera(30, window.innerWidth / window.innerHeight, 0.1, 200);

await document.fonts.load('700 54px "Unbounded"');
const world = buildWorld(scene);

// jogador
const player = makeCat();
player.position.set(-1.2, 0, 5.6);
player.rotation.y = Math.PI;
scene.add(player);
const playerLight = new THREE.PointLight('#ffe2c8', 2.5, 3, 1.5);
playerLight.position.set(0, 2, 0.6);
player.add(playerLight);

// seguranças com rota de patrulha
const guards = [
  { route: [[-1.5, 4.2], [5.5, 4.2], [5.5, 0.5], [-1.5, 0.5]] },
  { route: [[9.5, -8], [9.5, -1], [13.5, -1], [13.5, -6]] },
  { route: [[-9.8, -5.5], [-3.5, -5.5]] },
  { route: [[-12.4, -0.5], [-12.4, 7.5]] },
].map((g, i) => {
  const obj = makeGuard();
  obj.position.set(g.route[0][0], 0, g.route[0][1]);
  scene.add(obj);
  return { ...g, obj, idx: 1, speed: 1.6 + i * 0.25, look: 0 };
});

// ---------- pós-processamento ----------
const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(window.innerWidth, window.innerHeight), 0.75, 0.5, 0.5);
composer.addPass(bloom);
const grade = new ShaderPass({
  uniforms: { tDiffuse: { value: null }, uTime: { value: 0 }, uAspect: { value: 1 } },
  vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
  fragmentShader: `uniform sampler2D tDiffuse; uniform float uTime; uniform float uAspect; varying vec2 vUv;
    float hash(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233))) * 43758.5453); }
    void main(){
      vec2 c = vUv - 0.5;
      float d = length(c * vec2(uAspect, 1.0));
      vec2 off = c * 0.0035 * d;
      vec3 col;
      col.r = texture2D(tDiffuse, vUv + off).r;
      col.g = texture2D(tDiffuse, vUv).g;
      col.b = texture2D(tDiffuse, vUv - off).b;
      col *= smoothstep(1.05, 0.25, d);
      col += (hash(vUv * 900.0 + uTime) - 0.5) * 0.02;
      gl_FragColor = vec4(col, 1.0);
    }`,
});
composer.addPass(grade);
composer.addPass(new OutputPass());

// ---------- câmera ----------
const camTarget = new THREE.Vector3();
const camOffset = new THREE.Vector3(0, 10.5, 12.5);
const VIEWS = {
  title: { pos: [-5.0, 2.6, 6.8], look: [-9.6, 1.6, 1.4], follow: false },
  play: { follow: true },
  talk: { pos: [-11.15, 1.55, 4.9], look: [-12.35, 1.25, -0.3], follow: false },
  overview: { pos: [2, 26, 24], look: [0, 0, -1.5], follow: false },
};
let mode = location.hash.replace('#', '') || 'title';

// ---------- input ----------
const keys = new Set();
addEventListener('keydown', e => keys.add(e.key.toLowerCase()));
addEventListener('keyup', e => keys.delete(e.key.toLowerCase()));
const stick = { x: 0, y: 0, active: false };
const stickEl = document.getElementById('stick');
const knob = stickEl.querySelector('span');
stickEl.addEventListener('pointerdown', e => { stick.active = true; stickEl.setPointerCapture(e.pointerId); moveStick(e); });
stickEl.addEventListener('pointermove', e => stick.active && moveStick(e));
stickEl.addEventListener('pointerup', () => { stick.active = false; stick.x = stick.y = 0; knob.style.transform = ''; });
function moveStick(e) {
  const r = stickEl.getBoundingClientRect();
  let x = (e.clientX - r.left - r.width / 2) / (r.width / 2);
  let y = (e.clientY - r.top - r.height / 2) / (r.height / 2);
  const l = Math.hypot(x, y); if (l > 1) { x /= l; y /= l; }
  stick.x = x; stick.y = y;
  knob.style.transform = `translate(${x * 34}px, ${y * 34}px)`;
}

// ---------- estado do jogo ----------
const state = { suspicion: 0.38, clock: 2 * 60 + 47, carrying: null };
const hud = {
  root: document.getElementById('hud'),
  clock: document.getElementById('clock'),
  eye: document.getElementById('eye-fill'),
  eyeWrap: document.getElementById('eye'),
};

function setMode(m) {
  mode = m;
  document.body.dataset.mode = m;
  if (m === 'talk') {
    player.position.set(-11.45, 0, 1.1); player.rotation.y = -2.55;
    const g = guards[3].obj; g.position.set(-12.75, 0, -0.5); g.rotation.y = 0.55;
    g.userData.cone.visible = false;
    guards[3].frozen = true;
  }
  if (m === 'play') { player.position.set(-1.2, 0, 5.6); player.rotation.y = 2.6; }
}
addEventListener('hashchange', () => setMode(location.hash.replace('#', '') || 'title'));
document.getElementById('enter').addEventListener('click', () => { location.hash = 'play'; });
document.querySelectorAll('[data-choice]').forEach(b => b.addEventListener('click', () => { location.hash = 'play'; }));
setMode(mode);

const tmpV = new THREE.Vector3();
function collide(pos) {
  for (const b of world.colliders) {
    if (pos.x > b.min.x - 0.3 && pos.x < b.max.x + 0.3 && pos.z > b.min.z - 0.3 && pos.z < b.max.z + 0.3) return true;
  }
  return Math.abs(pos.x) > 14.5 || pos.z < -10.6 || pos.z > 10.5;
}

function updatePlayer(dt, t) {
  let x = stick.x, z = stick.y;
  if (keys.has('a') || keys.has('arrowleft')) x -= 1;
  if (keys.has('d') || keys.has('arrowright')) x += 1;
  if (keys.has('w') || keys.has('arrowup')) z -= 1;
  if (keys.has('s') || keys.has('arrowdown')) z += 1;
  const len = Math.hypot(x, z);
  const moving = len > 0.1;
  if (moving) {
    x /= Math.max(1, len); z /= Math.max(1, len);
    const speed = 4.2;
    tmpV.copy(player.position); tmpV.x += x * speed * dt;
    if (!collide(tmpV)) player.position.x = tmpV.x;
    tmpV.copy(player.position); tmpV.z += z * speed * dt;
    if (!collide(tmpV)) player.position.z = tmpV.z;
    const target = Math.atan2(x, z);
    let d = target - player.rotation.y;
    d = Math.atan2(Math.sin(d), Math.cos(d));
    player.rotation.y += d * Math.min(1, dt * 12);
  }
  // andar com gingado
  const bob = moving ? Math.abs(Math.sin(t * 11)) * 0.08 : Math.sin(t * 2) * 0.01;
  player.position.y = bob;
  player.userData.body.rotation.z = moving ? Math.sin(t * 11) * 0.08 : 0;
}

function updateGuards(dt) {
  let seen = false;
  for (const g of guards) {
    if (!g.frozen && mode === 'play') {
      const [tx, tz] = g.route[g.idx];
      const dx = tx - g.obj.position.x, dz = tz - g.obj.position.z;
      const d = Math.hypot(dx, dz);
      if (d < 0.1) g.idx = (g.idx + 1) % g.route.length;
      else {
        g.obj.position.x += (dx / d) * g.speed * dt;
        g.obj.position.z += (dz / d) * g.speed * dt;
        const target = Math.atan2(dx, dz);
        let a = target - g.obj.rotation.y; a = Math.atan2(Math.sin(a), Math.cos(a));
        g.obj.rotation.y += a * Math.min(1, dt * 5);
      }
    }
    // jogador no cone de visão?
    const toP = tmpV.copy(player.position).sub(g.obj.position); toP.y = 0;
    const dist = toP.length();
    const fwd = new THREE.Vector3(Math.sin(g.obj.rotation.y), 0, Math.cos(g.obj.rotation.y));
    if (dist < 4.5 && toP.normalize().dot(fwd) > 0.82) seen = true;
  }
  return seen;
}

function updateCamera(dt) {
  const v = VIEWS[mode] || VIEWS.play;
  if (v.follow) {
    camTarget.lerp(player.position, 1 - Math.exp(-dt * 4));
    const desired = tmpV.copy(camTarget).add(camOffset);
    camera.position.lerp(desired, 1 - Math.exp(-dt * 4));
    camera.lookAt(camTarget.x, camTarget.y + 0.6, camTarget.z);
  } else {
    camera.position.lerp(new THREE.Vector3(...v.pos), 1 - Math.exp(-dt * 3));
    camTarget.lerp(new THREE.Vector3(...v.look), 1 - Math.exp(-dt * 3));
    camera.lookAt(camTarget);
  }
}

// posiciona a câmera de imediato no primeiro quadro
(() => {
  const v = VIEWS[mode] || VIEWS.play;
  if (v.follow) { camTarget.copy(player.position); camera.position.copy(player.position).add(camOffset); }
  else { camera.position.set(...v.pos); camTarget.set(...v.look); }
  camera.lookAt(camTarget);
})();

function updateHud(seen, dt) {
  if (mode === 'play') {
    state.suspicion = Math.min(1, Math.max(0, state.suspicion + (seen ? dt * 0.35 : -dt * 0.04)));
    state.clock += dt * 0.5;
  }
  const m = Math.floor(state.clock / 60) % 24, s = Math.floor(state.clock % 60);
  hud.clock.textContent = `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  hud.eye.setAttribute('transform', `scale(1 ${0.15 + state.suspicion * 0.85})`);
  hud.eyeWrap.dataset.level = state.suspicion > 0.75 ? 'high' : state.suspicion > 0.4 ? 'mid' : 'low';
}

const clock = new THREE.Clock();
function resize() {
  const w = window.innerWidth, h = window.innerHeight;
  renderer.setSize(w, h); composer.setSize(w, h);
  camera.aspect = w / h; camera.updateProjectionMatrix();
  grade.uniforms.uAspect.value = w / h;
  // em retrato a câmera se afasta para caber a casa
  camOffset.set(0, w < h ? 15 : 10.5, w < h ? 15 : 12.5);
}
addEventListener('resize', resize);
resize();

function frame() {
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;
  updateAnimated(world.animated, t, dt);
  if (mode === 'play') updatePlayer(dt, t);
  const seen = updateGuards(dt);
  updateHud(seen, dt);
  updateCamera(dt);
  grade.uniforms.uTime.value = t;
  composer.render();
  requestAnimationFrame(frame);
}
frame();
window.__ready = true;
