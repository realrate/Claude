---
description: Generate a RealRate mind map for a company. Usage: /mindmap <company>
argument-hint: <company>
allowed-tools: [Bash, Read]
---

# Mind Map Generator

Generate a 1920×1080 LinkedIn mind map image for a RealRate-ranked company.

## Arguments

The user invoked this command with: $ARGUMENTS

## Supported Companies

| Argument | Company |
|---|---|
| `trilinc` | TriLinc Global |
| `strata` | Strata Critical Medical |
| `hp` | HP Inc. |
| `angi` | Angi Inc. |
| `nvidia` | Nvidia Corp. |
| `tesla` | Tesla Inc. |
| `apple` | Apple Inc. |

## Instructions

1. Parse $ARGUMENTS to get the company name (lowercase, strip whitespace).
2. If no argument is given, tell the user to provide a company name and list the supported ones above.
3. For all companies, run:
   ```
   python gen_mindmap.py <company>
   ```
4. Run the command from the Mind Map claude directory using Bash.
5. Report the output path and any errors to the user.
6. If the company is not in the supported list, tell the user and suggest adding an `elif COMPANY == "<name>":` block to `gen_mindmap.py` per the CLAUDE.md standing rule.
