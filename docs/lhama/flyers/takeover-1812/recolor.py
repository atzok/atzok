"""Recolore as imagens de referência do usuário pra paleta da Lhama,
mantendo os pontinhos da retícula (cada pixel vai pra tinta mais próxima).
Uso: python3 recolor.py <entrada> <saida> <mapa: agua|velas|velas-menta>"""
import sys
import numpy as np
from PIL import Image
src, dst, mapa = sys.argv[1], sys.argv[2], sys.argv[3]
im = np.asarray(Image.open(src).convert("RGB")).astype(np.float32)
hx = lambda h: np.array([int(h[i:i+2], 16) for i in (1, 3, 5)], np.float32)
LAV, PINK, YEL, MINT, CREAM, INK, LAVD = map(hx, ["#6E78E8", "#E679D3", "#EEE27A", "#B6D4A6", "#F2EAD8", "#151515", "#4E57C2"])
MAPS = {
    # tinta da referência -> tinta da Lhama
    "agua": [("#3c3cc4", LAV), ("#b4ec6e", YEL), ("#061006", INK), ("#f2f2f2", CREAM), ("#9090dc", "#8A94E6")],
    "velas": [("#7a5ce0", LAV), ("#b4f080", YEL), ("#f08ce6", PINK), ("#000000", INK), ("#e8e8e0", CREAM), ("#a8a8b0", "#C3A6E6")],
    "velas-menta": [("#7a5ce0", PINK), ("#b4f080", MINT), ("#f08ce6", YEL), ("#000000", "#82004E"), ("#e8e8e0", CREAM), ("#a8a8b0", "#E7C6E9")],
}
pairs = [(hx(a), hx(b) if isinstance(b, str) else b) for a, b in MAPS[mapa]]
src_c = np.stack([a for a, _ in pairs]); dst_c = np.stack([b for _, b in pairs])
d = ((im[:, :, None, :] - src_c[None, None]) ** 2).sum(-1)
w = np.exp(-(d - d.min(-1, keepdims=True)) / 900.0)
w /= w.sum(-1, keepdims=True)
out = (w[..., None] * dst_c[None, None]).sum(-2)
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(dst)
print("ok", dst)
