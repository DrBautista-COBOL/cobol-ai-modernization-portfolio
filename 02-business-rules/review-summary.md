# AI Review Summary — Copilot analysis of CBACT04C (interest calculation)

**AI tool:** GitHub Copilot Chat · **Reviewer:** Eduardo Bautista, PhD · **Date:** 2026-09-24
**Method:** each Copilot claim checked line-by-line against the COBOL source; full detail in `copilot-review.csv`.

## Scorecard

| Result | Count |
|---|---|
| Claims correct | 4 of 10 |
| Claims partly correct (true but incomplete or over-stated) | 5 of 10 |
| Claims wrong | 1 of 10 |
| Important items the AI missed entirely | 5 |

## Findings that would have caused defects in a conversion

1. **Fees invented (C6 — wrong).** Copilot said the program computes fees. Paragraph `1400-COMPUTE-FEES` is an empty stub (`* To be implemented`). The AI described the paragraph from its name, not its code.
2. **Rounding (C5 / M5).** The interest COMPUTE has no `ROUNDED`, so COBOL truncates (4.99717 → 4.99). A Python/Java rewrite that rounds would differ by a cent on some accounts.
3. **Transaction-ID uniqueness (C8).** IDs = hard-coded JCL PARM date + a counter that restarts at 0 each run. Unique only within one run; a rerun produces duplicate IDs. Copilot claimed they were unique.
4. **Last account at end of file (M2) — corrected after testing.** The end-of-file branch (lines 219–220) is dead code: the loop exits before reaching it, so the last account's interest is written as a transaction but never added to its balance. This was first misread during review and caught only when the original program was run in Step 4. Copilot did not mention end-of-file handling.
5. **Zero-rate condition (M1).** Interest and its transaction are produced only when the rate is non-zero (line 214).
6. **Whole-batch abend (C10).** One missing ACCOUNT or XREF record stops the entire job (abend 999) instead of skipping that account.
7. **Unstated input assumption (C2).** The control break assumes TCATBAL is sorted by account; this is not validated anywhere.

## Prompt compliance
Copilot did not return the requested files table with open modes (M3) or numbered rules with line numbers (M4). Without line references, every claim required manual tracing by an SME.

## Conclusion
The AI produced a useful first-pass overview quickly, but 6 of 10 claims needed correction or qualification, and the most consequential defects (invented fee logic, rounding, duplicate IDs, last-record handling) were only found by checking the source. AI accelerates discovery; it does not replace verification.
