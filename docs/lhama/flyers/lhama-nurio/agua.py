"""Fundo de água animado do reels Lhama Nurio.
1) limpa a arte: tira personagens e textos (máscara) e preenche com água copiada de áreas vizinhas;
2) anima: ondulação por deslocamento (soma de senos com ciclos inteiros = loop perfeito) + brilho das cáusticas.
Uso: python3 agua.py <flyer.png> <mascara.npy> <saida.mp4> [segundos=12] [loop=4]"""
import sys, math, subprocess
import numpy as np, cv2
from PIL import Image

SRC, MASK, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
DUR = float(sys.argv[4]) if len(sys.argv) > 4 else 12.0
LOOP = float(sys.argv[5]) if len(sys.argv) > 5 else 4.0
FPS = 30
im = np.asarray(Image.open(SRC).convert("RGB")).astype(np.float32)
H, W, _ = im.shape
m = np.load(MASK).astype(np.uint8)
m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (37, 37))) > 0

# ---- placa limpa por "quilting": cobre a área mascarada com blocos de água tirados das partes limpas,
# escolhendo em cada posição o bloco que melhor casa com o que já está ao redor; emendas misturadas em degradê.
rng = np.random.default_rng(11)
P, OV = 72, 24                       # bloco e sobreposição
STEP = P - OV
clean = ~cv2.dilate(m.astype(np.uint8), np.ones((P, P), np.uint8)).astype(bool)
cy, cx = np.nonzero(clean[: H - P, : W - P])
pick = rng.choice(len(cy), 900, replace=False)
cands = np.stack([im[cy[i]:cy[i] + P, cx[i]:cx[i] + P] for i in pick])          # (N,P,P,3)
small = cands[:, ::4, ::4]
plate = im.copy()
known = ~m
ramp = np.linspace(0, 1, OV, dtype=np.float32)
ys_, xs_ = np.nonzero(m)
y0, y1, x0, x1 = max(ys_.min() - OV, 0), min(ys_.max() + P, H - P + 1), max(xs_.min() - OV, 0), min(xs_.max() + P, W - P + 1)
ylist = list(range(y0, y1, STEP)) + [H - P]
xlist = list(range(x0, x1, STEP)) + [W - P]
for y in sorted(set(min(v, H - P) for v in ylist)):
    for x in sorted(set(min(v, W - P) for v in xlist)):
        if not m[y:y + P, x:x + P].any():
            continue
        tgt = plate[y:y + P, x:x + P]
        kn = known[y:y + P, x:x + P]
        if kn.sum() > 40:
            w = kn[::4, ::4][None, ..., None]
            err = (((small - tgt[::4, ::4][None]) ** 2) * w).sum((1, 2, 3))
            best = np.argsort(err)[:8][rng.integers(0, 8)]
        else:
            best = rng.integers(0, len(cands))
        blk = cands[best]
        # peso: entra cheio onde é desconhecido; nas bordas já conhecidas, degradê
        wgt = np.ones((P, P), np.float32)
        if known[y:y + P, x:x + OV].any():
            wgt[:, :OV] = np.minimum(wgt[:, :OV], ramp[None, :])
        if known[y:y + OV, x:x + P].any():
            wgt[:OV, :] = np.minimum(wgt[:OV, :], ramp[:, None])
        wgt = np.where(kn, wgt * 0.0 + np.where(m[y:y + P, x:x + P], wgt, 0), wgt)
        wgt = np.where(~m[y:y + P, x:x + P] & kn, 0, wgt)
        plate[y:y + P, x:x + P] = tgt * (1 - wgt[..., None]) + blk * wgt[..., None]
        known[y:y + P, x:x + P] |= m[y:y + P, x:x + P]
# costura suave entre a placa e o original
feather = np.clip(cv2.GaussianBlur(m.astype(np.float32), (0, 0), 10)[..., None] * 1.5, 0, 1)
plate = im * (1 - feather) + plate * feather

# ---- animação em loop
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
proc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16",
                         "-preset", "medium", OUT], stdin=subprocess.PIPE)
N = int(DUR * FPS)
for f in range(N):
    p = 2 * math.pi * ((f / FPS) % LOOP) / LOOP          # fase 0..2π, fecha o loop
    dx = (7 * np.sin(yy / 140 + p) + 4 * np.sin((xx + yy) / 90 - 2 * p) + 2.5 * np.sin(xx / 55 + 3 * p))
    dy = (7 * np.cos(xx / 160 - p) + 4 * np.sin((xx - yy) / 110 + 2 * p) + 2.5 * np.cos(yy / 60 - 3 * p))
    fr = cv2.remap(plate, xx + dx, yy + dy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    # brilho: as cáusticas claras pulsam de leve
    lum = fr.mean(-1, keepdims=True) / 255
    shine = 1 + 0.10 * np.sin(xx / 70 + yy / 95 + 2 * p)[..., None] * np.clip(lum - 0.45, 0, 1) * 2
    fr = np.clip(fr * shine, 0, 255).astype(np.uint8)
    proc.stdin.write(fr.tobytes())
proc.stdin.close(); proc.wait()
Image.fromarray(plate.astype(np.uint8)).save(OUT.rsplit(".", 1)[0] + "-placa.png")
print("ok", OUT, N, "quadros")
