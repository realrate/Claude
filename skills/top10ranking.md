---
description: Generate a RealRate "Top 10" ranking LinkedIn post for an industry — a 1200x1500 infographic PNG plus a matching LinkedIn caption .txt, pulled live from realrate-archive.com. Use whenever asked to create/generate a top 10 ranking, industry ranking post, or LinkedIn infographic for an industry (e.g. "make the top 10 software ranking post", "generate this year's motor industry ranking", "do the air rankings"), even if only the industry is named.
argument-hint: [industry_slug]
---

# RealRate Top 10 Ranking Generator

Generates a 1200x1500 px portrait LinkedIn infographic plus a matching LinkedIn caption for a
RealRate industry "Top 10" ranking, using live data fetched from realrate-archive.com.

This skill requires the `generate_infographic.py` script and `requirements.txt` from the
**Top 10 ranking** project repo to be present in the project you invoke it from. It is not
self-contained inside this skills library — copy or check out the Top 10 ranking project
alongside it, then run commands from that project's root (`${CLAUDE_PROJECT_DIR}`).

## Setup (first run only)

```bash
pip install -r "${CLAUDE_PROJECT_DIR}/requirements.txt"
```

## Generate a ranking

```bash
python "${CLAUDE_PROJECT_DIR}/generate_infographic.py" <industry_slug>
```

This produces both output files together — never generate just the PNG or just the caption:

- `${CLAUDE_PROJECT_DIR}/output/<slug>_<year>.png` — the infographic
- `${CLAUDE_PROJECT_DIR}/output/linkedin_<slug>_<year>.txt` — the matching LinkedIn caption

If `$ARGUMENTS` names an industry (e.g. "motor", "software", "air"), map it to the closest slug
below and run the command. If it's ambiguous, ask which slug before running.

## Available slugs

`air` · `motor` · `software` · `computers` · `finance_services` · `food` · `health_services` ·
`advertising` · `semiconductors` · `programming` · `petrol` · `mining` · `construction` ·
`realestate` · `hotels` · `consulting` · `data_processing` · `brokers` · `savings` ·
`life` · `non_life` · `pharma` · `chemicals` · `state_banks` · `medicinal_products` · `recreation`

## Behavior notes

- Data source is archive-first: the script fetches live from realrate-archive.com. Cards show
  ECR%, a ★ TOP RATED badge where applicable, and trend arrows.
- Ranking links in the caption always use the `us_` prefix: `https://realrate.ai/rankings/us_<industry>/<year>`.
- Every industry gets a unique blue-tone accent and themed background pattern — accent colors
  must stay in the blue family even when the pattern differs per industry.
- Title, filename, and ranking URL use the current calendar year; the archive fetch itself uses
  the latest year available in the archive listing.
- Full design spec and field reference: see `top10ranking.md` at the root of the Top 10 ranking
  project repo.

## After generating

Report the output file paths and confirm both the PNG and the caption .txt were created.
