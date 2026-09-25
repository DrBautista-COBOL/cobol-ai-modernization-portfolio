# Application Discovery — Job INTCALC / Program CBACT04C

Source files (CardDemo): `app/jcl/INTCALC.jcl` · `app/cbl/CBACT04C.cbl` · copybooks in `app/cpy/`
Reviewer: Eduardo Bautista, PhD · 2026-09-24

## 1. Job steps (from INTCALC JCL)

| Step | Program | PARM | Purpose |
|---|---|---|---|
| STEP15 | CBACT04C | 2022071800 | Compute interest and fees |

## 2. Files used — JCL DD matched to the program's SELECT … ASSIGN

| DD name | Dataset (DSN) | Organization | Copybook | Open mode | Access | Role |
|---|---|---|---|---|---|---|
| TCATBALF | AWS.M2.CARDDEMO.TCATBALF.VSAM.KSDS | KSDS | CVTRA01Y (file TCATBAL-FILE) | INPUT | sequential | driver: one record per account + transaction category balance |
| XREFFILE | AWS.M2.CARDDEMO.CARDXREF.VSAM.KSDS | KSDS | CVACT03Y (file XREF-FILE) | INPUT | random | lookup (base cluster; primary key card number not used by this program) |
| XREFFIL1 | AWS.M2.CARDDEMO.CARDXREF.VSAM.AIX.PATH | AIX path | CVACT03Y (via XREF-FILE; no SELECT of its own) | INPUT (opened with XREF-FILE) | random, by alternate key ACCT-ID | lookup: account → card number |
| ACCTFILE | AWS.M2.CARDDEMO.ACCTDATA.VSAM.KSDS | KSDS | CVACT01Y (file ACCOUNT-FILE) | I-O | random | update: read account, add interest to balance, rewrite |
| DISCGRP | AWS.M2.CARDDEMO.DISCGRP.VSAM.KSDS | KSDS | CVTRA02Y (file DISCGRP-FILE) | INPUT | random | lookup: interest rate by group + type + category (falls back to DEFAULT group) |
| TRANSACT | AWS.M2.CARDDEMO.SYSTRAN(+1) | GDG (new generation, sequential) | CVTRA05Y (file TRANSACT-FILE) | OUTPUT | sequential | output: one interest transaction per category balance |

## 3. Copybooks

| Copybook | Record | Key field(s) | Record length | Special formats |
|---|---|---|---|---|
| CVTRA01Y | TRAN-CAT-BAL-RECORD | TRAN-CAT-KEY = account 9(11) + type X(2) + category 9(4) | 50 | Signed zoned decimal S9(09)V99 |
| CVACT03Y | CARD-XREF-RECORD | Card number X(16); alternate key account ID 9(11) | 50 | none |
| CVTRA02Y | DIS-GROUP-RECORD | DIS-GROUP-KEY = group X(10) + type X(2) + category 9(4) | 50 | Rate S9(04)V99 (annual %) |
| CVACT01Y | ACCOUNT-RECORD | ACCT-ID 9(11) | 300 | Signed zoned decimal S9(10)V99; field name misspelled `ACCT-EXPIRAION-DATE` |
| CVTRA05Y | TRAN-RECORD | TRAN-ID X(16) | 350 | Signed zoned decimal amount |

No COMP-3, REDEFINES or OCCURS in these copybooks. (Sections 3–4 compiled from the copybooks; see Step 2 for line-level verification of how they are used.)

## 4. External calls

| Module | Called from (paragraph) | Purpose |
|---|---|---|
| CEE3ABD | 9999-ABEND-PROGRAM (line 632) | Language Environment abend service; ends the job with user abend code 999 |

## 5. Processing flow

```
open 5 files
read TCATBAL sequentially until end of file
   ├─ account changed? (control break, line 194)
   │     ├─ not first account → rewrite previous account (1050)
   │     ├─ reset interest total
   │     └─ read ACCOUNT (1100) and XREF by alternate key (1110)
   ├─ build DISCGRP key (group + type + category) and read rate (1200; DEFAULT on not-found)
   └─ rate not zero? → compute interest (1300), write transaction, call fees stub (1400)
end of file → rewrite last account (line 220)
close files
```

## 6. Observations

- **XREFFIL1 has no SELECT in the program.** It is the alternate-index path for XREFFILE (z/OS convention: DD name + "1", truncated to 8 characters). The program reads XREF-FILE by alternate key FD-XREF-ACCT-ID (lines 204, 394–395) to find the card number for each account. The primary key (card number) is never used here. Migration impact: the target cross-reference table needs an index on account ID.
- **Copybooks sit in WORKING-STORAGE, not under the FDs.** Records are read `INTO` those structures; the FDs define only keys and raw record areas.
- **The control break assumes TCATBAL is sorted by account.** Nothing validates this.
- **The whole job abends on one missing ACCOUNT or XREF record** (abend 999) instead of skipping it.
- **AI comparison:** Copilot's analysis (Step 2) did not mention XREFFIL1, the alternate-index access, or the open modes of any file.
