#!/bin/bash
# Runs the ORIGINAL CBACT04C (unchanged) under GnuCOBOL on the test data.
# Stand-ins for z/OS: RUNINT (passes PARM like the JCL EXEC card),
# CEE3ABD stub (abend service), LOADVSAM/UNLDACCT (like IDCAMS REPRO).
set -e
export PATH=/opt/gnucobol/bin:$PATH LD_LIBRARY_PATH=/opt/gnucobol/lib
H=$(cd "$(dirname "$0")" && pwd); W=$H/run-cobol; rm -rf $W; mkdir -p $W; cd $W
for f in cardxref acctdata discgrp; do tr -d '\r' < $H/data/$f.txt > $f.txt; done
tr -d '\r' < $H/data/${1:-tcatbal-TEST}.txt > tcatbal.txt
export DD_TCATIN=tcatbal.txt DD_XREFIN=cardxref.txt DD_ACCTIN=acctdata.txt DD_DISCIN=discgrp.txt
export DD_TCATBALF=tcatbal.idx DD_XREFFILE=xref.idx DD_ACCTFILE=acct.idx DD_DISCGRP=discgrp.idx
export DD_TRANSACT=systran.dat DD_ACCTOUT=acctdata-out.txt
$H/cobol/loadvsam
$H/cobol/runint > cobol-sysout.txt 2>&1 || echo "RUN ENDED WITH RC=$?"
$H/cobol/unldacct
fold -w 350 systran.dat > systran.txt 2>/dev/null || true
echo "--- COBOL run finished: $(grep -c '' systran.txt 2>/dev/null) transactions written"
