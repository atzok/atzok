"""Gera os adesivos com borda branca (die-cut) usados nos mockups de merch.
Uso: python3 prep_merch.py <pasta-formas-png> <pasta-saida>"""
import sys, os
import numpy as np
from PIL import Image, ImageFilter
F, OUT = sys.argv[1], sys.argv[2]
IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

def diecut(src, name, border=26, size=700):
    im = Image.open(src).convert("RGBA")
    im = im.crop(im.getbbox())
    im.thumbnail((size, size), Image.LANCZOS)
    pad = border * 2
    can = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    can.paste(im, (pad, pad), im)
    a = can.split()[3].point(lambda v: 255 if v > 40 else 0)
    # fecha buracos pequenos e arredonda a borda do recorte
    m = a.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(9))
    for _ in range(border // 6):
        m = m.filter(ImageFilter.MaxFilter(13))
    m = m.filter(ImageFilter.GaussianBlur(2)).point(lambda v: 255 if v > 128 else 0)
    white = Image.new("RGBA", can.size, (250, 248, 242, 255))
    white.putalpha(m)
    out = Image.alpha_composite(white, can)
    out.save(os.path.join(OUT, name + ".png"))

jobs = [
    (os.path.join(IMG, "head.png"), "st-head"),
    (os.path.join(IMG, "espiral.png"), "st-espiral"),
    (os.path.join(IMG, "arco.png"), "st-arco"),
    (os.path.join(IMG, "mpb-badge.png"), "st-mpb"),
    (os.path.join(IMG, "nome-cor.png"), "st-nome"),
    (os.path.join(F, "09-minhoca-com-bracos.png"), "st-minhoca"),
    (os.path.join(F, "15-mancha-rosa-aneis.png"), "st-mancha"),
    (os.path.join(F, "30-adesivo-blob.png"), "st-blob"),
    (os.path.join(F, "26-caleidoscopio-lhamas.png"), "st-caleido"),
    (os.path.join(F, "10-minhoca-s--rosa.png"), "st-minhoca-rosa"),
    (os.path.join(F, "22-lava-badroom.png"), "st-lava"),
    (os.path.join(F, "03-topo-anel-vazado--amarelo.png"), "st-anel"),
]
for src, name in jobs:
    diecut(src, name)
print(len(jobs), "adesivos em", OUT)
