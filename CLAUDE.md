# RealRate — Claude Guide

## What This Project Is
RealRate is a B2B fintech that uses explainable causal AI to evaluate and rank company financial health.
Social media and marketing is managed by Amneh Qaljawi.

---

## Folder Structure

```
RealRate/
├── context/                      ← Stable reference data — load as needed
│   ├── brand-core.md             ← Company identity, LinkedIn strategy, standing rules (always load)
│   ├── brand-voice.md            ← Tone rules, what not to say, Holger's voice (always load)
│   ├── design-system.md          ← All visual specs: colors, typography, layouts, export
│   ├── audience.md               ← ICP profiles and differentiators
│   ├── product-offering.md       ← Products, value prop, pricing, social proof
│   ├── competitive-landscape.md  ← Competitor profiles and content angles
│   └── sources.md                ← Trusted URLs for research
│
├── skills/                       ← Executable task workflows — load the matching skill file
│   ├── linkedin-post.md          ← Write a LinkedIn company page post
│   ├── holger-post.md            ← Write a Holger personal LinkedIn post
│   ├── insight-post.md           ← Build insight posts (types 1–4): design + caption
│   ├── deep-dive.md              ← Build a deep dive LinkedIn document
│   ├── content-calendar.md       ← Plan a content calendar (company page or Holger)
│   ├── outreach-campaign.md      ← Write Instantly campaigns or LinkedIn DM sequences
│   └── market-research.md        ← Run competitor or market research
│
└── SOP/                          ← Multi-step process references
    ├── ranking-publication-protocol.md  ← Full ranking launch sequence (Day 0 → Day +10)
    ├── outreach-sop.md                  ← LinkedIn DM + Instantly detailed process
    └── research-sop.md                  ← Market and competitor research process
```

---

## How to Use

**For any task:** Find the matching skill file in `skills/` and follow it. Each skill file lists exactly which context files to load and the steps to execute.

**Context files** are the base layer — reference data that skills point to.
**Skill files** are the execution layer — load only what the task needs.
**SOP files** are detailed process references — consulted for complex multi-step operations.

---

## Quick Skill Lookup

| Task | Skill file | Also load |
|---|---|---|
| Write a LinkedIn company post | `skills/linkedin-post.md` | — |
| Write a Holger personal post | `skills/holger-post.md` | — |
| Build an insight post (design + caption) | `skills/insight-post.md` | — |
| Build a deep dive document | `skills/deep-dive.md` | — |
| Plan a content calendar | `skills/content-calendar.md` | — |
| Write an Instantly campaign or sequence | `skills/outreach-campaign.md` | — |
| Run competitor or market research | `skills/market-research.md` | — |
| Full ranking launch | `SOP/ranking-publication-protocol.md` | `skills/insight-post.md` · `skills/deep-dive.md` |

---

## Standing Rules

- **Always verify ECR data** against https://www.realrate-archive.com before finalising any content
- **Never use:** "excited to share," "game-changing," "revolutionary," "best-in-class" without data
- **Never link** to sales pages, pricing, or the archive in public posts
- **Archive is internal only** — data verification only, never shared publicly
- **Never tag companies** in captions — always in first pinned comment
- **No hashtags** in captions
- **Ranking link in caption** — always end with realrate.ai/rankings/[industry]/[year]
- **Never use "we"** — always "RealRate"
- **Company page is primary** — only produce Holger personal page content when explicitly requested
- **No emojis on images** — max 2 in captions
- **Tagline on image only** — never in the caption
- **Pinned comments:** Day 0 (ranking carousel) and Day +1 (seal post) only

---

## Key Links

| | URL |
|---|---|
| Website | https://realrate.ai |
| Archive *(internal, data verification only)* | https://www.realrate-archive.com |
| LinkedIn Company | https://www.linkedin.com/company/realrate/ |
| LinkedIn Holger | https://www.linkedin.com/in/dr-holger-bartel/ |
| News | https://news.realrate.ai |
