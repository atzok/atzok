"""Gera os arquivos de gráfica do adesivo 'Música Psicodélica Brasileira'.
Entradas: arte com o texto corrigido (fix_texto.py) e a máscara da faca (faca-mask.npy,
no sistema de coordenadas da arte 1080x1350, que fica em x=660 dentro da arte expandida).
Saídas por opção (A = @ no braço esquerdo, B = @ no braço direito):
  - PDF com a arte + linha de corte vetorial em cor especial 'CutContour' (0,100,0,0)
  - PNG da arte em alta (fundo transparente, com sangria branca)
  - SVG só da faca
Uso: python3 build_print.py <arte-corrigida.png> <saida-dir> [largura_cm=9]"""
import sys, os, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage as nd
from reportlab.pdfgen import canvas
from reportlab.lib.colors import CMYKColorSep
from reportlab.lib.utils import ImageReader

SRC, OUT = sys.argv[1], sys.argv[2]
WCM = float(sys.argv[3]) if len(sys.argv) > 3 else 9.0
HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "../../carrossel-onde-o-clube/Adca.ttf")
os.makedirs(OUT, exist_ok=True)

OFF = 660          # posição da arte 1080x1350 dentro da expandida
PAD = 80           # margem pra borda branca + sangria
BORDER = 22        # borda branca entre a arte e a faca (px)
BLEED = 24         # sangria além da faca (px)
UP = 2             # fator de ampliação do arquivo final

art_full = Image.open(SRC).convert("RGB")
reg0 = np.load(os.path.join(HERE, "faca-mask.npy"))
H0, W0 = reg0.shape
crop = art_full.crop((OFF - PAD, -PAD, OFF + W0 + PAD, H0 + PAD))   # fora da imagem vira preto, mas fica fora da máscara
reg = np.zeros((H0 + 2 * PAD, W0 + 2 * PAD), bool)
reg[PAD:PAD + H0, PAD:PAD + W0] = reg0


def disk(k):
    y, x = np.ogrid[-k:k + 1, -k:k + 1]
    return (x * x + y * y <= k * k).astype(np.uint8)


cut = cv2.dilate(reg.astype(np.uint8), disk(BORDER)) > 0
bleed = cv2.dilate(reg.astype(np.uint8), disk(BORDER + BLEED)) > 0

PINK, CREAM, INK, LAVD = (230, 121, 211), (242, 234, 216), (21, 21, 21), (78, 87, 194)
HANDLE = "@LHAMABOOKINGS"


def pill(img, cx, cy, size, fill, txt, rot=0, stroke=False):
    f = ImageFont.truetype(FONT, size)
    tmp = Image.new("RGBA", (900, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(tmp)
    tw = d.textlength(HANDLE, font=f); h = size * 1.55
    x0, x1 = 450 - tw / 2 - size * 0.6, 450 + tw / 2 + size * 0.6
    d.rounded_rectangle([x0 + 5, 100 - h / 2 + 7, x1 + 5, 100 + h / 2 + 7], radius=h / 2, fill=LAVD + (255,))
    d.rounded_rectangle([x0, 100 - h / 2, x1, 100 + h / 2], radius=h / 2, fill=fill + (255,), outline=INK + (255,), width=4)
    kw = dict(stroke_width=3, stroke_fill=INK) if stroke else {}
    d.text((450, 102), HANDLE, font=f, fill=txt, anchor="mm", **kw)
    tmp = tmp.rotate(rot, expand=True, resample=Image.BICUBIC)
    img.paste(tmp, (int(cx + PAD - tmp.width / 2), int(cy + PAD - tmp.height / 2)), tmp)


OPTS = {
    "A": lambda a: pill(a, 235, 945, 32, CREAM, INK, rot=-6),
    "B": lambda a: pill(a, 700, 430, 36, PINK, CREAM, rot=8, stroke=True),
}

for name, fn in OPTS.items():
    a = crop.copy(); fn(a)
    Hc, Wc = reg.shape
    # composição: sangria branca -> borda branca -> arte recortada
    rgba = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0))
    rgba.paste(Image.new("RGBA", (Wc, Hc), (255, 255, 255, 255)), (0, 0), Image.fromarray((bleed * 255).astype(np.uint8)))
    m = Image.fromarray((reg * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7))
    rgba.paste(a, (0, 0), m)
    # recorta no limite da sangria e amplia
    ys, xs = np.nonzero(bleed)
    x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    rgba = rgba.crop((x0, y0, x1, y1))
    big = rgba.resize((rgba.width * UP, rgba.height * UP), Image.LANCZOS)
    w_px, h_px = big.size
    dpi = w_px / (WCM / 2.54)
    big.save(os.path.join(OUT, f"adesivo-mpb-{name}_arte.png"), dpi=(dpi, dpi))
    # contorno da faca (no recorte, em px ampliados)
    cm_ = (cut[y0:y1, x0:x1] * 255).astype(np.uint8)
    cm_ = cv2.resize(cm_, (w_px, h_px), interpolation=cv2.INTER_LINEAR)
    cm_ = cv2.GaussianBlur(cm_, (0, 0), 3)
    cs, _ = cv2.findContours((cm_ > 127).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=cv2.contourArea)
    c = cv2.approxPolyDP(c, 1.2, True)[:, 0, :]
    # PDF em pontos (1 pt = 1/72 in)
    pw = WCM / 2.54 * 72; ph = pw * h_px / w_px; k = pw / w_px
    pdf = canvas.Canvas(os.path.join(OUT, f"adesivo-mpb-{name}_grafica.pdf"), pagesize=(pw, ph))
    pdf.setTitle(f"Adesivo Lhama Bookings MPB {name}")
    pdf.drawImage(ImageReader(big), 0, 0, width=pw, height=ph, mask="auto")
    cut_col = CMYKColorSep(0, 1, 0, 0, spotName="CutContour", density=1)
    pdf.setStrokeColor(cut_col); pdf.setLineWidth(0.25)
    p = pdf.beginPath()
    p.moveTo(c[0][0] * k, ph - c[0][1] * k)
    for x, y in c[1:]:
        p.lineTo(x * k, ph - y * k)
    p.close()
    pdf.drawPath(p, stroke=1, fill=0)
    pdf.showPage(); pdf.save()
    # SVG da faca
    d = "M" + " L".join(f"{x * k:.2f} {(y * k):.2f}" for x, y in c) + " Z"
    open(os.path.join(OUT, f"adesivo-mpb-{name}_faca.svg"), "w").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{pw:.2f}pt" height="{ph:.2f}pt" viewBox="0 0 {pw:.2f} {ph:.2f}">'
        f'<path d="{d}" fill="none" stroke="#EC008C" stroke-width="0.25"/></svg>')
    print(name, f"{w_px}x{h_px}px", f"{WCM:.1f}x{WCM * h_px / w_px:.1f} cm", f"{dpi:.0f} dpi")
