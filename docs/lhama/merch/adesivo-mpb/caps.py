"""Fecha os dois braços da faixa com uma curva em U (as listras dão a volta, como no lóbulo de cima),
no lugar das pontas bagunçadas da arte expandida. Gera:
  - arte-caps.png: arte expandida com as pontas refeitas
  - forma-full.npy: máscara da forma do adesivo (faixa amarela grossa preenchida), em coordenadas da arte expandida
Uso: python3 caps.py <arte-corrigida.png> <saida-dir>"""
import sys, os
import numpy as np, cv2
from PIL import Image, ImageDraw
from scipy import ndimage as nd

SRC, OUT = sys.argv[1], sys.argv[2]
im = np.asarray(Image.open(SRC).convert("RGB")).astype(np.float32)
H, W, _ = im.shape
r, g, b = im[..., 0], im[..., 1], im[..., 2]
K = lambda k: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * k + 1, 2 * k + 1))

# faixa amarela grossa
yel = ((r > 185) & (g > 180) & (b < 180) & (r - b > 50)).astype(np.uint8)
yel = cv2.morphologyEx(yel, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
thick = cv2.morphologyEx(yel, cv2.MORPH_OPEN, K(13))
n, lab, st, _ = cv2.connectedComponentsWithStats(thick)
core = np.zeros_like(thick)
for i in range(1, n):
    x, y, w, h, a = st[i]
    if a > 2500 and x > 250 and x + w < 2150:
        core[lab == i] = 1
band = (cv2.morphologyEx(yel, cv2.MORPH_OPEN, K(6)) & cv2.dilate(core, K(45))).astype(np.uint8)

# braços: coluna do corte, topo/base externos e lado pra onde o braço aponta
ARMS = [dict(xc=480, side=-1), dict(xc=1860, side=+1)]
rng = np.random.default_rng(3)
out = im.copy()
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
closed = band.copy()
caps = np.zeros((H, W), bool)
def arm_span(x, yc_guess):
    ys = np.nonzero(band[:, x])[0]
    ys = ys[np.abs(ys - yc_guess) < 160]
    return (ys.min(), ys.max()) if len(ys) else (None, None)


RANGES = [(430, 640, 875), (1760, 1900, 455)]
for A, (xa, xb, ycg) in zip(ARMS, RANGES):
    best = None
    for x in range(xa, xb, 4):
        t0, b0 = arm_span(x, ycg); t1, b1 = arm_span(x + 12, ycg); t2, b2 = arm_span(x - 12, ycg)
        if None in (t0, t1, t2):
            continue
        cost = abs(t1 - t2) + abs(b1 - b2)
        if best is None or cost < best[0]:
            best = (cost, x)
    A["xc"] = best[1]
    print("corte", A["side"], best)
for A in ARMS:
    xc, side = A["xc"], A["side"]
    col = band[:, xc]
    ys = np.nonzero(col)[0]
    # parte do braço: perto da linha central esperada
    yc_guess = 875 if side < 0 else 455
    ys = ys[np.abs(ys - yc_guess) < 160]
    ytop, ybot = ys.min(), ys.max()
    yc, R = (ytop + ybot) / 2, (ybot - ytop) / 2
    # perfil de cor ao longo da coluna (média de 5 colunas antes do corte, pra tirar ruído)
    xs = [xc - side * k for k in range(0, 3)]
    prof = np.median(np.stack([im[int(ytop):int(ybot) + 1, x] for x in xs]), axis=0)   # (2R+1, 3)
    prof = cv2.GaussianBlur(prof[None], (1, 5), 0)[0]
    tgrid = np.arange(prof.shape[0]) - R                                                # -R..R
    # região da tampa: meio-disco além do corte
    dx = (xx - xc) * side
    d = np.hypot(xx - xc, yy - yc)
    cap = (dx > 0) & (d <= R + 1.5)
    def sample(tv):
        return np.stack([np.interp(tv, tgrid, prof[:, k]) for k in range(3)], -1)

    # listras do perfil -> tintas -> faixas (runs) de cima pra baixo
    pal = np.array([[233, 226, 128], [182, 214, 166], [126, 134, 232]], np.float32)
    for _ in range(6):
        lab_ = np.argmin(((prof[:, None] - pal[None]) ** 2).sum(-1), 1)
        pal = np.stack([prof[lab_ == k].mean(0) if (lab_ == k).any() else pal[k] for k in range(3)])
    lab_ = np.argmin(((prof[:, None] - pal[None]) ** 2).sum(-1), 1).astype(np.uint8)
    lab_ = cv2.medianBlur(lab_[:, None].repeat(3, 1), 5)[:, 1].astype(int)
    runs = []
    st0 = 0
    for k in range(1, len(lab_) + 1):
        if k == len(lab_) or lab_[k] != lab_[st0]:
            runs.append([st0, k - 1, int(lab_[st0])]); st0 = k
    clean_runs = []
    for r_ in runs:   # listras de 1-2 px viram parte da vizinha
        if clean_runs and (r_[1] - r_[0] < 2 or r_[2] == clean_runs[-1][2]):
            clean_runs[-1][1] = r_[1]
        else:
            clean_runs.append(r_)
    runs = clean_runs
    n_r = len(runs)
    print("listras", side, n_r, [r_[2] for r_ in runs])
    # U's aninhados de fora pra dentro (supersampling 4x)
    SSc = 4
    x0c = int(xc - R - 6)
    y0c = int(ytop - 6)
    wc, hc = int(2 * R + 12), int(2 * R + 14)
    canv = Image.new("RGB", (wc * SSc, hc * SSc), tuple(int(v) for v in pal[runs[0][2]]))
    dc = ImageDraw.Draw(canv)
    for jj in range((n_r + 1) // 2):
        tr_, br_ = runs[jj], runs[n_r - 1 - jj]
        ty = ytop + tr_[0]; by = ytop + br_[1] + 1
        cyy, rr_ = (ty + by) / 2, (by - ty) / 2
        dc.ellipse([(xc - rr_ - x0c) * SSc, (cyy - rr_ - y0c) * SSc, (xc + rr_ - x0c) * SSc, (cyy + rr_ - y0c) * SSc],
                   fill=tuple(int(v) for v in pal[tr_[2]]))
    canv = np.asarray(canv.resize((wc, hc), Image.LANCZOS)).astype(np.float32)
    capimg = np.zeros_like(im)
    capimg[y0c:y0c + hc, x0c:x0c + wc] = canv[:max(0, min(hc, H - y0c)), :max(0, min(wc, W - x0c))]
    grain = rng.standard_normal((H, W, 1)).astype(np.float32) * 7.0
    colr = np.clip(capimg + grain, 0, 255)
    out = np.where(cap[..., None], colr, out)
    # costura curta (6 px)
    zone = (np.abs(dx) <= 6) & (np.abs(yy - yc) <= R)
    a_ = np.clip((dx + 6) / 12, 0, 1)[..., None]
    out = np.where(zone[..., None], out * (1 - a_) + colr * a_, out)
    caps |= cap
    # fecha a forma: corte reto + meio-disco
    beyond = (dx > 0)
    closed[beyond] = 0
    closed[cap] = 1
    cv2.line(closed, (xc, int(ytop)), (xc, int(ybot)), 1, 3)

# a faixa é interrompida pelo texto do anel em dois trechos: liga só ali
big = cv2.morphologyEx(closed, cv2.MORPH_CLOSE, K(100))
GAPS = [(800, 470, 1000, 780), (1360, 590, 1600, 1040)]
for x0, y0, x1, y1 in GAPS:
    closed[y0:y1, x0:x1] |= big[y0:y1, x0:x1]
Image.fromarray(closed * 255).resize((1200, 675)).save(os.path.join(OUT, "debug-closed.png"))
f = nd.binary_fill_holes(cv2.morphologyEx(closed, cv2.MORPH_CLOSE, K(20)))
lab2, _ = nd.label(f)
shape = lab2 == lab2[650, 1210]
shape = cv2.morphologyEx(shape.astype(np.uint8), cv2.MORPH_OPEN, K(12)) > 0
Image.fromarray(out.astype(np.uint8)).save(os.path.join(OUT, "arte-caps.png"))
np.save(os.path.join(OUT, "forma-full.npy"), shape)
ys, xs = np.nonzero(shape)
print("forma", xs.min(), xs.max(), ys.min(), ys.max(), round(shape.mean(), 3))
