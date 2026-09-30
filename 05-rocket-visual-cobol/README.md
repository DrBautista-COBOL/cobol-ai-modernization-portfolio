# Step 5: CBACT04C on an Enterprise COBOL Toolchain (Rocket Visual COBOL)

**Reviewer:** Eduardo Bautista, PhD · **Date:** 2026-09-30
**Question:** does the original CardDemo interest program give the same results on a commercial, mainframe-compatible COBOL toolchain as it did under GnuCOBOL in Step 4? Can the Step 4 findings be shown line by line in a debugger?

## Summary
I ran the original `CBACT04C`, **unchanged**, in **Rocket Visual COBOL Personal Edition 11.0 for Eclipse** (the product line formerly sold by Micro Focus), compiled with the **Enterprise COBOL for z/OS dialect**. The whole INTCALC job was reproduced: load the files, run the program with its PARM, then unload the results.

- **All business results are identical to GnuCOBOL:** 50 of 50 account records match byte for byte, and all 9 interest transactions have the same IDs, accounts, codes and amounts.
- **The only differences** are the run timestamps and the uninitialized filler bytes (binary zeros under GnuCOBOL, spaces under Rocket). This confirms finding **D4** from Step 4: that content depends on the compiler/runtime, not on the program.
- **The Rocket debugger confirmed the Step 4 findings on the running program.** It showed interest truncated, not rounded (**D2**). It showed account 1's balance going from 194.00 to 200.46. It also showed that the end-of-file branch at lines 219–220 is **never executed**, so the last account's interest is never posted (**D3**).

## Why a second compiler
Step 4 relied on GnuCOBOL, a free compiler. Enterprise projects use commercial toolchains that emulate z/OS. Running the same program and data on one of them shows whether the results are a property of the **program** or of the **compiler**. It also exercises the skills a rehosting or testing project needs: dialect settings, mapping JCL DD statements, building, and debugging.

## How the job was reproduced

| z/OS (INTCALC JCL) | Rocket Visual COBOL (this project) |
|---|---|
| `EXEC PGM=CBACT04C,PARM='2022071800'` | `kit/src/RUNJOB.cbl` calls the steps in order and passes the PARM in the z/OS layout (length + value) |
| IDCAMS REPRO into VSAM KSDS + alternate index | `LOADVSAM.cbl` builds indexed files from the text data |
| DD statements | Run Configuration → Environment tab: 11 variables such as `dd_ACCTFILE=ACCTFILE.dat` |
| Enterprise COBOL compiler | Directives `DIALECT"ENTCOBOL"`, `SIGN"EBCDIC"`, `ASSIGN"EXTERNAL"` |
| `CEE3ABD` abend service | `CEE3ABD.cbl` stub (displays the code and ends with return code 16) |
| Browsing the output datasets | `UNLDACCT.cbl` and `UNLDTRAN.cbl` write readable files |

The test data is the same as in Step 4. `kit/data/tcatin-PURPOSE.txt` explains every record. The full setup is in `kit/README.txt`.

## Results

| Check | Result |
|---|---|
| Records loaded (TCATBAL / XREF / ACCOUNT / DISCGRP) | 11 / 50 / 50 / 51 (same as GnuCOBOL) |
| Account file after the run | **Identical**, 50 of 50 records |
| Interest transactions | 9 in each run. Amounts 1.25, 5.21, 12.50, 2.08, −1.00, 1.25, 2.08, 1.25, 2.50, the same in both |
| Timestamps | Differ (they record when each job ran) |
| Filler after the description, and the last 20 bytes | GnuCOBOL: binary zeros · Rocket: spaces (**D4**) |

Comparison script: `compare_rocket_gnucobol.py`. Output: `results/comparison-output.txt`. It classifies each differing byte as TIMESTAMP, FILLER or OTHER; **OTHER = 0 for every record**.

## Debugger evidence
Breakpoints were set at line 467 (interest added to the running total), line 352 (total posted to the account) and line 220 (the end-of-file posting).

| Screenshot | What it shows |
|---|---|
| `screenshots/01-line352-ws-total-int-6.46.png` | Account 1's total interest = **6.46** (1.25 + 5.21), just before posting. 100.44 × 15% ÷ 12 = 1.2555 was stored as **1.25**: truncated, not rounded (**D2**) |
| `screenshots/02-line352-acct-curr-bal-before-194.00.png` | Account 1's balance **before** the ADD: 194.00 |
| `screenshots/03-line353-acct-curr-bal-after-200.46.png` | Balance **after** the ADD: **200.46**, matching the output file |
| `screenshots/04-breakpoints-220-352-467.png` | All three breakpoints active. Stepping through the whole run with Resume, the program stopped only at 467 and 352. **Line 220 was never reached** (**D3**) |

The dead branch was first proven by running the program in Step 4 and comparing results. Here it is shown directly: an active breakpoint on the only code that would post the last account is never hit. Account 50's interest transaction (2.50) is written, but its balance stays at **492.00**.

## Findings

| # | Finding | Meaning for a migration |
|---|---|---|
| RV1 | Business results are identical across two independent compilers | The Step 4 baseline is a reliable reference for testing any translation |
| RV2 | Uninitialized bytes differ between runtimes (D4 confirmed) | Equivalence tests must mask fields the program never sets, or the business must define their content |
| RV3 | Dead end-of-file branch confirmed in the debugger (D3) | The legacy defect is real and repeatable. Reproducing or fixing it is a business decision |
| RV4 | Interest truncation observed at the variable level (D2) | Any target language must truncate the same way to match the books |
| RV5 | With the Enterprise COBOL dialect, file ASSIGN names are resolved at run time. Until `ASSIGN"EXTERNAL"` was set, every OPEN failed with "Illegal file name ''" (error 9/004) | Rehosting needs the DD-to-file mapping planned explicitly, as a replacement for the JCL |

## How this step was done

| Work | Done by |
|---|---|
| Installing and licensing Visual COBOL; creating the workspace and project; setting dialect, directives, entry point and the 11 DD variables | Eduardo Bautista |
| Diagnosing the build hang (Eclipse indexing blocking the build) and the 9/004 file-name error | Eduardo Bautista, with Claude (AI assistant) |
| Driver and helper programs (`RUNJOB`, `LOADVSAM`, `UNLDACCT`, `UNLDTRAN`, `CEE3ABD` stub), setup notes, comparison script | Claude (AI assistant) |
| Building and running the job, comparing outputs (Windows `fc`), debugging session and screenshots | Eduardo Bautista |
| Interpretation of results and final approval | Eduardo Bautista |

`CBACT04C.cbl` and its five copybooks are the original CardDemo sources, unmodified.

## Reproducing the test
1. Install Rocket Visual COBOL for Eclipse (a Personal Edition license is enough).
2. Create a COBOL project and import `kit/src/`. Set the dialect to Enterprise COBOL, add the directives `SIGN"EBCDIC"` and `ASSIGN"EXTERNAL"`, and set the entry point to `RUNJOB`.
3. Copy `kit/data/` to a run folder. In the Run Configuration, set that folder as the working directory and add the 11 `dd_` variables listed in `kit/README.txt`.
4. Build, then run. Compare `acctdata-out.txt` and `systran.txt` with `kit/expected/`, or copy them into `results/` and run `compare_rocket_gnucobol.py`.
