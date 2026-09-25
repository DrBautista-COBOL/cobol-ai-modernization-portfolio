"""
Load the CardDemo Account file (copybook CVACT01Y, 300-byte fixed records)
into SQLite and print reconciliation control totals.

Usage:   python load_accounts.py [input-file]
Output:  accounts.db (SQLite), rejects.log (skipped records + reason),
         control totals printed to the screen

The source file is the ASCII version of the VSAM data. Signed numeric
fields (PIC S9(10)V99) are zoned decimal with the sign "overpunched" into
the last byte, e.g. '{' = +0, 'A' = +1 ... '}' = -0, 'J' = -1 ...
"""
import sqlite3
from decimal import Decimal
from pathlib import Path

import sys
SOURCE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "sample-data" / "acctdata.txt"
TARGET = Path(__file__).parent / "accounts.db"
REJECTS = Path(__file__).parent / "rejects.log"

# Overpunch: last character carries both the last digit and the sign
POSITIVE = {"{": 0, "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8, "I": 9}
NEGATIVE = {"}": 0, "J": 1, "K": 2, "L": 3, "M": 4, "N": 5, "O": 6, "P": 7, "Q": 8, "R": 9}


class BadField(ValueError):
    """Raised when a field does not match its COBOL PIC clause."""


def zoned_signed(raw: str, decimals: int = 2) -> Decimal:
    """Decode a signed zoned-decimal field (PIC S9(n)V99) with an implied decimal point.

    Strict: no trimming. Every byte but the last must be a digit, and the last
    byte must be a valid overpunch sign character. Anything else is rejected,
    because silently accepting it can shift the decimal point (e.g. 194.00 -> 19.40).
    """
    body, last = raw[:-1], raw[-1:]
    if not body.isdigit():
        raise BadField(f"non-digit in {raw!r}")
    if last in POSITIVE:
        digits, sign = body + str(POSITIVE[last]), 1
    elif last in NEGATIVE:
        digits, sign = body + str(NEGATIVE[last]), -1
    else:
        raise BadField(f"invalid sign byte {last!r} in {raw!r}")
    return sign * Decimal(int(digits)).scaleb(-decimals)


# (column, start, length, type) — positions are 1-based, as in mapping.csv
LAYOUT = [
    ("acct_id",               1, 11, "int"),
    ("active_status",        12,  1, "str"),
    ("curr_bal",             13, 12, "money"),
    ("credit_limit",         25, 12, "money"),
    ("cash_credit_limit",    37, 12, "money"),
    ("open_date",            49, 10, "str"),
    ("expiration_date",      59, 10, "str"),
    ("reissue_date",         69, 10, "str"),
    ("curr_cyc_credit",      79, 12, "money"),
    ("curr_cyc_debit",       91, 12, "money"),
    ("addr_zip",            103, 10, "str"),
    ("group_id",            113, 10, "str"),
]


RECORD_LENGTH = 300


def parse(line: str) -> dict:
    if len(line) != RECORD_LENGTH:
        raise BadField(f"record length {len(line)}, expected {RECORD_LENGTH}")
    rec = {}
    for name, start, length, kind in LAYOUT:
        raw = line[start - 1 : start - 1 + length]
        try:
            if kind == "int":
                if not raw.isdigit():
                    raise BadField(f"non-digit in {raw!r}")
                rec[name] = int(raw)
            elif kind == "money":
                rec[name] = zoned_signed(raw)
            else:
                rec[name] = raw.strip()
        except BadField as e:
            raise BadField(f"field {name} (positions {start}-{start + length - 1}): {e}")
    return rec


def main():
    lines = [l for l in SOURCE.read_text().splitlines() if l.strip()]
    records, rejects = [], []
    for n, line in enumerate(lines, start=1):
        try:
            records.append(parse(line))
        except BadField as e:
            rejects.append((n, line[:11], str(e)))

    # Reject log: one line per skipped record, with the reason
    with open(REJECTS, "w") as f:
        f.write("input_line\tacct_id_raw\treason\n")
        for n, acct, reason in rejects:
            f.write(f"{n}\t{acct}\t{reason}\n")

    TARGET.unlink(missing_ok=True)
    con = sqlite3.connect(TARGET)
    con.execute("""
        CREATE TABLE account (
            acct_id            INTEGER PRIMARY KEY,
            active_status      TEXT,
            curr_bal           NUMERIC(12,2),
            credit_limit       NUMERIC(12,2),
            cash_credit_limit  NUMERIC(12,2),
            open_date          TEXT,
            expiration_date    TEXT,
            reissue_date       TEXT,
            curr_cyc_credit    NUMERIC(12,2),
            curr_cyc_debit     NUMERIC(12,2),
            addr_zip           TEXT,
            group_id           TEXT
        )""")
    cols = [c[0] for c in LAYOUT]
    con.executemany(
        f"INSERT INTO account ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})",
        [tuple(str(r[c]) if isinstance(r[c], Decimal) else r[c] for c in cols) for r in records],
    )
    con.commit()

    # ---- Record accounting: every input record is either loaded or rejected ----
    print(f"Input records:    {len(lines)}")
    print(f"Loaded:           {len(records)}")
    print(f"Rejected:         {len(rejects)}  (see {REJECTS.name})")
    print(f"Loaded + rejected = input: {'YES' if len(records) + len(rejects) == len(lines) else 'NO - RECORDS LOST'}")
    print()

    # ---- Reconciliation: source side (computed from the accepted records) ----
    src_count = len(records)
    src_bal = sum(r["curr_bal"] for r in records)
    src_limit = sum(r["credit_limit"] for r in records)
    src_neg = sum(1 for r in records if r["curr_bal"] < 0)

    # ---- Reconciliation: target side (queried back from SQL) ----
    tgt_count, tgt_bal, tgt_limit, tgt_neg = con.execute("""
        SELECT COUNT(*), ROUND(SUM(curr_bal),2), ROUND(SUM(credit_limit),2),
               SUM(CASE WHEN curr_bal < 0 THEN 1 ELSE 0 END)
        FROM account""").fetchone()

    print(f"{'Check':<28}{'Source':>18}{'Target':>18}  Result")
    for label, s, t in [
        ("Record count", src_count, tgt_count),
        ("Sum of current balance", src_bal, Decimal(str(tgt_bal)).quantize(Decimal("0.01"))),
        ("Sum of credit limit", src_limit, Decimal(str(tgt_limit)).quantize(Decimal("0.01"))),
        ("Accounts w/ negative bal.", src_neg, tgt_neg),
    ]:
        print(f"{label:<28}{str(s):>18}{str(t):>18}  {'MATCH' if s == t else 'DIFF'}")
    con.close()


if __name__ == "__main__":
    main()
