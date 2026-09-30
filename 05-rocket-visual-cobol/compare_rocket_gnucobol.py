"""Compare the CBACT04C job output of Rocket Visual COBOL with GnuCOBOL.

Usage:  python compare_rocket_gnucobol.py  > results/comparison-output.txt
Every difference is reported with its byte position and classified as
  TIMESTAMP  - positions 279-330 (TRAN-ORIG-TS, TRAN-PROC-TS: time of the run)
  FILLER     - GnuCOBOL has binary zeros (shown as '~'), Rocket has spaces
  OTHER      - anything else (would be a real difference)
"""
from pathlib import Path

HERE = Path(__file__).parent
ROCKET = HERE / "results"
GNU = HERE / "kit" / "expected"


def lines(path):
    text = path.read_text(encoding="latin-1").replace("\r", "")
    return [ln.ljust(350) for ln in text.split("\n") if ln.strip()]


def zoned(field):
    """Decode a signed zoned amount (EBCDIC-style sign in the last byte)."""
    pos, neg = "{ABCDEFGHI", "}JKLMNOPQR"
    last = field[-1]
    if last in pos:
        digit, sign = pos.index(last), 1
    elif last in neg:
        digit, sign = neg.index(last), -1
    else:
        digit, sign = int(last), 1
    return sign * int(field[:-1] + str(digit)) / 100


def main():
    ok = True
    a_r, a_g = lines(ROCKET / "rocket-acctdata-out.txt"), lines(GNU / "gnucobol-acctdata-out.txt")
    same = a_r == a_g
    ok &= same
    print(f"ACCOUNT FILE: {len(a_r)} records Rocket, {len(a_g)} GnuCOBOL -> "
          f"{'IDENTICAL' if same else 'DIFFERENT'}")

    t_r, t_g = lines(ROCKET / "rocket-systran.txt"), lines(GNU / "gnucobol-systran.txt")
    print(f"TRANSACTIONS: {len(t_r)} records Rocket, {len(t_g)} GnuCOBOL")
    for n, (r, g) in enumerate(zip(t_r, t_g), 1):
        kinds = {"TIMESTAMP": 0, "FILLER": 0, "OTHER": 0}
        for pos, (x, y) in enumerate(zip(r, g), 1):
            if x == y:
                continue
            if 279 <= pos <= 330:
                kinds["TIMESTAMP"] += 1
            elif y == "~" and x == " ":
                kinds["FILLER"] += 1
            else:
                kinds["OTHER"] += 1
        ok &= kinds["OTHER"] == 0
        amount = zoned(r[132:143])
        print(f"  tran {n}: id {r[0:16]}  acct {r[45:56]}  amount {amount:6.2f}  "
              f"diff bytes: timestamp={kinds['TIMESTAMP']} filler={kinds['FILLER']} "
              f"other={kinds['OTHER']}")
    print("RESULT:", "business fields identical" if ok else "REAL DIFFERENCES FOUND")


if __name__ == "__main__":
    main()
