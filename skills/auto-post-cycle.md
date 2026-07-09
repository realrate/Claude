---
description: Generate and upload LinkedIn content for a full bizdev cycle
arguments: industry_slug year [task1 task2 ...]
---

# Auto-Post Cycle — Orchestrator Skill

Generate all (or selected) LinkedIn deliverables for an industry/year and upload them as drafts to the LinkedIn Scheduler dashboard.

## Arguments

- `$ARGUMENTS` is parsed as: `{industry_slug} {year} [task1 task2 ...]`
- `industry_slug` (required) — e.g., `us_air`, `us_construction`
- `year` (required) — marketing year (balance sheet year = year - 1)
- Tasks (optional) — space-separated task IDs. Defaults to all. `insights` expands to `insight1 insight2 insight3 insight4`.

Valid task IDs: `top10`, `article`, `seal`, `insight1`, `insight2`, `insight3`, `insight4`, `deepdive`, `insights`, `all`

## Step 0 — Pull Latest Skills

```bash
cd C:\Users\User\Claude && git pull
```

This ensures all skill files, context files, and design system rules are up to date.

## Step 1 — Parse Arguments and Set Up Output Directory

Parse `$ARGUMENTS` into `industry_slug`, `year`, and `selected_tasks`.
- If no tasks specified, select all 8: `top10 article seal insight1 insight2 insight3 insight4 deepdive`
- If `insights` is specified, expand to `insight1 insight2 insight3 insight4`
- If `all` is specified, select all 8

Create output directory:
```
C:\Users\User\Claude\output\{industry_slug}\{year}\
```

Set variables:
- `archive_slug` = `industry_slug` with `us_` prefix removed (e.g., `us_air` → `air`)
- `bsy` = `year - 1` (balance sheet year)
- `ranking_url` = `https://realrate-archive.com/{archive_slug}/{bsy}/website-ranking.json`
- `prior_url` = `https://realrate-archive.com/{archive_slug}/{bsy - 1}/website-ranking.json`
- `output_dir` = `C:\Users\User\Claude\output\{industry_slug}\{year}`

## Step 2 — Fetch Ranking Data

Fetch the ranking JSON:
```
GET {ranking_url}
```

Parse and extract:
- Full company list with rank, ECR value, trend, top_rated flag, report_text
- List of top-rated companies (where `top_rated === true`)
- Industry name from the data

If `insight2` is in selected tasks, also fetch `{prior_url}` for YoY comparison.

**If fetch fails, STOP the pipeline and report the error.** Ranking data is required for all tasks.

## Step 3 — Check Angle History (if generating insight3 or insight4)

If `insight3` or `insight4` is in selected tasks:

```bash
curl -H "Authorization: Bearer $ADMIN_SECRET" \
  "https://realrate-linkedin-scheduler.vercel.app/api/angles?slug={industry_slug}"
```

Parse the response to find angles used in the last 2 cycles. These angles are **excluded** from selection.

## Step 4 — Generate Each Selected Task

For each task, load the relevant skill file and follow its exact instructions. Do NOT hardcode captions or design rules — they come from the skill files.

### Task: `top10`
1. Read `skills/top10ranking.md`
2. Run: `python generate_infographic.py {archive_slug}`
3. Copy output to `{output_dir}/top10_{industry_slug}_{year}.png`
4. Write caption following the template in `top10ranking.md` → save to `{output_dir}/top10_caption.txt`

### Task: `article`
1. Read `skills/linkedin-post.md` + `context/brand-core.md` + `context/brand-voice.md` + `context/design-system.md`
2. Build HTML following the design system (1200×1200px canvas, Manrope font, dark background)
3. Save HTML to `{output_dir}/article_announce.html`
4. Export: `node posts/export.mjs` → `{output_dir}/article_announce.png`
5. Write caption using the storytelling formula → save to `{output_dir}/article_announce_caption.txt`

### Task: `seal`
1. Run the Drive download script:
   ```bash
   python scripts/pull_seal_posts.py --industry {industry_slug} --output-dir {output_dir}
   ```
2. For each downloaded seal post:
   - Read the existing caption from `seal_{company}_caption.txt`
   - Web search for the company's CEO and CFO LinkedIn profiles
   - Append C-level mentions to the caption: `cc @FirstName LastName — CEO, @FirstName LastName — CFO`
   - Save updated caption back to `seal_{company}_caption.txt`
3. If Drive download fails (no `GOOGLE_SERVICE_ACCOUNT_KEY`), skip seal posts and report the error.

### Task: `insight1`
1. Read `skills/finalinsightpost.md` (Insight 1 section) + all context files
2. Select an angle from the Insight 1 angle bank: **Reputable NTR**, **Unknown TR**, or **The Surprise**
3. Pick a company that fits the angle. Verify its ECR data at `realrate-archive.com/{archive_slug}/{bsy}/`
4. Build HTML using the L4 layout from `design-system.md`
5. Save HTML to `{output_dir}/insight1_{company_slug}.html`
6. Export PNG: `node posts/export.mjs` → `{output_dir}/insight1_{company_slug}.png`
7. Write caption per the approved Insight 1 structure → save to `{output_dir}/insight1_caption.txt`

### Task: `insight2`
1. Read `skills/finalinsightpost.md` (Insight 2 section) + all context files
2. Choose: **Industry-Wide** or **Company-Level YoY Shift** based on the data (compare current vs prior year)
3. Build up to 3 HTML slides using the L2 layout
4. Save as `{output_dir}/insight2_slide1_{slug}.html`, `insight2_slide2_{slug}.html`, etc.
5. Export each slide to PNG
6. Write one caption for all slides → save to `{output_dir}/insight2_caption.txt`

### Task: `insight3`
1. Read `skills/finalinsightpost.md` (Insight 3 section) + all context files
2. Select a **rotating angle** from the bank: Industry Blind Spot, Market vs Balance Sheet, Industry Trend, Methodology Moment, Investor Signal, Macro Lens
3. **Exclude** angles used in the last 2 cycles (from Step 3 angle history)
4. Build HTML (L4 layout), export PNG
5. Save to `{output_dir}/insight3_{angle_slug}.html` and `.png`
6. Write caption → save to `{output_dir}/insight3_caption.txt`

### Task: `insight4`
1. Read `skills/finalinsightpost.md` (Insight 4 section) + all context files
2. Select a **rotating NTR angle** from the bank: Almost There, The One Thing, The Fallen, Sector Drag, Close But Not Rated, Due Diligence Gap
3. **Exclude** angles used in the last 2 cycles (from Step 3 angle history)
4. Build HTML, export PNG
5. Save to `{output_dir}/insight4_{angle_slug}.html` and `.png`
6. Write caption with mandatory ECR disclaimer → save to `{output_dir}/insight4_caption.txt`

### Task: `deepdive`
1. Read `skills/deep-dive-carousel.md` + all context files
2. Build 8–10 slide PDF: cover → snapshot → top tier → biggest mover → surprise → warning → separators → implications → methodology → CTA
3. Save to `{output_dir}/deepdive.pdf`
4. Write caption → save to `{output_dir}/deepdive_caption.txt`

## Step 5 — Save Angle Selections (if insight3 or insight4 was generated)

If insight3 or insight4 was generated, save the selected angles to the dashboard:

```bash
curl -X POST -H "Authorization: Bearer $ADMIN_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"industrySlug":"{industry_slug}","year":{year},"angles":{"insight3":"{selected_insight3_angle}","insight4":"{selected_insight4_angle}"}}' \
  https://realrate-linkedin-scheduler.vercel.app/api/angles
```

Only include the angles that were actually generated (e.g., if only insight3 was requested, only send insight3).

## Step 6 — Upload to Dashboard

Run the upload script:

```bash
python C:\Users\User\realrate-linkedin-scheduler\upload_to_scheduler.py \
  --industry {industry_slug} --year {year} \
  --output-dir {output_dir} --token $ADMIN_SECRET
```

The script will find all generated files, encode them, and upload as drafts.

## Step 7 — Summary

Print a summary table:

```
╔══════════════════════════════════════════════╗
║  Auto-Post Cycle Complete                    ║
╠══════════════════════════════════════════════╣
║  Industry: U.S. Air                          ║
║  Year:     2026                              ║
║  Output:   C:\Users\User\Claude\output\...   ║
╠══════════════════════════════════════════════╣
║  ✓ top10     — Top 10 Ranking                ║
║  ✓ article   — Article Announcement          ║
║  ✓ seal (3)  — Seal Posts                    ║
║  ✓ insight1  — Company Editorial             ║
║  ✓ insight2  — Industry YoY (2 slides)       ║
║  ✓ insight3  — Macro Lens                    ║
║  ✓ insight4  — The Fallen                    ║
║  ✓ deepdive  — Deep Dive Document            ║
╠══════════════════════════════════════════════╣
║  Uploaded: 11 drafts                         ║
║  Dashboard: realrate-linkedin-scheduler...   ║
╚══════════════════════════════════════════════╝
```

Report any skipped tasks and errors.

**Remind:** "Review drafts in the dashboard before approving for publish."

## Error Handling

- **Ranking data fetch fails:** STOP — data is required for all tasks
- **Individual task fails:** Skip that task, continue with remaining tasks, report in summary
- **Drive not accessible:** Skip seal posts, report "Set up GOOGLE_SERVICE_ACCOUNT_KEY"
- **Puppeteer not installed:** Skip HTML-rendered tasks, report "Run `npm install` in `posts/`"
- **Upload fails:** Files persist in output folder — team can retry or upload manually
- **C-level search fails:** Keep caption without mentions, flag for manual review

## Standing Rules (from brand-core.md)

These rules apply to ALL generated captions and images:
- Never use hashtags (except Top 10 which uses exactly 8)
- Maximum 2 emoji per caption
- Never use "we" — always "RealRate"
- Ranking URL goes at the end of every caption
- The archive is internal only — never link directly to it
- Font minimum 18pt body, 46pt+ headlines (mobile readability)
- No emojis on images
