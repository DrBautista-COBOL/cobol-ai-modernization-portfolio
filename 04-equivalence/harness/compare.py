"""Field-by-field comparison of COBOL vs Python outputs (timestamps excluded: they record run time)."""
from decimal import Decimal
POS="{ABCDEFGHI"; NEG="}JKLMNOPQR"
def z(s):
    s=s; d=s[-1]; sign=1
    if d in POS: v=POS.index(d)
    elif d in NEG: v=NEG.index(d); sign=-1
    else: v=int(d)
    return sign*Decimal(int(s[:-1]+str(v))).scaleb(-2)
T=[("TRAN-ID",0,16),("TYPE",16,18),("CAT",18,22),("SOURCE",22,32),("DESC",32,132),("AMOUNT",132,143),
   ("MERCHANT-ID",143,152),("MERCH-NAME",152,202),("MERCH-CITY",202,252),("MERCH-ZIP",252,262),("CARD-NUM",262,278)]
def recs(path,n):
    d=open(path).read()
    if "\n" in d: return [l.rstrip("\r\n").ljust(n) for l in d.splitlines() if l.strip()]
    return [d[i:i+n] for i in range(0,len(d),n)]
c=recs("run-cobol/systran.dat",350); p=recs("run-python/systran.txt",350)
print(f"Transactions: COBOL {len(c)}  Python {len(p)}")
diffs=0
for i,(a,b) in enumerate(zip(c,p),1):
    for name,s,e in T:
        if a[s:e]!=b[s:e]:
            diffs+=1
            extra=f"  ({z(a[s:e])} vs {z(b[s:e])})" if name=="AMOUNT" else ""
            print(f"  tran {i} acct {a[45:56]} {name}: COBOL {a[s:e].strip()!r} Python {b[s:e].strip()!r}{extra}")
print(f"Transaction field differences: {diffs}")
A=[("CURR-BAL",12,24),("CYC-CREDIT",78,90),("CYC-DEBIT",90,102)]
ca=recs("run-cobol/acctdata-out.txt",300); pa=recs("run-python/acctdata-out.txt",300)
orig=recs("data/acctdata.txt",300)
print(f"Accounts: COBOL {len(ca)}  Python {len(pa)}")
ad=0; other=0
for a,b,o in zip(ca,pa,orig):
    for name,s,e in A:
        if a[s:e]!=b[s:e]:
            ad+=1; print(f"  acct {a[:11]} {name}: original {z(o[s:e])}  COBOL {z(a[s:e])}  Python {z(b[s:e])}")
    rest_a=a[:12]+a[24:78]+a[102:]; rest_b=b[:12]+b[24:78]+b[102:]
    if rest_a.rstrip()!=rest_b.rstrip(): other+=1
print(f"Account balance differences: {ad};  other-field differences: {other}")
changed=[(a[:11],z(o[12:24]),z(a[12:24])) for a,o in zip(ca,orig) if a[12:24]!=o[12:24]]
print("COBOL balance changes:",[(int(x),str(y),str(w)) for x,y,w in changed])
