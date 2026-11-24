# ÄTZØK / RAIO-X

Vídeo vertical (1080×1920, ~30 s) que mostra uma faixa por dentro: forma de onda,
espectro, faixas de frequência e campo estéreo, tudo tirado do áudio real.
A frase de cima troca no drop; no fim entram o wordmark e o @.

## Um vídeo novo

1. Coloque o áudio da faixa em qualquer lugar (wav, mp3, flac).
2. Rode a análise (acha BPM e drop sozinha):

       python3 tools/analisar.py caminho/da/faixa.wav

   Se errar, force: `--bpm 140`, `--drop 92.5` (segundo do drop na faixa
   original), `--compassos 8`.
3. Troque nome da faixa e frases nas variáveis de `index.html`
   (`titulo`, `frase1`, `frase2`, `handle`) ou no painel de variáveis do preview.
4. Confira: `npx --yes hyperframes@0.9.72 check --safe-zone reels`
   e `npx --yes hyperframes@0.9.72 preview`.
5. Renderize: `npx --yes hyperframes@0.9.72 render`.

O áudio cortado (`assets/trecho.wav`) não vai para o git.
