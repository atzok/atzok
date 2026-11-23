"""Rodada 8 · referências 08 (glow/borrão), 09 (duotone) e 10 (tipo em retícula + explosão de luz).
Fundo escuro, UMA tinta luminosa por peça, tipo como textura. Tudo renderizado aqui (sem HTML).
Uso: python3 noite.py <pasta-rc> <saida> [escala=1]"""
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

RC, OUT = sys.argv[1], sys.argv[2]
S = float(sys.argv[3]) if len(sys.argv) > 3 else 1
os.makedirs(OUT, exist_ok=True)
W, H = int(1080 * S), int(1350 * S)
HERE = os.path.dirname(os.path.abspath(__file__))
F_ADCA = os.path.join(HERE, "../../carrossel-onde-o-clube/Adca.ttf")
F_MONO = os.path.join(HERE, "../../carrossel-onde-o-clube/DMMono-Regular.ttf")
F_COND = os.path.join(HERE, "../fonts/BigShoulders-Bold.ttf")
hx = lambda h: np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32)
YEL, PINK, LAV, MINT, CREAM = hx("#EEE27A"), hx("#E679D3"), hx("#7E88F0"), hx("#B6D4A6"), hx("#F2EAD8")
NIGHT = hx("#17141C")
rng = np.random.default_rng(1812)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)


def font(path, size):
    return ImageFont.truetype(path, int(size * S))


def text_mask(lines, anchor="mm"):
    """lines: (texto, fonte, x, y, [tracking]) -> máscara L"""
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    for t, f, x, y, *rest in lines:
        tr = rest[0] if rest else 0
        if not tr:
            d.text((x * S, y * S), t, font=f, fill=255, anchor=anchor)
        else:
            tw = sum(d.textlength(c, font=f) for c in t) + tr * S * (len(t) - 1)
            cx = x * S - tw / 2
            for c in t:
                d.text((cx, y * S), c, font=f, fill=255, anchor="lm"); cx += d.textlength(c, font=f) + tr * S
    return np.asarray(m).astype(np.float32) / 255


def blur(a, r):
    return np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r * S))).astype(np.float32) / 255


def screen_dots(val, cell=9, angle=45):
    a = math.radians(angle)
    u = (xx * math.cos(a) + yy * math.sin(a)) / (cell * S) * 2 * math.pi
    v = (-xx * math.sin(a) + yy * math.cos(a)) / (cell * S) * 2 * math.pi
    t = 0.5 - 0.25 * (np.cos(u) + np.cos(v))
    return np.clip((val - t) * 9 + 0.5, 0, 1)


def stochastic(val, k=1.0, seed=3):
    """Pontilhado aleatório (spray) das bordas da luz, como a ref 10."""
    n = np.random.default_rng(seed).random(val.shape).astype(np.float32)
    return (n < np.clip(val * k, 0, 1)).astype(np.float32)


def paper(base, k=0.08):
    base = base * (1 + k * rng.standard_normal((H, W, 1)).astype(np.float32))
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))


def ink(base, a, col):
    return base * (1 - a[..., None]) + col * a[..., None]


def tag_mask(items, y, x0, f, pad=12, gap=14, h=52):
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m); x = x0 * S
    for t in items:
        tw = d.textlength(t, font=f)
        box = [x, y * S, x + tw + 2 * pad * S, (y + h) * S]
        d.rounded_rectangle(box, radius=8 * S, outline=255, width=int(3 * S))
        d.text((x + pad * S, (y + h / 2) * S), t, font=f, fill=255, anchor="lm")
        x = box[2] + gap * S
    return np.asarray(m).astype(np.float32) / 255


def plain(lines, anchor="la"):
    return text_mask(lines, anchor)


# ---------------------------------------------------------------- R1 · tipo em retícula + explosão de luz (ref 10)
def r1(col=YEL, name="n1"):
    base = np.ones((H, W, 3), np.float32) * NIGHT
    big = font(F_ADCA, 262)
    title = text_mask([("SAIDEIRA", big, 540, 175)])
    title_soft = blur(title, 5)
    t_dots = screen_dots(title_soft * 1.08, cell=15)
    # explosão de luz no centro, alongada na horizontal, borda em spray
    cx, cy = 540, 690
    r = np.sqrt(((xx / S - cx) / 1.0) ** 2 + ((yy / S - cy) / 0.55) ** 2)
    star = np.exp(-r / 330) * 1.15 + 0.7 * np.exp(-np.abs(yy / S - cy) / 40) * np.exp(-np.abs(xx / S - cx) / 700)
    ang = np.arctan2(yy / S - cy, xx / S - cx)
    star *= 0.8 + 0.35 * np.cos(ang * 8) ** 2
    burst = np.clip(star * 1.35, 0, 1)
    burst_ink = np.maximum(stochastic(burst ** 1.4, 1.15, 5), (burst > 0.82).astype(np.float32))
    bottom = text_mask([("LHAMA", font(F_ADCA, 230), 540, 1080), ("TAKEOVER", font(F_ADCA, 150), 540, 1245)])
    b_dots = screen_dots(blur(bottom, 5) * 1.08, cell=15)
    small = font(F_MONO, 24)
    tags = tag_mask(["18.12", "22H"], 322, 60, small)
    genre = plain([("A ÚLTIMA DO ANO", font(F_MONO, 24), 1020, 356)], "rm")
    live = tag_mask(["CARMEM BAR"], 880, 772, small) + plain([("RUA SILVA PINTO, 429", font(F_MONO, 22), 1020, 958)], "rm")
    arrow = Image.new("L", (W, H), 0); da = ImageDraw.Draw(arrow)
    da.polygon([(60 * S, 886 * S), (150 * S, 886 * S), (150 * S, 866 * S), (200 * S, 906 * S), (150 * S, 946 * S), (150 * S, 926 * S), (60 * S, 926 * S)], fill=255)
    arrow = np.asarray(arrow).astype(np.float32) / 255
    a = np.clip(t_dots + burst_ink + b_dots + tags + genre + live + arrow, 0, 1)
    base = ink(base, a, col)
    paper(base).save(os.path.join(OUT, name + ".png")); print(name)


# ---------------------------------------------------------------- R2 · glow e borrão de movimento (ref 08)
def r2(col=PINK, name="n2"):
    base = np.ones((H, W, 3), np.float32) * hx("#0E0B14")
    f1, f2 = font(F_ADCA, 170), font(F_COND, 175)
    lines = [("LHAMA", f1, 540, 330), ("TAKEOVER", f1, 540, 485), ("A SAIDEIRA", f2, 540, 650),
             ("18.12 · 22H", f2, 540, 810), ("CARMEM BAR", f2, 540, 970)]
    m = text_mask(lines)
    # eco horizontal (borrão de movimento) nas linhas 1 e 4, como a ref
    echo = np.zeros_like(m)
    band = ((np.abs(yy / S - 330) < 70) | (np.abs(yy / S - 810) < 75)).astype(np.float32)
    for dx, w in [(-560, .35), (-280, .5), (280, .5), (560, .35)]:
        sh = np.roll(m * band, int(dx * S), axis=1)
        sh = np.asarray(Image.fromarray((sh * 255).astype(np.uint8)).filter(ImageFilter.BoxBlur(int(10 * S)))).astype(np.float32) / 255
        echo = np.maximum(echo, sh * w)
    echo = blur(echo, 6)
    motion = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.BoxBlur(int(4 * S)))).astype(np.float32) / 255
    glow = blur(m, 22) * 1.3 + blur(m, 60) * 0.8
    lum = np.clip(motion * 0.95 + echo + glow * 0.5, 0, 1.4)
    # linhas de varredura
    scan = 0.85 + 0.15 * (np.sin(yy / S * math.pi / 3) > 0)
    lum *= scan
    # barra de "código" no topo (como o bloco listrado da ref)
    bars = ((np.abs(xx / S - 540) < 190) & (np.abs(yy / S - 140) < 50) & ((yy / S).astype(int) % 9 < 5)).astype(np.float32)
    lum = np.clip(lum + blur(bars, 2) * 0.9, 0, 1.4)
    small = plain([("RUA SILVA PINTO, 429 · BOM RETIRO", font(F_MONO, 22), 540, 1120), ("LHAMA BOOKINGS · A ÚLTIMA DO ANO", font(F_MONO, 22), 540, 1230)], "mm")
    lum = np.clip(lum + blur(small, 1.2) * 0.85, 0, 1.4)
    out = base + (col[None, None] - base * 0.3) * np.clip(lum, 0, 1)[..., None] + 255 * np.clip(lum - 1, 0, 0.4)[..., None]
    paper(out, 0.1).save(os.path.join(OUT, name + ".png")); print(name)


# ---------------------------------------------------------------- R3 · duotone da textura em moldura (ref 09)
def r3(name="n3"):
    base = np.ones((H, W, 3), np.float32) * hx("#120F18")
    tex = Image.open(os.path.join(RC, "../../../../../home/user/atzok/docs/lhama/referencias/07-halftone-velas.jpg") if False else os.path.join(HERE, "../../referencias/07-halftone-velas.jpg")).convert("L")
    tex = np.asarray(tex.resize((int(860 * S), int(1290 * S)))).astype(np.float32) / 255
    fx, fy, fw, fh = 110, 300, 860, 760
    crop = tex[int(260 * S):int((260 + fh) * S), :int(fw * S)]
    lo, hi = hx("#2A1F55"), LAV
    duo = lo + (hi - lo) * crop[..., None] ** 0.8
    gmask = np.clip((crop - 0.62) * 4, 0, 1)
    duo = duo * (1 - gmask[..., None]) + MINT * gmask[..., None]
    base[int(fy * S):int((fy + fh) * S), int(fx * S):int((fx + fw) * S)] = duo
    title = text_mask([("SAIDEIRA", font(F_ADCA, 210), 540, 170)], "mm")
    base = ink(base, np.clip(title, 0, 1), LAV)
    # "globo" com o nome, como o logo da ref
    g = Image.new("L", (W, H), 0); dg = ImageDraw.Draw(g)
    for k in range(3):
        dg.ellipse([300 * S, (1105 + k * 20) * S, 780 * S, (1235 - k * 20) * S], outline=255, width=int(3 * S))
    dg.ellipse([440 * S, 1095 * S, 640 * S, 1245 * S], outline=255, width=int(3 * S))
    dg.rectangle([318 * S, 1146 * S, 762 * S, 1194 * S], fill=0)
    dg.text((540 * S, 1170 * S), "LHAMA TAKEOVER", font=font(F_ADCA, 46), fill=255, anchor="mm")
    g = np.asarray(g).astype(np.float32) / 255
    info = plain([("18.12 · 22H", font(F_ADCA, 44), 64, 1290), ("CARMEM BAR", font(F_MONO, 22), 64, 1150), ("SILVA PINTO, 429", font(F_MONO, 22), 64, 1185)], "lm")
    code = plain([("LT-1812", font(F_MONO, 22), 1016, 1290)], "rm")
    bar = np.zeros((H, W), np.float32)
    for i, w in enumerate([3, 1, 2, 1, 3, 1, 1, 2, 3, 1, 2, 1, 3, 2, 1, 1, 3, 1, 2]):
        x = 860 + sum([3, 1, 2, 1, 3, 1, 1, 2, 3, 1, 2, 1, 3, 2, 1, 1, 3, 1, 2][:i]) * 6
        bar[int(1130 * S):int(1240 * S), int(x * S):int((x + w * 4) * S)] = 1
    base = ink(base, np.clip(g + info + code + bar, 0, 1), LAV)
    paper(base, 0.1).save(os.path.join(OUT, name + ".png")); print(name)


r1(); r2(); r3()
