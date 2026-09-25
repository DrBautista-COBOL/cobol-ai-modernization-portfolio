# Reconciliation Report — Account Master (VSAM KSDS → SQL)

**Source:** CardDemo `ACCTDATA` sample (ASCII copy), copybook `CVACT01Y`, 300-byte fixed records
**Target:** SQLite table `account` · **Loader:** `load_accounts.py` · **Mapping:** `mapping.csv`
**Reviewer:** Eduardo Bautista, PhD · **Date:** 2026-09-24

## Summary
All 50 account records migrated; counts and money totals reconcile. Testing beyond the sample found and fixed a defect in the loader that could silently shift the decimal point. One open data issue (group ID / ZIP) is escalated to the data owner because it changes which interest rate the batch program applies.

## 1. Field layout
Byte positions for all 12 migrated fields were checked against the PIC clauses of `CVACT01Y` and total 300 bytes (122 data + 178 FILLER). **Result: verified.**

## 2. Money-field decoding
Signed zoned-decimal fields (`PIC S9(10)V99`) carry the sign as an overpunch in the last byte (`{`=+0, `A`–`I`=+1…+9, `}`=−0, `J`–`R`=−1…−9) with an implied 2 decimals. Four sample accounts decoded by hand (e.g. `00000001940{` → +194.00). **Result: verified.**

## 3. Control totals — production sample

| Check | Source | Target | Result |
|---|---|---|---|
| Record count | 50 | 50 | Match |
| Distinct account IDs | 50 | 50 | Match |
| Sum of current balance | 12,269.00 | 12,269.00 | Match |
| Sum of credit limit | 233,711.00 | 233,711.00 | Match |
| Sum of cash credit limit | 122,148.00 | 122,148.00 | Match |
| Sum of cycle credit / debit | 0.00 / 0.00 | 0.00 / 0.00 | Match |
| Accounts with negative balance | 0 | 0 | Match |

**Accepted, with limitations:**
- Source totals were computed from the flat file, not supplied independently by the mainframe. On a live project they would be matched against a control report from the source system.
- The sample contains only active accounts, positive whole-dollar balances and zero cycle amounts, so it does not exercise negatives, cents, inactive accounts or cycle amounts. (Addressed by the edge-case test in section 5.)

## 4. Data-quality finding — escalated (OPEN)

| | |
|---|---|
| **Observation** | In all 50 records, ACCT-ADDR-ZIP (pos. 103–112) contains `A000000000` and ACCT-GROUP-ID (pos. 113–122) is blank. `A000000000` is one of only three group IDs in the disclosure-group (interest-rate) file (`A000000000`, `DEFAULT`, `ZEROAPR`). |
| **Second observation** | The EBCDIC and ASCII versions of the same sample disagree on account 49: `ZEROAPR` vs `A000000000`. |
| **Impact** | Interest program CBACT04C reads the group ID from pos. 113–122. Blank → rate not found → falls back to `DEFAULT` (see Step 2, C4). Account 49, intended for zero APR, would be charged the DEFAULT 15%. In this sample the dollar impact is zero (account 49 balance is 0.00; A000000000 and DEFAULT rates are equal for the type/category present), but on real data special-rate accounts would be mis-charged. |
| **Reviewer decision** | Cannot determine from the data alone whether this is a layout shift or wrong content — **escalate to the data owner** with the evidence above. |
| **Recommended controls** | (1) Validation rule: every ACCT-GROUP-ID must exist in DISCGRP. (2) Format rule for ZIP. (3) Confirm which sample version (EBCDIC or ASCII) is authoritative. |

## 5. Edge-case testing and loader defect

**Defect found:** the first version of the loader trimmed spaces before decoding, so a money field with a blank sign byte (`00000001940 `) was read as **19.40 instead of being rejected** — a silent 10× error that control totals alone would not reveal.

**Fix (reviewer decision: skip and log, not stop):** every field is validated against its PIC clause and record length is checked. A failing record is skipped and written to `rejects.log` with line, account and reason; the run proves loaded + rejected = input.

**Test file** `sample-data/acctdata-TEST-edge-cases.txt` (50 records):

| Case | Account | Result |
|---|---|---|
| Negative with cents `00000001234N` | 2 | Loaded as −123.45 ✔ |
| One cent negative `00000000000J` | 3 | Loaded as −0.01 ✔ |
| Blank sign byte `00000001940 ` | 4 | Rejected: invalid sign byte ✔ |
| Letter in amount `0000000194X{` | 5 | Rejected: non-digit ✔ |
| Blank amount | 6 | Rejected: non-digit ✔ |
| Short record (250 bytes) | 7 | Rejected: record length ✔ |

Record accounting: 50 input = 46 loaded + 4 rejected. Totals on loaded records reconcile (46/46; 2 negative balances on both sides). Re-run on the real sample: 50 loaded, 0 rejected, totals unchanged.

**Operational note:** because bad records are skipped, the target will be missing those accounts until the reject log is worked. Rejects must be resolved and re-loaded before go-live.

## 6. Conclusion
The account master migrates completely and accurately for the data provided. Two items stand between this and production: resolution of the group-ID/ZIP issue by the data owner, and independent source control totals from the mainframe.
