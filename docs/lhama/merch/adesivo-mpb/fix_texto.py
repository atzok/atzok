"""Corrige o texto do anel da arte 'Música Psicodélica Brasileira' (BRASILERA -> BRASILEIRA).
Apaga o trecho visível do texto antigo (inpaint) e redesenha no mesmo arco elíptico,
mesmo estilo: preenchimento amarelo, contorno rosa e sombra preta deslocada.
Uso: python3 fix_texto.py <mpb-expandido.png> <saida.png>"""
import sys, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as nd

SRC, OUT = sys.argv[1], sys.argv[2]
FONT = __file__.rsplit("/", 1)[0] + "/../../carrossel-onde-o-clube/Adca.ttf"
im = np.asarray(Image.open(SRC).convert("RGB"))
H, W, _ = im.shape
r, g, b = [im[..., i].astype(int) for i in range(3)]
pink = (r > 200) & (b > 150) & (g < 170) & (r - g > 60)

# elipse do texto (ajustada nos pixels rosa, fora da lhama)
cx, cy, d1, d2, ang = 1208.21, 694.25, 441.65, 880.34, 126.28
A = math.radians(ang)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
u = ((xx - cx) * math.cos(A) + (yy - cy) * math.sin(A)) / (d1 / 2)
v = (-(xx - cx) * math.sin(A) + (yy - cy) * math.cos(A)) / (d2 / 2)
rr = np.hypot(u, v)
tt = np.degrees(np.arctan2(v, u)) % 360
T0, T1 = 74.0, 201.0          # trecho visível: de t=74 descendo até t=201 (passando por 0)
S_B = 700.0                   # comprimento de arco onde começa o "B" de BRASILERA no original
_ts = np.linspace(T0, T1 - 360, 4000)
_pp = np.array([(cx + d1 / 2 * math.cos(math.radians(t)) * math.cos(A) - d2 / 2 * math.sin(math.radians(t)) * math.sin(A),
                 cy + d1 / 2 * math.cos(math.radians(t)) * math.sin(A) + d2 / 2 * math.sin(math.radians(t)) * math.cos(A)) for t in _ts])
_s = np.r_[0, np.cumsum(np.hypot(*np.diff(_pp, axis=0).T))]
T_B = float(_ts[np.searchsorted(_s, S_B - 6)]) % 360      # ângulo do início do trecho apagado
in_run = (tt <= T_B) & (tt >= T1) if T_B > T1 else (tt <= T_B) | (tt >= T1)
band = (rr > 0.80) & (rr < 1.20) & in_run

# máscara do texto antigo: rosa + sombra escura vizinha + miolo das letras
dark = (r + g + b) < 200
pk = pink & band
near = nd.binary_dilation(pk, iterations=11)
yelw = (r > 190) & (g > 180) & (b < 190)
light = (r + g + b) > 600
txt = pk | (dark & near & band) | ((yelw | light) & nd.binary_dilation(pk, iterations=9) & band)
txt = nd.binary_dilation(txt, iterations=2)
txt = nd.binary_fill_holes(txt) | txt
txt = nd.binary_closing(txt, iterations=4) & band
txt = nd.binary_dilation(txt, iterations=3)
clean = cv2.inpaint(np.ascontiguousarray(im[..., ::-1]), (txt * 255).astype(np.uint8), 5, cv2.INPAINT_TELEA)[..., ::-1].astype(np.float32)
# devolve o grão do papel na área reconstruída (textura tirada de outra parte da arte)
hp = im.astype(np.float32) - cv2.GaussianBlur(im.astype(np.float32), (0, 0), 2.5)
hp = np.roll(np.roll(hp, 211, 0), 157, 1)
clean = np.where(txt[..., None], np.clip(clean + np.clip(hp, -14, 14), 0, 255), clean)


KR = float(sys.argv[3]) if len(sys.argv) > 3 else 0.98   # ajusta o texto novo pra fora, sobre o rastro do antigo


def P(td):
    t = math.radians(td)
    x, y = KR * d1 / 2 * math.cos(t), KR * d2 / 2 * math.sin(t)
    return cx + x * math.cos(A) - y * math.sin(A), cy + x * math.sin(A) + y * math.cos(A)


# amostra o caminho (t decrescendo de T0 até T1-360) e acumula comprimento
ts = np.linspace(T0, T1 - 360, 4000)
pts = np.array([P(t) for t in ts])
seg = np.hypot(*np.diff(pts, axis=0).T)
s = np.r_[0, np.cumsum(seg)]
L = s[-1]

TEXT = "BRASILEIRA MÚSICA"
SIZE = 68
font = ImageFont.truetype(FONT, SIZE)
TRACK = 3.0
dmy = ImageDraw.Draw(Image.new("L", (10, 10)))
widths = [dmy.textlength(c, font=font) + TRACK for c in TEXT]
total = sum(widths)
avail = L - S_B - 25
scale = min(1.0, avail / total)
widths = [w * scale for w in widths]
start = S_B + 8

YEL, PINK, INK = (238, 226, 122), (230, 121, 211), (18, 18, 18)
layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
pos = start
for c, w in zip(TEXT, widths):
    mid = pos + w / 2
    pos += w
    if c == " ":
        continue
    i = int(np.searchsorted(s, mid))
    i = min(max(i, 1), len(pts) - 2)
    x, y = pts[i]
    dx, dy = pts[i + 1] - pts[i - 1]
    rot = math.degrees(math.atan2(dy, dx))
    g_im = Image.new("RGBA", (220, 220), (0, 0, 0, 0))
    gd = ImageDraw.Draw(g_im)
    # deslocamento radial: centro da letra sobre a elipse
    gd.text((110, 110), c, font=font, fill=YEL + (255,), anchor="mm", stroke_width=7, stroke_fill=PINK + (255,))
    g_im = g_im.rotate(-rot, resample=Image.BICUBIC)
    layer.alpha_composite(g_im, (int(x - 110), int(y - 110)))

# sombra preta deslocada (como no original)
alpha = layer.split()[3]
shadow = Image.new("RGBA", (W, H), INK + (0,))
shadow.putalpha(alpha)
out = Image.fromarray(clean.astype(np.uint8)).convert("RGBA")
out.alpha_composite(shadow, (-6, 9))
out.alpha_composite(layer)
out.convert("RGB").save(OUT)
print("ok", OUT, "arco", round(L), "texto", round(total), "escala", round(scale, 3))
