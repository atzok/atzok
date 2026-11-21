"""Generate the poster textures for the ÄTZØK agenda video.
Outputs (into ../assets): dither-pink.png, contour.svg, grain.png"""
import numpy as np, sys, os
from PIL import Image
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
rng = np.random.default_rng(1557)
PINK = (238, 60, 152); BLACK = (20, 20, 20); GREEN = "#2BAE4C"

def smooth_noise(h, w, scale, octaves=4, seed=0):
    r = np.random.default_rng(seed); acc = np.zeros((h, w)); amp = 1.0
    for o in range(octaves):
        f = np.fft.fft2(r.standard_normal((h, w)))
        ky = np.fft.fftfreq(h)[:, None]; kx = np.fft.fftfreq(w)[None, :]
        s = scale / (2 ** o)
        acc += amp * np.real(np.fft.ifft2(f * np.exp(-(kx**2 + ky**2) * (s**2) * 2 * np.pi**2)))
        amp *= 0.5
    acc -= acc.min(); return acc / acc.max()

# 1. pink block with black error-diffusion dither (riso / photocopy grain)
h, w = 92, 136
n = smooth_noise(h, w, 10, 4, seed=7) ** 1.3 * 0.8 + rng.random((h, w)) * 0.2 + 0.12
img = n.copy(); out = np.zeros_like(img)
for y in range(h):
    for x in range(w):
        o = 1.0 if img[y, x] > 0.42 else 0.0; out[y, x] = o; e = img[y, x] - o
        if x + 1 < w: img[y, x + 1] += e * 7 / 16
        if y + 1 < h:
            if x > 0: img[y + 1, x - 1] += e * 3 / 16
            img[y + 1, x] += e * 5 / 16
            if x + 1 < w: img[y + 1, x + 1] += e * 1 / 16
rgb = np.where(out[..., None] > 0.5, PINK, BLACK).astype(np.uint8)
Image.fromarray(rgb).resize((w * 6, h * 6), Image.NEAREST).save(f"{OUT}/dither-pink.png")

# 2. green topographic contour field (marching squares) with a ragged top edge
W, H, step = 960, 640, 4
gw, gh = W // step + 1, H // step + 1
f = smooth_noise(gh, gw, 16, 3, seed=3) + 0.12 * smooth_noise(gh, gw, 3, 2, seed=9)
walk = np.cumsum(rng.choice([-1, 0, 0, 0, 1], gw)) * 3
edge = np.clip(40 + walk - walk.mean() + rng.integers(0, 10, gw) * (rng.random(gw) < .25), 12, 90)  # ragged top, grid px
paths = []
for lv in np.linspace(0.12, 1.05, 9):
    segs = []
    for j in range(gh - 1):
        for i in range(gw - 1):
            a, b, c, d = f[j, i], f[j, i + 1], f[j + 1, i + 1], f[j + 1, i]
            idx = (a > lv) | ((b > lv) << 1) | ((c > lv) << 2) | ((d > lv) << 3)
            if idx in (0, 15) or j * step < edge[i] / 1 * 0 + edge[i]: continue
            def lerp(p, q, va, vb):
                t = (lv - va) / (vb - va + 1e-9); return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
            P = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]; V = [a, b, c, d]
            E = {0: lerp(P[0], P[1], a, b), 1: lerp(P[1], P[2], b, c), 2: lerp(P[3], P[2], d, c), 3: lerp(P[0], P[3], a, d)}
            pairs = {1:[(3,0)],2:[(0,1)],3:[(3,1)],4:[(1,2)],5:[(3,0),(1,2)],6:[(0,2)],7:[(3,2)],8:[(3,2)],
                     9:[(0,2)],10:[(0,1),(3,2)],11:[(1,2)],12:[(3,1)],13:[(0,1)],14:[(3,0)]}[idx]
            for e1, e2 in pairs:
                p1, p2 = E[e1], E[e2]
                segs.append(f"M{p1[0]*step:.1f} {p1[1]*step:.1f}L{p2[0]*step:.1f} {p2[1]*step:.1f}")
    paths.append("".join(segs))
outline = "M0 %d " % (H) + " ".join(f"L{i*step} {edge[i]*1:.0f}" for i in range(gw)) + f" L{W} {H} Z"
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" fill="none" stroke="{GREEN}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">',
       f'<path class="ct-edge" d="{outline}"/>'] + [f'<path class="ct-l" d="{p}"/>' for p in paths if p] + ["</svg>"]
open(f"{OUT}/contour.svg", "w").write("\n".join(svg))

# 3. paper grain overlay (transparent PNG, light + dark specks)
g = rng.normal(0, 1, (960, 540))
a = np.clip(np.abs(g) * 22, 0, 60).astype(np.uint8)
c = np.where(g > 0, 255, 0).astype(np.uint8)
Image.fromarray(np.dstack([c, c, c, a]), "RGBA").resize((1080, 1920), Image.NEAREST).save(f"{OUT}/grain.png")
print("ok")
