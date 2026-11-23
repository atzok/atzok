"""Formas da Lhama: gera 30 formas + variações de cor vetoriais fiéis às referências
(topográficas, linhas menta, minhocas 3D, manchas com anéis, rabiscos, pílulas)
e exporta SVG. O render em PNG transparente fica em render_formas.js.

Uso: python3 gen_formas.py  -> svg/NN-nome.svg
"""
import math, os, random
from shapely.geometry import LineString, MultiLineString, Polygon, MultiPolygon, Point, box
from shapely.ops import unary_union
from shapely import affinity

OUT = os.path.join(os.path.dirname(__file__), "svg")
os.makedirs(OUT, exist_ok=True)

# cores tiradas das artes da Lhama (pixels das referências)
LAV = "#8A94E6"      # banda lavanda das topográficas
LAVW = "#6E78E8"     # corpo da minhoca / lavanda forte
LAVD = "#5A63CF"     # contorno fino lavanda escuro
MINT = "#B6D4A6"
YEL = "#EEE27A"
YELP = "#E7E2A6"     # amarelo pálido (linhas finas)
PINK = "#E679D3"
LILAC = "#C3A6E6"
CREAM = "#F2EAD8"
INK = "#2B2F6B"
WINE = "#82004E"     # vinho do "Bad Lhama"
WINED = "#4E0030"
VIOLET = "#B478B8"   # violeta do "Badroom"
GRAPH = "#3E3B45"    # grafite do "Badroom"

# paletas: banda, linha 1, banda, linha 2, centro
TOPO_PAL = {
    "lavanda": (LAV, MINT, LAV, YELP, YEL),
    "rosa": (PINK, MINT, PINK, YEL, YEL),
    "menta": (MINT, LAVW, MINT, YEL, PINK),
    "amarelo": (YEL, LAVW, YEL, PINK, LAVW),
    "vinho": (WINE, PINK, WINE, LILAC, PINK),
    "violeta": (VIOLET, PINK, VIOLET, MINT, YEL),
    "grafite": (GRAPH, MINT, GRAPH, YEL, PINK),
}
# minhoca: corpo, fio, contorno, camadas (de baixo pra cima)
WORM_PAL = {
    "lavanda": (LAVW, YEL, LAVD, (LILAC, PINK, YEL)),
    "rosa": (PINK, YEL, "#B04A9C", (LAVW, LILAC, MINT)),
    "menta": (MINT, YEL, LAVD, (LAVW, PINK, YEL)),
    "amarelo": (YEL, PINK, LAVD, (LAVW, LILAC, MINT)),
    "vinho": (WINE, PINK, WINED, (PINK, LILAC, LAV)),
}
# linhas soltas: linha grossa, linha fina
LINE_PAL = {
    "menta": (MINT, YELP), "rosa": (PINK, YEL), "lavanda": (LAVW, PINK),
    "amarelo": (YEL, CREAM), "vinho": (WINE, PINK),
}
OVR = None  # quando definido, troca a paleta de todas as funções (variações de cor)

# ---------------------------------------------------------------- geometria


def catmull(pts, n=24, closed=False):
    """Curva suave passando pelos pontos de controle."""
    P = list(pts)
    if closed:
        P = P[-1:] + P + P[:2]
    else:
        P = [P[0]] + P + [P[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    out.append(P[-2])
    return out


def wobble_ring(coords, amp, seed, waves=((420, 1.0), (170, 0.45), (48, 0.12), (17, 0.06))):
    """Desloca o contorno ao longo da normal: ondulações largas e suaves
    + um tremor fino de traço feito à mão. Comprimentos de onda em unidades."""
    rnd = random.Random(seed)
    ph = [rnd.uniform(0, 6.28) for _ in waves]
    pts = list(coords)[:-1]
    n = len(pts)
    if n < 3:
        return coords
    acc = [0.0]
    for i in range(1, n):
        acc.append(acc[-1] + math.dist(pts[i - 1], pts[i]))
    L = acc[-1] + math.dist(pts[-1], pts[0])
    res = []
    for i, (x, y) in enumerate(pts):
        a, b = pts[i - 1], pts[(i + 1) % n]
        tx, ty = b[0] - a[0], b[1] - a[1]
        tl = math.hypot(tx, ty) or 1
        nx, ny = -ty / tl, tx / tl
        d = 0.0
        for j, (lam, w) in enumerate(waves):
            k = max(1, round(L / lam))  # inteiro: o anel fecha sem emenda
            d += amp * w * math.sin(2 * math.pi * k * acc[i] / L + ph[j])
        res.append((x + nx * d, y + ny * d))
    res.append(res[0])
    return res


FINE = ((52, 0.55), (19, 0.3))  # só o tremor do traço, sem ondular o anel


def wobble(geom, amp, seed, waves=None):
    if geom.is_empty:
        return geom
    polys = [geom] if isinstance(geom, Polygon) else list(getattr(geom, "geoms", []))
    out = []
    for k, p in enumerate(polys):
        if not isinstance(p, Polygon):
            continue
        kw = {} if waves is None else {"waves": waves}
        ext = wobble_ring(p.exterior.coords, amp, seed + k, **kw)
        holes = [wobble_ring(h.coords, amp, seed + 100 + k + j, **kw) for j, h in enumerate(p.interiors)]
        q = Polygon(ext, holes).buffer(0)
        out.append(q)
    return unary_union(out)


def dens(geom, step=4):
    """Densifica para o ruído ter pontos suficientes."""
    return geom.segmentize(step)


def path_d(geom):
    """Polígono(s) shapely -> atributo d de SVG (evenodd)."""
    polys = [geom] if isinstance(geom, Polygon) else [g for g in getattr(geom, "geoms", []) if isinstance(g, Polygon)]
    parts = []
    for p in polys:
        for ring in [p.exterior] + list(p.interiors):
            c = list(ring.coords)
            parts.append("M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in c) + "Z")
    return " ".join(parts)


class SVG:
    def __init__(self, w, h):
        self.w, self.h, self.items = w, h, []

    def poly(self, geom, fill, opacity=1, extra=""):
        if geom.is_empty:
            return
        self.items.append(f'<path d="{path_d(geom)}" fill="{fill}" fill-rule="evenodd" opacity="{opacity}" {extra}/>')

    def raw(self, s):
        self.items.append(s)

    def save(self, name):
        defs = ('<defs><filter id="soft" x="-20%" y="-20%" width="140%" height="140%">'
                '<feGaussianBlur stdDeviation="9"/></filter></defs>')
        s = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}">'
             + defs + "".join(self.items) + "</svg>")
        open(os.path.join(OUT, name + ".svg"), "w").write(s)


# ---------------------------------------------------------------- famílias


def topo(svg, core, period, rings, seed, palette="lav", amp=6.0, clip=None, inner=None):
    """Curvas de nível em volta de `core` (linha ou polígono).
    Cada período: banda lavanda + linha menta + banda lavanda + linha amarela.
    palette 'lav' = fundo lavanda com linhas (post 'Música psicodélica');
    'pink' = rosa com anéis menta/amarelo (mancha do post 'Quem lhama')."""
    name = OVR or {"lav": "lavanda", "pink": "rosa"}.get(palette, palette)
    b1, l1, b2, l2, center = TOPO_PAL[name]
    seq = [(b1, 0.44), (l1, 0.20), (b2, 0.16), (l2, 0.20)]
    bands = []
    for k in range(rings, 0, -1):
        base = (k - 1) * period
        acc = period
        for col, frac in seq:
            bands.append((base + acc, col))
            acc -= frac * period
    for d, col in bands:
        g = dens(core.buffer(d, quad_segs=24, join_style="round"), 5)
        g = wobble(g, amp * 0.35, seed, FINE)
        if clip is not None:
            g = g.intersection(clip)
        if inner is not None:
            g = g.difference(inner)
        svg.poly(g, col)
    c = wobble(dens(core.buffer(period * 0.12, quad_segs=24), 5), amp * 0.35, seed, FINE)
    if clip is not None:
        c = c.intersection(clip)
    if inner is not None:
        c = c.difference(inner)
    svg.poly(c, center)


def mint_lines(svg, core, period, rings, seed, mw=0.26, yw=0.12, amp=3.0, inner=None, pal="menta"):
    """Só as linhas, sem as bandas: linha menta grossa e linha amarela fina
    alternadas, com fundo transparente (post 'É booking')."""
    def line(d, w, col, sd):
        outer = wobble(dens(core.buffer(d + w / 2, quad_segs=24), 5), amp * 0.35, seed, FINE)
        hole = wobble(dens(core.buffer(max(0.1, d - w / 2), quad_segs=24), 5), amp * 0.35, seed, FINE)
        r = outer.difference(hole)
        if inner is not None:
            r = r.difference(inner)
        svg.poly(r, col)
    for k in range(1, rings + 1):
        c1, c2 = LINE_PAL[OVR or pal]
        line(k * period, mw * period, c1, seed + k)
        line(k * period + 0.5 * period, yw * period, c2, seed + 40 + k)


def worm(svg, core, width, seed, pal="lavanda", shadow=True, amp=3.0):
    """Minhoca gorda 3D do post 'Quem lhama com a gente?': sombra suave,
    camadas deslocadas para baixo (lilás, rosa, amarelo), contorno lavanda,
    fio amarelo largo por dentro da borda e corpo lavanda."""
    body, rim, edge, (c1, c2, c3) = WORM_PAL[OVR or pal]
    layers = [(c1, 0.20), (c2, 0.14), (c3, 0.08)]
    tube = wobble(dens(core.buffer(width / 2, quad_segs=24, cap_style="round", join_style="round"), 4), amp, seed)
    ang = math.radians(70)
    if shadow:
        sh = affinity.translate(tube, 0.34 * width * math.cos(ang), 0.34 * width * math.sin(ang))
        svg.poly(sh, "#1d1f3f", 0.20, 'filter="url(#soft)"')
    for col, off in layers:
        lay = affinity.translate(tube, off * width * math.cos(ang), off * width * math.sin(ang))
        svg.poly(lay, edge)
        svg.poly(lay.buffer(-width * 0.025), col)
    svg.poly(tube, edge)
    e = width * 0.05
    yr = tube.buffer(-e).difference(tube.buffer(-e - width * 0.09))
    svg.poly(yr, rim)
    svg.poly(tube.buffer(-e - width * 0.09), body)


def blob(cx, cy, r, seed, lobes=5, irregular=0.28, n=14):
    rnd = random.Random(seed)
    pts = []
    for i in range(n):
        a = i / n * 2 * math.pi
        rr = r * (1 + irregular * math.sin(lobes * a + rnd.uniform(0, 6)) * rnd.uniform(0.5, 1) + rnd.uniform(-0.08, 0.08))
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return Polygon(catmull(pts, 16, closed=True))


def meander(pts, n=24):
    return LineString(catmull(pts, n))


# ---------------------------------------------------------------- as 20 formas

S = 1000  # lado do quadro de cada forma (unidades)
shapes = []


def make(name, w=S, h=S):
    def deco(fn):
        shapes.append((name, w, h, fn))
        return fn
    return deco


@make("01-topo-meandro")
def f01(svg):
    core = meander([(330, 300), (520, 260), (640, 380), (520, 470), (420, 560), (560, 650), (690, 620)])
    topo(svg, core, 62, 5, 11)


@make("02-topo-nucleo-ramificado")
def f02(svg):
    a = meander([(380, 300), (430, 420), (520, 470), (640, 430), (660, 330)])
    b = meander([(520, 470), (500, 590), (420, 650)])
    c = meander([(520, 470), (620, 560), (700, 540)])
    core = unary_union([a, b, c])
    topo(svg, core, 58, 5, 22)


@make("03-topo-anel-vazado")
def f03(svg):
    ring = Point(500, 500).buffer(250, quad_segs=48).exterior
    core = LineString(list(ring.coords))
    inner = wobble(dens(Point(500, 500).buffer(150, quad_segs=48), 5), 3, 33)
    topo(svg, core, 56, 3, 33, inner=inner)


@make("04-topo-faixa-divisoria", 1600, 520)
def f04(svg):
    core = meander([(-200, 260), (180, 210), (420, 300), (700, 220), (980, 300), (1260, 230), (1800, 270)])
    topo(svg, core, 52, 4, 44, clip=box(0, 0, 1600, 520))


@make("05-topo-canto")
def f05(svg):
    core = meander([(-50, 140), (120, 160), (180, 60), (300, -40)])
    topo(svg, core, 64, 9, 55, clip=box(0, 0, 1000, 1000))


@make("06-fundo-topografico", 1080, 1350)
def f06(svg):
    a = meander([(200, 300), (380, 240), (520, 380), (420, 520), (560, 640), (760, 560)])
    b = meander([(700, 980), (820, 1080), (760, 1200), (880, 1290)])
    c = meander([(120, 1000), (260, 1060), (220, 1180)])
    core = unary_union([a, b, c])
    svg.raw(f'<rect width="1080" height="1350" fill="{LAV}"/>')
    topo(svg, core, 64, 12, 66, clip=box(0, 0, 1080, 1350))


@make("07-linhas-menta-meandro")
def f07(svg):
    core = meander([(240, 380), (420, 300), (560, 420), (460, 560), (640, 660), (780, 560)])
    mint_lines(svg, core, 72, 4, 77)


@make("08-linhas-menta-u")
def f08(svg):
    core = meander([(380, 150), (380, 520), (500, 640), (620, 520), (620, 150)])
    mint_lines(svg, core, 66, 4, 88, inner=box(0, -500, 1000, 120))


@make("09-minhoca-com-bracos")
def f09(svg):
    a = meander([(80, 140), (220, 260), (180, 420), (330, 470), (560, 450), (700, 560), (660, 640), (520, 610)])
    b = meander([(440, 460), (430, 600), (360, 720), (420, 880)])
    c = meander([(380, 700), (240, 760), (120, 720)])
    worm(svg, unary_union([a, b, c]), 118, 99)


@make("10-minhoca-s")
def f10(svg):
    worm(svg, meander([(180, 220), (430, 170), (560, 330), (420, 500), (520, 680), (800, 720)]), 136, 101)


@make("11-minhoca-laco")
def f11(svg):
    worm(svg, meander([(140, 700), (330, 650), (520, 420), (650, 300), (760, 420), (650, 560), (480, 470), (560, 300), (860, 230)]), 104, 111)


@make("12-minhoca-arco")
def f12(svg):
    arc = [(500 + 330 * math.cos(math.pi - t * math.pi / 30), 700 - 330 * math.sin(math.pi - t * math.pi / 30)) for t in range(31)]
    worm(svg, LineString(arc), 140, 121)


@make("13-minhoca-anel-moldura")
def f13(svg):
    ring = Point(500, 480).buffer(300, quad_segs=48).exterior
    worm(svg, LineString(list(ring.coords)), 120, 131)


@make("14-minhocas-curtas-trio")
def f14(svg):
    worm(svg, meander([(170, 260), (320, 210), (420, 290)]), 116, 141)
    worm(svg, meander([(560, 460), (700, 400), (820, 470)]), 116, 142)
    worm(svg, meander([(260, 700), (400, 760), (520, 690), (600, 760)]), 116, 143)


@make("15-mancha-rosa-aneis")
def f15(svg):
    core = blob(500, 500, 60, 151, lobes=3, irregular=0.35)
    topo(svg, core, 74, 5, 152, palette="pink", amp=7)


@make("16-mancha-amarela")
def f16(svg):
    b = wobble(dens(blob(500, 500, 330, 161, lobes=4, irregular=0.22), 5), 5, 162)
    svg.poly(b, YEL)


@make("17-mancha-lavanda-aneis")
def f17(svg):
    core = blob(500, 500, 70, 171, lobes=4, irregular=0.35)
    topo(svg, core, 70, 5, 172, amp=6)


@make("18-rabisco-orbita")
def f18(svg):
    rnd = random.Random(181)
    for k in range(7):
        rx, ry = 330 + rnd.uniform(-40, 40), 130 + rnd.uniform(-30, 40)
        rot = -18 + rnd.uniform(-12, 12)
        cx, cy = 500 + rnd.uniform(-30, 30), 500 + rnd.uniform(-25, 25)
        pts = []
        for i in range(0, 361, 6):
            a = math.radians(i)
            j = 1 + 0.03 * math.sin(3 * a + k)
            pts.append((rx * j * math.cos(a), ry * j * math.sin(a)))
        ell = affinity.translate(affinity.rotate(LineString(pts), rot, origin=(0, 0)), cx, cy)
        w = rnd.uniform(9, 15)
        col = {"rosa": PINK, "lavanda": LAVW, "amarelo": YEL, "menta": MINT, "vinho": WINE}[OVR or "rosa"]
        svg.poly(ell.buffer(w / 2, quad_segs=8), col, rnd.uniform(0.75, 1))


@make("19-pilula-etiqueta", 1000, 300)
def f19(svg):
    core = LineString([(150, 150), (850, 150)])
    pill = wobble(dens(core.buffer(110, quad_segs=32), 4), 1.6, 191)
    fill, under = {"rosa": (PINK, LILAC), "lilas": (LILAC, LAVW), "menta": (MINT, LAVW), "amarelo": (YEL, PINK), "vinho": (WINE, PINK)}[OVR or "rosa"]
    svg.poly(affinity.translate(pill, 0, 16), under)
    svg.poly(pill, fill)
    svg.poly(pill.buffer(-12).difference(pill.buffer(-19)), CREAM, 0.6)


@make("20-moldura-arco-topografica", 1000, 1250)
def f20(svg):
    arch = unary_union([box(300, 470, 700, 1000), Point(500, 470).buffer(200, quad_segs=48)])
    core = LineString(list(arch.exterior.coords))
    inner = wobble(dens(arch.buffer(-6), 4), 2, 201)
    topo(svg, core, 52, 4, 202, inner=inner, clip=box(0, 0, 1000, 1180))


import base64

IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "carrossel-onde-o-clube", "img")


def data_uri(name):
    mime = "image/png" if name.endswith(".png") else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(open(os.path.join(IMG, name), "rb").read()).decode()


FUNDO = {"azul": "fundo-azul.jpg", "amarelo": "fundo-amarelo.jpg", "preto": "fundo-preto.jpg"}


def ribbon_with_pattern(svg, geom, fundo, cid, scale=1.0):
    """Preenche a forma com o padrão de ondas da própria marca (LHAMAFUNDO)."""
    svg.raw(f'<clipPath id="{cid}"><path d="{path_d(geom)}"/></clipPath>')
    x0, y0, x1, y1 = geom.bounds
    w = (x1 - x0) * scale
    svg.raw(f'<image href="{data_uri(FUNDO[fundo])}" x="{x0}" y="{y0 - 40}" width="{w}" preserveAspectRatio="xMidYMid slice" '
            f'height="{(y1 - y0) + 80}" clip-path="url(#{cid})"/>')


# ---------------------------------------------------------------- formas novas (21-30)


@make("21-mancha-rasgada")
def f21(svg):
    """Manchas de papel rasgado do cartaz 'Bad Lhama in the Veludo Room'."""
    rough = ((260, 1.0), (90, 0.42), (31, 0.10), (11, 0.035))
    a = wobble_ring(dens(blob(430, 520, 300, 211, lobes=3, irregular=0.3), 4).exterior.coords, 34, 212, rough)
    b = wobble_ring(dens(blob(720, 300, 150, 213, lobes=2, irregular=0.3), 4).exterior.coords, 22, 214, rough)
    col = {None: WINE, "vinho": WINE, "lavanda": LAVW, "rosa": PINK, "menta": MINT, "amarelo": YEL}[OVR]
    svg.poly(unary_union([Polygon(a).buffer(0), Polygon(b).buffer(0)]), col)


@make("22-lava-badroom")
def f22(svg):
    """Formas de lâmpada de lava do 'Badroom': feijões e argolas com contorno grosso."""
    fill, ring = {None: (WINE, PINK), "vinho": (WINE, PINK), "grafite": (GRAPH, PINK), "lavanda": (LAVW, YEL), "violeta": (VIOLET, MINT)}[OVR]
    beans = [meander([(160, 240), (300, 180), (430, 260)]), meander([(560, 620), (700, 520), (840, 600), (820, 760)]),
             meander([(180, 760), (260, 640), (380, 700)])]
    shapes_ = [b.buffer(70, quad_segs=24) for b in beans]
    for cx, cy, r in [(640, 260, 95), (420, 470, 70), (800, 400, 48), (500, 840, 58)]:
        shapes_.append(Point(cx, cy).buffer(r, quad_segs=32).difference(Point(cx, cy).buffer(r * 0.42, quad_segs=32)))
    for k, g in enumerate(shapes_):
        g = wobble(dens(g, 4), 4, 220 + k)
        svg.poly(g.buffer(26, quad_segs=16), ring)
        svg.poly(g, fill)


@make("23-argolas-confete")
def f23(svg):
    fill, ring = {None: (WINE, PINK), "vinho": (WINE, PINK), "lavanda": (LAVW, YEL), "menta": (MINT, LAVW), "amarelo": (YEL, PINK)}[OVR]
    rnd = random.Random(231)
    for k in range(11):
        cx, cy, r = rnd.uniform(120, 880), rnd.uniform(120, 880), rnd.uniform(34, 78)
        g = Point(cx, cy).buffer(r, quad_segs=32).difference(Point(cx, cy).buffer(r * 0.45, quad_segs=32))
        g = wobble(dens(g, 4), 2.5, 232 + k)
        svg.poly(g.buffer(14, quad_segs=12), ring)
        svg.poly(g, fill)


@make("24-fita-ondas", 1400, 900)
def f24(svg):
    """Fita larga preenchida com o padrão de ondas da Lhama ('O que fazemos?')."""
    core = meander([(-150, 520), (200, 330), (520, 420), (820, 600), (1120, 430), (1600, 300)])
    g = wobble(dens(core.buffer(150, quad_segs=24), 5), 6, 241)
    ribbon_with_pattern(svg, g, OVR or "azul", "c24")


@make("25-fitas-ondas-dupla", 1080, 1350)
def f25(svg):
    a = meander([(-150, 420), (250, 300), (560, 420), (820, 330), (1250, 380)])
    b = meander([(-150, 1080), (240, 900), (520, 960), (800, 1120), (1250, 980)])
    ga = wobble(dens(a.buffer(140, quad_segs=24), 5), 6, 251)
    gb = wobble(dens(b.buffer(130, quad_segs=24), 5), 6, 252)
    ribbon_with_pattern(svg, ga, OVR or "azul", "c25a")
    ribbon_with_pattern(svg, gb, OVR or "azul", "c25b")


@make("26-caleidoscopio-lhamas")
def f26(svg):
    """Lhamas em giro radial, como no post 'Sabia que as lhamas não gostam de andar sozinhas?'."""
    svg.raw(f'<defs><image id="hd" href="{data_uri("head.png")}" width="200" height="402"/></defs>')
    n = 7
    for k in range(n):
        svg.raw(f'<use href="#hd" transform="rotate({k * 360 / n:.1f} 500 500) translate(445 120)"/>')


@make("27-mini-topos-confete")
def f27(svg):
    global OVR
    keep = OVR
    for k, (cx, cy, r, pal) in enumerate([(230, 250, 36, "rosa"), (700, 220, 30, "lavanda"), (520, 560, 42, "amarelo"),
                                          (210, 760, 28, "menta"), (790, 740, 34, "vinho")]):
        OVR = keep or pal
        topo(svg, blob(cx, cy, r, 270 + k, lobes=3, irregular=0.3), 30, 3, 271 + k, amp=3)
    OVR = keep


@make("28-minhoca-onda-longa", 1600, 600)
def f28(svg):
    worm(svg, meander([(80, 330), (330, 200), (580, 360), (830, 220), (1080, 380), (1330, 230), (1520, 300)]), 110, 281)


@make("29-fundo-linhas", 1080, 1350)
def f29(svg):
    """Fundo lavanda com linhas menta e amarelas (post 'É booking.')."""
    bg = {None: LAV, "menta": LAV, "rosa": WINE, "lavanda": MINT, "amarelo": LAVW, "vinho": VIOLET}[OVR]
    svg.raw(f'<rect width="1080" height="1350" fill="{bg}"/>')
    a = meander([(180, 260), (420, 180), (560, 360), (380, 520), (620, 700), (860, 600)])
    b = meander([(160, 1040), (360, 980), (420, 1180)])
    c = meander([(860, 1120), (900, 960)])
    mint_lines(svg, unary_union([a, b, c]), 78, 9, 291, inner=None)


@make("30-adesivo-blob")
def f30(svg):
    """Mancha-adesivo com o tratamento 3D da minhoca: pra selo e texto curto."""
    body, rim, edge, (c1, c2, c3) = WORM_PAL[OVR or "amarelo"]
    g = wobble(dens(blob(500, 470, 300, 301, lobes=5, irregular=0.12), 4), 4, 302)
    ang = math.radians(70)
    svg.poly(affinity.translate(g, 34 * math.cos(ang), 34 * math.sin(ang)), "#1d1f3f", 0.2, 'filter="url(#soft)"')
    for col, off in [(c1, 30), (c2, 21), (c3, 12)]:
        lay = affinity.translate(g, off * math.cos(ang), off * math.sin(ang))
        svg.poly(lay, edge)
        svg.poly(lay.buffer(-4), col)
    svg.poly(g, edge)
    svg.poly(g.buffer(-8).difference(g.buffer(-24)), rim)
    svg.poly(g.buffer(-24), body)


# ---------------------------------------------------------------- variações de cor

VARIANTS = {
    "01-topo-meandro": ["rosa", "menta", "amarelo", "vinho", "violeta", "grafite"],
    "03-topo-anel-vazado": ["rosa", "menta", "amarelo", "vinho", "grafite"],
    "15-mancha-rosa-aneis": ["lavanda", "menta", "amarelo", "vinho", "violeta"],
    "06-fundo-topografico": ["rosa", "menta", "vinho", "grafite"],
    "07-linhas-menta-meandro": ["rosa", "lavanda", "amarelo", "vinho"],
    "09-minhoca-com-bracos": ["rosa", "menta", "amarelo", "vinho"],
    "10-minhoca-s": ["rosa", "menta", "amarelo", "vinho"],
    "13-minhoca-anel-moldura": ["rosa", "menta", "amarelo", "vinho"],
    "18-rabisco-orbita": ["lavanda", "amarelo", "menta", "vinho"],
    "19-pilula-etiqueta": ["lilas", "menta", "amarelo", "vinho"],
    "21-mancha-rasgada": ["lavanda", "rosa", "menta", "amarelo"],
    "22-lava-badroom": ["grafite", "lavanda", "violeta"],
    "23-argolas-confete": ["lavanda", "menta", "amarelo"],
    "24-fita-ondas": ["amarelo", "preto"],
    "25-fitas-ondas-dupla": ["amarelo", "preto"],
    "29-fundo-linhas": ["rosa", "lavanda", "amarelo", "vinho"],
    "30-adesivo-blob": ["lavanda", "rosa", "menta", "vinho"],
}

if __name__ == "__main__":
    import shutil
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT)
    n = 0
    for name, w, h, fn in shapes:
        svg = SVG(w, h)
        OVR = None
        fn(svg)
        svg.save(name)
        n += 1
        for pal in VARIANTS.get(name, []):
            OVR = pal
            svg = SVG(w, h)
            fn(svg)
            svg.save(f"{name}--{pal}")
            n += 1
    OVR = None
    print(n, "arquivos em", OUT)
