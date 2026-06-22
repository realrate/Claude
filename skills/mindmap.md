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

Use `all` to run every company in sequence.

## Instructions

1. Parse $ARGUMENTS. Lowercase and trim each token.
2. If no argument is given, list the supported companies and stop.
3. If the argument is `all`, expand to the full company list above.
4. For each company in the list:
   - If not in the supported list, warn the user and skip.
   - Otherwise run via Bash:
     ```
     python gen_mindmap.py <company>
     ```
5. After all runs, report which succeeded and which (if any) failed.

## Automation scripts (run outside Claude)

- PowerShell: `.\run_mindmaps.ps1 apple nvidia` or `.\run_mindmaps.ps1 all`
- Bash:        `bash run_mindmaps.sh apple nvidia` or `bash run_mindmaps.sh all`
