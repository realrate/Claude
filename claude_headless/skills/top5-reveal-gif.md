---
description: Generate a RealRate Top 5 reveal GIF for an industry — an animated countdown-style reveal from rank 5 up to rank 1. Ported from "Industry Deep Dive Carousel/generate_cover_gif.py" (real repo), fixing its Windows-only font paths and its hand-edit-per-industry template into a CLI-driven, cross-platform skill.
argument-hint: [industry_slug] [year (optional)]
---

# Practice Skill — Top 5 Reveal GIF

Generates a single animated GIF: ranks 5→1 reveal one at a time (suspense
builds toward the industry leader), holds on the fully-revealed frame,
then loops.

Design source: this is a direct port of the real repo's cover-GIF
generator, not a from-scratch design like `mindmap` — the layout concept
(reveal order, hold-then-loop) is preserved. What changed is fixed, not
reimagined; see "What was fixed" below.

## Arguments

- `$ARGUMENTS` parses as: `{industry_slug} [year]`
- `industry_slug` (required) — e.g. `air` (also accepts `us_air` / `us-air`)
- `year` (optional) — overrides the balance-sheet-year URL fetched

## Setup (first run only)

Same venv as `top10-infographic` / `mindmap` — Pillow + cairosvg only, no
browser:

```bash
python3 -m venv "${CLAUDE_PROJECT_DIR}/claude_practice/.venv"
"${CLAUDE_PROJECT_DIR}/claude_practice/.venv/bin/pip" install --upgrade pip
"${CLAUDE_PROJECT_DIR}/claude_practice/.venv/bin/pip" install Pillow cairosvg
```

## Generate

```bash
cd "${CLAUDE_PROJECT_DIR}/claude_practice"
"${CLAUDE_PROJECT_DIR}/claude_practice/.venv/bin/python" \
  "${CLAUDE_PROJECT_DIR}/claude_practice/scripts/generate_top5_reveal_gif.py" <industry_slug>
```

Pass `--year <year>` only if `$ARGUMENTS` explicitly names one.

## What was fixed vs. the real repo's version

1. **Font loading was Windows-only.** The original's `load_font()` only
   tried `C:\Windows\Fonts\...` paths, silently degrading to Pillow's
   bitmap default font everywhere else — invisible on Windows, ugly on
   Linux/Mac. This version reuses the cross-platform fallback chain
   already proven in `generate_infographic.py`.
2. **Hand-edited template → CLI-driven.** The original is meant to be
   edited in place (every `# EDIT` constant) per industry and left
   edited for the next run. This version takes the industry as an
   argument like every other skill here — no manual editing required.
3. **Duplicate-frame "hold" doesn't work in Pillow.** An early version of
   this script tried to hold the final frame by appending 4 duplicate
   `Image` objects — Pillow's GIF writer collapsed them back down to one
   frame even with `optimize=False` (verified: `im.n_frames` came back 5
   instead of the intended 9). Fixed by passing a **per-frame duration
   list** instead (`[700, 700, 700, 700, 3000]`) — the correct way to make
   one frame linger in a GIF. If you ever need a longer hold elsewhere in
   this project, use a duration list, not repeated frames.

## Output contract

- `claude_practice/output/us_<slug>/top5-reveal-gif/<slug>_<year>_top5.gif`

5 frames, 700ms per reveal step, 3000ms hold on the final frame, infinite
loop.

## After generating

Report the output GIF path and frame count from stdout.
