#!/usr/bin/env python3
"""Analisa a mix e prepara o vídeo de órbitas (camadas por frequência).
Uso: python3 tools/orbitas.py <audio> --bpm 85 [--inicio 92.3] [--compassos 21]
"""
import argparse, json, re, subprocess
from pathlib import Path
import numpy as np
SR, FPS, OUTRO = 44100, 30, 3.0
RAIZ = Path(__file__).resolve().parent.parent
CAMADAS = [("SUB", 30, 120, "sus"), ("LASER", 800, 2600, "on"), ("TEXTURA", 2600, 6000, "on"), ("HATS", 7000, 16000, "on")]

def ler(f):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(f), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2)

def bandas(m, hop, n=2048):
    w = np.hanning(n).astype(np.float32); fr = np.fft.rfftfreq(n, 1 / SR); out = []
    for i in range(0, len(m) - n, hop):
        p = np.abs(np.fft.rfft(m[i:i + n] * w)) ** 2
        out.append([p[(fr >= a) & (fr < b)].sum() for _, a, b, _ in CAMADAS] + [p[(fr >= 40) & (fr < 110)].sum()])
    return 10 * np.log10(np.array(out) + 1e-12)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("audio"); ap.add_argument("--bpm", type=float, required=True)
    ap.add_argument("--inicio", type=float); ap.add_argument("--compassos", type=int, default=21); a = ap.parse_args()
    st = ler(a.audio); m = st.mean(1); comp = 240 / a.bpm; passo = comp / 16
    hop = int(SR * passo / 4)                       # 4 janelas por semicolcheia
    B = bandas(m, hop); tB = (np.arange(len(B)) * hop + 1024) / SR
    on = np.maximum(np.diff(B, axis=0, prepend=B[:1]), 0)   # ataques por banda
    nb = int((len(m) / SR) // comp)
    # grade: valor por compasso/passo/camada
    def grade(bar):
        g = []
        for k, (_, _, _, modo) in enumerate(CAMADAS):
            row = []
            for s in range(16):
                t0 = bar * comp + s * passo; sel = (tB >= t0) & (tB < t0 + passo)
                row.append(float((B[sel, k].mean() if modo == "sus" else on[sel, k].max()) if sel.any() else -120))
            g.append(row)
        return g
    G = np.array([grade(b) for b in range(nb)])     # nb x 4 x 16
    for k in range(4):                               # normaliza por camada
        v = G[:, k, :]; lo, hi = np.percentile(v, 30), np.percentile(v, 99)
        G[:, k, :] = np.clip((v - lo) / (hi - lo + 1e-9), 0, 1)
    if a.inicio is None:                              # janela com mais mudança de camadas
        pres = G.mean(2); best, bi = -1, 0
        for i in range(0, nb - a.compassos):
            w = pres[i:i + a.compassos]; sc = np.abs(np.diff(w, axis=0)).sum() + 0.5 * w.std(0).sum()
            if sc > best: best, bi = sc, i
        ini_bar = bi
    else:
        ini_bar = int(round(a.inicio / comp))
    ini = ini_bar * comp; dur = a.compassos * comp
    print(f"trecho {ini:.2f}s → {ini + dur:.2f}s ({a.compassos} compassos de {comp:.3f}s)")
    trecho = st[int(ini * SR):int((ini + dur) * SR)].copy()
    cauda = st[int((ini + dur) * SR):int((ini + dur + OUTRO) * SR)].copy()
    cauda *= np.linspace(1, 0, len(cauda))[:, None]
    trecho[:int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))[:, None]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", str(RAIZ / "assets/trecho.wav")],
                   input=np.concatenate([trecho, cauda]).astype(np.float32).tobytes(), check=True)
    # kick por quadro (envelope do ataque no grave) e níveis por camada
    q = int(round(dur * FPS)); kick, niv = [], []
    kon = on[:, 4]; klo, khi = np.percentile(kon, 50), np.percentile(kon, 99.5)
    for f in range(q):
        t = ini + f / FPS; sel = (tB >= t - 0.12) & (tB <= t)
        v = kon[sel] if sel.any() else np.array([0]); age = (t - tB[sel][np.argmax(v)]) if sel.any() else 1
        kick.append(int(round(100 * np.clip((v.max() - klo) / (khi - klo), 0, 1) * np.exp(-age / 0.09))))
    mm = trecho.mean(1); cols = 200; pc = len(mm) // cols
    onda = [int(round(np.abs(mm[i * pc:(i + 1) * pc]).max() / (np.abs(mm).max() + 1e-9) * 100)) for i in range(cols)]
    D = {"bpm": a.bpm, "compasso": comp, "compassos": a.compassos, "duracao": dur, "fps": FPS,
         "camadas": [c[0] for c in CAMADAS], "grade": (G[ini_bar:ini_bar + a.compassos] * 100).round().astype(int).tolist(),
         "kick": kick, "onda": onda, "inicioMusica": ini}
    p = RAIZ / "compositions/orbitas.html"; h = p.read_text()
    h = re.sub(r"/\*DADOS\*/.*?/\*FIM\*/", lambda _: "/*DADOS*/" + json.dumps(D, separators=(",", ":")) + "/*FIM*/", h, flags=re.S); p.write_text(h)
    tot = dur + OUTRO; i = RAIZ / "index.html"; t = i.read_text()
    t = re.sub(r'(data-duration=")[0-9.]+', lambda mm_: f"{mm_.group(1)}{tot:.3f}", t); i.write_text(t)
    print(f"ok: vídeo de {tot:.2f}s")

if __name__ == "__main__":
    main()
