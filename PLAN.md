# Project Plan — status as of 2026-09-24

**Done:** Steps 0–4 · **Next:** Step 5 (publish)

Tick items off as you go. Each step produces one file in this repository.

## Step 0 — Set up (1 session)
- [ ] Create a free GitHub account (do in Step 5) (use a professional username, e.g. `ebautista-modernization`)
- [x] CardDemo files provided directly (INTCALC, CBACT04C, 5 copybooks)
- [x] Locate these files inside the ZIP:
  - Program: `app/cbl/CBACT04C.cbl` (interest calculation)
  - JCL: `app/jcl/INTCALC.jcl`
  - Copybooks (in `app/cpy/`): `CVTRA01Y`, `CVACT03Y`, `CVTRA02Y`, `CVACT01Y`, `CVTRA05Y`
  - Sample data: `app/data/ASCII/` (the Account file is already copied into `03-data-migration/sample-data/`)
- [x] GnuCOBOL 3.2 set up on the project side (Step 4)

## Step 1 — Discovery (1–2 sessions) → `01-discovery/inventory.md`
- [x] Read INTCALC JCL: list every DD statement and the dataset behind it
- [x] Read CBACT04C: list every file (SELECT/FD), copybook, and CALL
- [x] Ask the AI for the same inventory (Prompt 0 in `02-business-rules/prompts.md`); note any differences
- [x] Draw the data flow: input files → CBACT04C → output files

## Step 2 — Business rules (2–4 sessions) → `02-business-rules/copilot-review.csv` + `review-summary.md`  ★ highest value
- [x] Run Prompt A on CBACT04C
- [x] Put every AI-claimed rule in the register
- [x] Verify each against the source; cite paragraph + line numbers
- [x] Mark each: Confirmed / Corrected / Missed by AI / Hallucinated
- [x] Summarize: how many rules, how many AI errors, which kind

## Step 3 — Data migration (2–3 sessions) → `03-data-migration/`  ★ highest value
- [x] Take the Account file (copybook CVACT01Y) as the migration source
- [x] Fill `mapping.csv`: every COBOL field → SQL column, type, transformation
- [x] Run `python load_accounts.py` (loader already written) and read through it until you can explain every line
- [x] Investigate the two data-quality findings pre-noted in the reconciliation report
- [x] Complete `reconciliation-report.md`: counts, control totals, edge cases

## Step 4 — Equivalence test (2–3 sessions) → `04-equivalence/`
- [x] Ask the AI to translate CBACT04C to Python
- [x] Run the original with GnuCOBOL and the Python version on the same input
- [x] Diff the outputs; explain every difference

## Step 5 — Publish (1 session)
- [ ] Fill in the README "At a glance" and "Key findings"
- [ ] Upload everything to a public GitHub repository
- [ ] Add the link to résumé, LinkedIn and freelancermap
