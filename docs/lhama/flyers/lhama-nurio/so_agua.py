"""Lhama Nurio: anima SÓ a água do flyer. Nada é recortado nem se move.
A imagem original é distorcida por uma ondulação em loop, com peso que vai a zero perto dos
textos e personagens. Esses pixels ficam idênticos ao original, sem borda nem recorte.
Uso: python3 so_agua.py <flyer.png> <mascara-elementos.npy> <saida.mp4> [segundos=12] [loop=4]"""
import sys, math, subprocess
import numpy as np, cv2
from PIL import Image

SRC, MASK, OUT = sys.argv[1:4]
DUR = float(sys.argv[4]) if len(sys.argv) > 4 else 12.0
LOOP = float(sys.argv[5]) if len(sys.argv) > 5 else 4.0
FPS = 30
im = np.asarray(Image.open(SRC).convert("RGB")).astype(np.float32)
H, W, _ = im.shape
m = np.load(MASK).astype(np.uint8)
m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (29, 29)))
# peso da ondulação: 0 sobre/perto dos elementos, sobe suave até 1 em ~70 px
dist = cv2.distanceTransform((1 - m).astype(np.uint8), cv2.DIST_L2, 5)
wgt = np.clip(dist / 70.0, 0, 1)
wgt = wgt * wgt * (3 - 2 * wgt)

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
proc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "15",
                         "-preset", "slow", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
for f in range(int(DUR * FPS)):
    p = 2 * math.pi * ((f / FPS) % LOOP) / LOOP        # ciclos inteiros: o loop fecha sem emenda
    dx = 6 * np.sin(yy / 130 + p) + 3.5 * np.sin((xx + yy) / 85 - 2 * p) + 2 * np.sin(xx / 50 + 3 * p)
    dy = 6 * np.cos(xx / 150 - p) + 3.5 * np.sin((xx - yy) / 105 + 2 * p) + 2 * np.cos(yy / 55 - 3 * p)
    fr = cv2.remap(im, xx + dx * wgt, yy + dy * wgt, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    lum = fr.mean(-1) / 255
    shine = 1 + 0.10 * np.sin(xx / 70 + yy / 95 + 2 * p) * np.clip(lum - 0.45, 0, 1) * 2 * wgt
    fr = np.clip(fr * shine[..., None], 0, 255).astype(np.uint8)
    proc.stdin.write(fr.tobytes())
proc.stdin.close(); proc.wait()
print("ok", OUT)
