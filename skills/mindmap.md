---
description: Generate a RealRate mind map for one or more companies. Usage: /mindmap <company> [company2 ...] | /mindmap all
argument-hint: <company | all>
allowed-tools: [Bash]
---

# Mind Map Generator

Generate 1920×1080 LinkedIn mind map images for one or more RealRate-ranked companies.

## Arguments

The user invoked this command with: $ARGUMENTS

## Supported Companies

| Argument | Company | Industry | ECR | Rank |
|---|---|---|---|---|
| `trilinc` | TriLinc Global | US Finance Services | 124% | #1/4 |
| `strata` | Strata Critical Medical | US Air | 123% | #1/4 |
| `hp` | HP Inc. | US Computers | 258% | #9/17 |
| `angi` | Angi Inc. | US Advertising | 157% | #1/4 |
| `nvidia` | Nvidia Corp. | US Semiconductors | 351% | #8/44 |
| `tesla` | Tesla Inc. | US Motor | 135% | #9/38 |
| `apple` | Apple Inc. | US Computers | 430% | #1/17 |
| `harley` | Harley Davidson INC | US Motor | 147% | #5/38 |

Use `all` to run every company in sequence.

## Instructions

1. Parse $ARGUMENTS. Lowercase and trim each token.
2. If no argument is given, list the supported companies above and stop.
3. If the argument is `all`, expand to the full company list above.
4. For each company in the list:
   - Run via Bash:
     ```
     python gen_mindmap.py <company>
     ```
   - `gen_mindmap.py` is the source of truth for supported companies. If it exits with an error, report the error message to the user and continue to the next company.
   - On success, report the output path printed by the script (e.g. `Done (1920×1080): <path>`).
5. After all runs, print a summary:
   - ✓ succeeded: list company names
   - ✗ failed: list company names with their error

## Output locations

Each company writes to its own subfolder inside the project directory:

| Company | Subfolder |
|---|---|
| trilinc | *(root — no subfolder)* |
| strata | `Strata Critical Medical/` |
| hp | `HP Inc/` |
| angi | `Angi Inc/` |
| nvidia | `Nvidia Corp/` |
| tesla | `Tesla Inc/` |
| apple | `Apple Inc/` |
| harley | `Harley Davidson INC/` |

Files per company: `<company>-mindmap.png` (1920×1080) · `<company>-linkedin-post.txt`

## First-run dependencies

The generator needs the packages in `requirements.txt` (repo root) and a
one-time Playwright browser install. If a run fails with a missing package or
missing browser error, tell the user to run:

```
pip install -r requirements.txt
playwright install chromium
```

and then retry — do not silently install dependencies without asking first.
Fall back to `python3`/`pip3` if `python`/`pip` don't resolve on this machine.

## Automation scripts (run outside Claude)

- PowerShell: `.\run_mindmaps.ps1 apple nvidia` or `.\run_mindmaps.ps1 all`
- Bash:        `bash run_mindmaps.sh apple nvidia` or `bash run_mindmaps.sh all`
