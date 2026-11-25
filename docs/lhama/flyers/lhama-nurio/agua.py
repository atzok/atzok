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
m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))) > 0

# ---- placa limpa: cada pixel mascarado recebe o pixel do primeiro deslocamento que cai em água
plate = im.copy()
todo = m.copy()
pid = np.zeros((H, W), np.int16)
offs = [(170, 230), (-190, 250), (0, 260), (0, -260), (240, 0), (-240, 0), (0, 420), (0, -420), (300, 300), (-300, -300), (380, 0), (-380, 0),
        (0, 560), (0, -560), (520, 200), (-520, -200)]
for k, (dx, dy) in enumerate(offs, 1):
    if not todo.any():
        break
    sh = np.roll(np.roll(im, dy, 0), dx, 1)
    ok = ~np.roll(np.roll(m, dy, 0), dx, 1)
    take = todo & ok
    plate[take] = sh[take]
    pid[take] = k
    todo &= ~take
# suaviza só as emendas entre remendos diferentes
edge = np.zeros((H, W), bool)
edge[:, 1:] |= (pid[:, 1:] != pid[:, :-1]) & m[:, 1:]
edge[1:, :] |= (pid[1:, :] != pid[:-1, :]) & m[1:, :]
band = np.clip(cv2.GaussianBlur(edge.astype(np.float32), (0, 0), 10) * 12, 0, 1)[..., None]
plate = plate * (1 - band) + cv2.GaussianBlur(plate, (0, 0), 7) * band
if todo.any():
    plate = cv2.inpaint(plate.astype(np.uint8), todo.astype(np.uint8) * 255, 9, cv2.INPAINT_TELEA).astype(np.float32)
# costura suave entre placa e original
feather = np.clip(cv2.GaussianBlur(m.astype(np.float32), (0, 0), 18)[..., None] * 1.6, 0, 1)
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
