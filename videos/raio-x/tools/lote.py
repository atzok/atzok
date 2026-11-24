#!/usr/bin/env python3
"""Gera vários RAIO-X de uma vez.

Uso: python3 tools/lote.py faixas/bliss030.json <pasta-dos-audios> [só-estas: 01 03 ...]

Para cada faixa: analisa o áudio (tools/analisar.py) e renderiza
renders/<saida>.mp4 com as variáveis da faixa (titulo, frase1, frase2,
versao, credito). Campos opcionais por faixa: bpm, drop, compassos.
"""
import json, subprocess, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CLI = Path.home() / ".claude/skills/hyperframes/scripts/plugin-cli.mjs"

cfg = json.loads(Path(sys.argv[1]).read_text())
pasta = Path(sys.argv[2])
filtro = sys.argv[3:]
VARS = ["titulo", "frase1", "frase2", "handle", "versao", "credito"]
for f in cfg["faixas"]:
    if filtro and not any(f["audio"].startswith(x) for x in filtro):
        continue
    args = [sys.executable, str(RAIZ / "tools/analisar.py"), str(pasta / f["audio"])]
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
    print("ok:", out)
