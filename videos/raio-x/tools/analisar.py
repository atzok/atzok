#!/usr/bin/env python3
"""RAIO-X: analisa uma faixa e prepara o vídeo.

Uso:
  python3 tools/analisar.py <audio> [--bpm 140] [--drop 92.5] [--compassos 8]
                            [--max 60] [--projeto ../raio-x-bliss030]

- Acha o BPM e o drop (onde o grave volta com mais força) se não forem dados.
- Corta um trecho com metade dos compassos antes do drop e metade depois,
  com no máximo ~30 s, e salva em assets/trecho.wav.
- Mede, quadro a quadro (30 fps): espectro, cinco faixas de frequência,
  campo estéreo e forma de onda. Escreve tudo em compositions/painel.html
  (entre os marcadores DADOS) e acerta as durações em index.html.
"""
import argparse, json, re, subprocess, sys
from pathlib import Path
import numpy as np

SR = 44100
FPS = 30
OUTRO = 3.0           # segundos de encerramento (logo + @)
MAX_TRECHO = 30.0     # duração máxima do trecho
RAIZ = Path(__file__).resolve().parent.parent


def ler_audio(caminho):
    cmd = ["ffmpeg", "-v", "error", "-i", str(caminho), "-ac", "2", "-ar", str(SR),
           "-f", "f32le", "-"]
    raw = subprocess.run(cmd, check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()


def energia_banda(mono, hop, n, f0, f1):
    """Energia (dB) de uma banda em janelas de `n` amostras a cada `hop`."""
    win = np.hanning(n).astype(np.float32)
    freqs = np.fft.rfftfreq(n, 1 / SR)
    sel = (freqs >= f0) & (freqs < f1)
    out = []
    for i in range(0, len(mono) - n, hop):
        spec = np.abs(np.fft.rfft(mono[i:i + n] * win)) ** 2
        out.append(10 * np.log10(spec[sel].sum() + 1e-12))
    return np.array(out)


def estimar_bpm(mono):
    hop, n = 512, 2048
    win = np.hanning(n).astype(np.float32)
    prev = None
    flux = []
    for i in range(0, len(mono) - n, hop):
        mag = np.log1p(np.abs(np.fft.rfft(mono[i:i + n] * win)))
        if prev is not None:
            flux.append(np.maximum(mag - prev, 0).sum())
        prev = mag
    flux = np.array(flux) - np.mean(flux)
    ac = np.correlate(flux, flux, "full")[len(flux) - 1:]
    fr = SR / hop
    melhor, bpm = -1, 120.0
    for b in np.arange(70, 180, 0.5):
        lag = fr * 60 / b
        v = sum(ac[int(round(lag * k))] for k in (1, 2, 4) if int(round(lag * k)) < len(ac))
        if v > melhor:
            melhor, bpm = v, b
    return float(bpm)


def achar_drop(mono, compasso):
    """Instante em que o grave (30-120 Hz) mais sobe depois de um trecho baixo."""
    hop = int(SR * 0.05)
    low = energia_banda(mono, hop, 4096, 30, 120)
    t = np.arange(len(low)) * hop / SR
    passos = int(round(compasso * 2 / 0.05))      # dois compassos
    melhor, quando = -1e9, None
    for i in range(passos, len(low) - passos):
        antes = np.median(low[i - passos:i])
        depois = np.median(low[i:i + passos])
        if depois - antes > melhor:
            melhor, quando = depois - antes, t[i]
    return quando, melhor


def refinar_drop(mono, aprox, janela=1.0):
    """Ajusta o drop ao ataque mais forte (subida de volume em 50 ms) perto de `aprox`."""
    h = int(SR * 0.01)
    i0, i1 = int(max(0, aprox - janela) * SR), int(min(len(mono) / SR, aprox + janela) * SR)
    seg = mono[i0:i1]
    rms = np.sqrt(np.array([np.mean(seg[k:k + h] ** 2) for k in range(0, len(seg) - h, h)]) + 1e-12)
    db = 20 * np.log10(rms)
    salto = db[5:] - db[:-5]
    return (i0 + (int(np.argmax(salto)) + 5) * h) / SR


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("--bpm", type=float)
    ap.add_argument("--drop", type=float, help="segundo do drop na faixa original")
    ap.add_argument("--compassos", type=int, help="total de compassos no vídeo (par)")
    ap.add_argument("--max", type=float, default=MAX_TRECHO, help="duração máxima do trecho (s)")
    ap.add_argument("--projeto", help="pasta do projeto HyperFrames (padrão: este)")
    a = ap.parse_args()
    global RAIZ
    if a.projeto:
        RAIZ = Path(a.projeto).resolve()

    st = ler_audio(a.audio)
    mono = st.mean(axis=1)
    bpm = a.bpm or estimar_bpm(mono)
    compasso = 4 * 60 / bpm
    n_comp = a.compassos or max(4, int((a.max + 0.01) // compasso) // 2 * 2)
    antes = n_comp // 2
    drop = a.drop
    if drop is None:
        drop, ganho = achar_drop(mono, compasso)
        drop = refinar_drop(mono, drop)
        print(f"drop encontrado em {drop:.2f}s (grave +{ganho:.1f} dB)")
    inicio = max(0.0, drop - antes * compasso)
    dur = n_comp * compasso
    if inicio + dur > len(st) / SR:
        inicio = max(0.0, len(st) / SR - dur)
    i0, i1 = int(inicio * SR), int((inicio + dur) * SR)
    trecho = st[i0:i1].copy()
    drop_rel = drop - inicio
    print(f"bpm {bpm:.1f} · {n_comp} compassos de {compasso:.2f}s · trecho {inicio:.2f}s → {inicio + dur:.2f}s · drop em {drop_rel:.2f}s")

    # áudio do trecho com fades curtos
    fi, fo = int(0.02 * SR), int(OUTRO * SR)
    trecho[:fi] *= np.linspace(0, 1, fi)[:, None]
    saida = np.concatenate([trecho, np.zeros((fo, 2), np.float32)])
    # deixa o fim do trecho soar até o logo, com fade
    cauda = st[i1:i1 + fo].copy()
    if len(cauda):
        cauda *= np.linspace(1, 0, len(cauda))[:, None]
        saida[len(trecho):len(trecho) + len(cauda)] = cauda
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2",
                    "-i", "-", str(RAIZ / "assets/trecho.wav")], input=saida.tobytes(), check=True)

    # análise quadro a quadro
    m = trecho.mean(axis=1)
    n = 4096
    win = np.hanning(n).astype(np.float32)
    freqs = np.fft.rfftfreq(n, 1 / SR)
    nb = 64
    bordas = np.geomspace(30, 12000, nb + 1)
    bandas = [(30, 120), (120, 400), (400, 2000), (2000, 5000), (5000, 12000)]
    quadros = int(round(dur * FPS))
    espec, faixas, estereo = [], [], []
    pico = np.abs(trecho).max() + 1e-9
    rng = np.random.default_rng(7)
    for q in range(quadros):
        c = int(q / FPS * SR)
        seg = m[max(0, c - n // 2): c + n // 2]
        if len(seg) < n:
            seg = np.pad(seg, (0, n - len(seg)))
        p = np.abs(np.fft.rfft(seg * win)) ** 2
        linha = []
        for k in range(nb):
            sel = (freqs >= bordas[k]) & (freqs < bordas[k + 1])
            v = p[sel].mean() if sel.any() else p[np.argmin(abs(freqs - bordas[k]))]
            linha.append(10 * np.log10(v + 1e-12))
        espec.append(linha)
        faixas.append([10 * np.log10(p[(freqs >= f0) & (freqs < f1)].sum() + 1e-12) for f0, f1 in bandas])
        # campo estéreo: 90 amostras do quadro
        bloco = trecho[c: c + SR // FPS]
        if len(bloco):
            idx = rng.choice(len(bloco), size=min(90, len(bloco)), replace=False)
            L, R = bloco[idx, 0] / pico, bloco[idx, 1] / pico
            M, S = (L + R) / 2, (L - R) / 2
            estereo.append([int(x) for x in np.clip(np.stack([S, M], 1) * 130, -99, 99).round().flatten()])
        else:
            estereo.append([])

    espec = np.array(espec)
    # suaviza no tempo: sobe rápido, cai devagar
    for q in range(1, len(espec)):
        espec[q] = np.maximum(espec[q], espec[q - 1] - 1.6)
    lo, hi = np.percentile(espec, 2), espec.max()
    espec = np.clip((espec - lo) / (hi - lo) * 100, 0, 100).round().astype(int)

    faixas = np.array(faixas)
    for q in range(1, len(faixas)):
        faixas[q] = np.maximum(faixas[q], faixas[q - 1] - 1.2)
    fmin = np.percentile(faixas, 5, axis=0)
    fmax = faixas.max(axis=0)
    faixas = np.clip((faixas - fmin) / (fmax - fmin + 1e-9) * 100, 0, 100).round().astype(int)

    colunas = 200
    passo = len(m) // colunas
    onda = [int(round(np.abs(m[i * passo:(i + 1) * passo]).max() / (np.abs(m).max() + 1e-9) * 100))
            for i in range(colunas)]

    # golpes de grave (bumbos): subidas fortes na faixa 30-120 Hz
    gr = np.array([10 * np.log10(10 ** (x / 10)) for x in np.array(faixas)[:, 0]], float)
    golpes, ultimo = [], -99
    for q in range(2, len(gr)):
        if gr[q] - gr[q - 2] > 18 and gr[q] > 55 and q - ultimo > 6:
            golpes.append(q); ultimo = q

    q_drop = int(round(drop_rel * FPS))
    q_ref0 = max(0, q_drop - 2 * FPS)
    fantasma = espec[q_ref0:q_drop].mean(axis=0).round().astype(int).tolist() if q_drop > 0 else []

    dados = {
        "fps": FPS, "bpm": round(bpm), "compassos": n_comp, "compasso": compasso,
        "duracao": dur, "drop": drop_rel, "dropCompasso": antes + 1,
        "espectro": espec.tolist(), "fantasma": fantasma, "faixas": faixas.tolist(),
        "estereo": estereo, "onda": onda, "golpes": golpes,
    }
    js = json.dumps(dados, separators=(",", ":"))

    painel = RAIZ / "compositions/painel.html"
    html = painel.read_text()
    html = re.sub(r"/\*DADOS\*/.*?/\*FIM\*/", lambda _: f"/*DADOS*/{js}/*FIM*/", html, flags=re.S)
    painel.write_text(html)

    total = dur + OUTRO
    idx = RAIZ / "index.html"
    t = idx.read_text()
    t = re.sub(r'(<!--DUR-->[^>]*?data-duration=")[0-9.]+', lambda mm: f"{mm.group(1)}{total:.3f}", t)
    t = re.sub(r'(id="painel"[^>]*?data-duration=")[0-9.]+', lambda mm: f"{mm.group(1)}{total:.3f}", t, flags=re.S)
    t = re.sub(r'(id="root"[^>]*?data-duration=")[0-9.]+', lambda mm: f"{mm.group(1)}{total:.3f}", t, flags=re.S)
    t = re.sub(r'(id="trecho"[^>]*?data-duration=")[0-9.]+', lambda mm: f"{mm.group(1)}{total:.3f}", t, flags=re.S)
    idx.write_text(t)
    print(f"ok: vídeo de {total:.2f}s, {quadros} quadros analisados ({len(js) // 1024} KB de dados)")


if __name__ == "__main__":
    main()
