"""Adesivo 'Música Psicodélica Brasileira', versão final (v2).
- @lhamabookings na posição da opção A (braço esquerdo) com as cores da opção B (pílula rosa, letra creme).
- Contorno refeito em vetor: a borda da arte é suavizada como curva, a borda branca e a faca
  são offsets geométricos dessa curva (cantos redondos), e a faca vai pro PDF como caminho vetorial
  em cor especial 'CutContour'. Nada de borda serrilhada vinda do raster.
- Render final em escala alta (UP) com supersampling nas bordas.
Uso: python3 build_print_v2.py <arte-corrigida.png> <saida-dir> [largura_cm=9] [UP=4]"""
import sys, os, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter1d
from shapely.geometry import Polygon
from reportlab.pdfgen import canvas
from reportlab.lib.colors import CMYKColorSep
from reportlab.lib.utils import ImageReader

SRC, OUT = sys.argv[1], sys.argv[2]
WCM = float(sys.argv[3]) if len(sys.argv) > 3 else 9.0
UP = int(sys.argv[4]) if len(sys.argv) > 4 else 4
HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "../../carrossel-onde-o-clube/Adca.ttf")
os.makedirs(OUT, exist_ok=True)

OFF = 0              # a máscara já está nas coordenadas da arte expandida
BORDER = 24          # borda branca entre arte e faca (px da arte base)
BLEED = 26           # sangria branca além da faca
SMOOTH = 22          # suavização da borda da arte (px base)
RIM = 20             # faixa amarela uniforme na borda da arte (px base)
SS = 2               # supersampling das máscaras
PILL_X, PILL_Y, PILL_R = 700, 872, -2

art_full = Image.open(SRC).convert("RGB")
reg0 = np.load(sys.argv[5] if len(sys.argv) > 5 else os.path.join(HERE, "forma-full.npy")).astype(np.uint8)
# letras do anel que escapam da faixa entram inteiras na forma (com sombra)
_a = np.asarray(art_full.crop((OFF, 0, OFF + reg0.shape[1], reg0.shape[0]))).astype(int)
_pk = ((_a[..., 0] > 195) & (_a[..., 2] > 140) & (_a[..., 1] < 175)).astype(np.uint8)
_near = cv2.dilate(reg0, np.ones((3, 3), np.uint8), iterations=70)
_txt = cv2.dilate(_pk & _near, np.ones((3, 3), np.uint8), iterations=7)
_txt = cv2.morphologyEx(_txt, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41)))
reg0 = np.maximum(reg0, _txt)

# ---------------------------------------------------------------- curvas
cs, _ = cv2.findContours(reg0, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
c = max(cs, key=cv2.contourArea)[:, 0, :].astype(float)
# reamostra com passo uniforme e suaviza como curva fechada
seg = np.hypot(*np.diff(np.vstack([c, c[:1]]), axis=0).T)
s = np.r_[0, np.cumsum(seg)]
n = int(s[-1] / 1.5)
su = np.linspace(0, s[-1], n, endpoint=False)
x = np.interp(su, s, np.r_[c[:, 0], c[0, 0]]); y = np.interp(su, s, np.r_[c[:, 1], c[0, 1]])
x = gaussian_filter1d(x, SMOOTH / 1.5, mode="wrap"); y = gaussian_filter1d(y, SMOOTH / 1.5, mode="wrap")
art_poly = Polygon(np.c_[x, y]).buffer(0)
cut_poly = art_poly.buffer(BORDER + 30, quad_segs=48, join_style="round").buffer(-30, quad_segs=48, join_style="round")
bleed_poly = cut_poly.buffer(BLEED, quad_segs=32, join_style="round")
minx, miny, maxx, maxy = bleed_poly.bounds
minx, miny = math.floor(minx), math.floor(miny)
Wb, Hb = math.ceil(maxx) - minx, math.ceil(maxy) - miny
Wf, Hf = Wb * UP, Hb * UP


def poly_mask(poly, scale=UP, ss=SS):
    m = Image.new("L", (Wf * ss, Hf * ss), 0)
    d = ImageDraw.Draw(m)
    pts = [((px - minx) * scale * ss, (py - miny) * scale * ss) for px, py in np.asarray(poly.exterior.coords)]
    d.polygon(pts, fill=255)
    return m.resize((Wf, Hf), Image.LANCZOS)


# ---------------------------------------------------------------- arte em alta
src = art_full.crop((OFF + minx, miny, OFF + minx + Wb, miny + Hb))   # fora da imagem = preto, mas cai fora da máscara
art = src.resize((Wf, Hf), Image.LANCZOS)
# leve nitidez pra compensar a ampliação
art = Image.fromarray(np.clip(cv2.addWeighted(np.asarray(art, np.float32), 1.35,
                                              cv2.GaussianBlur(np.asarray(art, np.float32), (0, 0), 1.2 * UP), -0.35, 0), 0, 255).astype(np.uint8))

# ---------------------------------------------------------------- pílula @lhamabookings (vetor, desenhada já em alta)
PINK, CREAM, INK, LAVD = (230, 121, 211), (242, 234, 216), (21, 21, 21), (78, 87, 194)
HANDLE = "@LHAMABOOKINGS"


def pill_layer(cx, cy, size, rot):
    S = UP * SS
    f = ImageFont.truetype(FONT, int(size * S))
    w, h = int(900 * S), int(220 * S)
    tmp = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(tmp)
    tw = d.textlength(HANDLE, font=f); ph = size * 1.62 * S
    x0, x1 = w / 2 - tw / 2 - size * 0.62 * S, w / 2 + tw / 2 + size * 0.62 * S
    y0, y1 = h / 2 - ph / 2, h / 2 + ph / 2
    d.rounded_rectangle([x0 + 5 * S, y0 + 7 * S, x1 + 5 * S, y1 + 7 * S], radius=ph / 2, fill=LAVD + (255,))
    d.rounded_rectangle([x0, y0, x1, y1], radius=ph / 2, fill=PINK + (255,), outline=INK + (255,), width=int(4 * S))
    d.text((w / 2, h / 2 + 2 * S), HANDLE, font=f, fill=CREAM, anchor="mm", stroke_width=int(3 * S), stroke_fill=INK)
    tmp = tmp.rotate(rot, expand=True, resample=Image.BICUBIC)
    tmp = tmp.resize((tmp.width // SS, tmp.height // SS), Image.LANCZOS)
    lay = Image.new("RGBA", (Wf, Hf), (0, 0, 0, 0))
    lay.alpha_composite(tmp, (int((cx - minx) * UP - tmp.width / 2), int((cy - miny) * UP - tmp.height / 2)))
    return lay


pill = pill_layer(PILL_X, PILL_Y, 34, PILL_R)   # braço esquerdo (posição A), cores da opção B

# ---------------------------------------------------------------- composição
final = Image.new("RGBA", (Wf, Hf), (0, 0, 0, 0))
final.paste((255, 255, 255, 255), (0, 0), poly_mask(bleed_poly))
art_rgba = art.convert("RGBA")
final.paste(art_rgba, (0, 0), poly_mask(art_poly))
# faixa amarela de espessura constante na borda: acabamento limpo, sem "dentes" da arte
arr = np.asarray(art).astype(np.float32)
hsv_y = (arr[..., 0] > 200) & (arr[..., 1] > 195) & (arr[..., 2] < 175)
yel = np.median(arr[hsv_y], axis=0) if hsv_y.any() else np.array([233, 226, 128], np.float32)
noise = np.random.default_rng(7).standard_normal((Hf // UP + 1, Wf // UP + 1)).astype(np.float32)
noise = cv2.resize(noise, (Wf, Hf), interpolation=cv2.INTER_CUBIC)[..., None]
rim_rgb = np.clip(yel[None, None, :] * (1 + 0.045 * noise), 0, 255).astype(np.uint8)
# o texto do anel (rosa + sombra preta) fica por cima da faixa
pinkm = (arr[..., 0] > 195) & (arr[..., 2] > 140) & (arr[..., 1] < 175)
darkm = arr.sum(-1) < 210
textm = cv2.dilate(pinkm.astype(np.uint8), np.ones((3, 3), np.uint8), iterations=UP) > 0
textm = textm | (darkm & (cv2.dilate(pinkm.astype(np.uint8), np.ones((3, 3), np.uint8), iterations=3 * UP) > 0))
textm = cv2.GaussianBlur(textm.astype(np.float32), (0, 0), 0.8 * UP)
ring = art_poly.difference(art_poly.buffer(-RIM, quad_segs=32, join_style="round"))
rm = Image.new("L", (Wf * SS, Hf * SS), 0); dr = ImageDraw.Draw(rm)
for g in getattr(ring, "geoms", [ring]):
    dr.polygon([((px - minx) * UP * SS, (py - miny) * UP * SS) for px, py in np.asarray(g.exterior.coords)], fill=255)
    for hole in g.interiors:
        dr.polygon([((px - minx) * UP * SS, (py - miny) * UP * SS) for px, py in np.asarray(hole.coords)], fill=0)
rm = rm.resize((Wf, Hf), Image.LANCZOS)
rm = Image.fromarray((np.asarray(rm, np.float32) * (1 - np.clip(textm, 0, 1))).astype(np.uint8))
final.paste(Image.fromarray(rim_rgb).convert("RGBA"), (0, 0), rm)
final.alpha_composite(pill)   # pílula por cima da faixa
dpi = Wf / (WCM / 2.54)
final.save(os.path.join(OUT, "adesivo-mpb_arte.png"), dpi=(dpi, dpi))

# ---------------------------------------------------------------- PDF com faca vetorial
pw = WCM / 2.54 * 72; ph = pw * Hf / Wf; k = pw / Wb      # pt por px base
pdf = canvas.Canvas(os.path.join(OUT, "adesivo-mpb_grafica.pdf"), pagesize=(pw, ph))
pdf.setTitle("Adesivo Lhama Bookings - Musica Psicodelica Brasileira")
pdf.setAuthor("Lhama Bookings")
pdf.drawImage(ImageReader(final), 0, 0, width=pw, height=ph, mask="auto")
pdf.setStrokeColor(CMYKColorSep(0, 1, 0, 0, spotName="CutContour", density=1))
pdf.setLineWidth(0.25)
pts = np.asarray(cut_poly.exterior.coords)
p = pdf.beginPath()
p.moveTo((pts[0][0] - minx) * k, ph - (pts[0][1] - miny) * k)
for px, py in pts[1:]:
    p.lineTo((px - minx) * k, ph - (py - miny) * k)
p.close()
pdf.drawPath(p, stroke=1, fill=0)
pdf.showPage(); pdf.save()

d = "M" + " L".join(f"{(px - minx) * k:.3f} {(py - miny) * k:.3f}" for px, py in pts) + " Z"
open(os.path.join(OUT, "adesivo-mpb_faca.svg"), "w").write(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{pw / 72 * 25.4:.2f}mm" height="{ph / 72 * 25.4:.2f}mm" viewBox="0 0 {pw:.3f} {ph:.3f}">'
    f'<path d="{d}" fill="none" stroke="#EC008C" stroke-width="0.25"/></svg>')
print(f"{Wf}x{Hf}px  {WCM:.1f}x{WCM * Hf / Wf:.1f} cm  {dpi:.0f} dpi  faca: {len(pts)} pontos")
