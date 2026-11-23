"""Formas da Lhama: gera 20 formas vetoriais fiéis às referências
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
    if palette == "lav":
        seq = [(LAV, 0.44), (MINT, 0.20), (LAV, 0.16), (YELP, 0.20)]
        center = YEL
    else:
        seq = [(PINK, 0.52), (MINT, 0.16), (PINK, 0.14), (YEL, 0.18)]
        center = YEL
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


def mint_lines(svg, core, period, rings, seed, mw=0.26, yw=0.12, amp=3.0, inner=None):
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
        line(k * period, mw * period, MINT, seed + k)
        line(k * period + 0.5 * period, yw * period, YELP, seed + 40 + k)


def worm(svg, core, width, seed, body=LAVW, rim=YEL, layers=None, shadow=True, amp=3.0):
    """Minhoca gorda 3D do post 'Quem lhama com a gente?': sombra suave,
    camadas deslocadas para baixo (lilás, rosa, amarelo), contorno lavanda,
    fio amarelo largo por dentro da borda e corpo lavanda."""
    if layers is None:
        layers = [(LILAC, 0.20), (PINK, 0.14), (YEL, 0.08)]
    tube = wobble(dens(core.buffer(width / 2, quad_segs=24, cap_style="round", join_style="round"), 4), amp, seed)
    ang = math.radians(70)
    if shadow:
        sh = affinity.translate(tube, 0.34 * width * math.cos(ang), 0.34 * width * math.sin(ang))
        svg.poly(sh, "#1d1f3f", 0.20, 'filter="url(#soft)"')
    for col, off in layers:
        lay = affinity.translate(tube, off * width * math.cos(ang), off * width * math.sin(ang))
        svg.poly(lay, LAVD)
        svg.poly(lay.buffer(-width * 0.025), col)
    svg.poly(tube, LAVD)
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
        svg.poly(ell.buffer(w / 2, quad_segs=8), PINK, rnd.uniform(0.75, 1))


@make("19-pilula-etiqueta", 1000, 300)
def f19(svg):
    core = LineString([(150, 150), (850, 150)])
    pill = wobble(dens(core.buffer(110, quad_segs=32), 4), 1.6, 191)
    svg.poly(affinity.translate(pill, 0, 16), LILAC)
    svg.poly(pill, PINK)
    svg.poly(pill.buffer(-12).difference(pill.buffer(-19)), CREAM, 0.6)


@make("20-moldura-arco-topografica", 1000, 1250)
def f20(svg):
    arch = unary_union([box(300, 470, 700, 1000), Point(500, 470).buffer(200, quad_segs=48)])
    core = LineString(list(arch.exterior.coords))
    inner = wobble(dens(arch.buffer(-6), 4), 2, 201)
    topo(svg, core, 52, 4, 202, inner=inner, clip=box(0, 0, 1000, 1180))


if __name__ == "__main__":
    for name, w, h, fn in shapes:
        svg = SVG(w, h)
        fn(svg)
        svg.save(name)
    print(len(shapes), "formas em", OUT)
