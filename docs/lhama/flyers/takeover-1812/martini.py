"""Rodada 5 · taça de martini. A taça é a imagem central; o líquido e o brilho
são as texturas de retícula que o usuário mandou (recoloridas pra Lhama).
Saída: fundos 1080x1350 (texto entra no HTML).
Uso: python3 martini.py <pasta-rc> <saida> [escala=1]"""
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageChops, ImageFilter

RC, OUT = sys.argv[1], sys.argv[2]
S = float(sys.argv[3]) if len(sys.argv) > 3 else 1
os.makedirs(OUT, exist_ok=True)
W, H = int(1080 * S), int(1350 * S)
hx = lambda h: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
LAV, LAVD, PINK, YEL, MINT, CREAM, INK, WINE = map(hx, ["#6E78E8", "#4E57C2", "#E679D3", "#EEE27A", "#B6D4A6", "#F2EAD8", "#151515", "#82004E"])
agua = Image.open(os.path.join(RC, "rc-agua.png")).convert("RGB")
velas = Image.open(os.path.join(RC, "rc-velas.png")).convert("RGB")
velasm = Image.open(os.path.join(RC, "rc-velas-menta.png")).convert("RGB")


def P(x, y):
    return (x * S, y * S)


def tex(img, box, scale=1.0, rot=0):
    """Recorta a textura pra caber no retângulo `box` (cover)."""
    x0, y0, x1, y1 = [int(v * S) for v in box]
    w, h = x1 - x0, y1 - y0
    t = img.rotate(rot, resample=Image.BICUBIC, expand=True)
    k = max(w / t.width, h / t.height) * scale
    t = t.resize((int(t.width * k), int(t.height * k)), Image.LANCZOS)
    cx, cy = (t.width - w) // 2, (t.height - h) // 2
    return t.crop((cx, cy, cx + w, cy + h)), (x0, y0)


def mask(fn):
    m = Image.new("L", (W, H), 0)
    fn(ImageDraw.Draw(m))
    return m


def paper_grain(img, k=0.07, seed=1):
    a = np.asarray(img).astype(np.float32)
    n = np.random.default_rng(seed).standard_normal(a.shape[:2])[..., None]
    return Image.fromarray(np.clip(a * (1 + k * n), 0, 255).astype(np.uint8))


def halftone_flat(color, bg, density, angle=45, cell=7):
    """Campo chapado com retícula leve (pra fundos não ficarem digitais)."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a = math.radians(angle)
    u = (xx * math.cos(a) + yy * math.sin(a)) / (cell * S) * 2 * math.pi
    v = (-xx * math.sin(a) + yy * math.cos(a)) / (cell * S) * 2 * math.pi
    t = 0.5 - 0.25 * (np.cos(u) + np.cos(v))
    ink = np.clip((density - t) * 8 + 0.5, 0, 1)[..., None]
    out = np.array(bg, np.float32) * (1 - ink) + np.array(color, np.float32) * ink
    return Image.fromarray(out.astype(np.uint8))


def glass(d, cx, top, rim, depth, stem, foot, tilt=0, width=10, fill=None, outline=INK):
    """Taça de martini (cone + haste + pé). Retorna os polígonos."""
    def R(x, y):
        a = math.radians(tilt)
        x, y = x - cx, y - (top + depth)
        return P(cx + x * math.cos(a) - y * math.sin(a), top + depth + x * math.sin(a) + y * math.cos(a))
    cone = [R(cx - rim, top), R(cx + rim, top), R(cx + 14, top + depth), R(cx - 14, top + depth)]
    st = [R(cx - 9, top + depth - 4), R(cx + 9, top + depth - 4), R(cx + 9, top + depth + stem), R(cx - 9, top + depth + stem)]
    ft = [R(cx - foot, top + depth + stem + 14), R(cx + foot, top + depth + stem + 14), R(cx + foot * 0.7, top + depth + stem - 4), R(cx - foot * 0.7, top + depth + stem - 4)]
    return cone, st, ft, R


def liquid_poly(R, cx, top, rim, depth, level):
    """Líquido até `level` (0..1 da altura do cone), com superfície levemente curva."""
    y = top + depth * (1 - level)
    half = rim * level + 14 * (1 - level)
    pts = [R(cx - half + 6, y)]
    for i in range(1, 12):
        t = i / 12
        pts.append(R(cx - half + 6 + (2 * half - 12) * t, y + 8 * math.sin(t * math.pi)))
    pts += [R(cx + half - 6, y), R(cx + 12, top + depth - 6), R(cx - 12, top + depth - 6)]
    return pts


def draw_martini(base, cx, top, rim, depth, stem, foot, tilt, liq_tex, glow=None, olive=PINK, misreg=PINK, level=0.8, pick=True, lw=9, off_px=16):
    cone, st, ft, R = glass(None, cx, top, rim, depth, stem, foot, tilt)
    # sombra de registro (rosa deslocado) — erro de impressão
    off = Image.new("RGBA", (W, H), (0, 0, 0, 0)); do = ImageDraw.Draw(off)
    for poly in (cone, st, ft):
        do.polygon([(x + off_px * S, y + off_px * 0.9 * S) for x, y in poly], fill=misreg + (255,))
    base.alpha_composite(off)
    # vidro: creme translúcido
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dg = ImageDraw.Draw(g)
    for poly in (cone, st, ft):
        dg.polygon(poly, fill=CREAM + (235,))
    base.alpha_composite(g)
    # líquido = textura da água
    if level > 0:
        lm = mask(lambda d: d.polygon(liquid_poly(R, cx, top, rim, depth, level), fill=255))
        t, (x0, y0) = tex(liq_tex, (cx - rim - 40, top - 40, cx + rim + 40, top + depth + 40), 1.25, rot=-tilt)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); layer.paste(t, (x0, y0))
        layer.putalpha(ImageChops.multiply(layer.split()[3], lm))
        base.alpha_composite(layer)
    # contorno nanquim
    ln = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(ln)
    for poly in (cone, st, ft):
        dl.line(poly + [poly[0]], fill=INK + (255,), width=int(lw * S), joint="curve")
    if level > 0:
        dl.line(liquid_poly(R, cx, top, rim, depth, level)[:12], fill=INK + (255,), width=int(max(3, lw * 0.55) * S))
    # brilho no vidro
    hl = [R(cx - rim * 0.72, top + 30), R(cx - rim * 0.6, top + 30), R(cx - 30, top + depth * 0.78), R(cx - 44, top + depth * 0.78)]
    dl.polygon(hl, fill=(255, 255, 255, 150))
    base.alpha_composite(ln)
    if not pick:
        return R
    # palito com azeitona-lhama (rosa com miolo amarelo)
    p0, p1 = R(cx + rim * 0.15, top + depth * 0.62), R(cx + rim * 0.85, top - rim * 0.3)
    dp = ImageDraw.Draw(base)
    dp.line([p0, p1], fill=INK, width=int(10 * S))
    ox, oy = R(cx + rim * 0.42, top + depth * 0.05)
    r = max(22, rim * 0.165) * S
    dp.ellipse([ox - r + 12 * S, oy - r * 0.86 + 12 * S, ox + r + 12 * S, oy + r * 0.86 + 12 * S], fill=misreg)
    dp.ellipse([ox - r, oy - r * 0.86, ox + r, oy + r * 0.86], fill=olive, outline=INK, width=int(8 * S))
    dp.ellipse([ox - r * 0.36, oy - r * 0.3, ox + r * 0.36, oy + r * 0.3], fill=YEL, outline=INK, width=int(5 * S))
    return R


def save(img, name):
    paper_grain(img.convert("RGB")).save(os.path.join(OUT, name))
    print(name)


# 1 · a taça gigante, lavanda, brilho das velas atrás
b = halftone_flat(LAVD, LAV, 0.22).convert("RGBA")
t, (x0, y0) = tex(velas, (140, 260, 940, 1100), 1.0)
halo = Image.new("RGBA", (W, H), (0, 0, 0, 0)); halo.paste(t, (x0, y0))
hm = mask(lambda d: d.ellipse([P(260, 400), P(820, 1000)], fill=255)).filter(ImageFilter.GaussianBlur(70 * S))
halo.putalpha(hm); b.alpha_composite(halo)
draw_martini(b, 540, 420, 330, 330, 270, 190, 0, agua, level=0.82)
save(b, "m1.png")

# 2 · taça inclinada derramando, fundo tinta, com respingo de água
b = Image.new("RGBA", (W, H), INK + (255,))
t, (x0, y0) = tex(agua, (0, 700, 1080, 1350), 1.0, rot=90)
sp = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sp.paste(t, (x0, y0))
spm = mask(lambda d: (d.ellipse([P(-200, 930), P(1300, 1500)], fill=255), d.ellipse([P(380, 760), P(820, 1060)], fill=255)))
spm = spm.filter(ImageFilter.GaussianBlur(3 * S))
sp.putalpha(spm); b.alpha_composite(sp)
draw_martini(b, 560, 300, 300, 300, 250, 170, -28, agua, misreg=YEL, level=0.7)
save(b, "m2.png")

# 3 · tim-tim: duas taças, fundo rosa, líquido com as velas (brilho quente)
b = halftone_flat(WINE, PINK, 0.12, angle=15).convert("RGBA")
draw_martini(b, 360, 520, 230, 250, 240, 140, 14, velas, olive=YEL, misreg=WINE, level=0.85)
draw_martini(b, 720, 520, 230, 250, 240, 140, -14, velasm, olive=MINT, misreg=WINE, level=0.85)
dt = ImageDraw.Draw(b)
for x1, y1, x2, y2 in [(520, 420, 500, 350), (545, 410, 548, 330), (570, 420, 594, 352)]:
    dt.line([P(x1, y1), P(x2, y2)], fill=INK, width=int(11 * S))
save(b, "m3.png")


# ---------------------------------------------------------------- rodada 6 · a saideira
# S1 · uma taça só, quase no fim (a última dose), brilho das velas atrás
b = halftone_flat(LAVD, LAV, 0.22).convert("RGBA")
t, (x0, y0) = tex(velas, (140, 300, 940, 1140), 1.0)
halo = Image.new("RGBA", (W, H), (0, 0, 0, 0)); halo.paste(t, (x0, y0))
hm = mask(lambda d: d.ellipse([P(260, 440), P(820, 1040)], fill=255)).filter(ImageFilter.GaussianBlur(70 * S))
halo.putalpha(hm); b.alpha_composite(halo)
draw_martini(b, 540, 470, 320, 320, 250, 180, 0, agua, level=0.38)
save(b, "s1.png")

# S2 · tim-tim da saideira: duas taças, fundo rosa
b = halftone_flat(WINE, PINK, 0.12, angle=15).convert("RGBA")
draw_martini(b, 380, 470, 230, 250, 230, 140, 14, agua, olive=YEL, misreg=WINE, level=0.5)
draw_martini(b, 700, 470, 230, 250, 230, 140, -14, velas, olive=MINT, misreg=WINE, level=0.5)
dt = ImageDraw.Draw(b)
for x1, y1, x2, y2 in [(520, 380, 500, 310), (545, 370, 548, 290), (570, 380, 594, 312)]:
    dt.line([P(x1, y1), P(x2, y2)], fill=INK, width=int(11 * S))
save(b, "s2.png")

# S3 · doze taças = doze meses; onze vazias, a de dezembro cheia
b = Image.new("RGBA", (W, H), CREAM + (255,))
cols, rows = 4, 3
for i in range(12):
    cx = 165 + (i % cols) * 250; top = 330 + (i // cols) * 255
    full = i == 11
    draw_martini(b, cx, top, 88, 92, 82, 56, 0, velas if full else agua, olive=PINK, misreg=PINK if full else LAV,
                 level=0.85 if full else 0, pick=full, lw=6, off_px=8)
save(b, "s3.png")
