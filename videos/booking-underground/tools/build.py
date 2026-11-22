"""Gera index.html e compositions/*.html do Reels "booking underground".

Rodar uma vez (a partir da pasta do projeto): python3 tools/build.py
Depois disso os arquivos são editados direto (ou no app); rodar de novo sobrescreve.
"""
import math, os

ROOT = os.path.join(os.path.dirname(__file__), '..')
INK, PAPER, SHEET, EMBER, SOFT = '#141210', '#eae3d2', '#f6f2e8', '#bc6d21', '#5a534a'
EMBER_TXT = '#a65c16'  # laranja um pouco mais escuro para texto: 3.3:1 sobre o papel

# ---------- linha do tempo (s) ----------
SCENES = [  # id, start
    ('capa', 0.00), ('sozinho', 4.85), ('gosto', 13.10), ('contrata', 18.50), ('cupom', 28.40),
    ('som', 32.20), ('erra', 35.25), ('acordo', 42.25), ('risco', 50.05), ('sinal', 55.40), ('cena', 57.75),
]
END = 62.0
VOICE = [('l1', 0.30), ('l2', 4.95), ('l3', 13.25), ('l4', 18.65), ('l5a', 28.55), ('l5b', 32.35),
         ('l6', 35.40), ('l7', 42.40), ('l8', 50.20), ('l9', 55.55), ('l10', 57.90)]
VOICE_DUR = {'l1': 4.288, 'l2': 7.936, 'l3': 5.035, 'l4': 9.536, 'l5a': 1.74, 'l5b': 1.716, 'l6': 6.635,
             'l7': 7.445, 'l8': 4.949, 'l9': 1.771, 'l10': 2.091}
SFX_PEAK = {'whoosh': .165, 'whoosh-short': .165, 'pop': .122, 'click-soft': .075, 'click': .075,
            'key-press': .08, 'typing': 0.0, 'impact-bass-1': 1.956, 'impact-bass-2': 2.066, 'glitch-3': .293}
SFX_DUR = {'whoosh': .575, 'whoosh-short': .575, 'pop': .72, 'click-soft': .366, 'click': .366, 'key-press': .432,
           'typing': 1.541, 'impact-bass-1': 2.116, 'impact-bass-2': 2.592, 'glitch-3': 3.096}


def start_of(sid):
    return dict(SCENES)[sid]


def dur_of(sid):
    ids = [s for s, _ in SCENES]
    i = ids.index(sid)
    return round((SCENES[i + 1][1] if i + 1 < len(SCENES) else END) - SCENES[i][1], 3)


SFX = []  # (file, hit global, volume)


def sfx(name, sid, t_local, vol):
    SFX.append((name, round(start_of(sid) + t_local, 3), vol))


# ---------- formas ----------
def burst(n=18, inner=40, outer=50):
    pts = []
    for i in range(n * 2):
        a = math.pi * i / n
        r = inner if i % 2 else outer
        pts.append(f'{50 + r * math.cos(a):.2f}% {50 + r * math.sin(a):.2f}%')
    return 'polygon(' + ','.join(pts) + ')'


def zigzag():
    pts = ['0 0', '100% 0']
    for i in range(20, -1, -1):
        pts.append(f'{i * 5}% {98 if i % 2 else 100}%')
    return 'polygon(' + ','.join(pts) + ')'


TAPE = 'polygon(2% 8%, 10% 0, 22% 10%, 35% 2%, 50% 9%, 64% 0, 78% 8%, 90% 1%, 100% 10%, 98% 92%, 88% 100%, 74% 91%, 60% 100%, 45% 92%, 30% 100%, 15% 91%, 0 100%)'

CSS = """
    @font-face { font-family: "Instrument Serif"; font-style: italic; font-weight: 400; src: url('assets/fonts/instrument-serif-italic.woff2') format('woff2'); }
    @font-face { font-family: "Caveat"; font-weight: 700; src: url('assets/fonts/caveat-700.woff2') format('woff2'); }
    #root { position: absolute; inset: 0; overflow: hidden; }
    .all { position: absolute; inset: 0; }
    .mono { font-family: "Space Mono", monospace; font-weight: 700; text-transform: uppercase; letter-spacing: .14em; }
    .tag { position: absolute; left: 130px; top: 300px; font-size: 28px; background: INK; color: PAPER; padding: 10px 16px 9px; }
    .tag.or { background: EMBER; color: INK; }
    .num { position: absolute; left: 760px; top: 310px; width: 120px; text-align: right; font-size: 28px; color: INK; }
    .h { position: absolute; left: 130px; width: 760px; font-family: Inter, sans-serif; font-weight: 900; letter-spacing: -.055em; line-height: .92; color: INK; }
    .or { color: EMBER_TXT; }
    .w { display: inline-block; }
    .serif { font-family: "Instrument Serif", serif; font-style: italic; font-weight: 400; }
    .hand { font-family: "Caveat", cursive; font-weight: 700; }
    .body { position: absolute; left: 130px; width: 720px; font-family: Inter, sans-serif; font-weight: 500; font-size: 38px; line-height: 1.28; color: INK; }
    .sheet { position: absolute; background: SHEET; box-shadow: 0 2px 0 rgba(0,0,0,.05), 0 22px 34px -20px rgba(0,0,0,.4); }
    .tape { position: absolute; width: 170px; height: 46px; background: rgba(246,242,232,.75); box-shadow: 0 1px 2px rgba(0,0,0,.12); clip-path: TAPE; }
    .stamp { position: absolute; border: 8px solid EMBER; color: EMBER_TXT; font-family: "Space Mono", monospace; font-weight: 700; text-transform: uppercase; letter-spacing: .12em; padding: 12px 26px 8px; mix-blend-mode: multiply; }
    .burst { position: absolute; display: flex; align-items: center; justify-content: center; text-align: center; }
    .box { display: inline-block; position: relative; width: 34px; height: 34px; border: 4px solid INK; border-radius: 3px; margin-right: 22px; vertical-align: -4px; }
    .box svg { position: absolute; left: -6px; top: -16px; overflow: visible; }
    svg.draw { position: absolute; overflow: visible; }
    svg path.ln { fill: none; stroke: INK; stroke-width: 6; stroke-linecap: round; stroke-linejoin: round; }
    svg path.ln.or { stroke: EMBER; }
""".replace('EMBER_TXT', EMBER_TXT).replace('INK', INK).replace('PAPER', PAPER).replace('SHEET', SHEET).replace('EMBER', EMBER).replace('TAPE', TAPE)


def words(text, cls='w'):
    """'a b <or>c</or>' -> spans por palavra (destaque com <or>)."""
    out = []
    for line in text.split(' | '):
        ws = []
        for tok in line.strip().split(' '):
            if tok.startswith('<or>'):
                ws.append(f'<span class="{cls} or">{tok[4:].replace("</or>", "")}</span>')
            else:
                ws.append(f'<span class="{cls}">{tok}</span>')
        out.append(' '.join(ws))
    return '<br>'.join(out)


def tick(i):
    return f'<svg width="56" height="56" viewBox="0 0 56 56"><path class="ln" id="TK{i}" pathLength="1" d="M6 30 L22 46 L52 4" style="stroke-dasharray:1;stroke-dashoffset:1;stroke-width:7"/></svg>'


def scene(sid, body, js):
    d = dur_of(sid)
    html = f"""<template>
  <style>{CSS}  </style>
  <div id="root" data-composition-id="{sid}" data-width="1080" data-height="1920">
    <div id="{sid}-all" class="all clip" data-start="0" data-duration="{d}" data-track-index="1">
{body}
    </div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      const S = "#{sid}-all";
{js}
      window.__timelines["{sid}"] = tl;
    }})();
  </script>
</template>
"""
    os.makedirs(os.path.join(ROOT, 'compositions'), exist_ok=True)
    open(os.path.join(ROOT, 'compositions', sid + '.html'), 'w').write(html)


# helpers de animação (strings JS)
def blur_words(sel, t, stagger=.067):
    return f'      tl.fromTo("{sel}", {{ opacity: 0, filter: "blur(6px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: .13, stagger: {stagger}, ease: "power2.out" }}, {t});\n'


def grey_words(sel, t, stagger=.09):
    return f'      tl.fromTo("{sel}", {{ color: "#c9c0ad" }}, {{ color: (i, el) => el.classList.contains("or") ? "{EMBER_TXT}" : "{INK}", duration: .12, stagger: {stagger} }}, {t});\n'


def line_blur(sel, t):
    return f'      tl.fromTo("{sel}", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: .18, ease: "power2.out" }}, {t});\n'


def blur_out(sid, d):
    return f'      tl.to(S, {{ opacity: 0, filter: "blur(8px)", duration: .2, ease: "power3.in" }}, {round(d - .22, 3)});\n'


def draw(sel, t, dur=.35):
    return f'      tl.fromTo("{sel}", {{ strokeDashoffset: 1 }}, {{ strokeDashoffset: 0, duration: {dur}, ease: "power2.inOut" }}, {t});\n'


def slam(sel, t, rot):
    return (f'      tl.fromTo("{sel}", {{ opacity: 0, scale: 1.7, rotation: {rot - 6} }}, {{ opacity: .95, scale: 1, rotation: {rot}, duration: .16, ease: "power4.in" }}, {round(t - .16, 3)});\n')


def arrive(sel, t, frm, rot_to=0, dur=.6):
    return f'      tl.fromTo("{sel}", {{ opacity: 0, {frm} }}, {{ opacity: 1, x: 0, y: 0, rotation: {rot_to}, scale: 1, duration: {dur}, ease: "expo.out" }}, {t});\n'


def head(sid, tag, n, orange=False):
    return f'      <div id="{sid}-tag" class="tag mono{" or" if orange else ""}">{tag}</div>\n      <div id="{sid}-num" class="num mono">{n:02d}/11</div>\n'


HEADJS = lambda sid: line_blur(f'#{sid}-tag, #{sid}-num', 0)

# ================= cenas =================
# 01 capa ------------------------------------------------------------
sid = 'capa'; d = dur_of(sid)
body = head(sid, 'papo reto sobre a cena', 1) + f"""      <div id="ca-t" class="h" style="top:370px; font-size:146px">o booking<br><span class="or">não<br>funciona!?</span></div>
      <div id="ca-sub" class="serif" style="position:absolute; left:130px; top:880px; width:540px; font-size:54px; line-height:1.04; color:{INK}">{words('Seguinte, vou contar como isso funciona do meu lado.')}</div>
      <img id="ca-logo" src="assets/wordmark-preto.png" alt="Ätzøk" style="position:absolute; left:130px; top:1150px; height:84px">
      <div id="ca-vinil" style="position:absolute; left:560px; top:1000px; width:760px; height:760px">
        <div style="position:absolute; inset:34%; border-radius:50%; background:{EMBER}"></div>
        <img src="assets/vinil.png" style="position:absolute; inset:0; width:100%">
        <div style="position:absolute; left:50%; top:50%; width:24px; height:24px; margin:-12px; border-radius:50%; background:{PAPER}"></div>
      </div>
      <div id="ca-burst" class="burst" style="left:690px; top:1010px; width:210px; height:210px; background:{EMBER}; clip-path:{burst(16)}">
        <span class="mono" style="font-size:24px; line-height:1.2; color:{INK}">parte<br><b style="font-size:58px; letter-spacing:0">1</b></span></div>
"""
js = f"""      tl.fromTo("#ca-vinil", {{ rotation: 0 }}, {{ rotation: 60, duration: {d}, ease: "none" }}, 0);
      tl.fromTo("#ca-burst", {{ scale: 0, rotation: -40 }}, {{ scale: 1, rotation: -12, duration: .5, ease: "back.out(1.6)" }}, .7);
""" + blur_words('#ca-sub .w', 1.76, .07) + f"""      tl.to("#ca-vinil", {{ x: 700, duration: .45, ease: "power3.in" }}, {d - .5});
      tl.to("#ca-burst", {{ x: 700, rotation: 40, duration: .45, ease: "power3.in" }}, {d - .5});
""" + blur_out(sid, d)
sfx('pop', sid, .78, .5)
sfx('whoosh', sid, d - .2, .45)
scene(sid, body, js)

# 02 sozinho --------------------------------------------------------
sid = 'sozinho'; d = dur_of(sid)
items = ['responder o direct', 'fechar a data', 'cobrar o cachê', 'atualizar o rider', 'fazer o flyer']
rows = ''.join(f'<div style="height:62px">{"<span class=box>" + tick(i).replace("TK", "so-tk") + "</span>"}{it}</div>' for i, it in enumerate(items))
body = head(sid, 'como é hoje', 2) + f"""      <div id="so-t" class="h" style="top:380px; font-size:116px">{words('hoje eu faço | tudo <or>sozinho</or>')}</div>
      <div id="so-pad" class="sheet" style="left:140px; top:665px; width:600px; height:470px; transform:rotate(-3deg);
        background:repeating-linear-gradient(transparent 0 60px, #c9d3da 60px 62px) 0 86px / 100% 100% no-repeat, {SHEET}">
        <div style="position:absolute; left:64px; top:0; bottom:0; width:3px; background:{EMBER}; opacity:.6"></div>
        <div class="hand" style="position:absolute; left:90px; top:16px; font-size:54px; color:{INK}">essa semana:</div>
        <div class="hand" style="position:absolute; left:90px; top:92px; font-size:42px; color:{INK}">{rows}
          <div style="height:62px; color:{EMBER_TXT}"><span class="box" style="border-color:{EMBER_TXT}"></span>pesquisar música</div></div>
      </div>
      <div id="so-tape" class="tape" style="left:340px; top:641px; transform:rotate(4deg)"></div>
      <div id="so-note" class="hand" style="position:absolute; left:665px; top:880px; width:150px; font-size:44px; line-height:.95; color:{EMBER_TXT}; transform:rotate(-6deg)">ficou pra depois</div>
      <svg class="draw" style="left:610px; top:980px" width="160" height="120"><path id="so-arrow" class="ln or" pathLength="1" style="stroke-dasharray:1" d="M110 6 C 120 60, 80 96, 12 92 M12 92 l 28 -22 M12 92 l 30 16"/></svg>
      <div id="so-body" class="body" style="top:1150px">{words('a semana acabou e eu não ouvi um disco novo.')}</div>
"""
TK = [1.85, 2.45, 3.15, 3.5, 3.95]
js = HEADJS(sid) + blur_words('#so-t .w', .1) + arrive('#so-pad', .5, 'y: 260, rotation: -9', -3) + \
    f'      tl.fromTo("#so-tape", {{ opacity: 0, scale: 1.3 }}, {{ opacity: 1, scale: 1, duration: .2, ease: "power3.out" }}, .95);\n' + \
    ''.join(draw(f'#so-tk{i}', t, .18) for i, t in enumerate(TK)) + \
    blur_words('#so-note', 5.12) + draw('#so-arrow', 5.3, .45) + blur_words('#so-body .w', 5.25, .06) + blur_out(sid, d)
sfx('click-soft', sid, .97, .4)
for t in TK:
    sfx('click', sid, t + .1, .35)
scene(sid, body, js)

# 03 gosto ----------------------------------------------------------
sid = 'gosto'; d = dur_of(sid)
body = head(sid, 'por quê', 3) + f"""      <div id="go-t" class="h" style="top:380px; font-size:116px">{words('e não é porque | eu <or>gosto</or>')}</div>
      <div id="go-ticket" class="sheet" style="left:140px; top:680px; width:680px; height:320px; transform:rotate(-2.5deg); display:flex">
        <div style="flex:1; padding:36px 40px; border-right:4px dashed #bdb5a5">
          <div class="mono" style="font-size:28px; color:{SOFT}">line-up · sábado</div>
          <div id="go-hora" style="font-family:Inter; font-weight:900; font-size:116px; letter-spacing:-.05em; line-height:1; margin-top:10px; color:{INK}; transform-origin:left center">06:00</div>
          <div class="mono" style="font-size:28px; margin-top:12px; color:{INK}">pista: <span style="color:{EMBER_TXT}">vazia</span></div>
        </div>
        <div style="width:200px; padding:36px 24px">
          <div class="mono" style="font-size:28px; color:{SOFT}">cachê</div>
          <div style="font-family:Inter; font-weight:900; font-size:56px; letter-spacing:-.04em; margin-top:10px; color:{INK}">R$ ?</div>
          <div class="mono" style="font-size:28px; color:{SOFT}; margin-top:22px; line-height:1.2">pago:<br>nunca</div>
        </div>
      </div>
      <div id="go-stamp" class="stamp" style="left:300px; top:920px; font-size:70px">calote</div>
      <div id="go-body" class="body" style="top:1110px; width:660px">{words('já levei calote. já toquei às 6h pra pista vazia.')}</div>
      <div id="go-dip" style="position:absolute; inset:0; background:{INK}; opacity:0"></div>
"""
js = HEADJS(sid) + grey_words('#go-t .w', .1) + arrive('#go-ticket', 1.2, 'y: 220, rotation: 4', -2.5) + slam('#go-stamp', 2.05, -9) + \
    f'      tl.fromTo("#go-hora", {{ scale: 1 }}, {{ scale: 1.08, duration: .12, yoyo: true, repeat: 1, ease: "power2.out" }}, 3.65);\n' + \
    blur_words('#go-body .w', 1.5, .07) + \
    f'      tl.fromTo("#go-dip", {{ opacity: 0 }}, {{ opacity: .4, duration: .1 }}, {round(d - .1, 3)});\n'
sfx('whoosh-short', sid, 1.25, .3)
sfx('impact-bass-1', sid, 2.05, .22)
sfx('click', sid, 2.05, .6)
scene(sid, body, js)

# 04 contrata -------------------------------------------------------
sid = 'contrata'; d = dur_of(sid)
body = head(sid, 'do outro lado', 4) + f"""      <div id="ct-t" class="h" style="top:380px; font-size:104px">quem contrata<br>também tá<br><span class="or">apertado</span></div>
      <div id="ct-sub" class="serif" style="position:absolute; left:130px; top:720px; width:450px; font-size:52px; line-height:1.04; color:{INK}">{words('se a festa não vende, o prejuízo é do produtor.')}</div>
      <div id="ct-burst" class="burst" style="left:560px; top:840px; width:340px; height:340px; background:{EMBER}; clip-path:{burst(22)}">
        <div><div style="font-family:Inter; font-weight:900; font-size:82px; letter-spacing:-.05em; line-height:.9; color:{INK}">15 a<br>20%</div><div class="serif" style="font-size:38px; color:{INK}">de comissão</div></div></div>
      <div id="ct-stamp" class="stamp" style="left:135px; top:1050px; font-size:50px">burocracia</div>
"""
js = HEADJS(sid) + line_blur('#ct-t', .1) + blur_words('#ct-sub .w', 2.95, .06) + \
    f'      tl.fromTo("#ct-burst", {{ scale: 0, rotation: -30 }}, {{ scale: 1, rotation: 8, duration: .55, ease: "back.out(1.7)" }}, 5.75);\n' + \
    slam('#ct-stamp', 8.85, -7) + blur_out(sid, d)
sfx('pop', sid, 5.82, .55)
sfx('impact-bass-1', sid, 8.85, .2)
sfx('click', sid, 8.85, .6)
scene(sid, body, js)

# 05 cupom ----------------------------------------------------------
sid = 'cupom'; d = dur_of(sid)
lines = [('CACHÊ COMBINADO', 'R$ ___', True), ('horário mudou', '−', False), ('volta por minha conta', '−', False),
         ('"acerto na segunda"', '−', False), ('consumação no lugar', '−', False)]
rl = ''.join(f'<div class="cu-ln" style="display:flex; justify-content:space-between;{" font-weight:700;" if b else ""}"><span>{a}</span><span>{c}</span></div>' for a, c, b in lines)
body = head(sid, 'no fim das contas', 5) + f"""      <div id="cu-t" class="h" style="top:380px; font-size:100px">{words('no meio disso, | o cachê')} <span id="cu-enc" class="w or" style="transform-origin:left bottom">encolhe</span></div>
      <div id="cu-rec" class="sheet" style="left:200px; top:620px; width:610px; height:640px; transform:rotate(2.5deg); padding:40px 44px; font-family:'Space Mono',monospace; font-size:28px; line-height:1.5; color:{INK}; clip-path:{zigzag()}">
        <div style="text-align:center; font-weight:700; letter-spacing:.16em">*** FESTA DE SÁBADO ***</div>
        <div style="border-top:3px dashed {INK}; margin:18px 0 12px"></div>
        {rl}
        <div style="border-top:3px dashed {INK}; margin:14px 0"></div>
        <div id="cu-sob" style="display:flex; justify-content:space-between; font-weight:700; font-size:40px"><span>SOBROU</span><span style="color:{EMBER_TXT}">???</span></div>
        <div class="cu-ln" style="text-align:center; margin-top:26px; font-size:28px; color:{SOFT}">obrigado pela visibilidade</div>
      </div>
"""
js = HEADJS(sid) + blur_words('#cu-t .w', .1) + \
    f'      tl.fromTo("#cu-enc", {{ scaleX: 1, scaleY: 1 }}, {{ scaleX: .72, scaleY: .72, duration: .5, ease: "expo.out" }}, 1.45);\n' + \
    f'      tl.fromTo("#cu-rec", {{ y: 700, rotation: -2 }}, {{ y: 0, rotation: 2.5, duration: .55, ease: "expo.out" }}, .35);\n' + \
    f'      tl.fromTo("#cu-rec .cu-ln", {{ opacity: 0 }}, {{ opacity: 1, duration: .05, stagger: .3 }}, .8);\n' + \
    f'      tl.fromTo("#cu-sob", {{ opacity: 0, scale: 1.3 }}, {{ opacity: 1, scale: 1, duration: .25, ease: "back.out(2)" }}, 2.75);\n' + \
    f'      tl.to("#cu-rec", {{ y: -1500, rotation: -6, duration: .35, ease: "power3.in" }}, {round(d - .38, 3)});\n' + \
    f'      tl.to("#cu-t, #cupom-tag, #cupom-num", {{ opacity: 0, filter: "blur(8px)", duration: .2, ease: "power3.in" }}, {round(d - .25, 3)});\n'
sfx('whoosh-short', sid, .45, .3)
SFX.append(('typing', round(start_of(sid) + .8, 3), .3))
sfx('pop', sid, 2.8, .45)
sfx('whoosh', sid, d - .12, .45)
scene(sid, body, js)

# 06 som ------------------------------------------------------------
sid = 'som'; d = dur_of(sid)
body = head(sid, 'o que ninguém vê', 6) + f"""      <div id="sm-t" class="h" style="top:380px; font-size:112px">{words('e quem mais | perde é o <or>som</or>')}</div>
      <div id="sm-vin" style="position:absolute; left:200px; top:660px; width:640px; height:640px; --a: 0deg">
        <img src="assets/vinil-laranja.png" style="position:absolute; inset:0; width:100%; -webkit-mask: conic-gradient(from -20deg, #000 0 var(--a), transparent var(--a)); mask: conic-gradient(from -20deg, #000 0 var(--a), transparent var(--a))">
        <img src="assets/vinil.png" style="position:absolute; inset:0; width:100%; -webkit-mask: conic-gradient(from -20deg, transparent 0 var(--a), #000 var(--a)); mask: conic-gradient(from -20deg, transparent 0 var(--a), #000 var(--a))">
        <div style="position:absolute; inset:34%; border-radius:50%; border:5px solid {INK}"></div>
      </div>
      <div id="sm-l1" class="hand" style="position:absolute; left:680px; top:640px; font-size:58px; color:{EMBER_TXT}; transform:rotate(6deg)">o corre</div>
      <div id="sm-l2" class="hand" style="position:absolute; left:135px; top:680px; font-size:58px; color:{INK}; transform:rotate(-5deg)">a música</div>
      <svg class="draw" style="left:170px; top:750px" width="200" height="130"><path id="sm-a2" class="ln" pathLength="1" style="stroke-dasharray:1" d="M10 10 C 40 80, 110 100, 180 92 M180 92 l -30 -22 M180 92 l -26 24"/></svg>
"""
js = HEADJS(sid) + grey_words('#sm-t .w', .1, .08) + \
    f'      tl.fromTo("#sm-vin", {{ "--a": "0deg", scale: .85, opacity: 0 }}, {{ "--a": "290deg", scale: 1, opacity: 1, duration: 1.3, ease: "power2.inOut" }}, .2);\n' + \
    f'      tl.fromTo("#sm-vin", {{ rotation: 0 }}, {{ rotation: 25, duration: {d}, ease: "none" }}, 0);\n' + \
    blur_words('#sm-l1', 1.0) + blur_words('#sm-l2', 1.6) + draw('#sm-a2', 1.7, .4) + blur_out(sid, d)
sfx('whoosh-short', sid, .3, .3)
sfx('glitch-3', sid, 1.75, .25)
scene(sid, body, js)

# 07 erra -----------------------------------------------------------
sid = 'erra'; d = dur_of(sid)
labs = [('er-a', 'press kit velho', 130, 700, -4, 2.0), ('er-b', 'rider desatualizado', 330, 840, 3, 3.05),
        ('er-c', 'mensagem respondida<br>3 dias depois', 150, 990, -1.5, 4.35)]
lb = ''.join(f'      <div id="{i}" class="sheet" style="left:{x}px; top:{y}px; padding:26px 34px; transform:rotate({r}deg); font-family:Inter; font-size:44px; font-weight:800; line-height:1.1; color:{INK}">{t}<div class="tape" style="left:30%; top:-24px; width:130px; transform:rotate({-r * 2}deg)"></div></div>\n' for i, t, x, y, r, _ in labs)
body = head(sid, 'autocrítica', 7, True) + f"""      <img id="er-dot" src="assets/mancha-laranja.png" style="position:absolute; left:520px; top:900px; width:620px; mix-blend-mode:multiply">
      <div id="er-t" class="h" style="top:380px; font-size:116px">mas a gente<br>também <span class="or">erra</span></div>
{lb}"""
js = HEADJS(sid) + line_blur('#er-t', .1) + f'      tl.fromTo("#er-dot", {{ opacity: 0, scale: .6 }}, {{ opacity: 1, scale: 1, duration: .9, ease: "expo.out" }}, .3);\n' + \
    ''.join(f'      tl.fromTo("#{i}", {{ opacity: 0, y: -60, scale: 1.15, rotation: {r * 3} }}, {{ opacity: 1, y: 0, scale: 1, rotation: {r}, duration: .45, ease: "back.out(1.4)" }}, {t - .1});\n' for i, _, _, _, r, t in labs) + \
    blur_out(sid, d)
for _, _, _, _, _, t in labs:
    sfx('click-soft', sid, t + .05, .45)
sfx('whoosh-short', sid, 2.0, .18)
scene(sid, body, js)

# 08 acordo ---------------------------------------------------------
sid = 'acordo'; d = dur_of(sid)
fields = ['data e horário', 'cachê e prazo do pix', 'sinal e cancelamento', 'transporte', 'equipamento', 'contato no dia']
FT = [4.45, 4.75, 5.05, 5.35, 5.6, 5.8]
fl = ''.join(f'<div style="padding:14px 0 8px; border-bottom:2px solid #bdb5a5"><span class="box" style="border-color:{EMBER_TXT}; width:30px; height:30px">{tick(i).replace("TK", "ac-tk")}</span>{f}</div>' for i, f in enumerate(fields))
body = head(sid, 'ideia 1', 8) + f"""      <div id="ac-t" class="h" style="top:380px; font-size:92px">{words('o que eu acho que | dá pra <or>fazer</or>')}</div>
      <div id="ac-form" class="sheet" style="left:135px; top:610px; width:560px; height:620px; transform:rotate(-2deg); padding:38px 40px; color:{INK}">
        <div class="mono" style="font-size:28px; display:flex; justify-content:space-between"><span>acordo de 1 página</span></div>
        <div style="border-top:4px solid {INK}; margin:14px 0 4px"></div>
        <div style="font-family:Inter; font-size:32px; font-weight:600">{fl}</div>
      </div>
      <div id="ac-tape" class="tape" style="left:320px; top:588px; transform:rotate(3deg)"></div>
      <div id="ac-note" class="hand" style="position:absolute; left:705px; top:780px; width:170px; font-size:46px; line-height:.95; color:{EMBER_TXT}; transform:rotate(-4deg)">manda no zap e guarda o print</div>
      <svg class="draw" style="left:690px; top:1010px" width="140" height="140"><path id="ac-arrow" class="ln or" pathLength="1" style="stroke-dasharray:1" d="M70 10 C 90 60, 70 100, 15 120 M15 120 l 34 4 M15 120 l 14 -30"/></svg>
"""
js = HEADJS(sid) + blur_words('#ac-t .w', .1) + arrive('#ac-form', 3.0, 'y: 300, rotation: 6', -2) + \
    f'      tl.fromTo("#ac-tape", {{ opacity: 0, scale: 1.3 }}, {{ opacity: 1, scale: 1, duration: .2, ease: "power3.out" }}, 3.4);\n' + \
    ''.join(draw(f'#ac-tk{i}', t, .16) for i, t in enumerate(FT)) + blur_words('#ac-note', 4.6) + draw('#ac-arrow', 4.85, .4) + blur_out(sid, d)
sfx('whoosh-short', sid, 3.1, .3)
for i, t in enumerate(FT):
    sfx('click' if i % 2 else 'click-soft', sid, t + .08, .35)
scene(sid, body, js)

# 09 risco ----------------------------------------------------------
sid = 'risco'; d = dur_of(sid)
body = head(sid, 'ideias 2 e 3', 9) + f"""      <div id="ri-t" class="h" style="top:380px; font-size:104px">{words('e dá pra dividir | o <or>risco</or>')}</div>
      <div id="ri-a" class="sheet" style="left:135px; top:650px; width:390px; height:350px; padding:36px 32px; transform:rotate(-1.5deg); color:{INK}">
        <span class="mono" style="display:inline-block; background:{EMBER}; border-radius:999px; padding:8px 22px; font-size:28px">piso + bônus</span>
        <p style="font-family:Inter; font-size:36px; line-height:1.25; font-weight:500; margin-top:26px">Cachê mínimo garantido. <b>Se bombar, uma parte da porta.</b></p>
      </div>
      <div id="ri-b" class="sheet" style="left:525px; top:690px; width:350px; height:350px; padding:36px 32px; transform:rotate(1.5deg); color:{INK}">
        <span class="mono" style="display:inline-block; background:{INK}; color:{PAPER}; border-radius:999px; padding:8px 22px; font-size:28px">coletivo</span>
        <p style="font-family:Inter; font-size:36px; line-height:1.25; font-weight:500; margin-top:26px">Quatro, cinco DJs <b>dividindo um booker.</b></p>
      </div>
"""
js = HEADJS(sid) + grey_words('#ri-t .w', .1) + arrive('#ri-a', 1.7, 'x: -420, rotation: -8', -1.5, .55) + arrive('#ri-b', 3.1, 'x: 420, rotation: 8', 1.5, .55) + blur_out(sid, d)
sfx('whoosh-short', sid, 1.85, .3)
sfx('whoosh', sid, 3.25, .3)
scene(sid, body, js)

# 10 sinal ----------------------------------------------------------
sid = 'sinal'; d = dur_of(sid)
body = f"""      <div id="si-flood" style="position:absolute; inset:0; background:{EMBER}"></div>
      <img id="si-dot" src="assets/mancha-preta.png" style="position:absolute; left:280px; top:420px; width:900px; mix-blend-mode:multiply; opacity:.35">
      <div id="si-t" class="h" style="top:420px; font-size:186px; line-height:.86"><span class="w">sinal</span><br><span class="w">pago,</span><br><span class="w">set</span><br><span class="w serif" style="font-weight:400; letter-spacing:-.02em">pensado.</span></div>
"""
WT = [.15, .6, 1.05, 1.3]
js = f'      tl.fromTo("#si-flood", {{ clipPath: "circle(0% at 50% 45%)" }}, {{ clipPath: "circle(120% at 50% 45%)", duration: .4, ease: "power2.inOut" }}, 0);\n' + \
    f'      tl.fromTo("#si-dot", {{ scale: .7, opacity: 0 }}, {{ scale: 1, opacity: .35, duration: 1.2, ease: "expo.out" }}, .1);\n' + \
    ''.join(f'      tl.fromTo("#si-t .w:nth-of-type({i + 1})", {{ opacity: 0, scale: 1.25, filter: "blur(10px)" }}, {{ opacity: 1, scale: 1, filter: "blur(0px)", duration: .22, ease: "expo.out" }}, {t});\n' for i, t in enumerate(WT)) + \
    f'      tl.to(S, {{ clipPath: "inset(0 0 100% 0)", duration: .35, ease: "power3.in" }}, {round(d - .37, 3)});\n'
SFX.append(('impact-bass-2', round(start_of(sid) + .15, 3), .3))
sfx('whoosh-short', sid, d - .2, .3)
scene(sid, body.replace('class="w"', 'class="w" style="transform-origin:left center"'), js)

# 11 cena -----------------------------------------------------------
sid = 'cena'; d = dur_of(sid)
qs = ['já fechou data sem nada por escrito?', 'o que não pode faltar no seu acordo?', 'e o público, tem culpa nisso!?']
ql = ''.join(f'<div class="ce-q" style="display:flex; gap:22px; align-items:baseline; padding:20px 0; border-top:4px solid {INK}"><span class="mono" style="font-size:28px; color:{EMBER_TXT}">0{i + 1}</span>{q}</div>' for i, q in enumerate(qs))
body = head(sid, 'sua vez', 11, True) + f"""      <div id="ce-t" class="h" style="top:380px; font-size:112px">e aí, como é<br>na sua <span class="or">cena?</span></div>
      <div id="ce-qs" style="position:absolute; left:135px; width:745px; top:640px; font-family:Inter; font-weight:800; font-size:42px; letter-spacing:-.03em; line-height:1.08; color:{INK}">{ql}</div>
      <div id="ce-note" class="hand" style="position:absolute; left:430px; top:1010px; font-size:46px; color:{EMBER_TXT}; transform:rotate(-4deg)">↑ fica pro próximo post</div>
      <img id="ce-logo" src="assets/wordmark-preto.png" alt="Ätzøk" style="position:absolute; left:135px; top:1110px; height:90px">
      <div id="ce-cta" class="mono" style="position:absolute; left:330px; top:1150px; font-size:30px; color:{INK}">comenta aí · @_atzok</div>
"""
QT = [.7, 1.2, 1.7]
js = HEADJS(sid) + line_blur('#ce-t', .05) + \
    ''.join(f'      tl.fromTo("#ce-qs .ce-q:nth-child({i + 1})", {{ opacity: 0, x: -40 }}, {{ opacity: 1, x: 0, duration: .4, ease: "expo.out" }}, {t});\n' for i, t in enumerate(QT)) + \
    blur_words('#ce-note', 1.9) + line_blur('#ce-logo, #ce-cta', 1.6)
for t in QT:
    sfx('pop', sid, t + .05, .35)
scene(sid, body, js)

# ================= root =================
hosts = '\n'.join(
    f'      <div id="{s}" data-composition-id="{s}" data-composition-src="compositions/{s}.html" data-start="{st}" data-duration="{dur_of(s)}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>'
    for s, st in SCENES)
voices = '\n'.join(f'      <audio id="voz-{v}" class="clip" src="assets/voice/{v}.wav" data-start="{t}" data-duration="{VOICE_DUR[v]}" data-track-index="4" data-volume="1"></audio>' for v, t in VOICE)
sf = []
for k, (name, hit, vol) in enumerate(sorted(SFX, key=lambda x: x[1])):
    st = max(0, round(hit - SFX_PEAK[name] + .033, 3))
    du = round(min(SFX_DUR[name], END - st), 3)
    sf.append(f'      <audio id="sfx{k + 1:02d}" class="clip" src="assets/sfx/{name}.mp3" data-start="{st}" data-duration="{du}" data-track-index="{5 + k % 3}" data-volume="{vol}"></audio>')
sfx_html = '\n'.join(sf)

index = f"""<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      :root {{ --paper: {PAPER}; --ink: {INK}; --ember: {EMBER}; }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: var(--paper); }}
      #root {{ position: relative; width: 100%; height: 100%; background: var(--paper); }}
      #papel {{ position: absolute; inset: 0; background: url('assets/papel-9x16.jpg') center / cover; }}
      #grao {{ position: absolute; inset: 0; background: url('assets/papel-9x16.jpg') center / cover; mix-blend-mode: multiply; opacity: .5; z-index: 50; pointer-events: none; }}
      .crop {{ position: absolute; width: 40px; height: 40px; border: 0 solid var(--ink); z-index: 40; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920">
      <div id="papel"></div>
      <img id="disco" class="clip" src="assets/vinil-selo.png" alt="" data-start="{start_of('sozinho')}" data-duration="{round(start_of('sinal') - start_of('sozinho'), 3)}" data-track-index="2" style="position:absolute; left:520px; top:1460px; width:900px; height:900px">
{hosts}
      <div class="crop" style="left:48px; top:48px; border-left-width:4px; border-top-width:4px"></div>
      <div class="crop" style="right:48px; top:48px; border-right-width:4px; border-top-width:4px"></div>
      <div class="crop" style="left:48px; bottom:48px; border-left-width:4px; border-bottom-width:4px"></div>
      <div class="crop" style="right:48px; bottom:48px; border-right-width:4px; border-bottom-width:4px"></div>
      <div id="grao"></div>
{voices}
{sfx_html}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#disco", {{ y: 500, rotation: 0 }}, {{ y: 0, rotation: 30, duration: .8, ease: "expo.out" }}, {start_of('sozinho')});
      tl.to("#disco", {{ rotation: 300, duration: {round(start_of('sinal') - start_of('sozinho') - .8, 3)}, ease: "none" }}, {round(start_of('sozinho') + .8, 3)});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
open(os.path.join(ROOT, 'index.html'), 'w').write(index)
print('cenas:', len(SCENES), 'sfx:', len(SFX))
