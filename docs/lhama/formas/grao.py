"""Aplica grão de papel (risografia) num PNG transparente, sem mexer no alfa.
Uso: python3 grao.py <pasta-entrada> <pasta-saida> [forca=0.09]"""
import sys, os, glob
import numpy as np
from PIL import Image, ImageFilter
src, dst = sys.argv[1], sys.argv[2]
k = float(sys.argv[3]) if len(sys.argv) > 3 else 0.09
os.makedirs(dst, exist_ok=True)
for f in sorted(glob.glob(os.path.join(src, "*.png"))):
    im = Image.open(f).convert("RGBA")
    a = np.asarray(im).astype(np.float32)
    h, w = a.shape[:2]
    rng = np.random.default_rng(abs(hash(os.path.basename(f))) % 2**32)
    fine = rng.standard_normal((h, w)).astype(np.float32)
    blob = Image.fromarray(((rng.standard_normal((h // 3 + 1, w // 3 + 1)) * 40 + 128).clip(0, 255)).astype(np.uint8)).resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.2))
    coarse = (np.asarray(blob).astype(np.float32) - 128) / 40
    n = 0.65 * fine + 0.55 * coarse
    a[..., :3] *= (1 + k * n)[..., None]
    Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA").save(os.path.join(dst, os.path.basename(f)), optimize=True)
print("grão aplicado em", dst)
