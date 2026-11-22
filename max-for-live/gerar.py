#!/usr/bin/env python3
"""Gera devices Max for Live (.amxd) compativeis com Live 9 / Max 6.1+.

Uso:  python3 gerar.py      -> escreve os .amxd na pasta devices/
"""
import json
import struct
from pathlib import Path

OUT = Path(__file__).parent / "devices"


# --------------------------------------------------------------------------
# Construtor de patch
# --------------------------------------------------------------------------
class Patch:
    def __init__(self, kind):
        self.kind = kind  # "midi" | "audio" | "instrument"
        self.boxes = []
        self.lines = []
        self.n = 0

    def _pos(self):
        col, row = divmod(self.n, 18)
        return [30 + col * 210, 30 + row * 34]

    def obj(self, text, ins, outs, outtype=None, **attrs):
        return self._box("newobj", ins, outs, outtype, text=text, **attrs)

    def msg(self, text, **attrs):
        return self._box("message", 2, 1, [""], text=text, **attrs)

    def comment(self, text, pres=None, **attrs):
        return self._box("comment", 1, 0, [], text=text, pres=pres, **attrs)

    def _box(self, cls, ins, outs, outtype, pres=None, **attrs):
        self.n += 1
        bid = f"obj-{self.n}"
        x, y = self._pos()
        box = {
            "id": bid,
            "maxclass": cls,
            "numinlets": ins,
            "numoutlets": outs,
            "patching_rect": [x, y, 180.0, 22.0],
        }
        if outs:
            box["outlettype"] = outtype if outtype is not None else [""] * outs
        if pres:
            box["presentation"] = 1
            box["presentation_rect"] = pres
        box.update(attrs)
        self.boxes.append({"box": box})
        return bid

    def _param(self, cls, ins, outs, outtype, name, short, valueof, pres, **attrs):
        valueof = {"parameter_longname": name, "parameter_shortname": short, **valueof}
        return self._box(
            cls, ins, outs, outtype, pres=pres,
            parameter_enable=1, varname=name,
            saved_attribute_attributes={"valueof": valueof}, **attrs,
        )

    def dial(self, name, short, lo, hi, init, unit, pres, integer=False, exponent=1.0):
        return self._param(
            "live.dial", 1, 2, ["", "float"], name, short,
            {
                "parameter_type": 1 if integer else 0,
                "parameter_mmin": lo, "parameter_mmax": hi,
                "parameter_initial_enable": 1, "parameter_initial": [init],
                "parameter_unitstyle": unit, "parameter_exponent": exponent,
            },
            pres,
        )

    def toggle(self, name, short, init, pres):
        return self._param(
            "live.toggle", 1, 1, [""], name, short,
            {
                "parameter_type": 2, "parameter_enum": ["off", "on"],
                "parameter_mmax": 1, "parameter_initial_enable": 1,
                "parameter_initial": [init],
            },
            pres,
        )

    def menu(self, name, short, items, init, pres):
        return self._param(
            "live.menu", 1, 3, ["", "", "float"], name, short,
            {
                "parameter_type": 2, "parameter_enum": items,
                "parameter_mmax": len(items) - 1,
                "parameter_initial_enable": 1, "parameter_initial": [init],
            },
            pres,
        )

    def button_text(self, label, pres):
        # live.text em modo botao, SEM ser parametro do Live (assim clicar nele
        # nao muda o "parametro selecionado" do Live).
        return self._box(
            "live.text", 1, 2, ["", ""], pres=pres,
            mode=0, text=label, texton=label, parameter_enable=0,
        )

    def umenu(self, items, pres):
        flat = []
        for i, it in enumerate(items):
            if i:
                flat.append(",")
            flat.append(it)
        return self._box("umenu", 1, 3, ["int", "", ""], pres=pres, items=flat)

    def wire(self, src, outlet, dst, inlet=0):
        self.lines.append({"patchline": {
            "source": [src, outlet], "destination": [dst, inlet],
            "hidden": 0, "disabled": 0,
        }})

    # ------------------------------------------------------------------
    def to_json(self):
        return {"patcher": {
            "fileversion": 1,
            "appversion": {"major": 6, "minor": 1, "revision": 10, "architecture": "x86"},
            "rect": [80.0, 80.0, 1100.0, 720.0],
            "bglocked": 0,
            "openinpresentation": 1,
            "default_fontsize": 10.0,
            "default_fontface": 0,
            "default_fontname": "Arial Bold",
            "gridonopen": 0,
            "gridsize": [8.0, 8.0],
            "gridsnaponopen": 0,
            "statusbarvisible": 2,
            "toolbarvisible": 1,
            "boxanimatetime": 200,
            "imprint": 0,
            "enablehscroll": 1,
            "enablevscroll": 1,
            "devicewidth": 0.0,
            "description": "",
            "digest": "",
            "tags": "",
            "boxes": self.boxes,
            "lines": self.lines,
            "dependency_cache": [],
        }}

    def write(self, path):
        body = json.dumps(self.to_json(), indent=1).encode("utf-8") + b"\n\x00"
        dtype = {"audio": b"aaaa", "midi": b"mmmm", "instrument": b"iiii"}[self.kind]
        data = (
            b"ampf" + struct.pack("<I", 4) + dtype
            + b"meta" + struct.pack("<I", 4) + struct.pack("<I", 0)
            + b"ptch" + struct.pack("<I", len(body)) + body
        )
        path.write_bytes(data)
        print("ok ->", path)


# --------------------------------------------------------------------------
# Blocos reutilizaveis
# --------------------------------------------------------------------------
def midi_passthrough(p):
    """midiin -> midiparse ... midiformat -> midiout.
    Notas saem do outlet 0 do parse; tudo o resto passa direto."""
    mi = p.obj("midiin", 1, 1, ["int"])
    parse = p.obj("midiparse", 1, 7, ["", "", "", "int", "int", "int", "int"])
    fmt = p.obj("midiformat", 7, 1, ["int"])
    mo = p.obj("midiout", 1, 0)
    p.wire(mi, 0, parse)
    for k in range(1, 7):
        p.wire(parse, k, fmt, k)
    p.wire(fmt, 0, mo)
    return parse, fmt


def audio_passthrough(p):
    pin = p.obj("plugin~", 2, 2, ["signal", "signal"])
    pout = p.obj("plugout~", 2, 0)
    return pin, pout


def note_flush(p, fmt):
    """flush evita notas presas quando um parametro muda com notas tocando."""
    fl = p.obj("flush", 2, 2, ["", ""])
    pk = p.obj("pack 0 0", 2, 1)
    p.wire(fl, 0, pk, 0)
    p.wire(fl, 1, pk, 1)
    p.wire(pk, 0, fmt, 0)
    bang = p.obj("t b", 1, 1, ["bang"])
    p.wire(bang, 0, fl, 0)
    return fl, bang


def title(p, text, width):
    p.comment(text, pres=[4.0, 2.0, width, 18.0], fontsize=12.0)


# --------------------------------------------------------------------------
# 1) Acordes  (MIDI)
# --------------------------------------------------------------------------
def acordes():
    p = Patch("midi")
    title(p, "ACORDES - 1 nota vira acorde", 220)
    parse, fmt = midi_passthrough(p)
    fl, refresh = note_flush(p, fmt)

    fan = p.obj("t l l l l", 1, 4)
    p.wire(parse, 0, fan)
    p.wire(fan, 3, fl, 0)  # nota original sempre passa

    presets = {
        "Maior": (4, 7, 12), "Menor": (3, 7, 12), "Maior 7": (4, 7, 11),
        "Menor 7": (3, 7, 10), "Dom 7": (4, 7, 10), "Sus4": (5, 7, 12),
        "Quinta": (7, 12, 19), "Diminuto": (3, 6, 9),
    }
    p.comment("Preset", pres=[4.0, 24.0, 60.0, 16.0])
    um = p.umenu(["Livre"] + list(presets), pres=[4.0, 40.0, 84.0, 18.0])
    sel = p.obj("sel " + " ".join(str(i + 1) for i in range(len(presets))), 2, len(presets) + 1)
    p.wire(um, 0, sel)
    unp = p.obj("unpack 0 0 0", 1, 3)
    for i, iv in enumerate(presets.values()):
        m = p.msg(" ".join(map(str, iv)))
        p.wire(sel, i, m)
        p.wire(m, 0, unp)

    defaults = (4, 7, 12)
    for v in range(3):
        x = 96.0 + v * 56
        d = p.dial(f"Intervalo {v + 1}", f"Voz {v + 1}", -24, 24, defaults[v], 7,
                   pres=[x, 22.0, 44.0, 48.0], integer=True)
        t = p.toggle(f"Liga Voz {v + 1}", f"On {v + 1}", 1, pres=[x + 14, 76.0, 16.0, 16.0])
        p.wire(unp, v, d)

        g = p.obj("gate 1 1", 2, 1)
        un = p.obj("unpack 0 0", 1, 2)
        add = p.obj("+ 0", 2, 1, ["int"])
        clip = p.obj("clip 0 127", 3, 1)
        pk = p.obj("pack 0 0", 2, 1)
        p.wire(fan, 2 - v, g, 1)
        p.wire(t, 0, g, 0)
        p.wire(g, 0, un)
        p.wire(un, 1, pk, 1)
        p.wire(un, 0, add, 0)
        p.wire(d, 0, add, 1)
        p.wire(add, 0, clip)
        p.wire(clip, 0, pk, 0)
        p.wire(pk, 0, fl, 0)
        p.wire(d, 0, refresh)
        p.wire(t, 0, refresh)

    p.comment("Intervalos em semitons a partir da nota tocada.",
              pres=[4.0, 100.0, 270.0, 16.0])
    p.write(OUT / "Acordes.amxd")


# --------------------------------------------------------------------------
# 2) Escala  (MIDI) - forca qualquer nota a cair numa escala
# --------------------------------------------------------------------------
SCALES = {
    "Maior": [0, 2, 4, 5, 7, 9, 11],
    "Menor": [0, 2, 3, 5, 7, 8, 10],
    "Menor Harm": [0, 2, 3, 5, 7, 8, 11],
    "Dorico": [0, 2, 3, 5, 7, 9, 10],
    "Frigio": [0, 1, 3, 5, 7, 8, 10],
    "Mixolidio": [0, 2, 4, 5, 7, 9, 10],
    "Penta Maior": [0, 2, 4, 7, 9],
    "Penta Menor": [0, 3, 5, 7, 10],
    "Blues": [0, 3, 5, 6, 7, 10],
    "Cromatica": list(range(12)),
}


def deltas(scale):
    cands = scale + [12]
    out = []
    for d in range(12):
        best = min(cands, key=lambda s: (abs(s - d), s))  # empate: desce
        out.append(best - d)
    return out


def escala():
    p = Patch("midi")
    title(p, "ESCALA - nunca erra nota", 200)
    parse, fmt = midi_passthrough(p)
    fl, refresh = note_flush(p, fmt)

    notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    root = p.menu("Tonica", "Tonica", notes, 0, pres=[4.0, 40.0, 56.0, 16.0])
    p.comment("Tonica", pres=[4.0, 22.0, 56.0, 16.0])
    scale = p.menu("Escala", "Escala", list(SCALES), 0, pres=[68.0, 40.0, 100.0, 16.0])
    p.comment("Escala", pres=[68.0, 22.0, 100.0, 16.0])

    un = p.obj("unpack 0 0", 1, 2)
    tii = p.obj("t i i", 1, 2, ["int", "int"])
    deg = p.obj("expr ($i1 - $i2 + 120) % 12", 2, 1)
    look = p.obj("zl lookup", 2, 2)
    add = p.obj("+ 0", 2, 1, ["int"])
    clip = p.obj("clip 0 127", 3, 1)
    pk = p.obj("pack 0 0", 2, 1)

    p.wire(parse, 0, un)
    p.wire(un, 1, pk, 1)
    p.wire(un, 0, tii)
    p.wire(tii, 1, deg, 0)
    p.wire(deg, 0, look, 0)
    p.wire(look, 0, add, 1)
    p.wire(tii, 0, add, 0)
    p.wire(add, 0, clip)
    p.wire(clip, 0, pk, 0)
    p.wire(pk, 0, fl, 0)

    p.wire(root, 0, deg, 1)
    p.wire(root, 0, refresh)

    sel = p.obj("sel " + " ".join(str(i) for i in range(len(SCALES))), 2, len(SCALES) + 1)
    p.wire(scale, 0, sel)
    p.wire(scale, 0, refresh)
    for i, sc in enumerate(SCALES.values()):
        m = p.msg(" ".join(map(str, deltas(sc))))
        p.wire(sel, i, m)
        p.wire(m, 0, look, 1)

    p.comment("Coloque antes de um instrumento e toque qualquer tecla.",
              pres=[4.0, 64.0, 280.0, 16.0])
    p.write(OUT / "Escala.amxd")


# --------------------------------------------------------------------------
# 3) Stutter Gate  (audio) - corta o som no ritmo do Live
# --------------------------------------------------------------------------
def stutter():
    p = Patch("audio")
    title(p, "STUTTER GATE", 160)
    pin, pout = audio_passthrough(p)
    vl = p.obj("*~ 1.", 2, 1, ["signal"])
    vr = p.obj("*~ 1.", 2, 1, ["signal"])
    p.wire(pin, 0, vl, 0)
    p.wire(pin, 1, vr, 0)
    p.wire(vl, 0, pout, 0)
    p.wire(vr, 0, pout, 1)

    rates = ["1/4", "1/8", "1/8T", "1/16", "1/16T", "1/32"]
    mult = [1, 2, 3, 4, 6, 8]
    rate = p.menu("Divisao", "Divisao", rates, 3, pres=[4.0, 40.0, 60.0, 16.0])
    p.comment("Divisao", pres=[4.0, 22.0, 60.0, 16.0])
    duty = p.dial("Duracao", "Duracao", 5.0, 95.0, 50.0, 5, pres=[72.0, 22.0, 44.0, 48.0])
    depth = p.dial("Profundidade", "Profund.", 0.0, 100.0, 100.0, 5, pres=[124.0, 22.0, 44.0, 48.0])

    beat = p.obj("plugphasor~", 1, 1, ["signal"])
    m = p.obj("*~ 4.", 2, 1, ["signal"])
    wrap = p.obj("%~ 1.", 2, 1, ["signal"])
    lt = p.obj("<~ 0.5", 2, 1, ["signal"])
    inv1 = p.obj("!-~ 1.", 2, 1, ["signal"])
    dep = p.obj("*~ 1.", 2, 1, ["signal"])
    inv2 = p.obj("!-~ 1.", 2, 1, ["signal"])
    smooth = p.obj("rampsmooth~ 64 64", 1, 1, ["signal"])
    for a, b in [(beat, m), (m, wrap), (wrap, lt), (lt, inv1), (inv1, dep), (dep, inv2), (inv2, smooth)]:
        p.wire(a, 0, b, 0)
    p.wire(smooth, 0, vl, 1)
    p.wire(smooth, 0, vr, 1)

    sel = p.obj("sel 0 1 2 3 4 5", 2, 7)
    p.wire(rate, 0, sel)
    for i, k in enumerate(mult):
        mm = p.msg(str(k))
        p.wire(sel, i, mm)
        p.wire(mm, 0, m, 1)

    for d, target in [(duty, lt), (depth, dep)]:
        sc = p.obj("/ 100.", 2, 1, ["float"])
        p.wire(d, 0, sc)
        p.wire(sc, 0, target, 1)

    p.comment("Segue o tempo do Live. Aperte Play.", pres=[4.0, 76.0, 200.0, 16.0])
    p.write(OUT / "Stutter Gate.amxd")


# --------------------------------------------------------------------------
# 4) Modulador  (audio + Live API) - LFO em QUALQUER parametro do Live
# --------------------------------------------------------------------------
def modulador():
    p = Patch("audio")
    title(p, "MODULADOR - LFO em qualquer knob", 240)
    pin, pout = audio_passthrough(p)
    p.wire(pin, 0, pout, 0)
    p.wire(pin, 1, pout, 1)

    btn_map = p.button_text("Map", pres=[4.0, 24.0, 44.0, 18.0])
    btn_off = p.button_text("Solta", pres=[52.0, 24.0, 44.0, 18.0])
    name = p.comment("(livre)", pres=[4.0, 46.0, 170.0, 16.0])

    shape = p.menu("Forma", "Forma", ["Seno", "Triangulo", "Serra", "Quadrada", "Aleatorio"], 0,
                   pres=[4.0, 70.0, 80.0, 16.0])
    rate = p.dial("Velocidade", "Hz", 0.01, 20.0, 1.0, 3, pres=[180.0, 22.0, 44.0, 48.0], exponent=3.0)
    depth = p.dial("Quantidade", "Quant.", 0.0, 100.0, 50.0, 5, pres=[228.0, 22.0, 44.0, 48.0])
    center = p.dial("Centro", "Centro", 0.0, 100.0, 50.0, 5, pres=[276.0, 22.0, 44.0, 48.0])

    # --- LFO ---
    ph = p.obj("phasor~ 1.", 2, 1, ["signal"])
    p.wire(rate, 0, ph, 0)
    sel = p.obj("selector~ 5 1", 6, 1, ["signal"])

    def uni(src):  # -1..1 -> 0..1
        a = p.obj("*~ 0.5", 2, 1, ["signal"])
        b = p.obj("+~ 0.5", 2, 1, ["signal"])
        p.wire(src, 0, a)
        p.wire(a, 0, b)
        return b

    cyc = p.obj("cycle~ 0.", 2, 1, ["signal"])
    p.wire(ph, 0, cyc, 1)
    p.wire(uni(cyc), 0, sel, 1)
    tri = p.obj("triangle~ 0.5", 2, 1, ["signal"])
    p.wire(ph, 0, tri, 0)
    p.wire(uni(tri), 0, sel, 2)
    p.wire(ph, 0, sel, 3)
    sq = p.obj("<~ 0.5", 2, 1, ["signal"])
    p.wire(ph, 0, sq, 0)
    p.wire(sq, 0, sel, 4)
    nz = p.obj("noise~", 1, 1, ["signal"])
    sah = p.obj("sah~ 0.5", 2, 1, ["signal"])
    p.wire(nz, 0, sah, 0)
    p.wire(ph, 0, sah, 1)
    p.wire(uni(sah), 0, sel, 5)

    plus1 = p.obj("+ 1", 2, 1, ["int"])
    p.wire(shape, 0, plus1)
    p.wire(plus1, 0, sel, 0)

    cen = p.obj("-~ 0.5", 2, 1, ["signal"])
    amt = p.obj("*~ 0.5", 2, 1, ["signal"])
    off = p.obj("+~ 0.5", 2, 1, ["signal"])
    clp = p.obj("clip~ 0. 1.", 3, 1, ["signal"])
    rng = p.obj("*~ 1.", 2, 1, ["signal"])
    mn = p.obj("+~ 0.", 2, 1, ["signal"])
    remote = p.obj("live.remote~", 2, 1)
    for a, b in [(sel, cen), (cen, amt), (amt, off), (off, clp), (clp, rng), (rng, mn), (mn, remote)]:
        p.wire(a, 0, b, 0)
    for d, target in [(depth, amt), (center, off)]:
        sc = p.obj("/ 100.", 2, 1, ["float"])
        p.wire(d, 0, sc)
        p.wire(sc, 0, target, 1)

    # --- Map: pega o parametro selecionado no Live ---
    tb = p.obj("t b", 1, 1, ["bang"])
    p.wire(btn_map, 0, tb)
    path_msg = p.msg("path live_set view selected_parameter")
    path = p.obj("live.path", 1, 3)
    rid = p.obj("route id", 2, 2)
    zero = p.obj("sel 0", 2, 2, ["bang", ""])
    p.wire(tb, 0, path_msg)
    p.wire(path_msg, 0, path)
    p.wire(path, 0, rid)
    p.wire(rid, 0, zero)
    warn = p.msg("set Clique num knob e depois Map")
    p.wire(zero, 0, warn)
    p.wire(warn, 0, name)

    tri3 = p.obj("t i b i", 1, 3, ["int", "bang", "int"])
    p.wire(zero, 1, tri3)
    lobj = p.obj("live.object", 2, 1)
    id_obj = p.msg("id $1")
    p.wire(tri3, 2, id_obj)
    p.wire(id_obj, 0, lobj, 1)
    gets = p.msg("get min, get max, get name")
    p.wire(tri3, 1, gets)
    p.wire(gets, 0, lobj, 0)
    id_rem = p.msg("id $1")
    p.wire(tri3, 0, id_rem)
    p.wire(id_rem, 0, remote, 1)

    rt = p.obj("route min max name", 2, 4)
    p.wire(lobj, 0, rt)
    tmin = p.obj("t f f", 1, 2, ["float", "float"])
    sub = p.obj("- 0.", 2, 1, ["float"])
    p.wire(rt, 0, tmin)
    p.wire(tmin, 1, sub, 1)
    p.wire(tmin, 0, mn, 1)
    p.wire(rt, 1, sub, 0)
    p.wire(sub, 0, rng, 1)
    pre = p.obj("prepend set", 1, 1)
    p.wire(rt, 2, pre)
    p.wire(pre, 0, name)

    # --- Solta ---
    tb2 = p.obj("t b b", 1, 2, ["bang", "bang"])
    p.wire(btn_off, 0, tb2)
    rel = p.msg("id 0")
    p.wire(tb2, 1, rel)
    p.wire(rel, 0, remote, 1)
    clr = p.msg("set (livre)")
    p.wire(tb2, 0, clr)
    p.wire(clr, 0, name)

    p.comment("1) clique num knob do Live  2) Map", pres=[90.0, 70.0, 200.0, 16.0])
    p.write(OUT / "Modulador.amxd")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    acordes()
    escala()
    stutter()
    modulador()
