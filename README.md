# AI-Assisted COBOL Modernization — CardDemo Interest Calculation

**Eduardo Bautista, PhD** · Legacy Modernization & Data Migration Specialist · Miami, FL
Available for B2B / C2C contracts (US LLC)

---

## At a glance

| | |
|---|---|
| **Source system** | AWS CardDemo (open-source mainframe credit-card app; COBOL, JCL, VSAM) |
| **Scope** | Batch interest calculation — job `INTCALC`, program `CBACT04C` — plus Account master data migration |
| **AI tools used** | GitHub Copilot Chat (program analysis), Claude (project assistant, loader script) |
| **COBOL toolchains** | GnuCOBOL 3.2 · Rocket Visual COBOL 11.0 for Eclipse (Enterprise COBOL dialect, debugger) |
| **What I validated** | 10 AI claims reviewed: 4 correct, 5 partly correct, 1 wrong, plus 5 important omissions · 50 account records migrated and reconciled · 1 data-quality issue escalated · 1 loader defect found and fixed · COBOL vs. AI-Python run side by side: 4 differences, each classified · Same job on a second, enterprise compiler: business results identical; findings confirmed in the debugger |

## The problem

Organizations are using AI to read and translate COBOL, but AI output is only as trustworthy as the validation behind it.
This project shows a repeatable method: **let AI do the first pass, then prove or disprove every claim against the code and the data.**

## What's in this repository

| Folder | What it shows | Hiring relevance |
|---|---|---|
| `01-discovery/` | Program, file, copybook and JCL inventory; dependency map | Application discovery |
| `02-business-rules/` | AI-extracted rules vs. verified rules, with line-level evidence | Business-rule extraction, AI evaluation |
| `03-data-migration/` | VSAM → SQL source-to-target mapping and reconciliation report | Data migration & data quality |
| `04-equivalence/` | Same inputs through COBOL and the AI-generated translation; output diff | Modernization validation |
| `05-rocket-visual-cobol/` | Original program on Rocket Visual COBOL (Enterprise COBOL dialect); JCL reproduced; cross-compiler comparison; debugger evidence | Rehosting, testing, enterprise tooling |

## Key findings

1. **The AI invented business logic.** Copilot said the program computes fees; the fee paragraph is an empty stub (`* To be implemented`). It described the paragraph from its name, not its code.
2. **Conversion traps the AI missed:** interest is truncated, not rounded (no `ROUNDED`); transaction IDs repeat on a rerun.
3. **Data migration:** all 50 accounts reconcile, but every record has its group ID blank and a group value in the ZIP position — so the interest program silently uses the DEFAULT rate for everyone. Escalated with evidence.
4. **Edge-case testing found a defect in the migration tool itself** (a blank sign byte turned 194.00 into 19.40). Fixed with field-level validation and a reject log.
5. **Running both versions side by side** (original COBOL compiled unchanged vs. Copilot's Python, same data): the AI's program crashed on record 1 (lost COBOL space-padding); after a one-line fix, 3 of 9 interest amounts were off by a cent; and it silently "fixed" a latent defect in the original — the last account's interest is written but never posted to its balance. Execution also corrected a claim made during the code review.
6. **A second, enterprise toolchain agrees.** Compiled unchanged in Rocket Visual COBOL with the Enterprise COBOL dialect, the program gave byte-identical account results and identical interest amounts. The debugger showed the truncation (1.2555 stored as 1.25), the posting (194.00 → 200.46), and an active breakpoint on the last-account posting that is never hit. Only uninitialized filler bytes differ between compilers, a detail an equivalence test must allow for.

## How this project was done

This project deliberately combines AI tools with human review. The division of work:

| Work | Done by |
|---|---|
| First-pass analysis of CBACT04C | GitHub Copilot Chat (saved unedited in `02-business-rules/copilot-answer-1.txt`) |
| Python translation of CBACT04C | GitHub Copilot Chat (saved unedited in `04-equivalence/cbact04c_copilot.py`) |
| Reading the JCL and COBOL; file inventory (tables 1–2) | Eduardo Bautista |
| Splitting the AI answer into checkable claims; pulling the matching code; drafting reports; writing the loader script; building the COBOL test harness, test data and comparison script | Claude (AI assistant) |
| Every verdict on the AI's claims, and every migration decision (accept totals, escalate the data issue, skip-and-log rejects) | Eduardo Bautista |
| Rocket Visual COBOL setup, build, runs, output comparison and debugging session | Eduardo Bautista (driver and helper programs written by Claude) |
| Final approval of all reports | Eduardo Bautista |

Verdicts were discussed with the AI assistant where the evidence was debatable (for example, "wrong" versus "partly correct"), in the same way a second reviewer would challenge a first — the final call was always the reviewer's.

## Method

AI first pass → SME review against source (paragraph + line cited) → test with real data → document the gap.

## About me

40+ years in enterprise IT — COBOL, JCL, VSAM, CA-IDMS, relational migrations — including 35 years as Senior Systems Analyst/Programmer at Miami-Dade County, and 19 years teaching databases and systems analysis. PhD in Information Systems.

## Credits and license

Source application, code excerpts and sample data: [AWS CardDemo](https://github.com/aws-samples/aws-mainframe-modernization-carddemo), © Amazon.com, Inc. or its affiliates, used under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) (see `CARDDEMO-LICENSE.txt` and `CARDDEMO-NOTICE.txt`). The CardDemo sample data in `03-data-migration/sample-data/` is unmodified except for the clearly named test file `acctdata-TEST-edge-cases.txt`. Analysis, reviews and reports in this repository are the author's own work.
