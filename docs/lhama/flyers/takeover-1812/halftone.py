"""Imagens em retícula (halftone/risografia) para o flyer 18.12, rodada 3.
Referências: docs/lhama/referencias/06-halftone-agua.jpg e 07-halftone-velas.jpg.
Cada imagem é desenhada como camadas de tinta (0..1) e impressa com retícula
em ângulos diferentes por tinta, sobre papel. Saída 1080x1350 (x2 pra alta).

Uso: python3 halftone.py <saida> [escala=1]
"""
import sys, os, math
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from scipy.spatial import cKDTree

OUT = sys.argv[1]
S = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
os.makedirs(OUT, exist_ok=True)
W, H = int(1080 * S), int(1350 * S)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32) / S  # coordenadas no espaço 1080x1350
rng = np.random.default_rng(1812)

INK = {  # cores tiradas das referências
    "blue": (64, 56, 200), "lime": (196, 238, 110), "pink": (236, 128, 222),
    "black": (10, 18, 10), "lilac": (150, 120, 232),
}
PAPER = (240, 238, 232)


def noise(scale, seed):
    r = np.random.default_rng(seed).standard_normal((H // 8 + 2, W // 8 + 2)).astype(np.float32)
    r = gaussian_filter(r, scale / 8)
    r = np.array(Image.fromarray(r).resize((W, H), Image.BICUBIC))
    return (r - r.mean()) / (r.std() + 1e-6)


def screen(val, angle, cell, jitter=0.07, seed=0):
    """Retícula clássica: limiar em cosseno girado; antialias por suavização."""
    a = math.radians(angle)
    u = (xx * math.cos(a) + yy * math.sin(a)) / cell * 2 * math.pi
    v = (-xx * math.sin(a) + yy * math.cos(a)) / cell * 2 * math.pi
    t = 0.5 - 0.25 * (np.cos(u) + np.cos(v))
    val = np.clip(val + jitter * np.random.default_rng(seed).standard_normal(val.shape).astype(np.float32), 0, 1)
    return np.clip((val - t) * 10 * S + 0.5, 0, 1)


def press(layers, paper=PAPER, grain=0.06, blur=2.5):
    img = np.ones((H, W, 3), np.float32) * np.array(paper, np.float32)
    for name, val, angle, cell in layers:
        val = gaussian_filter(val.astype(np.float32), blur * S)
        a = screen(val, angle, cell, seed=hash(name) % 999)[..., None]
        img = img * (1 - a) + np.array(INK[name], np.float32) * a
    img *= (1 + grain * np.random.default_rng(7).standard_normal((H, W, 1)).astype(np.float32))
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


def soft(mask, r):
    return gaussian_filter(mask.astype(np.float32), r * S)


# ------------------------------------------------------------ A · velas
def velas():
    def cyl(cx, top, w):
        body = (np.abs(xx - cx) < w / 2) & (yy > top)
        cap = ((xx - cx) / (w / 2)) ** 2 + ((yy - top) / (w * 0.16)) ** 2 < 1
        return body | cap, cap

    b1, c1 = cyl(395, 880, 300)
    b2, c2 = cyl(640, 1010, 320)

    def flame(cx, base, h, w, lean, seed):
        t = np.clip((base - yy) / h, 0, 1)
        prof = np.sqrt(np.clip(np.sin(t * math.pi * 0.92 + 0.12), 0, 1)) * (1 - t) ** 0.55
        x0 = cx + lean * t ** 1.8 + 34 * np.sin(t * 5.5 + seed) * t + 14 * noise(140, seed) * t
        return (np.abs(xx - x0) < w * prof) & (yy < base) & (yy > base - h)

    f1 = flame(395, 910, 560, 120, 90, 3)
    f2 = flame(640, 1040, 560, 128, -70, 4)
    fl = (f1 | f2).astype(np.float32)
    bodies = (b1 | b2).astype(np.float32)
    caps = (c1 | c2).astype(np.float32)
    # chama interna rosa (miolo) e brilho
    core = soft(fl, 30) > 0.62
    glow = soft(fl, 70)
    shade = np.clip((yy - 1000) / 300, 0, 1)
    bg = 0.30 + 0.12 * noise(300, 9)
    blue = np.clip(bg * 0.9 + glow * 0.35 + bodies * 0.65 - fl * 1.0 - caps * 0.7, 0, 1)
    lime = np.clip(0.28 + 0.1 * noise(260, 11) + soft(fl, 10) * 0.95 + caps * 0.85 - core * 0.9 - bodies * 0.3, 0, 1)
    pink = np.clip(soft(core, 10) * 0.95, 0, 1)
    black = np.clip(bodies * shade * 1.05 * (1 - caps), 0, 1)
    return press([("lime", lime, 15, 7), ("blue", blue, 75, 7), ("pink", pink, 45, 7), ("black", black, 0, 7)], blur=9)


# ------------------------------------------------------------ B · água / pista
def agua():
    pts = np.stack([rng.uniform(-200, 1280, 260), rng.uniform(-200, 1550, 260)], 1)
    wx = (xx + 120 * noise(380, 21) + 30 * noise(110, 22)) * 0.75 + yy * 0.25
    wy = (yy + 120 * noise(380, 23) + 30 * noise(110, 24)) * 1.35
    tree = cKDTree(pts)
    d, _ = tree.query(np.stack([wx.ravel(), wy.ravel()], 1), k=2)
    edge = (d[:, 1] - d[:, 0]).reshape(H, W)
    lines = np.exp(-edge / 9)  # linhas brancas das cáusticas
    blobs = np.clip(noise(110, 31) * 1.1 - 0.55, 0, 1)
    shadow = (noise(300, 41) * 0.9 + noise(70, 42) * 0.25 + (xx - 600) / 230 - (yy - 200) / 2200) > 0.9
    shadow = soft(shadow, 4) > 0.5
    blue = np.clip(0.95 - lines * 1.3 - blobs * 0.55, 0, 1) * (1 - shadow)
    lime = np.clip(blobs * 1.3 - lines * 0.6, 0, 1) * (1 - shadow)
    black = shadow.astype(np.float32)
    return press([("blue", blue, 45, 6), ("lime", lime, 15, 6), ("black", black, 0, 6)], paper=(244, 244, 248))


# ------------------------------------------------------------ C · bola espelhada
def bola():
    cx, cy, r = 540, 470, 300
    dx, dy = (xx - cx) / r, (yy - cy) / r
    inside = dx ** 2 + dy ** 2 < 1
    dz = np.sqrt(np.clip(1 - dx ** 2 - dy ** 2, 0, 1))
    lat = np.arcsin(np.clip(dy, -1, 1)); lon = np.arctan2(dx, dz)
    tile = (np.abs(np.sin(lat * 13)) < 0.12) | (np.abs(np.sin(lon * 13)) < 0.12)
    cellid = (np.floor(lat * 13 / math.pi * 2) * 31 + np.floor(lon * 13 / math.pi * 2)).astype(np.int64)
    rnd = (np.sin(cellid * 12.9898) * 43758.5453) % 1
    light = np.clip(-0.5 * dx - 0.6 * dy + 0.62 * dz, 0, 1)
    sparkle = (rnd > 0.9) & inside
    # feixes de luz saindo da bola
    ang = np.arctan2(yy - cy, xx - cx)
    beams = np.zeros_like(xx)
    for k, a0 in enumerate(np.linspace(0.25, math.pi - 0.25, 9)):
        beams += np.exp(-((ang - a0) / 0.035) ** 2) * np.clip((np.hypot(xx - cx, yy - cy) - r) / 600, 0, 1)
    beams = np.clip(beams, 0, 1) * (~inside)
    blue = np.where(inside, np.clip(0.25 + (1 - light) * 0.75, 0, 1) * (~tile) + tile * 0.0, beams * 0.55)
    lime = np.where(inside, sparkle * 1.0 + (light > 0.82) * 0.7, beams * 0.65)
    pink = np.where(inside, (rnd > 0.8) * (rnd <= 0.9) * 0.9, 0)
    black = np.where(inside, tile * 0.95 + (1 - light) * 0.35, 0.92 - beams * 0.9)
    black = np.clip(black, 0, 1)
    return press([("black", black, 0, 7), ("blue", blue, 75, 7), ("lime", lime, 15, 7), ("pink", pink, 45, 7)], grain=0.05)


for name, fn in [("velas", velas), ("agua", agua), ("bola", bola)]:
    fn().save(os.path.join(OUT, f"ht-{name}.png"))
    print(name, "ok")
