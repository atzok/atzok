"""Builds index.html and compositions/*.html for the 'Onde o clube encontra a rave' reel.
Edit the scene markup/timelines here and re-run: python3 gen.py"""
import math, os

W, H = 1080, 1920
X0, CW = 120, 780  # text column (inside Reels safe zone)
C = dict(lav="#6A75F2", lilac="#BCC2F6", pink="#EE69DA", yel="#EDF06F", mint="#9EDAA3",
         wool="#E6DFCD", paper="#F4EFE2", ink="#151515")

SCENES = [  # id, duration
    ("s1", 4.6), ("s2", 5.6), ("s3", 8.0), ("s4", 5.8), ("s5", 6.0), ("s6", 7.0)]

GRAIN = ("url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'>"
         "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3' stitchTiles='stitch'/>"
         "<feColorMatrix values='0 0 0 0 .5  0 0 0 0 .45  0 0 0 0 .4  0 0 0 .55 0'/></filter>"
         "<rect width='300' height='300' filter='url(%23n)'/></svg>\")")


def shared(p, bg, fg, dark=False):
    """CSS shared by every scene. p = id prefix."""
    return f"""
    @font-face {{ font-family: Adca; src: url('assets/fonts/Adca.ttf'); }}
    @font-face {{ font-family: LhMono; src: url('assets/fonts/DMMono-Regular.ttf'); }}
    #root {{ position: absolute; inset: 0; overflow: hidden; background: {bg}; color: {fg}; font-family: Adca; }}
    #root .grain {{ position: absolute; inset: 0; z-index: 40; pointer-events: none; background-image: {GRAIN};
      opacity: {'.10' if dark else '.22'}; mix-blend-mode: {'screen' if dark else 'multiply'}; }}
    #root .mono {{ font-family: LhMono; text-transform: uppercase; letter-spacing: .16em; font-size: 24px; }}
    #root .abs {{ position: absolute; }}
    #root .hd {{ position: absolute; left: {X0}px; width: {CW}px; top: 300px; height: 40px; display: flex;
      justify-content: space-between; align-items: center; z-index: 6; }}
    #root .hd .t {{ display: flex; align-items: center; gap: 14px; }}
    #root .hd .dot {{ width: 18px; height: 18px; border-radius: 50%; background: {C['pink']}; border: 3px solid currentColor; }}
    #root .cnt {{ display: flex; gap: .5em; }}
    #root .roll {{ display: inline-block; height: 1.25em; overflow: hidden; vertical-align: top; }}
    #root .roll span {{ display: block; line-height: 1.25em; }}
    #root .rule {{ position: absolute; left: {X0}px; width: {CW}px; top: 352px; height: 4px; background: currentColor; transform-origin: 0 50%; z-index: 6; }}
    #root .big {{ position: absolute; left: {X0}px; white-space: nowrap; text-transform: uppercase; line-height: .86; }}
    #root .reg {{ color: {C['lav']}; text-shadow: .045em .045em 0 {C['pink']}; }}
    #root .w {{ display: inline-block; }}
    #root .band {{ position: absolute; left: 0; width: {W}px; background-size: auto 100%; background-repeat: repeat-x; }}
    #root .b-azul {{ background-image: url('assets/img/fundo-azul.jpg'); }}
    #root .b-amar {{ background-image: url('assets/img/fundo-amarelo.jpg'); }}
    #root .wipe {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; z-index: 30; }}
    """


def header(p, n, prev):
    return f"""
    <div id="{p}-hd" class="hd mono">
      <span id="{p}-hdt" class="t"><i id="{p}-hdd" class="dot"></i>Onde o clube encontra a rave</span>
      <span class="cnt"><span class="roll"><span id="{p}-roll"><span>{prev}</span><span>{n}</span></span></span><span>/ 6</span></span>
    </div>
    <div id="{p}-rule" class="rule"></div>"""


def header_tl(p, t=0.0):
    return f"""
      tl.fromTo("#{p}-rule", {{scaleX: 0}}, {{scaleX: 1, duration: 0.7, ease: "expo.out"}}, {t});
      tl.fromTo("#{p}-hdt", {{opacity: 0, x: -24}}, {{opacity: 1, x: 0, duration: 0.5, ease: "expo.out"}}, {t + 0.05});
      tl.fromTo("#{p}-hdd", {{scale: 0}}, {{scale: 1, duration: 0.45, ease: "back.out(2.2)"}}, {t + 0.15});
      tl.fromTo("#{p}-roll", {{yPercent: 0}}, {{yPercent: -50, duration: 0.55, ease: "expo.inOut"}}, {t + 0.25});"""


def words(text, cls="w", idp=None):
    out = []
    for i, w in enumerate(text.split(" ")):
        out.append(f'<span class="{cls}">{w}</span>')
    return " ".join(out)


def scene(sid, dur, css, body, script, bg, fg, dark=False):
    return f"""<template>
  <style>{shared(sid, bg, fg, dark)}{css}
  </style>
  <div id="root" data-composition-id="{sid}" data-width="{W}" data-height="{H}">
    <div id="{sid}-stage" class="clip" data-start="0" data-duration="{dur}" data-track-index="1" data-layout-allow-overflow data-layout-allow-overlap style="position:absolute;inset:0">
{body}
      <div class="grain" data-layout-ignore></div>
    </div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
{script}
      window.__timelines["{sid}"] = tl;
    }})();
  </script>
</template>
"""


out = {}

# ---------------------------------------------------------------- S1 cover
p = "s1"
route_y = 985
stops = [X0 + 14 + i * (CW - 28) / 3 for i in range(4)]
labels = ["Houghton", "MoDem", "Pulsar", "Veludo"]
css1 = f"""
    #s1-kick {{ left: {X0}px; top: 404px; font-size: 64px; color: {C['lav']}; }}
    #s1-l1 {{ top: 488px; font-size: 112px; }}
    #s1-l2 {{ top: 596px; font-size: 148px; }}
    #s1-l3 {{ top: 736px; font-size: 226px; }}
    #s1-route {{ left: 0; top: 0; width: {W}px; height: {H}px; overflow: visible; }}
    #root .lbl {{ position: absolute; top: {route_y + 34}px; width: 230px; }}
    #s1-arco {{ left: 210px; top: 1060px; width: 660px; z-index: 2; }}
    #s1-band {{ top: 1590px; height: 330px; z-index: 3; border-top: 7px solid {C['ink']}; background-position: 0 0; }}
    #s1-iris {{ background: {C['lav']}; clip-path: circle(0px at 612px 1218px); }}
"""
def _lbl(i):
    if i == 0: return f"left:{X0}px;text-align:left"
    if i == 3: return f"left:{X0 + CW - 230}px;text-align:right"
    return f"left:{stops[i]-115:.0f}px;text-align:center"
lbl_html = "".join(f'<div id="s1-lb{i}" class="lbl mono abs" style="{_lbl(i)}">{labels[i]}</div>' for i in range(4))
dots = "".join(f'<circle id="s1-d{i}" cx="{stops[i]}" cy="{route_y}" r="13" fill="{[C["pink"], C["lav"], C["lav"], C["pink"]][i]}" stroke="{C["ink"]}" stroke-width="5"/>' for i in range(4))
body1 = header(p, 1, 0) + f"""
      <div id="s1-kick" class="abs">um mapa de</div>
      <div id="s1-l1" class="big"><span class="w">Onde</span> <span class="w">o</span> <span class="w">clube</span></div>
      <div id="s1-l2" class="big"><span class="w">Encontra</span></div>
      <div id="s1-l3" class="big reg">A rave</div>
      <svg id="s1-route" class="abs" viewBox="0 0 {W} {H}">
        <line id="s1-rl" x1="{stops[0]}" y1="{route_y}" x2="{stops[3]}" y2="{route_y}" stroke="{C['ink']}" stroke-width="4" stroke-dasharray="2 14" stroke-linecap="round"/>
        {dots}
      </svg>
      {lbl_html}
      <img id="s1-arco" class="abs" src="assets/img/arco.png" alt="Lhama">
      <div id="s1-band" class="band b-azul"></div>
      <div id="s1-iris" class="wipe"></div>"""
scr1 = header_tl(p, 0.0) + f"""
      // frame 0 already shows the title (thumbnail); registration shadow snaps in
      tl.fromTo("#s1-l3", {{textShadow: "0em 0em 0 {C['pink']}", scale: 1.06, transformOrigin: "0% 100%"}}, {{textShadow: ".045em .045em 0 {C['pink']}", scale: 1, duration: 0.6, ease: "back.out(2)"}}, 0.1);
      tl.fromTo("#s1-kick", {{opacity: 0, filter: "blur(8px)"}}, {{opacity: 1, filter: "blur(0px)", duration: 0.25, ease: "power4.out"}}, 0.3);
      // the route draws and its stops pop
      tl.fromTo("#s1-rl", {{attr: {{x2: {stops[0]}}}}}, {{attr: {{x2: {stops[3]}}}, duration: 0.9, ease: "power2.inOut"}}, 0.55);
      {"".join(f'tl.fromTo("#s1-d{i}", {{scale: 0, transformOrigin: "50% 50%"}}, {{scale: 1, duration: 0.4, ease: "back.out(2.6)"}}, {0.55 + i * 0.27:.2f});' for i in range(4))}
      {"".join(f'tl.fromTo("#s1-lb{i}", {{opacity: 0, y: 14}}, {{opacity: 1, y: 0, duration: 0.35, ease: "expo.out"}}, {0.62 + i * 0.27:.2f});' for i in range(4))}
      // the llama rises out of the waves
      tl.fromTo("#s1-arco", {{y: 560}}, {{y: 0, duration: 1.1, ease: "expo.out"}}, 0.9);
      tl.fromTo("#s1-band", {{backgroundPositionX: 0}}, {{backgroundPositionX: -260, duration: 4.6, ease: "none"}}, 0);
      // exit: lavender iris opens from the headphone
      tl.fromTo("#s1-iris", {{clipPath: "circle(0px at 612px 1218px)"}}, {{clipPath: "circle(2300px at 612px 1218px)", duration: 0.62, ease: "power3.in"}}, 3.95);"""
out[p] = scene(p, 4.6, css1, body1, scr1, C["paper"], C["ink"])

# ---------------------------------------------------------------- S2 Houghton
p = "s2"
wv_top, wv_bot, wv_w = 46, 186, CW
pts = []
for x in range(0, wv_w + 1, 4):
    y = (wv_top + wv_bot) / 2 + (wv_bot - wv_top) / 2 * math.cos(x / (wv_w / 4) * 2 * math.pi)
    pts.append(f"{'L' if x else 'M'}{x} {y:.1f}")
wave_d = "".join(pts)
suns = "".join(f'<circle id="s2-sun{i}" cx="{i*wv_w/4+wv_w/8:.1f}" cy="{wv_top}" r="22" fill="{C["paper"]}" stroke="{C["ink"]}" stroke-width="5"/>' for i in range(4))
moons = "".join(f'<circle id="s2-moon{i}" cx="{i*wv_w/4:.1f}" cy="{wv_bot}" r="19" fill="{C["pink"]}" stroke="{C["ink"]}" stroke-width="5"/>' for i in range(5))
grid = "".join(f'<line x1="{i*wv_w/4:.1f}" y1="0" x2="{i*wv_w/4:.1f}" y2="236" stroke="{C["lilac"]}" stroke-width="2" stroke-dasharray="2 9" stroke-linecap="round"/>'
               f'<text id="s2-day{i}" x="{i*wv_w/4+18:.1f}" y="232" fill="{C["paper"]}" font-family="LhMono" font-size="26" letter-spacing="4">{d}</text>'
               for i, d in enumerate(["QUI", "SEX", "SÁB", "DOM"]))
css2 = f"""
    #s2-loc {{ left: {X0}px; top: 392px; color: {C['paper']}; opacity: .85; }}
    #s2-t1 {{ top: 448px; font-size: 120px; color: {C['paper']}; }}
    #s2-t2 {{ top: 556px; font-size: 100px; color: {C['yel']}; text-shadow: .045em .045em 0 {C['pink']}; }}
    #s2-stats {{ left: {X0}px; top: 708px; width: {CW}px; display: grid; grid-template-columns: 1fr 1fr; row-gap: 18px;
      border-top: 3px solid rgba(244,239,226,.35); padding-top: 26px; }}
    #root .st b {{ display: block; font-weight: 400; font-size: 84px; line-height: 1; color: {C['paper']}; }}
    #root .st span {{ display: block; font-family: LhMono; font-size: 25px; letter-spacing: .12em; color: {C['paper']}; opacity: .85; margin-top: 10px; text-transform: uppercase; }}
    #s2-wave {{ left: {X0}px; top: 984px; width: {wv_w}px; height: 240px; overflow: visible; }}
    #s2-band {{ top: 1480px; height: 440px; border-top: 7px solid {C['ink']}; }}
    #s2-wy {{ top: {H}px; height: {H}px; z-index: 31; background-size: auto 700px; background-repeat: repeat; border-top: 7px solid {C['ink']}; }}
    #s2-wc {{ top: {H}px; background: {C['paper']}; z-index: 32; border-top: 7px solid {C['ink']}; }}
"""
body2 = header(p, 2, 1) + f"""
      <div id="s2-loc" class="mono abs">Houghton — Norfolk, Inglaterra</div>
      <div id="s2-t1" class="big"><span class="w">Quatro</span> <span class="w">dias,</span></div>
      <div id="s2-t2" class="big"><span class="w">Som</span> <span class="w">sem</span> <span class="w">parar</span></div>
      <div id="s2-stats" class="abs">
        <div id="s2-st0" class="st"><b id="s2-n0">7-10.08</b><span>quinta a domingo</span></div>
        <div id="s2-st1" class="st"><b id="s2-n1">13</b><span>pistas</span></div>
        <div id="s2-st2" class="st"><b id="s2-n2">+200</b><span>artistas</span></div>
        <div id="s2-st3" class="st"><b id="s2-n3">24h</b><span>de som por dia</span></div>
      </div>
      <svg id="s2-wave" class="abs" viewBox="0 0 {wv_w} 240">
        {grid}
        <path id="s2-wsh" d="{wave_d}" fill="none" stroke="{C['ink']}" stroke-width="16" stroke-linecap="round" opacity=".3" transform="translate(5 5)"/>
        <path id="s2-wl" d="{wave_d}" fill="none" stroke="{C['yel']}" stroke-width="12" stroke-linecap="round"/>
        {suns}{moons}
        <text id="s2-dia" x="{wv_w/8+34:.1f}" y="{wv_top+14}" fill="{C['paper']}" font-family="Adca" font-size="40">dia</text>
        <text id="s2-noite" x="{wv_w/4+28:.1f}" y="{wv_bot+14}" fill="{C['paper']}" font-family="Adca" font-size="40">noite</text>
      </svg>
      <div id="s2-band" class="band b-amar"></div>
      <div id="s2-wy" class="wipe band b-amar"></div>
      <div id="s2-wc" class="wipe"></div>"""
counters = []
for i, (a, b, fmt) in enumerate([(0, 13, "{}"), (0, 200, "+{}"), (0, 24, "{}h")]):
    counters.append(f'(function(){{const o={{v:{a}}},el=document.getElementById("s2-n{i+1}");'
                    f'tl.fromTo(o,{{v:{a}}},{{v:{b},duration:1.1,ease:"power3.out",onUpdate(){{el.textContent="{fmt}".replace("{{}}",Math.round(o.v));}}}},{1.05+i*0.12:.2f});}})();')
scr2 = header_tl(p, 0.05) + f"""
      tl.fromTo("#s2-loc", {{opacity: 0, x: -30}}, {{opacity: 1, x: 0, duration: 0.5, ease: "expo.out"}}, 0.2);
      tl.fromTo("#s2-t1 .w", {{opacity: 0, filter: "blur(8px)", y: 40}}, {{opacity: 1, filter: "blur(0px)", y: 0, duration: 0.5, ease: "expo.out", stagger: 0.09}}, 0.28);
      tl.fromTo("#s2-t2 .w", {{opacity: 0, filter: "blur(8px)", y: 40}}, {{opacity: 1, filter: "blur(0px)", y: 0, duration: 0.5, ease: "expo.out", stagger: 0.09}}, 0.5);
      tl.fromTo("#s2-t2", {{textShadow: "0em 0em 0 {C['pink']}"}}, {{textShadow: ".045em .045em 0 {C['pink']}", duration: 0.4, ease: "back.out(2)"}}, 0.85);
      tl.fromTo("#s2-stats", {{borderTopColor: "rgba(244,239,226,0)"}}, {{borderTopColor: "rgba(244,239,226,.35)", duration: 0.4}}, 0.9);
      tl.fromTo("#s2-stats .st", {{opacity: 0, y: 30}}, {{opacity: 1, y: 0, duration: 0.5, ease: "expo.out", stagger: 0.1}}, 0.95);
      {''.join(counters)}
      // day/night wave draws across the four days
      (function(){{const L=document.getElementById("s2-wl").getTotalLength();
        ["#s2-wl","#s2-wsh"].forEach(s=>tl.fromTo(s,{{strokeDasharray:L,strokeDashoffset:L}},{{strokeDashoffset:0,duration:1.6,ease:"power1.inOut"}},1.5));}})();
      tl.fromTo("#s2-wave text[id^=s2-day]", {{opacity: 0}}, {{opacity: 1, duration: 0.3, stagger: 0.35}}, 1.4);
      {"".join(f'tl.fromTo("#s2-moon{i}", {{scale: 0, transformOrigin: "50% 50%"}}, {{scale: 1, duration: 0.35, ease: "back.out(2.6)"}}, {1.5 + i*0.4:.2f});' for i in range(5))}
      {"".join(f'tl.fromTo("#s2-sun{i}", {{scale: 0, transformOrigin: "50% 50%"}}, {{scale: 1, duration: 0.35, ease: "back.out(2.6)"}}, {1.7 + i*0.4:.2f});' for i in range(4))}
      tl.fromTo("#s2-dia", {{opacity: 0, y: 12}}, {{opacity: 1, y: 0, duration: 0.35, ease: "expo.out"}}, 1.85);
      tl.fromTo("#s2-noite", {{opacity: 0, y: -12}}, {{opacity: 1, y: 0, duration: 0.35, ease: "expo.out"}}, 2.1);
      tl.fromTo("#s2-band", {{y: 440}}, {{y: 0, duration: 0.9, ease: "expo.out"}}, 0.4);
      tl.fromTo("#s2-band", {{backgroundPositionX: 0}}, {{backgroundPositionX: 260, duration: 5.6, ease: "none"}}, 0);
      // exit: yellow then cream sheet sweep up
      tl.fromTo("#s2-wy", {{y: 0}}, {{y: -{H}, duration: 0.5, ease: "power3.in"}}, 5.0);
      tl.fromTo("#s2-wc", {{y: 0}}, {{y: -{H}, duration: 0.5, ease: "power3.in"}}, 5.08);"""
out[p] = scene(p, 5.6, css2, body2, scr2, C["lav"], C["paper"])

# ---------------------------------------------------------------- S3 MoDem
p = "s3"
band_t, band_h = 570, 300
body_words = "O MoDem tem três pistas. A Hive toca psy rápido, a Seed fica com chill e downtempo. No meio, a Swamp desce o BPM até encontrar o techno."
bw = " ".join(f'<span class="bw{" hl" if w.startswith("Swamp") else ""}">{w}</span>' for w in body_words.split(" "))
css3 = f"""
    #s3-loc {{ left: {X0}px; top: 392px; color: {C['lav']}; }}
    #s3-t {{ top: 448px; font-size: 98px; }}
    #s3-band {{ top: 0; height: {H}px; z-index: 7; clip-path: inset({band_t}px 0px {H-band_t-band_h}px 0px); }}
    #s3-bl {{ left: 0; width: {W}px; height: 7px; background: {C['ink']}; z-index: 5; }}
    #s3-sw {{ left: 0; width: {W}px; top: {band_t}px; height: {band_h}px; display: flex; justify-content: center; align-items: center; z-index: 9; }}
    #s3-sw span {{ display: inline-block; font-size: 210px; line-height: 1; color: {C['paper']}; -webkit-text-stroke: 7px {C['ink']}; paint-order: stroke fill; text-shadow: 13px 13px 0 {C['pink']}; }}
    #s3-tags {{ left: {X0}px; width: {CW-20}px; top: 912px; display: flex; justify-content: space-between; color: {C['lav']}; }}
    #s3-tags span {{ display: inline-block; }}
    #s3-r2 {{ left: {X0}px; width: {CW}px; top: 962px; height: 4px; background: {C['ink']}; transform-origin: 0 50%; }}
    #s3-body {{ left: {X0}px; width: {CW}px; top: 994px; font-size: 37px; line-height: 1.24; }}
    #root .bw {{ display: inline-block; }}
    #root .bw.hl {{ color: {C['lav']}; }}
"""
body3 = header(p, 3, 2) + f"""
      <div id="s3-loc" class="mono abs">MoDem — Primišlje, Croácia</div>
      <div id="s3-t" class="big"><span class="w">A</span> <span class="w">pista</span> <span class="w">do</span> <span class="w">meio</span></div>
      <div id="s3-band" class="band b-azul"></div>
      <div id="s3-blt" class="abs" style="left:0;width:{W}px;height:7px;background:{C['ink']};top:{band_t-7}px;z-index:8"></div>
      <div id="s3-blb" class="abs" style="left:0;width:{W}px;height:7px;background:{C['ink']};top:{band_t+band_h}px;z-index:8"></div>
      <div id="s3-sw" class="abs">{''.join(f'<span>{c}</span>' for c in 'SWAMP')}</div>
      <div id="s3-tags" class="mono abs"><span>Dark prog</span><span>Zenon</span><span>Techno</span><span>Minimal</span></div>
      <div id="s3-r2" class="abs"></div>
      <p id="s3-body" class="abs">{bw}</p>"""
scr3 = header_tl(p, 0.05) + f"""
      tl.fromTo("#s3-loc", {{opacity: 0, x: -30}}, {{opacity: 1, x: 0, duration: 0.5, ease: "expo.out"}}, 0.2);
      tl.fromTo("#s3-t .w", {{opacity: 0, filter: "blur(8px)"}}, {{opacity: 1, filter: "blur(0px)", duration: 0.16, ease: "power4.out", stagger: 0.08}}, 0.3);
      // the swamp band wipes open from the left, letters drop in
      tl.fromTo("#s3-band", {{clipPath: "inset({band_t}px {W}px {H-band_t-band_h}px 0px)"}}, {{clipPath: "inset({band_t}px 0px {H-band_t-band_h}px 0px)", duration: 0.7, ease: "expo.inOut"}}, 0.55);
      tl.fromTo(["#s3-blt", "#s3-blb"], {{scaleX: 0, transformOrigin: "0% 50%"}}, {{scaleX: 1, duration: 0.7, ease: "expo.inOut"}}, 0.5);
      tl.fromTo("#s3-sw span", {{y: -260, rotation: -8, opacity: 0}}, {{y: 0, rotation: 0, opacity: 1, duration: 0.7, ease: "back.out(1.7)", stagger: 0.07}}, 0.95);
      tl.fromTo("#s3-band", {{backgroundPositionX: 0}}, {{backgroundPositionX: -360, duration: 8.0, ease: "none"}}, 0);
      tl.fromTo("#s3-tags span", {{opacity: 0, y: 20}}, {{opacity: 1, y: 0, duration: 0.4, ease: "expo.out", stagger: 0.08}}, 1.5);
      tl.fromTo("#s3-r2", {{scaleX: 0}}, {{scaleX: 1, duration: 0.6, ease: "expo.out"}}, 1.65);
      tl.fromTo("#s3-body .bw", {{opacity: 0}}, {{opacity: 1, duration: 0.25, ease: "power1.out", stagger: 0.06}}, 1.25);
      tl.fromTo("#s3-body .hl", {{scale: 1}}, {{scale: 1.12, duration: 0.18, yoyo: true, repeat: 1, ease: "power2.out"}}, 1.25 + 0.06 * {body_words.split(' ').index('Swamp')});
      // exit: the band swallows the screen
      tl.to("#s3-sw span", {{opacity: 0, filter: "blur(10px)", scale: 1.3, duration: 0.3, ease: "power3.in", stagger: 0.03}}, 7.3);
      tl.to("#s3-band", {{clipPath: "inset(0px 0px 0px 0px)", duration: 0.55, ease: "power3.inOut"}}, 7.4);
      tl.to("#s3-blt", {{y: -{band_t}, duration: 0.55, ease: "power3.inOut"}}, 7.4);
      tl.to("#s3-blb", {{y: {H-band_t-band_h}, duration: 0.55, ease: "power3.inOut"}}, 7.4);"""
out[p] = scene(p, 8.0, css3, body3, scr3, C["paper"], C["ink"])

# ---------------------------------------------------------------- S4 Pulsar
p = "s4"
AX, AY, AW, AH = 690, 700, 270, 480  # arch window
rows = [("Techno", "o clube", "hot"), ("Prog dark", "a ponte", "mid"), ("Forest", "", ""),
        ("Dark psy", "", ""), ("Hi-tech", "", ""), ("Psycore", "", "")]
rows_html = "".join(
    f'<div id="s4-row{i}" class="row {k}" style="top:{690 + i*82}px"><i id="s4-dot{i}"></i><span class="n">{n}</span>'
    + (f'<span class="a">{a}</span>' if a else "") + "</div>" for i, (n, a, k) in enumerate(rows))
css4 = f"""
    #s4-loc {{ left: {X0}px; top: 392px; color: {C['lav']}; }}
    #s4-t1 {{ top: 448px; font-size: 88px; }}
    #s4-t2 {{ top: 534px; font-size: 118px; }}
    #s4-spine {{ left: {X0+11}px; top: 720px; width: 5px; height: 410px; background: {C['ink']}; transform-origin: 50% 0; }}
    #root .row {{ position: absolute; left: {X0}px; height: 82px; display: flex; align-items: baseline; gap: 24px; white-space: nowrap; }}
    #root .row i {{ position: absolute; left: 0; top: 18px; width: 27px; height: 27px; border-radius: 50%; background: {C['paper']}; border: 5px solid {C['ink']}; }}
    #root .row .n {{ margin-left: 56px; font-size: 46px; color: rgba(21,21,21,.42); }}
    #root .row .a {{ font-size: 38px; color: {C['pink']}; }}
    #root .row.hot .n {{ color: {C['pink']}; font-size: 56px; }}
    #root .row.hot i {{ background: {C['pink']}; }}
    #root .row.mid .n {{ color: {C['lav']}; font-size: 56px; text-shadow: .04em .04em 0 {C['pink']}; }}
    #root .row.mid i {{ background: {C['lav']}; }}
    #s4-win {{ top: 0; height: {H}px; z-index: 20; background-size: auto 100%; background-repeat: repeat-x;
      clip-path: inset(0px 0px 0px 0px round 0px 0px 0px 0px); }}
    #s4-ring {{ left: {AX-7}px; top: {AY-7}px; width: {AW+14}px; height: {AH+7}px; border: 7px solid {C['ink']}; border-bottom: 7px solid {C['ink']};
      border-radius: {AW/2+7}px {AW/2+7}px 0 0; z-index: 22; }}
    #s4-headw {{ left: {AX}px; top: {AY}px; width: {AW}px; height: {AH}px; overflow: hidden; border-radius: {AW/2}px {AW/2}px 0 0; z-index: 21; }}
    #s4-head {{ position: absolute; left: 22px; top: 70px; width: 250px; }}
    #s4-r2 {{ left: {X0}px; width: {CW}px; top: 1190px; height: 4px; background: {C['ink']}; transform-origin: 0 50%; }}
    #s4-foot {{ left: {X0}px; top: 1206px; font-size: 22px; letter-spacing: .08em; }}
    #s4-iris {{ background: {C['yel']}; clip-path: circle(0px at {AX+150}px {AY+200}px); }}
"""
win_in = f"inset({AY}px {W-AX-AW}px {H-AY-AH}px {AX}px round {AW/2}px {AW/2}px 0px 0px)"
body4 = header(p, 4, 3) + f"""
      <div id="s4-loc" class="mono abs">Pulsar — Ipoema, MG</div>
      <div id="s4-t1" class="big"><span class="w">O</span> <span class="w">psy</span> <span class="w">mais</span> <span class="w">perto</span></div>
      <div id="s4-t2" class="big reg">Do techno</div>
      <div id="s4-spine" class="abs"></div>
      {rows_html}
      <div id="s4-win" class="band b-azul"></div>
      <div id="s4-headw" class="abs"><img id="s4-head" src="assets/img/head.png" alt="Lhama"></div>
      <div id="s4-ring" class="abs"></div>
      <div id="s4-r2" class="abs"></div>
      <div id="s4-foot" class="mono abs">Pista principal do Pulsar, em Cachoeira Alta</div>
      <div id="s4-iris" class="wipe"></div>"""
scr4 = f"""
      // entry: the full-screen swamp pattern shrinks into the arch window
      tl.fromTo("#s4-win", {{clipPath: "inset(0px 0px 0px 0px round 0px 0px 0px 0px)"}}, {{clipPath: "{win_in}", duration: 0.75, ease: "expo.inOut"}}, 0.05);
      tl.fromTo("#s4-win", {{backgroundPositionX: -360}}, {{backgroundPositionX: -620, duration: 5.8, ease: "none"}}, 0);
      tl.fromTo("#s4-ring", {{opacity: 0, scale: 1.08, transformOrigin: "50% 100%"}}, {{opacity: 1, scale: 1, duration: 0.4, ease: "expo.out"}}, 0.62);
      tl.fromTo("#s4-head", {{y: 420}}, {{y: 0, duration: 0.9, ease: "expo.out"}}, 0.85);""" + header_tl(p, 0.4) + f"""
      tl.fromTo("#s4-loc", {{opacity: 0, x: -30}}, {{opacity: 1, x: 0, duration: 0.5, ease: "expo.out"}}, 0.55);
      tl.fromTo("#s4-t1 .w", {{opacity: 0, filter: "blur(8px)"}}, {{opacity: 1, filter: "blur(0px)", duration: 0.16, ease: "power4.out", stagger: 0.08}}, 0.65);
      tl.fromTo("#s4-t2", {{opacity: 0, y: 60, textShadow: "0em 0em 0 {C['pink']}"}}, {{opacity: 1, y: 0, textShadow: ".045em .045em 0 {C['pink']}", duration: 0.6, ease: "expo.out"}}, 0.95);
      // the scale: spine draws down, each genre lands on it
      tl.fromTo("#s4-spine", {{scaleY: 0}}, {{scaleY: 1, duration: 1.0, ease: "power2.inOut"}}, 1.3);
      {"".join(f'tl.fromTo("#s4-dot{i}", {{scale: 0}}, {{scale: 1, duration: 0.35, ease: "back.out(2.6)"}}, {1.3 + i*0.16:.2f});' for i in range(6))}
      {"".join(f'tl.fromTo("#s4-row{i} .n", {{opacity: 0, x: -40}}, {{opacity: 1, x: 0, duration: 0.5, ease: "expo.out"}}, {1.36 + i*0.16:.2f});' for i in range(6))}
      tl.fromTo("#s4-row0 .a", {{opacity: 0, y: 14}}, {{opacity: 1, y: 0, duration: 0.4, ease: "expo.out"}}, 2.5);
      tl.fromTo("#s4-row1 .a", {{opacity: 0, y: 14}}, {{opacity: 1, y: 0, duration: 0.4, ease: "expo.out"}}, 2.7);
      tl.fromTo("#s4-row1 .n", {{scale: 1}}, {{scale: 1.08, duration: 0.2, yoyo: true, repeat: 1, ease: "power2.out", transformOrigin: "0% 70%"}}, 2.75);
      tl.fromTo("#s4-r2", {{scaleX: 0}}, {{scaleX: 1, duration: 0.6, ease: "expo.out"}}, 2.2);
      tl.fromTo("#s4-foot", {{opacity: 0}}, {{opacity: 1, duration: 0.4}}, 2.4);
      // exit: yellow iris from the llama
      tl.fromTo("#s4-iris", {{clipPath: "circle(0px at {AX+150}px {AY+200}px)"}}, {{clipPath: "circle(2300px at {AX+150}px {AY+200}px)", duration: 0.6, ease: "power3.in"}}, 5.15);"""
out[p] = scene(p, 5.8, css4, body4, scr4, C["paper"], C["ink"])

# ---------------------------------------------------------------- S5 Pra ouvir
p = "s5"
tracks = [("Ray Tchi", "Cakkou · ACIDEXPRESS EP, 2024"), ("Versa 360", "Dona Sinistrus, como Kenya20hz · DJ mix, 2026"),
          ("Diza vs Mavka", "Diza · set no Psico Bloco, BH, 2024"), ("Lizard Theme", "Reptant · Craigie Knowes, 2019")]
TY0, TS = 566, 162
eq = lambda i: "".join(f'<i id="s5-eq{i}-{k}" style="left:{k*13}px"></i>' for k in range(6))
tr_html = "".join(f'''
      <div id="s5-tr{i}" class="tr" style="top:{TY0 + i*TS}px">
        <span id="s5-num{i}" class="num">0{i+1}</span>
        <div class="t">{t}</div>
        <div class="m">{m}</div>
        <div class="eq">{eq(i)}</div>
        <div id="s5-pb{i}" class="pb"></div>
      </div>''' for i, (t, m) in enumerate(tracks))
css5 = f"""
    #s5-t {{ top: 392px; font-size: 128px; }}
    #root .tr {{ position: absolute; left: {X0}px; width: {CW}px; height: {TS}px; }}
    #root .tr .num {{ position: absolute; left: 0; top: 18px; font-family: LhMono; font-size: 28px; color: {C['ink']}; }}
    #root .tr .t {{ position: absolute; left: 72px; top: 0; font-size: 66px; line-height: 1; text-transform: uppercase; white-space: nowrap; }}
    #root .tr .m {{ position: absolute; left: 72px; top: 82px; font-family: LhMono; font-size: 22px; letter-spacing: .06em; text-transform: uppercase; white-space: nowrap; }}
    #root .tr .eq {{ position: absolute; right: 0; top: 14px; width: 78px; height: 48px; }}
    #root .tr .eq i {{ position: absolute; bottom: 0; width: 8px; height: 48px; background: {C['ink']}; transform-origin: 50% 100%; transform: scaleY(.15); }}
    #root .tr .pb {{ position: absolute; left: 72px; top: 122px; width: {CW-72}px; height: 4px; background: {C['ink']}; transform-origin: 0 50%; opacity: .9; }}
    #s5-band {{ top: 1640px; height: 280px; border-top: 7px solid {C['ink']}; }}
    #s5-head {{ left: 640px; top: 1250px; width: 420px; z-index: 5; transform-origin: 40% 90%; }}
    #s5-wk {{ top: {H}px; background: {C['ink']}; }}
"""
body5 = header(p, 5, 4) + f"""
      <div id="s5-t" class="big reg"><span class="w">Pra</span> <span class="w">ouvir</span></div>
      {tr_html}
      <div id="s5-band" class="band b-azul"></div>
      <img id="s5-head" class="abs" src="assets/img/head.png" alt="Lhama">
      <div id="s5-wk" class="wipe"></div>"""
# a playlist that plays: each track takes its turn (number turns pink, eq dances, progress fills)
eq_tl = []
for i in range(4):
    t0 = 1.45 + i * 0.95
    eq_tl.append(f'tl.fromTo("#s5-num{i}", {{color: "{C["ink"]}"}}, {{color: "{C["pink"]}", duration: 0.15}}, {t0:.2f});')
    eq_tl.append(f'tl.to("#s5-num{i}", {{color: "{C["ink"]}", duration: 0.2}}, {t0+0.95:.2f});' if i < 3 else "")
    eq_tl.append(f'tl.fromTo("#s5-pb{i}", {{scaleX: 0}}, {{scaleX: 1, duration: 0.95, ease: "none"}}, {t0:.2f});')
    for k in range(6):
        hs = [0.9, 0.45, 1.0, 0.6, 0.8, 0.35]
        eq_tl.append(f'tl.fromTo("#s5-eq{i}-{k}", {{scaleY: .15}}, {{scaleY: {hs[(k+i)%6]}, duration: {0.118 + 0.02*((k*7+i)%4):.3f}, yoyo: true, repeat: {7 - (k % 2)}, ease: "sine.inOut"}}, {t0 + 0.02*k:.2f});')
scr5 = header_tl(p, 0.05) + f"""
      tl.fromTo("#s5-t .w", {{opacity: 0, y: 70, rotation: -4}}, {{opacity: 1, y: 0, rotation: 0, duration: 0.6, ease: "back.out(1.6)", stagger: 0.1}}, 0.15);
      tl.fromTo("#s5-t", {{textShadow: "0em 0em 0 {C['pink']}"}}, {{textShadow: ".045em .045em 0 {C['pink']}", duration: 0.4, ease: "back.out(2)"}}, 0.55);
      {"".join(f'tl.fromTo("#s5-tr{i} .t", {{opacity: 0, x: 60, filter: "blur(6px)"}}, {{opacity: 1, x: 0, filter: "blur(0px)", duration: 0.5, ease: "expo.out"}}, {0.55 + i*0.12:.2f});' for i in range(4))}
      {"".join(f'tl.fromTo("#s5-tr{i} .num", {{opacity: 0, scale: 0.4}}, {{opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2.4)"}}, {0.6 + i*0.12:.2f});' for i in range(4))}
      {"".join(f'tl.fromTo("#s5-tr{i} .m", {{opacity: 0}}, {{opacity: 1, duration: 0.35}}, {0.8 + i*0.12:.2f});' for i in range(4))}
      {chr(10).join(eq_tl)}
      tl.fromTo("#s5-band", {{y: 280}}, {{y: 0, duration: 0.8, ease: "expo.out"}}, 0.3);
      tl.fromTo("#s5-band", {{backgroundPositionX: 0}}, {{backgroundPositionX: -240, duration: 6.0, ease: "none"}}, 0);
      tl.fromTo("#s5-head", {{y: 700, rotation: 6}}, {{y: 0, rotation: 0, duration: 1.0, ease: "expo.out"}}, 0.6);
      // head nods on the beat while the playlist runs
      tl.to("#s5-head", {{rotation: -3.5, duration: 0.227, yoyo: true, repeat: 15, ease: "sine.inOut"}}, 1.6);
      // exit: ink sheet sweeps up
      tl.to("#s5-head", {{y: -260, duration: 0.55, ease: "power3.in"}}, 5.4);
      tl.fromTo("#s5-wk", {{y: 0}}, {{y: -{H}, duration: 0.5, ease: "power3.in"}}, 5.45);"""
out[p] = scene(p, 6.0, css5, body5, scr5, C["yel"], C["ink"])

# ---------------------------------------------------------------- S6 map
p = "s6"
places = [("Houghton", "Inglaterra", "o clube foi pro bosque", "pink"),
          ("MoDem", "Croácia", "o psy desceu até o techno", "lav"),
          ("Pulsar", "Minas Gerais", "o prog dark faz a ponte", "lav"),
          ("Veludo", "Minas Gerais", "em 2025, a pista foi pra Heliodora", "pink")]
RY0, RS = 642, 124
rows6 = "".join(f'''
      <div id="s6-r{i}" class="r" style="top:{RY0 + i*RS}px">
        <i id="s6-d{i}" style="background:{C[c]}"></i>
        <div class="p"><span class="pn">{n}</span><span class="rg" style="color:{C['pink'] if c=='pink' else C['lilac']}">{r}</span></div>
        <div class="ph">{" ".join(f'<span class="pw">{w}</span>' for w in ph.split(" "))}</div>
      </div>''' for i, (n, r, ph, c) in enumerate(places))
css6 = f"""
    #s6-t1 {{ top: 392px; font-size: 112px; color: {C['paper']}; }}
    #s6-t2 {{ top: 494px; font-size: 88px; color: {C['paper']}; }}
    #s6-spine {{ left: {X0+11}px; top: {RY0+24}px; width: 4px; height: {3*RS}px; background: {C['paper']}; transform-origin: 50% 0; }}
    #root .r {{ position: absolute; left: {X0}px; width: {CW}px; height: {RS}px; }}
    #root .r i {{ position: absolute; left: 0; top: 12px; width: 27px; height: 27px; border-radius: 50%; border: 4px solid {C['paper']}; }}
    #root .r .p {{ position: absolute; left: 56px; top: 0; display: flex; align-items: baseline; gap: 18px; white-space: nowrap; }}
    #root .r .pn {{ font-size: 56px; text-transform: uppercase; color: {C['paper']}; line-height: 1; }}
    #root .r .rg {{ font-family: LhMono; font-size: 20px; letter-spacing: .18em; text-transform: uppercase; }}
    #root .r .ph {{ position: absolute; left: 56px; top: 62px; font-size: 32px; color: {C['wool']}; white-space: nowrap; }}
    #root .pw {{ display: inline-block; }}
    #s6-leg {{ left: {X0}px; top: 1162px; width: {CW}px; display: flex; align-items: center; gap: 44px; color: {C['wool']}; font-size: 22px; }}
    #s6-leg span::before {{ content: ""; display: inline-block; width: 13px; height: 13px; border-radius: 50%; margin-right: 12px; vertical-align: 1px; }}
    #s6-la::before {{ background: {C['pink']}; }}
    #s6-lb::before {{ background: {C['lav']}; }}
    #s6-sig {{ margin-left: auto; width: 180px; filter: invert(1); }}
    #s6-band {{ top: 1560px; height: 360px; border-top: 7px solid {C['paper']}; }}
    #s6-esp {{ left: 290px; top: 1330px; width: 500px; z-index: 5; }}
"""
body6 = header(p, 6, 5) + f"""
      <div id="s6-t1" class="big"><span class="w">Onde</span> <span class="w">o</span> <span class="w">clube</span></div>
      <div id="s6-t2" class="big"><span class="w">encontra</span> <span class="w reg">a rave</span></div>
      <div id="s6-spine" class="abs"></div>
      {rows6}
      <div id="s6-leg" class="mono abs"><span id="s6-la">Clube → mato</span><span id="s6-lb">Psy → techno</span><img id="s6-sig" src="assets/img/nome-pb.png" alt="Lhama Bookings"></div>
      <div id="s6-band" class="band b-azul"></div>
      <img id="s6-esp" class="abs" src="assets/img/espiral.png" alt="Lhama">"""
scr6 = header_tl(p, 0.05) + f"""
      tl.fromTo("#s6-t1 .w", {{opacity: 0, filter: "blur(8px)", y: 30}}, {{opacity: 1, filter: "blur(0px)", y: 0, duration: 0.45, ease: "expo.out", stagger: 0.08}}, 0.2);
      tl.fromTo("#s6-t2 .w", {{opacity: 0, filter: "blur(8px)", y: 30}}, {{opacity: 1, filter: "blur(0px)", y: 0, duration: 0.45, ease: "expo.out", stagger: 0.12}}, 0.45);
      tl.fromTo("#s6-t2 .reg", {{textShadow: "0em 0em 0 {C['pink']}"}}, {{textShadow: ".045em .045em 0 {C['pink']}", duration: 0.4, ease: "back.out(2)"}}, 0.8);
      // the route of the map: spine draws stop by stop
      tl.fromTo("#s6-spine", {{scaleY: 0}}, {{scaleY: 1, duration: 2.0, ease: "power1.inOut"}}, 1.0);
      {"".join(f'tl.fromTo("#s6-d{i}", {{scale: 0}}, {{scale: 1, duration: 0.4, ease: "back.out(2.6)"}}, {1.0 + i*0.66:.2f});' for i in range(4))}
      {"".join(f'tl.fromTo("#s6-r{i} .pn", {{opacity: 0, x: -40, filter: "blur(6px)"}}, {{opacity: 1, x: 0, filter: "blur(0px)", duration: 0.5, ease: "expo.out"}}, {1.05 + i*0.66:.2f});' for i in range(4))}
      {"".join(f'tl.fromTo("#s6-r{i} .rg", {{opacity: 0}}, {{opacity: 1, duration: 0.3}}, {1.25 + i*0.66:.2f});' for i in range(4))}
      {"".join(f'tl.fromTo("#s6-r{i} .pw", {{opacity: 0}}, {{opacity: 1, duration: 0.2, stagger: 0.06}}, {1.3 + i*0.66:.2f});' for i in range(4))}
      tl.fromTo("#s6-leg span", {{opacity: 0, y: 12}}, {{opacity: 1, y: 0, duration: 0.4, ease: "expo.out", stagger: 0.1}}, 3.7);
      tl.fromTo("#s6-sig", {{opacity: 0, scale: 0.85}}, {{opacity: 1, scale: 1, duration: 0.5, ease: "back.out(1.8)"}}, 3.9);
      tl.fromTo("#s6-band", {{y: 360}}, {{y: 0, duration: 0.9, ease: "expo.out"}}, 0.5);
      tl.fromTo("#s6-band", {{backgroundPositionX: 0}}, {{backgroundPositionX: -300, duration: 7.0, ease: "none"}}, 0);
      tl.fromTo("#s6-esp", {{y: 600, rotation: -10}}, {{y: 0, rotation: 0, duration: 1.2, ease: "expo.out"}}, 0.9);"""
out[p] = scene(p, 7.0, css6, body6, scr6, C["ink"], C["paper"], dark=True)

os.makedirs("compositions", exist_ok=True)
for k, v in out.items():
    open(f"compositions/{k}.html", "w").write(v)

t = 0.0
hosts = []
names = {"s1": "Capa", "s2": "Houghton", "s3": "MoDem", "s4": "Pulsar", "s5": "Pra ouvir", "s6": "Mapa"}
for sid, d in SCENES:
    hosts.append(f'''      <div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html"
        data-start="{t:.3f}" data-duration="{d}" data-track-index="1" data-track-kind="graphics"
        data-width="{W}" data-height="{H}"></div>''')
    t += d
total = round(t, 3)
index = f"""<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: {C['paper']}; }}
      #root {{ position: relative; width: 100%; height: 100%; background: {C['paper']}; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="{W}" data-height="{H}">
{chr(10).join(hosts)}
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""
open("index.html", "w").write(index)
print("total", total)
