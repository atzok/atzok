#!/usr/bin/env python3
"""Gera vários RAIO-X de uma vez.

Uso: python3 tools/lote.py <config.json> <pasta-dos-audios> [só-estas: 01 03 ...]

No config: "projeto" (pasta do projeto, relativa ao config), "max" (duração
do trecho em s), "variaveis" (quais campos viram variáveis), "previa": true
(gera também uma cópia 720p leve).

Para cada faixa: analisa o áudio (tools/analisar.py) e renderiza
renders/<saida>.mp4 com as variáveis da faixa (titulo, frase1, frase2,
versao, credito). Campos opcionais por faixa: bpm, drop, compassos.
"""
import json, subprocess, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ANALISAR = RAIZ / "tools/analisar.py"
CLI = Path.home() / ".claude/skills/hyperframes/scripts/plugin-cli.mjs"

cfg = json.loads(Path(sys.argv[1]).read_text())
if cfg.get("projeto"):
    RAIZ = (Path(sys.argv[1]).resolve().parent / cfg["projeto"]).resolve()
pasta = Path(sys.argv[2])
filtro = sys.argv[3:]
VARS = cfg.get("variaveis", ["titulo", "frase1", "frase2", "handle", "versao", "credito"])
for f in cfg["faixas"]:
    if filtro and not any(f["audio"].startswith(x) for x in filtro):
        continue
    args = [sys.executable, str(ANALISAR), str(pasta / f["audio"]), "--projeto", str(RAIZ)]
    if cfg.get("max"):
        args += ["--max", str(cfg["max"])]
    for k in ("bpm", "drop", "compassos"):
        if k in f:
            args += [f"--{k}", str(f[k])]
    subprocess.run(args, check=True)
    v = {k: f[k] for k in VARS if k in f}
    v.setdefault("versao", "")
    v.setdefault("credito", "")
    out = RAIZ / "renders" / f"{f['saida']}.mp4"
    subprocess.run(["node", str(CLI), "render", "--output", str(out), "--variables", json.dumps(v, ensure_ascii=False)],
                   cwd=RAIZ, check=True, stdout=subprocess.DEVNULL)
    if cfg.get("previa"):
        prev = out.with_name(out.stem + "-previa.mp4")
        log = str(RAIZ / ".hyperframes/x264")
        for passo in (1, 2):
            cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(out), "-vf", "scale=720:1280:flags=lanczos", "-c:v", "libx264",
                   "-profile:v", "main", "-level", "4.0", "-preset", "slow", "-b:v", "480k", "-pass", str(passo), "-passlogfile", log]
            cmd += ["-an", "-f", "mp4", "/dev/null"] if passo == 1 else ["-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(prev)]
            subprocess.run(cmd, check=True)
    print("ok:", out)
