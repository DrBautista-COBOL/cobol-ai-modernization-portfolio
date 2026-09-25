# Prompts — copy, paste, and save the AI's full answer in this folder

Save each response as `ai-output-<prompt>-<tool>.md` (e.g. `ai-output-A-claude.md`).
The raw AI output is evidence — do not edit it. Your corrections go in `rules-register.csv`.

## Prompt 0 — Inventory (for Step 1)
> You are a mainframe application analyst. Below are a JCL job and the COBOL program it runs.
> List: (1) every job step and program, (2) every file with its DD name, dataset, organization,
> open mode and access mode, (3) every copybook, (4) every CALL. Answer in tables only.
> [paste INTCALC.jcl] [paste CBACT04C.cbl]

## Prompt A — Business-rule extraction (for Step 2)
> You are a business analyst documenting a legacy COBOL program for a modernization project.
> Extract every business rule from this program. For each rule give:
> rule ID, plain-English statement, the COBOL paragraph it comes from, and the line numbers.
> Include calculation rules, lookup/default rules, conditions, error-handling rules and
> anything the program writes. Do not describe file open/close mechanics as rules.
> [paste CBACT04C.cbl] [paste copybooks CVTRA01Y, CVACT03Y, CVTRA02Y, CVACT01Y, CVTRA05Y]

## Prompt B — Challenge (run after Prompt A, same conversation)
> For each rule you listed, quote the exact COBOL lines that implement it.
> If you cannot quote lines for a rule, say so explicitly.

## What to check yourself (don't tell the AI these in advance)
- Does it describe a fee calculation? Read paragraph `1400-COMPUTE-FEES` carefully.
- Does it explain what happens when an account's disclosure group is not found?
- Does it state the interest formula exactly, including the divisor, and why?
- When is the account master updated — per record, or on a control break? What gets updated?
- How is the new transaction ID built, and where does its date come from?
- What happens to rounding/truncation in the COMPUTE (no ROUNDED clause)?
