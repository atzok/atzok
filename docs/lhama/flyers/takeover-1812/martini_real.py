"""Rodada 10 · variações da opção amarela (retícula + explosão de luz) com uma taça
de martini realista: vidro com fresnel nas bordas, reflexos, líquido com menisco,
azeitona com pimentão e palito. A taça é renderizada em tons de cinza e depois
impressa em retícula, junto com o resto do cartaz.
Uso: python3 martini_real.py <saida> [escala=1]"""
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = sys.argv[1]
S = float(sys.argv[2]) if len(sys.argv) > 2 else 1
os.makedirs(OUT, exist_ok=True)
W, H = int(1080 * S), int(1350 * S)
HERE = os.path.dirname(os.path.abspath(__file__))
F_ADCA = os.path.join(HERE, "../../carrossel-onde-o-clube/Adca.ttf")
F_MONO = os.path.join(HERE, "../../carrossel-onde-o-clube/DMMono-Regular.ttf")
hx = lambda h: np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32)
YEL, PINK, NIGHT = hx("#EEE27A"), hx("#E679D3"), hx("#17141C")
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
X, Y = xx / S, yy / S  # coordenadas no espaço 1080x1350


def font(p, s):
    return ImageFont.truetype(p, int(s * S))


def blur(a, r):
    return np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r * S))).astype(np.float32) / 255


def sstep(e0, e1, v):
    t = np.clip((v - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def screen(val, cell=9, angle=45):
    a = math.radians(angle)
    u = (xx * math.cos(a) + yy * math.sin(a)) / (cell * S) * 2 * math.pi
    v = (-xx * math.sin(a) + yy * math.cos(a)) / (cell * S) * 2 * math.pi
    t = 0.5 - 0.25 * (np.cos(u) + np.cos(v))
    return np.clip((val - t) * 9 + 0.5, 0, 1)


def spray(val, seed=5):
    n = np.random.default_rng(seed).random(val.shape).astype(np.float32)
    return (n < np.clip(val, 0, 1)).astype(np.float32)


def text(lines, anchor="mm"):
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    for t, f, x, y in lines:
        d.text((x * S, y * S), t, font=f, fill=255, anchor=anchor)
    return np.asarray(m).astype(np.float32) / 255


def tags(items, x0, y, f, pad=12, gap=14, h=52):
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m); x = x0 * S
    for t in items:
        tw = d.textlength(t, font=f)
        box = [x, y * S, x + tw + 2 * pad * S, (y + h) * S]
        d.rounded_rectangle(box, radius=8 * S, outline=255, width=int(3 * S))
        d.text((x + pad * S, (y + h / 2) * S), t, font=f, fill=255, anchor="lm")
        x = box[2] + gap * S
    return np.asarray(m).astype(np.float32) / 255


def burst(cx, cy, k=1.0):
    r = np.sqrt((X - cx) ** 2 + ((Y - cy) / 0.55) ** 2)
    st = np.exp(-r / 330) * 1.15 + 0.7 * np.exp(-np.abs(Y - cy) / 40) * np.exp(-np.abs(X - cx) / 700)
    ang = np.arctan2(Y - cy, X - cx)
    st *= 0.8 + 0.35 * np.cos(ang * 8) ** 2
    b = np.clip(st * 1.35 * k, 0, 1)
    return np.maximum(spray(b ** 1.4 * 1.15), (b > 0.82).astype(np.float32))


def glass(cx, top, rim, depth, stem, foot, level=0.72, tilt=0.0):
    """Devolve (luminância 0..1, alfa 0..1) de uma taça de martini realista."""
    ca, sa = math.cos(tilt), math.sin(tilt)
    pivot_y = top + depth
    lx = (X - cx) * ca + (Y - pivot_y) * sa + cx          # coordenadas locais (taça "em pé")
    ly = -(X - cx) * sa + (Y - pivot_y) * ca + pivot_y
    L = np.zeros_like(X); A = np.zeros_like(X)
    ery = rim * 0.13                                       # elipse da boca
    # ---- taça (cone)
    t = (ly - top) / depth
    half = rim * (1 - t) + 9 * t
    inside = (t >= 0) & (t <= 1) & (np.abs(lx - cx) <= half)
    rim_ell = ((lx - cx) / rim) ** 2 + ((ly - top) / ery) ** 2 <= 1
    bowl = inside | rim_ell
    u = np.clip((lx - cx) / np.maximum(half, 1), -1, 1)
    fres = sstep(0.72, 1.0, np.abs(u))                     # bordas claras (vidro)
    spec1 = np.exp(-((u + 0.58) / 0.07) ** 2) * sstep(0.02, 0.2, t) * (1 - sstep(0.75, 0.95, t))
    spec2 = np.exp(-((u - 0.45) / 0.04) ** 2) * 0.55 * sstep(0.1, 0.3, t) * (1 - sstep(0.6, 0.8, t))
    gl = 0.10 + 0.55 * fres + 0.95 * spec1 + spec2
    # líquido
    yl = top + depth * (1 - level)
    hl = rim * level + 9 * (1 - level)
    surf = ((lx - cx) / hl) ** 2 + ((ly - yl) / (hl * 0.13)) ** 2
    liq = inside & ((ly > yl) | (surf <= 1))
    liq_l = 0.30 + 0.22 * (1 - u ** 2) + 0.12 * np.sin(u * 9 + t * 6) * 0.5
    liq_l += 0.35 * np.exp(-((u + 0.4) / 0.18) ** 2) * sstep(0.3, 0.7, t)   # cáustica
    meniscus = np.exp(-((np.sqrt(np.maximum(surf, 0)) - 1) / 0.05) ** 2) * (np.abs(ly - yl) < hl * 0.2)
    top_surf = (surf <= 1) * (0.55 + 0.3 * (lx - cx) / hl)
    lum = np.where(liq, np.maximum(liq_l, top_surf), gl)
    lum = np.maximum(lum, meniscus * 0.95)
    # boca: linha de luz da frente e de trás
    rd = np.sqrt(((lx - cx) / rim) ** 2 + ((ly - top) / ery) ** 2)
    rimline = np.exp(-((rd - 1) / 0.018) ** 2) * (0.55 + 0.45 * (ly > top))
    L = np.where(bowl, lum, 0); A = bowl.astype(np.float32)
    L = np.maximum(L, rimline); A = np.maximum(A, rimline)
    # ---- haste
    sw = 9 + 5 * sstep(0.85, 1.0, (ly - pivot_y) / stem)
    sx = (lx - cx) / sw
    st = (np.abs(sx) <= 1) & (ly >= pivot_y - 4) & (ly <= pivot_y + stem)
    st_l = 0.18 + 0.6 * np.exp(-((sx + 0.4) / 0.25) ** 2) + 0.4 * sstep(0.7, 1, np.abs(sx))
    L = np.where(st, st_l, L); A = np.maximum(A, st.astype(np.float32))
    # ---- pé
    fy = pivot_y + stem + 10
    fd = ((lx - cx) / foot) ** 2 + ((ly - fy) / (foot * 0.17)) ** 2
    ft = fd <= 1
    ft_l = 0.2 + 0.55 * sstep(0.75, 1, fd) + 0.5 * np.exp(-((lx - cx + foot * 0.45) / (foot * 0.12)) ** 2) * (ly < fy)
    L = np.where(ft, ft_l, L); A = np.maximum(A, ft.astype(np.float32))
    # ---- azeitona com pimentão + palito
    ox, oy, orr = cx + rim * 0.12, yl + depth * 0.26, rim * 0.15
    od = ((lx - ox) / orr) ** 2 + ((ly - oy) / (orr * 0.88)) ** 2
    ol = od <= 1
    nz = np.sqrt(np.clip(1 - od, 0, 1))
    shade = np.clip(0.25 + 0.6 * (-(lx - ox) / orr * 0.5 - (ly - oy) / orr * 0.6 + nz * 0.6), 0, 1)
    spec = np.exp(-(((lx - ox + orr * 0.35) ** 2 + (ly - oy + orr * 0.4) ** 2) / (orr * 0.16) ** 2))
    pim = ((lx - ox - orr * 0.15) / (orr * 0.34)) ** 2 + ((ly - oy + orr * 0.05) / (orr * 0.3)) ** 2 <= 1
    olive_l = np.where(pim, 0.12, 0.15 + shade * 0.85 + spec)
    olive_l = olive_l * 0.92
    L = np.where(ol, olive_l, L)
    # palito: da azeitona até acima da boca, com brilho
    px0, py0, px1, py1 = ox - orr * 0.9, oy + orr * 0.5, cx + rim * 0.8, top - rim * 0.45
    vx, vy = px1 - px0, py1 - py0; ln = math.hypot(vx, vy)
    tt = np.clip(((lx - px0) * vx + (ly - py0) * vy) / ln ** 2, 0, 1)
    dd = np.hypot(lx - (px0 + tt * vx), ly - (py0 + tt * vy))
    pick = (dd < 6) & ~(ol & (tt > 0.05) & (tt < 0.3))
    pick_l = 0.35 + 0.6 * np.exp(-((dd - 1) / 2.2) ** 2)
    L = np.where(pick, np.where(liq & pick, pick_l * 0.7, pick_l), L); A = np.maximum(A, pick.astype(np.float32))
    return np.clip(L, 0, 1), np.clip(A, 0, 1)


def compose(name, glass_kw, layout, burst_c=(540, 600), cell=8, col=YEL, col2=None):
    base = np.ones((H, W, 3), np.float32) * NIGHT
    gL, gA = glass(**glass_kw)
    gA_s = blur(gA, 1.5)
    # a explosão fica atrás e "contorna" a taça com um halo
    b = burst(*burst_c) * (1 - blur(gA, 6))
    glass_ink = screen(blur(gL, 0.6) * 1.05, cell=cell) * gA_s
    halo = spray(blur(gA, 18) * 0.6 * (1 - gA), seed=9)
    ink = np.clip(b + glass_ink + halo, 0, 1)
    ink = np.clip(ink + layout, 0, 1)
    out = base * (1 - ink[..., None]) + col * ink[..., None]
    if col2 is not None:  # segunda tinta: rosa só no líquido, deslocada (registro)
        liq = screen(blur(gL * gA, 1) * 0.6, cell=cell, angle=15) * gA_s
        liq = np.roll(np.roll(liq, int(5 * S), 1), int(4 * S), 0)
        out = out * (1 - liq[..., None] * 0.85) + col2 * liq[..., None] * 0.85
    out *= (1 + 0.07 * np.random.default_rng(1).standard_normal((H, W, 1)).astype(np.float32))
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(os.path.join(OUT, name + ".png"))
    print(name)


big = lambda s: font(F_ADCA, s)
mono = font(F_MONO, 24)


def halftone_title(lines, cell=15):
    return screen(blur(text(lines), 5) * 1.08, cell=cell)


# V1 · taça grande, frontal, explosão atrás (evolução direta da opção 1)
lay1 = halftone_title([("LHAMA", big(300), 540, 175), ("TAKEOVER", big(196), 540, 1205)]) \
    + tags(["18.12", "22H"], 60, 322, mono) + text([("A ÚLTIMA DO ANO", font(F_MONO, 24), 1020, 348)], "rm") \
    + tags(["CARMEM BAR"], 60, 960, mono) + text([("RUA SILVA PINTO, 429", font(F_MONO, 22), 1020, 986)], "rm")
compose("t1", dict(cx=540, top=440, rim=270, depth=290, stem=210, foot=150), lay1, burst_c=(540, 560))

# V2 · close na taça inclinada, cortada pela borda, tipo empilhado à esquerda
lay2 = halftone_title([("LHAMA", big(210), 40, 120), ("TAKE", big(210), 40, 300), ("OVER", big(210), 40, 480)], cell=13) * 0
lay2 = screen(blur(text([("LHAMA", big(200), 52, 150), ("TAKE", big(200), 52, 330), ("OVER", big(200), 52, 510)], "lm"), 5) * 1.08, cell=13) \
    + tags(["18.12", "22H", "CARMEM BAR"], 60, 1150, mono) + text([("RUA SILVA PINTO, 429 · BOM RETIRO", font(F_MONO, 22), 60, 1250), ("A ÚLTIMA DO ANO", font(F_MONO, 22), 1020, 1250)], "lm") * 1
lay2 = np.clip(lay2 - text([("A ÚLTIMA DO ANO", font(F_MONO, 22), 1020, 1250)], "lm") + text([("A ÚLTIMA DO ANO", font(F_MONO, 22), 1020, 1250)], "rm"), 0, 1)
compose("t2", dict(cx=760, top=560, rim=330, depth=350, stem=260, foot=170, tilt=-0.32, level=0.6), lay2, burst_c=(760, 700))

# V3 · duas tintas: amarelo + rosa só no líquido, taça centrada menor, mais respiro
lay3 = halftone_title([("LHAMA TAKEOVER", big(120), 540, 140)], cell=11) \
    + text([("18.12 · 22H", big(110), 540, 1110)]) \
    + text([("CARMEM BAR · RUA SILVA PINTO, 429 · BOM RETIRO", font(F_MONO, 22), 540, 1200), ("A ÚLTIMA DO ANO", font(F_MONO, 22), 540, 1250)])
compose("t3", dict(cx=540, top=360, rim=250, depth=270, stem=210, foot=140), lay3, burst_c=(540, 480), col2=PINK)
