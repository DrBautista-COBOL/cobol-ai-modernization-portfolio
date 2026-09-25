#!/usr/bin/env python3
import sys
from datetime import datetime
from decimal import Decimal, getcontext

# Set sufficient precision for money calculations
getcontext().prec = 18

# ----------------------------------------------------------------------
# Zoned decimal overpunch encode/decode
# ----------------------------------------------------------------------

POSITIVE_OVERPUNCH = {
    '0': '{',
    '1': 'A',
    '2': 'B',
    '3': 'C',
    '4': 'D',
    '5': 'E',
    '6': 'F',
    '7': 'G',
    '8': 'H',
    '9': 'I',
}

NEGATIVE_OVERPUNCH = {
    '0': '}',
    '1': 'J',
    '2': 'K',
    '3': 'L',
    '4': 'M',
    '5': 'N',
    '6': 'O',
    '7': 'P',
    '8': 'Q',
    '9': 'R',
}

OVERPUNCH_DECODE = {}
for d, c in POSITIVE_OVERPUNCH.items():
    OVERPUNCH_DECODE[c] = (1, d)
for d, c in NEGATIVE_OVERPUNCH.items():
    OVERPUNCH_DECODE[c] = (-1, d)


def decode_zoned(s: str, scale: int) -> Decimal:
    """
    Decode a zoned-decimal string (with overpunch in last character) into Decimal.
    s: full field string (no spaces trimmed).
    scale: number of decimal digits (V99 -> scale=2).
    """
    s = s.rstrip()
    if not s:
        return Decimal(0)

    last = s[-1]
    body = s[:-1]

    if last in OVERPUNCH_DECODE:
        sign, digit = OVERPUNCH_DECODE[last]
        digits = body + digit
    else:
        # No overpunch, treat as unsigned
        sign = 1
        digits = s

    if not digits.strip():
        return Decimal(0)

    int_val = int(digits)
    val = Decimal(int_val) / (Decimal(10) ** scale)
    return val * sign


def encode_zoned(value: Decimal, length: int, scale: int) -> str:
    """
    Encode a Decimal into zoned-decimal string with overpunch in last character.
    length: total field length.
    scale: number of decimal digits.
    """
    # Normalize to integer scaled value
    scaled = (value * (Decimal(10) ** scale)).quantize(Decimal('1'))
    sign = 1
    if scaled < 0:
        sign = -1
        scaled = -scaled

    digits = f"{int(scaled):d}"
    # Pad with leading zeros to length-1 (last char is overpunch)
    if len(digits) > length:
        raise ValueError(f"Value {value} too large for zoned field length {length}")
    if len(digits) < length:
        digits = digits.rjust(length, '0')

    # Apply overpunch to last digit
    last_digit = digits[-1]
    if sign >= 0:
        over = POSITIVE_OVERPUNCH[last_digit]
    else:
        over = NEGATIVE_OVERPUNCH[last_digit]
    encoded = digits[:-1] + over
    return encoded


# ----------------------------------------------------------------------
# Fixed-width record layouts
# ----------------------------------------------------------------------

# TRAN-CAT-BAL-RECORD (RECLN = 50)
#  10 TRANCAT-ACCT-ID       PIC 9(11).
#  10 TRANCAT-TYPE-CD       PIC X(02).
#  10 TRANCAT-CD            PIC 9(04).
#  05 TRAN-CAT-BAL          PIC S9(09)V99.
#  05 FILLER                PIC X(22).

def parse_tcatbal_line(line: str):
    if len(line) < 50:
        line = line.rstrip('\n')
        line = line.ljust(50)
    acct_id = line[0:11]
    tran_type_cd = line[11:13]
    tran_cat_cd = line[13:17]
    tran_cat_bal_str = line[17:28]  # 11 chars
    filler = line[28:50]
    tran_cat_bal = decode_zoned(tran_cat_bal_str, scale=2)
    return {
        "raw": line[:50],
        "TRANCAT_ACCT_ID": acct_id,
        "TRANCAT_TYPE_CD": tran_type_cd,
        "TRANCAT_CD": tran_cat_cd,
        "TRAN_CAT_BAL": tran_cat_bal,
        "FILLER": filler,
    }


# CARD-XREF-RECORD (RECLN = 50)
#  05 XREF-CARD-NUM         PIC X(16).
#  05 XREF-CUST-ID          PIC 9(09).
#  05 XREF-ACCT-ID          PIC 9(11).
#  05 FILLER                PIC X(14).

def parse_cardxref_line(line: str):
    if len(line) < 50:
        line = line.rstrip('\n')
        line = line.ljust(50)
    card_num = line[0:16]
    cust_id = line[16:25]
    acct_id = line[25:36]
    filler = line[36:50]
    return {
        "raw": line[:50],
        "XREF_CARD_NUM": card_num,
        "XREF_CUST_ID": cust_id,
        "XREF_ACCT_ID": acct_id,
        "FILLER": filler,
    }


def format_cardxref_record(rec):
    # Just return original raw; we don't modify xref in this program
    return rec["raw"]


# DIS-GROUP-RECORD (RECLN = 50)
#  10 DIS-ACCT-GROUP-ID     PIC X(10).
#  10 DIS-TRAN-TYPE-CD      PIC X(02).
#  10 DIS-TRAN-CAT-CD       PIC 9(04).
#  05 DIS-INT-RATE          PIC S9(04)V99.
#  05 FILLER                PIC X(28).

def parse_discgrp_line(line: str):
    if len(line) < 50:
        line = line.rstrip('\n')
        line = line.ljust(50)
    acct_group_id = line[0:10]
    tran_type_cd = line[10:12]
    tran_cat_cd = line[12:16]
    int_rate_str = line[16:22]  # 6 chars
    filler = line[22:50]
    int_rate = decode_zoned(int_rate_str, scale=2)
    return {
        "raw": line[:50],
        "DIS_ACCT_GROUP_ID": acct_group_id,
        "DIS_TRAN_TYPE_CD": tran_type_cd,
        "DIS_TRAN_CAT_CD": tran_cat_cd,
        "DIS_INT_RATE": int_rate,
        "FILLER": filler,
    }


def format_discgrp_record(rec):
    # Not modified in this program
    return rec["raw"]


# ACCOUNT-RECORD (RECLN = 300)
#  05 ACCT-ID                   PIC 9(11).
#  05 ACCT-ACTIVE-STATUS        PIC X(01).
#  05 ACCT-CURR-BAL             PIC S9(10)V99.
#  05 ACCT-CREDIT-LIMIT         PIC S9(10)V99.
#  05 ACCT-CASH-CREDIT-LIMIT    PIC S9(10)V99.
#  05 ACCT-OPEN-DATE            PIC X(10).
#  05 ACCT-EXPIRAION-DATE       PIC X(10).
#  05 ACCT-REISSUE-DATE         PIC X(10).
#  05 ACCT-CURR-CYC-CREDIT      PIC S9(10)V99.
#  05 ACCT-CURR-CYC-DEBIT       PIC S9(10)V99.
#  05 ACCT-ADDR-ZIP             PIC X(10).
#  05 ACCT-GROUP-ID             PIC X(10).
#  05 FILLER                    PIC X(178).

def parse_acct_line(line: str):
    if len(line) < 300:
        line = line.rstrip('\n')
        line = line.ljust(300)
    acct_id = line[0:11]
    active_status = line[11:12]
    curr_bal_str = line[12:24]          # 12 chars
    credit_limit_str = line[24:36]      # 12
    cash_credit_limit_str = line[36:48] # 12
    open_date = line[48:58]
    expiration_date = line[58:68]
    reissue_date = line[68:78]
    curr_cyc_credit_str = line[78:90]   # 12
    curr_cyc_debit_str = line[90:102]   # 12
    addr_zip = line[102:112]
    acct_group_id = line[112:122]
    filler = line[122:300]

    curr_bal = decode_zoned(curr_bal_str, scale=2)
    credit_limit = decode_zoned(credit_limit_str, scale=2)
    cash_credit_limit = decode_zoned(cash_credit_limit_str, scale=2)
    curr_cyc_credit = decode_zoned(curr_cyc_credit_str, scale=2)
    curr_cyc_debit = decode_zoned(curr_cyc_debit_str, scale=2)

    return {
        "raw": line[:300],
        "ACCT_ID": acct_id,
        "ACCT_ACTIVE_STATUS": active_status,
        "ACCT_CURR_BAL": curr_bal,
        "ACCT_CREDIT_LIMIT": credit_limit,
        "ACCT_CASH_CREDIT_LIMIT": cash_credit_limit,
        "ACCT_OPEN_DATE": open_date,
        "ACCT_EXPIRAION_DATE": expiration_date,
        "ACCT_REISSUE_DATE": reissue_date,
        "ACCT_CURR_CYC_CREDIT": curr_cyc_credit,
        "ACCT_CURR_CYC_DEBIT": curr_cyc_debit,
        "ACCT_ADDR_ZIP": addr_zip,
        "ACCT_GROUP_ID": acct_group_id,
        "FILLER": filler,
    }


def format_acct_record(rec):
    # Rebuild the 300-byte record from fields
    acct_id = rec["ACCT_ID"]
    active_status = rec["ACCT_ACTIVE_STATUS"]
    curr_bal_str = encode_zoned(rec["ACCT_CURR_BAL"], length=12, scale=2)
    credit_limit_str = encode_zoned(rec["ACCT_CREDIT_LIMIT"], length=12, scale=2)
    cash_credit_limit_str = encode_zoned(rec["ACCT_CASH_CREDIT_LIMIT"], length=12, scale=2)
    open_date = rec["ACCT_OPEN_DATE"]
    expiration_date = rec["ACCT_EXPIRAION_DATE"]
    reissue_date = rec["ACCT_REISSUE_DATE"]
    curr_cyc_credit_str = encode_zoned(rec["ACCT_CURR_CYC_CREDIT"], length=12, scale=2)
    curr_cyc_debit_str = encode_zoned(rec["ACCT_CURR_CYC_DEBIT"], length=12, scale=2)
    addr_zip = rec["ACCT_ADDR_ZIP"]
    acct_group_id = rec["ACCT_GROUP_ID"]
    filler = rec["FILLER"]

    parts = [
        acct_id,
        active_status,
        curr_bal_str,
        credit_limit_str,
        cash_credit_limit_str,
        open_date,
        expiration_date,
        reissue_date,
        curr_cyc_credit_str,
        curr_cyc_debit_str,
        addr_zip,
        acct_group_id,
        filler,
    ]
    record = "".join(parts)
    if len(record) != 300:
        record = record.ljust(300)
    return record


# TRAN-RECORD (RECLN = 350)
#  05 TRAN-ID                 PIC X(16).
#  05 TRAN-TYPE-CD            PIC X(02).
#  05 TRAN-CAT-CD             PIC 9(04).
#  05 TRAN-SOURCE             PIC X(10).
#  05 TRAN-DESC               PIC X(100).
#  05 TRAN-AMT                PIC S9(09)V99.
#  05 TRAN-MERCHANT-ID        PIC 9(09).
#  05 TRAN-MERCHANT-NAME      PIC X(50).
#  05 TRAN-MERCHANT-CITY      PIC X(50).
#  05 TRAN-MERCHANT-ZIP       PIC X(10).
#  05 TRAN-CARD-NUM           PIC X(16).
#  05 TRAN-ORIG-TS            PIC X(26).
#  05 TRAN-PROC-TS            PIC X(26).
#  05 FILLER                  PIC X(20).

def format_tran_record(rec):
    tran_id = rec["TRAN_ID"].ljust(16)[:16]
    tran_type_cd = rec["TRAN_TYPE_CD"].ljust(2)[:2]
    tran_cat_cd = rec["TRAN_CAT_CD"].rjust(4, '0')[:4]
    tran_source = rec["TRAN_SOURCE"].ljust(10)[:10]
    tran_desc = rec["TRAN_DESC"].ljust(100)[:100]
    tran_amt_str = encode_zoned(rec["TRAN_AMT"], length=11, scale=2)
    tran_merchant_id = rec["TRAN_MERCHANT_ID"].rjust(9, '0')[:9]
    tran_merchant_name = rec["TRAN_MERCHANT_NAME"].ljust(50)[:50]
    tran_merchant_city = rec["TRAN_MERCHANT_CITY"].ljust(50)[:50]
    tran_merchant_zip = rec["TRAN_MERCHANT_ZIP"].ljust(10)[:10]
    tran_card_num = rec["TRAN_CARD_NUM"].ljust(16)[:16]
    tran_orig_ts = rec["TRAN_ORIG_TS"].ljust(26)[:26]
    tran_proc_ts = rec["TRAN_PROC_TS"].ljust(26)[:26]
    filler = rec["FILLER"].ljust(20)[:20]

    parts = [
        tran_id,
        tran_type_cd,
        tran_cat_cd,
        tran_source,
        tran_desc,
        tran_amt_str,
        tran_merchant_id,
        tran_merchant_name,
        tran_merchant_city,
        tran_merchant_zip,
        tran_card_num,
        tran_orig_ts,
        tran_proc_ts,
        filler,
    ]
    record = "".join(parts)
    if len(record) != 350:
        record = record.ljust(350)
    return record


# ----------------------------------------------------------------------
# DB2-format timestamp (YYYY-MM-DD-HH.MM.SS.MIL0000)
# ----------------------------------------------------------------------

def get_db2_timestamp() -> str:
    now = datetime.now()
    yyyy = f"{now.year:04d}"
    mm = f"{now.month:02d}"
    dd = f"{now.day:02d}"
    hh = f"{now.hour:02d}"
    mi = f"{now.minute:02d}"
    ss = f"{now.second:02d}"
    mil = f"{int(now.microsecond / 10000):02d}"  # approximate hundredths
    rest = "0000"
    # COBOL code:
    # YYYY-MM-DD-HH.MM.SS.MIL0000
    return f"{yyyy}-{mm}-{dd}-{hh}.{mi}.{ss}.{mil}{rest}"


# ----------------------------------------------------------------------
# Main program logic (translation of CBACT04C)
# ----------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: cbact04c.py <PARM-DATE>")
        sys.exit(1)

    parm_date = sys.argv[1]  # COBOL PARM-DATE PIC X(10)

    print("START OF EXECUTION OF PROGRAM CBACT04C")

    # ------------------------------------------------------------------
    # Load indexed files into dictionaries (Option A)
    # ------------------------------------------------------------------

    # XREF-FILE: cardxref.txt
    xref_by_acct = {}
    try:
        with open("cardxref.txt", "r", encoding="ascii") as f:
            for line in f:
                line = line.rstrip("\n")
                rec = parse_cardxref_line(line)
                key = rec["XREF_ACCT_ID"]
                xref_by_acct[key] = rec
    except FileNotFoundError:
        print("ERROR OPENING CROSS REF FILE")
        sys.exit(1)

    # ACCOUNT-FILE: acctdata.txt
    acct_records = []  # preserve original order
    acct_by_id = {}
    try:
        with open("acctdata.txt", "r", encoding="ascii") as f:
            for line in f:
                line = line.rstrip("\n")
                rec = parse_acct_line(line)
                acct_records.append(rec)
                key = rec["ACCT_ID"]
                acct_by_id[key] = rec
    except FileNotFoundError:
        print("ERROR OPENING ACCOUNT MASTER FILE")
        sys.exit(1)

    # DISCGRP-FILE: discgrp.txt
    discgrp_by_key = {}
    try:
        with open("discgrp.txt", "r", encoding="ascii") as f:
            for line in f:
                line = line.rstrip("\n")
                rec = parse_discgrp_line(line)
                key = (
                    rec["DIS_ACCT_GROUP_ID"],
                    rec["DIS_TRAN_TYPE_CD"],
                    rec["DIS_TRAN_CAT_CD"],
                )
                discgrp_by_key[key] = rec
    except FileNotFoundError:
        print("ERROR OPENING DISCLOSURE GROUP FILE")
        sys.exit(1)

    # TRANSACT-FILE: systran.txt (output)
    try:
        tran_out = open("systran.txt", "w", encoding="ascii")
    except OSError:
        print("ERROR OPENING TRANSACTION FILE")
        sys.exit(1)

    # ------------------------------------------------------------------
    # Process TCATBAL-FILE: tcatbal.txt sequentially
    # ------------------------------------------------------------------

    ws_record_count = 0
    ws_tranid_suffix = 0
    ws_last_acct_num = " " * 11
    ws_monthly_int = Decimal(0)
    ws_total_int = Decimal(0)
    ws_first_time = "Y"

    def update_account():
        nonlocal ws_total_int
        nonlocal ws_last_acct_num

        if ws_last_acct_num.strip() == "":
            return

        acct_rec = acct_by_id.get(ws_last_acct_num)
        if acct_rec is None:
            print(f"ACCOUNT NOT FOUND (UPDATE): {ws_last_acct_num}")
            raise RuntimeError("ABEND: ACCOUNT NOT FOUND DURING UPDATE")

        # ADD WS-TOTAL-INT TO ACCT-CURR-BAL
        acct_rec["ACCT_CURR_BAL"] = acct_rec["ACCT_CURR_BAL"] + ws_total_int
        # MOVE 0 TO ACCT-CURR-CYC-CREDIT / DEBIT
        acct_rec["ACCT_CURR_CYC_CREDIT"] = Decimal(0)
        acct_rec["ACCT_CURR_CYC_DEBIT"] = Decimal(0)
        # REWRITE simulated by updating record; will be written to acctdata-out.txt
        # (No separate status handling; errors would occur on final write)

    def get_acct_data(acct_id: str):
        acct_rec = acct_by_id.get(acct_id)
        if acct_rec is None:
            print(f"ACCOUNT NOT FOUND: {acct_id}")
            raise RuntimeError("ABEND: ERROR READING ACCOUNT FILE")
        return acct_rec

    def get_xref_data(acct_id: str):
        xref_rec = xref_by_acct.get(acct_id)
        if xref_rec is None:
            print(f"ACCOUNT NOT FOUND: {acct_id}")
            raise RuntimeError("ABEND: ERROR READING XREF FILE")
        return xref_rec

    def get_interest_rate(acct_group_id: str, tran_type_cd: str, tran_cat_cd: str):
        key = (acct_group_id, tran_type_cd, tran_cat_cd)
        rec = discgrp_by_key.get(key)
        if rec is not None:
            return rec["DIS_INT_RATE"]

        # Simulate DISCGRP-STATUS = '23' (record missing) -> try DEFAULT group
        default_key = ("DEFAULT", tran_type_cd, tran_cat_cd)
        rec_default = discgrp_by_key.get(default_key)
        if rec_default is None:
            print("DISCLOSURE GROUP RECORD MISSING")
            print("TRY WITH DEFAULT GROUP CODE")
            print("ERROR READING DEFAULT DISCLOSURE GROUP")
            raise RuntimeError("ABEND: ERROR READING DISCLOSURE GROUP FILE")
        return rec_default["DIS_INT_RATE"]

    def write_transaction(acct_rec, xref_rec, monthly_int: Decimal):
        nonlocal ws_tranid_suffix

        ws_tranid_suffix += 1

        # TRAN-ID = PARM-DATE + WS-TRANID-SUFFIX (PIC 9(06))
        tran_id = f"{parm_date}{ws_tranid_suffix:06d}"

        tran_type_cd = "01"
        tran_cat_cd = "05"
        tran_source = "System"
        tran_desc = f"Int. for a/c {acct_rec['ACCT_ID']}"
        tran_amt = monthly_int
        tran_merchant_id = "0"
        tran_merchant_name = ""
        tran_merchant_city = ""
        tran_merchant_zip = ""
        tran_card_num = xref_rec["XREF_CARD_NUM"]
        db2_ts = get_db2_timestamp()

        tran_rec = {
            "TRAN_ID": tran_id,
            "TRAN_TYPE_CD": tran_type_cd,
            "TRAN_CAT_CD": tran_cat_cd,
            "TRAN_SOURCE": tran_source,
            "TRAN_DESC": tran_desc,
            "TRAN_AMT": tran_amt,
            "TRAN_MERCHANT_ID": tran_merchant_id,
            "TRAN_MERCHANT_NAME": tran_merchant_name,
            "TRAN_MERCHANT_CITY": tran_merchant_city,
            "TRAN_MERCHANT_ZIP": tran_merchant_zip,
            "TRAN_CARD_NUM": tran_card_num,
            "TRAN_ORIG_TS": db2_ts,
            "TRAN_PROC_TS": db2_ts,
            "FILLER": "",
        }

        line = format_tran_record(tran_rec)
        tran_out.write(line + "\n")

    # Main loop over tcatbal.txt
    try:
        with open("tcatbal.txt", "r", encoding="ascii") as tcat_file:
            for line in tcat_file:
                line = line.rstrip("\n")
                rec = parse_tcatbal_line(line)
                ws_record_count += 1

                trancat_acct_id = rec["TRANCAT_ACCT_ID"]
                trancat_type_cd = rec["TRANCAT_TYPE_CD"]
                trancat_cd = rec["TRANCAT_CD"]
                tran_cat_bal = rec["TRAN_CAT_BAL"]

                # DISPLAY TRAN-CAT-BAL-RECORD (we skip actual display of full record)
                # Account change handling
                if trancat_acct_id != ws_last_acct_num:
                    if ws_first_time != "Y":
                        update_account()
                    else:
                        ws_first_time = "N"

                    ws_total_int = Decimal(0)
                    ws_last_acct_num = trancat_acct_id

                    # Get account data
                    acct_rec = get_acct_data(trancat_acct_id)
                    # Get xref data
                    xref_rec = get_xref_data(trancat_acct_id)
                else:
                    # Same account as previous
                    acct_rec = get_acct_data(trancat_acct_id)
                    xref_rec = get_xref_data(trancat_acct_id)

                # Prepare disclosure group key
                acct_group_id = acct_rec["ACCT_GROUP_ID"]
                dis_int_rate = get_interest_rate(acct_group_id, trancat_type_cd, trancat_cd)

                if dis_int_rate != Decimal(0):
                    # COMPUTE WS-MONTHLY-INT = (TRAN-CAT-BAL * DIS-INT-RATE) / 1200
                    ws_monthly_int = (tran_cat_bal * dis_int_rate) / Decimal(1200)
                    ws_total_int = ws_total_int + ws_monthly_int
                    write_transaction(acct_rec, xref_rec, ws_monthly_int)
                # 1400-COMPUTE-FEES is "To be implemented" -> no-op

    except FileNotFoundError:
        print("ERROR OPENING TRANSACTION CATEGORY BALANCE")
        tran_out.close()
        sys.exit(1)

    # After EOF, update last account if any records processed
    if ws_first_time != "Y" and ws_last_acct_num.strip() != "":
        update_account()

    tran_out.close()

    # ------------------------------------------------------------------
    # Write updated accounts to acctdata-out.txt
    # ------------------------------------------------------------------

    try:
        with open("acctdata-out.txt", "w", encoding="ascii") as acct_out:
            for rec in acct_records:
                # rec in acct_records is the same dict as in acct_by_id; updated in place
                line = format_acct_record(rec)
                acct_out.write(line + "\n")
    except OSError:
        print("ERROR WRITING ACCOUNT FILE")
        sys.exit(1)

    print("END OF EXECUTION OF PROGRAM CBACT04C")


if __name__ == "__main__":
    main()
