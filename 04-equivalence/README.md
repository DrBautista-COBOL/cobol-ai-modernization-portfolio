# Equivalence Test — CBACT04C (COBOL) vs. Copilot's Python translation

**Reviewer:** Eduardo Bautista, PhD · **Date:** 2026-09-25
**Question:** does the AI-generated Python program produce the same results as the original COBOL on the same data?

## Summary
Copilot's translation **crashed on the first record**. After a one-line, documented fix it ran, and matched the original on most fields — but **3 interest amounts and 3 account balances differ by one cent**, and it **silently changes the behavior of the last account** because the original COBOL contains a latent defect that Copilot did not reproduce. The test also disproved a claim made during the Step 2 code review.

## How the test was run

| | Original COBOL | Copilot's Python |
|---|---|---|
| Program | `CBACT04C.cbl` from CardDemo, **compiled unchanged** (GnuCOBOL 3.2, `-std=ibm -fsign=EBCDIC`) | `cbact04c_copilot.py`, as delivered |
| Files | Indexed files built from the sample data (stand-ins for the VSAM KSDS + alternate index) | Same data as fixed-width text |
| PARM | `2022071800`, passed by a small driver (`harness/RUNINT.cbl`) in place of the JCL EXEC card | Same, on the command line |
| z/OS services | `CEE3ABD` abend replaced by a stub (`harness/CEE3ABD.cbl`) | — |

- **Prompt:** `copilot-prompt.txt` (program and all five copybooks were supplied in full; the prompt did not mention any known issue).
- **Test data:** the CardDemo balance file contains only 0.00 balances, which would make any comparison meaningless. A small test file was built instead — `test-data/tcatbal-TEST.txt`, with the purpose of every record in `tcatbal-TEST-purpose.txt` — covering: cents that truncate differently than they round, a negative (credit) balance, three categories on one account, two zero-rate categories, and the last account in the file. Account, cross-reference and rate files are the unmodified CardDemo samples.
- **Comparison:** `harness/compare.py`, field by field; timestamps excluded (they record run time). Full output in `results/comparison-output.txt`.

## What matched
Transaction count (9 each), transaction IDs, type/category codes, card numbers, zero-rate categories skipped (no transaction), the three-category account (4.58 in both), and all other account fields.

## Differences and reviewer verdicts

| # | Difference | Evidence | Verdict |
|---|---|---|---|
| D1 | **Python crashed on record 1.** COBOL `MOVE 'DEFAULT'` to a PIC X(10) field pads with spaces; Copilot looked up `'DEFAULT'` unpadded, found nothing, and abended. | `results/` run log; fix is one line in `cbact04c_copilot_fix1.py` (marked `FIX 1`). Copilot's original is kept unedited. | **Copilot conversion bug** |
| D2 | **Interest off by one cent on 3 of 9 transactions**, and on those 3 account balances. COBOL truncates (no `ROUNDED`); Python rounds. Predicted in Step 2 (C5), now proven. | Acct 1: 1.25 vs 1.26 · Acct 4: 2.08 vs 2.09 · Acct 5: −1.00 vs −1.01 | **Copilot conversion bug** |
| D3 | **Last account's balance.** COBOL writes account 50's interest transaction (2.50) but never adds it to the balance — its end-of-file branch (lines 219–220) is dead code. Python updates the balance. | Acct 50: original 492.00 · COBOL 492.00 · Python 494.50 | **Business decision** (root cause: latent defect in the original COBOL — books out of balance by the interest on the last account) |
| D4 | **Transaction description filler.** The program never clears the transaction record, so bytes after the text contain whatever was in memory (binary zeros in this run); Python writes spaces. On z/OS the result depends on compiler/runtime settings. | All 9 transactions | **Business decision** (define the required content) |

## Correction to the Step 2 review
During the code review (Step 2, item M2), lines 219–220 were read — with the AI assistant — as updating the last account at end of file. Running the original program proved that branch is never reached: `PERFORM UNTIL END-OF-FILE = 'Y'` tests before each pass, so the loop exits as soon as end of file is set. The Step 2 record has been corrected. **Reading code is not proof; execution is.**

## Other observation (not triggered by this data)
Copilot's `decode_zoned` trims spaces and treats a missing sign as unsigned — the same flaw found and fixed in the Step 3 loader (a blank sign byte turns 194.00 into 19.40). Its handling of a blank field is to return 0 rather than reject it.

## Conclusion
The AI produced a plausible, well-structured program that **would have failed in production on its first record**, and after that fix would still post **wrong interest amounts** and **diverge from the legacy system's behavior** in ways only a side-by-side run exposed. Two of the four differences cannot be settled by programmers at all: they need a business owner to decide whether the new system should reproduce the old behavior or correct it.

## Reproducing the test
Requires GnuCOBOL 3.2 and Python 3. `harness/run_cobol.sh` compiles nothing — build first with
`cobc -x -std=ibm -fsign=EBCDIC RUNINT.cbl CBACT04C.cbl CEE3ABD.cbl -o runint` and
`cobc -x -fformat=variable LOADVSAM.cbl` / `UNLDACCT.cbl`, then run `run_cobol.sh`, `run_python.sh tcatbal-TEST cbact04c_copilot_fix1`, and `compare.py`.
