"""Gera os assets graficos do carrossel: papel reciclado, vinil e manchas em retícula.

Uso: python3 tools/make_assets.py  (a partir de social/booking-underground/)
"""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(__file__), '..', 'assets')
INK = (20, 18, 16)
EMBER = (188, 109, 33)
rng = np.random.default_rng(7)
random.seed(7)


def paper(w, h, name):
    base = np.array([234, 227, 210], dtype=np.float32)
    img = np.ones((h, w, 3), np.float32) * base
    # manchas grandes (variação do papel)
    low = rng.normal(0, 1, (h // 60 + 2, w // 60 + 2)).astype(np.float32)
    low = np.array(Image.fromarray(((low + 3) * 40).clip(0, 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32)
    img += ((low - 120) / 120 * 6)[..., None]
    # grão fino
    img += rng.normal(0, 5, (h, w, 1))
    out = Image.fromarray(img.clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(out, 'RGBA')
    # fibras e pontinhos do papel reciclado
    for _ in range(int(w * h / 900)):
        x, y = random.random() * w, random.random() * h
        a = random.random() * math.pi
        l = random.uniform(3, 14)
        c = random.choice([(120, 110, 95, 70), (160, 150, 130, 60), (90, 80, 70, 50), (255, 255, 250, 70)])
        d.line([(x, y), (x + math.cos(a) * l, y + math.sin(a) * l)], fill=c, width=1)
    for _ in range(int(w * h / 5000)):
        x, y = random.random() * w, random.random() * h
        r = random.uniform(.6, 1.8)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(60, 55, 50, random.randint(40, 120)))
    out = out.filter(ImageFilter.GaussianBlur(.35))
    out.save(os.path.join(OUT, name), quality=92)


def halftone(gray, cell, color, name, angle=45):
    """gray: array 0..1 (1 = tinta cheia). Desenha pontos girados como retícula de xerox."""
    h, w = gray.shape
    S = 3
    im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ca, sa = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    diag = int(math.hypot(w, h))
    for i in range(-diag, diag, cell):
        for j in range(-diag, diag, cell):
            x = w / 2 + i * ca - j * sa
            y = h / 2 + i * sa + j * ca
            if 0 <= x < w and 0 <= y < h:
                v = gray[int(y), int(x)]
                if v > 0.04:
                    r = cell * 0.72 * math.sqrt(v)
                    d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=color + (255,))
    im = im.resize((w, h), Image.LANCZOS)
    im.save(os.path.join(OUT, name))


def vinyl(n=900, color=INK, name='vinil.png'):
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    cx = cy = n / 2
    r = np.hypot(xx - cx, yy - cy) / (n / 2)
    th = np.arctan2(yy - cy, xx - cx)
    g = np.zeros((n, n), np.float32)
    disc = r < 0.98
    g[disc] = 0.92
    grooves = 0.08 * (np.sin(r * 140) > 0.6)
    g -= grooves * disc
    # reflexo em cunha
    shine = np.exp(-((np.mod(th + 0.6, math.pi) - 1.0) ** 2) / 0.05) * (r > 0.38) * (r < 0.96)
    g -= 0.65 * shine * disc
    # selo central vazio
    g[r < 0.34] = 0
    g[(r < 0.36) & (r >= 0.34)] = 0.9
    g[r < 0.035] = 0
    halftone(g.clip(0, 1), 9, color, name, angle=30)


def blob(n, color, name, seed=1):
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    r = np.hypot(xx - n / 2, yy - n / 2) / (n / 2)
    g = (1 - r).clip(0, 1) ** 0.8
    halftone(g, 12, color, name)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    paper(1080, 1350, 'papel-4x5.jpg')
    paper(1080, 1920, 'papel-9x16.jpg')
    vinyl()
    vinyl(color=EMBER, name='vinil-laranja.png')
    blob(700, EMBER, 'mancha-laranja.png')
    blob(700, INK, 'mancha-preta.png')
    print('ok')
