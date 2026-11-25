"""Recorta a lhama e o boto do flyer Lhama Nurio como camadas separadas, sem cortar mão nem focinho.
- máscara por cor (contornos pretos + preenchimentos), buracos internos preenchidos,
  EXCETO o vão de água entre a nadadeira e a boca do boto;
- a faísca do high five sai só pelos pixels amarelos (não corta o focinho);
- na zona do toque, cada pixel vai pro personagem cuja cor de preenchimento está mais perto
  (rosa = boto, creme/caramelo = lhama).
Uso: python3 recorta_personagens.py <flyer.png> <ele.npy> <pasta-layers>"""
import sys
import numpy as np, cv2
from PIL import Image
from scipy import ndimage as nd

SRC, ELE, OUT = sys.argv[1:4]
im = np.asarray(Image.open(SRC).convert("RGB")); H, W, _ = im.shape
r, g, b = [im[..., i].astype(int) for i in range(3)]
ele = np.load(ELE).astype(np.uint8)
hsv = cv2.cvtColor(im, cv2.COLOR_RGB2HSV).astype(int)
ele = (ele.astype(bool) | (hsv[..., 2] < 105)).astype(np.uint8)          # pega o contorno preto inteiro, inclusive o anti-alias
water = (hsv[..., 0] >= 85) & (hsv[..., 0] <= 140) & (hsv[..., 1] > 50) & (hsv[..., 2] > 105)
K = lambda k: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * k + 1, 2 * k + 1))
yellow = (r > 200) & (g > 170) & (b < 120)
X0, Y0, X1, Y1 = 285, 840, 860, 1470
m = np.zeros((H, W), np.uint8); m[Y0:Y1, X0:X1] = ele[Y0:Y1, X0:X1]
spark = np.zeros((H, W), bool); spark[970:1045, 528:608] = True
spark &= cv2.dilate(yellow.astype(np.uint8), K(3)) > 0
m[spark] = 0
m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, K(4)).astype(bool)
f = nd.binary_fill_holes(m); holes = f & ~m
lab, n = nd.label(holes)
for i in range(1, n + 1):
    ys, xs = np.nonzero(lab == i)
    cxh, cyh = xs.mean(), ys.mean()
    if (555 < cxh < 630 and 1040 < cyh < 1105) or (615 < cxh < 660 and 1110 < cyh < 1145):   # vãos de água do boto
        f[lab == i] = False
n2, lab2, st, _ = cv2.connectedComponentsWithStats(f.astype(np.uint8))
m = np.zeros((H, W), bool)
for i in range(1, n2):
    if st[i, 4] > 300:
        m |= lab2 == i
pink = (r > 200) & (g < 175) & (b > 140) & (r - g > 45)
cream = (r > 180) & (g > 140) & (b < 200) & (r - b > 30) & ~pink
dp = nd.distance_transform_edt(~pink); dc = nd.distance_transform_edt(~cream)
xx = np.arange(W)[None, :].repeat(H, 0); yy = np.arange(H)[:, None].repeat(W, 1)
golf = m & np.where(yy >= 1150, xx >= 554, xx >= 573)   # embaixo, a divisa é o vão entre as boias (x≈554)
zone = m & (xx > 530) & (xx < 610) & (yy > 1025) & (yy < 1200)
golf = np.where(zone, dp < dc, golf) | (m & (yy >= 1295))
golf &= ~((cv2.dilate(yellow.astype(np.uint8), K(4)) > 0) & (xx < 610) & (yy < 1040))   # só a faísca sai do boto
for name, mm, (x0, y0, x1, y1) in [("lhamaChar", m & ~golf, (285, 840, 573, 1290)), ("golfinho", golf, (455, 930, 860, 1470))]:
    mm = mm.copy(); mm[:y0] = 0; mm[y1:] = 0; mm[:, :x0] = 0; mm[:, x1:] = 0
    mm = cv2.morphologyEx(mm.astype(np.uint8), cv2.MORPH_OPEN, K(1)).astype(bool)
    # tira a água que ficou grudada na borda (só numa faixa de 4 px da borda)
    for _ in range(2):
        edge = mm & ~(cv2.erode(mm.astype(np.uint8), K(2)) > 0)
        mm &= ~(edge & water)
    # completa o traço preto da borda (anti-alias escuro que ficou de fora)
    for _ in range(2):
        mm = mm | ((cv2.dilate(mm.astype(np.uint8), K(1)) > 0) & (hsv[..., 2] < 150) & ~water)
    nn, ll, ss_, _ = cv2.connectedComponentsWithStats(mm.astype(np.uint8))
    mm = np.isin(ll, [i for i in range(1, nn) if ss_[i, 4] > 150]).astype(np.uint8)   # sem pontinhos soltos
    big = cv2.GaussianBlur(cv2.resize(mm.astype(np.float32), (W * 2, H * 2)), (0, 0), 1.2)
    a = np.clip((cv2.resize(big, (W, H), interpolation=cv2.INTER_AREA) - 0.15) / 0.7, 0, 1) * 255
    Image.fromarray(np.dstack([im, a.astype(np.uint8)])[y0:y1, x0:x1], "RGBA").save(f"{OUT}/{name}.png")
# faísca: só o amarelo + contorno
sm = (cv2.dilate(spark.astype(np.uint8), K(3)) & ele).astype(bool)
for _ in range(2):
    edge = sm & ~(cv2.erode(sm.astype(np.uint8), K(2)) > 0)
    sm &= ~(edge & water)
big = cv2.GaussianBlur(cv2.resize(sm.astype(np.float32), (W * 2, H * 2)), (0, 0), 1.2)
a = np.clip((cv2.resize(big, (W, H), interpolation=cv2.INTER_AREA) - 0.15) / 0.7, 0, 1) * 255
Image.fromarray(np.dstack([im, a.astype(np.uint8)])[975:1040, 530:605], "RGBA").save(f"{OUT}/spark.png")
print("ok")
