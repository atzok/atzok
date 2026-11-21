# Figma → code: design system rules for this repository

Rules for turning Figma designs (via the Figma MCP) into code in `atzok/atzok`.
Read this before calling `get_design_context` or writing UI from a Figma frame.

## 0. What this codebase actually is

| Area | Reality today |
|---|---|
| Product code | One HyperFrames video project: `videos/apresentacao/` (Ätzøk 60 s vertical intro). |
| Agent tooling | Installed agent skills in `.agents/skills/` (symlinked into `.claude/skills/`), locked in `skills-lock.json`. Not app code: never edit them to implement a design. |
| UI framework | None. No React/Vue/Svelte, no app bundler. Plain HTML + CSS + GSAP 3.15 (CDN). |
| Component library / Storybook | None. "Components" are HyperFrames scene files. |
| Design tokens file | None in the repo. Values are hardcoded hex/px in each scene's `<style>`. The brand's tokens live in the Ätzøk design system (section 1). |
| Build | `hyperframes` CLI, pinned in `videos/apresentacao/package.json` (`hyperframes@0.9.72`): `check` (lint), `render` (MP4), `preview`. |

So "implementing a Figma design" here means one of:
1. a new or changed **video scene** (`videos/<project>/compositions/*.html`), or
2. a new **static brand piece** (press kit page, flyer, social card) as a new folder, following the same tokens.

If a request needs a real web app (React, etc.), say so and scaffold it in its own folder; do not bolt it onto the video project.

## 1. Design tokens (Ätzøk brand)

Source of truth: the Ätzøk design system (`project/ds/atzok/tokens.json` in the "ÄTZØK — Press Kit 2026/27" canvas on claude.ai). Mirror of the values used in code:

### Color

| Token | Value | Use |
|---|---|---|
| `surface` | `#000000` (dark) / `#FFFFFF` (light) | Page and scene ground. Black is the brand default. |
| `surface-raised` | `#141414` / `#F2F2F2` | Cards and blocks on `surface`. |
| `ink` | `#FFFFFF` / `#000000` | Main text and wordmark (21:1). |
| `muted` | `#9A9A9A` / `#5E5E5E` | Secondary text, credits, dates (≥ 6:1). |
| `ember` | `#BC6D21` | Accent. Text on black OK (5.3:1); on white only at 24 px+. |
| `plum` | `#7E406E` | Accent. Text on white OK (7.3:1); on black decorative only, never text. |
| `dusk` | `#985359` | Decorative only (gradient middle). |

Rules:
- One accent per screen, carrying meaning (a label, the highlighted word, a rule line). Never ember and plum as text on the same ground.
- Map Figma variables/styles to these names. If a Figma hex is within a few units of a token, use the token; if it is genuinely new, ask before adding it.
- Dimmed "past" items in lists use `#5E5E5E` on black (see `som.html`, `palcos.html`).

### Typography

The brand family is a heavy grotesk (`"Helvetica Neue", Arial`). In HyperFrames only bundled fonts resolve by name, so:

| Role | Code | Size in 1080×1920 video |
|---|---|---|
| Display / hero | `font-family: Inter; font-weight: 900; text-transform: uppercase; letter-spacing: -0.03em…-0.04em; line-height: 0.88–1` | 92–168 px |
| Headline | Inter 900 uppercase | 54–76 px |
| Label / kicker | `font-family: "Space Mono"; font-weight: 700; uppercase; letter-spacing: 0.18em` | 28–30 px |
| Body | Inter 400 | 36–40 px |

- Nothing readable under 28 px in video (lint `text_below_floor`).
- Any other Figma font needs `@font-face` to a file in `assets/fonts/`; do not reference system or Google fonts by name.
- Web pieces (press kit HTML) have used Anton / Special Elite / Space Mono; for new work follow the design system above unless the Figma file says otherwise.

### Spacing and radius

| Token | Value |
|---|---|
| `space-2` / `space-4` / `space-6` / `space-12` | 8 / 16 / 24 / 48 px |
| `radius-none` | 0 (color blocks, photos) |
| `radius-md` | 8 px (buttons, cards) |
| `radius-full` | 9999 px (badge disc, graffiti drips) |

### Token format going forward

There is no token transformation pipeline. When a second project reuses the brand, create `brand/tokens.css`:

```css
:root {
  --surface: #000; --ink: #fff; --muted: #9a9a9a;
  --ember: #bc6d21; --plum: #7e406e; --dusk: #985359;
}
```

HyperFrames scenes can read `var(--token)` if the root `index.html` defines them; today each scene hardcodes hex, so keep values identical to the table when editing.

## 2. "Components": HyperFrames scenes

Root `videos/apresentacao/index.html` mounts one host per scene; each scene is a self-contained file.

```html
<!-- index.html: host (ids must match the scene's data-composition-id) -->
<div id="bio" data-composition-id="bio" data-composition-src="compositions/bio.html"
  data-start="4.067" data-duration="9.4" data-track-index="1" data-track-kind="graphics"
  data-width="1080" data-height="1920"></div>
```

```html
<!-- compositions/bio.html: everything inside <template>, root styled as #root -->
<template>
  <style>
    #root { position: absolute; inset: 0; background: #000; overflow: hidden; }
    .bi-big { position: absolute; left: 130px; font-family: Inter, sans-serif; font-weight: 900;
      color: #fff; line-height: .88; letter-spacing: -.035em; text-transform: uppercase; }
  </style>
  <div id="root" data-composition-id="bio" data-width="1080" data-height="1920">
    <div id="bi-12" class="bi-big clip" data-start="0" data-duration="9.4" data-track-index="4">12 anos</div>
  </div>
  <script>
    (function () {
      const tl = gsap.timeline({ paused: true });
      tl.fromTo("#bi-12", { opacity: 0, scale: 1.12 }, { opacity: 1, scale: 1, duration: .45, ease: "expo.out" }, 4.68);
      window.__timelines["bio"] = tl;
    })();
  </script>
</template>
```

Rules when translating a Figma frame into a scene:
- One Figma frame (or section) = one scene file. Prefix every id with the scene's short code (`bi-`, `so-`, `la-`, `pa-`, `bo-`, `ab-`).
- Every visible element is written in the HTML with a stable `id`, `class="clip"`, `data-start`, `data-duration`. Never create elements from script.
- Animate with `gsap.fromTo` on the scene's own paused timeline; never `from`, `play()`, CSS `transform` on a GSAP-animated element, or `display`/`visibility` tweens on a `.clip`.
- Figma auto-layout → absolute positions in px (the canvas is fixed 1080×1920). Keep text left-aligned at `left: 130px` (the house layout).
- Time entrances to the narration words or the music beat (89.6 BPM: `bt(k) = round(k · 60/89.6 · 30) / 30`), as the existing scenes do.
- After any edit: `npm run check` (from `videos/apresentacao/`), fix every error, then snapshot the changed seconds before rendering.

## 3. Layout and "responsive"

There is no responsive web layout. Video formats are fixed canvases:
- **Vertical 9:16, 1080×1920** (Reels/TikTok/Shorts). Keep all text inside the platform safe area: x 130–888 px (780 px below y 840), y 288–1248 px. The bottom ~670 px is covered by app UI: decoration only.
- A Figma frame in another aspect is recomposed, not scaled.
- For web pieces (if added): fluid layout, `max-width` container, works at 390 px phone width, 16 px side gutter.

## 4. Assets

- Stored per project in `videos/<project>/assets/`, referenced as `assets/...` (no leading `/`), also inside scene files.
- Logos come only from the real source files, never redrawn from Figma vectors by hand:
  - `assets/wordmark-branco.png`: white graffiti wordmark, for black grounds.
  - `assets/wordmark-preto.png`: black version (generated from the white one) for white/paper grounds.
  - The ember→plum gradient wordmark exists in the press kit but the brand currently uses black and white.
- Export Figma images with the Figma MCP's asset download into `assets/`; PNG for logos/flat art, JPG for photos.
- Audio and voice files (`*.wav`, `*.mp3`, `*.m4a`, `assets/voice/`) are git-ignored on purpose: the music is an unreleased demo. Do not commit them.
- No CDN or optimization pipeline. GSAP loads from jsDelivr; the render bundles everything locally.

## 5. Icons

There is no icon system. If a Figma design uses icons:
- Inline SVG with `stroke="currentColor"`, `aria-hidden="true"` when decorative.
- Name them by meaning (`icon-instagram`, `icon-arrow-right`), store reusable ones in `videos/<project>/assets/icons/`.
- Never use emoji as icons; separators in text use `·` and `✶` (the brand's flyer star).

## 6. Styling approach

- Plain CSS inside each scene's `<template><style>`, scoped by the scene's `#root` and id prefixes. No CSS Modules, Tailwind or CSS-in-JS.
- No global stylesheet; the root `index.html` holds only `:root` variables, `body` size and the scene hosts.
- Brand look: black ground, white heavy uppercase type, one ember accent, photocopy/xerox flicker as the signature motion (two-frame opacity dip to 0.55 on a downbeat).

## 7. Project structure

```
atzok/
├── CLAUDE.md                  # graphify rules (+ pointer to this file)
├── docs/figma-design-system-rules.md
├── skills-lock.json           # installed agent skills (npx skills)
├── .agents/skills/, .claude/  # agent tooling, not product code
└── videos/
    └── apresentacao/          # one HyperFrames project per video
        ├── index.html         # root: scene hosts + <audio> (music, voice lines)
        ├── compositions/      # one scene per file
        ├── assets/            # logos (tracked), audio (ignored)
        ├── narracao.txt       # narration script
        └── renders/           # MP4 output (ignored)
```

New videos go in `videos/<slug>/` created with `hyperframes init`. New brand pages go in their own top-level folder (for example `presskit/`).

## 8. Figma MCP workflow checklist

1. Get the file key and node id from the Figma URL; `create_session` first.
2. Load the `figma-design-to-code` skill (via the Figma MCP) before `get_design_context`.
3. Treat the returned code as a reference: rewrite it into the target format (HyperFrames scene or plain HTML/CSS), replacing every color, font and spacing with the tokens in section 1.
4. Pull real assets (logos, photos) through the MCP; never trace them.
5. Check: `npm run check` for video, contrast per the color table, safe area for vertical.
6. Ask before introducing a new token, font, or framework.
